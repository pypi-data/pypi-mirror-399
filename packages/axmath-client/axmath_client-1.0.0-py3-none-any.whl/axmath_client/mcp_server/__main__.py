"""
AxMath MCP Server - calls authenticated AxMath API.

This MCP server connects to the private AxMath service using API key authentication.
"""

import asyncio
import logging
import sys
from .server import create_server

logging.basicConfig(level=logging.INFO)


def main():
    """Run MCP server."""
    try:
        server = create_server()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logging.info("Shutting down MCP server...")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
