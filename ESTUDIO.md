# Tres mejoras para discutir con la cátedra

Las dos primeras salen de lo que marcó la cátedra: que la ventana de cada
prueba no está recortada en los extremos (y por eso los targets quedan mal
definidos) y que conviene dejar fijo uno de los dos parámetros y usar el lugar
que queda para modelar la asimetría del par. La tercera es lo que quedó
colgando de la primera: el recorte por rapidez arregla 18 de los 19 eventos y
no alcanza para el 14.

Nada de esto cambia los números de la entrega: el recorte relativo (`--ritmo`),
el del corredor (`--corredor`) y el reparto (`--alfa`) vienen apagados por
omisión (`RITMO = 0`, `CORREDOR = 0`, `alfa = 0,5`), y el barrido fino vuelve a
dar bit a bit los mismos errores que el archivo entregado. Los estudios nuevos
se corren con `make recorte`, `make barrido-recorte`, `make corredor` y
`make asimetria`, y escriben en carpetas aparte.

---

## 1. El recorte de la ventana

### El problema, medido

La ventana de cada evento es hoy la intersección del intervalo del LEEME con
los cuadros en que están seguidos los dos peatones, recortada a donde los dos
miden al menos 0,3 m/s. Ese umbral absoluto casi no recorta nada: los peatones
caminan entre 1,2 y 1,6 m/s, así que 0,3 m/s es el 20 % del ritmo de uno y el
25 % del de otro, y se pierde sólo el 9 % de los instantes. Con esa ventana:

- **La rapidez deseada queda baja.** `v_d` es el camino medido sobre el tiempo
  de la ventana, y la ventana incluye el arranque y la frenada: en promedio
  sobre los 38 peatones, `v_d` es el **76 %** del ritmo de crucero de cada uno
  (el percentil 75 de su rapidez medida). En el evento 11 el de la izquierda
  camina a 1,31 m/s y el modelo lo manda a 0,83 m/s.
- **El target final queda fuera del corredor.** El target es la última posición
  medida, y al final de casi todas las pruebas el peatón frena y dobla hacia la
  fila de la vuelta siguiente. El desvío de la dirección final respecto de la
  cuerda del recorrido llega a **52°** (evento 18, derecha), y hay targets en
  `y = 2,77` (evento 1), `y = 3,04` (evento 6) y `y = 3,48` (evento 3) cuando
  el corredor está en `y ≈ 2`. El agente simulado apunta de costado desde
  `t = 0`.
- **La población "sale de la fila" es en parte un artefacto.** De los 19
  eventos, 9 quedan clasificados como "sale de la fila" porque la velocidad
  inicial medida forma más de 45° con la recta al target. Pero eso es porque la
  ventana arranca mientras el peatón todavía está doblando para salir de la
  fila, no porque la prueba sea distinta.

### La corrección

El umbral de cada peatón pasa a ser **una fracción β de su propio ritmo de
crucero** (`--ritmo β`; el recorte usa el mayor entre ése y el absoluto). Es
una sola perilla, se aplica igual a los dos extremos y es relativa a cada
peatón, que es lo que el umbral absoluto no puede hacer.

**β se elige por un criterio independiente del error:** el que hace que la
rapidez media de la ventana sea la rapidez con la que el peatón camina, que es
la condición que el enunciado le pide a la velocidad deseada.

| β | instantes | Nm mín | ⟨v_d / v_crucero⟩ | desvío final máx | el cruce cae en | eventos "fila" |
|---|---|---|---|---|---|---|
| 0,00 | 91 % | 79 | 0,765 | 52° | 32–78 % | 9 |
| 0,50 | 65 % | 41 | 0,892 | 71° | 38–85 % | 8 |
| 0,60 | 57 % | 40 | 0,931 | 73° | 39–85 % | 5 |
| 0,70 | 48 % | 35 | 0,979 | 33° | 38–82 % | 3 |
| **0,75** | **44 %** | **35** | **1,004** | **34°** | **39–82 %** | **1** |
| 0,80 | 39 % | 35 | 1,031 | 17° | 42–82 % | 0 |
| 0,90 | 34 % | 35 | 1,043 | 20° | 45–82 % | 0 |

β = 0,75 es donde `⟨v_d / v_crucero⟩ = 1,00`. Las 19 distancias mínimas siguen
adentro de la ventana y el cruce cae entre el 39 % y el 82 % de ella, así que
no se recorta la elusión. Se paga con la mitad de los instantes: `Nm` baja de
134 a 64 en promedio (de 8,8 s a 4,2 s).

Con β = 0,75 los targets caen todos sobre el eje del corredor (`y` entre 1,8 y
2,3) y los arranques también, que es por qué la población "sale de la fila"
baja de 9 eventos a 1.

### Qué pasa con la calibración

Misma grilla fina (81 × 61) y mismo criterio de óptimo, cambiando sólo β:

| β | métrica | óptimo `(t_a, d_s)` | ⟨E⟩ | ⟨E⟩ sin capa | reducción |
|---|---|---|---|---|---|
| 0,00 (entrega) | 1 | 2,50 s · 0,070 m | 1,476 ± 0,253 | 2,735 | 46 % |
| 0,00 (entrega) | 2 | 3,85 s · 0,050 m | 0,314 ± 0,074 | 0,838 | 63 % |
| 0,70 | 1 | 1,55 s · 0,160 m | 0,248 ± 0,123 | 0,906 | 73 % |
| 0,70 | 2 | 1,55 s · 0,160 m | 0,038 ± 0,017 | 0,414 | 91 % |
| **0,75** | **1** | **4,0 s · 0,090 m** | **0,074 ± 0,045** | **0,757** | **90 %** |
| **0,75** | **2** | **4,0 s · 0,120 m** | **0,014 ± 0,002** | **0,345** | **96 %** |

Lo que importa no es que ⟨E⟩ baje —una ventana más corta acumula menos error
por sí sola— sino que **la fracción del error que la capa explica sube del
63 % al 96 %** con la misma métrica y la misma ventana para los dos modelos. Y
aparecen cuatro cosas que antes no estaban:

1. **Las dos métricas coinciden en el óptimo** (`t_a = 4 s`, `d_s` entre 0,09 y
   0,12 m). Con la ventana de la entrega discrepaban (2,50 · 0,070 contra
   3,85 · 0,050).
2. **`t_a` sigue determinado sólo por abajo**, ahora verificado hasta 12 s:
   ⟨E⁽²⁾⟩ vale 0,0158 a 2 s, 0,0144 a 4 s y 0,0139 a 12 s, diferencias muy por
   debajo del error estándar de 0,002.
3. **Desaparece el contacto.** El observable es el que ya informa
   `visualization/check.py`: en cuántos eventos los dos agentes llegan a
   solaparse. Con la ventana de la entrega, el SFM puro choca en 17 de 19 y la
   capa calibrada baja a 7 de 19 (métrica 1) o 10 de 19 (métrica 2): sigue
   habiendo choque en la mitad de los eventos. Con la ventana recortada, el SFM
   puro choca en 16 de 19 y la capa calibrada en **0 de 19**.
4. **El error se reparte parejo.** Con β = 0,75 los 18 eventos del corredor
   tienen `E⁽²⁾` entre 0,006 y 0,034 m², y el único que queda alto es el 14
   (`E⁽¹⁾ = 0,886` contra ≤ 0,096 del resto), que es justamente el único que
   sigue clasificando como "sale de la fila": ahí la recta al target no es la
   ruta del peatón, que es el modo de falla que ya está documentado.

### Lo que hay que preguntar

- ¿Está bien elegir β por "la rapidez media de la ventana es la rapidez con la
  que el peatón camina" en lugar de por el error?
- ¿Molesta quedarse con el 44 % de los instantes (`Nm` de 35 a 107) a cambio de
  que las condiciones iniciales y el target sean los del experimento que
  describe el enunciado?
- Con el recorte, 18 de 19 eventos son una sola población. ¿Sigue teniendo
  sentido presentar la separación en dos poblaciones, o pasa a ser parte de la
  justificación del recorte?

---

## 2. El reparto de la elusión (la asimetría)

### La asimetría existe y se mide sin simular

Para cada peatón, el desvío lateral respecto de su propia recta de arranque a
target, en el instante del cruce. La fracción del desvío total que se lleva el
que sale de la izquierda, `α`:

- **media 0,53**, mediana 0,55: no hay un lado que ceda sistemáticamente;
- **desvío 0,26**, rango **0,17 a 1,00**: en cada par uno de los dos cede casi
  todo, y cuál de los dos parece sorteado.

La capa simétrica no puede reproducir eso: los dos agentes se corren lo mismo
por construcción.

### La corrección

La capa lleva un tercer número, `α`, la fracción de la separación que falta que
se lleva el peatón de la izquierda (el de la derecha se lleva `1 − α`):

```
T_i* = q_i + w(τ*) · 2 α_i · (D − d*) ŝ,    α_izq = α,  α_der = 1 − α
```

El factor 2 hace que `α = 0,5` sea exactamente la capa simétrica de siempre.
Siguen siendo **dos parámetros a calibrar**: como el barrido determina `t_a`
sólo por abajo, se lo deja fijo (4 s) y se calibra el par `(d_s, α)`, que es lo
que sugirió la cátedra.

### Qué da

Sobre la ventana recortada, `t_a = 4 s`:

| | métrica 1 | métrica 2 |
|---|---|---|
| simétrico (`α = 0,5`) | `d_s* = 0,090` · ⟨E⟩ = 0,0742 ± 0,0453 | `d_s* = 0,120` · ⟨E⟩ = 0,0144 ± 0,0020 |
| `α` poblacional libre | `α* = 0,600` · ⟨E⟩ = 0,0734 | `α* = 0,575` · ⟨E⟩ = 0,0141 |
| `α` propio de cada par | ⟨E⟩ = 0,0709 | ⟨E⟩ = **0,0106 ± 0,0015** |
| ganancia pareada | 0,0033 ± 0,0008 (4 %) | **0,0038 ± 0,0012 (26 %)** |
| `α` por evento | media 0,62 · sd 0,23 | media 0,56 · sd 0,25 · rango 0,17–1,00 |

Tres conclusiones:

1. **El óptimo poblacional de `α` es 0,5** (0,575 con ⟨E⟩ a 0,0003 m² del
   simétrico, muy por debajo del error estándar). Como modelo de población, la
   capa simétrica es la correcta: no hay un lado que ceda.
2. **Par por par, `α` gana de verdad en la métrica 2:** 26 % de reducción, 3,2
   desvíos del error pareado. En la métrica 1 gana 4 % (significativo pero
   chico, porque ⟨E⁽¹⁾⟩ está dominado por el evento 14).
3. **El `α` que calibra el barrido es el `α` que se mide en las trayectorias:**
   correlación **r = 0,91** sobre los 19 eventos (0,93 sobre los 18 del
   corredor). No es un parámetro de ajuste que absorbe residuo: es una
   propiedad medible de cada par que la capa recupera.

Y una contra, que conviene decirla: `α` **describe pero no predice**. Es un
número por par, así que para un par nuevo la mejor estimación es 0,5 y no
mejora nada (⟨E⟩ 0,0141 contra 0,0144). Para la validación cruzada del ítem d,
el modelo que se valida sigue siendo el simétrico.

Sobre la ventana de la entrega el ejercicio no sirve: los `α` calibrados se van
a 0 o a 1 (sd 0,39) y la ganancia es del 6 %, porque `α` se usa para compensar
targets mal puestos en lugar de describir el reparto. La asimetría recién tiene
sentido **después** del recorte.

### Lo que hay que preguntar

- ¿Está bien contar el tercer número así —`t_a` fijo porque el barrido lo
  determina sólo por abajo, y el par calibrado es `(d_s, α)`— o prefieren que
  `α` se presente como una extensión de tres parámetros declarada como tal?
- ¿Alcanza esto como respuesta al 2 c) opcional (optimizar por peatón), siendo
  **un** parámetro por par en lugar de cuatro?
- ¿Les interesa la correlación `r = 0,91` entre el `α` calibrado y el medido
  como validación de que la capa captura el mecanismo?

---

## 3. El evento 14: lo que el recorte por rapidez no alcanza

### El problema, medido

Las dos condiciones de §1 miran **cuánto** camina el peatón, no **por dónde**.
Y hay un tramo de fila que se camina rápido: **salir de la fila hacia el
corredor**. Las dos filas están por debajo del corredor, así que entrar a él es
subir en `y` sin avanzar en `x`, a 0,6–1,0 m/s — por encima de cualquiera de
los dos umbrales.

Conviene decir que esto **no es un problema de seguimiento**: las filas están
adentro del rectángulo filmado. Todo el archivo crudo abarca `x` de 0,08 a
11,40 m y `y` de −0,69 a 3,73 m, y el histograma de `y` es bimodal — unas 6300
muestras alrededor de `y = 2` (el corredor) y unas 8800 por debajo de `y = 0,5`
(las dos filas), separadas por un valle casi vacío en `y = 1`. Lo que sobra de
la ventana es fila filmada, no trayectoria extrapolada.

De los 19 eventos **le pasa a uno solo, el 14**, que es exactamente el que §1
deja afuera. Con `β = 0,75` su ventana arranca en el cuadro 22058, con los dos
todavía subiendo:

| | izquierda (30) | derecha (28) |
|---|---|---|
| arranque | (0,63 , 1,47) | (8,01 , 1,29) |
| ángulo de `v(0)` | **95°** | **88°** |
| desvío de `v(0)` respecto de la cuerda al target | **88°** | **86°** |
| `v_d` | 0,77 m/s | 1,05 m/s |

Y el recorte por rapidez no puede arreglarlo, porque sólo corta los extremos:
el peatón 30 sube al corredor, **se queda parado 2 s en `x ≈ 0,64`** esperando
a que el otro llegue, y recién entonces arranca. Como el primer cuadro de la
ventana ya pasa el umbral (está subiendo rápido), la espera queda adentro.

### La corrección

Una condición de **lugar**, no de rapidez: los dos peatones tienen que estar
pisando el corredor, `|y − 2| ≤ Δ` (`--corredor Δ`). El eje `y = 2` es el que
declara el LEEME ("se cruzan por y ~ 2 m") y el que marca el histograma.

**Δ se elige en el medio de la meseta.** Barriendo el semiancho (`make
corredor`):

| Δ (m) | instantes | eventos que cambian vs. `β = 0,75` | Nm del evento 14 | desvío final máx |
|---|---|---|---|---|
| 0,20 | 755 | 1, 2, 3, 6, 7, 12, 14, 18 | 6 | 26° |
| 0,25 | 1001 | 1, 12, 14, 18 | 8 | 26° |
| 0,30 | 1008 | 1, 12, 14, 18 | 10 | 26° |
| **0,40** | **1157** | **14** | **53** | **26°** |
| **0,50** | **1157** | **14** | **53** | **26°** |
| **0,60** | **1157** | **14** | **53** | **26°** |
| 0,70 | 1210 | 14 | 106 | 88° |
| 0,80 | 1211 | ninguno | 107 | 88° |

Entre 0,40 y 0,60 el resultado es **bit a bit el mismo**: toca únicamente al
evento 14 y deja los otros 18 cuadro por cuadro idénticos. Por abajo de 0,40
empieza a comerse la elusión de otros eventos (con Δ = 0,30 el evento 1 se
queda en 11 instantes y el 14 en 10); en 0,70 ya no alcanza. `Δ = 0,5` es el
medio de la meseta. Pedir en vez de eso que el **rumbo** esté a menos de
40°–70° del eje `x` da exactamente el mismo recorte, así que el criterio
tampoco depende de haberlo escrito como banda.

Con `Δ = 0,5` el evento 14 queda así:

| | `β = 0,75` | `β = 0,75` + corredor |
|---|---|---|
| ventana | 22058–22164 (Nm = 107) | 22112–22164 (**Nm = 53**) |
| arranque izq / der | (0,63 , 1,47) / (8,01 , 1,29) | (1,44 , 1,98) / (5,85 , 1,65) |
| desvío de `v(0)` izq / der | 88° / 86° | **10° / 3°** |
| `v_d` izq / der | 0,77 / 1,05 m/s | **1,15 / 1,31 m/s** |
| distancia mínima | 0,92 m, al 76 % de la ventana | 0,92 m, al **52 %** |

Se pagan 3,6 s de evento, que son los que el peatón 30 tarda en subir al
corredor y esperar. La distancia mínima sigue adentro y ahora cae en el medio.

Sobre los 19 eventos:

| ventana | Nm medio | mín | ⟨v_d / v_crucero⟩ | desvío final máx | "sale de la fila" |
|---|---|---|---|---|---|
| `β = 0` (entrega) | 134 | 79 | 0,752 | 103° | 17/38 |
| `β = 0,75` | 64 | 35 | 0,903 | 88° | 2/38 (los dos del 14) |
| `β = 0,75` + corredor | **61** | **35** | **0,913** | **26°** | **0/38** |

### Qué pasa con la calibración

Misma grilla fina (81 × 61) y mismo criterio de óptimo:

| ventana | métrica | óptimo `(t_a, d_s)` | ⟨E⟩ | ⟨E⟩ sin capa | reducción |
|---|---|---|---|---|---|
| `β = 0,75` | 1 | 4,0 s · 0,090 m | 0,0742 ± 0,0453 | 0,757 | 90 % |
| `β = 0,75` | 2 | 4,0 s · 0,120 m | 0,0144 ± 0,0020 | 0,345 | 96 % |
| **+ corredor** | **1** | **4,0 s · 0,090 m** | **0,0286 ± 0,0045** | **0,730** | **96 %** |
| **+ corredor** | **2** | **4,0 s · 0,120 m** | **0,0132 ± 0,0017** | **0,346** | **96 %** |

Lo que importa:

1. **El óptimo no se mueve.** Los dos pares son los mismos que con `β = 0,75`,
   con las dos métricas. El recorte del corredor no reajusta la calibración:
   saca un evento del residuo.
2. **Las dos métricas dan la misma reducción, 96 %.** Con `β = 0,75` la
   métrica 1 se quedaba en 90 % porque el evento 14 pesaba él solo más que los
   otros 18 juntos.
3. **La barra de error de la métrica 1 se cae de 0,045 a 0,0045**, un factor
   10. Era dispersión de un evento, no del modelo: `E⁽¹⁾` del evento 14 pasa de
   **0,886 a 0,021**, y el rango sobre los 19 eventos, de 0,012–0,886 a
   0,012–0,096.
4. **El contacto no cambia**: el SFM puro choca en 16 de 19 y la capa calibrada
   en 0 de 19, igual que con `β = 0,75` (`make corredor` deja las dos corridas
   para verificarlo con `visualization/check.py`).
5. **Las dos poblaciones desaparecen del todo.** Con `β = 0,75` quedaba 1
   evento clasificado como "sale de la fila"; con el corredor, ninguno. Los 19
   eventos son una sola población.

### Lo que hay que preguntar

- La condición de rapidez es sobre la trayectoria; ésta es sobre la geometría
  del experimento (dónde está el corredor). ¿Les cierra meter una condición de
  lugar, o prefieren que el recorte salga sólo de la trayectoria?
- Para el evento 14 el recorte deja `Nm = 53` (3,5 s). ¿Es poco evento?
- Si el criterio se acepta, los 19 eventos pasan a ser una sola población.
  ¿Qué hacemos con la separación en dos poblaciones, que hoy es un resultado de
  la presentación (ver también la duda 8 de `PLAN.md`)?

---

## Cómo reproducir

```
make recorte            # eventos + barrido fino para β = 0; 0,4 … 0,9
make barrido-recorte    # la calibración completa con β = 0,75 (RITMO_NUEVO)
make corredor           # eventos para Δ = 0,2 … 1 y la calibración con Δ = 0,5
make asimetria          # (d_s, α) con t_a fijo, sobre las dos ventanas
```

Los cuatro escriben en `data/recorte/`, `data/corredor/` y `data/asimetria/`,
sin tocar `data/barrido/` ni `data/experimental/`. Para correr todo con los dos
recortes puestos alcanza `make todo RITMO=0.75 CORREDOR=0.5`.

De paso quedó arreglado un error que todavía no se había disparado:
`writeStatic` escribe la línea `capa predictiva` (texto) y `read_static`
convertía todo valor a número, así que al regenerar `make corridas` se rompían
`make check` y todas las figuras que leen una corrida. Las corridas entregadas
son anteriores a esa línea, que es por qué no se había visto.
