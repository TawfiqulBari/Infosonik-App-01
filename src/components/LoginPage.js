import React from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Container,
  Avatar
} from '@mui/material';
import { Google as GoogleIcon } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const { login } = useAuth();

  return (
    <Box
      className="gradient-bg min-h-screen flex items-center justify-center"
      sx={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <Container maxWidth="sm">
        <Card 
          className="glass-effect animate-fade-in"
          sx={{
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: 4,
            p: 4,
          }}
        >
          <CardContent sx={{ textAlign: 'center', p: 4 }}>
            <Avatar
              sx={{
                width: 80,
                height: 80,
                margin: '0 auto 24px',
                background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                fontSize: '2rem',
              }}
            >
              📝
            </Avatar>
            
            <Typography 
              variant="h3" 
              component="h1" 
              gutterBottom
              sx={{
                fontWeight: 700,
                background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Infosonik
            </Typography>
            
            <Typography 
              variant="h5" 
              component="h2" 
              gutterBottom
              color="textSecondary"
              sx={{ mb: 3 }}
            >
              Notes & Calendar App
            </Typography>
            
            <Typography 
              variant="body1" 
              color="textSecondary" 
              sx={{ mb: 4, maxWidth: 400, mx: 'auto' }}
            >
              Secure workspace for Infosonik team members. Manage your notes, 
              calendar events, files, and collaborate seamlessly with Google integration.
            </Typography>
            
            <Button
              variant="contained"
              size="large"
              startIcon={<GoogleIcon />}
              onClick={login}
              sx={{
                py: 1.5,
                px: 4,
                fontSize: '1.1rem',
                borderRadius: 3,
                textTransform: 'none',
                background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #2563eb, #7c3aed)',
                  transform: 'translateY(-2px)',
                },
                transition: 'all 0.2s ease-in-out',
              }}
            >
              Sign in with Google Workspace
            </Button>
            
            <Typography 
              variant="caption" 
              display="block" 
              color="textSecondary" 
              sx={{ mt: 3, opacity: 0.7 }}
            >
              Access restricted to @infosonik.com accounts only
            </Typography>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
}
