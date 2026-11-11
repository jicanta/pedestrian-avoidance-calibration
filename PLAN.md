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
target). La isotrópica queda lejos (−52 % contra −63 %: de frente no tiene
componente lateral); las otras dos empatan dentro de la diferencia pareada
pero sus óptimos degeneran (`B → 0` y `B = 4,5 m`). La tabla completa está en
el README.

Las dos decisiones de diseño se probaron contra sus alternativas, con el mismo
barrido y los mismos 19 eventos (`--sin-rampa` y `--mira-horizonte` en el
motor):

| variante | peso de urgencia | punto de mira | `<E(1)>` mín. | `<E(2)>` mín. |
|---|---|---|---|---|
| **la que corre** | `w = 1 − τ*/ta` | `v^d τ*` (el conflicto) | 1,480 | 0,315 |
| sin rampa | `w = 1` | `v^d τ*` | 1,472 | 0,309 |
| mira al horizonte | `w = 1 − τ*/ta` | `v^d ta` | 1,478 | 0,316 |
| ninguna de las dos | `w = 1` | `v^d ta` | 1,456 | 0,313 |

Las cuatro dan el mismo error dentro del 2 %, que está muy por debajo del error
estándar de la media entre eventos (0,25 m² en la métrica 1). Se elige la
primera porque es la **única continua en los dos bordes del disparo** y porque
el punto de mira en el conflicto es el que el esquema de la diapositiva puede
explicar en una línea.

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
2. **Caminata**: la ventana se recorta a la parte en que los dos miden una
   rapidez de al menos **0,3 m/s** (diferencia centrada sobre ±2 cuadros).

Hay dos recortes más, **apagados por omisión** y medidos en `ESTUDIO.md` §1 y
§3 para llevarlos a la consulta: `--ritmo β` sube el umbral de cada peatón a
una fracción de su propio ritmo de crucero (recorta los dos extremos, no sólo
el arranque) y `--corredor Δ` pide además que los dos estén pisando el
corredor, `|y − 2| ≤ Δ`. El segundo hace falta porque el primero mira cuánto
camina el peatón y no por dónde, y hay un tramo de fila que se camina rápido:
salir de la fila hacia el corredor. De los 19 eventos le pasa a uno solo, el 14.

El segundo recorte es necesario, no cosmético. El enunciado habla de dos
peatones *que caminan en curso de colisión*, y al principio de varias pruebas
uno de los dos todavía está **parado haciendo la fila**: en la prueba 14 los
dos están quietos los primeros 4 s de los 13. Con el peatón quieto adentro de
la ventana, la rapidez media — que es el módulo de la velocidad deseada — baja
muy por debajo de la que camina (de 1,2 a 0,76 m/s), y el agente simulado
arranca a caminar en `t = 0` contra un peatón que no se movió en cuatro
segundos. Con el umbral de 0,3 m/s se pierde el **9 %** de los instantes
(2787 → 2543) y las **19 distancias mínimas siguen adentro de la ventana**: el
cruce nunca se recorta. El error poblacional sin capa baja de 3,05 a 2,73 m² y
el calibrado, de 1,70 a 1,48 m².

### 4.3 Huecos de seguimiento

Adentro de la ventana quedan huecos en un solo peatón de los 38 (32 instantes
del peatón derecho del evento 1). **No se interpolan**: el agente se simula
igual (hace falta para acoplarlo con el otro) pero el error no se evalúa en los
instantes sin muestra. Por eso la media de cada métrica va sobre los instantes
que ese peatón *tiene*, que es el `Nm` de ese peatón.

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
`n` (`make convergencia`) da que la tolerancia del 0,01 % contra el paso más
fino se cumple **desde `n = 16`**; se usa **`n = 64`** (`dt = 1,04 ms`), que ya
está en el piso de 0,001 % y hace que el barrido fino entero tarde un minuto.

---

## 5. Estructura del repositorio

```
tp-5/
├── Makefile            # todo el flujo desde la raíz
├── README.md           # este trabajo, en detalle
├── PLAN.md             # este documento
├── FEEDBACK.md         # devoluciones de la cátedra aplicadas acá
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
  en el instante de mínima aproximación simulada.
- Figuras por evento: trayectorias superpuestas, observable primario `e(t)` y
  distancia entre los dos peatones.

### Ítem b — calibración poblacional

Proceso en dos etapas: una grilla gruesa (17 × 21) para acotar el plano y una
fina (81 × 61) sobre `p1 ∈ [0, 4] s` y `p2 ∈ [0, 0,6] m`, que es la que se usa.
El techo de `p1` se verifica con un barrido aparte hasta 8 s en la `p2` de
cada óptimo: entre 4 y 8 s la diferencia pareada de `<E>` es `+0,05 ± 0,04 m²`
(métrica 1) y `0,000 ± 0,007 m²` (métrica 2), compatible con cero. El de `p2`
sale de la grilla gruesa: más allá de 0,6 m `<E>` sube monótono.

La **región compatible** con el óptimo no se calcula con el error estándar de
la media (que mide la dispersión entre eventos y es enorme comparada con las
diferencias entre pares), sino con la **diferencia pareada**: todos los pares se
evalúan sobre los mismos 19 eventos, así que lo que importa es si
`E_m(p) − E_m(p*)` promediada supera su propio error estándar.

### Ítem c — calibración individual

El mismo archivo del barrido: para cada evento, el mínimo de su propia
superficie. Se comparan los 19 pares con el poblacional y los 19 errores con
los que da el poblacional.

### De dónde viene el error que queda

Los eventos se separan solos en **dos poblaciones** por el ángulo entre la
velocidad inicial medida y el camino nominal (bimodal: < 32° o > 60°): en 10
los dos ya caminan por el corredor y en 9 alguno sale de la fila,
perpendicular. En los segundos la recta al target es la ruta equivocada (la
persona sube por la fila y después dobla), y la capa no tiene cómo arreglarlo.
Se reporta el error por población, la calibración con cada una por separado
(`population.py --clase corredor|fila`), la descomposición del residuo a lo
largo y perpendicular al camino nominal, y el lado del cruce medido contra
simulado.

### Ítem d — validación cruzada

500 particiones al azar de 13 eventos de entrenamiento y 6 de validación, más
la de dejar uno afuera (19 particiones de 18/1). Como el barrido ya tiene el
error de cada evento en cada par, una partición es un promedio sobre un
subconjunto de columnas: no hay que volver a simular.

---

## 7. Presentación (13 min)

Secciones de la guía: Introducción (el experimento, el modelo y **tres
diapositivas de capa de elusión**, como pide el enunciado), Implementación (UML
del motor y el bucle), Simulaciones (parámetros, observables y casos),
Resultados (ítems a, b, c y d en ese orden) y Conclusiones. Cierre con la
declaración de uso de agentes de IA y "Muchas gracias", y después de ésa, el
**apéndice de tres diapositivas con las libertades que se tomó el agente y que
hubo que corregir** (el registro completo está en `IA.md`), que es lo que la
cátedra agregó al pedido del TP5.

La beamer de `report/` es la **versión de referencia**: la presentación que se
expone se arma a mano en Google Slides con las imágenes de `slides-images/` y
los GIF de `gif/`. Tiene 34 diapositivas de contenido, más de lo que entra en
13 minutos; la lista de prescindibles está en el README.

---

## 8. Dudas para plantear a los docentes

1. **Ventana de los eventos.** La cátedra ya marcó que el recorte que había
   **no recorta los extremos**, y por eso los targets quedan mal definidos. Está
   medido y corregido en `ESTUDIO.md` §1: el umbral absoluto de `0,3 m/s` saca
   el 9 % de los instantes, la rapidez deseada queda en el 76 % de la que el
   peatón camina y hay targets a 52° de su recorrido. El umbral pasó a ser una
   fracción `β` del ritmo de crucero de cada peatón, con `β = 0,75` elegido
   porque es el que hace que la rapidez media de la ventana sea la rapidez con
   la que el peatón camina. Lo que queda por preguntar: **(a)** si ese criterio
   para elegir `β` les cierra, **(b)** si molesta quedarse con el 44 % de los
   instantes, y **(c)** si con el recorte —18 de 19 eventos pasan a ser una sola
   población— la separación en dos poblaciones sigue siendo un resultado o pasa
   a ser parte de la justificación del recorte (ver también la duda 8).
   El evento 19 que falta es el **14**, y lo que le pasa está medido aparte en
   `ESTUDIO.md` §3: ver la duda 9.
2. **Peatón sin identificar.** ¿Confirman que el "V?" de la prueba 2 es el id
   1000 del archivo (§4.1)? La cuenta no deja otra opción —las 19 filas nombran
   38 ranuras con 38 ids distintos y el archivo tiene exactamente 38 ids—, así
   que es confirmar, no decidir.
3. ~~**Huecos de seguimiento.**~~ Cerrada: no se interpola nada (§4.3). Es un
   solo peatón de los 38, 32 instantes.
4. ~~**Métrica 2.**~~ Cerrada por el propio enunciado: la fórmula (2) está
   escrita como `mín_j` sobre los instantes simulados `t_j`, que es punto a
   punto y es lo que hace el motor. Medido, usar la poligonal continua en lugar
   de los puntos baja ⟨E⁽²⁾⟩ de 0,0133 a 0,0127 m² —4,6 %, muy adentro de la
   barra de ±0,0017— y no mueve ningún óptimo.
5. ~~**Llegada al target.**~~ Cerrada: la regla se sacó (§4.5). No está en el
   enunciado y, medida, no mueve ningún número.
6. **Región compatible.** ¿Les parece razonable informar, además del óptimo, el
   conjunto de pares que empatan con él según la diferencia pareada? Con la
   barra de error estándar de la media, el 70 % de la grilla "empata".
7. **El reparto de la elusión.** La cátedra sugirió dejar fijo uno de los dos
   parámetros y usar el lugar que queda para modelar la asimetría del par. Está
   hecho y medido en `ESTUDIO.md` §2: `t_a` fijo (el barrido lo determina sólo
   por abajo) y el par calibrado es `(d_s, α)`, con `α` la fracción de la
   separación que falta que se lleva el peatón de la izquierda. El `α`
   poblacional es 0,5, pero par por par baja `<E(2)>` un 26 % y correlaciona con
   el `α` medido en las trayectorias con `r = 0,91`. **No es la respuesta al
   2 c) opcional**, que pide cuatro parámetros y no uno (ver la duda 10): `α` se
   presenta como una *medición* del reparto, no como un modelo alternativo. Lo
   que queda por preguntar: si prefieren que `α` se presente como tercer
   parámetro declarado o como el segundo del par calibrado con `t_a` fijo.

8. **Las dos poblaciones.** En 9 de las 19 pruebas al menos un peatón arranca
   caminando por la fila, perpendicular al corredor, y la recta al target final
   no es su ruta. ¿Esperan que esos eventos entren en la calibración tal cual
   (es lo que se hace, y se muestra qué pasa calibrando sólo con los otros 10),
   o preferirían que la ventana arranque cuando los dos ya caminan por el
   corredor?

9. **El evento 14 y el recorte por lugar.** El recorte de la duda 1 mira
   *cuánto* camina el peatón, no *por dónde*, y hay un tramo de fila que se
   camina rápido: salir de la fila hacia el corredor (las filas están debajo de
   él, así que entrar es subir en `y` sin avanzar en `x`). De los 19 eventos le
   pasa a uno solo, el 14, y es el único que con `β = 0,75` sigue arrancando
   perpendicular al corredor y el que se lleva solo el 60 % de ⟨E⁽¹⁾⟩. Está
   medido en `ESTUDIO.md` §3: pidiendo además que los dos estén pisando el
   corredor (`|y − 2| ≤ 0,5`, con una meseta de 0,4 a 0,6 donde el resultado es
   idéntico) el óptimo no se mueve, la reducción de la métrica 1 sube del 90 %
   al 96 % y la barra de error se cae de 0,045 a 0,0045. Lo que queda por
   preguntar: **(a)** si aceptan una condición de *lugar* (la geometría del
   experimento) además de las de trayectoria, **(b)** si `Nm = 53` es poco
   evento para el 14, y **(c)** qué hacemos entonces con la separación en dos
   poblaciones de la duda 8, que con este recorte desaparece del todo.

10. **El 2 c) opcional, los parámetros por peatón.** El enunciado pide
    "optimizar parámetros por cada peatón (en lugar de 1 juego de parámetros
    por cada par de peatones)", o sea **cuatro** números por evento. Como los
    dos agentes están acoplados —el error de cada uno depende también de los
    parámetros del otro— el mínimo se busca en la grilla de los cuatro a la
    vez, `G × G` por evento (`make pares`, comando `pairs` del motor), y de la
    misma grilla sale el óptimo de dos parámetros con el que se compara. Lo que
    queda por preguntar: si minimizar `E_m` (el promedio de los 2 peatones) con
    los cuatro parámetros juntos es lo que esperan, o si prefieren minimizar el
    error de cada peatón por separado —que no es lo mismo, porque el problema
    no es separable.
