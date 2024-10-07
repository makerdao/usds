// SPDX-FileCopyrightText: © 2024 Dai Foundation <www.daifoundation.org>
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

import { Upgrades } from "openzeppelin-foundry-upgrades/Upgrades.sol";

import { UsdsL2Instance } from "deploy/UsdsInstance.sol";
import { UsdsDeploy } from "deploy/UsdsDeploy.sol";

import { Usds } from "src/Usds.sol";

contract L2DeploymentTest is DssTest {

    address l2GovRelay = address(222);
    UsdsL2Instance inst;

    function setUp() public {
        inst = UsdsDeploy.deployL2(address(this), l2GovRelay);
    }

    function testSetUp() public view {
        assertEq(Usds(inst.usds).wards(l2GovRelay), 1);
        assertEq(Usds(inst.usds).wards(address(this)), 0);
        assertEq(Upgrades.getImplementationAddress(inst.usds), inst.usdsImp);
        assertEq(Usds(inst.usds).version(), "1");
    }
}
