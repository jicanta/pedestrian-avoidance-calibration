"""Item d: validacion cruzada.

Se parten los M eventos al azar en entrenamiento y validacion, se calibra el
par (p1, p2) minimizando <E> SOLO sobre los de entrenamiento y se reporta el
error sobre los de validacion, que no se usaron para calibrar. Eso se repite
para muchas particiones. Como el barrido ya tiene el error de cada evento en
cada par de la grilla, cada particion es un promedio sobre un subconjunto de
columnas: no hay que volver a simular nada.

Tres figuras por metrica:

* `error`: la distribucion del error de validacion sobre las particiones,
  contra el de entrenamiento y contra el <E> del item b (que usa los M
  eventos para calibrar Y para medir).
* `parametros`: el par calibrado en cada particion, en el plano (p1, p2).
* `tamano`: el error de entrenamiento y el de validacion contra el tamano del
  conjunto de entrenamiento, que es como se ve el sobreajuste.

Tambien se corre la validacion cruzada dejando uno afuera (M particiones de
M-1 eventos), que es el caso limite y no tiene azar.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import common


def split_error(event_error: np.ndarray, train: np.ndarray, test: np.ndarray, p1, p2):
    """Calibra con `train` y devuelve (p1*, p2*, error de train, error de test)."""
    surface = event_error[:, :, train].mean(axis=2)
    i, j = np.unravel_index(np.argmin(surface), surface.shape)
    return p1[i], p2[j], surface[i, j], float(event_error[i, j, test].mean())


def crossvalidate(event_error, p1, p2, size, partitions, generator):
    count = event_error.shape[2]
    rows = []
    for _ in range(partitions):
        order = generator.permutation(count)
        rows.append(split_error(event_error, order[:size], order[size:], p1, p2))
    return np.array(rows)


def leave_one_out(event_error, p1, p2):
    count = event_error.shape[2]
    rows = []
    for k in range(count):
        train = np.array([index for index in range(count) if index != k])
        rows.append(split_error(event_error, train, np.array([k]), p1, p2))
    return np.array(rows)


def error_figure(rows, reference, metric, figures, style):
    common.use_style(style)
    color, _ = common.METRIC_STYLE[metric]
    figure, axes = plt.subplots()
    axes.hist(rows[:, 3], bins=24, color=color, alpha=0.75, label="validación")
    axes.hist(rows[:, 2], bins=24, color="#6e7680", histtype="step", linewidth=1.8,
              label="entrenamiento")
    axes.axvline(reference, color="#2ca02c", linestyle="--", linewidth=2.0,
                 label="ítem b")
    axes.axvline(rows[:, 3].mean(), color=color, linestyle=":", linewidth=2.0,
                 label="media de validación")
    axes.set_xlabel(common.METRIC_EVENT[metric])
    axes.set_ylabel("particiones")
    common.legend_inside(axes)
    common.save(figure, common.folder("d", figures) / f"error_metrica{metric}_{style}.png")
    plt.close(figure)


def parameter_figure(rows, best, metric, p1, p2, figures, style):
    common.use_style(style)
    color, marker = common.METRIC_STYLE[metric]
    figure, axes = plt.subplots()
    pairs, counts = np.unique(rows[:, :2], axis=0, return_counts=True)
    axes.scatter(pairs[:, 0], pairs[:, 1], s=18 + 220 * counts / counts.max(), color=color,
                 alpha=0.55, edgecolors="none",
                 label="par calibrado")
    axes.plot([best[0]], [best[1]], marker="o", color="#2ca02c", markersize=10,
              linestyle="none", markeredgecolor="#1a1a1a", markeredgewidth=0.8,
              label="ítem b")
    axes.set_xlabel(common.AXIS_P1)
    axes.set_ylabel(common.AXIS_P2)
    axes.set_xlim(p1.min() - 0.1, p1.max() + 0.1)
    axes.set_ylim(p2.min() - 0.02, p2.max() + 0.02)
    common.legend_inside(axes, loc="upper left")
    common.save(figure, common.folder("d", figures) /
                f"parametros_metrica{metric}_{style}.png")
    plt.close(figure)


def size_figure(event_error, p1, p2, sizes, partitions, seed, reference, metric,
                figures, style):
    common.use_style(style)
    color, marker = common.METRIC_STYLE[metric]
    generator = np.random.default_rng(seed)
    train_mean, train_error, test_mean, test_error = [], [], [], []
    for size in sizes:
        rows = crossvalidate(event_error, p1, p2, size, partitions, generator)
        train_mean.append(rows[:, 2].mean())
        train_error.append(rows[:, 2].std(ddof=1) / np.sqrt(partitions))
        test_mean.append(rows[:, 3].mean())
        test_error.append(rows[:, 3].std(ddof=1) / np.sqrt(partitions))
    figure, axes = plt.subplots()
    axes.errorbar(sizes, train_mean, yerr=train_error, color="#6e7680", marker="s",
                  label="entrenamiento", **common.ERRORBAR)
    axes.plot(sizes, train_mean, color="#6e7680", linewidth=1.6)
    axes.errorbar(sizes, test_mean, yerr=test_error, color=color, marker=marker,
                  label="validación", **common.ERRORBAR)
    axes.plot(sizes, test_mean, color=color, linewidth=1.6)
    axes.axhline(reference, color="#2ca02c", linestyle="--", linewidth=1.8,
                 label="ítem b")
    axes.set_xlabel("eventos de entrenamiento")
    axes.set_ylabel(common.METRIC_AVERAGE[metric])
    common.legend_inside(axes)
    common.save(figure, common.folder("d", figures) / f"tamano_metrica{metric}_{style}.png")
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--barrido", type=Path, default=common.SWEEP / "fino" / "errores.txt")
    parser.add_argument("--particiones", type=int, default=500)
    parser.add_argument("--entrenamiento", type=int, default=13,
                        help="eventos de entrenamiento (de los M)")
    parser.add_argument("--semilla", type=int, default=7)
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    p1, p2, labels, error1, error2 = common.read_sweep(arguments.barrido)
    count = len(labels)
    for metric, event_error in ((1, error1), (2, error2)):
        mean, _ = common.population(event_error)
        i, j = np.unravel_index(np.argmin(mean), mean.shape)
        reference = mean[i, j]
        generator = np.random.default_rng(arguments.semilla)
        rows = crossvalidate(event_error, p1, p2, arguments.entrenamiento,
                             arguments.particiones, generator)
        error_figure(rows, reference, metric, arguments.figures, arguments.estilo)
        parameter_figure(rows, (p1[i], p2[j]), metric, p1, p2, arguments.figures,
                         arguments.estilo)
        sizes = list(range(3, count))
        size_figure(event_error, p1, p2, sizes, max(100, arguments.particiones // 4),
                    arguments.semilla, reference, metric, arguments.figures,
                    arguments.estilo)
        loo = leave_one_out(event_error, p1, p2)

        print(f"\n{common.METRIC_LABEL[metric]}")
        print(f"  item b (calibra y mide con los {count}): <E> = {reference:.4f} m2 "
              f"en p1 = {p1[i]:.2f} s, p2 = {p2[j]:.3f} m")
        print(f"  {arguments.particiones} particiones de "
              f"{arguments.entrenamiento}/{count - arguments.entrenamiento}:")
        print(f"    entrenamiento {rows[:, 2].mean():.4f} +- "
              f"{rows[:, 2].std(ddof=1):.4f} m2 (desvio entre particiones)")
        print(f"    validacion    {rows[:, 3].mean():.4f} +- {rows[:, 3].std(ddof=1):.4f} m2")
        print(f"    el error de validacion es un "
              f"{100 * (rows[:, 3].mean() / reference - 1):+.1f} % respecto del item b")
        print(f"    parametros calibrados: p1 mediana {np.median(rows[:, 0]):.2f} s "
              f"(de {rows[:, 0].min():.2f} a {rows[:, 0].max():.2f}), "
              f"p2 mediana {np.median(rows[:, 1]):.3f} m "
              f"(de {rows[:, 1].min():.3f} a {rows[:, 1].max():.3f})")
        pairs, counts = np.unique(rows[:, :2], axis=0, return_counts=True)
        winner = pairs[np.argmax(counts)]
        print(f"    el par mas frecuente, ({winner[0]:.2f} s, {winner[1]:.3f} m), sale en "
              f"{100 * counts.max() / arguments.particiones:.0f} % de las particiones "
              f"({len(pairs)} pares distintos)")
        print(f"  dejando uno afuera ({count} particiones de {count - 1}/1): "
              f"validacion {loo[:, 3].mean():.4f} m2 "
              f"({100 * (loo[:, 3].mean() / reference - 1):+.1f} %)")


if __name__ == "__main__":
    main()
