"""Item (a): animacion caracteristica y cuadros sueltos para el informe.

Cada particula se dibuja como un vector con origen en su posicion y color
segun el angulo de la velocidad. La longitud del vector es fija: con v = 0.03 y
L = 10 el desplazamiento real por paso es invisible, asi que la flecha indica
direccion, no modulo. El PDF de la entrega no puede llevar animaciones
embebidas, por eso el modo --snapshots genera la tira de cuadros que si va
impresa, con el link a la animacion aparte.

    python3 visualization/animate.py --out-file data/figures/vicsek_eta0.5.mp4
    python3 visualization/animate.py --snapshots 0,200,2000
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


def subtitle(static: dict) -> str:
    return (
        f"{static.get('model', '?')}  ·  $N$ = {static.get('N', '?')}, "
        f"$\\rho$ = {static.get('rho', '?')}, $\\eta$ = {static.get('eta', '?')}, "
        f"$L$ = {static.get('L', '?')}, $r_c$ = {static.get('rc', '?')}"
    )


def animate(arguments) -> None:
    static = common.read_static(arguments.static)
    count = int(static["N"])
    side = float(static["L"])
    # dynamic.txt ya viene raleado por --save-every, asi que este stride es un
    # raleo adicional solo para acortar la animacion.
    stride = max(1, arguments.stride)

    common.use_report_style()
    figure, axes = plt.subplots(figsize=(6.4, 6.0))
    decorate(axes, side)

    stream = common.frames(arguments.dynamic, count, stride=1, limit=arguments.frames * stride)
    collected = [snapshot for index, snapshot in enumerate(stream) if index % stride == 0]
    if not collected:
        raise SystemExit(f"{arguments.dynamic} no tiene cuadros")

    time, x, y, theta = collected[0]
    artist = draw(axes, x, y, theta, arguments.arrow)
    add_colorbar(figure, artist, axes)
    title = axes.set_title(f"$t$ = {time:.0f}\n{subtitle(static)}", fontsize=11)

    def update(index):
        time, x, y, theta = collected[index]
        artist.set_offsets(np.column_stack((x, y)))
        artist.set_UVC(np.cos(theta), np.sin(theta), theta)
        title.set_text(f"$t$ = {time:.0f}\n{subtitle(static)}")
        return artist, title

    animation = FuncAnimation(figure, update, frames=len(collected),
                              interval=1000 / arguments.fps, blit=False)

    destination = Path(arguments.out_file)
    destination.parent.mkdir(parents=True, exist_ok=True)
    writer = (FFMpegWriter(fps=arguments.fps, bitrate=2400)
              if destination.suffix == ".mp4"
              else PillowWriter(fps=arguments.fps))
    animation.save(destination, writer=writer)
    print(f"animacion: {destination} ({len(collected)} cuadros)")


def snapshots(arguments) -> None:
    static = common.read_static(arguments.static)
    count = int(static["N"])
    side = float(static["L"])
    wanted = sorted(float(piece) for piece in arguments.snapshots.split(","))

    taken: dict[float, tuple] = {}
    for time, x, y, theta in common.frames(arguments.dynamic, count):
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
        axes.set_title(f"$t$ = {time:.0f}")
        if axes is not panels[0]:
            axes.set_ylabel("")
    add_colorbar(figure, artist, list(panels))
    figure.suptitle(subtitle(static), fontsize=11, y=1.02)
    common.save(figure, arguments.name, arguments.out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--static", type=Path, default=common.DATA / "static.txt")
    parser.add_argument("--dynamic", type=Path, default=common.DATA / "dynamic.txt")
    parser.add_argument("--out-file", type=Path, default=common.FIGURES / "animacion.mp4",
                        help="archivo .mp4 o .gif de la animacion")
    parser.add_argument("--frames", type=int, default=400, help="cuadros a animar")
    parser.add_argument("--stride", type=int, default=1,
                        help="tomar uno de cada k cuadros guardados")
    parser.add_argument("--fps", type=int, default=20)
    parser.add_argument("--arrow", type=float, default=0.35,
                        help="longitud fija de la flecha, en unidades de la caja")
    parser.add_argument("--snapshots", type=str, default="",
                        help="tiempos separados por coma: genera un PNG en vez de la animacion")
    parser.add_argument("--name", type=str, default="cuadros.png",
                        help="nombre del PNG en modo --snapshots")
    common.add_common_arguments(parser)
    arguments = parser.parse_args()

    if arguments.snapshots:
        snapshots(arguments)
    else:
        animate(arguments)
    if arguments.show:
        plt.show()


if __name__ == "__main__":
    main()
