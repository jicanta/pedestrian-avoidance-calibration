"""Item 2 c) OPCIONAL: los parametros por peaton, cuatro por evento.

El enunciado pide "optimizar parametros por cada peaton (en lugar de 1 juego
de parametros por cada par de peatones)", y aclara que eso son CUATRO
parametros en lugar de dos. Los dos agentes estan acoplados -- el error de
cada uno depende tambien de los parametros del otro -- asi que el minimo lo
busca el motor sobre la grilla de los cuatro a la vez (comando `pairs`), y de
la MISMA grilla sale el optimo de dos parametros con el que se compara.

Por cada metrica, dos figuras y la tabla por consola:

* `optimos`: el plano (p1, p2) con, por cada evento, los DOS optimos de sus
  peatones unidos por un segmento, el optimo de dos parametros de ese evento y
  el poblacional. Lo que se lee es cuanto se separan los dos peatones de un
  mismo par: si el segmento es corto, el par no necesita parametros distintos.
* `errores`: E_m evento por evento con los tres juegos -- poblacional, dos
  individuales, cuatro individuales -- ordenado, con las tres medias.

Los tres se miden sobre LA MISMA grilla, que es la unica forma de que la
comparacion diga algo: una grilla mas fina baja el error de los tres a la vez.

    python3 visualization/pares.py --pares data/individual/recortada
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import common

COLUMNS = ("m", "metrica", "p1_izq", "p2_izq", "p1_der", "p2_der", "Em_cuatro",
           "E_izq_cuatro", "E_der_cuatro", "p1_comun", "p2_comun", "Em_dos",
           "E_izq_dos", "E_der_dos")


def read_pairs(path: Path) -> dict:
    values = np.loadtxt(path, comments="#")
    return {name: values[:, k] for k, name in enumerate(COLUMNS)}


def population_optimum(path: Path, metric: int):
    """El optimo poblacional sobre la MISMA grilla, y el E_m de cada evento ahi."""
    values = np.loadtxt(path, comments="#")
    labels = np.unique(values[:, 0])
    p1 = np.unique(values[:, 1])
    p2 = np.unique(values[:, 2])
    columns = (3, 4) if metric == 1 else (5, 6)
    error = np.zeros((len(p1), len(p2), len(labels)))
    index1 = {value: k for k, value in enumerate(p1)}
    index2 = {value: k for k, value in enumerate(p2)}
    index3 = {value: k for k, value in enumerate(labels)}
    for row in values:
        error[index1[row[1]], index2[row[2]], index3[row[0]]] = \
            0.5 * (row[columns[0]] + row[columns[1]])
    mean = error.mean(axis=2)
    i, j = np.unravel_index(np.argmin(mean), mean.shape)
    return p1[i], p2[j], error[i, j, :], labels


def optima(table, metric, population, figures, style, name):
    keep = table["metrica"] == metric
    p1_left = table["p1_izq"][keep]
    p2_left = table["p2_izq"][keep]
    p1_right = table["p1_der"][keep]
    p2_right = table["p2_der"][keep]
    p1_shared = table["p1_comun"][keep]
    p2_shared = table["p2_comun"][keep]

    common.use_style(style)
    figure, axes = plt.subplots()
    for k in range(len(p1_left)):
        axes.plot([p2_left[k], p2_right[k]], [p1_left[k], p1_right[k]],
                  color="#9aa3ad", linewidth=1.0, zorder=1)
    axes.plot(p2_left, p1_left, linestyle="none", marker="o", markersize=7,
              color=common.EXPERIMENT_COLOR[0], alpha=0.85, zorder=3,
              label="peatón de la izquierda")
    axes.plot(p2_right, p1_right, linestyle="none", marker="o", markersize=7,
              color=common.EXPERIMENT_COLOR[1], alpha=0.85, zorder=3,
              label="peatón de la derecha")
    axes.plot(p2_shared, p1_shared, linestyle="none", marker="s", markersize=6,
              markerfacecolor="none", markeredgecolor="#1a1a1a", markeredgewidth=1.0,
              zorder=2, label="óptimo del par (2 parámetros)")
    axes.plot([population[1]], [population[0]], linestyle="none", marker="*",
              markersize=17, color="#f5c518", markeredgecolor="#1a1a1a",
              markeredgewidth=0.8, zorder=4,
              label=f"poblacional $({common.decimal(population[0], 2)}$ s$,\\ "
                    f"{common.decimal(population[1], 3)}$ m$)$")
    axes.set_xlabel(common.AXIS_P2)
    axes.set_ylabel(common.AXIS_P1)
    axes.legend(loc="best", fontsize=plt.rcParams["legend.fontsize"] - 1)
    common.comma_ticks(figure)
    common.save(figure, common.folder("c", figures) /
                f"pares_optimos_metrica{metric}_{name}_{style}.png")


def errors(table, metric, population_errors, labels, figures, style, name):
    keep = table["metrica"] == metric
    four = table["Em_cuatro"][keep]
    two = table["Em_dos"][keep]
    order = np.argsort(-population_errors)

    common.use_style(style)
    figure, axes = plt.subplots()
    positions = np.arange(len(order))
    axes.bar(positions - 0.27, population_errors[order], width=0.27, color="#9aa3ad",
             label=f"poblacional (media {common.decimal(population_errors.mean(), 4)})")
    axes.bar(positions, two[order], width=0.27, color=common.EXPERIMENT_COLOR[0],
             alpha=0.85, label=f"2 por evento (media {common.decimal(two.mean(), 4)})")
    axes.bar(positions + 0.27, four[order], width=0.27, color=common.EXPERIMENT_COLOR[1],
             alpha=0.85, label=f"4 por evento (media {common.decimal(four.mean(), 4)})")
    axes.set_xticks(positions)
    axes.set_xticklabels([str(int(labels[k])) for k in order])
    axes.set_xlabel("evento")
    axes.set_ylabel(common.METRIC_EVENT[metric])
    axes.set_yscale("log")
    axes.legend(loc="best", fontsize=plt.rcParams["legend.fontsize"] - 1)
    common.comma_ticks(figure)
    common.save(figure, common.folder("c", figures) /
                f"pares_errores_metrica{metric}_{name}_{style}.png")


def report(table, metric, population, population_errors, labels):
    keep = table["metrica"] == metric
    four = table["Em_cuatro"][keep]
    two = table["Em_dos"][keep]
    gain = two - four
    spread = gain.std(ddof=1) / np.sqrt(len(gain))
    separation = np.hypot(table["p1_izq"][keep] - table["p1_der"][keep],
                          table["p2_izq"][keep] - table["p2_der"][keep])
    same = int(np.sum((table["p1_izq"][keep] == table["p1_der"][keep]) &
                      (table["p2_izq"][keep] == table["p2_der"][keep])))
    print(f"\n  metrica {metric}")
    print(f"    optimo poblacional en esta grilla: ({population[0]:.2f} s, "
          f"{population[1]:.3f} m), <E> = {population_errors.mean():.4f}")
    print(f"    2 parametros por evento: <E> = {two.mean():.4f}  "
          f"(baja {100 * (1 - two.mean() / population_errors.mean()):.0f} %)")
    print(f"    4 parametros por evento: <E> = {four.mean():.4f}  "
          f"(baja {100 * (1 - four.mean() / two.mean()):.0f} % mas)")
    print(f"    ganancia pareada 4 contra 2: {gain.mean():.4f} +- {spread:.4f} m2 "
          f"({gain.mean() / spread:.1f} desvios)")
    print(f"    los dos peatones del par eligen el MISMO par en {same} de "
          f"{len(four)} eventos")
    print(f"    separacion entre los dos optimos de un par: mediana "
          f"{np.median(separation):.3f}, maxima {separation.max():.3f}")
    print("     m   poblacional        2 param        4 param     izq (p1,p2)      der (p1,p2)")
    for k in range(len(four)):
        print(f"    {int(labels[k]):2d}   {population_errors[k]:10.4f}   "
              f"{two[k]:12.4f}   {four[k]:12.4f}   "
              f"({table['p1_izq'][keep][k]:.2f}, {table['p2_izq'][keep][k]:.3f})   "
              f"({table['p1_der'][keep][k]:.2f}, {table['p2_der'][keep][k]:.3f})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pares", type=Path, default=Path("data/individual/recortada"),
                        help="carpeta con pares.txt y errores.txt de la MISMA grilla")
    parser.add_argument("--name", type=str, default="")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    table = read_pairs(arguments.pares / "pares.txt")
    name = arguments.name or arguments.pares.name
    print(f"item 2 c) opcional -- {name}")
    for metric in (1, 2):
        p1, p2, population_errors, labels = population_optimum(
            arguments.pares / "errores.txt", metric)
        optima(table, metric, (p1, p2), arguments.figures, arguments.estilo, name)
        errors(table, metric, population_errors, labels, arguments.figures,
               arguments.estilo, name)
        report(table, metric, (p1, p2), population_errors, labels)


if __name__ == "__main__":
    main()
