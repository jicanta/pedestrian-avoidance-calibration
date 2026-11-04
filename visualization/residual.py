"""De donde viene el error que queda despues de calibrar.

Tres miradas sobre los 19 eventos con los parametros poblacionales del item b:

1. `poblaciones`: los eventos son de dos clases, que se separan solas por el
   angulo entre la velocidad inicial medida y el camino nominal (del arranque
   al target final): en unos los dos peatones ya caminan por el corredor
   (angulo < 32 grados) y en otros al menos uno todavia esta saliendo de la
   fila, perpendicular al corredor (> 60 grados). En los segundos la linea
   recta al target es la ruta equivocada, y eso no lo decide la capa de
   elusion: es la condicion que el enunciado fija para el target.
2. `descomposicion`: el apartamiento de cada instante abierto en la direccion
   del camino nominal (ritmo: el agente camina a vd constante y la persona
   acelera y frena) y en la perpendicular (forma: cuanto se corrio, que es lo
   que la capa decide). Promediadas en el tiempo las dos suman exactamente el
   E(1) del evento. Para los eventos de la fila la componente longitudinal
   tambien lleva la ruta, no solo el ritmo, asi que la figura los separa.
3. `lado`: el desvio lateral entre los dos peatones en el instante de minima
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


def grouped_positions(labels, kinds, values):
    """Posiciones de las barras: primero los eventos del corredor y despues
    los de la fila, cada grupo ordenado de mayor a menor, con un hueco."""
    order, positions, boundary = [], [], None
    offset = 0
    for kind in ("corredor", "fila"):
        members = [k for k in range(len(labels)) if kinds[k] == kind]
        members.sort(key=lambda k: -values[k])
        order.extend(members)
        positions.extend(offset + np.arange(len(members)))
        offset += len(members) + 1
        if kind == "corredor":
            boundary = offset - 1
    return np.array(order), np.array(positions), boundary


def populations(labels, kinds, metric, errors, figures, style):
    """E_m con los parametros poblacionales, agrupado por clase, con el
    promedio de cada clase."""
    common.use_style(style)
    order, positions, boundary = grouped_positions(labels, kinds, errors)
    figure, axes = plt.subplots()
    for kind in ("corredor", "fila"):
        members = [k for k in order if kinds[k] == kind]
        where = [positions[list(order).index(k)] for k in members]
        mean = float(np.mean([errors[k] for k in members]))
        axes.bar(where, [errors[k] for k in members], color=common.CLASS_COLOR[kind],
                 label=f"{common.CLASS_LABEL[kind]} ({len(members)}), promedio "
                       f"{common.decimal(mean, 2)} m$^2$")
        axes.hlines(mean, min(where) - 0.4, max(where) + 0.4, color=common.CLASS_COLOR[kind],
                    linestyle="--", linewidth=1.8)
    axes.axvline(boundary, color="#6e7680", linewidth=1.0, linestyle=":")
    axes.set_xticks(positions)
    axes.set_xticklabels([str(int(labels[k])) for k in order])
    axes.tick_params(axis="x", labelsize=matplotlib.rcParams["xtick.labelsize"] - 3)
    axes.set_xlabel(common.AXIS_EVENT)
    axes.set_ylabel(common.METRIC_EVENT[metric])
    common.legend_inside(axes)
    common.save(figure, common.folder("c", figures) /
                f"residuo_poblaciones_metrica{metric}_{style}.png")
    plt.close(figure)


def breakdown(labels, kinds, parts, figures, style):
    common.use_style(style)
    order, positions, boundary = grouped_positions(labels, kinds, parts.sum(axis=1))
    figure, axes = plt.subplots()
    axes.bar(positions, parts[order, 0], color=common.EXPERIMENT_COLOR[1],
             label="a lo largo del camino nominal")
    axes.bar(positions, parts[order, 1], bottom=parts[order, 0],
             color=common.EXPERIMENT_COLOR[0], label="perpendicular (forma)")
    axes.axvline(boundary, color="#6e7680", linewidth=1.0, linestyle=":")
    axes.set_xticks(positions)
    axes.set_xticklabels([str(int(labels[k])) for k in order])
    axes.tick_params(axis="x", labelsize=matplotlib.rcParams["xtick.labelsize"] - 3)
    axes.set_xlabel(common.AXIS_EVENT)
    axes.set_ylabel(common.AXIS_EM1)
    common.legend_inside(axes, loc="upper left")
    # Los rotulos de las dos poblaciones, a media altura: encima de las barras
    # del corredor (bajas) y, a la derecha, encima de las ultimas de la fila.
    top = axes.get_ylim()[1]
    axes.text(boundary - 0.6, 0.58 * top, "ya en el corredor", ha="right", va="center",
              color="#6e7680", fontsize=matplotlib.rcParams["legend.fontsize"])
    axes.text(positions.max() + 0.4, 0.58 * top, "sale de la fila", ha="right", va="center",
              color="#6e7680", fontsize=matplotlib.rcParams["legend.fontsize"])
    common.save(figure, common.folder("c", figures) / f"residuo_descomposicion_{style}.png")
    plt.close(figure)


def sides(labels, kinds, offsets, figures, style):
    common.use_style(style)
    figure, axes = plt.subplots()
    agree = np.sign(offsets[:, 0]) == np.sign(offsets[:, 1])
    limit = 1.1 * np.abs(offsets).max()
    axes.axhspan(0, limit, xmin=0.0, xmax=0.5, color="#d62728", alpha=0.07)
    axes.axhspan(-limit, 0, xmin=0.5, xmax=1.0, color="#d62728", alpha=0.07)
    for kind, marker in (("corredor", "o"), ("fila", "s")):
        pick = kinds == kind
        axes.plot(offsets[pick & agree, 0], offsets[pick & agree, 1], linestyle="none",
                  marker=marker, color=common.CLASS_COLOR[kind], markersize=8,
                  label=f"{common.CLASS_LABEL[kind]}: mismo lado "
                        f"({int((pick & agree).sum())} de {int(pick.sum())})")
        axes.plot(offsets[pick & ~agree, 0], offsets[pick & ~agree, 1], linestyle="none",
                  marker=marker, markerfacecolor="none", markeredgewidth=2.0,
                  color=common.CLASS_COLOR[kind], markersize=9,
                  label="lado opuesto" if kind == "corredor" else None)
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
    parser.add_argument("--runs2", type=Path, default=common.RUNS / "optimo-metrica2",
                        help="las corridas con el optimo de la metrica 2, para su figura de poblaciones")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    folders = sorted(Path(arguments.runs).glob("m*"), key=lambda path: int(path.name[1:]))
    statics = [common.read_static(path) for path in folders]
    labels = np.array([static["evento"] for static in statics])
    events = common.read_events()
    kinds = common.classes(labels, events)
    parts = np.array([decompose(path) for path in folders])
    offsets = np.array([crossing_offset(path) for path in folders])
    total = parts.sum(axis=1)

    populations(labels, kinds, 1, total, arguments.figures, arguments.estilo)
    folders2 = sorted(Path(arguments.runs2).glob("m*"), key=lambda path: int(path.name[1:]))
    if folders2:
        errors2 = []
        for path in folders2:
            _, _, simulated, experimental = common.load_run(path)
            values = [np.nanmean(common.metric_errors(experimental[:, side], simulated[:, side])[1])
                      for side in (0, 1)]
            errors2.append(float(np.mean(values)))
        populations(labels, kinds, 2, np.array(errors2), arguments.figures, arguments.estilo)
    breakdown(labels, kinds, parts, arguments.figures, arguments.estilo)
    agree = sides(labels, kinds, offsets, arguments.figures, arguments.estilo)

    print("angulo inicial (grados) entre v(0) y el camino nominal, por peaton:")
    for event in events:
        a, b = common.initial_angles(event)
        print(f"  m = {event['m']:2d}: {a:5.1f} {b:5.1f}  -> {common.event_class(event)}")
    for kind in ("corredor", "fila"):
        pick = kinds == kind
        print(f"\n{common.CLASS_LABEL[kind]}: {int(pick.sum())} eventos "
              f"({', '.join(str(int(label)) for label in labels[pick])})")
        print(f"  <E(1)> = {total[pick].mean():.3f} m2 = {parts[pick, 0].mean():.3f} a lo "
              f"largo + {parts[pick, 1].mean():.3f} perpendicular "
              f"({100 * parts[pick, 0].mean() / total[pick].mean():.0f} % y "
              f"{100 * parts[pick, 1].mean() / total[pick].mean():.0f} %)")
        if folders2:
            print(f"  <E(2)> = {np.array(errors2)[pick].mean():.3f} m2")
        print(f"  mismo lado que las personas: {int((pick & agree).sum())} de {int(pick.sum())}")
    print(f"\ntodos: <E(1)> = {total.mean():.4f} m2 = {parts[:, 0].mean():.4f} + "
          f"{parts[:, 1].mean():.4f}; mismo lado en {int(agree.sum())} de {len(labels)}")
    print("\n  m  clase     E1     largo  perp   dy_medido dy_simulado  lado")
    for label, kind, (a, b), (dy, ds) in zip(labels, kinds, parts, offsets):
        print(f"{int(label):3d}  {kind:8s} {a + b:6.3f} {a:6.3f} {b:6.3f}   {dy:+8.2f} "
              f"{ds:+10.2f}   {'=' if np.sign(dy) == np.sign(ds) else 'X'}")


if __name__ == "__main__":
    main()
