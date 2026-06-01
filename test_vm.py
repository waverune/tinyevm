from src.evm import *


def test_add1():
    result = run(ExecutionContext(code=[0x60, 0x03, 0x60, 0x04, 0x01, 0x00]))
    assert result.stack == [7]


def test_add_wrap_around_max_uint256():
    result = run(
        ExecutionContext(
            code=bytes([0x7F])
            + bytes([0xFF] * 32)
            + bytes(
                [
                    0x60,
                    0x04,
                    0x01,
                    0x00,
                ]
            )
        )
    )
    assert result.stack == [3]


def test_eq_true():
    result = run(ExecutionContext(code=bytes([0x60, 0x05, 0x60, 0x05, 0x14, 0x00])))
    assert result.stack == [1]


def test_eq_false():
    result = run(
        ExecutionContext(code=bytes([0x61, 0x05, 0x01, 0x60, 0x05, 0x14, 0x00]))
    )
    assert result.stack == [0]


def test_dup1():
    result = run(
        ExecutionContext(code=bytes([0x60, 0x05, 0x62, 0x1, 0x2, 0x3, 0x80, 0x00]))
    )
    print(result)

    assert result.stack == [5, 66051, 66051]


def test_dup3():
    result = run(
        ExecutionContext(code=bytes([0x60, 0x05, 0x60, 0x6, 0x60, 0xF, 0x82, 0x00]))
    )
    print(result)

    assert result.stack == [5, 6, 15, 5]


def test_push32_max():
    # PUSH32 of UINT256_MAX, then STOP
    code = bytes([0x7F]) + bytes([0xFF] * 32) + bytes([0x00])
    result = run(ExecutionContext(code=code))
    assert result.stack == [2**256 - 1]


def test_shr_gt_0xff():
    code = bytes([0x61, 0x12, 0x34, 0x60, 0x00])
    result = run(ExecutionContext(code=code))
    print(result)
    assert result.stack == [0]


### FAILS


def test_invalid_op_revert():
    result = run(ExecutionContext(code=bytes([0xF9, 0x05, 0x80, 0x00])))
    print("fails >>>>>", result)
    assert result.reverted == True


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} passed")
