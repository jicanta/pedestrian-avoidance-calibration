"""Animacion de un evento: trayectoria medida y simulada superpuestas.

Cada peaton es un disco de radio r = 0,25 m: relleno el simulado, con el borde
del mismo color y sin relleno el medido. Atras queda la estela de los dos (la
medida entera, la simulada hasta el instante que se muestra). Cuando la capa
de elusion declara conflicto, el disco simulado se dibuja con borde negro y se
marca con una cruz su target temporal, unido al agente por una linea: asi se
ve en que momento el agente deja de mirar su target final y a donde mira
mientras dura el conflicto. El rotulo de arriba lleva el instante, la
distancia entre los dos peatones medida y simulada, y si hay conflicto.

    python3 visualization/animate.py --run data/runs/optimo-metrica1/m10
    python3 visualization/animate.py --run data/runs/optimo-metrica1/m10 --cuadro 4.5

Un cuadro por instante experimental: el video a 1/dtExp = 15 cuadros por
segundo corre en tiempo real.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.patches import Circle

import common


def frame_index(times: np.ndarray, target: float) -> int:
    return int(np.searchsorted(times, target, side="right") - 1)


def caption(static: dict, t: float, simulated: np.ndarray, experimental: np.ndarray) -> str:
    computed = float(np.hypot(*(simulated[0, :2] - simulated[1, :2])))
    text = (f"evento {static['evento']}    $t$ = {common.decimal(t, 2):>5} s"
            f"    $d$ simulada = {common.decimal(computed, 2)} m")
    if experimental[0, 2] > 0.5 and experimental[1, 2] > 0.5:
        measured = float(np.hypot(*(experimental[0, :2] - experimental[1, :2])))
        text += f"    medida = {common.decimal(measured, 2)} m"
    if simulated[:, 6].max() > 0.5:
        text += "    conflicto"
    return text


class Scene:
    """Todo lo que se redibuja cuadro a cuadro, para que el video y el cuadro
    fijo salgan exactamente iguales."""

    def __init__(self, axes, static, time, simulated, experimental):
        self.static = static
        self.time = time
        self.simulated = simulated
        self.experimental = experimental
        radius = static["r"]

        present = experimental[:, :, 2] > 0.5
        xs = np.concatenate([experimental[:, :, 0][present], simulated[:, :, 0].ravel()])
        ys = np.concatenate([experimental[:, :, 1][present], simulated[:, :, 1].ravel()])
        axes.set_xlim(xs.min() - 0.6, xs.max() + 0.6)
        axes.set_ylim(ys.min() - 0.6, ys.max() + 0.6)
        axes.set_aspect("equal")
        axes.set_xlabel(common.AXIS_X)
        axes.set_ylabel(common.AXIS_Y)
        axes.grid(False)

        self.discs, self.ghosts, self.trails, self.targets, self.links = [], [], [], [], []
        for side in (0, 1):
            visible = present[:, side]
            axes.plot(experimental[visible, side, 0], experimental[visible, side, 1],
                      color=common.EXPERIMENT_COLOR[side], linewidth=1.2, alpha=0.45,
                      zorder=2)
            disc = Circle((0, 0), radius, facecolor=common.EXPERIMENT_COLOR[side],
                          edgecolor="none", alpha=0.9, zorder=6)
            ghost = Circle((0, 0), radius, facecolor="none", linestyle="--",
                           edgecolor=common.EXPERIMENT_COLOR[side], linewidth=1.8, zorder=5)
            axes.add_patch(disc)
            axes.add_patch(ghost)
            trail, = axes.plot([], [], color=common.EXPERIMENT_COLOR[side], linewidth=2.2,
                               zorder=3)
            target, = axes.plot([], [], linestyle="none", marker="x",
                                color=common.TARGET_COLOR, markersize=10,
                                markeredgewidth=2.0, zorder=7)
            link, = axes.plot([], [], color=common.TARGET_COLOR, linewidth=1.0,
                              linestyle=":", zorder=4)
            self.discs.append(disc)
            self.ghosts.append(ghost)
            self.trails.append(trail)
            self.targets.append(target)
            self.links.append(link)
        axes.plot([], [], color=common.EXPERIMENT_COLOR[0], linewidth=2.2,
                  label="simulada")
        axes.plot([], [], color=common.EXPERIMENT_COLOR[0], linewidth=1.2, alpha=0.45,
                  label="medida")
        axes.plot([], [], linestyle="none", marker="x", color=common.TARGET_COLOR,
                  markersize=9, markeredgewidth=2.0, label="target temporal")
        axes.legend(loc="lower center", ncol=3,
                    fontsize=plt.rcParams["legend.fontsize"] - 1)
        self.text = axes.text(0.0, 1.02, "", transform=axes.transAxes,
                              fontsize=plt.rcParams["font.size"], va="bottom")

    def update(self, index):
        for side in (0, 1):
            state = self.simulated[index, side]
            self.discs[side].center = (state[0], state[1])
            self.discs[side].set_edgecolor("#1a1a1a" if state[6] > 0.5 else "none")
            self.discs[side].set_linewidth(1.8 if state[6] > 0.5 else 0.0)
            sample = self.experimental[index, side]
            self.ghosts[side].set_visible(sample[2] > 0.5)
            self.ghosts[side].center = (sample[0], sample[1])
            self.trails[side].set_data(self.simulated[:index + 1, side, 0],
                                       self.simulated[:index + 1, side, 1])
            if state[6] > 0.5:
                self.targets[side].set_data([state[4]], [state[5]])
                self.links[side].set_data([state[0], state[4]], [state[1], state[5]])
            else:
                self.targets[side].set_data([], [])
                self.links[side].set_data([], [])
        self.text.set_text(caption(self.static, self.time[index], self.simulated[index],
                                   self.experimental[index]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--fps", type=int, default=15,
                        help="cuadros por segundo; 1/dt_exp = 15 corre en tiempo real")
    parser.add_argument("--cuadro", type=float, default=-1.0,
                        help="instante (s) de un cuadro unico con el lienzo del video")
    parser.add_argument("--cruce", action="store_true",
                        help="el cuadro unico, en el instante de minima aproximacion "
                             "SIMULADA: es el momento en el que se ve la elusion")
    parser.add_argument("--name", type=str, default="")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    common.use_style(arguments.estilo)

    static, time, simulated, experimental = common.load_run(arguments.run)
    name = arguments.name or f"evento{static['evento']:02d}"
    out_dir = common.folder("anim", arguments.figures)

    figure, axes = plt.subplots(figsize=(10.0, 3.8))
    scene = Scene(axes, static, time, simulated, experimental)
    common.comma_ticks(figure)

    if arguments.cruce or arguments.cuadro >= 0:
        if arguments.cruce:
            gap = np.hypot(simulated[:, 0, 0] - simulated[:, 1, 0],
                           simulated[:, 0, 1] - simulated[:, 1, 1])
            index = int(np.argmin(gap))
            tag = "cruce"
        else:
            index = frame_index(time, arguments.cuadro)
            tag = f"t{arguments.cuadro:g}"
        scene.update(index)
        path = out_dir / f"{name}_cuadro_{tag}.png"
        common.save(figure, path)
        print(path, f"(t = {time[index]:.3f} s)")
        return

    animation = FuncAnimation(figure, scene.update, frames=len(time),
                              interval=1000 / arguments.fps, blit=False)
    path = out_dir / f"{name}.mp4"
    animation.save(path, writer=FFMpegWriter(fps=arguments.fps, bitrate=2400))
    print(path, f"({len(time)} cuadros)")


if __name__ == "__main__":
    main()
