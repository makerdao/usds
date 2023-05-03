// SPDX-License-Identifier: AGPL-3.0-or-later

pragma solidity ^0.8.16;

import "dss-test/DssTest.sol";

import { Nst } from "../Nst.sol";
import { NstJoin } from "../NstJoin.sol";
import { DaiNst } from "../DaiNst.sol";

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
        daiNst.daiToNst(4_000 * WAD);
        assertEq(dai.balanceOf(address(this)), 6_000 * WAD);
        assertEq(dai.totalSupply(),            6_000 * WAD);
        assertEq(nst.balanceOf(address(this)), 4_000 * WAD);
        assertEq(nst.totalSupply(),            4_000 * WAD);

        nst.approve(address(daiNst), 2_000 * WAD);
        daiNst.nstToDai(2_000 * WAD);
        assertEq(dai.balanceOf(address(this)), 8_000 * WAD);
        assertEq(dai.totalSupply(),            8_000 * WAD);
        assertEq(nst.balanceOf(address(this)), 2_000 * WAD);
        assertEq(nst.totalSupply(),            2_000 * WAD);
    }
}
