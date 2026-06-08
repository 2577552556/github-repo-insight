"use client";

import type { AIScore as AIScoreType } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface AIScoreCardProps {
  aiScore: AIScoreType;
}

const GRADE_COLORS: Record<string, string> = {
  A: "bg-green-500",
  B: "bg-blue-500",
  C: "bg-yellow-500",
  D: "bg-orange-500",
  F: "bg-red-500",
};

export function AIScoreCard({ aiScore }: AIScoreCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>AI Evaluation</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-4">
          <div
            className={`w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold text-white ${GRADE_COLORS[aiScore.grade] || "bg-gray-500"}`}
          >
            {aiScore.grade}
          </div>
          <div className="space-y-1">
            <div className="text-2xl font-bold">{aiScore.score}/100</div>
            <div className="text-sm text-muted-foreground">AI-generated score</div>
          </div>
        </div>
        <div className="pt-4 border-t">
          <p className="text-sm text-muted-foreground leading-relaxed">
            {aiScore.summary}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}