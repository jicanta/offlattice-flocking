# TP2 -- todo el flujo desde la raiz del repositorio.
#
#   make build        compila el motor (engine/build/flock)
#   make sweep        barrido de parametros para los items (b) a (f)
#   make clusters     barrido extra de baja densidad para el item (d)
#   make animations   corridas caracteristicas + animaciones del item (a)
#   make bench        tiempos del CIM para el item (g)
#   make figures      todas las figuras del informe
#   make figuras-diapositivas   las mismas, con tipografia de presentacion
#   make all          sweep + clusters + animations + bench + figures
#   make ayudamemoria el guion del presentador (no se entrega)
#   make entregables  los tres archivos del campus, con los nombres del enunciado
#
# Las variables de abajo se pueden pisar: make sweep SEEDS=30 ETAS=0:5:0.5

PY      ?= python3
FLOCK   := engine/build/flock
SEEDS   ?= 20
ETAS    ?= 0:5:0.25
RHOS    ?= 2,4,8
STEPS   ?= 5000
SWEEP   := data/sweep
CLUSTERS:= data/sweep_clusters
RUNS    := data/runs
BENCH   := data/bench
SLIDES  := data/figuras_diapositivas

# Casos caracteristicos para las animaciones: modelo rho eta pasos.
ANIM_CASES := vicsek:4:0.5 vicsek:4:4 voter:4:0.5 voter:4:4 vicsek:2:3.5
ANIM_STEPS := 3000
ANIM_SAVE  := 5
SNAPSHOTS  := 0,250,1000,3000

# Animaciones del item (d). El observable de ese item es S, asi que los dos
# casos tienen que diferir en conectividad y no en alineacion: a rho = 1/pi el
# ruido bajo coalesce hasta S = 1 y el alto deja grupitos de dos o tres
# particulas. A baja densidad los encuentros son raros y el transitorio de
# agregacion es un orden de magnitud mas largo, de ahi los pasos extra.
CLUSTER_ANIM_CASES := vicsek:0.31831:0.5 vicsek:0.31831:5
CLUSTER_ANIM_STEPS := 20000
CLUSTER_ANIM_SAVE  := 25
CLUSTER_SNAPSHOTS  := 0,2000,8000,20000

# Densidades del estudio extendido de clusters: rho = 1/(k*pi) da <k> = 1/k
# vecinos en promedio, por debajo del umbral de percolacion. Los valores van
# con seis cifras, que es la precision con la que el motor los escribe en
# index.txt; asi el analisis los reencuentra exactamente.
CRHOS   ?= 0.31831,0.159155,0.106103
CRHO_ETAS := 0.5 2 4
# A baja densidad los encuentros entre particulas son mucho mas raros y el
# transitorio de coalescencia se alarga: con 5000 pasos cuatro casos todavia
# derivan y con 20000 no queda ninguno.
CSTEPS  ?= 20000

.PHONY: all build sweep clusters animations bench summary figures cluster-figures \
        mixed-figures report-figures figuras-diapositivas clean-figures \
        entrega documentos ayudamemoria entregables

all: sweep clusters animations bench figures

build:
	$(MAKE) -C engine

# --------------------------------------------------------------------------
# Simulaciones
# --------------------------------------------------------------------------

sweep: build
	cd engine && ./build/flock sweep --models vicsek,voter --rhos $(RHOS) \
	    --etas $(ETAS) --seeds $(SEEDS) --seed 1 --steps $(STEPS) --dir ../$(SWEEP)

# El enunciado fija rho = 2, 4, 8 para todo el trabajo; solo el estudio de
# clusters (item d, y el (e) que se apoya en el) se extiende a estas tres
# densidades bajas, que son las unicas en las que S deja de valer ~1.
clusters: build
	cd engine && ./build/flock sweep --models vicsek,voter --rhos $(CRHOS) \
	    --etas $(ETAS) --seeds $(SEEDS) --seed 1 --steps $(CSTEPS) --dir ../$(CLUSTERS)

animations: build
	@for spec in $(ANIM_CASES); do \
	    model=$${spec%%:*}; rest=$${spec#*:}; rho=$${rest%%:*}; eta=$${rest#*:}; \
	    run=$(RUNS)/$${model}_rho$${rho}_eta$${eta}; \
	    echo "== $$run"; \
	    (cd engine && ./build/flock simulate --model $$model --rho $$rho --eta $$eta \
	        --steps $(ANIM_STEPS) --save-every $(ANIM_SAVE) --seed 1 --dir ../$$run) > /dev/null; \
	    (cd engine && ./build/flock analyse --dir ../$$run) > /dev/null; \
	    $(PY) visualization/animate.py --run $$run --frames 600; \
	    $(PY) visualization/animate.py --run $$run --snapshots $(SNAPSHOTS); \
	done
	@for spec in $(CLUSTER_ANIM_CASES); do \
	    model=$${spec%%:*}; rest=$${spec#*:}; rho=$${rest%%:*}; eta=$${rest#*:}; \
	    run=$(RUNS)/$${model}_rho1pi_eta$${eta}; \
	    echo "== $$run"; \
	    (cd engine && ./build/flock simulate --model $$model --rho $$rho --eta $$eta \
	        --steps $(CLUSTER_ANIM_STEPS) --save-every $(CLUSTER_ANIM_SAVE) --seed 1 \
	        --dir ../$$run) > /dev/null; \
	    (cd engine && ./build/flock analyse --dir ../$$run) > /dev/null; \
	    $(PY) visualization/animate.py --run $$run --frames 600 \
	        --name $${model}_rho1pi_eta$${eta}.mp4; \
	    $(PY) visualization/animate.py --run $$run --snapshots $(CLUSTER_SNAPSHOTS) \
	        --name cuadros_$${model}_rho1pi_eta$${eta}_t$$(echo $(CLUSTER_SNAPSHOTS) | tr , -).png; \
	done

# Misma caja que el TP1 (L = 20, M = 13) y mismos N, para que los tiempos sean
# comparables. Correr con la maquina descargada.
bench: build
	mkdir -p $(BENCH)
	cd engine && ./build/flock bench --l 20 --ms 13 \
	    --ns 10,113,217,320,424,528,631,735,839,942,1046,1150 \
	    --steps 200 --repeats 5 --eta 6.283185307 --out ../$(BENCH)/bench_l20.txt

# --------------------------------------------------------------------------
# Analisis y figuras
# --------------------------------------------------------------------------

summary:
	$(PY) visualization/summarise.py

figures: summary cluster-figures mixed-figures report-figures
	$(PY) visualization/temporal.py
	$(PY) visualization/curves.py --pares
	-$(PY) visualization/bench.py --log

# Solo los items (d) y (e): las densidades bajas no entran en las curvas de
# polarizacion contra ruido del item (c).
cluster-figures:
	$(PY) visualization/summarise.py --sweep $(CLUSTERS)
	$(PY) visualization/curves.py --sweep $(CLUSTERS) --items d,e,f
	@for eta in $(CRHO_ETAS); do \
	    $(PY) visualization/temporal.py --sweep $(CLUSTERS) --model vicsek \
	        --eta $$eta --rhos $(CRHOS) --item d; \
	    $(PY) visualization/temporal.py --sweep $(CLUSTERS) --model voter \
	        --eta $$eta --rhos $(CRHOS) --item f; \
	done

# Items (d) y (e) del enunciado: una sola figura por modelo con densidades de
# los dos barridos. Sin mezclarlas no se ve nada, porque rho = 2, 4, 8 estan
# saturadas en S = 1 y las de 1/(k*pi) recorren todo el rango; juntas, y con el
# eje en [0, 1], la comparacion es directa. El orden es el de la leyenda.
MIXED_RHOS ?= 8,2,0.31831,0.106103
# S(t) de la diapositiva del item (d): las tres densidades de la consigna y las
# dos bajas del barrido extendido, superpuestas a un mismo ruido.
TEMPORAL_RHOS ?= 8,4,2,0.31831,0.106103

mixed-figures:
	$(PY) visualization/curves.py --sweeps $(SWEEP),$(CLUSTERS) \
	    --rhos $(MIXED_RHOS) --items d,e,f

# --------------------------------------------------------------------------
# Figuras que solo usan los documentos
# --------------------------------------------------------------------------

# Ruidos de la figura de evolucion temporal del informe: ordenado, transicion
# y desorden, una realizacion por curva. En las diapositivas van solo las dos
# corridas de las animaciones, ruido bajo y alto, tambien una realizacion cada
# una.
TRIO      ?= 0.5,2,5
PAR       ?= 0.5,4
TRIO_SEED ?= 1

# Cuadro suelto de cada corrida animada: caso:instante. Es lo que va impreso en
# la diapositiva, con el link a la animacion debajo.
FRAMES := vicsek_rho4_eta0.5:3000 vicsek_rho4_eta4:3000 \
          voter_rho4_eta0.5:3000 voter_rho4_eta4:3000 \
          vicsek_rho1pi_eta0.5:20000 vicsek_rho1pi_eta5:20000

# El informe necesita los dos paneles (va y S) lado a lado en vez de apilados:
# asi cada evolucion temporal ocupa la mitad de alto de pagina.
report-figures:
	$(PY) visualization/temporal.py --model vicsek --rho 4 --eta 2 --item b --paneles lado
	$(PY) visualization/temporal.py --model vicsek --rho 4 --etas $(TRIO) \
	    --seed $(TRIO_SEED) --item b --paneles lado
	$(PY) visualization/temporal.py --model voter --rho 4 --etas $(TRIO) \
	    --seed $(TRIO_SEED) --item f --paneles lado
	$(PY) visualization/temporal.py --sweeps $(SWEEP),$(CLUSTERS) --model vicsek --eta 2 \
	    --rhos $(TEMPORAL_RHOS) --item d --paneles lado
	@for spec in $(FRAMES); do \
	    $(PY) visualization/animate.py --run $(RUNS)/$${spec%%:*} \
	        --snapshots $${spec#*:} --columns 1 \
	        --name cuadro_$${spec%%:*}_t$${spec#*:}.png; \
	done

# La guia de presentaciones pide que las letras dentro de la figura se lean del
# tamano del texto de la diapositiva (al menos 20 pt). Con la figura del informe
# reducida para entrar en un slide eso no se cumple, asi que se genera un juego
# aparte con tipografia mas grande y los paneles lado a lado, en 16:9.
#
# Las comparaciones entre reglas van en una sola figura (item f): va contra
# eta a rho = 4, y S contra eta y va contra S a rho = 1/pi, que es donde S
# recorre todo su rango.

figuras-diapositivas:
	$(PY) visualization/curves.py --items c --figures $(SLIDES) --estilo diapositiva
	$(PY) visualization/curves.py --items c,f --pares --rhos 4 --figures $(SLIDES) \
	    --estilo diapositiva
	$(PY) visualization/curves.py --sweeps $(SWEEP),$(CLUSTERS) --rhos 0.31831 \
	    --items d,e,f --pares --figures $(SLIDES) --estilo diapositiva
	-$(PY) visualization/bench.py --log --figures $(SLIDES) --estilo diapositiva
	$(PY) visualization/temporal.py --model vicsek --rho 4 --etas $(PAR) \
	    --seed $(TRIO_SEED) --item b --figures $(SLIDES) --estilo diapositiva
	$(PY) visualization/temporal.py --model voter --rho 4 --etas $(PAR) \
	    --seed $(TRIO_SEED) --item f --figures $(SLIDES) --estilo diapositiva
	$(PY) visualization/temporal.py --sweeps $(SWEEP),$(CLUSTERS) --model vicsek --eta 2 \
	    --rhos $(TEMPORAL_RHOS) --item d --figures $(SLIDES) --estilo diapositiva
	@for spec in $(FRAMES); do \
	    $(PY) visualization/animate.py --run $(RUNS)/$${spec%%:*} \
	        --snapshots $${spec#*:} --columns 1 \
	        --name cuadro_$${spec%%:*}_t$${spec#*:}.png \
	        --figures $(SLIDES) --estilo diapositiva; \
	done

clean-figures:
	rm -rf data/figures $(SLIDES)

# --------------------------------------------------------------------------
# Entrega
# --------------------------------------------------------------------------

# Zip del punto (c) del enunciado: solo el codigo fuente, sin historial, sin
# documentos y sin salida de simulaciones. Queda en el orden de las decenas
# de kb, como pide la consigna.
GRUPO   ?= 10
COMISION?= S2
ENTREGA := SdS_TP2_2026Q2G$(GRUPO)$(COMISION)
ZIP     := $(ENTREGA)_Codigo.zip
INFORME := $(ENTREGA)_Informe.pdf
PRESENT := $(ENTREGA)_Presentación.pdf

# Compilador de LaTeX. tectonic baja solo los paquetes que falten; con otro
# motor alcanza con pisar la variable (TEX y LATEX son variables predefinidas de
# make, por eso el nombre): make documentos TEXC="latexmk -pdf -outdir"
TEXC    ?= tectonic -X compile
DOCS    := report/build

entrega:
	rm -f $(ZIP)
	zip -q -r $(ZIP) Makefile requirements.txt README.md \
	    engine/Makefile engine/include engine/src \
	    visualization/*.py \
	    -x '*/__pycache__/*' '*.pyc'
	@echo "$(ZIP)  ($$(du -h $(ZIP) | cut -f1))"
	@unzip -l $(ZIP) | tail -n +4 | head -n -2 | awk '{print "  " $$4}'

documentos:
	$(TEXC) report/informe.tex --outdir $(DOCS)
	$(TEXC) report/presentacion.tex --outdir $(DOCS)

# Guion de apoyo para quien expone. Queda fuera de 'entregables': la consigna
# pide presentacion, codigo e informe, y nada mas. Reune el texto que se saco de
# las diapositivas para cumplir con GuiaPresentaciones.pdf (1.6), que pide poco
# texto y sin parrafos.
ayudamemoria:
	$(TEXC) report/ayudamemoria.tex --outdir $(DOCS)
	@echo "  $(DOCS)/ayudamemoria.pdf"

# Los tres archivos que se suben al campus, con los nombres que pide el
# enunciado: informe y presentacion en pdf, y el codigo fuente en zip.
entregables: entrega documentos
	cp $(DOCS)/informe.pdf "$(INFORME)"
	cp $(DOCS)/presentacion.pdf "$(PRESENT)"
	@ls -l $(ZIP) "$(INFORME)" "$(PRESENT)" | awk '{print "  " $$5 "\t" $$9}'
