// SPDX-License-Identifier: AGPL-3.0-or-later

pragma solidity ^0.8.16;

import "dss-test/DssTest.sol";

import { Nst, IERC1271 } from "../Nst.sol";

contract MockMultisig is IERC1271 {
    address public signer1;
    address public signer2;

    constructor(address signer1_, address signer2_) {
        signer1 = signer1_;
        signer2 = signer2_;
    }

    function isValidSignature(bytes32 digest, bytes memory signature) external view returns (bytes4 sig) {
        bytes32 r;
        bytes32 s;
        uint8 v;
        assembly {
            r := mload(add(signature, 0x20))
            s := mload(add(signature, 0x40))
            v := byte(0, mload(add(signature, 0x60)))
        }
        if (signer1 == ecrecover(digest, v, r, s)) {
            assembly {
                r := mload(add(signature, 0x80))
                s := mload(add(signature, 0xA0))
                v := byte(0, mload(add(signature, 0xC0)))
            }
            if (signer2 == ecrecover(digest, v, r, s)) {
                sig = IERC1271.isValidSignature.selector;
            }
        }
    }
}

contract NstTest is DssTest {
    Nst nst;

    event Transfer(address indexed from, address indexed to, uint256 amount);
    event Approval(address indexed owner, address indexed spender, uint256 amount);

    bytes32 constant PERMIT_TYPEHASH =
        keccak256("Permit(address owner,address spender,uint256 value,uint256 nonce,uint256 deadline)");

    function setUp() public {
        vm.expectEmit(true, true, true, true);
        emit Rely(address(this));
        nst = new Nst();
    }

    function testAuth() public {
        checkAuth(address(nst), "Nst");
    }

    function invariantMetadata() public {
        assertEq(nst.name(), "Nst Stablecoin");
        assertEq(nst.symbol(), "NST");
        assertEq(nst.version(), "1");
        assertEq(nst.decimals(), 18);
    }

    function testMint() public {
        vm.expectEmit(true, true, true, true);
        emit Transfer(address(0), address(0xBEEF), 1e18);
        nst.mint(address(0xBEEF), 1e18);

        assertEq(nst.totalSupply(), 1e18);
        assertEq(nst.balanceOf(address(0xBEEF)), 1e18);
    }

    function testMintBadAddress() public {
        vm.expectRevert("Nst/invalid-address");
        nst.mint(address(0), 1e18);
        vm.expectRevert("Nst/invalid-address");
        nst.mint(address(nst), 1e18);
    }

    function testBurn() public {
        nst.mint(address(0xBEEF), 1e18);

        vm.expectEmit(true, true, true, true);
        emit Transfer(address(0xBEEF), address(0), 0.9e18);
        vm.prank(address(0xBEEF));
        nst.burn(address(0xBEEF), 0.9e18);

        assertEq(nst.totalSupply(), 1e18 - 0.9e18);
        assertEq(nst.balanceOf(address(0xBEEF)), 0.1e18);
    }

    function testBurnDifferentFrom() public {
        nst.mint(address(0xBEEF), 1e18);

        assertEq(nst.allowance(address(0xBEEF), address(this)), 0);
        vm.prank(address(0xBEEF));
        nst.approve(address(this), 0.4e18);
        assertEq(nst.allowance(address(0xBEEF), address(this)), 0.4e18);
        vm.expectEmit(true, true, true, true);
        emit Transfer(address(0xBEEF), address(0), 0.4e18);
        nst.burn(address(0xBEEF), 0.4e18);
        assertEq(nst.allowance(address(0xBEEF), address(this)), 0);

        assertEq(nst.totalSupply(), 1e18 - 0.4e18);
        assertEq(nst.balanceOf(address(0xBEEF)), 0.6e18);

        vm.prank(address(0xBEEF));
        nst.approve(address(this), type(uint256).max);
        assertEq(nst.allowance(address(0xBEEF), address(this)), type(uint256).max);
        vm.expectEmit(true, true, true, true);
        emit Transfer(address(0xBEEF), address(0), 0.4e18);
        nst.burn(address(0xBEEF), 0.4e18);
        assertEq(nst.allowance(address(0xBEEF), address(this)), type(uint256).max);

        assertEq(nst.totalSupply(), 0.6e18 - 0.4e18);
        assertEq(nst.balanceOf(address(0xBEEF)), 0.2e18);
    }

    function testApprove() public {
        vm.expectEmit(true, true, true, true);
        emit Approval(address(this), address(0xBEEF), 1e18);
        assertTrue(nst.approve(address(0xBEEF), 1e18));

        assertEq(nst.allowance(address(this), address(0xBEEF)), 1e18);
    }

    function testIncreaseAllowance() public {
        vm.expectEmit(true, true, true, true);
        emit Approval(address(this), address(0xBEEF), 1e18);
        assertTrue(nst.increaseAllowance(address(0xBEEF), 1e18));

        assertEq(nst.allowance(address(this), address(0xBEEF)), 1e18);
    }

    function testDecreaseAllowance() public {
        assertTrue(nst.increaseAllowance(address(0xBEEF), 3e18));
        vm.expectEmit(true, true, true, true);
        emit Approval(address(this), address(0xBEEF), 2e18);
        assertTrue(nst.decreaseAllowance(address(0xBEEF), 1e18));

        assertEq(nst.allowance(address(this), address(0xBEEF)), 2e18);
    }

    function testDecreaseAllowanceInsufficientBalance() public {
        assertTrue(nst.increaseAllowance(address(0xBEEF), 1e18));
        vm.expectRevert("Nst/insufficient-allowance");
        nst.decreaseAllowance(address(0xBEEF), 2e18);
    }

    function testTransfer() public {
        nst.mint(address(this), 1e18);

        vm.expectEmit(true, true, true, true);
        emit Transfer(address(this), address(0xBEEF), 1e18);
        assertTrue(nst.transfer(address(0xBEEF), 1e18));
        assertEq(nst.totalSupply(), 1e18);

        assertEq(nst.balanceOf(address(this)), 0);
        assertEq(nst.balanceOf(address(0xBEEF)), 1e18);
    }

    function testTransferBadAddress() public {
        nst.mint(address(this), 1e18);

        vm.expectRevert("Nst/invalid-address");
        nst.transfer(address(0), 1e18);
        vm.expectRevert("Nst/invalid-address");
        nst.transfer(address(nst), 1e18);
    }

    function testTransferFrom() public {
        address from = address(0xABCD);

        nst.mint(from, 1e18);

        vm.prank(from);
        nst.approve(address(this), 1e18);

        vm.expectEmit(true, true, true, true);
        emit Transfer(from, address(0xBEEF), 1e18);
        assertTrue(nst.transferFrom(from, address(0xBEEF), 1e18));
        assertEq(nst.totalSupply(), 1e18);

        assertEq(nst.allowance(from, address(this)), 0);

        assertEq(nst.balanceOf(from), 0);
        assertEq(nst.balanceOf(address(0xBEEF)), 1e18);
    }

    function testTransferFromBadAddress() public {
        nst.mint(address(this), 1e18);
        
        vm.expectRevert("Nst/invalid-address");
        nst.transferFrom(address(this), address(0), 1e18);
        vm.expectRevert("Nst/invalid-address");
        nst.transferFrom(address(this), address(nst), 1e18);
    }

    function testInfiniteApproveTransferFrom() public {
        address from = address(0xABCD);

        nst.mint(from, 1e18);

        vm.prank(from);
        vm.expectEmit(true, true, true, true);
        emit Approval(from, address(this), type(uint256).max);
        nst.approve(address(this), type(uint256).max);

        vm.expectEmit(true, true, true, true);
        emit Transfer(from, address(0xBEEF), 1e18);
        assertTrue(nst.transferFrom(from, address(0xBEEF), 1e18));
        assertEq(nst.totalSupply(), 1e18);

        assertEq(nst.allowance(from, address(this)), type(uint256).max);

        assertEq(nst.balanceOf(from), 0);
        assertEq(nst.balanceOf(address(0xBEEF)), 1e18);
    }

    function testPermit() public {
        uint256 privateKey = 0xBEEF;
        address owner = vm.addr(privateKey);

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(
            privateKey,
            keccak256(
                abi.encodePacked(
                    "\x19\x01",
                    nst.DOMAIN_SEPARATOR(),
                    keccak256(abi.encode(PERMIT_TYPEHASH, owner, address(0xCAFE), 1e18, 0, block.timestamp))
                )
            )
        );

        vm.expectEmit(true, true, true, true);
        emit Approval(owner, address(0xCAFE), 1e18);
        nst.permit(owner, address(0xCAFE), 1e18, block.timestamp, v, r, s);

        assertEq(nst.allowance(owner, address(0xCAFE)), 1e18);
        assertEq(nst.nonces(owner), 1);
    }

    function testPermitContract() public {
        uint256 privateKey1 = 0xBEEF;
        address signer1 = vm.addr(privateKey1);
        uint256 privateKey2 = 0xBEEE;
        address signer2 = vm.addr(privateKey2);

        address mockMultisig = address(new MockMultisig(signer1, signer2));

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(
            uint256(privateKey1),
            keccak256(
                abi.encodePacked(
                    "\x19\x01",
                    nst.DOMAIN_SEPARATOR(),
                    keccak256(abi.encode(PERMIT_TYPEHASH, mockMultisig, address(0xCAFE), 1e18, 0, block.timestamp))
                )
            )
        );

        (uint8 v2, bytes32 r2, bytes32 s2) = vm.sign(
            uint256(privateKey2),
            keccak256(
                abi.encodePacked(
                    "\x19\x01",
                    nst.DOMAIN_SEPARATOR(),
                    keccak256(abi.encode(PERMIT_TYPEHASH, mockMultisig, address(0xCAFE), 1e18, 0, block.timestamp))
                )
            )
        );

        bytes memory signature = abi.encode(r, s, bytes32(uint256(v) << 248), r2, s2, bytes32(uint256(v2) << 248));
        vm.expectEmit(true, true, true, true);
        emit Approval(mockMultisig, address(0xCAFE), 1e18);
        nst.permit(mockMultisig, address(0xCAFE), 1e18, block.timestamp, signature);

        assertEq(nst.allowance(mockMultisig, address(0xCAFE)), 1e18);
        assertEq(nst.nonces(mockMultisig), 1);
    }

    function testPermitContractInvalidSignature() public {
        uint256 privateKey1 = 0xBEEF;
        address signer1 = vm.addr(privateKey1);
        uint256 privateKey2 = 0xBEEE;
        address signer2 = vm.addr(privateKey2);

        address mockMultisig = address(new MockMultisig(signer1, signer2));

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(
            uint256(privateKey1),
            keccak256(
                abi.encodePacked(
                    "\x19\x01",
                    nst.DOMAIN_SEPARATOR(),
                    keccak256(abi.encode(PERMIT_TYPEHASH, mockMultisig, address(0xCAFE), 1e18, 0, block.timestamp))
                )
            )
        );

        (uint8 v2, bytes32 r2, bytes32 s2) = vm.sign(
            uint256(0xCEEE),
            keccak256(
                abi.encodePacked(
                    "\x19\x01",
                    nst.DOMAIN_SEPARATOR(),
                    keccak256(abi.encode(PERMIT_TYPEHASH, mockMultisig, address(0xCAFE), 1e18, 0, block.timestamp))
                )
            )
        );

        bytes memory signature = abi.encode(r, s, bytes32(uint256(v) << 248), r2, s2, bytes32(uint256(v2) << 248));
        vm.expectRevert("Nst/invalid-permit");
        nst.permit(mockMultisig, address(0xCAFE), 1e18, block.timestamp, signature);
    }

    function testTransferInsufficientBalance() public {
        nst.mint(address(this), 0.9e18);
        vm.expectRevert("Nst/insufficient-balance");
        nst.transfer(address(0xBEEF), 1e18);
    }

    function testTransferFromInsufficientAllowance() public {
        address from = address(0xABCD);

        nst.mint(from, 1e18);

        vm.prank(from);
        nst.approve(address(this), 0.9e18);

        vm.expectRevert("Nst/insufficient-allowance");
        nst.transferFrom(from, address(0xBEEF), 1e18);
    }

    function testTransferFromInsufficientBalance() public {
        address from = address(0xABCD);

        nst.mint(from, 0.9e18);

        vm.prank(from);
        nst.approve(address(this), 1e18);

        vm.expectRevert("Nst/insufficient-balance");
        nst.transferFrom(from, address(0xBEEF), 1e18);
    }

    function testPermitBadNonce() public {
        uint256 privateKey = 0xBEEF;
        address owner = vm.addr(privateKey);

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(
            privateKey,
            keccak256(
                abi.encodePacked(
                    "\x19\x01",
                    nst.DOMAIN_SEPARATOR(),
                    keccak256(abi.encode(PERMIT_TYPEHASH, owner, address(0xCAFE), 1e18, 1, block.timestamp))
                )
            )
        );

        vm.expectRevert("Nst/invalid-permit");
        nst.permit(owner, address(0xCAFE), 1e18, block.timestamp, v, r, s);
    }

    function testPermitBadDeadline() public {
        uint256 privateKey = 0xBEEF;
        address owner = vm.addr(privateKey);

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(
            privateKey,
            keccak256(
                abi.encodePacked(
                    "\x19\x01",
                    nst.DOMAIN_SEPARATOR(),
                    keccak256(abi.encode(PERMIT_TYPEHASH, owner, address(0xCAFE), 1e18, 0, block.timestamp))
                )
            )
        );

        vm.expectRevert("Nst/invalid-permit");
        nst.permit(owner, address(0xCAFE), 1e18, block.timestamp + 1, v, r, s);
    }

    function testPermitPastDeadline() public {
        uint256 privateKey = 0xBEEF;
        address owner = vm.addr(privateKey);
        uint256 deadline = block.timestamp;

        bytes32 domain_separator = nst.DOMAIN_SEPARATOR();
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(
            privateKey,
            keccak256(
                abi.encodePacked(
                    "\x19\x01",
                    domain_separator,
                    keccak256(abi.encode(PERMIT_TYPEHASH, owner, address(0xCAFE), 1e18, 0, deadline))
                )
            )
        );

        vm.warp(deadline + 1);

        vm.expectRevert("Nst/permit-expired");
        nst.permit(owner, address(0xCAFE), 1e18, deadline, v, r, s);
    }

    function testPermitOwnerZero() public {
        vm.expectRevert("Nst/invalid-owner");
        nst.permit(address(0), address(0xCAFE), 1e18, block.timestamp, 28, bytes32(0), bytes32(0));
    }

    function testPermitReplay() public {
        uint256 privateKey = 0xBEEF;
        address owner = vm.addr(privateKey);

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(
            privateKey,
            keccak256(
                abi.encodePacked(
                    "\x19\x01",
                    nst.DOMAIN_SEPARATOR(),
                    keccak256(abi.encode(PERMIT_TYPEHASH, owner, address(0xCAFE), 1e18, 0, block.timestamp))
                )
            )
        );

        nst.permit(owner, address(0xCAFE), 1e18, block.timestamp, v, r, s);
        vm.expectRevert("Nst/invalid-permit");
        nst.permit(owner, address(0xCAFE), 1e18, block.timestamp, v, r, s);
    }

    function testMint(address to, uint256 amount) public {
        if (to != address(0) && to != address(nst)) {
            vm.expectEmit(true, true, true, true);
            emit Transfer(address(0), to, amount);
        } else {
            vm.expectRevert("Nst/invalid-address");
        }
        nst.mint(to, amount);

        if (to != address(0) && to != address(nst)) {
            assertEq(nst.totalSupply(), amount);
            assertEq(nst.balanceOf(to), amount);
        }
    }

    function testBurn(
        address from,
        uint256 mintAmount,
        uint256 burnAmount
    ) public {
        if (from == address(0) || from == address(nst)) return;

        burnAmount = bound(burnAmount, 0, mintAmount);

        nst.mint(from, mintAmount);

        vm.expectEmit(true, true, true, true);
        emit Transfer(from, address(0), burnAmount);
        vm.prank(from);
        nst.burn(from, burnAmount);

        assertEq(nst.totalSupply(), mintAmount - burnAmount);
        assertEq(nst.balanceOf(from), mintAmount - burnAmount);
    }

    function testApprove(address to, uint256 amount) public {
        vm.expectEmit(true, true, true, true);
        emit Approval(address(this), to, amount);
        assertTrue(nst.approve(to, amount));

        assertEq(nst.allowance(address(this), to), amount);
    }

    function testTransfer(address to, uint256 amount) public {
        if (to == address(0) || to == address(nst)) return;

        nst.mint(address(this), amount);

        vm.expectEmit(true, true, true, true);
        emit Transfer(address(this), to, amount);
        assertTrue(nst.transfer(to, amount));
        assertEq(nst.totalSupply(), amount);

        if (address(this) == to) {
            assertEq(nst.balanceOf(address(this)), amount);
        } else {
            assertEq(nst.balanceOf(address(this)), 0);
            assertEq(nst.balanceOf(to), amount);
        }
    }

    function testTransferFrom(
        address to,
        uint256 approval,
        uint256 amount
    ) public {
        if (to == address(0) || to == address(nst)) return;

        amount = bound(amount, 0, approval);

        address from = address(0xABCD);

        nst.mint(from, amount);

        vm.prank(from);
        nst.approve(address(this), approval);

        vm.expectEmit(true, true, true, true);
        emit Transfer(from, to, amount);
        assertTrue(nst.transferFrom(from, to, amount));
        assertEq(nst.totalSupply(), amount);

        uint256 app = from == address(this) || approval == type(uint256).max ? approval : approval - amount;
        assertEq(nst.allowance(from, address(this)), app);

        if (from == to) {
            assertEq(nst.balanceOf(from), amount);
        } else  {
            assertEq(nst.balanceOf(from), 0);
            assertEq(nst.balanceOf(to), amount);
        }
    }

    function testPermit(
        uint248 privKey,
        address to,
        uint256 amount,
        uint256 deadline
    ) public {
        uint256 privateKey = privKey;
        if (deadline < block.timestamp) deadline = block.timestamp;
        if (privateKey == 0) privateKey = 1;

        address owner = vm.addr(privateKey);

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(
            privateKey,
            keccak256(
                abi.encodePacked(
                    "\x19\x01",
                    nst.DOMAIN_SEPARATOR(),
                    keccak256(abi.encode(PERMIT_TYPEHASH, owner, to, amount, 0, deadline))
                )
            )
        );

        vm.expectEmit(true, true, true, true);
        emit Approval(owner, to, amount);
        nst.permit(owner, to, amount, deadline, v, r, s);

        assertEq(nst.allowance(owner, to), amount);
        assertEq(nst.nonces(owner), 1);
    }

    function testBurnInsufficientBalance(
        address to,
        uint256 mintAmount,
        uint256 burnAmount
    ) public {
        if (to == address(0) || to == address(nst)) return;

        if (mintAmount == type(uint256).max) mintAmount -= 1;
        burnAmount = bound(burnAmount, mintAmount + 1, type(uint256).max);

        nst.mint(to, mintAmount);
        vm.expectRevert("Nst/insufficient-balance");
        nst.burn(to, burnAmount);
    }

    function testTransferInsufficientBalance(
        address to,
        uint256 mintAmount,
        uint256 sendAmount
    ) public {
        if (to == address(0) || to == address(nst)) return;

        if (mintAmount == type(uint256).max) mintAmount -= 1;
        sendAmount = bound(sendAmount, mintAmount + 1, type(uint256).max);

        nst.mint(address(this), mintAmount);
        vm.expectRevert("Nst/insufficient-balance");
        nst.transfer(to, sendAmount);
    }

    function testTransferFromInsufficientAllowance(
        address to,
        uint256 approval,
        uint256 amount
    ) public {
        if (to == address(0) || to == address(nst)) return;

        if (approval == type(uint256).max) approval -= 1;
        amount = bound(amount, approval + 1, type(uint256).max);

        address from = address(0xABCD);

        nst.mint(from, amount);

        vm.prank(from);
        nst.approve(address(this), approval);

        vm.expectRevert("Nst/insufficient-allowance");
        nst.transferFrom(from, to, amount);
    }

    function testTransferFromInsufficientBalance(
        address to,
        uint256 mintAmount,
        uint256 sendAmount
    ) public {
        if (to == address(0) || to == address(nst)) return;

        if (mintAmount == type(uint256).max) mintAmount -= 1;
        sendAmount = bound(sendAmount, mintAmount + 1, type(uint256).max);

        address from = address(0xABCD);

        nst.mint(from, mintAmount);

        vm.prank(from);
        nst.approve(address(this), sendAmount);

        vm.expectRevert("Nst/insufficient-balance");
        nst.transferFrom(from, to, sendAmount);
    }

    function testPermitBadNonce(
        uint128 privateKey,
        address to,
        uint256 amount,
        uint256 deadline,
        uint256 nonce
    ) public {
        if (deadline < block.timestamp) deadline = block.timestamp;
        if (privateKey == 0) privateKey = 1;
        if (nonce == 0) nonce = 1;

        address owner = vm.addr(privateKey);

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(
            privateKey,
            keccak256(
                abi.encodePacked(
                    "\x19\x01",
                    nst.DOMAIN_SEPARATOR(),
                    keccak256(abi.encode(PERMIT_TYPEHASH, owner, to, amount, nonce, deadline))
                )
            )
        );

        vm.expectRevert("Nst/invalid-permit");
        nst.permit(owner, to, amount, deadline, v, r, s);
    }

    function testPermitBadDeadline(
        uint128 privateKey,
        address to,
        uint256 amount,
        uint256 deadline
    ) public {
        if (deadline == type(uint256).max) deadline -= 1;
        if (deadline < block.timestamp) deadline = block.timestamp;
        if (privateKey == 0) privateKey = 1;

        address owner = vm.addr(privateKey);

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(
            privateKey,
            keccak256(
                abi.encodePacked(
                    "\x19\x01",
                    nst.DOMAIN_SEPARATOR(),
                    keccak256(abi.encode(PERMIT_TYPEHASH, owner, to, amount, 0, deadline))
                )
            )
        );

        vm.expectRevert("Nst/invalid-permit");
        nst.permit(owner, to, amount, deadline + 1, v, r, s);
    }

    function testPermitPastDeadline(
        uint128 privateKey,
        address to,
        uint256 amount,
        uint256 deadline
    ) public {
        if (deadline == type(uint256).max) deadline -= 1;

        // private key cannot be 0 for secp256k1 pubkey generation
        if (privateKey == 0) privateKey = 1;

        address owner = vm.addr(privateKey);

        bytes32 domain_separator = nst.DOMAIN_SEPARATOR();
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(
            privateKey,
            keccak256(
                abi.encodePacked(
                    "\x19\x01",
                    domain_separator,
                    keccak256(abi.encode(PERMIT_TYPEHASH, owner, to, amount, 0, deadline))
                )
            )
        );

        vm.warp(deadline + 1);

        vm.expectRevert("Nst/permit-expired");
        nst.permit(owner, to, amount, deadline, v, r, s);
    }

    function testPermitReplay(
        uint128 privateKey,
        address to,
        uint256 amount,
        uint256 deadline
    ) public {
        if (deadline < block.timestamp) deadline = block.timestamp;
        if (privateKey == 0) privateKey = 1;

        address owner = vm.addr(privateKey);

        (uint8 v, bytes32 r, bytes32 s) = vm.sign(
            privateKey,
            keccak256(
                abi.encodePacked(
                    "\x19\x01",
                    nst.DOMAIN_SEPARATOR(),
                    keccak256(abi.encode(PERMIT_TYPEHASH, owner, to, amount, 0, deadline))
                )
            )
        );

        nst.permit(owner, to, amount, deadline, v, r, s);
        vm.expectRevert("Nst/invalid-permit");
        nst.permit(owner, to, amount, deadline, v, r, s);
    }
}
