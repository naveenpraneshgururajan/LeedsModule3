/**
 * TypeScript Type Definitions for Configuration Manager
 */

export interface Environment {
  name: string;
  filename: string;
  type: 'dev' | 'cit' | 'sit' | 'luat' | 'prod' | 'unknown';
  total_keys: number;
  config: Record<string, any>;
  flattened_config: Record<string, any>;
  coverage?: number;
  anomaly_score?: number;
  is_anomaly?: boolean;
  missing_keys?: string[];
  missing_count?: number;
  health?: 'healthy' | 'warning' | 'critical';
  similar_environments?: string[];
  last_modified?: LastModified;
  recent_history?: CommitHistory[];
  ml_insights?: MLInsights;
}

export interface MLInsights {
  environment: string;
  is_anomaly: boolean;
  anomaly_score: number;
  confidence: number;
  cluster: number;
  missing_keys: string[];
  missing_count: number;
  present_keys_count: number;
  expected_keys_count: number;
  coverage: number;
}

export interface LastModified {
  timestamp: string;
  date: string;
  author?: string;
  author_name?: string;
  message?: string;
  commit_hash?: string;
  source: 'git' | 'filesystem';
}

export interface CommitHistory {
  timestamp: string;
  date: string;
  author: string;
  author_name: string;
  message: string;
  commit_hash: string;
  full_hash: string;
}

export interface Change {
  timestamp: string;
  date: string;
  file: string;
  environment: string;
  author: string;
  author_name: string;
  message: string;
  commit_hash: string;
  stats: any;
}

export interface UpliftAnalysis {
  source: string;
  target: string;
  valid_direction: boolean;
  analyzed_at: string;
  critical: UpliftItem[];
  recommended: UpliftItem[];
  optional: UpliftItem[];
  summary: UpliftSummary;
  warning?: string;
  error?: string;
}

export interface UpliftItem {
  key: string;
  status: 'missing_in_target' | 'different_values';
  source_value: any;
  target_value: any;
  recently_changed: boolean;
  change_date: string | null;
  ml_confidence: number;
  is_critical: boolean;
}

export interface UpliftSummary {
  critical_count: number;
  recommended_count: number;
  optional_count: number;
  total_items: number;
  recent_changes_count: number;
  ml_insights?: any;
}

export interface ComparisonResult {
  source: string;
  target: string;
  added: string[];
  removed: string[];
  modified: ModifiedKey[];
  identical: string[];
  summary: {
    added_count: number;
    removed_count: number;
    modified_count: number;
    identical_count: number;
  };
}

export interface ModifiedKey {
  key: string;
  source_value: any;
  target_value: any;
}

export interface CoverageReport {
  coverage_matrix: CoverageMatrixRow[];
  statistics_by_type: StatisticsByType[];
  total_environments: number;
  total_unique_keys: number;
  generated_at: string;
}

export interface CoverageMatrixRow {
  environment: string;
  type: string;
  total_keys: number;
  coverage: Record<string, boolean>;
  overall_coverage: number;
}

export interface StatisticsByType {
  type: string;
  count: number;
  avg_coverage: number;
}

export interface Summary {
  total_environments: number;
  total_unique_keys: number;
  environments_by_type: Record<string, number>;
  average_coverage: number;
  ml_loaded: boolean;
  recent_changes_count: number;
  generated_at: string;
}

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  count?: number;
}
