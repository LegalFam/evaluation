import { api, db, PASSWORD, USER_EMAIL } from './lib.mjs'

const count = Number(process.argv[2] || 20)

for (let index = 1; index <= count; index += 1) {
  const email = USER_EMAIL(index)
  const exists = await db.query('SELECT id FROM users WHERE email = $1', [email])
  if (!exists.rowCount) {
    const { status, data } = await api('/auth/signup', {
      method: 'POST',
      body: { email, password: PASSWORD, name: `Fault Injection ${index}`, phone: '999000000' },
    })
    if (status >= 300) throw new Error(`signup ${email}: ${status} ${JSON.stringify(data)}`)
  }
  await db.query('UPDATE users SET email_verified = TRUE, email_verified_at = now() WHERE email = $1', [email])
  const { rows } = await db.query('SELECT id FROM users WHERE email = $1', [email])
  const userId = rows[0].id
  const updated = await db.query(
    `UPDATE subscriptions
        SET plan_code = 'PREMIUM', status = 'ACTIVE', monthly_token_limit = 100000, remaining_tokens = 100000,
            current_period_start = now(), current_period_end = now() + interval '365 days', updated_at = now()
      WHERE user_id = $1`,
    [userId]
  )
  if (!updated.rowCount) {
    await db.query(
      `INSERT INTO subscriptions (user_id, plan_code, status, provider, current_period_start, current_period_end,
                                  monthly_token_limit, remaining_tokens, created_at, updated_at)
       VALUES ($1, 'PREMIUM', 'ACTIVE', 'FREE', now(), now() + interval '365 days', 100000, 100000, now(), now())`,
      [userId]
    )
  }
}

const { rows } = await db.query(
  `SELECT u.email, s.plan_code, s.remaining_tokens FROM users u JOIN subscriptions s ON s.user_id = u.id
    WHERE u.email LIKE 'fi-user-%' ORDER BY u.email`
)
console.table(rows)
await db.end()
