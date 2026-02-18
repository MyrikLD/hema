import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import {
  AppBar,
  BottomNavigation,
  BottomNavigationAction,
  Box,
  Paper,
  Toolbar,
  Typography,
  useMediaQuery,
  useTheme,
  IconButton,
} from '@mui/material';
import {
  CalendarMonth,
  History,
  Person,
  Logout,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

function getNavValue(pathname: string): number {
  if (pathname.startsWith('/history')) return 1;
  if (pathname.startsWith('/profile')) return 2;
  return 0;
}

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const navValue = getNavValue(location.pathname);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="fixed" color="primary">
        <Toolbar variant="dense">
          <Typography
            variant="h6"
            sx={{ flexGrow: 1, cursor: 'pointer', fontSize: '1rem' }}
            onClick={() => navigate('/')}
          >
            HEMA Training
          </Typography>
          {!isMobile && (
            <>
              <IconButton color="inherit" onClick={() => navigate('/')}>
                <CalendarMonth />
              </IconButton>
              <IconButton color="inherit" onClick={() => navigate('/history')}>
                <History />
              </IconButton>
              <IconButton color="inherit" onClick={() => navigate('/profile')}>
                <Person />
              </IconButton>
              <IconButton color="inherit" onClick={logout}>
                <Logout />
              </IconButton>
            </>
          )}
        </Toolbar>
      </AppBar>

      <Toolbar variant="dense" />
      <Box sx={{ flex: 1, overflow: 'auto', pb: isMobile ? 7 : 0 }}>
        <Outlet />
      </Box>

      {isMobile && (
        <Paper
          sx={{ position: 'fixed', bottom: 0, left: 0, right: 0, zIndex: 1100 }}
          elevation={3}
        >
          <BottomNavigation
            value={navValue}
            onChange={(_, val) => {
              if (val === 0) navigate('/');
              else if (val === 1) navigate('/history');
              else if (val === 2) navigate('/profile');
            }}
            showLabels
          >
            <BottomNavigationAction label="Calendar" icon={<CalendarMonth />} />
            <BottomNavigationAction label="History" icon={<History />} />
            <BottomNavigationAction label="Profile" icon={<Person />} />
          </BottomNavigation>
        </Paper>
      )}
    </Box>
  );
}
