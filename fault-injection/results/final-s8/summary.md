# Resumen — `final-s8`

Commits: frontend `a730cda`, backend `ec0fdd3`

## Entrega

| Escenario | n | Entregadas | % | IC 95 % (Wilson) | Mediana (s) | p90 (s) | Errores del runner |
|---|--:|--:|--:|---|--:|--:|--:|
| S8 | 50 | 50 | 100.0 % | [92.9 %; 100.0 %] | 301.8 | 302.9 | 0 |

Tiempo hasta la entrega = max(visible en pantalla, `READ`) − vuelta de la conexión (en S0, − t₀; en S4, − apertura de la página nueva; en S5, − caída de Rabbit, porque la respuesta llega por historial antes de que vuelva).

## Camino de entrega

| Escenario | sse | history | retry_sse | sin llegada |
|---|--:|--:|--:|--:|
| S8 | 0 | 0 | 0 | 50 |

## Duplicados, cobros y bloqueo

| Escenario | Dup. transporte (pruebas / eventos extra) | Dup. pantalla | Dup. BD | Cobros dobles | Violaciones de bloqueo | Control de bloqueo |
|---|---|--:|--:|--:|--:|---|
| S8 | 0 / 0 | 0 | 0 | 0 | 0 | not_applicable: 50 |

`subscription_delta` incluye el cobro de una consulta de control aceptada después de `READ`; en ese caso se revisa `notes`.

## Estado final del outbox

| Escenario | READ | PUBLISHED | PENDING | sin evento | attempt_count (mín–máx) |
|---|--:|--:|--:|--:|---|
| S8 | 50 | 0 | 0 | 0 | 1–1 |

## Tandas (S5, S6)

| Tanda | Pruebas | Entregadas | Inicio del fallo | Fin del fallo |
|---|--:|--:|---|---|
| S8-001 … S8-008 | 8 | 8 | 1789771901914 | 1789771912391 (10.5 s) |
| S8-009 … S8-016 | 8 | 8 | 1789772314903 | 1789772326482 (11.6 s) |
| S8-017 … S8-024 | 8 | 8 | 1789772730074 | 1789772740079 (10.0 s) |
| S8-025 … S8-032 | 8 | 8 | 1789773141958 | 1789773153487 (11.5 s) |
| S8-033 … S8-040 | 8 | 8 | 1789773556505 | 1789773566263 (9.8 s) |
| S8-041 … S8-048 | 8 | 8 | 1789773969045 | 1789773979063 (10.0 s) |
| S8-049 … S8-050 | 2 | 2 | 1789774380929 | 1789774390806 (9.9 s) |
