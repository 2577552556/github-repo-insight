"use client";

import type { AIAnalysis, ConclusionItem } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface AIAnalysisCardProps {
  aiAnalysis: AIAnalysis | null;
}

// 置信度颜色
const CONFIDENCE_COLORS = {
  high: "bg-green-500/10 text-green-600 border-green-500/30",
  medium: "bg-yellow-500/10 text-yellow-600 border-yellow-500/30",
  low: "bg-red-500/10 text-red-600 border-red-500/30",
};

// 因果关系颜色
const CAUSATION_COLORS = {
  causation: "bg-blue-500/10 text-blue-600",
  correlation: "bg-purple-500/10 text-purple-600",
  unknown: "bg-gray-500/10 text-gray-600",
};

// 因果关系标签
const CAUSATION_LABELS = {
  causation: "因果",
  correlation: "相关",
  unknown: "未知",
};

function AnalysisItem({
  item,
  type,
}: {
  item: ConclusionItem;
  type: "strength" | "risk" | "suggestion";
}) {
  const config = {
    strength: {
      icon: "✓",
      iconClass: "text-green-500",
      bgClass: "bg-green-500/10 border-green-500/20",
    },
    risk: {
      icon: "⚠",
      iconClass: "text-amber-500",
      bgClass: "bg-amber-500/10 border-amber-500/20",
    },
    suggestion: {
      icon: "•",
      iconClass: "text-blue-500",
      bgClass: "bg-blue-500/10 border-blue-500/20",
    },
  };

  const { icon, iconClass, bgClass } = config[type];

  return (
    <div
      className={cn(
        "p-4 rounded-lg border",
        bgClass
      )}
    >
      <div className="flex gap-3">
        <span className={cn("text-lg font-bold", iconClass)}>{icon}</span>
        <div className="flex-1 space-y-2">
          <p className="text-sm leading-relaxed text-foreground/90">{item.text}</p>

          {/* 数据溯源和置信度 */}
          <div className="flex flex-wrap items-center gap-2">
            {/* 数据来源 */}
            {item.source && item.source !== "N/A" && (
              <Badge variant="outline" className="text-xs border-muted-foreground/30">
                <span className="text-muted-foreground mr-1">来源:</span>
                {item.source.length > 40 ? item.source.slice(0, 40) + "..." : item.source}
              </Badge>
            )}

            {/* 置信度 */}
            <Badge variant="outline" className={cn("text-xs", CONFIDENCE_COLORS[item.confidence])}>
              {item.confidence === "high" ? "高置信" : item.confidence === "medium" ? "中置信" : "低置信"}
            </Badge>

            {/* 因果关系 */}
            <Badge variant="outline" className={cn("text-xs", CAUSATION_COLORS[item.causation])}>
              {CAUSATION_LABELS[item.causation]}
            </Badge>
          </div>
        </div>
      </div>
    </div>
  );
}

function SectionTitle({
  title,
  icon,
  count,
}: {
  title: string;
  icon: string;
  count?: number;
}) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-lg">{icon}</span>
      <h4 className="font-medium">{title}</h4>
      {count !== undefined && (
        <span className="text-xs text-muted-foreground">({count}条)</span>
      )}
    </div>
  );
}

export function AIAnalysisCard({ aiAnalysis }: AIAnalysisCardProps) {
  if (!aiAnalysis) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>AI 深度分析</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">暂无 AI 分析数据</p>
        </CardContent>
      </Card>
    );
  }

  const { summary, strengths, risks, suggestions } = aiAnalysis;

  return (
    <Card className="border-muted">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span>AI 深度分析</span>
          {aiAnalysis.ai_used && (
            <span className="text-xs px-2 py-0.5 bg-green-500/10 text-green-600 rounded-full">
              DeepSeek
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 综合评价 */}
        {summary && (
          <div className="p-4 rounded-lg bg-muted/50 border">
            <p className="text-sm leading-relaxed">{summary}</p>
          </div>
        )}

        {/* 优势分析 */}
        {strengths && strengths.length > 0 && (
          <div className="space-y-3">
            <SectionTitle
              title="优势分析"
              icon="✓"
              count={strengths.length}
            />
            <div className="space-y-2">
              {strengths.map((item, index) => (
                <AnalysisItem key={index} item={item} type="strength" />
              ))}
            </div>
          </div>
        )}

        {/* 风险分析 */}
        {risks && risks.length > 0 && (
          <div className="space-y-3">
            <SectionTitle
              title="风险分析"
              icon="⚠"
              count={risks.length}
            />
            <div className="space-y-2">
              {risks.map((item, index) => (
                <AnalysisItem key={index} item={item} type="risk" />
              ))}
            </div>
          </div>
        )}

        {/* 改进建议 */}
        {suggestions && suggestions.length > 0 && (
          <div className="space-y-3">
            <SectionTitle
              title="改进建议"
              icon="•"
              count={suggestions.length}
            />
            <div className="space-y-2">
              {suggestions.map((item, index) => (
                <AnalysisItem key={index} item={item} type="suggestion" />
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}