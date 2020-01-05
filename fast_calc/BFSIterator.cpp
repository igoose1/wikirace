#include "BFSIterator.h"

BFSIterator::BFSIterator() {}

BFSIterator::BFSIterator(GraphReader* gr, VertexID start_vertex, int max_depth) :
    gr(gr), start_vertex(start_vertex), max_depth(max_depth) 
{
    q.emplace(start_vertex, 0);     
    used.emplace(start_vertex);
}

VertexID BFSIterator::operator *()
{
    return q.front().first;
}

BFSIterator &BFSIterator::operator ++()
{
    VertexID current_vertex = q.front().first;
    int current_depth = q.front().second;
    q.pop();
    if (current_depth < max_depth)
    {
        for (VertexID next_vertex : gr->list_edges(current_vertex))
        {
            if (used.find(current_vertex) == used.end())
            {
                q.emplace(next_vertex, current_depth + 1);
                used.emplace(next_vertex); 
            }
        }
    }
    return *this;
}

bool BFSIterator::operator ==(BFSIterator const & another)
{
    return q.empty() && another.q.empty();
}

bool BFSIterator::operator!=(BFSIterator const & another)
{
    return !(*this == another); 
}

int main(){
}
