from typing import List, Optional, Union

__all__ = ["ReceiveBuffer"]


# Operations we want to support:
# - find next \r\n or \r\n\r\n (\n or \n\n are also acceptable),
#   or wait until there is one
# - read at-most-N bytes
# Goals:
# - on average, do this fast
# - worst case, do this in O(n) where n is the number of bytes processed
# Plan:
# - store bytearray, offset, how far we've searched for a separator token
# - use the how-far-we've-searched data to avoid rescanning
# - while doing a stream of uninterrupted processing, advance offset instead
#   of constantly copying
# WARNING:
# - I haven't benchmarked or profiled any of this yet.
#
# Note that starting in Python 3.4, deleting the initial n bytes from a
# bytearray is amortized O(n), thanks to some excellent work by Antoine
# Martin:
#
#     https://bugs.python.org/issue19087
#
# This means that if we only supported 3.4+, we could get rid of the code here
# involving self._start and self.compress, because it's doing exactly the same
# thing that bytearray now does internally.
#
# BUT unfortunately, we still support 2.7, and reading short segments out of a
# long buffer MUST be O(bytes read) to avoid DoS issues, so we can't actually
# delete this code. Yet:
#
#     https://pythonclock.org/
#
# (Two things to double-check first though: make sure PyPy also has the
# optimization, and benchmark to make sure it's a win, since we do have a
# slightly clever thing where we delay calling compress() until we've
# processed a whole event, which could in theory be slightly more efficient
# than the internal bytearray support.)


class ReceiveBuffer:
    def __init__(self) -> None:
        self._data = bytearray()
        self._next_line_search = 0
        self._multiple_lines_search = 0

    def __iadd__(self, byteslike: Union[bytes, bytearray]) -> "ReceiveBuffer":
        self._data += byteslike
        return self

    def __bool__(self) -> bool:
        return bool(self._data)

    def __len__(self) -> int:
        return len(self._data)

    # for @property unprocessed_data
    def __bytes__(self) -> bytes:
        return bytes(self._data)

    def _extract(self, count: int) -> bytearray:
        # extracting an initial slice of the data buffer and return it
        out = self._data[:count]
        del self._data[:count]

        self._next_line_search = 0
        self._multiple_lines_search = 0

        return out

    def maybe_extract_at_most(self, count: int) -> Optional[bytearray]:
        """
        Extract a fixed number of bytes from the buffer.
        """
        data = self._data
        if not data:
            return None
        available = len(data)
        if count >= available:
            return self._extract(available)
        return self._extract(count)

    def maybe_extract_next_line(self) -> Optional[bytearray]:
        """
        Extract the first line, if it is completed in the buffer.
        """
        data = self._data
        # Only search in buffer space that we've not already looked at.
        search_start_index = self._next_line_search - 1
        if search_start_index < 0:
            search_start_index = 0
        partial_idx = data.find(b"\r\n", search_start_index)

        if partial_idx == -1:
            self._next_line_search = len(data)
            return None

        # + 2 is to compensate len(b"\r\n")
        idx = partial_idx + 2

        return self._extract(idx)

    def _find_blank_line_end(self) -> Optional[int]:
        data = self._data
        search_start = self._multiple_lines_search
        data_len = len(data)

        while True:
            newline_index = data.find(b"\n", search_start)
            if newline_index == -1:
                break

            search_start = newline_index + 1
            self._multiple_lines_search = search_start

            if search_start >= data_len:
                break

            next_byte = data[search_start]

            if next_byte == 0x0A:  # \n\n
                return search_start + 1

            if next_byte == 0x0D:  # \n\r\n (covers \r\n\r\n)
                trailer_index = search_start + 1
                if trailer_index >= data_len:
                    break
                if data[trailer_index] == 0x0A:
                    return trailer_index + 1

        self._multiple_lines_search = max(0, data_len - 2)
        return None

    def maybe_extract_lines(self) -> Optional[List[bytearray]]:
        """
        Extract everything up to the first blank line, and return a list of lines.
        """
        # Handle the case where we have an immediate empty line.
        data = self._data
        if data[:1] == b"\n":
            self._extract(1)
            return []

        if data[:2] == b"\r\n":
            self._extract(2)
            return []

        # Only search in buffer space that we've not already looked at.
        idx = self._find_blank_line_end()
        if idx is None:
            return None

        # Truncate the buffer and return it.
        out = self._extract(idx)
        lines: List[bytearray] = []
        start = 0
        end = len(out)
        while start < end:
            newline_index = out.find(b"\n", start)
            if newline_index == -1:
                break
            line = out[start:newline_index]
            if line.endswith(b"\r"):
                del line[-1]
            if not line:
                break
            lines.append(line)
            start = newline_index + 1
        return lines

    # In theory we should wait until `\r\n` before starting to validate
    # incoming data. However it's interesting to detect (very) invalid data
    # early given they might not even contain `\r\n` at all (hence only
    # timeout will get rid of them).
    # This is not a 100% effective detection but more of a cheap sanity check
    # allowing for early abort in some useful cases.
    # This is especially interesting when peer is messing up with HTTPS and
    # sent us a TLS stream where we were expecting plain HTTP given all
    # versions of TLS so far start handshake with a 0x16 message type code.
    def is_next_line_obviously_invalid_request_line(self) -> bool:
        try:
            # HTTP header line must not contain non-printable characters
            # and should not start with a space
            return self._data[0] < 0x21
        except IndexError:
            return False
