"""
Agent with Tools (LangGraph Version)
=====================================
Advanced AI agent using LangGraph for tool coordination.

Features:
- Automatic tool selection based on user query
- Multiple tool coordination
- Detailed reasoning about tool choices
- Conversation memory
- Emergency detection

Author: Team A - Pratik
"""

import logging
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

# Import our config and tools
from app.config import Config
from app.tools.calculator_tool import CalculatorTool
from app.tools.datetime_tool import DateTimeTool
from app.tools.medical_info_tool import MedicalInfoTool
from app.tools.emergency_tool import EmergencyTool

# Setup logger
logger = logging.getLogger(__name__)


class AgentWithTools:
    """Advanced AI Agent that uses multiple tools intelligently."""

    def __init__(
        self,
        model: str = None,
        temperature: float = None,
        verbose: bool = True
    ):
        """Initialize the agent with all tools."""
        # Validate configuration
        Config.validate()

        # Set model parameters
        self.model = model or Config.DEFAULT_MODEL
        self.temperature = temperature if temperature is not None else Config.DEFAULT_TEMPERATURE
        self.verbose = verbose

        # Initialize LLM
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

        # Initialize all tools
        self.tools = self._initialize_tools()

        # Create system prompt
        self.system_prompt = self._create_system_prompt()

        # Create the agent using LangGraph
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
        )

        # Chat history
        self.chat_history = []

        logger.info(f"✅ Agent with {len(self.tools)} tools initialized")

    def _initialize_tools(self) -> List:
        """Initialize and return all available tools."""
        tools = [
            CalculatorTool(),
            DateTimeTool(),
            MedicalInfoTool(),
            EmergencyTool()
        ]
        logger.info(f"🔧 Loaded tools: {[t.name for t in tools]}")
        return tools

    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agent."""
        return f"""You are {Config.AGENT_NAME}, an intelligent AI assistant for a Medical Operations Dashboard.

You have access to these tools:
- calculator: For math calculations (BMI, dosage, percentages, arithmetic)
- datetime: For date/time operations (current time, age, appointments)
- medical_info: For medical information (diseases, medicines, departments)
- emergency: For emergency contacts and first aid procedures

INSTRUCTIONS:
1. ALWAYS use the appropriate tool when user asks for calculations, dates, medical info, or emergency help
2. Choose the RIGHT tool based on the query
3. For emergencies, IMMEDIATELY use the emergency tool
4. Provide clear, professional responses
5. NEVER give medical diagnoses - recommend consulting a doctor
6. Be concise but thorough

Supported departments: {', '.join(Config.SUPPORTED_DEPARTMENTS)}"""

    def chat(self, user_input: str) -> str:
        """Process user input and return agent response."""
        try:
            if not user_input.strip():
                return "⚠️ Please provide a valid question."

            logger.info(f"👤 User query: {user_input}")

            # Build messages
            messages = [SystemMessage(content=self.system_prompt)]
            messages.extend(self.chat_history)
            messages.append(HumanMessage(content=user_input))

            # Invoke the agent
            result = self.agent.invoke({"messages": messages})

            # Extract the final answer
            final_messages = result.get("messages", [])
            answer = ""
            tools_used = []

            for msg in final_messages:
                # Check if it's a tool call
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tc in msg.tool_calls:
                        tools_used.append(tc.get('name', 'unknown'))

                # Get the final AI message content
                if isinstance(msg, AIMessage) and msg.content:
                    answer = msg.content

            # If no answer, get the last message content
            if not answer and final_messages:
                answer = str(final_messages[-1].content)

            # Update chat history
            self.chat_history.append(HumanMessage(content=user_input))
            self.chat_history.append(AIMessage(content=answer))

            if tools_used and self.verbose:
                logger.info(f"🔧 Tools used: {tools_used}")

            return answer

        except Exception as e:
            logger.error(f"❌ Agent error: {e}")
            return f"❌ Sorry, I encountered an error: {str(e)}"

    def reset_conversation(self) -> None:
        """Clear conversation history."""
        self.chat_history = []
        logger.info("🔄 Conversation reset")

    def show_tools_stats(self) -> None:
        """Show statistics for all tools."""
        print("\n" + "=" * 60)
        print("  📊 TOOLS USAGE STATISTICS")
        print("=" * 60)
        for tool in self.tools:
            if hasattr(tool, 'get_stats'):
                stats = tool.get_stats()
                print(f"  🔧 {stats['tool_name']:15} : {stats['usage_count']} calls")
        print("=" * 60 + "\n")

    def show_available_tools(self) -> None:
        """Show all available tools."""
        print("\n" + "=" * 60)
        print("  🔧 AVAILABLE TOOLS")
        print("=" * 60)
        for i, tool in enumerate(self.tools, 1):
            print(f"  {i}. {tool.name}")
            first_line = tool.description.split(chr(10))[0]
            print(f"     {first_line}")
            print()
        print("=" * 60 + "\n")


# ============================================
# Interactive Chat Interface
# ============================================
def run_chat():
    """Run the interactive chat with tools."""
    print("\n" + "=" * 60)
    print(f"  🤖 {Config.AGENT_NAME} - AI Agent with Tools")
    print(f"  🌐 Powered by OpenRouter + LangGraph")
    print("=" * 60)
    print("  Commands:")
    print("    'exit'    - Exit the chat")
    print("    'reset'   - Clear conversation history")
    print("    'tools'   - Show available tools")
    print("    'stats'   - Show tools usage stats")
    print("=" * 60 + "\n")

    # Initialize agent
    try:
        print("🔄 Initializing agent with tools...")
        agent = AgentWithTools(verbose=True)
        print("✅ Agent ready!\n")
        agent.show_available_tools()
    except Exception as e:
        print(f"❌ Failed to start agent: {e}")
        return

    # Example queries
    print("💡 Try these example queries:")
    print("   • What is BMI for 70kg and 1.75m?")
    print("   • What's the current time?")
    print("   • Tell me about diabetes")
    print("   • What's the ambulance number?")
    print("   • Calculate dosage for 60kg with 15mg/kg\n")

    # Chat loop
    while True:
        try:
            user_input = input("👤 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "bye"]:
                print(f"\n🤖 {Config.AGENT_NAME}: Goodbye! Stay healthy! 👋\n")
                agent.show_tools_stats()
                break

            if user_input.lower() == "reset":
                agent.reset_conversation()
                print("✅ Conversation reset.\n")
                continue

            if user_input.lower() == "tools":
                agent.show_available_tools()
                continue

            if user_input.lower() == "stats":
                agent.show_tools_stats()
                continue

            # Get response
            print("🤔 Thinking...\n")
            response = agent.chat(user_input)
            print(f"🤖 {Config.AGENT_NAME}: {response}\n")

        except KeyboardInterrupt:
            print(f"\n\n🤖 {Config.AGENT_NAME}: Goodbye! 👋\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    run_chat()