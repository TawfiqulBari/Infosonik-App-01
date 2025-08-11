import React, { useState, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  IconButton,
  LinearProgress,
  Alert,
  Chip,
  useMediaQuery,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import {
  CloudUpload as CloudUploadIcon,
  PhotoCamera as PhotoCameraIcon,
  Delete as DeleteIcon,
  InsertDriveFile as FileIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';

const ReceiptUpload = ({ onFileSelect, selectedFile }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const fileInputRef = useRef(null);
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const allowedTypes = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'];
  const maxSizeMB = 10;
  const maxSizeBytes = maxSizeMB * 1024 * 1024;

  const validateFile = (file) => {
    if (!allowedTypes.includes(file.type)) {
      setError(`File type ${file.type} not supported. Please use JPG, PNG, WebP, or PDF.`);
      return false;
    }
    
    if (file.size > maxSizeBytes) {
      setError(`File size ${(file.size / 1024 / 1024).toFixed(1)}MB exceeds limit of ${maxSizeMB}MB.`);
      return false;
    }
    
    setError(null);
    return true;
  };

  const handleFileSelect = (file) => {
    if (!validateFile(file)) return;
    
    setUploading(true);
    
    // Simulate upload delay
    setTimeout(() => {
      onFileSelect(file);
      setUploading(false);
    }, 500);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleFileInputChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleRemoveFile = () => {
    onFileSelect(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const getFileIcon = (file) => {
    if (file.type.startsWith('image/')) {
      return <PhotoCameraIcon />;
    }
    return <FileIcon />;
  };

  return (
    <Box>
      <input
        ref={fileInputRef}
        type="file"
        accept={allowedTypes.join(',')}
        onChange={handleFileInputChange}
        style={{ display: 'none' }}
      />

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Upload Area */}
      {!selectedFile && (
        <Paper
          elevation={dragOver ? 4 : 1}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          sx={{
            p: isMobile ? 2 : 3,
            border: `2px dashed ${dragOver ? theme.palette.primary.main : theme.palette.divider}`,
            borderColor: dragOver ? 'primary.main' : 'divider',
            backgroundColor: dragOver ? 'primary.light' : 'background.paper',
            cursor: 'pointer',
            textAlign: 'center',
            transition: 'all 0.3s ease',
            '&:hover': {
              borderColor: 'primary.main',
              backgroundColor: 'primary.light',
            }
          }}
          onClick={() => fileInputRef.current?.click()}
        >
          <CloudUploadIcon 
            sx={{ 
              fontSize: isMobile ? 40 : 48, 
              color: dragOver ? 'primary.main' : 'text.secondary',
              mb: 2 
            }} 
          />
          
          <Typography 
            variant={isMobile ? "body1" : "h6"} 
            gutterBottom
            color={dragOver ? 'primary.main' : 'text.primary'}
          >
            Drop receipt here or click to select
          </Typography>
          
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Supports JPG, PNG, WebP, PDF • Max {maxSizeMB}MB
          </Typography>
          
          <Box display="flex" gap={1} justifyContent="center" flexWrap="wrap">
            <Button
              variant="contained"
              startIcon={<CloudUploadIcon />}
              size={isMobile ? "small" : "medium"}
              onClick={(e) => {
                e.stopPropagation();
                fileInputRef.current?.click();
              }}
            >
              Select File
            </Button>
            
            {isMobile && (
              <Button
                variant="outlined"
                startIcon={<PhotoCameraIcon />}
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  // On mobile, this would ideally open camera
                  fileInputRef.current?.click();
                }}
              >
                Camera
              </Button>
            )}
          </Box>
        </Paper>
      )}

      {/* Selected File Display */}
      {selectedFile && (
        <Paper
          elevation={1}
          sx={{
            p: 2,
            border: '2px solid',
            borderColor: 'success.main',
            backgroundColor: 'success.light',
          }}
        >
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" sx={{ flex: 1, minWidth: 0 }}>
              <Box sx={{ color: 'success.main', mr: 1 }}>
                {getFileIcon(selectedFile)}
              </Box>
              
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography 
                  variant="body1" 
                  noWrap
                  sx={{ fontWeight: 'medium' }}
                >
                  {selectedFile.name}
                </Typography>
                
                <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                  <Chip
                    icon={<CheckCircleIcon />}
                    label="Ready"
                    size="small"
                    color="success"
                  />
                  <Typography variant="caption" color="text.secondary">
                    {formatFileSize(selectedFile.size)}
                  </Typography>
                </Box>
              </Box>
            </Box>
            
            <IconButton 
              onClick={handleRemoveFile}
              color="error"
              size="small"
            >
              <DeleteIcon />
            </IconButton>
          </Box>
        </Paper>
      )}

      {/* Upload Progress */}
      {uploading && (
        <Box sx={{ mt: 2 }}>
          <LinearProgress />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
            Processing receipt...
          </Typography>
        </Box>
      )}

      {/* Help Text */}
      <Typography 
        variant="caption" 
        color="text.secondary" 
        sx={{ mt: 1, display: 'block' }}
      >
        💡 Clear, well-lit photos of receipts help with automatic expense categorization
      </Typography>
    </Box>
  );
};

export default ReceiptUpload;
