#include <exception>
#include <iostream>

#include "commands.hpp"

namespace {

void printUsage() {
  std::cerr
      << "uso: elusion <comando> [opciones]\n\n"
      << "  events      [--datos experimental/elusion_1_contra_1.txt]\n"
      << "              [--eventos experimental/eventos.txt] [--pruebas 1,5,...]\n"
      << "              [--xmin 1.0] [--xmax 7.7] [--dir ../data/experimental]\n\n"
      << "  run         [--pruebas 5] [--p1 2] [--p2 0.4] [--subdivisiones 64]\n"
      << "              [--dir ../data/runs/prueba]\n\n"
      << "  sweep       [--p1 0:4:41] [--p2 0:0.8:41] [--subdivisiones 64]\n"
      << "              [--dir ../data/barrido]\n\n"
      << "  asymmetry   [--p1 2.15] [--p2 0:0.6:61] [--alfas 0:1:41]\n"
      << "              [--subdivisiones 64] [--dir ../data/asimetria]\n\n"
      << "  pairs       [--p1 0:4:41] [--p2 0:0.6:31] [--subdivisiones 64]\n"
      << "              [--dir ../data/individual]\n\n"
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
      << "  La ventana de cada evento se recorta al tramo del corredor en que los\n"
      << "  dos peatones estan en --xmin <= x <= --xmax (las cabeceras de las dos\n"
      << "  filas estan en x = 0,6 m y x = 8,1 m); vale para todos los comandos.\n\n"
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
      << "  asymmetry deja t_a fijo en --p1 y recorre el par (d_s, alfa), con alfa\n"
      << "  la fraccion de la separacion que falta que se lleva el peaton de la\n"
      << "  izquierda (--alfa fija ese reparto en los otros comandos; 0,5 es la\n"
      << "  capa simetrica). Escribe el mismo archivo que sweep.\n"
      << "  pairs es el item 2 c) OPCIONAL: optimiza los parametros POR PEATON,\n"
      << "  cuatro numeros por evento en lugar de dos. Como los dos agentes estan\n"
      << "  acoplados (el error de uno depende de los parametros del otro) el\n"
      << "  minimo se busca en la grilla de los cuatro a la vez, G x G por evento;\n"
      << "  de la misma grilla sale tambien el optimo de dos parametros (la\n"
      << "  diagonal), que es con lo que se compara.\n"
      << "  Reparte las corridas en --hilos hilos (todos, por omision) y con\n"
      << "  --reanudar saltea los eventos que ya estan en pares.txt.\n"
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
    if (arguments.command() == "asymmetry") {
      return runAsymmetry(arguments);
    }
    if (arguments.command() == "pairs") {
      return runPairs(arguments);
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
