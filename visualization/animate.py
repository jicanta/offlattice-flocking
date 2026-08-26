"""Item (a): animacion caracteristica y cuadros sueltos para el informe.

Cada particula se dibuja como un vector con origen en su posicion y color
segun el angulo de la velocidad. La longitud del vector es fija: con v = 0.03 y
L = 10 el desplazamiento real por paso es invisible, asi que la flecha indica
direccion, no modulo. El PDF de la entrega no puede llevar animaciones
embebidas, por eso el modo --snapshots genera la tira de cuadros que si va
impresa, con el link a la animacion aparte.

La corrida se lee de una carpeta con static.txt y dynamic.txt (--run), como
las que genera `make animations` en data/runs/<caso>/. El nombre del archivo
de salida se arma con los parametros de la corrida.

    python3 visualization/animate.py --run data/runs/vicsek_rho4_eta0.5
    python3 visualization/animate.py --run data/runs/vicsek_rho4_eta0.5 --snapshots 0,250,1000,3000
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter
from matplotlib.colors import Normalize

import common

CYCLIC = "hsv"


def decorate(axes, side: float) -> None:
    axes.set_xlim(0.0, side)
    axes.set_ylim(0.0, side)
    axes.set_aspect("equal")
    axes.set_xlabel("$x$ [m]")
    axes.set_ylabel("$y$ [m]")
    axes.grid(alpha=0.15)


def draw(axes, x, y, theta, arrow: float):
    return axes.quiver(
        x, y, np.cos(theta), np.sin(theta), theta,
        cmap=CYCLIC, norm=Normalize(-np.pi, np.pi),
        angles="xy", scale_units="xy", scale=1.0 / arrow,
        width=0.004, headwidth=3.5, headlength=4.0, pivot="tail",
    )


def add_colorbar(figure, artist, axes=None) -> None:
    bar = figure.colorbar(artist, ax=axes, ticks=[-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi])
    bar.ax.set_yticklabels(["$-\\pi$", "$-\\pi/2$", "$0$", "$\\pi/2$", "$\\pi$"])
    bar.set_label("$\\theta$ [rad]")


def time_label(axes, time: float):
    """Marca de tiempo dentro del panel: no es un titulo, es parte del cuadro."""
    return axes.text(0.02, 0.98, f"$t$ = {time:.0f}", transform=axes.transAxes,
                     ha="left", va="top", fontsize=12,
                     bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "alpha": 0.85,
                           "edgecolor": "none"})


def stem(static: dict) -> str:
    """vicsek_rho4_eta0.5 (mas L si no es la caja del enunciado)."""
    pieces = [str(static.get("model", "run")),
              f"rho{float(static.get('rho', 0)):g}",
              f"eta{float(static.get('eta', 0)):g}"]
    if float(static.get("L", 10)) != 10.0:
        pieces.insert(1, f"L{float(static['L']):g}")
    return "_".join(pieces)


def animate(arguments, static: dict) -> None:
    count = int(static["N"])
    side = float(static["L"])
    stride = max(1, arguments.stride)

    common.use_report_style()
    figure, axes = plt.subplots(figsize=(6.4, 6.0))
    decorate(axes, side)

    # Se lee de a un cuadro y se corta apenas se junta lo pedido: dynamic.txt de
    # una corrida larga no entra en memoria.
    collected = []
    for index, snapshot in enumerate(common.frames(arguments.run / "dynamic.txt", count)):
        if snapshot[0] < arguments.desde or index % stride:
            continue
        collected.append(snapshot)
        if len(collected) >= arguments.frames:
            break
    if not collected:
        raise SystemExit(f"{arguments.run} no tiene cuadros desde t = {arguments.desde:g}")

    time, x, y, theta = collected[0]
    artist = draw(axes, x, y, theta, arguments.arrow)
    add_colorbar(figure, artist, axes)
    label = time_label(axes, time)

    def update(index):
        time, x, y, theta = collected[index]
        artist.set_offsets(np.column_stack((x, y)))
        artist.set_UVC(np.cos(theta), np.sin(theta), theta)
        label.set_text(f"$t$ = {time:.0f}")
        return artist, label

    animation = FuncAnimation(figure, update, frames=len(collected),
                              interval=1000 / arguments.fps, blit=False)

    folder = common.folder("a", arguments.figures)
    folder.mkdir(parents=True, exist_ok=True)
    suffix = f"_desde{arguments.desde:g}" if arguments.desde > 0 else ""
    destination = folder / (arguments.name or f"{stem(static)}{suffix}.{arguments.format}")
    writer = (FFMpegWriter(fps=arguments.fps, bitrate=2400)
              if destination.suffix == ".mp4" else PillowWriter(fps=arguments.fps))
    animation.save(destination, writer=writer)
    plt.close(figure)
    print(f"animacion: {common.shown(destination)} ({len(collected)} cuadros)")


def snapshots(arguments, static: dict) -> None:
    count = int(static["N"])
    side = float(static["L"])
    wanted = sorted(float(piece) for piece in arguments.snapshots.split(","))

    taken: dict[float, tuple] = {}
    for time, x, y, theta in common.frames(arguments.run / "dynamic.txt", count):
        if time in wanted:
            taken[time] = (x, y, theta)
        if len(taken) == len(wanted):
            break
    missing = [time for time in wanted if time not in taken]
    if missing:
        raise SystemExit(
            f"no estan guardados los cuadros {missing}; revisar --save-every de la simulacion"
        )

    common.use_report_style()
    figure, panels = plt.subplots(1, len(wanted), figsize=(4.2 * len(wanted), 4.6))
    panels = np.atleast_1d(panels)
    for axes, time in zip(panels, wanted):
        x, y, theta = taken[time]
        artist = draw(axes, x, y, theta, arguments.arrow)
        decorate(axes, side)
        time_label(axes, time)
        if axes is not panels[0]:
            axes.set_ylabel("")
    add_colorbar(figure, artist, list(panels))
    name = arguments.name or f"cuadros_{stem(static)}_t{common.joined(wanted)}.png"
    common.save(figure, common.folder("a", arguments.figures), name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", type=Path, required=True,
                        help="carpeta con static.txt y dynamic.txt")
    parser.add_argument("--format", choices=("mp4", "gif"), default="mp4")
    parser.add_argument("--name", default="", help="nombre de salida (por defecto se arma solo)")
    parser.add_argument("--frames", type=int, default=600, help="cuadros a animar")
    parser.add_argument("--stride", type=int, default=1,
                        help="tomar uno de cada k cuadros guardados")
    parser.add_argument("--fps", type=int, default=20)
    parser.add_argument("--desde", type=float, default=0.0,
                        help="animar desde este tiempo: sirve para mostrar solo el estacionario")
    parser.add_argument("--arrow", type=float, default=0.35,
                        help="longitud fija de la flecha, en unidades de la caja")
    parser.add_argument("--snapshots", type=str, default="",
                        help="tiempos separados por coma: genera un PNG en vez de la animacion")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    static = common.read_static(arguments.run / "static.txt")
    if arguments.snapshots:
        snapshots(arguments, static)
    else:
        animate(arguments, static)


if __name__ == "__main__":
    main()
