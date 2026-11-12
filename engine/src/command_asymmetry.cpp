#include <iomanip>
#include <iostream>
#include <vector>

#include "commands.hpp"
#include "io.hpp"
#include "setup.hpp"
#include "simulation.hpp"
#include "stopwatch.hpp"

// Barrido del reparto de la elusion. La capa simetrica hace que los DOS
// peatones del par se corran lo mismo, y en los datos de la catedra eso no es
// lo que pasa: en cada par uno de los dos cede mas. Es un EXTRA que propuso la
// catedra, fuera de lo que pide el enunciado: t_a queda fijo en --p1 y el
// barrido recorre el par (d_s, alfa):
//
//   alfa = fraccion de la separacion que falta que se lleva el peaton de la
//          IZQUIERDA; el de la derecha se lleva 1 - alfa. alfa = 0,5 es la capa
//          simetrica de siempre, asi que ese corte del barrido reproduce
//          exactamente la columna correspondiente del barrido de dos
//          parametros y sirve de control.
//
// El archivo tiene la misma forma que el del comando sweep (una linea por
// evento y por punto de la grilla, con las DOS metricas de los DOS peatones):
// el promedio poblacional, el optimo de cada evento y la distribucion de alfa
// se calculan despues, en Python.
int runAsymmetry(const Arguments& arguments) {
  const Experiment experiment = experimentFromArguments(arguments);
  const Model model = modelFromArguments(arguments);
  const double anticipation = arguments.number("p1", 2.15);
  const std::vector<double> margins = linearGrid("p2", arguments.text("p2", "0:0.6:61"));
  const std::vector<double> shares = linearGrid("alfas", arguments.text("alfas", "0:1:41"));
  const int subdivisions = arguments.integer("subdivisiones", 64);
  const std::string directory = arguments.text("dir", "../data/asimetria");

  std::ofstream file = openOutput(directory + "/errores.txt");
  file << "# capa " << arguments.text("capa", "predictiva") << " con reparto asimetrico\n"
       << "# SFM sin fuerza social, m " << model.mass << " r " << model.radius << " tau "
       << model.relaxation << " kn " << model.normal << " kt " << model.tangential
       << " dt " << experiment.sampling / subdivisions << " subdivisiones " << subdivisions
       << "\n"
       << "# t_a fijo en " << anticipation << " s\n"
       << "# p2 = d_s (m) en " << margins.size() << " valores de " << margins.front()
       << " a " << margins.back() << "; alfa en " << shares.size() << " valores de "
       << shares.front() << " a " << shares.back() << "\n"
       << "# m p2 alfa E1_izquierda E1_derecha E2_izquierda E2_derecha\n";

  Stopwatch watch;
  long long runs = 0;
  for (const double margin : margins) {
    for (const double share : shares) {
      Avoidance layer;
      configureLayer(layer, arguments);
      layer.anticipation = anticipation;
      layer.margin = margin;
      layer.share = share;
      for (const Event& event : experiment.events) {
        const Run run = simulate(event, model, layer, experiment.sampling, subdivisions);
        const Errors left = measure(event.left, run, 0);
        const Errors right = measure(event.right, run, 1);
        file << event.label << " " << margin << " " << share << " " << left.sameTime << " "
             << right.sameTime << " " << left.closestPoint << " " << right.closestPoint
             << "\n";
        ++runs;
      }
    }
  }
  std::cout << runs << " corridas (" << margins.size() << " x " << shares.size()
            << " pares (d_s, alfa) x " << experiment.events.size() << " eventos, t_a = "
            << std::fixed << std::setprecision(2) << anticipation << " s) en "
            << std::setprecision(1) << watch.elapsedMilliseconds() / 1000.0 << " s -> "
            << directory << "/errores.txt\n";
  return 0;
}
