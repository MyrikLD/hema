import type { Event } from '../types';

function fmtDate(dateStr: string, timeStr: string): string {
  // "2026-04-21" + "17:00:00" → "20260421T170000"
  return dateStr.replace(/-/g, '') + 'T' + timeStr.replace(/:/g, '').slice(0, 6);
}

function vevent(event: Event): string {
  const lines = [
    'BEGIN:VEVENT',
    `UID:hema-event-${event.id}@hema`,
    `DTSTART;TZID=Europe/Warsaw:${fmtDate(event.date, event.time_start)}`,
    `DTEND;TZID=Europe/Warsaw:${fmtDate(event.date, event.time_end)}`,
  ];
  if (event.weekly_id !== null) {
    lines.push('RRULE:FREQ=WEEKLY');
  }
  lines.push(`SUMMARY:${event.name}`, 'END:VEVENT');
  return lines.join('\r\n');
}

function wrap(vevents: string[]): string {
  return [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//HEMA Calendar//PL',
    'CALSCALE:GREGORIAN',
    'METHOD:PUBLISH',
    ...vevents,
    'END:VCALENDAR',
  ].join('\r\n');
}

function download(content: string, filename: string): void {
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([content], { type: 'text/calendar;charset=utf-8' }));
  a.download = filename;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 3000);
}

export function exportEvent(event: Event): void {
  download(wrap([vevent(event)]), `${event.name.replace(/\s+/g, '_')}.ics`);
}

export function exportEvents(events: Event[], filename = 'hema.ics'): void {
  download(wrap(events.map(vevent)), filename);
}
