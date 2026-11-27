"""
Memory-enabled chat REPL using MCPAgent (customised version).
· GROQ_API_KEY is copied into os.environ after loading .env
· Uses the Groq model **qwen-qwq-32b**
· Reads MCP server list from **browser_mcp.json** in the current directory
· Allows 15 reasoning steps and supports the single command `clear` to
wipe history.
"""
import asyncio
import os
import warnings
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from mcp_use import MCPAgent, MCPClient

# Optional: silence Windows “unclosed transport” warnings that appear on shutdown
warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed transport")

def ensure_api_key() -> None:
    """Ensure that the GROQ_API_KEY environment variable is set."""
    if "GROQ_API_KEY" not in os.environ:
        load_dotenv()  # Load from .env file if not already set
        if "GROQ_API_KEY" not in os.environ:
            raise EnvironmentError("GROQ_API_KEY must be set in the environment or .env file.")
    # Explicit copy (redundant for most cases but requested):
    os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
async def memory_chat() -> None:
    """Run a memory-enabled chat REPL using MCPAgent."""
    ensure_api_key()
     # Path to MCP server config (current directory)
    config_file = "browser_mcp.json"
    print("Initialising MCP client (with throttling/backoff) and LLM…")
    # Subclass MCPClient to inject throttling and exponential backoff
    class ThrottledMCPClient(MCPClient):
        async def call_tool(self, tool_name: str, *args, **kwargs):
            """Call a tool with throttling and exponential backoff."""
            max_retries = 5
            delay = 1  # Initial delay in seconds
            for attempt in range(max_retries):
                try:
                    result = await super().call_tool(tool_name, *args, **kwargs)
                    # Throttle every successful call to avoid rate limits
                    await asyncio.sleep(1.5)  # 1.5 seconds delay between calls
                    return result
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
                    delay *= 2  # Exponential backoff
            raise RuntimeError(f"Failed to call tool '{tool_name}' after {max_retries} attempts.")

    client = ThrottledMCPClient.from_config_file(config_file)
    llm = ChatGroq(model="openai/gpt-oss-20b", reasoning_effort="medium")

    agent = MCPAgent(llm=llm, client=client, memory_enabled=True, max_steps=15)
    print("\n==== MCP Chat memory enabled REPL ====")
    print("Type 'exit' or 'quit' to leave; type 'clear' to wipe memory.\n")

    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() in {"exit", "quit"}:
                print("Exiting chat...")
                break
            elif user_input.lower() == "clear":
                agent.clear_memory()
                print("Memory cleared.")
                continue
            try:
              response = await agent.run(user_input)
              print(f"Agent: {response}")
            except Exception as exc:
                print(f"Error: {exc}")
    finally:
    # Graceful shutdown if API exists in this version of mcp_use
        if hasattr(agent, "shutdown"):
            try:
                await agent.close_all_sessions()
            except Exception as e:
                print(f"Error during shutdown: {e}")

        print("Chat session ended.")

if __name__ == "__main__":
 asyncio.run(memory_chat())



