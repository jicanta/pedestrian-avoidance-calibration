#include "setup.hpp"

#include <fstream>

#include "io.hpp"

namespace {

// Tramo del corredor por omision (m). Ver README, "El recorte de la ventana".
constexpr double kXMin = 1.0;
constexpr double kXMax = 7.7;

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
  // --xmin y --xmax: el tramo del corredor al que se recorta la ventana de
  // cada evento (experiment.cpp). Las cabeceras de las dos filas estan en
  // x = 0,6 m y x = 8,1 m.
  return readExperiment(trajectories, table, labels, arguments.number("xmin", kXMin),
                        arguments.number("xmax", kXMax));
}

void configureLayer(Avoidance& layer, const Arguments& arguments) {
  layer.kind = kindFromName(arguments.text("capa", "predictiva"));
  layer.ramp = !arguments.flag("sin-rampa");
  layer.leadIsHorizon = arguments.flag("mira-horizonte");
  layer.share = arguments.number("alfa", 0.5);
}
