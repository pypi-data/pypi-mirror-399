"""
Wallet-related tools for the Crypto.com developer platform.

All addresses are stored and returned in lowercase format for consistency.
"""

from datetime import datetime
from typing import Annotated

from crypto_com_developer_platform_client import Wallet
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from crypto_com_agent_client.core.tools.eip7702 import EIP7702_DELEGATE_CONTRACTS
from crypto_com_agent_client.lib.enums.workflow_enum import Workflow
from crypto_com_agent_client.lib.utils.address import normalize_address
from crypto_com_agent_client.lib.utils.eip7702_checker import (
    get_smart_account_addresses,
)


@tool
def create_wallet(state: Annotated[dict, InjectedState]) -> str:
    """
    Create a new wallet and return its address and private key.

    This function interacts with the Crypto.com developer platform to create a new
    blockchain wallet. It retrieves the wallet's address and private key.

    After creating the wallet, it offers EIP-7702 delegation to enable batch transactions
    and gas sponsorship features.

    The wallet is automatically stored in state and set as the active wallet.
    The wallet dictionary stored in state contains:
        - address (str): The wallet's blockchain address
        - private_key (str): The wallet's private key
        - created_at (str): ISO format timestamp of when the wallet was created

    Args:
        state: The current state of the workflow

    Returns:
        str: A formatted string containing the wallet's address, private key, and EIP-7702 prompt.

    Example:
        >>> wallet_info = create_wallet(state)
        >>> print(wallet_info)
        Wallet created! Address: 0x123..., Private Key: abcd...
        Want to enable batch transactions? Reply 'yes' to authorize EIP-7702.
    """

    wallet = Wallet.create_wallet()
    # Normalize address to lowercase for consistent storage
    address = normalize_address(wallet["data"]["address"])
    private_key = wallet["data"]["privateKey"]

    if Workflow.Wallets not in state:
        state[Workflow.Wallets] = {"Active": "", "WalletList": {}}

    # Add wallet to the dictionary (keyed by address)
    state[Workflow.Wallets]["WalletList"][address] = {
        "address": address,
        "private_key": private_key,
        "created_at": datetime.now().isoformat(),
    }

    # Set as active wallet
    state[Workflow.Wallets]["Active"] = address

    # Get network information for EIP-7702 prompt
    chain_id = int(state.get(Workflow.ChainID, 338))

    # Get EIP-7702 contract for this network
    delegate_contract = EIP7702_DELEGATE_CONTRACTS.get(chain_id)

    eip7702_section = ""
    if delegate_contract:
        eip7702_section = (
            f"Unlock superpowers with EIP-7702:\n"
            f"• Batch transactions\n"
            f"• Gas savings\n"
            f"• Smart account features\n\n"
            f'Enable: reply "yes" or "authorize eip 7702"\n'
            f'Skip: reply "no" or continue\n\n'
        )

    # Return response
    return (
        f"Wallet created!\n\n"
        f"Address: {address}\n\n"
        f"Private Key: {private_key}\n\n"
        f"WARNING: Keep your private key secure! Never share it.\n\n"
        f"{eip7702_section}"
        f"This is now your active wallet."
    )


@tool
def get_wallet_balance(address: str) -> str:
    """
    Get the balance of a wallet.

    This function retrieves the balance of a specified wallet address
    using the Crypto.com developer platform.

    Args:
        address (str): The address to get the balance for (e.g., "xyz.cro").

    Returns:
        str: A formatted string containing the wallet balance.

    Example:
        >>> balance = get_wallet_balance("0x123...")
        >>> print(balance)
        Balance for wallet 0x123...: {...}
    """
    # Normalize address to lowercase
    address = normalize_address(address)
    balance = Wallet.get_balance(address)
    return f"Balance for wallet {address}: {balance}"


@tool
def list_wallets(state: Annotated[dict, InjectedState]) -> str:
    """
    List all wallets stored in the current session.

    This function displays all wallets that have been created in the current session,
    showing their addresses, labels, and which one is currently active.

    Args:
        state: The current state of the workflow

    Returns:
        str: A formatted string listing all wallets with their details.

    Example:
        >>> wallets = list_wallets(state)
        >>> print(wallets)
        You have 2 wallets:
        1. Wallet 1: 0x123... (Active)
        2. Wallet 2: 0x456...
    """
    if Workflow.Wallets not in state:
        state[Workflow.Wallets] = {"Active": "", "WalletList": {}}

    wallet_dict = state[Workflow.Wallets]["WalletList"]
    active_wallet = state[Workflow.Wallets]["Active"]

    if not wallet_dict:
        return 'Your Wallets (0)\n\nYou don\'t have any wallets yet.\n\nCreate one by saying: "create wallet"'

    # Check on-chain which wallets are smart accounts (EIP-7702 delegated)
    smart_account_addresses = get_smart_account_addresses(
        state, list(wallet_dict.keys())
    )

    # Build display list from dictionary values
    display_list = []
    for idx, (address, wallet) in enumerate(wallet_dict.items(), start=1):
        labels = []
        is_active = address == active_wallet

        # Check if it's a smart account (on-chain)
        if address in smart_account_addresses:
            labels.append("Smart account")

        # Format the display with (Active) prepended for active wallet
        prefix = "(Active) " if is_active else ""
        if labels:
            label_str = " (" + ", ".join(labels) + ")"
            display_list.append(f"{idx}. {prefix}{address}{label_str}")
        else:
            display_list.append(f"{idx}. {prefix}{address}")

    return (
        f"Your Wallets ({len(wallet_dict)})\n\n"
        + "\n\n".join(display_list)
        + '\n\nSwitch wallet: "switch to [address]"'
    )


@tool
def switch_wallet(state: Annotated[dict, InjectedState], address: str) -> str:
    """
    Switch the active wallet to a different wallet.

    This function changes which wallet is used for all blockchain operations.
    The wallet must exist in the current session.

    Args:
        state: The current state of the workflow
        address: The address of the wallet to switch to

    Returns:
        str: A confirmation message with the new active wallet.

    Example:
        >>> result = switch_wallet(state, "0x123...")
        >>> print(result)
        Switched to wallet 0x123...
    """
    # Normalize address to lowercase for lookup
    address = normalize_address(address)

    if Workflow.Wallets not in state:
        state[Workflow.Wallets] = {"Active": "", "WalletList": {}}

    wallet_dict = state[Workflow.Wallets]["WalletList"]

    # Check if wallet exists
    if address not in wallet_dict:
        available = "\n".join([f"• {addr}" for addr in wallet_dict.keys()])
        if not available:
            return 'You don\'t have any wallets yet.\n\nCreate one by saying: "create wallet"'
        return (
            f"Wallet {address} not found.\n\n"
            f"Available wallets:\n{available}\n\n"
            'Use "list wallets" to see all wallets.'
        )

    # Switch to the wallet
    state[Workflow.Wallets]["Active"] = address

    # Check on-chain if it's a smart account (EIP-7702 delegated)
    smart_accounts = get_smart_account_addresses(state, [address])
    is_smart_account = address in smart_accounts

    account_type = " (Smart account)" if is_smart_account else ""

    return f"Switched to wallet\n\n{address}{account_type}\n\nThis wallet will now be used for all operations."


@tool
def delete_wallet(state: Annotated[dict, InjectedState], address: str) -> str:
    """
    Delete a wallet from the current session.

    This function removes a specified wallet from the current session.
    The wallet must exist in the current session.
    If the deleted wallet is the active wallet, another wallet will be automatically set as active.
    """
    # Normalize address to lowercase for lookup
    address = normalize_address(address)

    if Workflow.Wallets not in state:
        state[Workflow.Wallets] = {"Active": "", "WalletList": {}}

    wallet_dict = state[Workflow.Wallets]["WalletList"]
    active_wallet = state[Workflow.Wallets]["Active"]

    if address not in wallet_dict:
        return 'Wallet not found.\n\nUse "list wallets" to see all wallets.'

    # Check if the wallet being deleted is the active one
    was_active = address == active_wallet

    # Delete the wallet
    del wallet_dict[address]

    # If the deleted wallet was active, switch to another wallet
    if was_active:
        if wallet_dict:
            # Set the first available wallet as active
            new_active = next(iter(wallet_dict.keys()))
            state[Workflow.Wallets]["Active"] = new_active

            # Check on-chain if the new active wallet is a smart account (EIP-7702 delegated)
            smart_accounts = get_smart_account_addresses(state, [new_active])
            is_smart_account = new_active in smart_accounts

            account_type = " (Smart account)" if is_smart_account else ""

            return (
                f"Deleted wallet\n\n{address}\n\n"
                f"Switched to:\n{new_active}{account_type}\n\n"
                "This wallet is now your active wallet."
            )
        else:
            # No wallets left
            state[Workflow.Wallets]["Active"] = ""
            return (
                f"Deleted wallet\n\n{address}\n\n"
                'This was your last wallet. Create a new one with: "create wallet"'
            )

    return f"Deleted wallet\n\n{address}\n\nThis wallet has been removed from the current session."


@tool
def send_ssowallet(
    state: Annotated[dict, InjectedState], receiver: str, amount: int, data: str = "0x"
) -> str:
    """
    Generate a URL for SSO wallet transfer.

    This function generates a URL that can be used to initiate a token transfer
    through the SSO wallet interface. If "null" is specified as the receiver,
    it will use the null address (0x0000000000000000000000000000000000000000).

    Args:
        receiver (str): The recipient's blockchain address or "null" for null address.
        amount (int): The amount of tokens to transfer in Wei.
        data (str, optional): Additional data for the transfer. Defaults to "0x".

    Returns:
        str: A formatted URL for the SSO wallet transfer.

    Example:
        >>> url = send_ssowallet("null", 1)  # Send 1 Wei to null address
        >>> print(url)
        http://your-sso-wallet-url/transfer-token?recipient=0x0000000000000000000000000000000000000000&amount=1&data=0x
        >>> url = send_ssowallet("0x123...", 1000000000000000000)  # 1 ETH in Wei
        >>> print(url)
        http://your-sso-wallet-url/transfer-token?recipient=0x123...&amount=1000000000000000000&data=0x
    """
    sso_wallet_url = state[Workflow.SSOWalletURL]
    base_url = f"{sso_wallet_url}/transfer-token"

    # Handle null address case
    if receiver.lower() == "null":
        receiver = "0x" + "0" * 40  # Creates 0x0000000000000000000000000000000000000000
    else:
        # Normalize address to lowercase
        receiver = normalize_address(receiver)

    url = f"{base_url}?recipient={receiver}&amount={amount}&data={data}"
    return url
