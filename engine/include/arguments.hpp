#pragma once

#include <map>
#include <string>
#include <vector>

class Arguments {
 public:
  Arguments(int argc, char** argv);

  const std::string& command() const;
  bool has(const std::string& name) const;

  std::string text(const std::string& name, const std::string& fallback) const;
  double number(const std::string& name, double fallback) const;
  int integer(const std::string& name, int fallback) const;
  bool flag(const std::string& name) const;

 private:
  const std::string& valueOf(const std::string& name) const;

  std::string command_;
  std::map<std::string, std::string> values_;
};

// "1,2,3" -> {1, 2, 3}. Las listas de la linea de comandos (--dts, --ns, --xos)
// se escriben separadas por coma.
std::vector<double> numberList(const std::string& name, const std::string& text);
std::vector<int> integerList(const std::string& name, const std::string& text);
std::vector<std::string> textList(const std::string& text);
