class GraphReader:
    def __init__(self, offset_file:str, edges_file:str):
        self.offset = open(offset_file, 'rb')
        self.edges = open(edges_file, 'rb')
        self.offset_block = 4
        self.edge_b_count = 4
    def _bytes_to_int(self,byte_array:bytes):
        ret = 0
        ret |= byte_array[0] << 24
        ret |= byte_array[1] << 16
        ret |= byte_array[2] << 8
        ret |= byte_array[3] << 0
        return ret
    def edges_count(self, parent_id:int):
        self.offset.seek(self.offset_block*parent_id)
        offset_begin = self.offset.read(4)
        offset_begin = self._bytes_to_int(offset_begin)
        offset_end = self.offset.read(4)
        offset_end = self._bytes_to_int(offset_end)
        edges_count = (offset_end - offset_begin) // self.edge_b_count
        return edges_count
    def Edges(self, parent_id:int):
        self.offset.seek(self.offset_block*parent_id)
        offset_begin = self.offset.read(4)
        offset_begin = self._bytes_to_int(offset_begin)
        offset_end = self.offset.read(4)
        offset_end = self._bytes_to_int(offset_end)
        self.edges.seek(offset_begin)
        edges_count = (offset_end - offset_begin) // self.edge_b_count
        for edge_id in range(edges_count):
            child_id = self.edges.read(4)
            child_id = self._bytes_to_int(child_id)
            yield child_id
    def __exit__(self, *_):
        self.offset.close()
        self.edges.close()
