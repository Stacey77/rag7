import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/db/prisma';

// GET /api/interviews - List all interviews
export async function GET(request: NextRequest) {
  try {
    const interviews = await prisma.interview.findMany({
      orderBy: { createdAt: 'desc' },
      include: {
        analyses: true,
      },
    });

    const formattedInterviews = interviews.map((interview) => ({
      ...interview,
      responses: JSON.parse(interview.responses),
    }));

    return NextResponse.json(formattedInterviews);
  } catch (error) {
    console.error('Error fetching interviews:', error);
    return NextResponse.json(
      { error: 'Failed to fetch interviews' },
      { status: 500 }
    );
  }
}

// POST /api/interviews - Create new interview
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { title, responses, status = 'draft', userId } = body;

    if (!title || !responses) {
      return NextResponse.json(
        { error: 'Title and responses are required' },
        { status: 400 }
      );
    }

    const interview = await prisma.interview.create({
      data: {
        title,
        responses: JSON.stringify(responses),
        status,
        userId,
      },
    });

    return NextResponse.json({
      ...interview,
      responses: JSON.parse(interview.responses),
    });
  } catch (error) {
    console.error('Error creating interview:', error);
    return NextResponse.json(
      { error: 'Failed to create interview' },
      { status: 500 }
    );
  }
}
