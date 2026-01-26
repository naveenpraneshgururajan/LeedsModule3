import React from 'react';
import { Box, Typography, Card, CardContent, Grid, Button, LinearProgress } from '@mui/material';
import { useCoverageReport, useAnomaliesReport, useMLStatus } from '../hooks/useReports';

export const Reports: React.FC = () => {
  const { data: coverageData, isLoading: coverageLoading } = useCoverageReport();
  const { data: anomaliesData } = useAnomaliesReport();
  const { data: mlStatusData } = useMLStatus();

  if (coverageLoading) return <LinearProgress />;

  const mlStatus = mlStatusData?.data;
  const anomalies = anomaliesData?.data;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Reports & Analytics
      </Typography>

      {/* ML Model Status */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🤖 ML Model Status
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Typography color="textSecondary">Status</Typography>
              <Typography variant="h6">{mlStatus?.loaded ? '✅ Loaded' : '❌ Not Loaded'}</Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography color="textSecondary">Features</Typography>
              <Typography variant="h6">{mlStatus?.num_features || 0}</Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Typography color="textSecondary">Trained Date</Typography>
              <Typography variant="body2">
                {mlStatus?.model_info?.trained_date
                  ? new Date(mlStatus.model_info.trained_date).toLocaleDateString()
                  : 'N/A'}
              </Typography>
            </Grid>
            <Grid item xs={12} md={3}>
              <Button variant="outlined" fullWidth>
                Retrain Models
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Anomalies */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🔍 Detected Anomalies
          </Typography>
          <Typography variant="body2" color="textSecondary" gutterBottom>
            Total Anomalies: {anomalies?.total_anomalies || 0} / {anomalies?.total_environments || 0} environments
          </Typography>
          {anomalies?.anomalies?.slice(0, 5).map((anom: any, idx: number) => (
            <Box key={idx} sx={{ p: 1, borderBottom: '1px solid #eee' }}>
              <Typography variant="body1">
                {anom.environment} - Score: {anom.anomaly_score.toFixed(2)}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Missing {anom.missing_count} keys | Coverage: {(anom.coverage * 100).toFixed(0)}%
              </Typography>
            </Box>
          ))}
        </CardContent>
      </Card>

      <Box sx={{ display: 'flex', gap: 2 }}>
        <Button variant="contained">Generate Coverage Report</Button>
        <Button variant="outlined">Export to HTML</Button>
        <Button variant="outlined">Export to JSON</Button>
      </Box>
    </Box>
  );
};

export default Reports;
