import { useState } from 'react';
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  Alert,
  Box,
} from '@mui/material';
import { post } from '../api/client';
import type { Event } from '../types';

interface Props {
  open: boolean;
  defaultDate: string; // YYYY-MM-DD
  onClose: () => void;
  onCreated: (event: Event) => void;
}

export default function CreateEventDialog({ open, defaultDate, onClose, onCreated }: Props) {
  const [name, setName] = useState('');
  const [color, setColor] = useState('4CAF50');
  const [date, setDate] = useState(defaultDate);
  const [timeStart, setTimeStart] = useState('10:00');
  const [timeEnd, setTimeEnd] = useState('11:30');
  const [price, setPrice] = useState('0');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleClose = () => {
    setError('');
    onClose();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const created = await post<Event>('/events', {
        name: name.trim(),
        color,
        date,
        time_start: timeStart,
        time_end: timeEnd,
        price: parseInt(price) || 0,
      });
      onCreated(created);
      // reset form
      setName('');
      setColor('4CAF50');
      setDate(defaultDate);
      setTimeStart('10:00');
      setTimeEnd('11:30');
      setPrice('0');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create event');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} fullWidth maxWidth="xs">
      <DialogTitle>New event</DialogTitle>
      <Box component="form" onSubmit={handleSubmit}>
        <DialogContent sx={{ pt: 1 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <TextField
            label="Name"
            fullWidth
            margin="dense"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            autoFocus
          />
          <TextField
            label="Date"
            type="date"
            fullWidth
            margin="dense"
            required
            value={date}
            onChange={(e) => setDate(e.target.value)}
            slotProps={{ inputLabel: { shrink: true } }}
          />
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              label="Start"
              type="time"
              fullWidth
              margin="dense"
              required
              value={timeStart}
              onChange={(e) => setTimeStart(e.target.value)}
              slotProps={{ inputLabel: { shrink: true } }}
            />
            <TextField
              label="End"
              type="time"
              fullWidth
              margin="dense"
              required
              value={timeEnd}
              onChange={(e) => setTimeEnd(e.target.value)}
              slotProps={{ inputLabel: { shrink: true } }}
            />
          </Box>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
            <TextField
              label="Price"
              type="number"
              fullWidth
              margin="dense"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              slotProps={{ input: { inputProps: { min: 0 } } }}
            />
            <TextField
              label="Color"
              type="color"
              margin="dense"
              value={`#${color}`}
              onChange={(e) => setColor(e.target.value.slice(1).toUpperCase())}
              sx={{ width: 80, flexShrink: 0 }}
              slotProps={{ inputLabel: { shrink: true } }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            Cancel
          </Button>
          <Button type="submit" variant="contained" disabled={loading || !name.trim()}>
            {loading ? 'Creating…' : 'Create'}
          </Button>
        </DialogActions>
      </Box>
    </Dialog>
  );
}
