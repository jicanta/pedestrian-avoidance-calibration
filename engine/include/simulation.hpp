#pragma once

#include <array>
#include <vector>

#include "avoidance.hpp"
#include "experiment.hpp"
#include "geometry.hpp"
#include "model.hpp"

// Estado de un agente en un instante experimental, tal como se guarda.
struct AgentState {
  Vec2 position;
  Vec2 velocity;
  Vec2 target;        // el target que la capa de elusion le puso en ese instante
  bool conflict = false;
};

// Una corrida: el estado de los dos agentes en cada uno de los Nm instantes
// experimentales del evento. El paso de integracion divide dtExp en un numero
// entero de partes, asi que todo instante experimental es exactamente un paso
// de la simulacion y no hay que interpolar nada para comparar.
struct Run {
  double step = 0.0;        // dt
  int subdivisions = 0;     // dtExp / dt
  std::vector<double> time;                   // Nm instantes
  std::vector<std::array<AgentState, 2>> states;
  int conflictInstants = 0;  // instantes con conflicto declarado (agente 0 u 1)
};

Run simulate(const Event& event, const Model& model, const Avoidance& layer,
             double sampling, int subdivisions);

// Las dos metricas de error cuadratico medio del enunciado, para un peaton.
//   metrica 1 (a iguales tiempos):  media_k |r^exp(t_k) - r^sim(t_k)|^2
//   metrica 2 (punto mas cercano):  media_k min_j |r^exp(t_k) - r^sim(t_j)|^2
// La media va sobre los instantes en que ese peaton TIENE muestra: los huecos
// de seguimiento no se interpolan, asi que tampoco se puntuan.
struct Errors {
  double sameTime = 0.0;
  double closestPoint = 0.0;
};

Errors measure(const Pedestrian& pedestrian, const Run& run, int index);
