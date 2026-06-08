"""
AI Evaluation Service using LangGraph + DeepSeek.

功能：
1. AIScore: DeepSeek AI 快速评分 (0-100)
2. AIAnalysis: DeepSeek AI 深度分析 (summary/strengths/risks/suggestions)

注意：无 DEEPSEEK_API_KEY 时抛出异常
"""

import logging
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, END

from app.core.config import settings
from app.core.exceptions import NetworkError
from app.schemas.analyze import (
    RepositoryInfo,
    LanguageDistribution,
    AIScore,
    AIAnalysis,
)

logger = logging.getLogger(__name__)


class EvaluationState(TypedDict):
    """LangGraph 状态定义."""
    repository: RepositoryInfo
    languages: LanguageDistribution
    recent_commits: int
    contributors_count: int
    score: int
    grade: str
    summary: str
    strengths: list[str]
    risks: list[str]
    suggestions: list[str]
    iteration: int


SYSTEM_PROMPT = """你是一个专业的 GitHub 仓库评估专家。请对仓库进行深度分析。

分析维度：
1. 项目定位：这个仓库是什么，用什么技术栈，解决什么问题
2. 优势：社区活跃、文档完善、技术成熟、维护及时等
3. 风险：长期未更新、贡献者少、Issue 积压、依赖过时等
4. 建议：如何改进该项目

请用中文回复，始终输出 JSON 格式：

{
  "score": 85,
  "grade": "A",
  "summary": "项目一句话总结（50字内）",
  "strengths": ["优势1", "优势2", "优势3"],
  "risks": ["风险1", "风险2", "风险3"],
  "suggestions": ["建议1", "建议2", "建议3"]
}

只输出 JSON，不要有其他内容。"""


def build_analysis_prompt(
    repository: RepositoryInfo,
    languages: LanguageDistribution,
    recent_commits: int,
    contributors_count: int,
) -> str:
    """构建分析提示词."""
    lang_str = ", ".join(
        f"{lang} ({pct:.1f}%)" for lang, pct in languages.languages.items()
    ) if languages.languages else "无可用数据"

    return f"""请分析以下 GitHub 仓库：

## 基础信息
仓库名称：{repository.full_name}
描述：{repository.description or "暂无描述"}
主要语言：{repository.language or "未指定"}
星标数：{repository.stars:,}
分支数：{repository.forks:,}
关注者数：{repository.watchers}
开放 Issues：{repository.open_issues}
默认分支：{repository.default_branch}
创建时间：{repository.created_at}
最后更新：{repository.updated_at}
开源协议：{repository.license or "未指定"}
主题标签：{', '.join(repository.topics) if repository.topics else "无"}

## 编程语言分布
{lang_str}

## 活跃度
近30天 Commit 数：{recent_commits}
贡献者数量：{contributors_count}

请分析并给出 JSON 格式的评估结果。"""


def create_analysis_agent() -> StateGraph:
    """创建 LangGraph 分析 Agent."""

    def analyze_node(state: EvaluationState) -> EvaluationState:
        """LLM 分析节点."""
        repo = state["repository"]
        langs = state["languages"]

        llm = ChatDeepSeek(
            model="deepseek-chat",
            api_key=settings.DEEPSEEK_API_KEY or "",
            base_url=settings.DEEPSEEK_API_URL,
            temperature=0.3,
        )

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=build_analysis_prompt(
                repo, langs,
                state["recent_commits"],
                state["contributors_count"]
            )),
        ]

        response = llm.invoke(messages)
        content = response.content if hasattr(response, "content") else str(response)

        # 解析 JSON 响应
        score, grade, summary, strengths, risks, suggestions = parse_analysis_response(content, repo)

        return {
            **state,
            "score": score,
            "grade": grade,
            "summary": summary,
            "strengths": strengths,
            "risks": risks,
            "suggestions": suggestions,
            "iteration": state["iteration"] + 1,
        }

    # 构建图
    graph = StateGraph(EvaluationState)
    graph.add_node("analyze", analyze_node)
    graph.set_entry_point("analyze")
    graph.add_edge("analyze", END)

    return graph.compile()


def parse_analysis_response(content: str, repository: RepositoryInfo) -> tuple[int, str, str, list[str], list[str], list[str]]:
    """解析 LLM 响应为分析结果."""
    import json
    import re

    # 尝试提取 JSON
    json_match = re.search(r'\{[\s\S]*\}', content)
    if not json_match:
        return 50, "C", f"仓库 '{repository.full_name}' 的 AI 评分", [], [], []

    try:
        data = json.loads(json_match.group())
        score = data.get("score", 50)
        grade = data.get("grade", "C")
        summary = data.get("summary", f"仓库 '{repository.full_name}' 的 AI 评分")
        strengths = data.get("strengths", [])
        risks = data.get("risks", [])
        suggestions = data.get("suggestions", [])
        return score, grade, summary, strengths, risks, suggestions
    except (json.JSONDecodeError, KeyError):
        return 50, "C", f"仓库 '{repository.full_name}' 的 AI 评分", [], [], []


class AIEvaluationService:
    """AI 评估服务 (仅支持 DeepSeek)."""

    def __init__(self):
        self._agent = None

    @property
    def agent(self):
        """延迟初始化 Agent."""
        if self._agent is None:
            self._agent = create_analysis_agent()
        return self._agent

    def _check_api_key(self) -> None:
        """检查 API Key 是否配置."""
        if not settings.DEEPSEEK_API_KEY:
            raise ValueError(
                "DEEPSEEK_API_KEY 未配置。"
                "请设置环境变量 DEEPSEEK_API_KEY 或在 .env 文件中配置。"
                "AI 分析功能需要有效的 DeepSeek API Key。"
            )

    async def evaluate_quick(
        self,
        repository: RepositoryInfo,
        recent_commits: int = 0,
        contributors_count: int = 0,
    ) -> AIScore:
        """快速评分 (仅支持 DeepSeek AI)."""
        self._check_api_key()

        try:
            initial_state: EvaluationState = {
                "repository": repository,
                "languages": LanguageDistribution(languages={}),
                "recent_commits": recent_commits,
                "contributors_count": contributors_count,
                "score": 50,
                "grade": "C",
                "summary": "",
                "strengths": [],
                "risks": [],
                "suggestions": [],
                "iteration": 0,
            }

            result = await self.agent.ainvoke(initial_state)

            return AIScore(
                score=max(0, min(100, result["score"])),
                grade=result["grade"],
                summary=result["summary"] or f"仓库 '{repository.full_name}' 的 AI 评分",
                ai_used=True,
            )
        except Exception as e:
            logger.error(f"AI 快速评分失败: {e}")
            raise NetworkError(f"AI 评分服务调用失败: {str(e)}")

    async def analyze(
        self,
        repository: RepositoryInfo,
        languages: LanguageDistribution,
        recent_commits: int = 0,
        contributors_count: int = 0,
    ) -> AIAnalysis:
        """深度 AI 分析 (仅支持 DeepSeek AI)."""
        self._check_api_key()

        try:
            initial_state: EvaluationState = {
                "repository": repository,
                "languages": languages,
                "recent_commits": recent_commits,
                "contributors_count": contributors_count,
                "score": 50,
                "grade": "C",
                "summary": "",
                "strengths": [],
                "risks": [],
                "suggestions": [],
                "iteration": 0,
            }

            result = await self.agent.ainvoke(initial_state)

            return AIAnalysis(
                summary=result["summary"] or f"这是一个名为 {repository.name} 的 GitHub 仓库",
                strengths=result["strengths"],
                risks=result["risks"],
                suggestions=result["suggestions"],
                ai_used=True,
            )
        except Exception as e:
            logger.error(f"DeepSeek API 调用失败: {e}")
            raise NetworkError(f"AI 分析服务调用失败: {str(e)}")


ai_evaluation_service = AIEvaluationService()