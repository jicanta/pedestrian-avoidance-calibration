"""De donde viene el error que queda despues de calibrar.

Con los parametros poblacionales del item b, el apartamiento de cada instante
se descompone en la direccion del camino nominal del peaton (del arranque a su
target final) y en la perpendicular:

    |r_exp - r_sim|^2 = e_long^2 + e_trans^2

La componente longitudinal es error de RITMO: el agente camina a vd constante
y el peaton real acelera y frena. La transversal es error de FORMA: cuanto se
corrio de su camino, que es lo que la capa de elusion decide. Promediadas en
el tiempo, las dos suman exactamente el E^(1) del evento, asi que la figura es
el mismo escalar del item b abierto en sus dos causas.

La segunda figura mira el LADO: el desvio lateral entre los dos peatones en el
instante de minima aproximacion, medido contra simulado. Si los dos tienen el
mismo signo, el modelo eludio por el mismo lado que las personas.
"""

from __future__ import annotations

import argparse
from pathlib import Path

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
             label="ritmo (a lo largo del camino)")
    axes.bar(positions, parts[order, 1], bottom=parts[order, 0],
             color=common.EXPERIMENT_COLOR[0], label="forma (perpendicular)")
    axes.set_xticks(positions)
    axes.set_xticklabels([str(int(labels[k])) for k in order])
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
              label=f"mismo lado ({int(agree.sum())} eventos)")
    axes.plot(offsets[~agree, 0], offsets[~agree, 1], linestyle="none", marker="X",
              color=common.EXPERIMENT_COLOR[1], markersize=9,
              label=f"lado opuesto ({int((~agree).sum())} eventos)")
    for (a, b), label in zip(offsets, labels):
        axes.annotate(str(int(label)), (a, b), textcoords="offset points", xytext=(6, 4),
                      fontsize=10, color="#6e7680")
    axes.axhline(0.0, color="#1a1a1a", linewidth=1.0)
    axes.axvline(0.0, color="#1a1a1a", linewidth=1.0)
    axes.set_xlim(-limit, limit)
    axes.set_ylim(-limit, limit)
    axes.set_xlabel("$\\Delta y$ medido en el cruce (m)")
    axes.set_ylabel("$\\Delta y$ simulado en el cruce (m)")
    common.legend_inside(axes, loc="lower right")
    common.save(figure, common.folder("c", figures) / f"residuo_lado_{style}.png")
    plt.close(figure)
    return agree


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, default=common.RUNS / "optimo-metrica1")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    folders = sorted(Path(arguments.runs).glob("m*"),
                     key=lambda path: int(path.name[1:]))
    labels = np.array([common.read_static(path)["evento"] for path in folders])
    parts = np.array([decompose(path) for path in folders])
    offsets = np.array([crossing_offset(path) for path in folders])

    breakdown(labels, parts, arguments.figures, arguments.estilo)
    agree = sides(labels, offsets, arguments.figures, arguments.estilo)

    total = parts.sum(axis=1)
    print(f"con los parametros poblacionales de la metrica 1, sobre {len(labels)} eventos:")
    print(f"  <E(1)> = {total.mean():.4f} m2 = {parts[:, 0].mean():.4f} de ritmo + "
          f"{parts[:, 1].mean():.4f} de forma "
          f"({100 * parts[:, 0].mean() / total.mean():.0f} % y "
          f"{100 * parts[:, 1].mean() / total.mean():.0f} %)")
    print(f"  el modelo elude por el mismo lado que las personas en "
          f"{int(agree.sum())} de {len(labels)} eventos")
    print(f"  esos {int(agree.sum())} tienen <E(1)> = {total[agree].mean():.3f} m2; "
          f"los otros {int((~agree).sum())}, {total[~agree].mean():.3f} m2")
    print("\n  m   E1     ritmo  forma   dy_medido dy_simulado  lado")
    for label, (a, b), (dy, ds) in zip(labels, parts, offsets):
        print(f"{int(label):3d}  {a + b:6.3f} {a:6.3f} {b:6.3f}   {dy:+8.2f} {ds:+10.2f}"
              f"   {'=' if np.sign(dy) == np.sign(ds) else 'X'}")


if __name__ == "__main__":
    main()
