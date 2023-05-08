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

// Verify that wards behaves correctly on rely
rule rely(address usr) {
    env e;

    rely(e, usr);

    assert wards(usr) == 1, "rely did not set the wards as expected";
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

// Verify that wards behaves correctly on deny
rule deny(address usr) {
    env e;

    deny(e, usr);

    assert wards(usr) == 0, "deny did not set the wards as expected";
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

// Verify that balance behaves correctly on transfer
rule transfer(address to, uint256 value) {
    env e;

    requireInvariant balanceSum_equals_totalSupply();

    mathint senderBalanceBefore = balanceOf(e.msg.sender);
    mathint toBalanceBefore = balanceOf(to);
    mathint supplyBefore = totalSupply();
    bool senderSameAsTo = e.msg.sender == to;

    transfer(e, to, value);

    mathint senderBalanceAfter = balanceOf(e.msg.sender);
    mathint toBalanceAfter = balanceOf(to);
    mathint supplyAfter = totalSupply();

    assert supplyAfter == supplyBefore, "supply changed";

    assert !senderSameAsTo =>
            senderBalanceAfter == senderBalanceBefore - value &&
            toBalanceAfter == toBalanceBefore + value,
            "transfer did not change balances as expected"
    ;

    assert senderSameAsTo =>
            senderBalanceAfter == senderBalanceBefore,
            "transfer changed the balance when sender and receiver are the same"
    ;
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

// Verify that balance and allowance behave correctly on transferFrom
rule transferFrom(address from, address to, uint256 value) {
    env e;

    requireInvariant balanceSum_equals_totalSupply();

    mathint fromBalanceBefore = balanceOf(from);
    mathint toBalanceBefore = balanceOf(to);
    mathint supplyBefore = totalSupply();
    mathint allowanceBefore = allowance(from, e.msg.sender);
    bool deductAllowance = e.msg.sender != from && allowanceBefore != max_uint256;
    bool fromSameAsTo = from == to;

    transferFrom(e, from, to, value);

    mathint fromBalanceAfter = balanceOf(from);
    mathint toBalanceAfter = balanceOf(to);
    mathint supplyAfter = totalSupply();
    mathint allowanceAfter = allowance(from, e.msg.sender);

    assert supplyAfter == supplyBefore, "supply changed";
    assert deductAllowance => allowanceAfter == allowanceBefore - value, "allowance did not decrease in value";
    assert !deductAllowance => allowanceAfter == allowanceBefore, "allowance did not remain the same";
    assert !fromSameAsTo => fromBalanceAfter == fromBalanceBefore - value, "transferFrom did not decrease the balance as expected";
    assert !fromSameAsTo => toBalanceAfter == toBalanceBefore + value, "transferFrom did not increase the balance as expected";
    assert fromSameAsTo => fromBalanceAfter == fromBalanceBefore, "transferFrom did not keep the balance the same as expected";
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

// Verify that allowance behaves correctly on approve
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

// Verify that allowance behaves correctly on increaseAllowance
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

// Verify that allowance behaves correctly on decreaseAllowance
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

// Verify that supply and balance behave correctly on mint
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

// Verify that supply and balance behave correctly on burn
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

// Verify that allowance behaves correctly on permit
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
