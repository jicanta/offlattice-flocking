import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import Normalize
import argparse


# =========================================================
# CONFIGURACIÓN
# =========================================================

L = 10.0                 # lado de la caja
VELOCIDAD = 0.1          # módulo de la velocidad
ESCALA_VECTOR = 4.0      # escala visual de los vectores
FPS = 20


# =========================================================
# LECTURA DE DATOS
# =========================================================

def leer_datos(nombre_archivo, N):
    """
    Lee un archivo generado por TrajectoryWriter.

    Formato:

        0
        x1 y1 theta1
        x2 y2 theta2
        ...
        xN yN thetaN

        1
        x1 y1 theta1
        x2 y2 theta2
        ...
        xN yN thetaN

    La primera línea de cada bloque es el número de frame/step.
    """

    frames = []
    steps = []
    posiciones = []

    with open(nombre_archivo, "r") as archivo:

        for numero_linea, linea in enumerate(archivo, start=1):

            linea = linea.strip()

            # Ignorar líneas vacías
            if not linea:
                continue

            valores = linea.split()

            # -------------------------------------------------
            # Línea de frame / step
            # -------------------------------------------------

            if len(valores) == 1:

                # Si ya tenemos partículas del frame anterior,
                # terminamos de almacenarlo.
                if posiciones:

                    if len(posiciones) != N:
                        raise ValueError(
                            f"El frame anterior tiene "
                            f"{len(posiciones)} partículas, "
                            f"pero se esperaban N={N}."
                        )

                    frames.append(posiciones)
                    posiciones = []

                try:
                    step = int(float(valores[0]))
                except ValueError:
                    raise ValueError(
                        f"Línea {numero_linea}: "
                        f"el número de frame no es válido: {valores[0]}"
                    )

                steps.append(step)

            # -------------------------------------------------
            # Línea de partícula
            # -------------------------------------------------

            elif len(valores) >= 3:

                try:
                    x = float(valores[0])
                    y = float(valores[1])
                    theta = float(valores[2])
                except ValueError:
                    raise ValueError(
                        f"Línea {numero_linea}: "
                        f"los valores de la partícula no son válidos."
                    )

                posiciones.append([x, y, theta])

                # Evitar que se agreguen más de N partículas
                if len(posiciones) > N:
                    raise ValueError(
                        f"El frame tiene más de N={N} partículas."
                    )

            else:
                raise ValueError(
                    f"Línea {numero_linea}: formato incorrecto:\n"
                    f"{linea}"
                )

    # ---------------------------------------------------------
    # Guardar el último frame
    # ---------------------------------------------------------

    if posiciones:

        if len(posiciones) != N:
            raise ValueError(
                f"El último frame tiene {len(posiciones)} partículas, "
                f"pero se esperaban N={N}."
            )

        frames.append(posiciones)

    # ---------------------------------------------------------
    # Verificaciones
    # ---------------------------------------------------------

    if not frames:
        raise ValueError("No se encontraron frames en el archivo.")

    if len(frames) != len(steps):
        raise ValueError(
            f"La cantidad de frames ({len(frames)}) "
            f"no coincide con la cantidad de steps ({len(steps)})."
        )

    # Convertir a numpy array
    datos = np.array(frames, dtype=float)

    x = datos[:, :, 0]
    y = datos[:, :, 1]
    theta = datos[:, :, 2]

    steps = np.array(steps)

    return x, y, theta, steps


# =========================================================
# ANIMACIÓN
# =========================================================

def crear_animacion(x, y, theta, steps, nombre_salida):

    cantidad_tiempos = x.shape[0]

    # ---------------------------------------------------------
    # Componentes de la velocidad
    # ---------------------------------------------------------

    vx = VELOCIDAD * np.cos(theta)
    vy = VELOCIDAD * np.sin(theta)

    # ---------------------------------------------------------
    # Normalización del ángulo para el mapa de colores
    # ---------------------------------------------------------

    normalizacion = Normalize(
        vmin=-np.pi,
        vmax=np.pi
    )

    # ---------------------------------------------------------
    # Figura
    # ---------------------------------------------------------

    fig, ax = plt.subplots(figsize=(7, 7))

    ax.set_xlim(0, L)
    ax.set_ylim(0, L)

    ax.set_aspect("equal")

    ax.set_xlabel("x")
    ax.set_ylabel("y")

    ax.set_title(
        f"Dinámica del sistema - t = {steps[0]}"
    )

    # ---------------------------------------------------------
    # QUIVER INICIAL
    # ---------------------------------------------------------

    quiver = ax.quiver(
        x[0],
        y[0],
        vx[0],
        vy[0],
        theta[0],
        cmap="hsv",
        norm=normalizacion,
        angles="xy",
        scale_units="xy",
        scale=ESCALA_VECTOR,
        width=0.004
    )

    # ---------------------------------------------------------
    # Barra de color
    # ---------------------------------------------------------

    colorbar = fig.colorbar(quiver, ax=ax)

    colorbar.set_label(r"$\theta$")

    colorbar.set_ticks([
        -np.pi,
        -np.pi / 2,
        0,
        np.pi / 2,
        np.pi
    ])

    colorbar.set_ticklabels([
        r"$-\pi$",
        r"$-\pi/2$",
        r"$0$",
        r"$\pi/2$",
        r"$\pi$"
    ])

    # ---------------------------------------------------------
    # ACTUALIZACIÓN DE LA ANIMACIÓN
    # ---------------------------------------------------------

    def actualizar(frame):

        # Actualizar posición de los vectores
        quiver.set_offsets(
            np.column_stack((
                x[frame],
                y[frame]
            ))
        )

        # Actualizar dirección y color
        quiver.set_UVC(
            vx[frame],
            vy[frame],
            theta[frame]
        )

        # Mostrar el step real del archivo
        ax.set_title(
            f"Dinámica del sistema - t = {steps[frame]}"
        )

        return quiver,

    # ---------------------------------------------------------
    # Crear animación
    # ---------------------------------------------------------

    animacion = FuncAnimation(
        fig,
        actualizar,
        frames=cantidad_tiempos,
        interval=1000 / FPS,
        blit=False
    )

    # ---------------------------------------------------------
    # GUARDAR
    # ---------------------------------------------------------

    if nombre_salida.endswith(".gif"):

        animacion.save(
            nombre_salida,
            writer="pillow",
            fps=FPS
        )

    elif nombre_salida.endswith(".mp4"):

        animacion.save(
            nombre_salida,
            writer="ffmpeg",
            fps=FPS
        )

    else:

        raise ValueError(
            "El archivo de salida debe terminar en .gif o .mp4"
        )

    plt.close(fig)


# =========================================================
# MAIN
# =========================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Genera una animación a partir de posiciones "
            "y ángulos."
        )
    )

    parser.add_argument(
        "archivo",
        help="Archivo generado por TrajectoryWriter"
    )

    parser.add_argument(
        "-N",
        "--particulas",
        type=int,
        required=True,
        help="Cantidad de partículas"
    )

    parser.add_argument(
        "-o",
        "--output",
        default="animacion.mp4",
        help="Archivo de salida (.mp4 o .gif)"
    )

    args = parser.parse_args()

    # ---------------------------------------------------------
    # Leer datos
    # ---------------------------------------------------------

    x, y, theta, steps = leer_datos(
        args.archivo,
        args.particulas
    )

    print(f"Frames encontrados: {len(steps)}")
    print(f"Partículas por frame: {args.particulas}")
    print(f"Primer step: {steps[0]}")
    print(f"Último step: {steps[-1]}")

    # ---------------------------------------------------------
    # Crear animación
    # ---------------------------------------------------------

    crear_animacion(
        x,
        y,
        theta,
        steps,
        args.output
    )

    print(f"Animación guardada en: {args.output}")


# =========================================================
# EJECUCIÓN
# =========================================================

if __name__ == "__main__":
    main()