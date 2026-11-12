# TP5 -- todo el flujo desde la raiz del repositorio.
#
#   make build          compila el motor (engine/build/elusion)
#   make eventos        lee los datos de la catedra y escribe el resumen de los M eventos
#   make eventos-figuras  las trayectorias medidas de los 19 eventos y d(t) de cada uno
#   make convergencia   eleccion del paso de integracion (barrido de subdivisiones de dt_exp)
#   make convergencia-figuras  apartamiento de <E> contra dt
#   make ventana        cuanto cambia la calibracion al mover el tramo de x del recorte
#   make barrido        items b, c y d: la grilla gruesa y la fina de (p1, p2)
#   make corridas       las corridas con cuadros: los dos optimos y la capa apagada
#   make pares          item c opcional: los 4 parametros por evento (2 por peaton)
#   make asimetria      EXTRA: t_a fijo y barrido del par (d_s, alfa)
#   make poblacional-figuras   item b: superficie <E>(p1,p2) y cortes, por metrica
#   make individual-figuras    item c: histogramas de los optimos individuales y error por evento
#   make pares-figuras         item c opcional: histogramas de los optimos por peaton
#   make asimetria-figuras     EXTRA: <E>(alfa), histograma de alfa por evento, alfa medido
#   make residuo-figuras       de donde viene el error que queda: ritmo/forma y lado
#   make validacion-figuras    item d: validacion cruzada
#   make trayectorias-figuras  item a: los 4 eventos representativos, observable primario y d(t)
#   make check          validacion de las corridas (metricas recalculadas, contactos)
#   make animations     videos de los eventos elegidos y el cuadro fijo de cada uno
#   make apoyo          animaciones de apoyo: la capa paso a paso, cabeza a cabeza y que hace cada parametro
#   make youtube        copia los videos con nombres legibles en youtube/
#   make gifs           los videos como GIF en gif/ (para embeber en la presentacion en vivo)
#   make figuras-diapositivas  todas las figuras con tipografia de presentacion
#   make slides-images  las imagenes de la presentacion numeradas por diapositiva
#   make slides-images-tikz    solo los esquemas TikZ de las diapositivas, renderizados a PNG
#   make documentos     report/presentacion.tex -> report/build/presentacion.pdf
#   make entrega        SdS_TP5_2026Q2G10S2_Codigo.zip y ..._Presentación.pdf
#   make todo           eventos + convergencia + barrido + alternativas + corridas + asimetria
#                       (make pares va aparte: tarda media hora)
#   make figuras        todas las figuras de analisis (estilo informe)
#   make clean-figures  borra data/figures y data/figuras_diapositivas
#
# Las variables se pueden pisar: make barrido P1_FINO=0:4:41 P2_FINO=0:0.6:31

PY       ?= python3
ELUSION  := engine/build/elusion

# --- datos de la catedra ---------------------------------------------------
DATOS    ?= experimental/elusion_1_contra_1.txt
EVENTOS  ?= experimental/eventos.txt
# Recorte de la ventana de cada evento: el tramo del corredor en que los DOS
# peatones caminan uno hacia el otro, X_MIN <= x <= X_MAX, el mismo para los 19
# eventos. Las cabeceras de las dos filas estan en x = 0,6 m y x = 8,1 m (se
# ven en la figura de las 38 trayectorias superpuestas): el tramo deja 0,4 m
# de cada lado. make ventana mide cuanto cambia la calibracion al moverlo. Ver
# README, "El recorte de la ventana".
X_MIN    ?= 1.0
X_MAX    ?= 7.7

# --- integracion -----------------------------------------------------------
# dt = dt_exp / SUBDIV, con SUBDIV entero: asi cada instante experimental cae
# exactamente en un paso de la simulacion y las dos trayectorias se comparan
# sin interpolar. SUBDIV sale de make convergencia.
SUBDIV   ?= 64
SUBDIVS  ?= 1,2,4,8,16,32,64,128,256,512
# Tolerancia sobre el apartamiento relativo de <E> respecto del paso mas fino:
# 0,2 %, cincuenta veces menos que el error estandar de <E> entre eventos (11 %).
TOLERANCIA ?= 2e-3

# --- grilla de parametros --------------------------------------------------
# Formato "desde:hasta:cantidad". La gruesa explora el plano entero y la fina
# es la que se usa para calibrar (items b, c y d).
#
# p1 = tiempo de anticipacion. El techo son 4 s: un barrido aparte hasta 8 s
# (P1_LARGO, en la p2 de cada optimo) muestra que mas alla de 4 s <E> no se
# mueve mas que su error pareado (metrica 2: 0,000 +- 0,007 m2 entre 4 y 8 s).
# p2 = margen de espacio personal. El techo de la gruesa es 1 m (dos veces la
# distancia de contacto) y el de la fina, 0,6 m: mas alla <E> sube monotono.
P1_GRUESO ?= 0:4:17
P2_GRUESO ?= 0:1:21
P1_FINO   ?= 0:4:81
P2_FINO   ?= 0:0.6:61
P1_LARGO  ?= 0:8:33
P2_LARGO  ?= 0.13,0.14

# --- optimos (salen de make poblacional-figuras) ---------------------------
P1_M1    ?= 2.15
P2_M1    ?= 0.13
P1_M2    ?= 1.5
P2_M2    ?= 0.14

# --- eventos con animacion y figuras propias -------------------------------
# Cuatro eventos representativos, cada uno por un motivo: 10, el que mas gana
# con la capa (y el principal: de el son la animacion sin capa, e(t) y d(t));
# 5, el cruce medido mas ajustado; 14, el mas holgado; 17, el unico en el que
# el modelo elude por el lado opuesto.
EVENTO      ?= 10
EVENTOS_FIG ?= 10 5 14 17
# El cuadro fijo de cada animacion se toma en el instante de minima
# aproximacion simulada, que es donde se ve la elusion.
FPS         ?= 15

DATA     := data
BARRIDO  := $(DATA)/barrido
RUNS     := $(DATA)/runs
FIGURES  := $(DATA)/figures
SLIDES   := $(DATA)/figuras_diapositivas
FIGS     := slides-images
TEXC     ?= tectonic -X compile
DOCS     := report/build
GRUPO    ?= 10
COMISION ?= S2
ENTREGA  := SdS_TP5_2026Q2G$(GRUPO)$(COMISION)
ZIP      := $(ENTREGA)_Codigo.zip

COMUN    := --datos $(DATOS) --eventos $(EVENTOS) --xmin $(X_MIN) --xmax $(X_MAX)

# --- EXTRA: reparto de la elusion (make asimetria) -------------------------
# alfa reparte la separacion que falta entre los dos peatones del par: el de la
# izquierda se lleva alfa y el de la derecha 1 - alfa, y con 0,5 la capa es la
# simetrica de dos parametros que se calibra en los items b, c y d. Se deja
# t_a en el optimo de cada metrica y se barre el par (d_s, alfa).
P2_ASIM  ?= 0:0.6:61
ALFAS    ?= 0:1:41
ASIM     := $(DATA)/asimetria

.PHONY: all todo build eventos eventos-figuras convergencia convergencia-figuras \
        ventana asimetria asimetria-figuras pares pares-figuras barrido corridas poblacional-figuras individual-figuras residuo-figuras \
        validacion-figuras trayectorias-figuras alternativas alternativas-figuras \
        check animations apoyo youtube gifs \
        figuras figuras-diapositivas slides-images slides-images-tikz documentos \
        entrega clean-figures

all: todo

todo: eventos convergencia barrido alternativas corridas asimetria

build:
	$(MAKE) -C engine

# --------------------------------------------------------------------------
# Datos experimentales
# --------------------------------------------------------------------------

# Verifica la lectura de los datos de la catedra contra el LEEME y escribe el
# resumen de los M eventos: ventana comun, muestras de cada peaton y las
# condiciones que el enunciado fija a partir de su trayectoria.
eventos: build
	$(ELUSION) events $(COMUN) --dir $(DATA)/experimental

eventos-figuras:
	$(PY) visualization/events.py --xmin $(X_MIN) --xmax $(X_MAX)
	$(PY) visualization/events.py --xmin $(X_MIN) --xmax $(X_MAX) \
	    --figures $(SLIDES) --estilo diapositiva

# --------------------------------------------------------------------------
# Paso de integracion
# --------------------------------------------------------------------------

convergencia: build
	$(ELUSION) convergence $(COMUN) --p1 $(P1_M1) --p2 $(P2_M1) \
	    --subdivisiones $(SUBDIVS) --dir $(DATA)/convergencia

convergencia-figuras:
	$(PY) visualization/convergence.py --tolerancia $(TOLERANCIA) --elegido $(SUBDIV)
	$(PY) visualization/convergence.py --tolerancia $(TOLERANCIA) --elegido $(SUBDIV) \
	    --figures $(SLIDES) --estilo diapositiva

# --------------------------------------------------------------------------
# El recorte de la ventana
# --------------------------------------------------------------------------

# Cuanto depende la calibracion del tramo de x elegido: por cada tramo, el
# resumen de los eventos y un barrido de la grilla. visualization/window.py
# arma la tabla.
TRAMOS ?= 0.8:7.9 1.0:8.0 1.0:7.7 1.25:7.45 1.5:7.2 2.0:6.7
ventana: build
	@for tramo in $(TRAMOS); do \
	    a=$${tramo%:*}; b=$${tramo#*:}; \
	    $(ELUSION) events --datos $(DATOS) --eventos $(EVENTOS) --xmin $$a --xmax $$b \
	        --dir $(DATA)/ventana/x-$$a-$$b >/dev/null; \
	    $(ELUSION) sweep --datos $(DATOS) --eventos $(EVENTOS) --xmin $$a --xmax $$b \
	        --p1 0:4:41 --p2 0:0.6:31 --subdivisiones $(SUBDIV) \
	        --dir $(DATA)/ventana/x-$$a-$$b >/dev/null; \
	done
	$(PY) visualization/window.py

# --------------------------------------------------------------------------
# Reparto de la elusion entre los dos peatones del par
# --------------------------------------------------------------------------

# EXTRA, fuera de lo que pide el enunciado (lo propuso la catedra): t_a fijo en
# el optimo de cada metrica y barrido del par (d_s, alfa). El optimo
# poblacional de alfa dice si hay un lado que cede sistematicamente y el de
# cada evento, cuanto se gana describiendo el reparto par por par.
asimetria: build
	$(ELUSION) asymmetry $(COMUN) --p1 $(P1_M1) --p2 $(P2_ASIM) \
	    --alfas $(ALFAS) --subdivisiones $(SUBDIV) --dir $(ASIM)/metrica1
	$(ELUSION) asymmetry $(COMUN) --p1 $(P1_M2) --p2 $(P2_ASIM) \
	    --alfas $(ALFAS) --subdivisiones $(SUBDIV) --dir $(ASIM)/metrica2

asimetria-figuras:
	$(PY) visualization/asymmetry.py
	$(PY) visualization/asymmetry.py --figures $(SLIDES) --estilo diapositiva

# --------------------------------------------------------------------------
# Item 2 c) OPCIONAL: los parametros por peaton (cuatro por evento)
# --------------------------------------------------------------------------

# "Optimizar parametros por cada peaton (en lugar de 1 juego de parametros por
# cada par de peatones). Notar que el caso opcional requiere hallar 4
# parametros en lugar de solo 2." Como los dos agentes estan acoplados, el
# minimo se busca en la grilla de los cuatro a la vez (G x G por evento), y de
# la MISMA grilla sale el optimo de dos parametros con el que se compara.
#
# La grilla es mas gruesa que la de la calibracion poblacional porque el costo
# va al cuadrado: 17 x 25 = 425 pares por agente son 180.625 combinaciones por
# evento.
P1_PARES ?= 0:4:17
P2_PARES ?= 0:0.6:25
PARES    := $(DATA)/individual

pares: build
	$(ELUSION) pairs $(COMUN) --p1 $(P1_PARES) --p2 $(P2_PARES) \
	    --subdivisiones $(SUBDIV) --dir $(PARES)
	$(ELUSION) sweep $(COMUN) --p1 $(P1_PARES) --p2 $(P2_PARES) \
	    --subdivisiones $(SUBDIV) --dir $(PARES)

pares-figuras:
	$(PY) visualization/pares.py
	$(PY) visualization/pares.py --figures $(SLIDES) --estilo diapositiva

# --------------------------------------------------------------------------
# Barrido de la grilla de parametros (items b, c y d)
# --------------------------------------------------------------------------

# El motor mide las dos metricas en los dos peatones de cada evento para cada
# par de la grilla. Todo lo demas -- el promedio poblacional, los optimos
# individuales y las particiones de la validacion cruzada -- se calcula
# despues sobre ese mismo archivo, sin volver a simular.
barrido: build
	$(ELUSION) sweep $(COMUN) --p1 $(P1_GRUESO) --p2 $(P2_GRUESO) \
	    --subdivisiones $(SUBDIV) --dir $(BARRIDO)/grueso
	$(ELUSION) sweep $(COMUN) --p1 $(P1_FINO) --p2 $(P2_FINO) \
	    --subdivisiones $(SUBDIV) --dir $(BARRIDO)/fino
	$(ELUSION) sweep $(COMUN) --p1 $(P1_LARGO) --p2 $(P2_LARGO) \
	    --subdivisiones $(SUBDIV) --dir $(BARRIDO)/p1largo

# Las alternativas de capa que se probaron contra la predictiva (README, "Las
# alternativas que se probaron"): tres variantes de campo, cada una en su
# grilla. La isotropica en una grilla gruesa alcanza (queda lejos); las otras
# dos en una fina, porque empatan.
alternativas: build
	$(ELUSION) sweep $(COMUN) --capa campo --p1 0:6:31 --p2 0.02:1.5:31 \
	    --subdivisiones $(SUBDIV) --dir $(BARRIDO)/alternativas/campo
	$(ELUSION) sweep $(COMUN) --capa campo-lateral --p1 0.1:3:30 --p2 0.1:5:50 \
	    --subdivisiones $(SUBDIV) --dir $(BARRIDO)/alternativas/campo-lateral-fino
	$(ELUSION) sweep $(COMUN) --capa campo-predictivo --p1 0.05:2:40 --p2 0.005:0.2:40 \
	    --subdivisiones $(SUBDIV) --dir $(BARRIDO)/alternativas/campo-predictivo-fino

alternativas-figuras:
	$(PY) visualization/alternatives.py
	$(PY) visualization/alternatives.py --figures $(SLIDES) --estilo diapositiva

# Las tres corridas con cuadros de los 19 eventos: con el optimo de cada
# metrica y con la capa apagada (p1 = 0), que es el SFM puro y la referencia
# contra la que se mide lo que la capa aporta.
corridas: build
	$(ELUSION) run $(COMUN) --p1 $(P1_M1) --p2 $(P2_M1) --subdivisiones $(SUBDIV) \
	    --dir $(RUNS)/optimo-metrica1
	$(ELUSION) run $(COMUN) --p1 $(P1_M2) --p2 $(P2_M2) --subdivisiones $(SUBDIV) \
	    --dir $(RUNS)/optimo-metrica2
	$(ELUSION) run $(COMUN) --p1 0 --p2 0 --subdivisiones $(SUBDIV) --dir $(RUNS)/sin-capa

poblacional-figuras:
	$(PY) visualization/population.py
	$(PY) visualization/population.py --figures $(SLIDES) --estilo diapositiva

individual-figuras:
	$(PY) visualization/individual.py
	$(PY) visualization/individual.py --figures $(SLIDES) --estilo diapositiva

residuo-figuras:
	$(PY) visualization/residual.py
	$(PY) visualization/residual.py --figures $(SLIDES) --estilo diapositiva

validacion-figuras:
	$(PY) visualization/crossval.py
	$(PY) visualization/crossval.py --figures $(SLIDES) --estilo diapositiva

# Item a: las trayectorias de los cuatro eventos representativos en una sola
# figura y, del evento principal, el observable primario contra el tiempo y la
# distancia entre los dos peatones.
trayectorias-figuras:
	$(PY) visualization/representative.py --eventos $(EVENTOS_FIG)
	$(PY) visualization/representative.py --eventos $(EVENTOS_FIG) \
	    --figures $(SLIDES) --estilo diapositiva
	@for m in $(EVENTOS_FIG); do \
	  $(PY) visualization/trajectory.py --run $(RUNS)/optimo-metrica1/m$$m \
	      --sin-capa $(RUNS)/sin-capa/m$$m ; \
	  $(PY) visualization/trajectory.py --run $(RUNS)/optimo-metrica1/m$$m \
	      --sin-capa $(RUNS)/sin-capa/m$$m --figures $(SLIDES) --estilo diapositiva ; \
	done

check:
	$(PY) visualization/check.py --runs $(RUNS)/optimo-metrica1
	$(PY) visualization/check.py --runs $(RUNS)/sin-capa

figuras: eventos-figuras convergencia-figuras poblacional-figuras individual-figuras \
         pares-figuras residuo-figuras validacion-figuras trayectorias-figuras \
         alternativas-figuras asimetria-figuras

figuras-diapositivas: figuras

# --------------------------------------------------------------------------
# Animaciones
# --------------------------------------------------------------------------

# Un cuadro por instante experimental: a 15 cuadros por segundo (1/dt_exp) el
# video corre en tiempo real. De cada evento sale el video y el cuadro fijo
# que va en el PDF, con el mismo lienzo y la misma tipografia. Y los 19
# eventos a la vez, un panel por evento, que es la verificacion a ojo de que
# la ventana de cada uno es el cruce y no la fila.
animations:
	@for m in $(EVENTOS_FIG); do \
	  $(PY) visualization/animate.py --run $(RUNS)/optimo-metrica1/m$$m --fps $(FPS) \
	      --figures $(SLIDES) --estilo diapositiva ; \
	  $(PY) visualization/animate.py --run $(RUNS)/optimo-metrica1/m$$m \
	      --cruce --figures $(SLIDES) --estilo diapositiva ; \
	done
	$(PY) visualization/animate.py --run $(RUNS)/sin-capa/m$(EVENTO) --fps $(FPS) \
	    --name evento$(EVENTO)-sin-capa --figures $(SLIDES) --estilo diapositiva
	$(PY) visualization/animate.py --run $(RUNS)/sin-capa/m$(EVENTO) --cruce \
	    --name evento$(EVENTO)-sin-capa --figures $(SLIDES) --estilo diapositiva
	$(PY) visualization/mosaico.py --runs $(RUNS)/optimo-metrica1 --modo grilla \
	    --name los19 --figures $(SLIDES) --estilo diapositiva

# Las animaciones de apoyo: la capa explicada paso a paso (el esquema de las
# diapositivas armado de a un elemento), la capa mirada de cerca en un cruce
# sintetico cabeza a cabeza con tres p2 a la vez, y el evento principal con
# cada parametro recorriendo su rango al lado del corte de <E>. Con los
# cuadros fijos que van en el PDF.
apoyo:
	$(PY) visualization/explain.py --cuadros --figures $(SLIDES) --estilo diapositiva
	$(PY) visualization/support.py cabeza-a-cabeza --p1 $(P1_M1) --p2s 0,0.2,0.5 \
	    --figures $(SLIDES) --estilo diapositiva
	$(PY) visualization/support.py cabeza-a-cabeza --p1 $(P1_M1) --p2s 0,0.2,0.5 \
	    --cuadro 2.4 --figures $(SLIDES) --estilo diapositiva
	$(PY) visualization/support.py barrido --parametro p2 --evento $(EVENTO) --cada 1 \
	    --figures $(SLIDES) --estilo diapositiva
	$(PY) visualization/support.py barrido --parametro p2 --evento $(EVENTO) --cada 1 \
	    --cuadros 0,0.14,0.3,0.6 --figures $(SLIDES) --estilo diapositiva
	$(PY) visualization/support.py barrido --parametro p1 --evento $(EVENTO) \
	    --figures $(SLIDES) --estilo diapositiva
	$(PY) visualization/support.py barrido --parametro p1 --evento $(EVENTO) \
	    --cuadros 0.5,1,1.5,4 --figures $(SLIDES) --estilo diapositiva

AN := $(SLIDES)/animaciones
youtube:
	mkdir -p youtube && rm -f youtube/*.mp4
	cp "$(AN)/evento10.mp4" "youtube/01 - SdS TP5 G10 - Evento 10 con capa de elusion.mp4"
	cp "$(AN)/evento10-sin-capa.mp4" "youtube/02 - SdS TP5 G10 - Evento 10 sin capa de elusion.mp4"
	cp "$(AN)/evento05.mp4" "youtube/03 - SdS TP5 G10 - Evento 5 el cruce mas ajustado.mp4"
	cp "$(AN)/evento14.mp4" "youtube/04 - SdS TP5 G10 - Evento 14 el cruce mas holgado.mp4"
	cp "$(AN)/evento17.mp4" "youtube/05 - SdS TP5 G10 - Evento 17 lado opuesto.mp4"
	cp "$(AN)/apoyo_cabeza_a_cabeza.mp4" "youtube/06 - SdS TP5 G10 - Apoyo - La capa de elusion cabeza a cabeza.mp4"
	cp "$(AN)/apoyo_barrido_p2_evento10.mp4" "youtube/07 - SdS TP5 G10 - Apoyo - Que hace p2.mp4"
	cp "$(AN)/apoyo_barrido_p1_evento10.mp4" "youtube/08 - SdS TP5 G10 - Apoyo - Que hace p1.mp4"
	cp "$(AN)/apoyo_capa_paso_a_paso.mp4" "youtube/09 - SdS TP5 G10 - Apoyo - La capa de elusion paso a paso.mp4"
	cp "$(AN)/los19_grilla.mp4" "youtube/10 - SdS TP5 G10 - Los 19 eventos.mp4"

gifs:
	mkdir -p gif && rm -rf gif/*.gif gif/estudio
	@for f in youtube/*.mp4; do \
	  name=$$(basename "$$f" .mp4); \
	  case "$$name" in 10*) ancho=1400;; *) ancho=900;; esac; \
	  ffmpeg -loglevel error -y -i "$$f" -vf "fps=12,scale=$$ancho:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" "gif/$$name.gif"; \
	done

# --------------------------------------------------------------------------
# Presentacion
# --------------------------------------------------------------------------

# Las imagenes de la presentacion, numeradas por la diapositiva en la que van.
# Son las mismas de data/figuras_diapositivas (el analisis con tipografia de
# presentacion) mas los esquemas TikZ renderizados sueltos: en slides-images/
# esta TODA imagen que aparece en la charla, que es la carpeta con la que se
# arma la presentacion a mano en Google Slides. Las del sufijo b son la misma
# figura con la otra metrica, por si hace falta en una pregunta; las "extra"
# son las del reparto de la elusion, que se muestran despues del cierre.
SL := $(SLIDES)
slides-images:
	rm -rf $(FIGS) && mkdir -p $(FIGS)
	cp $(SL)/0_datos_experimentales/eventos_trayectorias_diapositiva.png      $(FIGS)/slide-03-eventos-trayectorias.png
	cp $(SL)/animaciones/apoyo_capa_paso_4.png                                $(FIGS)/slide-06b-deteccion-paso-a-paso.png
	cp $(SL)/animaciones/apoyo_capa_paso_6.png                                $(FIGS)/slide-07b-target-paso-a-paso.png
	cp $(SL)/animaciones/apoyo_cabeza_a_cabeza_t2.4.png                       $(FIGS)/slide-09-capa-en-accion.png
	cp $(SL)/a_capa_de_elusion/alternativas_metrica2_diapositiva.png          $(FIGS)/slide-10-alternativas.png
	cp $(SL)/0_datos_experimentales/eventos_distancia_vs_t_diapositiva.png    $(FIGS)/slide-15-eventos-distancia-vs-t.png
	cp $(SL)/a_capa_de_elusion/convergencia_dt_diapositiva.png                $(FIGS)/slide-16-convergencia-dt.png
	cp $(SL)/animaciones/evento10-sin-capa_cuadro_cruce.png                   $(FIGS)/slide-17-animacion-evento10-sin-capa.png
	cp $(SL)/animaciones/evento10_cuadro_cruce.png                            $(FIGS)/slide-18-animacion-evento10.png
	cp $(SL)/a_capa_de_elusion/trayectorias_representativas_diapositiva.png   $(FIGS)/slide-19-trayectorias-representativas.png
	cp $(SL)/a_capa_de_elusion/evento10_observable_diapositiva.png            $(FIGS)/slide-20-evento10-observable.png
	cp $(SL)/a_capa_de_elusion/evento10_distancia_diapositiva.png             $(FIGS)/slide-21-evento10-distancia.png
	cp $(SL)/animaciones/apoyo_barrido_p2_evento10_resumen.png                $(FIGS)/slide-22-que-hace-p2.png
	cp $(SL)/animaciones/apoyo_barrido_p1_evento10_resumen.png                $(FIGS)/slide-22b-que-hace-p1.png
	cp $(SL)/b_calibracion_poblacional/superficie_metrica1_diapositiva.png    $(FIGS)/slide-23-superficie-metrica1.png
	cp $(SL)/b_calibracion_poblacional/cortes_metrica1_diapositiva.png        $(FIGS)/slide-24-cortes-metrica1.png
	cp $(SL)/b_calibracion_poblacional/techo_p1_diapositiva.png               $(FIGS)/slide-24b-techo-p1.png
	cp $(SL)/b_calibracion_poblacional/superficie_metrica2_diapositiva.png    $(FIGS)/slide-25-superficie-metrica2.png
	cp $(SL)/b_calibracion_poblacional/cortes_metrica2_diapositiva.png        $(FIGS)/slide-26-cortes-metrica2.png
	cp $(SL)/c_calibracion_individual/optimos_metrica1_diapositiva.png        $(FIGS)/slide-27-optimos-individuales.png
	cp $(SL)/c_calibracion_individual/optimos_metrica2_diapositiva.png        $(FIGS)/slide-27b-optimos-individuales-metrica2.png
	cp $(SL)/c_calibracion_individual/errores_metrica1_diapositiva.png        $(FIGS)/slide-28-errores-por-evento.png
	cp $(SL)/c_calibracion_individual/errores_metrica2_diapositiva.png        $(FIGS)/slide-28b-errores-por-evento-metrica2.png
	cp $(SL)/c_calibracion_individual/pares_optimos_metrica1_diapositiva.png  $(FIGS)/slide-29-optimos-por-peaton.png
	cp $(SL)/c_calibracion_individual/pares_optimos_metrica2_diapositiva.png  $(FIGS)/slide-29b-optimos-por-peaton-metrica2.png
	cp $(SL)/c_calibracion_individual/pares_errores_metrica1_diapositiva.png  $(FIGS)/slide-30-errores-por-peaton.png
	cp $(SL)/c_calibracion_individual/pares_errores_metrica2_diapositiva.png  $(FIGS)/slide-30b-errores-por-peaton-metrica2.png
	cp $(SL)/c_calibracion_individual/residuo_descomposicion_diapositiva.png  $(FIGS)/slide-31-residuo-descomposicion.png
	cp $(SL)/c_calibracion_individual/residuo_lado_diapositiva.png            $(FIGS)/slide-32-residuo-lado.png
	cp $(SL)/animaciones/evento17_cuadro_cruce.png                            $(FIGS)/slide-33-animacion-evento17.png
	cp $(SL)/d_validacion_cruzada/error_metrica1_diapositiva.png              $(FIGS)/slide-34-validacion-error.png
	cp $(SL)/d_validacion_cruzada/parametros_metrica1_diapositiva.png         $(FIGS)/slide-35-validacion-parametros.png
	cp $(SL)/d_validacion_cruzada/tamano_metrica1_diapositiva.png             $(FIGS)/slide-35b-validacion-tamano.png
	cp $(SL)/e_extra_reparto/alfa_curva_diapositiva.png                       $(FIGS)/slide-extra-1-alfa-curva.png
	cp $(SL)/e_extra_reparto/alfa_histograma_diapositiva.png                  $(FIGS)/slide-extra-2-alfa-histograma.png
	cp $(SL)/e_extra_reparto/alfa_medido_diapositiva.png                      $(FIGS)/slide-extra-3-alfa-medido.png
	$(MAKE) slides-images-tikz
	@echo "$$(ls $(FIGS) | wc -l) imágenes en $(FIGS)/"

# Los fragmentos de las diapositivas escritos en LaTeX (report/figuras/*.tikz,
# los mismos que \input presentacion.tex) renderizados sueltos a PNG con la
# misma tipografia y los mismos colores, numerados por diapositiva.
TIKZ_FIGS := 02-experimento 05-parametros-evento 06-elusion-deteccion 07-elusion-target \
             11-motor-uml 12-bucle 13-parametros-tabla
slides-images-tikz:
	mkdir -p $(DOCS)/figuras $(FIGS)
	@for f in $(TIKZ_FIGS); do \
	    n=$${f#*-}; \
	    printf '\\def\\figura{%s}\\input{render.tex}\n' "$$n" > report/figuras/_$$n.tex; \
	    (cd report/figuras && $(TEXC) _$$n.tex --outdir ../build/figuras >/dev/null); \
	    pdftoppm -r 600 -png -singlefile $(DOCS)/figuras/_$$n.pdf $(FIGS)/slide-$$f; \
	    rm -f report/figuras/_$$n.tex; \
	done

documentos:
	mkdir -p $(DOCS)
	cd report && $(TEXC) presentacion.tex --outdir build

entrega: documentos
	rm -f $(ZIP)
	cd engine && zip -q -r ../$(ZIP) Makefile include src -x '*/build/*'
	zip -q -j $(ZIP) experimental/eventos.txt visualization/animate.py visualization/common.py
	cp $(DOCS)/presentacion.pdf $(ENTREGA)_Presentación.pdf
	@ls -lh $(ZIP) $(ENTREGA)_Presentación.pdf

clean-figures:
	rm -rf $(FIGURES) $(SLIDES)
