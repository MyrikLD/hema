import { useState } from 'react';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Alert,
  Paper,
  MenuItem,
  Divider,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { updateProfile } from '../api/auth';

export default function ProfilePage() {
  const { user, logout, refreshUser } = useAuth();
  const [name, setName] = useState(user?.name || '');
  const [phone, setPhone] = useState(user?.phone || '');
  const [gender, setGender] = useState<string>(user?.gender || 'o');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setLoading(true);
    try {
      const data: Record<string, string> = {};
      if (name !== user?.name) data.name = name;
      if (phone !== (user?.phone || '')) data.phone = phone;
      if (gender !== user?.gender) data.gender = gender;
      if (password) data.password = password;

      if (Object.keys(data).length === 0) {
        setMessage('No changes to save');
        setLoading(false);
        return;
      }

      await updateProfile(data);
      await refreshUser();
      setPassword('');
      setMessage('Profile updated');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Update failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ py: 3 }}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Profile
          </Typography>

          {message && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {message}
            </Alert>
          )}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSave}>
            <TextField
              label="Name"
              fullWidth
              margin="normal"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <TextField
              label="Phone"
              fullWidth
              margin="normal"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
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
            <TextField
              label="New Password"
              type="password"
              fullWidth
              margin="normal"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              helperText="Leave blank to keep current password"
              autoComplete="new-password"
            />
            <Button
              type="submit"
              variant="contained"
              fullWidth
              sx={{ mt: 2 }}
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </Button>
          </Box>

          <Divider sx={{ my: 3 }} />

          <Button
            variant="outlined"
            color="error"
            fullWidth
            onClick={logout}
          >
            Logout
          </Button>
        </Paper>
      </Box>
    </Container>
  );
}
