# Inyección de fallos sobre la entrega de respuestas

Mide si la entrega *at-least-once* de las respuestas del asistente se cumple con el backend Java real cuando la
conexión falla en momentos controlados.

## Piezas

| Carpeta | Qué hace |
|---|---|
| `mock-n8n/` | Responde en `/webhook/chat-process` con la respuesta real de `alim-003` (brazo `full` de la ablación, `api/eval/runs/ablation/full.jsonl`). Demora por sesión con `POST /delay`; sin override se sortea de las 63 latencias del brazo `full` (mediana 42,5 s). `GET /hits` devuelve cada llamada con `receivedAt`, `delayMs` y `respondedAt`. |
| `fault-proxy/` | Proxy HTTP con `CONNECT`, un puerto por prueba, modos `pass`, `reset` y `blackhole` (`POST /mode` al mismo puerto). |
| `runner/` | Playwright + Node. `seed-users.mjs` crea los usuarios Premium, `services.mjs` arranca y mata el backend, `run.mjs` corre los escenarios. |
| `analyze.py` | Genera `summary.md` a partir de `results.jsonl`. |

### Semántica de `blackhole`

Modela una caída silenciosa larga, no una pausa de TCP que se recupera sola:

- Las conexiones abiertas al empezar quedan **semiabiertas**: el navegador conserva el socket y no recibe un byte
  más, ni siquiera cuando vuelve la red. El lado del backend se descarta al volver la red, como haría TCP tras 12 min
  sin ACK. Si el navegador escribe en uno de esos sockets después, recibe un reset.
- Las conexiones nuevas quedan colgadas y fallan a los 21 s (los reintentos de SYN de Windows) o al volver la red.
- Mientras dura, el backend puede seguir escribiendo en el socket: `emitter.send()` no falla, que es justo lo que
  pasa detrás de un balanceador.

`reset` destruye todos los sockets y rechaza las conexiones nuevas mientras dure.

## Montaje

Requisitos: Docker, JDK 21, Node 20+, Python 3.

```bash
docker run -d --name legalfam-fi-postgres -e POSTGRES_USER=legalfam -e POSTGRES_PASSWORD=legalfam -e POSTGRES_DB=legalfam -p 127.0.0.1:55432:5432 postgres:16-alpine
```

Aplicar `database/schema.sql` y después las migraciones de `database/` en orden de fecha.

```bash
RABBITMQ_DEFAULT_USER=legalfam RABBITMQ_DEFAULT_PASS=legalfam-local docker compose -f ../rabbitmq/docker-compose.yml -p legalfam-fi up -d
```

En esta rama `application.properties` ya apunta a esos servicios y al n8n simulado, y el correo está apagado. El JWT
se sigue leyendo del `.env` del backend.

```bash
./mvnw package -DskipTests
node experiments/fault-injection/mock-n8n/server.mjs 5690
node experiments/fault-injection/runner/services.mjs start-backend backend.log
```

Frontend (rama `fault-injection-experiment` del repo `frontend`, `.env.production` apunta a la API local):

```bash
npm run build
npx vite preview --host 127.0.0.1 --port 4173 --strictPort
```

Usuarios y dependencias del runner:

```bash
cd experiments/fault-injection/runner && npm ci && npx playwright install chromium
node seed-users.mjs 20
```

## Correr

```bash
node run.mjs --scenario S0,S1a,S1b,S2,S3,S4 --n 50 --concurrency 10 --out ../results/final
node run.mjs --scenario S5 --n 50 --concurrency 10 --out ../results/final
node run.mjs --scenario S6 --n 50 --concurrency 10 --out ../results/final
py ../analyze.py ../results/final
```

S5 y S6 afectan a todo el backend y corren solos, en tandas de `--concurrency` sesiones que comparten un único
evento de caída. `--trace-network` guarda además las peticiones del navegador en cada prueba.

## Qué mide cada prueba

- t₀ = `receivedAt + delayMs` del mock (demora fija de 20 s). Los fallos empiezan en t₀ − 5 s.
- **Entregada:** el mensaje aparece en el DOM (`[data-message-id]`) **y** su evento de outbox queda en `READ`,
  dentro de los 30 min siguientes a la vuelta de la conexión.
- **Camino:** `sse` si llegó primero por el stream en el primer intento, `retry_sse` si fue un reintento del worker,
  `history` si apareció primero al recargar el historial.
- **Duplicados:** eventos SSE con el mismo id (transporte), copias en el DOM (pantalla) y filas `ASSISTANT` (base de
  datos). **Cobros:** transacciones `CHAT_CONSUMPTION` del mensaje y descuento real de la suscripción.
- **Bloqueo:** apenas existe el evento de outbox y no está en `READ`, el runner hace `POST /chat/send` en la misma
  sesión. `blocked` es lo esperado; `violation` es un envío aceptado con la respuesta sin confirmar;
  `accepted_after_read` significa que el receipt llegó antes que la sonda y no cuenta como violación.
- **S6:** el backend se mata con `taskkill /F` en cuanto todas las sesiones de la tanda tienen su evento de outbox
  (respuesta ya persistida) y se rearranca con el mismo jar. El corte antes del commit no se prueba aquí.
