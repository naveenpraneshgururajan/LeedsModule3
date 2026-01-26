import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Alert,
  Chip,
} from '@mui/material';
import { useSummary, useRecentChanges } from '../hooks/useReports';
import { useEnvironmentTypesSummary } from '../hooks/useEnvironments';
import { healthColors } from '../theme/theme';

export const Home: React.FC = () => {
  const { data: summaryData, isLoading: summaryLoading } = useSummary();
  const { data: typesData } = useEnvironmentTypesSummary();
  const { data: changesData } = useRecentChanges(7);

  if (summaryLoading) return <LinearProgress />;

  const summary = summaryData?.data;
  const types = typesData?.data || [];
  const changes = changesData?.data || [];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Environments
              </Typography>
              <Typography variant="h3">{summary?.total_environments || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Keys
              </Typography>
              <Typography variant="h3">{summary?.total_unique_keys || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Coverage
              </Typography>
              <Typography variant="h3">
                {((summary?.average_coverage || 0) * 100).toFixed(0)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Recent Changes
              </Typography>
              <Typography variant="h3">{summary?.recent_changes_count || 0}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Environment Health by Type */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Environment Health Overview
          </Typography>
          <Grid container spacing={2}>
            {types.map((type: any) => (
              <Grid item xs={12} sm={6} md={2.4} key={type.type}>
                <Box textAlign="center">
                  <Typography variant="subtitle2" sx={{ textTransform: 'uppercase' }}>
                    {type.type}
                  </Typography>
                  <Typography variant="h4">
                    {(type.avg_coverage * 100).toFixed(0)}%
                  </Typography>
                  <Chip
                    label={type.count + ' envs'}
                    size="small"
                    color={type.avg_coverage >= 0.9 ? 'success' : type.avg_coverage >= 0.75 ? 'warning' : 'error'}
                  />
                </Box>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Recent Alerts */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Activity (Last 7 Days)
          </Typography>
          {changes.slice(0, 5).map((change: any, idx: number) => (
            <Alert key={idx} severity="info" sx={{ mb: 1 }}>
              <strong>{change.environment}</strong>: {change.message.substring(0, 60)}...
              <br />
              <small>{change.date} by {change.author_name}</small>
            </Alert>
          ))}
        </CardContent>
      </Card>
    </Box>
  );
};

export default Home;
