import React, { useState } from 'react';
import {
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  Box,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import {
  Backup as BackupIcon,
  Restore as RestoreIcon,
  CloudUpload,
  Download,
} from '@mui/icons-material';
import axios from 'axios';
import { toast } from 'react-toastify';

export default function BackupPage() {
  const [loading, setLoading] = useState(false);
  const [restoreDialogOpen, setRestoreDialogOpen] = useState(false);
  const [backupId, setBackupId] = useState('');
  const [includeFiles, setIncludeFiles] = useState(true);

  const handleCreateBackup = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/backup/create', {
        include_files: includeFiles,
        backup_name: `Manual_Backup_${new Date().toISOString().split('T')[0]}`,
      });
      
      toast.success(`Backup created successfully: ${response.data.backup_name}`);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create backup');
      console.error('Backup error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRestore = async () => {
    if (!backupId.trim()) {
      toast.error('Please enter a backup ID');
      return;
    }

    setLoading(true);
    try {
      await axios.post('/backup/restore', {
        backup_id: backupId.trim(),
        restore_files: includeFiles,
      });
      
      toast.success('Backup restored successfully');
      setRestoreDialogOpen(false);
      setBackupId('');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to restore backup');
      console.error('Restore error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Typography variant="h4" component="h1" gutterBottom>
        Backup & Restore
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        All backups are securely stored in your Google Drive account. Only users with @infosonik.com accounts can access this feature.
      </Alert>

      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <BackupIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">Create Backup</Typography>
            </Box>
            
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              Create a complete backup of your notes, events, and files to Google Drive.
            </Typography>

            <FormControlLabel
              control={
                <Checkbox
                  checked={includeFiles}
                  onChange={(e) => setIncludeFiles(e.target.checked)}
                />
              }
              label="Include uploaded files"
              sx={{ mb: 2 }}
            />

            <Button
              variant="contained"
              startIcon={<CloudUpload />}
              onClick={handleCreateBackup}
              disabled={loading}
              fullWidth
            >
              {loading ? 'Creating Backup...' : 'Create Backup'}
            </Button>
          </CardContent>
        </Card>

        <Card sx={{ flex: 1 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <RestoreIcon sx={{ mr: 1, color: 'secondary.main' }} />
              <Typography variant="h6">Restore Backup</Typography>
            </Box>
            
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              Restore your data from a previously created backup stored in Google Drive.
            </Typography>

            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={() => setRestoreDialogOpen(true)}
              disabled={loading}
              fullWidth
            >
              Restore from Backup
            </Button>
          </CardContent>
        </Card>
      </Box>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Backup Information
          </Typography>
          
          <Typography variant="body2" paragraph>
            <strong>What's included in backups:</strong>
          </Typography>
          
          <ul style={{ marginLeft: '20px', marginBottom: '16px' }}>
            <li>All your notes with content and metadata</li>
            <li>Calendar events and schedules</li>
            <li>File attachments (when enabled)</li>
            <li>User preferences and settings</li>
          </ul>

          <Typography variant="body2" paragraph>
            <strong>Backup Location:</strong> All backups are stored securely in your Google Drive account under the "Infosonik Backups" folder.
          </Typography>

          <Typography variant="body2">
            <strong>Note:</strong> Restoring a backup will add the backed-up data to your current data. It will not replace or delete existing notes and events.
          </Typography>
        </CardContent>
      </Card>

      {/* Restore Dialog */}
      <Dialog open={restoreDialogOpen} onClose={() => setRestoreDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Restore from Backup</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Backup ID"
              placeholder="Enter the Google Drive file ID of your backup"
              value={backupId}
              onChange={(e) => setBackupId(e.target.value)}
              sx={{ mb: 2 }}
              helperText="You can find the backup ID in the Google Drive URL or from the backup creation response"
            />
            
            <FormControlLabel
              control={
                <Checkbox
                  checked={includeFiles}
                  onChange={(e) => setIncludeFiles(e.target.checked)}
                />
              }
              label="Restore uploaded files"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setRestoreDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleRestore}
            variant="contained"
            disabled={loading || !backupId.trim()}
          >
            {loading ? 'Restoring...' : 'Restore'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
