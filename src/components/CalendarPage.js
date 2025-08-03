import React, { useState, useEffect, useContext } from 'react';
import {
  Container,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Box,
  Card,
  CardContent,
  Grid,
  Chip,
  CircularProgress,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Avatar,
  Paper,
  Fab,
  Badge,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
} from '@mui/material';
import {
  Add,
  Event as EventIcon,
  Refresh,
  Share,
  Person,
  CalendarToday,
  AccessTime,
  Description,
  Google,
  Edit,
  Delete,
  Visibility,
} from '@mui/icons-material';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import api from '../utils/api';
import { toast } from 'react-toastify';
import { format, addDays, startOfWeek, endOfWeek, eachDayOfInterval } from 'date-fns';
import { AuthContext } from '../contexts/AuthContext';

export default function CalendarPage() {
  const { token } = useContext(AuthContext);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    start_time: '',
    end_time: '',
  });

  useEffect(() => {
    if (token) {
      fetchEvents();
    }
  }, [token]);

  const fetchEvents = async () => {
    if (!token) {
      toast.error('Please log in to view events');
      return;
    }

    setLoading(true);
    try {
      const response = await api.get('/events/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setEvents(response.data);
      toast.success(`Loaded ${response.data.length} events (including Google Calendar)`);
    } catch (error) {
      toast.error('Failed to fetch events');
      console.error('Fetch events error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!token) {
      toast.error('Please log in to create events');
      return;
    }

    try {
      await api.post('/events/', formData, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      toast.success('Event created successfully');
      fetchEvents();
      setDialogOpen(false);
      setFormData({ title: '', description: '', start_time: '', end_time: '' });
    } catch (error) {
      toast.error('Failed to create event');
      console.error('Create event error:', error);
    }
  };

  const shareEvent = async (eventId) => {
    if (!token) {
      toast.error('Please log in to share events');
      return;
    }

    try {
      const response = await api.post(`/events/${eventId}/share`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      toast.success(response.data.message || 'Event shared successfully');
    } catch (error) {
      toast.error('Failed to share event');
      console.error('Share event error:', error);
    }
  };

  const eventsForSelectedDate = events.filter(event =>
    format(new Date(event.start_time), 'yyyy-MM-dd') === format(selectedDate, 'yyyy-MM-dd')
  );

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Calendar {loading && <CircularProgress size={24} sx={{ ml: 2 }} />}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchEvents}
            disabled={loading || !token}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setDialogOpen(true)}
            disabled={!token}
          >
            New Event
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Calendar
                onChange={setSelectedDate}
                value={selectedDate}
                className="w-full"
              />
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Events for {format(selectedDate, 'MMM dd, yyyy')}
              </Typography>
              {eventsForSelectedDate.length === 0 ? (
                <Typography color="textSecondary">
                  No events scheduled for this day.
                </Typography>
              ) : (
                eventsForSelectedDate.map((event) => (
                  <Box key={event.id} sx={{ mb: 2, p: 2, border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle1">{event.title}</Typography>
                        {event.google_event_id && event.id < 0 && (
                          <Chip size="small" label="Google" color="primary" variant="outlined" />
                        )}
                      </Box>
                      {event.id > 0 && (
                        <Tooltip title="Share Event">
                          <IconButton 
                            size="small" 
                            onClick={() => shareEvent(event.id)}
                            sx={{ color: 'primary.main' }}
                          >
                            <Share fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Box>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                      {event.description || 'No description'}
                    </Typography>
                    <Typography variant="caption">
                      {format(new Date(event.start_time), 'HH:mm')} - {format(new Date(event.end_time), 'HH:mm')}
                    </Typography>
                  </Box>
                ))
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Create New Event</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Description"
              multiline
              rows={3}
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Start Time"
              type="datetime-local"
              value={formData.start_time}
              onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
              InputLabelProps={{ shrink: true }}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="End Time"
              type="datetime-local"
              value={formData.end_time}
              onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
              InputLabelProps={{ shrink: true }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">Create</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
