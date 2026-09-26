# Resumen — `humo`

Commits: frontend `525af54`, backend `80d1826-dirty`; frontend `525af54-dirty`, backend `80d1826`; frontend `f206794`, backend `5cc5438`

## Entrega

| Escenario | n | Entregadas | % | IC 95 % (Wilson) | Mediana (s) | p90 (s) | Errores del runner |
|---|--:|--:|--:|---|--:|--:|--:|
| S0 | 1 | 1 | 100.0 % | [20.7 %; 100.0 %] | 3.8 | 3.8 | 0 |
| S1a | 1 | 1 | 100.0 % | [20.7 %; 100.0 %] | 18.4 | 18.4 | 0 |
| S1b | 1 | 1 | 100.0 % | [20.7 %; 100.0 %] | 18.5 | 18.5 | 0 |
| S2 | 1 | 0 | 0.0 % | [0.0 %; 79.3 %] | — | — | 0 |
| S3 | 1 | 1 | 100.0 % | [20.7 %; 100.0 %] | 491.6 | 491.6 | 0 |
| S4 | 1 | 0 | 0.0 % | [0.0 %; 79.3 %] | — | — | 0 |
| S5 | 1 | 1 | 100.0 % | [20.7 %; 100.0 %] | 487.5 | 487.5 | 0 |
| S6 | 1 | 1 | 100.0 % | [20.7 %; 100.0 %] | 1.5 | 1.5 | 0 |

Tiempo hasta la entrega = max(visible en pantalla, `READ`) − vuelta de la conexión (en S0, − t₀; en S4, − apertura de la página nueva).

## Camino de entrega

| Escenario | sse | history | retry_sse | sin llegada |
|---|--:|--:|--:|--:|
| S0 | 1 | 0 | 0 | 0 |
| S1a | 0 | 1 | 0 | 0 |
| S1b | 0 | 1 | 0 | 0 |
| S2 | 0 | 0 | 0 | 1 |
| S3 | 1 | 0 | 0 | 0 |
| S4 | 0 | 0 | 0 | 1 |
| S5 | 1 | 0 | 0 | 0 |
| S6 | 0 | 1 | 0 | 0 |

## Duplicados, cobros y bloqueo

| Escenario | Dup. transporte (pruebas / eventos extra) | Dup. pantalla | Dup. BD | Cobros dobles | Violaciones de bloqueo | Control de bloqueo |
|---|---|--:|--:|--:|--:|---|
| S0 | 0 / 0 | 0 | 0 | 0 | 0 | blocked: 1 |
| S1a | 0 / 0 | 0 | 0 | 0 | 0 | blocked: 1 |
| S1b | 0 / 0 | 0 | 0 | 0 | 0 | blocked: 1 |
| S2 | 0 / 0 | 0 | 0 | 0 | 0 | blocked: 1 |
| S3 | 1 / 2 | 0 | 0 | 0 | 0 | blocked: 1 |
| S4 | 0 / 0 | 0 | 0 | 0 | 0 | blocked: 1 |
| S5 | 0 / 0 | 0 | 0 | 0 | 0 | blocked: 1 |
| S6 | 0 / 0 | 0 | 0 | 0 | 0 | blocked: 1 |

`subscription_delta` incluye el cobro de una consulta de control aceptada después de `READ`; en ese caso se revisa `notes`.

## Estado final del outbox

| Escenario | READ | PUBLISHED | PENDING | sin evento | attempt_count (mín–máx) |
|---|--:|--:|--:|--:|---|
| S0 | 1 | 0 | 0 | 0 | 1–1 |
| S1a | 1 | 0 | 0 | 0 | 1–1 |
| S1b | 1 | 0 | 0 | 0 | 2–2 |
| S2 | 0 | 0 | 1 | 0 | 5–5 |
| S3 | 1 | 0 | 0 | 0 | 3–3 |
| S4 | 0 | 0 | 1 | 0 | 5–5 |
| S5 | 1 | 0 | 0 | 0 | 1–1 |
| S6 | 1 | 0 | 0 | 0 | 1–1 |

## Tandas (S5, S6)

| Tanda | Pruebas | Entregadas | Inicio del fallo | Fin del fallo |
|---|--:|--:|---|---|
| S5-batch-1 | 1 | 1 | 1789657588098 | 1789658310312 (722.2 s) |
| S6-batch-1 | 1 | 1 | 1789658869455 | 1789658878099 (8.6 s) |

## Pruebas no entregadas

- `S2-001`: error=None, outbox=PENDING (intentos 5), visible=False, read=False
- `S4-001`: error=None, outbox=PENDING (intentos 5), visible=False, read=False
