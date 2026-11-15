"""Item a: el evento que mejor ajusta, el que peor ajusta y uno sin la capa.

Una sola figura con tres paneles, todos con los mismos ejes y escala igual en
x e y (es lo que pidio la catedra el 13/11: "la trayectoria con mayor error,
la con menor error y una sin la capa de elusion"):

* el evento de MENOR error con la capa calibrada;
* el evento de MAYOR error con la capa calibrada;
* un evento simulado SIN la capa (el principal, el de las animaciones).

En cada panel van las dos trayectorias medidas (trazo lleno) y las dos
simuladas (trazo cortado). El mejor y el peor no se eligen a mano: salen de
E_m de la metrica pedida, recalculada aca desde las corridas con cuadros. Con
--excluir 1 el evento 1 no compite por el menor error: su ventana termina
poco despues del cruce (se pierde el seguimiento de un peaton) y por eso
acumula menos error que los demas, no porque ajuste mejor.

    python3 visualization/representative.py --sin-capa-evento 10
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import common


def minimum(track) -> float:
    return float(np.hypot(track[:, 0, 0] - track[:, 1, 0],
                          track[:, 0, 1] - track[:, 1, 1]).min())


def event_error(run: Path, metric: int) -> float:
    """E_m de una corrida: el promedio sobre los 2 peatones del promedio
    temporal del observable primario."""
    _, _, simulated, experimental = common.load_run(run)
    return float(np.mean([np.nanmean(common.metric_errors(experimental[:, side],
                                                          simulated[:, side])[metric - 1])
                          for side in (0, 1)]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs", type=Path, default=common.RUNS / "optimo-metrica1")
    parser.add_argument("--sin-capa", type=Path, default=common.RUNS / "sin-capa")
    parser.add_argument("--sin-capa-evento", type=int, default=10,
                        help="el evento que se muestra simulado sin la capa")
    parser.add_argument("--metrica", type=int, choices=(1, 2), default=1)
    parser.add_argument("--excluir", type=int, nargs="*", default=[],
                        help="eventos que no compiten por el menor error (el 1, cuya "
                             "ventana es mas corta que las demas: acumula menos error)")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    folders = sorted(arguments.runs.glob("m*"), key=lambda path: int(path.name[1:]))
    errors = {int(path.name[1:]): event_error(path, arguments.metrica) for path in folders}
    best = min((label for label in errors if label not in arguments.excluir),
               key=errors.get)
    worst = max(errors, key=errors.get)
    plain = arguments.sin_capa_evento
    plain_error = event_error(arguments.sin_capa / f"m{plain}", arguments.metrica)
    symbol = f"$E^{{({arguments.metrica})}}_m$"
    print("E_m por evento, de menor a mayor: " + "  ".join(
        f"{label}:{value:.3f}" for label, value in sorted(errors.items(),
                                                          key=lambda item: item[1])))

    panels_data = (
        (best, arguments.runs, "con la capa, el de menor error", errors[best]),
        (worst, arguments.runs, "con la capa, el de mayor error", errors[worst]),
        (plain, arguments.sin_capa, "sin la capa de elusión", plain_error),
    )
    figure, grid = plt.subplots(2, 2, sharex=True, sharey=True, figsize=(11.0, 4.7))
    panels = grid.ravel()
    small = matplotlib.rcParams["legend.fontsize"]
    for axes, (label, runs, reason, error) in zip(panels, panels_data):
        static, _, simulated, experimental = common.load_run(runs / f"m{label}")
        for side in (0, 1):
            axes.plot(experimental[:, side, 0], experimental[:, side, 1],
                      color=common.EXPERIMENT_COLOR[side], linewidth=2.2)
            axes.plot(simulated[:, side, 0], simulated[:, side, 1],
                      color=common.EXPERIMENT_COLOR[side], linewidth=1.8, linestyle="--")
        axes.set_aspect("equal")
        axes.set_ylim(1.05, 3.25)
        axes.set_yticks([1.5, 2.0, 2.5])
        axes.text(0.015, 0.95, f"evento {label}: {reason}", transform=axes.transAxes,
                  va="top", fontsize=small, color="#1a1a1a")
        axes.text(0.985, 0.06, f"{symbol} $= {common.math_decimal(error, 3)}$ m$^2$",
                  transform=axes.transAxes, va="bottom", ha="right", fontsize=small,
                  color="#1a1a1a")
        print(f"evento {label} ({reason}): Nm = {static['instantes']}, E_m = {error:.4f} m2, "
              f"distancia minima medida {minimum(experimental[:, :, :2]):.2f} m, simulada "
              f"{minimum(simulated[:, :, :2]):.2f} m")

    # El cuarto lugar de la grilla es la leyenda.
    legend_axes = panels[3]
    legend_axes.axis("off")
    handles = [
        plt.Line2D([], [], color="#1a1a1a", linewidth=2.2, label="medida"),
        plt.Line2D([], [], color="#1a1a1a", linewidth=1.8, linestyle="--", label="simulada"),
        plt.Line2D([], [], color=common.EXPERIMENT_COLOR[0], linewidth=2.2,
                   label="sale por la izquierda"),
        plt.Line2D([], [], color=common.EXPERIMENT_COLOR[1], linewidth=2.2,
                   label="sale por la derecha"),
    ]
    legend_axes.legend(handles=handles, loc="center", fontsize=small, frameon=False)
    panels[1].tick_params(labelbottom=True)
    panels[1].set_xlabel(common.AXIS_X)
    panels[2].set_xlabel(common.AXIS_X)
    panels[0].set_ylabel(common.AXIS_Y)
    panels[2].set_ylabel(common.AXIS_Y)
    figure.tight_layout(h_pad=0.4)
    common.save(figure, common.folder("a", arguments.figures) /
                f"trayectorias_representativas_{arguments.estilo}.png")
    plt.close(figure)


if __name__ == "__main__":
    main()
