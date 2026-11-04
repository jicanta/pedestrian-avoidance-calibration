"""Un evento: trayectorias medidas y simuladas, y el observable primario.

Tres figuras por evento:

* `trayectorias`: el plano x-y con las dos trayectorias medidas y las dos
  simuladas superpuestas, y la posicion de minima aproximacion marcada en las
  dos. Si se pasa `--sin-capa` tambien dibuja la corrida con la capa apagada,
  que es la comparacion que muestra que hace la capa.
* `observable`: el observable primario de cada metrica contra el tiempo,
  e(t) = |r_exp(t_k) - r_sim(t_k)|^2 (metrica 1) y su version al punto mas
  cercano (metrica 2), promediado sobre los dos peatones del evento. El
  escalar de cada metrica es el promedio temporal de su curva: la horizontal
  punteada.
* `distancia`: la distancia entre los dos peatones contra el tiempo, medida y
  simulada, con 2r marcado. Es lo que dice si la capa elude de mas o de menos.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import common


def plane(run: Path, baseline: Path | None, figures, style: str, name: str):
    # El recinto es largo y bajo (10 m x 2 m) y la figura va con escala igual en
    # los dos ejes: una proporcion distinta exagera o disimula el desvio lateral,
    # que es justamente lo que la figura muestra. Por eso el lienzo es ancho, y
    # la leyenda entra en la franja de arriba, que queda libre de datos.
    common.use_style(style)
    static, time, simulated, experimental = common.load_run(run)
    figure, axes = plt.subplots(figsize=(9.6, 3.4) if style == "informe" else (10.4, 3.6))
    for side in (0, 1):
        present = experimental[:, side, 2] > 0.5
        axes.plot(experimental[present, side, 0], experimental[present, side, 1],
                  color=common.EXPERIMENT_COLOR[side], linewidth=2.2,
                  label=f"medida, {common.PEDESTRIAN_LABEL[side]}")
        axes.plot(simulated[:, side, 0], simulated[:, side, 1],
                  color=common.EXPERIMENT_COLOR[side], linewidth=1.8, linestyle="--",
                  label=f"simulada, {common.PEDESTRIAN_LABEL[side]}")
    if baseline is not None:
        _, _, plain, _ = common.load_run(baseline)
        for side in (0, 1):
            axes.plot(plain[:, side, 0], plain[:, side, 1], color="#6e7680",
                      linewidth=1.4, linestyle=":",
                      label="simulada sin capa" if side == 0 else None)
    for track, marker, label in ((experimental[:, :, :2], "o", "cruce medido"),
                                 (simulated[:, :, :2], "x", "cruce simulado")):
        gap = np.hypot(track[:, 0, 0] - track[:, 1, 0], track[:, 0, 1] - track[:, 1, 1])
        k = int(np.argmin(gap))
        axes.plot(track[k, :, 0], track[k, :, 1], marker=marker, color="#1a1a1a",
                  linestyle="-", linewidth=1.0, markersize=7, label=label)
    axes.set_xlabel(common.AXIS_X)
    axes.set_ylabel(common.AXIS_Y)
    axes.set_aspect("equal")
    low = min(experimental[experimental[:, :, 2] > 0.5][:, 1].min(), simulated[:, :, 1].min())
    high = max(experimental[experimental[:, :, 2] > 0.5][:, 1].max(), simulated[:, :, 1].max())
    axes.set_ylim(low - 0.25, high + 1.15 * (high - low) + 0.35)
    axes.legend(ncol=3, loc="upper center", fontsize=matplotlib.rcParams["legend.fontsize"],
                columnspacing=1.2, handlelength=1.8)
    common.save(figure, common.folder("a", figures) / f"{name}_trayectorias_{style}.png")
    plt.close(figure)
    return static


def primary(run: Path, figures, style: str, name: str):
    common.use_style(style)
    static, time, simulated, experimental = common.load_run(run)
    figure, axes = plt.subplots()
    scalars = {}
    for metric in (1, 2):
        color, _ = common.METRIC_STYLE[metric]
        curves = []
        for side in (0, 1):
            same, closest = common.metric_errors(experimental[:, side], simulated[:, side])
            curves.append(same if metric == 1 else closest)
        curve = np.nanmean(np.vstack(curves), axis=0)
        scalars[metric] = float(np.nanmean(curve))
        axes.plot(time, curve, color=color, label=common.METRIC_LABEL[metric])
        axes.axhline(scalars[metric], color=color, linestyle="--", linewidth=1.4,
                     label=f"$E^{{({metric})}}_m = {common.decimal(scalars[metric], 3)}$ m$^2$")
    axes.set_xlabel(common.AXIS_TIME)
    axes.set_ylabel("$e(t)$ (m$^2$)")
    axes.set_ylim(0.0, None)
    common.legend_inside(axes, ncol=2)
    common.save(figure, common.folder("a", figures) / f"{name}_observable_{style}.png")
    plt.close(figure)
    return scalars


def separation(run: Path, figures, style: str, name: str):
    common.use_style(style)
    static, time, simulated, experimental = common.load_run(run)
    figure, axes = plt.subplots()
    both = (experimental[:, 0, 2] > 0.5) & (experimental[:, 1, 2] > 0.5)
    measured = np.hypot(experimental[:, 0, 0] - experimental[:, 1, 0],
                        experimental[:, 0, 1] - experimental[:, 1, 1])
    computed = np.hypot(simulated[:, 0, 0] - simulated[:, 1, 0],
                        simulated[:, 0, 1] - simulated[:, 1, 1])
    axes.plot(time[both], measured[both], color=common.EXPERIMENT_COLOR[0], label="medida")
    axes.plot(time, computed, color=common.EXPERIMENT_COLOR[1], linestyle="--",
              label="simulada")
    contact = 2.0 * static["r"]
    axes.axhline(contact, color="#6e7680", linestyle=":", linewidth=1.6,
                 label=f"contacto, $2r = {common.decimal(contact, 1)}$ m")
    axes.axhline(contact + static["p2"], color="#2ca02c", linestyle="-.", linewidth=1.6,
                 label=f"$D = 2r + p_2 = {common.decimal(contact + static['p2'], 2)}$ m")
    axes.set_xlabel(common.AXIS_TIME)
    axes.set_ylabel(common.AXIS_DISTANCE)
    axes.set_ylim(0.0, None)
    common.legend_inside(axes, ncol=2)
    common.save(figure, common.folder("a", figures) / f"{name}_distancia_{style}.png")
    plt.close(figure)
    print(f"  distancia minima: medida {measured[both].min():.2f} m, "
          f"simulada {computed.min():.2f} m")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True, help="carpeta de la corrida")
    parser.add_argument("--sin-capa", type=Path, default=None,
                        help="carpeta de la misma corrida con la capa apagada")
    parser.add_argument("--nombre", type=str, default=None)
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    static = common.read_static(arguments.run)
    name = arguments.nombre or f"evento{static['evento']:02d}"
    static = plane(arguments.run, arguments.sin_capa, arguments.figures, arguments.estilo, name)
    scalars = primary(arguments.run, arguments.figures, arguments.estilo, name)
    print(f"evento {static['evento']}: Nm = {static['instantes']}, "
          f"p1 = {static['p1']:.2f} s, p2 = {static['p2']:.3f} m, "
          f"{static['instantes_en_conflicto']} instantes en conflicto")
    print(f"  E1 = {scalars[1]:.4f} m2   E2 = {scalars[2]:.4f} m2")
    separation(arguments.run, arguments.figures, arguments.estilo, name)


if __name__ == "__main__":
    main()
