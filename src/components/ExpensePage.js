import React, { useState, useEffect, useContext } from 'react';
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
  Paper,
  Fab,
  InputAdornment,
  Chip,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CardActions,
  FormControlLabel,
  Switch,
  Autocomplete,
} from '@mui/material';
import {
  Add as AddIcon,
  Receipt as ReceiptIcon,
  CheckCircle as CheckCircleIcon,
  HourglassEmpty as HourglassEmptyIcon,
  Cancel as CancelIcon,
  CurrencyExchange as CurrencyIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Business as BusinessIcon,
} from '@mui/icons-material';
import { AuthContext } from '../contexts/AuthContext';
import axios from 'axios';
import { toast } from 'react-toastify';
import { format } from 'date-fns';

export default function ExpensePage() {
  const { token } = useContext(AuthContext);
  const [bills, setBills] = useState([]);
  const [clients, setClients] = useState([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({
    bill_date: '',
    transport_cost: 0,
    food_cost: 0,
    other_cost: 0,
    fuel_cost: 0,
    rental_cost: 0,
    description: '',
    transport_to: '',
    transport_from: '',
    means_of_transportation: '',
    receipt_file: null,
    // New client fields
    client_id: null,
    client_company_name: '',
    client_contact_number: '',
    expense_purpose: '',
    project_reference: '',
    is_billable: false
  });

  const transportationMeans = [
    'Car', 'Bus', 'Train', 'Rickshaw', 'CNG', 'Uber/Pathao', 
    'Bike', 'Walking', 'Flight', 'Taxi', 'Other'
  ];

  useEffect(() => {
    fetchBills();
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      const response = await axios.get('/clients', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setClients(response.data);
    } catch (error) {
      console.error('Failed to load clients:', error);
    }
  };

  const fetchBills = async () => {
    if (!token) {
      toast.error('Please log in to load bills');
      setLoading(false);
      return;
    }
    try {
      const response = await axios.get('/bills/my-bills', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setBills(response.data);
    } catch (error) {
      toast.error('Failed to load bills');
      console.error('ExpensePage error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!form.bill_date || !form.description || !form.expense_purpose ||
        (form.transport_cost === 0 && form.food_cost === 0 && 
         form.other_cost === 0 && form.fuel_cost === 0 && form.rental_cost === 0)) {
      toast.error('Please fill out all required fields and at least one expense amount');
      return;
    }

    if (!token) {
      toast.error('Please log in to submit bills');
      return;
    }

    try {
      const submitData = new FormData();
      submitData.append('bill_date', form.bill_date);
      submitData.append('transport_cost', Math.round(form.transport_cost * 100));
      submitData.append('food_cost', Math.round(form.food_cost * 100));
      submitData.append('other_cost', Math.round(form.other_cost * 100));
      submitData.append('fuel_cost', Math.round(form.fuel_cost * 100));
      submitData.append('rental_cost', Math.round(form.rental_cost * 100));
      submitData.append('description', form.description);
      submitData.append('transport_to', form.transport_to);
      submitData.append('transport_from', form.transport_from);
      submitData.append('means_of_transportation', form.means_of_transportation);
      
      // Client information
      if (form.client_id) {
        submitData.append('client_id', form.client_id);
      }
      submitData.append('client_company_name', form.client_company_name);
      submitData.append('client_contact_number', form.client_contact_number);
      submitData.append('expense_purpose', form.expense_purpose);
      submitData.append('project_reference', form.project_reference);
      submitData.append('is_billable', form.is_billable);
      
      if (form.receipt_file) {
        submitData.append('receipt_file', form.receipt_file);
      }

      const url = editing ? `/bills/${form.id}/update` : '/bills/submit';

      await axios.post(url, submitData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`
        }
      });

      toast.success(editing ? 'Expense bill updated successfully' : 'Expense bill submitted successfully');
      resetForm();
      setOpen(false);
      fetchBills();
    } catch (error) {
      toast.error('Failed to submit bill');
      console.error('Submit error:', error);
    }
  };

  const resetForm = () => {
    setForm({
      bill_date: '',
      transport_cost: 0,
      food_cost: 0,
      other_cost: 0,
      fuel_cost: 0,
      rental_cost: 0,
      description: '',
      transport_to: '',
      transport_from: '',
      means_of_transportation: '',
      receipt_file: null,
      client_id: null,
      client_company_name: '',
      client_contact_number: '',
      expense_purpose: '',
      project_reference: '',
      is_billable: false
    });
  };

  const handleDelete = async (billId) => {
    if (!token) {
      toast.error('Please log in to delete bills');
      return;
    }
    try {
      await axios.delete(`/bills/${billId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      toast.success('Expense bill deleted successfully');
      fetchBills();
    } catch (error) {
      toast.error('Failed to delete bill');
    }
  };

  const handleEdit = (bill) => {
    setForm({
      ...bill,
      transport_cost: bill.transport_cost / 100,
      food_cost: bill.food_cost / 100,
      other_cost: bill.other_cost / 100,
      fuel_cost: bill.fuel_cost / 100,
      rental_cost: bill.rental_cost / 100,
      receipt_file: null // Reset receipt file when editing
    });
    setEditing(true);
    setOpen(true);
  };

  const handleFileChange = (event) => {
    setForm({ ...form, receipt_file: event.target.files[0] });
  };

  const handleClientSelect = (event, newValue) => {
    if (newValue) {
      setForm({
        ...form,
        client_id: newValue.id,
        client_company_name: newValue.company_name,
        client_contact_number: newValue.contact_number || ''
      });
    } else {
      setForm({
        ...form,
        client_id: null,
        client_company_name: '',
        client_contact_number: ''
      });
    }
  };

  const formatBDT = (paisa) => {
    const taka = paisa / 100;
    return `৳${taka.toFixed(2)}`;
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'success';
      case 'rejected': return 'error';
      default: return 'warning';
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" gutterBottom>
          <CurrencyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Expense Management (BDT)
        </Typography>
        <Fab color="primary" aria-label="add" onClick={() => { setEditing(false); resetForm(); setOpen(true); }}>
          <AddIcon />
        </Fab>
      </Box>

      <Grid container spacing={3}>
        {loading ? (
          <Grid item xs={12}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography>Loading expenses...</Typography>
            </Paper>
          </Grid>
        ) : bills.length === 0 ? (
          <Grid item xs={12}>
            <Paper sx={{ p: 2, textAlign: 'center' }}>
              <Typography>No expense bills found. Click the + button to add your first expense.</Typography>
            </Paper>
          </Grid>
        ) : (
          bills.map((bill) => (
            <Grid item xs={12} md={6} key={bill.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="h6">
                      {format(new Date(bill.bill_date), 'MMM dd, yyyy')}
                    </Typography>
                    <Box display="flex" gap={1}>
                      {bill.is_billable && (
                        <Chip label="Billable" color="info" size="small" />
                      )}
                      <Chip
                        icon={
                          getStatusColor(bill.status) === 'success' ? <CheckCircleIcon /> : 
                          getStatusColor(bill.status) === 'error' ? <CancelIcon /> : <HourglassEmptyIcon />
                        }
                        label={bill.status.toUpperCase()}
                        color={getStatusColor(bill.status)}
                        size="small"
                      />
                    </Box>
                  </Box>
                  
                  <Typography variant="h4" color="primary" gutterBottom>
                    {formatBDT(bill.total_amount)}
                  </Typography>

                  {/* Client Information */}
                  {bill.client_company_name && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="textSecondary" display="flex" alignItems="center">
                        <BusinessIcon sx={{ mr: 0.5, fontSize: 16 }} />
                        Client: {bill.client_company_name}
                      </Typography>
                      {bill.client_contact_number && (
                        <Typography variant="body2" color="textSecondary">
                          Contact: {bill.client_contact_number}
                        </Typography>
                      )}
                      {bill.expense_purpose && (
                        <Typography variant="body2" color="textSecondary">
                          Purpose: {bill.expense_purpose}
                        </Typography>
                      )}
                    </Box>
                  )}
                  
                  <Divider sx={{ my: 2 }} />
                  
                  <Grid container spacing={2}>
                    {bill.transport_amount > 0 && (
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">Transportation</Typography>
                        <Typography variant="h6">{formatBDT(bill.transport_amount)}</Typography>
                      </Grid>
                    )}
                    {bill.food_amount > 0 && (
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">Food</Typography>
                        <Typography variant="h6">{formatBDT(bill.food_amount)}</Typography>
                      </Grid>
                    )}
                    {bill.fuel_cost > 0 && (
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">Fuel</Typography>
                        <Typography variant="h6">{formatBDT(bill.fuel_cost)}</Typography>
                      </Grid>
                    )}
                    {bill.rental_cost > 0 && (
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">Rental</Typography>
                        <Typography variant="h6">{formatBDT(bill.rental_cost)}</Typography>
                      </Grid>
                    )}
                    {bill.other_amount > 0 && (
                      <Grid item xs={6}>
                        <Typography variant="body2" color="textSecondary">Miscellaneous</Typography>
                        <Typography variant="h6">{formatBDT(bill.other_amount)}</Typography>
                      </Grid>
                    )}
                  </Grid>
                  
                  {bill.general_description && (
                    <>
                      <Divider sx={{ my: 2 }} />
                      <Typography variant="body2" color="textSecondary">
                        {bill.general_description}
                      </Typography>
                    </>
                  )}
                </CardContent>
                <CardActions>
                  <Button startIcon={<EditIcon />} onClick={() => handleEdit(bill)}>Edit</Button>
                  <Button startIcon={<DeleteIcon />} onClick={() => handleDelete(bill.id)}>Delete</Button>
                </CardActions>
              </Card>
            </Grid>
          ))
        )}
      </Grid>

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <ReceiptIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          {editing ? 'Edit Expense' : 'Submit New Expense'} (BDT)
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Bill Date"
                type="date"
                value={form.bill_date}
                onChange={(e) => setForm({ ...form, bill_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>

            {/* Client Information Section */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                <BusinessIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                Client Information
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <Autocomplete
                options={clients}
                getOptionLabel={(option) => option.company_name || ''}
                value={clients.find(client => client.id === form.client_id) || null}
                onChange={handleClientSelect}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Select Client/Company"
                    placeholder="Choose from existing clients"
                  />
                )}
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Client/Company Name"
                value={form.client_company_name}
                onChange={(e) => setForm({ ...form, client_company_name: e.target.value })}
                placeholder="Or enter new company name"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Client Contact Number"
                value={form.client_contact_number}
                onChange={(e) => setForm({ ...form, client_contact_number: e.target.value })}
                placeholder="+880 1XXXXXXXXX"
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Project Reference"
                value={form.project_reference}
                onChange={(e) => setForm({ ...form, project_reference: e.target.value })}
                placeholder="Project code or reference"
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Expense Purpose"
                multiline
                rows={2}
                value={form.expense_purpose}
                onChange={(e) => setForm({ ...form, expense_purpose: e.target.value })}
                placeholder="Purpose of this expense (required)"
                required
              />
            </Grid>

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={form.is_billable}
                    onChange={(e) => setForm({ ...form, is_billable: e.target.checked })}
                  />
                }
                label="This expense is billable to client"
              />
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>Transportation Details</Typography>
            </Grid>
            
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="From Location"
                value={form.transport_from}
                onChange={(e) => setForm({ ...form, transport_from: e.target.value })}
              />
            </Grid>
            
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="To Location"
                value={form.transport_to}
                onChange={(e) => setForm({ ...form, transport_to: e.target.value })}
              />
            </Grid>
            
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Means of Transportation</InputLabel>
                <Select
                  value={form.means_of_transportation}
                  label="Means of Transportation"
                  onChange={(e) => setForm({ ...form, means_of_transportation: e.target.value })}
                >
                  {transportationMeans.map((means) => (
                    <MenuItem key={means} value={means}>{means}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>Expense Breakdown (BDT)</Typography>
            </Grid>
            
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Transportation Cost"
                type="number"
                value={form.transport_cost}
                onChange={(e) => setForm({ ...form, transport_cost: parseFloat(e.target.value) || 0 })}
                InputProps={{
                  startAdornment: <InputAdornment position="start">৳</InputAdornment>,
                }}
              />
            </Grid>
            
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Food Cost"
                type="number"
                value={form.food_cost}
                onChange={(e) => setForm({ ...form, food_cost: parseFloat(e.target.value) || 0 })}
                InputProps={{
                  startAdornment: <InputAdornment position="start">৳</InputAdornment>,
                }}
              />
            </Grid>
            
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Fuel Cost"
                type="number"
                value={form.fuel_cost}
                onChange={(e) => setForm({ ...form, fuel_cost: parseFloat(e.target.value) || 0 })}
                InputProps={{
                  startAdornment: <InputAdornment position="start">৳</InputAdornment>,
                }}
              />
            </Grid>
            
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Rental Cost"
                type="number"
                value={form.rental_cost}
                onChange={(e) => setForm({ ...form, rental_cost: parseFloat(e.target.value) || 0 })}
                InputProps={{
                  startAdornment: <InputAdornment position="start">৳</InputAdornment>,
                }}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Miscellaneous Cost"
                type="number"
                value={form.other_cost}
                onChange={(e) => setForm({ ...form, other_cost: parseFloat(e.target.value) || 0 })}
                InputProps={{
                  startAdornment: <InputAdornment position="start">৳</InputAdornment>,
                }}
              />
            </Grid>
            
            <Grid item xs={12}>
              <Paper sx={{ p: 2, bgcolor: 'primary.light', color: 'primary.contrastText' }}>
                <Typography variant="h6">
                  Total: ৳{(form.transport_cost + form.food_cost + form.other_cost + form.fuel_cost + form.rental_cost).toFixed(2)}
                </Typography>
              </Paper>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="General Description"
                multiline
                rows={4}
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder="Please provide detailed description of the expenses..."
                required
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>Upload Receipt</Typography>
              <Button
                variant="outlined"
                component="label"
              >
                Upload File
                <input
                  type="file"
                  hidden
                  accept="image/*,.pdf"
                  onChange={handleFileChange}
                />
              </Button>
              {form.receipt_file && <Typography>{form.receipt_file.name}</Typography>}
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editing ? 'Update Expense' : 'Submit Expense'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
