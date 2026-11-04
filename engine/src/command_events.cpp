#include <iomanip>
#include <iostream>

#include "commands.hpp"
#include "io.hpp"
#include "setup.hpp"

// Resumen de los eventos experimentales tal como los arma el motor: la ventana
// comun, cuantas muestras tiene cada peaton, su rapidez media (que es el
// modulo de su velocidad deseada), su target final y la distancia minima
// medida. Es la tabla con la que se verifica la lectura de los datos contra el
// LEEME de la catedra, y la que lee la figura de los eventos.
int runEvents(const Arguments& arguments) {
  const Experiment experiment = experimentFromArguments(arguments);
  const std::string directory = arguments.text("dir", "../data/experimental");
  std::ofstream file = openOutput(directory + "/eventos_resumen.txt");

  file << "# framerate " << experiment.framerate << " dt_exp " << experiment.sampling
       << "\n"
       << "# m cuadro_inicial Nm duracion dmin "
       << "id_izq muestras_izq vd_izq camino_izq x0_izq y0_izq vx0_izq vy0_izq tx_izq ty_izq "
       << "id_der muestras_der vd_der camino_der x0_der y0_der vx0_der vy0_der tx_der ty_der\n";
  std::cout << std::fixed << std::setprecision(2);
  std::cout << "  m   Nm   dur  dmin   vd_izq vd_der  huecos\n";
  for (const Event& event : experiment.events) {
    file << event.label << " " << event.firstFrame << " " << event.instants << " "
         << event.duration << " " << event.minimumDistance;
    for (int i = 0; i < 2; ++i) {
      const Pedestrian& pedestrian = event.pedestrian(i);
      file << " " << pedestrian.id << " " << pedestrian.samples << " "
           << pedestrian.desiredSpeed << " " << pedestrian.pathLength << " "
           << pedestrian.start.x << " " << pedestrian.start.y << " "
           << pedestrian.initialVelocity.x << " " << pedestrian.initialVelocity.y << " "
           << pedestrian.target.x << " " << pedestrian.target.y;
    }
    file << "\n";
    std::cout << std::setw(3) << event.label << " " << std::setw(4) << event.instants << " "
              << std::setw(5) << event.duration << " " << std::setw(5)
              << event.minimumDistance << "   " << std::setw(6) << event.left.desiredSpeed
              << " " << std::setw(6) << event.right.desiredSpeed << "  "
              << std::setw(3) << event.instants - event.left.samples << "/"
              << event.instants - event.right.samples << "\n";
  }
  std::cout << experiment.events.size() << " eventos en " << directory
            << "/eventos_resumen.txt\n";
  return 0;
}
