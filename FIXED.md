# Revisión de resultados, diapositivas e informe (1/9/2026)

Estado: **propuesta, nada aplicado todavía.** Se revisó cada número de las
diapositivas, del ayuda-memoria y del informe contra `data/sweep/resumen.csv`,
`data/sweep_clusters/resumen.csv`, las series de la semilla 1 y
`data/bench/bench_l20.txt`.

## Verificación de los resultados

Todos los números reproducen:

- η de media polarización: 2,9 / 3,2 / 3,5 rad (estándar, ρ = 2, 4, 8) y
  0,4 / 0,3 / 0,2 rad (votante).
- η de media componente: 2,74 / 2,12 rad (estándar, 1/π y 1/3π) y
  1,19 / 1,13 rad (votante).
- va y S con sus desvíos en todos los puntos citados (0,986(3), 0,27(9),
  0,30(14), 0,48(12), 0,62(3), 0,90(11), 1,000(1), 0,991(40), etc.).
- Pisos por tamaño finito: 0,0627 / 0,0443 / 0,0313 y 0,157 / 0,267.
- Pearson: 0,45 / 0,61 / −0,48 / −0,13 y 0,985 / 0,994 / 0,968 / 0,987.
- t_eq del caso y de la semilla 1 en todas las figuras temporales; máximo
  2900 s en el barrido principal, 5550 s (con ruido) y 19600 s (η = 0) en el
  extendido; dos casos no convergidos (ρ = 2, η = 2,5 y 3,75), diferencia 0,03.
- S inicial a baja densidad: 14–18 %.
- CIM: exponentes 1,34 y 2,11; ×9,8 en N = 1150; cruce en N ≈ 90 (interpolado
  en log-log); factor 1,1–1,7 respecto del TP1; 5,3 % y 10,2 %.
- Las corridas animadas (`data/runs/`) son idénticas a la semilla 1 del
  barrido: "la misma corrida que la animación" es cierto.

**Una descripción está mal.** Baja densidad, η = 0,5 rad (diapositiva 20
izquierda, Fig. 7a del informe, `youtube/titulos.md`, ayuda-memoria 20):
se dice "termina agregado en un único grupo, S → 1". La corrida llega a
S = 1 en t ≈ 400 s, pero después el grupo se parte y se vuelve a juntar todo
el resto de la corrida: en el estacionario S = 1 sólo el 34 % del tiempo,
⟨S⟩ = 0,83 (semilla 1) y el cuadro mostrado (t = 20000 s) tiene dos grupos,
S = 0,59 (19 de 32). La diapositiva en sí no afirma nada (sólo "η = 0,5
rad"); hay que corregir epígrafe, guion y descripción del video: "uno o dos
grupos alineados que se separan y se vuelven a juntar". Además, a η = 5 rad
el grupo mayor tiene 5–6 partículas (S ≈ 0,16–0,2 × 32), no "dos o tres".

## Diapositivas: qué cambiaría y por qué

1. **Aros en las configuraciones animadas (diapositivas 14, 17, 22).** El
   profesor pidió marcar en las curvas los puntos del barrido que corresponden
   a las animaciones. `curves.py --resaltar` existe pero el Makefile nunca lo
   usa: ninguna diapositiva tiene los aros. Van en η = 0,5 y 4 rad sobre la
   curva de ρ = 4 (14, 17) y en η = 0,5 y 5 rad sobre la de ρ = 1/π (22).
2. **Figuras de evolución temporal (13, 16, 21, 24): limpieza.** Sacar el
   recuadro "inicio del estacionario" dentro del gráfico (tapa datos y repite
   el t_eq que ya está en la leyenda de arriba). Verticales de t_eq visibles
   (hoy son hilos). Reemplazar el verde-amarillo de la serie de ruido alto
   (casi invisible en la 16) por un par de colores con contraste. Líneas más
   gruesas y lienzo más ancho para que la figura llene la diapositiva 16:9 en
   vez del 60 % del ancho.
3. **Diapositivas 21 y 24: S(t) de las dos corridas animadas en lugar de
   cuatro densidades a η = 2.** Hoy las dos curvas escalonadas de baja
   densidad se superponen al mismo nivel y no se distinguen. S(t) a ρ = 1/π
   para η = 0,5 y 5 rad (semilla 1) se separa limpio (una sube a ~1, la otra
   queda en 0,2) y repite el esquema del bloque de polarización: animación →
   serie temporal de esa misma corrida → sus puntos en la curva.
   *Contra:* el "S(t) para las tres densidades" del enunciado quedaría sólo
   en el informe (Fig. 8). Alternativa: conservar la figura por densidad y
   sólo limpiarla como en el punto 2.
4. **Etiqueta de leyenda "Vicsek" → "estándar" (18, 27, 28).** Todos los
   títulos dicen "Modelo estándar"; sólo las leyendas dicen "Vicsek".
5. Nada más: estructura, tabla, observables, UML, CIM y conclusiones son
   consistentes con las dos devoluciones del profesor. El ayuda-memoria y
   `youtube/titulos.md` reciben la descripción corregida (y, si entra el
   punto 3, los nuevos t_eq: semilla 1, ρ = 1/π: 600 s en η = 0,5 y 150 s en
   η = 5, modelo estándar). En `titulos.md` la diapositiva de baja densidad es
   la 20, no la 19.

## Informe: qué haría

- Corregir el epígrafe de la Fig. 7, la frase de la Sección 5.5 y el "dos o
  tres partículas" (ver arriba).
- Regenerar las Figs. 6, 9 y 10 como una única figura de matplotlib con
  varios paneles y eje y compartido (1×3 y 1×2). Hoy son dos o tres imágenes
  independientes reducidas al 32–44 % del ancho de texto y el texto de los
  ejes queda en ~4,5–6 pt; como figura única a lo ancho sale en ~7,5 pt, como
  las temporales.
- La misma limpieza de las figuras temporales del punto 2 y la etiqueta del
  punto 4.

## Después del OK

Implementar los cambios en `visualization/`, regenerar los dos juegos de
figuras (`make figures figuras-diapositivas`), recompilar los tres PDF y el
ayuda-memoria (`make entregables ayudamemoria`) y rehacer el zip. Decidir el
punto 3 (recomendado) o conservar la figura de cuatro densidades.
