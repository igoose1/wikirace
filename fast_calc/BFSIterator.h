#pragma once 

#include <iterator>
#include <queue>
#include <unordered_set>
#include "reader.h"
#include <utility>

class BFSIterator: public std::iterator<std::input_iterator_tag, const VertexID> 
{
private:
    VertexID start_vertex;
    GraphReader* gr;
    VertexID _last; 
    int max_depth;
    std::queue<std::pair<VertexID, int>> q;
    std::vector<bool> used;
public:
    const VertexID * operator ++(int);
    static const BFSIterator Empty;
    BFSIterator();
    BFSIterator(GraphReader* gr, VertexID start_vertex, int max_depth);
    VertexID operator *();
    BFSIterator &operator ++();
    bool operator ==(BFSIterator const & another);
    bool operator !=(BFSIterator const & another);
};


