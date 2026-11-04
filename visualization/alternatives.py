"""Las alternativas de capa de elusion que se probaron contra la predictiva.

Todas de dos parametros y todas resueltas como target temporal (ninguna agrega
fuerzas). Las tres variantes de campo pesan la repulsion con A exp(-(d - 2r)/B)
y difieren en que distancia y que direccion usan:

* campo: la distancia actual y la direccion de j a i, como el termino social
  del SFM usado como direccion (Helbing). De frente no tiene componente
  lateral: es el problema que senala la Teorica 7.
* campo-lateral: la distancia actual, pero aplicado perpendicular al camino
  nominal, del lado contrario a j.
* campo-predictivo: la separacion PREDICHA d* y la direccion s de la capa
  predictiva: Karamouzas (2009) escrito como target.

Cada una se barre en su propia grilla (make alternativas) y se calibra con la
misma receta; la figura compara el <E> de cada una en su optimo, sobre los 19
eventos y por poblacion, y por consola va la diferencia pareada contra la
predictiva, que es lo que dice si una es mejor de verdad.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import common

VARIANTS = [("predictiva", "predictiva (la que corre)", common.SWEEP / "fino"),
            ("campo", "campo isotrópico", common.SWEEP / "alternativas" / "campo"),
            ("campo-lateral", "campo lateral", common.SWEEP / "alternativas" / "campo-lateral-fino"),
            ("campo-predictivo", "campo predictivo", common.SWEEP / "alternativas" / "campo-predictivo-fino")]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    events = common.read_events()
    rows = []
    reference = {}
    for key, label, folder in VARIANTS:
        path = Path(folder) / "errores.txt"
        if not path.exists():
            print(f"(falta {path})")
            continue
        p1, p2, labels, error1, error2 = common.read_sweep(path)
        corridor = common.classes(labels, events) == "corredor"
        row = {"key": key, "label": label}
        for metric, event_error in ((1, error1), (2, error2)):
            mean, _ = common.population(event_error)
            i, j = np.unravel_index(np.argmin(mean), mean.shape)
            best = event_error[i, j, :]
            edge = i in (0, len(p1) - 1) or j in (0, len(p2) - 1)
            row[metric] = dict(p1=p1[i], p2=p2[j], total=mean[i, j], corridor=best[corridor].mean(),
                               queue=best[~corridor].mean(), without=mean[0, 0], edge=edge,
                               events=best)
            if key == "predictiva":
                reference[metric] = best
        rows.append(row)

    print(f"{'capa':26s} {'m':>2} {'p1*':>7} {'p2*':>7} {'<E>':>7} {'-%':>4} {'corr':>6} {'fila':>6} "
          f"{'pareado vs predictiva':>24}")
    for row in rows:
        for metric in (1, 2):
            r = row[metric]
            d = reference[metric] - r["events"]
            sem = d.std(ddof=1) / np.sqrt(len(d))
            # "sin capa" es p1 = 0, que solo esta en la grilla de la predictiva.
            without = rows[0][metric]["without"]
            print(f"{row['label']:26s} {metric:2d} {r['p1']:7.3f} {r['p2']:7.3f} {r['total']:7.4f} "
                  f"{100 * (1 - r['total'] / without):4.0f} {r['corridor']:6.3f} {r['queue']:6.3f} "
                  f"{d.mean():+10.4f} +- {sem:.4f}{'  (borde de la grilla)' if r['edge'] else ''}")

    # Figura: <E(2)> en el optimo de cada variante, sobre los 19 y por poblacion.
    figure, axes = plt.subplots()
    positions = np.arange(len(rows))
    width = 0.27
    for offset, (name, color, text) in enumerate(
            (("total", "#6e7680", "los 19 eventos"),
             ("corridor", common.CLASS_COLOR["corredor"], "ya en el corredor"),
             ("queue", common.CLASS_COLOR["fila"], "sale de la fila"))):
        values = [row[2][name] for row in rows]
        axes.bar(positions + (offset - 1) * width, values, width, color=color, label=text)
    axes.axhline(rows[0][2]["without"], color="#1a1a1a", linestyle="--", linewidth=1.4,
                 label=f"sin capa, {common.decimal(rows[0][2]['without'], 2)} m$^2$")
    axes.set_xticks(positions)
    axes.set_xticklabels([row["label"].replace(" (la que corre)", "\n(la que corre)")
                          for row in rows],
                         fontsize=matplotlib.rcParams["xtick.labelsize"] - 2)
    axes.set_ylabel(common.AXIS_E2)
    common.legend_inside(axes, ncol=2)
    common.save(figure, common.folder("a", arguments.figures) /
                f"alternativas_metrica2_{arguments.estilo}.png")
    plt.close(figure)


if __name__ == "__main__":
    main()
