# Guion de la presentación

Dos o tres puntos para decir en cada diapositiva, con el tiempo de cada una.
El número es el del nombre de la imagen en `slides-images/` (el orden del mazo
que se arma en Google Slides; los separadores de sección no cuentan). Las
cifras son las de las figuras mostradas. Lo que va en *"Si preguntan"* no se
dice: es para contestar.

**Total: 13:00.** La cátedra pidió en la consulta del 11/11 que **explicar el
algoritmo** sea lo que más tiempo lleve: las diapositivas 5 a 9 y la 12 suman
4:10, un tercio de la charla. Reparto sugerido: expositor A dice 1–10 (5:05),
B dice 11–24 (4:00), C dice 25–36 (3:55). Las prescindibles si hay que acortar
están en el README (21, 26, 35, 33, 30, 10, 16, en ese orden).

---

## Portada — 0:10 (A)

- Calibración de una capa de elusión con trayectorias experimentales: TP5,
  problema 1. Grupo 10, comisión S2.

## Introducción (separador) — 0:05

## 2. El experimento — `slide-02-experimento.png` — 0:25

- Una persona sale de la fila izquierda, otra de la fila de abajo a la
  derecha, y se cruzan de frente alrededor de y = 2 m. La cátedra da las dos
  trayectorias medidas a 15 cuadros por segundo: 19 eventos, 38 peatones.
- Pasan a entre 0,49 y 0,92 m, con 2r = 0,5 m: se eluden **sin tocarse**. Lo
  que hay que proponer es una capa de dos parámetros que reproduzca eso.

## 3. Los datos y el tramo que se simula — `slide-03-eventos-trayectorias.png` — 0:30

- Las 38 trayectorias enteras. Se ve de dónde parten todos: las cabeceras de
  las dos filas, en x ≈ 0,6 y 8,1 m.
- Cada evento se recorta al tramo de 1 a 7,7 m, el mismo para los 19: empieza
  cuando el último de los dos entra y termina cuando el primero sale. Afuera
  queda la fila.
- En 14 de los 19 cruces cada uno pasó por su derecha.
- *Si preguntan por qué 7,7 y no 8:* la cabecera de la fila derecha está en
  8,1 m; con 8 la ventana terminaba con el peatón frenando contra la fila. Con
  seis tramos distintos la capa baja el error entre 90 y 96 %.

## 4. Modelo: SFM sin fuerza social — 0:30

- Newton con dos términos: conducción hacia el target (relaja v a la deseada
  en τ = 0,5 s) y contacto granular (normal y fricción), que sólo existe con
  solapamiento. Sin el término social: es el enunciado.
- Así el modelo **no anticipa**: va derecho al target y la única señal del otro
  es tocarlo. Lo único que decide a dónde va es ê^d, y ahí actúa la capa, y en
  ningún otro lado.
- *Si preguntan por qué SFM y no CPM:* el τ le da inercia a la respuesta, y el
  dt de SFM es libre, que es lo que permite dividir Δt_exp en partes enteras.

## 5. Condiciones y target de cada agente — `slide-05-parametros-evento.png` — 0:30

- Cada agente arranca en la posición y con la velocidad medidas en el primer
  instante de su ventana.
- Su target final es la **última posición medida dentro del tramo**: queda
  sobre el corredor. El módulo de la velocidad deseada es la rapidez media de
  su trayectoria, entre 1,15 y 1,63 m/s.
- Se simula hasta el último instante medido: entre 2,8 y 5,3 s por evento.

## 6. Capa (1/3): detección — `slide-06-elusion-deteccion.png` + GIF 09 — 1:10

- **Pasar el GIF paso a paso y hablar encima.** Dos peatones en curso de
  colisión. Se extrapolan las dos trayectorias en línea recta, con las
  velocidades que tienen ahora, y se mira la distancia entre las dos posiciones
  extrapoladas mientras avanza τ.
- El instante en que esa distancia es mínima es τ*, y la distancia, d*. Las dos
  salen de una cuenta cerrada con Δr y Δv.
- Los dos parámetros: t_a, el tiempo de anticipación (sólo se reacciona a
  lo que va a pasar dentro de t_a), y d_s, el margen de espacio personal:
  D = 2r + d_s es a cuánto se quiere pasar.
- Hay conflicto si 0 < τ* ≤ t_a y d* < D.

## 7. Capa (2/3): el target temporal — `slide-07-elusion-target.png` — 1:00

- (Sigue el GIF, pasos 5 y 6.) q_i es dónde estaría el agente en τ* si
  siguiera derecho a su target; ŝ es el lado hacia el que los dos ya van a
  estar corridos; (D − d*) es exactamente la separación que falta.
- El target temporal es q_i corrido lateralmente esa separación, pesada por
  la urgencia w = 1 − τ*/t_a. La velocidad deseada sólo cambia de dirección,
  nunca de módulo.
- El otro hace la misma cuenta y le sale el lado opuesto: se corren hacia
  lados contrarios sin ponerse de acuerdo.

## 8. Capa (3/3): por qué así — 0:35

- Recíproca, continua en los dos bordes del disparo (por w), con el límite
  correcto cuando el conflicto es inminente (target puramente lateral) y vuelta
  automática al target final.
- Es la geometría de Karamouzas (Teórica 7) resuelta como "goal temporario"
  y no como fuerza. Diferencia: se predice con las velocidades actuales de los
  dos, así la elusión sale recíproca.

## 9. La capa en acción — `slide-09-capa-en-accion.png` — 0:25 (GIF 06)

- Cruce sintético, tres márgenes a la vez. Discos punteados: posiciones
  predichas en τ*; trazo: d*; cruz: target temporal. A mayor d_s, más lejos del
  camino queda el target.

## 10. ¿Y con campos? — `slide-10-alternativas.png` — 0:25

- Se probaron tres capas más, de dos parámetros y como target temporal, con
  repulsión A·exp(−(d−2r)/B): isotrópica, lateral y predictiva.
- La isotrópica queda lejos (−66 % contra −94 %): de frente la repulsión no
  tiene componente lateral. El campo predictivo empata.
- El lateral da un error algo menor (0,014 contra 0,019 m²), pero con B en el
  borde de la grilla, 5 m: es empujar de costado siempre.
- *Si preguntan por qué no se usó el lateral:* no tiene horizonte ni distancia
  de paso; funciona acá porque hay un solo cruce de frente. La predictiva tiene
  dos parámetros con unidades y lectura directa.

## Implementación (separador) — 0:05 (B)

## 11. Motor — `slide-11-motor-uml.png` — 0:20

- Avoidance sólo devuelve el target temporal; Model no sabe que existe. El
  motor calcula las dos métricas porque son lo que el barrido minimiza (93 879
  corridas); promedios, óptimos y particiones salen después en Python del mismo
  archivo.

## 12. El algoritmo: el bucle — `slide-12-bucle.png` — 0:30

- En cada paso: la capa mira a los dos agentes y le da a cada uno su target
  (el temporal si hay conflicto, el final si no); con ese target sale la
  velocidad deseada; con ella, la fuerza de conducción más el contacto; y se
  integra.
- Beeman predictor-corrector, porque la fuerza depende de v. Δt = Δt_exp/n con
  n entero: cada instante medido cae exacto en un paso y no se interpola nada.

## Simulaciones (separador) — 0:05

## 13. Parámetros — `slide-13-parametros-tabla.png` — 0:20

- Los del modelo son los del paper, salvo el radio que lo fija el enunciado.
  Los dos únicos parámetros libres son los de la capa.

## 14. Observables — 0:35

- Observable primario: el apartamiento instantáneo e(t), al mismo instante
  (métrica 1) o al punto más cercano de toda la simulada (métrica 2). El
  escalar es su promedio temporal; la 1 castiga forma y tiempo de paso, la 2
  sólo la forma. Error de un evento: promedio de sus 2 peatones; poblacional:
  promedio sobre los 19.
- Barra de error: error estándar de la media entre eventos. Para decir qué
  valores **empatan** con el óptimo se usa la diferencia pareada evento por
  evento.

## 15. Casos estudiados — `slide-15-eventos-distancia-vs-t.png` — 0:20

- Los 19 eventos sobre su ventana: el cruce cae entre el 47 y el 80 % de la
  ventana, ninguno queda recortado.
- Barrido de 81 × 61 pares × 19 eventos, 32 s. Individual por evento y por
  peatón. Validación cruzada con 500 particiones de 13/6.

## Resultados (separador) — 0:05

## 16. Paso de integración — `slide-16-convergencia-dt.png` — 0:15

- Con n = 64, 1 ms, ⟨E⟩ se aparta 0,11 % del paso más fino: cien veces menos
  que el error estándar entre eventos.

## 17. Evento 10 sin capa — `slide-17-animacion-evento10-sin-capa.png` — 0:15 (GIF 02)

- Sin capa van derecho y se chocan de frente (0,48 m, menos que 2r). Pasa en
  los 19 eventos. E(1) = 1,91 m².

## 18. Evento 10 con capa — `slide-18-animacion-evento10.png` — 0:20 (GIF 01)

- Conflicto en 29 de 76 instantes, se corren de costado y se cruzan por el
  mismo lado que las personas. E(1) baja de 1,91 a 0,068 y E(2) de 0,99 a
  0,019 m². Con la capa no hay contacto en ninguno de los 19.

## 19. Cuatro eventos representativos — `slide-19-trayectorias-representativas.png` — 0:35

- El 10: sin capa el desvío lo hace el choque, tarde; con capa, el arco está
  donde lo hacen las personas.
- El 5 y el 14: las personas pasaron a 0,49 y a 0,92 m; el modelo, a 0,58 y
  0,57. La distancia de paso es una sola para todos.
- El 17: el único en que el modelo elude por el lado opuesto.

## 20. Evento 10: observable primario — `slide-20-evento10-observable.png` — 0:15

- La métrica 1 mira también el tiempo de paso; la 2, sólo la forma: 0,068 y
  0,019 m², un RMS de 26 y 14 cm.

## 21. Evento 10: distancia — `slide-21-evento10-distancia.png` — 0:10

- El mínimo simulado es 0,53 m, sobre el contacto; medido, 0,63.

## 22. Qué hace cada parámetro — `slide-22-que-hace-ds.png` — 0:20 (GIF 07)

- d_s fija por dónde se pasa: con 0,14 como las personas, con 0 se rozan, con
  0,3 y 0,6 se abren de más. t_a decide si llegan a correrse: con 0,5 s
  reaccionan tarde; desde 1,5 s casi no cambia.

## 23. Mapa, métrica 1 — `slide-23-superficie-metrica1.png` — 0:25

- Óptimo en (2,15 s, 0,13 m): 0,062 m² contra 0,87 sin capa, **−93 %**. Abajo
  y a la izquierda la capa reacciona tarde o no pide separación.

## 24. Cortes, métrica 1 — `slide-24-cortes-metrica1.png` — 0:25

- t_a sólo queda determinado por abajo: cae hasta 1,5 s y después es plano,
  hasta 8 s. El cruce llega entre 2,1 y 2,7 s después de empezar: con más
  anticipación el conflicto se declara desde el primer instante. d_s sí tiene
  mínimo claro en 0,13 m.

## 25. Mapa, métrica 2 — `slide-25-superficie-metrica2.png` — 0:20 (C)

- Mismo valle: 0,32 → 0,019 m², **−94 %**. Óptimo en (1,50 s, 0,14 m). Las dos
  métricas piden la misma distancia de paso, 0,63 y 0,64 m.

## 26. Cortes, métrica 2 — `slide-26-cortes-metrica2.png` — 0:15

- Coinciden en d_s y difieren en t_a, el parámetro plano. Los escalones son dos
  eventos (16 y 17) en los que el lado cambia con t_a.

## 27. Óptimos individuales — `slide-27-optimos-individuales.png` — 0:25

- Histograma de cada parámetro, con el global como línea vertical. En t_a, 17
  de 19 piden más de 3,75 s: más anticipación nunca molesta. En d_s cada par
  tiene el suyo, de 0,03 a 0,35 m.

## 28. Cuánto se gana — `slide-28-errores-por-evento.png` — 0:20

- Individualizar baja ⟨E(1)⟩ de 0,062 a 0,048 (−22 %) y ⟨E(2)⟩ de 0,019 a
  0,014 (−27 %). Casi la mitad de la ganancia de la métrica 1 es el evento 17.

## 29. Opcional: parámetros por peatón — `slide-29-optimos-por-peaton.png` — 0:25

- Cuatro parámetros por evento, dos por peatón. Los dos agentes están
  acoplados, así que el mínimo se busca en la grilla de los cuatro a la vez:
  1271 × 1271 combinaciones por evento, 30,7 millones de corridas.
- Histograma de los 38 óptimos con el global como línea vertical. En ningún
  evento los dos peatones eligen el mismo par: es la asimetría del reparto.

## 30. Opcional: cuánto se gana — `slide-30-errores-por-peaton.png` — 0:15

- Sobre la misma grilla: con dos por evento ⟨E(1)⟩ baja 23 %, con cuatro un
  11 % más (26 % y 31 % más con la métrica 2). Describe pero no predice: para
  un par nuevo no hay con qué estimar sus cuatro parámetros.

## 31. Ritmo y forma — `slide-31-residuo-descomposicion.png` — 0:15

- El 61 % del error es longitudinal: ritmo. La forma, lo que la capa decide,
  es el 39 %.

## 32. El lado y la distancia — `slide-32-residuo-lado.png` — 0:25

- Acierta el lado en 18 de 19, sin ninguna regla de lado. Lo que no reproduce
  es la dispersión: las personas pasaron a entre 0,49 y 0,92 m y el modelo
  siempre a ≈ 0,53.

## 33. Evento 17 — `slide-33-animacion-evento17.png` — 0:10 (GIF 05)

- Arrancan casi alineados y el modelo elige el otro lado. Con t_a = 1,5 s elude
  por el correcto.

## 34. Validación cruzada — `slide-34-validacion-error.png` — 0:25

- 500 particiones de 13/6: el error de validación es 0,084 contra 0,062 del
  ítem b, un 36 % más. Sigue siendo diez veces menos que sin capa.
- El segundo pico son las particiones en que el 16 o el 17 quedan en
  validación: sin ellos en validación la diferencia es del 5 %.

## 35. Qué par elige cada partición — `slide-35-validacion-parametros.png` — 0:10

- 6 pares distintos; d_s entre 0,07 y 0,14 m, t_a salta entre 1,5, 2,15 y 4 s.

## Conclusiones (separador) — 0:05

## 36. Conclusiones — 0:45

- Leer las seis, cada una con su cifra: −93 % y −94 %, y sin contacto; óptimos
  con la misma distancia de paso; t_a sólo por abajo; mismo lado en 18 de 19, y
  cada par a su propia distancia; el 61 % del residuo es ritmo; validación
  +36 % por dos eventos.

## 37. Uso de agentes de IA — 0:10

- Claude Code; en qué se usó y en qué no. Las correcciones, en el apéndice.

## Muchas gracias

---

## Extra, después del cierre: el reparto de la elusión (α)

La cátedra pidió mostrarlo al final, como un opcional. Un minuto y medio si
hay tiempo.

### Extra 1 — `slide-extra-1-alfa-curva.png`

- La capa calibrada es simétrica: los dos se corren lo mismo. Se le agrega α,
  la fracción de la separación que falta que se lleva el que sale de la
  izquierda; 0,5 es la capa simétrica.
- Con t_a y d_s en su óptimo, el mejor α global es 0,625 y 0,575, y gana 2 % y
  1 %: dentro del error. Como población, la capa simétrica alcanza.

### Extra 2 — `slide-extra-2-alfa-histograma.png`

- Evento por evento α va de 0,12 a 0,97: en cada par uno cede más, y cuál
  cambia de par en par. Con el α propio de cada par ⟨E(2)⟩ baja un 19 %.

### Extra 3 — `slide-extra-3-alfa-medido.png`

- α también se puede medir sin simular, del desvío lateral de cada uno en el
  cruce. El calibrado y el medido coinciden: r = 0,72 y 0,88. Es una propiedad
  de cada par, no un parámetro que absorbe residuo; pero describe y no predice.
