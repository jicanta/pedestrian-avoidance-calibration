"""La capa de elusion explicada paso a paso, en movimiento.

Es el esquema de las diapositivas de la capa (deteccion del conflicto y target
temporal) armado de a un elemento por vez, para explicar la formula en la
charla. No es una simulacion: es geometria, con dos peatones quietos en el
instante en que la capa hace la cuenta.

Los pasos, cada uno con su formula al pie:

1. dos peatones en curso de colision, con su velocidad;
2. se extrapolan las dos trayectorias en linea recta y se mira la distancia
   entre las dos posiciones extrapoladas mientras avanza tau;
3. el instante en que esa distancia es minima es tau*, y la distancia, d*;
4. se compara d* con la separacion requerida D = r_i + r_j + d_s: si no
   alcanza (y tau* <= t_a) hay conflicto;
5. el target temporal de i: el punto q_i al que llegaria en tau* caminando
   derecho, corrido lo que falta, w (D - d*), hacia el lado contrario a j;
6. j hace la misma cuenta y le sale el lado opuesto: la elusion es reciproca.

Escribe el video (para el GIF) y, con --cuadros, un PNG del final de cada paso.

    python3 visualization/explain.py --figures data/figuras_diapositivas --estilo diapositiva
"""

from __future__ import annotations

import argparse

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation
from matplotlib.patches import Circle, FancyArrowPatch

import common

FPS = 15
RADIUS = 0.25
# Geometria del esquema (unidades arbitrarias, las del TikZ de la diapositiva).
START = (np.array([0.0, 0.0]), np.array([7.0, 2.2]))
VELOCITY = (np.array([1.35, 0.26]), np.array([-1.35, -0.24]))
REQUIRED = 1.9     # D, exagerada para que el corrimiento se vea
HORIZON = 14.0     # t_a del esquema
BLACK = "#1a1a1a"
GREY = "#6e7680"

# (duracion en segundos, titulo, formula al pie)
STEPS = [
    (2.0, "1. Dos peatones en curso de colisión",
     "cada uno camina hacia su target con su velocidad actual"),
    (4.0, "2. Se extrapolan las dos trayectorias en línea recta",
     r"distancia entre las posiciones extrapoladas:  $d(\tau) = |\Delta\mathbf{r} + \Delta\mathbf{v}\,\tau|$"),
    (3.0, "3. Instante de mínima aproximación",
     r"$\tau^{*} = -\,\dfrac{\Delta\mathbf{r}\cdot\Delta\mathbf{v}}{|\Delta\mathbf{v}|^{2}}$"
     r"$\qquad d^{*} = |\Delta\mathbf{r} + \Delta\mathbf{v}\,\tau^{*}|$"),
    (3.5, "4. ¿Alcanza la separación?",
     r"conflicto si  $0 < \tau^{*} \leq t_a$  y  $d^{*} < D = r_i + r_j + d_s$"),
    (5.0, "5. Target temporal: se corre lo que falta",
     r"$\mathbf{T}_i^{*} = \mathbf{q}_i + w(\tau^{*})\,(D - d^{*})\,\hat{\mathbf{s}}$"
     r"$\qquad w(\tau^{*}) = 1 - \tau^{*}/t_a$"),
    (4.0, "6. El otro hace la misma cuenta: elusión recíproca",
     "los dos se corren hacia lados opuestos, sin ponerse de acuerdo"),
]


def geometry():
    relative = START[1] - START[0]
    closing = VELOCITY[1] - VELOCITY[0]
    tau = -(relative @ closing) / (closing @ closing)
    predicted = [START[k] + VELOCITY[k] * tau for k in (0, 1)]
    gap = float(np.linalg.norm(predicted[0] - predicted[1]))
    weight = 1.0 - tau / HORIZON
    targets = []
    for k in (0, 1):
        away = (predicted[k] - predicted[1 - k]) / gap
        targets.append(predicted[k] + weight * (REQUIRED - gap) * away)
    return tau, predicted, gap, targets


def arrow(axes, color, width=2.6, style="-|>", zorder=6):
    patch = FancyArrowPatch((0, 0), (0, 0), arrowstyle=style, mutation_scale=18,
                            color=color, linewidth=width, zorder=zorder)
    patch.set_visible(False)
    axes.add_patch(patch)
    return patch


def build(style: str):
    common.use_style(style)
    tau, predicted, gap, targets = geometry()
    figure, axes = plt.subplots(figsize=(10.4, 5.6))
    figure.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.2)
    axes.set_xlim(-0.9, 8.6)
    axes.set_ylim(-1.15, 3.15)
    axes.set_aspect("equal")
    axes.axis("off")
    colors = [common.EXPERIMENT_COLOR[0], common.EXPERIMENT_COLOR[1]]
    size = matplotlib.rcParams["font.size"]

    title = figure.text(0.5, 0.94, "", ha="center", va="center", fontsize=size + 2,
                        color="#17426e", fontweight="bold")
    formula = figure.text(0.5, 0.09, "", ha="center", va="center", fontsize=size + 1,
                          color=BLACK)

    art = {"discs": [], "names": [], "speeds": [], "rays": [], "ghosts": [], "targets": [],
           "shifts": [], "headings": []}
    for k in (0, 1):
        disc = Circle(START[k], RADIUS, facecolor=colors[k], edgecolor="none", zorder=7)
        axes.add_patch(disc)
        art["discs"].append(disc)
        art["names"].append(axes.text(START[k][0], START[k][1] + (-0.5 if k == 0 else 0.5),
                                      "$i$" if k == 0 else "$j$", color=colors[k],
                                      ha="center", va="center", fontsize=size + 2))
        speed = arrow(axes, colors[k], width=3.2)
        speed.set_positions(START[k], START[k] + VELOCITY[k])
        speed.set_visible(True)
        art["speeds"].append(speed)
        ray, = axes.plot([], [], color=colors[k], linestyle="--", linewidth=1.6, zorder=3)
        art["rays"].append(ray)
        ghost = Circle(START[k], RADIUS, facecolor=colors[k], alpha=0.18, linestyle="--",
                       edgecolor=colors[k], linewidth=1.8, zorder=5)
        ghost.set_visible(False)
        axes.add_patch(ghost)
        art["ghosts"].append(ghost)
        target, = axes.plot([], [], linestyle="none", marker="X", markersize=13,
                            color=common.TARGET_COLOR, markeredgecolor="white", zorder=8)
        art["targets"].append(target)
        art["shifts"].append(arrow(axes, common.TARGET_COLOR, width=3.0, zorder=7))
        art["headings"].append(arrow(axes, colors[k], width=3.2))
        link, = axes.plot([], [], color=common.TARGET_COLOR, linestyle=":", linewidth=1.6,
                          zorder=4)
        art.setdefault("links", []).append(link)
    art["gap"], = axes.plot([], [], color=BLACK, linewidth=2.4, zorder=6,
                            marker="o", markersize=4)
    art["gap_text"] = axes.text(0, 0, "", color=BLACK, ha="left", va="center",
                                fontsize=size)
    art["clock"] = axes.text(0.5 * (START[0][0] + START[1][0]), 3.0, "", color=GREY,
                             ha="center", va="center", fontsize=size)
    # La separacion requerida D, como una barra del mismo largo al lado de d*.
    art["required"], = axes.plot([], [], color=common.TARGET_COLOR, linewidth=4.0, zorder=6,
                                 solid_capstyle="butt")
    art["required_text"] = axes.text(0, 0, "", color=common.TARGET_COLOR, ha="left",
                                     va="center", fontsize=size)
    art["verdict"] = axes.text(6.3, -0.55, "", color="#c55a11", ha="center", va="center",
                               fontsize=size + 3, fontweight="bold")
    art["nominal"] = axes.text(0, 0, "", color=BLACK, ha="right", va="top", fontsize=size)
    art["target_text"] = axes.text(0, 0, "", color=common.TARGET_COLOR, ha="right",
                                   va="center", fontsize=size)
    art["point"], = axes.plot([], [], linestyle="none", marker="o", markersize=6, color=BLACK,
                              zorder=8)

    frames_per_step = [int(round(seconds * FPS)) for seconds, _, _ in STEPS]
    total = sum(frames_per_step)

    def locate(frame):
        for step, count in enumerate(frames_per_step):
            if frame < count:
                return step, frame / max(1, count - 1)
            frame -= count
        return len(STEPS) - 1, 1.0

    def ease(fraction, span=0.6):
        value = min(1.0, fraction / span)
        return value * value * (3.0 - 2.0 * value)

    def draw(frame):
        step, fraction = locate(frame)
        title.set_text(STEPS[step][1])
        formula.set_text(STEPS[step][2])

        # Pasos 2 en adelante: las rectas y las posiciones extrapoladas.
        advance = 0.0 if step < 1 else (ease(fraction, 0.85) if step == 1 else 1.0)
        now = advance * tau
        for k in (0, 1):
            visible = step >= 1
            end = START[k] + VELOCITY[k] * (now + 0.9 if visible else 0.0)
            art["rays"][k].set_data(*zip(START[k], end) if visible else ([], []))
            art["ghosts"][k].set_visible(visible)
            art["ghosts"][k].center = START[k] + VELOCITY[k] * now
        if step >= 1:
            a, b = (START[k] + VELOCITY[k] * now for k in (0, 1))
            art["gap"].set_data([a[0], b[0]], [a[1], b[1]])
            middle = 0.5 * (a + b)
            art["gap_text"].set_position((middle[0] + 0.18, middle[1] + 0.05))
            art["gap_text"].set_text(r"$d(\tau)$" if step == 1 else r"$d^{*}$")
            art["clock"].set_text(r"$\tau$ avanza…" if step == 1 else
                                  r"en $\tau = \tau^{*}$ la distancia es mínima")
        else:
            art["gap"].set_data([], [])
            art["gap_text"].set_text("")
            art["clock"].set_text("")

        # Paso 4: D al lado de d*.
        if step >= 3:
            grow = ease(fraction) if step == 3 else 1.0
            direction = (predicted[1] - predicted[0]) / gap
            origin = predicted[0] + np.array([0.75, -0.1])
            centre = origin + 0.5 * gap * direction
            a = centre - 0.5 * grow * REQUIRED * direction
            b = centre + 0.5 * grow * REQUIRED * direction
            art["required"].set_data([a[0], b[0]], [a[1], b[1]])
            art["required_text"].set_position((b[0] + 0.12, b[1] + 0.12))
            art["required_text"].set_text("$D$" if grow > 0.6 else "")
            art["verdict"].set_text(r"$d^{*} < D$:  conflicto"
                                    if (step > 3 or fraction > 0.55) else "")
        else:
            art["required"].set_data([], [])
            art["required_text"].set_text("")
            art["verdict"].set_text("")

        # Pasos 5 y 6: el target temporal, primero el de i y despues el de j.
        for k in (0, 1):
            shown = step >= 4 + k
            grow = (ease(fraction) if step == 4 + k else 1.0) if shown else 0.0
            tip = predicted[k] + grow * (targets[k] - predicted[k])
            art["shifts"][k].set_visible(shown and grow > 0.05)
            art["shifts"][k].set_positions(predicted[k], tip)
            art["targets"][k].set_data([tip[0]], [tip[1]]) if shown and grow >= 1.0 \
                else art["targets"][k].set_data([], [])
            heading = shown and (step > 4 + k or fraction > 0.7)
            art["headings"][k].set_visible(heading)
            aim = targets[k] - START[k]
            art["headings"][k].set_positions(
                START[k], START[k] + 1.25 * np.linalg.norm(VELOCITY[k]) * aim / np.linalg.norm(aim))
            art["speeds"][k].set_alpha(0.25 if heading else 1.0)
            art["links"][k].set_data(*zip(START[k], targets[k]) if heading else ([], []))
        if step >= 4:
            art["point"].set_data([predicted[0][0]], [predicted[0][1]])
            art["nominal"].set_position((predicted[0][0] - 0.38, predicted[0][1] + 0.16))
            art["nominal"].set_text(r"$\mathbf{q}_i$")
            art["target_text"].set_position((targets[0][0] - 0.25, targets[0][1] - 0.12))
            art["target_text"].set_text(r"$\mathbf{T}_i^{*}$"
                                        if (step > 4 or fraction > 0.6) else "")
        else:
            art["point"].set_data([], [])
            art["nominal"].set_text("")
            art["target_text"].set_text("")
        return []

    return figure, draw, total, frames_per_step


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cuadros", action="store_true",
                        help="ademas del video, un PNG del final de cada paso")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    figure, draw, total, frames_per_step = build(arguments.estilo)
    folder = common.folder("anim", arguments.figures)
    animation = FuncAnimation(figure, draw, frames=total, blit=False)
    animation.save(folder / "apoyo_capa_paso_a_paso.mp4",
                   writer=FFMpegWriter(fps=FPS, bitrate=2400), dpi=150)
    print(f"{total} cuadros ({total / FPS:.1f} s) -> {folder / 'apoyo_capa_paso_a_paso.mp4'}")
    if arguments.cuadros:
        last = -1
        for step, count in enumerate(frames_per_step):
            last += count
            draw(last)
            figure.savefig(folder / f"apoyo_capa_paso_{step + 1}.png", dpi=200)
    plt.close(figure)


if __name__ == "__main__":
    main()
