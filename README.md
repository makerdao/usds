# NST Token and contracts associated

This repository includes 3 smart contracts:

- NST token
- NstJoin
- DaiNst Converter

### NST token

This is a standard erc20 implementation with regular `permit` functionality + EIP-1271 smart contract signature validation.

The token uses the ERC-1822 UUPS pattern for upgradeability and the ERC-1967 proxy storage slots standard.
It is important that the `NstDeploy` library sequence be used for deploying the token.

#### OZ upgradeability validations

The OZ validations can be run alongside the existing tests:  
`VALIDATE=true forge test --ffi --build-info --extra-output storageLayout`

### NstJoin

This is the contract in charge of `mint`ing the erc20 IOUs in exchange of native `vat.dai` balance. It also manages the reverse operation, `burn`ing tokens and releasing `vat.dai`.
A noticeable code difference against `DaiJoin` is this contract doesn't have any permissions system at all.
However, in practice, `NstJoin` acts the exact same way as the production `DaiJoin` implementation. This is because there isn't any `wards(address)` set there.

### DaiNst

It is a permissionless converter between `Dai` and `Nst` (both ways). Using the `public` functions of `NstJoin` and `DaiJoin` moves from one token to the other. The exchange rate is 1:1.
It is just a "convenience" contract, users could still get the same outcome executing the separate methods in the `join`s or use any other converter implementation.
