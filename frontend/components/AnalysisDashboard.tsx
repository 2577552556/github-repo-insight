"use client";

import type { AnalyzeResponse } from "@/types";
import { RepositoryInfo } from "@/components/RepositoryInfo";
import { LanguageChart } from "@/components/LanguageChart";
import { HealthScoreCard } from "@/components/HealthScoreCard";
import { AIAnalysisCard } from "@/components/AIAnalysisCard";
import { AIScoreCard } from "@/components/AIScoreCard";

interface AnalysisDashboardProps {
  result: AnalyzeResponse;
}

export function AnalysisDashboard({ result }: AnalysisDashboardProps) {
  return (
    <div className="space-y-6">
      <RepositoryInfo repository={result.repository} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <LanguageChart languages={result.languages} />
        <HealthScoreCard healthScore={result.health_score} />
      </div>

      <AIAnalysisCard aiAnalysis={result.ai_analysis} />

      <AIScoreCard aiScore={result.ai_score} />
    </div>
  );
}