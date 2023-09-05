// SPDX-FileCopyrightText: © 2023 Dai Foundation <www.daifoundation.org>
// SPDX-License-Identifier: AGPL-3.0-or-later
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

pragma solidity ^0.8.16;

import "dss-test/DssTest.sol";

import { NstInstance } from "deploy/NstInstance.sol";
import { NstDeploy } from "deploy/NstDeploy.sol";
import { NstInit } from "deploy/NstInit.sol";

import { Nst } from "src/Nst.sol";
import { DaiNst } from "src/DaiNst.sol";

interface ChainlogLike {
    function getAddress(bytes32) external view returns (address);
}

interface GemLike {
    function balanceOf(address) external view returns (uint256);
    function approve(address, uint256) external;
}

contract DeploymentTest is DssTest {
    address constant LOG = 0xdA0Ab1e0017DEbCd72Be8599041a2aa3bA7e740F;

    address PAUSE_PROXY;
    address DAI;
    address DAIJOIN;

    NstInstance inst;

    function setUp() public {
        vm.createSelectFork(vm.envString("ETH_RPC_URL"));

        PAUSE_PROXY = ChainlogLike(LOG).getAddress("MCD_PAUSE_PROXY");
        DAIJOIN     = ChainlogLike(LOG).getAddress("MCD_JOIN_DAI");
        DAI         = ChainlogLike(LOG).getAddress("MCD_DAI");

        inst = NstDeploy.deploy(address(this), PAUSE_PROXY, DAIJOIN);
    }

    function testSetUp() public {
        DssInstance memory dss = MCD.loadFromChainlog(LOG);

        assertEq(Nst(inst.nst).wards(PAUSE_PROXY), 1);
        assertEq(Nst(inst.nst).wards(inst.nstJoin), 0);

        vm.startPrank(PAUSE_PROXY);
        NstInit.init(dss, inst);
        vm.stopPrank();

        assertEq(Nst(inst.nst).wards(PAUSE_PROXY), 0);
        assertEq(Nst(inst.nst).wards(inst.nstJoin), 1);

        deal(DAI, address(this), 1000);

        assertEq(GemLike(DAI).balanceOf(address(this)), 1000);
        assertEq(GemLike(inst.nst).balanceOf(address(this)), 0);

        GemLike(DAI).approve(inst.daiNst, 600);
        DaiNst(inst.daiNst).daiToNst(address(this), 600);

        assertEq(GemLike(DAI).balanceOf(address(this)), 400);
        assertEq(GemLike(inst.nst).balanceOf(address(this)), 600);

        GemLike(inst.nst).approve(inst.daiNst, 400);
        DaiNst(inst.daiNst).nstToDai(address(this), 400);

        assertEq(GemLike(DAI).balanceOf(address(this)), 800);
        assertEq(GemLike(inst.nst).balanceOf(address(this)), 200);

        assertEq(ChainlogLike(LOG).getAddress("NST"), inst.nst);
        assertEq(ChainlogLike(LOG).getAddress("NSTJOIN"), inst.nstJoin);
        assertEq(ChainlogLike(LOG).getAddress("DAINST"), inst.daiNst);
    }
}
