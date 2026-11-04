#include <iomanip>
#include <iostream>

#include "commands.hpp"
#include "io.hpp"
#include "setup.hpp"
#include "simulation.hpp"

// Una corrida de un evento con un par (p1, p2) dado. Escribe la salida
// primaria con la que se hacen las animaciones y la figura del observable
// primario: el estado de los dos agentes en cada instante experimental y, al
// lado, las trayectorias medidas sobre la misma grilla temporal.
int runSingle(const Arguments& arguments) {
  const Experiment experiment = experimentFromArguments(arguments);
  const Model model = modelFromArguments(arguments);
  Avoidance layer;
  layer.anticipation = arguments.number("p1", 0.0);
  configureLayer(layer, arguments);
  layer.margin = arguments.number("p2", 0.0);
  const int subdivisions = arguments.integer("subdivisiones", 64);
  const std::string directory = arguments.text("dir", "../data/runs/prueba");

  std::cout << std::fixed << std::setprecision(4);
  for (const Event& event : experiment.events) {
    const Run run = simulate(event, model, layer, experiment.sampling, subdivisions);
    const std::string folder =
        experiment.events.size() == 1 ? directory
                                      : directory + "/m" + std::to_string(event.label);
    writeStatic(folder + "/static.txt", event, model, layer, run, experiment.sampling);
    writeDynamic(folder + "/dynamic.txt", run);
    writeExperimental(folder + "/experimental.txt", event, run, experiment.sampling);

    const Errors left = measure(event.left, run, 0);
    const Errors right = measure(event.right, run, 1);
    std::cout << "evento " << event.label << "  E1 = "
              << 0.5 * (left.sameTime + right.sameTime) << " m2   E2 = "
              << 0.5 * (left.closestPoint + right.closestPoint) << " m2   "
              << run.conflictInstants << "/" << event.instants
              << " instantes en conflicto   -> " << folder << "\n";
  }
  return 0;
}
