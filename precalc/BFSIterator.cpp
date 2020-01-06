#include "BFSIterator.h"

#include <boost/core/noncopyable.hpp>
#include <boost/python.hpp>

const BFSIterator BFSIterator::Empty = BFSIterator();

BFSIterator::BFSIterator() {}

BFSIterator::BFSIterator(GraphReader* g, VertexID start, int max_depth) :
    start_vertex({start, std::vector<VertexID>(MAX_DEPTH,-1), 0}), gr(g), max_depth(max_depth), used(g->vertex_count(), 0) 
{
    used[start] = 1;
    start_vertex.prev[0] = start;
    q.emplace(start_vertex);     
}

vertex BFSIterator::operator *()
{
    return q.front();
}

BFSIterator &BFSIterator::operator ++()
{
    VertexID current_vertex = q.front().curr_id;
    int current_depth = q.front().depth;
    if (current_depth < max_depth && current_depth < MAX_DEPTH)
    {
        for (VertexID next_vertex : gr->list_edges(current_vertex))
        {
            if (!used[next_vertex])
            {
                std::vector<VertexID> n = q.front().prev;
                n[current_depth + 1] = next_vertex;
                q.push({next_vertex, n, current_depth + 1});
                used[next_vertex] = 1; 
            }
        }

    }
    q.pop();
    return *this;
}
const vertex *BFSIterator::operator++(int){
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


template <class T>
boost::python::list toList(std::vector<T> vector) {
	typename std::vector<T>::iterator iter;
	boost::python::list list;
	for (iter = vector.begin(); iter != vector.end(); ++iter) {
		list.append(*iter);
	}
	return list;
}


range<BFSIterator> bfs(VertexID start, int depth, GraphReader &gr){
    BFSIterator iter(&gr, start, depth);
    return range<BFSIterator>(iter, BFSIterator::Empty);
};

boost::python::list get_path(vertex &v){
    std::vector<VertexID> ret;
    for (int i = 0; i <= v.depth; ++i){
        ret.push_back(v.prev[i]);
    }
    return toList<VertexID>(ret);
}



BOOST_PYTHON_MODULE(fast_calc){
using namespace boost::python;
    class_<boost::iterator_range<const vertex*>>("vertex_range", no_init)
    .def("__len__", &::range<BFSIterator>::size)
    .def("__iter__", iterator<::range<BFSIterator>>())
    ;

    class_<GraphReader, boost::noncopyable>("GraphReader", init<std::string>())
       .def("edges", &GraphReader::list_edges)
       .def("vertex_count", &GraphReader::vertex_count)
    ;

    class_<vertex>("bfs_vertex")
        .def_readonly("curr", &vertex::curr_id)
        .def_readonly("depth", &vertex::depth);

    def ("get_path", &get_path);

    class_<::range<BFSIterator>>("_bfs_range", no_init)
        .def("__iter__", iterator<::range<BFSIterator>>());
    def ("bfs", &bfs);
}

int main(){
    GraphReader g("/home/artolord/Projects/wikirace_app/data/graph/graph");
    int c = 0;
    for(vertex i: bfs(2160195, 2, g)){
        i = i; // unused
        c++;
    }
    std::cout<<c;
    return 0;
}
