import React, { useEffect, useState } from 'react';
import { Container, Typography, Box, CircularProgress, List, ListItem, ListItemText, Button } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import { toast } from 'react-toastify';

export default function EmailPage() {
  const { token } = useAuth();
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchEmails();
  }, []);

  const fetchEmails = async () => {
    setLoading(true);
    try {
      const response = await api.get('/gmail/messages', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setEmails(response.data);
    } catch (error) {
      console.error('Error fetching emails:', error);
      toast.error('Failed to load emails');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container>
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="md">
      <Typography variant="h4" gutterBottom>
        Your Emails
      </Typography>
      <List>
        {emails.map((email) => (
          <ListItem key={email.id} divider>
            <ListItemText
              primary={`Subject: ${email.subject}`}
              secondary={`From: ${email.sender} | Received: ${new Date(email.timestamp).toLocaleString()}`}
            />
            <Button variant="contained">View</Button>
          </ListItem>
        ))}
      </List>
    </Container>
  );
}

