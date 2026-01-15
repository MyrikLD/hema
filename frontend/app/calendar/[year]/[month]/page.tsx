'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { CalendarGrid } from '@/components/Calendar/CalendarGrid';
import { MonthNav } from '@/components/Header/MonthNav';
import { calendarAPI } from '@/lib/api/calendar';
import { Box, CircularProgress, Alert } from '@mui/material';
import { CalendarMonth } from '@/types/calendar';
import { AuthGuard } from '@/components/Auth/AuthGuard';

export default function CalendarMonthPage() {
  const params = useParams();
  const router = useRouter();
  const [data, setData] = useState<CalendarMonth | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const year = parseInt(params.year as string);
  const month = parseInt(params.month as string);

  const fetchMonth = async (year: number, month: number, showLoader = false) => {
    try {
      if (showLoader) setLoading(true);
      setError(null);
      const calendar = await calendarAPI.getMonth(year, month);
      setData(calendar);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load calendar');
    } finally {
      if (showLoader) setLoading(false);
    }
  };

  useEffect(() => {
    fetchMonth(year, month, true);
  }, [year, month]);

  const handlePrevMonth = async () => {
    if (!data) return;
    const prev = new Date(data.prev_date);
    const calendar = await calendarAPI.getMonth(prev.getFullYear(), prev.getMonth() + 1);

    setData(calendar);
    router.push(`/calendar/${prev.getFullYear()}/${prev.getMonth() + 1}`);
  };

  const handleNextMonth = async () => {
    if (!data) return;
    const next = new Date(data.next_date);
    const calendar = await calendarAPI.getMonth(next.getFullYear(), next.getMonth() + 1);

    setData(calendar);
    router.push(`/calendar/${next.getFullYear()}/${next.getMonth() + 1}`);
  };

  const handleCurrentMonth = async () => {
    try {
      setError(null);
      const calendar = await calendarAPI.getCurrentMonth();
      setData(calendar);
      const now = new Date(calendar.date);
      router.push(`/calendar/${now.getFullYear()}/${now.getMonth() + 1}`);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load calendar');
    }
  };

  const handleEventChange = async () => {
    await fetchMonth(year, month, false);
  };

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

  return (
    <AuthGuard>
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
    </AuthGuard>
  );
}
