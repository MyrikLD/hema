import { useEffect, useRef, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Html5Qrcode } from 'html5-qrcode';
import {
  Box,
  CircularProgress,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Typography,
  Button,
} from '@mui/material';
import { get, post, ApiError } from '../api/client';
import type { Event } from '../types';

const DEBOUNCE_MS = 3000;
const NOTIF_DURATION_MS = 3000;

type NotifType = 'success' | 'warning' | 'error';

interface Notification {
  type: NotifType;
  lines: string[];
}

const NOTIF_BG: Record<NotifType, string> = {
  success: '#2e7d32',
  warning: '#e65100',
  error: '#c62828',
};

export default function ScannerPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const eventIdParam = searchParams.get('event_id');

  const initialEventId = eventIdParam ? parseInt(eventIdParam) : '';

  const [events, setEvents] = useState<Event[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<number | ''>(initialEventId);
  const [loadingEvents, setLoadingEvents] = useState(true);
  const [cameraStarted, setCameraStarted] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [notification, setNotification] = useState<Notification | null>(null);

  const selectedEventIdRef = useRef<number | null>(typeof initialEventId === 'number' ? initialEventId : null);
  const lastScannedRef = useRef<{ qr: string; time: number } | null>(null);
  const notifTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const qrRef = useRef<Html5Qrcode | null>(null);
  const pendingRef = useRef<Promise<void>>(Promise.resolve());

  // Keep ref in sync so the scanner callback always sees the latest selection
  useEffect(() => {
    selectedEventIdRef.current = typeof selectedEventId === 'number' ? selectedEventId : null;
  }, [selectedEventId]);

  // Fetch events
  useEffect(() => {
    if (eventIdParam) {
      get<Event>(`/events/${eventIdParam}`)
        .then((e) => setEvents([e]))
        .catch(() => {})
        .finally(() => setLoadingEvents(false));
    } else {
      const today = new Date().toISOString().slice(0, 10);
      get<Event[]>(`/events?start=${today}&end=${today}`)
        .then((data) => {
          setEvents(data);
          if (data.length === 1) setSelectedEventId(data[0].id);
        })
        .catch(() => {})
        .finally(() => setLoadingEvents(false));
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Start QR scanner — sequenced via promise chain to prevent double init
  useEffect(() => {
    // Each effect invocation gets its own `active` flag.
    // StrictMode cancels the first invocation (sets active=false) before the
    // microtask task queue runs, so the first invocation's `then` callback returns
    // early and never creates an Html5Qrcode instance.
    let active = true;

    const startPromise = pendingRef.current.then(async () => {
      if (!active) return; // cancelled by StrictMode cleanup before we ran

      const showNotif = (type: NotifType, lines: string[]) => {
        if (!active) return;
        if (notifTimerRef.current) clearTimeout(notifTimerRef.current);
        setNotification({ type, lines });
        notifTimerRef.current = setTimeout(() => setNotification(null), NOTIF_DURATION_MS);
      };

      const handleScan = async (decodedText: string) => {
        if (!active) return;
        const eventId = selectedEventIdRef.current;
        if (!eventId) return;

        const now = Date.now();
        if (
          lastScannedRef.current?.qr === decodedText &&
          now - lastScannedRef.current.time < DEBOUNCE_MS
        ) return;
        lastScannedRef.current = { qr: decodedText, time: now };

        let userId: number;
        try {
          const payload = JSON.parse(decodedText);
          if (typeof payload?.user_id !== 'number') return;
          userId = payload.user_id;
        } catch {
          return;
        }

        try {
          await post<void>('/visits', { user_id: userId, event_id: eventId });
          const user = await get<{ name: string | null; username: string }>(`/users/${userId}`);
          showNotif('success', [user.name || user.username, 'Checked in']);
        } catch (err) {
          if (err instanceof ApiError && err.status === 409) {
            const user = await get<{ name: string | null; username: string }>(`/users/${userId}`).catch(() => null);
            showNotif('warning', [user?.name || user?.username || 'Unknown', 'Already checked in']);
          } else {
            showNotif(
              'error',
              err instanceof ApiError && err.status === 403
                ? ['Access denied']
                : ['Request failed'],
            );
          }
        }
      };

      const qr = new Html5Qrcode('qr-reader');
      qrRef.current = qr;

      try {
        await qr.start(
          { facingMode: 'environment' },
          { fps: 10, qrbox: { width: 250, height: 250 } },
          handleScan,
          () => {},
        );
        if (active) setCameraStarted(true);
      } catch (err) {
        if (active) setCameraError(err instanceof Error ? err.message : 'Camera error');
      }
    });

    return () => {
      active = false;
      // Append cleanup AFTER startPromise so stop() never races with start().
      // The next effect invocation chains its own start after this cleanup.
      pendingRef.current = startPromise.then(async () => {
        const qr = qrRef.current;
        if (!qr) return;
        qrRef.current = null;
        try {
          if (qr.isScanning) await qr.stop();
          qr.clear();
        } catch {
          // ignore cleanup errors
        }
      });
    };
  }, []);

  useEffect(
    () => () => {
      if (notifTimerRef.current) clearTimeout(notifTimerRef.current);
    },
    [],
  );

  const selectedEvent = events.find((e) => e.id === selectedEventId) ?? null;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Event selector */}
      <Box sx={{ p: 2, pb: 1 }}>
        {loadingEvents ? (
          <CircularProgress size={24} />
        ) : events.length === 0 && !eventIdParam ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Typography variant="body2" color="text.secondary">
              No active events right now
            </Typography>
            <Button variant="outlined" size="small" onClick={() => navigate('/')}>
              Create event
            </Button>
          </Box>
        ) : events.length > 1 ? (
          <FormControl fullWidth size="small">
            <InputLabel>Select event</InputLabel>
            <Select
              value={selectedEventId}
              label="Select event"
              onChange={(e) => setSelectedEventId(e.target.value as number)}
            >
              {events.map((ev) => (
                <MenuItem key={ev.id} value={ev.id}>
                  {ev.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        ) : selectedEvent ? (
          <Typography variant="subtitle1" fontWeight={600}>
            {selectedEvent.name}
          </Typography>
        ) : null}
      </Box>

      {/* Scanner area */}
      <Box sx={{ flex: 1, position: 'relative', overflow: 'hidden', minHeight: 300 }}>
        {cameraError ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography color="error">{cameraError}</Typography>
          </Box>
        ) : (
          <>
            {!cameraStarted && (
              <Box
                sx={{
                  position: 'absolute',
                  inset: 0,
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  zIndex: 1,
                }}
              >
                <CircularProgress />
              </Box>
            )}
            <Box
              id="qr-reader"
              sx={{
                width: '100%',
                '& video': { width: '100% !important', height: 'auto !important' },
                '& img': { display: 'none' },
              }}
            />
          </>
        )}

        {/* Floating notification */}
        {notification && (
          <Paper
            elevation={6}
            sx={{
              position: 'absolute',
              bottom: 24,
              left: '50%',
              transform: 'translateX(-50%)',
              bgcolor: NOTIF_BG[notification.type],
              color: 'white',
              px: 3,
              py: 1.5,
              borderRadius: 2,
              minWidth: 200,
              textAlign: 'center',
              zIndex: 10,
            }}
          >
            {notification.lines.map((line, i) => (
              <Typography
                key={i}
                variant={i === 0 ? 'subtitle1' : 'body2'}
                fontWeight={i === 0 ? 600 : 400}
              >
                {line}
              </Typography>
            ))}
          </Paper>
        )}
      </Box>
    </Box>
  );
}
