import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    primary: {
      main: '#2c3e50',
    },
    secondary: {
      main: '#4CAF50',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiBottomNavigation: {
      styleOverrides: {
        root: {
          borderTop: '1px solid #e0e0e0',
        },
      },
    },
  },
});

export default theme;
