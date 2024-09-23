PATH := ~/.solc-select/artifacts/solc-0.8.21:~/.solc-select/artifacts:$(PATH)
certora-usds      :; PATH=${PATH} certoraRun certora/Usds.conf$(if $(rule), --rule $(rule),)
certora-usds-join :; PATH=${PATH} certoraRun certora/UsdsJoin.conf$(if $(rule), --rule $(rule),)
certora-dai-usds  :; PATH=${PATH} certoraRun certora/DaiUsds.conf$(if $(rule), --rule $(rule),)
