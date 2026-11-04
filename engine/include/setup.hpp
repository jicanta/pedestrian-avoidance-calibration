#pragma once

#include "arguments.hpp"
#include "experiment.hpp"
#include "model.hpp"

// Los parametros del SFM (los del paper, salvo el radio que fija el enunciado)
// y los datos experimentales, leidos de la linea de comandos. Los comparten
// los cuatro comandos.
Model modelFromArguments(const Arguments& arguments);
Experiment experimentFromArguments(const Arguments& arguments);
