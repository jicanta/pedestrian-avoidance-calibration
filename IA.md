# Registro de libertades de la IA y de las correcciones del grupo

La cátedra pide, para el TP5, un **apéndice a la presentación con todas las
libertades que se tomó la IA y que el grupo tuvo que corregir**. Este archivo es
el registro del que sale ese apéndice (`report/presentacion.tex`, diapositivas
de apéndice A1 a A3).

**Herramienta.** Claude Code (Anthropic), modelos Claude Opus 5 y Claude
Fable 5.1 y 5.2, sobre este repositorio.

**Cómo se lleva.** Una entrada por corrección, con qué hizo el agente por su
cuenta, por qué está mal y con qué quedó, más el commit o el archivo donde se ve
el cambio. Las entradas 1 a 14 son las que quedaron documentadas en la historia
del repositorio (`git log`, `PLAN.md`, `README.md`); de la 15 en adelante se
anotan **en el momento**, porque el detalle se pierde rápido. Las entradas 15 a
17 salen de la primera revisión con la cátedra (el recorte de la ventana y la
asimetría del par), las 18 a 24, de la consulta del 11/11/2026
(`FEEDBACK.md`), después de la cual **todos los números cambiaron** (las cifras
que citan las entradas 1 a 14 son las de la ventana de entonces), y la 25, de
la devolución del 12/11 sobre el evento 1.

---

## Metodología y modelado

**1. Justificó el techo de la grilla de `t_a` con un argumento falso.**
Puso como razón que `t_a` no podía pasar de la mediana del tiempo al cruce en el
instante inicial. Es incorrecto: con la rampa de urgencia `w = 1 − τ*/ta`, `t_a`
sigue entrando en el cálculo aunque el conflicto se detecte desde `t = 0`, así
que ese número no acota nada. Se reemplazó por la medición que corresponde: un
barrido aparte hasta `8 s` que muestra que entre 4 y 8 s `<E>` se mueve un
2,6 % (métrica 1) y un 1,4 % (métrica 2): el techo no esconde nada.
*(commit `e95b7c3`; `PLAN.md` §«ítem b»)*

**2. Promedió los 19 eventos como una sola población — y la corrección fue
otro error (ver la 19).**
Informaba `<E>` sobre los 19 eventos sin mirar evento por evento. Al revisarlos
uno por uno aparecieron "dos poblaciones", separadas por el ángulo entre la
velocidad inicial medida y el camino nominal: 10 eventos en que los dos ya
caminaban por el corredor y 9 en que alguno salía de la fila. Se presentó como
un resultado. No lo era: era la ventana mal recortada, y con el recorte en `x`
los 19 eventos son una sola población (entrada 19).
*(commit `e95b7c3`; después, `FEEDBACK.md`, consulta del 11/11)*

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
compararon con la diferencia pareada. La isotrópica queda lejos (−66 % contra
−94 %: de frente la repulsión apunta hacia atrás y no tiene componente
lateral); el campo predictivo empata; el lateral da un error algo menor pero
con el óptimo en el borde de la grilla (`B = 5 m` es empujar de costado
siempre). Se quedó la predictiva **con el argumento medido y dicho**, no con la
intuición.
*(commit `45835e1`; `--capa predictiva|campo|campo-lateral|campo-predictivo`,
`alternatives.py`, `make alternativas`; diapositiva 8b)*

**5. Eligió una sola combinación de rampa y punto de mira sin decir por qué.**
Escribió la capa con una variante de peso de urgencia y de punto de mira como si
fuera la única. Se dejaron las otras tres detrás de `--sin-rampa` y
`--mira-horizonte` para poder compararlas, y el criterio de elección pasó a ser
explícito y geométrico — **la única continua en los dos bordes del disparo**.
Con la primera ventana las cuatro daban lo mismo dentro del 2 %; con la
recortada ya no (sin la rampa el error baja un 16–19 %), y eso está dicho en el
README y va como pregunta a la cátedra.
*(commit `f73afef`; `README.md` §«variantes de diseño»)*

**6. Tomó como buenas las métricas que informa el motor.**
El motor calcula `E(1)` y `E(2)` porque son lo que minimiza el barrido (93 879
corridas: volcar todas las trayectorias serían decenas de GB), y el
post-procesamiento las usaba sin verificarlas. Se agregó `check.py`, que
recalcula las dos métricas desde las trayectorias, las compara con lo que
informó el motor, verifica que la grilla temporal sea la experimental y que las
condiciones iniciales sean las medidas, e informa cuánto contacto queda
(19 de 19 eventos sin la capa, ninguno con la capa calibrada).
*(commit `4b5fef7`; `visualization/check.py`)*

**15. Recortó la ventana de cada evento con un umbral absoluto, que no recorta
nada.**
Para sacar de la ventana la parte en que un peatón todavía hace la fila puso un
umbral de rapidez **absoluto** (`0,3 m/s`) e igual para los dos. Los peatones
caminan entre 1,2 y 1,6 m/s, así que ese umbral casi no recortaba: la rapidez
deseada quedaba en el 76 % de la rapidez con la que el peatón camina, y el
target final —la última posición medida— caía donde el peatón ya había frenado
y doblado hacia la fila siguiente, con targets en `y = 3,5` cuando el corredor
está en `y ≈ 2`. Lo marcó la cátedra.
*(primera revisión; `engine/src/experiment.cpp`)*

**16. Escribió una capa simétrica sobre datos que no lo son.**
La capa hace que los dos peatones del par se corran lo mismo, y eso se dio por
bueno sin medirlo. Midiéndolo —el desvío lateral de cada peatón respecto de su
propia recta, en el instante del cruce— la fracción que se lleva el de la
izquierda tiene media 0,59 pero va de **0,17 a 0,99**: en cada par uno de los
dos cede más. Se le agregó a la capa el reparto `α` (`--alfa`). El `α` global
óptimo queda cerca de 0,5 (la capa simétrica alcanza como modelo de población),
pero par por par baja `<E(2)>` un **19 %**, y el `α` calibrado correlaciona con
el medido con **r = 0,88**. Por pedido de la cátedra se muestra **al final,
como extra**, sin reemplazar la calibración de `(t_a, d_s)`.
*(`engine/include/avoidance.hpp`, `visualization/asymmetry.py`)*

**18. Arregló el recorte de la 15 con un criterio rebuscado.**
En lugar del umbral absoluto puso una **fracción del percentil 75 de la rapidez
de cada peatón** (`--ritmo`), con la fracción elegida para que la rapidez media
de la ventana fuera la de crucero, y como eso no alcanzaba para un evento (el
14) le agregó una **banda en `y`** (`--corredor`) con su propio barrido para
elegir el ancho. Funcionaba, pero eran dos perillas, un percentil y dos
barridos para justificar lo que se ve en una figura. La cátedra lo dijo sin
vueltas: está mal hecho; la figura de las trayectorias muestra de dónde parten
todos, y el recorte es **una restricción en `x`, con el rango fijo**. Quedó
`1,0 m ≤ x ≤ 7,7 m` para los 19 eventos, y se sacó todo lo anterior.
*(consulta del 11/11; `trimToCorridor` en `engine/src/experiment.cpp`)*

**19. Explicó con "dos poblaciones de eventos" lo que era un defecto de la
ventana.**
Es la consecuencia de la 2, la 15 y la 18. Con la ventana mal recortada los
eventos parecían de dos clases, el modelo eludía por el lado opuesto al de las
personas en 7 de 19 y quedaba contacto en 7; todo eso se presentó como
resultado, con sus figuras y una conclusión. Con el recorte en `x` los 19
eventos son una sola población, el modelo acierta el lado en **18 de 19** y no
hay contacto en **ninguno**. Las figuras y la conclusión de las dos poblaciones
se sacaron.
*(consulta del 11/11; `residual.py`, `population.py`)*

**20. Agregó una regla de frenado al llegar al target.**
El agente frenaba a menos de un radio de su target final. No está en el
enunciado, que pide que la capa "no modifique las reglas propias del modelo", y
medida no cambiaba ningún número. Se sacó.
*(commit `3a513dd`; `engine/src/simulation.cpp`)*

## Afirmaciones sobre las figuras y atribución

**7. Una viñeta afirmaba lo contrario de lo que muestra la figura.**
En la diapositiva del evento 10 decía que el arco de elusión sale correcto.
Sale **en espejo**: la capa elude por el lado opuesto al que eligieron las
personas. La viñeta se corrigió, y ese hecho pasó a ser un observable del
análisis del residuo: el lado del cruce, medido contra simulado. (Con la
ventana recortada el evento 10 elude por el lado correcto, y el modelo acierta
en 18 de 19.)
*(commit `e95b7c3`)*

**8. Atribuyó la predicción a Karamouzas *et al.* sin la diferencia.**
La capa extrapola con **las velocidades actuales de los dos** peatones;
Karamouzas usa la velocidad **deseada** para `i`. Es la misma geometría pero no
la misma fórmula, y la diapositiva no lo aclaraba. Ahora lo dice.
*(commit `e95b7c3`; diapositiva 7)*

**9. Eligió los eventos que se muestran sin decir por qué esos.**
Primero usó el evento 19, que no ilustraba nada en particular; después el 14 y
el 3 por razones que dependían de las dos poblaciones (entrada 19). La cátedra
pidió **unos cuatro eventos representativos que sirvan para contar algo**, en
una sola figura. Quedaron el **10** (el que más gana con la capa), el **5** (el
cruce medido más ajustado), el **14** (el más holgado) y el **17** (el único en
que el modelo elude por el lado opuesto), cada uno con su motivo escrito en el
panel.
*(consulta del 11/11; `visualization/representative.py`)*

## Figuras

**10. La leyenda de la convergencia decía «tolerancia 0,0 %».**
Era 0,01 % mal redondeado, y además la curva incluía el punto de referencia
contra el que se mide el apartamiento, que por construcción vale cero. (Hoy la
tolerancia marcada es 0,2 % y la leyenda la escribe con su cifra.)
*(commit `e95b7c3`; `convergence.py`)*

**11, 12 y 21. Sobrecargó los mapas de `<E>(t_a,d_s)`.**
Fueron tres pasos en la misma dirección. Primero la escala de color lineal,
donde todo el valle quedaba de un tono; se corrigió con una escala de potencia
y **curvas de nivel rotuladas en múltiplos del mínimo** (12). Encima fue la
región de pares que empatan, primero como contorno lleno de islas y después
como **velo sobre las celdas** (11). El resultado, dijo la cátedra, estaba
"ultra sobrecomplejizado". Los mapas quedaron como los de los TP anteriores: el
mapa en escala logarítmica, la barra de color y el óptimo (21). Los valores que
empatan se leen en los cortes, que es donde se entienden.
*(commits `e95b7c3` y `4b5fef7`; consulta del 11/11; `population.py`)*

**13 y 22. Mostró los óptimos individuales como una nube de puntos.**
Primero con una etiqueta por evento, que se pisaban porque varios óptimos caen
en el mismo par (13); después con una etiqueta por cúmulo. Seguía sin leerse lo
que importa: dónde está la distribución respecto del óptimo global. Por pedido
de la cátedra son **histogramas de cada parámetro con una línea vertical en el
óptimo global**, para los óptimos por evento y para los del opcional por peatón.
*(commit `e95b7c3`; consulta del 11/11; `individual.py`, `pares.py`)*

**23. Rotuló de más el esquema de la detección del conflicto.**
Cada posición llevaba su `r` y su `v`, y las predichas su fórmula entera: la
cátedra marcó que eso sobra. El esquema quedó con `i`, `j`, `d*`, `D` y la
condición de conflicto, y se agregó una animación que lo arma **paso a paso**,
con la fórmula de cada paso al pie.
*(consulta del 11/11; `report/figuras/elusion-deteccion.tikz`,
`visualization/explain.py`)*

**24. Puso la definición del target en la sección de Simulaciones.**
Cómo se fijan la posición y la velocidad iniciales, el target final y la
rapidez deseada de cada agente estaba en la diapositiva de parámetros. Es parte
del modelo, no de los casos estudiados: pasó a la Introducción, antes de la
capa.
*(consulta del 11/11; `report/presentacion.tex`)*

**25. Cortó la ventana del evento 1 donde se pierde el seguimiento de un
peatón.**
Al pasar al recorte en `x`, definió el final de la ventana como el último
cuadro con muestra de los **dos** peatones adentro del tramo. Al peatón 36 se le
pierde el seguimiento en `x = 3,19 m`, justo después del cruce, así que el
evento 1 terminaba ahí (`Nm = 42`) con los dos en la mitad del corredor, y lo
dejó anotado como "duda para la consulta" en vez de verlo como un defecto de la
condición de corte. La cátedra lo marcó al ver el GIF de los 19 eventos. Ahora
un cuadro sin muestra no cierra la ventana: termina cuando a alguno de los dos
se lo ve salir de `1,0 m ≤ x ≤ 7,7 m` (`Nm = 71`), el error del 36 no se evalúa
donde no hay muestra y su target sigue siendo su última posición medida. (En
el medio probó poner el target donde el peatón reaparece, en la fila: el grupo
lo sacó porque el enunciado dice "la última posición de su trayectoria
experimental".) Los óptimos
no cambiaron; `<E(1)>` pasó de 0,062 a 0,064 m².
*(devolución del 12/11; `engine/src/experiment.cpp`, `trimToCorridor`)*

## Proceso de entrega

**14. Dejó GIF de una lista de videos anterior en la carpeta de entrega.**
Al cambiar la lista de animaciones, `make youtube` y `make gifs` copiaban los
nuevos encima pero no borraban los viejos, y quedaron en la carpeta GIF de
eventos que ya no se mostraban. Los dos objetivos **vacían la
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

- El diseño de la capa de elusión, el esquema de integración y el criterio de
  compatibilidad entre pares los decidió el grupo a partir de las Teóricas 5 a 7
  y de la bibliografía; la ventana de cada evento, con la cátedra.
- El motor calcula métricas, pero **ningún promedio y ninguna decisión**: eso
  sale del post-procesamiento (devolución del TP3).
- Ninguna conclusión entra a la presentación sin la cifra de una figura ya
  mostrada, y nada se muestra que no se pueda explicar entero en la diapositiva
  (devoluciones D16 y D26 del TP4, en `FEEDBACK.md`).
