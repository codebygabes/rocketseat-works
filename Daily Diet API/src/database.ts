import setupKnex from 'knex'
import type { Knex } from 'knex'
import { fileURLToPath } from 'node:url'

// Caminhos absolutos, para funcionar tanto no servidor quanto no CLI do knex
const dbFolder = fileURLToPath(new URL('../db', import.meta.url))

export const config: Knex.Config = {
  client: 'better-sqlite3',
  connection: { filename: `${dbFolder}/app.db` },
  useNullAsDefault: true,
  migrations: {
    extension: 'ts',
    directory: `${dbFolder}/migrations`,
  },
}

export const knex = setupKnex(config)

export default config
