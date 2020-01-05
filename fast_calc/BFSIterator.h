#pragma once 

#include <queue>
#include <set>

typedef vertex_id;
  
class BFSIterator 
{
private:
    vertex_id start_vertex;
    graph* gr; 
    int max_depth;
    queue<pair<vertex_id, int>> q;
    ordered_set<vertex_id> used;
public:
    BFSIterator();
    BFSIterator(graph* gr, vertex_id start_vertex, int max_depth);
    vertex_id operator *();
    BFSIterator operator ++();
    bool operator ==(BFSIterator const & another);
    bool operator !=(BFSIterator const & another);
};

#endif
