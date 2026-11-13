# Videos de las animaciones

Se suben a YouTube como **no listados** (no privados: en el TP4 la cátedra no
pudo verlos). Antes de entregar hay que abrir cada link desde una ventana de
incógnito y verificar que se ve. Los links van en el PDF que se entrega
(`PENDIENTE-0n` en `report/presentacion.tex`, uno por video, en este orden);
en la presentación en vivo se usan los GIF de `gif/`.

Los `.mp4` se generan con `make animations` y `make apoyo` y se copian acá con
`make youtube`; no se versionan.

Convenciones de dibujo, iguales en los videos de eventos: disco lleno = agente simulado, disco
punteado = posición medida en el mismo instante, cruz verde = target temporal
mientras la capa declara conflicto (y el disco lleva borde negro). Un cuadro
por instante medido, a 15 cuadros por segundo: corren en tiempo real.

---

### 01 — Evento 10 con la capa de elusión calibrada (PENDIENTE-01)

**Título:** SdS TP5 G10 — Elusión 1 contra 1: evento 10 con la capa calibrada

**Descripción:** Simulación de Sistemas (ITBA, 2026 Q2) — TP5, Problema 1,
Grupo 10, comisión S2. Evento 10 de los datos experimentales de elusión 1
contra 1 de frente, simulado con SFM sin fuerza social y la capa de elusión
calibrada (t_a = 2,15 s, d_s = 0,13 m). Es el evento que más gana con la capa.

### 02 — Evento 10 sin la capa (PENDIENTE-02)

**Título:** SdS TP5 G10 — Elusión 1 contra 1: evento 10 sin la capa (SFM puro)

**Descripción:** El mismo evento con la capa apagada (t_a = 0): el SFM sin
fuerza social no anticipa, los dos agentes van derecho a su target y se chocan
de frente. El desvío lo produce la fuerza de contacto, tarde.

### 03 — Evento 5: el cruce más ajustado (PENDIENTE-03)

**Título:** SdS TP5 G10 — Elusión 1 contra 1: evento 5, el cruce más ajustado

**Descripción:** Evento 5, el de menor distancia mínima medida de las 19
pruebas (0,49 m, menos que la distancia de contacto 2r = 0,5 m), con la capa
calibrada: los agentes pasan a 0,58 m.

### 04 — Evento 14: el cruce más holgado (PENDIENTE-04)

**Título:** SdS TP5 G10 — Elusión 1 contra 1: evento 14, el cruce más holgado

**Descripción:** Evento 14, el de mayor distancia mínima medida (0,92 m). Los
agentes pasan a 0,57 m: la distancia de paso del modelo es una sola para todos
los pares.

### 05 — Evento 17: por el lado opuesto (PENDIENTE-05)

**Título:** SdS TP5 G10 — Elusión 1 contra 1: evento 17, elusión por el lado opuesto

**Descripción:** Evento 17, el único de los 19 en que la capa calibrada elude
por el lado contrario al que usaron las personas.

### 06 — Apoyo: la capa de elusión cabeza a cabeza (PENDIENTE-06)

**Título:** SdS TP5 G10 — La capa de elusión en acción: cruce de frente con tres márgenes

**Descripción:** Cruce sintético de dos agentes a 1 m/s, 8 m aparte y corridos
4 cm, con tres márgenes de espacio personal d_s a la vez (un carril por valor,
t_a = 2,15 s). Se dibuja lo que la capa calcula en cada instante: las posiciones
predichas al instante de mínima aproximación (discos punteados), la
separación predicha d* (trazo entre ellos) y el target temporal (cruz).

### 07 — Apoyo: qué hace d_s (PENDIENTE-07)

**Título:** SdS TP5 G10 — Qué hace d_s: el evento 10 con el margen recorriendo su rango

**Descripción:** El evento 10 simulado con d_s de 0 a 0,6 m (t_a = 1,5 s) y, al
lado, el corte de <E(2)> del ítem b con el punto que marca dónde está. d_s fija
por dónde se pasa.

### 08 — Apoyo: qué hace t_a (PENDIENTE-08)

**Título:** SdS TP5 G10 — Qué hace t_a: el evento 10 con la anticipación recorriendo su rango

**Descripción:** El evento 10 simulado con t_a de 0 a 4 s (d_s = 0,14 m) y, al
lado, el corte de <E(2)>. t_a decide si llegan a correrse; desde ~1,5 s casi no
cambia.

### 09 — Apoyo: la capa de elusión paso a paso (PENDIENTE-09)

**Título:** SdS TP5 G10 — La capa de elusión paso a paso

**Descripción:** El esquema de la capa armado de a un elemento, con la fórmula
de cada paso: se extrapolan las dos trayectorias, se busca el instante de
mínima aproximación τ* y la separación d* que habrá ahí, se la compara con la
separación requerida D, y si no alcanza el target de cada agente se corre lo
que falta, hacia lados opuestos.

### 10 — Los 19 eventos (sólo GIF)

Los 19 eventos con la capa calibrada, un panel por evento. No va a YouTube: es
el GIF de `gif/` para mostrar en la consulta que la ventana de cada evento es
el cruce.
