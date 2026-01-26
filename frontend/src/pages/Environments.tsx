import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Button,
  LinearProgress,
} from '@mui/material';
import { useEnvironments } from '../hooks/useEnvironments';
import { useNavigate } from 'react-router-dom';
import type { Environment } from '../types';

export const Environments: React.FC = () => {
  const { data, isLoading } = useEnvironments();
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');

  if (isLoading) return <LinearProgress />;

  const environments = data?.data || [];

  const filtered = environments.filter((env: Environment) => {
    const matchesSearch = env.name.toLowerCase().includes(search.toLowerCase());
    const matchesType = typeFilter === 'all' || env.type === typeFilter;
    return matchesSearch && matchesType;
  });

  const getHealthColor = (health?: string) => {
    if (health === 'healthy') return 'success';
    if (health === 'warning') return 'warning';
    return 'error';
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        All Environments
      </Typography>

      {/* Filters */}
      <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
        <TextField
          label="Search"
          variant="outlined"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          sx={{ flexGrow: 1 }}
        />
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Type</InputLabel>
          <Select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)} label="Type">
            <MenuItem value="all">All</MenuItem>
            <MenuItem value="dev">DEV</MenuItem>
            <MenuItem value="cit">CIT</MenuItem>
            <MenuItem value="sit">SIT</MenuItem>
            <MenuItem value="luat">LUAT</MenuItem>
            <MenuItem value="prod">PROD</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Environment Cards */}
      <Grid container spacing={2}>
        {filtered.map((env: Environment) => (
          <Grid item xs={12} key={env.name}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box>
                    <Typography variant="h6">
                      {env.name}
                      <Chip
                        label={env.type.toUpperCase()}
                        size="small"
                        sx={{ ml: 2 }}
                      />
                      <Chip
                        label={env.health || 'unknown'}
                        size="small"
                        color={getHealthColor(env.health)}
                        sx={{ ml: 1 }}
                      />
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                      Total Keys: {env.total_keys} | Coverage: {((env.coverage || 0) * 100).toFixed(0)}%
                      {env.missing_count ? ` | Missing: ${env.missing_count}` : ''}
                    </Typography>
                  </Box>
                  <Button variant="outlined" size="small">
                    View Details
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {filtered.length === 0 && (
        <Typography variant="body1" color="textSecondary" sx={{ mt: 3 }}>
          No environments found matching your filters.
        </Typography>
      )}
    </Box>
  );
};

export default Environments;
