# TP5 — Calibración de una capa de elusión con trayectorias experimentales

Simulación de Sistemas — ITBA. **Problema 1** del TP5: proponer una capa de
elusión de exactamente dos parámetros sobre un modelo de dinámica peatonal que
no anticipa colisiones, y calibrarla contra las trayectorias reales de 19
cruces 1 contra 1 medidos por la cátedra.

## El problema

La cátedra provee `M = 19` eventos de **elusión 1 contra 1 de frente**: en cada
prueba una persona sale de la fila izquierda y otra de la fila de abajo a la
derecha y se cruzan alrededor de `y = 2 m`. De cada peatón se tiene su
trayectoria medida `r_i^exp(t_k)` a 15,0192 cuadros por segundo
(`Δt_exp = 66,58 ms`).

El modelo elegido es **SFM sin fuerza social** (Helbing, Farkas y Vicsek 2000)
con los parámetros del paper (`m = 80 kg`, `τ = 0,5 s`, `k = 1,2·10⁵ N/m`,
`κ = 2,4·10⁵ kg/(m·s)`) y el radio del enunciado (`r = 0,25 m`). Ese modelo
sólo interactúa **por contacto**: mientras no hay solapamiento, cada agente va
derecho a su target y la única señal del otro llega cuando ya lo está tocando.

La **capa de elusión** le agrega la anticipación sin tocar el modelo: no suma
ninguna fuerza ni cambia ninguna regla, sólo reemplaza transitoriamente el
target final `T_i` por un target temporal `T_i*`, que es lo único que decide la
dirección de la velocidad deseada.

Se calibra con las dos métricas de error cuadrático medio del enunciado:

```
E(1)_i = (1/Nm) Σ_k |r_i^exp(t_k) − r_i^sim(t_k)|²          (a iguales tiempos)
E(2)_i = (1/Nm) Σ_k min_j |r_i^exp(t_k) − r_i^sim(t_j)|²    (punto más cercano)
```

El error de un evento es el promedio sobre sus 2 peatones y el poblacional,
`<E>`, el promedio sobre los 19 eventos.

## La capa de elusión

**Dos parámetros:** `p1 = ta`, el tiempo de anticipación (s), y `p2 = ds`, el
margen de espacio personal (m). Con `ta = 0` la capa está apagada y queda el
SFM puro, que es la referencia contra la que se mide todo.

**Detección.** Con `Δr = r_j − r_i` y `Δv = v_j − v_i`, se extrapolan
linealmente las dos trayectorias:

```
τ* = −(Δr · Δv)/|Δv|²        instante de mínima aproximación
d* = |Δr + Δv τ*|            separación predicha ahí
D  = r_i + r_j + ds          separación requerida
```

Hay **conflicto** si `0 < τ* ≤ ta` y `d* < D`.

**Target temporal.** Sin conflicto, `T_i* = T_i`. Con conflicto:

```
ê_i^0 = (T_i − r_i)/|T_i − r_i|
q_i   = r_i + v_i^d τ* ê_i^0                            punto de mira
ŝ     = [(r_i + v_i τ*) − (r_j + v_j τ*)]/d*            lado de la separación
w(τ*) = 1 − τ*/ta                                       peso de urgencia
T_i*  = q_i + w(τ*) (D − d*) ŝ
```

`q_i` es dónde estaría el agente al momento del conflicto si siguiera derecho a
su target; `(D − d*)` es exactamente la separación que falta; `ŝ` es el lado
hacia el que los dos ya van a estar corridos, de modo que la elusión es
**recíproca** sin que haga falta ninguna negociación.

El peso `w` hace la capa **continua en los dos bordes del disparo**: en
`τ* = ta` vale 0 y el target temporal cae sobre la recta al target final, así
que al entrar y al salir del horizonte la dirección deseada no salta; y en
`τ* → 0` vale 1 y, como ahí `q_i → r_i`, el target queda puramente lateral,
que es el límite correcto cuando el conflicto es inminente. La vuelta al target
final es automática: en cuanto se separan, `τ* ≤ 0`.

Es la geometría predictiva de Karamouzas *et al.* (2009,
`docs/bibliografia/Biblio_6_7/PCA.pdf`) —el mismo par tiempo de anticipación /
espacio personal— resuelta con un target temporal en vez de con una fuerza
evasiva, que es lo que el enunciado no permite.

### Las alternativas que se probaron

**¿Y con campos?** La intuición natural es que una capa basada en un campo de
repulsión —como el término social del SFM, pero usado para decidir la
dirección deseada y no como fuerza— tendría que funcionar. Se probaron tres,
todas de dos parámetros y todas como target temporal, con la repulsión pesada
por `A exp(−(d − 2r)/B)` (`--capa campo|campo-lateral|campo-predictivo`,
`make alternativas`, `visualization/alternatives.py`):

| capa | qué distancia y qué dirección usa | óptimo (métrica 2) | `<E(2)>` | corredor / fila | pareado contra la predictiva |
|---|---|---|---|---|---|
| **predictiva (la que corre)** | `(D − d*)` en la dirección `ŝ`, con horizonte `t_a` | 3,85 s, 0,050 m | **0,314 m² (−63 %)** | 0,081 / 0,574 | — |
| campo isotrópico | la distancia actual, de `j` a `i` (Helbing como dirección) | A = 1,0, B = 0,66 m | 0,399 m² (−52 %) | 0,244 / 0,572 | **−0,085 ± 0,027** (peor) |
| campo lateral | la distancia actual, perpendicular al camino, del lado contrario a `j` | A = 0,3, B = 4,5 m | 0,303 m² (−64 %) | 0,137 / 0,488 | +0,011 ± 0,026 (empata) |
| campo predictivo | la separación predicha `d*`, en `ŝ` (Karamouzas como target) | A = 0,25, B = 0,005 m | 0,303 m² (−64 %) | 0,054 / 0,580 | +0,011 ± 0,013 (empata) |

- El **campo isotrópico queda lejos**: de frente, la repulsión apunta hacia
  atrás y no tiene componente lateral, así que el agente frena en vez de
  correrse. Es exactamente el problema que señala la Teórica 7 para los
  modelos "particle-based" y que motiva a Karamouzas.
- Los otros dos **empatan** con la predictiva dentro de la diferencia pareada,
  pero sus óptimos **degeneran**: el predictivo se va a `B → 0`, donde el peso
  exponencial es un escalón sobre el contacto predicho (y en el corredor es un
  30 % mejor, 0,054 contra 0,081, a costa de la fila); el lateral se va a
  `B = 4,5 m`, que es empujar de costado siempre que haya alguien adelante, y
  "gana" sólo con la métrica 1 (`+0,20 ± 0,08`) porque en los eventos de la
  fila veer temprano se parece a subir por la fila: no es mejor elusión.
- La predictiva se queda porque hace lo mismo con dos parámetros que tienen
  **unidades y lectura directa** (un tiempo de anticipación y un margen de
  espacio personal, el par de la Teórica 7) y porque es continua en los dos
  bordes del disparo.

Dentro de la predictiva, las dos decisiones de diseño también tienen
alternativa, y las cuatro combinaciones se corrieron con el mismo barrido y
los mismos 19 eventos (`--sin-rampa` y `--mira-horizonte`):

| variante | peso de urgencia | punto de mira | `<E(1)>` mín. | `<E(2)>` mín. |
|---|---|---|---|---|
| **la que corre** | `w = 1 − τ*/ta` | `v^d τ*` | 1,480 | 0,315 |
| sin rampa | `w = 1` | `v^d τ*` | 1,472 | 0,309 |
| mira al horizonte | `w = 1 − τ*/ta` | `v^d ta` | 1,478 | 0,316 |
| ninguna de las dos | `w = 1` | `v^d ta` | 1,456 | 0,313 |

Las cuatro dan lo mismo dentro del 2 %, que está muy por debajo del error
estándar de la media entre eventos (0,25 m² en la métrica 1). Se eligió la
primera porque es la única **continua** en los dos bordes del disparo, y porque
el punto de mira en el instante del conflicto es el que el esquema de la
presentación puede explicar en una línea.

## Estructura

```
tp-5/
├── Makefile            # todo el flujo desde la raíz: build, eventos, barrido, figuras, animaciones, entrega
├── README.md           # este documento
├── PLAN.md             # qué pide el enunciado, cómo se resuelve, decisiones y dudas a la cátedra
├── FEEDBACK.md         # devoluciones de la cátedra (TP2, TP3 y TP4) aplicadas al TP5
├── requirements.txt    # matplotlib, numpy
├── docs/
│   ├── enunciado/      # TP5_Enunciado.pdf
│   ├── teoria/         # Teóricas 5, 6 y 7
│   └── bibliografia/   # Biblio_6_7 (SFM, CPM, PCA, elusión) y BiblioGranulares; los zip originales quedan fuera de git
├── experimental/       # los datos de la cátedra, sin tocar, y la tabla de eventos del LEEME
├── engine/             # C++17: el motor (va en el zip de entrega con animate.py y common.py)
├── visualization/      # Python: post-procesamiento, figuras y animaciones
├── report/             # presentacion.tex (beamer 16:9), comun.tex, figuras/*.tikz y guion.md (qué decir en cada una, con tiempos); build/ ignorado
├── slides-images/      # todas las imágenes de la presentación, numeradas por diapositiva
├── youtube/            # titulos.md con el título y la descripción de cada video (los .mp4 no se versionan)
├── gif/                # los videos como GIF, para embeber en la presentación en vivo
└── data/               # salidas de simulación y figuras (ignoradas por git)
    ├── experimental/   #   resumen de los 19 eventos tal como los lee el motor
    ├── convergencia/   #   barrido del paso de integración
    ├── barrido/        #   grueso/ y fino/: las dos grillas de (p1, p2)
    ├── runs/           #   corridas con cuadros: los dos óptimos y la capa apagada
    └── figures/, figuras_diapositivas/   # figuras por ítem, en estilo de revisión y de diapositiva
```

## Flujo

```bash
pip install -r requirements.txt
make build                 # engine/build/elusion
make eventos               # lee los datos de la cátedra y escribe el resumen de los 19 eventos
make eventos-figuras       # las 38 trayectorias medidas y d(t) de cada evento
make convergencia          # barrido del paso de integración
make convergencia-figuras  # apartamiento de <E> contra dt
make barrido               # ítems b, c y d: la grilla gruesa (4 s), la fina (62 s) y el barrido largo de p1
make alternativas          # las tres capas de campo, cada una en su grilla (2 min)
make alternativas-figuras  # la comparación de las cuatro capas
make corridas              # los 19 eventos con cada óptimo y con la capa apagada
make check                 # validación: métricas recalculadas en Python, contactos, grilla temporal
make poblacional-figuras   # ítem b: superficie <E>(p1,p2) y cortes, por métrica
make individual-figuras    # ítem c: óptimos individuales y error por evento
make residuo-figuras       # de dónde viene el error que queda: ritmo/forma y lado
make validacion-figuras    # ítem d: validación cruzada
make trayectorias-figuras  # ítem a: trayectorias, observable primario y d(t) de los eventos elegidos
make animations            # videos y el cuadro fijo de cada uno, congelado en el último instante en conflicto antes del cruce simulado
make apoyo                 # animaciones de apoyo: la capa cabeza a cabeza con tres p2, y qué hace cada parámetro en el evento 10
make youtube               # copia los videos con nombres legibles en youtube/
make gifs                  # los videos como GIF en gif/
make figuras               # todas las figuras de análisis, en los dos estilos
make slides-images         # las 35 imágenes de la presentación, numeradas por diapositiva
make documentos            # report/presentacion.tex -> report/build/presentacion.pdf
make entrega               # SdS_TP5_2026Q2G10S2_Codigo.zip y ..._Presentación.pdf
make todo                  # eventos + convergencia + barrido + corridas
```

## Motor

C++17, sin dependencias. Cuatro comandos:

```bash
cd engine && make
./build/elusion events                                     # verifica la lectura de los datos
./build/elusion run --pruebas 10 --p1 2.5 --p2 0.07        # una corrida con cuadros
./build/elusion sweep --p1 0:4:81 --p2 0:0.6:61            # la grilla de parámetros
./build/elusion convergence --subdivisiones 1,2,4,...,512  # el paso de integración
```

Opciones comunes: `--datos` y `--eventos` (los archivos de la cátedra),
`--pruebas 1,5,10` (qué eventos), `--arranque 0.3` (el umbral de caminata, ver
abajo), `--subdivisiones 64` (el paso), `--dir` (dónde escribir). Los
parámetros del modelo se pueden pisar (`--m 80 --r 0.25 --tau 0.5 --kn 1.2e5
--kt 2.4e5`), y las dos variantes de la capa con `--sin-rampa` y
`--mira-horizonte`.

### Cómo arma los eventos

El motor lee el archivo crudo de la cátedra (`id cuadro x y markerID`) y la
tabla de eventos (`m id_izquierda id_derecha cuadro_inicial cuadro_final`,
copiada del LEEME) y, por cada prueba, recorta la ventana en dos pasos:

1. **Intersección**: desde el primer cuadro en que los dos peatones están
   seguidos hasta el último, *dentro* del intervalo que declara el LEEME. El
   recorte al intervalo del LEEME va primero porque un mismo peatón aparece en
   varias pruebas (haciendo la fila) y sus cuadros extremos en el archivo no
   son los de su prueba.
2. **Caminata**: la parte en que los dos miden una rapidez de al menos
   `--arranque` (0,3 m/s por defecto, con una diferencia centrada sobre ±2
   cuadros).

El segundo recorte no es cosmético. El enunciado habla de dos peatones *que
caminan en curso de colisión*, y al principio de varias pruebas uno de los dos
está **parado haciendo la fila**: en la prueba 14 los dos están quietos los
primeros 4 s de los 13. Con el peatón quieto adentro de la ventana, la rapidez
media —que es el módulo de la velocidad deseada— baja de 1,2 a 0,76 m/s, y el
agente simulado arranca a caminar en `t = 0` contra un peatón que no se movió
en cuatro segundos. Con el umbral de 0,3 m/s se pierde el **9 %** de los
instantes (2787 → 2543) y las **19 distancias mínimas siguen adentro de la
ventana**: el cruce nunca se recorta. El error poblacional sin capa baja de
3,05 a 2,73 m² y el calibrado, de 1,70 a 1,48 m².

De esa ventana salen, por peatón, las condiciones que el enunciado fija:
posición y velocidad iniciales (la velocidad, como diferencia finita sobre 5
cuadros: una diferencia entre cuadros consecutivos mide el ruido del
seguimiento, 0,08 m/s sobre una rapidez de 0,9), target final (la última
posición medida) y rapidez deseada (el largo del camino medido sobre su
duración).

Los **huecos de seguimiento** que quedan adentro —uno solo de los 38 peatones,
32 instantes— **no se interpolan**: el agente se simula igual, porque hace
falta para acoplarlo con el otro, pero el error no se evalúa en los instantes
sin muestra.

El peatón que el LEEME deja sin identificar en la prueba 2 (`sale izquierda
V?`) es el **id 1000**: es la única trayectoria de esa ventana que va de
izquierda a derecha y no está asignada a ninguna otra prueba. Queda anotado en
`experimental/eventos.txt`.

### Integración

Beeman predictor-corrector (Teórica 4, diapositiva 20), que es el esquema que
la teórica da para fuerzas que dependen de la velocidad: acá la fuerza depende
de `v` por dos lados, el término de conducción y la fricción tangencial del
contacto. El primer paso usa `a(−Δt) = a(0)`.

El paso es `dt = Δt_exp / n` con `n` **entero**, de modo que cada instante
experimental cae exactamente en un paso de la simulación y las dos
trayectorias se comparan sin interpolar. `make convergencia` barre `n` de 1 a
512: la tolerancia del 0,01 % contra el paso más fino se cumple desde `n = 16`
y se usa **`n = 64`** (`dt = 1,04 ms`), que ya está en el piso de 0,001 % y
hace que el barrido fino entero tarde un minuto.

### Salida

- `sweep` con `--p1 0:8:33` (`make barrido` lo corre aparte, en la `p2` de cada
  óptimo) es el barrido largo con el que se justifica el techo de la grilla.
- `events` escribe `eventos_resumen.txt`: una línea por evento con la ventana,
  las muestras de cada peatón y sus condiciones iniciales, target y rapidez
  deseada.
- `run` escribe, por evento, `static.txt` (los parámetros de la corrida),
  `dynamic.txt` (por instante experimental, una línea con `t` y dos líneas
  `x y vx vy tx ty conflicto`, una por agente, con `tx ty` el target que la
  capa le puso) y `experimental.txt` (las trayectorias medidas sobre la misma
  grilla, con una bandera de presencia).
- `sweep` escribe `errores.txt`: una línea `m p1 p2 E1_izq E1_der E2_izq E2_der`
  por evento y por par de la grilla.
- `convergence` escribe `convergencia.txt`: `n dt <E1> <E2> ms`.

### Qué calcula el motor y qué no

El motor **sí** calcula las dos métricas, y es la única excepción a la regla
del TP3 y el TP4 de que los observables salen del post-procesamiento: el
barrido fino son 93 879 corridas y volcar las trayectorias de todas para
medirlas después serían decenas de GB. Lo que el motor **no** hace es ningún
promedio ni ninguna decisión: el error poblacional, los óptimos individuales,
la región compatible y las particiones de la validación cruzada se calculan en
Python sobre ese mismo archivo. Y `visualization/check.py` **recalcula las dos
métricas desde las trayectorias** de una corrida y las compara con lo que
informó el motor, para que el camino corto esté verificado contra el largo.

## Post-procesamiento

| Script | Ítem | Qué hace |
|---|---|---|
| `common.py` | — | lectura de los archivos del motor y del archivo crudo de la cátedra, las dos métricas instante por instante, promedios poblacionales, estilos `informe`/`diapositiva` y `save()` con coma decimal en los ejes |
| `events.py` | datos | las 38 trayectorias medidas en el plano y la distancia entre los dos peatones de cada evento contra el tiempo; por consola, la tabla de los 19 eventos |
| `convergence.py` | dt | apartamiento relativo de `<E>` contra `dt` en doble logarítmica, con la tolerancia y el paso usado marcados |
| `trajectory.py` | a | por evento: trayectorias medidas y simuladas superpuestas (con la corrida sin capa de fondo y el cruce marcado en las dos), el observable primario `e(t)` de las dos métricas con su promedio temporal, y la distancia entre los dos peatones con `2r` y `D` marcados |
| `animate.py` | a | animación del evento (un cuadro por instante medido: a 15 cuadros por segundo corre en tiempo real) y cuadro fijo con `--cruce`, congelado en el instante de mínima aproximación simulada |
| `population.py` | b | mapa de `<E>(p1,p2)` con escala de color de potencia y curvas de nivel en múltiplos del mínimo, el óptimo y el contorno de la región compatible; los dos cortes por el óptimo con barras de error y la franja de los valores que empatan |
| `individual.py` | c | los 19 óptimos individuales en el plano `(p1,p2)` con el poblacional marcado, y el error de cada evento con los parámetros poblacionales contra los propios |
| `residual.py` | c | de dónde viene el error que queda: las **dos poblaciones** de eventos (los que ya caminan por el corredor y los que salen de la fila, separadas por el ángulo entre `v(0)` y el camino nominal), `E(1)_m` abierto en la componente a lo largo del camino nominal (ritmo, o ruta en los de la fila) y la perpendicular (forma), y el desvío lateral en el cruce medido contra simulado, que dice si el modelo eludió por el mismo lado |
| `alternatives.py` | capa | la tabla y la figura de las tres capas de campo contra la predictiva: óptimo de cada una en su grilla, error por población y diferencia pareada |
| `support.py` | apoyo | las animaciones de apoyo: un cruce sintético cabeza a cabeza con tres `p2` a la vez, dibujando lo que la capa calcula (posiciones predichas en `τ*`, `d*`, target temporal), y el evento 10 con cada parámetro recorriendo su rango al lado del corte de `<E>` (video y resumen estático con cuatro valores superpuestos) |
| `crossval.py` | d | validación cruzada: distribución del error de validación contra el del ítem b, el par calibrado en cada partición y el error contra el tamaño del conjunto de entrenamiento; también deja-uno-afuera |
| `check.py` | — | validación de las corridas: recalcula las dos métricas, verifica que la grilla temporal sea la experimental y que las condiciones iniciales sean las medidas, e informa el solapamiento y el exceso de rapidez (que miden cuánto contacto queda) |

El nombre de cada eje es el **símbolo del enunciado con su unidad**
(`p_1 = t_a (s)`, `<E^(1)> (m²)`, `d (m)`), no la frase que lo describe; entra
siempre en una sola línea, los números llevan coma decimal y la leyenda va
adentro del gráfico sin tapar datos.

Una **barra de error** sobre `<E>` es el error estándar de la media entre
eventos, `σ/√M`. Para decidir qué pares **empatan** con el óptimo esa barra no
sirve: mide la dispersión entre eventos, que es enorme comparada con las
diferencias entre pares, y con ella el 70 % de la grilla "empata". Como todos
los pares se evalúan sobre los **mismos** 19 eventos, lo que corresponde es la
diferencia **pareada**: un par empata si la media de `E_m(p) − E_m(p*)` no
supera su propio error estándar.

## Resultados

### Ítem b: calibración poblacional

| | métrica 1 (iguales tiempos) | métrica 2 (punto más cercano) |
|---|---|---|
| sin capa (`p1 = 0`) | 2,735 m² (RMS 1,65 m) | 0,838 m² (RMS 0,92 m) |
| óptimo | **2,50 s, 0,070 m** | **3,85 s, 0,050 m** |
| `<E>` en el óptimo | 1,477 ± 0,253 m² (RMS 1,22 m) | 0,314 ± 0,074 m² (RMS 0,56 m) |
| cuánto baja la capa | **46 %** | **63 %** |
| región compatible | `p1` 0,85–4,00 s, `p2` 0,05–0,42 m (1482 pares) | `p1` 2,95–4,00 s, `p2` 0,02–0,09 m (129 pares) |
| distancia de paso `D = 2r + p2` | 0,570 m | 0,550 m |

Los dos óptimos difieren en `p1` y coinciden en `p2`, e **intercambiarlos
cuesta menos del 2 %** en cualquiera de las dos métricas: las dos eligen
esencialmente la misma capa. La diferencia es estadísticamente significativa
con el test pareado —las dos superficies se miden sobre los mismos 19
eventos— pero irrelevante en magnitud.

El techo de la grilla, `p1 = 4 s`, se verifica con un barrido aparte hasta 8 s
(`data/barrido/p1largo`, figura `techo_p1`): entre 4 y 8 s la diferencia
pareada de `<E>` es `+0,05 ± 0,04 m²` con la métrica 1 y `0,000 ± 0,007 m²`
con la 2, compatible con cero. Con la rampa de urgencia `p1` sigue entrando en
`w` aunque el conflicto ya se detecte desde el primer instante, así que la
superficie nunca es exactamente plana; pero lo que se mueve es menos que lo que
se puede resolver con 19 eventos.

`p1` queda determinado **sólo por abajo**: `<E>` cae de 2,73 a 1,5 m² entre 0 y
1,2 s y después es plano dentro del error pareado. Es físico y no un artefacto
de la parametrización: con más de un segundo de anticipación el agente ya llega
a correrse lo que necesita, y adelantar la reacción no cambia por dónde pasa.
Las cuatro variantes de la capa (tabla de arriba) dan la misma meseta. `p2` sí
tiene un mínimo claro y sube monótono después: es el parámetro que fija por
dónde pasa.

### Ítem c: calibración individual

| | métrica 1 | métrica 2 |
|---|---|---|
| `p1` individual (mediana, rango) | 1,35 s (0,00–4,00) | 3,40 s (0,00–4,00) |
| `p2` individual (mediana, rango) | 0,050 m (0,000–0,480) | 0,050 m (0,000–0,600) |
| eventos con `p1 = 0` | 4 de 19 | 2 de 19 |
| `<E_m>` con los poblacionales | 1,477 m² | 0,314 m² |
| `<E_m>` con los individuales | 1,219 m² | 0,296 m² |
| **cuánto se gana** | **17,5 %** | **5,9 %** |

Es poco para 19 pares de parámetros contra uno. El error que queda **no está en
los parámetros**.

### De dónde viene el error que queda

**Los eventos son dos poblaciones.** El ángulo entre la velocidad inicial
medida de cada peatón y su camino nominal (del arranque al target final) es
bimodal: o es menor que 32° o mayor que 60°, sin nada en el medio. En 10
eventos los dos peatones **ya caminan por el corredor** y en 9 al menos uno
**sale de la fila**, perpendicular al corredor (eventos 6, 7, 8, 9, 11, 13, 14,
18 y 19; el recorte de la ventana a `|v| ≥ 0,3 m/s` saca el tiempo parado,
pero no el tramo en que caminan por la fila). En los segundos la recta al
target es la **ruta equivocada** —la persona sube por la fila y recién
después dobla al corredor— y eso lo fija la condición del enunciado para el
target, no la capa de elusión:

| con los parámetros poblacionales | ya en el corredor (10) | sale de la fila (9) |
|---|---|---|
| `<E(1)>` | 0,78 m² | 2,25 m² |
| `<E(2)>` | **0,08 m²** | **0,57 m²** |
| mismo lado que las personas | 6 de 10 | 6 de 9 |

Calibrando **sólo con los 10 del corredor** (`population.py --clase corredor`),
el óptimo de la métrica 2 es `(4,00 s, 0,070 m)` con `<E(2)> = 0,078 m²` (RMS
0,28 m), **un 92 % menos que sin capa**, y el de la métrica 1 `(4,00 s, 0,080
m)` con 0,663 m² (−78 %): el mismo `p2` que con los 19, y la capa hace casi
todo el trabajo. Sólo con los 9 de la fila, la capa apenas baja el error un 19 %
y el óptimo se va a `p2 ≈ 0`. Como referencia, la calibración del AA-CPM de la
cátedra sobre su propio experimento de dos peatones da un error medio de 0,24 m
(Martin y Parisi 2024, distancia media al punto más cercano): el mismo orden
que el RMS de 0,28 m del corredor.

Con los parámetros poblacionales de la métrica 1, además:

- **En el corredor, el 88 % de `<E(1)>` va a lo largo del camino nominal** (0,69
  de 0,78 m²): es **ritmo**, el agente camina a velocidad deseada constante y las
  personas aceleran, frenan y vuelven a acelerar. La forma —lo que la capa
  decide— es el 12 %. En los de la fila la componente longitudinal también
  lleva la ruta (73 %) y la perpendicular es cinco veces mayor que en el
  corredor. Sobre los 19, 77 % y 23 %.
- **El modelo elude por el mismo lado que las personas en 12 de los 19
  eventos** (6 de 10 en el corredor). Esos 12 tienen `<E(1)> = 1,32 m²` y los
  otros 7, 1,75 m². La capa decide el lado con la geometría recíproca a partir
  de las velocidades del momento, y de frente lo decide un corrimiento de
  centímetros; las personas lo deciden antes y por otros motivos: en 14 de los
  19 cruces pasaron **cada uno por su derecha**, que es una convención que el
  modelo no tiene. El evento 3 es el caso limpio: en el corredor, la elusión
  correcta (pasan a 0,57 m contra 0,60 m medidos) pero en espejo.
- **Contacto.** Sin la capa hay contacto en 17 de los 19 eventos (solapamiento
  de hasta 4,4 cm); con la capa calibrada, en 7 (hasta 0,7 cm). En los datos,
  un solo evento tiene distancia mínima por debajo de `2r`.

### Ítem d: validación cruzada

| | métrica 1 | métrica 2 |
|---|---|---|
| ítem b (calibra y mide con los 19) | 1,477 m² | 0,314 m² |
| entrenamiento (500 particiones de 13/6) | 1,466 ± 0,182 m² | 0,315 ± 0,052 m² |
| validación | 1,554 ± 0,383 m² (**+5,2 %**) | 0,315 ± 0,111 m² (**+0,2 %**) |
| dejando uno afuera (19 de 18/1) | 1,571 m² (+6,4 %) | 0,316 m² (+0,4 %) |

Con dos parámetros y 19 eventos **no hay sobreajuste**: lo calibrado sobre una
parte vale para la otra. El par calibrado sí cambia de partición en partición
(52 pares distintos en 500 particiones, el más frecuente en el 26 %), y la
dispersión está casi toda en `p1`: es la misma conclusión que la región
compatible del ítem b, medida de otra manera.

## Presentación

`report/presentacion.tex` es la presentación de referencia en beamer 16:9 y
sigue la guía de la cátedra, las devoluciones de `FEEDBACK.md` y el esquema que
funcionó en el TP3 y el TP4: sin diapositiva de contenido, sólo separadores de
sección; UML del motor sin archivos ni post-proceso; tabla de parámetros en
bloques con las unidades en un solo lugar; una diapositiva define los
observables matemáticamente; en Resultados, un bloque por ítem, cada
diapositiva con el gráfico grande más dos o tres viñetas; conclusiones como
punteo corto y sólo con cifras que estén en las figuras mostradas; y la
declaración de uso de agentes de IA al final.

Como pide el enunciado, **a la capa de elusión se le dedican tres diapositivas
seguidas** (la detección del conflicto, el target temporal y los casos límite),
más la animación de apoyo y la comparación con las capas de campo (`8b`), que
es más de lo habitual para una introducción matemática. `report/guion.md`
tiene qué decir en cada diapositiva, con el tiempo de cada una (13:00 en
total) y un reparto entre los tres expositores.

Los esquemas de las diapositivas (el experimento, los dos de la capa de
elusión, el UML, el bucle, la tabla de parámetros y el esquema del evento)
están en `report/figuras/*.tikz`; `presentacion.tex` los lee con `\input` y
`make slides-images-tikz` los renderiza sueltos a PNG en `slides-images/`, con
los mismos colores (`report/comun.tex`). Así en `slides-images/` está **toda**
imagen que aparece en la charla, numerada por la diapositiva en la que va: es
la carpeta con la que se arma la presentación a mano en Google Slides.

**La presentación que se expone** se arma en Google Slides con esas imágenes y
los GIF de `gif/`. La beamer de referencia tiene 34 diapositivas de contenido,
más de lo que entra en 13 minutos: las prescindibles son, en este orden, 19
(distancia del evento 10), 24 (cortes de la métrica 2, dejando la comparación
de óptimos en viñetas), 33 (parámetros por partición), 31 (evento 3, que se
puede contar sobre la figura del lado), 29 (ritmo y forma, cuya cifra cabe en
la de las dos poblaciones) y 14 (paso de integración, que puede ser una
viñeta). Las imágenes con sufijo `b` y `c` (`20b`, `21b`, `27b`, `27c`, `33b`)
son opcionales: no van en la beamer y están por si hacen falta en una pregunta.

Las **animaciones de apoyo** (`make apoyo`) son tres: el cruce sintético cabeza
a cabeza con tres `p2` a la vez, que muestra en vivo lo que la capa calcula
(diapositiva 8), y el evento 10 con `p2` y con `p1` recorriendo su rango al
lado del corte de `<E>` (diapositiva 20). Son GIF para la charla en vivo, igual
que las cinco animaciones de eventos.

Los links de YouTube de la beamer dicen `PENDIENTE-0n`: hay que reemplazarlos
por los reales en `report/presentacion.tex` (y en la presentación de Google
Slides) una vez subidos los cinco videos de `youtube/`.

**Los videos se suben como "no listado", nunca privados**, y hay que abrir cada
link desde una ventana de incógnito antes de entregar: en el TP4 la cátedra no
pudo verlos y lo marcó como el problema importante de la entrega.

El zip de código que se entrega es el **motor de simulación** (`engine/`) más
**el código con el que se hacen las animaciones** a partir de las salidas
primarias (`visualization/animate.py` y `common.py`, del que depende), más la
tabla de eventos, como pidió la cátedra en el TP3.
