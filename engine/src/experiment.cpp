#include "experiment.hpp"

#include <algorithm>
#include <cmath>
#include <fstream>
#include <iterator>
#include <map>
#include <sstream>
#include <stdexcept>
#include <vector>

namespace {

// Cuantos cuadros abarca la diferencia finita con la que se estima la
// velocidad experimental inicial. Una sola diferencia entre cuadros
// consecutivos mide el ruido del seguimiento (unos 5 mm, que a 15 cuadros por
// segundo son 0,08 m/s sobre una rapidez de 0,9 m/s) y no la velocidad del
// peaton; con cinco cuadros (un tercio de segundo) el ruido queda en 0,02 m/s
// y el peaton todavia no cambio de direccion.
constexpr int kVelocityWindow = 5;

struct Track {
  std::map<int, Vec2> byFrame;
};

std::map<int, Track> readTracks(const std::string& path, double& framerate) {
  std::ifstream file(path);
  if (!file) {
    throw std::invalid_argument("no se puede abrir el archivo de trayectorias " + path);
  }
  std::map<int, Track> tracks;
  std::string line;
  while (std::getline(file, line)) {
    if (line.empty()) {
      continue;
    }
    if (line[0] == '#') {
      // "# framerate: 15.0192 fps" es la unica linea del encabezado con un
      // numero que haga falta; el resto son los nombres de las columnas.
      const std::size_t colon = line.find(':');
      if (line.find("framerate") != std::string::npos && colon != std::string::npos) {
        std::istringstream rest(line.substr(colon + 1));
        rest >> framerate;
      }
      continue;
    }
    std::istringstream pieces(line);
    int id = 0;
    int frame = 0;
    Vec2 position;
    if (!(pieces >> id >> frame >> position.x >> position.y)) {
      continue;
    }
    tracks[id].byFrame[frame] = position;
  }
  if (framerate <= 0.0) {
    throw std::invalid_argument("el archivo de trayectorias no declara framerate");
  }
  return tracks;
}

// Primer y ultimo cuadro de una trayectoria dentro del intervalo [from, to]
// que declara el LEEME; -1 si no tiene ninguno.
int firstFrameIn(const Track& track, int from, int to) {
  const auto found = track.byFrame.lower_bound(from);
  if (found == track.byFrame.end() || found->first > to) {
    return -1;
  }
  return found->first;
}

int lastFrameIn(const Track& track, int from, int to) {
  const auto found = track.byFrame.upper_bound(to);
  if (found == track.byFrame.begin()) {
    return -1;
  }
  const int frame = std::prev(found)->first;
  return frame < from ? -1 : frame;
}


// Recorte de la ventana al TRAMO DEL CORREDOR en que los dos peatones caminan
// uno hacia el otro: xMin <= x <= xMax para los dos.
//
// La ventana que declara el LEEME es mas larga que el cruce por los dos
// extremos: al principio los peatones todavia estan en la fila (parados, o
// subiendo hacia la cabecera) y al final frenan y doblan hacia la fila de la
// vuelta siguiente. Las 38 trayectorias medidas, dibujadas juntas, muestran de
// donde parten y adonde llegan todos: las cabeceras de las dos filas estan en
// x = 0,6 m y en x = 8,1 m, y entre una y otra los peatones caminan por el
// corredor. El recorte es entonces una restriccion sobre el eje x, la misma
// para los 19 eventos: la ventana va del primer cuadro al ultimo en que los
// dos peatones estan adentro de [xMin, xMax]. Empieza cuando el ultimo de los
// dos entra al tramo y termina cuando el primero de los dos lo deja.
//
// Los cuadros en que a alguno le falta la muestra (huecos de seguimiento) no
// abren ni cierran la ventana, pero pueden quedar adentro: ahi el error no se
// evalua (ver experiment.hpp).
void trimToCorridor(const Track& left, const Track& right, double xMin, double xMax,
                    int& first, int& last) {
  int insideFirst = -1;
  int insideLast = -1;
  for (int frame = first; frame <= last; ++frame) {
    const auto a = left.byFrame.find(frame);
    const auto b = right.byFrame.find(frame);
    if (a == left.byFrame.end() || b == right.byFrame.end()) {
      continue;
    }
    const bool inside = a->second.x >= xMin && a->second.x <= xMax &&
                        b->second.x >= xMin && b->second.x <= xMax;
    if (inside) {
      if (insideFirst < 0) {
        insideFirst = frame;
      }
      insideLast = frame;
    }
  }
  if (insideFirst < 0 || insideLast - insideFirst < 2) {
    throw std::invalid_argument("los dos peatones no coinciden dentro del tramo de x pedido");
  }
  first = insideFirst;
  last = insideLast;
}

struct Row {
  int label = 0;
  int left = 0;
  int right = 0;
  int firstFrame = 0;
  int lastFrame = 0;
};

std::vector<Row> readTable(const std::string& path) {
  std::ifstream file(path);
  if (!file) {
    throw std::invalid_argument("no se puede abrir la tabla de eventos " + path);
  }
  std::vector<Row> rows;
  std::string line;
  while (std::getline(file, line)) {
    if (line.empty() || line[0] == '#') {
      continue;
    }
    std::istringstream pieces(line);
    Row row;
    if (pieces >> row.label >> row.left >> row.right >> row.firstFrame >> row.lastFrame) {
      rows.push_back(row);
    }
  }
  if (rows.empty()) {
    throw std::invalid_argument("la tabla de eventos " + path + " esta vacia");
  }
  return rows;
}

// Trayectoria de un peaton sobre la ventana [first, last], con las condiciones
// que el enunciado fija a partir de ella: posicion y velocidad iniciales,
// target final y rapidez media.
Pedestrian build(int id, const Track& track, int first, int last, double sampling) {
  Pedestrian pedestrian;
  pedestrian.id = id;
  pedestrian.experimental.resize(static_cast<std::size_t>(last - first + 1));
  for (int frame = first; frame <= last; ++frame) {
    const auto found = track.byFrame.find(frame);
    if (found != track.byFrame.end()) {
      Sample& sample = pedestrian.experimental[static_cast<std::size_t>(frame - first)];
      sample.position = found->second;
      sample.present = true;
      ++pedestrian.samples;
    }
  }

  // Largo del camino medido: solo los tramos entre muestras consecutivas
  // presentes (los huecos de seguimiento no se interpolan, asi que tampoco
  // aportan camino ni tiempo). La rapidez media es ese camino sobre el tiempo
  // que cubren esos tramos.
  int segments = 0;
  for (std::size_t k = 0; k + 1 < pedestrian.experimental.size(); ++k) {
    const Sample& a = pedestrian.experimental[k];
    const Sample& b = pedestrian.experimental[k + 1];
    if (a.present && b.present) {
      pedestrian.pathLength += norm(b.position - a.position);
      ++segments;
    }
  }
  if (segments == 0) {
    throw std::invalid_argument("el peaton " + std::to_string(id) +
                                " no tiene dos muestras consecutivas en la ventana");
  }
  pedestrian.desiredSpeed = pedestrian.pathLength / (segments * sampling);

  pedestrian.start = pedestrian.experimental.front().position;
  for (std::size_t k = pedestrian.experimental.size(); k-- > 0;) {
    if (pedestrian.experimental[k].present) {
      pedestrian.target = pedestrian.experimental[k].position;
      break;
    }
  }

  // Velocidad inicial: diferencia finita hacia adelante sobre kVelocityWindow
  // cuadros. Si justo ahi hay un hueco de seguimiento se toma la primera
  // muestra que haya mas adelante, y si la ventana es mas corta que eso, la
  // ultima que haya antes.
  const int lastIndex = static_cast<int>(pedestrian.experimental.size()) - 1;
  int span = 0;
  for (int j = std::min(kVelocityWindow, lastIndex); j <= lastIndex; ++j) {
    if (pedestrian.experimental[static_cast<std::size_t>(j)].present) {
      span = j;
      break;
    }
  }
  for (int j = std::min(kVelocityWindow, lastIndex) - 1; span == 0 && j >= 1; --j) {
    if (pedestrian.experimental[static_cast<std::size_t>(j)].present) {
      span = j;
    }
  }
  if (span == 0) {
    throw std::invalid_argument("el peaton " + std::to_string(id) +
                                " no tiene con que estimar la velocidad inicial");
  }
  pedestrian.initialVelocity =
      (pedestrian.experimental[static_cast<std::size_t>(span)].position -
       pedestrian.start) * (1.0 / (span * sampling));
  return pedestrian;
}

}

Experiment readExperiment(const std::string& trajectories, const std::string& table,
                          const std::vector<int>& labels, double xMin, double xMax) {
  Experiment experiment;
  const std::map<int, Track> tracks = readTracks(trajectories, experiment.framerate);
  experiment.sampling = 1.0 / experiment.framerate;

  for (const Row& row : readTable(table)) {
    if (!labels.empty() &&
        std::find(labels.begin(), labels.end(), row.label) == labels.end()) {
      continue;
    }
    const auto left = tracks.find(row.left);
    const auto right = tracks.find(row.right);
    if (left == tracks.end() || right == tracks.end()) {
      throw std::invalid_argument("la prueba " + std::to_string(row.label) +
                                  " nombra un peaton que no esta en los datos");
    }

    // Ventana comun: dentro del intervalo que declara el LEEME, desde el
    // primer cuadro en que estan los dos hasta el ultimo en que estan los dos.
    // El recorte al intervalo del LEEME va PRIMERO: un mismo peaton aparece en
    // varias pruebas (haciendo la fila, antes y despues de la suya), asi que
    // sus cuadros extremos en el archivo no son los de este evento.
    const int leftFirst = firstFrameIn(left->second, row.firstFrame, row.lastFrame);
    const int leftLast = lastFrameIn(left->second, row.firstFrame, row.lastFrame);
    const int rightFirst = firstFrameIn(right->second, row.firstFrame, row.lastFrame);
    const int rightLast = lastFrameIn(right->second, row.firstFrame, row.lastFrame);
    if (leftFirst < 0 || rightFirst < 0) {
      throw std::invalid_argument("la prueba " + std::to_string(row.label) +
                                  " no tiene muestras en los cuadros del LEEME");
    }
    const int first = std::max(leftFirst, rightFirst);
    const int last = std::min(leftLast, rightLast);
    if (last - first < 2) {
      throw std::invalid_argument("la prueba " + std::to_string(row.label) +
                                  " no tiene ventana comun");
    }

    int firstFrame = first;
    int lastFrame = last;
    trimToCorridor(left->second, right->second, xMin, xMax, firstFrame, lastFrame);

    Event event;
    event.label = row.label;
    event.firstFrame = firstFrame;
    event.instants = lastFrame - firstFrame + 1;
    event.duration = (event.instants - 1) * experiment.sampling;
    event.left = build(row.left, left->second, firstFrame, lastFrame, experiment.sampling);
    event.right =
        build(row.right, right->second, firstFrame, lastFrame, experiment.sampling);

    event.minimumDistance = -1.0;
    for (int k = 0; k < event.instants; ++k) {
      const Sample& a = event.left.experimental[static_cast<std::size_t>(k)];
      const Sample& b = event.right.experimental[static_cast<std::size_t>(k)];
      if (a.present && b.present) {
        const double distance = norm(a.position - b.position);
        if (event.minimumDistance < 0.0 || distance < event.minimumDistance) {
          event.minimumDistance = distance;
        }
      }
    }
    experiment.events.push_back(event);
  }
  if (experiment.events.empty()) {
    throw std::invalid_argument("ninguna prueba de la tabla quedo seleccionada");
  }
  return experiment;
}
