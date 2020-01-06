#include "BFSIterator.h"

#include <boost/core/noncopyable.hpp>
#include <boost/python.hpp>
#include <iterator>

const BFSIterator BFSIterator::Empty = BFSIterator();

BFSIterator::BFSIterator() {}

BFSIterator::BFSIterator(GraphReader* g, VertexID start_vertex, int max_depth) :
    start_vertex(start_vertex), gr(g), max_depth(max_depth), used(g->vertex_count(), 0) 
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
const VertexID *BFSIterator::operator++(int){
    _last = **this;
    ++*this;
    return &_last;
}
bool BFSIterator::operator ==(BFSIterator const & another)
{
    return q.empty() && another.q.empty();
}

bool BFSIterator::operator!=(BFSIterator const & another)
{
    return !(*this == another); 
}

template <class Iterator>
class range{
    private:
        const Iterator _begin;
        const Iterator _end;
    public:
        typedef Iterator iterator;
        typedef Iterator const_iterator;
        size_t size() const{return std::distance(_begin, _end);}
        bool empty() const {return _begin == _end;}
        range(Iterator begin, Iterator end):
            _begin(begin), _end(end){}
        const Iterator begin() const{
            return _begin;
        };
        const Iterator end() const{
            return _end;
        };
}; 


range<BFSIterator> bfs(VertexID start, int depth, GraphReader &gr){
    BFSIterator iter(&gr, start, depth);
    return range<BFSIterator>(iter, BFSIterator::Empty);
};

BOOST_PYTHON_MODULE(fast_calc){
using namespace boost::python;
    class_<boost::iterator_range<const VertexID*>>("vertex_range", no_init)
    .def("__len__", &::range<BFSIterator>::size)
    .def("__iter__", iterator<::range<BFSIterator>>())
    ;

    class_<GraphReader, boost::noncopyable>("GraphReader", init<std::string>())
       .def("edges", &GraphReader::list_edges)
       .def("vertex_count", &GraphReader::vertex_count)
    ;

    class_<::range<BFSIterator>>("_bfs_range", no_init)
        .def("__iter__", iterator<::range<BFSIterator>>());
    def ("bfs", &bfs);
}

int main(){
    GraphReader g("/home/artolord/Projects/wikirace_app/data/graph/graph");
    int c = 0;
    for(VertexID i: bfs(2160195, 2, g)){
        i = i; // unused
        c++;
    }
    std::cout<<c;
    return 0;
}
