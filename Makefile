# TP2 -- todo el flujo desde la raiz del repositorio.
#
#   make build        compila el motor (engine/build/flock)
#   make sweep        barrido de parametros para los items (b) a (f)
#   make animations   corridas caracteristicas + animaciones del item (a)
#   make bench        tiempos del CIM para el item (g)
#   make figures      todas las figuras a partir de lo simulado
#   make all          sweep + animations + bench + figures
#
# Las variables de abajo se pueden pisar: make sweep SEEDS=30 ETAS=0:5:0.5

PY      ?= python3
FLOCK   := engine/build/flock
SEEDS   ?= 20
ETAS    ?= 0:5:0.25
RHOS    ?= 2,4,8
STEPS   ?= 5000
SWEEP   := data/sweep
RUNS    := data/runs
BENCH   := data/bench

# Casos caracteristicos para las animaciones: modelo rho eta pasos.
ANIM_CASES := vicsek:4:0.5 vicsek:4:4 voter:4:0.5 voter:4:4 vicsek:2:3.5
ANIM_STEPS := 3000
ANIM_SAVE  := 5
SNAPSHOTS  := 0,250,1000,3000

.PHONY: all build sweep animations bench summary figures clean-figures

all: sweep animations bench figures

build:
	$(MAKE) -C engine

# --------------------------------------------------------------------------
# Simulaciones
# --------------------------------------------------------------------------

sweep: build
	cd engine && ./build/flock sweep --models vicsek,voter --rhos $(RHOS) \
	    --etas $(ETAS) --seeds $(SEEDS) --seed 1 --steps $(STEPS) --dir ../$(SWEEP)

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

figures: summary
	$(PY) visualization/temporal.py
	$(PY) visualization/curves.py
	-$(PY) visualization/bench.py --log

clean-figures:
	rm -rf data/figures
