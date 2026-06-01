# minievm

A minimal Ethereum Virtual Machine (EVM) implementation in pure Python, built for educational purposes and experimentation.

## Synopsis

minievm is a lightweight, from-scratch EVM interpreter that executes Ethereum bytecode. It implements a subset of opcodes with correct uint256 arithmetic, stack/memory operations, and jump-destination validation. The codebase is deliberately small (~170 lines) and readable, making it suitable for learning how the EVM works under the hood.

## Features

- **PUSH0–PUSH32** — Push 1–33 bytes onto the stack
- **DUP1–DUP16** — Duplicate stack items at depth 1–16
- **ADD** — Addition with uint256 wrap-around
- **EQ** — Equality comparison (0 or 1)
- **SHR** — Bitwise shift right
- **CALLDATALOAD** — Load 32 bytes from calldata
- **JUMPI / JUMPDEST** — Conditional jumps with validated destinations
- **STOP** — Clean halting
- **Memory** — Automatic expansion on read/write (planned: `MLOAD`/`MSTORE`)
- **Gas** — Gas table defined (not yet wired into execution)

### Opcode support

| Opcode | Value | Status |
|---|---|---|
| STOP | 0x00 | ✅ |
| ADD | 0x01 | ✅ |
| EQ | 0x14 | ✅ |
| SHR | 0x1C | ✅ |
| CALLDATALOAD | 0x35 | ✅ |
| JUMPI | 0x57 | ✅ |
| JUMPDEST | 0x5B | ✅ |
| PUSH0 | 0x5F | ✅ |
| PUSH1–PUSH32 | 0x60–0x7F | ✅ |
| DUP1–DUP16 | 0x80–0x8F | ✅ |
| MLOAD / MSTORE | 0x51–0x52 | 🔲 (gas table only) |
| CALL | 0xF1 | 🔲 (gas table only) |
| RETURN | 0xF3 | 🔲 (gas table only) |
| REVERT | 0xFD | 🔲 (gas table only) |
| All others | — | ❌ |

## Quick start

```python
from src.evm import ExecutionContext, run

# PUSH1 3, PUSH1 4, ADD, STOP
code = bytes([0x60, 0x03, 0x60, 0x04, 0x01, 0x00])
result = run(ExecutionContext(code=code))

print(result.stack)   # [7]
print(result.stopped) # True
```

No dependencies outside the Python standard library (3.12+).

## API

### `ExecutionContext`

Input context for a single EVM execution.

| Field | Type | Default | Description |
|---|---|---|---|
| `code` | `bytes` | — | EVM bytecode to execute |
| `calldata` | `bytes` | `b""` | Input data (e.g. for transactions) |
| `caller` | `int` | `0` | Address of the caller |
| `origin` | `int` | `0` | Origin address |
| `value` | `int` | `0` | Value sent (in wei) |
| `gas_limit` | `int` | `0` | Gas limit for execution |
| `address` | `int` | `0` | Address of the executing contract |
| `blocknumber` | `int` | `0` | Current block number |
| `timestamp` | `int` | `0` | Current block timestamp |

### `EVMState`

Mutable VM state produced by `run()`.

| Field | Type | Description |
|---|---|---|
| `pc` | `int` | Program counter |
| `gas_remaining` | `int` | Remaining gas (zero unless gas_limit is set) |
| `stack` | `list[int]` | EVM stack (max 1024) |
| `memory` | `bytearray` | Linear memory (auto-expanding) |
| `storage` | `dict[int, int]` | Persistent storage |
| `stopped` | `bool` | Whether execution has halted |
| `reverted` | `bool` | Whether the execution reverted |
| `output` | `bytes` | Return data |

### `run(ctx: ExecutionContext) -> EVMState`

Main entry point. Executes bytecode and returns the final state.

### Helpers

- `push(state, value)` — Push a uint256 value onto the stack.
- `pop(state)` — Pop and return the top stack item.
- `mem_read(state, offset, size)` — Read `size` bytes from memory at `offset` (auto-expands).
- `mem_write(state, offset, data)` — Write `data` bytes to memory at `offset` (auto-expands).
- `find_valid_jumpdests(code)` — Return a `set[int]` of valid JUMPDEST offsets, skipping PUSH data.

## Running tests

```bash
python test_vm.py
```

Tests are self-contained (no pytest). The runner discovers all `test_*` functions and reports pass/fail.

## Project structure

```
minievm/
├── README.md          <- This file
├── LICENSE            <- GPL-3.0
├── src/
│   ├── __init__.py    <- Package marker
│   ├── evm.py         <- Core EVM engine (run, opcodes, helpers)
│   ├── gas.py         <- Gas cost table
│   ├── opcodes.py     <- Placeholder
│   └── types.py       <- Placeholder
└── test_vm.py         <- Test suite
```

## License

GNU General Public License v3.0 — see [LICENSE](LICENSE).
