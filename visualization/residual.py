"""De donde viene el error que queda despues de calibrar.

Dos miradas sobre los 19 eventos con los parametros poblacionales del item b:

1. `descomposicion`: el apartamiento de cada instante abierto en la direccion
   del camino nominal (ritmo: el agente camina a vd constante y la persona
   acelera y frena) y en la perpendicular (forma: cuanto se corrio, que es lo
   que la capa decide). Promediadas en el tiempo las dos suman exactamente el
   E(1) del evento.
2. `lado`: el desvio lateral entre los dos peatones en el instante de minima
   aproximacion, medido contra simulado. Si tienen el mismo signo, el modelo
   eludio por el mismo lado que las personas.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import common


def decompose(run: Path):
    """(E_long, E_trans) del evento, promediando sus dos peatones."""
    static, time, simulated, experimental = common.load_run(run)
    longitudinal, transverse = [], []
    for side, name in ((0, "izquierda"), (1, "derecha")):
        start = np.array(static[f"{name}_inicio"])
        target = np.array(static[f"{name}_target"])
        direction = (target - start) / np.linalg.norm(target - start)
        normal = np.array([-direction[1], direction[0]])
        present = experimental[:, side, 2] > 0.5
        difference = experimental[present, side, :2] - simulated[present, side, :2]
        longitudinal.append(float(np.mean((difference @ direction) ** 2)))
        transverse.append(float(np.mean((difference @ normal) ** 2)))
    return float(np.mean(longitudinal)), float(np.mean(transverse))


def crossing_offset(run: Path):
    """Desvio lateral y_izq - y_der en el instante de minima aproximacion,
    medido y simulado."""
    _, _, simulated, experimental = common.load_run(run)
    both = (experimental[:, 0, 2] > 0.5) & (experimental[:, 1, 2] > 0.5)
    measured = np.hypot(experimental[:, 0, 0] - experimental[:, 1, 0],
                        experimental[:, 0, 1] - experimental[:, 1, 1])
    measured[~both] = np.inf
    computed = np.hypot(simulated[:, 0, 0] - simulated[:, 1, 0],
                        simulated[:, 0, 1] - simulated[:, 1, 1])
    k = int(np.argmin(measured))
    n = int(np.argmin(computed))
    return (experimental[k, 0, 1] - experimental[k, 1, 1],
            simulated[n, 0, 1] - simulated[n, 1, 1])


def breakdown(labels, parts, figures, style):
    common.use_style(style)
    order = np.argsort(-parts.sum(axis=1))
    positions = np.arange(len(order))
    figure, axes = plt.subplots()
    axes.bar(positions, parts[order, 0], color=common.EXPERIMENT_COLOR[1],
             label="a lo largo del camino nominal (ritmo)")
    axes.bar(positions, parts[order, 1], bottom=parts[order, 0],
             color=common.EXPERIMENT_COLOR[0], label="perpendicular (forma)")
    axes.set_xticks(positions)
    axes.set_xticklabels([str(int(labels[k])) for k in order])
    axes.tick_params(axis="x", labelsize=matplotlib.rcParams["xtick.labelsize"] - 3)
    axes.set_xlabel(common.AXIS_EVENT)
    axes.set_ylabel(common.AXIS_EM1)
    common.legend_inside(axes)
    common.save(figure, common.folder("c", figures) / f"residuo_descomposicion_{style}.png")
    plt.close(figure)


def sides(labels, offsets, figures, style):
    common.use_style(style)
    figure, axes = plt.subplots()
    agree = np.sign(offsets[:, 0]) == np.sign(offsets[:, 1])
    limit = 1.1 * np.abs(offsets).max()
    axes.axhspan(0, limit, xmin=0.0, xmax=0.5, color="#d62728", alpha=0.07)
    axes.axhspan(-limit, 0, xmin=0.5, xmax=1.0, color="#d62728", alpha=0.07)
    axes.plot(offsets[agree, 0], offsets[agree, 1], linestyle="none", marker="o",
              color=common.EXPERIMENT_COLOR[0], markersize=8,
              label="mismo lado")
    if (~agree).any():
        axes.plot(offsets[~agree, 0], offsets[~agree, 1], linestyle="none", marker="o",
                  markerfacecolor="none", markeredgewidth=2.0,
                  color=common.EXPERIMENT_COLOR[1], markersize=9,
                  label="lado opuesto")
    axes.plot([-limit, limit], [-limit, limit], color="#6e7680", linestyle=":",
              linewidth=1.4, label="simulado = medido")
    axes.axhline(0.0, color="#1a1a1a", linewidth=1.0)
    axes.axvline(0.0, color="#1a1a1a", linewidth=1.0)
    axes.set_xlim(-limit, limit)
    axes.set_ylim(-limit, limit)
    axes.set_xlabel("$\\Delta y$ medido en el cruce (m)")
    axes.set_ylabel("$\\Delta y$ simulado en el cruce (m)")
    axes.legend(loc="lower right", fontsize=matplotlib.rcParams["legend.fontsize"])
    common.save(figure, common.folder("c", figures) / f"residuo_lado_{style}.png")
    plt.close(figure)
    return agree


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=common.RUNS / "optimo-metrica1")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    folders = sorted(Path(arguments.runs).glob("m*"), key=lambda path: int(path.name[1:]))
    statics = [common.read_static(path) for path in folders]
    labels = np.array([static["evento"] for static in statics])
    parts = np.array([decompose(path) for path in folders])
    offsets = np.array([crossing_offset(path) for path in folders])
    total = parts.sum(axis=1)

    breakdown(labels, parts, arguments.figures, arguments.estilo)
    agree = sides(labels, offsets, arguments.figures, arguments.estilo)

    print(f"<E(1)> = {total.mean():.4f} m2 = {parts[:, 0].mean():.4f} a lo largo + "
          f"{parts[:, 1].mean():.4f} perpendicular "
          f"({100 * parts[:, 0].mean() / total.mean():.0f} % y "
          f"{100 * parts[:, 1].mean() / total.mean():.0f} %)")
    print(f"mismo lado que las personas en {int(agree.sum())} de {len(labels)} eventos")
    right = int((offsets[:, 0] < 0).sum())
    print(f"las personas pasaron cada una por su derecha (dy medido < 0) en {right} de "
          f"{len(labels)}")
    amplitude = np.abs(offsets)
    print(f"|dy| en el cruce: medido {amplitude[:, 0].mean():.2f} m en promedio "
          f"(de {amplitude[:, 0].min():.2f} a {amplitude[:, 0].max():.2f}), simulado "
          f"{amplitude[:, 1].mean():.2f} (de {amplitude[:, 1].min():.2f} a "
          f"{amplitude[:, 1].max():.2f})")
    print("\n  m     E1     largo  perp   dy_medido dy_simulado  lado")
    for label, (a, b), (dy, ds) in zip(labels, parts, offsets):
        print(f"{int(label):3d}  {a + b:6.3f} {a:6.3f} {b:6.3f}   {dy:+8.2f} "
              f"{ds:+10.2f}   {'=' if np.sign(dy) == np.sign(ds) else 'X'}")


if __name__ == "__main__":
    main()
