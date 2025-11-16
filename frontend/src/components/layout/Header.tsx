import { AppBar, Toolbar, Typography, Box, IconButton, Avatar } from '@mui/material';
import { Notifications as NotificationsIcon } from '@mui/icons-material';
import { format } from 'date-fns';

function Header() {
  const currentDate = format(new Date(), 'EEEE, MMMM d, yyyy');

  return (
    <AppBar
      position="static"
      color="transparent"
      elevation={0}
      sx={{
        backgroundColor: 'white',
        borderBottom: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Toolbar>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="body2" color="text.secondary">
            {currentDate}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton color="inherit">
            <NotificationsIcon />
          </IconButton>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
              U
            </Avatar>
            <Typography variant="body2" sx={{ fontWeight: 500 }}>
              Admin User
            </Typography>
          </Box>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Header;
