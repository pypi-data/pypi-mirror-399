# streamframer

Small, low-level framing primitives for byte streams.

This library provides:
- persistent buffering for stream-oriented I/O (e.g. TCP sockets)
- delimiter-based framing rules
- zero-copy frame views with explicit consumption

It is designed for instrument protocols and other byte streams where messages may span multiple `recv()` calls.

⚠️ **Status**: Pre-alpha. API is not yet stable.

---

## Design Goals

- No protocol assumptions
- No background threads
- No hidden buffering
- Zero-copy access to payloads
- Explicit lifecycle control

This is **not** a full protocol library.  
It only solves buffering and framing.

---

## Core Concepts

### BufferManager
Owns a single byte buffer and scan position.  
Bytes persist across reads until explicitly consumed.

### Framing Rules
A rule inspects `(buffer, scan_position)` and decides:
- whether a complete message exists
- where scanning should resume
- how many bytes belong to the message

Rules may minimize unnecessary rescanning when possible, but no protocol-level guarantees are made.

Included helpers:
- `until_delim(b"...")`
- `until_eot(byte)`

### Frame
A zero-copy `memoryview` into the buffer.

Bytes are removed **only** when `Frame.consume()` is explicitly called.  
While a `Frame` exists, the underlying buffer must not be mutated.

---

## Important Notes

- **Rule selection is the caller’s responsibility.**
- Trying multiple rules sequentially (e.g. newline first, then EOT) can cause protocol misclassification if payloads contain overlapping delimiters.
- This library does not attempt to detect or resolve such ambiguities.

---

## Minimal Example

```python
from streamframer import BufferManager, until_delim, read_with_rule
import socket

sock = socket.create_connection(("127.0.0.1", 1234))
mgr = BufferManager()
rule = until_delim(b"\n")

while True:
    frame = read_with_rule(sock, mgr, rule)
    if frame is None:
        continue

    data = bytes(frame)
    frame.consume()
    print(data)

```

## Non-Goals

- No protocol detection
- No message validation
- No concurrency abstractions

If you need a full protocol stack, this library is not for you.