#include <iomanip>
#include <iostream>
#include <vector>

#include "commands.hpp"
#include "io.hpp"
#include "setup.hpp"
#include "simulation.hpp"
#include "stopwatch.hpp"

// Eleccion del paso de integracion. dt no es libre: tiene que dividir dtExp en
// un numero entero de partes para que cada instante experimental sea
// exactamente un paso de la simulacion. El comando corre los eventos con
// varios numeros de subdivisiones y escribe, por cada uno, las dos metricas y
// el tiempo de ejecucion; el paso elegido es el mas largo cuyo resultado ya no
// se mueve respecto del mas fino.
int runConvergence(const Arguments& arguments) {
  const Experiment experiment = experimentFromArguments(arguments);
  const Model model = modelFromArguments(arguments);
  Avoidance layer;
  layer.anticipation = arguments.number("p1", 2.0);
  layer.ramp = !arguments.flag("sin-rampa");
  layer.leadIsHorizon = arguments.flag("mira-horizonte");
  layer.margin = arguments.number("p2", 0.4);
  const std::vector<int> subdivisions =
      integerList("subdivisiones", arguments.text("subdivisiones", "1,2,4,8,16,32,64,128,256,512"));
  const std::string directory = arguments.text("dir", "../data/convergencia");

  std::ofstream file = openOutput(directory + "/convergencia.txt");
  file << "# p1 " << layer.anticipation << " p2 " << layer.margin << " dt_exp "
       << experiment.sampling << " eventos " << experiment.events.size() << "\n"
       << "# subdivisiones dt E1_media E2_media ms\n";
  std::cout << std::scientific << std::setprecision(4);
  for (const int count : subdivisions) {
    Stopwatch watch;
    double sameTime = 0.0;
    double closest = 0.0;
    for (const Event& event : experiment.events) {
      const Run run = simulate(event, model, layer, experiment.sampling, count);
      const Errors left = measure(event.left, run, 0);
      const Errors right = measure(event.right, run, 1);
      sameTime += 0.5 * (left.sameTime + right.sameTime);
      closest += 0.5 * (left.closestPoint + right.closestPoint);
    }
    const double events = static_cast<double>(experiment.events.size());
    const double elapsed = watch.elapsedMilliseconds();
    file << count << " " << experiment.sampling / count << " " << sameTime / events << " "
         << closest / events << " " << elapsed << "\n";
    std::cout << "subdivisiones " << std::setw(4) << count << "  dt "
              << experiment.sampling / count << " s   <E1> " << sameTime / events
              << " m2   <E2> " << closest / events << " m2   " << std::fixed
              << std::setprecision(0) << elapsed << " ms\n"
              << std::scientific << std::setprecision(4);
  }
  return 0;
}
