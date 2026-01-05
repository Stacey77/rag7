import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/db/prisma';

// GET /api/contexts - List all context templates
export async function GET(request: NextRequest) {
  try {
    const templates = await prisma.contextTemplate.findMany({
      orderBy: { createdAt: 'desc' },
    });

    return NextResponse.json(templates);
  } catch (error) {
    console.error('Error fetching context templates:', error);
    return NextResponse.json(
      { error: 'Failed to fetch templates' },
      { status: 500 }
    );
  }
}

// POST /api/contexts - Create new context template
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, description, role, domain, context, tone, constraints, userId } = body;

    if (!name || !role || !domain || !context || !tone) {
      return NextResponse.json(
        { error: 'Required fields are missing' },
        { status: 400 }
      );
    }

    const template = await prisma.contextTemplate.create({
      data: {
        name,
        description: description || '',
        role,
        domain,
        context,
        tone,
        constraints: typeof constraints === 'string' ? constraints : JSON.stringify(constraints),
        userId,
      },
    });

    return NextResponse.json(template);
  } catch (error) {
    console.error('Error creating context template:', error);
    return NextResponse.json(
      { error: 'Failed to create template' },
      { status: 500 }
    );
  }
}
