"""
Token-related tools for the Crypto.com developer platform.
"""

from decimal import Decimal
from typing import Annotated, Optional, Tuple

from crypto_com_developer_platform_client import Token
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from web3 import Web3

from crypto_com_agent_client.config.constants import DEFAULT_TRANSFER_LIMIT
from crypto_com_agent_client.lib.enums.workflow_enum import Workflow
from crypto_com_agent_client.lib.types.chain_helper import (
    erc20Abi_string,
    explorerBaseUrl_string,
    get_chain_helpers,
    routerAbi_string,
    routerAddress_string,
    wrapperAbi_string,
    wrapperAddress_string,
)
from crypto_com_agent_client.lib.types.token_helper import parse_token
from crypto_com_agent_client.lib.utils.address import normalize_address


def check_transfer_limit(state: dict, amount: float) -> Tuple[bool, Optional[str]]:
    """
    Check if the transfer amount is within the configured limit.

    Args:
        state: The workflow state containing transfer_limit
        amount: The amount to transfer

    Returns:
        Tuple of (is_allowed, error_message). If allowed, error_message is None.
    """
    transfer_limit = state.get(Workflow.TransferLimit, DEFAULT_TRANSFER_LIMIT)

    # -1 means unlimited
    if transfer_limit == -1:
        return True, None

    # 0 means transfers disabled
    if transfer_limit == 0:
        return False, "Transfers are disabled (transfer-limit is set to 0)"

    # Check against limit
    if amount > transfer_limit:
        return False, (
            f"Transfer amount {amount} exceeds the limit of {transfer_limit}. "
            f"To increase the limit, set 'transfer-limit' in blockchain_config. "
            f"Use -1 for unlimited."
        )

    return True, None


@tool
def get_native_balance(
    address: str, use_wei: bool = True, decimal_places: int = None
) -> str:
    """
    Get the native token balance of a given blockchain address.

    This function queries the native token balance for the specified blockchain
    address using the Crypto.com developer platform.

    Args:
        address (str): The blockchain address to query.
        use_wei (bool): If True, returns balance in WEI. If False, returns balance in CRO.
                       1 CRO = 10^18 WEI. Defaults to True.
        decimal_places (int, optional): Number of decimal places to show in the result.
                                      If None (default), shows all available digits.
                                      Only applies when use_wei=False (CRO format).
                                      Example: decimal_places=2 shows "123.45 CRO"

    Returns:
        str: A formatted string containing the native token balance for the address.

    Example:
        >>> balance = get_native_balance("0x123...")
        >>> print(balance)
        The native balance for address 0x123... is 100.0 WEI.

        >>> balance = get_native_balance("0x123...", use_wei=False)
        >>> print(balance)
        The native balance for address 0x123... is 0.0001 CRO.

        >>> balance = get_native_balance("0x123...", use_wei=False, decimal_places=2)
        >>> print(balance)
        The native balance for address 0x123... is 0.00 CRO.
    """
    # Normalize address to lowercase
    address = normalize_address(address)
    response = Token.get_native_balance(address)

    # Extract balance from JSON response
    if isinstance(response, dict) and response.get("status") == "Success":
        balance = response["data"]["balance"]
    else:
        return f"Error retrieving balance"
    if not use_wei:
        # Use Decimal for precise arithmetic to avoid precision loss
        balance_decimal = Decimal(str(balance)) / Decimal(str(10**18))  # 10^18
        unit = "CRO"
        # Format balance with specified decimal places
        if decimal_places is not None:
            balance_decimal = balance_decimal.quantize(
                Decimal("0." + "0" * decimal_places)
            )
            balance_str = f"{balance_decimal:.{decimal_places}f}"
        else:
            balance_str = str(balance_decimal)
    else:
        unit = "WEI"
        balance_str = str(balance)
    return f"The native balance for address {address} is {balance_str} {unit}."


@tool
def get_erc20_balance(address: str, contract_address: str) -> str:
    """
    Retrieve the ERC20 token balance for a specific address and contract.

    This function queries the ERC20 token balance for the specified blockchain
    address and ERC20 contract address.

    Args:
        address (str): The blockchain address to query.
        contract_address (str): The contract address of the ERC20 token.

    Returns:
        str: A formatted string containing the ERC20 token balance for the address.

    Example:
        >>> erc20_balance = get_erc20_balance("0x123...", "0xcontract...")
        >>> print(erc20_balance)
        The ERC20 balance for address 0x123... (contract: 0xcontract...) is 500.0.
    """
    # Normalize addresses to lowercase
    address = normalize_address(address)
    contract_address = normalize_address(contract_address)
    balance = Token.get_erc20_balance(
        wallet_address=address,
        contract_address=contract_address,
    )
    return f"The ERC20 balance for address {address} (contract: {contract_address}) is {balance}."


@tool
def transfer_native_token(
    state: Annotated[dict, InjectedState], to: str, amount: float
) -> str:
    """
    Transfers native tokens (cro, CRO, tcro, tCRO, zkcro, zkCRO, zktcro, zkTCRO) to a specified address.

    Args:
        state (dict): The current state of the workflow
        to (str): The recipient's blockchain address.
        amount (float): The amount of native tokens to transfer.

    Returns:
        str: A formatted string confirming the success of the token transfer.
    """
    # Normalize address to lowercase for storage/display
    to = normalize_address(to)

    # Check transfer limit
    is_allowed, error_msg = check_transfer_limit(state, amount)
    if not is_allowed:
        return f"Transfer blocked: {error_msg}"

    try:
        w3, account, chain_info = get_chain_helpers(state)
        chain_id = int(
            state.get("chain_id")
        )  # Convert to int - Web3 expects integer chainId
    except Exception as e:
        print(f"Error getting chain helpers: {str(e)}")
        return f"Error getting chain helpers: {str(e)}"

    try:
        # Native token transfer
        amount_in_wei = w3.to_wei(amount, "ether")

        # Convert to checksum for web3.py
        to_checksum = Web3.to_checksum_address(to)

        transaction = {
            "to": to_checksum,
            "value": amount_in_wei,
            "from": account.address,
            "gasPrice": w3.eth.gas_price,
            "nonce": w3.eth.get_transaction_count(account.address),
            "chainId": chain_id,
        }

        estimated_gas = w3.eth.estimate_gas(transaction)
        transaction["gas"] = int(estimated_gas * 1.2)  # Add 20% buffer

        signed_txn = w3.eth.account.sign_transaction(transaction, account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        tx_hash_hex = f"0x{receipt.transactionHash.hex()}"
        tx_link = f"{chain_info[explorerBaseUrl_string]}/tx/{tx_hash_hex}"

        return f"Native token transfer successful, tx_hash: {tx_hash_hex}, tx_link: {tx_link}"
    except Exception as e:
        error_msg = str(e)
        if "gas" in error_msg.lower():
            return (
                f"Error transferring native token: Gas estimation failed. This could be due to:\n"
                f"1. Insufficient funds for gas\n"
                f"2. Contract execution would fail\n"
                f"3. Network congestion\n"
                f"Original error: {error_msg}"
            )
        print(f"Error transferring native token: {e}")
        return f"Error transferring native token: {e}"


@tool
def transfer_erc20_token(
    state: Annotated[dict, InjectedState],
    to: str,
    amount: float,
    token_symbol_or_address: str,
) -> str:
    """
    Transfers ERC20 tokens to a specified address.

    Args:
        state (dict): The current state of the workflow
        to (str): The recipient's blockchain address.
        amount (float): The amount of tokens to transfer.
        token_symbol_or_address (str): The ERC20 token symbol or contract address.

    Returns:
        str: A formatted string confirming the success of the token transfer.
    """
    # Normalize address to lowercase for storage/display
    to = normalize_address(to)

    # Check transfer limit
    is_allowed, error_msg = check_transfer_limit(state, amount)
    if not is_allowed:
        return f"Transfer blocked: {error_msg}"

    try:
        w3, account, chain_info = get_chain_helpers(state)
        chain_id = int(
            state.get("chain_id")
        )  # Convert to int - Web3 expects integer chainId
    except Exception as e:
        print(f"Error getting chain helpers: {str(e)}")
        return f"Error getting chain helpers: {str(e)}"

    try:
        try:
            token_info = parse_token(w3, chain_info, token_symbol_or_address)
        except Exception as e:
            print(f"Error parsing tokens: {str(e)}")
            return f"Error parsing tokens: {str(e)}"

        # Convert to checksum for web3.py contract interaction
        token_address_checksum = Web3.to_checksum_address(token_info["address"])
        token_contract = w3.eth.contract(
            address=token_address_checksum, abi=chain_info[erc20Abi_string]
        )

        decimals = token_contract.functions.decimals().call()
        amount_in_wei = int(amount * (10**decimals))

        # Convert to checksum for web3.py
        to_checksum = Web3.to_checksum_address(to)

        transaction = token_contract.functions.transfer(
            to_checksum, amount_in_wei
        ).build_transaction(
            {
                "from": account.address,
                "nonce": w3.eth.get_transaction_count(account.address),
                "gasPrice": w3.eth.gas_price,
                "chainId": chain_id,
            }
        )

        estimated_gas = w3.eth.estimate_gas(transaction)
        transaction["gas"] = int(estimated_gas * 1.2)  # Add 20% buffer

        signed_txn = w3.eth.account.sign_transaction(transaction, account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        tx_hash_hex = f"0x{receipt.transactionHash.hex()}"
        tx_link = f"{chain_info[explorerBaseUrl_string]}/tx/{tx_hash_hex}"

        return f"ERC20 token transfer successful, tx_hash: {tx_hash_hex}, tx_link: {tx_link}"
    except Exception as e:
        error_msg = str(e)
        if "gas" in error_msg.lower():
            return (
                f"Error transferring ERC20 token: Gas estimation failed. This could be due to:\n"
                f"1. Insufficient funds for gas\n"
                f"2. Contract execution would fail\n"
                f"3. Network congestion\n"
                f"Original error: {error_msg}"
            )
        print(f"Error transferring ERC20 token: {e}")
        return f"Error transferring ERC20 token: {e}"


@tool
def wrap_token(state: Annotated[dict, InjectedState], amount: float) -> str:
    """
    Wrap native tokens into wrapped tokens.

    Args:
        state (dict): The current state of the workflow
        amount (float): The amount of native tokens to wrap.

    Returns:
        str: A formatted string confirming the success of the wrapping operation.
    """
    try:
        w3, account, chain_info = get_chain_helpers(state)
        chain_id = int(
            state.get("chain_id")
        )  # Convert to int - Web3 expects integer chainId

        # Convert to checksum for web3.py contract interaction
        weth_address = Web3.to_checksum_address(chain_info[wrapperAddress_string])
        contract = w3.eth.contract(
            address=weth_address, abi=chain_info[wrapperAbi_string]
        )
        amount_in_wei = w3.to_wei(amount, "ether")

        transaction = contract.functions.deposit().build_transaction(
            {
                "from": account.address,
                "value": amount_in_wei,
                "nonce": w3.eth.get_transaction_count(account.address),
                "gasPrice": w3.eth.gas_price,
                "chainId": chain_id,
            }
        )

        estimated_gas = w3.eth.estimate_gas(transaction)
        transaction["gas"] = int(estimated_gas * 1.2)

        signed_txn = w3.eth.account.sign_transaction(transaction, account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        tx_hash_hex = f"0x{receipt.transactionHash.hex()}"
        tx_link = f"{chain_info[explorerBaseUrl_string]}/tx/{tx_hash_hex}"

        return f"Token wrapping successful, tx_hash: {tx_hash_hex}, tx_link: {tx_link}"
    except Exception as e:
        print(f"Error wrapping token: {e}")
        return f"Error wrapping token: {e}"


@tool
def swap_token(
    state: Annotated[dict, InjectedState],
    from_token_symbol_or_address: str,
    to_token_symbol_or_address: str,
    amountIn: float,
) -> str:
    """
    Swap tokens between two different tokens.

    Args:
        state: The current state of the workflow
        from_token_symbol_or_address (str): The symbol or contract address of the token to swap from
        to_token_symbol_or_address (str): The symbol or contract address of the token to swap to
        amountIn (float): The amount of tokens to swap

    Returns:
        str: A formatted string confirming the success of the token swap
    """
    try:
        w3, account, chain_info = get_chain_helpers(state)
        chain_id = int(
            state.get("chain_id")
        )  # Convert to int - Web3 expects integer chainId
    except Exception as e:
        print(f"Error getting chain helpers: {str(e)}")
        return f"Error getting chain helpers: {str(e)}"

    try:
        from_token = parse_token(w3, chain_info, from_token_symbol_or_address)
        to_token = parse_token(w3, chain_info, to_token_symbol_or_address)
    except Exception as e:
        print(f"Error parsing tokens: {str(e)}")
        return f"Error parsing tokens: {str(e)}"

    try:
        # Convert addresses to checksum for web3.py
        router_address = Web3.to_checksum_address(chain_info[routerAddress_string])
        from_token_address = Web3.to_checksum_address(from_token["address"])
        to_token_address = Web3.to_checksum_address(to_token["address"])

        try:
            router = w3.eth.contract(
                address=router_address, abi=chain_info[routerAbi_string]
            )
            from_token_contract = w3.eth.contract(
                address=from_token_address, abi=chain_info[erc20Abi_string]
            )
        except Exception as e:
            return f"Error initializing contracts: {str(e)}"

        # Check token balance and allowance
        try:
            decimals = from_token_contract.functions.decimals().call()
            amount_in_wei = int(amountIn * (10**decimals))

            token_balance = from_token_contract.functions.balanceOf(
                account.address
            ).call()
            if token_balance < amount_in_wei:
                return f"Insufficient token balance. Have: {token_balance}, Need: {amount_in_wei}"

            current_allowance = from_token_contract.functions.allowance(
                account.address, router_address
            ).call()
        except Exception as e:
            print(f"Error checking balance/allowance: {str(e)}")
            return f"Error checking balance/allowance: {str(e)}"

        # Approve router if needed
        if current_allowance < amount_in_wei:
            try:
                approve_tx = from_token_contract.functions.approve(
                    router_address, amount_in_wei
                ).build_transaction(
                    {
                        "from": account.address,
                        "nonce": w3.eth.get_transaction_count(account.address),
                        "gasPrice": w3.eth.gas_price,
                        "chainId": chain_id,
                    }
                )

                estimated_approve_gas = w3.eth.estimate_gas(approve_tx)
                approve_tx["gas"] = int(estimated_approve_gas * 1.2)

                signed_approve = w3.eth.account.sign_transaction(
                    approve_tx, account.key
                )
                approve_hash = w3.eth.send_raw_transaction(
                    signed_approve.raw_transaction
                )
                approve_receipt = w3.eth.wait_for_transaction_receipt(approve_hash)
            except Exception as e:
                print(f"Error during token approval: {str(e)}")
                return f"Error during token approval: {str(e)}"

        # Perform swap
        try:
            swap_tx = router.functions.swapExactTokensForTokens(
                amount_in_wei,
                0,
                [from_token_address, to_token_address],
                account.address,
            ).build_transaction(
                {
                    "from": account.address,
                    "nonce": w3.eth.get_transaction_count(account.address),
                    "gasPrice": w3.eth.gas_price,
                    "chainId": chain_id,
                    "value": 0,
                }
            )

            estimated_swap_gas = w3.eth.estimate_gas(swap_tx)
            swap_tx["gas"] = int(estimated_swap_gas * 1.2)

            signed_swap = w3.eth.account.sign_transaction(swap_tx, account.key)
            tx_hash = w3.eth.send_raw_transaction(signed_swap.raw_transaction)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

            tx_hash_hex = f"0x{receipt.transactionHash.hex()}"
            tx_link = f"{chain_info[explorerBaseUrl_string]}/tx/{tx_hash_hex}"
            return f"Token swap successful, tx_hash: {tx_hash_hex}, tx_link: {tx_link}"
        except Exception as e:
            print(f"Error during swap execution: {str(e)}")
            return f"Error during swap execution: {str(e)}"

    except Exception as e:
        print(f"Error swapping token: {e}")
        return f"Error swapping token: {e}"
