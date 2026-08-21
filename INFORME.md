# INFORME — TP2: Autómatas Celulares (Vicsek off-lattice y modelo de votante)

> Documento de trabajo: consolida los **requisitos de formato** del informe y la
> **estructura propuesta** del mismo. Sirve como guía para la redacción posterior
> en LaTeX (Overleaf). Fuentes: consigna `TP2_Enunciado.pdf` y guía de cátedra
> `GuiaInformes.pdf`.

---

## 0. Datos de la entrega

**Materia:** Simulación de Sistemas (SdS) — 2026 Q2
**Comisión:** S2 · **Grupo:** 10

| Integrante | Legajo | Correo |
|---|---|---|
| Javier Liu | 64332 | jaliu@itba.edu.ar |
| Juan Ignacio Cantarella | 64509 | jcantarella@itba.edu.ar |
| Nicolás Rivas | 64292 | nrivas@itba.edu.ar |

**Nombres de archivo para la entrega en campus** (patrón `SdS_TP2_2026Q2GXXCSS_*`
con XX = 10 y SS = S2):

```
SdS_TP2_2026Q2G10S2_Presentación.pdf
SdS_TP2_2026Q2G10S2_Codigo.zip
SdS_TP2_2026Q2G10S2_Informe.pdf
```

**Fecha límite:** 04/09/2026, 13:00 h (campus). Presentación oral de 13 min el mismo día.

La portada del informe en LaTeX debe llevar: título del TP, materia, comisión,
grupo e integrantes con legajo.

---

## 1. Requisitos de formato (obligatorios)

### 1.1 Documento autocontenido

- El informe y la presentación son **documentos independientes y autocontenidos**.
  No se puede omitir un ítem en uno bajo el argumento de que "está en el otro".
- **Numerar secciones y sub-secciones.**
- Secciones habituales (mismas que la presentación): *Introducción; Modelo;
  Implementación; Simulaciones; Resultados; Conclusiones*. Detalle en
  `GuiaPresentaciones.pdf` / `Formato_Informes.pdf`.
- Sección final **"Referencias", sin número**.

### 1.2 Redacción técnica

- **Lenguaje técnico escrito.** Sin lenguaje coloquial ni descripciones
  "literarias". Un **único idioma** en todo el informe (castellano).
- **Todas** las secciones llevan texto que analiza y mantiene un hilo lógico del
  estudio. **En ningún caso** puede haber una sección con figuras sueltas.
- Toda afirmación, descripción y conclusión debe estar **basada en los datos**
  mostrados en las figuras/tablas del propio informe. Nada de aseveraciones sin
  respaldo cuantitativo.
- Las conclusiones se establecen **a partir de los resultados presentados**.

### 1.3 Ecuaciones

- **Numeradas** y **referenciadas en el texto**: "En la Ec. (1) ...".
- Toda ecuación va seguida de la definición de sus símbolos:

  > *donde E es la energía, m la masa de la partícula y c la velocidad de la luz.*

- Convención tipográfica para símbolos matemáticos (informe y presentación):

  | Elemento | Fuente | Estilo | Ejemplo |
  |---|---|---|---|
  | Escalares | Times New Roman | *itálica*, sin negrita | *t*, *η*, *v*<sub>a</sub> |
  | Vectores | Times New Roman | **negrita**, sin itálica | **r**<sub>i</sub>(*t*) |
  | Números y unidades | Times New Roman | sin negrita, sin itálica | m = 4 kg |

- Unidades: metros `m`, segundos `s`, kilogramo `kg`, etc.

### 1.4 Figuras

- **Numeradas** y **referenciadas en el texto**: "En la Fig. 1 ...".
- **Leyenda (caption) descriptiva**: qué se grafica, parámetros usados,
  N, L, ρ, η, número de realizaciones, criterio de promediado.
- Regla general del contenido: **observable vs. input/parámetro**, con
  **promedios y barras de error**.
- **Ejes rotulados** con magnitud y unidad; **tamaño de fuente legible**
  (ejes, ticks y leyenda deben leerse a tamaño impreso, comparable al del cuerpo
  del texto). Leyenda interna (*legend*) cuando haya más de una serie.
- Si una figura no se referencia en el texto, no va en el informe.

### 1.5 Promedios sobre realizaciones

- **Promediar varias realizaciones** (múltiples semillas / condiciones iniciales
  independientes) para todo observable escalar reportado.
- Reportar explícitamente: número de realizaciones *M*, la definición del
  promedio y la barra de error usada (desvío estándar o error estándar
  σ/√*M* — indicar cuál).
- Para observables estacionarios: promediar **primero** en el tiempo dentro del
  estado estacionario y **luego** entre realizaciones; justificar el instante
  *t*<sub>eq</sub> de inicio del estacionario con las evoluciones temporales.

### 1.6 Referencias

- Sección extra **sin número**, al final, con la bibliografía **citada** en el
  trabajo. Si no está citado en el texto, **no se lista**.
- Cita en el texto: "Se ha demostrado [1] que ...".
- Formato de entrada:

  ```
  [1] Nombre Apellido, "Título trabajo", Nombre publicación, vol., nro., pp. (año).
  ```

- Fuente de las citas: Google Scholar → símbolo de doble comilla bajo la
  publicación.

### 1.7 Herramienta

- **Sugerencia general de la cátedra: usar LaTeX** como procesador de texto y de
  ecuaciones (p. ej. Overleaf, <https://www.overleaf.com>).

---

## 2. Estructura propuesta del informe

### 1. Introducción
Motivación del modelo de Vicsek [1] como transición de fase en sistemas de
partículas autopropulsadas; objetivo del trabajo: caracterizar la polarización
*v*<sub>a</sub> y la fracción de la componente gigante *S* en función del ruido
*η* para ρ = 2, 4, 8, comparando el modelo estándar con el modelo de votante [2].

### 2. Modelo
- Caja cuadrada de lado *L* = 10 con condiciones periódicas de contorno.
- Regla de actualización de posiciones — **Ec. (1)**.
- Regla de actualización de direcciones, modelo estándar (promedio vectorial de
  las direcciones de los vecinos dentro de *r*<sub>c</sub> + ruido *η*) —
  **Ec. (2)**. **Criterio confirmado por la cátedra:** el promedio del modelo
  estándar **incluye a la propia partícula**; debe explicitarse en el texto que
  acompaña a la Ec. (2).
- Regla del modelo de votante: la partícula **copia** la dirección
  *θ*<sub>j</sub>(*t*) de **un** vecino elegido al azar, sin promediar, más el
  ruido *η* [2] — **Ec. (3)**. La copia se toma del estado en *t* (actualización
  sincrónica).
- Observable polarización *v*<sub>a</sub> — **Ec. (4)**.
- Definición de cluster (cadena de vecinos dentro de *r*<sub>c</sub>) y del
  observable *S* (fracción de nodos en el cluster mayor) — **Ec. (5)**.
- Definición de densidad ρ = *N*/*L*² — **Ec. (6)**.

### 3. Implementación
- Motor de simulación y método de vecinos: **Cell Index Method (CIM)** off-lattice
  con condiciones periódicas; parámetros *M* de grilla y *r*<sub>c</sub>.
- Formato del **archivo de texto de salida**; el módulo de animación se ejecuta
  de forma **independiente** tomando esos archivos como entrada (la velocidad de
  animación no queda supeditada a la de simulación).
- Pseudocódigo / diagrama de flujo del paso de simulación.

### 4. Simulaciones
Tabla de parámetros: *L*, *N* por densidad, *r*<sub>c</sub>, *v*, Δ*t*, barrido de
*η*, cantidad de pasos, *t*<sub>eq</sub>, número de realizaciones *M* por punto y
semillas.

### 5. Resultados
Un bloque por estudio, cada uno con: **animación característica** → **evolución
temporal del observable primario** → **explicitación del cálculo del escalar**
(promedio o derivada) → **curva input vs. observable escalar**.

| Ítem consigna | Contenido | Figura(s) |
|---|---|---|
| (a) | Animaciones características: partículas como vectores velocidad, coloreados por ángulo | link/captura |
| (b) | Evolución temporal de *v*<sub>a</sub>(*t*); línea vertical marcando el inicio del estacionario | Fig. X |
| (c) | *v*<sub>a</sub> vs. *η* con barras de error, una curva por ρ | Fig. X |
| (d) | *S*(*t*) para las tres ρ; ⟨*S*⟩ estacionario con desvío vs. *η* | Fig. X, X |
| (e) | *v*<sub>a</sub> vs. *S*, distinguiendo densidades | Fig. X |
| (f) | Repetición de (a–e) para el modelo de votante y **comparación superpuesta** en las figuras de (b, c, d, e) | Fig. X |
| (g) | Tiempos de ejecución del CIM para *N* comparable al TP1, contrastados con los del TP1 | Fig. X / Tabla X |

### 6. Conclusiones
Conclusiones **basadas exclusivamente en los datos** de la Sección 5: dependencia
de la transición con ρ, comparación cuantitativa estándar vs. votante, relación
*v*<sub>a</sub>–*S*, y desempeño del CIM.

### Referencias *(sin número)*

```
[1] T. Vicsek, A. Czirók, E. Ben-Jacob, I. Cohen y O. Shochet, "Novel type of phase
    transition in a system of self-driven particles", Physical Review Letters,
    vol. 75, nro. 6, p. 1226 (1995).
[2] E. S. Loscar, G. Baglietto y F. Vazquez, "Noisy multistate voter model for
    flocking in finite dimensions", Physical Review E, vol. 104, nro. 3,
    p. 034111 (2021).
```

---

## 3. Checklist previo a la entrega

- [ ] Explicitado en el texto de la Ec. (2) que el promedio del modelo estándar
      incluye a la propia partícula, y en la Ec. (3) que el votante copia
      *θ*<sub>j</sub>(*t*).
- [ ] Secciones y sub-secciones numeradas; "Referencias" sin numerar.
- [ ] Todas las ecuaciones numeradas y citadas como "Ec. (n)" en el texto.
- [ ] Símbolos definidos tras cada ecuación; escalares en itálica, vectores en
      negrita, unidades en redonda.
- [ ] Todas las figuras numeradas, citadas como "Fig. n", con leyenda completa.
- [ ] Ejes rotulados con unidades y fuente legible en todas las figuras.
- [ ] Todo observable escalar promediado sobre *M* realizaciones, con barras de
      error y *M* declarado.
- [ ] Criterio de estado estacionario justificado con evoluciones temporales.
- [ ] Ninguna sección con figuras sueltas: todas con texto analítico.
- [ ] Cada afirmación/conclusión remite a una figura o tabla del informe.
- [ ] Un solo idioma; registro técnico.
- [ ] Toda referencia listada está citada en el texto, y viceversa.
- [ ] Portada con título, materia, comisión S2, grupo 10 e integrantes con legajo.
- [ ] Compilado en LaTeX; archivo nombrado `SdS_TP2_2026Q2G10S2_Informe.pdf`.
- [ ] Entrega por campus antes del 04/09/2026, 13:00 h.
