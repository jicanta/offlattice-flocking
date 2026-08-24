import numpy as np
import matplotlib.pyplot as plt
import argparse


# =========================================================
# CONFIGURACIÓN
# =========================================================

# =========================================================
# LECTURA DE DATOS
# =========================================================

def leer_datos(nombre_archivo):
    """
    Lee un archivo con formato:

        step polarizacion [fraccion_componente_gigante]

    La tercera columna es la que agrega el motor para el item (d) y aca se
    ignora: este script solo grafica la polarizacion.

    Ejemplo:

        0 0.1163246464 0.995
        1 0.2667016356 0.995
        2 0.303589255 0.9975
        ...
    """

    datos = np.loadtxt(nombre_archivo)

    if datos.ndim != 2 or datos.shape[1] < 2:
        raise ValueError(
            "El archivo debe contener al menos dos columnas: "
            "step y polarizacion."
        )

    steps = datos[:, 0]
    polarizacion = datos[:, 1]

    return steps, polarizacion


# =========================================================
# VISUALIZACIÓN
# =========================================================

def graficar_polarizacion(
    steps,
    polarizacion,
    t_eq,
    nombre_salida=None
):

    # -----------------------------------------------------
    # Seleccionar régimen estacionario
    # -----------------------------------------------------

    mascara = steps >= t_eq

    if not np.any(mascara):
        raise ValueError(
            f"No hay datos para steps >= {t_eq}."
        )

    polarizacion_estacionaria = polarizacion[mascara]

    # -----------------------------------------------------
    # Promedio y desvío estándar
    # -----------------------------------------------------

    promedio = np.mean(
        polarizacion_estacionaria
    )

    desvio = np.std(
        polarizacion_estacionaria,
        ddof=1
    )

    # -----------------------------------------------------
    # Gráfico
    # -----------------------------------------------------

    fig, ax = plt.subplots(
        figsize=(9, 5)
    )

    ax.plot(
        steps,
        polarizacion,
        linewidth=1.2,
        label=r"$v_a(t)$"
    )

    # Línea vertical: inicio del estacionario
    ax.axvline(
        t_eq,
        linestyle="--",
        linewidth=1.5,
        label=rf"$t_{{eq}} = {t_eq}$"
    )

    # Promedio estacionario
    ax.axhline(
        promedio,
        linestyle="-.",
        linewidth=1.5,
        label=rf"$\langle v_a \rangle = {promedio:.4f}$"
    )

    # -----------------------------------------------------
    # Etiquetas
    # -----------------------------------------------------

    ax.set_xlabel(r"$t$")
    ax.set_ylabel(r"$v_a$")

    ax.set_title(
        "Evolución temporal de la polarización"
    )

    ax.grid(
        True,
        alpha=0.3
    )

    ax.legend()

    fig.tight_layout()

    # -----------------------------------------------------
    # Mostrar valores
    # -----------------------------------------------------

    print()
    print("==========================================")
    print("Polarización")
    print("==========================================")
    print(f"Inicio del estacionario: t_eq = {t_eq}")
    print(f"Cantidad de muestras:     {len(polarizacion_estacionaria)}")
    print(f"Promedio estacionario:    {promedio:.6f}")
    print(f"Desvío estándar:           {desvio:.6f}")
    print("==========================================")
    print()

    # -----------------------------------------------------
    # Guardar / mostrar
    # -----------------------------------------------------

    if nombre_salida is not None:
        fig.savefig(
            nombre_salida,
            dpi=300,
            bbox_inches="tight"
        )

        print(
            f"Figura guardada en: {nombre_salida}"
        )

    plt.show()


# =========================================================
# MAIN
# =========================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Visualización de la evolución temporal "
            "de la polarización."
        )
    )

    parser.add_argument(
        "archivo",
        help="Archivo con step y polarización."
    )

    parser.add_argument(
        "--teq",
        type=float,
        required=True,
        help="Tiempo de inicio del estado estacionario."
    )

    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Archivo de salida de la figura."
    )

    args = parser.parse_args()

    # -----------------------------------------------------
    # Leer datos
    # -----------------------------------------------------

    steps, polarizacion = leer_datos(
        args.archivo
    )

    print(
        f"Frames encontrados: {len(steps)}"
    )

    print(
        f"Primer step: {steps[0]}"
    )

    print(
        f"Último step: {steps[-1]}"
    )

    # -----------------------------------------------------
    # Graficar
    # -----------------------------------------------------

    graficar_polarizacion(
        steps,
        polarizacion,
        args.teq,
        args.output
    )


# =========================================================
# EJECUCIÓN
# =========================================================

if __name__ == "__main__":
    main()