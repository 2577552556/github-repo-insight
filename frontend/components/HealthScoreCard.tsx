"use client";

import type { HealthScore } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface HealthScoreCardProps {
  healthScore: HealthScore;
}

function CircularProgress({ score }: { score: number }) {
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="relative flex items-center justify-center">
      <svg width="160" height="160" className="transform -rotate-90">
        <circle
          cx="80"
          cy="80"
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="12"
          className="text-muted"
        />
        <circle
          cx="80"
          cy="80"
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth="12"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className={cn(
            score >= 70 ? "text-green-500" : score >= 40 ? "text-yellow-500" : "text-red-500"
          )}
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="text-3xl font-bold">{score}</span>
        <span className="text-xs text-muted-foreground">/ 100</span>
      </div>
    </div>
  );
}

// 项目类型中文映射
const TYPE_LABELS: Record<string, string> = {
  personal: "个人项目",
  community: "社区开源",
  corporate: "企业主导",
  opencore: "Open Core",
  source_available: "源码可见",
  ai_platform: "AI平台",
  infrastructure: "基础设施",
  sdk_library: "SDK/工具库",
  developer_tool: "开发者工具",
};

// 项目类型颜色
const TYPE_COLORS: Record<string, string> = {
  ai_platform: "bg-purple-500/10 text-purple-600 border-purple-500/30",
  infrastructure: "bg-blue-500/10 text-blue-600 border-blue-500/30",
  sdk_library: "bg-green-500/10 text-green-600 border-green-500/30",
  developer_tool: "bg-orange-500/10 text-orange-600 border-orange-500/30",
  corporate: "bg-red-500/10 text-red-600 border-red-500/30",
  community: "bg-cyan-500/10 text-cyan-600 border-cyan-500/30",
  opencore: "bg-pink-500/10 text-pink-600 border-pink-500/30",
  source_available: "bg-amber-500/10 text-amber-600 border-amber-500/30",
  personal: "bg-gray-500/10 text-gray-600 border-gray-500/30",
};

function TypeAwarenessBadge({ healthScore }: { healthScore: HealthScore }) {
  const typeDetection = healthScore.type_detection;
  if (!typeDetection) return null;

  const primaryType = typeDetection.primary_type;
  const confidence = typeDetection.confidence;
  const label = TYPE_LABELS[primaryType] || primaryType;
  const colorClass = TYPE_COLORS[primaryType] || TYPE_COLORS.personal;

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <Badge variant="outline" className={cn("border", colorClass)}>
        {label}
      </Badge>
      {typeDetection.secondary_types && typeDetection.secondary_types.length > 0 && (
        <div className="flex gap-1">
          {typeDetection.secondary_types.slice(0, 2).map((t) => (
            <Badge key={t} variant="outline" className={cn("border text-xs", TYPE_COLORS[t] || TYPE_COLORS.personal)}>
              {TYPE_LABELS[t] || t}
            </Badge>
          ))}
        </div>
      )}
      <span className="text-xs text-muted-foreground">
        置信度 {Math.round(confidence * 100)}%
      </span>
    </div>
  );
}

function AIMaturityBadge({ healthScore }: { healthScore: HealthScore }) {
  const aiMaturity = healthScore.ai_maturity;
  if (!aiMaturity) return null;

  const detectedCaps = aiMaturity.capabilities
    .filter((c) => c.detected)
    .map((c) => c.capability);

  return (
    <div className="space-y-2 p-3 rounded-lg bg-purple-500/5 border border-purple-500/20">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-purple-600">AI 成熟度</span>
        <span className="text-lg font-bold text-purple-600">{aiMaturity.total_score}/100</span>
      </div>
      <div className="flex flex-wrap gap-1">
        {detectedCaps.map((cap) => (
          <Badge key={cap} variant="outline" className="text-xs border-purple-500/30 text-purple-600">
            {cap}
          </Badge>
        ))}
      </div>
      {aiMaturity.model_support && aiMaturity.model_support.length > 0 && (
        <div className="text-xs text-muted-foreground">
          支持模型: {aiMaturity.model_support.slice(0, 5).join(", ")}
        </div>
      )}
    </div>
  );
}

export function HealthScoreCard({ healthScore }: HealthScoreCardProps) {
  const dimensions = [
    { name: "流行度", value: healthScore.dimensions.popularity, max: 25 },
    { name: "活跃度", value: healthScore.dimensions.activity, max: 25 },
    { name: "社区", value: healthScore.dimensions.community, max: 15 },
    { name: "Issue治理", value: healthScore.dimensions.issue_governance, max: 10 },
    { name: "PR治理", value: healthScore.dimensions.pr_governance, max: 10 },
    { name: "工程化", value: healthScore.dimensions.engineering, max: 10 },
    { name: "发布维护", value: healthScore.dimensions.release_maintenance, max: 5 },
  ];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>健康评分</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex justify-center">
          <CircularProgress score={healthScore.score} />
        </div>

        {/* 项目类型标签 */}
        <TypeAwarenessBadge healthScore={healthScore} />

        {/* AI 成熟度（仅 AI Platform 项目） */}
        <AIMaturityBadge healthScore={healthScore} />

       <div className="grid grid-cols-2 gap-4">
          {dimensions.map((dim) => (
            <div key={dim.name} className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">{dim.name}</span>
                <span className="font-medium">{dim.value}/{dim.max}</span>
              </div>
              <div className="h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className={cn(
                    "h-full rounded-full",
                    dim.value >= dim.max * 0.7 ? "bg-green-500" : dim.value >= dim.max * 0.4 ? "bg-yellow-500" : "bg-red-500"
                  )}
                  style={{ width: `${(dim.value / dim.max) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}