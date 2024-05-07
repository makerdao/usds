pragma solidity ^0.8.21;

import "../src/NstJoin.sol";

contract DaiJoinMock is NstJoin {
    constructor(address vat_, address dai_) NstJoin(vat_, dai_) {}
}
