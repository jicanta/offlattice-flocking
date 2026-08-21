"""Items (b) y (d): evolucion temporal de va y de S, con el inicio del
estacionario marcado con una linea vertical.

Los datos salen del barrido (data/sweep), asi que las mismas corridas que
alimentan las curvas de los items (c), (d) y (e) son las que se muestran aca.

    python3 visualization/temporal.py --mode eta   --model vicsek --rho 4 --etas 0.5,2,4
    python3 visualization/temporal.py --mode rho   --model vicsek --eta 2
    python3 visualization/temporal.py --mode model --rho 4 --eta 2
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import common

COLUMN = {"va": 1, "S": 2}
LABEL = {"va": "$v_a$", "S": "$S$"}


def close(first: float, second: float) -> bool:
    return abs(first - second) < 1e-9


def pick(runs: list[dict], **filters) -> list[dict]:
    chosen = []
    for run in runs:
        if all(
            (close(run[key], value) if isinstance(value, float) else run[key] == value)
            for key, value in filters.items()
        ):
            chosen.append(run)
    return chosen


def series(arguments) -> tuple[list[tuple], str, str]:
    """Devuelve [(etiqueta, color, tabla)], el titulo y el nombre del archivo."""
    runs = common.read_index(arguments.sweep)
    chosen: list[tuple] = []

    if arguments.mode == "eta":
        wanted = [float(piece) for piece in arguments.etas.split(",")]
        colors = plt.cm.viridis(np.linspace(0.05, 0.85, len(wanted)))
        for noise, color in zip(wanted, colors):
            found = pick(runs, model=arguments.model, rho=arguments.rho,
                         eta=noise, seed=arguments.seed)
            if not found:
                raise SystemExit(f"no hay corrida con eta={noise} en el barrido")
            chosen.append((f"$\\eta$ = {noise:g}", color, common.read_observables(found[0]["path"])))
        title = (f"{common.MODEL_STYLE[arguments.model]['label']}, "
                 f"$\\rho$ = {arguments.rho:g}, semilla {arguments.seed}")
        name = f"temporal_eta_{arguments.model}_rho{arguments.rho:g}.png"

    elif arguments.mode == "rho":
        wanted = [float(piece) for piece in arguments.rhos.split(",")]
        for density in wanted:
            found = pick(runs, model=arguments.model, rho=density,
                         eta=arguments.eta, seed=arguments.seed)
            if not found:
                raise SystemExit(f"no hay corrida con rho={density} en el barrido")
            chosen.append((f"$\\rho$ = {density:g} ($N$ = {found[0]['N']})",
                           common.density_color(density),
                           common.read_observables(found[0]["path"])))
        title = (f"{common.MODEL_STYLE[arguments.model]['label']}, "
                 f"$\\eta$ = {arguments.eta:g}, semilla {arguments.seed}")
        name = f"temporal_rho_{arguments.model}_eta{arguments.eta:g}.png"

    else:
        for model in ("vicsek", "voter"):
            found = pick(runs, model=model, rho=arguments.rho,
                         eta=arguments.eta, seed=arguments.seed)
            if not found:
                raise SystemExit(f"no hay corrida del modelo {model} en el barrido")
            style = common.MODEL_STYLE[model]
            chosen.append((style["label"],
                           "#1f77b4" if model == "vicsek" else "#d62728",
                           common.read_observables(found[0]["path"])))
        title = (f"$\\rho$ = {arguments.rho:g}, $\\eta$ = {arguments.eta:g}, "
                 f"semilla {arguments.seed}")
        name = f"temporal_modelos_rho{arguments.rho:g}_eta{arguments.eta:g}.png"

    return chosen, title, name


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sweep", type=Path, default=common.DATA / "sweep")
    parser.add_argument("--mode", choices=("eta", "rho", "model"), default="eta")
    parser.add_argument("--model", default="vicsek", choices=("vicsek", "voter"))
    parser.add_argument("--rho", type=float, default=4.0)
    parser.add_argument("--eta", type=float, default=2.0)
    parser.add_argument("--etas", default="0.5,2,4")
    parser.add_argument("--rhos", default="2,4,8")
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--observable", choices=("va", "S", "both"), default="both")
    parser.add_argument("--teq", type=int, default=-1,
                        help="forzar el inicio del estacionario (-1 = criterio automatico)")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    common.use_report_style()
    chosen, title, name = series(arguments)
    observables = ("va", "S") if arguments.observable == "both" else (arguments.observable,)

    figure, panels = plt.subplots(len(observables), 1, sharex=True,
                                  figsize=(7.6, 3.2 * len(observables)))
    panels = np.atleast_1d(panels)

    # El estacionario se define con la polarizacion, que es el observable
    # primario, y ese mismo t_eq se usa para S: asi las dos series se promedian
    # sobre la misma ventana temporal.
    for axes, observable in zip(panels, observables):
        column = COLUMN[observable]
        for label, color, table in chosen:
            time = table[:, 0]
            values = table[:, column]
            axes.plot(time, values, color=color, linewidth=1.0, alpha=0.85, label=label)

            start = (arguments.teq if arguments.teq >= 0
                     else common.steady_state_start(table[:, COLUMN["va"]]))
            index = min(start, len(time) - 1)
            axes.axvline(time[index], color=color, linestyle=":", linewidth=1.4)
            mean = values[index:].mean()
            axes.hlines(mean, time[index], time[-1], color=color,
                        linestyle="--", linewidth=1.2)
        axes.set_ylabel(LABEL[observable])
        axes.set_ylim(0.0, 1.05)

    panels[-1].set_xlabel("$t$ [s]")
    figure.suptitle(title, fontsize=12, y=1.05)
    panels[0].legend(loc="lower center", bbox_to_anchor=(0.5, 1.01),
                     ncol=len(chosen), frameon=False)
    figure.text(0.5, -0.02,
                "punteada vertical: inicio del estacionario · rayada horizontal: "
                "promedio temporal en el estacionario",
                ha="center", fontsize=9.5)
    common.save(figure, name, arguments.out)
    if arguments.show:
        plt.show()


if __name__ == "__main__":
    main()
