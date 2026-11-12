"""Item a: las trayectorias de unos pocos eventos representativos, juntas.

Una sola figura con un panel por evento (cuatro por omision), todos con los
mismos ejes y escala igual en x e y: en cada uno, las dos trayectorias medidas
(trazo lleno) y las dos simuladas con la capa calibrada (trazo cortado), y de
fondo la simulacion con la capa apagada (punteada gris). Cada panel lleva el
numero del evento y por que se lo eligio.

Los cuatro que se muestran cuentan cuatro cosas distintas:

* el que mas gana con la capa;
* el cruce mas ajustado que se midio (menor distancia minima);
* el cruce mas holgado (mayor distancia minima): el modelo pasa mas cerca que
  las personas, porque la distancia de paso es la misma para todos;
* el unico en el que el modelo elude por el lado opuesto.

    python3 visualization/representative.py --eventos 10 5 14 17
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import common

REASON = {
    0: "el que más gana con la capa",
    1: "el cruce medido más ajustado",
    2: "el cruce medido más holgado",
    3: "elude por el lado opuesto",
}


def minimum(track) -> float:
    return float(np.hypot(track[:, 0, 0] - track[:, 1, 0],
                          track[:, 0, 1] - track[:, 1, 1]).min())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs", type=Path, default=common.RUNS / "optimo-metrica1")
    parser.add_argument("--sin-capa", type=Path, default=common.RUNS / "sin-capa")
    parser.add_argument("--eventos", type=int, nargs="+", default=[10, 5, 14, 17])
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    count = len(arguments.eventos)
    rows = (count + 1) // 2
    figure, grid = plt.subplots(rows, 2, sharex=True, sharey=True,
                                figsize=(11.0, 2.0 * rows + 0.7))
    panels = np.atleast_2d(grid).ravel()
    small = matplotlib.rcParams["legend.fontsize"]
    for index, (axes, label) in enumerate(zip(panels, arguments.eventos)):
        static, _, simulated, experimental = common.load_run(arguments.runs / f"m{label}")
        _, _, plain, _ = common.load_run(arguments.sin_capa / f"m{label}")
        for side in (0, 1):
            axes.plot(plain[:, side, 0], plain[:, side, 1], color="#9aa3ad", linewidth=1.4,
                      linestyle=":", label="simulada sin capa" if side == 0 else None)
            axes.plot(experimental[:, side, 0], experimental[:, side, 1],
                      color=common.EXPERIMENT_COLOR[side], linewidth=2.2,
                      label="medida" if side == 0 else None)
            axes.plot(simulated[:, side, 0], simulated[:, side, 1],
                      color=common.EXPERIMENT_COLOR[side], linewidth=1.8, linestyle="--",
                      label="simulada con la capa" if side == 0 else None)
        axes.set_aspect("equal")
        axes.set_ylim(1.05, 3.25)
        axes.set_yticks([1.5, 2.0, 2.5])
        axes.text(0.015, 0.95, f"evento {label}: {REASON.get(index, '')}",
                  transform=axes.transAxes, va="top", fontsize=small, color="#1a1a1a")
        print(f"evento {label}: Nm = {static['instantes']}, distancia minima medida "
              f"{minimum(experimental[:, :, :2]):.2f} m, simulada "
              f"{minimum(simulated[:, :, :2]):.2f} m, sin capa {minimum(plain[:, :, :2]):.2f} m")
    for axes in panels[count:]:
        axes.set_visible(False)
    for axes in panels[-2:]:
        axes.set_xlabel(common.AXIS_X)
    for axes in panels[::2]:
        axes.set_ylabel(common.AXIS_Y)
    handles, names = panels[0].get_legend_handles_labels()
    order = [1, 2, 0]
    legend = figure.legend([handles[k] for k in order], [names[k] for k in order],
                           loc="upper center", ncol=3, fontsize=small, frameon=False,
                           bbox_to_anchor=(0.5, 1.0))
    for line in legend.get_lines():
        line.set_color("#1a1a1a")
    figure.tight_layout(rect=(0, 0, 1, 0.93), h_pad=0.2)
    common.save(figure, common.folder("a", arguments.figures) /
                f"trayectorias_representativas_{arguments.estilo}.png")
    plt.close(figure)


if __name__ == "__main__":
    main()
