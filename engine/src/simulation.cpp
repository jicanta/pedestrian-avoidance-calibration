#include "simulation.hpp"

#include <array>
#include <cmath>

namespace {

struct Agent {
  Vec2 position;
  Vec2 velocity;
  Vec2 acceleration;
  Vec2 previousAcceleration;
  Vec2 target;        // target final
  double desiredSpeed = 0.0;
  Vec2 temporaryTarget;
  bool conflict = false;
};

// Velocidad deseada del agente: modulo fijo (la rapidez media de su
// trayectoria experimental) en la direccion del target que le toca en este
// instante, que es el temporal si la capa declaro conflicto y el final si no.
// Al llegar al target final el agente se detiene.
Vec2 desiredVelocity(const Model& model, const Agent& agent) {
  if (norm(agent.target - agent.position) < model.arrival * model.radius) {
    return {0.0, 0.0};
  }
  const Vec2 toTarget = agent.temporaryTarget - agent.position;
  const double distance = norm(toTarget);
  if (distance <= 0.0) {
    return {0.0, 0.0};
  }
  return toTarget * (agent.desiredSpeed / distance);
}

// Decide el target de los dos agentes con la capa de elusion y despues calcula
// la aceleracion de cada uno: conduccion mas contacto. La capa se evalua con
// las posiciones y velocidades del mismo instante para los dos, de modo que la
// elusion es reciproca.
void accelerations(const Model& model, const Avoidance& layer, std::array<Agent, 2>& agents) {
  const double contactDistance = 2.0 * model.radius;
  for (int i = 0; i < 2; ++i) {
    const Agent& other = agents[1 - i];
    const AvoidanceDecision decision =
        temporaryTarget(layer, contactDistance, agents[i].position, agents[i].velocity,
                        other.position, other.velocity, agents[i].target,
                        agents[i].desiredSpeed);
    agents[i].temporaryTarget = decision.target;
    agents[i].conflict = decision.conflict;
  }
  for (int i = 0; i < 2; ++i) {
    const Agent& other = agents[1 - i];
    const Vec2 force =
        drivingForce(model, agents[i].velocity, desiredVelocity(model, agents[i])) +
        contactForce(model, agents[i].position, agents[i].velocity, other.position,
                     other.velocity);
    agents[i].acceleration = force * (1.0 / model.mass);
  }
}

AgentState snapshot(const Agent& agent) {
  AgentState state;
  state.position = agent.position;
  state.velocity = agent.velocity;
  state.target = agent.temporaryTarget;
  state.conflict = agent.conflict;
  return state;
}

}

Run simulate(const Event& event, const Model& model, const Avoidance& layer,
             double sampling, int subdivisions) {
  Run run;
  run.subdivisions = subdivisions;
  run.step = sampling / subdivisions;
  const double step = run.step;

  std::array<Agent, 2> agents;
  for (int i = 0; i < 2; ++i) {
    const Pedestrian& pedestrian = event.pedestrian(i);
    agents[static_cast<std::size_t>(i)].position = pedestrian.start;
    agents[static_cast<std::size_t>(i)].velocity = pedestrian.initialVelocity;
    agents[static_cast<std::size_t>(i)].target = pedestrian.target;
    agents[static_cast<std::size_t>(i)].desiredSpeed = pedestrian.desiredSpeed;
    agents[static_cast<std::size_t>(i)].temporaryTarget = pedestrian.target;
  }

  // Beeman predictor-corrector (Teorica 4, diapositiva 20): es el esquema que
  // la teorica da para fuerzas que dependen de la velocidad, que es el caso
  // aca (la conduccion lleva -v/tau y el contacto, friccion tangencial). El
  // primer paso no tiene a(t - dt): se usa a(0), que es el arranque habitual.
  accelerations(model, layer, agents);
  for (Agent& agent : agents) {
    agent.previousAcceleration = agent.acceleration;
  }

  run.time.reserve(static_cast<std::size_t>(event.instants));
  run.states.reserve(static_cast<std::size_t>(event.instants));
  run.time.push_back(0.0);
  run.states.push_back({snapshot(agents[0]), snapshot(agents[1])});

  const long long steps = static_cast<long long>(event.instants - 1) * subdivisions;
  for (long long n = 0; n < steps; ++n) {
    std::array<Agent, 2> predicted = agents;
    for (int i = 0; i < 2; ++i) {
      Agent& agent = predicted[static_cast<std::size_t>(i)];
      const Agent& current = agents[static_cast<std::size_t>(i)];
      agent.position = current.position + current.velocity * step +
                       current.acceleration * (2.0 / 3.0 * step * step) -
                       current.previousAcceleration * (1.0 / 6.0 * step * step);
      agent.velocity = current.velocity + current.acceleration * (1.5 * step) -
                       current.previousAcceleration * (0.5 * step);
    }
    accelerations(model, layer, predicted);
    for (int i = 0; i < 2; ++i) {
      Agent& agent = agents[static_cast<std::size_t>(i)];
      const Agent& guess = predicted[static_cast<std::size_t>(i)];
      const Vec2 corrected = agent.velocity + guess.acceleration * (step / 3.0) +
                             agent.acceleration * (5.0 / 6.0 * step) -
                             agent.previousAcceleration * (step / 6.0);
      agent.position = guess.position;
      agent.velocity = corrected;
      agent.previousAcceleration = agent.acceleration;
      agent.temporaryTarget = guess.temporaryTarget;
      agent.conflict = guess.conflict;
    }
    // La aceleracion del nuevo instante se evalua con el estado corregido, que
    // es el que se guarda: asi r, v y a del estado son del mismo instante.
    accelerations(model, layer, agents);

    if ((n + 1) % subdivisions == 0) {
      const int instant = static_cast<int>((n + 1) / subdivisions);
      run.time.push_back(instant * sampling);
      run.states.push_back({snapshot(agents[0]), snapshot(agents[1])});
      if (agents[0].conflict || agents[1].conflict) {
        ++run.conflictInstants;
      }
    }
  }
  return run;
}

Errors measure(const Pedestrian& pedestrian, const Run& run, int index) {
  Errors errors;
  int counted = 0;
  for (std::size_t k = 0; k < pedestrian.experimental.size() && k < run.states.size(); ++k) {
    const Sample& sample = pedestrian.experimental[k];
    if (!sample.present) {
      continue;
    }
    const Vec2& simulated = run.states[k][static_cast<std::size_t>(index)].position;
    errors.sameTime += squaredNorm(sample.position - simulated);

    double closest = -1.0;
    for (const auto& state : run.states) {
      const double distance =
          squaredNorm(sample.position - state[static_cast<std::size_t>(index)].position);
      if (closest < 0.0 || distance < closest) {
        closest = distance;
      }
    }
    errors.closestPoint += closest;
    ++counted;
  }
  if (counted > 0) {
    errors.sameTime /= counted;
    errors.closestPoint /= counted;
  }
  return errors;
}
