import { Box, Typography } from '@mui/material';
import type { CalendarDay, Event } from '../types';
import EventCard from './EventCard';

const WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

interface CalendarGridProps {
  days: CalendarDay[];
  onEventClick: (event: Event) => void;
}

export default function CalendarGrid({ days, onEventClick }: CalendarGridProps) {
  return (
    <Box sx={{ overflow: 'hidden', width: '100%' }}>
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(7, minmax(0, 1fr))',
          width: '100%',
        }}
      >
        {/* Weekday headers */}
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

        {/* Day cells */}
        {days.map((day) => {
          const isToday = day.is_today;
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
              {day.events.map((event) => (
                <EventCard key={event.id} event={event} onClick={onEventClick} />
              ))}
            </Box>
          );
        })}
      </Box>
    </Box>
  );
}
