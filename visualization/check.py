"""Validacion de una corrida, desde los archivos que escribe el motor.

Cuatro verificaciones, todas sobre la salida primaria y ninguna sobre valores
que el motor haya calculado aparte:

1. Las DOS metricas recalculadas aca coinciden con las que informa el motor
   (el motor las calcula porque son lo que el barrido minimiza; esta es la
   comprobacion de que ese calculo es el del enunciado).
2. Las condiciones iniciales son las experimentales: la posicion del primer
   instante simulado es la medida, y la velocidad deseada tiene el modulo que
   declara static.txt.
3. La grilla temporal es la experimental: los Nm instantes simulados caen
   exactamente en k dtExp.
4. Se informa cuanto llegan a solaparse los dos agentes y si alguno supero su
   techo de rapidez. No son errores: el SFM sin fuerza social solo interactua
   por contacto y, cuando lo hay, la fuerza normal empuja y la rapidez pasa
   por encima de vd. Es justamente la medida de cuanto contacto queda: sin la
   capa de elusion hay choque en varios eventos y con la capa calibrada casi
   ninguno.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

import common


def check(run: Path, tolerance: float) -> list[str]:
    static, time, simulated, experimental = common.load_run(run)
    problems: list[str] = []
    excess = 0.0
    sampling = static["dt_exp"]

    # 1e-6 s y no cero: el motor escribe los instantes con diez cifras.
    grid = np.arange(len(time)) * sampling
    if np.max(np.abs(time - grid)) > 1e-6:
        problems.append("la grilla temporal no es la experimental")

    for side, name in ((0, "izquierda"), (1, "derecha")):
        start = np.array(static[f"{name}_inicio"])
        if np.linalg.norm(simulated[0, side, :2] - start) > 1e-9:
            problems.append(f"{name}: la posicion inicial no es la experimental")
        velocity = np.array(static[f"{name}_velocidad_inicial"])
        if np.linalg.norm(simulated[0, side, 2:4] - velocity) > 1e-6:
            problems.append(f"{name}: la velocidad inicial no es la experimental")
        # El agente no puede ir mas rapido que su velocidad deseada salvo
        # durante un contacto; el techo es vd o el modulo de la velocidad
        # inicial, que es la experimental y puede ser mayor que la media.
        ceiling = max(static[f"{name}_vd"], float(np.linalg.norm(velocity)))
        speed = np.hypot(simulated[:, side, 2], simulated[:, side, 3])
        excess = max(excess, speed.max() / ceiling - 1.0)

    gap = np.hypot(simulated[:, 0, 0] - simulated[:, 1, 0],
                   simulated[:, 0, 1] - simulated[:, 1, 1])
    overlap = max(0.0, 2.0 * static["r"] - gap.min())

    errors = {}
    for metric in (1, 2):
        values = []
        for side in (0, 1):
            same, closest = common.metric_errors(experimental[:, side], simulated[:, side])
            values.append(np.nanmean(same if metric == 1 else closest))
        errors[metric] = float(np.mean(values))
    return problems, errors, overlap, excess


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, required=True,
                        help="carpeta de una corrida o carpeta con varias (m1, m2, ...)")
    parser.add_argument("--tolerancia", type=float, default=0.02)
    arguments = parser.parse_args()

    folders = sorted(Path(arguments.runs).glob("m*"), key=lambda p: int(p.name[1:]))
    if not folders:
        folders = [arguments.runs]

    failures = 0
    contacts = 0
    print("  m    E1 (python)  E2 (python)  solapamiento  rapidez sobre el techo")
    for folder in folders:
        problems, errors, overlap, excess = check(folder, arguments.tolerancia)
        label = common.read_static(folder)["evento"]
        contacts += overlap > 0.0
        print(f"{label:3d}  {errors[1]:11.5f}  {errors[2]:11.5f}  {overlap * 100:8.2f} cm"
              f"  {100 * max(0.0, excess):8.1f} %"
              + ("" if not problems else "   <-- " + "; ".join(problems)))
        failures += len(problems)
    print(f"\n{len(folders)} corridas verificadas, {failures} problemas; "
          f"hay contacto en {contacts} de {len(folders)} eventos")
    print("comparar las dos columnas con lo que informa `elusion run`: el motor y este "
          "script calculan las metricas por caminos distintos")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()
