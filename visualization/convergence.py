"""Eleccion del paso de integracion (convergencia.txt de `elusion convergence`).

dt no es libre: tiene que dividir el intervalo experimental dtExp en un numero
entero n de partes, para que cada instante experimental sea exactamente un paso
de la simulacion y las dos trayectorias se comparen sin interpolar. La figura
muestra el error poblacional de las dos metricas contra dt, con el valor del
paso mas fino como referencia, y el tiempo de ejecucion del barrido completo.
El paso elegido es el mas largo cuyo <E> ya no se mueve mas de la tolerancia
respecto del mas fino.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import common


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--convergencia", type=Path,
                        default=common.CONVERGENCE / "convergencia.txt")
    parser.add_argument("--tolerancia", type=float, default=1e-4,
                        help="apartamiento relativo aceptado respecto del paso mas fino")
    parser.add_argument("--elegido", type=int, default=64,
                        help="subdivisiones con las que corre todo el trabajo")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    values = np.loadtxt(arguments.convergencia)
    subdivisions, step, mean1, mean2, milliseconds = values.T
    relative = {1: np.abs(mean1 / mean1[-1] - 1.0), 2: np.abs(mean2 / mean2[-1] - 1.0)}
    worst = np.maximum(relative[1], relative[2])
    accepted = np.where(worst <= arguments.tolerancia)[0]
    enough = int(subdivisions[accepted[0]]) if accepted.size else int(subdivisions[-1])
    chosen = arguments.elegido

    common.use_style(style := arguments.estilo)
    figure, axes = plt.subplots()
    # El paso mas fino es la referencia: su apartamiento es cero por definicion
    # y no entra en la curva (en escala logaritmica no se puede dibujar).
    shown = slice(0, len(step) - 1)
    for metric in (1, 2):
        color, marker = common.METRIC_STYLE[metric]
        axes.plot(step[shown], relative[metric][shown], marker=marker, color=color,
                  label=common.METRIC_LABEL[metric])
    axes.axhline(arguments.tolerancia, color="#6e7680", linestyle="--", linewidth=1.4,
                 label=f"tolerancia {common.decimal(100 * arguments.tolerancia)} %")
    index = int(np.argmin(np.abs(subdivisions - chosen)))
    axes.axvline(step[index], color="#2ca02c", linestyle=":", linewidth=1.8,
                 label=f"$\\Delta t$ elegido = $\\Delta t_{{exp}}/{chosen}$")
    axes.set_xscale("log")
    axes.set_yscale("log")
    axes.set_xlabel(common.AXIS_STEP)
    axes.set_ylabel("apartamiento relativo de $\\langle E \\rangle$")
    axes.set_title(f"referencia: $\\Delta t_{{exp}}/{int(subdivisions[-1])}$",
                   fontsize=matplotlib.rcParams["legend.fontsize"], color="#6e7680", loc="right")
    common.legend_inside(axes)
    common.save(figure, common.folder("a", arguments.figures) /
                f"convergencia_dt_{arguments.estilo}.png")
    plt.close(figure)

    print(f"la tolerancia del {100*arguments.tolerancia:g} % se cumple desde n = {enough} "
          f"(dt = {1e3/15.0192/enough:.2f} ms)")
    print(f"paso usado en todo el trabajo: dt = dt_exp/{chosen} = {step[index]*1e3:.2f} ms")
    for n, dt, e1, e2, ms, w in zip(subdivisions, step, mean1, mean2, milliseconds, worst):
        print(f"  n = {int(n):4d}  dt = {dt*1e3:7.3f} ms  <E1> = {e1:.5f}  <E2> = {e2:.5f}  "
              f"apartamiento {100*w:7.3f} %  {ms:7.1f} ms")


if __name__ == "__main__":
    main()
