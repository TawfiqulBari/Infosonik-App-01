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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Add,
  TrendingUp,
  Assignment,
  ExpandMore,
  Edit,
  Delete,
  Business,
  AttachMoney,
  Schedule,
} from '@mui/icons-material';
import axios from 'axios';
import { toast } from 'react-toastify';
import { useAuth } from '../contexts/AuthContext';
import { format } from 'date-fns';

export default function SalesPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState(0);
  const [meddpiccData, setMeddpiccData] = useState([]);
  const [salesFunnelData, setSalesFunnelData] = useState([]);
  const [openMeddpiccDialog, setOpenMeddpiccDialog] = useState(false);
  const [openFunnelDialog, setOpenFunnelDialog] = useState(false);
  const [loading, setLoading] = useState(true);
  
  const [meddpiccForm, setMeddpiccForm] = useState({
    client_name: '',
    opportunity_name: '',
    metrics: '',
    economic_buyer: '',
    decision_criteria: '',
    decision_process: '',
    paper_process: '',
    identify_pain: '',
    champion: '',
    competition: ''
  });

  const [funnelForm, setFunnelForm] = useState({
    opportunity_name: '',
    client_name: '',
    stage: 'Lead',
    probability: 10,
    amount: 0,
    closing_date: '',
    notes: ''
  });

  const stages = ['Lead', 'Qualified', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost'];
  const stageColors = {
    'Lead': 'info',
    'Qualified': 'primary',
    'Proposal': 'warning',
    'Negotiation': 'secondary',
    'Closed Won': 'success',
    'Closed Lost': 'error'
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [meddpiccRes, funnelRes] = await Promise.all([
        axios.get('/sales/meddpicc'),
        axios.get('/sales/funnel')
      ]);
      
      setMeddpiccData(meddpiccRes.data);
      setSalesFunnelData(funnelRes.data);
    } catch (error) {
      toast.error('Failed to load sales data');
      console.error('Sales data error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMeddpiccSubmit = async () => {
    try {
      await axios.post('/sales/meddpicc', meddpiccForm);
      toast.success('MEDDPICC analysis created successfully');
      setOpenMeddpiccDialog(false);
      setMeddpiccForm({
        client_name: '',
        opportunity_name: '',
        metrics: '',
        economic_buyer: '',
        decision_criteria: '',
        decision_process: '',
        paper_process: '',
        identify_pain: '',
        champion: '',
        competition: ''
      });
      fetchData();
    } catch (error) {
      toast.error('Failed to create MEDDPICC analysis');
      console.error('MEDDPICC error:', error);
    }
  };

  const handleFunnelSubmit = async () => {
    try {
      const submitData = {
        ...funnelForm,
        amount: funnelForm.amount * 100, // Convert to cents
        closing_date: new Date(funnelForm.closing_date).toISOString()
      };
      
      await axios.post('/sales/funnel', submitData);
      toast.success('Sales funnel entry created successfully');
      setOpenFunnelDialog(false);
      setFunnelForm({
        opportunity_name: '',
        client_name: '',
        stage: 'Lead',
        probability: 10,
        amount: 0,
        closing_date: '',
        notes: ''
      });
      fetchData();
    } catch (error) {
      toast.error('Failed to create sales funnel entry');
      console.error('Funnel error:', error);
    }
  };

  const StatCard = ({ icon, title, value, subtitle, color }) => (
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
              {value}
            </Typography>
            <Typography variant="h6" component="div">
              {title}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="textSecondary">
                {subtitle}
              </Typography>
            )}
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  const totalOpportunities = salesFunnelData.length;
  const totalValue = salesFunnelData.reduce((sum, item) => sum + (item.amount || 0), 0) / 100;
  const wonDeals = salesFunnelData.filter(item => item.stage === 'Closed Won').length;
  const avgProbability = salesFunnelData.length > 0 
    ? Math.round(salesFunnelData.reduce((sum, item) => sum + item.probability, 0) / salesFunnelData.length)
    : 0;

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
          Sales Management 📊
        </Typography>
        <Typography variant="h6" color="textSecondary" gutterBottom>
          MEDDPICC Analysis & Sales Funnel Tracking
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<Business />}
            title="Total Opportunities"
            value={totalOpportunities}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<AttachMoney />}
            title="Pipeline Value"
            value={`$${totalValue.toLocaleString()}`}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<TrendingUp />}
            title="Won Deals"
            value={wonDeals}
            subtitle={`${totalOpportunities > 0 ? Math.round((wonDeals / totalOpportunities) * 100) : 0}% Win Rate`}
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            icon={<Schedule />}
            title="Avg Probability"
            value={`${avgProbability}%`}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Tabs */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="MEDDPICC Analysis" icon={<Assignment />} />
          <Tab label="Sales Funnel" icon={<TrendingUp />} />
        </Tabs>
      </Box>

      {/* MEDDPICC Tab */}
      {activeTab === 0 && (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h5">MEDDPICC Analysis</Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setOpenMeddpiccDialog(true)}
            >
              New Analysis
            </Button>
          </Box>

          {meddpiccData.length === 0 ? (
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 6 }}>
                <Assignment sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  No MEDDPICC Analysis Yet
                </Typography>
                <Typography color="textSecondary" sx={{ mb: 3 }}>
                  Create your first MEDDPICC analysis to track sales opportunities
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => setOpenMeddpiccDialog(true)}
                >
                  Create Analysis
                </Button>
              </CardContent>
            </Card>
          ) : (
            <Box>
              {meddpiccData.map((analysis, index) => (
                <Accordion key={analysis.id} sx={{ mb: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box sx={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Box>
                        <Typography variant="h6">{analysis.opportunity_name}</Typography>
                        <Typography variant="body2" color="textSecondary">
                          {analysis.client_name} • {format(new Date(analysis.created_at), 'MMM dd, yyyy')}
                        </Typography>
                      </Box>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" gutterBottom><strong>Metrics:</strong></Typography>
                        <Typography variant="body2" sx={{ mb: 2 }}>{analysis.metrics}</Typography>
                        
                        <Typography variant="subtitle2" gutterBottom><strong>Economic Buyer:</strong></Typography>
                        <Typography variant="body2" sx={{ mb: 2 }}>{analysis.economic_buyer}</Typography>
                        
                        <Typography variant="subtitle2" gutterBottom><strong>Decision Criteria:</strong></Typography>
                        <Typography variant="body2" sx={{ mb: 2 }}>{analysis.decision_criteria}</Typography>
                        
                        <Typography variant="subtitle2" gutterBottom><strong>Decision Process:</strong></Typography>
                        <Typography variant="body2" sx={{ mb: 2 }}>{analysis.decision_process}</Typography>
                        
                        <Typography variant="subtitle2" gutterBottom><strong>Paper Process:</strong></Typography>
                        <Typography variant="body2">{analysis.paper_process}</Typography>
                      </Grid>
                      <Grid item xs={12} md={6}>
                        <Typography variant="subtitle2" gutterBottom><strong>Identify Pain:</strong></Typography>
                        <Typography variant="body2" sx={{ mb: 2 }}>{analysis.identify_pain}</Typography>
                        
                        <Typography variant="subtitle2" gutterBottom><strong>Champion:</strong></Typography>
                        <Typography variant="body2" sx={{ mb: 2 }}>{analysis.champion}</Typography>
                        
                        <Typography variant="subtitle2" gutterBottom><strong>Competition:</strong></Typography>
                        <Typography variant="body2">{analysis.competition}</Typography>
                      </Grid>
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              ))}
            </Box>
          )}
        </Box>
      )}

      {/* Sales Funnel Tab */}
      {activeTab === 1 && (
        <Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h5">Sales Funnel</Typography>
            <Button
              variant="contained"
              startIcon={<Add />}
              onClick={() => setOpenFunnelDialog(true)}
            >
              New Opportunity
            </Button>
          </Box>

          {salesFunnelData.length === 0 ? (
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 6 }}>
                <TrendingUp sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  No Sales Opportunities Yet
                </Typography>
                <Typography color="textSecondary" sx={{ mb: 3 }}>
                  Add your first sales opportunity to start tracking your pipeline
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => setOpenFunnelDialog(true)}
                >
                  Add Opportunity
                </Button>
              </CardContent>
            </Card>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Opportunity</TableCell>
                    <TableCell>Client</TableCell>
                    <TableCell>Stage</TableCell>
                    <TableCell>Probability</TableCell>
                    <TableCell>Amount</TableCell>
                    <TableCell>Closing Date</TableCell>
                    <TableCell>Created</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {salesFunnelData.map((opportunity) => (
                    <TableRow key={opportunity.id}>
                      <TableCell>{opportunity.opportunity_name}</TableCell>
                      <TableCell>{opportunity.client_name}</TableCell>
                      <TableCell>
                        <Chip
                          label={opportunity.stage}
                          color={stageColors[opportunity.stage] || 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{opportunity.probability}%</TableCell>
                      <TableCell>${(opportunity.amount / 100).toLocaleString()}</TableCell>
                      <TableCell>
                        {format(new Date(opportunity.closing_date), 'MMM dd, yyyy')}
                      </TableCell>
                      <TableCell>
                        {format(new Date(opportunity.created_at), 'MMM dd, yyyy')}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </Box>
      )}

      {/* MEDDPICC Dialog */}
      <Dialog open={openMeddpiccDialog} onClose={() => setOpenMeddpiccDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>New MEDDPICC Analysis</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Client Name"
                value={meddpiccForm.client_name}
                onChange={(e) => setMeddpiccForm({ ...meddpiccForm, client_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Opportunity Name"
                value={meddpiccForm.opportunity_name}
                onChange={(e) => setMeddpiccForm({ ...meddpiccForm, opportunity_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Metrics"
                value={meddpiccForm.metrics}
                onChange={(e) => setMeddpiccForm({ ...meddpiccForm, metrics: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Economic Buyer"
                value={meddpiccForm.economic_buyer}
                onChange={(e) => setMeddpiccForm({ ...meddpiccForm, economic_buyer: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Decision Criteria"
                value={meddpiccForm.decision_criteria}
                onChange={(e) => setMeddpiccForm({ ...meddpiccForm, decision_criteria: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Decision Process"
                value={meddpiccForm.decision_process}
                onChange={(e) => setMeddpiccForm({ ...meddpiccForm, decision_process: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Paper Process"
                value={meddpiccForm.paper_process}
                onChange={(e) => setMeddpiccForm({ ...meddpiccForm, paper_process: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Identify Pain"
                value={meddpiccForm.identify_pain}
                onChange={(e) => setMeddpiccForm({ ...meddpiccForm, identify_pain: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Champion"
                value={meddpiccForm.champion}
                onChange={(e) => setMeddpiccForm({ ...meddpiccForm, champion: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Competition"
                value={meddpiccForm.competition}
                onChange={(e) => setMeddpiccForm({ ...meddpiccForm, competition: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenMeddpiccDialog(false)}>Cancel</Button>
          <Button onClick={handleMeddpiccSubmit} variant="contained">Create Analysis</Button>
        </DialogActions>
      </Dialog>

      {/* Sales Funnel Dialog */}
      <Dialog open={openFunnelDialog} onClose={() => setOpenFunnelDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Sales Opportunity</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Opportunity Name"
                value={funnelForm.opportunity_name}
                onChange={(e) => setFunnelForm({ ...funnelForm, opportunity_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Client Name"
                value={funnelForm.client_name}
                onChange={(e) => setFunnelForm({ ...funnelForm, client_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Stage</InputLabel>
                <Select
                  value={funnelForm.stage}
                  label="Stage"
                  onChange={(e) => setFunnelForm({ ...funnelForm, stage: e.target.value })}
                >
                  {stages.map((stage) => (
                    <MenuItem key={stage} value={stage}>
                      {stage}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Probability (%)"
                value={funnelForm.probability}
                onChange={(e) => setFunnelForm({ ...funnelForm, probability: parseInt(e.target.value) || 0 })}
                inputProps={{ min: 0, max: 100 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="number"
                label="Amount ($)"
                value={funnelForm.amount}
                onChange={(e) => setFunnelForm({ ...funnelForm, amount: parseFloat(e.target.value) || 0 })}
                inputProps={{ min: 0, step: 0.01 }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="date"
                label="Closing Date"
                InputLabelProps={{ shrink: true }}
                value={funnelForm.closing_date}
                onChange={(e) => setFunnelForm({ ...funnelForm, closing_date: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Notes"
                value={funnelForm.notes}
                onChange={(e) => setFunnelForm({ ...funnelForm, notes: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenFunnelDialog(false)}>Cancel</Button>
          <Button onClick={handleFunnelSubmit} variant="contained">Create Opportunity</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
