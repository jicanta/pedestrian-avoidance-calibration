"""Los M eventos experimentales de la catedra, tal como los lee el motor.

Dos figuras: las trayectorias medidas de los 19 eventos en el plano y la
distancia entre los dos peatones de cada evento contra el tiempo, que es la que
muestra que el cruce esta siempre adentro de la ventana con la que se simula.
Por consola sale la tabla de eventos (ventana, muestras, rapidez media y
distancia minima) y la comparacion de la ventana recortada contra la del LEEME.

La figura de las trayectorias dibuja SOLO el trayecto seleccionado: la ventana
de cada evento, adentro del tramo del corredor.
"""

from __future__ import annotations

import argparse

import matplotlib.pyplot as plt
import numpy as np

import common


def read_table(path):
    """experimental/eventos.txt: m, id izquierda, id derecha y los cuadros que
    declara el LEEME para la prueba."""
    rows = {}
    for line in open(path):
        if line.strip() and not line.startswith("#"):
            m, left, right, first, last = (int(piece) for piece in line.split())
            rows[m] = (left, right, first, last)
    return rows


def trajectories(events: list[dict], tracks: dict, x_range, figures, style: str):
    """Las trayectorias medidas de todos los eventos en el plano, SOLO sobre
    la ventana con la que se simula cada uno: el tramo del corredor entre las
    dos verticales. Lo que queda afuera (la fila de cada lado, el codo con el
    que cada peaton entra y sale de ella) no se dibuja: asi lo pidio la
    catedra el 13/11, mostrar solo el trayecto seleccionado."""
    common.use_style(style)
    figure, axes = plt.subplots(figsize=(8.6, 3.6) if style == "diapositiva" else (8.0, 3.4))
    for index, event in enumerate(events):
        inside = range(event["cuadro_inicial"], event["cuadro_inicial"] + event["Nm"])
        for side, name in common.PEDESTRIAN_LABEL.items():
            track = tracks[int(event["izquierda" if side == 0 else "derecha"]["id"])]
            used = np.array([track[frame] for frame in inside if frame in track])
            axes.plot(used[:, 0], used[:, 1], color=common.EXPERIMENT_COLOR[side],
                      linewidth=1.2, alpha=0.75,
                      label=f"sale por la {name}" if index == 0 else None)
    for k, edge in enumerate(x_range):
        axes.axvline(edge, color="#1a1a1a", linestyle="--", linewidth=1.6,
                     label="tramo simulado" if k == 0 else None)
    axes.set_xlabel(common.AXIS_X)
    axes.set_ylabel(common.AXIS_Y)
    axes.set_aspect("equal")
    axes.set_xlim(x_range[0] - 0.5, x_range[1] + 0.5)
    axes.set_ylim(0.9, 3.9)
    axes.set_yticks([1, 2, 3])
    axes.set_ylim(0.9, 3.1)
    handles, names = axes.get_legend_handles_labels()
    figure.legend(handles, names, loc="upper center", ncol=3, frameon=False,
                  fontsize=plt.rcParams["legend.fontsize"], bbox_to_anchor=(0.5, 1.0))
    figure.tight_layout(rect=(0, 0, 1, 0.9))
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
                 label="contacto, $2r$")
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
    parser.add_argument("--tabla", type=str,
                        default=str(common.ROOT / "experimental" / "eventos.txt"))
    parser.add_argument("--xmin", type=float, default=1.0)
    parser.add_argument("--xmax", type=float, default=7.7)
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    events = common.read_events(arguments.eventos)
    tracks, framerate = common.read_raw_tracks()

    table = read_table(arguments.tabla)
    trajectories(events, tracks, (arguments.xmin, arguments.xmax), arguments.figures,
                 arguments.estilo)
    minima = distance(events, tracks, framerate, arguments.figures, arguments.estilo)
    fractions = []
    for event in events:
        left = tracks[int(event["izquierda"]["id"])]
        right = tracks[int(event["derecha"]["id"])]
        gaps_ = [np.hypot(left[f][0] - right[f][0], left[f][1] - right[f][1])
                 if f in left and f in right else np.inf
                 for f in range(event["cuadro_inicial"], event["cuadro_inicial"] + event["Nm"])]
        fractions.append(int(np.argmin(gaps_)) / (event["Nm"] - 1))

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
    angles = np.array([angle for event in events for angle in common.initial_angles(event)])
    targets = np.array([event[side]["ty"] for event in events
                        for side in ("izquierda", "derecha")])
    whole = sum(last - first + 1 for _, _, first, last in table.values())
    print(f"la ventana se queda con {instants.sum()} de los {whole} cuadros del LEEME "
          f"({100 * instants.sum() / whole:.0f} %)")
    print(f"angulo entre v(0) y la recta al target: maximo {angles.max():.0f} grados, "
          f"mediana {np.median(angles):.0f}")
    print(f"y del target final: de {targets.min():.2f} a {targets.max():.2f} m")
    print("lugar del cruce dentro de la ventana (fraccion del tiempo): "
          f"de {min(fractions):.2f} a {max(fractions):.2f}")
    print(f"huecos de seguimiento: {int((gaps > 0).sum())} de {len(gaps)} peatones los "
          f"tienen; el mayor es de {gaps.max()} instantes")


if __name__ == "__main__":
    main()
