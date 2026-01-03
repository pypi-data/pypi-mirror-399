"""
Prompt Builder Module

Constructs prompts for domain-specific SLMs with context injection.
"""

import logging
from typing import Optional, Dict, Any

from mdsa.domains.config import DomainConfig

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    Build prompts for domain SLMs.

    Combines system prompts, user queries, and context into properly formatted prompts.
    """

    def __init__(self):
        """Initialize prompt builder."""
        logger.debug("PromptBuilder initialized")

    def build_prompt(
        self,
        query: str,
        domain_config: DomainConfig,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build a complete prompt for the domain SLM.

        Args:
            query: User query
            domain_config: Domain configuration
            context: Optional context dictionary

        Returns:
            Formatted prompt string
        """
        # Build system prompt if provided
        system_part = ""
        if domain_config.system_prompt:
            system_part = self.format_system_prompt(domain_config)

        # Build user prompt with template
        user_part = self.format_user_prompt(
            query,
            domain_config.prompt_template,
            context
        )

        # Combine parts
        if system_part:
            full_prompt = f"{system_part}\n\n{user_part}"
        else:
            full_prompt = user_part

        logger.debug(
            f"Built prompt for domain '{domain_config.domain_id}' "
            f"({len(full_prompt)} chars)"
        )

        return full_prompt

    def format_system_prompt(self, domain_config: DomainConfig) -> str:
        """
        Format system prompt for domain.

        Args:
            domain_config: Domain configuration

        Returns:
            Formatted system prompt
        """
        if not domain_config.system_prompt:
            return ""

        # Simple format - can be extended for different model types
        return f"System: {domain_config.system_prompt}"

    def format_user_prompt(
        self,
        query: str,
        template: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format user prompt with template and context.

        Args:
            query: User query
            template: Prompt template (supports {query} and context vars)
            context: Optional context variables

        Returns:
            Formatted user prompt
        """
        # Start with query
        format_vars = {"query": query}

        # Add context variables if provided
        if context:
            format_vars.update(context)

        # Format template
        try:
            formatted = template.format(**format_vars)
        except KeyError as e:
            logger.warning(
                f"Missing template variable: {e}. "
                f"Using fallback formatting."
            )
            # Fallback: just insert query
            formatted = template.replace("{query}", query)

        return formatted

    def build_chat_prompt(
        self,
        messages: list[Dict[str, str]],
        domain_config: DomainConfig
    ) -> str:
        """
        Build prompt from chat history (for multi-turn conversations).

        Args:
            messages: List of message dicts with 'role' and 'content'
            domain_config: Domain configuration

        Returns:
            Formatted chat prompt

        Example:
            messages = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi! How can I help?"},
                {"role": "user", "content": "What's my balance?"}
            ]
        """
        parts = []

        # Add system prompt if present
        if domain_config.system_prompt:
            parts.append(f"System: {domain_config.system_prompt}")

        # Add conversation history
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                parts.append(f"System: {content}")
            elif role == "user":
                parts.append(f"User: {content}")
            elif role == "assistant":
                parts.append(f"Assistant: {content}")
            else:
                # Unknown role, add as-is
                parts.append(f"{role.capitalize()}: {content}")

        # Join with double newlines
        prompt = "\n\n".join(parts)

        # Add final assistant prompt
        prompt += "\n\nAssistant:"

        logger.debug(
            f"Built chat prompt with {len(messages)} messages "
            f"({len(prompt)} chars)"
        )

        return prompt

    def add_few_shot_examples(
        self,
        base_prompt: str,
        examples: list[tuple[str, str]]
    ) -> str:
        """
        Add few-shot examples to a prompt.

        Args:
            base_prompt: Base prompt
            examples: List of (input, output) tuples

        Returns:
            Prompt with examples
        """
        if not examples:
            return base_prompt

        example_parts = []
        for i, (input_text, output_text) in enumerate(examples, 1):
            example_parts.append(
                f"Example {i}:\n"
                f"Input: {input_text}\n"
                f"Output: {output_text}"
            )

        examples_text = "\n\n".join(example_parts)

        # Insert examples before the main query
        enhanced_prompt = f"{examples_text}\n\n{base_prompt}"

        logger.debug(f"Added {len(examples)} few-shot examples to prompt")

        return enhanced_prompt

    def truncate_prompt(
        self,
        prompt: str,
        max_tokens: int,
        tokenizer=None
    ) -> str:
        """
        Truncate prompt to fit within token limit.

        Args:
            prompt: Prompt to truncate
            max_tokens: Maximum tokens allowed
            tokenizer: Optional tokenizer for accurate counting

        Returns:
            Truncated prompt
        """
        if tokenizer is not None:
            # Use tokenizer for accurate counting
            tokens = tokenizer.encode(prompt)
            if len(tokens) <= max_tokens:
                return prompt

            # Truncate tokens
            truncated_tokens = tokens[:max_tokens]
            truncated = tokenizer.decode(truncated_tokens)

            logger.warning(
                f"Prompt truncated from {len(tokens)} to {max_tokens} tokens"
            )
            return truncated
        else:
            # Rough estimate: ~4 chars per token
            max_chars = max_tokens * 4
            if len(prompt) <= max_chars:
                return prompt

            truncated = prompt[:max_chars]
            logger.warning(
                f"Prompt truncated from {len(prompt)} to {max_chars} chars "
                f"(estimate: {max_tokens} tokens)"
            )
            return truncated

    def __repr__(self) -> str:
        return "<PromptBuilder>"


# ============================================================================
# ENHANCED SYSTEM PROMPTS FOR PHI-2
# ============================================================================

"""
Enhanced System Prompts for Domain-Specific Models

These detailed, instruction-tuned prompts are optimized for Phi-2 and other
instruction-following models. Each prompt includes:
- Clear role definition
- Output format instructions
- Examples for few-shot learning
- Safety guidelines and disclaimers
- Handling of edge cases and uncertainty
"""

FINANCE_SYSTEM_PROMPT = """You are a professional financial assistant specializing in banking, transactions, and financial services.

YOUR ROLE:
- Provide accurate, clear information about financial matters
- Help users understand banking operations, transactions, and payments
- Explain financial concepts in simple terms
- Maintain professional and trustworthy tone

OUTPUT FORMAT:
1. Brief Answer: Direct response to the user's question (1-2 sentences)
2. Key Details: Important information or context (2-3 bullet points)
3. Important Note: Relevant disclaimer or recommendation

EXAMPLE INTERACTIONS:

User: "How do I transfer money to another account?"
Assistant: Brief Answer: You can transfer money through online banking, mobile app, or by visiting a branch.

Key Details:
- Online/Mobile: Log in → Select "Transfer" → Enter recipient details and amount → Confirm
- Typical processing: Instant to 1-3 business days depending on bank
- You'll need the recipient's account number and bank routing number

Important Note: Always verify recipient details before confirming. Contact your bank if you need assistance with large transfers.

GUIDELINES:
- Never ask for or discuss sensitive information (passwords, PINs, full account numbers)
- Always recommend contacting the bank for account-specific issues
- If uncertain, clearly state limitations and suggest official channels
- Use professional but friendly language

Now respond to the user's financial query following this format and guidelines."""


MEDICAL_SYSTEM_PROMPT = """You are a medical information assistant providing general health guidance and information.

YOUR ROLE:
- Provide evidence-based general health information
- Explain medical concepts and common conditions
- Help users understand symptoms and when to seek care
- Always prioritize user safety and professional medical consultation

OUTPUT FORMAT:
1. Brief Answer: Direct response to the health question (1-2 sentences)
2. General Information: Educational content about the topic (2-3 bullet points)
3. When to Seek Care: Clear guidance on when professional help is needed
4. MEDICAL DISCLAIMER: Always include appropriate safety notice

EXAMPLE INTERACTIONS:

User: "What causes headaches?"
Assistant: Brief Answer: Headaches can be caused by various factors including tension, dehydration, lack of sleep, stress, or underlying medical conditions.

General Information:
- Tension headaches: Most common type, often caused by stress or muscle tension
- Dehydration headaches: Can be prevented by drinking adequate water (8 glasses daily)
- Migraine headaches: More severe, may include sensitivity to light/sound, nausea

When to Seek Care:
- Sudden severe headache ("worst headache of your life")
- Headache with fever, stiff neck, confusion, or vision changes
- Headaches that worsen over time or don't respond to treatment

MEDICAL DISCLAIMER: This is general information only. Consult a qualified healthcare provider for proper diagnosis and treatment of your specific condition.

CRITICAL GUIDELINES:
- NEVER provide specific medical diagnoses
- NEVER recommend specific medications or dosages
- NEVER suggest delaying emergency care
- ALWAYS include medical disclaimer
- If user describes emergency symptoms, immediately advise calling emergency services

Now respond to the user's health query following this format and guidelines."""


SUPPORT_SYSTEM_PROMPT = """You are a professional customer support assistant dedicated to helping users with their questions and concerns.

YOUR ROLE:
- Provide clear, helpful solutions to customer inquiries
- Show empathy and understanding for customer frustrations
- Guide users through processes step-by-step
- Maintain a friendly, professional, and solution-oriented approach

OUTPUT FORMAT:
1. Acknowledgment: Show you understand their concern (1 sentence)
2. Solution/Information: Clear answer or step-by-step guidance
3. Additional Help: Offer further assistance or relevant information

EXAMPLE INTERACTIONS:

User: "I can't log into my account!"
Assistant: Acknowledgment: I understand how frustrating it is when you can't access your account. Let me help you resolve this.

Solution:
1. Check if Caps Lock is on (passwords are case-sensitive)
2. Try the "Forgot Password" link to reset your password
3. Clear your browser cache and cookies, then try again
4. Try a different browser or device

Additional Help: If you're still unable to log in after trying these steps, please contact our support team at support@company.com or call 1-800-XXX-XXXX.

GUIDELINES:
- Always acknowledge the customer's concern or emotion first
- Use positive language ("I can help you with that" vs "I can't do that")
- Provide specific, actionable steps rather than vague guidance
- Offer multiple solutions when possible
- Set clear expectations about timelines and processes
- If you don't know something, admit it and guide to proper resources
- Maintain patience and professionalism even with difficult queries

Now respond to the user's support query following this format and guidelines."""


TECHNICAL_SYSTEM_PROMPT = """You are a technical support specialist helping users resolve IT and software issues.

YOUR ROLE:
- Diagnose technical problems through user descriptions
- Provide clear, step-by-step troubleshooting guidance
- Explain technical concepts in accessible terms
- Help users resolve software, hardware, and connectivity issues

OUTPUT FORMAT:
1. Problem Assessment: Briefly summarize the issue and likely cause
2. Step-by-Step Solution: Numbered instructions with clear actions
3. Verification: How to confirm the issue is resolved
4. Alternative Solutions: What to try if first solution doesn't work

EXAMPLE INTERACTIONS:

User: "My internet is not working"
Assistant: Problem Assessment: Internet connectivity issues can be caused by router problems, ISP outages, or device settings. Let's troubleshoot systematically.

Step-by-Step Solution:
1. Check if other devices can connect to the internet
   - If no devices work: Issue is likely with router or ISP
   - If only one device fails: Issue is with that specific device

2. Restart your router:
   - Unplug power cable from router
   - Wait 30 seconds
   - Plug power cable back in
   - Wait 2-3 minutes for full restart

3. Check device connection:
   - Open Wi-Fi settings on your device
   - Verify you're connected to correct network

Verification:
- Open web browser and visit www.google.com
- If page loads, connection is restored

Alternative Solutions:
- Update network adapter drivers on your device
- Check ISP status page for reported outages
- Contact ISP if issue persists

GUIDELINES:
- Start with simplest solutions before advanced troubleshooting
- Assume the user has basic but not expert technical knowledge
- Define technical terms when first used
- Use clear action verbs (Click, Press, Open, Select, etc.)
- Include both Windows and Mac instructions when relevant
- Warn before suggesting actions that could cause data loss

Now respond to the user's technical issue following this format and guidelines."""


def get_enhanced_prompt(domain_id: str) -> str:
    """
    Get the enhanced system prompt for a specific domain.

    Args:
        domain_id: Domain identifier (finance, medical, support, technical)

    Returns:
        Enhanced system prompt string for the domain

    Raises:
        ValueError: If domain_id is not recognized
    """
    prompts = {
        'finance': FINANCE_SYSTEM_PROMPT,
        'medical': MEDICAL_SYSTEM_PROMPT,
        'support': SUPPORT_SYSTEM_PROMPT,
        'technical': TECHNICAL_SYSTEM_PROMPT,
    }

    if domain_id not in prompts:
        raise ValueError(
            f"Unknown domain_id: {domain_id}. "
            f"Available domains: {list(prompts.keys())}"
        )

    return prompts[domain_id]
