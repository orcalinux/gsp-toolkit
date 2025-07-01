# desktop/tests/test_slip.py

import pytest
from gsp_toolkit.slip import encode, decode, _END, _ESC, _ESC_END, _ESC_ESC

def test_encode_wraps_with_end():
    data = b"ABC"
    frame = encode(data)
    # Frame must start and end with END
    assert frame[0] == _END
    assert frame[-1] == _END
    # Middle bytes match original data
    assert frame[1:-1] == data

def test_escape_sequences_roundtrip():
    # Data containing special bytes
    data = bytes([_END, _ESC, 0x01, 0x02, _END, _ESC])
    frame = encode(data)
    decoded = decode(frame)
    assert decoded == data

def test_missing_delimiters_raises():
    with pytest.raises(ValueError):
        decode(b'')              # empty
    with pytest.raises(ValueError):
        decode(b'ABC')           # no delimiters at all
    with pytest.raises(ValueError):
        decode(bytes([_END, ord('A'), ord('B'), ord('C')]))  # missing trailing END
    with pytest.raises(ValueError):
        decode(bytes([ord('A'), ord('B'), ord('C'), _END]))  # missing leading END

def test_unfinished_escape_raises():
    # ESC without following escape code
    frame = bytes([_END, _ESC, _END])
    with pytest.raises(ValueError):
        decode(frame)

def test_invalid_escape_raises():
    # ESC followed by invalid code
    frame = bytes([_END, _ESC, 0x00, _END])
    with pytest.raises(ValueError):
        decode(frame)
