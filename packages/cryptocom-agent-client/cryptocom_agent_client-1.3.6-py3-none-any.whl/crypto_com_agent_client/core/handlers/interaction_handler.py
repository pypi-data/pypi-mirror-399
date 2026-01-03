"""
InteractionHandler Module.

This module defines the `InteractionHandler` class, which handles user interaction
logic for the LangGraph-based workflow.
"""

# Standard library imports
import os
import signal
from datetime import datetime
from typing import Optional

from crypto_com_developer_platform_client import Client, Network
from eth_account import Account

# Third-party imports
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

# Internal application imports
from crypto_com_agent_client.lib.enums.workflow_enum import Workflow
from crypto_com_agent_client.lib.types.blockchain_config import BlockchainConfig
from crypto_com_agent_client.lib.types.memory_config import DefaultMemoryConfigs
from crypto_com_agent_client.lib.utils.memory_manager import MemoryManager
from crypto_com_agent_client.lib.utils.storage import Storage
from crypto_com_agent_client.lib.utils.token_usage import print_workflow_token_usage


class InteractionHandler:
    """
    The `InteractionHandler` class manages user interactions with the LangGraph workflow.
    It handles state management, user input processing, and response generation.

    Attributes:
        app (CompiledStateGraph): The compiled LangGraph workflow.
        storage (Storage): The storage backend for persisting workflow state.
        blockchain_config (BlockchainConfig): Configuration for blockchain interactions.
        debug_logging (bool): Flag to control debug logging output.

    Example:
        >>> handler = InteractionHandler(
        ...     app=compiled_workflow,
        ...     storage=storage_instance,
        ...     blockchain_config=blockchain_config,
        ...     debug_logging=True
        ... )
        >>> response = handler.interact("Hello!", thread_id=42)
    """

    def __init__(
        self,
        app: CompiledStateGraph,
        storage: Storage,
        blockchain_config: BlockchainConfig,
        debug_logging: bool = False,
        memory_manager: Optional[MemoryManager] = None,
    ) -> None:
        """
        Initialize the InteractionHandler.

        Args:
            app (CompiledStateGraph): The compiled LangGraph workflow.
            storage (Storage): The storage backend for persisting workflow state.
            blockchain_config (BlockchainConfig): Configuration for blockchain interactions.
            debug_logging (bool): Enable/disable debug logging for interactions.
            memory_manager (Optional[MemoryManager]): Memory manager for conversation pruning.
        """
        self.app: CompiledStateGraph = app
        self.storage: Storage = storage
        self.blockchain_config: BlockchainConfig = blockchain_config
        self.debug_logging: bool = debug_logging

        # Initialize memory manager for conversation history management
        self.memory_manager = memory_manager or MemoryManager(
            DefaultMemoryConfigs.balanced()
        )

    def _get_chain_id_from_developer_platform(self) -> Optional[str]:
        """
        Get chain ID from Crypto.com Developer Platform with configurable timeout.

        Returns:
            Optional[str]: The chain ID if successful, None otherwise.
        """

        def timeout_handler(signum, frame):
            raise TimeoutError("API call timed out")

        try:
            # Get API key from blockchain config
            api_key = self.blockchain_config.api_key

            if not api_key:
                if self.debug_logging:
                    print("Warning: API key is not available in blockchain config")
                return None

            # Initialize the client with the API key
            Client.init(api_key=api_key)

            # Set up timeout using the configurable timeout from blockchain_config
            timeout_seconds = self.blockchain_config.timeout
            original_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)

            if self.debug_logging:
                print(
                    f"Using timeout of {timeout_seconds} seconds for developer platform API call"
                )

            try:
                # Get the chain ID
                chain_id_response = Network.chain_id()

                # Cancel the timeout
                signal.alarm(0)
                signal.signal(signal.SIGALRM, original_handler)

                if self.debug_logging:
                    print(
                        f"Chain ID response from developer platform: {chain_id_response}"
                    )

                # Extract the actual chain ID from the response
                # Expected response format: {'status': 'Success', 'data': {'chainId': '338'}}
                if isinstance(chain_id_response, dict):
                    # Check if the response has a 'data' field with 'chainId'
                    if "data" in chain_id_response and isinstance(
                        chain_id_response["data"], dict
                    ):
                        chain_id = chain_id_response["data"].get("chainId")
                    else:
                        chain_id = chain_id_response.get("chainId")

                    if chain_id is None:
                        if self.debug_logging:
                            print(
                                f"Could not extract chainId from response: {chain_id_response}"
                            )
                        return None

                    return str(chain_id)
                else:
                    # If it's already a simple value, return it as string
                    return str(chain_id_response)

            except (TimeoutError, Exception) as e:
                # Cancel the timeout
                signal.alarm(0)
                signal.signal(signal.SIGALRM, original_handler)
                raise e

        except Exception as e:
            if self.debug_logging:
                print(f"Error getting chain ID from developer platform: {e}")
            return None

    def interact(self, user_input: str, thread_id: int) -> str:
        """
        Processes user input and returns the generated response.

        Args:
            user_input (str): The user's input message.
            thread_id (int, optional): A thread ID for contextual execution.

        Returns:
            str: The response generated by the workflow.

        Raises:
            ValueError: If the workflow graph is not initialized.
        """
        if not self.app:
            raise ValueError("The workflow graph is not initialized.")

        # Load state from storage or initialize it
        loaded_state = self.storage.load_state(thread_id)
        loaded_messages = loaded_state.get(Workflow.Messages, []).copy()

        if self.debug_logging:
            print(f"LOADED: {len(loaded_messages)} messages (thread {thread_id})")

        # Track initial message count to identify new messages
        initial_message_count = len(loaded_messages)

        # Add user input to the loaded messages
        loaded_messages.append(HumanMessage(content=user_input))

        # Pre-processing: Only prune if needed to fit context window (no summarization yet)
        # This ensures we don't double-summarize (once here, once after workflow)
        if loaded_messages:
            total_tokens = self.memory_manager.token_counter.count_messages_tokens(
                loaded_messages
            )
            max_context = self.memory_manager.config.max_context_tokens

            if total_tokens > max_context:
                # Only prune to fit context window, don't summarize yet
                pruned_messages = self.memory_manager.prune_conversation(
                    loaded_messages
                )
                if self.debug_logging:
                    print(
                        f"PRE-PRUNE: {len(loaded_messages)} -> {len(pruned_messages)} messages ({total_tokens} -> {self.memory_manager.token_counter.count_messages_tokens(pruned_messages)} tokens)"
                    )
                optimized_messages = pruned_messages
            else:
                optimized_messages = loaded_messages
        else:
            optimized_messages = loaded_messages

        # Create state with replacement marker to ensure LangGraph uses our pruned messages
        # This tells our custom reducer to replace, not append
        from langchain_core.messages import SystemMessage

        replacement_marker = SystemMessage(
            content="[REPLACE_ALL] - Internal pruning marker"
        )

        state = {Workflow.Messages: [replacement_marker] + optimized_messages}

        # Initialise other state variables
        # Get chainId from the developer platform via api-key
        chain_id = self._get_chain_id_from_developer_platform()
        if chain_id is None:
            # Fallback to blockchain config if developer platform is unavailable
            chain_id = getattr(self.blockchain_config, "chainId", None)
            if self.debug_logging:
                print("Using fallback chain ID from blockchain config")

            # If still None, use a reasonable default (Cronos EVM Testnet)
            if chain_id is None:
                chain_id = "338"  # Cronos EVM Testnet
                if self.debug_logging:
                    print(f"Using default chain ID fallback: {chain_id}")

        state[Workflow.ChainID] = chain_id
        state[Workflow.PrivateKey] = self.blockchain_config.private_key
        state[Workflow.SSOWalletURL] = self.blockchain_config.sso_wallet_url
        state[Workflow.TransferLimit] = self.blockchain_config.transfer_limit
        if Workflow.Wallets not in state:
            state[Workflow.Wallets] = {"Active": "", "WalletList": {}}

        # If private_key is provided and no active wallet, derive address and set as active
        if self.blockchain_config.private_key and not state[Workflow.Wallets]["Active"]:
            try:
                account = Account.from_key(self.blockchain_config.private_key)
                address = account.address
                # Add to wallet list if not already present
                if address not in state[Workflow.Wallets]["WalletList"]:
                    state[Workflow.Wallets]["WalletList"][address] = {
                        "address": address,
                        "private_key": self.blockchain_config.private_key,
                        "created_at": datetime.now().isoformat(),
                    }
                # Set as active wallet
                state[Workflow.Wallets]["Active"] = address
                if self.debug_logging:
                    print(f"Set active wallet from PRIVATE_KEY: {address}")
            except Exception as e:
                if self.debug_logging:
                    print(f"Failed to derive address from PRIVATE_KEY: {e}")

        # Debug log to confirm chain_id is set correctly
        if self.debug_logging:
            print(f"State chain_id set to: {chain_id}")

        # Optional workflow configuration with increased recursion limit
        config = {
            "recursion_limit": 50,  # Increase from default 25 to handle complex tool chains
            Workflow.Configurable: {
                Workflow.ThreadID: thread_id if thread_id else "default_thread"
            },
        }

        # Show workflow start marker if debug logging is enabled
        if self.debug_logging:
            print("+" * 50)
            print("WORKFLOW STARTED")
            print("+" * 50)

        # Execute the workflow
        final_state = self.app.invoke(state, config=config)

        # Track token usage for this user request only
        messages = final_state.get("messages", [])
        new_messages = messages[initial_message_count:]

        # Only track and log token usage if debug logging is enabled
        if self.debug_logging:
            print_workflow_token_usage(new_messages)

        # Post-processing: optimize_context first, then prune
        messages = final_state.get(Workflow.Messages, [])
        if messages:
            # Step 1: Compress individual long messages (optimize_context)
            optimized_messages = self.memory_manager.optimize_context(messages)
            if self.debug_logging:
                compressed_count = len(
                    [m for m in optimized_messages if "[Compressed]" in str(m.content)]
                )
                if compressed_count > 0:
                    print(f"COMPRESSED: {compressed_count} long messages")

            # Step 2: Prune conversation history to prevent unbounded growth
            pruned_messages = self.memory_manager.prune_conversation(optimized_messages)
            if len(pruned_messages) != len(optimized_messages) and self.debug_logging:
                print(
                    f"PRUNED: {len(optimized_messages)} -> {len(pruned_messages)} messages"
                )

            # Create a new state dict for storage with pruned messages
            state_to_save = final_state.copy()
            state_to_save[Workflow.Messages] = pruned_messages
        else:
            state_to_save = final_state

        # Save updated state to storage
        if self.debug_logging:
            print(
                f"SAVING: {len(state_to_save.get(Workflow.Messages, []))} messages (thread {thread_id})"
            )
        self.storage.save_state(state_to_save, thread_id)

        # Extract and return the final response
        messages = final_state.get(Workflow.Messages, [])
        if not messages:
            return "I apologize, but I encountered an issue processing your request. Please try again."
        return messages[-1].content
