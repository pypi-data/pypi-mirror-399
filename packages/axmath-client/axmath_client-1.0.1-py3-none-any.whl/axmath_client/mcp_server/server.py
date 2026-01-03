"""
MCP server implementation that calls authenticated AxMath API.
"""

import json
import logging
import os
from typing import Any, Dict, List, Sequence

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Resource, Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logging.warning("MCP SDK not available. Install with: pip install axmath-client[mcp]")

from axmath_client import AxMath
from axmath_client.exceptions import AxMathError

logger = logging.getLogger(__name__)


class AxMathMCPServer:
    """MCP Server that connects to authenticated AxMath API."""

    def __init__(self):
        """Initialize MCP server."""
        if not MCP_AVAILABLE:
            raise RuntimeError("MCP SDK not installed. Install with: pip install axmath-client[mcp]")

        # Initialize API client
        try:
            self.client = AxMath()  # Uses AXMATH_API_KEY from environment
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize AxMath client: {e}\n"
                "Make sure AXMATH_API_KEY environment variable is set.\n"
                "Get your API key at: https://axmath.yourdomain.com/auth/register"
            )

        self.server = Server("axmath")
        self._register_resources()
        self._register_tools()

        logger.info("AxMath MCP Server initialized (authenticated mode)")

    def _register_resources(self):
        """Register MCP resources."""

        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available resources."""
            return [
                Resource(
                    uri="axmath://usage",
                    name="API Usage Statistics",
                    mimeType="application/json",
                    description="Your current API usage and quotas"
                ),
                Resource(
                    uri="axmath://config",
                    name="Client Configuration",
                    mimeType="application/json",
                    description="AxMath client configuration"
                ),
            ]

        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read a resource by URI."""
            if uri == "axmath://usage":
                try:
                    usage = self.client.get_usage()
                    return json.dumps(usage, indent=2)
                except AxMathError as e:
                    return json.dumps({"error": str(e)})

            elif uri == "axmath://config":
                return json.dumps({
                    "api_url": self.client.api_url,
                    "api_key": self.client.api_key[:10] + "..." if self.client.api_key else None,
                    "timeout": self.client.timeout,
                }, indent=2)

            else:
                raise ValueError(f"Unknown resource URI: {uri}")

    def _register_tools(self):
        """Register MCP tools."""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="prove_theorem",
                    description="Prove a theorem in LEAN 4 using AxMath API",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "statement": {
                                "type": "string",
                                "description": "Theorem statement to prove"
                            },
                            "search_premises": {
                                "type": "boolean",
                                "description": "Search for relevant premises",
                                "default": True
                            },
                            "max_iterations": {
                                "type": "integer",
                                "description": "Maximum proving iterations",
                                "default": 10
                            },
                        },
                        "required": ["statement"]
                    }
                ),
                Tool(
                    name="search_premises",
                    description="Search mathlib4 premises using AxMath API",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "k": {
                                "type": "integer",
                                "description": "Number of results",
                                "default": 10
                            },
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="verify_lean_code",
                    description="Verify LEAN 4 code compilation",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "lean_code": {
                                "type": "string",
                                "description": "LEAN code to verify"
                            }
                        },
                        "required": ["lean_code"]
                    }
                ),
                Tool(
                    name="solve_problem",
                    description="Solve problem with multi-agent orchestration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Problem description"
                            },
                        },
                        "required": ["query"]
                    }
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> Sequence[TextContent]:
            """Execute a tool."""
            try:
                if name == "prove_theorem":
                    result = await self.client.aprove(
                        statement=arguments["statement"],
                        search_premises=arguments.get("search_premises", True),
                        max_iterations=arguments.get("max_iterations", 10),
                    )

                    response = {
                        "verified": result.verified,
                        "lean_code": result.lean_code,
                        "iterations": result.iterations,
                        "total_time": result.total_time,
                        "premises_used": result.premises_used,
                        "errors": result.verification_details.errors,
                        "warnings": result.verification_details.warnings,
                        "sorry_count": result.verification_details.sorry_count
                    }

                    return [TextContent(type="text", text=json.dumps(response, indent=2))]

                elif name == "search_premises":
                    result = await self.client.asearch(
                        query=arguments["query"],
                        k=arguments.get("k", 10),
                    )

                    response = {
                        "count": result.count,
                        "search_method": result.search_method,
                        "premises": [
                            {
                                "full_name": p.full_name,
                                "statement": p.statement,
                                "similarity": p.similarity,
                                "file_path": p.file_path
                            }
                            for p in result.premises
                        ]
                    }

                    return [TextContent(type="text", text=json.dumps(response, indent=2))]

                elif name == "verify_lean_code":
                    result = self.client.verify(arguments["lean_code"])
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "solve_problem":
                    result = await self.client.asolve(query=arguments["query"])

                    response = {
                        "success": result.success,
                        "synthesis": result.synthesis,
                        "execution_time": result.execution_time,
                        "task_count": len(result.task_results),
                        "tasks": [
                            {
                                "task_type": tr.task_type,
                                "agent": tr.agent,
                                "success": tr.success,
                                "output": tr.output[:200] + "..." if len(tr.output) > 200 else tr.output,
                                "execution_time": tr.execution_time
                            }
                            for tr in result.task_results
                        ]
                    }

                    return [TextContent(type="text", text=json.dumps(response, indent=2))]

                else:
                    raise ValueError(f"Unknown tool: {name}")

            except AxMathError as e:
                logger.error(f"AxMath API error: {e}")
                return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]
            except Exception as e:
                logger.error(f"Tool execution failed: {e}", exc_info=True)
                return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]

    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Starting AxMath MCP Server (authenticated mode)...")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def create_server() -> AxMathMCPServer:
    """Create and configure AxMath MCP server."""
    return AxMathMCPServer()
