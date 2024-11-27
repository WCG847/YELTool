import struct
import json

class SYMParser:
    """
    Class to parse and serialise SYM binary format with little-endian encoding.
    """
    
    def __init__(self, binary_data: bytes = None):
        """
        Initialises the SYMParser with optional binary data.
        
        :param binary_data: Bytes object containing the SYM format data
        """
        self.entries = []  # Holds the parsed entries as dictionaries
        if binary_data:
            self._parse_binary(binary_data)

    def _parse_binary(self, binary_data: bytes):
        """
        Parses the provided binary data into the `entries` attribute.

        :param binary_data: Bytes object containing the SYM format data
        """
        offset = 0

        # Read the LIST_ENTRYCOUNT (UINT32 at 0x00)
        entry_count = struct.unpack_from('<I', binary_data, offset)[0]
        offset += 4

        # Iterate over the entries
        for _ in range(entry_count):
            entry = {}

            # Read Asset ID (UINT32 at 0x00 in ENTRY_BLOCK)
            entry["asset_id"] = struct.unpack_from('<I', binary_data, offset)[0]
            offset += 4

            # Read Unlock ID (UINT32 at 0x04 in ENTRY_BLOCK)
            entry["unlock_id"] = struct.unpack_from('<I', binary_data, offset)[0]
            offset += 4

            # Read Asset Name (0x18-byte character array at 0x08 in ENTRY_BLOCK)
            asset_name_bytes = struct.unpack_from('<24s', binary_data, offset)[0]
            entry["asset_name"] = asset_name_bytes.decode('latin-1').rstrip('\x00')
            offset += 24

            self.entries.append(entry)

    def to_json(self) -> str:
        """
        Serialises the parsed entries into a JSON string.

        :return: JSON string representation of the entries
        """
        return json.dumps({"entries": self.entries}, indent=4)

    def from_json(self, json_data: str):
        """
        Deserialises JSON data and populates the `entries` attribute.

        :param json_data: JSON string containing the data
        """
        data = json.loads(json_data)
        if "entries" not in data or not isinstance(data["entries"], list):
            raise ValueError("Invalid JSON format: Missing 'entries' key or invalid type.")
        self.entries = data["entries"]

    def to_binary(self) -> bytes:
        """
        Serialises the `entries` attribute back into the binary format.

        :return: Bytes object in the SYM format
        """
        binary_data = bytearray()

        # Write the LIST_ENTRYCOUNT (UINT32 at 0x00)
        entry_count = len(self.entries)
        binary_data.extend(struct.pack('<I', entry_count))

        # Write each ENTRY_BLOCK
        for entry in self.entries:
            # Write Asset ID (UINT32 at 0x00 in ENTRY_BLOCK)
            binary_data.extend(struct.pack('<I', entry["asset_id"]))

            # Write Unlock ID (UINT32 at 0x04 in ENTRY_BLOCK)
            binary_data.extend(struct.pack('<I', entry["unlock_id"]))

            # Write Asset Name (18-byte character array at 0x08 in ENTRY_BLOCK)
            asset_name_bytes = entry["asset_name"].encode('latin-1')
            asset_name_bytes = asset_name_bytes.ljust(24, b'\x00')[:24]  # Pad/truncate to 24 bytes
            binary_data.extend(asset_name_bytes)

        return bytes(binary_data)