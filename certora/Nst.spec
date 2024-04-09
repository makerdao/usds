// Nst.spec

using Auxiliar as aux;
using SignerMock as signer;

methods {
    function wards(address) external returns (uint256) envfree;
    function name() external returns (string) envfree;
    function symbol() external returns (string) envfree;
    function version() external returns (string) envfree;
    function decimals() external returns (uint8) envfree;
    function totalSupply() external returns (uint256) envfree;
    function balanceOf(address) external returns (uint256) envfree;
    function allowance(address, address) external returns (uint256) envfree;
    function nonces(address) external returns (uint256) envfree;
    function deploymentChainId() external returns (uint256) envfree;
    function DOMAIN_SEPARATOR() external returns (bytes32) envfree;
    function PERMIT_TYPEHASH() external returns (bytes32) envfree;
    function aux.call_ecrecover(bytes32, uint8, bytes32, bytes32) external returns (address) envfree;
    function aux.computeDigestForToken(bytes32, bytes32, address, address, uint256, uint256, uint256) external returns (bytes32) envfree;
    function aux.signatureToVRS(bytes) external returns (uint8, bytes32, bytes32) envfree;
    function aux.VRSToSignature(uint8, bytes32, bytes32) external returns (bytes) envfree;
    function aux.size(bytes) external returns (uint256) envfree;
    function _.isValidSignature(bytes32, bytes) external => DISPATCHER(true);
}

ghost balanceSum() returns mathint {
    init_state axiom balanceSum() == 0;
}

hook Sstore balanceOf[KEY address a] uint256 balance (uint256 old_balance) {
    havoc balanceSum assuming balanceSum@new() == balanceSum@old() + balance - old_balance && balanceSum@new() >= 0;
}

invariant balanceSum_equals_totalSupply() balanceSum() == to_mathint(totalSupply());

// Verify correct storage changes for non reverting rely
rule rely(address usr) {
    env e;

    address other;
    require other != usr;
    address anyUsr; address anyUsr2;

    mathint wardsOtherBefore = wards(other);
    mathint totalSupplyBefore = totalSupply();
    mathint balanceOfBefore = balanceOf(anyUsr);
    mathint allowanceBefore = allowance(anyUsr, anyUsr2);
    mathint noncesBefore = nonces(anyUsr);

    rely(e, usr);

    mathint wardsUsrAfter = wards(usr);
    mathint wardsOtherAfter = wards(other);
    mathint totalSupplyAfter = totalSupply();
    mathint balanceOfAfter = balanceOf(anyUsr);
    mathint allowanceAfter = allowance(anyUsr, anyUsr2);
    mathint noncesAfter = nonces(anyUsr);

    assert wardsUsrAfter == 1, "rely did not set the wards";
    assert wardsOtherAfter == wardsOtherBefore, "rely did not keep unchanged the rest of wards[x]";
    assert totalSupplyAfter == totalSupplyBefore, "rely did not keep unchanged totalSupply";
    assert balanceOfAfter == balanceOfBefore, "rely did not keep unchanged every balanceOf[x]";
    assert allowanceAfter == allowanceBefore, "rely did not keep unchanged every allowance[x][y]";
    assert noncesAfter == noncesBefore, "rely did not keep unchanged every nonces[x]";
}

// Verify revert rules on rely
rule rely_revert(address usr) {
    env e;

    mathint wardsSender = wards(e.msg.sender);

    rely@withrevert(e, usr);

    bool revert1 = e.msg.value > 0;
    bool revert2 = wardsSender != 1;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert lastReverted => revert1 || revert2, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting deny
rule deny(address usr) {
    env e;

    address other;
    require other != usr;
    address anyUsr; address anyUsr2;

    mathint wardsOtherBefore = wards(other);
    mathint totalSupplyBefore = totalSupply();
    mathint balanceOfBefore = balanceOf(anyUsr);
    mathint allowanceBefore = allowance(anyUsr, anyUsr2);
    mathint noncesBefore = nonces(anyUsr);

    deny(e, usr);

    mathint wardsUsrAfter = wards(usr);
    mathint wardsOtherAfter = wards(other);
    mathint totalSupplyAfter = totalSupply();
    mathint balanceOfAfter = balanceOf(anyUsr);
    mathint allowanceAfter = allowance(anyUsr, anyUsr2);
    mathint noncesAfter = nonces(anyUsr);

    assert wardsUsrAfter == 0, "deny did not set the wards";
    assert wardsOtherAfter == wardsOtherBefore, "deny did not keep unchanged the rest of wards[x]";
    assert totalSupplyAfter == totalSupplyBefore, "deny did not keep unchanged totalSupply";
    assert balanceOfAfter == balanceOfBefore, "deny did not keep unchanged every balanceOf[x]";
    assert allowanceAfter == allowanceBefore, "deny did not keep unchanged every allowance[x][y]";
    assert noncesAfter == noncesBefore, "deny did not keep unchanged every nonces[x]";
}

// Verify revert rules on deny
rule deny_revert(address usr) {
    env e;

    mathint wardsSender = wards(e.msg.sender);

    deny@withrevert(e, usr);

    bool revert1 = e.msg.value > 0;
    bool revert2 = wardsSender != 1;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert lastReverted => revert1 || revert2, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting transfer
rule transfer(address to, uint256 value) {
    env e;

    requireInvariant balanceSum_equals_totalSupply();

    address other;
    require other != e.msg.sender && other != to;
    address anyUsr; address anyUsr2;

    mathint wardsBefore = wards(anyUsr);
    mathint totalSupplyBefore = totalSupply();
    mathint balanceOfSenderBefore = balanceOf(e.msg.sender);
    mathint balanceOfToBefore = balanceOf(to);
    mathint balanceOfOtherBefore = balanceOf(other);
    mathint allowanceBefore = allowance(anyUsr, anyUsr2);
    mathint noncesBefore = nonces(anyUsr);

    transfer(e, to, value);

    mathint wardsAfter = wards(anyUsr);
    mathint totalSupplyAfter = totalSupply();
    mathint balanceOfSenderAfter = balanceOf(e.msg.sender);
    mathint balanceOfToAfter = balanceOf(to);
    mathint balanceOfOtherAfter = balanceOf(other);
    mathint allowanceAfter = allowance(anyUsr, anyUsr2);
    mathint noncesAfter = nonces(anyUsr);

    assert wardsAfter == wardsBefore, "transfer did not keep unchanged wards";
    assert totalSupplyAfter == totalSupplyBefore, "transfer did not keep unchanged totalSupply";
    assert e.msg.sender != to => balanceOfSenderAfter == balanceOfSenderBefore - value, "transfer did not decrease balanceOf[sender] by value";
    assert e.msg.sender != to => balanceOfToAfter == balanceOfToBefore + value, "transfer did not increase balanceOf[to] by value";
    assert e.msg.sender == to => balanceOfSenderAfter == balanceOfSenderBefore, "transfer did not keep unchanged balanceOf[sender == to]";
    assert balanceOfOtherAfter == balanceOfOtherBefore, "transfer did not keep unchanged the rest of balanceOf[x]";
    assert allowanceAfter == allowanceBefore, "transfer did not keep unchanged every allowance[x][y]";
    assert noncesAfter == noncesBefore, "transfer did not keep unchanged every nonces[x]";
}

// Verify revert rules on transfer
rule transfer_revert(address to, uint256 value) {
    env e;

    mathint balanceOfSender = balanceOf(e.msg.sender);

    transfer@withrevert(e, to, value);

    bool revert1 = e.msg.value > 0;
    bool revert2 = to == 0 || to == currentContract;
    bool revert3 = balanceOfSender < to_mathint(value);

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert lastReverted => revert1 || revert2 || revert3, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting transferFrom
rule transferFrom(address from, address to, uint256 value) {
    env e;

    requireInvariant balanceSum_equals_totalSupply();

    address other;
    require other != from && other != to;
    address other2; address other3;
    require other2 != from || other3 != e.msg.sender;
    address anyUsr; address anyUsr2;

    mathint wardsBefore = wards(anyUsr);
    mathint totalSupplyBefore = totalSupply();
    mathint balanceOfFromBefore = balanceOf(from);
    mathint balanceOfToBefore = balanceOf(to);
    mathint balanceOfOtherBefore = balanceOf(other);
    mathint allowanceFromSenderBefore = allowance(from, e.msg.sender);
    mathint allowanceOtherBefore = allowance(other2, other3);
    mathint noncesBefore = nonces(anyUsr);

    transferFrom(e, from, to, value);

    mathint wardsAfter = wards(anyUsr);
    mathint totalSupplyAfter = totalSupply();
    mathint balanceOfFromAfter = balanceOf(from);
    mathint balanceOfToAfter = balanceOf(to);
    mathint balanceOfOtherAfter = balanceOf(other);
    mathint allowanceFromSenderAfter = allowance(from, e.msg.sender);
    mathint allowanceOtherAfter = allowance(other2, other3);
    mathint noncesAfter = nonces(anyUsr);

    assert wardsAfter == wardsBefore, "transferFrom did not keep unchanged wards";
    assert totalSupplyAfter == totalSupplyBefore, "transferFrom did not keep unchanged totalSupply";
    assert from != to => balanceOfFromAfter == balanceOfFromBefore - value, "transferFrom did not decrease balanceOf[from] by value";
    assert from != to => balanceOfToAfter == balanceOfToBefore + value, "transferFrom did not increase balanceOf[to] by value";
    assert from == to => balanceOfFromAfter == balanceOfFromBefore, "transferFrom did not keep unchanged balanceOf[from == to]";
    assert balanceOfOtherAfter == balanceOfOtherBefore, "transferFrom did not keep unchanged the rest of balanceOf[x]";
    assert e.msg.sender != from && allowanceFromSenderBefore != max_uint256 => allowanceFromSenderAfter == allowanceFromSenderBefore - value, "transferFrom did not decrease allowance[from][sender] by value";
    assert e.msg.sender == from => allowanceFromSenderAfter == allowanceFromSenderBefore, "transferFrom did not keep unchanged allowance[from][sender] when from == sender";
    assert allowanceFromSenderBefore == max_uint256 => allowanceFromSenderAfter == allowanceFromSenderBefore, "transferFrom did not keep unchanged allowance[from][sender] when is max_uint256";
    assert allowanceOtherAfter == allowanceOtherBefore, "transferFrom did not keep unchanged the rest of allowance[x][y]";
    assert noncesAfter == noncesBefore, "transferFrom did not keep unchanged every nonces[x]";
}

// Verify revert rules on transferFrom
rule transferFrom_revert(address from, address to, uint256 value) {
    env e;

    mathint balanceOfFrom = balanceOf(from);
    mathint allowanceFromSender = allowance(from, e.msg.sender);

    transferFrom@withrevert(e, from, to, value);

    bool revert1 = e.msg.value > 0;
    bool revert2 = to == 0 || to == currentContract;
    bool revert3 = balanceOfFrom < to_mathint(value);
    bool revert4 = allowanceFromSender < to_mathint(value) && e.msg.sender != from;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert revert4 => lastReverted, "revert4 failed";
    assert lastReverted => revert1 || revert2 || revert3 || revert4, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting approve
rule approve(address spender, uint256 value) {
    env e;

    address anyUsr;
    address anyUsr2; address anyUsr3;
    require anyUsr2 != e.msg.sender || anyUsr3 != spender;

    mathint wardsBefore = wards(anyUsr);
    mathint totalSupplyBefore = totalSupply();
    mathint balanceOfBefore = balanceOf(anyUsr);
    mathint allowanceOtherBefore = allowance(anyUsr2, anyUsr3);
    mathint noncesBefore = nonces(anyUsr);

    approve(e, spender, value);

    mathint wardsAfter = wards(anyUsr);
    mathint totalSupplyAfter = totalSupply();
    mathint balanceOfAfter = balanceOf(anyUsr);
    mathint allowanceSenderSpenderAfter = allowance(e.msg.sender, spender);
    mathint allowanceOtherAfter = allowance(anyUsr2, anyUsr3);
    mathint noncesAfter = nonces(anyUsr);

    assert wardsAfter == wardsBefore, "approve did not keep unchanged wards";
    assert totalSupplyAfter == totalSupplyBefore, "approve did not keep unchanged totalSupply";
    assert balanceOfAfter == balanceOfBefore, "approve did not keep unchanged every balanceOf[x]";
    assert allowanceSenderSpenderAfter == to_mathint(value), "approve did not set allowance[sender][spender] to value";
    assert allowanceOtherAfter == allowanceOtherBefore, "approve did not keep unchanged the rest of allowance[x][y]";
    assert noncesAfter == noncesBefore, "approve did not keep unchanged every nonces[x]";
}

// Verify revert rules on approve
rule approve_revert(address spender, uint256 value) {
    env e;

    approve@withrevert(e, spender, value);

    bool revert1 = e.msg.value > 0;

    assert revert1 => lastReverted, "revert1 failed";
    assert lastReverted => revert1, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting mint
rule mint(address to, uint256 value) {
    env e;

    requireInvariant balanceSum_equals_totalSupply();

    address other;
    require other != to;
    address anyUsr; address anyUsr2;

    bool senderSameAsTo = e.msg.sender == to;

    mathint wardsBefore = wards(anyUsr);
    mathint totalSupplyBefore = totalSupply();
    mathint balanceOfToBefore = balanceOf(to);
    mathint balanceOfOtherBefore = balanceOf(other);
    mathint allowanceBefore = allowance(anyUsr, anyUsr2);
    mathint noncesBefore = nonces(anyUsr);

    mint(e, to, value);

    mathint wardsAfter = wards(anyUsr);
    mathint totalSupplyAfter = totalSupply();
    mathint balanceOfToAfter = balanceOf(to);
    mathint balanceOfOtherAfter = balanceOf(other);
    mathint allowanceAfter = allowance(anyUsr, anyUsr2);
    mathint noncesAfter = nonces(anyUsr);

    assert wardsAfter == wardsBefore, "mint did not keep unchanged wards";
    assert totalSupplyAfter == totalSupplyBefore + value, "mint did not increase totalSupply by value";
    assert balanceOfToAfter == balanceOfToBefore + value, "mint did not increase balanceOf[to] by value";
    assert balanceOfOtherAfter == balanceOfOtherBefore, "mint did not keep unchanged the rest of balanceOf[x]";
    assert allowanceAfter == allowanceBefore, "mint did not keep unchanged every allowance[x][y]";
    assert noncesAfter == noncesBefore, "mint did not keep unchanged every nonces[x]";
}

// Verify revert rules on mint
rule mint_revert(address to, uint256 value) {
    env e;

    // Save the totalSupply and sender balance before minting
    mathint totalSupply = totalSupply();
    mathint wardsSender = wards(e.msg.sender);

    mint@withrevert(e, to, value);

    bool revert1 = e.msg.value > 0;
    bool revert2 = wardsSender != 1;
    bool revert3 = totalSupply + value > max_uint256;
    bool revert4 = to == 0 || to == currentContract;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert revert4 => lastReverted, "revert4 failed";
    assert lastReverted => revert1 || revert2 || revert3 || revert4, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting burn
rule burn(address from, uint256 value) {
    env e;

    requireInvariant balanceSum_equals_totalSupply();

    address other;
    require other != from;
    address anyUsr; address anyUsr2;
    require anyUsr != from || anyUsr2 != e.msg.sender;

    mathint wardsBefore = wards(anyUsr);
    mathint totalSupplyBefore = totalSupply();
    mathint balanceOfFromBefore = balanceOf(from);
    mathint balanceOfOtherBefore = balanceOf(other);
    mathint allowanceFromSenderBefore = allowance(from, e.msg.sender);
    mathint allowanceOtherBefore = allowance(anyUsr, anyUsr2);
    mathint noncesBefore = nonces(anyUsr);

    burn(e, from, value);

    mathint wardsAfter = wards(anyUsr);
    mathint totalSupplyAfter = totalSupply();
    mathint balanceOfSenderAfter = balanceOf(e.msg.sender);
    mathint balanceOfFromAfter = balanceOf(from);
    mathint balanceOfOtherAfter = balanceOf(other);
    mathint allowanceFromSenderAfter = allowance(from, e.msg.sender);
    mathint allowanceOtherAfter = allowance(anyUsr, anyUsr2);
    mathint noncesAfter = nonces(anyUsr);

    assert wardsAfter == wardsBefore, "burn did not keep unchanged wards";
    assert totalSupplyAfter == totalSupplyBefore - value, "burn did not decrease totalSupply by value";
    assert balanceOfFromAfter == balanceOfFromBefore - value, "burn did not decrease balanceOf[from] by value";
    assert balanceOfOtherAfter == balanceOfOtherBefore, "burn did not keep unchanged the rest of balanceOf[x]";
    assert e.msg.sender != from && allowanceFromSenderBefore != max_uint256 => allowanceFromSenderAfter == allowanceFromSenderBefore - value, "burn did not decrease allowance[from][sender] by value";
    assert e.msg.sender == from => allowanceFromSenderAfter == allowanceFromSenderBefore, "burn did not keep unchanged allowance[from][sender] when from == sender";
    assert allowanceFromSenderBefore == max_uint256 => allowanceFromSenderAfter == allowanceFromSenderBefore, "burn did not keep unchanged allowance[from][sender] when is max_uint256";
    assert allowanceOtherAfter == allowanceOtherBefore, "burn did not keep unchanged the rest of allowance[x][y]";
    assert noncesAfter == noncesBefore, "burn did not keep unchanged every nonces[x]";
}

// Verify revert rules on burn
rule burn_revert(address from, uint256 value) {
    env e;

    mathint balanceOfFrom = balanceOf(from);
    mathint allowanceFromSender = allowance(from, e.msg.sender);

    burn@withrevert(e, from, value);

    bool revert1 = e.msg.value > 0;
    bool revert2 = balanceOfFrom < to_mathint(value);
    bool revert3 = from != e.msg.sender && allowanceFromSender < to_mathint(value);

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert lastReverted => revert1 || revert2 || revert3, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting permit
rule permitVRS(address owner, address spender, uint256 value, uint256 deadline, uint8 v, bytes32 r, bytes32 s) {
    env e;

    address anyUsr;
    address anyUsr2; address anyUsr3;
    require anyUsr2 != owner || anyUsr3 != spender;
    address other;
    require other != owner;

    mathint wardsBefore = wards(anyUsr);
    mathint totalSupplyBefore = totalSupply();
    mathint balanceOfBefore = balanceOf(anyUsr);
    mathint allowanceOtherBefore = allowance(anyUsr2, anyUsr3);
    mathint noncesOwnerBefore = nonces(owner);
    mathint noncesOtherBefore = nonces(other);

    permit(e, owner, spender, value, deadline, v, r, s);

    mathint wardsAfter = wards(anyUsr);
    mathint totalSupplyAfter = totalSupply();
    mathint balanceOfAfter = balanceOf(anyUsr);
    mathint allowanceOwnerSpenderAfter = allowance(owner, spender);
    mathint allowanceOtherAfter = allowance(anyUsr2, anyUsr3);
    mathint noncesOwnerAfter = nonces(owner);
    mathint noncesOtherAfter = nonces(other);

    assert wardsAfter == wardsBefore, "permit did not keep unchanged wards";
    assert totalSupplyAfter == totalSupplyBefore, "permit did not keep unchanged totalSupply";
    assert balanceOfAfter == balanceOfBefore, "permit did not keep unchanged every balanceOf[x]";
    assert allowanceOwnerSpenderAfter == to_mathint(value), "permit did not set allowance[owner][spender] to value";
    assert allowanceOtherAfter == allowanceOtherBefore, "permit did not keep unchanged the rest of allowance[x][y]";
    assert noncesOwnerBefore < max_uint256 => noncesOwnerAfter == noncesOwnerBefore + 1, "permit did not increase nonces[owner] by 1";
    assert noncesOwnerBefore == max_uint256 => noncesOwnerAfter == 0, "permit did not set nonces[owner] back to 0";
    assert noncesOtherAfter == noncesOtherBefore, "permit did not keep unchanged the rest of nonces[x]";
}

// Verify revert rules on permit
rule permitVRS_revert(address owner, address spender, uint256 value, uint256 deadline, uint8 v, bytes32 r, bytes32 s) {
    env e;

    bytes32 digest = aux.computeDigestForToken(
                        DOMAIN_SEPARATOR(),
                        PERMIT_TYPEHASH(),
                        owner,
                        spender,
                        value,
                        nonces(owner),
                        deadline
                    );
    address ownerRecover = aux.call_ecrecover(digest, v, r, s);
    bytes32 returnedSig = owner == signer ? signer.isValidSignature(e, digest, aux.VRSToSignature(v, r, s)) : to_bytes32(0);

    permit@withrevert(e, owner, spender, value, deadline, v, r, s);

    bool revert1 = e.msg.value > 0;
    bool revert2 = e.block.timestamp > deadline;
    bool revert3 = owner == 0;
    bool revert4 = owner != ownerRecover && returnedSig != to_bytes32(0x1626ba7e00000000000000000000000000000000000000000000000000000000);

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert revert4 => lastReverted, "revert4 failed";

    assert lastReverted => revert1 || revert2 || revert3 ||
                           revert4, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting permit
rule permitSignature(address owner, address spender, uint256 value, uint256 deadline, bytes signature) {
    env e;

    address anyUsr;
    address anyUsr2; address anyUsr3;
    require anyUsr2 != owner || anyUsr3 != spender;
    address other;
    require other != owner;

    mathint wardsBefore = wards(anyUsr);
    mathint totalSupplyBefore = totalSupply();
    mathint balanceOfBefore = balanceOf(anyUsr);
    mathint allowanceOtherBefore = allowance(anyUsr2, anyUsr3);
    mathint noncesOwnerBefore = nonces(owner);
    mathint noncesOtherBefore = nonces(other);

    permit(e, owner, spender, value, deadline, signature);

    mathint wardsAfter = wards(anyUsr);
    mathint totalSupplyAfter = totalSupply();
    mathint balanceOfAfter = balanceOf(anyUsr);
    mathint allowanceOwnerSpenderAfter = allowance(owner, spender);
    mathint allowanceOtherAfter = allowance(anyUsr2, anyUsr3);
    mathint noncesOwnerAfter = nonces(owner);
    mathint noncesOtherAfter = nonces(other);

    assert wardsAfter == wardsBefore, "permit did not keep unchanged wards";
    assert totalSupplyAfter == totalSupplyBefore, "permit did not keep unchanged totalSupply";
    assert balanceOfAfter == balanceOfBefore, "permit did not keep unchanged every balanceOf[x]";
    assert allowanceOwnerSpenderAfter == to_mathint(value), "permit did not set allowance[owner][spender] to value";
    assert allowanceOtherAfter == allowanceOtherBefore, "permit did not keep unchanged the rest of allowance[x][y]";
    assert noncesOwnerBefore < max_uint256 => noncesOwnerAfter == noncesOwnerBefore + 1, "permit did not increase nonces[owner] by 1";
    assert noncesOwnerBefore == max_uint256 => noncesOwnerAfter == 0, "permit did not set nonces[owner] back to 0";
    assert noncesOtherAfter == noncesOtherBefore, "permit did not keep unchanged the rest of nonces[x]";
}

// Verify revert rules on permit
rule permitSignature_revert(address owner, address spender, uint256 value, uint256 deadline, bytes signature) {
    env e;

    bytes32 digest = aux.computeDigestForToken(
                        DOMAIN_SEPARATOR(),
                        PERMIT_TYPEHASH(),
                        owner,
                        spender,
                        value,
                        nonces(owner),
                        deadline
                    );
    uint8 v; bytes32 r; bytes32 s;
    v, r, s = aux.signatureToVRS(signature);
    address null_address = 0;
    address ownerRecover = aux.size(signature) == 65 ? aux.call_ecrecover(digest, v, r, s) : null_address;
    bytes32 returnedSig = owner == signer ? signer.isValidSignature(e, digest, signature) : to_bytes32(0);

    permit@withrevert(e, owner, spender, value, deadline, signature);

    bool revert1 = e.msg.value > 0;
    bool revert2 = e.block.timestamp > deadline;
    bool revert3 = owner == 0;
    bool revert4 = owner != ownerRecover && returnedSig != to_bytes32(0x1626ba7e00000000000000000000000000000000000000000000000000000000);

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert revert4 => lastReverted, "revert4 failed";

    assert lastReverted => revert1 || revert2 || revert3 ||
                           revert4, "Revert rules are not covering all the cases";
}
