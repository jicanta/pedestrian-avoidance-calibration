"""Item b: calibracion poblacional.

<E>(p1, p2) es el promedio sobre los M eventos del error de cada evento, que a
su vez es el promedio sobre sus 2 peatones. Para cada metrica por separado:

* el mapa de <E> sobre la grilla de parametros, con el optimo marcado;
* los dos cortes unidimensionales que pasan por el optimo, con sus barras de
  error;
* por consola, el optimo de cada metrica, la region compatible y la
  comparacion entre las dos metricas.

La barra de error de <E> es el error estandar de la media entre eventos,
sigma/sqrt(M). Para decidir que valores EMPATAN con el optimo (la franja verde
de los cortes) esa barra no sirve:
todos los pares se evaluan sobre los MISMOS M eventos, asi que lo que hay que
mirar es la diferencia pareada evento por evento. La region compatible es el
conjunto de pares cuya diferencia media contra el optimo, E_m(p) - E_m(p*), no
supera su propio error estandar.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors
from matplotlib.ticker import FuncFormatter
import numpy as np

import common


def compatible(event_error: np.ndarray, i: int, j: int) -> np.ndarray:
    """Pares que empatan con el optimo segun la diferencia pareada."""
    difference = event_error - event_error[i, j, :][None, None, :]
    spread = difference.std(axis=2, ddof=1) / np.sqrt(event_error.shape[2])
    return difference.mean(axis=2) <= spread


def surface(p1, p2, mean, metric, figures, style):
    """Mapa de <E> sobre la grilla, como los mapas de los TP anteriores: el
    color es <E>, en escala logaritmica (entre el SFM puro y el optimo hay un
    orden de magnitud), y lo unico que va encima es el optimo."""
    common.use_style(style)
    figure, axes = plt.subplots()
    axes.grid(False)
    mesh = axes.pcolormesh(p2, p1, mean, shading="nearest", cmap=common.heat_colormap(),
                           norm=colors.LogNorm(vmin=mean.min(), vmax=mean.max()))
    bar = figure.colorbar(mesh, ax=axes)
    bar.set_label(common.METRIC_AVERAGE[metric])
    bar.ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: common.decimal(value)))
    bar.ax.yaxis.set_minor_formatter(FuncFormatter(
        lambda value, _: common.decimal(value)
        if f"{value:.0e}"[0] in "25" else ""))
    bar.ax.tick_params(which="minor", labelsize=matplotlib.rcParams["ytick.labelsize"])
    i, j = np.unravel_index(np.argmin(mean), mean.shape)
    axes.plot(p2[j], p1[i], marker="*", color="white", markersize=18, linestyle="none",
              markeredgecolor="#1a1a1a", markeredgewidth=1.0,
              label=f"óptimo $({common.decimal(p1[i], 2)}$ s$,\\ {common.decimal(p2[j], 2)}$ m$)$")
    axes.set_xlabel(common.AXIS_P2)
    axes.set_ylabel(common.AXIS_P1)
    axes.legend(loc="upper right", framealpha=0.9,
                fontsize=matplotlib.rcParams["legend.fontsize"])
    common.save(figure, common.folder("b", figures) / f"superficie_metrica{metric}_{style}.png")
    plt.close(figure)


def cuts(p1, p2, event_error, region, metric, figures, style):
    """Los dos cortes que pasan por el optimo, con sus barras de error.

    La curva va entera y las barras cada pocos puntos: con 81 y 61 valores de
    grilla, una barra por punto tapa la curva. La barra es el error estandar de
    la media entre los M eventos; la franja verde es el tramo del corte que
    EMPATA con el optimo segun la diferencia pareada, que es la incertidumbre
    que de verdad tiene el parametro.
    """
    common.use_style(style)
    mean, sem = common.population(event_error)
    i, j = np.unravel_index(np.argmin(mean), mean.shape)
    figure, axesrow = plt.subplots(1, 2, figsize=(10.0, 4.0) if style == "informe"
                                   else (11.0, 4.2))
    color, marker = common.METRIC_STYLE[metric]
    for axes, values, curve, bars, label, best, inside in (
            (axesrow[0], p1, mean[:, j], sem[:, j], common.AXIS_P1, p1[i], region[:, j]),
            (axesrow[1], p2, mean[i, :], sem[i, :], common.AXIS_P2, p2[j], region[i, :])):
        every = max(1, len(values) // 14)
        axes.plot(values, curve, color=color, linewidth=1.8)
        axes.errorbar(values[::every], curve[::every], yerr=bars[::every], color=color,
                      marker=marker, **common.ERRORBAR)
        if inside.any():
            axes.axvspan(values[inside].min(), values[inside].max(), color="#2ca02c",
                         alpha=0.15)
        axes.axvline(best, color="#2ca02c", linestyle="--", linewidth=1.8)
        axes.set_xlabel(label)
        axes.set_ylabel(common.METRIC_AVERAGE[metric])
    axesrow[0].set_title(f"$p_2 = {common.decimal(p2[j], 3)}$ m",
                         fontsize=matplotlib.rcParams["axes.labelsize"])
    axesrow[1].set_title(f"$p_1 = {common.decimal(p1[i], 2)}$ s",
                         fontsize=matplotlib.rcParams["axes.labelsize"])
    figure.tight_layout()
    common.save(figure, common.folder("b", figures) /
                f"cortes_metrica{metric}_{style}.png")
    plt.close(figure)


def ceiling(path: Path, figures, style):
    """Por que la grilla de p1 termina en 4 s: <E> contra p1 hasta 8 s, con la
    p2 del optimo de cada metrica. Mas alla del tiempo que falta para el cruce
    al empezar el evento (entre 2,4 y 3 s) el conflicto se declara desde el primer
    instante y <E> ya no baja."""
    if not Path(path).exists():
        print(f"(sin {path}: no se dibuja el techo de p1)")
        return
    common.use_style(style)
    p1, p2, labels, error1, error2 = common.read_sweep(path)
    figure, axes = plt.subplots()
    for metric, event_error in ((1, error1), (2, error2)):
        mean, sem = common.population(event_error)
        color, marker = common.METRIC_STYLE[metric]
        j = min(metric - 1, len(p2) - 1)
        axes.plot(p1, mean[:, j] / mean[:, j].min(), color=color, marker=marker, markersize=4,
                  label=f"{common.METRIC_LABEL[metric]}, $p_2 = {common.decimal(p2[j], 2)}$ m")
    axes.axvline(4.0, color="#2ca02c", linestyle="--", linewidth=1.8,
                 label="techo de la grilla fina")
    axes.set_xlabel(common.AXIS_P1)
    axes.set_ylabel("$\\langle E \\rangle / \\langle E \\rangle_{\\min}$")
    axes.set_ylim(0.9, 2.5)
    common.legend_inside(axes)
    common.save(figure, common.folder("b", figures) / f"techo_p1_{style}.png")
    plt.close(figure)
    for metric, event_error in ((1, error1), (2, error2)):
        mean, _ = common.population(event_error)
        j = min(metric - 1, len(p2) - 1)
        beyond = mean[p1 >= 4.0, j]
        print(f"  techo de p1, metrica {metric} (p2 = {p2[j]:g} m): de 4 a {p1.max():g} s "
              f"<E> se mueve {100 * (beyond.max() / beyond.min() - 1):.1f} %; minimo del "
              f"barrido largo en p1 = {p1[np.argmin(mean[:, j])]:g} s")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--barrido", type=Path, default=common.SWEEP / "fino" / "errores.txt")
    parser.add_argument("--largo", type=Path, default=common.SWEEP / "p1largo" / "errores.txt",
                        help="barrido de p1 hasta 8 s, para justificar el techo de la grilla")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    p1, p2, labels, error1, error2 = common.read_sweep(arguments.barrido)
    print(f"grilla: {len(p1)} x {len(p2)} pares, M = {len(labels)} eventos")
    best = {}
    for metric, event_error in ((1, error1), (2, error2)):
        mean, sem = common.population(event_error)
        i, j = np.unravel_index(np.argmin(mean), mean.shape)
        region = compatible(event_error, i, j)
        best[metric] = (p1[i], p2[j], mean[i, j], sem[i, j], region)
        surface(p1, p2, mean, metric, arguments.figures, arguments.estilo)
        cuts(p1, p2, event_error, region, metric, arguments.figures, arguments.estilo)
        print(f"\n{common.METRIC_LABEL[metric]}")
        print(f"  optimo: p1 = {p1[i]:.2f} s, p2 = {p2[j]:.3f} m, "
              f"<E> = {mean[i, j]:.4f} +- {sem[i, j]:.4f} m2 "
              f"(RMS {np.sqrt(mean[i, j]):.2f} m)")
        print(f"  sin capa (p1 = 0): <E> = {mean[0, 0]:.4f} m2 "
              f"(RMS {np.sqrt(mean[0, 0]):.2f} m); la capa baja el error un "
              f"{100 * (1 - mean[i, j] / mean[0, 0]):.0f} %")
        print(f"  region compatible: {int(region.sum())} de {region.size} pares, "
              f"p1 de {p1[region.any(axis=1)].min():.2f} a {p1[region.any(axis=1)].max():.2f} s, "
              f"p2 de {p2[region.any(axis=0)].min():.3f} a {p2[region.any(axis=0)].max():.3f} m")
        print(f"  distancia de paso que pide el optimo: D = 2r + p2 = {0.5 + p2[j]:.3f} m")

    (a1, b1, v1, _, r1), (a2, b2, v2, _, r2) = best[1], best[2]
    print(f"\ncomparacion de los dos optimos: p1 {a1:.2f} contra {a2:.2f} s, "
          f"p2 {b1:.3f} contra {b2:.3f} m")
    print(f"  el optimo de la metrica 2 esta "
          f"{'dentro' if r1[np.argmin(abs(p1 - a2)), np.argmin(abs(p2 - b2))] else 'fuera'}"
          f" de la region compatible de la metrica 1, y al reves "
          f"{'dentro' if r2[np.argmin(abs(p1 - a1)), np.argmin(abs(p2 - b1))] else 'fuera'}")
    mean1, _ = common.population(error1)
    mean2, _ = common.population(error2)
    print(f"  usar el optimo de la metrica 2 cuesta "
          f"{100 * (mean1[np.argmin(abs(p1 - a2)), np.argmin(abs(p2 - b2))] / v1 - 1):.1f} % "
          f"de <E(1)>, y al reves "
          f"{100 * (mean2[np.argmin(abs(p1 - a1)), np.argmin(abs(p2 - b1))] / v2 - 1):.1f} % "
          f"de <E(2)>")
    ceiling(arguments.largo, arguments.figures, arguments.estilo)


if __name__ == "__main__":
    main()
