"""
AI Evaluation Service using LangGraph + DeepSeek Agent.

架构：
    ┌─────────────────────────────────────────────────────────┐
    │                    LangGraph Agent                      │
    │  ┌───────────┐    ┌──────────────┐    ┌───────────┐     │
    │  │  Router   │───▶│   LLM Node   │───▶│  Output   │     │
    │  │  (LLM)    │    │  (DeepSeek)  │    │  Parser   │     │
    │  └───────────┘    └──────────────┘    └───────────┘     │
    │                          │                              │
    │                          ▼                              │
    │                   ┌──────────────┐                      │
    │                   │   Grading    │                      │
    │                   │   & Refine   │                      │
    │                   └──────────────┘                      │
    └─────────────────────────────────────────────────────────┘
"""

import logging
from typing import TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.graph import StateGraph, END

from app.core.config import settings
from app.schemas.analyze import RepositoryInfo, LanguageDistribution, AIScore

logger = logging.getLogger(__name__)


class EvaluationState(TypedDict):
    """LangGraph 状态定义."""
    repository: RepositoryInfo
    languages: LanguageDistribution
    score: int
    grade: str
    summary: str
    feedback: str
    iteration: int


SYSTEM_PROMPT = """你是一个专业的 GitHub 仓库评估专家。请评估仓库的健康状况并给出评分。

评估维度：
1. 热度 (Popularity): Stars、Forks、Watchers 数量
2. 活跃度 (Activity): 最近更新时间、提交频率
3. 社区 (Community): 贡献者数量、Issue 讨论
4. 维护 (Maintenance): Issue 处理速度、PR 合并情况

评分标准：
- A (85-100): 优秀 - 非常受欢迎，高度活跃维护，强大的社区
- B (70-84): 良好 - 维护良好，社区参与度不错
- C (50-69): 一般 - 中等活动和社区
- D (30-49): 较差 - 低活跃度或社区
- F (0-29): 差 - 新仓库、被放弃或几乎无互动

请提供：
1. Score: 0-100 的数字评分
2. Grade: A-F 的等级
3. Summary: 2-3 句的中文评估总结

始终使用中文回复。"""


def build_user_prompt(repository: RepositoryInfo, languages: LanguageDistribution) -> str:
    """构建用户提示词."""
    lang_str = ", ".join(
        f"{lang} ({pct:.1f}%)" for lang, pct in languages.languages.items()
    ) if languages.languages else "无可用数据"

    return f"""请评估以下 GitHub 仓库：

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

编程语言分布：
{lang_str}

请按以下格式回复：
Score: [0-100]
Grade: [A-F]
Summary: [中文评估总结]"""


def create_evaluation_agent() -> StateGraph:
    """创建 LangGraph 评估 Agent."""

    def evaluate_node(state: EvaluationState) -> EvaluationState:
        """LLM 评估节点."""
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
            HumanMessage(content=build_user_prompt(repo, langs)),
        ]

        response = llm.invoke(messages)
        content = response.content if hasattr(response, "content") else str(response)

        # 解析响应
        score, grade, summary = parse_response(content, state["repository"], state["languages"])

        return {
            **state,
            "score": score,
            "grade": grade,
            "summary": summary,
            "iteration": state["iteration"] + 1,
        }

    def should_refine(state: EvaluationState) -> str:
        """判断是否需要重新评估."""
        if state["iteration"] >= 2:
            return "end"
        if state["score"] == 0:
            return "retry"
        return "end"

    # 构建图
    graph = StateGraph(EvaluationState)
    graph.add_node("evaluate", evaluate_node)
    graph.set_entry_point("evaluate")
    graph.add_conditional_edges("evaluate", should_refine, {
        "retry": "evaluate",
        "end": END,
    })

    return graph.compile()


def parse_response(
    content: str,
    repository: RepositoryInfo,
    languages: LanguageDistribution,
) -> tuple[int, str, str]:
    """解析 LLM 响应."""
    score = 50
    grade = "C"
    summary = content

    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("Score:") or line.startswith("分数:"):
            try:
                parts = line.split(":")
                if len(parts) >= 2:
                    score = int(parts[1].strip().split()[0])
            except (ValueError, IndexError):
                pass
        elif line.startswith("Grade:") or line.startswith("等级:"):
            try:
                parts = line.split(":")
                if len(parts) >= 2:
                    grade = parts[1].strip()[0].upper()
                    if grade not in "ABCDEF":
                        grade = "C"
            except (ValueError, IndexError):
                pass

    score = max(0, min(100, score))

    return score, grade, summary


class AIEvaluationService:
    """基于 LangGraph + DeepSeek 的 AI 评估服务."""

    def __init__(self):
        self._agent = None

    @property
    def agent(self):
        """延迟初始化 Agent."""
        if self._agent is None:
            self._agent = create_evaluation_agent()
        return self._agent

    async def evaluate(
        self, repository: RepositoryInfo, languages: LanguageDistribution
    ) -> AIScore:
        """评估仓库并返回 AI 评分.

        如果设置了 DEEPSEEK_API_KEY，使用 DeepSeek Agent。
        否则使用规则评估作为 Fallback。
        """
        if settings.DEEPSEEK_API_KEY:
            return await self._evaluate_with_agent(repository, languages)
        result = self._evaluate_with_rules(repository, languages)
        result.ai_used = False
        return result

    async def _evaluate_with_agent(
        self, repository: RepositoryInfo, languages: LanguageDistribution
    ) -> AIScore:
        """使用 LangGraph Agent 评估."""
        try:
            initial_state: EvaluationState = {
                "repository": repository,
                "languages": languages,
                "score": 0,
                "grade": "C",
                "summary": "",
                "feedback": "",
                "iteration": 0,
            }

            result = await self.agent.ainvoke(initial_state)

            return AIScore(
                score=result["score"],
                grade=result["grade"],
                summary=result["summary"],
                ai_used=True,
            )
        except Exception as e:
            logger.warning(f"DeepSeek API 调用失败: {e}，使用规则评估")
            return self._evaluate_with_rules(repository, languages)

    def _evaluate_with_rules(
        self, repository: RepositoryInfo, languages: LanguageDistribution
    ) -> AIScore:
        """基于规则的评估 Fallback."""
        stars = repository.stars
        forks = repository.forks
        issues = repository.open_issues
        language_count = len(languages.languages)

        score = 0
        grade = "F"

        if stars > 100000:
            score = 95
            grade = "A"
        elif stars > 50000:
            score = 88
            grade = "A"
        elif stars > 10000:
            if forks > 1000:
                score = 82
                grade = "B"
            else:
                score = 78
                grade = "B"
        elif stars > 1000:
            if forks > 100:
                score = 72
                grade = "B"
            else:
                score = 65
                grade = "C"
        elif stars > 100:
            score = 45
            grade = "D"
        else:
            score = 20
            grade = "F"

        if language_count >= 5:
            score = min(100, score + 5)

        if issues > 0:
            issue_ratio = issues / max(stars, 1)
            if issue_ratio > 0.5:
                score = max(0, score - 10)

        grade_text = "优秀" if score >= 85 else "良好" if score >= 70 else "一般" if score >= 50 else "较差" if score >= 30 else "需关注"

        return AIScore(
            score=score,
            grade=grade,
            summary=f"仓库 '{repository.full_name}' 拥有 {stars:,} 星标和 {forks:,} 分支。"
            f"使用 {language_count} 种编程语言。"
            f"综合评估：{grade_text}。",
            ai_used=False,
        )


ai_evaluation_service = AIEvaluationService()