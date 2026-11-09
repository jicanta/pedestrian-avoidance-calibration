# Registro de libertades de la IA y de las correcciones del grupo

La cátedra pide, para el TP5, un **apéndice a la presentación con todas las
libertades que se tomó la IA y que el grupo tuvo que corregir**. Este archivo es
el registro del que sale ese apéndice (`report/presentacion.tex`, diapositivas
de apéndice A1 a A3).

**Herramienta.** Claude Code (Anthropic), modelos Claude Opus 5 y Claude
Fable 5.1, sobre este repositorio.

**Cómo se lleva.** Una entrada por corrección, con qué hizo el agente por su
cuenta, por qué está mal y con qué quedó, más el commit o el archivo donde se ve
el cambio. Las entradas 1 a 14 son las que quedaron documentadas en la historia
del repositorio (`git log`, `PLAN.md`, `README.md`); de la 15 en adelante se
anotan **en el momento**, porque el detalle se pierde rápido. Las entradas 15 a
17 salen de la revisión posterior a la entrega, con lo que marcó la cátedra
sobre el recorte de la ventana y sobre la asimetría del par (`ESTUDIO.md`).

---

## Metodología y modelado

**1. Justificó el techo de la grilla de `p1` con un argumento falso.**
Puso como razón que `p1` no podía pasar de la mediana del tiempo al cruce en el
instante inicial. Es incorrecto: con la rampa de urgencia `w = 1 − τ*/ta`, `p1`
sigue entrando en el cálculo aunque el conflicto se detecte desde `t = 0`, así
que ese número no acota nada. Se reemplazó por la medición que corresponde: un
barrido aparte hasta `8 s` que muestra que entre 4 y 8 s la diferencia pareada
de `<E>` es `+0,05 ± 0,04 m²` (métrica 1) y `0,000 ± 0,007 m²` (métrica 2) —
plana dentro del error, el techo no esconde nada.
*(commit `e95b7c3`; `PLAN.md` §«ítem b»)*

**2. Promedió los 19 eventos como una sola población.**
Informaba `<E>` sobre los 19 eventos sin mirar evento por evento, y así el
resultado quedaba dominado por un defecto del planteo, no por la capa. Al
revisarlos uno por uno contra el enunciado aparecen **dos poblaciones**, que se
separan solas por el ángulo entre la velocidad inicial medida y el camino
nominal (bimodal: menor que 32° o mayor que 60°): en 10 eventos los dos ya
caminan por el corredor y en 9 alguno sale de la fila, perpendicular, y ahí la
recta al target final es la ruta equivocada. Con parámetros poblacionales,
`<E(2)> = 0,08 m²` en el corredor contra `0,57` en la fila, y calibrando sólo
con los 10 del corredor la capa baja el error un **92 %** en lugar del 63 %
agregado. Los números del residuo también cambian con la separación: el aporte
de ritmo pasa de «77 % de `<E(1)>`» a **88 % en el corredor**, y el acierto del
lado del cruce, de «12 de 19» a **6 de 10**.
*(commit `e95b7c3`; `residual.py`, `population.py --clase`)*

**3. Usó la barra de error de `<E>` para decidir qué pares de parámetros
empatan con el óptimo.**
La barra es el error estándar de la media **entre eventos**: mide la dispersión
de la población, que es enorme comparada con las diferencias entre pares de
parámetros, y con ese criterio «empata» el 70 % de la grilla. Como todos los
pares se evalúan sobre los mismos 19 eventos, lo que corresponde es la
**diferencia pareada** evento por evento. La barra de error se sigue informando,
pero ya no decide nada.
*(commit `4b5fef7`; `PLAN.md` §«ítem b», duda 5 para la cátedra)*

**4. Dio por buena la capa predictiva sin medir ninguna alternativa.**
Propuso una sola familia y la presentó como la solución. La Teórica 7 sugiere
mirar capas basadas en campos, así que se implementaron **tres más** (isotrópica
con el término social del SFM como dirección, lateral y predictiva con
repulsión), todas de dos parámetros y todas como target temporal, y se
compararon con la diferencia pareada. La isotrópica queda lejos (−52 % contra
−63 %: de frente la repulsión apunta hacia atrás y no tiene componente
lateral); las otras dos empatan pero sus óptimos degeneran (`B → 0` es un
escalón sobre el contacto predicho y `B = 4,5 m` es empujar de costado siempre).
Se quedó la predictiva **con el argumento medido**, no con la intuición.
*(commit `45835e1`; `--capa predictiva|campo|campo-lateral|campo-predictivo`,
`alternatives.py`, `make alternativas`; diapositiva 8b)*

**5. Eligió una sola combinación de rampa y punto de mira sin decir por qué.**
Escribió la capa con una variante de peso de urgencia y de punto de mira como si
fuera la única. Las cuatro combinaciones dan el mismo error dentro del 2 %, muy
por debajo del error entre eventos, así que el número no alcanza para elegir: se
dejaron las otras tres detrás de `--sin-rampa` y `--mira-horizonte` para poder
compararlas, y el criterio de elección pasó a ser explícito y geométrico —
**la única continua en los dos bordes del disparo**.
*(commit `f73afef`; `README.md` §«variantes de diseño»)*

**6. Tomó como buenas las métricas que informa el motor.**
El motor calcula `E(1)` y `E(2)` porque son lo que minimiza el barrido (93 879
corridas: volcar todas las trayectorias serían decenas de GB), y el
post-procesamiento las usaba sin verificarlas. Se agregó `check.py`, que
recalcula las dos métricas desde las trayectorias, las compara con lo que
informó el motor, verifica que la grilla temporal sea la experimental y que las
condiciones iniciales sean las medidas, e informa cuánto contacto queda
(17 de 19 eventos sin la capa, 7 con la capa calibrada).
*(commit `4b5fef7`; `visualization/check.py`)*

**15. Recortó la ventana de cada evento con un umbral absoluto, que no recorta
nada.**
Para sacar de la ventana la parte en que un peatón todavía hace la fila puso un
umbral de rapidez **absoluto** (`0,3 m/s`) e igual para los dos. Los peatones
caminan entre 1,2 y 1,6 m/s, así que ese umbral es el 20 % del ritmo de uno y el
25 % del de otro: se perdía el 9 % de los instantes y los dos extremos quedaban
adentro. Las consecuencias no eran cosméticas: la rapidez deseada quedaba en el
**76 %** de la rapidez con la que el peatón camina, y el target final —que es la
última posición medida— caía donde el peatón ya había frenado y doblado hacia la
fila siguiente (hasta **52°** fuera de su recorrido, con targets en `y = 3,5`
cuando el corredor está en `y ≈ 2`), así que el agente apuntaba de costado desde
`t = 0`. El umbral pasó a ser una **fracción del ritmo de crucero de cada
peatón** (`--ritmo`), elegida por un criterio independiente del error: la que
hace que la rapidez media de la ventana sea la rapidez con la que el peatón
camina (`β = 0,75`). Con eso la capa explica el **96 %** del error en lugar del
63 %, las dos métricas coinciden en el óptimo, el contacto entre agentes pasa de
10 eventos de 19 a **0**, y 18 de los 19 eventos resultan una sola población: la
segunda población era en buena parte un artefacto de que la ventana arrancaba
mientras el peatón todavía estaba doblando para salir de la fila.
*(`ESTUDIO.md` §1; `engine/src/experiment.cpp`)*

**16. Escribió una capa simétrica sobre datos que no lo son.**
La capa hace que los dos peatones del par se corran lo mismo, mitad y mitad de
la separación que falta, y eso se dio por bueno sin medirlo. Midiéndolo —el
desvío lateral de cada peatón respecto de su propia recta, en el instante del
cruce— la fracción que se lleva el de la izquierda tiene media 0,53 pero desvío
**0,26** y va de **0,17 a 1,00**: en cada par uno de los dos cede casi todo. Se
le agregó a la capa el reparto `α` (`--alfa`), con `t_a` fijo porque el barrido
lo determina sólo por abajo, y el par calibrado pasó a ser `(d_s, α)`. El `α`
poblacional sigue siendo 0,5 (no hay un lado que ceda), pero par por par baja
`<E(2)>` un **26 %**, y el `α` que calibra el barrido correlaciona con el `α`
medido en las trayectorias con **r = 0,91**: no es un parámetro que absorbe
residuo.
*(`ESTUDIO.md` §2; `engine/include/avoidance.hpp`)*

## Afirmaciones sobre las figuras y atribución

**7. Una viñeta afirmaba lo contrario de lo que muestra la figura.**
En la diapositiva del evento 10 decía que el arco de elusión sale correcto.
Sale **en espejo**: la capa elude por el lado opuesto al que eligieron las
personas. La viñeta ahora lo dice, y ese hecho pasó a ser parte del análisis del
residuo (el lado del cruce, acertado en 6 de 10 eventos del corredor).
*(commit `e95b7c3`)*

**8. Atribuyó la predicción a Karamouzas *et al.* sin la diferencia.**
La capa extrapola con **las velocidades actuales de los dos** peatones;
Karamouzas usa la velocidad **deseada** para `i`. Es la misma geometría pero no
la misma fórmula, y la diapositiva no lo aclaraba. Ahora lo dice.
*(commit `e95b7c3`; diapositiva 7)*

**9. Eligió como caso ilustrativo un evento que mezcla las dos poblaciones.**
Usaba el evento 19 para la animación de apoyo. Con las dos poblaciones
separadas, el 19 mezcla las dos cosas y no ilustra ninguna: se cambió por el
**14** (sale de la fila) y el **3** (en el corredor, lado opuesto), y las de
resultados quedaron en el **10** con y sin capa, más el 5.
*(commit `e95b7c3`)*

## Figuras

**10. La leyenda de la convergencia decía «tolerancia 0,0 %».**
Es **0,01 %**, y además la curva incluía el punto de referencia contra el que se
mide el apartamiento, que por construcción vale cero.
*(commit `e95b7c3`; `convergence.py`)*

**11. Dibujó la región de pares que empatan como una curva de contorno.**
Las celdas que empatan no forman una región conexa, así que el contorno llenaba
el mapa de islas sueltas. Va como **velo sobre las celdas**, que es lo que se
puede leer.
*(commit `e95b7c3`; `population.py`)*

**12. Puso los mapas de `<E>(p1,p2)` en escala de color lineal.**
En escala lineal los gobierna la franja de `p1` chico y **todo el valle queda
del mismo tono**, que es justo lo que hay que mirar. Van con `pcolormesh` sobre
la grilla real (81 × 61 valores equiespaciados de verdad), escala de color de
potencia y curvas de nivel rotuladas en múltiplos del mínimo. Es además la
devolución D24 del TP4, sobre ejes con valores equiespaciados que no lo son.
*(commit `4b5fef7`; `FEEDBACK.md` D24)*

**13. Superpuso etiquetas repetidas en los óptimos individuales.**
Varios de los 19 óptimos individuales caen en el mismo par de parámetros y el
agente etiquetaba cada uno, con los textos uno encima del otro. Llevan **una
sola etiqueta**, y la figura dice cuántos caen en el **borde de la grilla**, que
es información que faltaba.
*(commit `e95b7c3`; `individual.py`)*

## Proceso de entrega

**14. Dejó GIF de una lista de videos anterior en la carpeta de entrega.**
Al cambiar la lista de animaciones, `make youtube` y `make gifs` copiaban los
nuevos encima pero no borraban los viejos, y quedaron en la carpeta el GIF del
evento 19 y el del 14 con el nombre anterior. Los dos objetivos **vacían la
carpeta antes de copiar**. Importa porque la devolución fuerte del TP4 fue
justamente sobre las animaciones de la entrega.
*(commit `5f926fe`; `Makefile`)*

**17. Dejó que el motor escribiera en `static.txt` un campo de texto que el
lector de Python no sabe leer.**
Al agregar la variante de capa al archivo de parámetros de cada corrida
(`capa predictiva`), no tocó el lector, que convertía **todo** valor a número.
El error no se disparaba porque las corridas entregadas son anteriores a esa
línea: al regenerar `make corridas` se habrían roto `make check` y todas las
figuras que leen una corrida. El lector ahora deja como texto lo que no es
número.
*(`visualization/common.py`, `read_static`)*

---

## Límites fijados por adelantado (no son correcciones)

Para que el registro de arriba se lea bien, vale aclarar qué se le fijó al
agente desde el principio, en vez de corregírselo después:

- El diseño de la capa de elusión, la ventana de cada evento, el esquema de
  integración y el criterio de compatibilidad entre pares los decidió el grupo a
  partir de las Teóricas 5 a 7 y de la bibliografía.
- El motor calcula métricas, pero **ningún promedio y ninguna decisión**: eso
  sale del post-procesamiento (devolución del TP3).
- Ninguna conclusión entra a la presentación sin la cifra de una figura ya
  mostrada, y nada se muestra que no se pueda explicar entero en la diapositiva
  (devoluciones D16 y D26 del TP4, en `FEEDBACK.md`).
