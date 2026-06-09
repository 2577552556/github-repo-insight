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
  | "complete"
  | "error";

export interface StreamData {
  type: StreamDataType;
  data?: unknown;
  message?: string;
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