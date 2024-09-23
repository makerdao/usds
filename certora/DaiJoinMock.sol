pragma solidity ^0.8.21;

import "../src/UsdsJoin.sol";

contract DaiJoinMock is UsdsJoin {
    constructor(address vat_, address dai_) UsdsJoin(vat_, dai_) {}
}
