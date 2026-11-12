"""Item c: calibracion individual.

Para cada evento m se busca el par (p1_m, p2_m) que minimiza su propio error
E_m, con cada metrica por separado, sobre la misma grilla del item b. Dos
figuras por metrica:

* `optimos`: el histograma de los M optimos individuales de cada parametro
  (un panel para p1 y otro para p2), con una linea vertical en el optimo
  poblacional (global).
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
from matplotlib.ticker import MaxNLocator
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


def histogram_panel(axes, values, edges, best, label, unit, digits, ylabel):
    """Histograma de un parametro, con la linea vertical del optimo global."""
    axes.hist(values, bins=edges, color=common.EXPERIMENT_COLOR[0], alpha=0.85,
              edgecolor="white", linewidth=0.8)
    axes.axvline(best, color=common.GLOBAL_COLOR, linestyle="--", linewidth=2.4,
                 label=f"óptimo global, ${common.decimal(best, digits)}$ {unit}")
    axes.set_xlabel(label)
    axes.set_ylabel(ylabel)
    axes.set_xlim(edges[0], edges[-1])
    axes.yaxis.set_major_locator(MaxNLocator(integer=True))
    axes.legend(loc="upper center", fontsize=plt.rcParams["legend.fontsize"])


def histograms(rows, best, metric, p1, p2, figures, style):
    """Distribucion de los M optimos individuales, un panel por parametro, con
    el optimo poblacional (global) marcado con una linea vertical."""
    common.use_style(style)
    figure, axesrow = plt.subplots(1, 2, figsize=(10.0, 4.0) if style == "informe"
                                   else (11.0, 4.2))
    histogram_panel(axesrow[0], rows[:, 0], np.linspace(p1.min(), p1.max(), 17), best[0],
                    common.AXIS_P1, "s", 2, common.AXIS_COUNT)
    histogram_panel(axesrow[1], rows[:, 1], np.linspace(p2.min(), p2.max(), 16), best[1],
                    common.AXIS_P2, "m", 2, common.AXIS_COUNT)
    figure.tight_layout()
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
                 label=f"promedio poblacional {common.decimal(rows[:, 3].mean(), 3)} m$^2$")
    axes.axhline(rows[:, 2].mean(), color=common.EXPERIMENT_COLOR[0], linestyle=":",
                 linewidth=1.8,
                 label=f"promedio individual {common.decimal(rows[:, 2].mean(), 3)} m$^2$")
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
        histograms(rows, best, metric, p1, p2, arguments.figures, arguments.estilo)
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
        gain_pair = rows[:, 3] - rows[:, 2]
        print(f"  ganancia pareada: {gain_pair.mean():.4f} +- "
              f"{gain_pair.std(ddof=1) / np.sqrt(len(gain_pair)):.4f} m2")
        print("  optimos por evento: " + "  ".join(
            f"{int(label)}:({a:.2f},{b:.2f})" for label, (a, b, _, _) in zip(labels, rows)))
        print(f"  el evento que mas gana: m = {int(labels[np.argmax(rows[:, 3] - rows[:, 2])])} "
              f"({rows[:, 3].max():.2f} -> "
              f"{rows[np.argmax(rows[:, 3] - rows[:, 2]), 2]:.2f} m2)")


if __name__ == "__main__":
    main()
