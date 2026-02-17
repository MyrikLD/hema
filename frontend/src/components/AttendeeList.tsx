import { useEffect, useState } from 'react';
import { List, ListItem, ListItemText, Typography } from '@mui/material';
import type { IntentionWithUser } from '../types';
import { getAttendees } from '../api/intentions';

interface AttendeeListProps {
  eventId: number;
  refreshKey: number;
}

export default function AttendeeList({ eventId, refreshKey }: AttendeeListProps) {
  const [attendees, setAttendees] = useState<IntentionWithUser[]>([]);

  useEffect(() => {
    getAttendees(eventId).then(setAttendees).catch(() => setAttendees([]));
  }, [eventId, refreshKey]);

  if (attendees.length === 0) {
    return (
      <Typography variant="body2" color="text.secondary" sx={{ py: 1 }}>
        No one signed up yet
      </Typography>
    );
  }

  return (
    <>
      <Typography variant="subtitle2" sx={{ mt: 1 }}>
        Attendees ({attendees.length})
      </Typography>
      <List dense>
        {attendees.map((a) => (
          <ListItem key={a.id} disablePadding>
            <ListItemText primary={a.user_name} />
          </ListItem>
        ))}
      </List>
    </>
  );
}
