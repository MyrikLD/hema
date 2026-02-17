import { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Alert,
  Paper,
  Link,
  MenuItem,
} from '@mui/material';
import { register } from '../api/auth';
import { useAuth } from '../contexts/AuthContext';

export default function RegisterPage() {
  const [name, setName] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [gender, setGender] = useState('o');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register({
        name,
        password,
        gender,
        ...(phone ? { phone } : {}),
      });
      await login(name, password);
      navigate('/', { replace: true });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xs">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
        }}
      >
        <Paper sx={{ p: 4 }}>
          <Typography variant="h5" align="center" gutterBottom>
            Create Account
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              label="Name"
              fullWidth
              margin="normal"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              autoFocus
              autoComplete="name"
            />
            <TextField
              label="Password"
              type="password"
              fullWidth
              margin="normal"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="new-password"
            />
            <TextField
              label="Phone (optional)"
              fullWidth
              margin="normal"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              autoComplete="tel"
            />
            <TextField
              select
              label="Gender"
              fullWidth
              margin="normal"
              value={gender}
              onChange={(e) => setGender(e.target.value)}
            >
              <MenuItem value="m">Male</MenuItem>
              <MenuItem value="f">Female</MenuItem>
              <MenuItem value="o">Other</MenuItem>
            </TextField>
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 2, mb: 2 }}
              disabled={loading}
            >
              {loading ? 'Creating account...' : 'Register'}
            </Button>
          </Box>

          <Typography variant="body2" align="center">
            Already have an account?{' '}
            <Link component={RouterLink} to="/login">
              Sign in
            </Link>
          </Typography>
        </Paper>
      </Box>
    </Container>
  );
}
