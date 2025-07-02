# src/gsp_core/protocol/slip.py

_END     = 0xC0
_ESC     = 0xDB
_ESC_END = 0xDC
_ESC_ESC = 0xDD

def encode(raw: bytes) -> bytes:
    """
    SLIP-encode a raw byte sequence.
    - Prepends END (0xC0)
    - Escapes END → ESC, ESC_END
    - Escapes ESC → ESC, ESC_ESC
    - Appends END (0xC0)
    """
    buf = bytearray([_END])
    for b in raw:
        if b == _END:
            buf.extend([_ESC, _ESC_END])
        elif b == _ESC:
            buf.extend([_ESC, _ESC_ESC])
        else:
            buf.append(b)
    buf.append(_END)
    return bytes(buf)

def decode(frame: bytes) -> bytes:
    """
    Decode a SLIP frame with leading and trailing END.
    - Validates both delimiters
    - Removes delimiters
    - Un-escapes ESC_END → END and ESC_ESC → ESC
    """
    if not frame or frame[0] != _END or frame[-1] != _END:
        raise ValueError("Incomplete SLIP frame (missing END delimiters)")
    out = bytearray()
    esc = False
    # process payload between delimiters
    for b in frame[1:-1]:
        if esc:
            if b == _ESC_END:
                out.append(_END)
            elif b == _ESC_ESC:
                out.append(_ESC)
            else:
                raise ValueError(f"Invalid SLIP escape: 0x{b:02X}")
            esc = False
        elif b == _ESC:
            esc = True
        else:
            out.append(b)
    if esc:
        raise ValueError("SLIP frame ends with unfinished escape")
    return bytes(out)

