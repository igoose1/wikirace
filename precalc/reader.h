#pragma once

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

struct ptr_range
{
    const int*   _begin;                                                   
    const int*   _end;

    const int* begin() const;
    const int* end() const;

};

 struct opened_map
  {
      int* _values;
      int _values_fd;
      size_t _values_len;
      opened_map(const std::string& values_file_name);
      size_t size();
      const int& operator[](int i) const;
      void close_map();
  };

class GraphReader
  {
  private:
      std::vector<opened_map> maps;
      int _vertex_count;
      int _offset = 0;
      bool is_unified;
  public:
      int vertex_count() const;
      GraphReader(const std::string& offset_file_name, const std::string&     edges_file_name);
      GraphReader(const std::string& unifued_graph_file_name);
      const ptr_range list_edges(VertexID v) const;
      int re(int x);
      ~GraphReader();
  };
