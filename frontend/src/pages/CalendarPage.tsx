import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Box, IconButton, Typography, CircularProgress, Tooltip } from '@mui/material';
import { ChevronLeft, ChevronRight, CalendarMonth, Add } from '@mui/icons-material';
import type { Event } from '../types';
import { get } from '../api/client';
import { exportEvents } from '../utils/ics';
import { useAuth } from '../contexts/AuthContext';
import CalendarGrid from '../components/CalendarGrid';
import EventDetailSheet from '../components/EventDetailSheet';
import CreateEventDialog from '../components/CreateEventDialog';

function getMondayOf(d: Date): Date {
  const day = d.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  return new Date(d.getFullYear(), d.getMonth(), d.getDate() + diff);
}

function addDays(d: Date, n: number): Date {
  return new Date(d.getFullYear(), d.getMonth(), d.getDate() + n);
}

function toISODate(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

function formatWeekTitle(monday: Date): string {
  const sunday = addDays(monday, 6);
  const mo = { day: 'numeric', month: 'short' } as const;
  if (monday.getMonth() === sunday.getMonth()) {
    return `${monday.getDate()}–${sunday.getDate()} ${sunday.toLocaleString('default', { month: 'short' })} ${sunday.getFullYear()}`;
  }
  if (monday.getFullYear() === sunday.getFullYear()) {
    return `${monday.toLocaleString('default', mo)} – ${sunday.toLocaleString('default', { ...mo, year: 'numeric' })}`;
  }
  return `${monday.toLocaleString('default', { ...mo, year: 'numeric' })} – ${sunday.toLocaleString('default', { ...mo, year: 'numeric' })}`;
}

export default function CalendarPage() {
  const { monday: mondayParam } = useParams<{ monday: string }>();
  const navigate = useNavigate();

  const monday = useMemo(
    () => mondayParam ? getMondayOf(new Date(mondayParam + 'T00:00:00')) : getMondayOf(new Date()),
    [mondayParam],
  );
  const mondayStr = toISODate(monday);
  const sundayStr = toISODate(addDays(monday, 6));

  const { user } = useAuth();
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [sheetOpen, setSheetOpen] = useState(false);
  const [createOpen, setCreateOpen] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const evts = await get<Event[]>(`/events?start=${mondayStr}&end=${sundayStr}`);
      setEvents(evts);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, [mondayStr]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const goWeek = (offset: number) => {
    navigate(`/calendar/${toISODate(addDays(monday, offset * 7))}`);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', py: 1, px: 1 }}>
        <IconButton onClick={() => goWeek(-1)} size="small">
          <ChevronLeft />
        </IconButton>
        <Typography
          variant="h6"
          sx={{ cursor: 'pointer', fontWeight: 600, fontSize: '1rem' }}
          onClick={() => navigate('/')}
        >
          {formatWeekTitle(monday)}
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          {user?.is_trainer && (
            <Tooltip title="New event">
              <IconButton size="small" onClick={() => setCreateOpen(true)}>
                <Add fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
          <Tooltip title="Экспорт недели (.ics)">
            <span>
              <IconButton
                size="small"
                onClick={() => exportEvents(events, `hema_${mondayStr}.ics`)}
                disabled={events.length === 0}
              >
                <CalendarMonth fontSize="small" />
              </IconButton>
            </span>
          </Tooltip>
          <IconButton onClick={() => goWeek(1)} size="small">
            <ChevronRight />
          </IconButton>
        </Box>
      </Box>

      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <CircularProgress />
        </Box>
      ) : (
        <CalendarGrid
          events={events}
          weekStart={monday}
          onEventClick={(e) => { setSelectedEvent(e); setSheetOpen(true); }}
        />
      )}

      <EventDetailSheet
        event={selectedEvent}
        open={sheetOpen}
        onClose={() => setSheetOpen(false)}
        onOpen={() => setSheetOpen(true)}
      />

      <CreateEventDialog
        open={createOpen}
        defaultDate={mondayStr}
        onClose={() => setCreateOpen(false)}
        onCreated={() => { setCreateOpen(false); fetchData(); }}
      />
    </Box>
  );
}
