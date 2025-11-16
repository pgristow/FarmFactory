import { Card as MuiCard, CardContent, Typography, Box } from '@mui/material';
import { ReactNode } from 'react';

interface CardProps {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  action?: ReactNode;
  sx?: object;
}

function Card({ title, subtitle, children, action, sx }: CardProps) {
  return (
    <MuiCard sx={{ ...sx }}>
      <CardContent>
        {(title || action) && (
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              mb: subtitle ? 1 : 2,
            }}
          >
            {title && (
              <Typography variant="h6" component="div">
                {title}
              </Typography>
            )}
            {action && <Box>{action}</Box>}
          </Box>
        )}
        {subtitle && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            {subtitle}
          </Typography>
        )}
        {children}
      </CardContent>
    </MuiCard>
  );
}

export default Card;
