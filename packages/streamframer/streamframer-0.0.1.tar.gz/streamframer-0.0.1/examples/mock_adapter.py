import socket
import time
from collections import deque
from streamframer.manager import BufferManager, until_delim, until_eot, read_with_rule, read_until_timeout
from typing import Optional


class CustomError(Exception):
    pass


class FakeSocket:
    """
    Minimal socket-like object:
    - sendall(data): parses '\n'-terminated commands
    - recv(n): returns queued reply bytes (or raises socket.timeout)
    - settimeout/gettimeout/connect/close/shutdown implemented
    """
    def __init__(self, responder, default_timeout=1.0):
        self._responder = responder          # callable(cmd_str)->bytes|None
        self._timeout = default_timeout
        self._rx = deque()                   # queued bytes objects
        self._closed = False
        self._connected = False

    def settimeout(self, t):
        self._timeout = t

    def gettimeout(self):
        return self._timeout

    def connect(self, addr):
        self._connected = True

    def close(self):
        self._closed = True

    def shutdown(self, how):
        self._closed = True

    def sendall(self, data: bytes):
        if self._closed:
            raise OSError("Socket is closed")
        text = data.decode("ascii", errors="replace")
        # may contain multiple commands if caller batches
        for line in text.split("\n"):
            cmd = line.strip()
            if not cmd:
                continue
            reply = self._responder(cmd)
            if reply:
                self._rx.append(reply)

    def recv(self, n: int) -> bytes:
        if self._closed:
            return b""
        
        if not self._rx:
            # behave like a real socket: block until timeout -> socket.timeout
            if self._timeout is None:
                # blocking mode: wait until data arrives (or socket is closed)
                while not self._rx and not self._closed:
                    time.sleep(0.001)
                if self._closed:
                    return b""
                # data arrived
            else:
                time.sleep(self._timeout)
                raise socket.timeout()
            
        chunk = self._rx.popleft()
        if len(chunk) <= n:
            return chunk
        # if reply bigger than n, split it like TCP can
        self._rx.appendleft(chunk[n:])
        return chunk[:n]


class MockPrologixResponder:
    """
    Scripted “adapter + instrument” behavior.
    - ++ver -> version line ending with LF
    - instrument cmd -> stored as pending reply
    - ++read eoi -> returns pending reply + NUL (0x00) to emulate EOI/EOT framing
    - ++read -> returns pending reply (no NUL), for timeout-based reads if you want
    """
    def __init__(self, version="Prologix GPIB-ETHERNET 6.0"):
        self.version = version
        self.pending = b"MOCK_REPLY\n"

    def __call__(self, cmd: str) -> Optional[bytes]:
        # Prologix commands:
        if cmd == "++ver":
            return (self.version + "\n").encode("ascii")
        if cmd.startswith("++addr "):
            return b""  # no response
        if cmd.startswith("++eos "):
            return b""  # no response
        if cmd.startswith("++eot_enable "):
            return b""
        if cmd.startswith("++eot_char "):
            return b""
        if cmd.startswith("++auto "):
            return b""
        if cmd.startswith("++mode "):
            return b""
        if cmd in ("++mode", "++srq", "++spoll"):
            return b"0\n"

        # Reads:
        if cmd == "++read eoi":
            return self.pending + b"\x00"   # NUL terminator as EOT marker
        if cmd == "++read":
            return self.pending             # no NUL

        # Otherwise treat as instrument command:
        # You can customize per command here:
        if cmd in ("*IDN?", "IDN?", "ID?"):
            self.pending = b"MOCK,MODEL,1234,1.0\n"
        else:
            self.pending = f"OK:{cmd}\n".encode("ascii")
        return b""


class AdapterConnection:
    """
    Drop-in mock version (same name) to let you run your higher-level logic without hardware.
    Keeps your read/write/query API.

    Uses the new BufferManager + read_with_rule/read_until_timeout API (single buffer per socket).
    """
    PORT = 1234

    def __init__(self, device_name, ip_ad, gpib_ad, timeout=1):
        self.device_name = device_name
        self.ip_ad = ip_ad
        self.gpib_ad = gpib_ad

        # framing / adapter settings
        self._eot_char = 10          # LF by default
        self._eos = None
        self._eoi_supported = True   # mock supports EOI/EOT framing by default

        # one BufferManager per byte stream (socket)
        self.buf_man = BufferManager()

        # fake socket wired to scripted responder
        self._responder = MockPrologixResponder()
        self._socket = FakeSocket(self._responder, default_timeout=timeout)

        self.set_timeout(timeout)
        self._init_adapter()

    def set_timeout(self, value):
        if value < 1e-3 or value > 3:
            raise CustomError("Timeout must be >= 1e-3 and <= 3")
        self._socket.settimeout(value)

    # ---------------- adapter IO helpers

    def _send_to_adap(self, cmd: str) -> None:
        try:
            self._socket.sendall((f"{cmd}\n").encode("ascii"))
        except Exception as e:
            raise CustomError(f"Failed to send command: {e}") from e

    def _read_prologix_line(self) -> str:
        # Prologix responses are line-based; accept \n or \r\n
        line_rule = until_delim(b"\n", strip_before=b"\r")  # public API (do not use internal _FRAMING_RULES)
        f = read_with_rule(self._socket, self.buf_man, line_rule)
        try:
            raw = f.to_bytes()
        finally:
            f.consume()
        return raw.decode("ascii", errors="replace").strip()

    def _read_instr_eot(self, max_bytes: int = 1024 * 1024) -> str:
        # Instrument replies framed by EOT byte (often enabled via ++eot_enable)
        f = read_with_rule(
            self._socket,
            self.buf_man,
            until_eot(self._eot_char),
            max_bytes=max_bytes,
        )
        try:
            raw = f.to_bytes()
        finally:
            f.consume()
        return raw.decode("ascii", errors="replace")

    def _read_prologix_cmds(self) -> str:
        # ignore empty lines
        while True:
            line = self._read_prologix_line()
            if line:
                return line

    def _recv_until_eot(self, max_bytes: int = 1024 * 1024) -> str:
        return self._read_instr_eot(max_bytes=max_bytes)

    def _recv_until_timeout(self, **kw) -> str:
        # consume=True consumes only bytes received during THIS call.
        raw = read_until_timeout(self._socket, self.buf_man, consume=True, **kw)
        return raw.decode("ascii", errors="replace")

    def _read_gpib(self, max_bytes=1024 * 1024, overall_timeout=2.0) -> str:
        self._send_to_adap("++read eoi")
        if getattr(self, "_eoi_supported", False):
            return self._recv_until_eot(max_bytes=max_bytes)
        return self._recv_until_timeout(max_bytes=max_bytes, overall_timeout=overall_timeout)

    # ---------------- public API

    def write(self, cmd: str) -> None:
        self._send_to_adap(cmd)

    def read(self, max_bytes=1024 * 1024, overall_timeout=2.0) -> str:
        return self._read_gpib(max_bytes=max_bytes, overall_timeout=overall_timeout)

    def query(self, cmd: str, max_bytes=1024 * 1024, overall_timeout=2.0) -> str:
        self.write(cmd)
        return self.read(max_bytes=max_bytes, overall_timeout=overall_timeout)

    # ---------------- init / shutdown

    def _init_adapter(self):
        self._connect_to_adapter()
        self._set_eot_char(self._eot_char)
        self._set_eot_enable(1)
        self._set_gpib_address(self.gpib_ad)

    def _connect_to_adapter(self):
        self._socket.connect((self.ip_ad, self.PORT))
        version = self._get_version()
        print(f"✅ Adapter (MOCK): {self.ip_ad} - Version: {version}")

    def close(self):
        self._socket.close()

    def shutdown(self):
        self._socket.shutdown(socket.SHUT_RDWR)

    # ---------------- prologix commands you use

    def _get_version(self):
        self._send_to_adap("++ver")
        return self._read_prologix_cmds()

    def _set_gpib_address(self, addr: int):
        self._send_to_adap(f"++addr {addr}")

    def _set_eos(self, eos: int):
        self._send_to_adap(f"++eos {eos}")

    def _set_eot_enable(self, value: int):
        self._send_to_adap(f"++eot_enable {value}")

    def _set_eot_char(self, value: int):
        self._send_to_adap(f"++eot_char {value}")


# ---------------- examples

def main():
    c = AdapterConnection("dev", "127.0.0.1", 5, timeout=3)

    # 1) Standard SCPI-style query
    print("IDN:", c.query("*IDN?"))

    # 2) Another instrument query
    print("VSET:", c.query("VSET?"))

    # 3) Read-only (assumes something is already waiting after prior commands)
    print("READ:", c.read(overall_timeout=1.0))

    # 4) Timeout-style read (settings/probing style; consumes only new bytes received this call)
    print("RAW:", c._recv_until_timeout(overall_timeout=0.5))

    c.close()


if __name__ == "__main__":
    main()
