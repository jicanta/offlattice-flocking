"""Items (b), (d) y (f): evolucion temporal de va y de S.

Dos tipos de figura, siempre con dos paneles (va arriba, S abajo):

* Un caso, todas sus realizaciones: las M curvas en gris, el promedio en
  color, la linea vertical en t_eq, y la linea horizontal con su banda que
  son el valor escalar y su desvio, calculados tal como se usan luego en las
  curvas contra eta. Es la figura que explicita como se calcula el escalar.
* Varios casos superpuestos: solo la curva promedio de cada caso, con su t_eq
  y su promedio estacionario. Sirve para comparar ruidos, densidades o
  modelos. Con --seed se dibuja una realizacion de cada caso en vez del
  promedio, con el t_eq de esa corrida (mismo criterio, aplicado a ella sola)
  y sin el promedio estacionario: se ve la fluctuacion real de una corrida,
  no la que queda despues de promediar.

En las superposiciones el t_eq de cada serie va escrito en su etiqueta de la
leyenda; no hay un recuadro aparte con la convencion de trazos, que taparia
datos y repetiria lo que ya dice la leyenda (el epigrafe del informe explica
los trazos).

Sin argumentos genera el juego completo de figuras del informe. Con --model,
--rho y --eta genera una figura puntual.

    python3 visualization/temporal.py
    python3 visualization/temporal.py --model voter --rho 4 --eta 0.5
    python3 visualization/temporal.py --model vicsek --rho 4 --etas 0.5,2,4
    python3 visualization/temporal.py --model vicsek --eta 2 --rhos 2,4,8 --item d
"""

from __future__ import annotations

import argparse
from pathlib import Path
from functools import lru_cache

import matplotlib.pyplot as plt
import numpy as np
import common

GREY = "#9a9a9a"

# Trazo de las verticales de t_eq: rayas de 4 puntos con hueco de 4, en fases
# distintas para cada caso, de modo que dos casos con el mismo t_eq se
# intercalen en vez de que el ultimo dibujado tape al anterior. El trazo es
# ancho a proposito: un punteado fino no se ve proyectado.
DASH_PHASES = [(phase, (4, 4)) for phase in (0, 4, 2, 6, 1, 5)]


def vertical_width() -> float:
    return 2.4 if common.STYLE == "diapositiva" else 1.4


def curve_width(seed) -> float:
    """Ancho de las curvas superpuestas: una realizacion es mas ruidosa que
    el promedio y va un poco mas fina, pero nunca tanto que se pierda."""
    if common.STYLE == "diapositiva":
        return 2.0 if seed is not None else 2.6
    return 1.1 if seed is not None else 1.4

class Cases:
    """Carga (y recuerda) las realizaciones de cada caso del barrido."""

    def __init__(self, sweeps):
        # Uno o varios barridos: con varios se superponen casos de distinta
        # duracion (5e3 s en data/sweep, 2e4 s en data/sweep_clusters) en una
        # misma figura, que es lo que pide el item (d) para comparar densidades.
        if isinstance(sweeps, (str, Path)):
            sweeps = [sweeps]
        runs = [run for sweep in sweeps for run in common.read_index(sweep)]
        self.grouped = common.group_runs(runs)

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


# Disposicion de los paneles. main() fija ambas a partir de --paneles y de
# --observables: con un solo observable la figura tiene un unico panel.
SIDE_BY_SIDE = False
OBSERVABLES: tuple = ("va", "S")


def new_figure():
    """Un panel por observable: va arriba y S abajo, o uno al lado del otro."""
    if len(OBSERVABLES) == 1:
        # En la diapositiva el panel unico es ancho (16:9 con la leyenda
        # encima) para que la figura llene el ancho del slide.
        size = (11.0, 4.6) if common.STYLE == "diapositiva" else (5.6, 3.3)
        figure, axes = plt.subplots(figsize=size)
        panels = [axes]
        axes.set_xlabel(common.AXIS_TIME)
    elif SIDE_BY_SIDE:
        size = (13.4, 4.8) if common.STYLE == "diapositiva" else (11.0, 3.3)
        figure, panels = plt.subplots(1, 2, figsize=size)
        if common.STYLE == "diapositiva":
            # Con la tipografia grande el rotulo del eje y del panel derecho
            # se mete en el panel izquierdo si queda el espaciado por defecto.
            figure.subplots_adjust(wspace=0.34)
        for axes in panels:
            axes.set_xlabel(common.AXIS_TIME)
    else:
        figure, panels = plt.subplots(2, 1, sharex=True, figsize=(7.6, 6.4))
        panels[1].set_xlabel(common.AXIS_TIME)
    for axes, observable in zip(panels, OBSERVABLES):
        axes.set_ylabel(common.AXIS[observable])
        if observable == "va":
            axes.set_ylim(0.0, 1.05)
    return figure, panels


def prefix() -> str:
    """Nombre de los observables dibujados, tal como encabeza el archivo."""
    return "_".join(OBSERVABLES)


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
    for axes, observable in zip(panels, OBSERVABLES):
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
                f"{prefix()}_vs_t_{model}_rho{common.density_number(rho)}"
                f"_eta{common.number(eta)}_M{result['M']}{marca}.png")


def overlay(cases: Cases, entries: list[tuple], folder, name: str, seed: int | None = None) -> None:
    """entries: [(model, rho, eta, etiqueta, color)].

    Con seed se dibuja esa realizacion en lugar del promedio de las M, y la
    vertical es el t_eq de esa corrida: el mismo criterio de
    common.steady_state_start, aplicado a su va(t) en vez de a la curva
    promedio. Asi la marca se corresponde con lo que se ve. Los escalares de
    las curvas contra eta siguen usando el t_eq del caso (sobre el promedio de
    las M), que puede diferir; el promedio estacionario no se marca en este
    modo porque es el de las M y no el de la corrida dibujada.
    """
    figure, panels = new_figure()
    realizations = None
    # El trazo de cada regla (llena el estandar, de trazos el votante) solo
    # distingue algo cuando la figura mezcla las dos; con una sola regla las
    # curvas van llenas, que sobre una serie ruidosa se lee mucho mejor.
    mixed_models = len({entry[0] for entry in entries}) > 1
    for index, (model, rho, eta, label, color) in enumerate(entries):
        stack = cases.stack(model, rho, eta)
        result = common.analyse_case(stack)
        realizations = result["M"] if realizations is None else min(realizations, result["M"])
        time = stack[0, :, 0]
        style = common.MODEL_STYLE[model]["linestyle"] if mixed_models else "-"
        if seed is None:
            start = result["start"]
        else:
            row = cases.row(model, rho, eta, seed)
            start = min(common.steady_state_start(stack[row, :, common.COLUMN["va"]]),
                        stack.shape[1] - 2)
        for axes, observable in zip(panels, OBSERVABLES):
            column = common.COLUMN[observable]
            curve = (stack[:, :, column].mean(axis=0) if seed is None
                     else stack[row, :, column])
            # El t_eq va en la etiqueta: si dos verticales coinciden, el valor
            # sigue estando escrito aunque una tape a la otra.
            axes.plot(time, curve, color=color, linewidth=curve_width(seed),
                      linestyle=style,
                      label=f"{label},  $t_{{eq}}$ = {time[start]:.0f} s")
            axes.axvline(time[start], color=color, linewidth=vertical_width(),
                         linestyle=DASH_PHASES[index % len(DASH_PHASES)], zorder=1.5)
            if seed is None:
                axes.hlines(result[observable], time[start], time[-1], color=color,
                            linestyle="--", linewidth=1.0, alpha=0.8)
    # La leyenda de las series va arriba del area de datos, porque las curvas
    # ocupan todo el ancho; el t_eq de cada serie esta escrito en su etiqueta.
    place_legend(figure, panels, min(len(entries), 3))
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
    eta_colors = common.noise_colors(len(eta_set))
    trio_colors = common.noise_colors(len(eta_trio))

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
    parser.add_argument("--observables", default="va,S",
                        help="cuales dibujar, separados por coma (va, S o ambos); "
                             "con uno solo la figura tiene un unico panel")
    parser.add_argument("--item", default="b", choices=tuple(common.FOLDER_NAME),
                        help="carpeta de destino de la figura puntual")
    parser.add_argument("--sweeps",
                        help="lista separada por coma de barridos a unir; reemplaza a "
                             "--sweep cuando una superposicion mezcla densidades del "
                             "barrido principal y del extendido")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()
    sweeps = ([piece.strip() for piece in arguments.sweeps.split(",") if piece.strip()]
              if arguments.sweeps else [arguments.sweep])

    common.use_report_style(arguments.estilo)
    global SIDE_BY_SIDE, OBSERVABLES
    SIDE_BY_SIDE = (arguments.paneles == "lado"
                    or (arguments.paneles == "auto" and arguments.estilo == "diapositiva"))
    OBSERVABLES = tuple(piece.strip() for piece in arguments.observables.split(",")
                        if piece.strip())
    if not OBSERVABLES or any(name not in ("va", "S") for name in OBSERVABLES):
        raise SystemExit("--observables admite va, S o va,S")
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
        standard_set(Cases(sweeps), arguments.figures)
        return

    cases = Cases(sweeps)
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
                f"{prefix()}_vs_t_{arguments.model}_eta{common.number(arguments.eta)}"
                f"_rhos{common.joined_densities(rhos)}_{suffix}.png",
                seed=arguments.seed)
        return
    if arguments.rho is None:
        raise SystemExit("--rho es obligatorio junto con --model")
    if arguments.etas:
        etas = [float(piece) for piece in arguments.etas.split(",")]
        colors = common.noise_colors(len(etas))
        overlay(cases,
                [(arguments.model, arguments.rho, eta, common.noise_legend(eta), color)
                 for eta, color in zip(etas, colors)],
                folder,
                f"{prefix()}_vs_t_{arguments.model}_rho{common.density_number(arguments.rho)}"
                f"_etas{common.joined(etas)}_{suffix}.png",
                seed=arguments.seed)
    elif arguments.eta is not None:
        single_case(cases, arguments.model, arguments.rho, arguments.eta, folder)
    else:
        raise SystemExit("indicar --eta (un caso) o --etas (superposicion)")


if __name__ == "__main__":
    main()
