import React, { useEffect, useState, useMemo, useCallback } from 'react';
import {
  Box,
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
  Popper,
  ClickAwayListener,
  MenuList,
  ListItemAvatar,
  Chip,
  LinearProgress,
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
  Person as PersonIcon,
  ExpandMore as ExpandMoreIcon,
  CloudUpload as CloudUploadIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import { toast } from 'react-toastify';
import { format, isToday, isYesterday } from 'date-fns';

const DRAWER_WIDTH = 280;

// Contact suggestion component
const ContactSuggestion = ({ contacts, onSelectContact, anchorEl, open, onClose }) => {
  const [filteredContacts, setFilteredContacts] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (searchTerm) {
      const filtered = contacts.filter(contact =>
        contact.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        contact.primary_email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (contact.organization && contact.organization.toLowerCase().includes(searchTerm.toLowerCase()))
      );
      setFilteredContacts(filtered.slice(0, 5)); // Show max 5 suggestions
    } else {
      setFilteredContacts([]);
    }
  }, [contacts, searchTerm]);

  const handleContactSelect = (contact) => {
    onSelectContact(contact);
    setSearchTerm('');
    setFilteredContacts([]);
    onClose();
  };

  if (!open || filteredContacts.length === 0) {
    return null;
  }

  return (
    <Popper
      open={open}
      anchorEl={anchorEl}
      placement="bottom-start"
      style={{ zIndex: 1300 }}
    >
      <Paper sx={{ mt: 1, maxWidth: 400, maxHeight: 300, overflow: 'auto' }}>
        <MenuList>
          {filteredContacts.map((contact) => (
            <MenuItem
              key={contact.id}
              onClick={() => handleContactSelect(contact)}
              sx={{ py: 1 }}
            >
              <ListItemAvatar>
                <Avatar sx={{ width: 32, height: 32 }}>
                  {contact.photo ? (
                    <img 
                      src={contact.photo} 
                      alt={contact.name} 
                      style={{ width: '100%', height: '100%', borderRadius: '50%' }} 
                    />
                  ) : (
                    contact.name ? contact.name.charAt(0).toUpperCase() : <PersonIcon />
                  )}
                </Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={contact.name || contact.primary_email}
                secondary={
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      {contact.primary_email}
                    </Typography>
                    {contact.organization && (
                      <Typography variant="caption" color="text.secondary" display="block">
                        {contact.organization}
                      </Typography>
                    )}
                  </Box>
                }
              />
            </MenuItem>
          ))}
        </MenuList>
      </Paper>
    </Popper>
  );
};

// Enhanced TextField with contact suggestions
const ContactTextField = ({ 
  label, 
  value, 
  onChange, 
  contacts, 
  placeholder,
  size = "small",
  sx = {},
  ...props 
}) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [inputValue, setInputValue] = useState(value);

  useEffect(() => {
    setInputValue(value);
  }, [value]);

  const handleInputChange = (e) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    onChange(newValue);
    
    // Show suggestions if typing and there's text
    if (newValue && newValue.length > 1) {
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }
  };

  const handleFocus = (e) => {
    setAnchorEl(e.currentTarget);
    if (inputValue && inputValue.length > 1) {
      setShowSuggestions(true);
    }
  };

  const handleSelectContact = (contact) => {
    const newValue = inputValue ? `${inputValue}, ${contact.primary_email}` : contact.primary_email;
    setInputValue(newValue);
    onChange(newValue);
    setShowSuggestions(false);
  };

  const handleClickAway = () => {
    setShowSuggestions(false);
  };

  return (
    <ClickAwayListener onClickAway={handleClickAway}>
      <Box sx={{ position: 'relative', ...sx }}>
        <TextField
          {...props}
          label={label}
          value={inputValue}
          onChange={handleInputChange}
          onFocus={handleFocus}
          placeholder={placeholder}
          size={size}
          fullWidth
        />
        <ContactSuggestion
          contacts={contacts}
          onSelectContact={handleSelectContact}
          anchorEl={anchorEl}
          open={showSuggestions}
          onClose={() => setShowSuggestions(false)}
        />
      </Box>
    </ClickAwayListener>
  );
};

// File attachment component
const FileAttachments = ({ attachments, onAddFiles, onRemoveFile, uploading }) => {
  const fileInputRef = React.useRef();

  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event) => {
    const files = Array.from(event.target.files);
    if (files.length > 0) {
      onAddFiles(files);
    }
    // Reset the input
    event.target.value = '';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Box>
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        style={{ display: 'none' }}
        multiple
        accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif,.zip,.xlsx,.xls,.ppt,.pptx"
      />
      
      <Button
        startIcon={uploading ? <CircularProgress size={16} /> : <CloudUploadIcon />}
        variant="outlined"
        onClick={handleFileSelect}
        disabled={uploading}
        size="small"
      >
        {uploading ? 'Uploading...' : 'Attach Files'}
      </Button>
      
      {attachments.length > 0 && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Attachments ({attachments.length})
          </Typography>
          <List dense>
            {attachments.map((file, index) => (
              <ListItem
                key={index}
                sx={{
                  border: 1,
                  borderColor: 'divider',
                  borderRadius: 1,
                  mb: 1,
                  bgcolor: 'background.paper'
                }}
              >
                <ListItemIcon>
                  <AttachmentIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary={file.name}
                  secondary={formatFileSize(file.size)}
                />
                <IconButton
                  size="small"
                  onClick={() => onRemoveFile(index)}
                  disabled={uploading}
                >
                  <Close />
                </IconButton>
              </ListItem>
            ))}
          </List>
        </Box>
      )}
    </Box>
  );
};

export default function EmailPage() {
  const { user } = useAuth();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
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
  const [sendingEmail, setSendingEmail] = useState(false);
  const [attachments, setAttachments] = useState([]);
  const [uploadingFiles, setUploadingFiles] = useState(false);

  // Compose email state
  const [composeData, setComposeData] = useState({
    to: '',
    cc: '',
    bcc: '',
    subject: '',
    body: '',
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
    }
  }, []);

  const loadEmails = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get('/gmail/messages', {
        params: { max_results: 50 }
      });
      
      const transformedEmails = response.data.map(email => {
        const senderMatch = email.sender.match(/(.*?)\s*<(.+?)>/) || [null, email.sender, email.sender];
        const senderName = senderMatch[1]?.trim() || email.sender;
        const senderEmail = senderMatch[2] || email.sender;

        return {
          id: email.id,
          from: { name: senderName, email: senderEmail },
          to: [{ email: email.recipient }],
          subject: email.subject,
          preview: email.body ? email.body.substring(0, 200) + '...' : '',
          body: email.body || '',
          timestamp: new Date(email.timestamp),
          isRead: email.is_read,
          isStarred: false,
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
      console.log('Contacts loaded:', response.data);
      setContacts(response.data || []);
    } catch (error) {
      console.error('Failed to load contacts:', error);
      toast.info('Contact suggestions unavailable');
      setContacts([]);
    } finally {
      setContactsLoading(false);
    }
  }, []);

  const uploadFiles = useCallback(async (files) => {
    setUploadingFiles(true);
    const uploadedFiles = [];
    
    try {
      for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await api.post('/files/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        
        uploadedFiles.push({
          id: response.data.id,
          name: file.name,
          size: file.size,
          url: response.data.url,
        });
      }
      
      setAttachments(prev => [...prev, ...uploadedFiles]);
      toast.success(`${files.length} file(s) attached successfully`);
    } catch (error) {
      console.error('Failed to upload files:', error);
      toast.error('Failed to upload files');
    } finally {
      setUploadingFiles(false);
    }
  }, []);

  const removeAttachment = useCallback((index) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  }, []);

  const filteredEmails = useMemo(() => {
    let filtered = emails.filter(email => {
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return (
          email.subject.toLowerCase().includes(query) ||
          email.from.name.toLowerCase().includes(query) ||
          email.from.email.toLowerCase().includes(query) ||
          email.preview.toLowerCase().includes(query)
        );
      }
      
      if (filterBy === 'unread' && email.isRead) return false;
      if (filterBy === 'starred' && !email.isStarred) return false;
      if (filterBy === 'attachments' && !email.hasAttachments) return false;
      
      return true;
    });

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
      if (isToday(date)) return format(date, 'h:mm a');
      if (isYesterday(date)) return 'Yesterday';
      return format(date, 'MMM dd');
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
    });
    setAttachments([]);
    setComposeOpen(true);
  }, []);

  const handleReply = useCallback((email) => {
    setComposeData({
      to: email.from.email,
      cc: '',
      bcc: '',
      subject: `Re: ${email.subject}`,
      body: `\n\n--- Original Message ---\nFrom: ${email.from.name} <${email.from.email}>\nDate: ${format(email.timestamp, 'PPpp')}\nSubject: ${email.subject}\n\n${email.body}`,
    });
    setAttachments([]);
    setComposeOpen(true);
  }, []);

  const handleForward = useCallback((email) => {
    setComposeData({
      to: '',
      cc: '',
      bcc: '',
      subject: `Fwd: ${email.subject}`,
      body: `\n\n--- Forwarded Message ---\nFrom: ${email.from.name} <${email.from.email}>\nDate: ${format(email.timestamp, 'PPpp')}\nSubject: ${email.subject}\n\n${email.body}`,
    });
    setAttachments([]);
    setComposeOpen(true);
  }, []);

  const handleCloseCompose = useCallback(() => {
    setComposeOpen(false);
    setAttachments([]);
  }, []);

  const sendEmail = useCallback(async () => {
    try {
      setSendingEmail(true);
      
      const emailData = {
        ...composeData,
        attachments: attachments.map(file => file.id), // Send file IDs
      };
      
      await api.post('/gmail/send', emailData);
      toast.success('Email sent successfully');
      setComposeOpen(false);
      setComposeData({
        to: '',
        cc: '',
        bcc: '',
        subject: '',
        body: '',
      });
      setAttachments([]);
    } catch (error) {
      console.error('Failed to send email:', error);
      toast.error('Failed to send email');
    } finally {
      setSendingEmail(false);
    }
  }, [composeData, attachments]);

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
          from: { name: senderName, email: senderEmail },
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
      
      {/* Contact Status */}
      {contactsLoading && (
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CircularProgress size={12} />
            Loading contacts...
          </Typography>
        </Box>
      )}
      
      {contacts.length > 0 && (
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary">
            {contacts.length} contacts loaded
          </Typography>
        </Box>
      )}
      
      {!contactsLoading && contacts.length === 0 && (
        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary">
            No contacts available
          </Typography>
        </Box>
      )}
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
        ModalProps={{ keepMounted: true }}
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

      {/* Compose Dialog with Contact Suggestions and File Attachments */}
      <Dialog 
        open={composeOpen} 
        onClose={handleCloseCompose}
        maxWidth="md"
        fullWidth
        fullScreen={isMobile}
        disableEscapeKeyDown={false}
        PaperProps={{
          sx: { 
            height: isMobile ? '100vh' : '85vh', 
            display: 'flex', 
            flexDirection: 'column',
            maxWidth: '100%',
            overflow: 'hidden'
          }
        }}
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="h6">Compose Email</Typography>
            {contacts.length > 0 && (
              <Chip 
                size="small" 
                label={`${contacts.length} contacts`} 
                color="primary" 
                variant="outlined" 
              />
            )}
            {attachments.length > 0 && (
              <Chip 
                size="small" 
                label={`${attachments.length} files`} 
                color="secondary" 
                variant="outlined" 
              />
            )}
          </Box>
          <IconButton onClick={handleCloseCompose}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        
        <DialogContent sx={{ 
          flexGrow: 1, 
          display: 'flex', 
          flexDirection: 'column', 
          gap: 2,
          overflow: 'auto',
          p: 3
        }}>
          <ContactTextField
            label="To"
            placeholder="Enter email addresses... (type to see suggestions)"
            value={composeData.to}
            onChange={(value) => setComposeData(prev => ({ ...prev, to: value }))}
            contacts={contacts}
            size="small"
          />
          
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <ContactTextField
              label="CC"
              placeholder="CC recipients..."
              value={composeData.cc}
              onChange={(value) => setComposeData(prev => ({ ...prev, cc: value }))}
              contacts={contacts}
              sx={{ flexGrow: 1, minWidth: 150 }}
              size="small"
            />
            <ContactTextField
              label="BCC"
              placeholder="BCC recipients..."
              value={composeData.bcc}
              onChange={(value) => setComposeData(prev => ({ ...prev, bcc: value }))}
              contacts={contacts}
              sx={{ flexGrow: 1, minWidth: 150 }}
              size="small"
            />
          </Box>
          
          <TextField
            fullWidth
            label="Subject"
            value={composeData.subject}
            onChange={(e) => setComposeData(prev => ({ ...prev, subject: e.target.value }))}
            size="small"
          />
          
          <FileAttachments
            attachments={attachments}
            onAddFiles={uploadFiles}
            onRemoveFile={removeAttachment}
            uploading={uploadingFiles}
          />
          
          <TextField
            fullWidth
            multiline
            rows={isMobile ? 8 : 10}
            label="Message"
            value={composeData.body}
            onChange={(e) => setComposeData(prev => ({ ...prev, body: e.target.value }))}
            sx={{ flexGrow: 1 }}
            placeholder="Type your message here..."
          />
        </DialogContent>
        
        <DialogActions sx={{ p: 3, gap: 1, flexWrap: 'wrap', flexShrink: 0 }}>
          <Box sx={{ flexGrow: 1 }} />
          <Button onClick={handleCloseCompose} variant="outlined">
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={sendEmail}
            disabled={sendingEmail || !composeData.to.trim() || !composeData.subject.trim()}
            startIcon={sendingEmail ? <CircularProgress size={16} /> : <SendIcon />}
          >
            {sendingEmail ? 'Sending...' : 'Send'}
          </Button>
        </DialogActions>
      </Dialog>

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
