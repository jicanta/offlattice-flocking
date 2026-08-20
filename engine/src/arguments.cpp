#include "arguments.hpp"

#include <cstddef>
#include <stdexcept>
#include <vector>

namespace {

bool isOptionName(const std::string& token) {
  return token.size() > 2 && token.compare(0, 2, "--") == 0;
}

[[noreturn]] void rejectValue(const std::string& name, const std::string& value,
                              const std::string& expected) {
  throw std::invalid_argument("--" + name + " espera " + expected +
                              " y recibio \"" + value + "\"");
}

int toInteger(const std::string& name, const std::string& value) {
  std::size_t consumed = 0;
  int parsed = 0;
  try {
    parsed = std::stoi(value, &consumed);
  } catch (const std::exception&) {
    rejectValue(name, value, "un entero");
  }
  if (consumed != value.size()) {
    rejectValue(name, value, "un entero");
  }
  return parsed;
}

double toNumber(const std::string& name, const std::string& value) {
  std::size_t consumed = 0;
  double parsed = 0.0;
  try {
    parsed = std::stod(value, &consumed);
  } catch (const std::exception&) {
    rejectValue(name, value, "un numero");
  }
  if (consumed != value.size()) {
    rejectValue(name, value, "un numero");
  }
  return parsed;
}

}  // namespace

Arguments::Arguments(int argc, char** argv) {
  std::vector<std::string> tokens(argv + (argc > 0 ? 1 : 0), argv + argc);
  std::size_t index = 0;

  if (index < tokens.size() && !isOptionName(tokens[index])) {
    command_ = tokens[index];
    ++index;
  }

  while (index < tokens.size()) {
    if (!isOptionName(tokens[index])) {
      throw std::invalid_argument("argumento inesperado: " + tokens[index]);
    }
    const std::string name = tokens[index].substr(2);
    ++index;
    if (index < tokens.size() && !isOptionName(tokens[index])) {
      values_[name] = tokens[index];
      ++index;
    } else {
      values_[name] = "true";
    }
  }
}

const std::string& Arguments::command() const { return command_; }

bool Arguments::has(const std::string& name) const {
  return values_.find(name) != values_.end();
}

const std::string& Arguments::valueOf(const std::string& name) const {
  const auto found = values_.find(name);
  if (found == values_.end()) {
    throw std::invalid_argument("falta el argumento --" + name);
  }
  return found->second;
}

std::string Arguments::text(const std::string& name,
                            const std::string& fallback) const {
  return has(name) ? valueOf(name) : fallback;
}

double Arguments::number(const std::string& name, double fallback) const {
  return has(name) ? toNumber(name, valueOf(name)) : fallback;
}

int Arguments::integer(const std::string& name, int fallback) const {
  return has(name) ? toInteger(name, valueOf(name)) : fallback;
}

int Arguments::requiredInteger(const std::string& name) const {
  return toInteger(name, valueOf(name));
}
