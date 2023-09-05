// SPDX-License-Identifier: AGPL-3.0-or-later

pragma solidity ^0.8.16;

import "token-tests/TokenFuzzTests.sol";

import { Nst } from "src/Nst.sol";

contract NstTest is TokenFuzzTests {
    Nst nst;

    function setUp() public {
        vm.expectEmit(true, true, true, true);
        emit Rely(address(this));
        nst = new Nst();

        _token_ = address(nst);
        _contractName_ = "Nst";
        _tokenName_ ="Nst Stablecoin";
        _symbol_ = "NST";
    }

    function invariantMetadata() public {
        assertEq(nst.name(), "Nst Stablecoin");
        assertEq(nst.symbol(), "NST");
        assertEq(nst.version(), "1");
        assertEq(nst.decimals(), 18);
    }
}
