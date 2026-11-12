# Devoluciones de la cátedra que se aplican al TP5

El TP3 se entregó el 28/09/2026 y obtuvo **10**; el TP4, el 23/10/2026, y
obtuvo **9**. Lo que se mantiene es lo que funcionó en los dos (el esquema de
presentación, las convenciones de figuras y el reparto entre motor y
post-procesamiento) y lo que se corrige es lo que la cátedra marcó en el TP4.
Los errores que se repiten de un TP al siguiente penalizan: esta lista se
vuelve a revisar contra las diapositivas antes de entregar.

---

## Devolución del TP4 (nota 9)

> Bien el orden general y los resultados mostrados. Hay detalles menores en
> algunas gráficas (formato y escala) y algunas cosas que aparecen no fueron
> explicadas suficientemente (Verlet con solución algebraica y "celda de
> índice", que aparece remarcada y no la mencionaron). Es cierto que las
> conclusiones deben estar basadas en los resultados, pero no deberían tener
> que volver atrás para mostrarlas, al menos no hasta que haya preguntas.
>
> **CUIDADO, importante:** las animaciones no se pueden ver; los videos están
> en privado.

| # | Qué dijeron | Cómo se corrige en el TP5 |
|---|---|---|
| — | Los videos estaban en privado | **Antes de entregar, los cinco videos se suben a YouTube como "no listado" y se abre cada link desde una ventana de incógnito** para verificar que se ven. Los links van en el PDF que se entrega (`youtube/titulos.md` lleva el título y la descripción de cada uno). |
| — | Las conclusiones no deberían obligar a volver atrás | Cada conclusión repite **la cifra** que la sostiene, y las cifras son todas de figuras ya mostradas. Ninguna conclusión necesita que se vuelva a una diapositiva anterior. |
| D3 | "¿Solución algebraica? ¿Qué quiere decir?" | **Ningún término aparece sin estar definido antes.** Todo lo que se dice de la capa de elusión está escrito en las diapositivas 6, 7 y 8, con las fórmulas completas y los casos límite. El glosario de términos propios es corto y fijo: *capa de elusión, conflicto, tiempo de anticipación, margen de espacio personal, target temporal, punto de mira, peso de urgencia, ventana del evento, error de ritmo y de forma*. |
| D8 | "¿Qué es la celda de índice?" | Lo mismo: no se nombra ninguna técnica de implementación que no se explique. Acá hay dos agentes, así que no hay estructuras de vecinos; lo único de implementación que se cuenta es por qué `dt` divide a `dtexp` en un número entero de partes, y tiene su propio esquema (diapositiva 9). |
| D11 | "No agrega casi nada; puede ser la leyenda de una animación. Nunca dicen cuándo ni cómo pasa de fresca a usada. Solo qué colores usan." | Las diapositivas de animación **dicen qué pasa, no qué colores hay**: cuándo la capa declara conflicto, qué hace con el target y qué cambia en la trayectoria, con las cifras del evento. Las convenciones de dibujo (disco lleno = simulado, punteado = medido, cruz verde = target temporal) van **una sola vez**, en gris, como última viñeta. |
| D12 | "Debería ser *primer tiempo en que*…" | Las definiciones de los observables están escritas con cuidado y revisadas: *instante de mínima aproximación*, *primer instante en que la capa declara conflicto*, *promedio temporal sobre los `Nm` instantes medidos*. |
| D16 | "Dejaron la explicación a medias. Deben poder explicar todo lo que muestran con claridad." | **Nada entra a la presentación si no se puede explicar entero en la diapositiva.** La franja de valores que empatan con el óptimo en los cortes tiene su definición escrita (diferencia pareada evento por evento, diapositiva de observables); la descomposición del residuo en ritmo y forma también. Lo que no entra explicado queda en `README.md` y en `report/guion.md`. |
| D18 | "Acá debe ser una representativa, no con promedios. La leyenda es más prolija si ponen x0 como título y los colores solo tienen el valor." | Las figuras de un evento son de **eventos representativos** (el 10, y para las trayectorias cuatro: 10, 5, 14 y 17, cada uno elegido por un motivo), nunca un promedio sobre eventos. En las figuras de dos paneles, el parámetro que distingue los paneles va como **título del panel** (`p2 = 0,070 m`) y la leyenda sólo lleva lo que cambia dentro del panel. |
| D24 | "El eje Y (N) es engañoso, tiene los valores equiespaciados, aunque en un caso pasa de 10 a 20 y en otro de 200 a 300." | **Ningún eje lleva valores equiespaciados que no lo sean.** Los mapas de `<E>(p1,p2)` usan `pcolormesh` sobre la grilla real (81 × 61 valores equiespaciados de verdad), con la barra de color en escala logarítmica rotulada con sus valores. La figura de convergencia usa doble logarítmica. |
| D26 | "La última conclusión no es correcta. Para n grande es en el centro; para n menores, solo tiene mucho espacio." | Cada conclusión se verificó contra la figura de la que sale, y las que son condicionales lo dicen (por ejemplo: `p1` queda determinado **sólo por abajo**, no "`p1 = 2,5 s` es el valor correcto"). |

---

## Devoluciones anteriores que se siguen aplicando

### Generales (TP2)

- Los miembros no se pisan en la exposición ni "aclaran" lo que creen que el
  compañero no dijo; el reparto es parejo en cantidad y en calidad.
- No se saltea ninguna sección de la presentación, y menos la de observables.
- Terminología consistente y sostenida, sin palabras no definidas antes.
- Tamaño de fuente armonioso dentro de cada diapositiva y entre diapositivas.
- Mostrar el trabajo intermedio a la cátedra antes de presentarlo.
- Cualquier integrante tiene que poder explicar todo lo presentado.
- Subir todo el material al Campus.

### Presentación (TP2 y borradores del TP3)

- Sin diapositiva de contenido ni carátulas de bloque dentro de Resultados;
  sólo los separadores de sección que pide la guía.
- Poco detalle al inicio: cada concepto se explica **una vez**, donde hace
  falta.
- Lo importante ocupa la pantalla: figura grande, texto mínimo. Cada
  diapositiva de figura es el gráfico grande más dos o tres viñetas.
- Tabla de parámetros en bloques, con las unidades en **un solo lugar**.
- UML **sólo del motor**, sin archivos ni post-procesamiento.
- Nombres de eje con la unidad y **en una sola línea**; coma decimal; el
  observable va al eje con su símbolo.
- Leyenda **dentro** del gráfico, sin tapar datos y más chica que el texto de
  la diapositiva.
- Sin rectas de referencia dibujadas a mano: si se compara con una ley, se
  ajusta y se informa el exponente.
- El error de un ajuste es el error cuadrático medio, y se muestra la curva
  `E(parámetro)` con su mínimo marcado (método de la Teórica 0).
- Sin la variable `M` en las figuras: se dice "promedio sobre N
  realizaciones" (acá, "promedio sobre los 19 eventos").
- Las conclusiones son un punteo corto.
- Cada diapositiva de figura lleva al costado los parámetros fijos bajo los
  que se obtuvo (guía §1.7), como última viñeta en gris y más chica.
- Diapositiva de cierre "Muchas gracias" (§2.6), sin la palabra "preguntas".
- Última diapositiva de contenido: la **declaración de uso de agentes de IA**.

---

## Lo específico del TP5

- El enunciado pide **dedicarle a la descripción matemática de la capa de
  elusión más tiempo del habitual**: son tres diapositivas seguidas (la
  detección del conflicto, el target temporal y los casos límite), con los dos
  esquemas en TikZ y todas las fórmulas.
- Para cada estudio hay que mostrar **una animación característica, la
  evolución temporal del observable primario y cómo se calcula el observable
  escalar**. Está en ese orden: animación sin capa, animación con capa,
  trayectorias, `e(t)` y recién después las superficies de `<E>`.
- Como en el TP4, hay **animaciones de apoyo** además de las de resultados: la
  capa mirada de cerca en un cruce sintético (para las diapositivas que la
  explican) y cada parámetro recorriendo su rango (para la de qué hace cada
  uno). Igual que las otras, cada una tiene su cuadro fijo en el PDF y su GIF
  para la charla.
- El cuadro fijo de cada animación se congela en el **último instante en
  conflicto antes del cruce simulado**, que es el momento en el que se ve la
  elusión y su target temporal, y la viñeta gris de la diapositiva lo dice.
- El observable escalar (las dos métricas) está definido **matemáticamente** en
  la diapositiva de observables, junto con cómo se promedia sobre peatones y
  sobre eventos y qué es la barra de error.
- La salida de la simulación es un archivo de texto y el módulo de animación
  corre aparte, sobre esos archivos.
- El zip de entrega lleva **sólo el motor final** (unos pocos kB), más el
  código con el que se hacen las animaciones, como pidió la cátedra en el TP3.

---

## Lo que la cátedra agregó sobre el TP5 (aviso del 04/11/2026)

- **No hay solución pre-establecida.** La formulación del problema y la
  estrategia de solución son lo más interesante del TP, así que la presentación
  está **centrada en la metodología**: por qué una capa de dos parámetros, qué
  se probó y se descartó (las cuatro variantes de diseño y las tres capas de
  campos), con qué criterio se decide que dos pares de parámetros empatan
  (diferencia pareada, no barra de error) y cómo se recorta la ventana de cada
  evento.
- **Hay que llevar ideas y propuestas a clase, no esperar al resultado final.**
  Las dudas de `PLAN.md` §8 son para eso. La primera —cómo recortar la ventana
  de cada prueba— cambió los números de todo el trabajo: ver la consulta del
  11/11, abajo.
- **La declaración de uso de IA cambia de forma:** ya no es una diapositiva
  sola, sino un **apéndice que describe todas las libertades que se tomó la IA y
  que el grupo tuvo que corregir**. Cuantas más correcciones se reporten, mejor.
  El registro está en `IA.md` y baja al apéndice A1–A3 de
  `report/presentacion.tex`; la diapositiva de uso de agentes de IA se mantiene
  y remite al apéndice.

---

## Consulta del 11/11/2026 (Ariel Salgado)

A grandes rasgos: el trabajo viene bien, y hay que **volver a mostrarlo el
viernes 13/11**. Como el algoritmo es complejo, Ariel se lo explica a Rafael
para que los dos lo conozcan antes de la presentación; si en la charla pasa
rápido no importa, pero es en lo que más tiempo hay que gastar.

| # | Qué dijo | Cómo quedó |
|---|---|---|
| 1 | La definición de nuestro modelo de target va en la **introducción**, no en Simulaciones. | La diapositiva "Del evento medido al evento simulado: condiciones y target" (el esquema `parametros-evento.tikz`: `r(0)`, `v(0)`, target final y `v^d`) pasó a la Introducción, entre el modelo y la capa. En Simulaciones queda sólo la tabla de parámetros. |
| 2 | Lo de la simetría está muy bien. Dejar **todo** el análisis de optimizar `d_s` y `t_a`, y **además**, al final, después de presentar todo, mostrar la optimización de `α` como un opcional extra. | Los ítems b, c y d calibran `(t_a, d_s)` con la capa simétrica, sin tocar. Después de "Muchas gracias" van tres diapositivas de extra: `<E>(α)` con su óptimo, el histograma del `α` de cada evento con la línea del global y el `α` calibrado contra el medido en las trayectorias (`make asimetria`, `make asimetria-figuras`, `visualization/asymmetry.py`; imágenes `slide-extra-*`). |
| 3 | Para explicar la fórmula, hacer GIF. El esquema de la detección está bueno pero **sobrecargado**: sobran los `r_i`, `v_i` de todo. Convertirlo en un GIF. | El esquema TikZ quedó sin los rótulos de `r` y `v` (sólo `i`, `j`, `d*`, `D` y la condición de conflicto). Y `visualization/explain.py` arma el mismo esquema de a un elemento, en seis pasos con la fórmula de cada uno al pie, hasta el target temporal de los dos: `gif/09 - … La capa de elusion paso a paso.gif`. Los cuadros finales de los pasos 4 y 6 están en `slides-images/` (`06b` y `07b`). |
| 4 | Un buen peso de la presentación es **explicar el algoritmo**. | El guion le da a la capa y al bucle más de un tercio del tiempo (`report/guion.md`), con el GIF paso a paso y el del cruce cabeza a cabeza. |
| 5 | **El recorte del dataset está mal** como estaba hecho. La figura de las 38 trayectorias muestra justo de dónde parten todos: usar ese rango de valores **hardcodeado** (a ojo, 1 y 8; mirarlo con más detalle). Sacar todo lo del percentil y la posición vertical; detectarlo con una **restricción en el eje x**. (Si no, también vale hacerlo a mano para cada uno.) | El motor recorta cada evento a `1,0 m ≤ x ≤ 7,7 m` para los dos peatones (`--xmin`, `--xmax`; `trimToCorridor` en `engine/src/experiment.cpp`). Se sacaron `--arranque`, `--ritmo` y `--corredor` con todo su código, y `ESTUDIO.md`, que los medía. Los valores salen de mirar los datos con más detalle: las cabeceras de las filas están en `x ≈ 0,6` y `8,1 m`, y el tramo deja 0,4 m de cada lado (con 8 la ventana terminaba con el peatón frenando contra la otra fila). La figura de las trayectorias ahora dibuja las dos verticales del tramo. `make ventana` muestra que con otros cinco tramos la capa baja el error entre 90 % y 96 %: el resultado no depende del valor exacto. **Todos los números del trabajo cambiaron** (README, "Resultados"). |
| 6 | Trayectorias: le gustó, pero para la diapositiva quiere **un par representativas (unas 4)** que sirvan para mostrar lo que queremos contar. | Una sola figura con cuatro paneles (`visualization/representative.py`, `slide-19`): el evento 10 (el que más gana con la capa), el 5 (el cruce medido más ajustado, 0,49 m), el 14 (el más holgado, 0,92 m) y el 17 (el único en que el modelo elude por el lado opuesto). |
| 7 | Los heatmaps están **ultra sobrecomplejizados**: reducirlos para que queden como los de los TP anteriores. | Los mapas de `<E>(p1, p2)` son el mapa, la barra de color y la estrella del óptimo, con el mismo mapa de color que el del TP4. Se fueron la escala de potencia, las curvas de nivel rotuladas y el velo de los pares que empatan (la franja de valores que empatan sigue en los cortes, que es donde se lee). |
| 8 | Para la optimización por peatón: **histograma de los parámetros con una línea vertical en el óptimo global**. | Así quedaron las dos: los óptimos por evento (`slide-27`) y los óptimos por peatón del opcional (`slide-29`), un panel por parámetro. El extra de `α` usa el mismo formato. |

Lo que aparece con el recorte nuevo y hay que llevar el viernes está en
`PLAN.md` §8: el valor del tramo, el evento 1 (se queda corto por un hueco de
seguimiento), la rampa de urgencia (sin ella el error baja un 15–20 %) y la
validación cruzada (+36 %, por dos eventos en los que el lado depende de
`t_a`).
