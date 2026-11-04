# Guion de la presentación

Dos o tres puntos para decir en cada diapositiva, con el tiempo de cada una.
El número es el del nombre de la imagen en `slides-images/` (el orden del mazo
que se arma en Google Slides; los separadores de sección no cuentan). Las
cifras son las de las figuras mostradas. Lo que va en *"Si preguntan"* no se
dice: es para contestar.

**Total: 13:00.** Reparto sugerido: expositor A dice 1–9 (4:10), B dice 10–22
(4:30), C dice 23–34 (4:20). Las prescindibles si hay que acortar están en el
README (19, 24, 33, 31, 29, 14, en ese orden).

---

## Portada — 0:10 (A)

- Calibración de una capa de elusión con trayectorias experimentales: TP5,
  problema 1. Grupo 10, comisión S2.

## Introducción (separador) — 0:05

- Primero el experimento y el modelo, después la capa de elusión con más
  detalle que de costumbre, porque es lo que se propone y calibra.

## 2. El experimento — `slide-02-experimento.png` — 0:30

- Una persona sale de la fila izquierda, otra de la fila de abajo a la
  derecha, y se cruzan de frente alrededor de y = 2 m. La cátedra da las dos
  trayectorias medidas a 15 cuadros por segundo: 19 eventos, 38 peatones, 2543
  instantes.
- Pasan a entre 0,49 y 0,92 m, con 2r = 0,5 m: se eluden **sin tocarse**. Lo
  que hay que proponer es una capa de dos parámetros que reproduzca eso.

## 3. Los datos — `slide-03-eventos-trayectorias.png` — 0:25

- Las 38 trayectorias superpuestas. El arco de elusión es sistemático: el que
  sale por la izquierda baja y el que sale por la derecha sube.
- En 14 de los 19 cruces cada uno pasó por su derecha; en 5, al revés. No es
  una convención estricta, y eso vuelve al final.

## 4. Modelo: SFM sin fuerza social — 0:35

- Newton con dos términos: conducción hacia el target (relaja v a la deseada
  en τ = 0,5 s) y contacto granular (normal y fricción), que sólo existe con
  solapamiento. Sin el término social A·exp(…): es el enunciado.
- Así el modelo **no anticipa**: va derecho al target y la única señal del otro
  es tocarlo. Lo único que decide a dónde va es ê^d, y ahí actúa la capa, y en
  ningún otro lado.
- El agente se detiene al llegar al target (a menos de un radio).
- *Si preguntan por qué SFM y no CPM:* las distancias mínimas casi nunca bajan
  de 2r, así que en CPM sin contacto el agente camina a vd en recta y la
  trayectoria queda enteramente a cargo de la capa; en SFM el τ le da inercia
  a la respuesta. Y el dt de SFM es libre, que es lo que permite dividir Δt_exp
  en partes enteras.

## 5. Capa (1/3): detección — `slide-05-elusion-deteccion.png` — 0:45

- Con Δr y Δv se extrapolan las dos trayectorias: τ* es el instante de mínima
  aproximación y d* la separación que habrá ahí.
- Dos parámetros: p1 = t_a, tiempo de anticipación, y p2 = d_s, margen de
  espacio personal: D = 2r + d_s es a cuánto se quiere pasar.
- Hay conflicto si 0 < τ* ≤ t_a y d* < D.

## 6. Capa (2/3): el target temporal — `slide-06-elusion-target.png` — 0:50

- q_i es dónde estaría el agente en τ* si siguiera derecho a su target; ŝ es
  el lado hacia el que los dos ya van a estar corridos; (D − d*) es exactamente
  la separación que falta.
- El target temporal es q_i corrido lateralmente esa separación, pesada por
  la urgencia w = 1 − τ*/t_a. La velocidad deseada sólo cambia de dirección,
  nunca de módulo.

## 7. Capa (3/3): por qué así — 0:40

- Recíproca (los dos calculan lo mismo con ŝ opuesto), continua en los dos
  bordes del disparo (por w), con el límite correcto cuando el conflicto es
  inminente (target puramente lateral) y vuelta automática al target final.
- Es la geometría de Karamouzas (Teórica 7) resuelta como "goal temporario"
  y no como fuerza. Diferencia: se predice con las velocidades actuales de los
  dos, así la elusión sale recíproca.

## 8. La capa en acción — `slide-08-capa-en-accion.png` — 0:25 (GIF)

- Cruce sintético, tres márgenes a la vez. Discos punteados: posiciones
  predichas en τ*; trazo: d*; cruz: target temporal. A mayor p2, más lejos del
  camino queda el target.

## 8b. ¿Y con campos? — `slide-08b-alternativas.png` — 0:30

- Se probaron tres capas más, todas de dos parámetros y como target temporal,
  con repulsión A·exp(−(d−2r)/B): isotrópica, lateral y predictiva.
- La isotrópica queda lejos (−52 % contra −63 %): de frente la repulsión no
  tiene componente lateral, lo mismo que dice la Teórica 7. Las otras dos
  empatan con la predictiva dentro del error pareado, pero sus óptimos
  degeneran (B → 0 es un escalón; B = 4,5 m es empujar de costado siempre).
- *Si preguntan:* la predictiva se queda porque sus dos parámetros tienen
  unidades y lectura directa, y porque es continua.

## Implementación (separador) — 0:05 (B)

## 9. Motor — `slide-09-motor-uml.png` — 0:25

- Avoidance sólo devuelve el target temporal; Model no sabe que existe. El
  motor calcula las dos métricas porque son lo que el barrido minimiza (93 879
  corridas); promedios, óptimos y particiones salen después en Python del mismo
  archivo.

## 10. El bucle y la grilla — `slide-10-bucle.png` — 0:25

- Beeman predictor-corrector, porque la fuerza depende de v (conducción y
  fricción). Δt = Δt_exp/n con n entero: cada instante medido cae exacto en un
  paso y no se interpola nada.

## Simulaciones (separador) — 0:05

## 11. Parámetros — `slide-11-parametros-tabla.png`, `slide-11-parametros-evento.png` — 0:30

- Los del modelo son los del paper, salvo el radio que lo fija el enunciado.
  De cada evento salen r(0), v(0), el target final y vd. Los dos únicos
  parámetros libres son los de la capa.

## 12. Observables — 0:40

- Observable primario: el apartamiento instantáneo e(t), al mismo instante
  (métrica 1) o al punto más cercano de toda la simulada (métrica 2). El
  escalar es su promedio temporal; la 1 castiga forma y tiempo de paso, la 2
  sólo la forma. Error de un evento: promedio de sus 2 peatones; poblacional:
  promedio sobre los 19.
- Barra de error: error estándar de la media entre eventos. Pero para decir
  qué pares **empatan** con el óptimo se usa la diferencia pareada evento por
  evento, porque todos los pares se miden sobre los mismos 19.

## 13. Casos estudiados — `slide-13-eventos-distancia-vs-t.png` — 0:30

- La ventana de cada evento es la parte en que los dos ya caminan (≥ 0,3 m/s):
  al principio de varias pruebas uno está parado en la fila y su rapidez media
  —que es vd— quedaría muy baja. Se pierde el 9 % de los instantes y los 19
  cruces siguen adentro.
- Barrido de 81 × 61 pares × 19 eventos, 62 s. Validación cruzada con 500
  particiones de 13/6.

## Resultados (separador) — 0:05

## 14. Paso de integración — `slide-14-convergencia-dt.png` — 0:20

- La tolerancia del 0,01 % se cumple desde n = 16; se usa n = 64, 1 ms, que
  ya está en el piso y cuesta un minuto el barrido entero.

## 15. Evento 10 sin capa — `slide-15-animacion-evento10-sin-capa.png` — 0:20 (GIF)

- Sin capa van derecho y se chocan de frente (0,49 m, menos que 2r); el
  contacto los separa a los empujones. E(1) = 7,9 m², el peor de los 19.

## 16. Evento 10 con capa — `slide-16-animacion-evento10.png` — 0:25 (GIF)

- Conflicto en 36 de 140 instantes, se corren de costado y se cruzan uno
  arriba y otro abajo. E(1) baja de 7,9 a 1,4 y E(2) de 4,0 a 0,07 m².

## 17. Evento 10: trayectorias — `slide-17-evento10-trayectorias.png` — 0:25

- Con la capa el arco aparece en el lugar y con la amplitud correctos, aunque
  en espejo (el lado, al final). Lo que queda es el retraso: vd constante
  contra personas que aceleran y frenan.

## 18. Evento 10: observable primario — `slide-18-evento10-observable.png` — 0:20

- La métrica 1 se acumula con el retraso; la 2 se queda abajo porque mira sólo
  la forma: 1,40 contra 0,07 m², un factor 20 que es puro tiempo de paso.

## 19. Evento 10: distancia — `slide-19-evento10-distancia.png` — 0:15

- El mínimo simulado es 0,50 m, cerca del D = 0,57 que pide la capa; medido,
  0,63. Y ocurre antes, otra vez por el ritmo.

## 20. Qué hace cada parámetro — `slide-20-que-hace-p2.png` — 0:25 (GIF)

- p2 fija por dónde se pasa: con 0,07 rozándose como las personas, con 0,3 y
  0,6 se abren de más y ⟨E⟩ sube. p1 decide si llegan a correrse: con 0,5 s
  reaccionan tarde; desde 1,2 s no cambia nada.

## 21. Superficie, métrica 1 — `slide-21-superficie-metrica1.png` — 0:30

- Óptimo en (2,50 s, 0,07 m): 1,48 m² contra 2,73 sin capa, **−46 %**. El velo
  blanco son los pares que empatan: p1 de 0,85 a 4 s. Verificado hasta 8 s.

## 22. Cortes, métrica 1 — `slide-22-cortes-metrica1.png` — 0:25

- p1 sólo queda determinado por abajo: cae hasta 1,2 s y después es plano.
  Con más de un segundo el agente ya llega a correrse lo que necesita. p2 sí
  tiene mínimo claro en 0,07 m.

## 23. Superficie, métrica 2 — `slide-23-superficie-metrica2.png` — 0:30 (C)

- Mismo valle, más profundo: 0,84 → 0,314 m², **−63 %**. Óptimo en
  (3,85 s, 0,05 m) y región que empata diez veces más chica: sin el tiempo de
  paso, la métrica determina mejor. D = 0,57 y 0,55 m: casi lo mismo.

## 24. Cortes, métrica 2 y comparación — `slide-24-cortes-metrica2.png` — 0:20

- Los óptimos coinciden en p2 y difieren en p1, el parámetro plano.
  Intercambiarlos cuesta menos del 2 %: eligen la misma capa.

## 25. Óptimos individuales — `slide-25-optimos-individuales.png` — 0:25

- En p2 están todos juntos (mediana 0,05 m); en p1, desparramados, 8 en el
  borde. 4 de 19 eligen p1 = 0: a esos la capa no les sirve.

## 26. Cuánto se gana — `slide-26-errores-por-evento.png` — 0:25

- Individualizar baja ⟨E(1)⟩ de 1,48 a 1,22 (−17 %) y ⟨E(2)⟩ de 0,314 a
  0,296 (−6 %): poco para 19 pares contra uno. El error no está en los
  parámetros.

## 27. Dos poblaciones — `slide-27-dos-poblaciones.png` — 0:40

- Los eventos se separan solos por el ángulo entre v(0) y el camino nominal:
  < 32° (ya en el corredor, 10) o > 60° (sale de la fila, 9). ⟨E(2)⟩: 0,08
  contra 0,57 m².
- En los de la fila la recta al target es la ruta equivocada, y eso lo fija
  el enunciado. Calibrando sólo con los 10 del corredor: (4 s, 0,07 m) y
  0,078 m², **−92 %**; sólo con la fila, −19 %.

## 28. Evento 14 — `slide-28-animacion-evento14.png` — 0:20 (GIF)

- Las dos personas suben por la fila y doblan en y ≈ 2 m; los agentes van en
  diagonal desde t = 0 y se cruzan cuando las personas aún están a 5,6 m.

## 29. Ritmo y forma — `slide-29-residuo-descomposicion.png` — 0:20

- En el corredor el 88 % es longitudinal: ritmo. La forma, lo que la capa
  decide, es el 12 %.

## 30. El lado — `slide-30-residuo-lado.png` — 0:25

- Acierta en 12 de 19: 6 de 10 en el corredor. De frente lo decide un
  corrimiento de centímetros; las personas lo deciden antes (14 de 19 por su
  derecha).

## 31. Evento 3 — `slide-31-animacion-evento03.png` — 0:15 (GIF)

- En el corredor, elusión correcta (0,57 contra 0,60 m) pero en espejo.

## 32. Validación cruzada — `slide-32-validacion-error.png` — 0:25

- 500 particiones de 13/6: el error de validación queda un 5,2 % por encima
  del ítem b (0,2 % con la métrica 2). Con dos parámetros y 19 eventos no hay
  sobreajuste.

## 33. Qué par elige cada partición — `slide-33-validacion-parametros.png` — 0:15

- 52 pares distintos; la dispersión está casi toda en p1. Lo mismo que la
  región que empata, medido de otra manera.

## Conclusiones (separador) — 0:05

## 34. Conclusiones — 0:50

- Leer las seis, cada una con su cifra: −46 % y −63 %; óptimos con la misma
  distancia de paso; p1 sólo por abajo; dos poblaciones (−92 % en el corredor);
  individualizar gana poco porque el error es ritmo y lado; sin sobreajuste.

## 35. Uso de agentes de IA — 0:10

- Claude Code; en qué se usó y en qué no.

## Muchas gracias
