# Videos de las animaciones

Se suben a YouTube como **no listados** (no privados: en el TP4 la cátedra no
pudo verlos). Antes de entregar hay que abrir cada link desde una ventana de
incógnito y verificar que se ve. Los links van en el PDF que se entrega
(`PENDIENTE-0n` en `report/presentacion.tex`, uno por video, en este orden);
en la presentación en vivo se usan los GIF de `gif/`.

Los `.mp4` se generan con `make animations` y `make apoyo` y se copian acá con
`make youtube`; no se versionan.

Convenciones de dibujo, iguales en todos: disco lleno = agente simulado, disco
punteado = posición medida en el mismo instante, cruz verde = target temporal
mientras la capa declara conflicto (y el disco lleva borde negro). Un cuadro
por instante medido, a 15 cuadros por segundo: corren en tiempo real.

---

### 01 — Evento 10 con la capa de elusión calibrada (PENDIENTE-01)

**Título:** SdS TP5 G10 — Elusión 1 contra 1: evento 10 con la capa calibrada

**Descripción:** Simulación de Sistemas (ITBA, 2026 Q2) — TP5, Problema 1,
Grupo 10, comisión S2. Evento 10 de los datos experimentales de elusión 1
contra 1 de frente, simulado con SFM sin fuerza social y la capa de elusión
calibrada (p1 = 2,5 s, p2 = 0,07 m).

### 02 — Evento 10 sin la capa (PENDIENTE-02)

**Título:** SdS TP5 G10 — Elusión 1 contra 1: evento 10 sin la capa (SFM puro)

**Descripción:** El mismo evento con la capa apagada (p1 = 0): el SFM sin
fuerza social no anticipa, los dos agentes van derecho a su target y se chocan
de frente. El desvío lo produce la fuerza de contacto, tarde.

### 03 — Evento 5 (PENDIENTE-03)

**Título:** SdS TP5 G10 — Elusión 1 contra 1: evento 5

**Descripción:** Evento 5, el de menor distancia mínima medida de las 19
pruebas (0,49 m, menos que la distancia de contacto 2r = 0,5 m), con la capa
calibrada.

### 04 — Evento 14: los dos salen de la fila (PENDIENTE-04)

**Título:** SdS TP5 G10 — Elusión 1 contra 1: evento 14, los dos salen de la fila

**Descripción:** Evento 14: las dos personas caminan primero por la fila,
hacia arriba, y recién después doblan al corredor; los agentes van derecho al
target desde el principio. La recta al target final es la ruta equivocada, y
eso la capa no lo puede arreglar.

### 05 — Evento 3: en el corredor, por el lado opuesto (PENDIENTE-05)

**Título:** SdS TP5 G10 — Elusión 1 contra 1: evento 3, elusión por el lado opuesto

**Descripción:** Evento 3: los dos ya caminan por el corredor y la capa elude
correctamente (pasan a 0,57 m contra 0,60 m medidos) pero por el lado
contrario al que usaron las personas.

### 06 — Apoyo: la capa de elusión cabeza a cabeza (PENDIENTE-06)

**Título:** SdS TP5 G10 — La capa de elusión en acción: cruce de frente con tres márgenes

**Descripción:** Cruce sintético de dos agentes a 1 m/s, 8 m aparte y corridos
4 cm, con tres márgenes de espacio personal p2 a la vez (un carril por valor,
p1 = 2,5 s). Se dibuja lo que la capa calcula en cada instante: las posiciones
predichas al instante de mínima aproximación (discos punteados), la
separación predicha d* (trazo entre ellos) y el target temporal (cruz).

### 07 — Apoyo: qué hace p2 (PENDIENTE-07)

**Título:** SdS TP5 G10 — Qué hace p2: el evento 10 con el margen recorriendo su rango

**Descripción:** El evento 10 simulado con p2 de 0 a 0,6 m (p1 = 3,85 s) y, al
lado, el corte de <E(2)> del ítem b con el punto que marca dónde está. p2 fija
por dónde se pasa.

### 08 — Apoyo: qué hace p1 (PENDIENTE-08)

**Título:** SdS TP5 G10 — Qué hace p1: el evento 10 con la anticipación recorriendo su rango

**Descripción:** El evento 10 simulado con p1 de 0 a 4 s (p2 = 0,05 m) y, al
lado, el corte de <E(2)>. p1 decide si llegan a correrse; desde ~1,2 s ya no
cambia nada.
