import type { Interview, Analysis, RoadmapPhase } from '@/types';

export function exportInterviewCSV(interview: Interview): string {
  const headers = ['Category', 'Question', 'Answer'];
  const rows = interview.responses.map((r) => [
    escapeCSV(r.category),
    escapeCSV(r.question),
    escapeCSV(r.answer),
  ]);
  
  return [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
}

export function exportRoadmapCSV(roadmap: RoadmapPhase[]): string {
  const headers = ['Phase', 'Name', 'Duration', 'Items', 'Considerations'];
  const rows = roadmap.map((phase) => [
    phase.phase.toString(),
    escapeCSV(phase.name),
    escapeCSV(phase.duration),
    escapeCSV(phase.items.join('; ')),
    escapeCSV(phase.considerations.join('; ')),
  ]);
  
  return [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
}

export function downloadCSV(content: string, filename: string) {
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function escapeCSV(value: string): string {
  if (value.includes(',') || value.includes('"') || value.includes('\n')) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}
