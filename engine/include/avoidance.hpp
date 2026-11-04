#pragma once

#include <algorithm>
#include <cmath>

#include "geometry.hpp"

// =========================================================================
// Capa de elusion: target temporal por anticipacion de colision
// =========================================================================
//
// El SFM sin fuerza social no anticipa: el agente va derecho a su target y
// solo reacciona cuando ya hay contacto. La capa agrega la anticipacion SIN
// tocar el modelo: no suma ninguna fuerza ni cambia ninguna regla, solo
// reemplaza transitoriamente el target final T_i por un target temporal
// T_i^*, que es lo unico que decide la DIRECCION de la velocidad deseada.
//
// Tiene exactamente DOS parametros a ajustar:
//
//   p1 = ta : tiempo de anticipacion (s). Solo se reacciona a conflictos que
//             van a ocurrir dentro de los proximos ta segundos. Con ta = 0 la
//             capa esta apagada y queda el SFM puro.
//   p2 = ds : margen de espacio personal (m). El agente quiere pasar a mas de
//             r_i + r_j + ds del otro; ds = 0 es querer pasar justo rozandolo.
//
// La geometria es la de los modelos predictivos de elusion (Karamouzas et al.
// 2009, que usan el mismo par tiempo de anticipacion / espacio personal pero
// lo resuelven con una fuerza evasiva, que aca no esta permitida).
//
// Para el agente i frente al agente j, con Dr = r_j - r_i y Dv = v_j - v_i:
//
//   1. Instante de minima aproximacion (extrapolacion lineal de las dos
//      trayectorias):            tau* = - (Dr . Dv) / |Dv|^2
//   2. Separacion predicha ahi:  d*   = |Dr + Dv tau*|
//   3. Distancia requerida:      D    = r_i + r_j + ds
//   4. Hay CONFLICTO si          0 < tau* <= ta  y  d* < D
//
// Si no hay conflicto, T_i^* = T_i: el agente va a su target final. Esto
// incluye el caso en que ya se cruzaron (tau* <= 0, se estan separando), asi
// que el regreso al target final es automatico.
//
// Si hay conflicto, el target temporal es el punto del camino nominal al
// instante del conflicto, corrido lateralmente lo que falta de separacion:
//
//   q_i     = r_i + vd_i tau* e_i^0,   e_i^0 = (T_i - r_i)/|T_i - r_i|
//   s       = (p_i - p_j)/|p_i - p_j|, p_i = r_i + v_i tau*, p_j = r_j + v_j tau*
//   w(tau*) = 1 - tau*/ta
//   T_i^*   = q_i + w(tau*) (D - d*) s
//
// q_i es donde estaria el agente al momento del conflicto si siguiera derecho
// a su target; s es la direccion en la que los dos ya van a estar separados en
// ese momento, de modo que cada uno acentua el lado al que ya esta corrido y
// los dos se eluden de manera reciproca y simetrica; (D - d*) es exactamente
// la separacion que falta.
//
// w(tau*) es un peso de urgencia que hace la capa CONTINUA en los dos bordes
// del disparo: en tau* = ta vale 0 y el target temporal coincide con q_i, que
// esta sobre la recta al target final, asi que al entrar y al salir del
// horizonte de anticipacion la direccion deseada no salta; y en tau* -> 0
// vale 1 y, como ahi q_i -> r_i, el target temporal queda puramente lateral:
// el agente se corre de costado, que es el limite correcto cuando el conflicto
// es inminente. Sin w, la direccion deseada saltaria al cruzar tau* = ta (la
// velocidad seguiria siendo continua porque la conduccion la relaja en tau,
// pero la aceleracion no).
//
// Degenerado: si los dos van exactamente de frente, p_i - p_j se hace cero y
// s queda indefinida. Ahi se usa la normal a la direccion nominal, con el lado
// que elige el signo de Dr x e_i^0 (el lado al que el otro NO esta), y si eso
// tambien es cero se elige la derecha, que es el criterio fijo del modelo.

struct Avoidance {
  double anticipation = 0.0;  // p1 = ta (s)
  double margin = 0.0;        // p2 = ds (m)
  // Peso de urgencia w(tau*). Con `ramp` la capa es continua en los dos
  // bordes del disparo; sin el (w = 1) el desvio es el mismo a cualquier
  // anticipacion y la direccion deseada salta al cruzar tau* = ta. Las dos
  // variantes se comparan en el README; la rampa es la que corre.
  bool ramp = true;
  // Donde se pone el punto de mira sobre el camino nominal: a vd*tau* (el
  // instante del conflicto, que es la variante que corre) o a vd*ta (el
  // horizonte de anticipacion). Ver README.
  bool leadIsHorizon = false;

  bool enabled() const { return anticipation > 0.0; }
};

// Lo que la capa decidio en un instante, para poder dibujarlo y contarlo.
struct AvoidanceDecision {
  bool conflict = false;
  double timeToClosest = 0.0;  // tau*
  double predicted = 0.0;      // d*
  Vec2 target;                 // T_i^* (el final si no hay conflicto)
};

// Target temporal del agente i frente al agente j. `finalTarget` es T_i y
// `desiredSpeed` el modulo de su velocidad deseada, que la capa no toca.
inline AvoidanceDecision temporaryTarget(const Avoidance& layer, double contactDistance,
                                         const Vec2& position, const Vec2& velocity,
                                         const Vec2& otherPosition,
                                         const Vec2& otherVelocity,
                                         const Vec2& finalTarget, double desiredSpeed) {
  AvoidanceDecision decision;
  decision.target = finalTarget;
  if (!layer.enabled()) {
    return decision;
  }

  const Vec2 relativePosition = otherPosition - position;
  const Vec2 relativeVelocity = otherVelocity - velocity;
  const double closingSpeed = squaredNorm(relativeVelocity);
  if (closingSpeed <= 0.0) {
    return decision;
  }

  const double timeToClosest = -dot(relativePosition, relativeVelocity) / closingSpeed;
  if (timeToClosest <= 0.0 || timeToClosest > layer.anticipation) {
    return decision;
  }
  const Vec2 separationAtClosest = relativePosition + relativeVelocity * timeToClosest;
  const double predicted = norm(separationAtClosest);
  const double required = contactDistance + layer.margin;
  decision.timeToClosest = timeToClosest;
  decision.predicted = predicted;
  if (predicted >= required) {
    return decision;
  }
  decision.conflict = true;

  const Vec2 toTarget = finalTarget - position;
  const double distanceToTarget = norm(toTarget);
  if (distanceToTarget <= 0.0) {
    return decision;
  }
  const Vec2 nominalDirection = toTarget * (1.0 / distanceToTarget);

  // Direccion de separacion al instante del conflicto: -separationAtClosest es
  // p_i - p_j, lo que queda de distancia entre los dos en ese momento.
  Vec2 sideways = separationAtClosest * -1.0;
  const double sidewaysNorm = norm(sideways);
  if (sidewaysNorm > 1e-9) {
    sideways = sideways * (1.0 / sidewaysNorm);
  } else {
    const Vec2 leftNormal{-nominalDirection.y, nominalDirection.x};
    const double cross =
        relativePosition.x * nominalDirection.y - relativePosition.y * nominalDirection.x;
    // cross > 0: el otro esta a la derecha del camino nominal, asi que se
    // elude por la izquierda. cross == 0 (de frente exacto): por la derecha.
    sideways = cross > 0.0 ? leftNormal : leftNormal * -1.0;
  }

  const double urgency = layer.ramp ? 1.0 - timeToClosest / layer.anticipation : 1.0;
  const double lead = layer.leadIsHorizon ? layer.anticipation : timeToClosest;
  const Vec2 nominalPoint = position + nominalDirection * (desiredSpeed * lead);
  decision.target = nominalPoint + sideways * (urgency * (required - predicted));
  return decision;
}
