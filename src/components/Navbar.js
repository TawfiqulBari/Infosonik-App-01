import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Box,
  Divider,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Home,
  Notes,
  Event,
  Folder,
  Settings,
  Backup,
  Logout,
  DarkMode,
  LightMode,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';

const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Notes', href: '/notes', icon: Notes },
  { name: 'Calendar', href: '/calendar', icon: Event },
  { name: 'Files', href: '/files', icon: Folder },
  { name: 'Backup', href: '/backup', icon: Backup },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const { theme, toggleTheme, isDark } = useTheme();
  const [anchorEl, setAnchorEl] = useState(null);

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleMenuClose();
    logout();
  };

  return (
    <AppBar position="sticky" elevation={0} sx={{ backdropFilter: 'blur(10px)' }}>
      <Toolbar>
        <Typography
          variant="h6"
          component="div"
          sx={{
            fontWeight: 700,
            background: 'linear-gradient(135deg, #ffffff, #e5e7eb)',
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            mr: 4,
          }}
        >
          📝 Infosonik
        </Typography>

        <Box sx={{ display: 'flex', gap: 1, flexGrow: 1 }}>
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.href;
            
            return (
              <Button
                key={item.name}
                startIcon={<Icon />}
                onClick={() => navigate(item.href)}
                sx={{
                  color: isActive ? 'primary.main' : 'inherit',
                  backgroundColor: isActive ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  },
                  textTransform: 'none',
                  borderRadius: 2,
                }}
              >
                {item.name}
              </Button>
            );
          })}
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton onClick={toggleTheme} color="inherit">
            {isDark ? <LightMode /> : <DarkMode />}
          </IconButton>

          <IconButton onClick={handleMenuOpen}>
            <Avatar
              src={user?.profile_picture}
              alt={user?.name}
              sx={{ width: 32, height: 32 }}
            >
              {user?.name?.charAt(0)}
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
            anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
            transformOrigin={{ vertical: 'top', horizontal: 'right' }}
            sx={{ mt: 1 }}
          >
            <MenuItem disabled>
              <Box>
                <Typography variant="subtitle2">{user?.name}</Typography>
                <Typography variant="caption" color="textSecondary">
                  {user?.email}
                </Typography>
              </Box>
            </MenuItem>
            <Divider />
            <MenuItem>
              <FormControlLabel
                control={
                  <Switch
                    checked={isDark}
                    onChange={toggleTheme}
                    size="small"
                  />
                }
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {isDark ? <DarkMode fontSize="small" /> : <LightMode fontSize="small" />}
                    Dark Mode
                  </Box>
                }
              />
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleLogout}>
              <Logout fontSize="small" sx={{ mr: 1 }} />
              Logout
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
