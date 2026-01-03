"""
Address normalization utilities.

This module provides utilities for normalizing Ethereum addresses to lowercase format.
All addresses in the codebase should be normalized using these utilities to ensure
consistent comparison and storage.
"""

from web3 import Web3


def normalize_address(address: str) -> str:
    """
    Normalize an Ethereum address to lowercase format.

    This function validates that the input is a valid Ethereum address
    and returns it in lowercase format for consistent handling.

    Args:
        address (str): The Ethereum address to normalize (can be checksum or lowercase).

    Returns:
        str: The normalized lowercase address with 0x prefix.

    Raises:
        ValueError: If the address is not a valid Ethereum address.

    Example:
        >>> normalize_address("0x5C7F8A570d578ED84E63fdFA7b1eE72dEae1AE23")
        '0x5c7f8a570d578ed84e63fdfa7b1ee72deae1ae23'
        >>> normalize_address("0x5c7f8a570d578ed84e63fdfa7b1ee72deae1ae23")
        '0x5c7f8a570d578ed84e63fdfa7b1ee72deae1ae23'
    """
    if not address:
        raise ValueError("Address cannot be empty")

    # Remove any whitespace
    address = address.strip()

    # Validate the address is a valid Ethereum address
    if not Web3.is_address(address):
        raise ValueError(f"Invalid Ethereum address: {address}")

    # Return lowercase address
    return address.lower()


def is_valid_address(address: str) -> bool:
    """
    Check if the given string is a valid Ethereum address.

    Args:
        address (str): The string to check.

    Returns:
        bool: True if the address is valid, False otherwise.

    Example:
        >>> is_valid_address("0x5C7F8A570d578ED84E63fdFA7b1eE72dEae1AE23")
        True
        >>> is_valid_address("invalid")
        False
    """
    if not address:
        return False
    try:
        return Web3.is_address(address.strip())
    except Exception:
        return False


def addresses_equal(addr1: str, addr2: str) -> bool:
    """
    Compare two Ethereum addresses for equality (case-insensitive).

    Args:
        addr1 (str): First address to compare.
        addr2 (str): Second address to compare.

    Returns:
        bool: True if the addresses are equal, False otherwise.

    Example:
        >>> addresses_equal("0x5C7F8A570d578ED84E63fdFA7b1eE72dEae1AE23",
        ...                 "0x5c7f8a570d578ed84e63fdfa7b1ee72deae1ae23")
        True
    """
    if not addr1 or not addr2:
        return False
    try:
        return normalize_address(addr1) == normalize_address(addr2)
    except ValueError:
        return False
