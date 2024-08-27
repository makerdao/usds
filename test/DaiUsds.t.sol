// SPDX-License-Identifier: AGPL-3.0-or-later

pragma solidity ^0.8.21;

import "dss-test/DssTest.sol";
import "dss-interfaces/Interfaces.sol";
import { ERC1967Proxy } from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

import { Usds } from "src/Usds.sol";
import { UsdsJoin } from "src/UsdsJoin.sol";
import { DaiUsds } from "src/DaiUsds.sol";

contract DaiUsdsTest is DssTest {
    ChainlogAbstract constant chainLog = ChainlogAbstract(0xdA0Ab1e0017DEbCd72Be8599041a2aa3bA7e740F);

    VatAbstract     vat;
    DaiAbstract     dai;
    DaiJoinAbstract daiJoin;
    Usds            usds;
    UsdsJoin        usdsJoin;
    DaiUsds         daiUsds;

    event DaiToUsds(address indexed caller, address indexed usr, uint256 wad);
    event UsdsToDai(address indexed caller, address indexed usr, uint256 wad);

    function setUp() public {
        vm.createSelectFork(vm.envString("ETH_RPC_URL"));

        vat = VatAbstract(chainLog.getAddress("MCD_VAT"));
        dai = DaiAbstract(chainLog.getAddress("MCD_DAI"));
        daiJoin = DaiJoinAbstract(chainLog.getAddress("MCD_JOIN_DAI"));
        address pauseProxy = chainLog.getAddress("MCD_PAUSE_PROXY");
        usds = Usds(address(new ERC1967Proxy(address(new Usds()), abi.encodeCall(Usds.initialize, ()))));
        usdsJoin = new UsdsJoin(address(vat), address(usds));
        usds.rely(address(usdsJoin));
        usds.deny(address(this));

        daiUsds = new DaiUsds(address(daiJoin), address(usdsJoin));

        vm.prank(pauseProxy); vat.suck(address(this), address(this), 10_000 * RAD);
    }

    function testExchange() public {
        uint256 daiSup = dai.totalSupply();
        vat.hope(address(daiJoin));
        daiJoin.exit(address(this), 10_000 * WAD);
        assertEq(dai.balanceOf(address(this)),  10_000 * WAD);
        assertEq(dai.totalSupply() - daiSup,    10_000 * WAD);
        assertEq(usds.balanceOf(address(this)),            0);
        assertEq(usds.totalSupply(),                       0);

        dai.approve(address(daiUsds), 4_000 * WAD);
        vm.expectEmit(true, true, true, true);
        emit DaiToUsds(address(this), address(this), 4_000 * WAD);
        daiUsds.daiToUsds(address(this), 4_000 * WAD);
        assertEq(dai.balanceOf(address(this)),   6_000 * WAD);
        assertEq(dai.totalSupply() - daiSup,     6_000 * WAD);
        assertEq(usds.balanceOf(address(this)),  4_000 * WAD);
        assertEq(usds.totalSupply(),             4_000 * WAD);

        usds.approve(address(daiUsds), 2_000 * WAD);
        vm.expectEmit(true, true, true, true);
        emit UsdsToDai(address(this), address(this), 2_000 * WAD);
        daiUsds.usdsToDai(address(this), 2_000 * WAD);
        assertEq(dai.balanceOf(address(this)),   8_000 * WAD);
        assertEq(dai.totalSupply() - daiSup,     8_000 * WAD);
        assertEq(usds.balanceOf(address(this)),  2_000 * WAD);
        assertEq(usds.totalSupply(),             2_000 * WAD);

        address receiver = address(123);
        assertEq(dai.balanceOf(receiver),                  0);
        assertEq(usds.balanceOf(receiver),                 0);

        dai.approve(address(daiUsds), 1_500 * WAD);
        vm.expectEmit(true, true, true, true);
        emit DaiToUsds(address(this), receiver,  1_500 * WAD);
        daiUsds.daiToUsds(receiver, 1_500 * WAD);
        assertEq(dai.balanceOf(address(this)),   6_500 * WAD);
        assertEq(dai.balanceOf(receiver),                 0);
        assertEq(dai.totalSupply() - daiSup,     6_500 * WAD);
        assertEq(usds.balanceOf(address(this)),  2_000 * WAD);
        assertEq(usds.balanceOf(receiver),       1_500 * WAD);
        assertEq(usds.totalSupply(),             3_500 * WAD);

        usds.approve(address(daiUsds), 500 * WAD);
        vm.expectEmit(true, true, true, true);
        emit UsdsToDai(address(this), receiver,    500 * WAD);
        daiUsds.usdsToDai(receiver, 500 * WAD);
        assertEq(dai.balanceOf(address(this)),   6_500 * WAD);
        assertEq(dai.balanceOf(receiver),          500 * WAD);
        assertEq(dai.totalSupply() - daiSup,     7_000 * WAD);
        assertEq(usds.balanceOf(address(this)),  1_500 * WAD);
        assertEq(usds.balanceOf(receiver),       1_500 * WAD);
        assertEq(usds.totalSupply(),             3_000 * WAD);
    }
}
