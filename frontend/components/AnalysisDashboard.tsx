"use client";

import type { ProgressiveResult } from "@/services/api";
import { RepositoryInfo } from "@/components/RepositoryInfo";
import { LanguageChart } from "@/components/LanguageChart";
import { HealthScoreCard } from "@/components/HealthScoreCard";
import { AIAnalysisCard } from "@/components/AIAnalysisCard";
import { AIScoreCard } from "@/components/AIScoreCard";
import {
  SkeletonRepositoryInfo,
  SkeletonLanguageChart,
  SkeletonHealthScore,
  SkeletonAIAnalysis,
  SkeletonAIScore,
} from "@/components/SkeletonCard";

interface AnalysisDashboardProps {
  result: ProgressiveResult;
  isStreaming?: boolean;
}

export function AnalysisDashboard({ result, isStreaming }: AnalysisDashboardProps) {
  return (
    <div className="space-y-6">
      {/* Repository Info - 最早到达 */}
      {result.repository ? (
        <RepositoryInfo repository={result.repository} />
      ) : (
        <SkeletonRepositoryInfo />
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Language Chart */}
        {result.languages ? (
          <LanguageChart languages={result.languages} />
        ) : (
          <SkeletonLanguageChart />
        )}

        {/* Health Score Card */}
        {result.healthScore ? (
          <HealthScoreCard healthScore={result.healthScore} />
        ) : (
          <SkeletonHealthScore />
        )}
      </div>

      {/* AI Analysis Card - 最后到达 */}
      {result.aiAnalysis ? (
        <AIAnalysisCard aiAnalysis={result.aiAnalysis} />
      ) : (
        <SkeletonAIAnalysis />
      )}

      {/* AI Score Card */}
      {result.aiScore ? (
        <AIScoreCard aiScore={result.aiScore} />
      ) : (
        <SkeletonAIScore />
      )}
    </div>
  );
}