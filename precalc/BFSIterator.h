#pragma once 

#include <iterator>
#include <queue>
#include <unordered_set>
#include "reader.h"
#include <utility>
#include <vector>

#define MAX_DEPTH 12

struct vertex{
    VertexID curr_id;
    std::vector<VertexID> prev;
    int depth;
};

class BFSIterator: public std::iterator<std::input_iterator_tag, const vertex> 
{
private:
    vertex start_vertex;
    GraphReader* gr;
    vertex _last; 
    int max_depth;
    std::queue<vertex> q;
    std::vector<bool> used;
public:
    const vertex * operator ++(int);
    static const BFSIterator Empty;
    BFSIterator();
    BFSIterator(GraphReader* gr, VertexID start_vertex, int max_depth);
    vertex operator *();
    BFSIterator &operator ++();
    bool operator ==(BFSIterator const & another);
    bool operator !=(BFSIterator const & another);
};

