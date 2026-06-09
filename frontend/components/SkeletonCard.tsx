"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface SkeletonCardProps {
  title: string;
  className?: string;
}

export function SkeletonCard({ title, className }: SkeletonCardProps) {
  return (
    <Card className={cn("animate-pulse", className)}>
      <CardHeader>
        <CardTitle className="text-sm">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {/* Skeleton lines */}
          <div className="h-4 bg-muted rounded w-3/4" />
          <div className="h-4 bg-muted rounded w-1/2" />
          <div className="h-4 bg-muted rounded w-5/6" />
        </div>
      </CardContent>
    </Card>
  );
}

export function SkeletonRepositoryInfo() {
  return (
    <Card className="animate-pulse">
      <CardHeader>
        <CardTitle className="text-sm">仓库信息</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="h-6 bg-muted rounded w-2/3" />
          <div className="h-4 bg-muted rounded w-full" />
          <div className="grid grid-cols-3 gap-4 mt-4">
            <div className="h-16 bg-muted rounded" />
            <div className="h-16 bg-muted rounded" />
            <div className="h-16 bg-muted rounded" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function SkeletonHealthScore() {
  return (
    <Card className="animate-pulse">
      <CardHeader>
        <CardTitle className="text-sm">健康评分</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex justify-center items-center">
          <div className="w-32 h-32 rounded-full bg-muted" />
        </div>
        <div className="grid grid-cols-2 gap-4 mt-6">
          <div className="h-8 bg-muted rounded" />
          <div className="h-8 bg-muted rounded" />
          <div className="h-8 bg-muted rounded" />
          <div className="h-8 bg-muted rounded" />
        </div>
      </CardContent>
    </Card>
  );
}

export function SkeletonLanguageChart() {
  return (
    <Card className="animate-pulse">
      <CardHeader>
        <CardTitle className="text-sm">语言分布</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex justify-center items-center h-40">
          <div className="w-32 h-32 rounded-full bg-muted" />
        </div>
      </CardContent>
    </Card>
  );
}

export function SkeletonAIAnalysis() {
  return (
    <Card className="animate-pulse">
      <CardHeader>
        <CardTitle className="text-sm">AI 深度分析</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="h-20 bg-muted rounded" />
          <div className="space-y-2">
            <div className="h-4 bg-muted rounded w-full" />
            <div className="h-4 bg-muted rounded w-5/6" />
            <div className="h-4 bg-muted rounded w-4/5" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function SkeletonAIScore() {
  return (
    <Card className="animate-pulse">
      <CardHeader>
        <CardTitle className="text-sm">健康等级</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-full bg-muted" />
          <div className="space-y-2">
            <div className="h-6 bg-muted rounded w-20" />
            <div className="h-4 bg-muted rounded w-16" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}