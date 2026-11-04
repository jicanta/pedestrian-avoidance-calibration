#pragma once

#include <fstream>
#include <string>
#include <vector>

#include "arguments.hpp"
#include "avoidance.hpp"
#include "experiment.hpp"
#include "model.hpp"
#include "simulation.hpp"

// Crea la carpeta (y las que falten) donde se va a escribir la salida.
void makeDirectory(const std::string& path);

std::ofstream openOutput(const std::string& path);

// "desde:hasta:cantidad" -> la grilla de ese parametro. Con cantidad 1 queda
// solo `desde`. Es el formato de --p1 y --p2 del comando sweep.
std::vector<double> linearGrid(const std::string& name, const std::string& text);

// static.txt: "clave valor" por linea, los parametros de la corrida y las
// condiciones que el enunciado fija para cada peaton del evento.
void writeStatic(const std::string& path, const Event& event, const Model& model,
                 const Avoidance& layer, const Run& run, double sampling);

// dynamic.txt: por instante, una linea con t y dos lineas "x y vx vy tx ty
// conflicto", una por agente (tx ty es el target que la capa le puso).
void writeDynamic(const std::string& path, const Run& run);

// experimental.txt: por instante, una linea "t x1 y1 presente1 x2 y2 presente2"
// con las trayectorias medidas sobre la misma grilla temporal.
void writeExperimental(const std::string& path, const Event& event, const Run& run,
                       double sampling);
