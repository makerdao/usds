// SPDX-License-Identifier: AGPL-3.0-or-later

pragma solidity ^0.8.21;

import "dss-test/DssTest.sol";
import "dss-interfaces/Interfaces.sol";
import { ERC1967Proxy } from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

import { Nst } from "src/Nst.sol";

import { NstJoin } from "src/NstJoin.sol";

contract NstJoinTest is DssTest {
    ChainlogAbstract constant chainLog = ChainlogAbstract(0xdA0Ab1e0017DEbCd72Be8599041a2aa3bA7e740F);

    VatAbstract vat;
    Nst         nst;
    NstJoin     nstJoin;

    event Join(address indexed caller, address indexed usr, uint256 wad);
    event Exit(address indexed caller, address indexed usr, uint256 wad);

    function setUp() public {
        vm.createSelectFork(vm.envString("ETH_RPC_URL"));

        vat = VatAbstract(chainLog.getAddress("MCD_VAT"));
        address pauseProxy = chainLog.getAddress("MCD_PAUSE_PROXY");
        nst = Nst(address(new ERC1967Proxy(address(new Nst()), abi.encodeCall(Nst.initialize, ()))));
        nstJoin = new NstJoin(address(vat), address(nst));
        assertEq(nstJoin.dai(), address(nstJoin.nst()));
        nst.rely(address(nstJoin));
        nst.deny(address(this));
        vm.prank(pauseProxy); vat.suck(address(this), address(this), 10_000 * RAD);
    }

    function testJoinExit() public {
        address receiver = address(123);
        assertEq(nst.balanceOf(receiver), 0);
        assertEq(vat.dai(address(this)), 10_000 * RAD);
        vm.expectRevert("Vat/not-allowed");
        nstJoin.exit(receiver, 4_000 * WAD);
        vat.hope(address(nstJoin));
        vm.expectEmit(true, true, true, true);
        emit Exit(address(this), receiver, 4_000 * WAD);
        nstJoin.exit(receiver, 4_000 * WAD);
        assertEq(nst.balanceOf(receiver), 4_000 * WAD);
        assertEq(vat.dai(address(this)), 6_000 * RAD);
        vm.startPrank(receiver);
        nst.approve(address(nstJoin), 2_000 * WAD);
        vm.expectEmit(true, true, true, true);
        emit Join(receiver, address(this), 2_000 * WAD);
        nstJoin.join(address(this), 2_000 * WAD);
        assertEq(nst.balanceOf(receiver), 2_000 * WAD);
        assertEq(vat.dai(address(this)), 8_000 * RAD);
    }
}
