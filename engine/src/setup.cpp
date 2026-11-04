#include "setup.hpp"

#include <fstream>

#include "io.hpp"

namespace {

// El motor se corre tanto desde engine/ como desde la raiz del repositorio
// (el Makefile de arriba lo llama como engine/build/elusion), asi que los
// archivos de la catedra se buscan en los dos lugares.
std::string locate(const std::string& relative) {
  for (const std::string& prefix : {std::string(), std::string("../")}) {
    std::ifstream probe(prefix + relative);
    if (probe) {
      return prefix + relative;
    }
  }
  return relative;
}

}

Model modelFromArguments(const Arguments& arguments) {
  Model model;
  model.mass = arguments.number("m", model.mass);
  model.radius = arguments.number("r", model.radius);
  model.relaxation = arguments.number("tau", model.relaxation);
  model.normal = arguments.number("kn", model.normal);
  model.tangential = arguments.number("kt", model.tangential);
  model.arrival = arguments.number("llegada", model.arrival);
  return model;
}

Experiment experimentFromArguments(const Arguments& arguments) {
  const std::string trajectories =
      arguments.text("datos", locate("experimental/elusion_1_contra_1.txt"));
  const std::string table = arguments.text("eventos", locate("experimental/eventos.txt"));
  std::vector<int> labels;
  if (arguments.has("pruebas")) {
    labels = integerList("pruebas", arguments.text("pruebas", ""));
  }
  return readExperiment(trajectories, table, labels,
                        arguments.number("arranque", 0.3));
}
