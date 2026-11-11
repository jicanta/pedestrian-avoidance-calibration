#include <algorithm>
#include <array>
#include <iomanip>
#include <iostream>
#include <limits>
#include <vector>

#include "commands.hpp"
#include "io.hpp"
#include "setup.hpp"
#include "simulation.hpp"
#include "stopwatch.hpp"

// Item 2 c) OPCIONAL: optimizar los parametros POR PEATON en lugar de un solo
// juego por par, o sea CUATRO numeros por evento -- (p1, p2) del de la
// izquierda y (p1, p2) del de la derecha -- en vez de dos.
//
// No es un barrido de dos parametros hecho dos veces: los dos agentes estan
// acoplados, asi que el error de cada peaton depende tambien de los parametros
// del OTRO (si el de la izquierda se corre mas, el de la derecha necesita
// correrse menos). El minimo hay que buscarlo en la grilla de los cuatro a la
// vez, que es lo que hace este comando: G x G combinaciones por evento, con G
// la grilla de un agente.
//
// Por cada evento y cada metrica escribe DOS optimos sobre LA MISMA grilla,
// que es lo que deja comparar sin trampa cuanto se gana al individualizar:
//
//   * el de cuatro parametros, el minimo de E_m sobre las G x G combinaciones;
//   * el de dos, el minimo sobre la diagonal (los dos agentes con el mismo
//     par), que es el item c) tal cual.
//
// El error de un evento es el promedio sobre sus 2 peatones, como lo define el
// enunciado, y es lo que se minimiza en los dos casos.
int runPairs(const Arguments& arguments) {
  const Experiment experiment = experimentFromArguments(arguments);
  const Model model = modelFromArguments(arguments);
  const std::vector<double> anticipations = linearGrid("p1", arguments.text("p1", "0:4:17"));
  const std::vector<double> margins = linearGrid("p2", arguments.text("p2", "0:0.6:25"));
  const int subdivisions = arguments.integer("subdivisiones", 64);
  const std::string directory = arguments.text("dir", "../data/individual");

  // La grilla de UN agente, aplanada: cada indice es un par (p1, p2).
  struct Pair {
    double anticipation = 0.0;
    double margin = 0.0;
  };
  std::vector<Pair> grid;
  grid.reserve(anticipations.size() * margins.size());
  for (const double anticipation : anticipations) {
    for (const double margin : margins) {
      grid.push_back({anticipation, margin});
    }
  }

  std::ofstream file = openOutput(directory + "/pares.txt");
  file << "# capa " << arguments.text("capa", "predictiva") << "\n"
       << "# SFM sin fuerza social, m " << model.mass << " r " << model.radius << " tau "
       << model.relaxation << " kn " << model.normal << " kt " << model.tangential
       << " dt " << experiment.sampling / subdivisions << " subdivisiones " << subdivisions
       << "\n"
       << "# grilla de UN agente: p1 (s) en " << anticipations.size() << " valores de "
       << anticipations.front() << " a " << anticipations.back() << "; p2 (m) en "
       << margins.size() << " valores de " << margins.front() << " a " << margins.back()
       << " (" << grid.size() << " pares, " << grid.size() * grid.size()
       << " combinaciones por evento)\n"
       << "# item 2 c) opcional: cuatro parametros por evento contra dos, sobre la"
       << " misma grilla\n"
       << "# m metrica p1_izq p2_izq p1_der p2_der Em_cuatro E_izq_cuatro E_der_cuatro"
       << " p1_comun p2_comun Em_dos E_izq_dos E_der_dos\n";

  // Para cada metrica: el mejor de los cuatro parametros y el mejor de la
  // diagonal (dos parametros), con los errores de cada peaton en cada caso.
  struct Best {
    double error = std::numeric_limits<double>::infinity();
    double left = 0.0;
    double right = 0.0;
    std::size_t leftIndex = 0;
    std::size_t rightIndex = 0;
  };

  Stopwatch watch;
  long long runs = 0;
  for (const Event& event : experiment.events) {
    std::array<Best, 2> four;
    std::array<Best, 2> two;
    for (std::size_t a = 0; a < grid.size(); ++a) {
      for (std::size_t b = 0; b < grid.size(); ++b) {
        std::array<Avoidance, 2> layers;
        for (int i = 0; i < 2; ++i) {
          const Pair& pair = i == 0 ? grid[a] : grid[b];
          layers[static_cast<std::size_t>(i)].anticipation = pair.anticipation;
          layers[static_cast<std::size_t>(i)].margin = pair.margin;
          configureLayer(layers[static_cast<std::size_t>(i)], arguments);
        }
        // configureLayer pone el mismo alfa en los dos; el reparto es del par,
        // no de cada peaton, asi que al de la derecha le toca 1 - alfa.
        layers[1].share = 1.0 - layers[0].share;

        const Run run = simulate(event, model, layers, experiment.sampling, subdivisions);
        const Errors left = measure(event.left, run, 0);
        const Errors right = measure(event.right, run, 1);
        ++runs;

        const std::array<double, 2> leftError{left.sameTime, left.closestPoint};
        const std::array<double, 2> rightError{right.sameTime, right.closestPoint};
        for (std::size_t metric = 0; metric < 2; ++metric) {
          const double mean = 0.5 * (leftError[metric] + rightError[metric]);
          if (mean < four[metric].error) {
            four[metric] = {mean, leftError[metric], rightError[metric], a, b};
          }
          if (a == b && mean < two[metric].error) {
            two[metric] = {mean, leftError[metric], rightError[metric], a, b};
          }
        }
      }
    }
    for (std::size_t metric = 0; metric < 2; ++metric) {
      const Pair& fourLeft = grid[four[metric].leftIndex];
      const Pair& fourRight = grid[four[metric].rightIndex];
      const Pair& shared = grid[two[metric].leftIndex];
      file << event.label << " " << (metric + 1) << " " << fourLeft.anticipation << " "
           << fourLeft.margin << " " << fourRight.anticipation << " " << fourRight.margin
           << " " << four[metric].error << " " << four[metric].left << " "
           << four[metric].right << " " << shared.anticipation << " " << shared.margin
           << " " << two[metric].error << " " << two[metric].left << " "
           << two[metric].right << "\n";
    }
    std::cout << "evento " << event.label << "  cuatro parametros: E1 = " << std::fixed
              << std::setprecision(4) << four[0].error << " contra " << two[0].error
              << " con dos\n"
              << std::defaultfloat;
  }
  std::cout << runs << " corridas (" << grid.size() << " x " << grid.size()
            << " combinaciones x " << experiment.events.size() << " eventos) en "
            << std::fixed << std::setprecision(1) << watch.elapsedMilliseconds() / 1000.0
            << " s -> " << directory << "/pares.txt\n";
  return 0;
}
