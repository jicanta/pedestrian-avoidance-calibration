# PLAN — TP5, Problema 1: calibración de una capa de elusión

> Documento de trabajo. Consolida qué pide el enunciado, cómo se resuelve, qué
> decisiones se tomaron y qué queda para preguntar. Fuentes:
> `docs/enunciado/TP5_Enunciado.pdf`, `docs/teoria/Teorica_{5,6,7}.pdf`, la
> bibliografía de la cátedra (`docs/bibliografia/`), la guía de presentaciones
> (`../tp-2/GuiaPresentaciones.pdf`, fuera de este repositorio) y las
> devoluciones recogidas en `FEEDBACK.md`.

---

## 0. Datos de la entrega

**Materia:** Simulación de Sistemas (SdS) — 2026 Q2 · **Comisión:** S2 · **Grupo:** 10

| Integrante | Legajo | Correo |
|---|---|---|
| Javier Liu | 64332 | jaliu@itba.edu.ar |
| Juan Ignacio Cantarella | 64509 | jcantarella@itba.edu.ar |
| Nicolás Rivas | 64292 | nrivas@itba.edu.ar |

**Fecha límite:** 16/11/2026, 13:00 h (campus). Presentación oral de **13
minutos** el mismo día.

**Entregables** (este TP **no lleva informe**):

```
SdS_TP5_2026Q2G10S2_Presentación.pdf   # cuadro fijo + link a YouTube por animación
SdS_TP5_2026Q2G10S2_Codigo.zip         # sólo el motor final (+ animate.py y common.py)
```

---

## 1. Qué pide el problema 1

La cátedra da `M` eventos experimentales de **elusión 1 contra 1 de frente**:
en cada prueba una persona sale de la fila izquierda y otra de la fila derecha
y se cruzan alrededor de `y = 2 m`. De cada peatón se tiene su trayectoria
medida `r_i^exp(t_k)` con `t_k = k Δt_exp`.

Hay que elegir **SFM sin fuerza social** o **CPM**, proponer una **capa de
elusión de exactamente 2 parámetros** que actúe *sólo* reemplazando
transitoriamente el target final por un target temporal, y calibrarla contra
los datos con dos métricas de error cuadrático medio:

- **Métrica 1** (iguales tiempos): `E(1)_i = (1/Nm) Σ_k |r_i^exp(t_k) − r_i^sim(t_k)|²`
- **Métrica 2** (punto más cercano): `E(2)_i = (1/Nm) Σ_k min_j |r_i^exp(t_k) − r_i^sim(t_j)|²`

El error de un evento es el promedio sobre sus 2 peatones y el poblacional, el
promedio sobre los `M` eventos.

**Ítems:** (a) implementar y mostrar animaciones con las trayectorias
superpuestas; (b) calibración poblacional con cada métrica, con la superficie
`<E>(p1,p2)` y cortes con barras de error; (c) calibración individual por
evento y cuánto se gana; (d) validación cruzada.

---

## 2. Modelo elegido: SFM sin fuerza social

Se elige **SFM** y no CPM por dos razones:

1. Las distancias mínimas medidas van de 0,49 a 0,92 m, y la de contacto es
   `2r = 0,5 m`: **casi no hay contacto**. En CPM, sin contacto el agente
   camina a `vd` en línea recta al target y la trayectoria queda enteramente
   determinada por la capa de elusión, sin ninguna dinámica propia. En SFM el
   tiempo de relajación `τ = 0,5 s` le da inercia a la respuesta, que es lo que
   hace que el giro sea suave y comparable con el de una persona.
2. El `dt` de CPM forma parte de las reglas del modelo y no se puede cambiar;
   con SFM el paso es libre y se puede elegir de modo que divida `Δt_exp` en un
   número entero de partes, que es lo que permite comparar las dos trayectorias
   **sin interpolar**.

Ecuación (Helbing, Farkas y Vicsek 2000, sin el término social
`A exp((r_ij − d_ij)/B)`):

```
m dv_i/dt = (m/τ)(v_i^d ê_i^d − v_i) + Σ_j [ k ξ_ij n̂_ij + κ ξ_ij (Δv_ji · t̂_ij) t̂_ij ]
ξ_ij = r_i + r_j − d_ij   (sólo si es positivo)
n̂_ij = (r_i − r_j)/d_ij,  t̂_ij = (−n_y, n_x),  Δv_ji = v_j − v_i
```

Parámetros del paper: `m = 80 kg`, `τ = 0,5 s`, `k = 1,2·10⁵ N/m`,
`κ = 2,4·10⁵ kg/(m·s)`. El radio lo fija el enunciado: `r = 0,25 m`.

**Integración:** Beeman predictor-corrector (Teórica 4, diapositiva 20), que es
el esquema que la teórica da para fuerzas que dependen de la velocidad — y acá
la fuerza depende de `v` por dos lados, la conducción y la fricción tangencial
del contacto. El primer paso usa `a(−Δt) = a(0)`.

---

## 3. La capa de elusión

### 3.1 Qué puede y qué no puede hacer

El enunciado es explícito: la capa **sólo** puede reemplazar transitoriamente
el target final por un target temporal, no puede agregar fuerzas ni cambiar las
reglas del modelo, y tiene que depender de **exactamente 2 parámetros**.

### 3.2 Los dos parámetros

- `p1 = ta`: **tiempo de anticipación** (s). Sólo se reacciona a conflictos que
  van a ocurrir dentro de los próximos `ta` segundos. Con `ta = 0` la capa está
  apagada y queda el SFM puro, que es la referencia del trabajo.
- `p2 = ds`: **margen de espacio personal** (m). El agente quiere pasar a más
  de `D = r_i + r_j + ds` del otro. Con `ds = 0` quiere pasar rozándolo.

Son los dos parámetros de la familia predictiva de la literatura (Karamouzas
*et al.* 2009, `docs/bibliografia/Biblio_6_7/PCA.pdf`: tiempo de anticipación y
espacio personal), pero ahí se resuelven con una **fuerza evasiva**, que acá no
está permitida.

### 3.3 Detección del conflicto

Extrapolación lineal de las dos trayectorias. Con `Δr = r_j − r_i` y
`Δv = v_j − v_i`:

```
τ* = −(Δr · Δv) / |Δv|²            instante de mínima aproximación
d* = |Δr + Δv τ*|                  separación predicha ahí
D  = r_i + r_j + ds                separación requerida
```

Hay conflicto si `0 < τ* ≤ ta` y `d* < D`. Si `|Δv| = 0` o `τ* ≤ 0` (se están
separando) no hay conflicto.

### 3.4 El target temporal

```
ê_i^0  = (T_i − r_i)/|T_i − r_i|            dirección nominal al target final
q_i    = r_i + v_i^d τ* ê_i^0               punto de mira sobre el camino nominal
ŝ      = [(r_i + v_i τ*) − (r_j + v_j τ*)] / d*     lado de la separación
w(τ*)  = 1 − τ*/ta                          peso de urgencia
T_i*   = q_i + w(τ*) (D − d*) ŝ
```

y la velocidad deseada pasa a ser `v_i^d ê_i^d` con
`ê_i^d = (T_i* − r_i)/|T_i* − r_i|`. **El módulo nunca cambia.**

### 3.5 Por qué así

- **Recíproca.** Los dos agentes calculan el mismo `d*` y el mismo `D`, y `ŝ`
  les sale opuesto: cada uno acentúa el lado al que ya está corrido y entre los
  dos cubren la separación que falta. No hace falta ninguna negociación.
- **Continua en los dos bordes del disparo.** En `τ* = ta` el peso `w` vale 0 y
  `T_i* = q_i`, que está sobre la recta al target final: al entrar y al salir
  del horizonte la dirección deseada no salta. En `d* → D` pasa lo mismo porque
  el factor `(D − d*)` se anula.
- **Límite de conflicto inminente.** Con `τ* → 0` se tiene `w → 1` y `q_i → r_i`:
  el target temporal queda puramente lateral y el agente se corre de costado.
- **Vuelta al target final automática**: en cuanto se separan, `τ* ≤ 0`.
- **Degenerado**: si van exactamente de frente, `d* → 0` y `ŝ` queda
  indefinida; se usa la normal a `ê_i^0` del lado en el que *no* está el otro, y
  si eso también es cero, la derecha.

### 3.6 Alternativas y variantes probadas (y por qué corre ésta)

Contra la predictiva se probaron tres capas basadas en **campos** de
repulsión (`A exp(−(d − 2r)/B)` como dirección, nunca como fuerza): isotrópica
(Helbing como dirección), lateral y predictiva (en `d*`, Karamouzas como
target). La isotrópica queda lejos (−66 % contra −94 %: de frente no tiene
componente lateral); el campo predictivo empata; el lateral da un error algo
menor (0,014 contra 0,019 m²) pero con el óptimo en el borde de la grilla,
`B = 5 m`, que es empujar de costado siempre. La tabla completa está en el
README.

Las dos decisiones de diseño se probaron contra sus alternativas, con el mismo
barrido y los mismos 19 eventos (`--sin-rampa` y `--mira-horizonte` en el
motor):

| variante | peso de urgencia | punto de mira | `<E(1)>` mín. | `<E(2)>` mín. |
|---|---|---|---|---|
| **la que corre** | `w = 1 − τ*/ta` | `v^d τ*` (el conflicto) | 0,063 | 0,019 |
| sin rampa | `w = 1` | `v^d τ*` | 0,051 | 0,016 |
| mira al horizonte | `w = 1 − τ*/ta` | `v^d ta` | 0,111 | 0,029 |
| ninguna de las dos | `w = 1` | `v^d ta` | 0,042 | 0,013 |

Con la ventana recortada **ya no dan lo mismo**: sin la rampa el error baja un
15–20 % (la diferencia pareada es significativa). Corre la primera porque es la
**única continua en los dos bordes del disparo** y porque es la que se discutió
con la cátedra; cambiarla es la duda 3 de §8.

---

## 4. Decisiones sobre los datos

### 4.1 El peatón sin identificar de la prueba 2

El LEEME dice `sale izquierda V?`. En los cuadros de esa prueba la única
trayectoria no asignada que va de izquierda a derecha (de `x = 0,75` a
`x = 10,8 m`) es el id **1000**. Se usa ése, y queda anotado en
`experimental/eventos.txt`.

### 4.2 La ventana de cada evento

Dos recortes, en este orden:

1. **Intersección**: el evento empieza cuando los **dos** peatones están
   seguidos y termina cuando deja de estarlo alguno. Antes de eso falta uno de
   los dos y no hay dos agentes que simular. El recorte se hace *dentro* del
   intervalo del LEEME, porque un mismo peatón aparece en varias pruebas
   (haciendo la fila) y sus cuadros extremos en el archivo no son los de su
   prueba.
2. **Tramo del corredor**: del primer al último cuadro en que los dos están en
   `1,0 m ≤ x ≤ 7,7 m`. Es una restricción sobre el eje `x`, la misma para los
   19 eventos, leída de la figura de las 38 trayectorias superpuestas: las
   cabeceras de las dos filas están en `x ≈ 0,6` y `x ≈ 8,1 m`, y el tramo deja
   0,4 m de cada lado.

Es lo que pidió la cátedra en la consulta del 11/11. Antes hubo otros dos
criterios, los dos sacados: un umbral de rapidez absoluto (0,3 m/s), que casi
no recortaba nada, y después una fracción del percentil 75 de la rapidez de
cada peatón más una banda en `y`, que recortaba bien pero con un criterio
rebuscado y difícil de defender. La historia está en `FEEDBACK.md` y en `git
log`.

Con el tramo quedan 1346 instantes (el 34 % de los que declara el LEEME), `Nm`
de 42 a 80, las 19 distancias mínimas adentro (entre el 47 % y el 80 % de la
ventana) y los 38 peatones arrancando hacia su target (ángulo máximo 29°).
`make ventana` mide cuánto cambia la calibración con otros cinco tramos: la
capa baja el error entre 90 % y 96 % con cualquiera.

### 4.3 Huecos de seguimiento

Con la ventana recortada **no queda ningún hueco adentro**. Si quedara, no se
interpola: el agente se simula igual (hace falta para acoplarlo con el otro)
pero el error no se evalúa en los instantes sin muestra.

El único hueco que importa está en el borde: al peatón 36 (evento 1) se le
corta el seguimiento 32 cuadros justo después del cruce, y cuando reaparece ya
está en la fila. Su última muestra adentro del tramo está en `x = 3,45 m`, así
que la ventana del evento 1 termina ahí (`Nm = 42`, la más corta). El cruce
queda adentro.

### 4.4 La velocidad inicial

Diferencia finita hacia adelante sobre **5 cuadros** (un tercio de segundo). Una
diferencia entre cuadros consecutivos mide el ruido del seguimiento (unos 5 mm,
que a 15 cuadros por segundo son 0,08 m/s sobre una rapidez de 0,9 m/s) y no la
velocidad del peatón. Si justo ahí hay un hueco se toma la primera muestra que
haya más adelante.

### 4.5 La llegada al target

**No hay regla de llegada.** El enunciado fija el target final y la rapidez
deseada y dice "se simula hasta el último instante experimental del evento",
nada más; el agente apunta a su target hasta el final.

Hubo una (el agente frenaba al llegar a menos de un radio del target, con
`v^d = 0`) y se sacó. Medida sobre las dos ventanas no mueve ningún número:
⟨E⁽¹⁾⟩ y ⟨E⁽²⁾⟩ iguales hasta la cuarta cifra decimal y la misma excursión
máxima pasado el target, 0,24 m. Era una regla agregada al modelo sin nada que
la justificara, y el enunciado pide que la capa de elusión "no agregue fuerzas
ni modifique las reglas propias del modelo elegido".

### 4.6 El paso de integración

`dt = Δt_exp / n` con `n` entero, para que cada instante experimental caiga
exactamente en un paso y no haya que interpolar para comparar. El barrido de
`n` (`make convergencia`) da un apartamiento de `<E>` respecto del paso más
fino de 1,5 % con `n = 1`, 0,3 % con `n = 16`, **0,11 % con `n = 64`** y
0,005 % con `n = 128`. Se usa **`n = 64`** (`dt = 1,04 ms`): 0,11 % es cien
veces menos que el error estándar de `<E(1)>` entre eventos, y el barrido fino
entero tarda medio minuto.

---

## 5. Estructura del repositorio

```
tp-5/
├── Makefile            # todo el flujo desde la raíz
├── README.md           # este trabajo, en detalle
├── PLAN.md             # este documento
├── FEEDBACK.md         # devoluciones de la cátedra aplicadas acá, incluidas las consultas del TP5
├── IA.md               # libertades que se tomó el agente y cómo se corrigieron
├── requirements.txt    # matplotlib, numpy
├── docs/               # enunciado, teóricas y bibliografía de la cátedra
├── experimental/       # los datos de la cátedra y la tabla de eventos
├── engine/             # C++17: el motor (va en el zip de entrega)
├── visualization/      # Python: post-procesamiento, figuras y animaciones
├── report/             # presentacion.tex (beamer 16:9), comun.tex, figuras/*.tikz
├── slides-images/      # toda imagen de la presentación, numerada por diapositiva
├── youtube/            # titulos.md (los .mp4 no se versionan)
├── gif/                # los videos como GIF, para embeber en la charla en vivo
└── data/               # salidas de simulación y figuras (ignoradas por git)
```

---

## 6. Plan por ítem

### Ítem a — implementación y animaciones

- `report/guion.md`: qué decir en cada diapositiva, con tiempos y reparto.
- `make eventos` verifica la lectura de los datos contra el LEEME.
- `make corridas` corre los 19 eventos con los dos óptimos y con la capa
  apagada.
- `make animations` genera los videos y el cuadro fijo de cada uno, congelado
  en el último instante en conflicto antes del cruce simulado.
- **Cuatro eventos representativos** en una sola figura de trayectorias
  (`representative.py`): el 10 (el que más gana con la capa), el 5 (el cruce
  medido más ajustado), el 14 (el más holgado) y el 17 (el único en que el
  modelo elude por el lado opuesto). Del 10, además, `e(t)` y la distancia
  entre los dos peatones.

### Ítem b — calibración poblacional

Proceso en dos etapas: una grilla gruesa (17 × 21) para acotar el plano y una
fina (81 × 61) sobre `p1 ∈ [0, 4] s` y `p2 ∈ [0, 0,6] m`, que es la que se usa.
El techo de `p1` se verifica con un barrido aparte hasta 8 s en la `p2` de
cada óptimo: entre 4 y 8 s `<E>` se mueve un 2,5 % (métrica 1) y un 1,3 %
(métrica 2). El de `p2` sale de la grilla gruesa: más allá de 0,6 m `<E>` sube
monótono. Los mapas de `<E>(p1, p2)` van **simples**, como los de los TP
anteriores: el mapa en escala logarítmica, la barra de color y el óptimo.

La **región compatible** con el óptimo no se calcula con el error estándar de
la media (que mide la dispersión entre eventos y es enorme comparada con las
diferencias entre pares), sino con la **diferencia pareada**: todos los pares se
evalúan sobre los mismos 19 eventos, así que lo que importa es si
`E_m(p) − E_m(p*)` promediada supera su propio error estándar.

### Ítem c — calibración individual

El mismo archivo del barrido: para cada evento, el mínimo de su propia
superficie. Los 19 óptimos se muestran como **histograma de cada parámetro con
una línea vertical en el óptimo global**, y los 19 errores contra los que da el
poblacional. El opcional (cuatro parámetros por evento, `make pares`) se
muestra igual: histograma de los 38 óptimos por peatón con la línea del global.

### De dónde viene el error que queda

Con la ventana recortada los 19 eventos son **una sola población** (las "dos
poblaciones" que aparecían antes eran un defecto de la ventana: el evento
arrancaba con el peatón todavía en la fila). Se reporta la descomposición del
residuo a lo largo y perpendicular al camino nominal (ritmo y forma) y el lado
del cruce medido contra simulado.

### Ítem d — validación cruzada

500 particiones al azar de 13 eventos de entrenamiento y 6 de validación, más
la de dejar uno afuera (19 particiones de 18/1). Como el barrido ya tiene el
error de cada evento en cada par, una partición es un promedio sobre un
subconjunto de columnas: no hay que volver a simular.

---

## 7. Presentación (13 min)

Secciones de la guía: Introducción (el experimento, los datos con el tramo que
se simula, el modelo, **cómo se fijan las condiciones y el target de cada
agente** y **tres diapositivas de capa de elusión**, como pide el enunciado),
Implementación (UML del motor y el bucle), Simulaciones (parámetros,
observables y casos), Resultados (ítems a, b, c y d en ese orden) y
Conclusiones. Cierre con la declaración de uso de agentes de IA y "Muchas
gracias". **Después del cierre** van las tres diapositivas del extra (la
optimización de `α`, el reparto de la elusión, que la cátedra pidió mostrar al
final como un opcional) y el **apéndice de tres diapositivas con las libertades
que se tomó el agente y que hubo que corregir** (el registro completo está en
`IA.md`).

Lo que más tiempo lleva es **explicar el algoritmo**: las tres diapositivas de
la capa, con el GIF que arma el esquema paso a paso
(`gif/09 … La capa de elusion paso a paso.gif`), y el bucle.

La beamer de `report/` es la **versión de referencia**: la presentación que se
expone se arma a mano en Google Slides con las imágenes de `slides-images/` y
los GIF de `gif/`. Tiene más diapositivas de las que entran en 13 minutos; la
lista de prescindibles está en el README.

---

## 8. Dudas para plantear a los docentes

Lo que se resolvió en la consulta del 11/11 está en `FEEDBACK.md`. Para la del
viernes 13/11 queda:

1. **El tramo de `x`.** Quedó en `1,0 m ≤ x ≤ 7,7 m` (0,4 m adentro de cada
   cabecera de fila; a ojo se había dicho 1 y 8). ¿Les cierra? Con 1 a 8 la
   ventana del que sale por la izquierda termina ya frenando contra la fila de
   la derecha. La tabla de `make ventana` muestra que el resultado no depende
   de eso.
2. **El evento 1.** Al peatón 36 se le corta el seguimiento 32 cuadros después
   del cruce, así que su ventana termina en `x = 3,45 m` (`Nm = 42`). Se dejó
   así, con el cruce adentro. ¿Prefieren que se interpole el hueco o que el
   evento quede afuera?
3. **La rampa de urgencia.** Con la ventana nueva las cuatro variantes de la
   capa ya no empatan: sin la rampa (`w = 1`) el error baja un 15–20 %, a costa
   de que la dirección deseada salte al entrar en conflicto. ¿Vale la pena
   cambiar la capa a esta altura, o alcanza con decirlo?
4. **La validación cruzada.** El error de validación queda un 36 % por encima
   del del ítem b, y es por dos eventos (16 y 17) en los que el lado por el que
   elude el modelo depende de `t_a`. ¿Lo presentamos así, explicando la causa?
5. **Peatón sin identificar.** ¿Confirman que el "V?" de la prueba 2 es el id
   1000 del archivo (§4.1)?
6. **El 2 c) opcional.** Se minimiza `E_m` (el promedio de los 2 peatones) con
   los cuatro parámetros juntos, porque el problema no es separable. ¿Es lo que
   esperan?
7. **¿Fijar `t_a`?** El óptimo individual de `t_a` cae en el techo de la
   grilla (4 s) en 14 de 19 eventos, y con el techo en 12 s se van hasta ahí:
   más allá del tiempo al cruce (2,1 a 2,7 s) `t_a` casi no cambia nada. Fijar
   `t_a = 4 s` cuesta +3 % de `<E(1)>` (empate) pero +38 % de `<E(2)>`, y en el
   ajuste individual los eventos 16 y 17 piden 2,15 y 1,5 s. ¿Se puede sacar
   `t_a` y calibrar sólo `d_s` (y `α`), o lo dejamos y lo decimos así?
