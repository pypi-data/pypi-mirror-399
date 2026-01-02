"""CRC utilities for generating Steam shortcut game IDs.

Steam uses a 64-bit identifier for shortcuts where:
- The first 32 bits are a CRC32 hash of (exe + appname) with the MSB set
- The last 32 bits are 0x02000000

This allows Steam to generate the steam://rungameid/### URL for shortcuts.
"""


class CRC32:
    """CRC32 calculator with configurable parameters.

    Based on the pycrc implementation by Thomas Pircher (MIT license).
    Configured for Steam's specific CRC32 variant.
    """

    def __init__(
        self,
        *,
        width: int = 32,
        poly: int = 0x04C11DB7,
        reflect_in: bool = True,
        xor_in: int = 0xFFFFFFFF,
        reflect_out: bool = True,
        xor_out: int = 0xFFFFFFFF,
    ):
        self.width = width
        self.poly = poly
        self.reflect_in = reflect_in
        self.xor_in = xor_in
        self.reflect_out = reflect_out
        self.xor_out = xor_out

        self.msb_mask = 1 << (self.width - 1)
        self.mask = ((self.msb_mask - 1) << 1) | 1

    def _reflect(self, data: int, width: int) -> int:
        """Reflect (reverse) the bits in a value."""
        result = data & 0x01
        for _ in range(width - 1):
            data >>= 1
            result = (result << 1) | (data & 0x01)
        return result

    def calculate(self, data: str | bytes) -> int:
        """Calculate CRC32 for the given data.

        Uses the bit-by-bit-fast algorithm.
        """
        if isinstance(data, str):
            data = data.encode("utf-8")

        register = self.xor_in
        for byte in data:
            octet = byte
            if self.reflect_in:
                octet = self._reflect(octet, 8)

            for i in range(8):
                topbit = register & self.msb_mask
                if octet & (0x80 >> i):
                    topbit ^= self.msb_mask
                register <<= 1
                if topbit:
                    register ^= self.poly
            register &= self.mask

        if self.reflect_out:
            register = self._reflect(register, self.width)

        return register ^ self.xor_out


# Pre-configured CRC32 for Steam shortcuts
_steam_crc = CRC32(
    width=32,
    poly=0x04C11DB7,
    reflect_in=True,
    xor_in=0xFFFFFFFF,
    reflect_out=True,
    xor_out=0xFFFFFFFF,
)


def generate_shortcut_id(exe: str, appname: str) -> int:
    """Generate a 64-bit Steam shortcut ID.

    Args:
        exe: The executable path (as stored in the shortcut)
        appname: The app/shortcut name

    Returns:
        A 64-bit integer that can be used with steam://rungameid/
    """
    input_string = exe + appname
    crc32 = _steam_crc.calculate(input_string)
    # Set the MSB of the CRC
    top_32 = crc32 | 0x80000000
    # Combine with the constant lower 32 bits
    full_64 = (top_32 << 32) | 0x02000000
    return full_64


def generate_steam_url(exe: str, appname: str) -> str:
    """Generate a steam:// URL for running a shortcut.

    Args:
        exe: The executable path (as stored in the shortcut)
        appname: The app/shortcut name

    Returns:
        A steam://rungameid/### URL string
    """
    shortcut_id = generate_shortcut_id(exe, appname)
    return f"steam://rungameid/{shortcut_id}"
