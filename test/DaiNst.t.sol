// SPDX-License-Identifier: AGPL-3.0-or-later

pragma solidity ^0.8.16;

import "dss-test/DssTest.sol";

import { Nst } from "src/Nst.sol";
import { NstJoin } from "src/NstJoin.sol";
import { DaiNst } from "src/DaiNst.sol";

contract VatMock {
    mapping (address => mapping (address => uint256)) public can;
    mapping (address => uint256)                      public dai;

    function either(bool x, bool y) internal pure returns (bool z) {
        assembly{ z := or(x, y)}
    }

    function wish(address bit, address usr) internal view returns (bool) {
        return either(bit == usr, can[bit][usr] == 1);
    }

    function hope(address usr) external {
        can[msg.sender][usr] = 1;
    }

    function suck(address addr, uint256 rad) external {
        dai[addr] = dai[addr] + rad;
    }

    function move(address src, address dst, uint256 rad) external {
        require(wish(src, msg.sender), "VatMock/not-allowed");
        dai[src] = dai[src] - rad;
        dai[dst] = dai[dst] + rad;
    }
}

contract Dai is Nst {}

contract DaiJoin is NstJoin {
    constructor(address vat_, address dai_) NstJoin(vat_, dai_) {}
}

contract DaiNstTest is DssTest {
    VatMock vat;
    Dai     dai;
    DaiJoin daiJoin;
    Nst     nst;
    NstJoin nstJoin;
    DaiNst  daiNst;

    event DaiToNst(address indexed caller, address indexed usr, uint256 wad);
    event NstToDai(address indexed caller, address indexed usr, uint256 wad);

    function setUp() public {
        vat = new VatMock();
        dai = new Dai();
        daiJoin = new DaiJoin(address(vat), address(dai));
        dai.rely(address(daiJoin));
        dai.deny(address(this));
        nst = new Nst();
        nstJoin = new NstJoin(address(vat), address(nst));
        nst.rely(address(nstJoin));
        nst.deny(address(this));

        daiNst = new DaiNst(address(daiJoin), address(nstJoin));

        vat.suck(address(this), 10_000 * RAD);
    }

    function testExchange() public {
        vat.hope(address(daiJoin));
        daiJoin.exit(address(this), 10_000 * WAD);
        assertEq(dai.balanceOf(address(this)), 10_000 * WAD);
        assertEq(dai.totalSupply(),            10_000 * WAD);
        assertEq(nst.balanceOf(address(this)), 0);
        assertEq(nst.totalSupply(),            0);

        dai.approve(address(daiNst), 4_000 * WAD);
        vm.expectEmit(true, true, true, true);
        emit DaiToNst(address(this), address(this), 4_000 * WAD);
        daiNst.daiToNst(address(this), 4_000 * WAD);
        assertEq(dai.balanceOf(address(this)), 6_000 * WAD);
        assertEq(dai.totalSupply(),            6_000 * WAD);
        assertEq(nst.balanceOf(address(this)), 4_000 * WAD);
        assertEq(nst.totalSupply(),            4_000 * WAD);

        nst.approve(address(daiNst), 2_000 * WAD);
        vm.expectEmit(true, true, true, true);
        emit NstToDai(address(this), address(this), 2_000 * WAD);
        daiNst.nstToDai(address(this), 2_000 * WAD);
        assertEq(dai.balanceOf(address(this)), 8_000 * WAD);
        assertEq(dai.totalSupply(),            8_000 * WAD);
        assertEq(nst.balanceOf(address(this)), 2_000 * WAD);
        assertEq(nst.totalSupply(),            2_000 * WAD);

        address receiver = address(123);
        assertEq(dai.balanceOf(receiver),                0);
        assertEq(nst.balanceOf(receiver),                0);

        dai.approve(address(daiNst), 1_500 * WAD);
        vm.expectEmit(true, true, true, true);
        emit DaiToNst(address(this), receiver, 1_500 * WAD);
        daiNst.daiToNst(receiver, 1_500 * WAD);
        assertEq(dai.balanceOf(address(this)), 6_500 * WAD);
        assertEq(dai.balanceOf(receiver),                0);
        assertEq(dai.totalSupply(),            6_500 * WAD);
        assertEq(nst.balanceOf(address(this)), 2_000 * WAD);
        assertEq(nst.balanceOf(receiver),      1_500 * WAD);
        assertEq(nst.totalSupply(),            3_500 * WAD);

        nst.approve(address(daiNst), 500 * WAD);
        vm.expectEmit(true, true, true, true);
        emit NstToDai(address(this), receiver, 500 * WAD);
        daiNst.nstToDai(receiver, 500 * WAD);
        assertEq(dai.balanceOf(address(this)), 6_500 * WAD);
        assertEq(dai.balanceOf(receiver),        500 * WAD);
        assertEq(dai.totalSupply(),            7_000 * WAD);
        assertEq(nst.balanceOf(address(this)), 1_500 * WAD);
        assertEq(nst.balanceOf(receiver),      1_500 * WAD);
        assertEq(nst.totalSupply(),            3_000 * WAD);
    }
}
