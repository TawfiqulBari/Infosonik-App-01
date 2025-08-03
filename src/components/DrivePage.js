import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  Grid,
  IconButton,
  Button,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Chip,
  CircularProgress,
  Alert,
  TextField,
  InputAdornment,
} from '@mui/material';
import {
  CloudQueue,
  Description,
  Folder as FolderIcon,
  Image,
  PictureAsPdf,
  GetApp,
  Refresh,
  Search,
  VideoFile,
  AudioFile,
  InsertDriveFile,
  Share,
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import api from '../utils/api';
import { useAuth } from '../contexts/AuthContext';

const getFileIcon = (mimeType) => {
  if (mimeType?.includes('folder')) return <FolderIcon color="primary" />;
  if (mimeType?.includes('image')) return <Image color="secondary" />;
  if (mimeType?.includes('pdf')) return <PictureAsPdf color="error" />;
  if (mimeType?.includes('video')) return <VideoFile color="success" />;
  if (mimeType?.includes('audio')) return <AudioFile color="warning" />;
  if (mimeType?.includes('document') || mimeType?.includes('text')) return <Description color="info" />;
  return <InsertDriveFile />;
};

const formatFileSize = (bytes) => {
  if (!bytes) return 'N/A';
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
};

export default function DrivePage() {
  const { user, token } = useAuth();
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredFiles, setFilteredFiles] = useState([]);

  useEffect(() => {
    fetchDriveFiles();
  }, []);

  useEffect(() => {
    if (searchTerm) {
      const filtered = files.filter(file =>
        file.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredFiles(filtered);
    } else {
      setFilteredFiles(files);
    }
  }, [searchTerm, files]);

  const fetchDriveFiles = async () => {
    setLoading(true);
    try {
      const response = await api.get('/drive/files', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setFiles(response.data);
    } catch (error) {
      console.error('Error fetching Drive files:', error);
      toast.error('Failed to load Google Drive files');
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = async (fileId, fileName) => {
    try {
      const response = await api.get(`/drive/files/${fileId}/download`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob',
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success(`Downloaded ${fileName}`);
    } catch (error) {
      console.error('Error downloading file:', error);
      toast.error('Failed to download file');
    }
  };

  const shareFile = async (fileId, fileName) => {
    try {
      const response = await api.post(`/drive/files/${fileId}/share`, {}, {
        headers: { Authorization: `Bearer ${token}` },
      });
      toast.success(`${fileName} shared with organization successfully`);
    } catch (error) {
      console.error('Error sharing file:', error);
      toast.error('Failed to share file');
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
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <CloudQueue color="primary" />
              Google Drive
            </Typography>
            <Typography variant="body1" color="textSecondary">
              Access and manage your Google Drive files
            </Typography>
          </Box>
          <Button
            startIcon={<Refresh />}
            onClick={fetchDriveFiles}
            variant="outlined"
          >
            Refresh
          </Button>
        </Box>

        <Card sx={{ mb: 3 }}>
          <CardContent>
            <TextField
              fullWidth
              placeholder="Search files..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />
          </CardContent>
        </Card>

        {filteredFiles.length === 0 ? (
          <Alert severity="info">
            {files.length === 0 ? 'No files found in your Google Drive.' : 'No files match your search.'}
          </Alert>
        ) : (
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Files ({filteredFiles.length})
              </Typography>
              <List>
                {filteredFiles.map((file) => (
                  <ListItem key={file.id} divider>
                    <ListItemIcon>
                      {getFileIcon(file.mimeType)}
                    </ListItemIcon>
                    <ListItemText
                      primary={file.name}
                      secondary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                          <Chip
                            label={formatFileSize(file.size)}
                            size="small"
                            variant="outlined"
                          />
                          <Typography variant="caption" color="textSecondary">
                            Modified: {new Date(file.modifiedTime).toLocaleDateString()}
                          </Typography>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <IconButton
                          onClick={() => shareFile(file.id, file.name)}
                          title="Share with Organization"
                          size="small"
                        >
                          <Share />
                        </IconButton>
                        {file.mimeType !== 'application/vnd.google-apps.folder' && (
                          <IconButton
                            onClick={() => downloadFile(file.id, file.name)}
                            title="Download"
                            size="small"
                          >
                            <GetApp />
                          </IconButton>
                        )}
                      </Box>
                    </ListItemSecondaryAction>
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        )}
      </Box>
    </Container>
  );
}
