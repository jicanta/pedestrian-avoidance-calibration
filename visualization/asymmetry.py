"""EXTRA (fuera de lo que pide el enunciado): el reparto de la elusion.

La capa que se calibra en los items b, c y d es simetrica: los dos peatones
del par se corren lo mismo. Aca la capa lleva un numero mas, alfa, la fraccion
de la separacion que falta que se lleva el peaton que sale de la IZQUIERDA (el
otro se lleva 1 - alfa); alfa = 0,5 es la capa simetrica. Con t_a y d_s fijos
en el optimo poblacional de cada metrica se optimiza alfa:

* `alfa_curva`: <E>(alfa) con sus barras de error y el optimo marcado. Dice
  si hay un lado que cede sistematicamente.
* `alfa_histograma`: el histograma del alfa optimo de cada evento, con una
  linea vertical en el optimo global.
* `alfa_medido`: el alfa optimo de cada evento contra el alfa MEDIDO en las
  trayectorias (la fraccion del desvio lateral en el cruce que hizo el de la
  izquierda), que no usa la simulacion para nada.

    python3 visualization/asymmetry.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

import common


def measured_share(run: Path) -> float:
    """Fraccion del desvio lateral total en el cruce que hizo el peaton de la
    izquierda: el desvio de cada uno es su distancia a su propia recta de
    arranque a target, en el instante de minima distancia medida."""
    static, _, _, experimental = common.load_run(run)
    gap = np.hypot(experimental[:, 0, 0] - experimental[:, 1, 0],
                   experimental[:, 0, 1] - experimental[:, 1, 1])
    k = int(np.argmin(gap))
    deviations = []
    for side, name in ((0, "izquierda"), (1, "derecha")):
        start = np.array(static[f"{name}_inicio"])
        target = np.array(static[f"{name}_target"])
        direction = (target - start) / np.linalg.norm(target - start)
        offset = experimental[k, side, :2] - start
        deviations.append(abs(offset[0] * direction[1] - offset[1] * direction[0]))
    return deviations[0] / (deviations[0] + deviations[1])


def analyse(path: Path, metric: int):
    """Sobre el barrido (d_s, alfa) de una metrica: d_s queda en el optimo de
    la capa simetrica y se devuelve el corte en alfa, evento por evento."""
    margins, shares, labels, error1, error2 = common.read_sweep(path)
    event_error = error1 if metric == 1 else error2
    half = int(np.argmin(np.abs(shares - 0.5)))
    j = int(np.argmin(event_error[:, half, :].mean(axis=1)))
    return margins[j], shares, labels, event_error[j, :, :], half, event_error, margins


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--barridos", type=Path, default=common.DATA / "asimetria")
    parser.add_argument("--runs", type=Path, default=common.RUNS / "optimo-metrica1")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    style = arguments.estilo
    common.use_style(style)
    wide = (10.0, 4.0) if style == "informe" else (11.0, 4.2)
    out = common.folder("extra", arguments.figures)

    results = {metric: analyse(arguments.barridos / f"metrica{metric}" / "errores.txt", metric)
               for metric in (1, 2)}
    folders = sorted(Path(arguments.runs).glob("m*"), key=lambda path: int(path.name[1:]))
    measured = np.array([measured_share(path) for path in folders])
    print(f"alfa medido en las trayectorias: media {measured.mean():.2f}, mediana "
          f"{np.median(measured):.2f}, desvio {measured.std(ddof=1):.2f}, de "
          f"{measured.min():.2f} a {measured.max():.2f}")

    curve, curve_axes = plt.subplots(1, 2, figsize=wide)
    histogram, histogram_axes = plt.subplots(1, 2, figsize=wide)
    scatter, scatter_axes = plt.subplots(1, 2, figsize=wide)
    for column, metric in enumerate((1, 2)):
        margin, shares, labels, cut, half, full, margins = results[metric]
        color, marker = common.METRIC_STYLE[metric]
        mean = cut.mean(axis=1)
        sem = cut.std(axis=1, ddof=1) / np.sqrt(cut.shape[1])
        best = int(np.argmin(mean))
        own = np.argmin(cut, axis=0)
        own_share = shares[own]
        own_error = cut[own, np.arange(cut.shape[1])]

        axes = curve_axes[column]
        every = max(1, len(shares) // 14)
        axes.plot(shares, mean, color=color, linewidth=1.8)
        axes.errorbar(shares[::every], mean[::every], yerr=sem[::every], color=color,
                      marker=marker, **common.ERRORBAR)
        axes.axvline(shares[best], color=common.GLOBAL_COLOR, linestyle="--", linewidth=2.2,
                     label="óptimo")
        axes.set_xlabel(common.AXIS_ALPHA)
        axes.set_ylabel(common.METRIC_AVERAGE[metric])
        common.legend_inside(axes)

        axes = histogram_axes[column]
        axes.hist(own_share, bins=np.linspace(0.0, 1.0, 11), color=common.EXPERIMENT_COLOR[0],
                  alpha=0.85, edgecolor="white", linewidth=0.8)
        axes.axvline(shares[best], color=common.GLOBAL_COLOR, linestyle="--", linewidth=2.4,
                     label="óptimo global")
        axes.set_xlabel(common.AXIS_ALPHA + f" óptimo de cada evento, métrica {metric}")
        axes.set_ylabel(common.AXIS_COUNT)
        axes.set_xlim(0.0, 1.0)
        axes.yaxis.set_major_locator(MaxNLocator(integer=True))
        axes.legend(loc="upper left", fontsize=plt.rcParams["legend.fontsize"])

        axes = scatter_axes[column]
        correlation = float(np.corrcoef(measured, own_share)[0, 1])
        axes.plot([0, 1], [0, 1], color="#6e7680", linestyle=":", linewidth=1.4)
        axes.plot(measured, own_share, linestyle="none", marker=marker, color=color,
                  markersize=8, alpha=0.85, label="un evento")
        axes.set_xlabel(common.AXIS_ALPHA + " medido en las trayectorias")
        axes.set_ylabel(common.AXIS_ALPHA + f" calibrado, métrica {metric}")
        axes.set_xlim(-0.03, 1.03)
        axes.set_ylim(-0.03, 1.03)
        axes.set_aspect("equal")
        axes.legend(loc="upper left", fontsize=plt.rcParams["legend.fontsize"])

        gain = cut[half, :] - own_error
        gain_sem = gain.std(ddof=1) / np.sqrt(len(gain))
        global_gain = cut[half, :] - cut[best, :]
        # Con d_s libre ademas de alfa: el optimo del plano (d_s, alfa).
        plane = full.mean(axis=2)
        a, b = np.unravel_index(np.argmin(plane), plane.shape)
        print(f"\n{common.METRIC_LABEL[metric]}, d_s = {margin:.3f} m")
        print(f"  simetrica (alfa = 0,5): <E> = {mean[half]:.4f} +- {sem[half]:.4f}")
        print(f"  alfa global optimo {shares[best]:.3f}: <E> = {mean[best]:.4f}; ganancia "
              f"pareada {global_gain.mean():.4f} +- "
              f"{global_gain.std(ddof=1) / np.sqrt(len(gain)):.4f} "
              f"({100 * (1 - mean[best] / mean[half]):.0f} %)")
        print(f"  alfa propio de cada evento: <E> = {own_error.mean():.4f} +- "
              f"{own_error.std(ddof=1) / np.sqrt(len(gain)):.4f}; ganancia pareada "
              f"{gain.mean():.4f} +- {gain_sem:.4f} "
              f"({100 * (1 - own_error.mean() / mean[half]):.0f} %, "
              f"{gain.mean() / gain_sem:.1f} desvios)")
        print(f"  alfa por evento: media {own_share.mean():.2f}, mediana "
              f"{np.median(own_share):.2f}, desvio {own_share.std(ddof=1):.2f}, de "
              f"{own_share.min():.2f} a {own_share.max():.2f}")
        print(f"  correlacion con el alfa medido: r = {correlation:.2f}")
        print(f"  con d_s tambien libre: optimo ({margins[a]:.3f} m, alfa {shares[b]:.3f}), "
              f"<E> = {plane[a, b]:.4f}")
        print("  alfa por evento: " + " ".join(
            f"{int(label)}:{value:.2f}" for label, value in zip(labels, own_share)))

    for figure, name in ((curve, "alfa_curva"), (histogram, "alfa_histograma"),
                         (scatter, "alfa_medido")):
        figure.tight_layout()
        common.save(figure, out / f"{name}_{style}.png")
        plt.close(figure)


if __name__ == "__main__":
    main()
