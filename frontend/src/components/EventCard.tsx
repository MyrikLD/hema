import { Box, Typography } from '@mui/material';
import type { Event } from '../types';

interface EventCardProps {
  event: Event;
  onClick: (event: Event) => void;
}

function formatTime(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
}

export default function EventCard({ event, onClick }: EventCardProps) {
  return (
    <Box
      onClick={() => onClick(event)}
      sx={{
        backgroundColor: `#${event.color}`,
        color: '#fff',
        borderRadius: 0.5,
        px: 0.5,
        py: 0.25,
        mb: 0.25,
        cursor: 'pointer',
        fontSize: '0.7rem',
        lineHeight: 1.2,
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
        '&:hover': {
          filter: 'brightness(0.9)',
        },
      }}
    >
      <Typography variant="caption" sx={{ color: 'inherit', fontWeight: 500, fontSize: 'inherit' }}>
        {formatTime(event.start)} {event.name}
      </Typography>
    </Box>
  );
}
