"""
EIP-7702 Detection Utility.

This module provides utilities to detect if an EOA has been upgraded to a smart account
via EIP-7702 delegation by checking on-chain bytecode.
"""

from typing import Any, Optional, Tuple

from web3 import Web3

from crypto_com_agent_client.lib.types.chain_helper import get_chain_helpers


def check_eip7702_delegation(w3: Web3, address: str) -> Tuple[bool, Optional[str]]:
    """
    Check if an address is an EIP-7702 delegated account by examining its bytecode.

    EIP-7702 delegated accounts have bytecode that starts with 0xEF0100 followed by
    the 20-byte delegate contract address.

    Expected bytecode format:
    0x EF 01 00 <20-byte delegate address>
    Total length: 0x + 6 hex chars (3 bytes) + 40 hex chars (20 bytes) = 48 chars

    Args:
        w3: Web3 instance connected to the blockchain
        address: The address to check

    Returns:
        Tuple[bool, Optional[str]]: (is_delegated, delegate_address)
            - is_delegated: True if the address is EIP-7702 delegated
            - delegate_address: The delegate contract address if delegated, None otherwise

    Example:
        >>> is_delegated, delegate = check_eip7702_delegation(w3, "0x123...")
        >>> if is_delegated:
        ...     print(f"Delegated to: {delegate}")
    """
    try:
        # Get the bytecode at the address
        code = w3.eth.get_code(Web3.to_checksum_address(address))

        # Convert bytes to hex string
        code_hex = code.hex() if isinstance(code, bytes) else code

        # Ensure it starts with '0x'
        if not code_hex.startswith("0x"):
            code_hex = "0x" + code_hex

        # No code means not delegated (regular EOA)
        if code_hex == "0x" or code_hex == "0x0":
            return False, None

        # Check if it's EIP-7702 delegation format
        # Expected: 0xEF0100 + 20-byte address (40 hex chars)
        # Total: 0x + 6 chars + 40 chars = 48 chars
        if len(code_hex) == 48 and code_hex[2:8].upper() == "EF0100":
            # Extract the delegate address (next 20 bytes = 40 hex chars)
            delegate_address = "0x" + code_hex[8:48]
            return True, delegate_address

        # Any other code means it's a regular contract, not EIP-7702
        return False, None

    except Exception as e:
        print(f"[EIP7702Checker] Error checking delegation for {address}: {e}")
        return False, None


def get_smart_account_addresses(
    state: dict[str, Any], addresses: list[str]
) -> dict[str, str]:
    """
    Check multiple addresses for EIP-7702 delegation and return a mapping.

    Args:
        state: The current workflow state (used to get web3 instance)
        addresses: List of addresses to check

    Returns:
        dict[str, str]: Mapping of delegated addresses to their delegate contract addresses
                       Returns empty dict if unable to connect or check

    Example:
        >>> addresses = ["0x123...", "0x456...", "0x789..."]
        >>> smart_accounts = get_smart_account_addresses(state, addresses)
        >>> print(smart_accounts)
        {'0x123...': '0xDelegate1...', '0x456...': '0xDelegate2...'}
    """
    try:
        w3, _, _ = get_chain_helpers(state)
    except Exception:
        return {}

    smart_accounts = {}

    for address in addresses:
        is_delegated, delegate_address = check_eip7702_delegation(w3, address)
        if is_delegated and delegate_address:
            smart_accounts[address] = delegate_address

    return smart_accounts
