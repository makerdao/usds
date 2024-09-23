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

import { UsdsInstance } from "deploy/UsdsInstance.sol";
import { UsdsDeploy } from "deploy/UsdsDeploy.sol";
import { UsdsInit } from "deploy/UsdsInit.sol";

import { Usds } from "src/Usds.sol";
import { DaiUsds } from "src/DaiUsds.sol";

contract DeploymentTest is DssTest {
    ChainlogAbstract constant chainLog = ChainlogAbstract(0xdA0Ab1e0017DEbCd72Be8599041a2aa3bA7e740F);

    address pauseProxy;
    DaiAbstract dai;
    address daiJoin;

    UsdsInstance inst;

    function setUp() public {
        vm.createSelectFork(vm.envString("ETH_RPC_URL"));

        pauseProxy = chainLog.getAddress("MCD_PAUSE_PROXY");
        daiJoin    = chainLog.getAddress("MCD_JOIN_DAI");
        dai        = DaiAbstract(chainLog.getAddress("MCD_DAI"));

        inst = UsdsDeploy.deploy(address(this), pauseProxy, daiJoin);
    }

    function testSetUp() public {
        DssInstance memory dss = MCD.loadFromChainlog(address(chainLog));

        assertEq(Usds(inst.usds).wards(pauseProxy), 1);
        assertEq(Usds(inst.usds).wards(inst.usdsJoin), 0);
        assertEq(Upgrades.getImplementationAddress(inst.usds), inst.usdsImp);

        vm.startPrank(pauseProxy);
        UsdsInit.init(dss, inst);
        vm.stopPrank();

        assertEq(Usds(inst.usds).wards(pauseProxy), 1);
        assertEq(Usds(inst.usds).wards(inst.usdsJoin), 1);

        deal(address(dai), address(this), 1000);

        assertEq(dai.balanceOf(address(this)), 1000);
        assertEq(Usds(inst.usds).balanceOf(address(this)), 0);

        dai.approve(inst.daiUsds, 600);
        DaiUsds(inst.daiUsds).daiToUsds(address(this), 600);

        assertEq(dai.balanceOf(address(this)), 400);
        assertEq(Usds(inst.usds).balanceOf(address(this)), 600);

        Usds(inst.usds).approve(inst.daiUsds, 400);
        DaiUsds(inst.daiUsds).usdsToDai(address(this), 400);

        assertEq(dai.balanceOf(address(this)), 800);
        assertEq(Usds(inst.usds).balanceOf(address(this)), 200);

        assertEq(chainLog.getAddress("USDS"), inst.usds);
        assertEq(chainLog.getAddress("USDS_IMP"), inst.usdsImp);
        assertEq(chainLog.getAddress("USDS_JOIN"), inst.usdsJoin);
        assertEq(chainLog.getAddress("DAI_USDS"), inst.daiUsds);
    }
}
