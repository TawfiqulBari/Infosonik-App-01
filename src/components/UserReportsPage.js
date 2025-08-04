import React, { useState, useEffect, useContext } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Box,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Divider,
} from '@mui/material';
import {
  Assessment as ReportIcon,
  GetApp as DownloadIcon,
  DateRange as DateIcon,
} from '@mui/icons-material';
import { AuthContext } from '../contexts/AuthContext';
import axios from 'axios';
import { toast } from 'react-toastify';
import { format, startOfMonth, endOfMonth, subMonths } from 'date-fns';

export default function UserReportsPage() {
  const { token } = useContext(AuthContext);
  const [monthlyData, setMonthlyData] = useState([]);
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth());
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  const [summary, setSummary] = useState({});
  const [loading, setLoading] = useState(true);

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const currentYear = new Date().getFullYear();
  const years = Array.from({ length: 5 }, (_, i) => currentYear - i);

  useEffect(() => {
    fetchMonthlyReport();
  }, [selectedMonth, selectedYear]);

  const fetchMonthlyReport = async () => {
    if (!token) {
      toast.error('Please log in to view reports');
      setLoading(false);
      return;
    }

    try {
      const startDate = startOfMonth(new Date(selectedYear, selectedMonth));
      const endDate = endOfMonth(new Date(selectedYear, selectedMonth));
      
      const response = await axios.get('/bills/monthly-report', {
        params: {
          start_date: format(startDate, 'yyyy-MM-dd'),
          end_date: format(endDate, 'yyyy-MM-dd')
        },
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      setMonthlyData(response.data.expenses || []);
      setSummary(response.data.summary || {});
    } catch (error) {
      toast.error('Failed to load monthly report');
      console.error('Monthly report error:', error);
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async (format) => {
    try {
      const startDate = startOfMonth(new Date(selectedYear, selectedMonth));
      const endDate = endOfMonth(new Date(selectedYear, selectedMonth));
      
      const response = await axios.get('/bills/download-report', {
        params: {
          start_date: format(startDate, 'yyyy-MM-dd'),
          end_date: format(endDate, 'yyyy-MM-dd'),
          format: format
        },
        headers: {
          Authorization: `Bearer ${token}`
        },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `expense_report_${selectedYear}_${selectedMonth + 1}.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Report downloaded successfully');
    } catch (error) {
      toast.error('Failed to download report');
    }
  };

  const formatBDT = (paisa) => {
    const taka = paisa / 100;
    return `৳${taka.toFixed(2)}`;
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          <ReportIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          My Expense Reports
        </Typography>
      </Box>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Month</InputLabel>
            <Select
              value={selectedMonth}
              label="Month"
              onChange={(e) => setSelectedMonth(e.target.value)}
            >
              {months.map((month, index) => (
                <MenuItem key={index} value={index}>{month}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Year</InputLabel>
            <Select
              value={selectedYear}
              label="Year"
              onChange={(e) => setSelectedYear(e.target.value)}
            >
              {years.map((year) => (
                <MenuItem key={year} value={year}>{year}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Box sx={{ display: 'flex', gap: 1, height: '100%', alignItems: 'center' }}>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={() => downloadReport('pdf')}
            >
              PDF
            </Button>
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={() => downloadReport('excel')}
            >
              Excel
            </Button>
          </Box>
        </Grid>
      </Grid>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Expenses
              </Typography>
              <Typography variant="h4" color="primary">
                {formatBDT(summary.total_amount || 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Transportation
              </Typography>
              <Typography variant="h5">
                {formatBDT(summary.transport_total || 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Food
              </Typography>
              <Typography variant="h5">
                {formatBDT(summary.food_total || 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Other Expenses
              </Typography>
              <Typography variant="h5">
                {formatBDT((summary.fuel_total || 0) + (summary.rental_total || 0) + (summary.other_total || 0))}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Expense Table */}
      <Paper elevation={3}>
        <Box sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            <DateIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Detailed Expenses - {months[selectedMonth]} {selectedYear}
          </Typography>
        </Box>
        
        <Divider />
        
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Description</TableCell>
                <TableCell align="right">Transportation</TableCell>
                <TableCell align="right">Food</TableCell>
                <TableCell align="right">Fuel</TableCell>
                <TableCell align="right">Rental</TableCell>
                <TableCell align="right">Other</TableCell>
                <TableCell align="right">Total</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    Loading expenses...
                  </TableCell>
                </TableRow>
              ) : monthlyData.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    No expenses found for {months[selectedMonth]} {selectedYear}
                  </TableCell>
                </TableRow>
              ) : (
                monthlyData.map((expense) => (
                  <TableRow key={expense.id} hover>
                    <TableCell>
                      {format(new Date(expense.bill_date), 'MMM dd')}
                    </TableCell>
                    <TableCell>
                      {expense.general_description?.substring(0, 30)}
                      {expense.general_description?.length > 30 ? '...' : ''}
                    </TableCell>
                    <TableCell align="right">
                      {expense.transport_amount > 0 ? formatBDT(expense.transport_amount) : '-'}
                    </TableCell>
                    <TableCell align="right">
                      {expense.food_amount > 0 ? formatBDT(expense.food_amount) : '-'}
                    </TableCell>
                    <TableCell align="right">
                      {expense.fuel_cost > 0 ? formatBDT(expense.fuel_cost) : '-'}
                    </TableCell>
                    <TableCell align="right">
                      {expense.rental_cost > 0 ? formatBDT(expense.rental_cost) : '-'}
                    </TableCell>
                    <TableCell align="right">
                      {expense.other_amount > 0 ? formatBDT(expense.other_amount) : '-'}
                    </TableCell>
                    <TableCell align="right">
                      <Typography variant="body2" fontWeight="bold">
                        {formatBDT(expense.total_amount)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        color={
                          expense.status === 'approved' ? 'success.main' :
                          expense.status === 'rejected' ? 'error.main' : 'warning.main'
                        }
                      >
                        {expense.status.toUpperCase()}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Container>
  );
}
