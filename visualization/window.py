"""Cuanto depende la calibracion del tramo de x al que se recorta la ventana.

Lee lo que deja `make ventana` (data/ventana/x-<xmin>-<xmax>/, con el resumen
de los eventos y un barrido de la grilla por cada tramo) y arma la tabla: por
tramo, cuantos instantes quedan, las condiciones que el enunciado fija a
partir de la trayectoria (el angulo entre v(0) y la recta al target, y donde
cae el target) y el optimo de cada metrica con lo que la capa baja el error.

    make ventana
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

import common


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--carpeta", type=Path, default=common.DATA / "ventana")
    arguments = parser.parse_args()

    folders = sorted((path for path in arguments.carpeta.glob("x-*")
                      if (path / "errores.txt").exists()),
                     key=lambda path: float(path.name.split("-")[1]))
    print("tramo (m)      Nm medio  min  angulo max  y del target    "
          "metrica 1: optimo, <E>, baja      metrica 2: optimo, <E>, baja")
    for folder in folders:
        _, low, high = folder.name.split("-")
        events = common.read_events(folder / "eventos_resumen.txt")
        instants = np.array([event["Nm"] for event in events])
        angles = [angle for event in events for angle in common.initial_angles(event)]
        targets = [event[side]["ty"] for event in events for side in ("izquierda", "derecha")]
        p1, p2, _, error1, error2 = common.read_sweep(folder / "errores.txt")
        cells = []
        for event_error in (error1, error2):
            mean, sem = common.population(event_error)
            i, j = np.unravel_index(np.argmin(mean), mean.shape)
            cells.append(f"({p1[i]:.1f} s, {p2[j]:.2f} m) {mean[i, j]:.4f} +- {sem[i, j]:.4f} "
                         f"-{100 * (1 - mean[i, j] / mean[0, 0]):.0f} %")
        print(f"{float(low):4.2f} a {float(high):4.2f}   {instants.mean():6.0f}  {instants.min():4d}"
              f"  {max(angles):8.0f}°   {min(targets):.2f} a {max(targets):.2f}    "
              f"{cells[0]}    {cells[1]}")


if __name__ == "__main__":
    main()
