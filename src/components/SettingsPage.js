import React, { useState } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  FormControlLabel,
  Switch,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Box,
  Divider,
} from '@mui/material';
import { Save } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { toast } from 'react-toastify';

export default function SettingsPage() {
  const { user, updatePreferences } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [preferences, setPreferences] = useState({
    theme: user?.preferences?.theme || 'light',
    language: user?.preferences?.language || 'en',
    notifications: user?.preferences?.notifications !== false,
    backup_frequency: user?.preferences?.backup_frequency || 'daily',
  });

  const handleSave = async () => {
    await updatePreferences(preferences);
  };

  return (
    <Container maxWidth="md">
      <Typography variant="h4" component="h1" gutterBottom>
        Settings
      </Typography>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Appearance
          </Typography>
          
          <FormControlLabel
            control={
              <Switch
                checked={preferences.theme === 'dark'}
                onChange={(e) => {
                  const newTheme = e.target.checked ? 'dark' : 'light';
                  setPreferences({ ...preferences, theme: newTheme });
                  if (newTheme !== theme) {
                    toggleTheme();
                  }
                }}
              />
            }
            label="Dark Mode"
            sx={{ mb: 2 }}
          />

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            Language & Region
          </Typography>
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Default Language</InputLabel>
            <Select
              value={preferences.language}
              label="Default Language"
              onChange={(e) => setPreferences({ ...preferences, language: e.target.value })}
            >
              <MenuItem value="en">English</MenuItem>
              <MenuItem value="bn">Bangla</MenuItem>
            </Select>
          </FormControl>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            Notifications
          </Typography>
          
          <FormControlLabel
            control={
              <Switch
                checked={preferences.notifications}
                onChange={(e) => setPreferences({ ...preferences, notifications: e.target.checked })}
              />
            }
            label="Enable Notifications"
            sx={{ mb: 2 }}
          />

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            Backup Settings
          </Typography>
          
          <FormControl fullWidth sx={{ mb: 3 }}>
            <InputLabel>Auto-backup Frequency</InputLabel>
            <Select
              value={preferences.backup_frequency}
              label="Auto-backup Frequency"
              onChange={(e) => setPreferences({ ...preferences, backup_frequency: e.target.value })}
            >
              <MenuItem value="daily">Daily</MenuItem>
              <MenuItem value="weekly">Weekly</MenuItem>
              <MenuItem value="monthly">Monthly</MenuItem>
              <MenuItem value="manual">Manual Only</MenuItem>
            </Select>
          </FormControl>

          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              startIcon={<Save />}
              onClick={handleSave}
            >
              Save Changes
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
}
