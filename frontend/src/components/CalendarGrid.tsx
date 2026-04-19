import { Box, Typography } from '@mui/material';
import type { Event } from '../types';

const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const PX_PER_MIN = 1;
const TIME_GUTTER_W = 44;
const DEFAULT_START = 8 * 60;
const DEFAULT_END = 22 * 60;

function timeToMin(t: string): number {
  const [h, m] = t.split(':').map(Number);
  return h * 60 + m;
}

function toPx(min: number, base: number): number {
  return (min - base) * PX_PER_MIN;
}

function fmtMin(min: number): string {
  return `${Math.floor(min / 60)}:${String(min % 60).padStart(2, '0')}`;
}

function isLightColor(hex: string): boolean {
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  return (r * 299 + g * 587 + b * 114) / 1000 > 150;
}

function addDays(d: Date, n: number): Date {
  return new Date(d.getFullYear(), d.getMonth(), d.getDate() + n);
}

function toISODate(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

interface CalendarGridProps {
  events: Event[];
  weekStart: Date;
  onEventClick: (event: Event) => void;
}

export default function CalendarGrid({ events, weekStart, onEventClick }: CalendarGridProps) {
  const days = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));
  const todayStr = toISODate(new Date());

  const allMins = events.flatMap(e => [timeToMin(e.time_start), timeToMin(e.time_end)]);
  const rangeStart = allMins.length > 0 ? Math.min(...allMins) : DEFAULT_START;
  const rangeEnd = allMins.length > 0 ? Math.max(...allMins) : DEFAULT_END;
  const totalHeight = toPx(rangeEnd, rangeStart);

  const firstHour = Math.ceil(rangeStart / 60) * 60;
  const hours: number[] = [];
  for (let m = firstHour; m < rangeEnd; m += 60) {
    if (m !== rangeStart) hours.push(m); // не дублировать standalone-лейбл начала
  }

  const byDate = new Map<string, Event[]>(days.map(d => [toISODate(d), []]));
  events.forEach(e => byDate.get(e.date)?.push(e));

  return (
    <Box data-print="calendar" sx={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch' }}>
      <Box sx={{ minWidth: 360 }}>

        {/* Day headers */}
        <Box
          sx={{
            display: 'flex',
            bgcolor: 'grey.100',
            borderBottom: '2px solid',
            borderColor: 'divider',
            position: 'sticky',
            top: 0,
            zIndex: 10,
          }}
        >
          <Box sx={{ width: TIME_GUTTER_W, minWidth: TIME_GUTTER_W, borderRight: '1px solid', borderColor: 'divider' }} />
          {days.map((d, i) => {
            const isToday = toISODate(d) === todayStr;
            return (
              <Box
                key={i}
                sx={{
                  flex: 1,
                  textAlign: 'center',
                  py: 0.75,
                  borderLeft: '1px solid',
                  borderColor: 'divider',
                  bgcolor: isToday ? '#dbeafe' : undefined,
                  lineHeight: 1.3,
                }}
              >
                <Typography sx={{ fontSize: '0.6rem', fontWeight: 700, color: isToday ? 'primary.main' : 'text.secondary', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                  {WEEKDAYS[i]}
                </Typography>
                <Typography sx={{ fontSize: '0.85rem', fontWeight: isToday ? 700 : 500, color: isToday ? 'primary.main' : 'text.primary' }}>
                  {d.getDate()}
                </Typography>
              </Box>
            );
          })}
        </Box>

        {/* Time grid */}
        <Box sx={{ display: 'flex' }}>

          {/* Time gutter */}
          <Box
            sx={{
              width: TIME_GUTTER_W,
              minWidth: TIME_GUTTER_W,
              position: 'relative',
              height: totalHeight,
              borderRight: '1px solid',
              borderColor: 'divider',
            }}
          >
            <Box sx={{ position: 'absolute', top: 0, right: 5, fontSize: '0.55rem', fontWeight: 600, color: 'text.secondary', lineHeight: 1 }}>
              {fmtMin(rangeStart)}
            </Box>
            {hours.map(m => (
              <Box
                key={m}
                sx={{
                  position: 'absolute',
                  top: toPx(m, rangeStart),
                  right: 5,
                  fontSize: '0.55rem',
                  fontWeight: 600,
                  color: 'text.secondary',
                  transform: 'translateY(-50%)',
                  lineHeight: 1,
                  pointerEvents: 'none',
                }}
              >
                {fmtMin(m)}
              </Box>
            ))}
            <Box sx={{ position: 'absolute', top: totalHeight, right: 5, fontSize: '0.55rem', fontWeight: 600, color: 'text.secondary', transform: 'translateY(-100%)', lineHeight: 1 }}>
              {fmtMin(rangeEnd)}
            </Box>
          </Box>

          {/* Day columns */}
          {days.map((d, i) => {
            const dateStr = toISODate(d);
            const isToday = dateStr === todayStr;
            const dayEvents = [...(byDate.get(dateStr) ?? [])].sort(
              (a, b) => timeToMin(a.time_start) - timeToMin(b.time_start),
            );

            const gaps: { start: number; end: number }[] = [];
            for (let j = 0; j < dayEvents.length - 1; j++) {
              const gapStart = timeToMin(dayEvents[j].time_end);
              const gapEnd   = timeToMin(dayEvents[j + 1].time_start);
              if (gapEnd - gapStart >= 5) gaps.push({ start: gapStart, end: gapEnd });
            }

            return (
              <Box
                key={i}
                sx={{
                  flex: 1,
                  minWidth: 0,
                  position: 'relative',
                  height: totalHeight,
                  borderLeft: '1px solid',
                  borderColor: 'divider',
                  bgcolor: isToday ? '#eff6ff' : undefined,
                }}
              >
                {hours.map(m => (
                  <Box
                    key={m}
                    sx={{
                      position: 'absolute',
                      left: 0,
                      right: 0,
                      top: toPx(m, rangeStart),
                      height: '1px',
                      bgcolor: 'divider',
                      pointerEvents: 'none',
                    }}
                  />
                ))}

                {/* Gap indicators */}
                {gaps.map(g => {
                  const top    = toPx(g.start, rangeStart);
                  const height = (g.end - g.start) * PX_PER_MIN;
                  return (
                    <Box
                      key={`gap-${g.start}`}
                      sx={{
                        position: 'absolute',
                        top,
                        height,
                        left: 2,
                        right: 2,
                        borderRadius: '3px',
                        border: '1px dashed',
                        borderColor: 'divider',
                        background: 'repeating-linear-gradient(45deg, transparent, transparent 3px, rgba(0,0,0,0.03) 3px, rgba(0,0,0,0.03) 6px)',
                        pointerEvents: 'none',
                        zIndex: 1,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      {height >= 18 && (
                        <Typography sx={{ fontSize: '0.5rem', color: 'text.disabled', fontStyle: 'italic', pointerEvents: 'none' }}>
                          перерыв
                        </Typography>
                      )}
                    </Box>
                  );
                })}

                {/* Events */}
                {dayEvents.map(event => {
                  const startMin = timeToMin(event.time_start);
                  const endMin = timeToMin(event.time_end);
                  const top = toPx(startMin, rangeStart);
                  const height = (endMin - startMin) * PX_PER_MIN;
                  const textColor = isLightColor(event.color) ? '#111827' : '#fff';
                  const tiny = height < 32;

                  return (
                    <Box
                      key={event.id}
                      onClick={() => onEventClick(event)}
                      title={`${event.name}\n${event.time_start.slice(0, 5)}–${event.time_end.slice(0, 5)}`}
                      sx={{
                        position: 'absolute',
                        top,
                        height,
                        left: 2,
                        right: 2,
                        borderRadius: '5px',
                        bgcolor: `#${event.color}`,
                        color: textColor,
                        px: '5px',
                        py: '3px',
                        overflow: 'hidden',
                        boxShadow: '0 1px 4px rgba(0,0,0,0.1), 0 0 0 1px rgba(0,0,0,0.06)',
                        cursor: 'pointer',
                        zIndex: 2,
                        transition: 'box-shadow 0.1s, transform 0.1s',
                        '&:hover': {
                          boxShadow: '0 3px 10px rgba(0,0,0,0.15)',
                          transform: 'translateX(-1px)',
                          zIndex: 5,
                        },
                      }}
                    >
                      <Typography sx={{ fontSize: '0.58rem', fontWeight: 700, lineHeight: 1.15, color: 'inherit' }}>
                        {event.time_start.slice(0, 5)}–{event.time_end.slice(0, 5)}
                      </Typography>
                      {!tiny && (
                        <Typography sx={{ fontSize: '0.62rem', fontWeight: 600, lineHeight: 1.2, color: 'inherit', letterSpacing: '0.01em' }}>
                          {event.name}
                        </Typography>
                      )}
                      {!tiny && event.trainer_name && (
                        <Typography sx={{ fontSize: '0.55rem', fontWeight: 500, lineHeight: 1.2, color: 'inherit', opacity: 0.65, mt: '2px', display: 'flex', alignItems: 'center', gap: '2px' }}>
                          {'👤 '}{event.trainer_name}
                        </Typography>
                      )}
                    </Box>
                  );
                })}
              </Box>
            );
          })}
        </Box>
      </Box>
    </Box>
  );
}
