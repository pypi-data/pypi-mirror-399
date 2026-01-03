"""
Simple Memory Manager Module using LangChain Built-ins.

This module provides streamlined memory management by leveraging LangChain's
native utilities:
- Token counting via trim_messages
- Message summarization via load_summarize_chain
- Message pruning with trim_messages
- Q&A pair compression with LangChain chains

The goal is to simplify the original implementation by reusing LangChain
components wherever possible.
"""

import logging
from typing import List, Optional

from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.messages.utils import trim_messages
from langchain_core.runnables import Runnable

from crypto_com_agent_client.lib.types.memory_config import MemoryConfig

logger = logging.getLogger(__name__)


class TokenCounter:
    """Simple token counting utility."""

    @staticmethod
    def count_tokens(text: str) -> int:
        """Estimate token count: ~4 characters per token."""
        return max(1, len(text) // 4)

    @staticmethod
    def count_message_tokens(message: BaseMessage) -> int:
        """Count tokens in a single message."""
        base_tokens = TokenCounter.count_tokens(str(message.content))
        overhead = 10  # Message type overhead

        # Add tool call overhead
        if hasattr(message, "tool_calls") and message.tool_calls:
            import json

            for tool_call in message.tool_calls:
                if isinstance(tool_call, dict):
                    overhead += TokenCounter.count_tokens(json.dumps(tool_call))

        return base_tokens + overhead

    @staticmethod
    def count_messages_tokens(messages: List[BaseMessage]) -> int:
        """Count total tokens in message list."""
        return sum(TokenCounter.count_message_tokens(msg) for msg in messages)


class MemoryManager:
    """
    Simplified memory manager using LangChain built-in components.

    Main functions:
    1. Summarization: Use load_summarize_chain to compress Q&A pairs
    2. Pruning: Use trim_messages to remove old messages
    """

    def __init__(
        self,
        config: MemoryConfig,
        model: Optional[Runnable] = None,
    ):
        self.config = config
        self.model = model
        self.token_counter = TokenCounter()

        # Initialize summarization chain if model is provided
        self.summarize_chain = None
        self.use_direct_invoke = False
        if model:
            try:
                # Try to use LangChain's load_summarize_chain (preferred)
                self.summarize_chain = load_summarize_chain(
                    llm=model,
                    chain_type="stuff",
                    verbose=False,
                )
            except Exception:
                # Fallback: Use direct model invocation if it has invoke method
                if hasattr(model, "invoke"):
                    self.use_direct_invoke = True

    def optimize_context(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        Compress Q&A pairs into summaries using LangChain's load_summarize_chain.
        Summaries go to top of message list.
        """
        if not messages or len(messages) <= 2:
            return messages

        # Separate summaries from regular messages
        summaries = []
        regular_messages = []

        for msg in messages:
            if self._is_summary(msg):
                summaries.append(msg)
            else:
                regular_messages.append(msg)

        # Process regular messages for Q&A compression
        optimized_messages = []
        i = 0

        # Calculate how many recent messages to preserve
        preserve_count = self.config.preserve_recent_messages

        while i < len(regular_messages):
            msg = regular_messages[i]

            # Check if we're in the preservation zone
            messages_from_end = len(regular_messages) - i
            should_preserve = messages_from_end <= preserve_count

            # If preserving, check if we should force processing due to size
            if should_preserve:
                if preserve_count > 0 and self.config.allow_recent_summarization:
                    # Calculate tokens in remaining messages
                    remaining_messages = regular_messages[i:]
                    remaining_tokens = self.token_counter.count_messages_tokens(
                        remaining_messages
                    )

                    if remaining_tokens > self.config.max_recent_message_tokens:
                        should_preserve = False

                if should_preserve:
                    optimized_messages.extend(regular_messages[i:])
                    break

            # Look for Q&A pairs to compress
            if (
                isinstance(msg, HumanMessage)
                and i + 1 < len(regular_messages)
                and isinstance(regular_messages[i + 1], AIMessage)
            ):

                next_msg = regular_messages[i + 1]

                # Skip if AI message has tool calls
                if hasattr(next_msg, "tool_calls") and next_msg.tool_calls:
                    optimized_messages.extend([msg, next_msg])
                    i += 2
                    continue

                # Check if pair exceeds compression threshold
                combined_tokens = self.token_counter.count_message_tokens(
                    msg
                ) + self.token_counter.count_message_tokens(next_msg)

                if (
                    combined_tokens > self.config.message_compression_threshold
                    and self.summarize_chain
                ):
                    # Compress the Q&A pair using LangChain's summarize chain
                    compressed_summary = self._compress_qa_pair_langchain(msg, next_msg)
                    if compressed_summary:
                        summaries.append(compressed_summary)
                        i += 2
                        continue

                # No compression needed, keep both messages
                optimized_messages.extend([msg, next_msg])
                i += 2
            else:
                # Single message, keep as is
                optimized_messages.append(msg)
                i += 1

        # Result: summaries first, then optimized regular messages
        result = summaries + optimized_messages
        return result

    def prune_conversation(self, messages: List[BaseMessage]) -> List[BaseMessage]:
        """
        Remove old messages using LangChain's trim_messages utility.
        This is much simpler than the original implementation.
        """
        current_tokens = self.token_counter.count_messages_tokens(messages)
        max_tokens = self.config.max_conversation_tokens

        if current_tokens <= max_tokens:
            return messages

        # Separate summaries from regular messages
        summaries = []
        regular_messages = []

        for msg in messages:
            if self._is_summary(msg):
                summaries.append(msg)
            else:
                regular_messages.append(msg)

        # Calculate summary tokens
        summary_tokens = self.token_counter.count_messages_tokens(summaries)

        # If summaries take up more than 50% of available space, prune them too
        summary_budget = max_tokens // 2
        if summary_tokens > summary_budget and len(summaries) > 2:
            summaries = self._prune_summaries(summaries, summary_budget)
            summary_tokens = self.token_counter.count_messages_tokens(summaries)

        # Calculate available space for regular messages
        available_tokens = max_tokens - summary_tokens

        if available_tokens <= 0:
            # No space for regular messages, keep only summaries + most recent
            pruned_messages = regular_messages[-1:] if regular_messages else []
        else:
            # Use LangChain's trim_messages to prune regular messages
            pruned_messages = self._trim_messages_langchain(
                regular_messages, available_tokens
            )

        # Result: summaries first, then pruned messages
        result = summaries + pruned_messages
        return result

    def _trim_messages_langchain(
        self, messages: List[BaseMessage], max_tokens: int
    ) -> List[BaseMessage]:
        """
        Use LangChain's trim_messages utility to prune messages.
        This replaces the complex FIFO + semantic pruning logic.
        """
        if not messages:
            return []

        try:
            # Use trim_messages with "last" strategy to keep most recent messages
            pruned = trim_messages(
                messages=messages,
                max_tokens=max_tokens,
                strategy="last",  # Keep the most recent messages
                token_counter=self.token_counter.count_message_tokens,
                include_system=True,  # Include system messages in the result
                allow_partial=False,  # Don't allow partial messages
                start_on="human",  # Try to start with a human message for context
            )
            return pruned

        except Exception as e:
            logger.warning(
                f"LangChain trim_messages failed: {str(e)}. Falling back to FIFO pruning."
            )

            # Fallback to simple FIFO if trim_messages fails
            pruned = []
            current_tokens = 0

            # Keep messages from most recent, working backwards
            for msg in reversed(messages):
                tokens = self.token_counter.count_message_tokens(msg)
                if current_tokens + tokens <= max_tokens:
                    pruned.append(msg)
                    current_tokens += tokens
                else:
                    break

            # Return to original order
            return list(reversed(pruned))

    def _compress_qa_pair_langchain(
        self, question: HumanMessage, answer: AIMessage
    ) -> Optional[SystemMessage]:
        """
        Compress a Q&A pair using LangChain's load_summarize_chain.
        This replaces the manual prompt-based compression.
        """
        if not self.summarize_chain:
            return None

        try:
            q_content = str(question.content)
            a_content = str(answer.content)

            # Create a document from the Q&A pair
            qa_text = f"Q: {q_content}\n\nA: {a_content}"
            doc = Document(page_content=qa_text)

            # Use LangChain's summarize chain
            summary_result = self.summarize_chain.invoke({"input_documents": [doc]})

            # Extract the summary text
            summary_text = summary_result.get("output_text", "")

            # Create a system message with the summary
            summary_content = f"[Compressed Q&A Exchange]\n{summary_text}"
            return SystemMessage(content=summary_content)

        except Exception as e:
            logger.warning(
                f"Failed to compress Q&A pair: {str(e)}. Keeping original messages."
            )
            return None

    def _prune_summaries(
        self, summaries: List[BaseMessage], max_tokens: int
    ) -> List[BaseMessage]:
        """
        Prune summaries by combining old ones using load_summarize_chain.
        """
        if not summaries:
            return summaries

        current_tokens = self.token_counter.count_messages_tokens(summaries)
        if current_tokens <= max_tokens:
            return summaries

        # If no summarization chain available, fall back to simple FIFO
        if not self.summarize_chain:
            # Keep as many recent summaries as fit within budget
            result = []
            current_tokens = 0

            for summary in reversed(summaries):
                summary_tokens = self.token_counter.count_message_tokens(summary)
                if current_tokens + summary_tokens <= max_tokens:
                    result.append(summary)
                    current_tokens += summary_tokens
                else:
                    break

            return list(reversed(result))

        # Always preserve the most recent summary
        if len(summaries) <= 1:
            return summaries

        preserved_summary = summaries[-1]
        old_summaries = summaries[:-1]

        # Create a meta-summary from old summaries using LangChain
        meta_summary = self._create_meta_summary_langchain(old_summaries)
        if meta_summary:
            result = [meta_summary, preserved_summary]
        else:
            # Fallback: keep only the most recent summary
            result = [preserved_summary]

        return result

    def _create_meta_summary_langchain(
        self, summaries: List[BaseMessage]
    ) -> Optional[SystemMessage]:
        """
        Create a meta-summary from multiple summaries using LangChain's summarize chain.
        """
        if not self.summarize_chain or not summaries:
            return None

        try:
            # Combine all summary contents into documents
            combined_content = "\n\n".join(
                [str(summary.content) for summary in summaries]
            )
            doc = Document(page_content=combined_content)

            # Use LangChain's summarize chain
            summary_result = self.summarize_chain.invoke({"input_documents": [doc]})

            # Extract the summary text
            summary_text = summary_result.get("output_text", "")

            # Create a system message with the meta-summary
            meta_content = (
                f"[Meta-Summary of {len(summaries)} conversations]\n{summary_text}"
            )
            return SystemMessage(content=meta_content)

        except Exception as e:
            logger.warning(
                f"Failed to create meta-summary from {len(summaries)} summaries: {str(e)}. "
                f"Falling back to keeping only recent summaries."
            )
            return None

    def _is_summary(self, message: BaseMessage) -> bool:
        """Check if message is a summary based on content markers."""
        content = str(message.content).lower()
        return any(
            marker in content
            for marker in [
                "[compressed q&a exchange]",
                "[compressed]",
                "[summary",
                "[meta-summary",
            ]
        )

    def get_memory_stats(self, messages: List[BaseMessage]) -> dict:
        """Get simple memory statistics."""
        total_tokens = self.token_counter.count_messages_tokens(messages)

        summaries = [msg for msg in messages if self._is_summary(msg)]
        regular_messages = [msg for msg in messages if not self._is_summary(msg)]

        return {
            "total_messages": len(messages),
            "total_tokens": total_tokens,
            "summaries": len(summaries),
            "regular_messages": len(regular_messages),
            "summary_tokens": self.token_counter.count_messages_tokens(summaries),
            "context_utilization": total_tokens / self.config.max_context_tokens,
            "conversation_utilization": total_tokens
            / self.config.max_conversation_tokens,
        }
