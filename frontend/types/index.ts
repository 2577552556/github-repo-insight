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
}

export interface LanguageDistribution {
  languages: Record<string, number>;
}

export interface HealthScoreDimensions {
  popularity: number;
  activity: number;
  community: number;
  maintenance: number;
}

export interface HealthScore {
  score: number;
  dimensions: HealthScoreDimensions;
}

export interface AIScore {
  score: number;
  grade: string;
  summary: string;
}

export interface AnalyzeResponse {
  repository: RepositoryInfo;
  languages: LanguageDistribution;
  health_score: HealthScore;
  ai_score: AIScore;
}

export interface AnalyzeRequest {
  url: string;
}

export type AnalysisStatus = "idle" | "loading" | "success" | "error";

export interface ApiError {
  detail: string;
}