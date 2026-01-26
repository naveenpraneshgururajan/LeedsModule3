import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Checkbox,
  FormControlLabel,
  LinearProgress,
} from '@mui/material';
import { ExpandMore } from '@mui/icons-material';
import { useAnalyzeUplift } from '../hooks/useUplift';
import { useEnvironments } from '../hooks/useEnvironments';
import type { UpliftAnalysis } from '../types';

export const Uplift: React.FC = () => {
  const [source, setSource] = useState('');
  const [target, setTarget] = useState('');
  const [analysis, setAnalysis] = useState<UpliftAnalysis | null>(null);
  const { data: envsData } = useEnvironments();
  const analyzeUplift = useAnalyzeUplift();

  const environments = envsData?.data || [];

  const handleAnalyze = async () => {
    const result = await analyzeUplift.mutateAsync({ source, target });
    if (result.success) {
      setAnalysis(result.data!);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Uplift Assistant
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Step 1: Select Environments
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Source</InputLabel>
              <Select value={source} onChange={(e) => setSource(e.target.value)} label="Source">
                {environments.map((env: any) => (
                  <MenuItem key={env.name} value={env.name}>
                    {env.name} ({env.type})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Typography>→</Typography>
            <FormControl sx={{ minWidth: 200 }}>
              <InputLabel>Target</InputLabel>
              <Select value={target} onChange={(e) => setTarget(e.target.value)} label="Target">
                {environments.map((env: any) => (
                  <MenuItem key={env.name} value={env.name}>
                    {env.name} ({env.type})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <Button variant="contained" onClick={handleAnalyze} disabled={!source || !target || analyzeUplift.isPending}>
              {analyzeUplift.isPending ? 'Analyzing...' : 'Analyze Changes'}
            </Button>
          </Box>
        </CardContent>
      </Card>

      {analyzeUplift.isPending && <LinearProgress />}

      {analysis && (
        <>
          <Card sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Step 2: Review Changes
              </Typography>
              <Alert severity="info" sx={{ mb: 2 }}>
                Found {analysis.summary.critical_count} critical, {analysis.summary.recommended_count} recommended,
                and {analysis.summary.optional_count} optional items.
              </Alert>
            </CardContent>
          </Card>

          {/* Critical Items */}
          {analysis.critical.length > 0 && (
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography sx={{ fontWeight: 'bold' }}>
                  🔴 CRITICAL ({analysis.critical.length} items)
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {analysis.critical.map((item, idx) => (
                  <Box key={idx} sx={{ mb: 2 }}>
                    <FormControlLabel control={<Checkbox defaultChecked />} label={item.key} />
                    <Typography variant="body2" color="textSecondary">
                      Status: {item.status} | Confidence: {(item.ml_confidence * 100).toFixed(0)}%
                    </Typography>
                  </Box>
                ))}
              </AccordionDetails>
            </Accordion>
          )}

          {/* Recommended Items */}
          {analysis.recommended.length > 0 && (
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography>🟡 RECOMMENDED ({analysis.recommended.length} items)</Typography>
              </AccordionSummary>
              <AccordionDetails>
                {analysis.recommended.map((item, idx) => (
                  <Box key={idx} sx={{ mb: 1 }}>
                    <FormControlLabel control={<Checkbox />} label={item.key} />
                  </Box>
                ))}
              </AccordionDetails>
            </Accordion>
          )}

          <Box sx={{ mt: 2 }}>
            <Button variant="contained" color="primary">
              Generate Checklist
            </Button>
            <Button variant="outlined" sx={{ ml: 2 }}>
              Export to JSON
            </Button>
          </Box>
        </>
      )}
    </Box>
  );
};

export default Uplift;
