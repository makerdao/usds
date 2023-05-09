// SPDX-License-Identifier: AGPL-3.0-or-later

pragma solidity ^0.8.16;

import "dss-test/DssTest.sol";

import { Nst } from "../Nst.sol";

import { NstJoin } from "../NstJoin.sol";

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

contract NstJoinTest is DssTest {
    VatMock vat;
    Nst     nst;
    NstJoin nstJoin;

    event Join(address indexed caller, address indexed usr, uint256 wad);
    event Exit(address indexed caller, address indexed usr, uint256 wad);

    function setUp() public {
        vat = new VatMock();
        nst = new Nst();
        nstJoin = new NstJoin(address(vat), address(nst));
        assertEq(nstJoin.dai(), address(nstJoin.nst()));
        nst.rely(address(nstJoin));
        nst.deny(address(this));
        vat.suck(address(this), 10_000 * RAD);
    }

    function testJoinExit() public {
        address receiver = address(123);
        assertEq(nst.balanceOf(receiver), 0);
        assertEq(vat.dai(address(this)), 10_000 * RAD);
        vm.expectRevert("VatMock/not-allowed");
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
