// UsdsJoin.spec

using Usds as usds;
using VatMock as vat;

methods {
    function usds.wards(address) external returns (uint256) envfree;
    function usds.totalSupply() external returns (uint256) envfree;
    function usds.balanceOf(address) external returns (uint256) envfree;
    function usds.allowance(address, address) external returns (uint256) envfree;
    function usds.nonces(address) external returns (uint256) envfree;
    function vat.dai(address) external returns (uint256) envfree;
}

definition RAY() returns uint256 = 10^27;

ghost balanceSum() returns mathint {
    init_state axiom balanceSum() == 0;
}

hook Sstore usds.balanceOf[KEY address a] uint256 balance (uint256 old_balance) {
    havoc balanceSum assuming balanceSum@new() == balanceSum@old() + balance - old_balance && balanceSum@new() >= 0;
}

invariant balanceSum_equals_totalSupply() balanceSum() == to_mathint(usds.totalSupply())
            filtered {
                m -> m.selector != sig:Usds.upgradeToAndCall(address, bytes).selector
            }

// Verify correct storage changes for non reverting join
rule join(address usr, uint256 wad) {
    env e;

    require e.msg.sender != currentContract;

    requireInvariant balanceSum_equals_totalSupply();

    address other;
    require other != e.msg.sender;
    address anyUsr;
    address anyUsr2; address anyUsr3;
    require anyUsr2 != e.msg.sender || anyUsr3 != currentContract;

    mathint wardsBefore = usds.wards(anyUsr);
    mathint totalSupplyBefore = usds.totalSupply();
    mathint balanceOfSenderBefore = usds.balanceOf(e.msg.sender);
    mathint balanceOfOtherBefore = usds.balanceOf(other);
    mathint allowanceSenderJoinBefore = usds.allowance(e.msg.sender, currentContract);
    mathint allowanceOtherBefore = usds.allowance(anyUsr2, anyUsr3);
    mathint noncesBefore = usds.nonces(anyUsr);
    mathint vatDaiJoinBefore = vat.dai(currentContract);
    mathint vatDaiUsrBefore = vat.dai(usr);

    join(e, usr, wad);

    mathint wardsAfter = usds.wards(anyUsr);
    mathint totalSupplyAfter = usds.totalSupply();
    mathint balanceOfSenderAfter = usds.balanceOf(e.msg.sender);
    mathint balanceOfOtherAfter = usds.balanceOf(other);
    mathint allowanceSenderJoinAfter = usds.allowance(e.msg.sender, currentContract);
    mathint allowanceOtherAfter = usds.allowance(anyUsr2, anyUsr3);
    mathint noncesAfter = usds.nonces(anyUsr);
    mathint vatDaiJoinAfter = vat.dai(currentContract);
    mathint vatDaiUsrAfter = vat.dai(usr);

    assert wardsAfter == wardsBefore, "join did not keep unchanged usds.wards";
    assert totalSupplyAfter == totalSupplyBefore - wad, "join did not decrease usds.totalSupply by wad";
    assert balanceOfSenderAfter == balanceOfSenderBefore - wad, "join did not decrease usds.balanceOf[sender] by wad";
    assert balanceOfOtherAfter == balanceOfOtherBefore, "join did not keep unchanged the rest of usds.balanceOf[x]";
    assert allowanceSenderJoinBefore != max_uint256 => allowanceSenderJoinAfter == allowanceSenderJoinBefore - wad, "join did not decrease allowance[sender][join]";
    assert allowanceSenderJoinBefore == max_uint256 => allowanceSenderJoinAfter == allowanceSenderJoinBefore, "join did not keep unchaged allowance[sender][join] when is max_uint256";
    assert allowanceOtherAfter == allowanceOtherBefore, "join did not keep unchanged the rest of allowance[x][y]";
    assert noncesAfter == noncesBefore, "join did not keep unchanged every usds.nonces[x]";
    assert usr != currentContract => vatDaiJoinAfter == vatDaiJoinBefore - wad * RAY(), "join did not decrease vat.dai(join) by wad * RAY";
    assert usr != currentContract => vatDaiUsrAfter == vatDaiUsrBefore + wad * RAY(), "join did not increase vat.dai(usr) by wad * RAY";
    assert usr == currentContract => vatDaiUsrAfter == vatDaiUsrBefore, "join did not keep unchanged vat.dai(usr) when usr == join";
}

// Verify revert rules on join
rule join_revert(address usr, uint256 wad) {
    env e;

    require e.msg.sender != currentContract;

    mathint balanceOfSender = usds.balanceOf(e.msg.sender);
    mathint allowanceSenderJoin = usds.allowance(e.msg.sender, currentContract);
    mathint vatDaiUsr = vat.dai(usr);
    mathint vatDaiJoin = vat.dai(currentContract);

    join@withrevert(e, usr, wad);

    bool revert1 = e.msg.value > 0;
    bool revert2 = vatDaiJoin < wad * RAY(); 
    bool revert3 = usr != currentContract && vatDaiUsr + wad * RAY() > max_uint256;
    bool revert4 = balanceOfSender < to_mathint(wad);
    bool revert5 = allowanceSenderJoin < to_mathint(wad);

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert revert4 => lastReverted, "revert4 failed";
    assert revert5 => lastReverted, "revert5 failed";
    assert lastReverted => revert1 || revert2 || revert3 ||
                           revert4 || revert5, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting exit
rule exit(address usr, uint256 wad) {
    env e;

    require e.msg.sender != currentContract;

    requireInvariant balanceSum_equals_totalSupply();

    address other;
    require other != usr;
    address anyUsr; address anyUsr2;

    mathint wardsBefore = usds.wards(anyUsr);
    mathint totalSupplyBefore = usds.totalSupply();
    mathint balanceOfUsrBefore = usds.balanceOf(usr);
    mathint balanceOfOtherBefore = usds.balanceOf(other);
    mathint allowanceBefore = usds.allowance(anyUsr, anyUsr2);
    mathint noncesBefore = usds.nonces(anyUsr);
    mathint vatDaiSenderBefore = vat.dai(e.msg.sender);
    mathint vatDaiJoinBefore = vat.dai(currentContract);

    exit(e, usr, wad);

    mathint wardsAfter = usds.wards(anyUsr);
    mathint totalSupplyAfter = usds.totalSupply();
    mathint balanceOfUsrAfter = usds.balanceOf(usr);
    mathint balanceOfOtherAfter = usds.balanceOf(other);
    mathint allowanceAfter = usds.allowance(anyUsr, anyUsr2);
    mathint noncesAfter = usds.nonces(anyUsr);
    mathint vatDaiSenderAfter = vat.dai(e.msg.sender);
    mathint vatDaiJoinAfter = vat.dai(currentContract);

    assert wardsAfter == wardsBefore, "exit did not keep unchanged usds.wards";
    assert totalSupplyAfter == totalSupplyBefore + wad, "exit did not increase usds.totalSupply by wad";
    assert balanceOfUsrAfter == balanceOfUsrBefore + wad, "exit did not increase usds.balanceOf[usr] by wad";
    assert balanceOfOtherAfter == balanceOfOtherBefore, "exit did not keep unchanged the rest of usds.balanceOf[x]";
    assert allowanceAfter == allowanceBefore, "exit did not keep unchanged every allowance[x][y]";
    assert noncesAfter == noncesBefore, "exit did not keep unchanged every usds.nonces[x]";
    assert vatDaiSenderAfter == vatDaiSenderBefore - wad * RAY(), "exit did not decrease vat.dai(sender) by wad * RAY";
    assert vatDaiJoinAfter == vatDaiJoinBefore + wad * RAY(), "exit did not increase vat.dai(join) by wad * RAY";
}

// Verify revert rules on exit
rule exit_revert(address usr, uint256 wad) {
    env e;

    require e.msg.sender != currentContract;

    requireInvariant balanceSum_equals_totalSupply();

    mathint wardsJoin = usds.wards(currentContract);
    mathint totalSupply = usds.totalSupply();
    mathint vatDaiSender = vat.dai(e.msg.sender);
    mathint vatDaiJoin = vat.dai(currentContract);

    exit@withrevert(e, usr, wad);

    bool revert1 = e.msg.value > 0;
    bool revert2 = vatDaiSender < wad * RAY();
    bool revert3 = vatDaiJoin + wad * RAY() > max_uint256;
    bool revert4 = wardsJoin != 1;
    bool revert5 = totalSupply + wad > max_uint256;
    bool revert6 = usr == 0 || usr == usds;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert revert4 => lastReverted, "revert4 failed";
    assert revert5 => lastReverted, "revert5 failed";
    assert revert6 => lastReverted, "revert6 failed";
    assert lastReverted => revert1 || revert2 || revert3 ||
                           revert4 || revert5 || revert6, "Revert rules are not covering all the cases";
}
