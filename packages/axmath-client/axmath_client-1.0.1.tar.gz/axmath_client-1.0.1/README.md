# AxMath Client

Python client for the **AxMath theorem proving API** - connects to private AxMath service.

> ⚠️ **This is a client library only.** The actual theorem proving happens on private AxMath servers. You need an API key to use this service.

## Installation

```bash
pip install axmath-client
```

## Quick Start

### 1. Get API Key

Register at **https://axmath.yourdomain.com/auth/register** to get your API key.

### 2. Set Environment Variable

```bash
export AXMATH_API_KEY="axm_abc123..."
```

### 3. Use the Client

```python
from axmath_client import AxMath

# Initialize client (uses AXMATH_API_KEY from environment)
client = AxMath()

# Prove a theorem
result = client.prove("Sum of two even numbers is even")
if result.verified:
    print("✅ Proof verified!")
    print(result.lean_code)
else:
    print("❌ Proof failed")
    print(result.verification_details.errors)

# Search for relevant premises
search_result = client.search("Cauchy-Schwarz inequality", k=5)
for premise in search_result.premises:
    print(f"{premise.similarity:.3f} - {premise.full_name}")

# Solve complex problems with multi-agent orchestration
solve_result = client.solve(
    "Prove that sqrt(2) is irrational and verify numerically"
)
print(solve_result.synthesis)
```

## Features

- ✅ **Theorem Proving** - Generate LEAN 4 proofs with DeepSeek-Prover-V2
- ✅ **Premise Search** - Search 180K mathlib4 premises with FAISS
- ✅ **Formal Verification** - Verify LEAN code compilation
- ✅ **Multi-Agent Solving** - Orchestrate complex problem solving
- ✅ **Async Support** - Full async/await API
- ✅ **Type Safe** - Pydantic models for all responses

## API Reference

### `AxMath(api_key=None, api_url=None, timeout=120.0)`

Initialize client.

**Parameters:**
- `api_key` (str, optional): API key. If not provided, reads from `AXMATH_API_KEY` env var.
- `api_url` (str, optional): API base URL. Defaults to production server.
- `timeout` (float): Default timeout for requests in seconds.

**Example:**
```python
# Option 1: Environment variable
client = AxMath()

# Option 2: Pass API key directly
client = AxMath(api_key="axm_abc123...")
```

### `prove(statement, search_premises=True, max_iterations=10, timeout=None)`

Prove a theorem in LEAN 4.

**Parameters:**
- `statement` (str): Theorem to prove (natural language or LEAN syntax)
- `search_premises` (bool): Search for relevant mathlib4 premises
- `max_iterations` (int): Maximum proving iterations
- `timeout` (float, optional): Override default timeout

**Returns:** `ProveResult`
- `verified` (bool): Whether proof was verified
- `lean_code` (str): Generated LEAN code
- `iterations` (int): Number of iterations used
- `total_time` (float): Execution time
- `premises_used` (List[str]): Premises used in proof
- `verification_details` (VerificationDetails): Errors, warnings, sorry count

**Example:**
```python
result = client.prove("∀ (n : ℕ), n + 0 = n")
print(result.lean_code)
```

### `search(query, k=10, use_tfidf_fallback=True)`

Search mathlib4 premises.

**Parameters:**
- `query` (str): Search query
- `k` (int): Number of results
- `use_tfidf_fallback` (bool): Use TF-IDF if FAISS fails

**Returns:** `SearchResult`
- `count` (int): Number of results
- `search_method` (str): "faiss" or "tfidf"
- `premises` (List[Premise]): Matching premises with similarity scores

**Example:**
```python
result = client.search("Cauchy-Schwarz", k=5)
for premise in result.premises:
    print(f"{premise.full_name}: {premise.similarity:.3f}")
```

### `verify(lean_code)`

Verify LEAN 4 code compilation.

**Parameters:**
- `lean_code` (str): LEAN code to verify

**Returns:** `dict` with errors, warnings, exit_code

**Example:**
```python
code = "theorem test : 2 + 2 = 4 := by rfl"
result = client.verify(code)
```

### `solve(query, timeout=300.0)`

Solve problem with multi-agent orchestration.

**Parameters:**
- `query` (str): Problem description
- `timeout` (float): Timeout in seconds

**Returns:** `SolveResult`
- `success` (bool): Whether problem was solved
- `synthesis` (str): Final synthesis
- `execution_time` (float): Total time
- `task_results` (List[TaskResult]): Individual task results

**Example:**
```python
result = client.solve("Prove sqrt(2) is irrational and verify numerically")
print(result.synthesis)
```

### `get_usage()`

Get usage statistics for your API key.

**Returns:** `dict` with request counts and quotas

**Example:**
```python
usage = client.get_usage()
print(f"Daily requests: {usage['daily_requests']}/{usage['daily_limit']}")
```

## Async API

All methods have async versions with `a` prefix:

```python
import asyncio
from axmath_client import AxMath

async def main():
    async with AxMath() as client:
        # Async prove
        result = await client.aprove("∀ n : ℕ, n + 0 = n")

        # Async search
        search_result = await client.asearch("Cauchy-Schwarz")

        # Async solve
        solve_result = await client.asolve("Prove sqrt(2) is irrational")

asyncio.run(main())
```

## MCP Server (Claude Desktop)

Install with MCP support:

```bash
pip install axmath-client[mcp]
```

Configure in Claude Desktop (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "axmath": {
      "command": "axmath-mcp-server",
      "env": {
        "AXMATH_API_KEY": "axm_abc123..."
      }
    }
  }
}
```

Then use in Claude Desktop:
- "Prove that n + 0 = n in LEAN 4"
- "Search mathlib for Cauchy-Schwarz inequality"

## Error Handling

```python
from axmath_client import (
    AxMath,
    AuthenticationError,
    RateLimitError,
    ServerError,
    NetworkError,
)

try:
    client = AxMath(api_key="invalid")
except AuthenticationError as e:
    print(f"Auth failed: {e}")

try:
    result = client.prove("theorem")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
except ServerError as e:
    print(f"Server error: {e}")
except NetworkError as e:
    print(f"Network error: {e}")
```

## Access

Contact for API access and credentials.

## What Stays Private

The AxMath service (not included in this package):
- DeepSeek-Prover-V2 integration
- FAISS search implementation (180K premises)
- LEAN verification infrastructure
- Multi-agent orchestration
- Proprietary algorithms

This package only provides the **API client** to connect to the private service.

## Support

- **Documentation**: https://axmath.yourdomain.com/docs
- **API Reference**: https://axmath.yourdomain.com/api/docs
- **Issues**: https://github.com/dirkenglund/math-physics-agents-dream-team/issues

## License

MIT License - See LICENSE file for details.
