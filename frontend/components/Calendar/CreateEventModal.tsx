'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  IconButton,
  Box,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { MuiColorInput } from 'mui-color-input';
import { eventsAPI } from '@/lib/api/events';

interface Props {
  open: boolean;
  selectedDate: string | null;
  onClose: () => void;
  onEventCreated: () => void;
}

export function CreateEventModal({ open, selectedDate, onClose, onEventCreated }: Props) {
  const [name, setName] = useState('');
  const [startTime, setStartTime] = useState('10:00');
  const [endTime, setEndTime] = useState('11:00');
  const [color, setColor] = useState('4CAF50');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedDate || !name.trim()) {
      setError('Заполните название события');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const startDateTime = `${selectedDate}T${startTime}:00Z`;
      const endDateTime = `${selectedDate}T${endTime}:00Z`;

      await eventsAPI.create({
        name: name.trim(),
        color,
        start: startDateTime,
        end: endDateTime,
      });

      // Сброс формы
      setName('');
      setStartTime('10:00');
      setEndTime('11:00');
      setColor('4CAF50');
      
      onEventCreated();
      onClose();
    } catch {
      setError('Не удалось создать событие');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setName('');
    setStartTime('10:00');
    setEndTime('11:00');
    setColor('4CAF50');
    setError(null);
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: { borderRadius: 2 },
      }}
    >
      <DialogTitle sx={{ m: 0, p: 2, pr: 6 }}>
        Создать событие
        <IconButton
          aria-label="close"
          onClick={handleClose}
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
      
      <form onSubmit={handleSubmit}>
        <DialogContent dividers>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Название"
              value={name}
              onChange={(e) => setName(e.target.value)}
              fullWidth
              required
              autoFocus
            />

            <TextField
              label="Дата"
              type="date"
              value={selectedDate || ''}
              InputProps={{
                readOnly: true,
              }}
              fullWidth
            />

            <Box sx={{ display: 'flex', gap: 2 }}>
              <TextField
                label="Начало"
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                fullWidth
                required
              />

              <TextField
                label="Конец"
                type="time"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                fullWidth
                required
              />
            </Box>

            <MuiColorInput
              label="Цвет"
              format="hex"
              value={`#${color}`}
              onChange={(newColor) => setColor(newColor.replace('#', '').toUpperCase())}
              fullWidth
            />

            {error && (
              <Box sx={{ color: 'error.main', fontSize: '0.875rem' }}>
                {error}
              </Box>
            )}
          </Box>
        </DialogContent>

        <DialogActions sx={{ p: 2 }}>
          <Button onClick={handleClose} disabled={loading}>
            Отмена
          </Button>
          <Button
            type="submit"
            variant="contained"
            disabled={loading}
          >
            {loading ? 'Создание...' : 'Создать'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
