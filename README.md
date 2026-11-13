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

**Dos parámetros:** `t_a`, el tiempo de anticipación (s), y `d_s`, el
margen de espacio personal (m). Con `ta = 0` la capa está apagada y queda el
SFM puro, que es la referencia contra la que se mide todo. Son el `p1` y el `p2` del
enunciado: esos nombres sólo quedan en las opciones del motor (`--p1`, `--p2`)
y en las columnas de sus archivos; en las figuras y en el texto van siempre
`t_a` y `d_s`.

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

| capa | qué distancia y qué dirección usa | óptimo (métrica 2) | `<E(2)>` | pareado contra la predictiva |
|---|---|---|---|---|
| **predictiva (la que corre)** | `(D − d*)` en la dirección `ŝ`, con horizonte `t_a` | 1,50 s, 0,14 m | **0,019 m² (−94 %)** | — |
| campo isotrópico | la distancia actual, de `j` a `i` (Helbing como dirección) | A = 1,4, B = 1,1 m | 0,111 m² (−66 %) | **−0,092 ± 0,011** (peor) |
| campo lateral | la distancia actual, perpendicular al camino, del lado contrario a `j` | A = 0,2, B = 5,0 m (borde) | 0,014 m² (−96 %) | +0,005 ± 0,002 (mejor) |
| campo predictivo | la separación predicha `d*`, en `ŝ` (Karamouzas como target) | A = 0,2, B = 0,2 m (borde) | 0,023 m² (−93 %) | −0,004 ± 0,008 (empata) |

- El **campo isotrópico queda lejos**: de frente, la repulsión apunta hacia
  atrás y no tiene componente lateral, así que el agente frena en vez de
  correrse. Es exactamente el problema que señala la Teórica 7 para los
  modelos "particle-based" y que motiva a Karamouzas.
- El **campo predictivo empata** con la predictiva dentro de la diferencia
  pareada.
- El **campo lateral da un error algo menor** (0,014 contra 0,019 m² con la
  métrica 2, y 0,045 contra 0,062 con la 1; la diferencia pareada es
  significativa), y hay que decirlo. Pero su óptimo está en el **borde de la
  grilla**, `B = 5 m`: con ese alcance el peso exponencial casi no depende de
  la distancia, y la capa es "empujar de costado siempre que haya alguien
  adelante". Funciona en un corredor con un solo cruce de frente porque ahí
  correrse temprano y siempre es justo lo que hacen las personas; no tiene un
  horizonte ni una distancia de paso.
- La predictiva se queda porque sus dos parámetros tienen **unidades y lectura
  directa** (un tiempo de anticipación y un margen de espacio personal, el par
  de la Teórica 7), porque es continua en los dos bordes del disparo y porque
  no elude cuando no hay conflicto.

Dentro de la predictiva, las dos decisiones de diseño también tienen
alternativa.
Las cuatro combinaciones se corrieron con el mismo barrido (41 × 31) y los
mismos 19 eventos (`--sin-rampa` y `--mira-horizonte`):

| variante | peso de urgencia | punto de mira | `<E(1)>` mín. | `<E(2)>` mín. | pareado contra la que corre (métrica 2) |
|---|---|---|---|---|---|
| **la que corre** | `w = 1 − τ*/ta` | `v^d τ*` | 0,063 | 0,019 | — |
| sin rampa | `w = 1` | `v^d τ*` | 0,051 | 0,016 | +0,003 ± 0,0003 (mejor) |
| mira al horizonte | `w = 1 − τ*/ta` | `v^d ta` | 0,111 | 0,029 | −0,010 ± 0,006 (peor, en el borde de `d_s`) |
| ninguna de las dos | `w = 1` | `v^d ta` | 0,042 | 0,013 | +0,006 ± 0,0003 (mejor) |

**Con la ventana recortada las cuatro ya no dan lo mismo**, y hay que decirlo:
sacar la rampa baja el error un 15–20 %, y sacar la rampa y mirar al horizonte,
un 30 %. (Con la ventana anterior, que incluía la fila, las cuatro empataban
dentro del 2 %: el error estaba dominado por otra cosa.) La que corre sigue
siendo la primera por dos motivos que no son el número: es la única
**continua** en los dos bordes del disparo —sin rampa, la dirección deseada
salta cuando `τ*` cruza `ta`— y es la que se discutió con la cátedra. Todas
bajan el error más de un 85 % respecto del modelo sin capa, así que la
conclusión del trabajo no depende de cuál se elija; cambiarla queda como
**pregunta para la consulta** (`PLAN.md` §8).

## Estructura

```
tp-5/
├── Makefile            # todo el flujo desde la raíz: build, eventos, barrido, figuras, animaciones, entrega
├── README.md           # este documento
├── PLAN.md             # qué pide el enunciado, cómo se resuelve, decisiones y dudas a la cátedra
├── FEEDBACK.md         # devoluciones de la cátedra (TP2, TP3, TP4 y las consultas del TP5) aplicadas
├── IA.md               # las libertades que se tomó el agente y cómo se corrigió cada una (de ahí sale el apéndice)
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
│   └── todos/          #   los 19 eventos sueltos, un GIF por evento
└── data/               # salidas de simulación y figuras (ignoradas por git)
    ├── experimental/   #   resumen de los 19 eventos tal como los lee el motor
    ├── convergencia/   #   barrido del paso de integración
    ├── barrido/        #   grueso/ y fino/: las dos grillas de (t_a, d_s); p1largo/; alternativas/
    ├── ventana/        #   la calibración con otros tramos de x (make ventana)
    ├── individual/     #   ítem c opcional: los 4 parámetros por evento
    ├── asimetria/      #   extra: el barrido de (d_s, α)
    ├── runs/           #   corridas con cuadros: los dos óptimos y la capa apagada
    └── figures/, figuras_diapositivas/   # figuras por ítem, en estilo de revisión y de diapositiva
```

## Flujo

```bash
pip install -r requirements.txt
make build                 # engine/build/elusion
make eventos               # lee los datos de la cátedra y escribe el resumen de los 19 eventos
make eventos-figuras       # las 38 trayectorias con el tramo del recorte marcado, y d(t) de cada evento
make ventana               # cuánto cambia la calibración al mover el tramo de x (3 min)
make convergencia          # barrido del paso de integración
make convergencia-figuras  # apartamiento de <E> contra dt
make barrido               # ítems b, c y d: la grilla gruesa, la fina (32 s) y el barrido largo de t_a
make alternativas          # las tres capas de campo, cada una en su grilla (1 min)
make alternativas-figuras  # la comparación de las cuatro capas
make corridas              # los 19 eventos con cada óptimo y con la capa apagada
make check                 # validación: métricas recalculadas en Python, contactos, grilla temporal
make poblacional-figuras   # ítem b: mapa de <E>(t_a,d_s) y cortes, por métrica
make individual-figuras    # ítem c: histogramas de los óptimos individuales y error por evento
make pares                 # ítem c opcional: los 4 parámetros por evento, 2 por peatón (5 min con 8 hilos)
make pares-figuras         # ítem c opcional: histogramas de los óptimos por peatón y el error con 1, 2 y 4 juegos
make residuo-figuras       # de dónde viene el error que queda: ritmo/forma y lado
make validacion-figuras    # ítem d: validación cruzada
make trayectorias-figuras  # ítem a: los cuatro eventos representativos, observable primario y d(t)
make asimetria             # extra: t_a fijo y barrido del par (d_s, α)
make asimetria-figuras     # extra: <E>(α), histograma de α por evento y α calibrado contra medido
make animations            # videos de los cuatro eventos, su cuadro fijo y los 19 eventos a la vez
make apoyo                 # animaciones de apoyo: la capa paso a paso, cabeza a cabeza y qué hace cada parámetro
make youtube               # copia los videos con nombres legibles en youtube/
make gifs                  # los videos como GIF en gif/, más los 19 eventos sueltos (gif/todos/) y las tandas
make pares-noche           # ítem c opcional sobre la grilla fina (81 × 61 por agente): ~11 h con 8 hilos, se reanuda solo
make figuras               # todas las figuras de análisis, en los dos estilos
make slides-images         # las imágenes de la presentación, numeradas por diapositiva
make documentos            # report/presentacion.tex -> report/build/presentacion.pdf
make entrega               # SdS_TP5_2026Q2G10S2_Codigo.zip y ..._Presentación.pdf
make todo                  # eventos + convergencia + barrido + alternativas + corridas + asimetria
```

## Motor

C++17, sin dependencias. Seis comandos:

```bash
cd engine && make
./build/elusion events                                     # verifica la lectura de los datos
./build/elusion run --pruebas 10 --p1 2.15 --p2 0.13       # una corrida con cuadros
./build/elusion sweep --p1 0:4:81 --p2 0:0.6:61            # la grilla de parámetros
./build/elusion pairs --p1 0:4:17 --p2 0:0.6:25            # los 4 parámetros por evento (2 c opcional)
./build/elusion asymmetry --p1 2.15 --alfas 0:1:41         # extra: el reparto de la elusión
./build/elusion convergence --subdivisiones 1,2,4,...,512  # el paso de integración
```

Opciones comunes: `--datos` y `--eventos` (los archivos de la cátedra),
`--pruebas 1,5,10` (qué eventos), `--xmin 1.0` y `--xmax 7.7` (el tramo del
corredor al que se recorta la ventana, ver abajo), `--subdivisiones 64` (el
paso), `--dir` (dónde escribir). Los parámetros del modelo se pueden pisar
(`--m 80 --r 0.25 --tau 0.5 --kn 1.2e5 --kt 2.4e5`), y las dos variantes de la
capa con `--sin-rampa` y `--mira-horizonte`.

### Cómo arma los eventos

El motor lee el archivo crudo de la cátedra (`id cuadro x y markerID`) y la
tabla de eventos (`m id_izquierda id_derecha cuadro_inicial cuadro_final`,
copiada del LEEME) y, por cada prueba, arma la ventana en dos pasos:

1. **Intersección**: desde el primer cuadro en que los dos peatones están
   seguidos hasta el último, *dentro* del intervalo que declara el LEEME. El
   recorte al intervalo del LEEME va primero porque un mismo peatón aparece en
   varias pruebas (haciendo la fila) y sus cuadros extremos en el archivo no
   son los de su prueba.
2. **Tramo del corredor**: del primer al último cuadro en que los dos
   peatones están en `1,0 m ≤ x ≤ 7,7 m`.

De esa ventana salen, por peatón, las condiciones que el enunciado fija:
posición y velocidad iniciales (la velocidad, como diferencia finita sobre 5
cuadros: una diferencia entre cuadros consecutivos mide el ruido del
seguimiento), target final (la última posición medida) y rapidez deseada (el
largo del camino medido sobre su duración).

El peatón que el LEEME deja sin identificar en la prueba 2 (`sale izquierda
V?`) es el **id 1000**: es la única trayectoria de esa ventana que va de
izquierda a derecha y no está asignada a ninguna otra prueba. Queda anotado en
`experimental/eventos.txt`.

### El recorte de la ventana

La ventana que declara el LEEME es mucho más larga que el cruce: al principio
los peatones todavía están en la fila (parados, o caminando hacia la cabecera)
y al final frenan y doblan hacia la fila de la vuelta siguiente. Si eso queda
adentro, las condiciones que el enunciado saca de la trayectoria salen mal: la
rapidez media —que es el módulo de la velocidad deseada— queda por debajo de
la que el peatón camina, y el target final —la última posición medida— cae
fuera del corredor.

El recorte es **una restricción sobre el eje `x`, la misma para los 19
eventos**. Sale de mirar las 38 trayectorias enteras superpuestas
(`slides-images/slide-03-eventos-trayectorias.png`): se ve de dónde parten
todos. Las cabeceras de las dos filas están en `x ≈ 0,6 m` (donde esperan los
que salen por la izquierda) y en `x ≈ 8,1 m` (los de la derecha), y entre una y
otra los peatones caminan por el corredor. El tramo que se simula es

```
1,0 m ≤ x ≤ 7,7 m        (0,4 m adentro de cada cabecera)
```

y la ventana de un evento empieza cuando el último de los dos entra al tramo y
termina cuando el primero de los dos sale. Es lo que pidió la cátedra en la
consulta del 11/11 (`FEEDBACK.md`): un rango fijo leído de la figura, en lugar
del criterio anterior (una fracción del percentil 75 de la rapidez de cada
peatón más una banda en `y`), que se sacó entero.

Con ese tramo (`make eventos-figuras`):

| | |
|---|---|
| instantes | 1346 de los 3941 que declara el LEEME (34 %) |
| `Nm` por evento | 42 a 80 (2,8 a 5,3 s) |
| `v_d` | 1,15 a 1,63 m/s, media 1,32 |
| ángulo entre `v(0)` y la recta al target | mediana 5°, máximo 29° |
| `y` del target final | 1,68 a 2,22 m (el corredor está en `y ≈ 2`) |
| el cruce cae en | entre el 47 % y el 80 % de la ventana |
| huecos de seguimiento adentro | ninguno |

El evento 1 es el más corto (`Nm = 42`) porque al peatón 36 se le corta el
seguimiento 32 cuadros justo después del cruce: su última muestra antes del
hueco está en `x = 3,45 m`, y cuando reaparece ya está parado en la fila. El
cruce queda adentro; lo que falta es la salida.

**Cuánto depende el resultado del tramo** (`make ventana`, grilla de 41 × 31):

| tramo de `x` (m) | `Nm` medio | métrica 1: óptimo, `<E>`, cuánto baja | métrica 2: óptimo, `<E>`, cuánto baja |
|---|---|---|---|
| 0,80 a 7,90 | 80 | (2,0 s, 0,12 m) · 0,109 · −92 % | (2,0 s, 0,12 m) · 0,027 · −96 % |
| 1,00 a 8,00 | 72 | (2,0 s, 0,14 m) · 0,076 · −92 % | (1,5 s, 0,14 m) · 0,027 · −94 % |
| **1,00 a 7,70** | **71** | **(2,1 s, 0,14 m) · 0,063 · −93 %** | **(1,5 s, 0,14 m) · 0,019 · −94 %** |
| 1,25 a 7,45 | 62 | (1,3 s, 0,18 m) · 0,042 · −94 % | (1,3 s, 0,18 m) · 0,017 · −94 % |
| 1,50 a 7,20 | 55 | (4,0 s, 0,08 m) · 0,019 · −96 % | (4,0 s, 0,12 m) · 0,010 · −94 % |
| 2,00 a 6,70 | 42 | (4,0 s, 0,06 m) · 0,011 · −95 % | (4,0 s, 0,12 m) · 0,008 · −90 % |

`<E>` baja al acortar la ventana porque una trayectoria más corta acumula menos
error; lo que se compara es **cuánto baja la capa el error**, y eso es entre
90 % y 96 % con cualquiera de los seis tramos. El margen `d_s` del óptimo se
mueve entre 0,06 y 0,18 m, y `t_a` salta entre 1,3 y 4 s, que es lo esperable
de un parámetro que queda determinado sólo por abajo (ver el ítem b). El tramo
no se eligió por el error: se eligió por la figura.

### Integración

Beeman predictor-corrector (Teórica 4, diapositiva 20), que es el esquema que
la teórica da para fuerzas que dependen de la velocidad: acá la fuerza depende
de `v` por dos lados, el término de conducción y la fricción tangencial del
contacto. El primer paso usa `a(−Δt) = a(0)`.

El paso es `dt = Δt_exp / n` con `n` **entero**, de modo que cada instante
experimental cae exactamente en un paso de la simulación y las dos
trayectorias se comparan sin interpolar. `make convergencia` barre `n` de 1 a
512 y mide cuánto se aparta `<E>` del valor del paso más fino: 1,5 % con
`n = 1`, 0,3 % con `n = 16`, **0,11 % con `n = 64`** y 0,005 % con `n = 128`.
Se usa **`n = 64`** (`dt = 1,04 ms`): 0,11 % es cien veces menos que el error
estándar de `<E(1)>` entre eventos (11 %), y el barrido fino entero tarda medio
minuto. La convergencia no es monótona (de `n = 2` a `n = 4` el apartamiento
sube de 0,7 % a 1,4 %), así que se informa el valor y no un orden.

### Salida

- `sweep` con `--p1 0:8:33` (`make barrido` lo corre aparte, en la `d_s` de cada
  óptimo) es el barrido largo con el que se justifica el techo de la grilla.
- `pairs` escribe `pares.txt`: por evento y por métrica, el óptimo de cuatro
  parámetros y el de dos sobre la misma grilla. `asymmetry` escribe un
  `errores.txt` como el de `sweep`, con `(d_s, α)` en lugar de `(t_a, d_s)`.
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
| `events.py` | datos | las 38 trayectorias medidas enteras con el tramo del recorte marcado, y la distancia entre los dos peatones de cada evento contra el tiempo; por consola, la tabla de los 19 eventos y lo que deja la ventana |
| `window.py` | datos | la tabla de `make ventana`: la calibración con otros tramos de `x` |
| `convergence.py` | dt | apartamiento relativo de `<E>` contra `dt` en doble logarítmica, con la tolerancia y el paso usado marcados |
| `representative.py` | a | las trayectorias de los cuatro eventos representativos en una sola figura: medida, simulada con la capa y simulada sin capa |
| `trajectory.py` | a | por evento: trayectorias medidas y simuladas superpuestas, el observable primario `e(t)` de las dos métricas con su promedio temporal, y la distancia entre los dos peatones con `2r` y `D` marcados |
| `animate.py` | a | animación del evento (un cuadro por instante medido: a 15 cuadros por segundo corre en tiempo real) y cuadro fijo con `--cruce`, congelado en el último instante en conflicto antes del cruce simulado |
| `mosaico.py` | a | los 19 eventos animados a la vez, un panel por evento: la verificación a ojo de que cada ventana es el cruce y no la fila |
| `population.py` | b | mapa de `<E>(t_a,d_s)` (escala logarítmica, con el óptimo marcado y nada más); los dos cortes por el óptimo con barras de error y la franja de los valores que empatan; el barrido largo de `t_a` |
| `individual.py` | c | histograma de los 19 óptimos individuales de cada parámetro con una línea vertical en el óptimo global, y el error de cada evento con los parámetros poblacionales contra los propios |
| `pares.py` | c opcional | histograma de los 38 óptimos por peatón con la línea del óptimo global, y el error de cada evento con uno, dos y cuatro juegos de parámetros |
| `residual.py` | c | de dónde viene el error que queda: `E(1)_m` abierto en la componente a lo largo del camino nominal (ritmo) y la perpendicular (forma), y el desvío lateral en el cruce medido contra simulado, que dice si el modelo eludió por el mismo lado |
| `alternatives.py` | capa | la tabla y la figura de las tres capas de campo contra la predictiva: óptimo de cada una en su grilla y diferencia pareada |
| `explain.py` | apoyo | la capa explicada paso a paso: el esquema de la detección y del target temporal armado de a un elemento, con la fórmula de cada paso al pie (video, GIF y un cuadro por paso) |
| `support.py` | apoyo | las otras animaciones de apoyo: un cruce sintético cabeza a cabeza con tres `d_s` a la vez, dibujando lo que la capa calcula (posiciones predichas en `τ*`, `d*`, target temporal), y el evento 10 con cada parámetro recorriendo su rango al lado del corte de `<E>` |
| `crossval.py` | d | validación cruzada: distribución del error de validación contra el del ítem b, el par calibrado en cada partición y el error contra el tamaño del conjunto de entrenamiento; también deja-uno-afuera |
| `asymmetry.py` | extra | el reparto de la elusión: `<E>(α)`, histograma del `α` de cada evento con la línea del óptimo global, y `α` calibrado contra `α` medido en las trayectorias |
| `check.py` | — | validación de las corridas: recalcula las dos métricas, verifica que la grilla temporal sea la experimental y que las condiciones iniciales sean las medidas, e informa el solapamiento y el exceso de rapidez (que miden cuánto contacto queda) |

El nombre de cada eje es el **símbolo del enunciado con su unidad**
(`p_1 = t_a (s)`, `<E^(1)> (m²)`, `d (m)`), no la frase que lo describe; entra
siempre en una sola línea, los números llevan coma decimal y la leyenda va
adentro del gráfico sin tapar datos.

Una **barra de error** sobre `<E>` es el error estándar de la media entre
eventos, `σ/√M`. Para decidir qué pares **empatan** con el óptimo esa barra no
sirve: mide la dispersión entre eventos, que es enorme comparada con las
diferencias entre pares. Como todos
los pares se evalúan sobre los **mismos** 19 eventos, lo que corresponde es la
diferencia **pareada**: un par empata si la media de `E_m(p) − E_m(p*)` no
supera su propio error estándar.

## Resultados

Todo con la ventana `1,0 m ≤ x ≤ 7,7 m`, 19 eventos, `dt = Δt_exp/64`.

### Ítem a: qué hace la capa

| | sin capa (`t_a = 0`) | con la capa calibrada (2,15 s, 0,13 m) |
|---|---|---|
| eventos con contacto entre los dos agentes | **19 de 19** (solapamiento de hasta 4,4 cm) | **0 de 19** |
| `<E(1)>` | 0,874 m² | 0,062 m² |
| `<E(2)>` | 0,323 m² | 0,022 m² (0,019 con su propio óptimo) |
| elude por el mismo lado que las personas | — | **18 de 19** (19 de 19 con el óptimo de la métrica 2) |

Los cuatro eventos que se muestran (`EVENTOS_FIG`):

| evento | por qué | distancia mínima medida | simulada con capa | sin capa | `E(1)_m` con capa |
|---|---|---|---|---|---|
| **10** | el que más gana con la capa (`E(1)_m` de 1,91 a 0,068 m²) | 0,63 m | 0,53 m | 0,48 m | 0,068 m² |
| **5** | el cruce medido más ajustado | 0,49 m | 0,58 m | 0,47 m | 0,055 m² |
| **14** | el cruce medido más holgado | 0,92 m | 0,57 m | 0,47 m | 0,037 m² |
| **17** | el único en que el modelo elude por el lado opuesto | 0,57 m | 0,51 m | 0,46 m | 0,155 m² |

El 5 y el 14 juntos dicen lo que el modelo no puede hacer: las personas
pasaron a 0,49 y a 0,92 m y el modelo pasa siempre a `≈ D`, porque **la
distancia de paso es una sola para todos los pares**.

### Ítem b: calibración poblacional

| | métrica 1 (iguales tiempos) | métrica 2 (punto más cercano) |
|---|---|---|
| sin capa (`t_a = 0`) | 0,874 m² (RMS 0,93 m) | 0,323 m² (RMS 0,57 m) |
| óptimo | **2,15 s, 0,13 m** | **1,50 s, 0,14 m** |
| `<E>` en el óptimo | 0,0617 ± 0,0067 m² (RMS 0,25 m) | 0,0191 ± 0,0017 m² (RMS 0,14 m) |
| cuánto baja la capa | **93 %** | **94 %** |
| valores que empatan con el óptimo | `t_a` 1,35–4,00 s, `d_s` 0,07–0,22 m | `t_a` 1,50–4,00 s, `d_s` 0,08–0,26 m |
| distancia de paso `D = 2r + d_s` | 0,63 m | 0,64 m |

Los dos óptimos coinciden en `d_s` y difieren en `t_a`. Usar el óptimo de la
métrica 2 cuesta un 1,9 % de `<E(1)>`; al revés, un 18 % de `<E(2)>`.

`t_a` queda determinado **sólo por abajo**: `<E(1)>` cae de 0,87 a 0,07 m²
entre 0 y 1,5 s y después es plano (0,065 m² en 4 s). Tiene una explicación
geométrica: al empezar el evento los dos peatones están a unos 6,2 m y la
mínima distancia medida llega entre 2,1 y 2,7 s después (mediana 2,4 s); con
más anticipación que eso el conflicto se declara desde el primer instante, y
`t_a` sólo entra a través del peso de urgencia. El techo de la grilla se
verifica con un barrido aparte hasta 8 s (`data/barrido/p1largo`, figura
`techo_ta`): entre 4 y 8 s `<E>` se mueve un 2,5 % (métrica 1) y un 1,3 %
(métrica 2).

Lo mismo pasa evento por evento, y por eso el histograma de los óptimos
individuales de `t_a` (ítem c) tiene el pico en 4 s: **es el techo de la
grilla, no un mínimo**. Con el techo en 12 s (`sweep --p1 0:12:121 --p2
0:0.6:61`, un minuto) 17 de los 19 óptimos individuales se van más allá de
4 s —11 hasta los 12 s en la métrica 1 y 15 en la 2— y el error individual
baja apenas un 4 % y un 5 %. En ese barrido el mínimo poblacional de la
métrica 1 también se muda, de (2,15 s; 0,13 m) a (12 s; 0,09 m), con una
diferencia pareada de −0,001 ± 0,008 m²: un empate. El de la métrica 2 no se
mueve de (1,5 s; 0,14 m). Lo que los datos fijan de `t_a` es que sea mayor que
≈ 1,5 s.

La curva no es lisa: tiene **escalones** en `t_a ≈ 1,5` y `2,2 s`. Son dos
eventos, el 17 y el 16, en los que el lado por el que elude el modelo cambia
con `t_a` (arrancan casi alineados, y de frente el lado lo decide un
corrimiento de centímetros). Verificado corriendo los dos con `d_s = 0,13 m`:
hasta `t_a = 1,5 s` los dos eluden por el lado de las personas; desde 1,8 s el
17 pasa al opuesto, y desde 2,3 s también el 16. El mínimo global de cada
métrica cae donde los dos (1,50 s), o uno de los dos (2,15 s), quedan bien.

`d_s` sí tiene un mínimo claro y sube monótono después: es el parámetro que
fija por dónde se pasa.

### Ítem c: calibración individual

| | métrica 1 | métrica 2 |
|---|---|---|
| `t_a` individual (mediana, rango) | 4,00 s (1,50–4,00) | 4,00 s (1,45–4,00) |
| eventos con `t_a` en el borde de la grilla (4 s) | 14 de 19 | 16 de 19 |
| `d_s` individual (mediana, rango) | 0,07 m (0,03–0,35) | 0,14 m (0,03–0,39) |
| eventos con `t_a = 0` | ninguno | ninguno |
| `<E_m>` con los poblacionales | 0,0617 m² | 0,0191 m² |
| `<E_m>` con los individuales | 0,0481 m² | 0,0140 m² |
| **cuánto se gana** | **22 %** (pareado 0,014 ± 0,006) | **27 %** (pareado 0,0051 ± 0,0004) |

Se muestran como histograma de cada parámetro con una línea vertical en el
óptimo global. Lo que se lee:

- **En `t_a` casi todos se van al borde**: evento por evento, más anticipación
  nunca molesta. El óptimo global queda en 2,15 s (o 1,50 s) por los dos
  eventos de los escalones, no porque haya un tiempo de anticipación preferido.
- **En `d_s` cada par tiene el suyo**, de 0,03 a 0,39 m: es la misma dispersión
  que tiene la distancia mínima medida (0,49 a 0,92 m). El global es un
  compromiso, y eso es lo que se gana al individualizar.
- Casi la mitad de la ganancia de la métrica 1 es **un solo evento**, el 17
  (0,155 → 0,043 m²): con sus propios parámetros elude por el lado correcto.

### Ítem c opcional: los parámetros por peatón

El opcional pide "optimizar parámetros por cada peatón (en lugar de 1 juego de
parámetros por cada par de peatones)", y aclara que eso son **cuatro**
parámetros por evento en lugar de dos.

No es el barrido de dos parámetros hecho dos veces: **los dos agentes están
acoplados**, así que el error de cada peatón depende también de los parámetros
del otro (si el de la izquierda se corre más, el de la derecha necesita
correrse menos). El mínimo hay que buscarlo en la grilla de los cuatro a la
vez, que es lo que hace el comando `pairs` del motor: `425 × 425 = 180 625`
combinaciones por evento, 3,4 millones de corridas en total (5 min repartidas
en 8 hilos). La grilla de cada peatón es más gruesa que la del ítem b —paso de
0,25 s y de 0,025 m— porque el costo va al cuadrado; `make pares-noche` lo
repite con el paso fino (`4941 × 4941` por evento, unas 11 h con 8 hilos). Se
minimiza `E_m`, el promedio sobre los 2 peatones, que es lo que el enunciado
define como error del evento.

La grilla es más gruesa que la de la calibración poblacional —`t_a` en 17
valores de 0 a 4 s, `d_s` en 25 de 0 a 0,6 m— porque el costo va al cuadrado.
Para que la comparación diga algo, **los tres juegos se miden sobre esa misma
grilla**: una grilla más fina baja el error de los tres a la vez. Por eso el
"poblacional" y el "2 por evento" de esta tabla no son exactamente los de
arriba, que salen de la grilla fina (en esta grilla, con `t_a` de a 0,25 s, el
óptimo poblacional de la métrica 1 cae en 4,00 s y 0,10 m).

| | métrica 1 | métrica 2 |
|---|---|---|
| poblacional (1 juego) | 0,0634 m² | 0,0192 m² |
| 2 por evento (ítem c) | 0,0484 m² (−24 %) | 0,0141 m² (−27 %) |
| **4 por evento (opcional)** | **0,0433 m² (−11 % más)** | **0,0097 m² (−31 % más)** |
| ganancia pareada, 4 contra 2 | 0,0051 ± 0,0012 m² (4,3 σ) | 0,0044 ± 0,0011 m² (4,1 σ) |
| los dos peatones eligen el mismo par | 0 de 19 | 1 de 19 |

Se muestra como histograma de los 38 óptimos de cada parámetro, con la línea
vertical en el óptimo global del ítem b. Lo que se lee:

1. **Los dos peatones de un par casi nunca quieren los mismos parámetros** (0
   de 19 con la métrica 1, 1 de 19 con la 2). Es la misma asimetría que se
   mide directamente en las trayectorias y que el extra de `α` describe con un
   solo número: en cada par uno de los dos cede más.
2. **En `t_a`, 29 de los 38 peatones piden 3,5 s o más**, igual que en el ítem
   c; en `d_s`, 30 de los 38 quedan en 0,15 m o menos.
3. **Con la métrica 2 se gana de verdad**: 31 % más que con dos por evento.
   Con la métrica 1, 11 % más.

Y la contra: **describe pero no predice**. Son cuatro números por evento, así
que para un par nuevo no hay con qué estimarlos. Lo que se valida en el ítem d
es el modelo poblacional de dos.

### De dónde viene el error que queda

Con los parámetros poblacionales de la métrica 1:

- **El 61 % de `<E(1)>` va a lo largo del camino nominal** (0,038 de 0,062
  m²): es **ritmo**, el agente camina a velocidad deseada constante y las
  personas aceleran al salir y frenan al llegar. La forma —lo que la capa
  decide— es el 39 %.
- **El modelo elude por el mismo lado que las personas en 18 de los 19
  eventos**, sin ninguna regla de lado: lo decide la geometría recíproca con
  las velocidades del momento. La excepción es el 17. (En 14 de los 19 cruces
  las personas pasaron cada una por su derecha.)
- **Lo que no reproduce es la dispersión de la distancia de paso.** El desvío
  lateral en el cruce medido va de 0,49 a 0,92 m (media 0,71) y el simulado, de
  0,44 a 0,58 (media 0,53): en la figura del lado los puntos quedan en una
  franja horizontal.
- **Contacto.** Sin la capa hay contacto en los 19 eventos (solapamiento de
  hasta 4,4 cm); con la capa calibrada, en ninguno. En los datos, un solo
  evento tiene distancia mínima por debajo de `2r`.

Como referencia, la calibración del AA-CPM de la cátedra sobre su propio
experimento de dos peatones da un error medio de 0,24 m (Martin y Parisi 2024,
distancia media al punto más cercano): el RMS de la métrica 2 acá es 0,14 m.

**Lo que desapareció.** Con la ventana anterior los eventos parecían "dos
poblaciones" (los que ya caminaban por el corredor y los que salían de la
fila), el modelo eludía por el lado opuesto en 7 de 19 y quedaba contacto en
7. Las tres cosas eran consecuencia de la ventana: el evento arrancaba con el
peatón todavía en la fila y terminaba con el target fuera del corredor. Con el
recorte en `x` no queda ninguna.

### Ítem d: validación cruzada

| | métrica 1 | métrica 2 |
|---|---|---|
| ítem b (calibra y mide con los 19) | 0,0617 m² | 0,0191 m² |
| entrenamiento (500 particiones de 13/6) | 0,058 ± 0,005 m² | 0,018 ± 0,001 m² |
| validación | 0,084 ± 0,027 m² (**+36 %**) | 0,026 ± 0,010 m² (**+36 %**) |
| dejando uno afuera (19 de 18/1) | 0,078 m² (+27 %) | 0,025 m² (+29 %) |
| sin capa, como referencia | 0,874 m² | 0,323 m² |

El error de validación queda un tercio por encima del del ítem b, y la causa
es concreta: **los eventos 16 y 17**, los de los escalones. Cuando uno de los
dos queda en el conjunto de validación, la calibración no tiene cómo saber que
ese evento necesita un `t_a` de un lado u otro del escalón. Separando las
particiones: si ninguno de los dos está en validación el error es 0,065 m² (un
5 % sobre el ítem b); si está el 17, 0,100; si están los dos, 0,158. Todas las
particiones con error de validación mayor que 0,09 m² tienen al 16 o al 17 en
validación.

En términos absolutos el error de validación sigue siendo **diez veces menor
que el del modelo sin capa**. El par calibrado cambia poco de partición en
partición (6 pares distintos en 500, el más frecuente —1,50 s, 0,14 m— en el
46 %): `d_s` se queda entre 0,07 y 0,14 m y `t_a` salta entre 1,5, 2,15 y 4 s.

### Extra: el reparto de la elusión (`α`)

Fuera de lo que pide el enunciado; lo propuso la cátedra y pidió mostrarlo al
final. La capa calibrada es simétrica: los dos peatones se corren lo mismo. Se
le agrega un número, `α`, la fracción de la separación que falta que se lleva
el peatón que sale de la **izquierda** (el otro se lleva `1 − α`):

```
T_i* = q_i + w(τ*) · 2 α_i · (D − d*) ŝ,    α_izq = α,  α_der = 1 − α
```

El factor 2 hace que `α = 0,5` sea exactamente la capa simétrica. Con `t_a` y
`d_s` en el óptimo de cada métrica (`make asimetria`, `asymmetry.py`):

| | métrica 1 | métrica 2 |
|---|---|---|
| simétrica (`α = 0,5`) | 0,0617 ± 0,0067 | 0,0191 ± 0,0017 |
| `α` global óptimo | **0,625** · 0,0603 (gana 2 %, pareado 0,0014 ± 0,0011) | **0,575** · 0,0188 (gana 1 %, pareado 0,0003 ± 0,0005) |
| `α` propio de cada evento | 0,0572 (gana 7 %, pareado 0,0045 ± 0,0014) | 0,0155 (gana **19 %**, pareado 0,0036 ± 0,0009) |
| `α` por evento | media 0,62 · de 0,23 a 0,97 | media 0,58 · de 0,12 a 0,95 |
| correlación con el `α` medido | r = 0,72 | **r = 0,88** |

- **Como población, la capa simétrica alcanza**: el mejor `α` global está un
  poco por encima de 0,5 pero gana 1–2 %, dentro del error pareado. Dejar
  también `d_s` libre no cambia el óptimo.
- **Par por par el reparto no es parejo**: `α` va de 0,12 a 0,97. En cada par
  uno de los dos cede más, y cuál cambia de par en par.
- **El `α` calibrado es el que se mide.** `α` también se puede medir sin
  simular: la fracción del desvío lateral en el cruce (respecto de la propia
  recta de arranque a target) que hizo el que sale de la izquierda. Medido da
  media 0,57, de 0,17 a 0,99, y correlaciona con el calibrado con r = 0,72
  (métrica 1) y 0,88 (métrica 2). No es un parámetro que absorbe residuo.
- **Describe pero no predice**: es un número por par, y para un par nuevo la
  mejor estimación es ≈ 0,5.

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
más dos animaciones de apoyo y la comparación con las capas de campo, que es
más de lo habitual para una introducción matemática; la cátedra insistió en la
consulta en que explicar el algoritmo es donde más tiempo hay que gastar.
Antes de la capa va la diapositiva que define **cómo se fijan las condiciones
y el target de cada agente**, que la cátedra pidió pasar a la introducción.
`report/guion.md` tiene qué decir en cada diapositiva, con el tiempo de cada
una (13:00 en total) y un reparto entre los tres expositores.

Los esquemas de las diapositivas (el experimento, el del evento, los dos de la
capa de elusión, el UML, el bucle y la tabla de parámetros) están en
`report/figuras/*.tikz`; `presentacion.tex` los lee con `\input` y
`make slides-images-tikz` los renderiza sueltos a PNG en `slides-images/`, con
los mismos colores (`report/comun.tex`). Así en `slides-images/` está **toda**
imagen que aparece en la charla, numerada por la diapositiva en la que va: es
la carpeta con la que se arma la presentación a mano en Google Slides.

**La presentación que se expone** se arma en Google Slides con esas imágenes y
los GIF de `gif/`. La beamer de referencia tiene 35 diapositivas de contenido,
más de lo que entra en 13 minutos: las prescindibles son, en este orden, 21
(distancia del evento 10), 26 (cortes de la métrica 2, dejando la comparación
de óptimos en viñetas), 35 (parámetros por partición), 33 (evento 17, que se
puede contar sobre la figura de las cuatro trayectorias), 30 (errores con
cuatro parámetros, cuya cifra cabe en la 29), 10 (las capas de campo) y 16
(paso de integración, que puede ser una viñeta). Las imágenes con sufijo `b`
(`06b`, `07b`, `22b`, `24b`, `27b` a `30b`, `35b`) son opcionales: los cuadros
finales del GIF paso a paso y las mismas figuras con la otra métrica, por si
hacen falta en una pregunta.

Después de "Muchas gracias" van **tres diapositivas de extra** con la
optimización de `α` (`slide-extra-1` a `3`), que la cátedra pidió mostrar al
final como un opcional, y **tres de apéndice** con las libertades que se tomó
el agente de IA y que hubo que corregir, una por una, como pidió la cátedra en
el aviso del 04/11. El registro completo —qué hizo por su cuenta, por qué está
mal, con qué quedó y el commit de cada corrección— está en `IA.md`, y de ahí
sale el apéndice. Cada corrección nueva se anota ahí **en el momento**: el
detalle se pierde rápido.

Las **animaciones de apoyo** (`make apoyo`) son cuatro: la capa explicada paso
a paso (el esquema de las diapositivas 6 y 7 armado de a un elemento, con la
fórmula de cada paso), el cruce sintético cabeza a cabeza con tres `d_s` a la
vez (diapositiva 9), y el evento 10 con `d_s` y con `t_a` recorriendo su rango al
lado del corte de `<E>` (diapositiva 22). Con los cuatro eventos, el evento 10
sin capa y los 19 eventos a la vez son **diez GIF** en `gif/`.

Además de esos diez, `make gifs` deja **todo el material para elegir a mano**
qué mostrar: los 19 eventos sueltos en `gif/todos/evento-NN.gif` (con el óptimo
de la métrica 1 y la ventana `1,0 ≤ x ≤ 7,7 m`) y las tandas de cinco eventos
superpuestos en un solo panel (`gif/11 - … Los 19 eventos en tandas de
cinco.gif`). Que un GIF no esté en las diapositivas no es motivo para sacarlo
del repositorio.

Los links de YouTube de la beamer dicen `PENDIENTE-0n`: hay que reemplazarlos
por los reales en `report/presentacion.tex` (y en la presentación de Google
Slides) una vez subidos los videos de `youtube/`.

**Los videos se suben como "no listado", nunca privados**, y hay que abrir cada
link desde una ventana de incógnito antes de entregar: en el TP4 la cátedra no
pudo verlos y lo marcó como el problema importante de la entrega.

El zip de código que se entrega es el **motor de simulación** (`engine/`) más
**el código con el que se hacen las animaciones** a partir de las salidas
primarias (`visualization/animate.py` y `common.py`, del que depende), más la
tabla de eventos, como pidió la cátedra en el TP3.
