#pragma once

#include <string>
#include <vector>

#include "geometry.hpp"

// Datos experimentales de la catedra (elusion 1 contra 1 de frente).
//
// El archivo crudo tiene una linea "id cuadro x y markerID" por muestra y un
// encabezado con la tasa de cuadros; el archivo de eventos tiene una linea
// "m id_izquierda id_derecha cuadro_inicial cuadro_final" por prueba, copiada
// del LEEME de la catedra. De ahi sale cada evento m con sus dos peatones.
//
// La ventana de un evento es la INTERSECCION de los intervalos en los que los
// dos peatones estan seguidos (dentro de los cuadros que declara el LEEME),
// recortada despues al tramo del corredor xMin <= x <= xMax (ver
// trimToCorridor en experiment.cpp): afuera de ese tramo los peatones estan en
// la fila o llegando a ella, y eso no es el cruce que el enunciado describe.
// Los huecos de seguimiento que quedan adentro de esa ventana no se rellenan:
// la muestra queda marcada como ausente y el error no se evalua en ese
// instante (el agente se simula igual, que es lo que lo acopla con el otro).

struct Sample {
  Vec2 position;
  bool present = false;
};

// Un peaton de un evento: su trayectoria experimental sobre la ventana comun y
// las condiciones que el enunciado fija a partir de ella.
struct Pedestrian {
  int id = 0;
  std::vector<Sample> experimental;  // una muestra por instante de la ventana
  Vec2 start;                        // posicion experimental inicial
  Vec2 initialVelocity;              // velocidad experimental inicial
  Vec2 target;                       // ultima posicion experimental: target final
  double desiredSpeed = 0.0;         // rapidez media de la trayectoria
  double pathLength = 0.0;
  int samples = 0;                   // muestras presentes (el Nm de este peaton)
};

struct Event {
  int label = 0;            // numero de prueba del LEEME
  int firstFrame = 0;       // primer cuadro de la ventana comun
  int instants = 0;         // Nm: instantes experimentales de la ventana
  double duration = 0.0;    // (Nm - 1) dtExp
  double minimumDistance = 0.0;
  Pedestrian left;
  Pedestrian right;

  const Pedestrian& pedestrian(int index) const { return index == 0 ? left : right; }
};

struct Experiment {
  double framerate = 0.0;
  double sampling = 0.0;  // dtExp = 1 / framerate
  std::vector<Event> events;
};

// Lee el archivo crudo de trayectorias y la tabla de eventos y arma los M
// eventos. `labels` vacio toma todos; si no, solo esas pruebas.
// `xMin` y `xMax` (m) son el tramo del corredor al que se recorta la ventana
// de cada evento: la misma restriccion sobre el eje x para todos.
Experiment readExperiment(const std::string& trajectories, const std::string& table,
                          const std::vector<int>& labels, double xMin, double xMax);
