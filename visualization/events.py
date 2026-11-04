"""Los M eventos experimentales de la catedra, tal como los lee el motor.

Dos figuras: las trayectorias medidas de los 19 eventos en el plano y la
distancia entre los dos peatones de cada evento contra el tiempo, que es la que
muestra que el cruce esta siempre adentro de la ventana con la que se simula.
Por consola sale la tabla de eventos (ventana, muestras, rapidez media y
distancia minima) y la comparacion de la ventana recortada contra la del LEEME.
"""

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np

import common


def trajectories(events: list[dict], tracks: dict, framerate: float, figures, style: str):
    """Las trayectorias medidas de todos los eventos en el plano. Un color por
    fila de salida (izquierda y derecha), una linea por peaton."""
    common.use_style(style)
    figure, axes = plt.subplots()
    for index, event in enumerate(events):
        for side, name in common.PEDESTRIAN_LABEL.items():
            pedestrian = event["izquierda" if side == 0 else "derecha"]
            frames = range(event["cuadro_inicial"], event["cuadro_inicial"] + event["Nm"])
            path = np.array([tracks[int(pedestrian["id"])][frame] for frame in frames
                             if frame in tracks[int(pedestrian["id"])]])
            axes.plot(path[:, 0], path[:, 1], color=common.EXPERIMENT_COLOR[side],
                      linewidth=1.0, alpha=0.55,
                      label=f"sale por la {name}" if index == 0 else None)
    axes.set_xlabel(common.AXIS_X)
    axes.set_ylabel(common.AXIS_Y)
    axes.set_aspect("equal")
    common.legend_inside(axes, loc="lower right")
    common.save(figure, common.folder("datos", figures) / f"eventos_trayectorias_{style}.png")
    plt.close(figure)


def distance(events: list[dict], tracks: dict, framerate: float, figures, style: str):
    """Distancia entre los dos peatones contra el tiempo, una curva por evento,
    con la distancia de contacto 2r marcada."""
    common.use_style(style)
    figure, axes = plt.subplots()
    sampling = 1.0 / framerate
    minima = []
    for index, event in enumerate(events):
        left = tracks[int(event["izquierda"]["id"])]
        right = tracks[int(event["derecha"]["id"])]
        time, gap = [], []
        for step in range(event["Nm"]):
            frame = event["cuadro_inicial"] + step
            if frame in left and frame in right:
                time.append(step * sampling)
                gap.append(float(np.hypot(left[frame][0] - right[frame][0],
                                          left[frame][1] - right[frame][1])))
        axes.plot(time, gap, color=common.EXPERIMENT_COLOR[0], linewidth=1.0, alpha=0.5,
                  label="eventos medidos" if index == 0 else None)
        minima.append(min(gap))
    axes.axhline(0.5, color=common.EXPERIMENT_COLOR[1], linestyle="--", linewidth=1.6,
                 label="contacto, $2r = 0{,}5$ m")
    axes.set_xlabel(common.AXIS_TIME)
    axes.set_ylabel(common.AXIS_DISTANCE)
    axes.set_ylim(0.0, None)
    common.legend_inside(axes)
    common.save(figure, common.folder("datos", figures) / f"eventos_distancia_vs_t_{style}.png")
    plt.close(figure)
    return np.array(minima)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eventos", type=str, default=str(common.EXPERIMENTAL /
                                                           "eventos_resumen.txt"))
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    events = common.read_events(arguments.eventos)
    tracks, framerate = common.read_raw_tracks()

    trajectories(events, tracks, framerate, arguments.figures, arguments.estilo)
    minima = distance(events, tracks, framerate, arguments.figures, arguments.estilo)

    speeds = np.array([event[side]["vd"] for event in events
                       for side in ("izquierda", "derecha")])
    instants = np.array([event["Nm"] for event in events])
    gaps = np.array([event["Nm"] - event[side]["muestras"] for event in events
                     for side in ("izquierda", "derecha")])
    print(f"M = {len(events)} eventos, {2 * len(events)} peatones, "
          f"{instants.sum()} instantes experimentales en total")
    print(f"framerate {framerate:.4f} fps -> dt_exp = {1 / framerate * 1e3:.2f} ms")
    print(f"Nm por evento: {instants.min()} a {instants.max()} "
          f"({instants.min() / framerate:.1f} a {instants.max() / framerate:.1f} s)")
    print(f"vd: {speeds.min():.2f} a {speeds.max():.2f} m/s, media {speeds.mean():.2f}")
    print(f"distancia minima medida: {minima.min():.2f} a {minima.max():.2f} m, "
          f"mediana {np.median(minima):.2f}")
    print(f"huecos de seguimiento: {int((gaps > 0).sum())} de {len(gaps)} peatones los "
          f"tienen; el mayor es de {gaps.max()} instantes")


if __name__ == "__main__":
    main()
