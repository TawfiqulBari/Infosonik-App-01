import React, { useState, useEffect, useContext } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Paper,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Menu,
  MenuItem,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  TextField,
  FormControl,
  InputLabel,
  Select,
  Chip,
  Card,
  CardContent,
  IconButton,
} from '@mui/material';
import {
  GetApp as DownloadIcon,
  Share as ShareIcon,
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon,
  Assessment as ReportIcon,
} from '@mui/icons-material';
import { TabContext, TabPanel } from '@mui/lab';
import { AuthContext } from '../contexts/AuthContext';
import axios from 'axios';
import { toast } from 'react-toastify';
import { format, subDays, subMonths } from 'date-fns';

function AdminPage() {
  const { token } = useContext(AuthContext);
  const [tabValue, setTabValue] = useState('1');
  const [expenses, setExpenses] = useState([]);
  const [reports, setReports] = useState([]);
  const [groups, setGroups] = useState([]);
  const [selectedGroup, setSelectedGroup] = useState('');
  const [selectedPeriod, setSelectedPeriod] = useState('monthly');
  const [reportMenuAnchor, setReportMenuAnchor] = useState(null);
  const [shareMenuAnchor, setShareMenuAnchor] = useState(null);
  const [reportDialogOpen, setReportDialogOpen] = useState(false);
  const [selectedReport, setSelectedReport] = useState(null);

  useEffect(() => {
    fetchGroups();
    fetchExpenses();
    fetchReports();
  }, [selectedGroup]);

  const fetchGroups = async () => {
    try {
      const response = await axios.get('/admin/groups', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setGroups(response.data);
    } catch (error) {
      toast.error('Failed to load groups');
    }
  };

  const fetchExpenses = async () => {
    try {
      let url = '/admin/expenses';
      if (selectedGroup) {
        url += `?group=${selectedGroup}`;
      }
      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setExpenses(response.data);
    } catch (error) {
      toast.error('Failed to load expenses');
    }
  };

  const fetchReports = async () => {
    try {
      const response = await axios.get('/admin/reports', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setReports(response.data);
    } catch (error) {
      toast.error('Failed to load reports');
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleGroupSelect = (event) => {
    setSelectedGroup(event.target.value);
  };

  const handlePeriodSelect = (event) => {
    setSelectedPeriod(event.target.value);
  };

  const approveExpense = async (expenseId) => {
    try {
      await axios.post(`/admin/expenses/${expenseId}/approve`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Expense approved successfully');
      fetchExpenses();
    } catch (error) {
      toast.error('Failed to approve expense');
    }
  };

  const rejectExpense = async (expenseId) => {
    try {
      await axios.post(`/admin/expenses/${expenseId}/reject`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Expense rejected successfully');
      fetchExpenses();
    } catch (error) {
      toast.error('Failed to reject expense');
    }
  };

  const generateReport = async () => {
    try {
      const days = selectedPeriod === 'monthly' ? 30 : selectedPeriod === 'weekly' ? 7 : 1;
      const startDate = subDays(new Date(), days);
      const endDate = new Date();
      
      const reportData = {
        group_id: selectedGroup || null,
        period: selectedPeriod,
        start_date: format(startDate, 'yyyy-MM-dd'),
        end_date: format(endDate, 'yyyy-MM-dd'),
        format: 'pdf'
      };

      const response = await axios.post('/admin/reports/generate', reportData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      toast.success('Report generated successfully');
      setReportDialogOpen(false);
      fetchReports();
    } catch (error) {
      toast.error('Failed to generate report');
    }
  };

  const downloadReport = async (reportId, format) => {
    try {
      const response = await axios.get(`/admin/reports/${reportId}/download?format=${format}`, {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `expense_report.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('Report downloaded successfully');
    } catch (error) {
      toast.error('Failed to download report');
    }
  };

  const shareReport = async (reportId, method) => {
    try {
      const response = await axios.post(`/admin/reports/${reportId}/share`, {
        method: method
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (method === 'link') {
        navigator.clipboard.writeText(response.data.share_link);
        toast.success('Link copied to clipboard');
      } else {
        toast.success(`Report shared via ${method}`);
      }
      
      setShareMenuAnchor(null);
    } catch (error) {
      toast.error(`Failed to share via ${method}`);
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
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          <ReportIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
          Admin Management Panel
        </Typography>
      </Box>

      <TabContext value={tabValue}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={tabValue} onChange={handleTabChange} aria-label="admin tabs">
            <Tab label="Expense Approvals" value="1" />
            <Tab label="Report Generation" value="2" />
            <Tab label="User Management" value="3" />
          </Tabs>
        </Box>

        <TabPanel value="1">
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Filter by Group</InputLabel>
                <Select value={selectedGroup} label="Filter by Group" onChange={handleGroupSelect}>
                  <MenuItem value="">
                    <em>All Groups</em>
                  </MenuItem>
                  {groups.map(group => (
                    <MenuItem key={group.id} value={group.id}>{group.name}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          <Paper elevation={3}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Date</TableCell>
                    <TableCell>User</TableCell>
                    <TableCell>Group</TableCell>
                    <TableCell>Amount (BDT)</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {expenses.map(expense => (
                    <TableRow key={expense.id} hover>
                      <TableCell>
                        {format(new Date(expense.bill_date), 'MMM dd, yyyy')}
                      </TableCell>
                      <TableCell>{expense.user_name}</TableCell>
                      <TableCell>{expense.group_name || 'N/A'}</TableCell>
                      <TableCell>{formatBDT(expense.total_amount)}</TableCell>
                      <TableCell>
                        {expense.general_description?.substring(0, 50)}
                        {expense.general_description?.length > 50 ? '...' : ''}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={expense.status.toUpperCase()}
                          color={getStatusColor(expense.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        {expense.status === 'pending' && (
                          <>
                            <IconButton
                              color="success"
                              onClick={() => approveExpense(expense.id)}
                              title="Approve"
                            >
                              <ApproveIcon />
                            </IconButton>
                            <IconButton
                              color="error"
                              onClick={() => rejectExpense(expense.id)}
                              title="Reject"
                            >
                              <RejectIcon />
                            </IconButton>
                          </>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </TabPanel>

        <TabPanel value="2">
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>Generate Expense Report</Typography>
                  
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth>
                        <InputLabel>Report Period</InputLabel>
                        <Select value={selectedPeriod} label="Report Period" onChange={handlePeriodSelect}>
                          <MenuItem value="daily">Daily</MenuItem>
                          <MenuItem value="weekly">Weekly</MenuItem>
                          <MenuItem value="monthly">Monthly</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    
                    <Grid item xs={12} md={6}>
                      <FormControl fullWidth>
                        <InputLabel>Group Filter</InputLabel>
                        <Select value={selectedGroup} label="Group Filter" onChange={handleGroupSelect}>
                          <MenuItem value="">
                            <em>All Groups</em>
                          </MenuItem>
                          {groups.map(group => (
                            <MenuItem key={group.id} value={group.id}>{group.name}</MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                  </Grid>
                  
                  <Button
                    variant="contained"
                    onClick={generateReport}
                    startIcon={<ReportIcon />}
                    size="large"
                  >
                    Generate Report
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          <Box sx={{ mt: 4 }}>
            <Typography variant="h6" gutterBottom>Generated Reports</Typography>
            
            <Grid container spacing={2}>
              {reports.map(report => (
                <Grid item xs={12} md={6} key={report.id}>
                  <Card>
                    <CardContent>
                      <Typography variant="h6">
                        {report.report_type} Report - {report.report_period}
                      </Typography>
                      <Typography color="textSecondary" gutterBottom>
                        Generated: {format(new Date(report.generated_at), 'MMM dd, yyyy HH:mm')}
                      </Typography>
                      <Typography variant="body2">
                        Period: {format(new Date(report.start_date), 'MMM dd')} - {format(new Date(report.end_date), 'MMM dd, yyyy')}
                      </Typography>
                      
                      <Box sx={{ mt: 2 }}>
                        <Button
                          startIcon={<DownloadIcon />}
                          onClick={() => downloadReport(report.id, 'pdf')}
                          sx={{ mr: 1 }}
                        >
                          PDF
                        </Button>
                        <Button
                          startIcon={<DownloadIcon />}
                          onClick={() => downloadReport(report.id, 'excel')}
                          sx={{ mr: 1 }}
                        >
                          Excel
                        </Button>
                        <Button
                          startIcon={<ShareIcon />}
                          onClick={(e) => {
                            setSelectedReport(report);
                            setShareMenuAnchor(e.currentTarget);
                          }}
                        >
                          Share
                        </Button>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>

          <Menu
            anchorEl={shareMenuAnchor}
            open={Boolean(shareMenuAnchor)}
            onClose={() => setShareMenuAnchor(null)}
          >
            <MenuItem onClick={() => shareReport(selectedReport?.id, 'email')}>
              Email
            </MenuItem>
            <MenuItem onClick={() => shareReport(selectedReport?.id, 'whatsapp')}>
              WhatsApp
            </MenuItem>
            <MenuItem onClick={() => shareReport(selectedReport?.id, 'drive')}>
              Save to Drive
            </MenuItem>
            <MenuItem onClick={() => shareReport(selectedReport?.id, 'link')}>
              Copy Link
            </MenuItem>
          </Menu>
        </TabPanel>

        <TabPanel value="3">
          <Typography variant="h6">User & Group Management</Typography>
          <Typography variant="body2" color="textSecondary">
            User and group management features coming soon...
          </Typography>
        </TabPanel>
      </TabContext>
    </Container>
  );
}

export default AdminPage;
