import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import type { Interview, Analysis, SecurityScan } from '@/types';
import { formatDateTime } from '@/lib/utils';

export function exportInterviewPDF(interview: Interview) {
  const doc = new jsPDF();
  
  // Title
  doc.setFontSize(20);
  doc.text('Interview Report', 20, 20);
  
  // Metadata
  doc.setFontSize(12);
  doc.text(`Title: ${interview.title}`, 20, 35);
  doc.text(`Status: ${interview.status}`, 20, 45);
  doc.text(`Created: ${formatDateTime(interview.createdAt)}`, 20, 55);
  
  // Responses table
  const tableData = interview.responses.map((r) => [
    r.category,
    r.question,
    r.answer,
  ]);
  
  autoTable(doc, {
    head: [['Category', 'Question', 'Answer']],
    body: tableData,
    startY: 65,
    styles: { fontSize: 10 },
    columnStyles: {
      0: { cellWidth: 30 },
      1: { cellWidth: 60 },
      2: { cellWidth: 90 },
    },
  });
  
  doc.save(`interview-${interview.id}.pdf`);
}

export function exportAnalysisPDF(analysis: Analysis, interview: Interview) {
  const doc = new jsPDF();
  
  // Title
  doc.setFontSize(20);
  doc.text('Workflow Analysis Report', 20, 20);
  
  // Interview info
  doc.setFontSize(12);
  doc.text(`Interview: ${interview.title}`, 20, 35);
  doc.text(`Analysis Date: ${formatDateTime(analysis.createdAt)}`, 20, 45);
  
  // Bottlenecks
  doc.setFontSize(16);
  doc.text('Identified Bottlenecks', 20, 60);
  
  const bottleneckData = analysis.bottlenecks.map((b) => [
    b.name,
    b.severity,
    b.description,
    b.impact,
  ]);
  
  autoTable(doc, {
    head: [['Name', 'Severity', 'Description', 'Impact']],
    body: bottleneckData,
    startY: 70,
    styles: { fontSize: 9 },
  });
  
  // Opportunities
  const finalY = (doc as any).lastAutoTable.finalY || 70;
  doc.setFontSize(16);
  doc.text('Automation Opportunities', 20, finalY + 15);
  
  const opportunityData = analysis.opportunities.map((o) => [
    o.name,
    o.impact,
    o.effort,
    o.description,
  ]);
  
  autoTable(doc, {
    head: [['Opportunity', 'Impact', 'Effort', 'Description']],
    body: opportunityData,
    startY: finalY + 25,
    styles: { fontSize: 9 },
  });
  
  doc.save(`analysis-${analysis.id}.pdf`);
}

export function exportSecurityReportPDF(scan: SecurityScan) {
  const doc = new jsPDF();
  
  // Title
  doc.setFontSize(20);
  doc.text('Security Scan Report', 20, 20);
  
  // Metadata
  doc.setFontSize(12);
  doc.text(`Language: ${scan.language}`, 20, 35);
  doc.text(`Overall Severity: ${scan.severity}`, 20, 45);
  doc.text(`Scan Date: ${formatDateTime(scan.createdAt)}`, 20, 55);
  
  // Vulnerabilities
  doc.setFontSize(16);
  doc.text('Vulnerabilities Found', 20, 70);
  
  const vulnData = scan.vulnerabilities.map((v) => [
    v.type,
    v.severity,
    v.cwe || 'N/A',
    v.owasp || 'N/A',
    v.description,
  ]);
  
  autoTable(doc, {
    head: [['Type', 'Severity', 'CWE', 'OWASP', 'Description']],
    body: vulnData,
    startY: 80,
    styles: { fontSize: 8 },
    columnStyles: {
      4: { cellWidth: 70 },
    },
  });
  
  doc.save(`security-scan-${scan.id}.pdf`);
}
