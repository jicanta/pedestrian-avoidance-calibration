#include <exception>
#include <iostream>

#include "commands.hpp"

namespace {

void printUsage() {
  std::cerr
      << "uso: elusion <comando> [opciones]\n\n"
      << "  events      [--datos experimental/elusion_1_contra_1.txt]\n"
      << "              [--eventos experimental/eventos.txt] [--pruebas 1,5,...]\n"
      << "              [--dir ../data/experimental]\n\n"
      << "  run         [--pruebas 5] [--p1 2] [--p2 0.4] [--subdivisiones 64]\n"
      << "              [--dir ../data/runs/prueba]\n\n"
      << "  sweep       [--p1 0:4:41] [--p2 0:0.8:41] [--subdivisiones 64]\n"
      << "              [--dir ../data/barrido]\n\n"
      << "  convergence [--p1 2] [--p2 0.4] [--subdivisiones 1,2,...,512]\n"
      << "              [--dir ../data/convergencia]\n\n"
      << "  Modelo: SFM sin fuerza social (Helbing, Farkas y Vicsek 2000) con los\n"
      << "  parametros del paper (--m 80 --tau 0.5 --kn 1.2e5 --kt 2.4e5) y el\n"
      << "  radio del enunciado (--r 0.25). La capa de elusion tiene exactamente\n"
      << "  dos parametros: --p1 el tiempo de anticipacion (s) y --p2 el margen de\n"
      << "  espacio personal (m); con --p1 0 la capa esta apagada y queda el SFM\n"
      << "  puro. --capa elige la variante: predictiva (la que corre), campo,\n"
      << "  campo-lateral o campo-predictivo (ver avoidance.hpp); en las de campo\n"
      << "  p1 es la ganancia A y p2 el alcance B en metros.\n"
      << "  La integracion es Beeman predictor-corrector y el paso se da en\n"
      << "  --subdivisiones, el numero entero de pasos por intervalo experimental:\n"
      << "  asi cada instante experimental cae exactamente en un paso.\n\n"
      << "  events verifica la lectura de los datos de la catedra: por cada evento\n"
      << "  escribe la ventana comun, las muestras de cada peaton y las\n"
      << "  condiciones que el enunciado fija a partir de su trayectoria (posicion\n"
      << "  y velocidad iniciales, target final y rapidez media).\n"
      << "  run escribe la salida primaria de una corrida (static.txt, dynamic.txt\n"
      << "  con el estado y el target de los dos agentes en cada instante\n"
      << "  experimental, y experimental.txt con las trayectorias medidas en la\n"
      << "  misma grilla); con --pruebas de varios eventos hace una carpeta por\n"
      << "  evento.\n"
      << "  sweep recorre la grilla de (p1, p2) y escribe las DOS metricas de los\n"
      << "  DOS peatones de cada evento en cada par. Las metricas se calculan en\n"
      << "  el motor porque son justamente lo que el barrido minimiza; el promedio\n"
      << "  poblacional, los optimos individuales y la validacion cruzada salen de\n"
      << "  ese archivo, en visualization/.\n"
      << "  convergence elige el paso de integracion.\n";
}

}

int main(int argc, char** argv) {
  try {
    const Arguments arguments(argc, argv);
    if (arguments.command() == "events") {
      return runEvents(arguments);
    }
    if (arguments.command() == "run") {
      return runSingle(arguments);
    }
    if (arguments.command() == "sweep") {
      return runSweep(arguments);
    }
    if (arguments.command() == "convergence") {
      return runConvergence(arguments);
    }
    printUsage();
    return 1;
  } catch (const std::exception& error) {
    std::cerr << "error: " << error.what() << "\n";
    return 1;
  }
}
