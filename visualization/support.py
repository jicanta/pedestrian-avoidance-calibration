"""Animaciones de apoyo: no son resultados, son la capa de elusion mirada de
cerca, para las diapositivas que la explican.

1. `cabeza-a-cabeza`: un cruce sintetico, dos agentes que caminan de frente a
   1 m/s con un desvio lateral inicial de 4 cm, con tres margenes de espacio
   personal p2 a la vez (un carril por valor). Se dibuja lo que la capa
   calcula en cada instante: las posiciones predichas al instante de minima
   aproximacion (discos punteados), la separacion predicha d*, y el target
   temporal con la linea que lo une al agente. Es la figura de la diapositiva
   del target temporal, en movimiento. Las trayectorias "experimentales" son
   las rectas a 1 m/s que hacen falta para que el motor arme el evento (de
   ahi salen r(0), v(0), el target final y vd), y no se dibujan.

2. `barrido-p2` y `barrido-p1`: el evento 10 simulado con el parametro
   recorriendo su rango, un cuadro por valor, al lado del corte de <E> con el
   punto que marca donde esta. Es lo que hace cada parametro, antes de mirar
   la superficie entera.

    python3 visualization/support.py cabeza-a-cabeza --p2s 0,0.2,0.5
    python3 visualization/support.py barrido --parametro p2 --evento 10
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.patches import Circle

import common

ENGINE = common.ROOT / "engine" / "build" / "elusion"
SUPPORT = common.DATA / "apoyo"
FRAMERATE = 15.0192


def synthetic_event(folder: Path, length: float = 8.0, speed: float = 1.0,
                    offset: float = 0.04, seconds: float = 9.0):
    """Escribe un archivo de trayectorias con el formato de la catedra: dos
    peatones que caminan de frente en linea recta, y la tabla del evento."""
    folder.mkdir(parents=True, exist_ok=True)
    frames = int(seconds * FRAMERATE)
    lines = ["# framerate: %.4f fps" % FRAMERATE, "# id frame x/m y/m markerID"]
    for k in range(frames):
        t = k / FRAMERATE
        lines.append(f"1 {1000 + k} {0.5 + speed * t:.5f} {2.0 - offset / 2:.5f} 1")
        lines.append(f"2 {1000 + k} {0.5 + length - speed * t:.5f} {2.0 + offset / 2:.5f} 2")
    (folder / "trayectorias.txt").write_text("\n".join(lines) + "\n")
    (folder / "eventos.txt").write_text(f"1 1 2 1000 {1000 + frames - 1}\n")


def run_engine(output: Path, p1: float, p2: float, data: Path | None = None,
               table: Path | None = None, event: int | None = None):
    command = [str(ENGINE), "run", "--p1", str(p1), "--p2", str(p2), "--dir", str(output)]
    if data is not None:
        command += ["--datos", str(data), "--eventos", str(table), "--xmin", "-100", "--xmax", "100"]
    if event is not None:
        command += ["--pruebas", str(event)]
    subprocess.run(command, check=True, capture_output=True, cwd=common.ROOT)


def prediction(position, velocity, other, other_velocity, anticipation, required):
    """Lo mismo que calcula la capa: tau*, las posiciones predichas y d*."""
    relative = other - position
    closing = other_velocity - velocity
    speed2 = closing @ closing
    if speed2 <= 0.0:
        return None
    tau = -(relative @ closing) / speed2
    if tau <= 0.0 or tau > anticipation:
        return None
    mine = position + velocity * tau
    theirs = other + other_velocity * tau
    return tau, mine, theirs, float(np.linalg.norm(theirs - mine))


class Lane:
    """Un carril de la animacion cabeza a cabeza: un valor de p2."""

    def __init__(self, axes, run: Path, title: str):
        self.static, self.time, self.simulated, _ = common.load_run(run)
        radius = self.static["r"]
        self.required = 2.0 * radius + self.static["p2"]
        self.anticipation = self.static["p1"]
        xs = self.simulated[:, :, 0]
        axes.set_xlim(xs.min() - 0.5, xs.max() + 0.5)
        axes.set_ylim(1.0, 3.0)
        axes.set_aspect("equal")
        axes.grid(False)
        axes.set_yticks([1.5, 2.0, 2.5])
        axes.set_ylabel(common.AXIS_Y)
        axes.text(0.01, 0.95, title, transform=axes.transAxes, va="top",
                  fontsize=matplotlib.rcParams["legend.fontsize"], color="#1a1a1a")
        self.discs, self.ghosts, self.trails, self.targets, self.links = [], [], [], [], []
        for side in (0, 1):
            disc = Circle((0, 0), radius, facecolor=common.EXPERIMENT_COLOR[side],
                          edgecolor="none", zorder=6)
            ghost = Circle((0, 0), radius, facecolor="none", linestyle="--",
                           edgecolor=common.EXPERIMENT_COLOR[side], linewidth=1.4,
                           alpha=0.7, zorder=5)
            axes.add_patch(disc)
            axes.add_patch(ghost)
            trail, = axes.plot([], [], color=common.EXPERIMENT_COLOR[side], linewidth=2.0,
                               zorder=3)
            target, = axes.plot([], [], linestyle="none", marker="x",
                                color=common.TARGET_COLOR, markersize=9, markeredgewidth=2.0,
                                zorder=7)
            link, = axes.plot([], [], color=common.TARGET_COLOR, linewidth=1.0,
                              linestyle=":", zorder=4)
            self.discs.append(disc)
            self.ghosts.append(ghost)
            self.trails.append(trail)
            self.targets.append(target)
            self.links.append(link)
        self.gap, = axes.plot([], [], color="#1a1a1a", linewidth=1.4, zorder=5)
        self.label = axes.text(0.99, 0.95, "", transform=axes.transAxes, va="top", ha="right",
                               fontsize=matplotlib.rcParams["legend.fontsize"],
                               color="#1a1a1a")

    def update(self, index):
        states = self.simulated[index]
        text = []
        for side in (0, 1):
            state = states[side]
            self.discs[side].center = (state[0], state[1])
            self.trails[side].set_data(self.simulated[:index + 1, side, 0],
                                       self.simulated[:index + 1, side, 1])
            conflict = state[6] > 0.5
            self.discs[side].set_edgecolor("#1a1a1a" if conflict else "none")
            self.discs[side].set_linewidth(1.6 if conflict else 0.0)
            if conflict:
                self.targets[side].set_data([state[4]], [state[5]])
                self.links[side].set_data([state[0], state[4]], [state[1], state[5]])
            else:
                self.targets[side].set_data([], [])
                self.links[side].set_data([], [])
        other = states[1]
        guess = prediction(states[0, :2], states[0, 2:4], other[:2], other[2:4],
                           self.anticipation, self.required)
        if guess is not None and states[0, 6] > 0.5:
            tau, mine, theirs, predicted = guess
            self.ghosts[0].center = tuple(mine)
            self.ghosts[1].center = tuple(theirs)
            self.ghosts[0].set_visible(True)
            self.ghosts[1].set_visible(True)
            self.gap.set_data([mine[0], theirs[0]], [mine[1], theirs[1]])
            text.append(f"$\\tau^* = {common.decimal(tau, 2)}$ s, "
                        f"$d^* = {common.decimal(predicted, 2)}$ m")
        else:
            self.ghosts[0].set_visible(False)
            self.ghosts[1].set_visible(False)
            self.gap.set_data([], [])
        distance = float(np.linalg.norm(states[0, :2] - states[1, :2]))
        text.append(f"$d = {common.decimal(distance, 2)}$ m")
        self.label.set_text("   ".join(text))


def head_on(arguments):
    common.use_style(arguments.estilo)
    folder = SUPPORT / "cabeza-a-cabeza"
    synthetic_event(folder)
    values = [float(v) for v in arguments.p2s.split(",")]
    runs = []
    for value in values:
        run = folder / f"p2-{value:g}"
        run_engine(run, arguments.p1, value, folder / "trayectorias.txt", folder / "eventos.txt")
        runs.append(run)

    figure, panels = plt.subplots(len(runs), 1, figsize=(10.0, 2.3 * len(runs) + 0.6),
                                  sharex=True)
    lanes = [Lane(axes, run, f"$d_s = {common.decimal(value, 2)}$ m, "
                             f"$D = {common.decimal(0.5 + value, 2)}$ m")
             for axes, run, value in zip(np.atleast_1d(panels), runs, values)]
    panels[-1].set_xlabel(common.AXIS_X)
    header = figure.text(0.5, 0.985, "", ha="center", va="top",
                         fontsize=matplotlib.rcParams["font.size"])
    panels[0].plot([], [], linestyle="none", marker="o", color="#6e7680", markersize=8,
                   label="agente")
    panels[0].plot([], [], linestyle="--", color="#6e7680", label="predicción en $\\tau^*$")
    panels[0].plot([], [], linestyle="none", marker="x", color=common.TARGET_COLOR,
                   markersize=8, markeredgewidth=2.0, label="target temporal")
    panels[0].legend(loc="lower right", ncol=3, fontsize=matplotlib.rcParams["legend.fontsize"] - 2)
    figure.tight_layout(rect=(0, 0, 1, 0.96))
    common.comma_ticks(figure)
    time = lanes[0].time

    def update(index):
        for lane in lanes:
            lane.update(index)
        header.set_text(f"cabeza a cabeza, $t_a = {common.decimal(arguments.p1, 2)}$ s, "
                        f"$t$ = {common.decimal(time[index], 2)} s")

    out_dir = common.folder("anim", arguments.figures)
    if arguments.cuadro >= 0:
        index = int(np.searchsorted(time, arguments.cuadro, side="right") - 1)
        update(index)
        path = out_dir / f"apoyo_cabeza_a_cabeza_t{arguments.cuadro:g}.png"
        common.save(figure, path)
        print(path, f"(t = {time[index]:.2f} s)")
        return
    animation = FuncAnimation(figure, update, frames=len(time), interval=1000 / arguments.fps)
    path = out_dir / "apoyo_cabeza_a_cabeza.mp4"
    animation.save(path, writer=FFMpegWriter(fps=arguments.fps, bitrate=2400))
    print(path, f"({len(time)} cuadros)")


def sweep(arguments):
    """El evento con el parametro recorriendo su rango, al lado del corte de
    <E> del item b con un punto que marca el valor del cuadro."""
    common.use_style(arguments.estilo)
    p1, p2, labels, error1, error2 = common.read_sweep(arguments.barrido)
    metric_error = error2 if arguments.metrica == 2 else error1
    mean, sem = common.population(metric_error)
    i, j = np.unravel_index(np.argmin(mean), mean.shape)
    if arguments.parametro == "p2":
        values = p2
        fixed = p1[i]
        curve = mean[i, :]
        label = common.AXIS_P2
    else:
        values = p1
        fixed = p2[j]
        curve = mean[:, j]
        label = common.AXIS_P1
    values = values[::arguments.cada]
    curve_values = curve[::arguments.cada]

    folder = SUPPORT / f"barrido-{arguments.parametro}-evento{arguments.evento:02d}"
    runs = []
    for value in values:
        run = folder / f"{arguments.parametro}-{value:g}"
        if arguments.parametro == "p2":
            run_engine(run, fixed, value, event=arguments.evento)
        else:
            run_engine(run, value, fixed, event=arguments.evento)
        runs.append(common.load_run(run))

    static, time, _, experimental = runs[0]
    figure = plt.figure(figsize=(12.0, 4.0))
    grid = figure.add_gridspec(1, 2, width_ratios=(1.9, 1.0))
    plane = figure.add_subplot(grid[0, 0])
    cut = figure.add_subplot(grid[0, 1])

    present = experimental[:, :, 2] > 0.5
    for side in (0, 1):
        visible = present[:, side]
        plane.plot(experimental[visible, side, 0], experimental[visible, side, 1],
                   color=common.EXPERIMENT_COLOR[side], linewidth=2.0, alpha=0.5,
                   label="medida" if side == 0 else None)
    lines = []
    for side in (0, 1):
        line, = plane.plot([], [], color=common.EXPERIMENT_COLOR[side], linewidth=2.2,
                           linestyle="--", label="simulada" if side == 0 else None)
        lines.append(line)
    xs = np.concatenate([experimental[:, :, 0][present]] +
                        [run[2][:, :, 0].ravel() for run in runs])
    ys = np.concatenate([experimental[:, :, 1][present]] +
                        [run[2][:, :, 1].ravel() for run in runs])
    plane.set_xlim(xs.min() - 0.4, xs.max() + 0.4)
    plane.set_ylim(ys.min() - 0.4, ys.max() + 0.9)
    plane.set_aspect("equal")
    plane.set_xlabel(common.AXIS_X)
    plane.set_ylabel(common.AXIS_Y)
    plane.legend(loc="upper right", ncol=2, fontsize=matplotlib.rcParams["legend.fontsize"] - 1)
    title = plane.text(0.01, 0.97, "", transform=plane.transAxes, va="top",
                       fontsize=matplotlib.rcParams["font.size"])

    color, marker = common.METRIC_STYLE[arguments.metrica]
    cut.plot(values, curve_values, color=color, linewidth=1.8)
    dot, = cut.plot([], [], marker="o", color="#2ca02c", markersize=11, linestyle="none",
                    markeredgecolor="#1a1a1a")
    cut.set_xlabel(label)
    cut.set_ylabel(common.METRIC_AVERAGE[arguments.metrica])
    other = "$t_a$" if arguments.parametro == "p2" else "$d_s$"
    unit = "s" if arguments.parametro == "p2" else "m"
    cut.set_title(f"{other} $= {common.decimal(fixed, 2)}$ {unit}, los 19 eventos",
                  fontsize=matplotlib.rcParams["legend.fontsize"])
    figure.tight_layout()
    common.comma_ticks(figure)

    def update(index):
        _, _, simulated, _ = runs[index]
        for side in (0, 1):
            lines[side].set_data(simulated[:, side, 0], simulated[:, side, 1])
        dot.set_data([values[index]], [curve_values[index]])
        unit_value = "s" if arguments.parametro == "p1" else "m"
        name = "t_a" if arguments.parametro == "p1" else "d_s"
        title.set_text(f"evento {arguments.evento}, ${name} = "
                       f"{common.decimal(values[index], 2)}$ {unit_value}")

    out_dir = common.folder("anim", arguments.figures)
    stem = f"apoyo_barrido_{arguments.parametro}_evento{arguments.evento:02d}"
    if arguments.cuadros:
        wanted = [float(v) for v in arguments.cuadros.split(",")]
        paths = []
        for value in wanted:
            index = int(np.argmin(np.abs(values - value)))
            update(index)
            path = out_dir / f"{stem}_{arguments.parametro}{values[index]:g}.png"
            common.save(figure, path)
            paths.append(path)
            print(path)
        # El resumen para el PDF: las trayectorias de los cuadros pedidos
        # superpuestas en un solo plano, y el corte con un punto por cuadro.
        summary(arguments, runs, values, curve_values, wanted, experimental, label, fixed,
                out_dir / f"{stem}_resumen.png")
        # La tira: los cuadros apilados en una sola imagen.
        from PIL import Image
        images = [Image.open(path) for path in paths]
        width = max(image.width for image in images)
        strip = Image.new("RGB", (width, sum(image.height for image in images)), "white")
        top = 0
        for image in images:
            strip.paste(image, (0, top))
            top += image.height
        strip.save(out_dir / f"{stem}_tira.png")
        print(out_dir / f"{stem}_tira.png")
        return
    animation = FuncAnimation(figure, update, frames=len(values), interval=1000 / arguments.fps)
    path = out_dir / f"{stem}.mp4"
    animation.save(path, writer=FFMpegWriter(fps=arguments.fps, bitrate=2400))
    print(path, f"({len(values)} cuadros)")


def summary(arguments, runs, values, curve_values, wanted, experimental, label, fixed, path):
    shades = plt.get_cmap("viridis")(np.linspace(0.05, 0.9, len(wanted)))
    figure = plt.figure(figsize=(12.0, 4.6))
    grid = figure.add_gridspec(1, 2, width_ratios=(2.1, 1.0))
    plane = figure.add_subplot(grid[0, 0])
    cut = figure.add_subplot(grid[0, 1])
    present = experimental[:, :, 2] > 0.5
    for side in (0, 1):
        visible = present[:, side]
        plane.plot(experimental[visible, side, 0], experimental[visible, side, 1],
                   color=common.EXPERIMENT_COLOR[side], linewidth=2.6, alpha=0.45,
                   label="medida" if side == 0 else None)
    name = "t_a" if arguments.parametro == "p1" else "d_s"
    unit = "s" if arguments.parametro == "p1" else "m"
    color, marker = common.METRIC_STYLE[arguments.metrica]
    cut.plot(values, curve_values, color=color, linewidth=1.8)
    for shade, value in zip(shades, wanted):
        index = int(np.argmin(np.abs(values - value)))
        _, _, simulated, _ = runs[index]
        for side in (0, 1):
            plane.plot(simulated[:, side, 0], simulated[:, side, 1], color=shade,
                       linewidth=1.8, linestyle="--",
                       label=f"${name} = {common.decimal(values[index], 2)}$ {unit}"
                       if side == 0 else None)
        cut.plot([values[index]], [curve_values[index]], marker="o", color=shade,
                 markersize=10, linestyle="none", markeredgecolor="#1a1a1a")
    ys = np.concatenate([experimental[:, :, 1][present]] +
                        [run[2][:, :, 1].ravel() for run in runs])
    plane.set_ylim(ys.min() - 0.3, ys.max() + 1.5)
    plane.set_aspect("equal")
    plane.set_xlabel(common.AXIS_X)
    plane.set_ylabel(common.AXIS_Y)
    plane.legend(loc="upper center", ncol=3, fontsize=matplotlib.rcParams["legend.fontsize"] - 2,
                 columnspacing=0.9, handlelength=1.5)
    plane.set_title(f"evento {arguments.evento}", loc="left",
                    fontsize=matplotlib.rcParams["legend.fontsize"])
    other_name = "$t_a$" if arguments.parametro == "p2" else "$d_s$"
    other_unit = "s" if arguments.parametro == "p2" else "m"
    cut.set_title(f"{other_name} $= {common.decimal(fixed, 2)}$ {other_unit}, los 19 eventos",
                  fontsize=matplotlib.rcParams["legend.fontsize"])
    cut.set_xlabel(label)
    cut.set_ylabel(common.METRIC_AVERAGE[arguments.metrica])
    figure.tight_layout()
    common.save(figure, path)
    plt.close(figure)
    print(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("que", choices=("cabeza-a-cabeza", "barrido"))
    parser.add_argument("--p1", type=float, default=2.15)
    parser.add_argument("--p2s", type=str, default="0,0.2,0.5")
    parser.add_argument("--parametro", choices=("p1", "p2"), default="p2")
    parser.add_argument("--metrica", type=int, choices=(1, 2), default=2)
    parser.add_argument("--evento", type=int, default=10)
    parser.add_argument("--cada", type=int, default=2, help="un cuadro cada tantos valores de la grilla")
    parser.add_argument("--barrido", type=Path, default=common.SWEEP / "fino" / "errores.txt")
    parser.add_argument("--fps", type=int, default=15)
    parser.add_argument("--cuadro", type=float, default=-1.0,
                        help="cabeza-a-cabeza: un cuadro fijo en ese instante")
    parser.add_argument("--cuadros", type=str, default="",
                        help="barrido: cuadros fijos en esos valores del parametro")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    if arguments.que == "cabeza-a-cabeza":
        head_on(arguments)
    else:
        sweep(arguments)


if __name__ == "__main__":
    main()
