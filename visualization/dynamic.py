import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import Normalize
import argparse


# =========================================================
# CONFIGURACIÓN
# =========================================================

L = 10.0                 # lado de la caja (se sobrescribe con static.txt)
VELOCIDAD = 0.03         # módulo de la velocidad (se sobrescribe con static.txt)
FPS = 20

# Longitud con la que se dibuja cada flecha, en unidades de la caja.
#
# No se usa el módulo real de la velocidad: con v = 0.03 y L = 10 el
# desplazamiento por paso es un 0.3% del ancho de la caja y las flechas se ven
# como puntos sueltos. La flecha indica dirección, no módulo, y todas miden lo
# mismo porque en este modelo la rapidez es común a todas las partículas.
LONGITUD_FLECHA = 0.35


# =========================================================
# LECTURA DE DATOS
# =========================================================

def leer_estatico(nombre_archivo):
    """
    Lee static.txt, que trae un `clave valor` por línea.

    Devuelve un diccionario vacío si el archivo no existe, de modo que el
    script siga andando con los valores por defecto.
    """

    parametros = {}

    try:
        with open(nombre_archivo, "r") as archivo:

            for linea in archivo:

                valores = linea.split()

                if len(valores) != 2:
                    continue

                clave, valor = valores

                try:
                    parametros[clave] = float(valor)
                except ValueError:
                    parametros[clave] = valor

    except FileNotFoundError:
        return {}

    return parametros


def leer_datos(nombre_archivo, N, maximo_frames=None, salto=1):
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
        ...

    La primera línea de cada bloque es el número de frame/step.

    `salto` toma uno de cada k bloques y `maximo_frames` corta la lectura:
    dynamic.txt de una corrida larga tiene millones de líneas y no entra en
    memoria si se lo carga entero.
    """

    frames = []
    steps = []
    posiciones = []

    step_actual = None
    bloques_leidos = 0

    def guardar_frame():
        """Cierra el bloque en curso respetando el salto y el máximo."""

        nonlocal posiciones, bloques_leidos

        if not posiciones:
            return False

        if len(posiciones) != N:
            raise ValueError(
                f"Un frame tiene {len(posiciones)} partículas, "
                f"pero se esperaban N={N}."
            )

        if bloques_leidos % salto == 0:
            frames.append(posiciones)
            steps.append(step_actual)

        bloques_leidos += 1
        posiciones = []

        return maximo_frames is not None and len(frames) >= maximo_frames

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

                if guardar_frame():
                    break

                try:
                    step_actual = int(float(valores[0]))
                except ValueError:
                    raise ValueError(
                        f"Línea {numero_linea}: "
                        f"el número de frame no es válido: {valores[0]}"
                    )

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

    guardar_frame()

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

def crear_animacion(
    x,
    y,
    theta,
    steps,
    nombre_salida,
    lado=L,
    longitud_flecha=LONGITUD_FLECHA,
    subtitulo=""
):

    cantidad_tiempos = x.shape[0]

    # ---------------------------------------------------------
    # Versores de dirección
    #
    # Se dibujan versores y no la velocidad real: con scale_units="xy" la
    # longitud de la flecha en unidades de la caja es |v| / scale, así que
    # tomando |v| = 1 y scale = 1 / longitud_flecha todas las flechas miden
    # exactamente longitud_flecha.
    # ---------------------------------------------------------

    vx = np.cos(theta)
    vy = np.sin(theta)

    escala = 1.0 / longitud_flecha

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

    fig, ax = plt.subplots(figsize=(7.2, 7.0))

    ax.set_xlim(0, lado)
    ax.set_ylim(0, lado)

    ax.set_aspect("equal")

    ax.set_xlabel("$x$ [m]", fontsize=14)
    ax.set_ylabel("$y$ [m]", fontsize=14)

    ax.tick_params(labelsize=12)

    ax.grid(True, alpha=0.15)

    titulo = ax.set_title(
        f"$t$ = {steps[0]}\n{subtitulo}",
        fontsize=12
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
        scale=escala,
        width=0.004,
        headwidth=3.5,
        headlength=4.0,
        pivot="tail"
    )

    # ---------------------------------------------------------
    # Barra de color
    # ---------------------------------------------------------

    colorbar = fig.colorbar(quiver, ax=ax)

    colorbar.set_label(r"$\theta$ [rad]", fontsize=14)

    colorbar.ax.tick_params(labelsize=12)

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

    fig.tight_layout()

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
        titulo.set_text(
            f"$t$ = {steps[frame]}\n{subtitulo}"
        )

        return quiver, titulo

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
        default=None,
        help="Cantidad de partículas (por defecto se lee de static.txt)"
    )

    parser.add_argument(
        "-s",
        "--static",
        default="data/static.txt",
        help="Archivo con los parámetros de la corrida"
    )

    parser.add_argument(
        "-o",
        "--output",
        default="animacion.mp4",
        help="Archivo de salida (.mp4 o .gif)"
    )

    parser.add_argument(
        "-f",
        "--frames",
        type=int,
        default=400,
        help="Máximo de cuadros a animar (0 = todos)"
    )

    parser.add_argument(
        "--salto",
        type=int,
        default=1,
        help="Tomar uno de cada k cuadros guardados"
    )

    parser.add_argument(
        "--flecha",
        type=float,
        default=LONGITUD_FLECHA,
        help="Longitud de la flecha, en unidades de la caja"
    )

    args = parser.parse_args()

    # ---------------------------------------------------------
    # Parámetros de la corrida
    # ---------------------------------------------------------

    parametros = leer_estatico(args.static)

    cantidad = args.particulas

    if cantidad is None:

        if "N" not in parametros:
            raise SystemExit(
                f"No se pudo leer N de {args.static}: "
                f"pasarlo a mano con -N."
            )

        cantidad = int(parametros["N"])

    lado = float(parametros.get("L", L))

    subtitulo = ""

    if parametros:
        subtitulo = (
            f"{parametros.get('model', '?')}  ·  "
            f"$N$ = {cantidad}, "
            f"$\\rho$ = {parametros.get('rho', '?'):g}, "
            f"$\\eta$ = {parametros.get('eta', '?'):g}, "
            f"$L$ = {lado:g}, "
            f"$r_c$ = {parametros.get('rc', '?'):g}"
        )

    # ---------------------------------------------------------
    # Leer datos
    # ---------------------------------------------------------

    x, y, theta, steps = leer_datos(
        args.archivo,
        cantidad,
        maximo_frames=args.frames if args.frames > 0 else None,
        salto=max(1, args.salto)
    )

    print(f"Frames encontrados: {len(steps)}")
    print(f"Partículas por frame: {cantidad}")
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
        args.output,
        lado=lado,
        longitud_flecha=args.flecha,
        subtitulo=subtitulo
    )

    print(f"Animación guardada en: {args.output}")


# =========================================================
# EJECUCIÓN
# =========================================================

if __name__ == "__main__":
    main()
