import { Box, Typography } from '@mui/material';
import type { CalendarDay, Event } from '../types';
import EventCard from './EventCard';

const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const MAX_VISIBLE_EVENTS = { xs: 2, sm: 3, md: 4 };

interface CalendarGridProps {
  days: CalendarDay[];
  onEventClick: (event: Event) => void;
}

export default function CalendarGrid({ days, onEventClick }: CalendarGridProps) {
  return (
    <Box sx={{ overflow: 'hidden' }}>
      {/* Weekday headers */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(7, 1fr)',
          gap: 0,
        }}
      >
        {WEEKDAYS.map((d) => (
          <Box
            key={d}
            sx={{
              textAlign: 'center',
              py: 0.5,
              fontWeight: 600,
              fontSize: '0.75rem',
              color: 'text.secondary',
              borderBottom: '1px solid',
              borderColor: 'divider',
              minWidth: 0,
            }}
          >
            {d}
          </Box>
        ))}
      </Box>

      {/* Day cells */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(7, minmax(0, 1fr))',
          gap: 0,
        }}
      >
        {days.map((day) => {
          const isToday = day.is_today;
          const hiddenCount = {
            xs: Math.max(0, day.events.length - MAX_VISIBLE_EVENTS.xs),
            sm: Math.max(0, day.events.length - MAX_VISIBLE_EVENTS.sm),
            md: Math.max(0, day.events.length - MAX_VISIBLE_EVENTS.md),
          };
          return (
            <Box
              key={day.date}
              sx={{
                minHeight: { xs: 52, sm: 80, md: 100 },
                borderBottom: '1px solid',
                borderRight: '1px solid',
                borderColor: 'divider',
                p: 0.5,
                opacity: day.is_current_month ? 1 : 0.4,
                backgroundColor: isToday ? 'action.selected' : 'transparent',
                minWidth: 0,
                overflow: 'hidden',
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  fontWeight: isToday ? 700 : 400,
                  display: 'block',
                  textAlign: 'right',
                  mb: 0.25,
                  fontSize: '0.7rem',
                }}
              >
                {new Date(day.date + 'T00:00:00').getDate()}
              </Typography>
              {day.events.map((event, idx) => (
                <Box
                  key={event.id}
                  sx={{
                    display: {
                      xs: idx < MAX_VISIBLE_EVENTS.xs ? 'block' : 'none',
                      sm: idx < MAX_VISIBLE_EVENTS.sm ? 'block' : 'none',
                      md: idx < MAX_VISIBLE_EVENTS.md ? 'block' : 'none',
                    },
                  }}
                >
                  <EventCard event={event} onClick={onEventClick} />
                </Box>
              ))}
              {/* "+N more" label, responsive per breakpoint */}
              {hiddenCount.md > 0 && (
                <Typography
                  variant="caption"
                  sx={{
                    fontSize: '0.65rem',
                    color: 'text.secondary',
                    display: { xs: 'none', md: 'block' },
                    textAlign: 'center',
                  }}
                >
                  +{hiddenCount.md} more
                </Typography>
              )}
              {hiddenCount.sm > 0 && (
                <Typography
                  variant="caption"
                  sx={{
                    fontSize: '0.65rem',
                    color: 'text.secondary',
                    display: { xs: 'none', sm: 'block', md: 'none' },
                    textAlign: 'center',
                  }}
                >
                  +{hiddenCount.sm} more
                </Typography>
              )}
              {hiddenCount.xs > 0 && (
                <Typography
                  variant="caption"
                  sx={{
                    fontSize: '0.65rem',
                    color: 'text.secondary',
                    display: { xs: 'block', sm: 'none' },
                    textAlign: 'center',
                  }}
                >
                  +{hiddenCount.xs} more
                </Typography>
              )}
            </Box>
          );
        })}
      </Box>
    </Box>
  );
}
