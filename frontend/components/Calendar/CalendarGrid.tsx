'use client';

import { CalendarMonth } from '@/types/calendar';
import { Box, Paper, Typography } from '@mui/material';
import { CalendarDay } from './CalendarDay';

interface Props {
  data: CalendarMonth;
  onEventChange?: () => void;
}

const WEEKDAYS = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];

export function CalendarGrid({ data, onEventChange }: Props) {
  return (
    <Box sx={{ 
      maxWidth: 1200, 
      mx: 'auto', 
      p: { xs: 0.5, sm: 1, md: 2 },
    }}>
      <Paper
        elevation={2}
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(7, 1fr)',
          gap: '1px',
          backgroundColor: 'grey.300',
          border: 1,
          borderColor: 'grey.300',
          borderRadius: { xs: 1, md: 2 },
          overflow: 'hidden',
        }}
      >
        {/* Заголовки дней недели */}
        {WEEKDAYS.map((day) => (
          <Box
            key={day}
            sx={{
              backgroundColor: 'grey.800',
              color: 'white',
              textAlign: 'center',
              py: { xs: 0.5, sm: 1, md: 1.5 },
              px: { xs: 0.25, sm: 0.5 },
            }}
          >
            <Typography 
              variant="body2" 
              fontWeight={600}
              sx={{ fontSize: { xs: '0.65rem', sm: '0.75rem', md: '0.875rem' } }}
            >
              {day}
            </Typography>
          </Box>
        ))}

        {/* Дни месяца */}
        {data.days.map((day, idx) => (
          <CalendarDay 
            key={idx} 
            day={day} 
            onEventCreated={() => onEventChange?.()} 
          />
        ))}
      </Paper>
    </Box>
  );
}
