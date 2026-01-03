"""
Minimal Bencode encoder/decoder for .torrent files.
"""

import io
from typing import Any, Dict, List, Tuple, Union

def decode(data: bytes) -> Any:
    """
    Decode bencoded data.

    Args:
        data: Bencoded bytes

    Returns:
        Decoded object (dict, list, int, bytes)
    """
    if not data:
        raise ValueError("Empty data")

    src = io.BytesIO(data)

    def decode_item() -> Any:
        char = src.read(1)
        if not char:
            raise ValueError("Unexpected EOF")

        if char == b'i':
            # Integer: i<digits>e
            digits = []
            while True:
                c = src.read(1)
                if c == b'e':
                    break
                if not c:
                    raise ValueError("Unexpected EOF in integer")
                digits.append(c)
            return int(b"".join(digits))

        elif char == b'l':
            # List: l<items>e
            items = []
            while True:
                peek = src.read(1)
                if peek == b'e':
                    return items
                src.seek(-1, 1) # Backtrack
                items.append(decode_item())

        elif char == b'd':
            # Dictionary: d<key><value>e
            d = {}
            while True:
                peek = src.read(1)
                if peek == b'e':
                    return d
                src.seek(-1, 1) # Backtrack
                key = decode_item()
                if not isinstance(key, bytes):
                    raise ValueError(f"Dictionary key must be bytes, got {type(key)}")
                val = decode_item()
                d[key] = val
            return d

        elif char.isdigit():
            # String: <len>:<contents>
            digits = [char]
            while True:
                c = src.read(1)
                if c == b':':
                    break
                if not c:
                    raise ValueError("Unexpected EOF in string length")
                digits.append(c)
            length = int(b"".join(digits))
            content = src.read(length)
            if len(content) != length:
                raise ValueError("Unexpected EOF in string content")
            return content

        else:
            raise ValueError(f"Invalid bencode character: {char!r}")

    return decode_item()

def encode(obj: Any) -> bytes:
    """
    Encode object to bencoded bytes.

    Args:
        obj: Object to encode (dict, list, int, bytes, str)

    Returns:
        Bencoded bytes
    """
    if isinstance(obj, int):
        return b'i' + str(obj).encode() + b'e'
    elif isinstance(obj, bytes):
        return str(len(obj)).encode() + b':' + obj
    elif isinstance(obj, str):
        b = obj.encode('utf-8')
        return str(len(b)).encode() + b':' + b
    elif isinstance(obj, list):
        return b'l' + b''.join(encode(x) for x in obj) + b'e'
    elif isinstance(obj, dict):
        # Keys must be sorted strings/bytes
        items = []
        for k, v in sorted(obj.items()):
            if isinstance(k, str):
                k_bytes = k.encode('utf-8')
            elif isinstance(k, bytes):
                k_bytes = k
            else:
                raise TypeError("Dict keys must be str or bytes")
            items.append(encode(k) + encode(v)) # Encode key manually to ensure bytes
        return b'd' + b''.join(items) + b'e'
    else:
        raise TypeError(f"Unsupported type: {type(obj)}")
