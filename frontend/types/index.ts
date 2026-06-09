export interface RepositoryInfo {
  name: string;
  owner: string;
  full_name: string;
  description: string | null;
  html_url: string;
  stars: number;
  forks: number;
  watchers: number;
  open_issues: number;
  language: string | null;
  created_at: string;
  updated_at: string;
  default_branch: string;
  license: string | null;
  topics: string[];
}

export interface LanguageDistribution {
  languages: Record<string, number>;
}

export interface RepositoryMetrics {
  recent_commits_30d: number;
  recent_commits_90d: number;
  contributors_count: number;
  open_issues_count: number;
  closed_issues_30d: number;
  open_prs_count: number;
  merged_prs_30d: number;
  releases_count: number;
  latest_release_date: string | null;
  issue_response_time_avg: number | null;
  issue_response_time_median: number | null;
  pr_merge_time_avg: number | null;
  pr_merge_time_median: number | null;
}

export interface HealthScoreDimensions {
  popularity: number;
  activity: number;
  community: number;
  issue_governance: number;
  pr_governance: number;
  engineering: number;
  release_maintenance: number;
}

export type ProjectType =
  | "personal"
  | "community"
  | "corporate"
  | "opencore"
  | "source_available"
  | "ai_platform"
  | "infrastructure"
  | "sdk_library"
  | "developer_tool";

export interface ProjectTypeInfo {
  primary_type: ProjectType;
  confidence: number;
  secondary_types: ProjectType[];
  features: Record<string, unknown>;
  signals: Array<Record<string, unknown>>;
  metadata: Record<string, unknown>;
}

export interface AICapabilityScore {
  capability: string;
  detected: boolean;
  confidence: number;
  signals: string[];
  maturity_score: number;
}

export interface AIMaturity {
  total_score: number;
  capabilities: AICapabilityScore[];
  model_support: string[];
  deployment_methods: string[];
}

export interface HealthScore {
  score: number;
  dimensions: HealthScoreDimensions;
  type_detection: ProjectTypeInfo | null;
  ai_maturity: AIMaturity | null;
}

export interface AIScore {
  score: number;
  grade: string;
  summary: string;
  ai_used: boolean;
}

export interface ConclusionItem {
  text: string;
  source: string;
  confidence: "high" | "medium" | "low";
  causation: "causation" | "correlation" | "unknown";
}

export interface AIAnalysis {
  summary: string;
  strengths: ConclusionItem[];
  risks: ConclusionItem[];
  suggestions: ConclusionItem[];
  ai_used: boolean;
}

export interface AnalyzeResponse {
  repository: RepositoryInfo;
  languages: LanguageDistribution;
  metrics: RepositoryMetrics;
  health_score: HealthScore;
  ai_score: AIScore;
  ai_analysis: AIAnalysis | null;
}

export interface AnalyzeRequest {
  url: string;
}

export interface SettingsStatus {
  deepseek_configured: boolean;
  github_configured: boolean;
}

export interface UpdateSettingsRequest {
  deepseek_api_key: string | null;
  github_token: string | null;
}

export type AnalysisStatus = "idle" | "loading" | "success" | "error";

export interface ApiError {
  detail: string;
}

// Analysis Record types for History
export interface AnalysisRecordSummary {
  id: string;
  repository_url: string;
  repository_name: string;
  owner: string;
  full_name: string;
  score: number | null;
  grade: string | null;
  type_detection: Record<string, unknown> | null;
  status: "processing" | "completed" | "failed";
  error_message: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface AnalysisRecord extends AnalysisRecordSummary {
  result_json: AnalyzeResponse | null;
}