# Validacion interna por ablacion: RAG x XAI

Corrida `ablation` · 63 preguntas · 315 respuestas puntuadas

Diseno factorial 2x2 pareado: los cuatro brazos responden las mismas preguntas.
Todo lo que se mide esta verificado contra el corpus normativo, no contra lo que
el sistema declara de si mismo.

## Brazos

| Brazo | RAG | XAI | Respuestas | Fallos |
|---|:-:|:-:|--:|--:|
| `full` | si | si | 63 | 0.00 |
| `no_rag` | no | si | 63 | 0.00 |
| `no_xai` | si | no | 63 | 0.00 |
| `base` | no | no | 63 | 0.00 |

## Resultados por metrica

| Metrica | full | no_rag | no_xai | base | Efecto RAG | Efecto XAI | Interaccion |
|---|--:|--:|--:|--:|--:|--:|--:|
| Respuestas trazables | 0.857 | 0.000 | 0.000 | 0.000 | 0.429 | 0.429 | 0.857 |
| Respuestas correctas | 0.889 | 0.882 | 0.889 | 0.860 | 0.031 | -0.011 | 0.020 |
| Recall de articulos esperados | 0.697 | 0.000 | 0.049 | 0.000 | 0.373 | 0.324 | 0.648 |
| Cobertura de puntos clave | 0.852 | 0.778 | 0.833 | 0.753 | 0.085 | -0.001 | 0.049 |
| Articulos que ve el usuario | 2.238 | 0.000 | 0.048 | 0.000 | 1.143 | 1.095 | 2.190 |
| Articulos nombrados en el texto | 0.063 | 0.000 | 0.048 | 0.000 | 0.056 | 0.008 | 0.016 |
| Articulos inventados por respuesta | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Citas sin norma por respuesta | 0.000 | 0.000 | 0.016 | 0.000 | 0.008 | -0.008 | -0.016 |
| Afirmaciones normativas | 2.349 | 2.032 | 2.365 | 2.095 | 0.294 | -0.040 | 0.048 |
| Citas por respuesta | 2.492 | 0.000 | 0.000 | 0.000 | 1.246 | 1.246 | 2.492 |

El efecto de cada componente es la media de sus dos contrastes (quitarlo con el
otro componente puesto y sin el). La interaccion es la diferencia entre ambos:
si es grande, los componentes no son independientes y el efecto principal por si
solo describe mal el sistema.

## Contrastes pareados

| Metrica | Contraste | Test | n | Diferencia media | IC 95% | p |
|---|---|---|--:|--:|---|--:|
| Respuestas trazables | full vs no_rag | McNemar | 63 | 0.857 | [0.762, 0.937] | <0.001 |
| Respuestas trazables | full vs no_xai | McNemar | 63 | 0.857 | [0.762, 0.937] | <0.001 |
| Respuestas correctas | full vs no_rag | McNemar | 49 | 0.041 | [-0.061, 0.143] | 0.688 |
| Respuestas correctas | full vs no_xai | McNemar | 51 | 0.000 | [-0.059, 0.059] | 1.000 |
| Recall de articulos esperados | full vs no_rag | Wilcoxon | 61 | 0.697 | [0.590, 0.803] | <0.001 |
| Recall de articulos esperados | full vs no_xai | Wilcoxon | 61 | 0.648 | [0.525, 0.762] | <0.001 |
| Cobertura de puntos clave | full vs no_rag | Wilcoxon | 49 | 0.109 | [0.010, 0.211] | 0.064 |
| Cobertura de puntos clave | full vs no_xai | Wilcoxon | 51 | 0.020 | [-0.049, 0.088] | 0.600 |
| Articulos que ve el usuario | full vs no_rag | Wilcoxon | 63 | 2.238 | [1.857, 2.635] | <0.001 |
| Articulos que ve el usuario | full vs no_xai | Wilcoxon | 63 | 2.190 | [1.810, 2.603] | <0.001 |
| Articulos nombrados en el texto | full vs no_rag | Wilcoxon | 63 | 0.063 | [0.000, 0.143] | n/d |
| Articulos nombrados en el texto | full vs no_xai | Wilcoxon | 63 | 0.016 | [-0.063, 0.111] | n/d |
| Articulos inventados por respuesta | full vs no_rag | Wilcoxon | 63 | 0.000 | [0.000, 0.000] | n/d |
| Articulos inventados por respuesta | full vs no_xai | Wilcoxon | 63 | 0.000 | [0.000, 0.000] | n/d |
| Citas sin norma por respuesta | full vs no_rag | Wilcoxon | 63 | 0.000 | [0.000, 0.000] | n/d |
| Citas sin norma por respuesta | full vs no_xai | Wilcoxon | 63 | -0.016 | [-0.048, 0.000] | n/d |
| Afirmaciones normativas | full vs no_rag | Wilcoxon | 63 | 0.317 | [-0.095, 0.730] | 0.179 |
| Afirmaciones normativas | full vs no_xai | Wilcoxon | 63 | -0.016 | [-0.460, 0.429] | 0.749 |
| Citas por respuesta | full vs no_rag | Wilcoxon | 63 | 2.492 | [2.143, 2.841] | <0.001 |
| Citas por respuesta | full vs no_xai | Wilcoxon | 63 | 2.492 | [2.143, 2.841] | <0.001 |

## Control de formato: `no_xai_inline`

`no_xai` conserva la instruccion de no nombrar fuentes dentro de la respuesta, pero
se queda sin la interfaz que las muestra. `no_xai_inline` es el mismo brazo con
permiso para citar en el texto. Lo que recupera frente a `no_xai` es sesgo de
formato; lo que aun le falta frente a `full` es el aporte propio de la capa XAI.

| Metrica | no_xai | no_xai_inline | full | Recupera (inline - no_xai) | IC 95% | p | Falta (full - inline) | IC 95% | p |
|---|--:|--:|--:|--:|---|--:|--:|---|--:|
| Respuestas trazables | 0.000 | 0.000 | 0.857 | 0.000 | [0.000, 0.000] | 1.000 | 0.857 | [0.762, 0.937] | <0.001 |
| Respuestas correctas | 0.889 | 0.923 | 0.889 | 0.039 | [0.000, 0.098] | 0.500 | -0.039 | [-0.118, 0.039] | 0.625 |
| Recall de articulos esperados | 0.049 | 0.311 | 0.697 | 0.262 | [0.156, 0.377] | <0.001 | 0.385 | [0.270, 0.500] | <0.001 |
| Cobertura de puntos clave | 0.833 | 0.856 | 0.852 | 0.029 | [-0.020, 0.088] | 0.345 | -0.010 | [-0.088, 0.059] | 0.753 |
| Articulos que ve el usuario | 0.048 | 0.714 | 2.238 | 0.667 | [0.460, 0.889] | <0.001 | 1.524 | [1.159, 1.905] | <0.001 |
| Articulos nombrados en el texto | 0.048 | 0.714 | 0.063 | 0.667 | [0.460, 0.889] | <0.001 | -0.651 | [-0.873, -0.444] | <0.001 |
| Articulos inventados por respuesta | 0.000 | 0.000 | 0.000 | 0.000 | [0.000, 0.000] | n/d | 0.000 | [0.000, 0.000] | n/d |
| Citas sin norma por respuesta | 0.016 | 0.159 | 0.000 | 0.143 | [0.048, 0.254] | 0.012 | -0.159 | [-0.270, -0.063] | 0.008 |
| Afirmaciones normativas | 2.365 | 2.508 | 2.349 | 0.143 | [-0.349, 0.651] | 0.666 | -0.159 | [-0.651, 0.317] | 0.626 |
| Citas por respuesta | 0.000 | 0.000 | 2.492 | 0.000 | [0.000, 0.000] | n/d | 2.492 | [2.143, 2.841] | <0.001 |

`traceable` exige citas estructuradas, que ninguno de los dos brazos sin XAI tiene:
en este contraste vale 0 por construccion y no dice nada. La senal esta en los
articulos nombrados en el texto y en el recall.

## Calidad de las citas (solo brazos con capa XAI)

| Brazo | Citas | Pasaje literal | Con ubicacion | Ubicacion correcta |
|---|--:|--:|--:|--:|
| `full` | 157 | 0.975 | 1.000 | 1.000 |

La ubicacion se recalcula sobre el markdown del corpus a partir del pasaje que la
cita dice haber usado. Una cita bien redactada y mal ubicada cuenta como fallo.

## Comprensibilidad

| Brazo | Respuesta | Articulado citado | **Salto** | Palabras por frase |
|---|--:|--:|--:|--:|
| `full` | 60.5 | 51.7 | **7.8** | 13.7 |
| `no_rag` | 60.0 | — | **—** | 14.0 |
| `no_xai` | 62.5 | — | **—** | 13.4 |
| `base` | 62.5 | — | **—** | 12.9 |

Indice Szigriszt-Pazos, escala 0-100: mas alto, mas facil de leer. El salto compara
**lo que el usuario lee** con el articulado que la respuesta cita: positivo significa
que la respuesta reestructura la norma en lenguaje mas accesible.

## Fidelidad de la cita (repeticiones)

La corrida no llevaba repeticiones, asi que no hay nada que comparar.
Correr con `--repeat 3` para medir esto.

## Calibracion de la confianza declarada

| Brazo | Nivel | n | Respuestas correctas |
|---|---|--:|--:|
| `full` | HIGH | 54 | 0.889 |
| `no_rag` | HIGH | 2 | 1.000 |
| `no_rag` | MEDIUM | 11 | 1.000 |
| `no_rag` | LOW | 38 | 0.842 |

Una confianza que no discrimina —HIGH y LOW con la misma tasa de acierto— es
peor que no declararla: le da al usuario una senal en la que no puede apoyarse.

## Coste y latencia

| Brazo | Latencia p50 | Latencia p95 | Caracteres por respuesta |
|---|--:|--:|--:|
| `full` | 42547 ms | 64452 ms | 1539 |
| `no_rag` | 20280 ms | 25343 ms | 1363 |
| `no_xai` | 39467 ms | 60688 ms | 1736 |
| `base` | 18375 ms | 23703 ms | 1550 |
