"""Item c: calibracion individual.

Para cada evento m se busca el par (p1_m, p2_m) que minimiza su propio error
E_m, con cada metrica por separado, sobre la misma grilla del item b. Dos
figuras por metrica:

* `optimos`: los M optimos individuales en el plano (p1, p2), con el optimo
  poblacional marcado. Cada punto lleva el numero de su evento.
* `errores`: el error de cada evento con los parametros POBLACIONALES y con
  los suyos propios, evento por evento y ordenados, mas los dos promedios.
  La diferencia entre los dos promedios es lo que se gana al individualizar.

Por consola sale la dispersion de los optimos individuales y cuanto baja el
error poblacional al individualizar, que es lo que el item pide discutir.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import common


def individual_optima(p1, p2, event_error):
    """Por evento: (p1_m, p2_m, E_m con los suyos, E_m con los poblacionales)."""
    mean, _ = common.population(event_error)
    i, j = np.unravel_index(np.argmin(mean), mean.shape)
    rows = []
    for k in range(event_error.shape[2]):
        a, b = np.unravel_index(np.argmin(event_error[:, :, k]), event_error.shape[:2])
        rows.append((p1[a], p2[b], event_error[a, b, k], event_error[i, j, k]))
    return np.array(rows), (p1[i], p2[j])


def scatter(rows, best, labels, metric, p1, p2, figures, style):
    common.use_style(style)
    color, marker = common.METRIC_STYLE[metric]
    figure, axes = plt.subplots()
    axes.plot(rows[:, 0], rows[:, 1], linestyle="none", marker=marker, color=color,
              markersize=8, alpha=0.8, label="óptimo de cada evento")
    # Varios eventos caen en el mismo par (o casi): una etiqueta por cumulo
    # con todos sus numeros, para que no se pisen.
    groups: dict[tuple[float, float], list[int]] = {}
    for (a, b, _, _), label in zip(rows, labels):
        key = (round(a / 0.25) * 0.25, round(b / 0.06) * 0.06)
        groups.setdefault(key, []).append(int(label))
    for (a, b), members in groups.items():
        text = ", ".join(str(member) for member in sorted(members))
        axes.annotate(text, (a, b), textcoords="offset points",
                      xytext=(-6 if a > 0.8 * p1.max() else 6, 5),
                      ha="right" if a > 0.8 * p1.max() else "left",
                      fontsize=matplotlib.rcParams["legend.fontsize"] - 2, color="#6e7680")
    axes.plot([best[0]], [best[1]], marker="*", color="#2ca02c", markersize=18,
              linestyle="none", markeredgecolor="#1a1a1a", markeredgewidth=0.8,
              label=f"poblacional $({common.decimal(best[0], 2)}$ s$,\\ "
                    f"{common.decimal(best[1], 3)}$ m$)$")
    axes.set_xlabel(common.AXIS_P1)
    axes.set_ylabel(common.AXIS_P2)
    axes.set_xlim(p1.min() - 0.1, p1.max() + 0.1)
    axes.set_ylim(p2.min() - 0.02, p2.max() + 0.02)
    common.legend_inside(axes, loc="upper left")
    common.save(figure, common.folder("c", figures) / f"optimos_metrica{metric}_{style}.png")
    plt.close(figure)


def comparison(rows, labels, metric, figures, style):
    common.use_style(style)
    order = np.argsort(rows[:, 3])
    positions = np.arange(len(order))
    figure, axes = plt.subplots()
    axes.bar(positions - 0.2, rows[order, 3], width=0.4, color=common.EXPERIMENT_COLOR[1],
             label="parámetros poblacionales")
    axes.bar(positions + 0.2, rows[order, 2], width=0.4, color=common.EXPERIMENT_COLOR[0],
             label="parámetros individuales")
    axes.axhline(rows[:, 3].mean(), color=common.EXPERIMENT_COLOR[1], linestyle="--",
                 linewidth=1.6,
                 label=f"promedio poblacional {common.decimal(rows[:, 3].mean(), 2)} m$^2$")
    axes.axhline(rows[:, 2].mean(), color=common.EXPERIMENT_COLOR[0], linestyle=":",
                 linewidth=1.8,
                 label=f"promedio individual {common.decimal(rows[:, 2].mean(), 2)} m$^2$")
    axes.set_xticks(positions)
    axes.set_xticklabels([str(int(labels[k])) for k in order])
    axes.tick_params(axis="x", labelsize=matplotlib.rcParams["xtick.labelsize"] - 3)
    axes.set_xlabel(common.AXIS_EVENT)
    axes.set_ylabel(common.METRIC_EVENT[metric])
    common.legend_inside(axes, ncol=2)
    common.save(figure, common.folder("c", figures) / f"errores_metrica{metric}_{style}.png")
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--barrido", type=Path, default=common.SWEEP / "fino" / "errores.txt")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    p1, p2, labels, error1, error2 = common.read_sweep(arguments.barrido)
    for metric, event_error in ((1, error1), (2, error2)):
        rows, best = individual_optima(p1, p2, event_error)
        scatter(rows, best, labels, metric, p1, p2, arguments.figures, arguments.estilo)
        comparison(rows, labels, metric, arguments.figures, arguments.estilo)
        gain = 100 * (1 - rows[:, 2].mean() / rows[:, 3].mean())
        print(f"\n{common.METRIC_LABEL[metric]}")
        print(f"  poblacional: p1 = {best[0]:.2f} s, p2 = {best[1]:.3f} m")
        print(f"  individuales: p1 mediana {np.median(rows[:, 0]):.2f} s "
              f"(de {rows[:, 0].min():.2f} a {rows[:, 0].max():.2f}), "
              f"p2 mediana {np.median(rows[:, 1]):.3f} m "
              f"(de {rows[:, 1].min():.3f} a {rows[:, 1].max():.3f})")
        print(f"  eventos con p1_m = 0 (la capa no les sirve): "
              f"{int((rows[:, 0] == 0).sum())} de {len(rows)}")
        edge = (rows[:, 0] >= p1.max() - 1e-9) | (rows[:, 1] >= p2.max() - 1e-9)
        print(f"  optimos en el borde de la grilla (p1 = {p1.max():g} s o p2 = {p2.max():g} m): "
              f"{int(edge.sum())} de {len(rows)}, eventos "
              f"{', '.join(str(int(labels[k])) for k in np.where(edge)[0])}")
        print(f"  <E_m> poblacional {rows[:, 3].mean():.4f} m2, individual "
              f"{rows[:, 2].mean():.4f} m2: individualizar gana {gain:.1f} %")
        print(f"  el evento que mas gana: m = {int(labels[np.argmax(rows[:, 3] - rows[:, 2])])} "
              f"({rows[:, 3].max():.2f} -> "
              f"{rows[np.argmax(rows[:, 3] - rows[:, 2]), 2]:.2f} m2)")


if __name__ == "__main__":
    main()
