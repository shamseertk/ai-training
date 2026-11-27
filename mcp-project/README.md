# MCP Personal Agent

A command-line chat agent built with `mcp-use` and Groq's LangChain integration. It keeps conversation memory for the current run and connects to the MCP servers listed in `browser_mcp.json`:

- Playwright for browser automation
- Airbnb search
- DuckDuckGo search

The agent is configured for up to 15 steps per request. Choose a currently supported Groq model ID in `app.py` when configuring `ChatGroq`.

## Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/)
- Node.js 20 or later, with `npm`/`npx` available on `PATH` (required by the Playwright MCP server)
- A Groq API key

## Setup

Install the repository's Python dependencies from the repository root if they are not installed yet:

```bash
uv sync
```

Create `mcp-project/.env` and add your Groq API key:

```dotenv
GROQ_API_KEY=your_groq_api_key
```

Keep the key private; do not commit `.env`.

## Run

Run from this directory so the app can find `browser_mcp.json`:

```bash
cd mcp-project
uv run app.py
```

`uv` uses the Python project environment at the repository root. If a different virtual environment is active and uv warns that it will be ignored, deactivate it before running.

The MCP servers are started on demand through `npx`; their first launch may download packages and requires network access. Edit `browser_mcp.json` to add or remove servers.

## Execution flow

1. `asyncio.run()` starts the chat coroutine, which loads `GROQ_API_KEY` from the environment or `.env`.
2. The app reads `browser_mcp.json`, creates the MCP client and Groq chat model, then configures an `MCPAgent` with memory and a 15-step limit.
3. The REPL reads input. `clear` resets agent memory; `exit` and `quit` end the loop.
4. Other input is passed to `agent.run()`. The agent can use the configured MCP tools; tool-call failures are retried up to five times with exponential backoff.
5. In a `finally` block, the app conditionally closes MCP sessions, reports any shutdown error, and prints the end message.

## Commands

- Enter a message to chat with the agent.
- Type `clear` to clear conversation memory.
- Type `exit` or `quit` to end the session.
