import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const here = path.dirname(fileURLToPath(import.meta.url))
const port = Number(process.argv[2] || 5690)
const fixedDelayArg = process.argv.find((arg) => arg.startsWith('--delay-ms='))
const defaultDelayMs = fixedDelayArg ? Number(fixedDelayArg.split('=')[1]) : null

const responseBody = fs.readFileSync(path.join(here, 'alim-003.response.json'), 'utf8')
const latencies = JSON.parse(fs.readFileSync(path.join(here, 'full-latencies-ms.json'), 'utf8'))
const hits = []

const sampleLatency = () => latencies[Math.floor(Math.random() * latencies.length)]

const readBody = (req) =>
  new Promise((resolve) => {
    const chunks = []
    req.on('data', (chunk) => chunks.push(chunk))
    req.on('end', () => resolve(Buffer.concat(chunks).toString('utf8')))
  })

const sendJson = (res, status, body) => {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8' })
  res.end(typeof body === 'string' ? body : JSON.stringify(body))
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`)

  if (req.method === 'GET' && url.pathname === '/hits') {
    const sessionId = url.searchParams.get('sessionId')
    return sendJson(res, 200, sessionId ? hits.filter((hit) => hit.sessionId === sessionId) : hits)
  }

  if (req.method === 'POST' && url.pathname === '/delay') {
    const { sessionId, delayMs, respondAt } = JSON.parse((await readBody(req)) || '{}')
    delayOverrides.set(sessionId, respondAt ? { respondAt: Number(respondAt) } : { delayMs: Number(delayMs) })
    return sendJson(res, 200, { ok: true })
  }

  if (req.method === 'POST' && url.pathname === '/fail') {
    const { sessionId } = JSON.parse((await readBody(req)) || '{}')
    failingSessions.add(sessionId)
    return sendJson(res, 200, { ok: true })
  }

  if (req.method === 'POST' && url.pathname === '/webhook/chat-process') {
    const payload = JSON.parse((await readBody(req)) || '{}')
    const sessionId = payload.session_id
    const receivedAt = Date.now()
    const override = delayOverrides.get(sessionId)
    const delayMs = override?.respondAt
      ? Math.max(0, override.respondAt - receivedAt)
      : override?.delayMs ?? defaultDelayMs ?? sampleLatency()
    const hit = { sessionId, receivedAt, delayMs, respondedAt: null, aborted: false }
    hits.push(hit)
    const timer = setTimeout(() => {
      hit.respondedAt = Date.now()
      if (failingSessions.has(sessionId)) {
        hit.failed = true
        return sendJson(res, 500, { code: 'upstream_unavailable', message: 'mock agent failure' })
      }
      return sendJson(res, 200, responseBody)
    }, delayMs)
    req.socket.on('close', () => {
      if (hit.respondedAt === null) {
        clearTimeout(timer)
        hit.aborted = true
      }
    })
    return undefined
  }

  return sendJson(res, 404, { error: 'not_found' })
})

const delayOverrides = new Map()
const failingSessions = new Set()

server.listen(port, '127.0.0.1', () => {
  console.log(`mock-n8n listening on http://127.0.0.1:${port} delay=${defaultDelayMs ?? 'sampled'}`)
})
