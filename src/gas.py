GAS_TABLE = {
    0x00: 0,
    0x01: 3,
    0x1C: 3,
    0x35: 3,  # calldataload
    0x51: 3,  # MLOAD
    0x52: 3,  # MSTORE
    0x57: 10,  # jumpi
    0x5B: 1,  # jumpdest
    0x5F: 3,
    0x60: 3,  # push1
    0x61: 3,
    0x7F: 3,
    0x80: 3,  # dup1
    0x8F: 3,
    0xF1: 100,  # CALL
    0xF3: 0,  # return
    0xFD: 0,  # revert
}
