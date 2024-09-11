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

import { ScriptTools } from "dss-test/ScriptTools.sol";
import { ERC1967Proxy } from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";

import { Usds } from "src/Usds.sol";
import { UsdsJoin } from "src/UsdsJoin.sol";
import { DaiUsds } from "src/DaiUsds.sol";

import { UsdsInstance, UsdsL2Instance } from "./UsdsInstance.sol";

interface DaiJoinLike {
    function vat() external view returns (address);
}

library UsdsDeploy {
    function deploy(
        address deployer,
        address owner,
        address daiJoin
    ) internal returns (UsdsInstance memory instance) {
        address _usdsImp = address(new Usds());
        address _usds = address((new ERC1967Proxy(_usdsImp, abi.encodeCall(Usds.initialize, ()))));
        ScriptTools.switchOwner(_usds, deployer, owner);

        address _usdsJoin = address(new UsdsJoin(DaiJoinLike(daiJoin).vat(), _usds));
        address _daiUsds = address(new DaiUsds(daiJoin, _usdsJoin));

        instance.usds     = _usds;
        instance.usdsImp  = _usdsImp;
        instance.usdsJoin = _usdsJoin;
        instance.daiUsds  = _daiUsds;
    }

    function deployL2(
        address deployer,
        address owner
    ) internal returns (UsdsL2Instance memory instance) {
        address _usdsImp = address(new Usds());
        address _usds = address((new ERC1967Proxy(_usdsImp, abi.encodeCall(Usds.initialize, ()))));
        ScriptTools.switchOwner(_usds, deployer, owner);

        instance.usds     = _usds;
        instance.usdsImp  = _usdsImp;
    }
}
