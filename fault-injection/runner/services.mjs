import { execFileSync, spawn } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import { BACKEND_DIR, EXPERIMENT_DIR, sleep } from './lib.mjs'

export const LOG_DIR = path.join(EXPERIMENT_DIR, 'results', 'logs')
export const BACKEND_JAR = path.join(BACKEND_DIR, 'target', 'backend-0.0.1-SNAPSHOT.jar')
export const RABBIT_CONTAINER = 'legalfam-rabbitmq'

const powershell = (command) =>
  execFileSync('powershell', ['-NoProfile', '-Command', command]).toString().trim()

export function backendPid() {
  const output = powershell(
    '(Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1).OwningProcess'
  )
  return output ? Number(output) : null
}

export async function waitBackendHealthy(timeoutMs = 120_000) {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    try {
      const response = await fetch('http://127.0.0.1:8080/health')
      if (response.ok) return Date.now()
    } catch {
      // todavía arrancando
    }
    await sleep(250)
  }
  throw new Error('backend did not become healthy')
}

export function startBackend(logName) {
  fs.mkdirSync(LOG_DIR, { recursive: true })
  const logFile = path.join(LOG_DIR, logName)
  const out = fs.openSync(logFile, 'a')
  const child = spawn('java', ['-jar', BACKEND_JAR], {
    cwd: BACKEND_DIR,
    detached: true,
    stdio: ['ignore', out, out],
    windowsHide: true,
  })
  child.unref()
  return logFile
}

export function killBackend() {
  const pid = backendPid()
  if (!pid) throw new Error('no backend listening on 8080')
  execFileSync('taskkill', ['/F', '/PID', String(pid)])
  return pid
}

export function stopRabbit() {
  execFileSync('docker', ['stop', RABBIT_CONTAINER])
}

export function startRabbit() {
  execFileSync('docker', ['start', RABBIT_CONTAINER])
}

export function backendLogFiles() {
  if (!fs.existsSync(LOG_DIR)) return []
  return fs
    .readdirSync(LOG_DIR)
    .filter((name) => name.startsWith('backend') && name.endsWith('.log'))
    .map((name) => path.join(LOG_DIR, name))
}

if (process.argv[1]?.endsWith('services.mjs')) {
  const [command, arg] = process.argv.slice(2)
  if (command === 'start-backend') {
    const logFile = startBackend(arg || 'backend.log')
    await waitBackendHealthy()
    console.log(`backend healthy pid=${backendPid()} log=${logFile}`)
  } else if (command === 'kill-backend') {
    console.log(`killed pid=${killBackend()}`)
  }
}
