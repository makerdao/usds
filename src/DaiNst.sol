// SPDX-License-Identifier: AGPL-3.0-or-later

/// DaiNst.sol -- Dai/Nst Exchanger

// Copyright (C) 2023 Dai Foundation
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

interface JoinLike {
    function vat() external view returns (address);
    function join(address, uint256) external;
    function exit(address, uint256) external;
}

interface DaiJoinLike is JoinLike {
    function dai() external view returns (address);
}

interface NstJoinLike is JoinLike {
    function nst() external view returns (address);
}

interface GemLike {
    function approve(address, uint256) external returns (bool);
    function transferFrom(address, address, uint256) external returns (bool);
}

interface VatLike {
    function hope(address) external;
}

contract DaiNst {
    DaiJoinLike public immutable daiJoin;
    NstJoinLike public immutable nstJoin;
    GemLike     public immutable dai;
    GemLike     public immutable nst;
    
    event DaiToNst(address indexed caller, address indexed usr, uint256 wad);
    event NstToDai(address indexed caller, address indexed usr, uint256 wad);

    constructor(address daiJoin_, address nstJoin_) {
        daiJoin = DaiJoinLike(daiJoin_);
        nstJoin = NstJoinLike(nstJoin_);

        address vat = daiJoin.vat();
        require(vat == nstJoin.vat(), "DaiNst/vat-not-same");

        dai = GemLike(daiJoin.dai());
        nst = GemLike(nstJoin.nst());

        dai.approve(address(daiJoin), type(uint256).max);
        nst.approve(address(nstJoin), type(uint256).max);

        VatLike(vat).hope(address(daiJoin));
        VatLike(vat).hope(address(nstJoin));
    }

    function daiToNst(address usr, uint256 wad) external {
        dai.transferFrom(msg.sender, address(this), wad);
        daiJoin.join(address(this), wad);
        nstJoin.exit(usr, wad);
        emit DaiToNst(msg.sender, usr, wad);
    }

    function nstToDai(address usr, uint256 wad) external {
        nst.transferFrom(msg.sender, address(this), wad);
        nstJoin.join(address(this), wad);
        daiJoin.exit(usr, wad);
        emit NstToDai(msg.sender, usr, wad);
    }
}
