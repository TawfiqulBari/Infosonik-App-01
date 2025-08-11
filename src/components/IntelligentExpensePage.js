import React, { useState, useEffect, useContext, useCallback } from 'react';
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
  LinearProgress,
  Alert,
  Badge,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  useMediaQuery,
  Slide,
  AppBar,
  Toolbar,
  SpeedDial,
  SpeedDialAction,
  SpeedDialIcon,
} from '@mui/material';
import { useTheme } from '@mui/material/styles';
import {
  Add as AddIcon,
  Receipt as ReceiptIcon,
  CheckCircle as CheckCircleIcon,
  HourglassEmpty as HourglassEmptyIcon,
  Cancel as CancelIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Business as BusinessIcon,
  SmartToy as SmartToyIcon,
  Send as SendIcon,
  Schedule as ScheduleIcon,
  AutoAwesome as AutoAwesomeIcon,
  DirectionsBus as DirectionsBusIcon,
  Train as TrainIcon,
  DirectionsCar as DirectionsCarIcon,
  TwoWheeler as TwoWheelerIcon,
  FlightTakeoff as FlightIcon,
  DirectionsBoat as DirectionsBoatIcon,
  ExpandMore as ExpandMoreIcon,
  LocationOn as LocationOnIcon,
  Remove as RemoveIcon,
  Map as MapIcon,
  Visibility as VisibilityIcon,
  Close as CloseIcon,
  Save as SaveIcon,
  DraftsIcon,
} from '@mui/icons-material';
import { AuthContext } from '../contexts/AuthContext';
import axios from 'axios';
import { toast } from 'react-toastify';
import { format, parseISO } from 'date-fns';
import GoogleMapRoute from './map/GoogleMapRoute';
import ReceiptUpload from './ReceiptUpload';

// Transport Modes with enhanced mobile support
const TRANSPORT_MODES = [
  { value: 'bus', label: 'Bus', icon: <DirectionsBusIcon />, color: '#4CAF50' },
  { value: 'cng', label: 'CNG Auto-rickshaw', icon: <TwoWheelerIcon />, color: '#FF9800' },
  { value: 'rickshaw', label: 'Rickshaw', icon: <TwoWheelerIcon />, color: '#2196F3' },
  { value: 'uber_pathao', label: 'Uber/Pathao', icon: <DirectionsCarIcon />, color: '#9C27B0' },
  { value: 'taxi', label: 'Taxi', icon: <DirectionsCarIcon />, color: '#F44336' },
  { value: 'train', label: 'Train', icon: <TrainIcon />, color: '#607D8B' },
  { value: 'launch', label: 'Launch/Ferry', icon: <DirectionsBoatIcon />, color: '#00BCD4' },
  { value: 'flight', label: 'Flight', icon: <FlightIcon />, color: '#3F51B5' },
  { value: 'motorcycle', label: 'Motorcycle', icon: <TwoWheelerIcon />, color: '#795548' },
  { value: 'private_car', label: 'Private Car', icon: <DirectionsCarIcon />, color: '#E91E63' },
  { value: 'tempo', label: 'Tempo', icon: <DirectionsBusIcon />, color: '#CDDC39' },
  { value: 'van', label: 'Microbus/Van', icon: <DirectionsBusIcon />, color: '#8BC34A' },
];

// Enhanced Dhaka Areas with proper grouping
const DHAKA_AREAS = [
  'Abdullahpur', 'Agargaon', 'Arambagh', 'Azimpur', 'Badda', 'Banani', 'Bangla Motor',
  'Baridhara', 'Basabo', 'Bashundhara', 'Cantonment', 'Chawkbazar', 'Dhanmondi',
  'Elephant Road', 'Farmgate', 'Gabtoli', 'Gulistan', 'Gulshan', 'Hazaribagh',
  'Jatrabari', 'Kakrail', 'Kallyanpur', 'Kamrangirchar', 'Kawran Bazar', 'Khilgaon',
  'Khilkhet', 'Lalbagh', 'Lalmatia', 'Malibagh', 'Mirpur', 'Mohakhali', 'Mohammadpur',
  'Motijheel', 'Mugdapara', 'New Market', 'Nikunja', 'Pallabi', 'Paltan', 'Panthapath',
  'Ramna', 'Rampura', 'Sabujbagh', 'Sadarghat', 'Savar', 'Shahbagh', 'Shantinagar',
  'Shyamoli', 'Sutrapur', 'Tejgaon', 'Tongi', 'Uttara', 'Wari'
];

const OTHER_BD_LOCATIONS = [
  'Chittagong', 'Cox\'s Bazar', 'Rangamati', 'Bandarban', 'Khagrachhari', 'Feni', 
  'Lakshmipur', 'Comilla', 'Noakhali', 'Brahmanbaria', 'Chandpur', 'Rajshahi', 
  'Bogra', 'Pabna', 'Sirajganj', 'Ishurdi', 'Natore', 'Naogaon', 'Joypurhat', 
  'Chapainawabganj', 'Khulna', 'Jessore', 'Narail', 'Magura', 'Jhenaidah', 
  'Bagerhat', 'Satkhira', 'Kushtia', 'Chuadanga', 'Meherpur', 'Sylhet', 
  'Moulvibazar', 'Habiganj', 'Sunamganj', 'Barisal', 'Bhola', 'Patuakhali', 
  'Pirojpur', 'Jhalokati', 'Barguna', 'Rangpur', 'Kurigram', 'Gaibandha', 
  'Lalmonirhat', 'Nilphamari', 'Thakurgaon', 'Panchagarh', 'Dinajpur', 
  'Mymensingh', 'Sherpur', 'Netrokona', 'Jamalpur'
];

// Transition component for full-screen dialogs
const Transition = React.forwardRef(function Transition(props, ref) {
  return <Slide direction="up" ref={ref} {...props} />;
});

// Enhanced Expense Entry Component
function ExpenseEntry({ entry, index, onUpdate, onRemove, categories, canRemove, isMobile }) {
  const [showMap, setShowMap] = useState(false);

  const handleReceiptUpload = (file) => {
    onUpdate(index, 'receipt_file', file);
  };

  const handleFieldUpdate = (field, value) => {
    onUpdate(index, field, value);
  };

  return (
    <Accordion defaultExpanded={index === 0} key={entry.id}>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box display="flex" alignItems="center" sx={{ width: '100%' }}>
          <Box display="flex" alignItems="center" sx={{ flex: 1, minWidth: 0 }}>
            {entry.transport_mode && (
              <Tooltip title={entry.transport_mode}>
                <Box sx={{ 
                  color: TRANSPORT_MODES.find(t => t.value === entry.transport_mode)?.color || '#757575',
                  mr: 1,
                  minWidth: 24
                }}>
                  {TRANSPORT_MODES.find(t => t.value === entry.transport_mode)?.icon}
                </Box>
              </Tooltip>
            )}
            <Typography variant="body1" noWrap sx={{ flex: 1 }}>
              {entry.title || `Entry ${index + 1}`}
            </Typography>
            {entry.amount > 0 && !isMobile && (
              <Chip 
                label={`৳${entry.amount}`}
                size="small" 
                color="primary" 
                sx={{ ml: 1 }}
              />
            )}
          </Box>
          {canRemove && (
            <IconButton 
              onClick={(e) => {
                e.stopPropagation();
                onRemove(index);
              }}
              color="error"
              size="small"
            >
              <RemoveIcon />
            </IconButton>
          )}
        </Box>
      </AccordionSummary>
      
      <AccordionDetails>
        <Grid container spacing={isMobile ? 2 : 3}>
          {/* Basic Info */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Expense Title"
              value={entry.title || ''}
              onChange={(e) => handleFieldUpdate('title', e.target.value)}
              required
              size={isMobile ? "small" : "medium"}
            />
          </Grid>
          
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Amount"
              type="number"
              value={entry.amount || ''}
              onChange={(e) => handleFieldUpdate('amount', parseFloat(e.target.value) || 0)}
              InputProps={{
                startAdornment: <InputAdornment position="start">৳</InputAdornment>,
              }}
              size={isMobile ? "small" : "medium"}
              required
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth size={isMobile ? "small" : "medium"}>
              <InputLabel>Transport Mode</InputLabel>
              <Select
                value={entry.transport_mode || ''}
                label="Transport Mode"
                onChange={(e) => handleFieldUpdate('transport_mode', e.target.value)}
              >
                {TRANSPORT_MODES.map((mode) => (
                  <MenuItem key={mode.value} value={mode.value}>
                    <Box display="flex" alignItems="center">
                      <Box sx={{ color: mode.color, mr: 1, minWidth: 24 }}>
                        {mode.icon}
                      </Box>
                      <Typography variant={isMobile ? "body2" : "body1"}>
                        {mode.label}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Location Fields */}
          <Grid item xs={12} sm={6}>
            <Autocomplete
              freeSolo
              options={[...DHAKA_AREAS, ...OTHER_BD_LOCATIONS]}
              groupBy={(option) => DHAKA_AREAS.includes(option) ? 'Dhaka City' : 'Other Areas'}
              value={entry.location_from || ''}
              onInputChange={(event, newValue) => handleFieldUpdate('location_from', newValue)}
              size={isMobile ? "small" : "medium"}
              renderInput={(params) => (
                <TextField 
                  {...params} 
                  label="From Location" 
                  InputProps={{
                    ...params.InputProps,
                    startAdornment: (
                      <>
                        <InputAdornment position="start">
                          <LocationOnIcon color="action" />
                        </InputAdornment>
                        {params.InputProps.startAdornment}
                      </>
                    ),
                  }}
                />
              )}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <Autocomplete
              freeSolo
              options={[...DHAKA_AREAS, ...OTHER_BD_LOCATIONS]}
              groupBy={(option) => DHAKA_AREAS.includes(option) ? 'Dhaka City' : 'Other Areas'}
              value={entry.location_to || ''}
              onInputChange={(event, newValue) => handleFieldUpdate('location_to', newValue)}
              size={isMobile ? "small" : "medium"}
              renderInput={(params) => (
                <TextField 
                  {...params} 
                  label="To Location"
                  InputProps={{
                    ...params.InputProps,
                    startAdornment: (
                      <>
                        <InputAdornment position="start">
                          <LocationOnIcon color="primary" />
                        </InputAdornment>
                        {params.InputProps.startAdornment}
                      </>
                    ),
                  }}
                />
              )}
            />
          </Grid>

          {/* Map Section */}
          {(entry.location_from || entry.location_to) && (
            <Grid item xs={12}>
              <Box sx={{ mb: 1 }}>
                <Button
                  size="small"
                  startIcon={<MapIcon />}
                  onClick={() => setShowMap(!showMap)}
                  variant="outlined"
                >
                  {showMap ? 'Hide Map' : 'Show Route Map'}
                </Button>
              </Box>
              {showMap && (
                <GoogleMapRoute 
                  origin={entry.location_from} 
                  destination={entry.location_to}
                  isFullscreen={false}
                />
              )}
            </Grid>
          )}

          {/* Category Selection */}
          <Grid item xs={12}>
            <FormControl fullWidth size={isMobile ? "small" : "medium"}>
              <InputLabel>Category (Auto-detect if empty)</InputLabel>
              <Select
                value={entry.category_id || ''}
                label="Category (Auto-detect if empty)"
                onChange={(e) => handleFieldUpdate('category_id', e.target.value || null)}
              >
                <MenuItem value="">
                  <Box display="flex" alignItems="center">
                    <SmartToyIcon sx={{ mr: 1, color: 'primary.main' }} />
                    <em>Auto-categorize with AI</em>
                  </Box>
                </MenuItem>
                {categories.map((category) => (
                  <MenuItem key={category.id} value={category.id}>
                    <Box display="flex" alignItems="center">
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          backgroundColor: category.color || '#ccc',
                          mr: 1
                        }}
                      />
                      {category.name}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Description */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Description"
              multiline
              rows={isMobile ? 2 : 3}
              value={entry.description || ''}
              onChange={(e) => handleFieldUpdate('description', e.target.value)}
              placeholder="Detailed description helps with automatic categorization"
              size={isMobile ? "small" : "medium"}
            />
          </Grid>

          {/* Receipt Upload */}
          <Grid item xs={12}>
            <Typography variant="subtitle2" gutterBottom>
              Receipt Upload
            </Typography>
            <ReceiptUpload
              onFileSelect={handleReceiptUpload}
              selectedFile={entry.receipt_file}
            />
          </Grid>
        </Grid>
      </AccordionDetails>
    </Accordion>
  );
}

export default function IntelligentExpensePage() {
  const { token } = useContext(AuthContext);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.between('sm', 'md'));
  
  // State Management
  const [expenses, setExpenses] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);
  const [editingExpenseId, setEditingExpenseId] = useState(null);
  
  // Dialog States
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [viewExpense, setViewExpense] = useState(null);
  
  // Form States
  const [expenseDate, setExpenseDate] = useState(new Date().toISOString().split('T')[0]);
  const [expenseEntries, setExpenseEntries] = useState([{
    id: `new-${Date.now()}`,
    title: '',
    amount: 0,
    category_id: null,
    transport_mode: '',
    location_from: '',
    location_to: '',
    description: '',
    receipt_file: null
  }]);
  
  // Speed Dial for mobile FAB actions
  const [speedDialOpen, setSpeedDialOpen] = useState(false);

  // Load data functions
  const loadExpenseCategories = useCallback(async () => {
    if (!token) return;
    try {
      const response = await axios.get('/expenses/categories', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCategories(response.data || []);
    } catch (error) {
      console.error('Failed to load categories:', error);
    }
  }, [token]);
  
  const loadMyExpenses = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const response = await axios.get('/expenses/my-expenses', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setExpenses(response.data || []);
    } catch (error) {
      console.error('Failed to load expenses:', error);
      toast.error('Failed to load expenses');
    } finally {
      setLoading(false);
    }
  }, [token]);
  
  // Initial data load
  useEffect(() => {
    if (!token || initialized) return;
    const loadInitialData = async () => {
      await Promise.all([loadExpenseCategories(), loadMyExpenses()]);
      setInitialized(true);
    };
    loadInitialData();
  }, [token, initialized, loadExpenseCategories, loadMyExpenses]);
  
  // Form management functions
  const updateExpenseEntry = (index, field, value) => {
    setExpenseEntries(prevEntries => {
      const updatedEntries = [...prevEntries];
      updatedEntries[index] = { ...updatedEntries[index], [field]: value };
      return updatedEntries;
    });
  };

  const addExpenseEntry = () => {
    const newEntry = {
      id: `new-${Date.now()}`,
      title: '',
      amount: 0,
      category_id: null,
      transport_mode: '',
      location_from: '',
      location_to: '',
      description: '',
      receipt_file: null
    };
    setExpenseEntries(prevEntries => [...prevEntries, newEntry]);
  };

  const removeExpenseEntry = (index) => {
    if (expenseEntries.length > 1) {
      setExpenseEntries(prevEntries => prevEntries.filter((_, i) => i !== index));
    }
  };

  const handleOpenCreateDialog = (expenseToEdit = null) => {
    if (expenseToEdit && expenseToEdit.status === 'draft') {
      setEditingExpenseId(expenseToEdit.id);
      setExpenseDate(format(parseISO(expenseToEdit.expense_date), 'yyyy-MM-dd'));
      setExpenseEntries([{
        id: expenseToEdit.id,
        title: expenseToEdit.title,
        amount: expenseToEdit.amount / 100,
        category_id: expenseToEdit.category_id,
        transport_mode: expenseToEdit.transport_mode,
        location_from: expenseToEdit.location_from,
        location_to: expenseToEdit.location_to,
        description: expenseToEdit.description,
        receipt_file: null
      }]);
    } else {
      resetExpenseForm();
    }
    setCreateDialogOpen(true);
  };

  const resetExpenseForm = () => {
    setEditingExpenseId(null);
    setExpenseDate(new Date().toISOString().split('T')[0]);
    setExpenseEntries([{
      id: `new-${Date.now()}`,
      title: '',
      amount: 0,
      category_id: null,
      transport_mode: '',
      location_from: '',
      location_to: '',
      description: '',
      receipt_file: null
    }]);
  };

  const saveExpenses = async () => {
    const validEntries = expenseEntries.filter(entry => entry.title && entry.amount > 0);
    if (validEntries.length === 0) {
      toast.error('Please fill in at least one complete expense entry');
      return;
    }

    setLoading(true);
    try {
      // For single expense (editing mode)
      if (editingExpenseId) {
        const entry = validEntries[0];
        const expenseData = {
          title: entry.title,
          amount: Math.round(entry.amount * 100), // Convert to paisa
          description: entry.description || '',
          transport_mode: entry.transport_mode || null,
          location_from: entry.location_from || null,
          location_to: entry.location_to || null,
          category_id: entry.category_id || null,
          expense_date: expenseDate
        };

        const response = await axios.put(`/expenses/${editingExpenseId}/update`, expenseData, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        toast.success('Expense updated successfully');
      } else {
        // For batch creation
        const entries = validEntries.map(entry => ({
          title: entry.title,
          amount: Math.round(entry.amount * 100), // Convert to paisa
          description: entry.description || '',
          transport_mode: entry.transport_mode || null,
          location_from: entry.location_from || null,
          location_to: entry.location_to || null,
          category_id: entry.category_id || null,
        }));

        const requestData = {
          expense_date: expenseDate,
          entries: entries
        };

        const response = await axios.post('/expenses/create_batch', requestData, {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        toast.success(`${validEntries.length} expense(s) created successfully`);
      }

      setCreateDialogOpen(false);
      await loadMyExpenses();
      resetExpenseForm();
    } catch (error) {
      console.error('Failed to save expenses:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to save expenses';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const submitExpense = async (expenseId) => {
    try {
      const response = await axios.post(`/expenses/${expenseId}/submit`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Expense submitted successfully');
      await loadMyExpenses();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to submit expense');
    }
  };

  const formatBDT = (paisa) => `৳${(paisa / 100).toLocaleString('en-BD', { minimumFractionDigits: 2 })}`;

  const getStatusChip = (status) => {
    const config = {
      approved: { color: 'success', icon: <CheckCircleIcon /> },
      rejected: { color: 'error', icon: <CancelIcon /> },
      submitted: { color: 'warning', icon: <HourglassEmptyIcon /> },
      draft: { color: 'default', icon: <EditIcon /> }
    };
    const { color, icon } = config[status] || { color: 'default', icon: <ScheduleIcon /> };
    
    return (
      <Chip
        icon={icon}
        label={status.toUpperCase()}
        color={color}
        size="small"
      />
    );
  };

  const getTotalAmount = () => {
    return expenseEntries.reduce((sum, entry) => sum + (entry.amount || 0), 0);
  };

  if (!token) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="warning">Please log in to access Smart Expenses.</Alert>
      </Container>
    );
  }
  
  return (
    <Container maxWidth="xl" sx={{ 
      mt: isMobile ? 2 : 4, 
      mb: isMobile ? 2 : 4, 
      px: isMobile ? 1 : 3 
    }}>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant={isMobile ? "h5" : "h4"} component="h1">
          <AutoAwesomeIcon sx={{ mr: 1, verticalAlign: 'middle', color: 'primary.main' }} />
          Smart Expenses
        </Typography>
        
        {isMobile ? (
          <SpeedDial
            ariaLabel="Expense Actions"
            sx={{ position: 'fixed', bottom: 16, right: 16 }}
            icon={<SpeedDialIcon />}
            onClose={() => setSpeedDialOpen(false)}
            onOpen={() => setSpeedDialOpen(true)}
            open={speedDialOpen}
          >
            <SpeedDialAction
              icon={<AddIcon />}
              tooltipTitle="Add Expense"
              onClick={() => {
                setSpeedDialOpen(false);
                handleOpenCreateDialog();
              }}
            />
          </SpeedDial>
        ) : (
          <Fab color="primary" onClick={() => handleOpenCreateDialog()}>
            <AddIcon />
          </Fab>
        )}
      </Box>

      {/* Loading State */}
      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Expenses Grid */}
      <Grid container spacing={isMobile ? 1 : 3}>
        {expenses.length === 0 ? (
          <Grid item xs={12}>
            <Paper sx={{ p: isMobile ? 2 : 4, textAlign: 'center' }}>
              <ReceiptIcon sx={{ 
                fontSize: isMobile ? 48 : 64, 
                color: 'text.secondary', 
                mb: 2 
              }} />
              <Typography variant="h6" gutterBottom>
                No expenses found
              </Typography>
              <Typography color="text.secondary" gutterBottom>
                Create your first smart expense to get started
              </Typography>
              <Button
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => handleOpenCreateDialog()}
                sx={{ mt: 2 }}
                size={isMobile ? "small" : "medium"}
              >
                Create Expense
              </Button>
            </Paper>
          </Grid>
        ) : (
          expenses.map((expense) => (
            <Grid item xs={12} sm={6} md={4} key={expense.id}>
              <Card 
                className="expense-card"
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  {/* Header */}
                  <Box display="flex" justifyContent="space-between" alignItems="start" mb={1}>
                    <Typography 
                      variant={isMobile ? "body1" : "h6"} 
                      noWrap 
                      sx={{ flex: 1, mr: 1 }}
                    >
                      {expense.title}
                    </Typography>
                    {getStatusChip(expense.status)}
                  </Box>

                  {/* Amount */}
                  <Typography 
                    variant={isMobile ? "h5" : "h4"} 
                    color="primary" 
                    gutterBottom
                  >
                    {formatBDT(expense.amount)}
                  </Typography>

                  {/* Transport Mode */}
                  {expense.transport_mode && (
                    <Box display="flex" alignItems="center" mb={1}>
                      <Box sx={{ 
                        color: TRANSPORT_MODES.find(t => t.value === expense.transport_mode)?.color,
                        mr: 1,
                        minWidth: 20
                      }}>
                        {TRANSPORT_MODES.find(t => t.value === expense.transport_mode)?.icon}
                      </Box>
                      <Typography variant="caption" color="text.secondary">
                        {TRANSPORT_MODES.find(t => t.value === expense.transport_mode)?.label}
                      </Typography>
                    </Box>
                  )}

                  {/* Location */}
                  {(expense.location_from || expense.location_to) && (
                    <Box display="flex" alignItems="center" mb={1}>
                      <LocationOnIcon sx={{ fontSize: 16, mr: 0.5, color: 'text.secondary' }} />
                      <Typography variant="body2" color="text.secondary" noWrap>
                        {expense.location_from || '...'} → {expense.location_to || '...'}
                      </Typography>
                    </Box>
                  )}

                  {/* Date */}
                  <Typography variant="body2" color="text.secondary">
                    {format(parseISO(expense.expense_date), 'MMM dd, yyyy')}
                  </Typography>

                  {/* AI Badge */}
                  {expense.auto_categorized && (
                    <Tooltip title={`Auto-categorized with ${expense.confidence_score}% confidence`}>
                      <Chip
                        icon={<SmartToyIcon />}
                        label="AI"
                        size="small"
                        color="info"
                        sx={{ mt: 1 }}
                      />
                    </Tooltip>
                  )}
                </CardContent>

                <CardActions sx={{ px: 2, pb: 2 }}>
                  <IconButton 
                    size="small"
                    onClick={() => setViewExpense(expense)}
                  >
                    <VisibilityIcon />
                  </IconButton>
                  
                  {expense.status === 'draft' && (
                    <>
                      <IconButton 
                        size="small"
                        onClick={() => handleOpenCreateDialog(expense)}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton 
                        size="small"
                        onClick={() => submitExpense(expense.id)}
                      >
                        <SendIcon />
                      </IconButton>
                    </>
                  )}
                </CardActions>
              </Card>
            </Grid>
          ))
        )}
      </Grid>

      {/* Create/Edit Expense Dialog */}
      <Dialog 
        open={createDialogOpen} 
        onClose={() => setCreateDialogOpen(false)} 
        maxWidth="lg" 
        fullWidth
        fullScreen={isMobile}
        TransitionComponent={isMobile ? Transition : undefined}
      >
        {isMobile && (
          <AppBar sx={{ position: 'relative' }}>
            <Toolbar>
              <IconButton
                edge="start"
                color="inherit"
                onClick={() => setCreateDialogOpen(false)}
                aria-label="close"
              >
                <CloseIcon />
              </IconButton>
              <Typography sx={{ ml: 2, flex: 1 }} variant="h6" component="div">
                {editingExpenseId ? 'Edit Expense' : 'New Expense'}
              </Typography>
              <Button color="inherit" onClick={saveExpenses} disabled={loading}>
                <SaveIcon sx={{ mr: 1 }} />
                Save
              </Button>
            </Toolbar>
          </AppBar>
        )}
        
        {!isMobile && (
          <DialogTitle>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h6">
                {editingExpenseId ? 'Edit Expense' : 'Create Smart Expenses'}
              </Typography>
              <Typography variant="h6" color="primary">
                Total: ৳{getTotalAmount().toFixed(2)}
              </Typography>
            </Box>
          </DialogTitle>
        )}
        
        <DialogContent 
          dividers={!isMobile}
          className="expense-form-container"
          sx={{ p: isMobile ? 1 : 2 }}
        >
          {isMobile && (
            <Box sx={{ mb: 2, p: 2, bgcolor: 'primary.main', color: 'white', borderRadius: 1 }}>
              <Typography variant="h6">
                Total: ৳{getTotalAmount().toFixed(2)}
              </Typography>
            </Box>
          )}
          
          <Box sx={{ mb: 3 }}>
            <TextField
              fullWidth
              label="Expense Date"
              type="date"
              value={expenseDate}
              onChange={(e) => setExpenseDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              size={isMobile ? "small" : "medium"}
              required
            />
          </Box>

          {expenseEntries.map((entry, index) => (
            <ExpenseEntry
              key={entry.id || index}
              entry={entry}
              index={index}
              onUpdate={updateExpenseEntry}
              onRemove={removeExpenseEntry}
              categories={categories}
              canRemove={expenseEntries.length > 1}
              isMobile={isMobile}
            />
          ))}

          {!editingExpenseId && (
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <Button
                variant="outlined"
                onClick={addExpenseEntry}
                startIcon={<AddIcon />}
                size={isMobile ? "small" : "medium"}
                fullWidth={isMobile}
              >
                Add Another Entry
              </Button>
            </Box>
          )}
        </DialogContent>
        
        {!isMobile && (
          <DialogActions sx={{ p: 2 }}>
            <Button onClick={() => setCreateDialogOpen(false)}>
              Cancel
            </Button>
            <Button 
              onClick={saveExpenses} 
              variant="contained" 
              disabled={loading}
              startIcon={loading ? null : <SaveIcon />}
            >
              {loading ? 'Saving...' : (editingExpenseId ? 'Update' : 'Create')} Expense{expenseEntries.length > 1 ? 's' : ''}
            </Button>
          </DialogActions>
        )}
      </Dialog>

      {/* View Expense Dialog */}
      <Dialog 
        open={!!viewExpense} 
        onClose={() => setViewExpense(null)} 
        maxWidth="md" 
        fullWidth
        fullScreen={isMobile}
        TransitionComponent={isMobile ? Transition : undefined}
      >
        {viewExpense && (
          <>
            {isMobile && (
              <AppBar sx={{ position: 'relative' }}>
                <Toolbar>
                  <IconButton
                    edge="start"
                    color="inherit"
                    onClick={() => setViewExpense(null)}
                  >
                    <CloseIcon />
                  </IconButton>
                  <Typography sx={{ ml: 2, flex: 1 }} variant="h6" component="div">
                    Expense Details
                  </Typography>
                </Toolbar>
              </AppBar>
            )}
            
            {!isMobile && (
              <DialogTitle>
                {viewExpense.title}
              </DialogTitle>
            )}
            
            <DialogContent sx={{ p: isMobile ? 1 : 2 }}>
              <Box sx={{ mb: 2 }}>
                <Typography 
                  variant={isMobile ? "h4" : "h3"} 
                  color="primary" 
                  gutterBottom
                >
                  {formatBDT(viewExpense.amount)}
                </Typography>
                {getStatusChip(viewExpense.status)}
              </Box>
              
              <Typography variant="body1" paragraph>
                <strong>Date:</strong> {format(parseISO(viewExpense.expense_date), 'MMM dd, yyyy')}
              </Typography>
              
              {viewExpense.description && (
                <Typography variant="body1" paragraph>
                  <strong>Description:</strong> {viewExpense.description}
                </Typography>
              )}
              
              {(viewExpense.location_from || viewExpense.location_to) && (
                <>
                  <Typography variant="body1" paragraph>
                    <strong>Route:</strong> {viewExpense.location_from || 'N/A'} → {viewExpense.location_to || 'N/A'}
                  </Typography>
                  <GoogleMapRoute 
                    origin={viewExpense.location_from} 
                    destination={viewExpense.location_to}
                    isFullscreen={true}
                  />
                </>
              )}
            </DialogContent>
            
            {!isMobile && (
              <DialogActions>
                <Button onClick={() => setViewExpense(null)}>
                  Close
                </Button>
              </DialogActions>
            )}
          </>
        )}
      </Dialog>
    </Container>
  );
}
