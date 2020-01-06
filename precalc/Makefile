CXX = g++
ODIR= .obj
DEPDIR = .deps

CXXFLAGS = -O3 -Wall -Wextra -Werror

SRCS = reader.cpp BFSIterator.cpp
OBJS = $(patsubst %,$(ODIR)/%.o,$(SRCS))
PYFLAGS =  $(shell python-config --cflags)

BIN = fast_calc.so

all: $(BIN)

$(ODIR)/%.cpp.o: %.cpp Makefile
	@mkdir -p $(dir $@) $(DEPDIR)
	$(CXX) $(PYFLAGS) $(CXXFLAGS) -c -o $@ $<  -fPIC -MD -MF $(DEPDIR)/$(subst /,_,$<).d -MQ $@

$(BIN): $(OBJS) Makefile
	$(CXX) -lboost_python3 -shared -o  $@ $(OBJS)  

clean:
	rm -rf $(ODIR) $(DEPDIR) $(BIN)

-include $(DEPDIR)/*.d
