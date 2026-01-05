import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/db/prisma';
import { GeminiService } from '@/lib/gemini/service';

// POST /api/analysis - Generate analysis from interview
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { interviewId } = body;

    if (!interviewId) {
      return NextResponse.json(
        { error: 'Interview ID is required' },
        { status: 400 }
      );
    }

    // Fetch interview
    const interview = await prisma.interview.findUnique({
      where: { id: interviewId },
    });

    if (!interview) {
      return NextResponse.json(
        { error: 'Interview not found' },
        { status: 404 }
      );
    }

    const responses = JSON.parse(interview.responses);

    // Generate analysis using Gemini
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      return NextResponse.json(
        { error: 'Gemini API key not configured' },
        { status: 500 }
      );
    }

    const gemini = new GeminiService(apiKey);
    const analysisResult = await gemini.analyzeWorkflow(responses);
    
    // Generate roadmap
    const roadmap = await gemini.generateRoadmap(analysisResult.opportunities);

    // Save analysis
    const analysis = await prisma.analysis.create({
      data: {
        interviewId,
        bottlenecks: JSON.stringify(analysisResult.bottlenecks),
        opportunities: JSON.stringify(analysisResult.opportunities),
        roadmap: JSON.stringify(roadmap),
      },
    });

    return NextResponse.json({
      ...analysis,
      bottlenecks: JSON.parse(analysis.bottlenecks),
      opportunities: JSON.parse(analysis.opportunities),
      roadmap: JSON.parse(analysis.roadmap),
    });
  } catch (error) {
    console.error('Error generating analysis:', error);
    return NextResponse.json(
      { error: 'Failed to generate analysis' },
      { status: 500 }
    );
  }
}
