#include <algorithm>
#include <array>
#include <atomic>
#include <fstream>
#include <set>
#include <sstream>
#include <thread>
#include <utility>
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
//
// Las G x G corridas de un evento son independientes entre si, asi que se
// reparten entre --hilos hilos (por omision, todos los del equipo). El
// resultado NO depende de la cantidad de hilos: ante un empate exacto gana la
// combinacion de menor indice, que es la que encontraria el recorrido en serie.
//
// Con la grilla fina la corrida dura horas: cada evento se escribe y se vuelca
// a disco apenas termina, y con --reanudar se saltean los eventos que ya estan
// en pares.txt (de una corrida anterior con la MISMA grilla).
int runPairs(const Arguments& arguments) {
  const Experiment experiment = experimentFromArguments(arguments);
  const Model model = modelFromArguments(arguments);
  const std::vector<double> anticipations = linearGrid("p1", arguments.text("p1", "0:4:17"));
  const std::vector<double> margins = linearGrid("p2", arguments.text("p2", "0:0.6:25"));
  const int subdivisions = arguments.integer("subdivisiones", 64);
  const std::string directory = arguments.text("dir", "../data/individual");
  const unsigned available = std::max(1u, std::thread::hardware_concurrency());
  const int threads = std::max(1, arguments.integer("hilos", static_cast<int>(available)));
  const bool resume = arguments.flag("reanudar");

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

  // Los eventos ya resueltos de una corrida anterior (--reanudar): los que
  // tienen sus dos filas, una por metrica, en pares.txt.
  const std::string path = directory + "/pares.txt";
  std::set<int> done;
  std::vector<std::pair<int, std::string>> kept;  // (evento o -1 si es cabecera, linea)
  if (resume) {
    std::ifstream previous(path);
    std::string line;
    std::vector<int> seen;
    while (std::getline(previous, line)) {
      int label = -1;
      if (!line.empty() && line[0] != '#') {
        std::istringstream fields(line);
        if (fields >> label) seen.push_back(label);
      }
      kept.push_back({label, line});
    }
    for (const int label : seen) {
      if (std::count(seen.begin(), seen.end(), label) == 2) done.insert(label);
    }
  }
  std::ofstream file;
  if (done.empty()) {
    file = openOutput(path);
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
  } else {
    // Se reescribe lo que ya estaba, sin la fila suelta que pudo dejar un
    // evento cortado a la mitad.
    file = openOutput(path);
    for (const auto& [label, line] : kept) {
      if (label < 0 || done.count(label) > 0) file << line << "\n";
    }
    std::cout << "reanudando: " << done.size() << " eventos ya estaban en " << path << "\n";
  }
  file.flush();

  // Para cada metrica: el mejor de los cuatro parametros y el mejor de la
  // diagonal (dos parametros), con los errores de cada peaton en cada caso.
  struct Best {
    double error = std::numeric_limits<double>::infinity();
    double left = 0.0;
    double right = 0.0;
    std::size_t leftIndex = 0;
    std::size_t rightIndex = 0;
  };

  // Orden total entre candidatos: menor error y, ante un empate exacto, menor
  // (a, b). Es el orden del recorrido en serie, asi que el optimo no depende
  // de como se repartan las corridas entre los hilos.
  const auto better = [](const Best& candidate, const Best& current) {
    if (candidate.error != current.error) return candidate.error < current.error;
    if (candidate.leftIndex != current.leftIndex) return candidate.leftIndex < current.leftIndex;
    return candidate.rightIndex < current.rightIndex;
  };

  struct Partial {
    std::array<Best, 2> four;
    std::array<Best, 2> two;
  };

  std::cout << grid.size() << " x " << grid.size() << " combinaciones por evento, "
            << threads << " hilos\n";
  Stopwatch watch;
  long long runs = 0;
  for (const Event& event : experiment.events) {
    if (done.count(event.label) > 0) continue;
    std::atomic<std::size_t> next{0};
    std::vector<Partial> partials(static_cast<std::size_t>(threads));
    const auto work = [&](Partial& partial) {
      for (std::size_t a = next.fetch_add(1); a < grid.size(); a = next.fetch_add(1)) {
        for (std::size_t b = 0; b < grid.size(); ++b) {
          std::array<Avoidance, 2> layers;
          for (int i = 0; i < 2; ++i) {
            const Pair& pair = i == 0 ? grid[a] : grid[b];
            layers[static_cast<std::size_t>(i)].anticipation = pair.anticipation;
            layers[static_cast<std::size_t>(i)].margin = pair.margin;
            configureLayer(layers[static_cast<std::size_t>(i)], arguments);
          }
          // configureLayer pone el mismo alfa en los dos; el reparto es del
          // par, no de cada peaton, asi que al de la derecha le toca 1 - alfa.
          layers[1].share = 1.0 - layers[0].share;

          const Run run = simulate(event, model, layers, experiment.sampling, subdivisions);
          const Errors left = measure(event.left, run, 0);
          const Errors right = measure(event.right, run, 1);

          const std::array<double, 2> leftError{left.sameTime, left.closestPoint};
          const std::array<double, 2> rightError{right.sameTime, right.closestPoint};
          for (std::size_t metric = 0; metric < 2; ++metric) {
            const Best candidate{0.5 * (leftError[metric] + rightError[metric]),
                                 leftError[metric], rightError[metric], a, b};
            if (better(candidate, partial.four[metric])) partial.four[metric] = candidate;
            if (a == b && better(candidate, partial.two[metric])) partial.two[metric] = candidate;
          }
        }
      }
    };
    std::vector<std::thread> pool;
    for (int t = 1; t < threads; ++t) {
      pool.emplace_back(work, std::ref(partials[static_cast<std::size_t>(t)]));
    }
    work(partials[0]);
    for (std::thread& thread : pool) thread.join();
    runs += static_cast<long long>(grid.size() * grid.size());

    std::array<Best, 2> four;
    std::array<Best, 2> two;
    for (const Partial& partial : partials) {
      for (std::size_t metric = 0; metric < 2; ++metric) {
        if (better(partial.four[metric], four[metric])) four[metric] = partial.four[metric];
        if (better(partial.two[metric], two[metric])) two[metric] = partial.two[metric];
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
    file.flush();
    std::cout << "evento " << event.label << "  cuatro parametros: E1 = " << std::fixed
              << std::setprecision(4) << four[0].error << " contra " << two[0].error
              << " con dos   ("
              << std::setprecision(0) << watch.elapsedMilliseconds() / 1000.0 << " s)\n"
              << std::defaultfloat << std::flush;
  }
  std::cout << runs << " corridas (" << grid.size() << " x " << grid.size()
            << " combinaciones x " << experiment.events.size() - done.size() << " eventos) en "
            << std::fixed << std::setprecision(1) << watch.elapsedMilliseconds() / 1000.0
            << " s -> " << directory << "/pares.txt\n";
  return 0;
}
