from dataclasses import dataclass, field

# from opcodes import *


@dataclass
class ExecutionContext:
    code: bytes
    calldata: bytes = b""
    caller: int = 0
    origin: int = 0
    value: int = 0
    gas_limit: int = 0
    address: int = 0
    blocknumber: int = 0
    timestamp: int = 0


@dataclass
class EVMState:
    pc: int = 0
    gas_remaining: int = 0
    stack: list[int] = field(default_factory=list)
    memory: bytearray = field(default_factory=bytearray)
    storage: dict[int, int] = field(default_factory=dict)
    stopped: bool = False
    reverted: bool = False
    output: bytes = b""


UINT256_MAX = 2**256 - 1


def push(state: EVMState, value: int):
    assert len(state.stack) < 1024, "Stack overflow"
    state.stack.append(value & UINT256_MAX)
    # self.stack.append(value)


def pop(state: EVMState) -> int:
    assert len(state.stack) > 0, "Stack underflow"
    return state.stack.pop()


def mem_read(state: EVMState, offset: int, size: int) -> bytes:
    end = offset + size
    if end > len(state.memory):
        state.memory.extend(b"\x00" * (end - len(state.memory)))
    return bytes(state.memory[offset:end])


def mem_write(state: EVMState, offset: int, data: bytes):
    end = offset + len(data)
    if end > len(state.memory):
        state.memory.extend(b"\x00" * (end - len(state.memory)))
    state.memory[offset:end] = data


def run(ctx: ExecutionContext) -> EVMState:
    state = EVMState()
    state.gas_remaining = ctx.gas_limit
    valid_jumpdests = find_valid_jumpdests(ctx.code)

    while not state.stopped and state.pc < len(ctx.code):
        opcode = ctx.code[state.pc]
        state.pc += 1
        execute_opcode(opcode, ctx, state, valid_jumpdests)
    print(state)
    return state


# TODO: PUSH2, PUSH4, DUP1, EQ, JUMPI, JUMPDEST, CALLDATALOAD, SHR
def execute_opcode(
    opcode: int, ctx: ExecutionContext, state: EVMState, valid_jumpdests: set[int]
):
    # STOP
    if opcode == 0x00:
        state.stopped = True
    # ADD
    elif opcode == 0x01:
        a, b = pop(state), pop(state)
        push(state, (a + b) & UINT256_MAX)
    # PUSH0
    elif opcode == 0x5F:
        push(state, 0)
    # PUSH1 -- PUSH32
    elif opcode >= 0x60 and opcode <= 0x7F:
        n = opcode - 0x5F
        exec_push(ctx, state, n)
    # CALLDATALOAD
    elif opcode == 0x35:
        offset = pop(state)
        chunk = ctx.calldata[offset : offset + 32]
        chunk = chunk.ljust(32, b"\x00")
        push(state, int.from_bytes(chunk, "big"))
    # DUP1 -- DUP16
    elif opcode >= 0x80 and opcode <= 0x8F:
        n = opcode - 0x7F
        assert len(state.stack) >= n, "Stack underflow while DUP"
        value = state.stack[-n]
        push(state, value)
    # JUMPI
    elif opcode == 0x57:
        target, condition = pop(state), pop(state)
        if condition != 0:
            if target not in valid_jumpdests:  # , f"Invalid jump target: {target: #x}"
                state.stopped = True
                state.reverted = True
                return
            state.pc = target
    # JUMPDEST
    elif opcode == 0x5B:
        pass
    # EQ
    elif opcode == 0x14:
        lhs, rhs = pop(state), pop(state)
        push(state, 1 if lhs == rhs else 0)

    # SHR
    elif opcode == 0x1C:
        shift, value = pop(state), pop(state)
        if shift > 0xFF:
            push(state, 0)
        else:
            push(state, value >> shift)
    else:
        state.reverted = True
        state.stopped = True
        # raise RuntimeError(f"reverted on Unknown opcode 0x{opcode: 02x}")
        return
    # # PUSH1
    # elif opcode == 0x60:
    #     value = ctx.code[state.pc]
    #     state.pc += 1
    #     push(state, value)
    # elif opcode == 0x61: # PUSH2
    #     assert  state.pc + 2 <= len(ctx.code), "Code out of bounds"
    #     value = int.from_bytes(ctx.code[state.pc:state.pc+2], 'big')
    #     state.pc += 2
    #     push(state, value)


def exec_push(ctx: ExecutionContext, state: EVMState, n: int):
    data = read_code_bytes(ctx, state, n)
    value = int.from_bytes(data, byteorder="big")
    push(state, value)


def read_code_bytes(ctx: ExecutionContext, state: EVMState, n: int) -> bytes:
    data = ctx.code[state.pc : state.pc + n]
    assert len(data) == n, "EOF while reading PUSH data"
    state.pc += n
    return data


def find_valid_jumpdests(code: bytes) -> set[int]:
    valid = set()
    i = 0
    while i < len(code):
        op = code[i]
        if op == 0x5B:
            valid.add(i)
        if 0x60 <= op <= 0x7F:
            i += op - 0x5F
        i += 1
    return valid
