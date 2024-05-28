// SPDX-License-Identifier: AGPL-3.0-or-later

pragma solidity ^0.8.21;

import "dss-test/DssTest.sol";
import "dss-interfaces/Interfaces.sol";
import { ERC1967Proxy } from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

import { Nst } from "src/Nst.sol";
import { NstJoin } from "src/NstJoin.sol";
import { DaiNst } from "src/DaiNst.sol";

contract DaiNstTest is DssTest {
    ChainlogAbstract constant chainLog = ChainlogAbstract(0xdA0Ab1e0017DEbCd72Be8599041a2aa3bA7e740F);

    VatAbstract     vat;
    DaiAbstract     dai;
    DaiJoinAbstract daiJoin;
    Nst             nst;
    NstJoin         nstJoin;
    DaiNst          daiNst;

    event DaiToNst(address indexed caller, address indexed usr, uint256 wad);
    event NstToDai(address indexed caller, address indexed usr, uint256 wad);

    function setUp() public {
        vm.createSelectFork(vm.envString("ETH_RPC_URL"));

        vat = VatAbstract(chainLog.getAddress("MCD_VAT"));
        dai = DaiAbstract(chainLog.getAddress("MCD_DAI"));
        daiJoin = DaiJoinAbstract(chainLog.getAddress("MCD_JOIN_DAI"));
        address pauseProxy = chainLog.getAddress("MCD_PAUSE_PROXY");
        nst = Nst(address(new ERC1967Proxy(address(new Nst()), abi.encodeCall(Nst.initialize, ()))));
        nstJoin = new NstJoin(address(vat), address(nst));
        nst.rely(address(nstJoin));
        nst.deny(address(this));

        daiNst = new DaiNst(address(daiJoin), address(nstJoin));

        vm.prank(pauseProxy); vat.suck(address(this), address(this), 10_000 * RAD);
    }

    function testExchange() public {
        uint256 daiSup = dai.totalSupply();
        vat.hope(address(daiJoin));
        daiJoin.exit(address(this), 10_000 * WAD);
        assertEq(dai.balanceOf(address(this)), 10_000 * WAD);
        assertEq(dai.totalSupply() - daiSup,   10_000 * WAD);
        assertEq(nst.balanceOf(address(this)),            0);
        assertEq(nst.totalSupply(),                       0);

        dai.approve(address(daiNst), 4_000 * WAD);
        vm.expectEmit(true, true, true, true);
        emit DaiToNst(address(this), address(this), 4_000 * WAD);
        daiNst.daiToNst(address(this), 4_000 * WAD);
        assertEq(dai.balanceOf(address(this)),  6_000 * WAD);
        assertEq(dai.totalSupply() - daiSup,    6_000 * WAD);
        assertEq(nst.balanceOf(address(this)),  4_000 * WAD);
        assertEq(nst.totalSupply(),             4_000 * WAD);

        nst.approve(address(daiNst), 2_000 * WAD);
        vm.expectEmit(true, true, true, true);
        emit NstToDai(address(this), address(this), 2_000 * WAD);
        daiNst.nstToDai(address(this), 2_000 * WAD);
        assertEq(dai.balanceOf(address(this)),  8_000 * WAD);
        assertEq(dai.totalSupply() - daiSup,    8_000 * WAD);
        assertEq(nst.balanceOf(address(this)),  2_000 * WAD);
        assertEq(nst.totalSupply(),             2_000 * WAD);

        address receiver = address(123);
        assertEq(dai.balanceOf(receiver),                 0);
        assertEq(nst.balanceOf(receiver),                 0);

        dai.approve(address(daiNst), 1_500 * WAD);
        vm.expectEmit(true, true, true, true);
        emit DaiToNst(address(this), receiver,  1_500 * WAD);
        daiNst.daiToNst(receiver, 1_500 * WAD);
        assertEq(dai.balanceOf(address(this)),  6_500 * WAD);
        assertEq(dai.balanceOf(receiver),                0);
        assertEq(dai.totalSupply() - daiSup,    6_500 * WAD);
        assertEq(nst.balanceOf(address(this)),  2_000 * WAD);
        assertEq(nst.balanceOf(receiver),       1_500 * WAD);
        assertEq(nst.totalSupply(),             3_500 * WAD);

        nst.approve(address(daiNst), 500 * WAD);
        vm.expectEmit(true, true, true, true);
        emit NstToDai(address(this), receiver,    500 * WAD);
        daiNst.nstToDai(receiver, 500 * WAD);
        assertEq(dai.balanceOf(address(this)),  6_500 * WAD);
        assertEq(dai.balanceOf(receiver),         500 * WAD);
        assertEq(dai.totalSupply() - daiSup,    7_000 * WAD);
        assertEq(nst.balanceOf(address(this)),  1_500 * WAD);
        assertEq(nst.balanceOf(receiver),       1_500 * WAD);
        assertEq(nst.totalSupply(),             3_000 * WAD);
    }
}
