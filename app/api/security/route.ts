import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/db/prisma';
import { GeminiService } from '@/lib/gemini/service';

// POST /api/security/scan - Run security scan
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { codeSnippet, language } = body;

    if (!codeSnippet || !language) {
      return NextResponse.json(
        { error: 'Code snippet and language are required' },
        { status: 400 }
      );
    }

    // Scan code using Gemini
    const apiKey = process.env.GEMINI_API_KEY;
    if (!apiKey) {
      return NextResponse.json(
        { error: 'Gemini API key not configured' },
        { status: 500 }
      );
    }

    const gemini = new GeminiService(apiKey);
    const scanResult = await gemini.scanForVulnerabilities(codeSnippet, language);

    // Save scan results
    const scan = await prisma.securityScan.create({
      data: {
        codeSnippet,
        language,
        vulnerabilities: JSON.stringify(scanResult.vulnerabilities),
        severity: scanResult.severity,
        owaspMappings: JSON.stringify(scanResult.owaspMappings),
      },
    });

    return NextResponse.json({
      ...scan,
      vulnerabilities: JSON.parse(scan.vulnerabilities),
      owaspMappings: JSON.parse(scan.owaspMappings),
    });
  } catch (error) {
    console.error('Error scanning code:', error);
    return NextResponse.json(
      { error: 'Failed to scan code' },
      { status: 500 }
    );
  }
}
