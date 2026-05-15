import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  SwipeableDrawer,
  Typography,
  Divider,
  IconButton,
  Tooltip,
  Button,
} from '@mui/material';
import { CalendarMonth, QrCodeScanner } from '@mui/icons-material';
import type { Event } from '../types';
import { exportEvent } from '../utils/ics';
import { useAuth } from '../contexts/AuthContext';
import SignUpButton from './SignUpButton';
import AttendeeList from './AttendeeList';

interface EventDetailSheetProps {
  event: Event | null;
  open: boolean;
  onClose: () => void;
  onOpen: () => void;
}

function formatDateTime(dateStr: string, timeStr: string): string {
  const d = new Date(`${dateStr}T${timeStr}`);
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
  const { user } = useAuth();
  const navigate = useNavigate();

  if (!event) return null;

  const isTrainer =
    user?.name != null &&
    event.trainer_name != null &&
    user.name === event.trainer_name;

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

      <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <Typography variant="h6">{event.name}</Typography>
        <Tooltip title="Добавить в календарь (.ics)">
          <IconButton size="small" onClick={() => exportEvent(event)}>
            <CalendarMonth fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
        {formatDateTime(event.date, event.time_start)} &mdash; {event.time_end.slice(0, 5)}
      </Typography>

      <Divider sx={{ my: 2 }} />

      {isTrainer && (
        <Button
          variant="contained"
          color="secondary"
          startIcon={<QrCodeScanner />}
          fullWidth
          sx={{ mt: 1 }}
          onClick={() => {
            onClose();
            navigate(`/scanner?event_id=${event.id}`);
          }}
        >
          Сканировать
        </Button>
      )}

      <SignUpButton eventId={event.id} onToggle={() => setRefreshKey((k) => k + 1)} />

      <AttendeeList eventId={event.id} refreshKey={refreshKey} />
    </SwipeableDrawer>
  );
}
