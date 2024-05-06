// SPDX-License-Identifier: AGPL-3.0-or-later

/// NstJoin.sol -- Nst adapter

// Copyright (C) 2018 Rain <rainbreak@riseup.net>
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

interface NstLike {
    function burn(address,uint256) external;
    function mint(address,uint256) external;
}

interface VatLike {
    function move(address,address,uint256) external;
}

contract NstJoin {
    VatLike public immutable vat;  // CDP Engine
    NstLike public immutable nst;  // Stablecoin Token

    uint256 constant RAY = 10 ** 27;

    // --- Events ---
    event Join(address indexed caller, address indexed usr, uint256 wad);
    event Exit(address indexed caller, address indexed usr, uint256 wad);

    constructor(address vat_, address nst_) {
        vat = VatLike(vat_);
        nst = NstLike(nst_);
    }

    function join(address usr, uint256 wad) external {
        vat.move(address(this), usr, RAY * wad);
        nst.burn(msg.sender, wad);
        emit Join(msg.sender, usr, wad);
    }

    function exit(address usr, uint256 wad) external {
        vat.move(msg.sender, address(this), RAY * wad);
        nst.mint(usr, wad);
        emit Exit(msg.sender, usr, wad);
    }

    // To fully cover daiJoin abi
    function dai() external view returns (address) {
        return address(nst);
    }
}
