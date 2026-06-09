"use client";

import { useState, useCallback, useRef } from "react";
import type {
  AnalyzeResponse,
  RepositoryInfo,
  LanguageDistribution,
  RepositoryMetrics,
  HealthScore,
  AIScore,
  AIAnalysis,
} from "@/types";
import { analyzeRepositoryStream, StreamData, ProgressiveResult } from "@/services/api";

export type LoadingPhase = "idle" | "streaming" | "success" | "error";

interface UseAnalysisReturn {
  status: LoadingPhase;
  result: ProgressiveResult;
  error: string | null;
  analyze: (url: string) => void;
  reset: () => void;
}

const initialResult: ProgressiveResult = {
  repository: null,
  languages: null,
  metrics: null,
  healthScore: null,
  aiScore: null,
  aiAnalysis: null,
};

export function useAnalysis(): UseAnalysisReturn {
  const [status, setStatus] = useState<LoadingPhase>("idle");
  const [result, setResult] = useState<ProgressiveResult>(initialResult);
  const [error, setError] = useState<string | null>(null);
  const cleanupRef = useRef<(() => void) | null>(null);

  const reset = useCallback(() => {
    if (cleanupRef.current) {
      cleanupRef.current();
      cleanupRef.current = null;
    }
    setStatus("idle");
    setResult(initialResult);
    setError(null);
  }, []);

  const analyze = useCallback((url: string) => {
    // Reset previous state
    if (cleanupRef.current) {
      cleanupRef.current();
      cleanupRef.current = null;
    }
    setStatus("streaming");
    setResult(initialResult);
    setError(null);

    // Handle stream data
    const handleData = (data: StreamData) => {
      switch (data.type) {
        case "repository":
          setResult((prev) => ({
            ...prev,
            repository: data.data as RepositoryInfo,
          }));
          break;
        case "languages":
          setResult((prev) => ({
            ...prev,
            languages: data.data as LanguageDistribution,
          }));
          break;
        case "metrics":
          setResult((prev) => ({
            ...prev,
            metrics: data.data as RepositoryMetrics,
          }));
          break;
        case "health_score":
          setResult((prev) => ({
            ...prev,
            healthScore: data.data as HealthScore,
          }));
          break;
        case "ai_score":
          setResult((prev) => ({
            ...prev,
            aiScore: data.data as AIScore,
          }));
          break;
        case "ai_analysis":
          setResult((prev) => ({
            ...prev,
            aiAnalysis: data.data as AIAnalysis,
          }));
          break;
        case "complete":
          setStatus("success");
          break;
        case "error":
          setError(data.message || "An error occurred");
          setStatus("error");
          break;
      }
    };

    // Start streaming
    cleanupRef.current = analyzeRepositoryStream(url, handleData);
  }, []);

  return { status, result, error, analyze, reset };
}