#pragma once

#include "arguments.hpp"
#include "experiment.hpp"
#include "model.hpp"

// Los parametros del SFM (los del paper, salvo el radio que fija el enunciado)
// y los datos experimentales, leidos de la linea de comandos. Los comparten
// los cuatro comandos.
#include "avoidance.hpp"

Model modelFromArguments(const Arguments& arguments);
// La variante de la capa (--capa) y sus dos interruptores (--sin-rampa,
// --mira-horizonte); p1 y p2 los pone cada comando.
void configureLayer(Avoidance& layer, const Arguments& arguments);
Experiment experimentFromArguments(const Arguments& arguments);
