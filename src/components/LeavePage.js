import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  LinearProgress,
  Tooltip,
  Badge,
  Alert,
  CircularProgress,
  Avatar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControlLabel,
  Switch,
  IconButton,
  Menu,
  ListItemIcon,
  ListItemText,
  Divider,
  Stack,
  Breadcrumbs,
  Link,
} from '@mui/material';
import {
  Add as AddIcon,
  FilterList as FilterIcon,
  GetApp as DownloadIcon,
  Visibility as ViewIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Check as ApproveIcon,
  Close as RejectIcon,
  AccessTime as PendingIcon,
  CheckCircle as ApprovedIcon,
  Cancel as RejectedIcon,
  Schedule as ScheduleIcon,
  Today as TodayIcon,
  DateRange as CalendarIcon,
  Person as PersonIcon,
  Work as WorkIcon,
  LocalHospital as MedicalIcon,
  Flight as VacationIcon,
  ChildCare as MaternityIcon,
  Elderly as FamilyIcon,
  School as StudyIcon,
  ExpandMore as ExpandMoreIcon,
  MoreVert as MoreVertIcon,
  Refresh as RefreshIcon,
  Assessment as ReportIcon,
  CalendarToday as CalendarTodayIcon,
  Event as EventIcon,
  TrendingUp as TrendingUpIcon,
  Money as MoneyIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import api from '../utils/api';
import { toast } from 'react-toastify';

// Leave types configuration
const LEAVE_TYPES = {
  casual: { label: 'Casual Leave', color: '#4CAF50', icon: TodayIcon },
  sick: { label: 'Sick Leave', color: '#f44336', icon: MedicalIcon },
  earned: { label: 'Earned Leave', color: '#2196F3', icon: VacationIcon },
  maternity: { label: 'Maternity Leave', color: '#9C27B0', icon: MaternityIcon },
  paternity: { label: 'Paternity Leave', color: '#FF5722', icon: FamilyIcon },
  study: { label: 'Study Leave', color: '#795548', icon: StudyIcon },
  special: { label: 'Special Leave', color: '#607D8B', icon: WorkIcon },
};

// Status configuration
const STATUS_CONFIG = {
  pending: { label: 'Pending', color: '#ff9800', icon: PendingIcon },
  approved: { label: 'Approved', color: '#4caf50', icon: ApprovedIcon },
  rejected: { label: 'Rejected', color: '#f44336', icon: RejectedIcon },
};

function TabPanel(props) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const LeavePage = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [leaveBalances, setLeaveBalances] = useState([]);
  const [myApplications, setMyApplications] = useState([]);
  const [pendingApprovals, setPendingApprovals] = useState([]);
  const [teamCalendar, setTeamCalendar] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedApplication, setSelectedApplication] = useState(null);
  const [newLeaveForm, setNewLeaveForm] = useState({
    leave_type: 'casual',
    start_date: '',
    end_date: '',
    reason: '',
    is_half_day: false,
    half_day_period: 'morning'
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [balanceResponse, applicationResponse, policyResponse] = await Promise.all([
        api.get('/leave/balances'),
        api.get('/leave/my-applications'),
        api.get('/leave/policies'),
      ]);
      
      setLeaveBalances(balanceResponse.data);
      setMyApplications(applicationResponse.data);
      setPolicies(policyResponse.data);
      
      if (user.role === 'manager' || user.role === 'hr' || user.role === 'admin') {
        const pendingResponse = await api.get('/leave/pending-approvals');
        setPendingApprovals(pendingResponse.data);
        
        const calendarResponse = await api.get('/leave/team-calendar');
        setTeamCalendar(calendarResponse.data);
      }
    } catch (error) {
      console.error('Error loading leave data:', error);
      toast.error('Failed to load leave data');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitLeave = async () => {
    try {
      await api.post('/leave/applications', newLeaveForm);
      toast.success('Leave application submitted successfully');
      setDialogOpen(false);
      setNewLeaveForm({
        leave_type: 'casual',
        start_date: '',
        end_date: '',
        reason: '',
        is_half_day: false,
        half_day_period: 'morning'
      });
      loadData();
    } catch (error) {
      console.error('Error submitting leave:', error);
      toast.error('Failed to submit leave application');
    }
  };

  const handleApproveReject = async (applicationId, action, comments = '') => {
    try {
      await api.put(`/leave/applications/${applicationId}/approve`, {
        action,
        comments
      });
      toast.success(`Leave ${action} successfully`);
      loadData();
    } catch (error) {
      console.error(`Error ${action} leave:`, error);
      toast.error(`Failed to ${action} leave application`);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Leave Management
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setDialogOpen(true)}
          sx={{ bgcolor: '#1976d2' }}
        >
          Apply for Leave
        </Button>
      </Box>

      <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="My Leave Balance" />
        <Tab label="My Applications" />
        {(user.role === 'manager' || user.role === 'hr' || user.role === 'admin') && (
          <>
            <Tab label="Pending Approvals" />
            <Tab label="Team Calendar" />
            <Tab label="Reports" />
          </>
        )}
        <Tab label="Leave Policies" />
      </Tabs>

      {/* My Leave Balance Tab */}
      <TabPanel value={activeTab} index={0}>
        <Grid container spacing={3}>
          {leaveBalances.map((balance) => {
            const leaveConfig = LEAVE_TYPES[balance.leave_type] || {};
            const usedPercentage = (balance.used / balance.annual_entitlement) * 100;
            
            return (
              <Grid item xs={12} md={6} lg={4} key={balance.leave_type}>
                <Card sx={{ height: '100%' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar
                        sx={{
                          bgcolor: leaveConfig.color + '20',
                          color: leaveConfig.color,
                          mr: 2
                        }}
                      >
                        {React.createElement(leaveConfig.icon || WorkIcon)}
                      </Avatar>
                      <Box>
                        <Typography variant="h6" component="div">
                          {leaveConfig.label}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {balance.available} of {balance.annual_entitlement} days available
                        </Typography>
                      </Box>
                    </Box>
                    
                    <Box sx={{ mb: 2 }}>
                      <LinearProgress
                        variant="determinate"
                        value={usedPercentage}
                        sx={{
                          height: 8,
                          borderRadius: 4,
                          backgroundColor: '#f0f0f0',
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: leaveConfig.color,
                            borderRadius: 4,
                          }
                        }}
                      />
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Used: {balance.used}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Remaining: {balance.available}
                        </Typography>
                      </Box>
                    </Box>

                    {balance.carry_forward > 0 && (
                      <Chip
                        label={`${balance.carry_forward} carried forward`}
                        size="small"
                        color="info"
                        sx={{ mb: 1 }}
                      />
                    )}
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      </TabPanel>

      {/* My Applications Tab */}
      <TabPanel value={activeTab} index={1}>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Leave Type</TableCell>
                <TableCell>Dates</TableCell>
                <TableCell>Days</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Applied On</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {myApplications.map((application) => {
                const leaveConfig = LEAVE_TYPES[application.leave_type] || {};
                const statusConfig = STATUS_CONFIG[application.status] || {};
                
                return (
                  <TableRow key={application.id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {React.createElement(leaveConfig.icon || WorkIcon, {
                          sx: { mr: 1, color: leaveConfig.color }
                        })}
                        {leaveConfig.label}
                      </Box>
                    </TableCell>
                    <TableCell>
                      {application.start_date} to {application.end_date}
                      {application.is_half_day && (
                        <Chip label={`Half Day (${application.half_day_period})`} size="small" sx={{ ml: 1 }} />
                      )}
                    </TableCell>
                    <TableCell>{application.total_days}</TableCell>
                    <TableCell>
                      <Chip
                        icon={React.createElement(statusConfig.icon || PendingIcon, { sx: { fontSize: 16 } })}
                        label={statusConfig.label}
                        sx={{
                          bgcolor: `${statusConfig.color}20`,
                          color: statusConfig.color,
                          '& .MuiChip-icon': { color: statusConfig.color }
                        }}
                      />
                    </TableCell>
                    <TableCell>{new Date(application.created_at).toLocaleDateString()}</TableCell>
                    <TableCell>
                      <IconButton onClick={() => setSelectedApplication(application)}>
                        <ViewIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      {/* Leave Policies Tab */}
      <TabPanel value={activeTab} index={user.role === 'manager' || user.role === 'hr' || user.role === 'admin' ? 5 : 2}>
        <Grid container spacing={3}>
          {policies.map((policy) => {
            const leaveConfig = LEAVE_TYPES[policy.leave_type] || {};
            
            return (
              <Grid item xs={12} md={6} key={policy.leave_type}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      {React.createElement(leaveConfig.icon || WorkIcon, {
                        sx: { mr: 2, color: leaveConfig.color }
                      })}
                      <Typography variant="h6">{leaveConfig.label}</Typography>
                    </Box>
                    
                    <Grid container spacing={2}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">Annual Entitlement</Typography>
                        <Typography variant="h6">{policy.annual_entitlement} days</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">Max Consecutive</Typography>
                        <Typography variant="h6">{policy.max_consecutive_days} days</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">Carry Forward</Typography>
                        <Typography variant="h6">{policy.carry_forward_limit} days</Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">Min Notice</Typography>
                        <Typography variant="h6">{policy.min_notice_days} days</Typography>
                      </Grid>
                    </Grid>

                    {policy.requires_medical_certificate && (
                      <Chip label="Medical Certificate Required" color="warning" sx={{ mt: 2 }} />
                    )}
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      </TabPanel>

      {/* Apply Leave Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Apply for Leave</DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Leave Type</InputLabel>
                <Select
                  value={newLeaveForm.leave_type}
                  label="Leave Type"
                  onChange={(e) => setNewLeaveForm({ ...newLeaveForm, leave_type: e.target.value })}
                >
                  {Object.entries(LEAVE_TYPES).map(([key, config]) => (
                    <MenuItem key={key} value={key}>
                      {config.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={newLeaveForm.is_half_day}
                    onChange={(e) => setNewLeaveForm({ ...newLeaveForm, is_half_day: e.target.checked })}
                  />
                }
                label="Half Day"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Start Date"
                type="date"
                value={newLeaveForm.start_date}
                onChange={(e) => setNewLeaveForm({ ...newLeaveForm, start_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="End Date"
                type="date"
                value={newLeaveForm.end_date}
                onChange={(e) => setNewLeaveForm({ ...newLeaveForm, end_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
                disabled={newLeaveForm.is_half_day}
              />
            </Grid>

            {newLeaveForm.is_half_day && (
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Half Day Period</InputLabel>
                  <Select
                    value={newLeaveForm.half_day_period}
                    label="Half Day Period"
                    onChange={(e) => setNewLeaveForm({ ...newLeaveForm, half_day_period: e.target.value })}
                  >
                    <MenuItem value="morning">Morning</MenuItem>
                    <MenuItem value="afternoon">Afternoon</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            )}

            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Reason"
                multiline
                rows={3}
                value={newLeaveForm.reason}
                onChange={(e) => setNewLeaveForm({ ...newLeaveForm, reason: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmitLeave} variant="contained">Submit Application</Button>
        </DialogActions>
      </Dialog>

      {/* Application Details Dialog */}
      <Dialog open={!!selectedApplication} onClose={() => setSelectedApplication(null)} maxWidth="md" fullWidth>
        <DialogTitle>Leave Application Details</DialogTitle>
        <DialogContent>
          {selectedApplication && (
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2">Leave Type</Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  {LEAVE_TYPES[selectedApplication.leave_type] && (
                    <React.Fragment>
                      {React.createElement(LEAVE_TYPES[selectedApplication.leave_type].icon, {
                        sx: { mr: 1, color: LEAVE_TYPES[selectedApplication.leave_type].color }
                      })}
                      {LEAVE_TYPES[selectedApplication.leave_type].label}
                    </React.Fragment>
                  )}
                </Box>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2">Status</Typography>
                <Chip
                  icon={STATUS_CONFIG[selectedApplication.status]?.icon ? 
                    React.createElement(STATUS_CONFIG[selectedApplication.status].icon, { sx: { fontSize: 16 } }) : null}
                  label={STATUS_CONFIG[selectedApplication.status]?.label || selectedApplication.status}
                  sx={{ 
                    mt: 1,
                    bgcolor: `${STATUS_CONFIG[selectedApplication.status]?.color}20`,
                    color: STATUS_CONFIG[selectedApplication.status]?.color
                  }}
                />
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2">Start Date</Typography>
                <Typography>{selectedApplication.start_date}</Typography>
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2">End Date</Typography>
                <Typography>{selectedApplication.end_date}</Typography>
              </Grid>

              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2">Total Days</Typography>
                <Typography>{selectedApplication.total_days}</Typography>
              </Grid>

              <Grid item xs={12}>
                <Typography variant="subtitle2">Reason</Typography>
                <Typography>{selectedApplication.reason}</Typography>
              </Grid>

              {selectedApplication.comments && (
                <Grid item xs={12}>
                  <Typography variant="subtitle2">Comments</Typography>
                  <Typography>{selectedApplication.comments}</Typography>
                </Grid>
              )}
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedApplication(null)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default LeavePage;
