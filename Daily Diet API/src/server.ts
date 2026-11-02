import fastify, { FastifyReply, FastifyRequest } from 'fastify'
import cookie from '@fastify/cookie'
import { randomUUID } from 'node:crypto'
import { z, ZodError } from 'zod'
import { knex } from './database'

type User = { id: string; name: string; session_id: string }

declare module 'fastify' {
  interface FastifyRequest {
    user?: User
  }
}

const app = fastify()
app.register(cookie)

app.setErrorHandler((error, _request, reply) => {
  if (error instanceof ZodError) {
    return reply.status(400).send({ error: 'Dados inválidos', issues: error.issues })
  }
  return reply.send(error)
})

// Identifica o usuário pelo cookie sessionId
async function checkUser(request: FastifyRequest, reply: FastifyReply) {
  const sessionId = request.cookies.sessionId
  const user = sessionId
    ? await knex<User>('users').where({ session_id: sessionId }).first()
    : undefined

  if (!user) return reply.status(401).send({ error: 'Não autorizado' })
  request.user = user
}

const mealBodySchema = z.object({
  name: z.string().min(1),
  description: z.string().min(1),
  date: z.coerce.date(),
  isOnDiet: z.boolean(),
})

const idParamsSchema = z.object({ id: z.string().uuid() })

function formatMeal(meal: any) {
  return { ...meal, is_on_diet: Boolean(meal.is_on_diet) }
}

// Criar usuário
app.post('/users', async (request, reply) => {
  const { name } = z.object({ name: z.string().min(1) }).parse(request.body)
  const sessionId = randomUUID()

  await knex('users').insert({ id: randomUUID(), name, session_id: sessionId })

  reply.cookie('sessionId', sessionId, { path: '/', maxAge: 60 * 60 * 24 * 7 })
  return reply.status(201).send()
})

// Registrar refeição
app.post('/meals', { preHandler: checkUser }, async (request, reply) => {
  const { name, description, date, isOnDiet } = mealBodySchema.parse(request.body)

  await knex('meals').insert({
    id: randomUUID(),
    user_id: request.user!.id,
    name,
    description,
    date: date.toISOString(),
    is_on_diet: isOnDiet,
  })

  return reply.status(201).send()
})

// Listar todas as refeições do usuário
app.get('/meals', { preHandler: checkUser }, async (request) => {
  const meals = await knex('meals')
    .where({ user_id: request.user!.id })
    .orderBy('date', 'desc')

  return { meals: meals.map(formatMeal) }
})

// Visualizar uma refeição
app.get('/meals/:id', { preHandler: checkUser }, async (request, reply) => {
  const { id } = idParamsSchema.parse(request.params)
  const meal = await knex('meals').where({ id, user_id: request.user!.id }).first()

  if (!meal) return reply.status(404).send({ error: 'Refeição não encontrada' })
  return { meal: formatMeal(meal) }
})

// Editar refeição
app.put('/meals/:id', { preHandler: checkUser }, async (request, reply) => {
  const { id } = idParamsSchema.parse(request.params)
  const { name, description, date, isOnDiet } = mealBodySchema.parse(request.body)

  const updated = await knex('meals')
    .where({ id, user_id: request.user!.id })
    .update({ name, description, date: date.toISOString(), is_on_diet: isOnDiet })

  if (!updated) return reply.status(404).send({ error: 'Refeição não encontrada' })
  return reply.status(204).send()
})

// Apagar refeição
app.delete('/meals/:id', { preHandler: checkUser }, async (request, reply) => {
  const { id } = idParamsSchema.parse(request.params)

  const deleted = await knex('meals').where({ id, user_id: request.user!.id }).delete()

  if (!deleted) return reply.status(404).send({ error: 'Refeição não encontrada' })
  return reply.status(204).send()
})

// Métricas do usuário
app.get('/metrics', { preHandler: checkUser }, async (request) => {
  const meals = await knex('meals')
    .where({ user_id: request.user!.id })
    .orderBy('date', 'asc')

  let onDietMeals = 0
  let currentSequence = 0
  let bestOnDietSequence = 0

  for (const meal of meals) {
    if (meal.is_on_diet) {
      onDietMeals++
      currentSequence++
      bestOnDietSequence = Math.max(bestOnDietSequence, currentSequence)
    } else {
      currentSequence = 0
    }
  }

  return {
    totalMeals: meals.length,
    onDietMeals,
    offDietMeals: meals.length - onDietMeals,
    bestOnDietSequence,
  }
})

app.listen({ port: 3333 }).then(() => {
  console.log('Servidor rodando em http://localhost:3333')
})
