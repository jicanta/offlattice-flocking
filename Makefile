# TP2 -- todo el flujo desde la raiz del repositorio.
#
#   make build        compila el motor (engine/build/flock)
#   make sweep        barrido de parametros para los items (b) a (f)
#   make clusters     barrido extra de baja densidad para el item (d)
#   make animations   corridas caracteristicas + animaciones del item (a)
#   make bench        tiempos del CIM para el item (g)
#   make figures      todas las figuras a partir de lo simulado
#   make all          sweep + clusters + animations + bench + figures
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

# Casos caracteristicos para las animaciones: modelo rho eta pasos.
ANIM_CASES := vicsek:4:0.5 vicsek:4:4 voter:4:0.5 voter:4:4 vicsek:2:3.5
ANIM_STEPS := 3000
ANIM_SAVE  := 5
SNAPSHOTS  := 0,250,1000,3000

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

.PHONY: all build sweep clusters animations bench summary figures cluster-figures clean-figures

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
	    $(PY) visualization/animate.py --run $$run --frames 600; \
	    $(PY) visualization/animate.py --run $$run --snapshots $(SNAPSHOTS); \
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

figures: summary cluster-figures
	$(PY) visualization/temporal.py
	$(PY) visualization/curves.py
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

clean-figures:
	rm -rf data/figures

# --------------------------------------------------------------------------
# Entrega
# --------------------------------------------------------------------------

# Zip del punto (c) del enunciado: solo el codigo fuente, sin historial, sin
# documentos y sin salida de simulaciones. Queda en el orden de las decenas
# de kb, como pide la consigna.
GRUPO   ?= 10
COMISION?= S2
ZIP     := SdS_TP2_2026Q2G$(GRUPO)$(COMISION)_Codigo.zip

entrega:
	rm -f $(ZIP)
	zip -q -r $(ZIP) Makefile requirements.txt README.md \
	    engine/Makefile engine/include engine/src \
	    visualization/*.py \
	    -x '*/__pycache__/*' '*.pyc'
	@echo "$(ZIP)  ($$(du -h $(ZIP) | cut -f1))"
	@unzip -l $(ZIP) | tail -n +4 | head -n -2 | awk '{print "  " $$4}'
