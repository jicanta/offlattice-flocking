# Animaciones para YouTube (TP2, Grupo 10, comisión S2)

Seis videos, uno por cuadro fijo de las diapositivas 12, 15 y 19. El nombre del archivo
queda como título por defecto al subirlo; abajo va un título con símbolos y una
descripción para pegar. Una vez subidos, los links van en `report/presentacion.tex`
(macro `\dosanim`), en el orden de esta lista; ya están pegados.

Requisitos que cumplen (TP2_Enunciado a; GuiaPresentaciones 2.4.1 y 2.4.8): cada partícula
es un vector con origen en su posición y color según el ángulo de la velocidad; dos
situaciones extremas de ruido por estudio, al inicio de cada uno; en el PDF sólo va un
fotograma de la animación con el link explícito debajo, sin videos embebidos ni adjuntos.
No hay una duración exigida; los videos duran 30 s (40 s los de baja densidad) a 20 fps.

Común a todos: caja L = 10 m con contorno periódico, r_c = 1 m, v = 0,03 m/s, Δt = 1 s,
semilla 1. Se guarda un cuadro cada 5 s (cada 25 s a baja densidad).

## 01 - SdS TP2 G10 - Modelo estandar - rho 4 - eta 0.5 rad.mp4

- **Link**: https://youtu.be/NdiRDSNqLrU

- **Diapositiva**: 12, cuadro de la izquierda.
- **Título sugerido**: SdS TP2 G10 — Modelo estándar (Vicsek), ρ = 4 m⁻², η = 0,5 rad
- **Sistema**: N = 400 partículas, 3000 s simulados, un cuadro cada 5 s.
- **Descripción**: Modelo estándar (Vicsek), ρ = 4 m⁻², η = 0,5 rad; ruido bajo: en unos 200 s todas las partículas se alinean en una única bandada (polarización v_a ≈ 0,99).

## 02 - SdS TP2 G10 - Modelo estandar - rho 4 - eta 4 rad.mp4

- **Link**: https://youtu.be/LxqkFsOcyE8

- **Diapositiva**: 12, cuadro de la derecha.
- **Título sugerido**: SdS TP2 G10 — Modelo estándar (Vicsek), ρ = 4 m⁻², η = 4 rad
- **Sistema**: N = 400 partículas, 3000 s simulados, un cuadro cada 5 s.
- **Descripción**: Modelo estándar (Vicsek), ρ = 4 m⁻², η = 4 rad; ruido alto: no aparece una dirección común; la polarización fluctúa alrededor de 0,27.

## 03 - SdS TP2 G10 - Modelo de votante - rho 4 - eta 0.5 rad.mp4

- **Link**: https://youtu.be/s5gE7K6xIb0

- **Diapositiva**: 15, cuadro de la izquierda.
- **Título sugerido**: SdS TP2 G10 — Modelo de votante, ρ = 4 m⁻², η = 0,5 rad
- **Sistema**: N = 400 partículas, 3000 s simulados, un cuadro cada 5 s.
- **Descripción**: Modelo de votante, ρ = 4 m⁻², η = 0,5 rad; mismo ruido que ordena al modelo estándar: acá se forman dominios de dirección que se arman y se disuelven, sin bandada única (v_a ≈ 0,3).

## 04 - SdS TP2 G10 - Modelo de votante - rho 4 - eta 4 rad.mp4

- **Link**: https://youtu.be/OEx4XdnXkis

- **Diapositiva**: 15, cuadro de la derecha.
- **Título sugerido**: SdS TP2 G10 — Modelo de votante, ρ = 4 m⁻², η = 4 rad
- **Sistema**: N = 400 partículas, 3000 s simulados, un cuadro cada 5 s.
- **Descripción**: Modelo de votante, ρ = 4 m⁻², η = 4 rad; ruido alto: desorden completo, polarización en el piso de tamaño finito (≈ 0,05).

## 05 - SdS TP2 G10 - Modelo estandar - rho 0.32 - eta 0.5 rad.mp4

- **Link**: https://youtu.be/_LJnusRUPjY

- **Diapositiva**: 19, cuadro de la izquierda.
- **Título sugerido**: SdS TP2 G10 — Modelo estándar (Vicsek), ρ = 1/π m⁻², η = 0,5 rad
- **Sistema**: N = 32 partículas, 20000 s simulados, un cuadro cada 25 s.
- **Descripción**: Modelo estándar (Vicsek), ρ = 1/π m⁻², η = 0,5 rad; baja densidad (un vecino por partícula en promedio) y ruido bajo: los grupos que se encuentran se alinean y quedan unidos; el sistema termina agregado en un único grupo (S → 1).

## 06 - SdS TP2 G10 - Modelo estandar - rho 0.32 - eta 5 rad.mp4

- **Link**: https://youtu.be/mAwkTua0wks

- **Diapositiva**: 19, cuadro de la derecha.
- **Título sugerido**: SdS TP2 G10 — Modelo estándar (Vicsek), ρ = 1/π m⁻², η = 5 rad
- **Sistema**: N = 32 partículas, 20000 s simulados, un cuadro cada 25 s.
- **Descripción**: Modelo estándar (Vicsek), ρ = 1/π m⁻², η = 5 rad; baja densidad y ruido alto: queda fragmentado en grupos de dos o tres partículas (S ≈ 0,2).
