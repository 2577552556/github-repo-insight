"use client";

import type { HealthScore } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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

export function HealthScoreCard({ healthScore }: HealthScoreCardProps) {
  const dimensions = [
    { name: "热度", value: healthScore.dimensions.popularity, max: 25 },
    { name: "活跃度", value: healthScore.dimensions.activity, max: 25 },
    { name: "社区", value: healthScore.dimensions.community, max: 25 },
    { name: "维护", value: healthScore.dimensions.maintenance, max: 25 },
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle>健康评分</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="flex justify-center">
          <CircularProgress score={healthScore.score} />
        </div>
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
                    dim.value >= 20 ? "bg-green-500" : dim.value >= 10 ? "bg-yellow-500" : "bg-red-500"
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