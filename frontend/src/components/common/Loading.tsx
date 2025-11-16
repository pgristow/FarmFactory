import { Box, CircularProgress, Typography } from '@mui/material';

interface LoadingProps {
  message?: string;
  fullScreen?: boolean;
}

function Loading({ message = 'Loading...', fullScreen = false }: LoadingProps) {
  const content = (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 2,
        p: 4,
      }}
    >
      <CircularProgress size={40} />
      <Typography variant="body2" color="text.secondary">
        {message}
      </Typography>
    </Box>
  );

  if (fullScreen) {
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          width: '100%',
        }}
      >
        {content}
      </Box>
    );
  }

  return content;
}

export default Loading;
