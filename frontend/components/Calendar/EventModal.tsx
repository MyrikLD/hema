'use client';

import { Event } from '@/types/event';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Typography,
  Box,
  Button,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { formatDateTime } from '@/lib/utils/dateUtils';

interface Props {
  event: Event | null;
  onClose: () => void;
}

export function EventModal({ event, onClose }: Props) {
  if (!event) return null;

  return (
    <Dialog
      open={!!event}
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 2,
        },
      }}
    >
      <DialogTitle sx={{ m: 0, p: 2, pr: 6 }}>
        {event.name}
        <IconButton
          aria-label="close"
          onClick={onClose}
          sx={{
            position: 'absolute',
            right: 8,
            top: 8,
            color: (theme) => theme.palette.grey[500],
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent dividers>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          <Typography variant="body1">
            <strong>Начало:</strong> {formatDateTime(event.start)}
          </Typography>
          <Typography variant="body1">
            <strong>Конец:</strong> {formatDateTime(event.end)}
          </Typography>
          <Typography variant="body1">
            <strong>Тренер ID:</strong> {event.trainer_id}
          </Typography>
        </Box>
      </DialogContent>

      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onClose}>
          Закрыть
        </Button>
      </DialogActions>
    </Dialog>
  );
}
