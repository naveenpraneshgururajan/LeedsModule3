/**
 * Material-UI Theme Configuration
 */

import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2', // Blue
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e', // Pink/Red
      light: '#ff5983',
      dark: '#9a0036',
    },
    success: {
      main: '#4caf50', // Green
      light: '#81c784',
      dark: '#388e3c',
    },
    warning: {
      main: '#ff9800', // Orange
      light: '#ffb74d',
      dark: '#f57c00',
    },
    error: {
      main: '#f44336', // Red
      light: '#e57373',
      dark: '#d32f2f',
    },
    info: {
      main: '#2196f3', // Light Blue
      light: '#64b5f6',
      dark: '#1976d2',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 500,
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 500,
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 500,
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none', // Disable uppercase
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

// Health status colors
export const healthColors = {
  healthy: '#4caf50',   // Green
  warning: '#ff9800',   // Orange
  critical: '#f44336',  // Red
};

// Environment type colors
export const envTypeColors = {
  dev: '#2196f3',       // Blue
  cit: '#ff9800',       // Orange
  sit: '#9c27b0',       // Purple
  luat: '#f44336',      // Red
  prod: '#4caf50',      // Green
  unknown: '#9e9e9e',   // Grey
};
