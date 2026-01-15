'use client';

import { useState } from 'react';
import { CalendarDay as CalendarDayType } from '@/types/calendar';
import { Event } from '@/types/event';
import { Box, Typography, Paper } from '@mui/material';
import { EventCard } from './EventCard';
import { EventModal } from './EventModal';
import { CreateEventModal } from './CreateEventModal';
import { getDayNumber } from '@/lib/utils/dateUtils';

interface Props {
  day: CalendarDayType;
  onEventCreated: () => void;
}

export function CalendarDay({ day, onEventCreated }: Props) {
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);

  const handleDayClick = (e: React.MouseEvent) => {
    // Открываем модалку создания только если клик не на событие
    if ((e.target as HTMLElement).closest('.event-card')) {
      return;
    }
    setCreateModalOpen(true);
  };

  return (
    <>
      <Paper
        onClick={handleDayClick}
        sx={{
          minHeight: { xs: 60, sm: 80, md: 100 },
          p: { xs: 0.25, sm: 0.5, md: 1 },
          backgroundColor: day.is_current_month ? 'white' : 'grey.100',
          opacity: day.is_current_month ? 1 : 0.6,
          border: day.is_today ? 2 : 0,
          borderColor: day.is_today ? 'primary.main' : 'transparent',
          transition: 'background-color 0.2s',
          cursor: 'pointer',
          '&:hover': {
            backgroundColor: day.is_current_month ? 'grey.50' : 'grey.200',
          },
        }}
        elevation={0}
      >
        <Typography
          variant="body2"
          fontWeight={600}
          sx={{
            mb: { xs: 0.25, sm: 0.5 },
            color: day.is_today ? 'primary.main' : 'text.secondary',
            fontSize: { 
              xs: day.is_today ? '0.75rem' : '0.65rem',
              sm: day.is_today ? '0.875rem' : '0.75rem',
              md: day.is_today ? '1rem' : '0.875rem'
            },
          }}
        >
          {getDayNumber(day.date)}
        </Typography>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          {day.events.map((event) => (
            <Box key={event.id} className="event-card">
              <EventCard
                event={event}
                onClick={() => setSelectedEvent(event)}
              />
            </Box>
          ))}
        </Box>
      </Paper>

      <EventModal
        event={selectedEvent}
        onClose={() => setSelectedEvent(null)}
      />

      <CreateEventModal
        open={createModalOpen}
        selectedDate={day.date}
        onClose={() => setCreateModalOpen(false)}
        onEventCreated={onEventCreated}
      />
    </>
  );
}
