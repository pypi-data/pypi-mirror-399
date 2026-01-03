# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Monora is a **dual-SDK project** providing governance and tracing for AI systems in both **Python** and **Node.js**. The two SDKs maintain feature parity and share the same configuration schema.

## Build and Test Commands

### Python SDK
```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,yaml,https]"

# Run all tests
.venv/bin/python -m pytest tests/ -v

# Run single test file
.venv/bin/python -m pytest tests/test_integration.py -v

# Run single test
.venv/bin/python -m pytest tests/test_integration.py::test_end_to_end_flow -v

# Lint
ruff check monora/
black --check monora/
```

### Node.js SDK
```bash
# Setup (from monora-node directory)
cd monora-node
npm install

# Run all tests
npm test

# Run single test file
npm test -- src/wal.test.ts

# Build
npm run build

# Clean
npm run clean
```

## Architecture

### Dual SDK Structure
```
Monora_beta/
├── monora/           # Python SDK
│   ├── runtime.py    # Core initialization, event emission, shutdown
│   ├── config.py     # Configuration loading (YAML/JSON/env)
│   ├── context.py    # Trace context propagation (contextvars)
│   ├── hasher.py     # SHA256 hash chain for event immutability
│   ├── signing.py    # Ed25519/HMAC-SHA256 event signatures
│   ├── wal.py        # Write-ahead log for crash resilience
│   ├── policy.py     # Model allowlist/denylist enforcement
│   ├── reporting.py  # Trust summary and compliance report generation
│   └── sinks/        # Output destinations (stdout, file, https)
├── monora-node/src/  # Node.js SDK (TypeScript)
│   ├── runtime.ts    # Core initialization, event emission, shutdown
│   ├── config.ts     # Configuration loading
│   ├── context.ts    # Trace context propagation (AsyncLocalStorage)
│   ├── hasher.ts     # SHA256 hash chain
│   ├── signing.ts    # Ed25519/HMAC-SHA256 signatures
│   ├── wal.ts        # Write-ahead log
│   ├── policy.ts     # Policy enforcement
│   └── sinks/        # Output sinks
└── tests/            # Python tests
```

### Event Flow
```
User Code → Decorator/API → Signer → Hasher → WAL → Dispatcher → Sinks
                                                          ↓
                                               Report Manager (trace completion)
```

1. **Signing** (optional): Event is signed with Ed25519 or HMAC-SHA256 before hashing
2. **Hashing**: Event gets `prev_hash` and `event_hash` for chain integrity
3. **WAL**: Event written to write-ahead log before emission (crash resilience)
4. **Dispatch**: Event queued to background worker
5. **Sinks**: Written to stdout/file/HTTPS endpoints
6. **WAL Commit**: After successful sink write, WAL entry marked committed

### Key Configuration Sections
```yaml
sinks:        # Output destinations
immutability: # Hash chain settings, verify_on_emit, verify_on_shutdown
policies:     # Model allowlist/denylist
data_handling: # Regex redaction rules
wal:          # Write-ahead log (enabled, path, sync_mode)
signing:      # Event signatures (enabled, algorithm, key_file/key_env)
ai_act:       # EU AI Act compliance settings
```

### Context Propagation
- **Python**: Uses `contextvars` for async-safe trace context
- **Node.js**: Uses `AsyncLocalStorage` for trace context
- Both provide `bind_context()`, `capture_context()`, `run_in_context()` utilities

### Important Patterns

**Adding a new feature to both SDKs:**
1. Add to Python `monora/config.py` DEFAULT_CONFIG
2. Add to Node.js `monora-node/src/config.ts` DEFAULT_CONFIG and MonoraConfig interface
3. Implement feature in Python module
4. Implement parallel feature in Node.js (maintain API parity)
5. Integrate into `runtime.py` and `runtime.ts`
6. Write tests in `tests/test_*.py` and `monora-node/src/*.test.ts`

**Event structure:**
```json
{
  "event_id": "evt_...",
  "event_type": "llm_call|tool_call|agent_step|custom",
  "trace_id": "trc_...",
  "timestamp": "ISO8601",
  "body": { ... },
  "event_signature": { "algorithm": "...", "signature": "..." },
  "prev_hash": "sha256:...",
  "event_hash": "sha256:..."
}
```

## CLI Tools

```bash
# Python CLI
monora init           # Generate config wizard
monora validate       # Validate config
monora doctor         # Diagnose config issues
monora report         # Generate reports from event logs
```

## Testing Notes

- Python tests use pytest with fixtures in each test file
- Node.js tests use Jest with `.test.ts` suffix
- Integration tests in `tests/test_integration.py` and `monora-node/src/runtime.test.ts`
- WAL tests require temp directories (use `tmp_path` fixture in Python, `fs.mkdtempSync` in Node.js)
- Signing tests use environment variables for keys (`MONORA_SIGNING_KEY`)
