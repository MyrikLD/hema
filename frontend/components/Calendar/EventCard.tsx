'use client';

import { Event } from '@/types/event';
import { Box, Paper, Typography } from '@mui/material';
import { formatTime } from '@/lib/utils/dateUtils';

interface Props {
  event: Event;
  onClick: () => void;
}

export function EventCard({ event, onClick }: Props) {
  return (
    <Paper
      onClick={onClick}
      sx={{
        backgroundColor: `#${event.color}`,
        color: 'white',
        padding: { xs: '2px 4px', sm: '3px 6px', md: '4px 8px' },
        borderRadius: { xs: 0.5, md: 1 },
        cursor: 'pointer',
        minHeight: { xs: 28, sm: 36, md: 44 },
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        transition: 'all 0.2s',
        '&:hover': {
          filter: 'brightness(0.9)',
          transform: 'translateY(-1px)',
        },
        '&:active': {
          transform: 'translateY(0)',
        },
      }}
      elevation={1}
    >
      <Typography 
        variant="caption" 
        fontWeight={600} 
        component="div"
        sx={{ fontSize: { xs: '0.5rem', sm: '0.65rem', md: '0.75rem' } }}
      >
        {formatTime(event.start)} - {formatTime(event.end)}
      </Typography>
      <Typography
        variant="caption"
        component="div"
        sx={{
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
          fontSize: { xs: '0.5rem', sm: '0.65rem', md: '0.75rem' },
        }}
      >
        {event.name}
      </Typography>
    </Paper>
  );
}
