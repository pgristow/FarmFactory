import { Grid, Typography, Box, Button, Paper } from '@mui/material';
import {
  Agriculture,
  Landscape,
  TrendingUp,
  WaterDrop,
  Upload as ImportIcon,
  History as HistoryIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import Card from '../components/common/Card';

// Placeholder dashboard - will be enhanced with real data
function Dashboard() {
  const navigate = useNavigate();

  const stats = [
    {
      title: 'Total Farms',
      value: '0',
      icon: <Agriculture sx={{ fontSize: 40, color: 'primary.main' }} />,
      subtitle: 'Active farms in system',
    },
    {
      title: 'Total Plots',
      value: '0',
      icon: <Landscape sx={{ fontSize: 40, color: 'secondary.main' }} />,
      subtitle: 'Plots under management',
    },
    {
      title: 'Yield Trend',
      value: 'N/A',
      icon: <TrendingUp sx={{ fontSize: 40, color: 'success.main' }} />,
      subtitle: 'Season performance',
    },
    {
      title: 'Water Usage',
      value: 'N/A',
      icon: <WaterDrop sx={{ fontSize: 40, color: 'info.main' }} />,
      subtitle: 'Total irrigation',
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
        Dashboard Overview
      </Typography>

      <Grid container spacing={3}>
        {stats.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 2,
                }}
              >
                <Box>{stat.icon}</Box>
                <Box sx={{ flexGrow: 1 }}>
                  <Typography variant="h4" component="div" sx={{ fontWeight: 600 }}>
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stat.title}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {stat.subtitle}
                  </Typography>
                </Box>
              </Box>
            </Card>
          </Grid>
        ))}

        <Grid item xs={12} md={6}>
          <Paper
            elevation={3}
            sx={{
              p: 3,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              cursor: 'pointer',
              transition: 'transform 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
              },
            }}
            onClick={() => navigate('/import')}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <ImportIcon sx={{ fontSize: 48, mr: 2 }} />
              <Typography variant="h5" fontWeight="bold">
                Import Data
              </Typography>
            </Box>
            <Typography variant="body1" sx={{ mb: 2 }}>
              Bulk import your farm data from CSV or Excel files
            </Typography>
            <Button
              variant="contained"
              sx={{
                backgroundColor: 'white',
                color: 'primary.main',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.9)',
                },
              }}
              startIcon={<ImportIcon />}
            >
              Start Import
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper
            elevation={3}
            sx={{
              p: 3,
              background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
              color: 'white',
              cursor: 'pointer',
              transition: 'transform 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
              },
            }}
            onClick={() => navigate('/import-history')}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <HistoryIcon sx={{ fontSize: 48, mr: 2 }} />
              <Typography variant="h5" fontWeight="bold">
                Import History
              </Typography>
            </Box>
            <Typography variant="body1" sx={{ mb: 2 }}>
              View and manage all your data import jobs
            </Typography>
            <Button
              variant="contained"
              sx={{
                backgroundColor: 'white',
                color: 'primary.main',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.9)',
                },
              }}
              startIcon={<HistoryIcon />}
            >
              View History
            </Button>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Card title="Welcome to FarmFactory">
            <Typography variant="body1" paragraph>
              FarmFactory is your comprehensive farm optimization system designed to maximize
              yields through data-driven decision making.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Get started by:
            </Typography>
            <Box component="ul" sx={{ mt: 1 }}>
              <li>
                <Typography variant="body2">Creating your first farm</Typography>
              </li>
              <li>
                <Typography variant="body2">Adding plots to your farm</Typography>
              </li>
              <li>
                <Typography variant="body2">
                  Importing irrigation and nutrient data using our Import tool
                </Typography>
              </li>
              <li>
                <Typography variant="body2">
                  Monitoring your farm's performance metrics (coming soon)
                </Typography>
              </li>
            </Box>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card title="Recent Activity" subtitle="No recent activity">
            <Typography variant="body2" color="text.secondary">
              Activity will appear here once you start managing your farms and plots.
            </Typography>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card title="Alerts" subtitle="No active alerts">
            <Typography variant="body2" color="text.secondary">
              System alerts and notifications will appear here.
            </Typography>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard;
