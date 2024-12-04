// src/components/DetailPanel.jsx
import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';

const DetailPanel = ({ point }) => {
  if (!point) return (
    <div className="detail-panel">
      <Typography variant="body2" color="text.secondary">
        Select a point to view details
      </Typography>
    </div>
  );

  return (
    <div className="detail-panel">
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Comment Details
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Site: {point.site}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Opinion: {point.opinion}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Date: {point.date}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Organization: {point.organization || 'N/A'}
          </Typography>
          <Typography variant="body1" sx={{ mt: 2 }}>
            {point.comment}
          </Typography>
        </CardContent>
      </Card>
    </div>
  );
};

export default DetailPanel;