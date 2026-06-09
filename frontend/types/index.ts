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
  pr_merge_time_avg: number | null;
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

export interface HealthScore {
  score: number;
  dimensions: HealthScoreDimensions;
}

export interface AIScore {
  score: number;
  grade: string;
  summary: string;
  ai_used: boolean;
}

export interface AIAnalysis {
  summary: string;
  strengths: string[];
  risks: string[];
  suggestions: string[];
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