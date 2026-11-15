"""EXTRA (fuera de lo que pide el enunciado): el reparto de la elusion.

La capa que se calibra en los items b, c y d es simetrica: los dos peatones
del par se corren lo mismo. Aca la capa lleva un numero mas, alfa, la fraccion
de la separacion que falta que se lleva el peaton que sale de la IZQUIERDA (el
otro se lleva 1 - alfa); alfa = 0,5 es la capa simetrica. Con t_a y d_s fijos
en el optimo poblacional se optimiza alfa, SOLO CON LA METRICA 1 (el error a
iguales tiempos; lo pidio la catedra):

* `alfa_curva`: <E(1)>(alfa) con sus barras de error (el optimo se informa por
  consola y se escribe a mano en la diapositiva). Dice si hay un lado que cede
  sistematicamente.
* `alfa_histograma`: el histograma del alfa optimo de cada evento (uno por
  PAR de peatones, no por peaton), con la cantidad de eventos de cada barra y
  una linea vertical en el optimo global. Las barras tienen 0,125 de ancho y
  estan centradas en 0, 0,125, ..., 1: la del medio son los pares simetricos y
  ningun valor de la grilla de alfa cae en un borde.
* `alfa_medido`: el alfa optimo de cada evento contra el alfa MEDIDO en las
  trayectorias (la fraccion del desvio lateral en el cruce que hizo el de la
  izquierda), que no usa la simulacion para nada.
* `alfa_extremos`: las trayectorias del evento MAS simetrico (alfa optimo mas
  cerca de 0,5) y del MENOS simetrico (el mas cerca de 0 o de 1): medidas,
  simuladas con la capa simetrica y simuladas con el alfa del par.

Ademas del optimo de cada par informa la ASIMETRIA |alfa - 0,5| (0 es el
reparto parejo; 0,5, que uno solo hace toda la elusion): que evento la tiene
mas chica, cual mas grande y su media sobre los 19, que se compara con la del
alfa poblacional. Lo pidio la catedra el 13/11.

Las corridas de los dos eventos extremos con su alfa quedan en
data/asimetria/corridas/, con extremos.txt (evento, alfa, rol), que es lo que
lee `make gifs-alfa` para armar sus GIF.

    python3 visualization/asymmetry.py
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

import common

ENGINE = common.ROOT / "engine" / "build" / "elusion"
# Barras de 0,125 centradas en 0, 0,125, ..., 1 (ver el encabezado).
BINS = np.linspace(-0.0625, 1.0625, 10)


def fixed_anticipation(path: Path) -> float:
    """El t_a con que se hizo el barrido (d_s, alfa), del encabezado."""
    with open(path) as stream:
        for line in stream:
            found = re.match(r"# t_a fijo en ([0-9.]+) s", line)
            if found:
                return float(found.group(1))
            if not line.startswith("#"):
                break
    raise ValueError(f"{path} no dice con que t_a se hizo el barrido")


def run_with_share(output: Path, event: int, p1: float, p2: float, share: float) -> Path:
    """Corre un evento con el reparto alfa fijo y devuelve la carpeta."""
    command = [str(ENGINE), "run", "--pruebas", str(event), "--p1", f"{p1:.6g}",
               "--p2", f"{p2:.6g}", "--alfa", f"{share:.6g}", "--dir", str(output / f"m{event}")]
    subprocess.run(command, check=True, capture_output=True, cwd=common.ROOT)
    return output / f"m{event}"


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


def extremes(folders, labels, share, gain, measured, p1, p2, runs, out, style):
    """Las trayectorias del par mas simetrico (alfa optimo mas cerca de 0,5) y
    del menos simetrico (el mas lejos): las medidas (trazo lleno), la
    simulacion con la capa simetrica (trazo cortado) y la simulacion con el
    alfa optimo de ese par (punteada). Si varios eventos empatan en el alfa de
    la grilla, el mas simetrico es el que MENOS gana con su alfa respecto de
    la capa simetrica (y el menos simetrico, el que mas)."""
    asymmetry = np.abs(share - 0.5)
    order = np.lexsort((gain, asymmetry))
    chosen = ((int(order[0]), "el más simétrico"), (int(order[-1]), "el menos simétrico"))
    runs.mkdir(parents=True, exist_ok=True)
    (runs / "extremos.txt").write_text(
        "# evento alfa rol\n" + "".join(
            f"{int(labels[index])} {share[index]:.6g} {role}\n"
            for (index, _), role in zip(chosen, ("mas-simetrico", "menos-simetrico"))))
    figure, panels = plt.subplots(1, 2, sharex=True, sharey=True, figsize=(11.0, 2.75))
    small = plt.rcParams["legend.fontsize"]
    for axes, (index, reason) in zip(panels, chosen):
        label = int(labels[index])
        _, _, symmetric, experimental = common.load_run(folders[index])
        _, _, own, _ = common.load_run(run_with_share(runs, label, p1, p2, share[index]))
        errors = [np.mean([np.nanmean(common.metric_errors(experimental[:, side],
                                                           simulated[:, side])[0])
                           for side in (0, 1)]) for simulated in (symmetric, own)]
        for side in (0, 1):
            color = common.EXPERIMENT_COLOR[side]
            axes.plot(experimental[:, side, 0], experimental[:, side, 1], color=color,
                      linewidth=2.4)
            axes.plot(symmetric[:, side, 0], symmetric[:, side, 1], color=color,
                      linewidth=1.6, linestyle="--")
            axes.plot(own[:, side, 0], own[:, side, 1], color="#1a1a1a",
                      linewidth=1.6, linestyle=":")
        axes.set_aspect("equal")
        axes.set_ylim(1.05, 3.25)
        axes.set_yticks([1.5, 2.0, 2.5])
        axes.set_xlabel(common.AXIS_X)
        axes.text(0.015, 0.95, f"evento {label}, {reason}: $\\alpha = "
                  f"{common.math_decimal(share[index], 3)}$", transform=axes.transAxes,
                  va="top", fontsize=small, color="#1a1a1a")
        print(f"  evento {label} ({reason}): alfa optimo {share[index]:.3f} (medido "
              f"{measured[index]:.2f}); E1 = {errors[0]:.4f} con la capa simetrica y "
              f"{errors[1]:.4f} con su alfa")
    panels[0].set_ylabel(common.AXIS_Y)
    handles = [
        plt.Line2D([], [], color="#1a1a1a", linewidth=2.4, label="medida"),
        plt.Line2D([], [], color="#1a1a1a", linewidth=1.6, linestyle="--",
                   label="simulada, $\\alpha = 0{,}5$"),
        plt.Line2D([], [], color="#1a1a1a", linewidth=1.6, linestyle=":",
                   label="simulada, $\\alpha$ del par"),
    ]
    figure.legend(handles=handles, loc="upper center", ncol=3, fontsize=small, frameon=False,
                  bbox_to_anchor=(0.5, 1.0))
    figure.tight_layout(rect=(0, 0, 1, 0.93))
    common.save(figure, out / f"alfa_extremos_{style}.png")
    plt.close(figure)


def describe_asymmetry(labels, share, global_share):
    """La asimetria |alfa - 0,5| de cada par: el evento que la tiene mas chica
    (con los que empatan), el que la tiene mas grande y la media, contra la
    del alfa poblacional."""
    asymmetry = np.abs(share - 0.5)
    names = lambda mask: ", ".join(str(int(label)) for label in labels[mask])
    nearest = np.isclose(asymmetry, asymmetry.min())
    farthest = np.isclose(asymmetry, asymmetry.max())
    mean = asymmetry.mean()
    sem = asymmetry.std(ddof=1) / np.sqrt(len(asymmetry))
    print(f"  alfa mas cercano a 0,5: evento(s) {names(nearest)}, alfa = "
          f"{share[nearest][0]:.3f} (|alfa - 0,5| = {asymmetry.min():.3f})")
    print(f"  alfa mas lejano de 0,5: evento(s) {names(farthest)}, alfa = "
          f"{share[farthest][0]:.3f} (|alfa - 0,5| = {asymmetry.max():.3f})")
    print(f"  media de |alfa - 0,5| sobre los {len(share)} pares: {mean:.3f} +- {sem:.3f} "
          f"(mediana {np.median(asymmetry):.3f}); equivale a alfa = {0.5 + mean:.3f} o "
          f"{0.5 - mean:.3f}. Poblacional: |{global_share:.3f} - 0,5| = "
          f"{abs(global_share - 0.5):.3f}")
    print(f"  ceden mas a la izquierda (alfa > 0,5): {int((share > 0.5).sum())} de "
          f"{len(share)}; a la derecha: {int((share < 0.5).sum())}")
    return mean


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
    single = (6.2, 4.3) if style == "informe" else (6.6, 4.5)
    out = common.folder("extra", arguments.figures)

    metric = 1
    sweep = arguments.barridos / f"metrica{metric}" / "errores.txt"
    margin, shares, labels, cut, half, full, margins = analyse(sweep, metric)
    folders = sorted(Path(arguments.runs).glob("m*"), key=lambda path: int(path.name[1:]))
    measured = np.array([measured_share(path) for path in folders])
    print(f"alfa medido en las trayectorias: media {measured.mean():.2f}, mediana "
          f"{np.median(measured):.2f}, desvio {measured.std(ddof=1):.2f}, de "
          f"{measured.min():.2f} a {measured.max():.2f}")

    color, marker = common.METRIC_STYLE[metric]
    small = plt.rcParams["legend.fontsize"]
    mean = cut.mean(axis=1)
    sem = cut.std(axis=1, ddof=1) / np.sqrt(cut.shape[1])
    best = int(np.argmin(mean))
    own = np.argmin(cut, axis=0)
    own_share = shares[own]
    own_error = cut[own, np.arange(cut.shape[1])]
    gain = cut[half, :] - own_error

    curve, axes = plt.subplots(figsize=single)
    # Solo puntos, sin linea que los una: los 41 valores de alfa simulados.
    axes.errorbar(shares, mean, yerr=sem, color=color, marker=marker, markersize=5,
                  **common.ERRORBAR)
    # Sin la linea del optimo: el valor se escribe a mano en la diapositiva.
    axes.set_xlabel(common.AXIS_ALPHA)
    axes.set_ylabel(common.METRIC_AVERAGE[metric])

    histogram, axes = plt.subplots(figsize=single)
    counts, _, bars = axes.hist(own_share, bins=BINS, color=common.EXPERIMENT_COLOR[0],
                                alpha=0.85, edgecolor="white", linewidth=0.8)
    assert int(counts.sum()) == len(own_share)
    axes.bar_label(bars, labels=[str(int(count)) if count else "" for count in counts],
                   padding=3, fontsize=small, zorder=5,
                   bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.0})
    axes.axvline(shares[best], color=common.GLOBAL_COLOR, linestyle="--", linewidth=2.4,
                 label="óptimo global")
    axes.set_xlabel(common.AXIS_ALPHA + " óptimo de cada evento")
    axes.set_ylabel(common.AXIS_COUNT)
    axes.set_xlim(BINS[0], BINS[-1])
    axes.set_xticks(np.linspace(0.0, 1.0, 5))
    axes.set_ylim(0, counts.max() + 2.2)
    axes.yaxis.set_major_locator(MaxNLocator(integer=True))
    axes.legend(loc="upper left", fontsize=small)
    axes.text(0.97, 0.95, "$\\langle|\\alpha - 0{,}5|\\rangle = "
              f"{common.math_decimal(float(np.abs(own_share - 0.5).mean()), 2)}$",
              transform=axes.transAxes, ha="right", va="top", fontsize=small,
              color="#1a1a1a")

    scatter, axes = plt.subplots(figsize=(single[1] + 0.6, single[1]))
    correlation = float(np.corrcoef(measured, own_share)[0, 1])
    axes.plot([0, 1], [0, 1], color="#6e7680", linestyle=":", linewidth=1.4)
    axes.plot(measured, own_share, linestyle="none", marker=marker, color=color,
              markersize=8, alpha=0.85, label="un evento")
    axes.set_xlabel(common.AXIS_ALPHA + " medido en las trayectorias")
    axes.set_ylabel(common.AXIS_ALPHA + " calibrado")
    axes.set_xlim(-0.03, 1.03)
    axes.set_ylim(-0.03, 1.03)
    axes.set_aspect("equal")
    axes.legend(loc="upper left", fontsize=small)

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
          f"{own_share.min():.3f} a {own_share.max():.3f}")
    describe_asymmetry(labels, own_share, shares[best])
    print(f"  correlacion con el alfa medido: r = {correlation:.2f}")
    print(f"  con d_s tambien libre: optimo ({margins[a]:.3f} m, alfa {shares[b]:.3f}), "
          f"<E> = {plane[a, b]:.4f}")
    print("  alfa por evento: " + " ".join(
        f"{int(label)}:{value:.3f}" for label, value in zip(labels, own_share)))

    print("\nel par mas simetrico y el menos simetrico (alfa optimo)")
    extremes(folders, labels, own_share, gain, measured, fixed_anticipation(sweep), margin,
             arguments.barridos / "corridas", out, style)

    for figure, name in ((curve, "alfa_curva"), (histogram, "alfa_histograma"),
                         (scatter, "alfa_medido")):
        figure.tight_layout()
        common.save(figure, out / f"{name}_{style}.png")
        plt.close(figure)


if __name__ == "__main__":
    main()
