// SPDX-License-Identifier: AGPL-3.0-or-later

pragma solidity ^0.8.21;

import "dss-test/DssTest.sol";
import "dss-interfaces/Interfaces.sol";
import { ERC1967Proxy } from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

import { Usds } from "src/Usds.sol";

import { UsdsJoin } from "src/UsdsJoin.sol";

contract UsdsJoinTest is DssTest {
    ChainlogAbstract constant chainLog = ChainlogAbstract(0xdA0Ab1e0017DEbCd72Be8599041a2aa3bA7e740F);

    VatAbstract vat;
    Usds        usds;
    UsdsJoin    usdsJoin;

    event Join(address indexed caller, address indexed usr, uint256 wad);
    event Exit(address indexed caller, address indexed usr, uint256 wad);

    function setUp() public {
        vm.createSelectFork(vm.envString("ETH_RPC_URL"));

        vat = VatAbstract(chainLog.getAddress("MCD_VAT"));
        address pauseProxy = chainLog.getAddress("MCD_PAUSE_PROXY");
        usds = Usds(address(new ERC1967Proxy(address(new Usds()), abi.encodeCall(Usds.initialize, ()))));
        usdsJoin = new UsdsJoin(address(vat), address(usds));
        assertEq(usdsJoin.dai(), address(usdsJoin.usds()));
        usds.rely(address(usdsJoin));
        usds.deny(address(this));
        vm.prank(pauseProxy); vat.suck(address(this), address(this), 10_000 * RAD);
    }

    function testJoinExit() public {
        address receiver = address(123);
        assertEq(usds.balanceOf(receiver), 0);
        assertEq(vat.dai(address(this)), 10_000 * RAD);
        vm.expectRevert("Vat/not-allowed");
        usdsJoin.exit(receiver, 4_000 * WAD);
        vat.hope(address(usdsJoin));
        vm.expectEmit(true, true, true, true);
        emit Exit(address(this), receiver, 4_000 * WAD);
        usdsJoin.exit(receiver, 4_000 * WAD);
        assertEq(usds.balanceOf(receiver), 4_000 * WAD);
        assertEq(vat.dai(address(this)), 6_000 * RAD);
        vm.startPrank(receiver);
        usds.approve(address(usdsJoin), 2_000 * WAD);
        vm.expectEmit(true, true, true, true);
        emit Join(receiver, address(this), 2_000 * WAD);
        usdsJoin.join(address(this), 2_000 * WAD);
        assertEq(usds.balanceOf(receiver), 2_000 * WAD);
        assertEq(vat.dai(address(this)), 8_000 * RAD);
    }
}
