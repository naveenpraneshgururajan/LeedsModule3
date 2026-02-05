import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import type { Environment, CategorizedConfigs } from '../types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`config-tabpanel-${index}`}
      aria-labelledby={`config-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

interface ConfigSectionProps {
  title: string;
  configs: Record<string, any>;
  isEmpty: boolean;
}

const ConfigSection: React.FC<ConfigSectionProps> = ({ title, configs, isEmpty }) => {
  if (isEmpty) {
    return (
      <Typography variant="body2" color="textSecondary" sx={{ fontStyle: 'italic', p: 2 }}>
        No {title.toLowerCase()} configurations found
      </Typography>
    );
  }

  const renderValue = (value: any): string => {
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  };

  return (
    <Box>
      {Object.entries(configs).map(([filename, fileConfig]) => (
        <Accordion key={filename} defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" sx={{ fontWeight: 500 }}>
              {filename}
              <Chip
                label={Object.keys(fileConfig).length + ' keys'}
                size="small"
                sx={{ ml: 2 }}
              />
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 'bold' }}>Key</TableCell>
                    <TableCell sx={{ fontWeight: 'bold' }}>Value</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(fileConfig).map(([key, value]) => (
                    <TableRow key={key} hover>
                      <TableCell sx={{ fontFamily: 'monospace', width: '40%' }}>
                        {key}
                      </TableCell>
                      <TableCell sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                        {renderValue(value)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
};

interface EnvironmentDetailsProps {
  environment: Environment;
}

export const EnvironmentDetails: React.FC<EnvironmentDetailsProps> = ({ environment }) => {
  const [selectedTab, setSelectedTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const categorizedConfigs = environment.categorized_configs;

  if (!categorizedConfigs) {
    // Fallback to showing all configs in one view
    return (
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            All Configurations
          </Typography>
          <TableContainer component={Paper}>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 'bold' }}>Key</TableCell>
                  <TableCell sx={{ fontWeight: 'bold' }}>Value</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(environment.flattened_config).map(([key, value]) => (
                  <TableRow key={key} hover>
                    <TableCell sx={{ fontFamily: 'monospace' }}>{key}</TableCell>
                    <TableCell sx={{ fontFamily: 'monospace' }}>
                      {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    );
  }

  // Count items in each category
  const categoryCounts = {
    switches: Object.keys(categorizedConfigs.switches).length,
    configmap: Object.keys(categorizedConfigs.configmap).length,
    cwa: Object.keys(categorizedConfigs.cwa).length,
    node: Object.keys(categorizedConfigs.node).length,
    dsapps: Object.keys(categorizedConfigs.dsapps).length,
    other: Object.keys(categorizedConfigs.other).length,
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>
          {environment.name}
          <Chip
            label={environment.type.toUpperCase()}
            size="small"
            color="primary"
            sx={{ ml: 2 }}
          />
        </Typography>

        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={selectedTab} onChange={handleTabChange} variant="scrollable">
            <Tab
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  Switches
                  {categoryCounts.switches > 0 && (
                    <Chip label={categoryCounts.switches} size="small" />
                  )}
                </Box>
              }
            />
            <Tab
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  Config Map
                  {categoryCounts.configmap > 0 && (
                    <Chip label={categoryCounts.configmap} size="small" />
                  )}
                </Box>
              }
            />
            <Tab
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  CWA Files
                  {categoryCounts.cwa > 0 && (
                    <Chip label={categoryCounts.cwa} size="small" />
                  )}
                </Box>
              }
            />
            <Tab
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  Node YAML
                  {categoryCounts.node > 0 && (
                    <Chip label={categoryCounts.node} size="small" />
                  )}
                </Box>
              }
            />
            <Tab
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  DS Apps
                  {categoryCounts.dsapps > 0 && (
                    <Chip label={categoryCounts.dsapps} size="small" />
                  )}
                </Box>
              }
            />
            {categoryCounts.other > 0 && (
              <Tab
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    Other
                    <Chip label={categoryCounts.other} size="small" />
                  </Box>
                }
              />
            )}
          </Tabs>
        </Box>

        <TabPanel value={selectedTab} index={0}>
          <ConfigSection
            title="Switches"
            configs={categorizedConfigs.switches}
            isEmpty={categoryCounts.switches === 0}
          />
        </TabPanel>

        <TabPanel value={selectedTab} index={1}>
          <ConfigSection
            title="Config Map"
            configs={categorizedConfigs.configmap}
            isEmpty={categoryCounts.configmap === 0}
          />
        </TabPanel>

        <TabPanel value={selectedTab} index={2}>
          <ConfigSection
            title="CWA Files"
            configs={categorizedConfigs.cwa}
            isEmpty={categoryCounts.cwa === 0}
          />
        </TabPanel>

        <TabPanel value={selectedTab} index={3}>
          <ConfigSection
            title="Node YAML"
            configs={categorizedConfigs.node}
            isEmpty={categoryCounts.node === 0}
          />
        </TabPanel>

        <TabPanel value={selectedTab} index={4}>
          <ConfigSection
            title="DS Apps"
            configs={categorizedConfigs.dsapps}
            isEmpty={categoryCounts.dsapps === 0}
          />
        </TabPanel>

        {categoryCounts.other > 0 && (
          <TabPanel value={selectedTab} index={5}>
            <ConfigSection
              title="Other"
              configs={categorizedConfigs.other}
              isEmpty={categoryCounts.other === 0}
            />
          </TabPanel>
        )}
      </CardContent>
    </Card>
  );
};

export default EnvironmentDetails;
