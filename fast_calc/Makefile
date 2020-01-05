CC = g++
ODIR= .obj
DEPDIR = .deps

SRCS = reader.cpp
OBJS = $(patsubst %,$(ODIR)/%.o,$(SRCS))

BIN = fast_calc

all: $(BIN)

$(ODIR)/%.cpp.o: %.cpp Makefile
	@mkdir -p $(dir $@) $(DEPDIR)
	$(CC) -c -o $@ $< $(CFLAGS) -MD -MF $(DEPDIR)/$(subst /,_,$<).d -MQ $@

$(BIN): $(OBJS) Makefile
	$(CC) -o $@ $(OBJS) $(CFLAGS) $(LIBS)

clean:
	rm -rf $(ODIR) $(DEPDIR) $(BIN)

-include $(DEPDIR)/*.d
