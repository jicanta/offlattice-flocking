"""Items (b), (d) y (f): evolucion temporal de va y de S.

Dos tipos de figura, siempre con dos paneles (va arriba, S abajo):

* Un caso, todas sus realizaciones: las M curvas en gris, el promedio en
  color, la linea vertical en t_eq, y la linea horizontal con su banda que
  son el valor escalar y su desvio, calculados tal como se usan luego en las
  curvas contra eta. Es la figura que explicita como se calcula el escalar.
* Varios casos superpuestos: solo la curva promedio de cada caso, con su t_eq
  y su promedio estacionario. Sirve para comparar ruidos, densidades o
  modelos.

Sin argumentos genera el juego completo de figuras del informe. Con --model,
--rho y --eta genera una figura puntual.

    python3 visualization/temporal.py
    python3 visualization/temporal.py --model voter --rho 4 --eta 0.5
    python3 visualization/temporal.py --model vicsek --rho 4 --etas 0.5,2,4
    python3 visualization/temporal.py --model vicsek --eta 2 --rhos 2,4,8 --item d
"""

from __future__ import annotations

import argparse
from functools import lru_cache

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

import common

GREY = "#9a9a9a"

# Fases distintas del punteado de las verticales: dos casos con el mismo t_eq
# caerian en el mismo pixel y el ultimo dibujado taparia al anterior.
DASH_PHASES = [(phase, (1, 5)) for phase in (0, 2, 4, 1, 3, 5)]

# Que significan la vertical punteada y la horizontal a trazos. En las figuras
# de un solo caso cada trazo ya lleva su etiqueta; en las superpuestas no se
# puede, porque habria una por serie, asi que se explican una sola vez.
CONVENTION = [
    Line2D([], [], color=GREY, linestyle=":", linewidth=1.2,
           label="inicio del estacionario ($t_{eq}$)"),
    Line2D([], [], color=GREY, linestyle="--", linewidth=1.0,
           label="promedio en el estacionario"),
]


class Cases:
    """Carga (y recuerda) las realizaciones de cada caso del barrido."""

    def __init__(self, sweep):
        self.grouped = common.group_runs(common.read_index(sweep))

    @lru_cache(maxsize=None)
    def stack(self, model: str, rho: float, eta: float) -> np.ndarray:
        return common.load_case(common.find_case(self.grouped, model, rho, eta))

    @lru_cache(maxsize=None)
    def row(self, model: str, rho: float, eta: float, seed: int) -> int:
        """Fila de stack() que corresponde a una semilla."""
        seeds = [run["seed"] for run in common.find_case(self.grouped, model, rho, eta)]
        if seed not in seeds:
            raise SystemExit(f"el caso {model}, rho={rho:g}, eta={eta:g} no tiene "
                             f"la semilla {seed}; hay de {min(seeds)} a {max(seeds)}")
        return seeds.index(seed)

    def realizations(self) -> int:
        return min(len(group) for group in self.grouped.values())


# Disposicion de los dos paneles. La fija main() a partir de --paneles.
SIDE_BY_SIDE = False


def new_figure():
    """Dos paneles: va arriba y S abajo, o uno al lado del otro."""
    if SIDE_BY_SIDE:
        size = (13.4, 4.8) if common.STYLE == "diapositiva" else (11.0, 3.3)
        figure, panels = plt.subplots(1, 2, figsize=size)
        for axes in panels:
            axes.set_xlabel(common.AXIS_TIME)
    else:
        figure, panels = plt.subplots(2, 1, sharex=True, figsize=(7.6, 6.4))
        panels[1].set_xlabel(common.AXIS_TIME)
    panels[0].set_ylabel(common.AXIS["va"])
    panels[0].set_ylim(0.0, 1.05)
    panels[1].set_ylabel(common.AXIS["S"])
    return figure, panels


def place_legend(figure, panels, columns: int) -> None:
    """Leyenda de las series, arriba del area de datos.

    Con los paneles apilados alcanza con ponerla sobre el de arriba; con los
    paneles lado a lado tiene que abarcar los dos, asi que va a nivel de
    figura. Las etiquetas se juntan de todos los paneles y se descartan las
    repetidas: los trazos comunes (t_eq, promedio) aparecen en los dos, pero el
    valor escalar de cada observable es distinto y tiene que estar en la
    leyenda una vez cada uno.
    """
    handles: list = []
    labels: list = []
    for axes in panels:
        for handle, label in zip(*axes.get_legend_handles_labels()):
            if label not in labels:
                handles.append(handle)
                labels.append(label)
    if SIDE_BY_SIDE:
        # La leyenda se ancla justo encima del area de los paneles. Si se la
        # anclara al borde de la figura quedaria una franja vacia entre ambos,
        # porque savefig recorta lo que sobresale pero no lo que queda adentro.
        figure.subplots_adjust(top=0.88)
        figure.legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 0.90),
                      ncol=columns, frameon=False)
    else:
        panels[0].legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 1.01),
                         ncol=columns, frameon=False)


def single_case(cases: Cases, model: str, rho: float, eta: float, folder) -> None:
    stack = cases.stack(model, rho, eta)
    result = common.analyse_case(stack)
    time = stack[0, :, 0]
    start = result["start"]

    figure, panels = new_figure()
    color = common.MODEL_STYLE[model]["color"]
    for axes, observable in zip(panels, ("va", "S")):
        column = common.COLUMN[observable]
        for index in range(stack.shape[0]):
            axes.plot(time, stack[index, :, column], color=GREY, linewidth=0.5, alpha=0.45,
                      label=f"realizaciones ($M$ = {result['M']})" if index == 0 else None)
        axes.plot(time, stack[:, :, column].mean(axis=0), color=color, linewidth=1.6,
                  label="promedio de las realizaciones")
        axes.axvline(time[start], color="black", linestyle=":", linewidth=1.4,
                     label=f"$t_{{eq}}$ = {time[start]:.0f}")
        mean, deviation = result[observable], result[f"{observable}_std"]
        axes.hlines(mean, time[start], time[-1], color="black", linestyle="--", linewidth=1.3,
                    label=f"$\\langle {common.LABEL[observable][1:-1]} \\rangle$ = "
                          f"{mean:.3f} $\\pm$ {deviation:.3f}")
        axes.fill_between([time[start], time[-1]], mean - deviation, mean + deviation,
                          color=color, alpha=0.18, linewidth=0)
    if SIDE_BY_SIDE:
        place_legend(figure, panels, 2)
    else:
        panels[0].legend(loc="best", ncol=2, fontsize=10)
    # El sufijo _lado distingue la version de paneles lado a lado de la apilada:
    # si no, una pisaria a la otra en la misma carpeta.
    marca = "_lado" if SIDE_BY_SIDE and common.STYLE != "diapositiva" else ""
    common.save(figure, folder,
                f"va_S_vs_t_{model}_rho{common.density_number(rho)}"
                f"_eta{common.number(eta)}_M{result['M']}{marca}.png")


def overlay(cases: Cases, entries: list[tuple], folder, name: str, seed: int | None = None) -> None:
    """entries: [(model, rho, eta, etiqueta, color)].

    Con seed se dibuja esa realizacion en lugar del promedio de las M. El
    t_eq y el promedio estacionario que se marcan siguen calculandose sobre
    las M realizaciones, que es la convencion unica del trabajo: lo que cambia
    es solo la curva que se muestra, para que se vea la fluctuacion real de
    una corrida y no la que queda despues de promediar.
    """
    figure, panels = new_figure()
    realizations = None
    for index, (model, rho, eta, label, color) in enumerate(entries):
        stack = cases.stack(model, rho, eta)
        result = common.analyse_case(stack)
        realizations = result["M"] if realizations is None else min(realizations, result["M"])
        time = stack[0, :, 0]
        start = result["start"]
        style = common.MODEL_STYLE[model]["linestyle"]
        for axes, observable in zip(panels, ("va", "S")):
            column = common.COLUMN[observable]
            curve = (stack[:, :, column].mean(axis=0) if seed is None
                     else stack[cases.row(model, rho, eta, seed), :, column])
            # El t_eq va en la etiqueta: si dos verticales coinciden, el valor
            # sigue estando escrito aunque una tape a la otra.
            axes.plot(time, curve, color=color, linewidth=1.3 if seed is None else 0.9,
                      linestyle=style,
                      label=f"{label},  $t_{{eq}}$ = {time[start]:.0f} s")
            axes.axvline(time[start], color=color, linewidth=1.2,
                         linestyle=DASH_PHASES[index % len(DASH_PHASES)])
            axes.hlines(result[observable], time[start], time[-1], color=color,
                        linestyle="--", linewidth=1.0, alpha=0.8)
    # Dos leyendas: las series arriba del area de datos, porque las curvas
    # ocupan todo el ancho, y la convencion de trazos dentro del panel de S,
    # que es el que suele tener lugar libre.
    place_legend(figure, panels, min(len(entries), 3))
    panels[1].legend(handles=CONVENTION, loc="best",
                     fontsize=13 if common.STYLE == "diapositiva" else 9)
    common.save(figure, folder, name.replace("{M}", str(realizations)))


def standard_set(cases: Cases, figures) -> None:
    low, high = 0.5, 4.0
    eta_set = [0.5, 1.0, 2.0, 3.0, 4.0]
    # Tres ruidos que dan comportamientos cualitativamente distintos --- banda
    # unica, transicion y desorden ---, con una sola realizacion por curva: es
    # la figura de evolucion temporal que se muestra en la presentacion.
    eta_trio = [0.5, 2.0, 5.0]
    trio_seed = 1
    rhos = [2.0, 4.0, 8.0]
    eta_colors = plt.cm.viridis(np.linspace(0.05, 0.85, len(eta_set)))
    trio_colors = plt.cm.viridis(np.linspace(0.05, 0.85, len(eta_trio)))

    for model in ("vicsek", "voter"):
        # (b) para Vicsek; (f) repite (b) para el votante.
        item = common.folder("b" if model == "vicsek" else "f", figures)
        for rho in rhos:
            for eta in (low, high):
                single_case(cases, model, rho, eta, item)
            overlay(cases,
                    [(model, rho, eta, common.noise_legend(eta), color)
                     for eta, color in zip(eta_set, eta_colors)],
                    item,
                    f"va_S_vs_t_{model}_rho{common.density_number(rho)}"
                    f"_etas{common.joined(eta_set)}_promedioM{{M}}.png")
            overlay(cases,
                    [(model, rho, eta, common.noise_legend(eta), color)
                     for eta, color in zip(eta_trio, trio_colors)],
                    item,
                    f"va_S_vs_t_{model}_rho{common.density_number(rho)}"
                    f"_etas{common.joined(eta_trio)}_semilla{trio_seed}.png",
                    seed=trio_seed)
        # (d) S(t) para las tres densidades; (f) lo repite para el votante.
        item = common.folder("d" if model == "vicsek" else "f", figures)
        for eta in (low, 2.0, high):
            overlay(cases,
                    [(model, rho, eta, common.density_legend(rho),
                      common.density_color(rho))
                     for rho in rhos],
                    item,
                    f"va_S_vs_t_{model}_eta{common.number(eta)}"
                    f"_rhos{common.joined_densities(rhos)}_promedioM{{M}}.png")

    # (f) comparacion directa entre modelos, misma densidad y mismo ruido.
    item = common.folder("f", figures)
    for rho in rhos:
        for eta in (low, 2.0):
            overlay(cases,
                    [(model, rho, eta, common.MODEL_LABEL[model], common.MODEL_STYLE[model]["color"])
                     for model in ("vicsek", "voter")],
                    item,
                    f"va_S_vs_t_vicsek_vs_voter_rho{common.density_number(rho)}"
                    f"_eta{common.number(eta)}_promedioM{{M}}.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", choices=("vicsek", "voter"))
    parser.add_argument("--rho", type=float)
    parser.add_argument("--eta", type=float, help="un caso con todas sus realizaciones")
    parser.add_argument("--etas", help="lista separada por coma: superpone las curvas promedio")
    parser.add_argument("--rhos", help="lista separada por coma: superpone las curvas promedio "
                                       "de esas densidades a un mismo --eta (figura del item d)")
    parser.add_argument("--seed", type=int,
                        help="en las superposiciones, dibujar esa realizacion en vez "
                             "del promedio de las M")
    parser.add_argument("--item", default="b", choices=tuple(common.FOLDER_NAME),
                        help="carpeta de destino de la figura puntual")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    common.use_report_style(arguments.estilo)
    global SIDE_BY_SIDE
    SIDE_BY_SIDE = (arguments.paneles == "lado"
                    or (arguments.paneles == "auto" and arguments.estilo == "diapositiva"))
    # Sin --model se genera el juego completo del informe. Cualquier otra opcion
    # de seleccion queda sin efecto en ese modo, asi que se rechaza en vez de
    # ignorarla en silencio.
    selectors = {"--rho": arguments.rho, "--eta": arguments.eta,
                 "--etas": arguments.etas, "--rhos": arguments.rhos,
                 "--seed": arguments.seed}
    if arguments.model is None:
        given = [name for name, value in selectors.items() if value is not None]
        if given:
            raise SystemExit(f"{', '.join(given)} necesita --model; sin --model se "
                             "genera el juego completo de figuras del informe")
        standard_set(Cases(arguments.sweep), arguments.figures)
        return

    cases = Cases(arguments.sweep)
    folder = common.folder(arguments.item, arguments.figures)
    # El nombre dice de donde sale cada curva: del promedio de las M
    # realizaciones o de una sola, identificada por su semilla.
    suffix = "promedioM{M}" if arguments.seed is None else f"semilla{arguments.seed}"
    if SIDE_BY_SIDE and arguments.estilo != "diapositiva":
        suffix += "_lado"
    if arguments.rhos:
        if arguments.eta is None:
            raise SystemExit("--rhos necesita un --eta")
        rhos = [float(piece) for piece in arguments.rhos.split(",")]
        overlay(cases,
                [(arguments.model, rho, arguments.eta,
                  common.density_legend(rho), common.density_color(rho))
                 for rho in rhos],
                folder,
                f"va_S_vs_t_{arguments.model}_eta{common.number(arguments.eta)}"
                f"_rhos{common.joined_densities(rhos)}_{suffix}.png",
                seed=arguments.seed)
        return
    if arguments.rho is None:
        raise SystemExit("--rho es obligatorio junto con --model")
    if arguments.etas:
        etas = [float(piece) for piece in arguments.etas.split(",")]
        colors = plt.cm.viridis(np.linspace(0.05, 0.85, len(etas)))
        overlay(cases,
                [(arguments.model, arguments.rho, eta, common.noise_legend(eta), color)
                 for eta, color in zip(etas, colors)],
                folder,
                f"va_S_vs_t_{arguments.model}_rho{common.density_number(arguments.rho)}"
                f"_etas{common.joined(etas)}_{suffix}.png",
                seed=arguments.seed)
    elif arguments.eta is not None:
        single_case(cases, arguments.model, arguments.rho, arguments.eta, folder)
    else:
        raise SystemExit("indicar --eta (un caso) o --etas (superposicion)")


if __name__ == "__main__":
    main()
