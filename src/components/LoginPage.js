import React from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Container,
  Avatar,
  Divider,
  Chip
} from '@mui/material';
import { Google as GoogleIcon, Security, Business, Cloud } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

export default function LoginPage() {
  const { login } = useAuth();

  return (
    <Box
      sx={{
        background: 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #06b6d4 100%)',
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 25% 25%, rgba(255,255,255,0.1) 0%, transparent 50%), radial-gradient(circle at 75% 75%, rgba(255,255,255,0.05) 0%, transparent 50%)',
          opacity: 0.8,
        },
      }}
    >
      <Container maxWidth="sm">
        <Card 
          elevation={20}
          sx={{
            background: 'rgba(255, 255, 255, 0.98)',
            backdropFilter: 'blur(15px)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: 3,
            overflow: 'hidden',
            position: 'relative',
          }}
        >
          {/* Header Banner */}
          <Box
            sx={{
              background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
              py: 4,
              px: 3,
              textAlign: 'center',
              color: 'white',
              position: 'relative',
              '&::after': {
                content: '""',
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                height: '3px',
                background: 'linear-gradient(90deg, #06b6d4, #10b981, #06b6d4)',
              },
            }}
          >
            <Avatar
              sx={{
                width: 64,
                height: 64,
                margin: '0 auto 16px',
                background: 'rgba(255, 255, 255, 0.15)',
                border: '2px solid rgba(255, 255, 255, 0.3)',
                fontSize: '1.8rem',
              }}
            >
              🔧
            </Avatar>
            
            <Typography 
              variant="h4" 
              component="h1" 
              sx={{
                fontWeight: 700,
                mb: 1,
                textShadow: '0 2px 4px rgba(0,0,0,0.1)',
              }}
            >
              INFOSONIK
            </Typography>
            
            <Typography 
              variant="subtitle1" 
              sx={{
                opacity: 0.95,
                fontWeight: 500,
                letterSpacing: '0.5px',
              }}
            >
              SYSTEMS LIMITED
            </Typography>
          </Box>
          
          <CardContent sx={{ p: 4 }}>
            {/* Service Tags */}
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, mb: 3, flexWrap: 'wrap' }}>
              <Chip 
                icon={<Business />} 
                label="IT Solutions" 
                size="small" 
                sx={{ 
                  background: 'linear-gradient(135deg, #e0f2fe, #b3e5fc)',
                  color: '#0277bd',
                  border: '1px solid #81d4fa'
                }} 
              />
              <Chip 
                icon={<Cloud />} 
                label="Cloud Services" 
                size="small" 
                sx={{ 
                  background: 'linear-gradient(135deg, #e8f5e8, #c8e6c9)',
                  color: '#2e7d32',
                  border: '1px solid #a5d6a7'
                }} 
              />
              <Chip 
                icon={<Security />} 
                label="Secure" 
                size="small" 
                sx={{ 
                  background: 'linear-gradient(135deg, #fce4ec, #f8bbd9)',
                  color: '#c2185b',
                  border: '1px solid #f48fb1'
                }} 
              />
            </Box>
            
            <Typography 
              variant="h5" 
              component="h2" 
              gutterBottom
              sx={{
                fontWeight: 600,
                color: '#1e40af',
                textAlign: 'center',
                mb: 2,
              }}
            >
              Notes & Calendar Platform
            </Typography>
            
            <Typography 
              variant="body1" 
              color="textSecondary" 
              sx={{ 
                mb: 4, 
                maxWidth: 420, 
                mx: 'auto',
                textAlign: 'center',
                lineHeight: 1.6,
                fontSize: '0.95rem',
              }}
            >
              Professional workspace for Infosonik team collaboration. Manage notes, 
              calendar events, documents, and integrate seamlessly with Google Workspace 
              for enhanced productivity.
            </Typography>
            
            <Divider sx={{ mb: 3, opacity: 0.3 }} />
            
            <Box sx={{ textAlign: 'center' }}>
              <Button
                variant="contained"
                size="large"
                startIcon={<GoogleIcon />}
                onClick={login}
                sx={{
                  py: 1.8,
                  px: 5,
                  fontSize: '1rem',
                  borderRadius: 2,
                  textTransform: 'none',
                  fontWeight: 600,
                  background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
                  boxShadow: '0 8px 24px rgba(59, 130, 246, 0.4)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 12px 32px rgba(59, 130, 246, 0.5)',
                  },
                  transition: 'all 0.3s ease-in-out',
                }}
              >
                Sign in with Google Workspace
              </Button>
              
              <Typography 
                variant="caption" 
                display="block" 
                color="textSecondary" 
                sx={{ 
                  mt: 3, 
                  opacity: 0.7,
                  fontSize: '0.8rem',
                  background: 'rgba(30, 64, 175, 0.05)',
                  padding: '8px 16px',
                  borderRadius: 2,
                  border: '1px solid rgba(30, 64, 175, 0.1)',
                }}
              >
                🔒 Access restricted to @infosonik.com accounts only
              </Typography>
            </Box>
            
            {/* Footer */}
            <Box sx={{ mt: 4, pt: 3, borderTop: '1px solid rgba(0,0,0,0.06)', textAlign: 'center' }}>
              <Typography 
                variant="caption" 
                color="textSecondary"
                sx={{ 
                  opacity: 0.6,
                  fontSize: '0.75rem',
                }}
              >
                Powered by Infosonik Systems Limited • Professional IT Solutions
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
}
