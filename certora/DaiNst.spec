// DaiNst.spec

using Nst as nst;
using NstJoin as nstJoin;
using DaiMock as dai;
using DaiJoinMock as daiJoin;
using VatMock as vat;

methods {
    function nst.wards(address) external returns (uint256) envfree;
    function nst.totalSupply() external returns (uint256) envfree;
    function nst.balanceOf(address) external returns (uint256) envfree;
    function nst.allowance(address, address) external returns (uint256) envfree;
    function dai.wards(address) external returns (uint256) envfree;
    function dai.totalSupply() external returns (uint256) envfree;
    function dai.balanceOf(address) external returns (uint256) envfree;
    function dai.allowance(address, address) external returns (uint256) envfree;
    function vat.dai(address) external returns (uint256) envfree;
    function _.vat() external => DISPATCHER(true);
    function _.dai() external => DISPATCHER(true);
    function _.nst() external => DISPATCHER(true);
    function _.approve(address, uint256) external => DISPATCHER(true);
    function _.hope(address) external => DISPATCHER(true);
}

definition RAY() returns uint256 = 10^27;

ghost balanceSumNst() returns mathint {
    init_state axiom balanceSumNst() == 0;
}

hook Sstore nst.balanceOf[KEY address a] uint256 balance (uint256 old_balance) {
    havoc balanceSumNst assuming balanceSumNst@new() == balanceSumNst@old() + balance - old_balance && balanceSumNst@new() >= 0;
}

invariant balanceSumNst_equals_totalSupply() balanceSumNst() == to_mathint(nst.totalSupply());

ghost balanceSumDai() returns mathint {
    init_state axiom balanceSumDai() == 0;
}

hook Sstore dai.balanceOf[KEY address a] uint256 balance (uint256 old_balance) {
    havoc balanceSumDai assuming balanceSumDai@new() == balanceSumDai@old() + balance - old_balance && balanceSumDai@new() >= 0;
}

invariant balanceSumDai_equals_totalSupply() balanceSumDai() == to_mathint(dai.totalSupply());

// Verify correct storage changes for non reverting daiToNst
rule daiToNst(address usr, uint256 wad) {
    env e;

    require e.msg.sender != currentContract;
    require e.msg.sender != nstJoin;
    require e.msg.sender != daiJoin;

    requireInvariant balanceSumNst_equals_totalSupply();
    requireInvariant balanceSumDai_equals_totalSupply();

    address other;
    require other != usr;
    address other2;
    require other2 != e.msg.sender;
    address anyUsr;
    address anyUsr2; address anyUsr3;
    require anyUsr2 != e.msg.sender || anyUsr3 != currentContract;

    mathint nstTotalSupplyBefore = nst.totalSupply();
    mathint nstBalanceOfUsrBefore = nst.balanceOf(usr);
    mathint nstBalanceOfOtherBefore = nst.balanceOf(other);
    mathint daiTotalSupplyBefore = dai.totalSupply();
    mathint daiBalanceOfSenderBefore = dai.balanceOf(e.msg.sender);
    mathint daiBalanceOfOtherBefore = dai.balanceOf(other2);
    mathint vatDaiNstJoinBefore = vat.dai(nstJoin);
    mathint vatDaiDaiJoinBefore = vat.dai(daiJoin);

    daiToNst(e, usr, wad);

    mathint nstTotalSupplyAfter = nst.totalSupply();
    mathint nstBalanceOfUsrAfter = nst.balanceOf(usr);
    mathint nstBalanceOfOtherAfter = nst.balanceOf(other);
    mathint daiTotalSupplyAfter = dai.totalSupply();
    mathint daiBalanceOfSenderAfter = dai.balanceOf(e.msg.sender);
    mathint daiBalanceOfOtherAfter = dai.balanceOf(other2);
    mathint vatDaiJoinAfter = vat.dai(currentContract);
    mathint vatDaiUsrAfter = vat.dai(usr);
    mathint vatDaiNstJoinAfter = vat.dai(nstJoin);
    mathint vatDaiDaiJoinAfter = vat.dai(daiJoin);

    assert nstTotalSupplyAfter == nstTotalSupplyBefore + wad, "daiToNst did not increase nst.totalSupply by wad";
    assert nstBalanceOfUsrAfter == nstBalanceOfUsrBefore + wad, "daiToNst did not increase nst.balanceOf[usr] by wad";
    assert nstBalanceOfOtherAfter == nstBalanceOfOtherBefore, "daiToNst did not keep unchanged the rest of nst.balanceOf[x]";
    assert daiTotalSupplyAfter == daiTotalSupplyBefore - wad, "daiToNst did not decrease dai.totalSupply by wad";
    assert daiBalanceOfSenderAfter == daiBalanceOfSenderBefore - wad, "daiToNst did not decrease dai.balanceOf[sender] by wad";
    assert daiBalanceOfOtherAfter == daiBalanceOfOtherBefore, "daiToNst did not keep unchanged the rest of dai.balanceOf[x]";
    assert vatDaiNstJoinAfter == vatDaiNstJoinBefore + wad * RAY(), "daiToNst did not increase vat.dai(nstJoin) by wad * RAY";
    assert vatDaiDaiJoinAfter == vatDaiDaiJoinBefore - wad * RAY(), "daiToNst did not decrease vat.dai(daiJoin) by wad * RAY";
}

// Verify revert rules on daiToNst
rule daiToNst_revert(address usr, uint256 wad) {
    env e;

    requireInvariant balanceSumNst_equals_totalSupply();
    requireInvariant balanceSumDai_equals_totalSupply();

    require e.msg.sender != currentContract;
    require to_mathint(vat.dai(nstJoin)) >= nst.totalSupply() * RAY(); // Property of the relationship nst/nstJoin (not need to prove here)
    require to_mathint(vat.dai(daiJoin)) >= dai.totalSupply() * RAY(); // Property of the relationship dai/daiJoin (not need to prove here)
    require nst.wards(nstJoin) == 1; // Proved in NstJoin that this is necessary
    require to_mathint(dai.allowance(currentContract, daiJoin)) == max_uint256; // Set in the constructor

    mathint daiBalanceOfSender = dai.balanceOf(e.msg.sender);
    mathint daiAllowanceSenderDaiNst = dai.allowance(e.msg.sender, currentContract);
    mathint vatDaiDaiNst = vat.dai(currentContract);
    mathint vatDaiNstJoin = vat.dai(nstJoin);
    mathint nstBalanceOfUsr = nst.balanceOf(usr);

    daiToNst@withrevert(e, usr, wad);

    bool revert1 = e.msg.value > 0;
    bool revert2 = daiBalanceOfSender < to_mathint(wad);
    bool revert3 = daiAllowanceSenderDaiNst < to_mathint(wad);
    bool revert4 = vatDaiDaiNst + wad * RAY() > max_uint256;
    bool revert5 = vatDaiNstJoin + wad * RAY() > max_uint256;
    bool revert6 = usr == 0 || usr == nst;

    assert revert1 => lastReverted, "revert1 failed";
    assert revert2 => lastReverted, "revert2 failed";
    assert revert3 => lastReverted, "revert3 failed";
    assert revert4 => lastReverted, "revert4 failed";
    assert revert5 => lastReverted, "revert5 failed";
    assert revert6 => lastReverted, "revert6 failed";
    assert lastReverted => revert1 || revert2 || revert3 ||
                           revert4 || revert5 || revert6, "Revert rules are not covering all the cases";
}

// Verify correct storage changes for non reverting nstToDai
rule nstToDai(address usr, uint256 wad) {
    env e;

    require e.msg.sender != currentContract;
    require e.msg.sender != nstJoin;
    require e.msg.sender != daiJoin;

    requireInvariant balanceSumNst_equals_totalSupply();
    requireInvariant balanceSumDai_equals_totalSupply();

    address other;
    require other != e.msg.sender;
    address other2;
    require other2 != usr;
    address anyUsr;
    address anyUsr2; address anyUsr3;
    require anyUsr2 != e.msg.sender || anyUsr3 != currentContract;

    mathint nstTotalSupplyBefore = nst.totalSupply();
    mathint nstBalanceOfSenderBefore = nst.balanceOf(e.msg.sender);
    mathint nstBalanceOfOtherBefore = nst.balanceOf(other);
    mathint daiTotalSupplyBefore = dai.totalSupply();
    mathint daiBalanceOfUsrBefore = dai.balanceOf(usr);
    mathint daiBalanceOfOtherBefore = dai.balanceOf(other2);
    mathint vatDaiNstJoinBefore = vat.dai(nstJoin);
    mathint vatDaiDaiJoinBefore = vat.dai(daiJoin);

    nstToDai(e, usr, wad);

    mathint nstTotalSupplyAfter = nst.totalSupply();
    mathint nstBalanceOfSenderAfter = nst.balanceOf(e.msg.sender);
    mathint nstBalanceOfOtherAfter = nst.balanceOf(other);
    mathint daiTotalSupplyAfter = dai.totalSupply();
    mathint daiBalanceOfUsrAfter = dai.balanceOf(usr);
    mathint daiBalanceOfOtherAfter = dai.balanceOf(other2);
    mathint vatDaiJoinAfter = vat.dai(currentContract);
    mathint vatDaiUsrAfter = vat.dai(usr);
    mathint vatDaiNstJoinAfter = vat.dai(nstJoin);
    mathint vatDaiDaiJoinAfter = vat.dai(daiJoin);

    assert nstTotalSupplyAfter == nstTotalSupplyBefore - wad, "nstToDai did not decrease nst.totalSupply by wad";
    assert nstBalanceOfSenderAfter == nstBalanceOfSenderBefore - wad, "nstToDai did not decrease nst.balanceOf[sender] by wad";
    assert nstBalanceOfOtherAfter == nstBalanceOfOtherBefore, "nstToDai did not keep unchanged the rest of nst.balanceOf[x]";
    assert daiTotalSupplyAfter == daiTotalSupplyBefore + wad, "nstToDai did not decrease dai.totalSupply by wad";
    assert daiBalanceOfUsrAfter == daiBalanceOfUsrBefore + wad, "nstToDai did not decrease dai.balanceOf[usr] by wad";
    assert daiBalanceOfOtherAfter == daiBalanceOfOtherBefore, "nstToDai did not keep unchanged the rest of dai.balanceOf[x]";
    assert vatDaiNstJoinAfter == vatDaiNstJoinBefore - wad * RAY(), "nstToDai did not decrease vat.dai(nstJoin) by wad * RAY";
    assert vatDaiDaiJoinAfter == vatDaiDaiJoinBefore + wad * RAY(), "nstToDai did not increase vat.dai(daiJoin) by wad * RAY";
}

// Verify revert rules on nstToDai
rule nstToDai_revert(address usr, uint256 wad) {
    env e;

    requireInvariant balanceSumNst_equals_totalSupply();
    requireInvariant balanceSumDai_equals_totalSupply();

    require e.msg.sender != currentContract;
    require to_mathint(vat.dai(nstJoin)) >= nst.totalSupply() * RAY(); // Property of the relationship nst/nstJoin (not need to prove here)
    require to_mathint(vat.dai(daiJoin)) >= dai.totalSupply() * RAY(); // Property of the relationship dai/daiJoin (not need to prove here)
    require dai.wards(daiJoin) == 1; // Assume proved property of daiJoin
    require to_mathint(nst.allowance(currentContract, nstJoin)) == max_uint256; // Set in the constructor

    mathint nstBalanceOfSender = nst.balanceOf(e.msg.sender);
    mathint nstAllowanceSenderDaiNst = nst.allowance(e.msg.sender, currentContract);
    mathint vatDaiDaiNst = vat.dai(currentContract);
    mathint vatDaiDaiJoin = vat.dai(daiJoin);
    mathint daiBalanceOfUsr = dai.balanceOf(usr);

    nstToDai@withrevert(e, usr, wad);

    bool revert1 = e.msg.value > 0;
    bool revert2 = nstBalanceOfSender < to_mathint(wad);
    bool revert3 = nstAllowanceSenderDaiNst < to_mathint(wad);
    bool revert4 = vatDaiDaiNst + wad * RAY() > max_uint256;
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
