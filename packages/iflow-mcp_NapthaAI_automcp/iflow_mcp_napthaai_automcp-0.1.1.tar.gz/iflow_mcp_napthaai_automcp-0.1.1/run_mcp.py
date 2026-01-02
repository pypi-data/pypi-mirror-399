import warnings
from typing import Any
import subprocess
import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Create MCP server
mcp = FastMCP("AutoMCP Server")

# Suppress warnings that might interfere with STDIO transport
warnings.filterwarnings("ignore")

@mcp.tool()
def init_mcp_server(framework: str) -> str:
    """
    Initialize a new MCP server configuration for the specified framework.
    
    Args:
        framework: The agent framework to use (crewai, langgraph, llamaindex, openai, pydantic, mcp_agent)
    
    Returns:
        Success message with next steps
    """
    try:
        result = subprocess.run(
            ["python3", "-m", "automcp.cli", "init", "-f", framework],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return f"Successfully initialized MCP server for {framework} framework.\n\nNext steps:\n1. Edit run_mcp.py to import and configure your {framework} agent/crew/graph\n2. Add a .env file with necessary environment variables\n3. Run your MCP server using: automcp serve -t stdio"
        else:
            return f"Error initializing MCP server: {result.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def get_available_frameworks() -> str:
    """
    Get list of available agent frameworks supported by AutoMCP.
    
    Returns:
        JSON string with available frameworks
    """
    frameworks = {
        "frameworks": [
            {
                "name": "crewai",
                "description": "CrewAI - Multi-agent orchestration framework"
            },
            {
                "name": "langgraph",
                "description": "LangGraph - Stateful, multi-actor applications with LLMs"
            },
            {
                "name": "llamaindex",
                "description": "LlamaIndex - Data framework for LLM applications"
            },
            {
                "name": "openai",
                "description": "OpenAI Agents SDK - Build agents with OpenAI"
            },
            {
                "name": "pydantic",
                "description": "Pydantic AI - Type-safe AI applications"
            },
            {
                "name": "mcp_agent",
                "description": "MCP Agent - Native MCP agent framework"
            }
        ]
    }
    return json.dumps(frameworks, indent=2)

@mcp.tool()
def serve_mcp_server(transport: str = "stdio") -> str:
    """
    Run the AutoMCP server (requires run_mcp.py to exist in current directory).
    
    Args:
        transport: Transport to use (stdio or sse, defaults to stdio)
    
    Returns:
        Message indicating server is running
    """
    current_dir = Path.cwd()
    automcp_file = current_dir / "run_mcp.py"
    
    if not automcp_file.exists():
        return "Error: run_mcp.py not found in current directory. Please run 'init_mcp_server' first."
    
    try:
        if transport == "stdio":
            subprocess.run(["python3", str(automcp_file)])
        elif transport == "sse":
            subprocess.run(["python3", str(automcp_file), "sse"])
        else:
            return f"Error: Invalid transport '{transport}'. Use 'stdio' or 'sse'."
        
        return f"AutoMCP server started with {transport} transport"
    except Exception as e:
        return f"Error: {str(e)}"


# Server entrypoints
def serve_sse():
    mcp.run(transport="sse")


def serve_stdio():
    # Redirect stderr to suppress warnings that bypass the filters
    import os
    import sys

    class NullWriter:
        def write(self, *args, **kwargs):
            pass

        def flush(self, *args, **kwargs):
            pass

    # Save the original stderr
    original_stderr = sys.stderr

    # Replace stderr with our null writer to prevent warnings from corrupting STDIO
    sys.stderr = NullWriter()

    # Set environment variable to ignore Python warnings
    os.environ["PYTHONWARNINGS"] = "ignore"

    try:
        mcp.run(transport="stdio")
    finally:
        # Restore stderr for normal operation
        sys.stderr = original_stderr


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "sse":
        serve_sse()
    else:
        serve_stdio()