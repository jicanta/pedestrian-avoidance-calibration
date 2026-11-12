"""Utilidades compartidas por las figuras del TP5.

El motor de C++ escribe archivos de texto en data/ y este modulo es el unico
lugar donde se los interpreta: el resto de los scripts solo grafica.

Convenciones (las mismas en todas las figuras):

* La grilla temporal es la experimental: dtExp = 1/framerate. El motor integra
  con dt = dtExp / n (n entero), asi que cada instante experimental es
  exactamente un paso de la simulacion y no hay que interpolar nada para
  comparar trayectorias.
* Las DOS metricas del enunciado se calculan en el motor (son lo que el barrido
  minimiza) y aca se verifican: check.py las recalcula desde las trayectorias
  de una corrida y compara. Lo que se calcula aca son los promedios: el error
  de un evento (promedio sobre sus 2 peatones), el poblacional (promedio sobre
  los M eventos) y las particiones de la validacion cruzada.
* Una barra de error sobre un promedio poblacional es el error estandar de la
  media entre eventos, sigma/sqrt(M), porque lo que se compara es el promedio;
  cuando lo que se muestra es la dispersion entre eventos se dice que es el
  desvio estandar y se dibuja como banda o como caja.
* Las figuras no llevan titulo: los parametros van en el nombre del archivo y
  al costado de la figura en la diapositiva.
* El nombre de cada eje es el simbolo del enunciado con su unidad.
* Coma decimal en los numeros, nombre de eje en UNA sola linea y leyenda
  adentro del grafico sin tapar datos (devoluciones del TP2 y del TP4).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
from matplotlib.ticker import FuncFormatter, ScalarFormatter

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
EXPERIMENTAL = DATA / "experimental"
SWEEP = DATA / "barrido"
RUNS = DATA / "runs"
CONVERGENCE = DATA / "convergencia"
FIGURES = DATA / "figures"

FOLDER_NAME = {
    "datos": "0_datos_experimentales",
    "a": "a_capa_de_elusion",
    "b": "b_calibracion_poblacional",
    "c": "c_calibracion_individual",
    "d": "d_validacion_cruzada",
    "extra": "e_extra_reparto",
    "anim": "animaciones",
}


def folder(item: str, root: Path = FIGURES) -> Path:
    path = Path(root) / FOLDER_NAME[item]
    path.mkdir(parents=True, exist_ok=True)
    return path


AXIS_X = "$x$ (m)"
AXIS_Y = "$y$ (m)"
AXIS_TIME = "$t$ (s)"
AXIS_STEP = "$\\Delta t$ (s)"
# p1 y p2 son los nombres del enunciado; ta y ds, los del modelo. Los ejes
# llevan los dos porque la diapositiva de la capa los define juntos.
AXIS_P1 = "$p_1 = t_a$ (s)"
AXIS_P2 = "$p_2 = d_s$ (m)"
AXIS_E1 = "$\\langle E^{(1)} \\rangle$ (m$^2$)"
AXIS_E2 = "$\\langle E^{(2)} \\rangle$ (m$^2$)"
AXIS_EM1 = "$E^{(1)}_m$ (m$^2$)"
AXIS_EM2 = "$E^{(2)}_m$ (m$^2$)"
AXIS_PRIMARY1 = "$e^{(1)}(t)$ (m$^2$)"
AXIS_PRIMARY2 = "$e^{(2)}(t)$ (m$^2$)"
AXIS_DISTANCE = "$d$ (m)"
AXIS_EVENT = "evento $m$"
AXIS_SPEED = "$|\\vec{v}|$ (m/s)"
AXIS_WALL = "tiempo de ejecución (s)"
AXIS_COUNT = "eventos"
AXIS_COUNT_PEDESTRIANS = "peatones"
AXIS_ALPHA = "$\\alpha$"

METRIC_LABEL = {1: "métrica 1 (iguales tiempos)", 2: "métrica 2 (punto más cercano)"}
METRIC_AVERAGE = {1: AXIS_E1, 2: AXIS_E2}
METRIC_EVENT = {1: AXIS_EM1, 2: AXIS_EM2}
METRIC_PRIMARY = {1: AXIS_PRIMARY1, 2: AXIS_PRIMARY2}
METRIC_STYLE = {1: ("#1f5fbf", "o"), 2: ("#c55a11", "s")}

# Experimental contra simulado, y peaton de la izquierda contra el de la
# derecha: los mismos cuatro estilos en todas las figuras y animaciones.
EXPERIMENT_COLOR = {0: "#1f5fbf", 1: "#d62728"}
SIMULATION_COLOR = {0: "#7fb0ee", 1: "#f09a98"}
PEDESTRIAN_LABEL = {0: "izquierda", 1: "derecha"}
TARGET_COLOR = "#2ca02c"

# Mapas de <E>(p1, p2): el mismo mapa de color que el del TP4 (turbo invertido,
# rojo = error bajo), sin nada encima mas que el optimo.
def heat_colormap():
    from matplotlib import colors
    import matplotlib.pyplot as plt
    return colors.LinearSegmentedColormap.from_list(
        "turbo-invertida", plt.get_cmap("turbo")(np.linspace(0.90, 0.10, 256)))


# Color de la linea que marca el optimo poblacional (global) en los
# histogramas de optimos individuales.
GLOBAL_COLOR = "#2ca02c"

ERRORBAR = {"linestyle": "none", "elinewidth": 1.2, "capsize": 2.5, "capthick": 1.2}

STYLE = "informe"
STYLES = ("informe", "diapositiva")


def use_style(style: str = "informe") -> None:
    """Tipografia y tamanos de figura para revision o para la presentacion."""
    if style not in STYLES:
        raise SystemExit(f"estilo desconocido: {style}; hay {', '.join(STYLES)}")
    global STYLE
    STYLE = style
    matplotlib.rcParams.update(
        {
            "figure.figsize": (7.2, 4.8),
            "figure.dpi": 120,
            "savefig.dpi": 220,
            "savefig.bbox": "tight",
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "Times New Roman"],
            "font.size": 13,
            "axes.labelsize": 15,
            "xtick.labelsize": 12,
            "ytick.labelsize": 12,
            "legend.fontsize": 11,
            "legend.frameon": True,
            "legend.framealpha": 0.9,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "lines.linewidth": 1.6,
            "lines.markersize": 5,
            "errorbar.capsize": 3,
        }
    )
    if style == "diapositiva":
        matplotlib.rcParams.update(
            {
                "figure.figsize": (6.3, 4.0),
                "font.family": "sans-serif",
                "font.sans-serif": ["DejaVu Sans"],
                "font.size": 17,
                "axes.labelsize": 16,
                "xtick.labelsize": 15,
                "ytick.labelsize": 15,
                "legend.fontsize": 13,
                "lines.linewidth": 2.2,
                "lines.markersize": 7,
            }
        )


def decimal(value: float, digits: int | None = None) -> str:
    """Numero con coma decimal, como en el texto de las diapositivas."""
    text = f"{value:.{digits}f}" if digits is not None else f"{value:g}"
    return text.replace(".", ",")


def comma_ticks(figure) -> None:
    """Coma decimal en las marcas de los ejes lineales con formato automatico."""
    formatter = FuncFormatter(lambda value, _: decimal(value))
    for axes in figure.get_axes():
        for axis in (axes.xaxis, axes.yaxis):
            if axis.get_scale() == "linear" and type(axis.get_major_formatter()) is ScalarFormatter:
                axis.set_major_formatter(formatter)


def fit_axis_labels(figure, minimum: float = 11.0) -> None:
    """Achica el nombre de un eje hasta que entre en UNA linea dentro del largo
    de ese eje (devolucion del 18/09 sobre el TP3)."""
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    for axes in figure.get_axes():
        box = axes.get_window_extent(renderer)
        for label, room in ((axes.xaxis.label, box.width), (axes.yaxis.label, box.height)):
            if not label.get_text():
                continue
            size = label.get_fontsize()
            while size > minimum:
                extent = label.get_window_extent(renderer)
                if max(extent.width, extent.height) <= room:
                    break
                size -= 0.5
                label.set_fontsize(size)


def headroom(axes, fraction: float = 0.3) -> None:
    """Deja libre la fraccion de arriba del area de dibujo para que la leyenda
    entre adentro de la figura sin taparla (devolucion del TP2, D13)."""
    low, high = axes.get_ylim()
    if axes.get_yscale() == "log":
        if low <= 0.0 or high <= 0.0:
            return
        span = np.log10(high) - np.log10(low)
        axes.set_ylim(low, 10.0 ** (np.log10(high) + fraction / (1.0 - fraction) * span))
    else:
        span = high - low
        axes.set_ylim(low, high + fraction / (1.0 - fraction) * span)


def legend_inside(axes, ncol: int = 1, minimum: float = 10.0, margin: float = 0.06, **kwargs):
    """Leyenda DENTRO del area de dibujo y sin tapar datos (TP2, D13), midiendo
    cuanto ocupa en vez de suponerlo."""
    figure = axes.get_figure()
    base = float(matplotlib.rcParams["legend.fontsize"])
    kwargs.setdefault("loc", "upper right")
    kwargs.setdefault("columnspacing", 1.0)
    for columns in range(max(1, ncol), 0, -1):
        size = base
        while True:
            legend = axes.legend(ncol=columns, fontsize=size, **kwargs)
            figure.canvas.draw()
            renderer = figure.canvas.get_renderer()
            room = axes.get_window_extent(renderer)
            box = legend.get_window_extent(renderer)
            fits = box.width <= (1.0 - margin) * room.width
            if fits or size <= minimum:
                break
            size -= 0.5
        if fits or columns == 1:
            headroom(axes, min(0.6, box.height / room.height + margin))
            return legend


def save(figure, path) -> None:
    comma_ticks(figure)
    fit_axis_labels(figure)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(path)


def add_common_arguments(parser) -> None:
    parser.add_argument("--figures", type=Path, default=FIGURES,
                        help="carpeta raiz de las figuras")
    parser.add_argument("--estilo", choices=STYLES, default="informe")


# --------------------------------------------------------------------------
# Datos experimentales y corridas
# --------------------------------------------------------------------------

EVENT_COLUMNS = ("m", "cuadro_inicial", "Nm", "duracion", "dmin")
PEDESTRIAN_COLUMNS = ("id", "muestras", "vd", "camino", "x0", "y0", "vx0", "vy0", "tx", "ty")


def read_events(path: Path = EXPERIMENTAL / "eventos_resumen.txt") -> list[dict]:
    """eventos_resumen.txt de `elusion events` -> una fila por evento, con las
    condiciones que el enunciado fija para cada peaton."""
    rows = []
    for line in Path(path).read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        values = [float(piece) for piece in line.split()]
        event = dict(zip(EVENT_COLUMNS, values))
        for key in ("m", "cuadro_inicial", "Nm"):
            event[key] = int(event[key])
        offset = len(EVENT_COLUMNS)
        for index, name in ((0, "izquierda"), (1, "derecha")):
            start = offset + index * len(PEDESTRIAN_COLUMNS)
            event[name] = dict(zip(PEDESTRIAN_COLUMNS,
                                   values[start:start + len(PEDESTRIAN_COLUMNS)]))
        rows.append(event)
    return rows


def read_raw_tracks(path: Path = ROOT / "experimental" / "elusion_1_contra_1.txt"):
    """El archivo crudo de la catedra: {id: {cuadro: (x, y)}} y el framerate."""
    tracks: dict[int, dict[int, tuple[float, float]]] = {}
    framerate = 0.0
    for line in Path(path).read_text().splitlines():
        if not line.strip():
            continue
        if line.startswith("#"):
            if "framerate" in line:
                framerate = float(line.split(":")[1].split()[0])
            continue
        pieces = line.split()
        tracks.setdefault(int(pieces[0]), {})[int(pieces[1])] = (float(pieces[2]),
                                                                 float(pieces[3]))
    return tracks, framerate


def _number_or_text(value: str):
    """Los valores de static.txt son numeros, menos 'capa', que es el nombre de
    la variante de capa; se deja como texto en vez de romper la lectura."""
    try:
        return float(value)
    except ValueError:
        return value


def read_static(run: Path) -> dict:
    """static.txt: 'clave valor' por linea; los pares x y quedan como tupla."""
    info: dict = {}
    for line in (Path(run) / "static.txt").read_text().splitlines():
        pieces = line.split()
        if not pieces:
            continue
        key, values = pieces[0], pieces[1:]
        if len(values) == 1:
            info[key] = _number_or_text(values[0])
        else:
            info[key] = tuple(_number_or_text(value) for value in values)
    for key in ("evento", "instantes", "subdivisiones", "instantes_en_conflicto",
                "cuadro_inicial"):
        if key in info:
            info[key] = int(info[key])
    return info


def load_run(run: Path):
    """Devuelve (static, t (Nm,), simulado (Nm, 2, 7), experimental (Nm, 2, 3)).

    Las siete columnas de cada agente simulado son x y vx vy tx ty conflicto
    (tx ty es el target que la capa de elusion le puso en ese instante); las
    tres del experimental, x y presente.
    """
    run = Path(run)
    static = read_static(run)
    values = np.fromstring((run / "dynamic.txt").read_text(), sep=" ")
    frames = values.size // 15
    values = values[:frames * 15].reshape(frames, 15)
    time = values[:, 0].copy()
    simulated = np.stack([values[:, 1:8], values[:, 8:15]], axis=1)
    measured = np.loadtxt(run / "experimental.txt")
    experimental = np.stack([measured[:, 1:4], measured[:, 4:7]], axis=1)
    return static, time, simulated, experimental


# --------------------------------------------------------------------------
# Metricas y promedios
# --------------------------------------------------------------------------

def metric_errors(experimental: np.ndarray, simulated: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Las dos metricas del enunciado para UN peaton, instante por instante.

    Devuelve (e1, e2) con un NaN en los instantes sin muestra experimental:
    e1(t_k) = |r_exp(t_k) - r_sim(t_k)|^2 es el observable primario de la
    metrica 1 y e2(t_k) = min_j |r_exp(t_k) - r_sim(t_j)|^2 el de la metrica 2.
    El escalar de cada metrica es el promedio temporal de su observable
    primario sobre los instantes con muestra.
    """
    present = experimental[:, 2] > 0.5
    measured = experimental[:, :2]
    track = simulated[:, :2]
    same = np.full(len(measured), np.nan)
    closest = np.full(len(measured), np.nan)
    same[present] = np.sum((measured[present] - track[present]) ** 2, axis=1)
    distances = np.sum((measured[present, None, :] - track[None, :, :]) ** 2, axis=2)
    closest[present] = distances.min(axis=1)
    return same, closest


def read_sweep(path: Path):
    """errores.txt de `elusion sweep` -> (p1, p2, labels, E1, E2) con E1 y E2 de
    forma (len(p1), len(p2), M): el error de CADA evento, que es el promedio
    sobre sus 2 peatones. El promedio poblacional y los optimos salen de aca."""
    values = np.loadtxt(path)
    labels = np.unique(values[:, 0].astype(int))
    p1 = np.unique(values[:, 1])
    p2 = np.unique(values[:, 2])
    shape = (len(p1), len(p2), len(labels))
    event_error = {1: np.full(shape, np.nan), 2: np.full(shape, np.nan)}
    index1 = {value: i for i, value in enumerate(p1)}
    index2 = {value: i for i, value in enumerate(p2)}
    index_label = {value: i for i, value in enumerate(labels)}
    for row in values:
        i, j, k = index1[row[1]], index2[row[2]], index_label[int(row[0])]
        event_error[1][i, j, k] = 0.5 * (row[3] + row[4])
        event_error[2][i, j, k] = 0.5 * (row[5] + row[6])
    if np.isnan(event_error[1]).any():
        raise SystemExit(f"{path}: la grilla esta incompleta")
    return p1, p2, labels, event_error[1], event_error[2]


def population(event_error: np.ndarray):
    """<E>(p1, p2) y su error estandar de la media entre los M eventos."""
    mean = event_error.mean(axis=2)
    deviation = event_error.std(axis=2, ddof=1)
    return mean, deviation / np.sqrt(event_error.shape[2])


def initial_angles(event: dict) -> tuple[float, float]:
    """Angulo (grados) entre v(0) y el camino nominal (del arranque al target
    final), para el peaton izquierdo y el derecho de un evento de
    read_events(). Con la ventana recortada al tramo del corredor es chico en
    los 38 peatones: todos arrancan caminando hacia su target."""
    angles = []
    for side in ("izquierda", "derecha"):
        pedestrian = event[side]
        velocity = np.array([pedestrian["vx0"], pedestrian["vy0"]])
        nominal = np.array([pedestrian["tx"] - pedestrian["x0"],
                            pedestrian["ty"] - pedestrian["y0"]])
        cosine = velocity @ nominal / (np.linalg.norm(velocity) * np.linalg.norm(nominal))
        angles.append(float(np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))))
    return angles[0], angles[1]


def optimum(surface: np.ndarray, p1: np.ndarray, p2: np.ndarray):
    """(i, j, p1*, p2*, valor) del minimo de la superficie."""
    i, j = np.unravel_index(np.argmin(surface), surface.shape)
    return i, j, p1[i], p2[j], surface[i, j]
