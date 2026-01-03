#!/usr/bin/env python3
"""Test script to verify MCP server functionality"""
import sys
import asyncio
from mcp.server.fastmcp import FastMCP

# Create a simple test server
mcp = FastMCP("Test SQL Analyzer")

@mcp.tool()
def test_tool(message: str) -> str:
    """A simple test tool"""
    return f"Received: {message}"

if __name__ == "__main__":
    print("Starting test server...", file=sys.stderr)
    mcp.run(transport='stdio')