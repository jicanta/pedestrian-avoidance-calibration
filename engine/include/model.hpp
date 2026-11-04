#pragma once

#include "geometry.hpp"

// SFM sin fuerza social (Helbing, Farkas y Vicsek 2000), con los parametros
// del paper y el radio que fija el enunciado.
//
//   m dv_i/dt = (m / tau) (v_i^d e_i^d - v_i) + sum_j f_ij
//
// El primer termino es la conduccion hacia el target: relaja la velocidad
// hacia la deseada en un tiempo tau. El segundo es el contacto, y SOLO existe
// mientras hay solapamiento (xi_ij = r_i + r_j - d_ij > 0): sacar la fuerza
// social es justamente quedarse con la parte granular,
//
//   f_ij = k xi_ij n_ij + kappa xi_ij (Dv_ji . t_ij) t_ij,
//
// con n_ij = (r_i - r_j)/d_ij la normal que empuja a i lejos de j, t_ij su
// perpendicular y Dv_ji = v_j - v_i la velocidad relativa.
//
// La capa de elusion (avoidance.hpp) no aparece aca: lo unico que cambia es
// e_i^d, la direccion de la velocidad deseada.
struct Model {
  double mass = 80.0;       // kg
  double radius = 0.25;     // m, lo fija el enunciado para SFM
  double relaxation = 0.5;  // s, tau del paper
  double normal = 1.2e5;    // k, N/m
  double tangential = 2.4e5;  // kappa, kg/(m s)
  // El agente se detiene al llegar al target final: a menos de `arrival`
  // radios de el la velocidad deseada pasa a ser cero y la conduccion lo frena
  // en tau. Sin esta regla el agente, que llega antes que el peaton real
  // porque su camino es mas corto que el medido, oscila alrededor del target.
  double arrival = 1.0;
};

// Fuerza de conduccion: (m / tau) (vd ed - v).
inline Vec2 drivingForce(const Model& model, const Vec2& velocity,
                         const Vec2& desiredVelocity) {
  return (desiredVelocity - velocity) * (model.mass / model.relaxation);
}

// Fuerza de contacto que j ejerce sobre i. Devuelve cero si no se solapan.
inline Vec2 contactForce(const Model& model, const Vec2& position, const Vec2& velocity,
                         const Vec2& otherPosition, const Vec2& otherVelocity) {
  const Vec2 difference = position - otherPosition;
  const double distance = norm(difference);
  const double overlap = 2.0 * model.radius - distance;
  if (overlap <= 0.0 || distance <= 0.0) {
    return {0.0, 0.0};
  }
  const Vec2 normalDirection = difference * (1.0 / distance);
  const Vec2 tangentDirection{-normalDirection.y, normalDirection.x};
  const double slip = dot(otherVelocity - velocity, tangentDirection);
  return normalDirection * (model.normal * overlap) +
         tangentDirection * (model.tangential * overlap * slip);
}
