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

function isLightColor(hex: string): boolean {
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  // Relative luminance formula
  return (r * 299 + g * 587 + b * 114) / 1000 > 150;
}

export default function EventCard({ event, onClick }: EventCardProps) {
  const textColor = isLightColor(event.color) ? '#000' : '#fff';

  return (
    <Box
      onClick={() => onClick(event)}
      sx={{
        backgroundColor: `#${event.color}`,
        color: textColor,
        borderRadius: 0.5,
        px: 0.5,
        py: 0.25,
        mb: 0.25,
        cursor: 'pointer',
        fontSize: '0.65rem',
        lineHeight: 1.2,
        overflow: 'hidden',
        maxWidth: '100%',
        '&:hover': {
          filter: 'brightness(0.9)',
        },
      }}
    >
      <Typography variant="caption" sx={{ color: 'inherit', fontWeight: 500, fontSize: 'inherit', display: 'block' }}>
        {formatTime(event.start)}
      </Typography>
      <Typography
        variant="caption"
        sx={{
          color: 'inherit',
          fontSize: 'inherit',
          display: 'block',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}
      >
        {event.name}
      </Typography>
    </Box>
  );
}
