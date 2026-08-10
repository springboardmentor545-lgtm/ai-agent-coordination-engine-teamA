"""
Basic AI Agent
==============
Foundation agent for the Medical Operations Dashboard.
Now uses OpenRouter API (FREE models).

Features:
- Interactive chat interface
- Conversation history tracking
- Error handling with retries
- Emergency detection
- Response formatting
- Logging support

Author: Team A - Pratik
"""

import time
import logging
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Import our config
from app.config import Config

# Setup logger
logger = logging.getLogger(__name__)


class BasicAgent:
    """
    Basic AI Agent for handling medical queries using OpenRouter.
    """

    def __init__(
        self,
        model: str = None,
        temperature: float = None,
        system_prompt: str = None
    ):
        """Initialize the Basic Agent."""
        # Validate configuration first
        Config.validate()

        # Set model parameters
        self.model = model or Config.DEFAULT_MODEL
        self.temperature = temperature if temperature is not None else Config.DEFAULT_TEMPERATURE

        # Initialize the LLM with OpenRouter
        self.llm = ChatOpenAI(
            model=self.model,
            api_key=Config.OPENROUTER_API_KEY,
            base_url=Config.OPENROUTER_API_BASE,
            temperature=self.temperature,
            max_tokens=Config.MAX_TOKENS,
            timeout=Config.REQUEST_TIMEOUT,
            default_headers={
                "HTTP-Referer": "https://github.com/springboardmentor545-lgtm/ai-agent-coordination-engine-teamA",
                "X-Title": "Medical Operations Dashboard - Team A"
            }
        )

        # Setup system prompt
        self.system_prompt = system_prompt or self._default_system_prompt()

        # Initialize conversation history
        self.conversation_history: List[Dict[str, str]] = []

        logger.info(f"✅ {Config.AGENT_NAME} initialized with model: {self.model}")

    def _default_system_prompt(self) -> str:
        """Default system prompt for medical assistant"""
        return f"""You are {Config.AGENT_NAME}, an intelligent AI assistant for a Medical Operations Dashboard.

Your responsibilities:
1. Help medical staff with information queries
2. Provide clear, professional responses
3. Flag emergencies immediately
4. Never provide direct medical diagnoses (recommend consulting a doctor)
5. Be concise but thorough

Supported departments: {', '.join(Config.SUPPORTED_DEPARTMENTS)}

Always be helpful, accurate, and safety-focused."""

    def _detect_emergency(self, message: str) -> bool:
        """Check if the message contains emergency keywords"""
        message_lower = message.lower()
        for keyword in Config.EMERGENCY_KEYWORDS:
            if keyword in message_lower:
                return True
        return False

    def chat(self, user_message: str, retry_count: int = 0) -> str:
        """Send a message to the agent and get a response."""
        try:
            # Check for empty input
            if not user_message.strip():
                return "⚠️ Please provide a valid question."

            # Emergency detection
            is_emergency = self._detect_emergency(user_message)
            if is_emergency:
                logger.warning(f"🚨 Emergency detected: {user_message[:50]}...")

            # Build message list
            messages = [SystemMessage(content=self.system_prompt)]

            # Add conversation history
            for msg in self.conversation_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

            # Add current message
            messages.append(HumanMessage(content=user_message))

            # Get response from LLM
            response = self.llm.invoke(messages)
            answer = response.content

            # Save to history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": answer})

            # Add emergency prefix if detected
            if is_emergency:
                answer = f"🚨 EMERGENCY DETECTED 🚨\n\n{answer}"

            return answer

        except Exception as e:
            logger.error(f"❌ Error in chat: {e}")

            # Retry logic
            if retry_count < Config.MAX_RETRIES:
                logger.info(f"🔄 Retrying... (attempt {retry_count + 1}/{Config.MAX_RETRIES})")
                time.sleep(2)
                return self.chat(user_message, retry_count + 1)

            return f"❌ Sorry, I encountered an error: {str(e)}"

    def reset_conversation(self) -> None:
        """Clear the conversation history"""
        self.conversation_history = []
        logger.info("🔄 Conversation history cleared")

    def get_history(self) -> List[Dict[str, str]]:
        """Return the full conversation history"""
        return self.conversation_history

    def show_stats(self) -> None:
        """Display agent statistics"""
        total_messages = len(self.conversation_history)
        user_messages = sum(1 for m in self.conversation_history if m["role"] == "user")

        print("\n" + "=" * 50)
        print(f"  📊 {Config.AGENT_NAME} Statistics")
        print("=" * 50)
        print(f"  Total Messages     : {total_messages}")
        print(f"  User Messages      : {user_messages}")
        print(f"  Agent Responses    : {total_messages - user_messages}")
        print(f"  Current Model      : {self.model}")
        print(f"  Temperature        : {self.temperature}")
        print("=" * 50 + "\n")


# ============================================
# Interactive Chat Interface
# ============================================
def run_chat():
    """Run the interactive chat interface"""
    print("\n" + "=" * 60)
    print(f"  🤖 {Config.AGENT_NAME} - Medical Operations Assistant")
    print(f"  🌐 Powered by OpenRouter (FREE)")
    print("=" * 60)
    print("  Commands:")
    print("    'exit' or 'quit'   - Exit the chat")
    print("    'reset'            - Clear conversation history")
    print("    'stats'            - Show agent statistics")
    print("    'history'          - Show conversation history")
    print("=" * 60 + "\n")

    # Initialize agent
    try:
        agent = BasicAgent()
    except ValueError as e:
        print(f"❌ Failed to start agent: {e}")
        return

    # Chat loop
    while True:
        try:
            user_input = input("👤 You: ").strip()

            # Handle commands
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "bye"]:
                print(f"\n🤖 {Config.AGENT_NAME}: Goodbye! Stay healthy! 👋\n")
                agent.show_stats()
                break

            if user_input.lower() == "reset":
                agent.reset_conversation()
                print("✅ Conversation reset.\n")
                continue

            if user_input.lower() == "stats":
                agent.show_stats()
                continue

            if user_input.lower() == "history":
                history = agent.get_history()
                if not history:
                    print("📭 No conversation history yet.\n")
                else:
                    print("\n📜 Conversation History:")
                    print("-" * 50)
                    for i, msg in enumerate(history, 1):
                        role_emoji = "👤" if msg["role"] == "user" else "🤖"
                        content_preview = msg['content'][:80]
                        print(f"{i}. {role_emoji} {msg['role'].title()}: {content_preview}...")
                    print("-" * 50 + "\n")
                continue

            # Get response from agent
            response = agent.chat(user_input)
            print(f"🤖 {Config.AGENT_NAME}: {response}\n")

        except KeyboardInterrupt:
            print(f"\n\n🤖 {Config.AGENT_NAME}: Chat interrupted. Goodbye! 👋\n")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}\n")


if __name__ == "__main__":
    run_chat()