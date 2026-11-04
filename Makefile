# TP5 -- todo el flujo desde la raiz del repositorio.
#
#   make build          compila el motor (engine/build/elusion)
#   make eventos        lee los datos de la catedra y escribe el resumen de los M eventos
#   make eventos-figuras  las trayectorias medidas de los 19 eventos y d(t) de cada uno
#   make convergencia   eleccion del paso de integracion (barrido de subdivisiones de dt_exp)
#   make convergencia-figuras  apartamiento de <E> contra dt
#   make barrido        items b, c y d: la grilla gruesa y la fina de (p1, p2)
#   make corridas       las corridas con cuadros: los dos optimos y la capa apagada
#   make poblacional-figuras   item b: superficie <E>(p1,p2) y cortes, por metrica
#   make individual-figuras    item c: optimos individuales y error por evento
#   make residuo-figuras       de donde viene el error que queda: ritmo/forma y lado
#   make validacion-figuras    item d: validacion cruzada
#   make trayectorias-figuras  item a: trayectorias, observable primario y d(t) de los eventos elegidos
#   make check          validacion de las corridas (metricas recalculadas, contactos)
#   make animations     videos de los eventos elegidos y el cuadro fijo de cada uno
#   make youtube        copia los videos con nombres legibles en youtube/
#   make gifs           los videos como GIF en gif/ (para embeber en la presentacion en vivo)
#   make figuras-diapositivas  todas las figuras con tipografia de presentacion
#   make slides-images  las imagenes de la presentacion numeradas por diapositiva
#   make slides-images-tikz    solo los esquemas TikZ de las diapositivas, renderizados a PNG
#   make documentos     report/presentacion.tex -> report/build/presentacion.pdf
#   make entrega        SdS_TP5_2026Q2G10S2_Codigo.zip y ..._Presentación.pdf
#   make todo           eventos + convergencia + barrido + corridas; make all es su alias
#   make figuras        todas las figuras de analisis (estilo informe)
#   make clean-figures  borra data/figures y data/figuras_diapositivas
#
# Las variables se pueden pisar: make barrido P1_FINO=0:4:41 P2_FINO=0:0.6:31

PY       ?= python3
ELUSION  := engine/build/elusion

# --- datos de la catedra ---------------------------------------------------
DATOS    ?= experimental/elusion_1_contra_1.txt
EVENTOS  ?= experimental/eventos.txt
# Recorte de la ventana de cada evento: se simula la parte en la que los DOS
# peatones ya caminan (rapidez medida >= ARRANQUE). Al principio de varias
# pruebas uno de los dos todavia esta haciendo la fila, parado, y con el
# peaton quieto adentro de la ventana la rapidez media -- que es el modulo de
# la velocidad deseada -- baja muy por debajo de la rapidez con la que camina.
# Con 0,3 m/s se pierde el 9 % de los instantes y las 19 distancias minimas
# siguen adentro de la ventana: el cruce nunca se recorta.
ARRANQUE ?= 0.3

# --- integracion -----------------------------------------------------------
# dt = dt_exp / SUBDIV, con SUBDIV entero: asi cada instante experimental cae
# exactamente en un paso de la simulacion y las dos trayectorias se comparan
# sin interpolar. SUBDIV sale de make convergencia.
SUBDIV   ?= 64
SUBDIVS  ?= 1,2,4,8,16,32,64,128,256,512
TOLERANCIA ?= 1e-4

# --- grilla de parametros --------------------------------------------------
# Formato "desde:hasta:cantidad". La gruesa explora el plano entero y la fina
# es la que se usa para calibrar (items b, c y d).
#
# p1 = tiempo de anticipacion. El techo son 4 s: la mediana del tiempo al
# cruce en el instante inicial de los eventos es 4,3 s, asi que con p1 mayor
# el conflicto ya se detecta desde el primer instante y nada cambia.
# p2 = margen de espacio personal. El techo de la gruesa es 1 m (dos veces la
# distancia de contacto) y el de la fina, 0,6 m: mas alla <E> sube monotono.
P1_GRUESO ?= 0:4:17
P2_GRUESO ?= 0:1:21
P1_FINO   ?= 0:4:81
P2_FINO   ?= 0:0.6:61

# --- optimos (salen de make poblacional-figuras) ---------------------------
P1_M1    ?= 2.5
P2_M1    ?= 0.07
P1_M2    ?= 3.85
P2_M2    ?= 0.05

# --- eventos con animacion y figuras propias -------------------------------
# 10: el que mas gana con la capa; 5: uno tipico; 14: el peor, donde el error
# de ritmo domina; 19: donde el modelo elude por el lado opuesto.
EVENTOS_FIG ?= 10 5 14 19
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

COMUN    := --datos $(DATOS) --eventos $(EVENTOS) --arranque $(ARRANQUE)

.PHONY: all todo build eventos eventos-figuras convergencia convergencia-figuras \
        barrido corridas poblacional-figuras individual-figuras residuo-figuras \
        validacion-figuras trayectorias-figuras check animations youtube gifs \
        figuras figuras-diapositivas slides-images slides-images-tikz documentos \
        entrega clean-figures

all: todo

todo: eventos convergencia barrido corridas

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
	$(PY) visualization/events.py
	$(PY) visualization/events.py --figures $(SLIDES) --estilo diapositiva

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

# Item a: por cada evento elegido, las trayectorias medidas y simuladas
# superpuestas (con la corrida sin capa de fondo), el observable primario
# contra el tiempo y la distancia entre los dos peatones.
trayectorias-figuras:
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
         residuo-figuras validacion-figuras trayectorias-figuras

figuras-diapositivas: figuras

# --------------------------------------------------------------------------
# Animaciones
# --------------------------------------------------------------------------

# Un cuadro por instante experimental: a 15 cuadros por segundo (1/dt_exp) el
# video corre en tiempo real. De cada evento sale el video y el cuadro fijo
# que va en el PDF, con el mismo lienzo y la misma tipografia.
animations:
	@for m in $(EVENTOS_FIG); do \
	  $(PY) visualization/animate.py --run $(RUNS)/optimo-metrica1/m$$m --fps $(FPS) \
	      --figures $(SLIDES) --estilo diapositiva ; \
	  $(PY) visualization/animate.py --run $(RUNS)/optimo-metrica1/m$$m \
	      --cruce --figures $(SLIDES) --estilo diapositiva ; \
	done
	$(PY) visualization/animate.py --run $(RUNS)/sin-capa/m10 --fps $(FPS) \
	    --name evento10-sin-capa --figures $(SLIDES) --estilo diapositiva
	$(PY) visualization/animate.py --run $(RUNS)/sin-capa/m10 --cruce \
	    --name evento10-sin-capa --figures $(SLIDES) --estilo diapositiva

youtube:
	mkdir -p youtube
	cp "$(SLIDES)/animaciones/evento10.mp4" "youtube/01 - SdS TP5 G10 - Evento 10 con capa de elusion.mp4"
	cp "$(SLIDES)/animaciones/evento10-sin-capa.mp4" "youtube/02 - SdS TP5 G10 - Evento 10 sin capa de elusion.mp4"
	cp "$(SLIDES)/animaciones/evento05.mp4" "youtube/03 - SdS TP5 G10 - Evento 5.mp4"
	cp "$(SLIDES)/animaciones/evento14.mp4" "youtube/04 - SdS TP5 G10 - Evento 14 error de ritmo.mp4"
	cp "$(SLIDES)/animaciones/evento19.mp4" "youtube/05 - SdS TP5 G10 - Evento 19 lado opuesto.mp4"

gifs:
	mkdir -p gif
	@for f in youtube/*.mp4; do \
	  name=$$(basename "$$f" .mp4); \
	  ffmpeg -loglevel error -y -i "$$f" -vf "fps=12,scale=900:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" "gif/$$name.gif"; \
	done

# --------------------------------------------------------------------------
# Presentacion
# --------------------------------------------------------------------------

# Las imagenes de la presentacion, numeradas por la diapositiva en la que van.
# Son las mismas de data/figuras_diapositivas (el analisis con tipografia de
# presentacion) mas los esquemas TikZ renderizados sueltos: en slides-images/
# esta TODA imagen que aparece en la charla, que es la carpeta con la que se
# arma la presentacion a mano en Google Slides.
SL := $(SLIDES)
slides-images:
	rm -rf $(FIGS) && mkdir -p $(FIGS)
	cp $(SL)/0_datos_experimentales/eventos_trayectorias_diapositiva.png      $(FIGS)/slide-03-eventos-trayectorias.png
	cp $(SL)/0_datos_experimentales/eventos_distancia_vs_t_diapositiva.png    $(FIGS)/slide-12-eventos-distancia-vs-t.png
	cp $(SL)/a_capa_de_elusion/convergencia_dt_diapositiva.png                $(FIGS)/slide-13-convergencia-dt.png
	cp $(SL)/animaciones/evento10-sin-capa_cuadro_cruce.png                 $(FIGS)/slide-14-animacion-evento10-sin-capa.png
	cp $(SL)/animaciones/evento10_cuadro_cruce.png                          $(FIGS)/slide-15-animacion-evento10.png
	cp $(SL)/a_capa_de_elusion/evento10_trayectorias_diapositiva.png          $(FIGS)/slide-16-evento10-trayectorias.png
	cp $(SL)/a_capa_de_elusion/evento10_observable_diapositiva.png            $(FIGS)/slide-17-evento10-observable.png
	cp $(SL)/a_capa_de_elusion/evento10_distancia_diapositiva.png             $(FIGS)/slide-18-evento10-distancia.png
	cp $(SL)/b_calibracion_poblacional/superficie_metrica1_diapositiva.png    $(FIGS)/slide-19-superficie-metrica1.png
	cp $(SL)/b_calibracion_poblacional/cortes_metrica1_diapositiva.png        $(FIGS)/slide-20-cortes-metrica1.png
	cp $(SL)/b_calibracion_poblacional/superficie_metrica2_diapositiva.png    $(FIGS)/slide-21-superficie-metrica2.png
	cp $(SL)/b_calibracion_poblacional/cortes_metrica2_diapositiva.png        $(FIGS)/slide-22-cortes-metrica2.png
	cp $(SL)/c_calibracion_individual/optimos_metrica1_diapositiva.png        $(FIGS)/slide-23-optimos-individuales.png
	cp $(SL)/c_calibracion_individual/errores_metrica1_diapositiva.png        $(FIGS)/slide-24-errores-por-evento.png
	cp $(SL)/c_calibracion_individual/residuo_descomposicion_diapositiva.png  $(FIGS)/slide-25-residuo-descomposicion.png
	cp $(SL)/c_calibracion_individual/residuo_lado_diapositiva.png            $(FIGS)/slide-26-residuo-lado.png
	cp $(SL)/animaciones/evento19_cuadro_cruce.png                          $(FIGS)/slide-27-animacion-evento19.png
	cp $(SL)/d_validacion_cruzada/error_metrica1_diapositiva.png              $(FIGS)/slide-28-validacion-error.png
	cp $(SL)/d_validacion_cruzada/parametros_metrica1_diapositiva.png         $(FIGS)/slide-29-validacion-parametros.png
	cp $(SL)/d_validacion_cruzada/tamano_metrica1_diapositiva.png             $(FIGS)/slide-29b-validacion-tamano.png
	$(MAKE) slides-images-tikz
	@echo "$$(ls $(FIGS) | wc -l) imágenes en $(FIGS)/"

# Los fragmentos de las diapositivas escritos en LaTeX (report/figuras/*.tikz,
# los mismos que \input presentacion.tex) renderizados sueltos a PNG con la
# misma tipografia y los mismos colores, numerados por diapositiva.
TIKZ_FIGS := 02-experimento 05-elusion-deteccion 06-elusion-target 08-motor-uml \
             09-bucle 10-parametros-tabla 10-parametros-evento
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
