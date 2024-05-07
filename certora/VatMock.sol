// SPDX-License-Identifier: AGPL-3.0-or-later

/// vat.sol -- Dai CDP database

// Copyright (C) 2018 Rain <rainbreak@riseup.net>
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

contract VatMock {
    mapping (address => uint256) public dai;

    function hope(address) external {
    }

    function move(address src, address dst, uint256 rad) external {
        dai[src] = dai[src] - rad;
        dai[dst] = dai[dst] + rad;
    }
}
