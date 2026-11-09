#include "io.hpp"

#include <iomanip>
#include <sstream>
#include <stdexcept>
#include <sys/stat.h>
#include <sys/types.h>

void makeDirectory(const std::string& path) {
  std::string partial;
  for (std::size_t i = 0; i <= path.size(); ++i) {
    if (i == path.size() || path[i] == '/') {
      if (!partial.empty() && partial != ".") {
        ::mkdir(partial.c_str(), 0755);
      }
    }
    if (i < path.size()) {
      partial.push_back(path[i]);
    }
  }
}

std::ofstream openOutput(const std::string& path) {
  const std::size_t slash = path.rfind('/');
  if (slash != std::string::npos) {
    makeDirectory(path.substr(0, slash));
  }
  std::ofstream file(path);
  if (!file) {
    throw std::runtime_error("no se puede escribir " + path);
  }
  file << std::setprecision(10);
  return file;
}

std::vector<double> linearGrid(const std::string& name, const std::string& text) {
  if (text.find(':') == std::string::npos) {
    return numberList(name, text);
  }
  std::vector<std::string> pieces;
  std::stringstream stream(text);
  std::string token;
  while (std::getline(stream, token, ':')) {
    pieces.push_back(token);
  }
  if (pieces.size() != 3) {
    throw std::invalid_argument("--" + name +
                                " espera \"desde:hasta:cantidad\" o una lista con comas");
  }
  const double from = numberList(name, pieces[0]).front();
  const double to = numberList(name, pieces[1]).front();
  const int count = integerList(name, pieces[2]).front();
  if (count < 1) {
    throw std::invalid_argument("--" + name + " necesita al menos un valor en la grilla");
  }
  std::vector<double> values;
  values.reserve(static_cast<std::size_t>(count));
  for (int i = 0; i < count; ++i) {
    values.push_back(count == 1 ? from : from + (to - from) * i / (count - 1));
  }
  return values;
}

namespace {

void writePedestrian(std::ofstream& file, const char* name, const Pedestrian& pedestrian) {
  file << name << "_id " << pedestrian.id << "\n"
       << name << "_inicio " << pedestrian.start.x << " " << pedestrian.start.y << "\n"
       << name << "_velocidad_inicial " << pedestrian.initialVelocity.x << " "
       << pedestrian.initialVelocity.y << "\n"
       << name << "_target " << pedestrian.target.x << " " << pedestrian.target.y << "\n"
       << name << "_vd " << pedestrian.desiredSpeed << "\n"
       << name << "_camino " << pedestrian.pathLength << "\n"
       << name << "_muestras " << pedestrian.samples << "\n";
}

}

void writeStatic(const std::string& path, const Event& event, const Model& model,
                 const Avoidance& layer, const Run& run, double sampling) {
  std::ofstream file = openOutput(path);
  file << "evento " << event.label << "\n"
       << "cuadro_inicial " << event.firstFrame << "\n"
       << "instantes " << event.instants << "\n"
       << "dt_exp " << sampling << "\n"
       << "duracion " << event.duration << "\n"
       << "distancia_minima " << event.minimumDistance << "\n"
       << "dt " << run.step << "\n"
       << "subdivisiones " << run.subdivisions << "\n"
       << "capa " << (layer.kind == Kind::Predictive ? "predictiva" :
                      layer.kind == Kind::Field ? "campo" :
                      layer.kind == Kind::LateralField ? "campo-lateral" : "campo-predictivo") << "\n"
       << "p1 " << layer.anticipation << "\n"
       << "p2 " << layer.margin << "\n"
       << "alfa " << layer.share << "\n"
       << "instantes_en_conflicto " << run.conflictInstants << "\n"
       << "m " << model.mass << "\n"
       << "r " << model.radius << "\n"
       << "tau " << model.relaxation << "\n"
       << "kn " << model.normal << "\n"
       << "kt " << model.tangential << "\n";
  writePedestrian(file, "izquierda", event.left);
  writePedestrian(file, "derecha", event.right);
}

void writeDynamic(const std::string& path, const Run& run) {
  std::ofstream file = openOutput(path);
  for (std::size_t k = 0; k < run.time.size(); ++k) {
    file << run.time[k] << "\n";
    for (const AgentState& state : run.states[k]) {
      file << state.position.x << " " << state.position.y << " " << state.velocity.x
           << " " << state.velocity.y << " " << state.target.x << " " << state.target.y
           << " " << (state.conflict ? 1 : 0) << "\n";
    }
  }
}

void writeExperimental(const std::string& path, const Event& event, const Run& run,
                       double sampling) {
  std::ofstream file = openOutput(path);
  for (int k = 0; k < event.instants; ++k) {
    file << k * sampling;
    for (int i = 0; i < 2; ++i) {
      const Sample& sample = event.pedestrian(i).experimental[static_cast<std::size_t>(k)];
      file << " " << sample.position.x << " " << sample.position.y << " "
           << (sample.present ? 1 : 0);
    }
    file << "\n";
  }
  (void)run;
}
