import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Box,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';
import {
  Add as AddIcon,
  CheckCircle as CheckCircleIcon,
  HourglassEmpty as HourglassEmptyIcon
} from '@mui/icons-material';
import axios from 'axios';
import { toast } from 'react-toastify';
import { format } from 'date-fns';

export default function LeavePage() {
  const [leaveApplications, setLeaveApplications] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    leave_type: '',
    start_date: '',
    end_date: '',
    reason: ''
  });

  useEffect(() => {
    fetchLeaveApplications();
  }, []);

  const fetchLeaveApplications = async () => {
    try {
      const response = await axios.get('/leave/my-applications');
      setLeaveApplications(response.data);
    } catch (error) {
      toast.error('Failed to load leave applications');
      console.error('LeavePage error:', error);
    }
  };

  const handleSubmit = async () => {
    if (!form.leave_type || !form.start_date || !form.end_date || !form.reason) {
      toast.error('Please fill out all fields');
      return;
    }

    try {
      await axios.post('/leave/apply', form);
      toast.success('Leave application submitted');
      setForm({ leave_type: '', start_date: '', end_date: '', reason: '' });
      setOpen(false);
      fetchLeaveApplications();
    } catch (error) {
      toast.error('Failed to submit leave application');
      console.error('Submit error:', error);
    }
  };

  const leaveStatuses = {
    approved: <CheckCircleIcon color="success" />, 
    pending: <HourglassEmptyIcon color="warning" />, 
    rejected: <>❌</>
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
          Leave Management ⚖️
        </Typography>
        <Typography variant="h6" color="textSecondary" gutterBottom>
          Manage your leave applications
        </Typography>
      </Box>

      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          {leaveApplications.length === 0 ? (
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 6 }}>
                <HourglassEmptyIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  No Leave Applications Yet
                </Typography>
                <Typography color="textSecondary" sx={{ mb: 3 }}>
                  Apply for leave to see your applications
                </Typography>
              </CardContent>
            </Card>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Type</TableCell>
                    <TableCell>Start Date</TableCell>
                    <TableCell>End Date</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Submitted</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {leaveApplications.map((application) => (
                    <TableRow key={application.id}>
                      <TableCell>{application.leave_type}</TableCell>
                      <TableCell>{format(new Date(application.start_date), 'MMM dd, yyyy')}</TableCell>
                      <TableCell>{format(new Date(application.end_date), 'MMM dd, yyyy')}</TableCell>
                      <TableCell>{leaveStatuses[application.status]}</TableCell>
                      <TableCell>{format(new Date(application.created_at), 'MMM dd, yyyy')}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Grid>
      </Grid>

      <Fab color="primary" aria-label="add" onClick={() => setOpen(true)} sx={{ position: 'fixed', bottom: 16, right: 16 }}>
        <AddIcon />
      </Fab>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Apply for Leave</DialogTitle>
        <DialogContent>
          <TextField
            margin="dense"
            label="Leave Type"
            fullWidth
            value={form.leave_type}
            onChange={(e) => setForm({ ...form, leave_type: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Start Date"
            type="date"
            fullWidth
            value={form.start_date}
            onChange={(e) => setForm({ ...form, start_date: e.target.value })}
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            margin="dense"
            label="End Date"
            type="date"
            fullWidth
            value={form.end_date}
            onChange={(e) => setForm({ ...form, end_date: e.target.value })}
            InputLabelProps={{ shrink: true }}
          />
          <TextField
            margin="dense"
            label="Reason"
            fullWidth
            multiline
            minRows={3}
            value={form.reason}
            onChange={(e) => setForm({ ...form, reason: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">Submit</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

