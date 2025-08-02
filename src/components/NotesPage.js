import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Box,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Fab,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  AttachFile,
  Description,
  Search,
  FilterList,
  Close,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import { toast } from 'react-toastify';
import { format } from 'date-fns';
import { useTheme } from '../contexts/ThemeContext';

export default function NotesPage() {
  const { theme } = useTheme();
  const [notes, setNotes] = useState([]);
  const [filteredNotes, setFilteredNotes] = useState([]);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingNote, setEditingNote] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [languageFilter, setLanguageFilter] = useState('all');
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    language: 'en',
    theme: theme,
    attachments: [],
  });

  useEffect(() => {
    fetchNotes();
    fetchFiles();
  }, []);

  useEffect(() => {
    setFormData(prev => ({ ...prev, theme }));
  }, [theme]);

  useEffect(() => {
    filterNotes();
  }, [notes, searchTerm, languageFilter]);

  const fetchNotes = async () => {
    try {
      const response = await axios.get('/notes/');
      setNotes(response.data);
    } catch (error) {
      toast.error('Failed to fetch notes');
      console.error('Fetch notes error:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFiles = async () => {
    try {
      const response = await axios.get('/files/');
      setFiles(response.data);
    } catch (error) {
      console.error('Fetch files error:', error);
    }
  };

  const filterNotes = () => {
    let filtered = notes;

    if (searchTerm) {
      filtered = filtered.filter(
        note =>
          note.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          note.content.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (languageFilter !== 'all') {
      filtered = filtered.filter(note => note.language === languageFilter);
    }

    setFilteredNotes(filtered);
  };

  const handleSubmit = async () => {
    try {
      if (editingNote) {
        await axios.put(`/notes/${editingNote.id}`, formData);
        toast.success('Note updated successfully');
      } else {
        await axios.post('/notes/', formData);
        toast.success('Note created successfully');
      }
      fetchNotes();
      handleCloseDialog();
    } catch (error) {
      toast.error('Failed to save note');
      console.error('Save note error:', error);
    }
  };

  const handleDelete = async (noteId) => {
    if (window.confirm('Are you sure you want to delete this note?')) {
      try {
        await axios.delete(`/notes/${noteId}`);
        toast.success('Note deleted successfully');
        fetchNotes();
      } catch (error) {
        toast.error('Failed to delete note');
        console.error('Delete note error:', error);
      }
    }
  };

  const handleEdit = (note) => {
    setEditingNote(note);
    setFormData({
      title: note.title,
      content: note.content,
      language: note.language,
      theme: note.theme,
      attachments: note.attachments?.map(att => att.id.toString()) || [],
    });
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditingNote(null);
    setFormData({
      title: '',
      content: '',
      language: 'en',
      theme: theme,
      attachments: [],
    });
  };

  const onDrop = async (acceptedFiles) => {
    for (const file of acceptedFiles) {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const response = await axios.post('/files/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        
        setFiles(prev => [...prev, response.data]);
        toast.success(`${file.name} uploaded successfully`);
      } catch (error) {
        toast.error(`Failed to upload ${file.name}`);
        console.error('Upload error:', error);
      }
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
  });

  const handleAttachmentToggle = (fileId) => {
    setFormData(prev => ({
      ...prev,
      attachments: prev.attachments.includes(fileId)
        ? prev.attachments.filter(id => id !== fileId)
        : [...prev.attachments, fileId],
    }));
  };

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
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          My Notes
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setDialogOpen(true)}
        >
          New Note
        </Button>
      </Box>

      <Box sx={{ mb: 3, display: 'flex', gap: 2, alignItems: 'center' }}>
        <TextField
          placeholder="Search notes..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: <Search sx={{ mr: 1, color: 'action.active' }} />,
          }}
          sx={{ minWidth: 300 }}
        />
        <FormControl sx={{ minWidth: 120 }}>
          <InputLabel>Language</InputLabel>
          <Select
            value={languageFilter}
            label="Language"
            onChange={(e) => setLanguageFilter(e.target.value)}
          >
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="en">English</MenuItem>
            <MenuItem value="bn">Bangla</MenuItem>
          </Select>
        </FormControl>
      </Box>

      <Grid container spacing={3}>
        {filteredNotes.map((note) => (
          <Grid item xs={12} sm={6} md={4} key={note.id}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'all 0.2s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                },
              }}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                  <Typography variant="h6" component="h2" noWrap>
                    {note.title}
                  </Typography>
                  <Chip
                    label={note.language.toUpperCase()}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                </Box>
                
                <Typography
                  variant="body2"
                  color="textSecondary"
                  sx={{
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    display: '-webkit-box',
                    WebkitLineClamp: 3,
                    WebkitBoxOrient: 'vertical',
                    mb: 2,
                  }}
                >
                  {note.content}
                </Typography>

                {note.attachments?.length > 0 && (
                  <Box sx={{ mb: 2 }}>
                    {note.attachments.map((attachment) => (
                      <Chip
                        key={attachment.id}
                        icon={<AttachFile />}
                        label={attachment.filename}
                        size="small"
                        variant="outlined"
                        sx={{ mr: 0.5, mb: 0.5 }}
                      />
                    ))}
                  </Box>
                )}

                <Typography variant="caption" color="textSecondary">
                  {format(new Date(note.created_at), 'MMM dd, yyyy HH:mm')}
                </Typography>
              </CardContent>
              
              <CardActions>
                <IconButton onClick={() => handleEdit(note)} size="small">
                  <Edit />
                </IconButton>
                <IconButton onClick={() => handleDelete(note.id)} size="small" color="error">
                  <Delete />
                </IconButton>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {filteredNotes.length === 0 && (
        <Box sx={{ textAlign: 'center', mt: 8 }}>
          <Description sx={{ fontSize: 64, color: 'action.disabled', mb: 2 }} />
          <Typography variant="h6" color="textSecondary">
            {searchTerm || languageFilter !== 'all' ? 'No notes found' : 'No notes yet'}
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
            {searchTerm || languageFilter !== 'all'
              ? 'Try adjusting your search or filters'
              : 'Create your first note to get started'}
          </Typography>
          {!searchTerm && languageFilter === 'all' && (
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setDialogOpen(true)}
            >
              Create Note
            </Button>
          )}
        </Box>
      )}

      {/* Create/Edit Note Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingNote ? 'Edit Note' : 'Create New Note'}
          <IconButton
            onClick={handleCloseDialog}
            sx={{ position: 'absolute', right: 8, top: 8 }}
          >
            <Close />
          </IconButton>
        </DialogTitle>
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
              label="Content"
              multiline
              rows={8}
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              sx={{ mb: 2 }}
            />
            
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Language</InputLabel>
              <Select
                value={formData.language}
                label="Language"
                onChange={(e) => setFormData({ ...formData, language: e.target.value })}
              >
                <MenuItem value="en">English</MenuItem>
                <MenuItem value="bn">Bangla</MenuItem>
              </Select>
            </FormControl>

            {/* File Upload Area */}
            <Box
              {...getRootProps()}
              sx={{
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : 'grey.300',
                borderRadius: 2,
                p: 3,
                textAlign: 'center',
                cursor: 'pointer',
                mb: 2,
                backgroundColor: isDragActive ? 'action.hover' : 'transparent',
              }}
            >
              <input {...getInputProps()} />
              <AttachFile sx={{ fontSize: 48, color: 'action.active', mb: 1 }} />
              <Typography variant="body1">
                {isDragActive ? 'Drop files here...' : 'Drag & drop files here, or click to select'}
              </Typography>
              <Typography variant="caption" color="textSecondary">
                Supports PDF, Excel, Word, images, and text files
              </Typography>
            </Box>

            {/* File Attachments */}
            {files.length > 0 && (
              <Box>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>
                  Available Files:
                </Typography>
                <List dense sx={{ maxHeight: 200, overflow: 'auto' }}>
                  {files.map((file) => (
                    <ListItem
                      key={file.id}
                      button
                      onClick={() => handleAttachmentToggle(file.id.toString())}
                      selected={formData.attachments.includes(file.id.toString())}
                    >
                      <ListItemIcon>
                        <Description />
                      </ListItemIcon>
                      <ListItemText
                        primary={file.filename}
                        secondary={`${(file.file_size / 1024).toFixed(1)} KB`}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={!formData.title || !formData.content}
          >
            {editingNote ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
