import { useEffect, useState } from 'react';
import { Button, CircularProgress } from '@mui/material';
import { signUp, cancelSignUp, hasIntention } from '../api/intentions';
import { useAuth } from '../contexts/AuthContext';

interface SignUpButtonProps {
  eventId: number;
  onToggle: () => void;
}

export default function SignUpButton({ eventId, onToggle }: SignUpButtonProps) {
  const { isAuthenticated } = useAuth();
  const [signed, setSigned] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      setLoading(false);
      return;
    }
    hasIntention(eventId)
      .then(setSigned)
      .finally(() => setLoading(false));
  }, [eventId, isAuthenticated]);

  const handleClick = async () => {
    setLoading(true);
    try {
      if (signed) {
        await cancelSignUp(eventId);
        setSigned(false);
      } else {
        await signUp(eventId);
        setSigned(true);
      }
      onToggle();
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <CircularProgress size={24} />;
  }

  return (
    <Button
      variant={signed ? 'outlined' : 'contained'}
      color={signed ? 'error' : 'secondary'}
      onClick={handleClick}
      fullWidth
      sx={{ mt: 1 }}
    >
      {signed ? 'Cancel Sign Up' : 'Sign Up'}
    </Button>
  );
}
