import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  InputAdornment,
  Fab
} from '@mui/material';
import {
  Add as AddIcon,
  Receipt as ReceiptIcon,
  AttachMoney as AttachMoneyIcon,
  CheckCircle as CheckCircleIcon,
  HourglassEmpty as HourglassEmptyIcon,
  Cancel as CancelIcon
} from '@mui/icons-material';
import axios from 'axios';
import { toast } from 'react-toastify';
import { format } from 'date-fns';

export default function ExpensePage() {
  const [bills, setBills] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState({
    week_start_date: '',
    week_end_date: '',
    total_amount: 0,
    description: ''
  });

  useEffect(() => {
    fetchBills();
  }, []);

  const fetchBills = async () => {
    try {
      const response = await axios.get('/bills/my-bills');
      setBills(response.data);
    } catch (error) {
      toast.error('Failed to load bills');
      console.error('ExpensePage error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!form.bill_date || !form.total_amount || !form.description) {
      toast.error('Please fill out all fields');
      return;
    }

    try {
      const submitData = {
        ...form,
        total_amount: Math.round(form.total_amount * 100), // Convert to cents
        bill_date: new Date(form.bill_date).toISOString()
      };

      await axios.post('/bills/submit', submitData);
      toast.success('Convenience bill submitted successfully');
      setForm({
        week_start_date: '',
        week_end_date: '',
        total_amount: 0,
        description: ''
      });
      setOpen(false);
      fetchBills();
    } catch (error) {
      toast.error('Failed to submit bill');
      console.error('Submit error:', error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'approved':
        return <CheckCircleIcon color="success" />;
      case 'pending':
        return <HourglassEmptyIcon color="warning" />;
      case 'rejected':
        return <CancelIcon color="error" />;
      default:
        return <HourglassEmptyIcon color="warning" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved':
        return 'success';
      case 'pending':
        return 'warning';
      case 'rejected':
        return 'error';
      default:
        return 'default';
    }
  };

  const totalPending = bills.filter(bill => bill.status === 'pending').reduce((sum, bill) => sum + bill.total_amount, 0) / 100;
  const totalApproved = bills.filter(bill => bill.status === 'approved').reduce((sum, bill) => sum + bill.total_amount, 0) / 100;
  const totalSubmitted = bills.reduce((sum, bill) => sum + bill.total_amount, 0) / 100;

  const StatCard = ({ icon, title, value, color }) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box sx={{
            backgroundColor: `${color}.main`,
            color: 'white',
            p: 1,
            borderRadius: 2,
            mr: 2
          }}>
            {icon}
          </Box>
          <Box>
            <Typography variant="h4" component="div" color={color}>
              ${value.toLocaleString()}
            </Typography>
            <Typography variant="h6" component="div">
              {title}
            </Typography>
          </Box>
        </Box>
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
        <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
          Expense Management 💳
        </Typography>
        <Typography variant="h6" color="textSecondary" gutterBottom>
          Submit and track your convenience bills
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<AttachMoneyIcon />}
            title="Total Submitted"
            value={totalSubmitted}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<HourglassEmptyIcon />}
            title="Pending Approval"
            value={totalPending}
            color="warning"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            icon={<CheckCircleIcon />}
            title="Approved"
            value={totalApproved}
            color="success"
          />
        </Grid>
      </Grid>

      {/* Bills Table */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h5">My Convenience Bills</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpen(true)}
            >
              Submit Bill
            </Button>
          </Box>

          {bills.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 6 }}>
              <ReceiptIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                No Bills Submitted Yet
              </Typography>
              <Typography color="textSecondary" sx={{ mb: 3 }}>
                Submit your first convenience bill to get started
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => setOpen(true)}
              >
                Submit Bill
              </Button>
            </Box>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Week Period</TableCell>
                    <TableCell>Amount</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Submitted</TableCell>
                    <TableCell>Approved Date</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {bills.map((bill) => (
                    <TableRow key={bill.id}>
                      <TableCell>
                        {format(new Date(bill.bill_date), 'MMM dd, yyyy')}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <AttachMoneyIcon sx={{ fontSize: 16, mr: 0.5 }} />
                          {(bill.total_amount / 100).toLocaleString()}
                        </Box>
                      </TableCell>
                      <TableCell>{bill.description}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getStatusIcon(bill.status)}
                          <Chip
                            label={bill.status.charAt(0).toUpperCase() + bill.status.slice(1)}
                            color={getStatusColor(bill.status)}
                            size="small"
                          />
                        </Box>
                      </TableCell>
                      <TableCell>
                        {format(new Date(bill.created_at), 'MMM dd, yyyy')}
                      </TableCell>
                      <TableCell>
                        {bill.approval_date ? format(new Date(bill.approval_date), 'MMM dd, yyyy') : '-'}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="add"
        onClick={() => setOpen(true)}
        sx={{ position: 'fixed', bottom: 16, right: 16 }}
      >
        <AddIcon />
      </Fab>

      {/* Submit Bill Dialog */}
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Submit Convenience Bill</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="date"
                label="Bill Date"
                InputLabelProps={{ shrink: true }}
                value={form.bill_date}
                onChange={(e) => setForm({ ...form, bill_date: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="date"
                fullWidth
                type="number"
                label="Total Amount"
                value={form.total_amount}
                onChange={(e) => setForm({ ...form, total_amount: parseFloat(e.target.value) || 0 })}
                InputProps={{
                  startAdornment: <InputAdornment position="start">$</InputAdornment>,
                }}
                inputProps={{ min: 0, step: 0.01 }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Description"
                placeholder="Describe the expenses (meals, transportation, etc.)"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">Submit Bill</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
