import { useCallback, useEffect, useState } from 'react';
import {
  Box,
  Container,
  Typography,
  List,
  ListItem,
  ListItemText,
  Chip,
  CircularProgress,
  Button,
  Paper,
} from '@mui/material';
import type { Visit } from '../types';
import { getMyHistory } from '../api/visits';

const PAGE_SIZE = 20;

export default function HistoryPage() {
  const [visits, setVisits] = useState<Visit[]>([]);
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);

  const loadMore = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getMyHistory(PAGE_SIZE, visits.length);
      setVisits((prev) => [...prev, ...data]);
      if (data.length < PAGE_SIZE) setHasMore(false);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, [visits.length]);

  useEffect(() => {
    getMyHistory(PAGE_SIZE, 0)
      .then((data) => {
        setVisits(data);
        if (data.length < PAGE_SIZE) setHasMore(false);
      })
      .finally(() => setLoading(false));
  }, []);

  const formatDate = (ts: string) => {
    const d = new Date(ts);
    return d.toLocaleString([], {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    });
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ py: 3 }}>
        <Typography variant="h6" gutterBottom>
          Attendance History
        </Typography>

        {visits.length === 0 && !loading && (
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography color="text.secondary">No attendance records yet</Typography>
          </Paper>
        )}

        <List>
          {visits.map((v, i) => (
            <ListItem key={`${v.timestamp}-${v.uid}-${i}`} divider>
              <ListItemText
                primary={v.event_name || 'Unknown event'}
                secondary={formatDate(v.timestamp)}
              />
              {v.event_color && (
                <Chip
                  size="small"
                  sx={{
                    backgroundColor: `#${v.event_color}`,
                    color: '#fff',
                    minWidth: 20,
                    height: 20,
                  }}
                  label=""
                />
              )}
            </ListItem>
          ))}
        </List>

        {loading && (
          <Box display="flex" justifyContent="center" py={2}>
            <CircularProgress size={24} />
          </Box>
        )}

        {hasMore && !loading && visits.length > 0 && (
          <Box display="flex" justifyContent="center" py={2}>
            <Button onClick={loadMore} variant="text">
              Load more
            </Button>
          </Box>
        )}
      </Box>
    </Container>
  );
}
