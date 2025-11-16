import { useLocation, useNavigate } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  Divider,
  Box,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Agriculture as FarmIcon,
  Landscape as PlotIcon,
  WaterDrop as IrrigationIcon,
  Science as NutrientIcon,
  AttachMoney as FinancialIcon,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';

interface SidebarProps {
  width: number;
}

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Farms', icon: <FarmIcon />, path: '/farms' },
  { text: 'Plots', icon: <PlotIcon />, path: '/plots' },
  { text: 'Irrigation', icon: <IrrigationIcon />, path: '/irrigation', disabled: true },
  { text: 'Nutrients', icon: <NutrientIcon />, path: '/nutrients', disabled: true },
  { text: 'Financial', icon: <FinancialIcon />, path: '/financial', disabled: true },
  { text: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics', disabled: true },
];

function Sidebar({ width }: SidebarProps) {
  const location = useLocation();
  const navigate = useNavigate();

  const handleNavigation = (path: string, disabled?: boolean) => {
    if (!disabled) {
      navigate(path);
    }
  };

  return (
    <Drawer
      variant="permanent"
      sx={{
        width,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width,
          boxSizing: 'border-box',
          backgroundColor: 'primary.dark',
          color: 'white',
        },
      }}
    >
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FarmIcon sx={{ fontSize: 32 }} />
          <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 700 }}>
            FarmFactory
          </Typography>
        </Box>
      </Toolbar>
      <Divider sx={{ borderColor: 'rgba(255, 255, 255, 0.12)' }} />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleNavigation(item.path, item.disabled)}
              disabled={item.disabled}
              sx={{
                '&.Mui-selected': {
                  backgroundColor: 'rgba(255, 255, 255, 0.16)',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.24)',
                  },
                },
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.08)',
                },
              }}
            >
              <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
}

export default Sidebar;
