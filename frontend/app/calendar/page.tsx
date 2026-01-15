'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { CalendarGrid } from '@/components/Calendar/CalendarGrid';
import { MonthNav } from '@/components/Header/MonthNav';
import { calendarAPI } from '@/lib/api/calendar';
import { Box, CircularProgress, Alert } from '@mui/material';
import { CalendarMonth } from '@/types/calendar';
import { AuthGuard } from '@/components/Auth/AuthGuard';

function CalendarContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [data, setData] = useState<CalendarMonth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const year = searchParams.get('year');
  const month = searchParams.get('month');

  useEffect(() => {
    async function fetchData() {
      try {
        let calendar;
        if (year && month) {
          calendar = await calendarAPI.getMonth(parseInt(year), parseInt(month));
        } else {
          calendar = await calendarAPI.getCurrentMonth();
        }
        setData(calendar);
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load calendar');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [year, month]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!data) return null;

  const handlePrevMonth = async () => {
    const prev = new Date(data.prev_date);
    const calendar = await calendarAPI.getMonth(prev.getFullYear(), prev.getMonth() + 1);
    setData(calendar);
    router.push(`/calendar?year=${prev.getFullYear()}&month=${prev.getMonth() + 1}`, { scroll: false });
  };

  const handleNextMonth = async () => {
    const next = new Date(data.next_date);
    const calendar = await calendarAPI.getMonth(next.getFullYear(), next.getMonth() + 1);
    setData(calendar);
    router.push(`/calendar?year=${next.getFullYear()}&month=${next.getMonth() + 1}`, { scroll: false });
  };

  const handleCurrentMonth = async () => {
    const calendar = await calendarAPI.getCurrentMonth();
    setData(calendar);
    router.push('/calendar', { scroll: false });
  };

  const handleEventChange = async () => {
    try {
      let calendar;
      if (year && month) {
        calendar = await calendarAPI.getMonth(parseInt(year), parseInt(month));
      } else {
        calendar = await calendarAPI.getCurrentMonth();
      }
      setData(calendar);
    } catch (err: unknown) {
      console.error('Failed to reload calendar:', err);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <MonthNav
        currentDate={data.date}
        prevDate={data.prev_date}
        nextDate={data.next_date}
        onPrevMonth={handlePrevMonth}
        onNextMonth={handleNextMonth}
        onCurrentMonth={handleCurrentMonth}
      />
      <CalendarGrid data={data} onEventChange={handleEventChange} />
    </Box>
  );
}

export default function CalendarPage() {
  return (
    <AuthGuard>
      <Suspense fallback={
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
          <CircularProgress />
        </Box>
      }>
        <CalendarContent />
      </Suspense>
    </AuthGuard>
  );
}
