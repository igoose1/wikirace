#include "stdio.h"
#include <fcntl.h>
#include "stdlib.h"
#include "string.h"
#include "unistd.h"
#include <iostream>
#include "sys/types.h"
#include "sys/mman.h"
#include <arpa/inet.h>
#include <vector>


typedef int VertexID;


struct prt_range
{
	const int* _begin;
	const int* _end;

	const int* begin() const
	{
		return _begin;
	} 
	const int* end() const {
		return _end;
	} 
};


struct opened_map
{
	int* _values;
	int _values_fd;
	size_t _values_len;

	opened_map(const std::string& values_file_name)
	{
		_values_fd = open(values_file_name.c_str(), O_RDONLY, 0);
		_values_len = lseek(_values_fd, 0, SEEK_END);
		_values = (int*) mmap(NULL, _values_len, PROT_READ, MAP_SHARED, _values_fd, 0);
	}

	size_t size()
	{
		return _values_len;
	}

	const int& operator[](int i) const
	{
		return _values[i];
	}

	void close_map(){
		munmap(_values, _values_len);
		close(_values_fd);
	}
};

class GraphReader
{
private:
	std::vector<opened_map> maps;
	int _vertex_count;
	int _offset = 0;
	bool is_unified;
public:
	int vertex_count() const
	{
		return _vertex_count; 
	}

	GraphReader(const std::string& offset_file_name, const std::string& edges_file_name)
	{
		is_unified = false;

		opened_map offset_map(offset_file_name);
		opened_map edges_map(edges_file_name);
		maps.push_back(offset_map);
		maps.push_back(edges_map);
		_vertex_count = (offset_map.size() / 4) - 1;
	}

	GraphReader(const std::string& unifued_graph_file_name)
	{
		is_unified = true;

		opened_map unified_map(unifued_graph_file_name);
		maps.push_back(unified_map);
		_offset = unified_map[0]+1;
		_vertex_count = unified_map[0] - 1;
	}

	const prt_range list_edges(VertexID v) const {
		if (is_unified)
		{
			prt_range result = {&maps[0][maps[0][v+1]/4+_offset], &maps[0][maps[0][v+2]/4+_offset]};
			return result;
		}
		else
		{
			prt_range result = {&maps[1][ntohl(maps[0][v])/4], &maps[1][ntohl(maps[0][v+1])/4]};
			return result;
		}
	}

	int re(int x) {
		if (is_unified)
			return x;
		else
			return ntohl(x);
	}


	~GraphReader() {
		for (opened_map map: maps)
			map.close_map();
	}
};

int main()
{

}