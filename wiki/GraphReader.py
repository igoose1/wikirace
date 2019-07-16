import struct
from wiki.file_holder import file_holder

OFFSET_BLOCK_SIZE = 4
EDGE_BLOCK_SIZE = 4


def read_int_from_file(file, block_size: int) -> int:
    byte = file.read(block_size)
    return struct.unpack('>I', byte)[0]


@file_holder
class GraphReader:
    def __init__(self, offset_file_name: str, edges_file_name: str):
        self.offset_file = None
        self.edges_file = None
        self.offset_file = self._open_file(offset_file_name, 'rb')
        self.edges_file = self._open_file(edges_file_name, 'rb')

    def _get_offset_by_id(self, parent_id: int):
        self.offset_file.seek(OFFSET_BLOCK_SIZE * parent_id)
        offset_begin = read_int_from_file(self.offset_file, OFFSET_BLOCK_SIZE)
        offset_end = read_int_from_file(self.offset_file, OFFSET_BLOCK_SIZE)
        return offset_begin, offset_end

    def edges_count(self, parent_id: int):
        offset_begin, offset_end = self._get_offset_by_id(parent_id)
        return (offset_end - offset_begin) // EDGE_BLOCK_SIZE

    def edges(self, parent_id: int):
        offset_begin = self._get_offset_by_id(parent_id)[0]
        self.edges_file.seek(offset_begin)
        for idx in range(self.edges_count(parent_id)):
            child_id = read_int_from_file(self.edges_file, EDGE_BLOCK_SIZE)
            yield child_id

    def close(self):
        self.offset_file.close()
        self.edges_file.close()