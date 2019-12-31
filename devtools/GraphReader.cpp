#include <stdio.h>
#include <string>
#include <vector>
#include <queue>
#include <iostream>
#include <algorithm>

using namespace std;

const int OFFSET_BLOCK_SIZE = 4;
const int EDGE_BLOCK_SIZE = 4;

#define pi pair<int, int>
typedef pair<int, int> OFFSET;


int read_int_from_file(FILE* file, int block_size) {
    unsigned char buffer[block_size];
    fread(&buffer,1,block_size, file);
    int result = (int)buffer[3] | (int)buffer[2]<<8 | (int)buffer[1]<<16 | (int)buffer[0]<<24;
    return result;
}

class GraphReader {
private:
    FILE* offset_file;
    FILE* edges_file;
    OFFSET _get_offset_by_id(int parent_id) {
        fseek(offset_file, OFFSET_BLOCK_SIZE * parent_id, SEEK_SET);
        int offset_begin = read_int_from_file(offset_file, OFFSET_BLOCK_SIZE);
        int offset_end = read_int_from_file(offset_file, OFFSET_BLOCK_SIZE);
        return {offset_begin, offset_end};
    }

public:
    GraphReader(string offset_file_name, string edges_file_name)
    {
        offset_file = nullptr;
        edges_file = nullptr;
        offset_file = fopen(offset_file_name.c_str(), "rb");
        edges_file = fopen(edges_file_name.c_str(), "rb");
    }

    int edges_count(int parent_id)
    {
        OFFSET offset = _get_offset_by_id(parent_id);
        return (offset.second - offset.first) / EDGE_BLOCK_SIZE;
    }

    void edges(int parent_id, vector<int> &result)
    {
        result.clear();
        int count = edges_count(parent_id);
        result.reserve(count);
        OFFSET offset = _get_offset_by_id(parent_id);
        fseek(edges_file, offset.first, SEEK_SET);
        for (int idx = 0; idx < count; idx++)
        {
            int child_id = read_int_from_file(edges_file, EDGE_BLOCK_SIZE);
            result.push_back(child_id);
        }
    }

    void close() {
        fclose(offset_file);
        fclose(edges_file);
    }   

};


class NiceSeeker {
private:
    GraphReader *graph;
    int nice_min;
    int nice_max;
public:
    NiceSeeker(GraphReader *graph)
    {
        this->graph = graph;
    }

    void Setup(int nice_min, int nice_max)
    {
        this->nice_min = nice_min;
        this->nice_max = nice_max;
    }

    void Find(int start, vector<pi> &nice_v) {
        nice_v.clear();
        vector<int> dist (6000000, INT32_MAX);
        queue<int> q;
        q.push(start);
        dist[start] = 0;
        vector<int> edges;
        while (!q.empty()) {
            int v = q.front();
            q.pop();

            if (dist[v] >= nice_min && dist[v] <= nice_max)
                nice_v.push_back({v, dist[v]});
            
            if (dist[v] > nice_max)
                return;
            graph->edges(v,edges);
            for (int e: edges) {
                if (dist[e] > dist[v] + 1)
                {
                    dist[e] = dist[v] + 1;
                    q.push(e);
                }
            }
        }
    }
};


class MinPathSeeker {
private:
    GraphReader *graph;
public:
    MinPathSeeker(GraphReader *graph)
    {
        this->graph = graph;
    }

    void Find(int start, int end, vector<int> &path) {
        path.clear();
        vector<int> dist (6000000, INT32_MAX);
        vector<int> prev (6000000, -1);
        queue<int> q;
        q.push(start);
        dist[start] = 0;
        vector<int> edges;
        while (!q.empty()) {
            int v = q.front();
            q.pop();

            if (v == end)
                break;

            graph->edges(v,edges);
            for (int e: edges)
                if (dist[e] > dist[v] + 1)
                {
                    dist[e] = dist[v] + 1;
                    prev[e] = v;
                    q.push(e);
                }
        }
        int prev_v = prev[end];

        while (prev_v != -1)
        {
            path.push_back(prev_v);
            prev_v = prev[prev_v];
        }

        reverse(path.begin(), path.end());
        path.push_back(end);
    }
};


//#define DEBUG

void FIND(vector<string> &argv){
    string arg1,arg2;
    int min, max, start;
    #ifdef DEBUG
        arg1 = "graph/offset_all";
        arg2 = "graph/edges_all";
        min = 7;
        max = 7;
        start = 2762551;
    #else
        arg1 = argv[2];
        arg2 = argv[3];
        min = stoi(argv[4]);
        max = stoi(argv[5]);
        start = stoi(argv[6]);
    #endif

    GraphReader graph(arg1, arg2);
    NiceSeeker seeker(&graph);
    seeker.Setup(min, max);
    vector<pi> result;
    seeker.Find(start, result);
    ios_base::sync_with_stdio(0);
    for (int i = 0; i < result.size(); i++)
        cout << result[i].first<<'|'<<result[i].second << ' ';
}

void EDGES(vector<string> &argv) {
    string arg1,arg2;
    int start;
    arg1 = argv[2];
    arg2 = argv[3];
    start = stoi(argv[4]);
    GraphReader graph(arg1, arg2);
    vector<int> result;
    graph.edges(start, result);
    for (int i = 0; i < result.size(); i++)
        cout << result[i] << ' ';
}


void MINPATH(vector<string> &argv) {
    string arg1,arg2;
    int start, end;
    arg1 = argv[2];
    arg2 = argv[3];
    start = stoi(argv[4]);
    end = stoi(argv[5]);
    GraphReader graph(arg1, arg2);
    MinPathSeeker seeker(&graph);
    vector<int> result;
    seeker.Find(start, end, result);
    for (int i = 0; i < result.size(); i++)
        cout << result[i] << ' ';
}


int main(int argc, char *argv[]) {
    vector<string> args;
    for (int i = 0; i < argc; i++)
        args.push_back(argv[i]);
    if (args[1] == "/FIND")
        FIND(args);
    else if (args[1] == "/EDGES")
        EDGES(args);
    else if (args[1] == "/MINPATH")
        MINPATH(args);
}