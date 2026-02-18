import { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Box,
  IconButton,
  Typography,
  CircularProgress,
} from '@mui/material';
import { ChevronLeft, ChevronRight } from '@mui/icons-material';
import type { CalendarMonth, Event } from '../types';
import { get } from '../api/client';
import CalendarGrid from '../components/CalendarGrid';
import EventDetailSheet from '../components/EventDetailSheet';

export default function CalendarPage() {
  const { year, month } = useParams<{ year: string; month: string }>();
  const navigate = useNavigate();
  const [data, setData] = useState<CalendarMonth | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [sheetOpen, setSheetOpen] = useState(false);

  const fetchCalendar = useCallback(async () => {
    setLoading(true);
    try {
      const path = year && month ? `/calendar/${year}/${month}` : '/calendar';
      const result = await get<CalendarMonth>(path);
      setData(result);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, [year, month]);

  useEffect(() => {
    fetchCalendar();
  }, [fetchCalendar]);

  const handleEventClick = (event: Event) => {
    setSelectedEvent(event);
    setSheetOpen(true);
  };

  const handleNavigate = (dateStr: string) => {
    const [y, m] = dateStr.split('-');
    navigate(`/calendar/${y}/${parseInt(m)}`);
  };

  const handleTitleClick = () => {
    navigate('/');
  };

  if (loading || !data) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  const monthDate = new Date(data.date + 'T00:00:00');
  const monthName = monthDate.toLocaleString('default', { month: 'long', year: 'numeric' });

  return (
    <Box>
      {/* Month navigation */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          py: 1,
          px: 1,
        }}
      >
        <IconButton onClick={() => handleNavigate(data.prev_date)} size="small">
          <ChevronLeft />
        </IconButton>
        <Typography
          variant="h6"
          sx={{ cursor: 'pointer', fontWeight: 600, fontSize: '1rem' }}
          onClick={handleTitleClick}
        >
          {monthName}
        </Typography>
        <IconButton onClick={() => handleNavigate(data.next_date)} size="small">
          <ChevronRight />
        </IconButton>
      </Box>

      <CalendarGrid days={data.days} onEventClick={handleEventClick} />

      <EventDetailSheet
        event={selectedEvent}
        open={sheetOpen}
        onClose={() => setSheetOpen(false)}
        onOpen={() => setSheetOpen(true)}
      />
    </Box>
  );
}
