CXX      ?= g++
CXXFLAGS ?= -std=c++17 -O3 -march=native -Wall -Wextra -Wpedantic
LDFLAGS  ?=

SRC := $(wildcard src/*.cpp)
OBJ := $(patsubst src/%.cpp,build/%.o,$(SRC))
DEP := $(OBJ:.o=.d)
BIN := sim

.PHONY: all clean debug

all: $(BIN)

$(BIN): $(OBJ)
	$(CXX) $(CXXFLAGS) $^ -o $@ $(LDFLAGS)

build/%.o: src/%.cpp | build
	$(CXX) $(CXXFLAGS) -MMD -MP -c $< -o $@

build:
	@mkdir -p build

debug: CXXFLAGS := -std=c++17 -O0 -g -fsanitize=address,undefined -Wall -Wextra
debug: clean $(BIN)

clean:
	@rm -rf build $(BIN)

-include $(DEP)
