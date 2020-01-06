#pragma once 

#include <queue>
#include <unordered_set>
#include "reader.h"
#include <utility>

class BFSIterator 
{
private:
    VertexID start_vertex;
    GraphReader* gr; 
    int max_depth;
    std::queue<std::pair<VertexID, int>> q;
    std::vector<bool> used;
public:
    static const BFSIterator Empty;
    BFSIterator();
    BFSIterator(GraphReader* gr, VertexID start_vertex, int max_depth);
    VertexID operator *();
    BFSIterator &operator ++();
    bool operator ==(BFSIterator const & another);
    bool operator !=(BFSIterator const & another);
};


