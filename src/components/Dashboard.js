import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Box,
  Avatar,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Alert,
  IconButton,
  Badge,
  Divider,
} from '@mui/material';
import {
  Notes as NotesIcon,
  Event as EventIcon,
  Folder as FolderIcon,
  Add,
  Description,
  Schedule,
  AttachFile,
  Email as EmailIcon,
  MailOutline as MailOutlineIcon,
  Person as PersonIcon,
  Refresh as RefreshIcon,
  Notifications as NotificationsIcon,
} from '@mui/icons-material';
import axios from 'axios';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { format, formatDistanceToNow } from 'date-fns';
import api from '../utils/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState({
    notes: 0,
    events: 0,
    files: 0,
    unread_emails: 0,
  });
  const [recentNotes, setRecentNotes] = useState([]);
  const [recentEvents, setRecentEvents] = useState([]);
  const [emailNotifications, setEmailNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [emailLoading, setEmailLoading] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    fetchEmailNotifications();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [notesRes, eventsRes, filesRes] = await Promise.all([
        axios.get('/notes/'),
        axios.get('/events/'),
        axios.get('/files/'),
      ]);

      setStats(prevStats => ({
        ...prevStats,
        notes: notesRes.data.length,
        events: eventsRes.data.length,
        files: filesRes.data.length,
      }));

      setRecentNotes(notesRes.data.slice(0, 5));
      setRecentEvents(eventsRes.data.slice(0, 5));
    } catch (error) {
      toast.error('Failed to load dashboard data');
      console.error('Dashboard error:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchEmailNotifications = async () => {
    setEmailLoading(true);
    try {
      const response = await api.get('/gmail/unread-notifications');
      setEmailNotifications(response.data.recent_emails || []);
      setStats(prevStats => ({
        ...prevStats,
        unread_emails: response.data.total_unread || 0,
      }));
    } catch (error) {
      console.error('Failed to fetch email notifications:', error);
      // Don't show error to user, just continue without email data
    } finally {
      setEmailLoading(false);
    }
  };

  const formatEmailDate = (timestamp) => {
    try {
      const date = new Date(parseInt(timestamp));
      return formatDistanceToNow(date, { addSuffix: true });
    } catch (error) {
      return 'Unknown time';
    }
  };

  const StatCard = ({ icon, title, value, color, onClick, isLoading = false }) => (
    <Card
      sx={{
        cursor: 'pointer',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 4,
        },
      }}
      onClick={onClick}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Avatar sx={{ bgcolor: color, mr: 2 }}>
            {icon}
          </Avatar>
          <Typography variant="h6" component="div">
            {title}
          </Typography>
          {isLoading && (
            <IconButton size="small" sx={{ ml: 'auto' }}>
              <RefreshIcon className="animate-spin" />
            </IconButton>
          )}
        </Box>
        <Typography variant="h3" component="div" color={color}>
          {value}
        </Typography>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Container>
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Box sx={{ 
          background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
          color: 'white',
          p: 4,
          borderRadius: 3,
          mb: 3,
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            right: 0,
            width: '200px',
            height: '200px',
            background: 'rgba(255, 255, 255, 0.05)',
            borderRadius: '50%',
            transform: 'translate(50%, -50%)',
          },
        }}>
          <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
            Welcome back, {user?.name?.split(' ')[0]}! 👋
          </Typography>
          <Typography variant="h6" sx={{ opacity: 0.9, mb: 2 }}>
            Infosonik Systems Limited - Professional Workspace
          </Typography>
          <Typography variant="body1" sx={{ opacity: 0.8 }}>
            Your centralized hub for notes, calendar events, documents, and team collaboration.
          </Typography>
        </Box>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<NotesIcon />}
            title="Notes"
            value={stats.notes}
            color="primary.main"
            onClick={() => navigate('/notes')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<EventIcon />}
            title="Events"
            value={stats.events}
            color="secondary.main"
            onClick={() => navigate('/calendar')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<FolderIcon />}
            title="Files"
            value={stats.files}
            color="success.main"
            onClick={() => navigate('/files')}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={
              <Badge badgeContent={stats.unread_emails > 0 ? stats.unread_emails : 0} color="error">
                <EmailIcon />
              </Badge>
            }
            title="Unread Emails"
            value={stats.unread_emails}
            color="warning.main"
            onClick={() => navigate('/email')}
            isLoading={emailLoading}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" component="h2">
                  Recent Notes
                </Typography>
                <Button
                  startIcon={<Add />}
                  onClick={() => navigate('/notes')}
                  size="small"
                >
                  New Note
                </Button>
              </Box>
              {recentNotes.length === 0 ? (
                <Typography color="textSecondary">
                  No notes yet. Create your first note!
                </Typography>
              ) : (
                <List dense>
                  {recentNotes.map((note) => (
                    <ListItem key={note.id} sx={{ px: 0 }}>
                      <ListItemIcon>
                        <Description color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={note.title}
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                            <Chip
                              label={note.language.toUpperCase()}
                              size="small"
                              color="primary"
                              variant="outlined"
                            />
                            <Typography variant="caption" color="textSecondary">
                              {format(new Date(note.created_at), 'MMM dd, yyyy')}
                            </Typography>
                            {note.attachments?.length > 0 && (
                              <AttachFile sx={{ fontSize: 16 }} color="action" />
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" component="h2">
                  Upcoming Events
                </Typography>
                <Button
                  startIcon={<Add />}
                  onClick={() => navigate('/calendar')}
                  size="small"
                >
                  New Event
                </Button>
              </Box>
              {recentEvents.length === 0 ? (
                <Typography color="textSecondary">
                  No events scheduled. Create your first event!
                </Typography>
              ) : (
                <List dense>
                  {recentEvents.map((event) => (
                    <ListItem key={event.id} sx={{ px: 0 }}>
                      <ListItemIcon>
                        <Schedule color="secondary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={event.title}
                        secondary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                            <Typography variant="caption" color="textSecondary">
                              {format(new Date(event.start_time), 'MMM dd, yyyy HH:mm')}
                            </Typography>
                            {event.attachments?.length > 0 && (
                              <AttachFile sx={{ fontSize: 16 }} color="action" />
                            )}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" component="h2">
                  <Badge badgeContent={stats.unread_emails} color="error">
                    <NotificationsIcon sx={{ mr: 1 }} />
                  </Badge>
                  Recent Emails
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <IconButton 
                    onClick={fetchEmailNotifications}
                    size="small"
                    disabled={emailLoading}
                  >
                    <RefreshIcon className={emailLoading ? 'animate-spin' : ''} />
                  </IconButton>
                  <Button
                    startIcon={<EmailIcon />}
                    onClick={() => navigate('/email')}
                    size="small"
                  >
                    View All
                  </Button>
                </Box>
              </Box>
              
              {emailLoading ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                </Box>
              ) : emailNotifications.length === 0 ? (
                <Box sx={{ textAlign: 'center', p: 2 }}>
                  <MailOutlineIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                  <Typography color="textSecondary">
                    No new emails! 📭
                  </Typography>
                </Box>
              ) : (
                <List dense>
                  {emailNotifications.map((email) => (
                    <ListItem 
                      key={email.id} 
                      sx={{ 
                        px: 0,
                        cursor: 'pointer',
                        '&:hover': { backgroundColor: 'action.hover' },
                        borderRadius: 1
                      }}
                      onClick={() => navigate('/email')}
                    >
                      <ListItemIcon>
                        <Avatar sx={{ width: 32, height: 32, bgcolor: 'warning.main' }}>
                          <MailOutlineIcon sx={{ fontSize: 16 }} />
                        </Avatar>
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Typography 
                            variant="body2" 
                            sx={{ 
                              fontWeight: 600,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap'
                            }}
                          >
                            {email.subject || '(No Subject)'}
                          </Typography>
                        }
                        secondary={
                          <Box>
                            <Typography 
                              variant="caption" 
                              color="textSecondary"
                              sx={{
                                display: 'block',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap'
                              }}
                            >
                              From: {email.from.split('<')[0].trim() || email.from}
                            </Typography>
                            <Typography 
                              variant="caption" 
                              color="textSecondary"
                              sx={{
                                display: 'block',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap'
                              }}
                            >
                              {email.snippet}
                            </Typography>
                            <Typography variant="caption" color="primary.main" sx={{ fontWeight: 500 }}>
                              {formatEmailDate(email.timestamp)}
                            </Typography>
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              )}
              
              {stats.unread_emails > emailNotifications.length && (
                <>
                  <Divider sx={{ my: 1 }} />
                  <Alert severity="info" sx={{ mt: 2 }}>
                    {stats.unread_emails - emailNotifications.length} more unread emails
                  </Alert>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
}
