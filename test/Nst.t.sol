// SPDX-License-Identifier: AGPL-3.0-or-later

pragma solidity ^0.8.21;

import "token-tests/TokenFuzzTests.sol";
import { ERC1967Proxy } from "@openzeppelin/contracts/proxy/ERC1967/ERC1967Proxy.sol";
import { Upgrades, Options } from "openzeppelin-foundry-upgrades/Upgrades.sol";

import { Nst, UUPSUpgradeable, Initializable, ERC1967Utils } from "src/Nst.sol";

contract Nst2 is UUPSUpgradeable {
    mapping (address => uint256) public wards;
    string  public constant version  = "2";

    uint256 public totalSupply;
    mapping (address => uint256)                      public balanceOf;
    mapping (address => mapping (address => uint256)) public allowance;
    mapping (address => uint256)                      public nonces;

    event UpgradedTo(string version);

    modifier auth {
        require(wards[msg.sender] == 1, "Nst/not-authorized");
        _;
    }

    constructor() {
        _disableInitializers(); // Avoid initializing in the context of the implementation
    }

    function reinitialize() reinitializer(2) external {
        emit UpgradedTo(version);
    }

    function _authorizeUpgrade(address newImplementation) internal override auth {}

    function getImplementation() external view returns (address) {
        return ERC1967Utils.getImplementation();
    }
}

contract NstTest is TokenFuzzTests {
    Nst nst;
    bool validate;

    event UpgradedTo(string version);

    function setUp() public {
        validate = vm.envOr("VALIDATE", false);

        address imp = address(new Nst());
        vm.expectEmit(true, true, true, true);
        emit Rely(address(this));
        nst = Nst(address(new ERC1967Proxy(imp, abi.encodeCall(Nst.initialize, ()))));
        assertEq(nst.version(), "1");
        assertEq(nst.wards(address(this)), 1);
        assertEq(nst.getImplementation(), imp);

        _token_ = address(nst);
        _contractName_ = "Nst";
        _tokenName_ ="Nst Stablecoin";
        _symbol_ = "NST";
    }

    function invariantMetadata() public view {
        assertEq(nst.name(), "Nst Stablecoin");
        assertEq(nst.symbol(), "NST");
        assertEq(nst.version(), "1");
        assertEq(nst.decimals(), 18);
    }

    function testDeployWithUpgradesLib() public {
        Options memory opts;
        if (!validate) {
            opts.unsafeSkipAllChecks = true;
        } else {
            opts.unsafeAllow = 'state-variable-immutable,constructor';
        }

        vm.expectEmit(true, true, true, true);
        emit Rely(address(this));
        address proxy = Upgrades.deployUUPSProxy(
            "out/Nst.sol/Nst.json",
            abi.encodeCall(Nst.initialize, ()),
            opts
        );
        assertEq(Nst(proxy).version(), "1");
        assertEq(Nst(proxy).wards(address(this)), 1);
    }

    function testUpgrade() public {
        address implementation1 = nst.getImplementation();

        address newImpl = address(new Nst2());
        vm.expectEmit(true, true, true, true);
        emit UpgradedTo("2");
        nst.upgradeToAndCall(newImpl, abi.encodeCall(Nst2.reinitialize, ()));

        address implementation2 = nst.getImplementation();
        assertEq(implementation2, newImpl);
        assertTrue(implementation2 != implementation1);
        assertEq(nst.version(), "2");
        assertEq(nst.wards(address(this)), 1); // still a ward
    }

    function testUpgradeWithUpgradesLib() public {
        address implementation1 = nst.getImplementation();

        Options memory opts;
        if (!validate) {
            opts.unsafeSkipAllChecks = true;
        } else {
            opts.referenceContract = "out/Nst.sol/Nst.json";
            opts.unsafeAllow = 'constructor';
        }

        vm.expectEmit(true, true, true, true);
        emit UpgradedTo("2");
        Upgrades.upgradeProxy(
            address(nst),
            "out/Nst.t.sol/Nst2.json",
            abi.encodeCall(Nst2.reinitialize, ()),
            opts
        );

        address implementation2 = nst.getImplementation();
        assertTrue(implementation1 != implementation2);
        assertEq(nst.version(), "2");
        assertEq(nst.wards(address(this)), 1); // still a ward
    }

    function testUpgradeUnauthed() public {
        address newImpl = address(new Nst2());
        vm.expectRevert("Nst/not-authorized");
        vm.prank(address(0x123)); nst.upgradeToAndCall(newImpl, abi.encodeCall(Nst2.reinitialize, ()));
    }

    function testInitializeAgain() public {
        vm.expectRevert(Initializable.InvalidInitialization.selector);
        nst.initialize();
    }

    function testInitializeDirectly() public {
        address implementation = nst.getImplementation();
        vm.expectRevert(Initializable.InvalidInitialization.selector);
        Nst(implementation).initialize();
    }
}
