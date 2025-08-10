import React, { useEffect, useState, useMemo, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  IconButton,
  TextField,
  InputAdornment,
  Chip,
  Avatar,
  Divider,
  Button,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Drawer,
  Toolbar,
  Badge,
  Fab,
  CircularProgress,
  Tooltip,
  FormControl,
  Select,
  Alert,
  useTheme,
  useMediaQuery,
  Autocomplete,
  ListItemAvatar,
} from '@mui/material';
import {
  Inbox as InboxIcon,
  Send as SendIcon,
  Drafts as DraftsIcon,
  Delete as DeleteIcon,
  Star as StarIcon,
  StarBorder as StarBorderIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  MoreVert as MoreVertIcon,
  Reply as ReplyIcon,
  Forward as ForwardIcon,
  Archive as ArchiveIcon,
  Label as LabelIcon,
  Attachment as AttachmentIcon,
  Edit as EditIcon,
  Close as CloseIcon,
  Email as EmailIcon,
  MailOutline as MailOutlineIcon,
  Menu as MenuIcon,
  ArrowBack as ArrowBackIcon,
  Contacts as ContactsIcon,
  Person as PersonIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import { toast } from 'react-toastify';
import { format, isToday, isYesterday } from 'date-fns';

const DRAWER_WIDTH = 280;

export default function EmailPage() {
  const { user } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.down('lg'));
  
  // State management
  const [selectedFolder, setSelectedFolder] = useState('inbox');
  const [folders, setFolders] = useState([
    { id: 'inbox', name: 'Inbox', icon: 'inbox', count: 0, color: '#1976d2' },
    { id: 'sent', name: 'Sent Items', icon: 'send', count: 0, color: '#388e3c' },
    { id: 'drafts', name: 'Drafts', icon: 'drafts', count: 0, color: '#f57c00' },
    { id: 'starred', name: 'Starred', icon: 'star', count: 0, color: '#fbc02d' },
    { id: 'trash', name: 'Deleted Items', icon: 'delete', count: 0, color: '#d32f2f' },
  ]);
  const [emails, setEmails] = useState([]);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [composeOpen, setComposeOpen] = useState(false);
  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  const [sortBy, setSortBy] = useState('timestamp');
  const [filterBy, setFilterBy] = useState('all');
  const [mobileOpen, setMobileOpen] = useState(false);
  const [error, setError] = useState(null);
  const [contacts, setContacts] = useState([]);
  const [contactsLoading, setContactsLoading] = useState(false);

  // Compose email state - using useCallback to prevent recreating on every render
  const [composeData, setComposeData] = useState({
    to: '',
    cc: '',
    bcc: '',
    subject: '',
    body: '',
    attachments: []
  });

  // Load folders and emails on mount
  useEffect(() => {
    loadFolders();
    loadEmails();
    loadContacts();
  }, [selectedFolder]);

  const loadFolders = useCallback(async () => {
    try {
      const response = await api.get('/gmail/folders');
      setFolders(response.data);
    } catch (error) {
      console.error('Failed to load folders:', error);
      // Keep default folders if API fails
    }
  }, []);

  const loadEmails = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get('/gmail/messages', {
        params: {
          max_results: 50
        }
      });
      
      // Transform the backend response to match our component structure
      const transformedEmails = response.data.map(email => {
        // Parse sender info
        const senderMatch = email.sender.match(/(.*?)\s*<(.+?)>/) || [null, email.sender, email.sender];
        const senderName = senderMatch[1]?.trim() || email.sender;
        const senderEmail = senderMatch[2] || email.sender;

        return {
          id: email.id,
          from: {
            name: senderName,
            email: senderEmail
          },
          to: [{ email: email.recipient }],
          subject: email.subject,
          preview: email.body ? email.body.substring(0, 200) + '...' : '',
          body: email.body || '',
          timestamp: new Date(email.timestamp),
          isRead: email.is_read,
          isStarred: false, // Will be updated when we have label info
          hasAttachments: email.has_attachments,
          folder: selectedFolder,
          labels: []
        };
      });
      
      setEmails(transformedEmails);
      setError(null);
    } catch (error) {
      console.error('Failed to load emails:', error);
      setError('Failed to load emails. Please try again.');
      toast.error('Failed to load emails');
    } finally {
      setLoading(false);
    }
  }, [selectedFolder]);

  const loadContacts = useCallback(async () => {
    setContactsLoading(true);
    try {
      const response = await api.get('/contacts');
      setContacts(response.data);
    } catch (error) {
      console.error('Failed to load contacts:', error);
      // Don't show error to user, just continue without contacts
    } finally {
      setContactsLoading(false);
    }
  }, []);

  const filteredEmails = useMemo(() => {
    let filtered = emails.filter(email => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          email.subject.toLowerCase().includes(query) ||
          email.from.name.toLowerCase().includes(query) ||
          email.from.email.toLowerCase().includes(query) ||
          email.preview.toLowerCase().includes(query)
        );
      }
      
      // Additional filters
      if (filterBy === 'unread' && email.isRead) return false;
      if (filterBy === 'starred' && !email.isStarred) return false;
      if (filterBy === 'attachments' && !email.hasAttachments) return false;
      
      return true;
    });

    // Sort emails
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'timestamp':
          return new Date(b.timestamp) - new Date(a.timestamp);
        case 'sender':
          return a.from.name.localeCompare(b.from.name);
        case 'subject':
          return a.subject.localeCompare(b.subject);
        default:
          return 0;
      }
    });

    return filtered;
  }, [emails, searchQuery, sortBy, filterBy]);

  const formatEmailDate = useCallback((date) => {
    try {
      if (isToday(date)) {
        return format(date, 'h:mm a');
      } else if (isYesterday(date)) {
        return 'Yesterday';
      } else {
        return format(date, 'MMM dd');
      }
    } catch (error) {
      return 'Unknown';
    }
  }, []);

  const handleEmailClick = useCallback(async (email) => {
    setSelectedEmail(email);
    if (!email.isRead) {
      await markAsRead(email.id);
    }
  }, []);

  const markAsRead = useCallback(async (emailId) => {
    try {
      await api.post(`/gmail/messages/${emailId}/mark-read`);
      setEmails(prev => prev.map(email => 
        email.id === emailId ? { ...email, isRead: true } : email
      ));
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  }, []);

  const toggleStar = useCallback(async (emailId) => {
    try {
      const response = await api.put(`/gmail/messages/${emailId}/star`);
      setEmails(prev => prev.map(email => 
        email.id === emailId ? { ...email, isStarred: response.data.starred } : email
      ));
      toast.success(response.data.message);
    } catch (error) {
      console.error('Failed to toggle star:', error);
      toast.error('Failed to update star');
    }
  }, []);

  const deleteEmail = useCallback(async (emailId) => {
    try {
      await api.delete(`/gmail/messages/${emailId}`);
      setEmails(prev => prev.filter(email => email.id !== emailId));
      if (selectedEmail?.id === emailId) {
        setSelectedEmail(null);
      }
      toast.success('Email moved to trash');
    } catch (error) {
      console.error('Failed to delete email:', error);
      toast.error('Failed to delete email');
    }
  }, [selectedEmail]);

  const archiveEmail = useCallback(async (emailId) => {
    try {
      await api.put(`/gmail/messages/${emailId}/archive`);
      setEmails(prev => prev.filter(email => email.id !== emailId));
      if (selectedEmail?.id === emailId) {
        setSelectedEmail(null);
      }
      toast.success('Email archived');
    } catch (error) {
      console.error('Failed to archive email:', error);
      toast.error('Failed to archive email');
    }
  }, [selectedEmail]);

  const handleCompose = useCallback(() => {
    setComposeData({
      to: '',
      cc: '',
      bcc: '',
      subject: '',
      body: '',
      attachments: []
    });
    setComposeOpen(true);
  }, []);

  const handleReply = useCallback((email) => {
    setComposeData({
      to: email.from.email,
      cc: '',
      bcc: '',
      subject: `Re: ${email.subject}`,
      body: `\n\n--- Original Message ---\nFrom: ${email.from.name} <${email.from.email}>\nDate: ${format(email.timestamp, 'PPpp')}\nSubject: ${email.subject}\n\n${email.body}`,
      attachments: []
    });
    setComposeOpen(true);
  }, []);

  const handleForward = useCallback((email) => {
    setComposeData({
      to: '',
      cc: '',
      bcc: '',
      subject: `Fwd: ${email.subject}`,
      body: `\n\n--- Forwarded Message ---\nFrom: ${email.from.name} <${email.from.email}>\nDate: ${format(email.timestamp, 'PPpp')}\nSubject: ${email.subject}\n\n${email.body}`,
      attachments: []
    });
    setComposeOpen(true);
  }, []);

  const sendEmail = useCallback(async () => {
    try {
      setLoading(true);
      await api.post('/gmail/send', composeData);
      toast.success('Email sent successfully');
      setComposeOpen(false);
      setComposeData({
        to: '',
        cc: '',
        bcc: '',
        subject: '',
        body: '',
        attachments: []
      });
    } catch (error) {
      console.error('Failed to send email:', error);
      toast.error('Failed to send email');
    } finally {
      setLoading(false);
    }
  }, [composeData]);

  // Memoized update functions to prevent re-renders
  const updateComposeField = useCallback((field, value) => {
    setComposeData(prev => ({ ...prev, [field]: value }));
  }, []);

  const searchEmails = useCallback(async () => {
    if (!searchQuery.trim()) {
      loadEmails();
      return;
    }

    setLoading(true);
    try {
      const response = await api.get('/gmail/search', {
        params: { query: searchQuery }
      });
      
      const transformedEmails = response.data.map(email => {
        const senderMatch = email.from.match(/(.*?)\s*<(.+?)>/) || [null, email.from, email.from];
        const senderName = senderMatch[1]?.trim() || email.from;
        const senderEmail = senderMatch[2] || email.from;

        return {
          id: email.id,
          from: {
            name: senderName,
            email: senderEmail
          },
          to: [{ email: email.to }],
          subject: email.subject,
          preview: email.snippet || '',
          body: email.snippet || '',
          timestamp: email.date ? new Date(email.date) : new Date(),
          isRead: !email.labels?.includes('UNREAD'),
          isStarred: email.labels?.includes('STARRED'),
          hasAttachments: false,
          folder: 'search',
          labels: email.labels || []
        };
      });
      
      setEmails(transformedEmails);
    } catch (error) {
      console.error('Search failed:', error);
      toast.error('Search failed');
    } finally {
      setLoading(false);
    }
  }, [searchQuery, loadEmails]);

  const getIconComponent = (iconName) => {
    const icons = {
      inbox: InboxIcon,
      send: SendIcon,
      drafts: DraftsIcon,
      star: StarIcon,
      delete: DeleteIcon,
    };
    return icons[iconName] || EmailIcon;
  };

  const FolderList = React.memo(() => (
    <List>
      {folders.map((folder) => {
        const IconComponent = getIconComponent(folder.icon);
        const isSelected = selectedFolder === folder.id;
        
        return (
          <ListItem key={folder.id} disablePadding>
            <ListItemButton
              selected={isSelected}
              onClick={() => {
                setSelectedFolder(folder.id);
                if (isMobile) {
                  setMobileOpen(false);
                }
              }}
              sx={{
                borderRadius: 1,
                mx: 1,
                mb: 0.5,
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                },
              }}
            >
              <ListItemIcon sx={{ color: isSelected ? 'white' : folder.color }}>
                <IconComponent />
              </ListItemIcon>
              <ListItemText 
                primary={folder.name} 
                sx={{ color: isSelected ? 'white' : 'inherit' }}
              />
              {folder.count > 0 && (
                <Badge 
                  badgeContent={folder.count} 
                  color={isSelected ? "secondary" : "primary"}
                />
              )}
            </ListItemButton>
          </ListItem>
        );
      })}
    </List>
  ));

  const EmailList = React.memo(() => (
    <Paper sx={{ 
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      maxWidth: '100%',
      overflow: 'hidden'
    }}>
      {/* Mobile Header */}
      {isMobile && (
        <Box sx={{ p: 2, display: 'flex', alignItems: 'center', borderBottom: 1, borderColor: 'divider' }}>
          <IconButton onClick={() => setMobileOpen(true)} sx={{ mr: 1 }}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            {folders.find(f => f.id === selectedFolder)?.name || 'Inbox'}
          </Typography>
        </Box>
      )}

      {/* Search and Actions Bar */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <TextField
            fullWidth
            size="small"
            placeholder="Search emails..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && searchEmails()}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
          <IconButton onClick={loadEmails}>
            <RefreshIcon />
          </IconButton>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 100 }}>
            <Select
              value={filterBy}
              onChange={(e) => setFilterBy(e.target.value)}
              displayEmpty
            >
              <MenuItem value="all">All</MenuItem>
              <MenuItem value="unread">Unread</MenuItem>
              <MenuItem value="starred">Starred</MenuItem>
              <MenuItem value="attachments">With Attachments</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <Select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <MenuItem value="timestamp">Date</MenuItem>
              <MenuItem value="sender">Sender</MenuItem>
              <MenuItem value="subject">Subject</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      {/* Loading Indicator */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Error Message */}
      {error && (
        <Alert severity="error" sx={{ m: 2 }}>
          {error}
          <Button 
            onClick={loadEmails} 
            sx={{ ml: 2 }}
            size="small"
            variant="outlined"
          >
            Retry
          </Button>
        </Alert>
      )}

      {/* Email List */}
      <List sx={{ 
        flexGrow: 1, 
        overflow: 'auto', 
        p: 0,
        maxWidth: '100%'
      }}>
        {filteredEmails.map((email) => (
          <ListItem
            key={email.id}
            disablePadding
            sx={{
              borderBottom: 1,
              borderColor: 'divider',
              '&:hover': { backgroundColor: 'action.hover' },
              maxWidth: '100%'
            }}
          >
            <ListItemButton
              selected={selectedEmail?.id === email.id}
              onClick={() => handleEmailClick(email)}
              sx={{
                px: 2,
                py: 1.5,
                display: 'flex',
                alignItems: 'flex-start',
                gap: 1,
                maxWidth: '100%'
              }}
            >
              <Avatar sx={{ width: 32, height: 32, mt: 0.5 }}>
                {email.from.name.charAt(0).toUpperCase()}
              </Avatar>
              
              <Box sx={{ 
                flexGrow: 1, 
                minWidth: 0,
                maxWidth: 'calc(100% - 80px)',
                overflow: 'hidden'
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                  <Typography
                    variant="subtitle2"
                    sx={{
                      fontWeight: email.isRead ? 400 : 600,
                      flexGrow: 1,
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      maxWidth: '70%'
                    }}
                  >
                    {email.from.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatEmailDate(email.timestamp)}
                  </Typography>
                </Box>
                
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: email.isRead ? 400 : 600,
                    mb: 0.5,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}
                >
                  {email.subject || '(No Subject)'}
                </Typography>
                
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    display: 'block'
                  }}
                >
                  {email.preview}
                </Typography>
                
                {email.hasAttachments && (
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                    <AttachmentIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
                  </Box>
                )}
              </Box>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0.5 }}>
                <IconButton
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleStar(email.id);
                  }}
                  sx={{ p: 0.5 }}
                >
                  {email.isStarred ? (
                    <StarIcon sx={{ color: 'warning.main', fontSize: 16 }} />
                  ) : (
                    <StarBorderIcon sx={{ fontSize: 16 }} />
                  )}
                </IconButton>
                
                {!email.isRead && (
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      backgroundColor: 'primary.main'
                    }}
                  />
                )}
              </Box>
            </ListItemButton>
          </ListItem>
        ))}
        
        {filteredEmails.length === 0 && !loading && !error && (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <MailOutlineIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              No emails found
            </Typography>
          </Box>
        )}
      </List>
    </Paper>
  ));

  const EmailViewer = React.memo(() => {
    if (!selectedEmail) {
      return (
        <Paper sx={{ 
          height: '100%', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          maxWidth: '100%',
          overflow: 'hidden'
        }}>
          <Box sx={{ textAlign: 'center' }}>
            <EmailIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              Select an email to view
            </Typography>
          </Box>
        </Paper>
      );
    }

    return (
      <Paper sx={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        maxWidth: '100%',
        overflow: 'hidden'
      }}>
        {/* Mobile Back Button */}
        {isMobile && (
          <Box sx={{ 
            p: 2, 
            borderBottom: 1, 
            borderColor: 'divider',
            display: 'flex',
            alignItems: 'center'
          }}>
            <IconButton 
              onClick={() => setSelectedEmail(null)}
              sx={{ mr: 1 }}
            >
              <ArrowBackIcon />
            </IconButton>
            <Typography variant="h6" sx={{ 
              flexGrow: 1,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}>
              {selectedEmail.subject || '(No Subject)'}
            </Typography>
          </Box>
        )}

        {/* Email Header */}
        <Box sx={{ 
          p: 3, 
          borderBottom: 1, 
          borderColor: 'divider',
          maxWidth: '100%',
          overflow: 'hidden'
        }}>
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'flex-start', 
            mb: 2,
            gap: 2
          }}>
            <Box sx={{ 
              flexGrow: 1, 
              minWidth: 0,
              maxWidth: '70%'
            }}>
              <Typography 
                variant="h6" 
                gutterBottom
                sx={{
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}
              >
                {selectedEmail.subject || '(No Subject)'}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Avatar sx={{ width: 40, height: 40 }}>
                  {selectedEmail.from.name.charAt(0).toUpperCase()}
                </Avatar>
                <Box sx={{ minWidth: 0, flexGrow: 1 }}>
                  <Typography 
                    variant="subtitle1" 
                    fontWeight={600}
                    sx={{
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}
                  >
                    {selectedEmail.from.name}
                  </Typography>
                  <Typography 
                    variant="body2" 
                    color="text.secondary"
                    sx={{
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap'
                    }}
                  >
                    {selectedEmail.from.email}
                  </Typography>
                </Box>
              </Box>
              <Typography 
                variant="body2" 
                color="text.secondary"
                sx={{
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}
              >
                To: {selectedEmail.to.map(t => t.email).join(', ')}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {format(selectedEmail.timestamp, 'PPpp')}
              </Typography>
            </Box>
            
            <Box sx={{ 
              display: 'flex', 
              gap: 1,
              flexWrap: 'wrap',
              justifyContent: 'flex-end'
            }}>
              <Tooltip title="Reply">
                <IconButton 
                  onClick={() => handleReply(selectedEmail)}
                  size={isMobile ? 'small' : 'medium'}
                >
                  <ReplyIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Forward">
                <IconButton 
                  onClick={() => handleForward(selectedEmail)}
                  size={isMobile ? 'small' : 'medium'}
                >
                  <ForwardIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Star">
                <IconButton 
                  onClick={() => toggleStar(selectedEmail.id)}
                  size={isMobile ? 'small' : 'medium'}
                >
                  {selectedEmail.isStarred ? <StarIcon color="warning" /> : <StarBorderIcon />}
                </IconButton>
              </Tooltip>
              <Tooltip title="Archive">
                <IconButton 
                  onClick={() => archiveEmail(selectedEmail.id)}
                  size={isMobile ? 'small' : 'medium'}
                >
                  <ArchiveIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Delete">
                <IconButton 
                  onClick={() => deleteEmail(selectedEmail.id)}
                  size={isMobile ? 'small' : 'medium'}
                >
                  <DeleteIcon />
                </IconButton>
              </Tooltip>
              <IconButton 
                onClick={(e) => setMenuAnchorEl(e.currentTarget)}
                size={isMobile ? 'small' : 'medium'}
              >
                <MoreVertIcon />
              </IconButton>
            </Box>
          </Box>
        </Box>

        {/* Email Content */}
        <Box sx={{ 
          p: 3, 
          flexGrow: 1, 
          overflow: 'auto',
          maxWidth: '100%',
          wordBreak: 'break-word'
        }}>
          <Typography 
            variant="body1" 
            sx={{ 
              whiteSpace: 'pre-wrap', 
              lineHeight: 1.6,
              wordBreak: 'break-word',
              overflowWrap: 'break-word',
              maxWidth: '100%',
              hyphens: 'auto'
            }}
          >
            {selectedEmail.body}
          </Typography>
        </Box>
      </Paper>
    );
  });

  const ComposeDialog = React.memo(() => (
    <Dialog 
      open={composeOpen} 
      onClose={() => setComposeOpen(false)}
      maxWidth="md"
      fullWidth
      fullScreen={isMobile}
      PaperProps={{
        sx: { 
          height: isMobile ? '100vh' : '80vh', 
          display: 'flex', 
          flexDirection: 'column',
          maxWidth: '100%',
          overflow: 'hidden'
        }
      }}
    >
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">Compose Email</Typography>
        <IconButton onClick={() => setComposeOpen(false)}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      <DialogContent sx={{ 
        flexGrow: 1, 
        display: 'flex', 
        flexDirection: 'column', 
        gap: 2,
        overflow: 'auto'
      }}>
        {/* To Field with Contacts Autocomplete */}
        <Autocomplete
          multiple
          freeSolo
          options={contacts}
          getOptionLabel={(option) => {
            if (typeof option === 'string') return option;
            return `${option.name} <${option.primary_email}>`;
          }}
          value={composeData.to.split(',').filter(Boolean)}
          onChange={(event, newValue) => {
            const emailString = newValue.map(item => {
              if (typeof item === 'string') return item.trim();
              return item.primary_email;
            }).join(', ');
            updateComposeField('to', emailString);
          }}
          renderOption={(props, option) => (
            <Box component="li" {...props}>
              <ListItemAvatar>
                <Avatar sx={{ width: 32, height: 32 }}>
                  {option.photo ? (
                    <img src={option.photo} alt={option.name} style={{ width: '100%', height: '100%' }} />
                  ) : (
                    <PersonIcon />
                  )}
                </Avatar>
              </ListItemAvatar>
              <Box>
                <Typography variant="body2">{option.name}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {option.primary_email}
                </Typography>
                {option.organization && (
                  <Typography variant="caption" color="text.secondary" display="block">
                    {option.organization}
                  </Typography>
                )}
              </Box>
            </Box>
          )}
          renderInput={(params) => (
            <TextField
              {...params}
              label="To"
              placeholder="Enter email addresses..."
              fullWidth
            />
          )}
          loading={contactsLoading}
        />
        
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Autocomplete
            multiple
            freeSolo
            options={contacts}
            getOptionLabel={(option) => {
              if (typeof option === 'string') return option;
              return `${option.name} <${option.primary_email}>`;
            }}
            value={composeData.cc.split(',').filter(Boolean)}
            onChange={(event, newValue) => {
              const emailString = newValue.map(item => {
                if (typeof item === 'string') return item.trim();
                return item.primary_email;
              }).join(', ');
              updateComposeField('cc', emailString);
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label="CC"
                placeholder="CC recipients..."
                sx={{ flexGrow: 1, minWidth: 150 }}
              />
            )}
          />
          <Autocomplete
            multiple
            freeSolo
            options={contacts}
            getOptionLabel={(option) => {
              if (typeof option === 'string') return option;
              return `${option.name} <${option.primary_email}>`;
            }}
            value={composeData.bcc.split(',').filter(Boolean)}
            onChange={(event, newValue) => {
              const emailString = newValue.map(item => {
                if (typeof item === 'string') return item.trim();
                return item.primary_email;
              }).join(', ');
              updateComposeField('bcc', emailString);
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label="BCC"
                placeholder="BCC recipients..."
                sx={{ flexGrow: 1, minWidth: 150 }}
              />
            )}
          />
        </Box>
        
        <TextField
          fullWidth
          label="Subject"
          value={composeData.subject}
          onChange={(e) => updateComposeField('subject', e.target.value)}
        />
        
        <TextField
          fullWidth
          multiline
          rows={isMobile ? 8 : 12}
          label="Message"
          value={composeData.body}
          onChange={(e) => updateComposeField('body', e.target.value)}
          sx={{ flexGrow: 1 }}
        />
      </DialogContent>
      
      <DialogActions sx={{ p: 3, gap: 1, flexWrap: 'wrap' }}>
        <Button startIcon={<AttachmentIcon />} variant="outlined">
          Attach Files
        </Button>
        <Box sx={{ flexGrow: 1 }} />
        <Button onClick={() => setComposeOpen(false)}>
          Cancel
        </Button>
        <Button 
          variant="contained" 
          onClick={sendEmail}
          disabled={loading || !composeData.to || !composeData.subject}
          startIcon={loading ? <CircularProgress size={16} /> : <SendIcon />}
        >
          Send
        </Button>
      </DialogActions>
    </Dialog>
  ));

  const drawer = (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          📧 Email
        </Typography>
      </Toolbar>
      
      <Box sx={{ p: 2 }}>
        <Button
          variant="contained"
          fullWidth
          startIcon={<EditIcon />}
          onClick={handleCompose}
          sx={{ mb: 2 }}
        >
          Compose
        </Button>
      </Box>
      
      <Divider />
      
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        <FolderList />
      </Box>
    </Box>
  );

  return (
    <Box sx={{ 
      display: 'flex', 
      height: 'calc(100vh - 120px)',
      maxWidth: '100vw',
      overflow: 'hidden'
    }}>
      {/* Desktop Drawer */}
      <Drawer
        variant="permanent"
        sx={{
          display: { xs: 'none', md: 'block' },
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            position: 'relative',
            height: '100%',
          },
        }}
      >
        {drawer}
      </Drawer>

      {/* Mobile Drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        ModalProps={{
          keepMounted: true,
        }}
        sx={{
          display: { xs: 'block', md: 'none' },
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
          },
        }}
      >
        {drawer}
      </Drawer>

      {/* Main Content */}
      <Box sx={{ 
        flexGrow: 1, 
        display: 'flex', 
        gap: 2, 
        p: { xs: 1, md: 2 },
        maxWidth: '100%',
        overflow: 'hidden'
      }}>
        {/* Email List */}
        <Box sx={{ 
          width: { xs: '100%', lg: '40%' },
          display: { 
            xs: selectedEmail ? 'none' : 'block', 
            lg: 'block' 
          },
          maxWidth: { xs: '100%', lg: '40%' },
          overflow: 'hidden'
        }}>
          <EmailList />
        </Box>

        {/* Email Viewer */}
        <Box sx={{ 
          width: { xs: '100%', lg: '60%' },
          display: { 
            xs: selectedEmail ? 'block' : 'none', 
            lg: 'block' 
          },
          maxWidth: { xs: '100%', lg: '60%' },
          overflow: 'hidden'
        }}>
          <EmailViewer />
        </Box>
      </Box>

      {/* Floating Action Button for Mobile */}
      <Fab
        color="primary"
        aria-label="compose"
        onClick={handleCompose}
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
          display: { xs: 'flex', md: 'none' }
        }}
      >
        <EditIcon />
      </Fab>

      {/* Compose Dialog */}
      <ComposeDialog />

      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={() => setMenuAnchorEl(null)}
      >
        <MenuItem onClick={() => {
          markAsRead(selectedEmail?.id);
          setMenuAnchorEl(null);
        }}>
          <ListItemIcon>
            <MailOutlineIcon fontSize="small" />
          </ListItemIcon>
          Mark as unread
        </MenuItem>
        <MenuItem onClick={() => {
          archiveEmail(selectedEmail?.id);
          setMenuAnchorEl(null);
        }}>
          <ListItemIcon>
            <ArchiveIcon fontSize="small" />
          </ListItemIcon>
          Archive
        </MenuItem>
        <MenuItem onClick={() => {
          setMenuAnchorEl(null);
        }}>
          <ListItemIcon>
            <LabelIcon fontSize="small" />
          </ListItemIcon>
          Add label
        </MenuItem>
      </Menu>
    </Box>
  );
}
