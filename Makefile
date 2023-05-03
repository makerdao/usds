all         :; forge build --use solc:0.8.16
clean       :; forge clean
test        :; forge test -vvv --use solc:0.8.16
certora-nst :; PATH=~/.solc-select/artifacts/solc-0.8.16:~/.solc-select/artifacts:${PATH} certoraRun --solc_map Nst=solc-0.8.16,Auxiliar=solc-0.8.16,SignerMock=solc-0.8.16 --optimize_map Nst=200,Auxiliar=0,SignerMock=0 --rule_sanity basic src/Nst.sol certora/Auxiliar.sol certora/SignerMock.sol --verify Nst:certora/Nst.spec --settings -mediumTimeout=180 --optimistic_loop$(if $(short), --short_output,)$(if $(rule), --rule $(rule),)$(if $(multi), --multi_assert_check,)
