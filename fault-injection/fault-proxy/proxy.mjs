import http from 'node:http'
import net from 'node:net'

const CONNECT_TIMEOUT_MS = 21000

export function startFaultProxy(port, { log = () => {} } = {}) {
  let mode = 'pass'
  const clientSockets = new Set()
  const upstreamSockets = new Set()
  const pendingDuringBlackhole = new Set()

  const track = (set, socket) => {
    set.add(socket)
    socket.on('close', () => set.delete(socket))
  }

  const muteClientSocket = (socket) => {
    socket.faultZombie = true
    socket.pause()
    socket.removeAllListeners('data')
    socket.on('data', () => socket.destroy())
  }

  const enterBlackhole = () => {
    for (const socket of clientSockets) {
      socket.faultZombie = true
      socket.faultMuted = true
    }
    for (const socket of upstreamSockets) {
      socket.pause()
      socket.faultMuted = true
    }
  }

  const leaveBlackhole = () => {
    for (const socket of upstreamSockets) {
      if (socket.faultMuted) socket.destroy()
    }
    for (const socket of clientSockets) {
      if (socket.faultMuted) muteClientSocket(socket)
    }
    for (const socket of pendingDuringBlackhole) socket.destroy()
    pendingDuringBlackhole.clear()
  }

  const resetAll = () => {
    for (const socket of [...clientSockets, ...upstreamSockets]) socket.destroy()
  }

  const setMode = (next) => {
    if (next === mode) return
    if (mode === 'blackhole' && next !== 'blackhole') leaveBlackhole()
    if (next === 'blackhole') enterBlackhole()
    if (next === 'reset') resetAll()
    mode = next
    log({ ev: 'mode', port, mode, t: Date.now() })
  }

  const holdUntilNetworkReturns = (socket) => {
    pendingDuringBlackhole.add(socket)
    socket.pause()
    setTimeout(() => {
      pendingDuringBlackhole.delete(socket)
      socket.destroy()
    }, CONNECT_TIMEOUT_MS)
  }

  const handleControl = (req, res) => {
    const chunks = []
    req.on('data', (chunk) => chunks.push(chunk))
    req.on('end', () => {
      if (req.method === 'POST' && req.url === '/mode') {
        const body = JSON.parse(Buffer.concat(chunks).toString('utf8') || '{}')
        if (!['pass', 'reset', 'blackhole'].includes(body.mode)) {
          res.writeHead(400).end()
          return
        }
        setMode(body.mode)
      }
      res.writeHead(200, { 'Content-Type': 'application/json', Connection: 'close' })
      res.end(JSON.stringify({ port, mode }))
    })
  }

  const forwardHttp = (req, res) => {
    const socket = req.socket
    if (mode === 'blackhole') {
      holdUntilNetworkReturns(socket)
      return
    }
    if (socket.faultZombie) {
      socket.destroy()
      return
    }
    const target = new URL(req.url)
    const upstreamReq = http.request({
      host: target.hostname,
      port: target.port || 80,
      method: req.method,
      path: `${target.pathname}${target.search}`,
      headers: req.headers,
      agent: false,
    })
    upstreamReq.on('socket', (upstreamSocket) => track(upstreamSockets, upstreamSocket))
    upstreamReq.on('response', (upstreamRes) => {
      if (socket.faultMuted || socket.destroyed) return
      res.writeHead(upstreamRes.statusCode, upstreamRes.headers)
      upstreamRes.on('data', (chunk) => {
        if (!socket.faultMuted) res.write(chunk)
      })
      upstreamRes.on('end', () => {
        if (!socket.faultMuted) res.end()
      })
    })
    upstreamReq.on('error', () => {
      if (!socket.faultMuted) socket.destroy()
    })
    res.on('close', () => upstreamReq.destroy())
    req.pipe(upstreamReq)
  }

  const server = http.createServer((req, res) => {
    if (req.url.startsWith('/')) return handleControl(req, res)
    return forwardHttp(req, res)
  })

  server.on('connection', (socket) => {
    if (mode === 'reset') {
      socket.destroy()
      return
    }
    track(clientSockets, socket)
    if (mode === 'blackhole') holdUntilNetworkReturns(socket)
  })

  server.on('connect', (req, clientSocket, head) => {
    if (clientSocket.faultZombie) {
      clientSocket.destroy()
      return
    }
    const [host, targetPort] = req.url.split(':')
    const upstream = net.connect(Number(targetPort) || 443, host, () => {
      clientSocket.write('HTTP/1.1 200 Connection Established\r\n\r\n')
      if (head?.length) upstream.write(head)
      clientSocket.on('data', (chunk) => {
        if (!clientSocket.faultMuted) upstream.write(chunk)
        else if (mode === 'blackhole') holdUntilNetworkReturns(clientSocket)
      })
      upstream.on('data', (chunk) => {
        if (!clientSocket.faultMuted) clientSocket.write(chunk)
      })
    })
    track(upstreamSockets, upstream)
    upstream.on('error', () => clientSocket.faultMuted || clientSocket.destroy())
    upstream.on('close', () => clientSocket.faultMuted || clientSocket.destroy())
    clientSocket.on('error', () => upstream.destroy())
    clientSocket.on('close', () => upstream.destroy())
  })

  server.keepAliveTimeout = 0
  return new Promise((resolve) => {
    server.listen(port, '127.0.0.1', () =>
      resolve({
        port,
        setMode,
        getMode: () => mode,
        close: () => {
          resetAll()
          server.close()
        },
      })
    )
  })
}

const isMain = process.argv[1] && import.meta.url.endsWith(process.argv[1].replace(/\\/g, '/'))
if (isMain) {
  const ports = process.argv.slice(2).map(Number)
  for (const port of ports) {
    await startFaultProxy(port, { log: (entry) => console.log(JSON.stringify(entry)) })
    console.log(`fault-proxy listening on 127.0.0.1:${port}`)
  }
}
