import struct
import json

class HCTPParser:
    """
    Class to parse and serialise HCTP binary format with little-endian encoding.
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

        # Read the LIST_ENTRYCOUNT (UINT8 at 0x00)
        entry_count = struct.unpack_from('<B', binary_data, offset)[0]
        offset += 1

        # Iterate over the entries
        for _ in range(entry_count):
            entry = {}

            # Read Unlock ID (UINT8 at 0x00 in ENTRY_BLOCK)
            entry["unlock_id"] = struct.unpack_from('<B', binary_data, offset)[0]
            offset += 1

            # Read Asset ID (UINT16 at 0x01 in ENTRY_BLOCK)
            entry["asset_id"] = struct.unpack_from('<H', binary_data, offset)[0]
            offset += 2

            # Read Asset Name (29-byte character array at 0x03 in ENTRY_BLOCK)
            asset_name_bytes = struct.unpack_from('<29s', binary_data, offset)[0]
            entry["asset_name"] = asset_name_bytes.decode('latin-1').rstrip('\x00')
            offset += 29

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

        :return: Bytes object in the HCTP format
        """
        binary_data = bytearray()

        # Write the LIST_ENTRYCOUNT (UINT8 at 0x00)
        entry_count = len(self.entries)
        binary_data.extend(struct.pack('<B', entry_count))

        # Write each ENTRY_BLOCK
        for entry in self.entries:
            # Write Unlock ID (UINT8 at 0x00 in ENTRY_BLOCK)
            binary_data.extend(struct.pack('<B', entry["unlock_id"]))

            # Write Asset ID (UINT16 at 0x01 in ENTRY_BLOCK)
            binary_data.extend(struct.pack('<H', entry["asset_id"]))

            # Write Asset Name (29-byte character array at 0x08 in ENTRY_BLOCK)
            asset_name_bytes = entry["asset_name"].encode('latin-1')
            asset_name_bytes = asset_name_bytes.ljust(29, b'\x00')[:29]  # Pad/truncate to 29 bytes
            binary_data.extend(asset_name_bytes)

        return bytes(binary_data)