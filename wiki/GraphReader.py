from byte_convert import bytes_to_int

offset_block_size = 4
edge_block_size = 4


def read_block_from_file(file, block_size: int) -> int:
    return bytes_to_int(file.read(block_size))


class GraphReader:
    def __init__(self, offset_file_name: str, edges_file_name: str):
        self.offset_file = open(offset_file_name, 'rb')
        self.edges_file = open(edges_file_name, 'rb')

    def _get_offset_by_id(self, parent_id: int):
        self.offset_file.seek(offset_block_size * parent_id)
        offset_begin = read_block_from_file(self.offset_file, offset_block_size)
        offset_end = read_block_from_file(self.offset_file, offset_block_size)
        return offset_begin, offset_end

    def edges_count(self, parent_id: int):
        offset_begin, offset_end = self._get_offset_by_id(parent_id)
        return (offset_end - offset_begin) // edge_block_size

    def edges(self, parent_id: int):
        offset_begin = self._get_offset_by_id(parent_id)[0]
        self.edges_file.seek(offset_begin)
        for idx in range(self.edges_count(parent_id)):
            child_id = read_block_from_file(self.edges_file, edge_block_size)
            yield child_id

    def close(self):
        self.offset_file.close()
        self.edges_file.close()
