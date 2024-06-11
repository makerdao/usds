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

pragma solidity ^0.8.21;

import "dss-test/DssTest.sol";
import "dss-interfaces/Interfaces.sol";

import { Upgrades } from "openzeppelin-foundry-upgrades/Upgrades.sol";

import { NstInstance } from "deploy/NstInstance.sol";
import { NstDeploy } from "deploy/NstDeploy.sol";
import { NstInit } from "deploy/NstInit.sol";

import { Nst } from "src/Nst.sol";
import { DaiNst } from "src/DaiNst.sol";

contract DeploymentTest is DssTest {
    ChainlogAbstract constant chainLog = ChainlogAbstract(0xdA0Ab1e0017DEbCd72Be8599041a2aa3bA7e740F);

    address pauseProxy;
    DaiAbstract dai;
    address daiJoin;

    NstInstance inst;

    function setUp() public {
        vm.createSelectFork(vm.envString("ETH_RPC_URL"));

        pauseProxy = chainLog.getAddress("MCD_PAUSE_PROXY");
        daiJoin    = chainLog.getAddress("MCD_JOIN_DAI");
        dai        = DaiAbstract(chainLog.getAddress("MCD_DAI"));

        inst = NstDeploy.deploy(address(this), pauseProxy, daiJoin);
    }

    function testSetUp() public {
        DssInstance memory dss = MCD.loadFromChainlog(address(chainLog));

        assertEq(Nst(inst.nst).wards(pauseProxy), 1);
        assertEq(Nst(inst.nst).wards(inst.nstJoin), 0);
        assertEq(Upgrades.getImplementationAddress(inst.nst), inst.nstImp);

        vm.startPrank(pauseProxy);
        NstInit.init(dss, inst);
        vm.stopPrank();

        assertEq(Nst(inst.nst).wards(pauseProxy), 1);
        assertEq(Nst(inst.nst).wards(inst.nstJoin), 1);

        deal(address(dai), address(this), 1000);

        assertEq(dai.balanceOf(address(this)), 1000);
        assertEq(Nst(inst.nst).balanceOf(address(this)), 0);

        dai.approve(inst.daiNst, 600);
        DaiNst(inst.daiNst).daiToNst(address(this), 600);

        assertEq(dai.balanceOf(address(this)), 400);
        assertEq(Nst(inst.nst).balanceOf(address(this)), 600);

        Nst(inst.nst).approve(inst.daiNst, 400);
        DaiNst(inst.daiNst).nstToDai(address(this), 400);

        assertEq(dai.balanceOf(address(this)), 800);
        assertEq(Nst(inst.nst).balanceOf(address(this)), 200);

        assertEq(chainLog.getAddress("NST"), inst.nst);
        assertEq(chainLog.getAddress("NST_IMP"), inst.nstImp);
        assertEq(chainLog.getAddress("NST_JOIN"), inst.nstJoin);
        assertEq(chainLog.getAddress("DAI_NST"), inst.daiNst);
    }
}
