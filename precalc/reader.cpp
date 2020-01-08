#include "reader.h"


const int* ptr_range::begin() const
{
    return _begin;
} 
const int* ptr_range:: end() const {
		return _end;
} 



opened_map::opened_map(const std::string& values_file_name)
	{
		_values_fd = open(values_file_name.c_str(), O_RDONLY, 0);
		_values_len = lseek(_values_fd, 0, SEEK_END);
		_values = (int*) mmap(NULL, _values_len, PROT_READ, MAP_SHARED, _values_fd, 0);
	}

size_t opened_map::size()
	{
		return _values_len;
	}

const int& opened_map::operator[](int i) const
	{
		return _values[i];
	}

void opened_map::close_map(){
		munmap(_values, _values_len);
		close(_values_fd);
	}


GraphReader::GraphReader(const std::string& offset_file_name, const std::string& edges_file_name)
	{
		is_unified = false;

		opened_map offset_map(offset_file_name);
		opened_map edges_map(edges_file_name);
		maps.push_back(offset_map);
		maps.push_back(edges_map);
		_vertex_count = (offset_map.size() / 4) - 1;
	}

GraphReader::GraphReader(const std::string& unifued_graph_file_name)
	{
		is_unified = true;

		opened_map unified_map(unifued_graph_file_name);
		maps.push_back(unified_map);
		_offset = unified_map[0]+1;
		_vertex_count = unified_map[0] - 1;
	}

const ptr_range GraphReader::list_edges(VertexID v) const {
		if (is_unified)
		{
			ptr_range result = {&maps[0][maps[0][v+1]/4+_offset], &maps[0][maps[0][v+2]/4+_offset]};
			return result;
		}
		else
		{
			ptr_range result = {&maps[1][ntohl(maps[0][v])/4], &maps[1][ntohl(maps[0][v+1])/4]};
			return result;
		}
	}

int GraphReader::re(int x) {
		if (is_unified)
			return x;
		else
			return ntohl(x);
}

int GraphReader::vertex_count() const{
    return _vertex_count;
};

GraphReader::~GraphReader() {
		for (opened_map map: maps)
			map.close_map();
	}

