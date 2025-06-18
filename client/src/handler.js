import { PrismaClient } from '@prisma/client'
const prisma = new PrismaClient()

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' })
  }

  const { userId, homeId } = req.body

  if (!userId || !homeId) {
    return res.status(400).json({ error: "Missing userId or homeId" })
  }

  try {
    await prisma.recentlyViewed.upsert({
      where: {
        userId_homeId: {
          userId,
          homeId,
        },
      },
      update: {
        viewedAt: new Date(),
      },
      create: {
        userId,
        homeId,
      },
    })

    res.status(200).json({ message: "Viewed home logged" })
  } catch (error) {
    console.error(error)
    res.status(500).json({ error: "Internal Server Error" })
  }
}
