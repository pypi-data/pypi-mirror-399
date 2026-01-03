"""
EIP-7702 related tools for the Crypto.com developer platform.

This module provides tools for EIP-7702 account delegation, allowing EOAs to
temporarily delegate execution to smart contracts for batching and gas sponsorship.

All addresses are stored and returned in lowercase format for consistency.
When interacting with web3.py, convert to checksum using Web3.to_checksum_address().
"""

import logging
from typing import Annotated

from eth_account import Account
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from web3 import Web3

from crypto_com_agent_client.lib.enums.workflow_enum import Workflow
from crypto_com_agent_client.lib.types.chain_helper import (
    ChainId,
    explorerBaseUrl_string,
    get_chain_helpers,
)
from crypto_com_agent_client.lib.utils.address import normalize_address
from crypto_com_agent_client.lib.utils.eip7702_checker import check_eip7702_delegation

logger = logging.getLogger(__name__)

# EIP-7702 delegate contract addresses per network
EIP7702_DELEGATE_CONTRACTS = {
    ChainId.CRONOS_EVM_TESTNET.value: "0xf9b064F11C07C28Db54BD45DDFcBe38DB4076C26",
    ChainId.CRONOS_EVM.value: "0xF5D0946451c71Fb25814927BC4E9e099C8235CA2",
}


@tool
def authorize_eoa_delegation(
    state: Annotated[dict, InjectedState],
    delegate_contract_address: str = None,
    authorization_nonce: int = 0,
) -> str:
    """
    Authorize the active wallet to delegate execution to a smart contract using EIP-7702.

    This upgrades the ACTIVE wallet from state to a smart account by sending a transaction
    WITH an authorizationList to set the EOA's code to the delegate contract.
    The SPONSOR wallet (from blockchain config) pays for the transaction.

    Flow:
    1. Active wallet signs the EIP-7702 authorization
    2. Sponsor wallet submits the transaction (pays gas)
    3. Active wallet becomes a smart account

    Args:
        state: The current state of the workflow
        delegate_contract_address: Optional address of the Simple7702Account contract to delegate to.
                                  If not provided, uses the network's default delegate contract.
        authorization_nonce: The nonce for this authorization (default: 0)

    Returns:
        str: A formatted string confirming the authorization with transaction hash

    Example:
        >>> result = authorize_eoa_delegation(state)
        >>> print(result)
        EIP-7702 delegation authorized! Active wallet upgraded to smart account.
    """
    try:
        w3, sponsor_wallet, chain_info = get_chain_helpers(state)
        chain_id = int(state.get("chain_id"))
    except Exception as e:
        logger.error(f"Error getting chain helpers: {e}")
        return f"Error getting chain helpers: {str(e)}"

    if delegate_contract_address is None:
        if chain_id not in EIP7702_DELEGATE_CONTRACTS:
            return f"No default EIP-7702 delegate contract configured for chain ID {chain_id}. Please provide a delegate_contract_address."
        delegate_contract_address = EIP7702_DELEGATE_CONTRACTS[chain_id]

    # Normalize delegate address to lowercase for storage/display
    try:
        delegate_contract_address = normalize_address(delegate_contract_address)
    except Exception as e:
        return f"Invalid delegate contract address: {delegate_contract_address}"

    # Convert to checksum for web3.py calls
    delegate_contract_address_checksum = Web3.to_checksum_address(
        delegate_contract_address
    )

    try:
        # Get the active wallet from state
        if Workflow.Wallets not in state or not state[Workflow.Wallets].get("Active"):
            return "No active wallet found. Please create a wallet first using 'create wallet'."

        # Addresses in state are already lowercase
        active_wallet_address = state[Workflow.Wallets]["Active"]
        wallet_list = state[Workflow.Wallets]["WalletList"]

        if active_wallet_address not in wallet_list:
            return f"Active wallet {active_wallet_address} not found in wallet list."

        active_wallet_private_key = wallet_list[active_wallet_address]["private_key"]
        # Convert to checksum for web3.py calls
        active_wallet_address_checksum = Web3.to_checksum_address(active_wallet_address)
    except Exception as e:
        logger.error(f"Error getting active wallet: {e}")
        return f"Error getting active wallet: {str(e)}"

    try:
        # Check if wallet is already delegated (use checksum for web3.py)
        is_delegated, current_delegate = check_eip7702_delegation(
            w3, active_wallet_address_checksum
        )
        if is_delegated:
            # Compare in lowercase
            current_delegate_lower = (
                current_delegate.lower() if current_delegate else ""
            )
            if current_delegate_lower == delegate_contract_address:
                return (
                    f"Wallet already upgraded!\n\n"
                    f"Wallet: {active_wallet_address}\n"
                    f"Already delegated to: {current_delegate_lower}\n\n"
                    f"No action needed. Your wallet is already a smart account."
                )
            else:
                logger.warning(
                    f"Wallet {active_wallet_address} already delegated to different contract: {current_delegate_lower}"
                )
                return (
                    f"WARNING: Wallet already delegated to a different contract!\n\n"
                    f"Wallet: {active_wallet_address}\n"
                    f"Current delegate: {current_delegate_lower}\n"
                    f"Requested delegate: {delegate_contract_address}\n\n"
                    f"Re-delegation requires incrementing authorization_nonce. "
                    f"Current implementation doesn't support this yet."
                )

        # Check if the delegate contract exists (use checksum for web3.py)
        code = w3.eth.get_code(delegate_contract_address_checksum)
        if code == b"":
            return f"No contract found at address {delegate_contract_address}. Please ensure the Simple7702Account contract is deployed."

        logger.info(
            f"Authorizing delegation for {active_wallet_address} to {delegate_contract_address}"
        )
        logger.debug(f"Authorization nonce: {authorization_nonce}")

        # Sign the EIP-7702 authorization
        active_wallet_account = Account.from_key(active_wallet_private_key)

        # Build authorization dict for the active wallet (use checksum for web3.py)
        auth = {
            "chainId": chain_id,
            "address": delegate_contract_address_checksum,
            "nonce": authorization_nonce,
        }

        signed_auth = active_wallet_account.sign_authorization(auth)

        sponsor_nonce = w3.eth.get_transaction_count(sponsor_wallet.address)

        try:
            latest_block = w3.eth.get_block("latest")
            base_fee = latest_block.get("baseFeePerGas", 0)
            max_priority_fee = w3.eth.max_priority_fee

            max_fee_per_gas = (base_fee * 2) + max_priority_fee

            logger.debug(
                f"Gas calculation - Base fee: {base_fee}, Max priority: {max_priority_fee}, Max fee: {max_fee_per_gas}"
            )
        except Exception as e:
            # Fallback if network doesn't support EIP-1559
            logger.warning(f"Failed to get EIP-1559 gas prices, using fallback: {e}")
            gas_price = w3.eth.gas_price or 0
            max_fee_per_gas = gas_price * 2
            max_priority_fee = gas_price

        # Build the type 0x04 transaction with authorizationList (use checksum for web3.py)
        transaction = {
            "type": 0x04,  # EIP-7702 transaction type
            "chainId": chain_id,
            "nonce": sponsor_nonce,
            "to": active_wallet_address_checksum,
            "value": 0,
            "data": "0x",
            "gas": 1_000_000,
            "maxFeePerGas": max_fee_per_gas,
            "maxPriorityFeePerGas": max_priority_fee,
            "authorizationList": [signed_auth],
        }

        # Sign and send the EIP-7702 transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, sponsor_wallet.key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        logger.info(f"Transaction sent: 0x{tx_hash.hex()}")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        tx_link = (
            f"{chain_info[explorerBaseUrl_string]}/tx/0x{receipt.transactionHash.hex()}"
        )

        # Check if transaction failed
        if receipt.status != 1:
            logger.error(f"EIP-7702 delegation transaction failed. Receipt: {receipt}")
            return (
                f"Transaction failed!\n\n"
                f"Wallet: {active_wallet_address}\n"
                f"Delegate Contract: {delegate_contract_address}\n"
                f"Gas Used: {receipt.gasUsed}\n\n"
                f"Explorer: {tx_link}\n\n"
                f"Check the transaction details for more information."
            )

        logger.info(
            f"Successfully delegated {active_wallet_address} to {delegate_contract_address}"
        )

        # Display lowercase addresses in output
        return (
            f"EIP-7702 delegation authorized!\n\n"
            f"Upgraded Wallet: {active_wallet_address}\n"
            f"Delegate Contract: {delegate_contract_address}\n"
            f"Status: Success\n"
            f"Gas Used: {receipt.gasUsed}\n\n"
            f"Explorer: {tx_link}\n\n"
            f"Your wallet is now a smart account!\n"
        )

    except Exception as e:
        logger.exception(f"Unexpected error creating EIP-7702 authorization: {e}")
        return f"Error creating EIP-7702 authorization: {str(e)}"
