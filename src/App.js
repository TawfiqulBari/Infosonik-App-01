import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box } from '@mui/material';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import AuthProvider, { useAuth } from './contexts/AuthContext';
import CustomThemeProvider, { useTheme } from './contexts/ThemeContext';
import LoginPage from './components/LoginPage';
import Dashboard from './components/Dashboard';
import Navbar from './components/Navbar';
import NotesPage from './components/NotesPage';
import CalendarPage from './components/CalendarPage';
import FilesPage from './components/FilesPage';
import SettingsPage from './components/SettingsPage';
import BackupPage from './components/BackupPage';

function AppContent() {
  const { user, loading } = useAuth();
  const { theme } = useTheme();

  const muiTheme = createTheme({
    palette: {
      mode: theme,
      primary: {
        main: '#3b82f6',
      },
      secondary: {
        main: '#8b5cf6',
      },
      background: {
        default: theme === 'dark' ? '#1a1a1a' : '#f5f5f5',
        paper: theme === 'dark' ? '#2d2d2d' : '#ffffff',
      },
    },
    typography: {
      fontFamily: 'Inter, sans-serif',
    },
  });

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        className="gradient-bg"
      >
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </Box>
    );
  }

  return (
    <ThemeProvider theme={muiTheme}>
      <CssBaseline />
      <Router>
        {!user ? (
          <LoginPage />
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
            <Navbar />
            <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/notes" element={<NotesPage />} />
                <Route path="/calendar" element={<CalendarPage />} />
                <Route path="/files" element={<FilesPage />} />
                <Route path="/settings" element={<SettingsPage />} />
                <Route path="/backup" element={<BackupPage />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Box>
          </Box>
        )}
      </Router>
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme={theme}
      />
    </ThemeProvider>
  );
}

function App() {
  return (
    <AuthProvider>
      <CustomThemeProvider>
        <AppContent />
      </CustomThemeProvider>
    </AuthProvider>
  );
}

export default App;
