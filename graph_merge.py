from byte_convert import *


def merge(file_count: int, offset_block: int = 4):
    """
        Merge edges and offset files
        :param file_count: count of files to merge
        :param offset_block: size of offset bytes block
    """
    # open files in write mod
    output_graph = open('edges_all', 'wb')
    output_offset = open('offset_all', 'wb')
    # sum of offsets from previous files
    offset = 0

    for i in range(file_count):
        input_graph = 'edges' + str(i)
        # open current graph file
        input_graph = open(input_graph, 'rb')
        # copy all data
        output_graph.write(input_graph.read())
        # close current graph file
        input_graph.close()

        input_offset = 'offset' + str(i)
        # open current offset file
        input_offset = open(input_offset, 'rb')
        # read all data from offset file
        offset_bytes = input_offset.read()
        # length of data (without end offset)
        bytes_count = len(offset_bytes) - offset_block

        # iterate every offset block
        for byte_index in range(0, bytes_count, offset_block):
            # get current offset
            byte = bytes([offset_bytes[byte_index + j] for j in range(offset_block)])
            byte = bytes_to_int(byte)
            # add offset from previous files
            byte += offset
            byte = int_to_bytes(byte, offset_block)
            # write current offset to file
            output_offset.write(byte)

        # close current offset file
        input_offset.close()
        # get end offset byte
        end_byte = bytes([offset_bytes[bytes_count + j] for j in range(offset_block)])
        # add end offset
        offset += bytes_to_int(end_byte)
        print(offset)

    # write end offset
    output_offset.write(int_to_bytes(offset))

    # close output files
    output_graph.close()
    output_offset.close()
