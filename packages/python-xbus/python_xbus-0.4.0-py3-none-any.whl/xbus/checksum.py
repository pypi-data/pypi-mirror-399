from typing import Optional

import crccheck.crc


class Checksum:
    def __init__(self, data: Optional[bytes] = None):
        self._crc = crccheck.crc.Crc32c()
        if data is not None:
            self.update(data)

    def update(self, data: bytes):
        self._crc.process(data)

    def final(self):
        return self._crc.final()
