"""MCP client example demonstrating MCP server integration.

Run with:
    python -m miu_examples.mcp_client

This example shows how to connect to an MCP server and use its tools.

Requires:
    An MCP server running (e.g., mcp-server-filesystem)
"""

import asyncio

from miu_core.mcp import MCPClient


async def main() -> None:
    """Demonstrate MCP client usage."""
    # Example: Connect to a filesystem MCP server
    # Note: You need to have an MCP server running for this to work
    print("MCP Client Example")
    print("=" * 40)

    # Create client for stdio transport
    # In production, replace with actual server command
    server_command = ["npx", "-y", "@anthropic-ai/mcp-server-filesystem", "."]

    try:
        async with MCPClient(server_command=server_command) as client:
            # Connection is established in __aenter__, check server info
            server_info = client.server_info
            print("Connected to server")
            print(f"Server info: {server_info}")

            # Get available tools
            tools = client.get_tools()
            print(f"\nAvailable tools ({len(tools)}):")
            for tool in tools:
                desc = tool.get("description", "")[:50]
                print(f"  - {tool['name']}: {desc}...")

            # Call a tool (if filesystem server has read_file)
            tool_names = [t["name"] for t in tools]
            if "mcp_read_file" in tool_names:
                print("\nReading README.md...")
                result = await client.call_tool(
                    "read_file",
                    {"path": "README.md"},
                )
                print(f"Result: {result[:200]}...")

    except FileNotFoundError:
        print("Error: MCP server not found.")
        print("Install with: npm install -g @anthropic-ai/mcp-server-filesystem")
    except Exception as e:
        print(f"Error connecting to MCP server: {e}")
        print("\nThis example requires an MCP server to be available.")
        print("Try running with a different MCP server or ensure npx is installed.")


if __name__ == "__main__":
    asyncio.run(main())
