#include "BFSIterator.h"

const BFSIterator BFSIterator::Empty = BFSIterator();

BFSIterator::BFSIterator() {}

BFSIterator::BFSIterator(GraphReader* gr, VertexID start_vertex, int max_depth) :
    gr(gr), start_vertex(start_vertex), max_depth(max_depth), used(gr->vertex_count(), 0) 
{
    used[start_vertex] = 1;
    q.emplace(start_vertex, 0);     
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
            if (!used[next_vertex])
            {
                q.emplace(next_vertex, current_depth + 1);
                used[next_vertex] = 1; 
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
    GraphReader gr("/home/artolord/Projects/wikirace_app/data/graph/graph");
    BFSIterator iter(&gr, 2160195, 300);
    int c = 0;
    for (BFSIterator i = iter; i!=BFSIterator::Empty; ++i){
        c++;
    }
    std::cout<<c;
}
