import pytest
from zippathlib.__main__ import _i2h, _h2i

@pytest.mark.parametrize("n, expected", [
    (0, "0 bytes"),
    (100, "100 bytes"),
    (1023, "1,023 bytes"),
    (1024, "1,024 bytes"),
    (1024 * 1024 - 1, "1,048,575 bytes"),
    (1024 * 1024, "1.00MB"),
    (1024 * 1024 * 1024, "1.00GB"),
    (1024 * 1024 * 1024 * 1024, "1.00TB"),
    (1500, "1,500 bytes"),
    (1500000, "1.43MB"),
    (1500000000, "1.40GB"),
])
def test_i2h(n: int, expected: str):
    assert _i2h(n) == expected

@pytest.mark.parametrize("s, expected", [
    ("", 0),
    ("0 bytes", 0),
    ("100 bytes", 100),
    ("1,023 bytes", 1023),
    ("1,024 bytes", 1024),
    ("1,048,575 bytes", 1048575),
    ("1024", 1024),
    ("1.00MB", 1024 * 1024),
    ("1.00GB", 1024 * 1024 * 1024),
    ("1.00TB", 1024 * 1024 * 1024 * 1024),
    ("1K", 1024),
    ("1.5K", 1536),
    ("1.43MB", 1499463), # 1.43 * 1024 * 1024 = 1499463.68 -> 1499463
    ("1.40GB", 1503238553), # 1.40 * 1024**3 = 1503238553.6 -> 1503238553
])
def test_h2i(s: str, expected: int):
    assert _h2i(s) == expected

def test_roundtrip():
    for n in [0, 100, 1024, 1024*1024, 1024*1024*1024]:
        assert _h2i(_i2h(n)) == n
