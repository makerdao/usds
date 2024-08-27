// SPDX-License-Identifier: AGPL-3.0-or-later

/// DaiUsds.sol -- Dai/Usds Exchanger

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

interface UsdsJoinLike is JoinLike {
    function usds() external view returns (address);
}

interface GemLike {
    function approve(address, uint256) external returns (bool);
    function transferFrom(address, address, uint256) external returns (bool);
}

interface VatLike {
    function hope(address) external;
}

contract DaiUsds {
    DaiJoinLike  public immutable daiJoin;
    UsdsJoinLike public immutable usdsJoin;
    GemLike      public immutable dai;
    GemLike      public immutable usds;
    
    event DaiToUsds(address indexed caller, address indexed usr, uint256 wad);
    event UsdsToDai(address indexed caller, address indexed usr, uint256 wad);

    constructor(address daiJoin_, address usdsJoin_) {
        daiJoin  = DaiJoinLike(daiJoin_);
        usdsJoin = UsdsJoinLike(usdsJoin_);

        address vat = daiJoin.vat();
        require(vat == usdsJoin.vat(), "DaiUsds/vat-not-same");

        dai  = GemLike(daiJoin.dai());
        usds = GemLike(usdsJoin.usds());

        dai.approve(address(daiJoin), type(uint256).max);
        usds.approve(address(usdsJoin), type(uint256).max);

        VatLike(vat).hope(address(daiJoin));
        VatLike(vat).hope(address(usdsJoin));
    }

    function daiToUsds(address usr, uint256 wad) external {
        dai.transferFrom(msg.sender, address(this), wad);
        daiJoin.join(address(this), wad);
        usdsJoin.exit(usr, wad);
        emit DaiToUsds(msg.sender, usr, wad);
    }

    function usdsToDai(address usr, uint256 wad) external {
        usds.transferFrom(msg.sender, address(this), wad);
        usdsJoin.join(address(this), wad);
        daiJoin.exit(usr, wad);
        emit UsdsToDai(msg.sender, usr, wad);
    }
}
