'use client';

import { useRouter } from 'next/navigation';
import { AppBar, Toolbar, Typography, IconButton, Button, Box } from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import { formatDate } from '@/lib/utils/dateUtils';
import { clearAuth } from '@/lib/auth';

interface Props {
  currentDate: string;
  prevDate: string;
  nextDate: string;
  onPrevMonth?: () => void | Promise<void>;
  onNextMonth?: () => void | Promise<void>;
  onCurrentMonth?: () => void | Promise<void>;
}

export function MonthNav({ currentDate, prevDate, nextDate, onPrevMonth, onNextMonth, onCurrentMonth }: Props) {
  const router = useRouter();
  const current = new Date(currentDate);
  const prev = new Date(prevDate);
  const next = new Date(nextDate);

  const handleLogout = () => {
    clearAuth();
    router.push('/login');
  };

  const handlePrev = async () => {
    if (onPrevMonth) {
      await onPrevMonth();
    } else {
      router.push(`/calendar?year=${prev.getFullYear()}&month=${prev.getMonth() + 1}`, { scroll: false });
    }
  };

  const handleNext = async () => {
    if (onNextMonth) {
      await onNextMonth();
    } else {
      router.push(`/calendar?year=${next.getFullYear()}&month=${next.getMonth() + 1}`, { scroll: false });
    }
  };

  const handleCurrent = async () => {
    if (onCurrentMonth) {
      await onCurrentMonth();
    } else {
      router.push('/calendar', { scroll: false });
    }
  };

  return (
    <AppBar position="static" sx={{ backgroundColor: 'grey.800' }}>
      <Toolbar sx={{ justifyContent: 'space-between', maxWidth: 1200, width: '100%', mx: 'auto' }}>
        <IconButton
          onClick={handlePrev}
          aria-label="Previous month"
          sx={{
            color: 'white',
            backgroundColor: 'grey.700',
            '&:hover': {
              backgroundColor: 'grey.600',
            },
          }}
        >
          <ArrowBackIcon />
        </IconButton>

        <Typography 
          variant="h5" 
          component="h1" 
          onClick={handleCurrent}
          sx={{ 
            cursor: 'pointer',
            '&:hover': { color: 'grey.300' } 
          }}
        >
          {formatDate(current, 'LLLL yyyy')}
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton
            onClick={handleNext}
            aria-label="Next month"
            sx={{
              color: 'white',
              backgroundColor: 'grey.700',
              '&:hover': {
                backgroundColor: 'grey.600',
              },
            }}
          >
            <ArrowForwardIcon />
          </IconButton>

          <Button
            variant="contained"
            color="error"
            onClick={handleLogout}
            sx={{ textTransform: 'none' }}
          >
            Выйти
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
