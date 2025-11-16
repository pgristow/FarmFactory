import { Grid, Typography, Box } from '@mui/material';
import {
  Agriculture,
  Landscape,
  TrendingUp,
  WaterDrop,
} from '@mui/icons-material';
import Card from '../components/common/Card';

// Placeholder dashboard - will be enhanced with real data
function Dashboard() {
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
                  Importing irrigation and nutrient data (coming soon)
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
