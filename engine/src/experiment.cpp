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

// Eje del corredor por el que se cruzan los dos peatones. El LEEME de la
// catedra lo declara ("se cruzan por y ~ 2 m") y el archivo crudo lo confirma:
// el histograma de y es bimodal, con unas 6300 muestras alrededor de y = 2 (el
// corredor) y unas 8800 debajo de y = 0,5 (las dos filas), separadas por un
// valle casi vacio en y = 1. Las filas estan DENTRO del rectangulo filmado
// (x de 0,08 a 11,40 m, y de -0,69 a 3,73 m): lo que sobra de la ventana no es
// seguimiento fuera de cuadro, es la fila.
constexpr double kCorridorAxis = 2.0;

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


// Rapidez medida de una trayectoria en el cuadro `frame`, como diferencia
// centrada sobre +-`half` cuadros (0,27 s con half = 2): una diferencia entre
// cuadros consecutivos mide el ruido del seguimiento y no el paso del peaton.
// Devuelve -1 si en ese cuadro no se puede estimar.
double measuredSpeed(const Track& track, int frame, int from, int to, double sampling,
                     int half) {
  const int low = std::max(from, frame - half);
  const int high = std::min(to, frame + half);
  if (high <= low) {
    return -1.0;
  }
  const auto a = track.byFrame.find(low);
  const auto b = track.byFrame.find(high);
  if (a == track.byFrame.end() || b == track.byFrame.end()) {
    return -1.0;
  }
  return norm(b->second - a->second) / ((high - low) * sampling);
}

// Ritmo de crucero de una trayectoria sobre la ventana: el percentil 75 de la
// rapidez medida. No se usa el maximo (es el ruido del seguimiento en el
// cuadro mas desafortunado) ni la media (que es justamente lo que el arranque
// y la frenada ensucian): el percentil 75 es la rapidez de la parte en que el
// peaton ya camina parejo.
double cruiseSpeed(const Track& track, int from, int to, double sampling) {
  std::vector<double> speeds;
  for (int frame = from; frame <= to; ++frame) {
    const double speed = measuredSpeed(track, frame, from, to, sampling, 2);
    if (speed > 0.0) {
      speeds.push_back(speed);
    }
  }
  if (speeds.empty()) {
    return -1.0;
  }
  std::sort(speeds.begin(), speeds.end());
  const double position = 0.75 * (static_cast<double>(speeds.size()) - 1.0);
  const std::size_t low = static_cast<std::size_t>(position);
  const std::size_t high = std::min(low + 1, speeds.size() - 1);
  return speeds[low] + (position - static_cast<double>(low)) * (speeds[high] - speeds[low]);
}

// Recorte de la ventana a la parte en que los DOS peatones ya estan caminando:
// el primero y el ultimo cuadro en que los dos miden una rapidez de al menos
// su umbral. El enunciado habla de dos peatones "que caminan en curso de
// colision", y la ventana que declara el LEEME es mas larga que eso por los
// DOS extremos: al principio de varias pruebas uno de los dos todavia esta
// haciendo la fila, parado, y al final casi todos frenan y doblan hacia la
// fila de la vuelta siguiente. Los dos extremos rompen las condiciones que el
// enunciado fija a partir de la trayectoria:
//
//   * la rapidez media (que es el modulo de la velocidad deseada) baja muy por
//     debajo de la rapidez con la que el peaton camina, porque promedia el
//     arranque y la frenada;
//   * el target final, que es la ULTIMA posicion medida, cae donde el peaton
//     ya dejo el corredor, asi que el agente simulado apunta de costado desde
//     t = 0 y la recta al target no es la ruta que el peaton caminaba.
//
// El umbral de cada peaton es el mayor entre `threshold` (absoluto, m/s) y
// `fraction` veces su propio ritmo de crucero. El relativo es el que hace el
// trabajo: los peatones caminan entre 1,2 y 1,6 m/s, asi que un mismo umbral
// absoluto recorta mucho a uno y nada al otro. Con los dos en 0 no se recorta.
//
// `corridor` (semiancho, m) agrega una condicion de LUGAR: los dos peatones
// tienen que estar sobre el corredor, |y - kCorridorAxis| <= corridor. Las dos
// condiciones de rapidez miran cuanto camina el peaton y no por donde, asi que
// no alcanzan para el unico tramo de fila que se camina rapido: salir de la
// fila hacia el corredor, que son 1,7 m de subida en y sin avanzar nada en x.
// Con 0 esta apagada.
void trimToWalking(const Track& left, const Track& right, double threshold, double fraction,
                   double corridor, double sampling, int& first, int& last) {
  if (threshold <= 0.0 && fraction <= 0.0 && corridor <= 0.0) {
    return;
  }
  double leftThreshold = threshold;
  double rightThreshold = threshold;
  if (fraction > 0.0) {
    const double leftCruise = cruiseSpeed(left, first, last, sampling);
    const double rightCruise = cruiseSpeed(right, first, last, sampling);
    if (leftCruise <= 0.0 || rightCruise <= 0.0) {
      return;
    }
    leftThreshold = std::max(leftThreshold, fraction * leftCruise);
    rightThreshold = std::max(rightThreshold, fraction * rightCruise);
  }
  int walkingFirst = -1;
  int walkingLast = -1;
  for (int frame = first; frame <= last; ++frame) {
    const double a = measuredSpeed(left, frame, first, last, sampling, 2);
    const double b = measuredSpeed(right, frame, first, last, sampling, 2);
    bool inside = a >= leftThreshold && b >= rightThreshold;
    if (inside && corridor > 0.0) {
      const auto leftSample = left.byFrame.find(frame);
      const auto rightSample = right.byFrame.find(frame);
      inside = leftSample != left.byFrame.end() && rightSample != right.byFrame.end() &&
               std::abs(leftSample->second.y - kCorridorAxis) <= corridor &&
               std::abs(rightSample->second.y - kCorridorAxis) <= corridor;
    }
    if (inside) {
      if (walkingFirst < 0) {
        walkingFirst = frame;
      }
      walkingLast = frame;
    }
  }
  if (walkingFirst >= 0 && walkingLast - walkingFirst >= 2) {
    first = walkingFirst;
    last = walkingLast;
  }
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
                          const std::vector<int>& labels, double walkingThreshold,
                          double walkingFraction, double corridorHalfWidth) {
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
    trimToWalking(left->second, right->second, walkingThreshold, walkingFraction,
                  corridorHalfWidth, experiment.sampling, firstFrame, lastFrame);

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
