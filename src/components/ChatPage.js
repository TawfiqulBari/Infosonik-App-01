import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemText,
  Divider,
  TextField,
  Chip,
  CircularProgress,
  Avatar,
} from '@mui/material';
import {
  Chat as ChatIcon,
  Send,
  Refresh,
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import api from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

export default function ChatPage() {
  const { user, token } = useAuth();
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newMessage, setNewMessage] = useState('');

  useEffect(() => {
    fetchChatMessages();
  }, []);

  const fetchChatMessages = async () => {
    setLoading(true);
    try {
      const response = await api.get('/chat/messages', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessages(response.data);
    } catch (error) {
      console.error('Error fetching chat messages:', error);
      toast.error('Failed to load chat messages');
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim()) return;
    try {
      const response = await api.post(
        '/chat/messages',
        { content: newMessage },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessages([...messages, response.data]);
      setNewMessage('');
      toast.success('Message sent');
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message');
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mb: 4 }}>
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mb: 3,
          }}
        >
          <Typography
            variant="h4"
            component="h1"
            gutterBottom
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
            }}
          >
            <ChatIcon color="primary" /> Google Chat
          </Typography>
          <Button startIcon={<Refresh />} onClick={fetchChatMessages} variant="outlined">
            Refresh
          </Button>
        </Box>

        <Card sx={{ mb: 3, maxHeight: 400, overflow: 'auto' }}>
          <CardContent>
            {loading ? (
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  minHeight: '60vh',
                }}
              >
                <CircularProgress />
              </Box>
            ) : (
              <List>
                {messages.map((msg) => (
                  <React.Fragment key={msg.id}>
                    <ListItem alignItems="flex-start">
                      <Avatar alt={msg.sender.name} src={msg.sender.avatar} />
                      <ListItemText
                        primary={<><strong>{msg.sender.name}</strong> <small>{new Date(msg.timestamp).toLocaleString()}</small></>}
                        secondary={<Typography component="span" variant="body2" color="text.primary">{msg.content}</Typography>}
                      />
                    </ListItem>
                    <Divider variant="inset" component="li" />
                  </React.Fragment>
                ))}
              </List>
            )}
          </CardContent>
        </Card>

        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
          }}
        >
          <TextField
            variant="outlined"
            placeholder="Type your message..."
            fullWidth
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
          />
          <Button
            startIcon={<Send />}
            onClick={sendMessage}
            sx={{ ml: 1 }}
            variant="contained"
          >
            Send
          </Button>
        </Box>
      </Box>
    </Container>
  );
}
