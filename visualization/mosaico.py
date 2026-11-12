"""Los M eventos de una calibracion a la vez, para mirarlos de un saque.

Dos modos, los dos sobre el MISMO lienzo para todos los eventos (el corredor
entero), que es lo que deja compararlos:

* `grilla`: un panel chico por evento, los M animandose a la vez. Es la
  verificacion a ojo de que la ventana de cada evento es el cruce y no la
  fila: con la ventana bien recortada los 19 paneles tienen que verse iguales
  — dos discos que se acercan de frente por el corredor, se esquivan y siguen.
  El evento que se quede corto congela en su ultimo instante.
* `tandas`: los eventos superpuestos en UN solo panel, de a tandas, una tanda
  despues de la otra en el mismo video (`--tandas 5,5,5,4`). Sirve para ver si
  todas las pasadas caen sobre el mismo corredor.

    python3 visualization/mosaico.py --runs data/runs/optimo-metrica1
    python3 visualization/mosaico.py --runs data/runs/optimo-metrica1 --modo tandas

El nombre del archivo sale de `--name`; si no se da, del nombre de la carpeta
de corridas.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.patches import Circle

import common


def load_events(runs: Path):
    """Las corridas mN de una carpeta, ordenadas por numero de evento."""
    folders = sorted(runs.glob("m*"), key=lambda p: int(re.sub(r"\D", "", p.name)))
    events = []
    for folder in folders:
        static, time, simulated, experimental = common.load_run(folder)
        events.append({
            "m": int(static["evento"]),
            "r": static["r"],
            "n": len(time),
            "time": time,
            "sim": simulated,
            "exp": experimental,
        })
    if not events:
        raise SystemExit(f"no hay corridas mN en {runs}")
    return events


def common_limits(events, margin=0.6):
    """Un solo lienzo para todos: el que entra todas las trayectorias."""
    xs, ys = [], []
    for event in events:
        present = event["exp"][:, :, 2] > 0.5
        xs.append(event["exp"][:, :, 0][present])
        ys.append(event["exp"][:, :, 1][present])
        xs.append(event["sim"][:, :, 0].ravel())
        ys.append(event["sim"][:, :, 1].ravel())
    xs = np.concatenate(xs)
    ys = np.concatenate(ys)
    return ((xs.min() - margin, xs.max() + margin),
            (ys.min() - margin, ys.max() + margin))


class EventArt:
    """Los artistas de UN evento sobre unos ejes, y como se actualizan.

    `faded` es el modo de las tandas: la estela medida se dibuja mas tenue
    porque hay varias superpuestas.
    """

    def __init__(self, axes, event, faded=False, discs=True):
        self.event = event
        self.discs, self.ghosts, self.trails = [], [], []
        radius = event["r"]
        present = event["exp"][:, :, 2] > 0.5
        for side in (0, 1):
            colour = common.EXPERIMENT_COLOR[side]
            visible = present[:, side]
            axes.plot(event["exp"][visible, side, 0], event["exp"][visible, side, 1],
                      color=colour, linewidth=1.0, alpha=0.25 if faded else 0.45, zorder=2)
            trail, = axes.plot([], [], color=colour, linewidth=1.8, zorder=3)
            self.trails.append(trail)
            if discs:
                disc = Circle((0, 0), radius, facecolor=colour, edgecolor="none",
                              alpha=0.9, zorder=6)
                ghost = Circle((0, 0), radius, facecolor="none", linestyle="--",
                               edgecolor=colour, linewidth=1.2, zorder=5)
                axes.add_patch(disc)
                axes.add_patch(ghost)
                self.discs.append(disc)
                self.ghosts.append(ghost)

    def update(self, index):
        # El evento mas corto que el video se queda congelado en su final.
        k = min(index, self.event["n"] - 1)
        for side in (0, 1):
            state = self.event["sim"][k, side]
            self.trails[side].set_data(self.event["sim"][:k + 1, side, 0],
                                       self.event["sim"][:k + 1, side, 1])
            if not self.discs:
                continue
            self.discs[side].center = (state[0], state[1])
            conflict = state[6] > 0.5
            self.discs[side].set_edgecolor("#1a1a1a" if conflict else "none")
            self.discs[side].set_linewidth(1.6 if conflict else 0.0)
            sample = self.event["exp"][k, side]
            self.ghosts[side].set_visible(sample[2] > 0.5)
            self.ghosts[side].center = (sample[0], sample[1])


def grid(events, limits, fps, path, columns):
    rows = int(np.ceil(len(events) / columns))
    (x0, x1), (y0, y1) = limits
    figure, grid_axes = plt.subplots(rows, columns, figsize=(3.6 * columns, 1.5 * rows),
                                     squeeze=False)
    arts = []
    for k, axes in enumerate(grid_axes.ravel()):
        axes.set_xlim(x0, x1)
        axes.set_ylim(y0, y1)
        axes.set_aspect("equal")
        axes.set_xticks([])
        axes.set_yticks([])
        axes.grid(False)
        if k >= len(events):
            axes.set_visible(False)
            continue
        event = events[k]
        axes.text(0.015, 0.97, f"{event['m']}  ($N_m$ = {event['n']})",
                  transform=axes.transAxes, va="top", ha="left",
                  fontsize=plt.rcParams["font.size"] - 2)
        arts.append(EventArt(axes, event))
    figure.tight_layout(pad=0.3)
    longest = max(event["n"] for event in events)

    def update(index):
        for art in arts:
            art.update(index)

    animation = FuncAnimation(figure, update, frames=longest, interval=1000 / fps,
                              blit=False)
    animation.save(path, writer=FFMpegWriter(fps=fps, bitrate=3200))
    print(path, f"({len(events)} eventos, {longest} cuadros)")


def batches(events, limits, fps, path, sizes, hold):
    """Las tandas, una despues de la otra en el mismo video.

    Cada tanda dura lo que su evento mas largo, mas `hold` cuadros quietos al
    final para que se alcance a ver como quedo antes de pasar a la siguiente.
    """
    (x0, x1), (y0, y1) = limits
    figure, axes = plt.subplots(figsize=(11.0, 3.4))
    axes.set_xlim(x0, x1)
    axes.set_ylim(y0, y1)
    axes.set_aspect("equal")
    axes.set_xlabel(common.AXIS_X)
    axes.set_ylabel(common.AXIS_Y)
    axes.grid(False)
    common.comma_ticks(figure)
    caption = axes.text(0.0, 1.02, "", transform=axes.transAxes,
                        fontsize=plt.rcParams["font.size"], va="bottom")
    figure.tight_layout(pad=0.6)

    # Cada tanda se arma sobre los mismos ejes y se apaga cuando termina: los
    # artistas de todas las tandas se crean una sola vez, al principio.
    groups, start = [], 0
    for size in sizes:
        groups.append(events[start:start + size])
        start += size
    if start < len(events):
        groups.append(events[start:])

    group_arts = []
    for group in groups:
        arts = [EventArt(axes, event, faded=True) for event in group]
        group_arts.append(arts)
    for arts in group_arts:
        for art in arts:
            set_visible(art, False)

    plan = []
    for index, (group, arts) in enumerate(zip(groups, group_arts)):
        longest = max(event["n"] for event in group)
        label = ", ".join(str(event["m"]) for event in group)
        for frame in range(longest + hold):
            plan.append((index, min(frame, longest - 1), label))

    def update(frame):
        group_index, k, label = plan[frame]
        for index, arts in enumerate(group_arts):
            for art in arts:
                set_visible(art, index == group_index)
        for art in group_arts[group_index]:
            art.update(k)
        caption.set_text(f"eventos {label}")

    animation = FuncAnimation(figure, update, frames=len(plan), interval=1000 / fps,
                              blit=False)
    animation.save(path, writer=FFMpegWriter(fps=fps, bitrate=2800))
    print(path, f"({len(groups)} tandas, {len(plan)} cuadros)")


def set_visible(art, visible):
    for collection in (art.trails, art.discs, art.ghosts):
        for artist in collection:
            artist.set_visible(visible)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--runs", type=Path, required=True,
                        help="carpeta con las corridas mN de una calibracion")
    parser.add_argument("--modo", choices=("grilla", "tandas"), default="grilla")
    parser.add_argument("--columnas", type=int, default=4,
                        help="columnas de la grilla")
    parser.add_argument("--tandas", type=str, default="5,5,5,4",
                        help="cuantos eventos por tanda, separados por coma")
    parser.add_argument("--espera", type=int, default=12,
                        help="cuadros quietos al final de cada tanda")
    parser.add_argument("--fps", type=int, default=12)
    parser.add_argument("--name", type=str, default="")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    events = load_events(arguments.runs)
    limits = common_limits(events)
    name = arguments.name or arguments.runs.name
    out_dir = common.folder("anim", arguments.figures)

    if arguments.modo == "grilla":
        grid(events, limits, arguments.fps, out_dir / f"{name}_grilla.mp4",
             arguments.columnas)
    else:
        sizes = [int(piece) for piece in arguments.tandas.split(",") if piece.strip()]
        batches(events, limits, arguments.fps, out_dir / f"{name}_tandas.mp4", sizes,
                arguments.espera)


if __name__ == "__main__":
    main()
