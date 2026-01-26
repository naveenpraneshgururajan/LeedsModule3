import React from 'react';
import { Box, Typography, Card, CardContent, TextField, Button, Divider } from '@mui/material';

export const Settings: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            📁 File Paths
          </Typography>
          <TextField
            label="YAML Files Path"
            fullWidth
            margin="normal"
            defaultValue="/path/to/your/configs"
            helperText="Path to your environment configuration files"
          />
          <TextField
            label="Git Repository Path"
            fullWidth
            margin="normal"
            defaultValue="/path/to/your/configs"
            helperText="Path to git repository for change tracking"
          />
          <Box sx={{ mt: 2 }}>
            <Button variant="contained">Save Changes</Button>
          </Box>
        </CardContent>
      </Card>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            🤖 ML Model Settings
          </Typography>
          <TextField
            label="Anomaly Detection Threshold"
            type="number"
            fullWidth
            margin="normal"
            defaultValue="0.7"
            helperText="Threshold for anomaly detection (0-1)"
          />
          <TextField
            label="Development Environment Leniency"
            type="number"
            fullWidth
            margin="normal"
            defaultValue="0.5"
            helperText="Higher = More tolerant of missing keys in dev (0-1)"
          />
          <Box sx={{ mt: 2 }}>
            <Button variant="contained">Save Settings</Button>
          </Box>
        </CardContent>
      </Card>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            ℹ️ System Information
          </Typography>
          <Typography variant="body2">
            <strong>Version:</strong> 1.0.0
          </Typography>
          <Typography variant="body2">
            <strong>API Status:</strong> ✅ Connected
          </Typography>
          <Typography variant="body2">
            <strong>Model Status:</strong> ✅ Loaded
          </Typography>
        </CardContent>
      </Card>
    </Box>
  );
};

export default Settings;
