import type {
  AnalyzeRequest,
  AnalyzeResponse,
  ApiError,
  RepositoryInfo,
  LanguageDistribution,
  RepositoryMetrics,
  HealthScore,
  AIScore,
  AIAnalysis,
  AnalysisRecordSummary,
  AnalysisRecord,
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function analyzeRepository(
  url: string
): Promise<AnalyzeResponse> {
  const request: AnalyzeRequest = { url };

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData: ApiError = await response.json();
    throw new Error(errorData.detail || "Failed to analyze repository");
  }

  return response.json();
}

export type StreamDataType =
  | "repository"
  | "languages"
  | "metrics"
  | "health_score"
  | "ai_score"
  | "ai_analysis"
  | "saved"
  | "complete"
  | "error";

export interface StreamData {
  type: StreamDataType;
  data?: unknown;
  message?: string;
  id?: string;
  status?: string;
}

export type StreamCallback = (data: StreamData) => void;

export function analyzeRepositoryStream(
  url: string,
  onData: StreamCallback
): () => void {
  const eventSource = new EventSource(
    `${API_BASE_URL}/api/analyze/stream?url=${encodeURIComponent(url)}`
  );

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) as StreamData;
      onData(data);

      if (data.type === "complete" || data.type === "error") {
        eventSource.close();
      }
    } catch {
      // Ignore parse errors
    }
  };

  eventSource.onerror = () => {
    eventSource.close();
    // 通知上层发生了错误
    onData({ type: "error", message: "连接中断，请检查网络或重试" });
  };

  // Return cleanup function
  return () => {
    eventSource.close();
  };
}

export interface ProgressiveResult {
  repository: RepositoryInfo | null;
  languages: LanguageDistribution | null;
  metrics: RepositoryMetrics | null;
  healthScore: HealthScore | null;
  aiScore: AIScore | null;
  aiAnalysis: AIAnalysis | null;
}

// History API functions
export async function getAnalysisHistory(
  skip: number = 0,
  limit: number = 20,
  search?: string
): Promise<AnalysisRecordSummary[]> {
  const params = new URLSearchParams({
    skip: String(skip),
    limit: String(limit),
  });
  if (search) {
    params.set("search", search);
  }

  const response = await fetch(
    `${API_BASE_URL}/api/analysis/history?${params.toString()}`
  );

  if (!response.ok) {
    const errorData: ApiError = await response.json();
    throw new Error(errorData.detail || "Failed to fetch history");
  }

  return response.json();
}

export async function getAnalysisRecord(
  id: string
): Promise<AnalysisRecord> {
  const response = await fetch(`${API_BASE_URL}/api/analysis/${id}`);

  if (!response.ok) {
    const errorData: ApiError = await response.json();
    throw new Error(errorData.detail || "Failed to fetch record");
  }

  return response.json();
}

export async function deleteAnalysisRecord(
  id: string
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/analysis/${id}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    const errorData: ApiError = await response.json();
    throw new Error(errorData.detail || "Failed to delete record");
  }
}

export async function createAnalysis(
  url: string
): Promise<{ id: string; status: string }> {
  const request: AnalyzeRequest = { url };

  const response = await fetch(`${API_BASE_URL}/api/analysis`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData: ApiError = await response.json();
    throw new Error(errorData.detail || "Failed to create analysis");
  }

  return response.json();
}