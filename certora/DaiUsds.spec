// DaiUsds.spec

using Usds as usds;
using UsdsJoin as usdsJoin;
using DaiMock as dai;
using DaiJoinMock as daiJoin;
using VatMock as vat;

methods {
    function usds.wards(address) external returns (uint256) envfree;
    function usds.totalSupply() external returns (uint256) envfree;
    function usds.balanceOf(address) external returns (uint256) envfree;
    function usds.allowance(address, address) external returns (uint256) envfree;
    function dai.wards(address) external returns (uint256) envfree;
    function dai.totalSupply() external returns (uint256) envfree;
    function dai.balanceOf(address) external returns (uint256) envfree;
    function dai.allowance(address, address) external returns (uint256) envfree;
    function vat.dai(address) external returns (uint256) envfree;
    function _.vat() external => DISPATCHER(true);
    function _.dai() external => DISPATCHER(true);
    function _.usds() external => DISPATCHER(true);
    function _.approve(address, uint256) external => DISPATCHER(true);
    function _.hope(address) external => DISPATCHER(true);
}

definition RAY() returns uint256 = 10^27;

ghost balanceSumUsds() returns mathint {
    init_state axiom balanceSumUsds() == 0;
}

hook Sstore usds.balanceOf[KEY address a] uint256 balance (uint256 old_balance) {
    havoc balanceSumUsds assuming balanceSumUsds@new() == balanceSumUsds@old() + balance - old_balance && balanceSumUsds@new() >= 0;
}

invariant balanceSumUsds_equals_totalSupply() balanceSumUsds() == to_mathint(usds.totalSupply())
            filtered {
                m -> m.selector != sig:Usds.upgradeToAndCall(address, bytes).selector
            }

ghost balanceSumDai() returns mathint {
    init_state axiom balanceSumDai() == 0;
}

hook Sstore dai.balanceOf[KEY address a] uint256 balance (uint256 old_balance) {
    havoc balanceSumDai assuming balanceSumDai@new() == balanceSumDai@old() + balance - old_balance && balanceSumDai@new() >= 0;
}

invariant balanceSumDai_equals_totalSupply() balanceSumDai() == to_mathint(dai.totalSupply())
            filtered {
                m -> m.selector != sig:DaiMock.upgradeToAndCall(address, bytes).selector
            }

// Verify correct storage changes for non reverting daiToUsds
rule daiToUsds(address usr, uint256 wad) {
    env e;

    require e.msg.sender != currentContract;
    require e.msg.sender != usdsJoin;
    require e.msg.sender != daiJoin;

    requireInvariant balanceSumUsds_equals_totalSupply();
    requireInvariant balanceSumDai_equals_totalSupply();

    address other;
    require other != usr;
    address other2;
    require other2 != e.msg.sender;
    address anyUsr;
    address anyUsr2; address anyUsr3;
    require anyUsr2 != e.msg.sender || anyUsr3 != currentContract;

    mathint usdsTotalSupplyBefore = usds.totalSupply();
    mathint usdsBalanceOfUsrBefore = usds.balanceOf(usr);
    mathint usdsBalanceOfOtherBefore = usds.balanceOf(other);
    mathint daiTotalSupplyBefore = dai.totalSupply();
    mathint daiBalanceOfSenderBefore = dai.balanceOf(e.msg.sender);
    mathint daiBalanceOfOtherBefore = dai.balanceOf(other2);
    mathint vatDaiUsdsJoinBefore = vat.dai(usdsJoin);
    mathint vatDaiDaiJoinBefore = vat.dai(daiJoin);

    daiToUsds(e, usr, wad);

    mathint usdsTotalSupplyAfter = usds.totalSupply();
    mathint usdsBalanceOfUsrAfter = usds.balanceOf(usr);
    mathint usdsBalanceOfOtherAfter = usds.balanceOf(other);
    mathint daiTotalSupplyAfter = dai.totalSupply();
    mathint daiBalanceOfSenderAfter = dai.balanceOf(e.msg.sender);
    mathint daiBalanceOfOtherAfter = dai.balanceOf(other2);
    mathint vatDaiJoinAfter = vat.dai(currentContract);
    mathint vatDaiUsrAfter = vat.dai(usr);
    mathint vatDaiUsdsJoinAfter = vat.dai(usdsJoin);
    mathint vatDaiDaiJoinAfter = vat.dai(daiJoin);

    assert usdsTotalSupplyAfter == usdsTotalSupplyBefore + wad, "daiToUsds did not increase usds.totalSupply by wad";
    assert usdsBalanceOfUsrAfter == usdsBalanceOfUsrBefore + wad, "daiToUsds did not increase usds.balanceOf[usr] by wad";
    assert usdsBalanceOfOtherAfter == usdsBalanceOfOtherBefore, "daiToUsds did not keep unchanged the rest of usds.balanceOf[x]";
    assert daiTotalSupplyAfter == daiTotalSupplyBefore - wad, "daiToUsds did not decrease dai.totalSupply by wad";
    assert daiBalanceOfSenderAfter == daiBalanceOfSenderBefore - wad, "daiToUsds did not decrease dai.balanceOf[sender] by wad";
    assert daiBalanceOfOtherAfter == daiBalanceOfOtherBefore, "daiToUsds did not keep unchanged the rest of dai.balanceOf[x]";
    assert vatDaiUsdsJoinAfter == vatDaiUsdsJoinBefore + wad * RAY(), "daiToUsds did not increase vat.dai(usdsJoin) by wad * RAY";
    assert vatDaiDaiJoinAfter == vatDaiDaiJoinBefore - wad * RAY(), "daiToUsds did not decrease vat.dai(daiJoin) by wad * RAY";
}

// Verify revert rules on daiToUsds
rule daiToUsds_revert(address usr, uint256 wad) {
    env e;

    requireInvariant balanceSumUsds_equals_totalSupply();
    requireInvariant balanceSumDai_equals_totalSupply();

    require e.msg.sender != currentContract;
    require to_mathint(vat.dai(usdsJoin)) >= usds.totalSupply() * RAY(); // Property of the relationship usds/usdsJoin (not need to prove here)
    require to_mathint(vat.dai(daiJoin)) >= dai.totalSupply() * RAY(); // Property of the relationship dai/daiJoin (not need to prove here)
    require usds.wards(usdsJoin) == 1; // Proved in UsdsJoin that this is necessary
    require to_mathint(dai.allowance(currentContract, daiJoin)) == max_uint256; // Set in the constructor

    mathint daiBalanceOfSender = dai.balanceOf(e.msg.sender);
    mathint daiAllowanceSenderDaiUsds = dai.allowance(e.msg.sender, currentContract);
    mathint vatDaiDaiUsds = vat.dai(currentContract);
    mathint vatDaiUsdsJoin = vat.dai(usdsJoin);
    mathint usdsBalanceOfUsr = usds.balanceOf(usr);

    daiToUsds@withrevert(e, usr, wad);

    bool revert1 = e.msg.value > 0;
    bool revert2 = daiBalanceOfSender < to_mathint(wad);
    bool revert3 = daiAllowanceSenderDaiUsds < to_mathint(wad);
    bool revert4 = vatDaiDaiUsds + wad * RAY() > max_uint256;
    bool revert5 = vatDaiUsdsJoin + wad * RAY() > max_uint256;
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

// Verify correct storage changes for non reverting usdsToDai
rule usdsToDai(address usr, uint256 wad) {
    env e;

    require e.msg.sender != currentContract;
    require e.msg.sender != usdsJoin;
    require e.msg.sender != daiJoin;

    requireInvariant balanceSumUsds_equals_totalSupply();
    requireInvariant balanceSumDai_equals_totalSupply();

    address other;
    require other != e.msg.sender;
    address other2;
    require other2 != usr;
    address anyUsr;
    address anyUsr2; address anyUsr3;
    require anyUsr2 != e.msg.sender || anyUsr3 != currentContract;

    mathint usdsTotalSupplyBefore = usds.totalSupply();
    mathint usdsBalanceOfSenderBefore = usds.balanceOf(e.msg.sender);
    mathint usdsBalanceOfOtherBefore = usds.balanceOf(other);
    mathint daiTotalSupplyBefore = dai.totalSupply();
    mathint daiBalanceOfUsrBefore = dai.balanceOf(usr);
    mathint daiBalanceOfOtherBefore = dai.balanceOf(other2);
    mathint vatDaiUsdsJoinBefore = vat.dai(usdsJoin);
    mathint vatDaiDaiJoinBefore = vat.dai(daiJoin);

    usdsToDai(e, usr, wad);

    mathint usdsTotalSupplyAfter = usds.totalSupply();
    mathint usdsBalanceOfSenderAfter = usds.balanceOf(e.msg.sender);
    mathint usdsBalanceOfOtherAfter = usds.balanceOf(other);
    mathint daiTotalSupplyAfter = dai.totalSupply();
    mathint daiBalanceOfUsrAfter = dai.balanceOf(usr);
    mathint daiBalanceOfOtherAfter = dai.balanceOf(other2);
    mathint vatDaiJoinAfter = vat.dai(currentContract);
    mathint vatDaiUsrAfter = vat.dai(usr);
    mathint vatDaiUsdsJoinAfter = vat.dai(usdsJoin);
    mathint vatDaiDaiJoinAfter = vat.dai(daiJoin);

    assert usdsTotalSupplyAfter == usdsTotalSupplyBefore - wad, "usdsToDai did not decrease usds.totalSupply by wad";
    assert usdsBalanceOfSenderAfter == usdsBalanceOfSenderBefore - wad, "usdsToDai did not decrease usds.balanceOf[sender] by wad";
    assert usdsBalanceOfOtherAfter == usdsBalanceOfOtherBefore, "usdsToDai did not keep unchanged the rest of usds.balanceOf[x]";
    assert daiTotalSupplyAfter == daiTotalSupplyBefore + wad, "usdsToDai did not decrease dai.totalSupply by wad";
    assert daiBalanceOfUsrAfter == daiBalanceOfUsrBefore + wad, "usdsToDai did not decrease dai.balanceOf[usr] by wad";
    assert daiBalanceOfOtherAfter == daiBalanceOfOtherBefore, "usdsToDai did not keep unchanged the rest of dai.balanceOf[x]";
    assert vatDaiUsdsJoinAfter == vatDaiUsdsJoinBefore - wad * RAY(), "usdsToDai did not decrease vat.dai(usdsJoin) by wad * RAY";
    assert vatDaiDaiJoinAfter == vatDaiDaiJoinBefore + wad * RAY(), "usdsToDai did not increase vat.dai(daiJoin) by wad * RAY";
}

// Verify revert rules on usdsToDai
rule usdsToDai_revert(address usr, uint256 wad) {
    env e;

    requireInvariant balanceSumUsds_equals_totalSupply();
    requireInvariant balanceSumDai_equals_totalSupply();

    require e.msg.sender != currentContract;
    require to_mathint(vat.dai(usdsJoin)) >= usds.totalSupply() * RAY(); // Property of the relationship usds/usdsJoin (not need to prove here)
    require to_mathint(vat.dai(daiJoin)) >= dai.totalSupply() * RAY(); // Property of the relationship dai/daiJoin (not need to prove here)
    require dai.wards(daiJoin) == 1; // Assume proved property of daiJoin
    require to_mathint(usds.allowance(currentContract, usdsJoin)) == max_uint256; // Set in the constructor

    mathint usdsBalanceOfSender = usds.balanceOf(e.msg.sender);
    mathint usdsAllowanceSenderDaiUsds = usds.allowance(e.msg.sender, currentContract);
    mathint vatDaiDaiUsds = vat.dai(currentContract);
    mathint vatDaiDaiJoin = vat.dai(daiJoin);
    mathint daiBalanceOfUsr = dai.balanceOf(usr);

    usdsToDai@withrevert(e, usr, wad);

    bool revert1 = e.msg.value > 0;
    bool revert2 = usdsBalanceOfSender < to_mathint(wad);
    bool revert3 = usdsAllowanceSenderDaiUsds < to_mathint(wad);
    bool revert4 = vatDaiDaiUsds + wad * RAY() > max_uint256;
    bool revert5 = vatDaiDaiJoin + wad * RAY() > max_uint256;
    bool revert6 = usr == 0 || usr == dai;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert revert4 => lastReverted, "revert4 failed";
    assert revert5 => lastReverted, "revert5 failed";
    assert revert6 => lastReverted, "revert6 failed";
    assert lastReverted => revert1 || revert2 || revert3 ||
                           revert4 || revert5 || revert6, "Revert rules are not covering all the cases";
}
