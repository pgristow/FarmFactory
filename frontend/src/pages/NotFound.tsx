import { useNavigate } from 'react-router-dom';
import { Box, Typography, Button, Container } from '@mui/material';
import { Home as HomeIcon } from '@mui/icons-material';

function NotFound() {
  const navigate = useNavigate();

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          textAlign: 'center',
          gap: 3,
        }}
      >
        <Typography
          variant="h1"
          component="div"
          sx={{ fontSize: '8rem', fontWeight: 700, color: 'primary.main' }}
        >
          404
        </Typography>
        <Typography variant="h4" component="h1" gutterBottom>
          Page Not Found
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
          The page you are looking for doesn't exist or has been moved.
        </Typography>
        <Button
          variant="contained"
          startIcon={<HomeIcon />}
          onClick={() => navigate('/')}
          size="large"
        >
          Go to Dashboard
        </Button>
      </Box>
    </Container>
  );
}

export default NotFound;
