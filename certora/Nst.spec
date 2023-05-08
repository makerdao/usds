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
    function aux.size(bytes) external returns (uint256) envfree;
    function _.isValidSignature(bytes32, bytes) external => DISPATCHER(true);
}

ghost balanceSum() returns mathint {
    init_state axiom balanceSum() == 0;
}

hook Sstore balanceOf[KEY address a] uint256 balance (uint256 old_balance) STORAGE {
    havoc balanceSum assuming balanceSum@new() == balanceSum@old() + balance - old_balance && balanceSum@new() >= 0;
}

invariant balanceSum_equals_totalSupply() balanceSum() == to_mathint(totalSupply());

// Verify correct storage changes for non reverting rely
rule rely(address usr) {
    env e;

    address other;
    require(other != usr);
    address anyUsr; address anyUsr2;

    mathint wardsOtherBefore = wards(other);
    mathint totalSupplyBefore = totalSupply();
    mathint balanceOfBefore = balanceOf(anyUsr);
    mathint allowanceBefore = allowance(anyUsr, anyUsr2);
    mathint noncesBefore = nonces(anyUsr);

    rely(e, usr);

    mathint wardsAfter = wards(usr);
    mathint wardsOtherAfter = wards(other);
    mathint totalSupplyAfter = totalSupply();
    mathint balanceOfAfter = balanceOf(anyUsr);
    mathint allowanceAfter = allowance(anyUsr, anyUsr2);
    mathint noncesAfter = nonces(anyUsr);

    assert wardsAfter == 1, "rely did not set the wards";
    assert wardsOtherAfter == wardsOtherBefore, "rely did not keep unchanged the rest of wards[x]";
    assert totalSupplyAfter == totalSupplyBefore, "rely did not keep unchanged totalSupply";
    assert balanceOfAfter == balanceOfBefore, "rely did not keep unchanged every balanceOf[x]";
    assert allowanceAfter == allowanceBefore, "rely did not keep unchanged every allowance[x][y]";
    assert noncesAfter == noncesBefore, "rely did not keep unchanged every nonces[x]";
}

// Verify revert rules on rely
rule rely_revert(address usr) {
    env e;

    mathint ward = wards(e.msg.sender);

    rely@withrevert(e, usr);

    bool revert1 = e.msg.value > 0;
    bool revert2 = ward != 1;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert lastReverted => revert1 || revert2, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting deny
rule deny(address usr) {
    env e;

    address other;
    require(other != usr);
    address anyUsr; address anyUsr2;

    mathint wardsOtherBefore = wards(other);
    mathint totalSupplyBefore = totalSupply();
    mathint balanceOfBefore = balanceOf(anyUsr);
    mathint allowanceBefore = allowance(anyUsr, anyUsr2);
    mathint noncesBefore = nonces(anyUsr);

    deny(e, usr);

    mathint wardsAfter = wards(usr);
    mathint wardsOtherAfter = wards(other);
    mathint totalSupplyAfter = totalSupply();
    mathint balanceOfAfter = balanceOf(anyUsr);
    mathint allowanceAfter = allowance(anyUsr, anyUsr2);
    mathint noncesAfter = nonces(anyUsr);

    assert wardsAfter == 0, "deny did not set the wards";
    assert wardsOtherAfter == wardsOtherBefore, "deny did not keep unchanged the rest of wards[x]";
    assert totalSupplyAfter == totalSupplyBefore, "deny did not keep unchanged totalSupply";
    assert balanceOfAfter == balanceOfBefore, "deny did not keep unchanged every balanceOf[x]";
    assert allowanceAfter == allowanceBefore, "deny did not keep unchanged every allowance[x][y]";
    assert noncesAfter == noncesBefore, "deny did not keep unchanged every nonces[x]";
}

// Verify revert rules on deny
rule deny_revert(address usr) {
    env e;

    mathint ward = wards(e.msg.sender);

    deny@withrevert(e, usr);

    bool revert1 = e.msg.value > 0;
    bool revert2 = ward != 1;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert lastReverted => revert1 || revert2, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting transfer
rule transfer(address to, uint256 value) {
    env e;

    requireInvariant balanceSum_equals_totalSupply();

    address other;
    require(other != e.msg.sender && other != to);
    address anyUsr; address anyUsr2;

    bool senderSameAsTo = e.msg.sender == to;

    mathint wardsBefore = wards(anyUsr);
    mathint totalSupplyBefore = totalSupply();
    mathint balanceOfSenderBefore = balanceOf(e.msg.sender);
    mathint balanceOfToBefore = balanceOf(to);
    mathint balanceOfOtherBefore = balanceOf(other);
    mathint allowanceBefore = allowance(anyUsr, anyUsr2);
    mathint noncesBefore = nonces(anyUsr);

    transfer(e, to, value);

    mathint wardsAfter = wards(anyUsr);
    mathint wardsOtherAfter = wards(other);
    mathint totalSupplyAfter = totalSupply();
    mathint balanceOfSenderAfter = balanceOf(e.msg.sender);
    mathint balanceOfToAfter = balanceOf(to);
    mathint balanceOfOtherAfter = balanceOf(other);
    mathint allowanceAfter = allowance(anyUsr, anyUsr2);
    mathint noncesAfter = nonces(anyUsr);

    assert wardsAfter == wardsBefore, "transfer did not keep unchanged wards";
    assert totalSupplyAfter == totalSupplyBefore, "transfer did not keep unchanged totalSupply";
    assert !senderSameAsTo => balanceOfSenderAfter == balanceOfSenderBefore - value, "transfer did not change balance of sender";
    assert !senderSameAsTo => balanceOfToAfter == balanceOfToBefore + value, "transfer did not change balance of to";
    assert senderSameAsTo => balanceOfSenderAfter == balanceOfSenderBefore, "transfer did not keep unchanged the balance when sender == to";
    assert balanceOfOtherAfter == balanceOfOtherBefore, "transfer did not keep unchanged the rest of balanceOf[x]";
    assert allowanceAfter == allowanceBefore, "transfer did not keep unchanged every allowance[x][y]";
    assert noncesAfter == noncesBefore, "transfer did not keep unchanged every nonces[x]";
}

// Verify revert rules on transfer
rule transfer_revert(address to, uint256 value) {
    env e;

    mathint senderBalance = balanceOf(e.msg.sender);

    transfer@withrevert(e, to, value);

    bool revert1 = e.msg.value > 0;
    bool revert2 = to == 0 || to == currentContract;
    bool revert3 = senderBalance < to_mathint(value);

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
    require(other != from && other != to);
    address other2; address other3;
    require(other2 != from || other3 != e.msg.sender);
    address anyUsr; address anyUsr2;

    bool fromSameAsTo = from == to;
    mathint wardsBefore = wards(anyUsr);
    mathint totalSupplyBefore = totalSupply();
    mathint balanceOfFromBefore = balanceOf(from);
    mathint balanceOfToBefore = balanceOf(to);
    mathint balanceOfOtherBefore = balanceOf(other);
    mathint allowanceBefore = allowance(from, e.msg.sender);
    mathint allowanceOtherBefore = allowance(other2, other3);
    mathint noncesBefore = nonces(anyUsr);

    bool deductAllowance = e.msg.sender != from && allowanceBefore != max_uint256;

    transferFrom(e, from, to, value);

    mathint wardsAfter = wards(anyUsr);
    mathint wardsOtherAfter = wards(other);
    mathint totalSupplyAfter = totalSupply();
    mathint balanceOfFromAfter = balanceOf(from);
    mathint balanceOfToAfter = balanceOf(to);
    mathint balanceOfOtherAfter = balanceOf(other);
    mathint allowanceAfter = allowance(from, e.msg.sender);
    mathint allowanceOtherAfter = allowance(other2, other3);
    mathint noncesAfter = nonces(anyUsr);

    assert wardsAfter == wardsBefore, "transferFrom did not keep unchanged wards";
    assert totalSupplyAfter == totalSupplyBefore, "transferFrom did not keep unchanged totalSupply";
    assert !fromSameAsTo => balanceOfFromAfter == balanceOfFromBefore - value, "transferFrom did not change balance of from";
    assert !fromSameAsTo => balanceOfToAfter == balanceOfToBefore + value, "transferFrom did not change balance of to";
    assert fromSameAsTo => balanceOfFromAfter == balanceOfFromBefore, "transferFrom did not keep unchanged balance when from == to";
    assert balanceOfOtherAfter == balanceOfOtherBefore, "transferFrom did not keep unchanged the rest of balanceOf[x]";
    assert deductAllowance => allowanceAfter == allowanceBefore - value, "transferFrom did not decrease allowance";
    assert !deductAllowance => allowanceAfter == allowanceBefore, "transferFrom did not keep unchanged allowance when sender == from";
    assert allowanceOtherAfter == allowanceOtherBefore, "transferFrom did not keep unchanged the rest of allowance[x][y]";
    assert noncesAfter == noncesBefore, "transferFrom did not keep unchanged every nonces[x]";
}

// Verify revert rules on transferFrom
rule transferFrom_revert(address from, address to, uint256 value) {
    env e;

    mathint fromBalance = balanceOf(from);
    mathint allowed = allowance(from, e.msg.sender);

    transferFrom@withrevert(e, from, to, value);

    bool revert1 = e.msg.value > 0;
    bool revert2 = to == 0 || to == currentContract;
    bool revert3 = fromBalance < to_mathint(value);
    bool revert4 = allowed < to_mathint(value) && e.msg.sender != from;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert revert4 => lastReverted, "revert4 failed";
    assert lastReverted => revert1 || revert2 || revert3 || revert4, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting approve
rule approve(address spender, uint256 value) {
    env e;

    approve(e, spender, value);

    assert allowance(e.msg.sender, spender) == value, "approve did not set the allowance as expected";
}

// Verify revert rules on approve
rule approve_revert(address spender, uint256 value) {
    env e;

    approve@withrevert(e, spender, value);

    bool revert1 = e.msg.value > 0;

    assert revert1 => lastReverted, "revert1 failed";
    assert lastReverted => revert1, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting increaseAllowance
rule increaseAllowance(address spender, uint256 value) {
    env e;

    mathint spenderAllowance = allowance(e.msg.sender, spender);

    increaseAllowance(e, spender, value);

    assert to_mathint(allowance(e.msg.sender, spender)) == spenderAllowance + value, "increaseAllowance did not increase the allowance as expected";
}

// Verify revert rules on increaseAllowance
rule increaseAllowance_revert(address spender, uint256 value) {
    env e;

    mathint spenderAllowance = allowance(e.msg.sender, spender);

    increaseAllowance@withrevert(e, spender, value);

    bool revert1 = e.msg.value > 0;
    bool revert2 = spenderAllowance + value > max_uint256;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert lastReverted => revert1 || revert2, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting decreaseAllowance
rule decreaseAllowance(address spender, uint256 value) {
    env e;

    mathint spenderAllowance = allowance(e.msg.sender, spender);

    decreaseAllowance(e, spender, value);

    assert to_mathint(allowance(e.msg.sender, spender)) == spenderAllowance - value, "decreaseAllowance did not decrease the allowance as expected";
}

// Verify revert rules on decreaseAllowance
rule decreaseAllowance_revert(address spender, uint256 value) {
    env e;

    mathint spenderAllowance = allowance(e.msg.sender, spender);

    decreaseAllowance@withrevert(e, spender, value);

    bool revert1 = e.msg.value > 0;
    bool revert2 = spenderAllowance - value < 0;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert lastReverted => revert1 || revert2, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting mint
rule mint(address to, uint256 value) {
    env e;

    requireInvariant balanceSum_equals_totalSupply();

    // Save the totalSupply and sender balance before minting
    mathint supply = totalSupply();
    mathint toBalance = balanceOf(to);

    mint(e, to, value);

    assert to_mathint(balanceOf(to)) == toBalance + value, "mint did not increase the balance as expected";
    assert to_mathint(totalSupply()) == supply + value, "mint did not increase the supply as expected";
}

// Verify revert rules on mint
rule mint_revert(address to, uint256 value) {
    env e;

    // Save the totalSupply and sender balance before minting
    mathint supply = totalSupply();
    mathint ward = wards(e.msg.sender);

    mint@withrevert(e, to, value);

    bool revert1 = e.msg.value > 0;
    bool revert2 = ward != 1;
    bool revert3 = supply + value > max_uint256;
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

    mathint supply = totalSupply();
    mathint fromBalance = balanceOf(from);
    mathint allowed = allowance(from, e.msg.sender);
    mathint ward = wards(e.msg.sender);
    bool senderSameAsFrom = e.msg.sender == from;
    bool allowedEqMaxUint = allowed == max_uint256;

    burn(e, from, value);

    assert !senderSameAsFrom && !allowedEqMaxUint => to_mathint(allowance(from, e.msg.sender)) == allowed - value, "burn did not decrease the allowance as expected";
    assert senderSameAsFrom || allowedEqMaxUint => to_mathint(allowance(from, e.msg.sender)) == allowed, "burn did not keep the allowance as expected";
    assert to_mathint(balanceOf(from)) == fromBalance - value, "burn did not decrease the balance as expected";
    assert to_mathint(totalSupply()) == supply - value, "burn did not decrease the supply as expected";
}

// Verify revert rules on burn
rule burn_revert(address from, uint256 value) {
    env e;

    mathint supply = totalSupply();
    mathint fromBalance = balanceOf(from);
    mathint allowed = allowance(from, e.msg.sender);

    burn@withrevert(e, from, value);

    bool revert1 = e.msg.value > 0;
    bool revert2 = fromBalance < to_mathint(value);
    bool revert3 = from != e.msg.sender && allowed < to_mathint(value);

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert lastReverted => revert1 || revert2 || revert3, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting permit
rule permitVRS(address owner, address spender, uint256 value, uint256 deadline, uint8 v, bytes32 r, bytes32 s) {
    env e;

    permit(e, owner, spender, value, deadline, v, r, s);

    assert allowance(owner, spender) == value, "permit did not set the allowance as expected";
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

    permit@withrevert(e, owner, spender, value, deadline, v, r, s);

    bool revert1 = e.msg.value > 0;
    bool revert2 = e.block.timestamp > deadline;
    bool revert3 = owner == 0;
    bool revert4 = owner != ownerRecover;

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

    permit(e, owner, spender, value, deadline, signature);

    assert allowance(owner, spender) == value, "permit did not set the allowance as expected";
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
    address ownerRecover = aux.size(signature) == 65 ? aux.call_ecrecover(digest, v, r, s) : 0;
    bytes32 returnedSig = owner == signer ? signer.isValidSignature(e, digest, signature) : 0;

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
