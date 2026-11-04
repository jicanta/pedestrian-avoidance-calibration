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
| D3 | "¿Solución algebraica? ¿Qué quiere decir?" | **Ningún término aparece sin estar definido antes.** Todo lo que se dice de la capa de elusión está escrito en las diapositivas 5, 6 y 7, con las fórmulas completas y los casos límite. El glosario de términos propios es corto y fijo: *capa de elusión, conflicto, tiempo de anticipación, margen de espacio personal, target temporal, punto de mira, peso de urgencia, ventana del evento, error de ritmo y de forma*. |
| D8 | "¿Qué es la celda de índice?" | Lo mismo: no se nombra ninguna técnica de implementación que no se explique. Acá hay dos agentes, así que no hay estructuras de vecinos; lo único de implementación que se cuenta es por qué `dt` divide a `dtexp` en un número entero de partes, y tiene su propio esquema (diapositiva 9). |
| D11 | "No agrega casi nada; puede ser la leyenda de una animación. Nunca dicen cuándo ni cómo pasa de fresca a usada. Solo qué colores usan." | Las diapositivas de animación **dicen qué pasa, no qué colores hay**: cuándo la capa declara conflicto, qué hace con el target y qué cambia en la trayectoria, con las cifras del evento. Las convenciones de dibujo (disco lleno = simulado, punteado = medido, cruz verde = target temporal) van **una sola vez**, en gris, como última viñeta. |
| D12 | "Debería ser *primer tiempo en que*…" | Las definiciones de los observables están escritas con cuidado y revisadas: *instante de mínima aproximación*, *primer instante en que la capa declara conflicto*, *promedio temporal sobre los `Nm` instantes medidos*. |
| D16 | "Dejaron la explicación a medias. Deben poder explicar todo lo que muestran con claridad." | **Nada entra a la presentación si no se puede explicar entero en la diapositiva.** La región "pares que empatan" de los mapas tiene su definición escrita (diferencia pareada evento por evento, diapositiva 11); la descomposición del residuo en ritmo y forma también. Lo que no entra explicado queda en `README.md` y en `report/guion.md`. |
| D18 | "Acá debe ser una representativa, no con promedios. La leyenda es más prolija si ponen x0 como título y los colores solo tienen el valor." | Las figuras de un evento son de **un evento representativo** (el 10), nunca un promedio sobre eventos. En las figuras de dos paneles, el parámetro que distingue los paneles va como **título del panel** (`p2 = 0,070 m`) y la leyenda sólo lleva lo que cambia dentro del panel. |
| D24 | "El eje Y (N) es engañoso, tiene los valores equiespaciados, aunque en un caso pasa de 10 a 20 y en otro de 200 a 300." | **Ningún eje lleva valores equiespaciados que no lo sean.** Los mapas de `<E>(p1,p2)` usan `pcolormesh` sobre la grilla real (81 × 61 valores equiespaciados de verdad) y la escala de color es de potencia, con curvas de nivel rotuladas, porque en escala lineal el valle quedaría de un solo tono. La figura de convergencia usa doble logarítmica. |
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
- El observable escalar (las dos métricas) está definido **matemáticamente** en
  la diapositiva de observables, junto con cómo se promedia sobre peatones y
  sobre eventos y qué es la barra de error.
- La salida de la simulación es un archivo de texto y el módulo de animación
  corre aparte, sobre esos archivos.
- El zip de entrega lleva **sólo el motor final** (unos pocos kB), más el
  código con el que se hacen las animaciones, como pidió la cátedra en el TP3.
