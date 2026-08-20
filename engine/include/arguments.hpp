#pragma once

#include <map>
#include <string>

class Arguments {
 public:
  Arguments(int argc, char** argv);

  const std::string& command() const;
  bool has(const std::string& name) const;

  std::string text(const std::string& name, const std::string& fallback) const;
  double number(const std::string& name, double fallback) const;
  int integer(const std::string& name, int fallback) const;
  int requiredInteger(const std::string& name) const;

 private:
  const std::string& valueOf(const std::string& name) const;

  std::string command_;
  std::map<std::string, std::string> values_;
};
