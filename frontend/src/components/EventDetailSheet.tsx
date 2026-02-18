import { useState } from 'react';
import {
  Box,
  SwipeableDrawer,
  Typography,
  Divider,
} from '@mui/material';
import type { Event } from '../types';
import SignUpButton from './SignUpButton';
import AttendeeList from './AttendeeList';

interface EventDetailSheetProps {
  event: Event | null;
  open: boolean;
  onClose: () => void;
  onOpen: () => void;
}

function formatDateTime(dateStr: string): string {
  const d = new Date(dateStr);
  return d.toLocaleString([], {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  });
}

export default function EventDetailSheet({ event, open, onClose, onOpen }: EventDetailSheetProps) {
  const [refreshKey, setRefreshKey] = useState(0);

  if (!event) return null;

  return (
    <SwipeableDrawer
      anchor="bottom"
      open={open}
      onClose={onClose}
      onOpen={onOpen}
      PaperProps={{
        sx: {
          borderTopLeftRadius: 16,
          borderTopRightRadius: 16,
          maxHeight: '70vh',
          px: 3,
          py: 2,
        },
      }}
    >
      <Box
        sx={{
          width: 40,
          height: 4,
          backgroundColor: '#ccc',
          borderRadius: 2,
          mx: 'auto',
          mb: 2,
        }}
      />

      <Box
        sx={{
          width: '100%',
          height: 6,
          backgroundColor: `#${event.color}`,
          borderRadius: 1,
          mb: 2,
        }}
      />

      <Typography variant="h6">{event.name}</Typography>

      <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
        {formatDateTime(event.start)} &mdash; {formatDateTime(event.end)}
      </Typography>

      <Divider sx={{ my: 2 }} />

      <SignUpButton eventId={event.id} onToggle={() => setRefreshKey((k) => k + 1)} />

      <AttendeeList eventId={event.id} refreshKey={refreshKey} />
    </SwipeableDrawer>
  );
}
