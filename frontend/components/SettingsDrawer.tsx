"use client";

import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useSettings } from "@/hooks/useSettings";

export function SettingsDrawer() {
  const { isOpen, settings, loading, error, closeDrawer, loadSettings, saveSettings } =
    useSettings();
  const [deepseekKey, setDeepseekKey] = useState("");
  const [githubToken, setGithubToken] = useState("");
  const [showDeepseekKey, setShowDeepseekKey] = useState(false);
  const [showGithubToken, setShowGithubToken] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadSettings();
    }
  }, [isOpen, loadSettings]);

  const handleSave = () => {
    saveSettings(deepseekKey, githubToken);
  };

  const handleClose = () => {
    setDeepseekKey("");
    setGithubToken("");
    setShowDeepseekKey(false);
    setShowGithubToken(false);
    closeDrawer();
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/50 animate-in fade-in duration-200"
        onClick={handleClose}
      />

      {/* Drawer */}
      <div className="fixed right-0 top-0 z-50 h-full w-full max-w-md bg-background border-l shadow-xl animate-in slide-in-from-right duration-300">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b">
            <h2 className="text-lg font-semibold">设置</h2>
            <Button variant="ghost" size="icon" onClick={handleClose}>
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            <div className="space-y-4">
              <h3 className="font-medium text-sm uppercase tracking-wide text-muted-foreground">
                AI 配置
              </h3>

              <div className="space-y-2">
                <Label htmlFor="deepseek-key">DeepSeek API Key</Label>
                <div className="relative">
                  <Input
                    id="deepseek-key"
                    type={showDeepseekKey ? "text" : "password"}
                    placeholder="sk-..."
                    value={deepseekKey}
                    onChange={(e) => setDeepseekKey(e.target.value)}
                    className="pr-10"
                  />
                  <Button
                    variant="ghost"
                    size="icon"
                    className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                    onClick={() => setShowDeepseekKey(!showDeepseekKey)}
                  >
                    {showDeepseekKey ? (
                      <span className="text-xs">隐藏</span>
                    ) : (
                      <span className="text-xs">显示</span>
                    )}
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground">
                  用于 AI 解读功能，无 API Key 时 AI 分析不可用
                </p>
                <a
                  href="https://platform.deepseek.com/api_keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-500 hover:underline"
                >
                  获取 DeepSeek API Key →
                </a>
              </div>

              <div className="space-y-2">
                <Label htmlFor="github-token">GitHub Token</Label>
                <div className="relative">
                  <Input
                    id="github-token"
                    type={showGithubToken ? "text" : "password"}
                    placeholder="ghp_..."
                    value={githubToken}
                    onChange={(e) => setGithubToken(e.target.value)}
                    className="pr-10"
                  />
                  <Button
                    variant="ghost"
                    size="icon"
                    className="absolute right-0 top-0 h-full px-3 hover:bg-transparent"
                    onClick={() => setShowGithubToken(!showGithubToken)}
                  >
                    {showGithubToken ? (
                      <span className="text-xs">隐藏</span>
                    ) : (
                      <span className="text-xs">显示</span>
                    )}
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground">
                  用于提高 GitHub API 请求限额（可选，无 Token 限制 60次/小时，有 Token 5000次/小时），只需配置`public_repo`权限
                </p>
                <a
                  href="https://github.com/settings/tokens/new?description=GitHub%20Repo%20Insight&scopes="
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-500 hover:underline"
                >
                  获取 GitHub Token →
                </a>
              </div>

              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">AI状态:</span>
                {settings?.deepseek_configured ? (
                  <span className="text-green-600 font-medium">已配置</span>
                ) : (
                  <span className="text-yellow-600 font-medium">未配置</span>
                )}
              </div>

              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">GitHub 状态:</span>
                {settings?.github_configured ? (
                  <span className="text-green-600 font-medium">已配置</span>
                ) : (
                  <span className="text-yellow-600 font-medium">未配置</span>
                )}
              </div>

              {error && (
                <div className="text-sm text-red-500 bg-red-50 dark:bg-red-950 p-3 rounded-md">
                  {error}
                </div>
              )}
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 px-6 py-4 border-t">
            <Button variant="outline" onClick={handleClose}>
              取消
            </Button>
            <Button onClick={handleSave} disabled={loading}>
              {loading ? "保存中..." : "保存"}
            </Button>
          </div>
        </div>
      </div>
    </>
  );
}