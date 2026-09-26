import pg from 'pg'
import { execFileSync } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

export const EXPERIMENT_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
export const BACKEND_DIR = path.resolve(EXPERIMENT_DIR, '..', '..')
export const FRONTEND_DIR = path.resolve(BACKEND_DIR, '..', 'frontend')

export const API_URL = 'http://127.0.0.1:8080/api/v1'
export const FRONTEND_URL = 'http://127.0.0.1:4173'
export const MOCK_URL = 'http://127.0.0.1:5690'
export const PASSWORD = 'fault-injection-2026'
export const USER_EMAIL = (index) => `fi-user-${String(index).padStart(3, '0')}@legalfam.test`
export const QUESTION = 'Si el padre de mi hija no puede pagar la pensión de alimentos, ¿quién más está obligado a pagarla?'

export const MINUTE = 60_000
export const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

export const db = new pg.Pool({
  host: '127.0.0.1',
  port: 55432,
  user: 'legalfam',
  password: 'legalfam',
  database: 'legalfam',
  max: 20,
})

export async function api(pathname, { method = 'GET', token, body } = {}) {
  const response = await fetch(`${API_URL}${pathname}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  const text = await response.text()
  let data = null
  try {
    data = text ? JSON.parse(text) : null
  } catch {
    data = text
  }
  return { status: response.status, data }
}

export async function login(email) {
  const { status, data } = await api('/auth/login', { method: 'POST', body: { email, password: PASSWORD } })
  if (status !== 200) throw new Error(`login ${email} failed: ${status} ${JSON.stringify(data)}`)
  const me = await api('/users/me', { token: data.accessToken })
  return { accessToken: data.accessToken, refreshToken: data.refreshToken, user: me.data }
}

export async function gitCommit(repoDir) {
  return execFileSync('git', ['-C', repoDir, 'rev-parse', '--short', 'HEAD']).toString().trim()
}

export async function gitDirty(repoDir) {
  return execFileSync('git', ['-C', repoDir, 'status', '--porcelain', '--untracked-files=no', '--', '.', ':!experiments']).toString().trim().length > 0
}

export async function mockHits(sessionId) {
  const response = await fetch(`${MOCK_URL}/hits?sessionId=${sessionId}`)
  return response.json()
}

export async function setProxyMode(port, mode) {
  const response = await fetch(`http://127.0.0.1:${port}/mode`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode }),
  })
  if (!response.ok) throw new Error(`proxy ${port} mode ${mode} failed`)
}
