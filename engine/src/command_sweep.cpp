#include <iomanip>
#include <iostream>
#include <vector>

#include "commands.hpp"
#include "io.hpp"
#include "setup.hpp"
#include "simulation.hpp"
#include "stopwatch.hpp"

// Barrido de la grilla de parametros de la capa de elusion: para cada par
// (p1, p2) y cada evento corre la simulacion y mide las DOS metricas en los
// DOS peatones. El archivo que escribe es la entrada de toda la calibracion:
// el promedio poblacional <E>(p1, p2) del item b, los optimos individuales del
// item c y las particiones del item d se calculan despues, en Python, desde
// estas mismas cuatro columnas.
int runSweep(const Arguments& arguments) {
  const Experiment experiment = experimentFromArguments(arguments);
  const Model model = modelFromArguments(arguments);
  const std::vector<double> anticipations = linearGrid("p1", arguments.text("p1", "0:4:41"));
  const std::vector<double> margins = linearGrid("p2", arguments.text("p2", "0:0.8:41"));
  const int subdivisions = arguments.integer("subdivisiones", 64);
  const std::string directory = arguments.text("dir", "../data/barrido");

  std::ofstream file = openOutput(directory + "/errores.txt");
  file << "# SFM sin fuerza social, m " << model.mass << " r " << model.radius << " tau "
       << model.relaxation << " kn " << model.normal << " kt " << model.tangential
       << " dt " << experiment.sampling / subdivisions << " subdivisiones " << subdivisions
       << "\n"
       << "# p1 (s) en " << anticipations.size() << " valores de " << anticipations.front()
       << " a " << anticipations.back() << "; p2 (m) en " << margins.size()
       << " valores de " << margins.front() << " a " << margins.back() << "\n"
       << "# m p1 p2 E1_izquierda E1_derecha E2_izquierda E2_derecha\n";

  Stopwatch watch;
  long long runs = 0;
  for (const double anticipation : anticipations) {
    for (const double margin : margins) {
      Avoidance layer;
      layer.anticipation = anticipation;
      layer.margin = margin;
      layer.ramp = !arguments.flag("sin-rampa");
      layer.leadIsHorizon = arguments.flag("mira-horizonte");
      for (const Event& event : experiment.events) {
        const Run run = simulate(event, model, layer, experiment.sampling, subdivisions);
        const Errors left = measure(event.left, run, 0);
        const Errors right = measure(event.right, run, 1);
        file << event.label << " " << anticipation << " " << margin << " " << left.sameTime
             << " " << right.sameTime << " " << left.closestPoint << " "
             << right.closestPoint << "\n";
        ++runs;
      }
    }
  }
  std::cout << runs << " corridas (" << anticipations.size() << " x " << margins.size()
            << " pares x " << experiment.events.size() << " eventos) en "
            << std::fixed << std::setprecision(1) << watch.elapsedMilliseconds() / 1000.0
            << " s -> " << directory << "/errores.txt\n";
  return 0;
}
