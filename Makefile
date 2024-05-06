PATH := ~/.solc-select/artifacts/solc-0.8.21:~/.solc-select/artifacts:$(PATH)
certora-nst      :; PATH=${PATH} certoraRun certora/Nst.conf$(if $(rule), --rule $(rule),)
certora-nst-join :; PATH=${PATH} certoraRun certora/NstJoin.conf$(if $(rule), --rule $(rule),)
certora-dai-nst  :; PATH=${PATH} certoraRun certora/DaiNst.conf$(if $(rule), --rule $(rule),)
