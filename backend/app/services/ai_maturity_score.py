"""
AI Project Maturity Score - AI 项目成熟度专项评分

针对 AI Platform 类型项目，增加专项评分：
- RAG (Retrieval-Augmented Generation)
- Agent (智能体)
- Workflow (工作流编排)
- Knowledge Base (知识库)
- Tool Calling (工具调用)
- Model Ecosystem (模型生态)
- Deployment (部署能力)

评分结果用于增强 AI 项目的评估深度。
"""

from dataclasses import dataclass
from typing import Any

from app.schemas.analyze import RepositoryInfo


# AI 能力检测关键词
CAPABILITY_KEYWORDS = {
    "rag": {
        "rag", "retrieval", "retrieval-augmented", "knowledge retrieval",
        "vector search", "embedding", "chunk", "indexing",
        "semantic search", "similarity search"
    },
    "agent": {
        "agent", "multi-agent", "multiagent", "autonomous agent",
        "agentic", "agentic workflow", "reflection", "planning",
        "reasoning", "react", "act"
    },
    "workflow": {
        "workflow", "pipeline", "orchestration", "flow", "node",
        "编排", "流程", "节点", "edges", "dag"
    },
    "knowledge_base": {
        "knowledge base", "knowledge-base", "知识库", "kb",
        "document qa", "document search", "qa system", "qa bot"
    },
    "tool_calling": {
        "tool", "tools", "function call", "function calling",
        "tool use", "tool calling", "plugin", "extension"
    },
    "model_ecosystem": {
        "gpt", "chatgpt", "claude", "llm", "openai", "anthropic",
        "gemini", "qwen", "deepseek", "mistral", "local llm",
        "ollama", "llama", "model support", "model ecosystem"
    },
    "deployment": {
        "deploy", "deployment", "docker", "kubernetes", "k8s",
        "cloud", "serverless", "api", "fastapi", "api server",
        "hosting", "saas", "paas"
    },
}

# 模型名称映射
KNOWN_MODELS = {
    "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "chatgpt",
    "claude-3", "claude-3-opus", "claude-3-sonnet", "claude-3-haiku",
    "qwen", "qwen-turbo", "qwen-plus", "qwen-max",
    "deepseek", "deepseek-chat", "deepseek-coder",
    "gemini", "gemini-pro", "gemini-ultra",
    "llama", "llama-2", "llama-3", "mistral",
    "ollama", "local llm", "huggingface",
}


@dataclass
class AICapabilityScore:
    """AI 能力评分结果"""
    capability: str
    detected: bool
    confidence: float  # 0.0-1.0
    signals: list[str]  # 检测信号
    maturity_score: int  # 0-10


@dataclass
class AIMaturityScore:
    """AI 成熟度评分结果"""
    is_ai_project: bool
    total_score: int  # 0-100 (AI专项，满分100)
    capabilities: list[dict[str, Any]]
    model_support: list[str]  # 支持的模型列表
    deployment_methods: list[str]  # 部署方式


def detect_ai_capabilities(repo: RepositoryInfo) -> list[dict[str, Any]]:
    """检测仓库的 AI 能力

    基于 topics、description 关键词匹配
    """
    capabilities = []

    # 合并所有文本特征用于匹配
    all_text = " ".join([
        repo.description or "",
        " ".join(repo.topics),
    ]).lower()

    for capability_name, keywords in CAPABILITY_KEYWORDS.items():
        signals = []
        confidence = 0.0

        # 检查每个关键词
        for keyword in keywords:
            if keyword in all_text:
                signals.append(f"包含关键词: {keyword}")
                confidence += 0.15

        # 检查是否有官方 topic
        topic_match = capability_name.replace("_", "-") in " ".join(repo.topics).lower()
        if topic_match:
            signals.append("有对应 Topic标签")
            confidence += 0.2

        # 置信度上限
        confidence = min(confidence, 1.0)

        capabilities.append({
            "capability": capability_name,
            "detected": confidence >= 0.2,  # 至少检测到一个信号
            "confidence": confidence,
            "signals": signals,
            "maturity_score": min(int(confidence * 10), 10),  # 转换为0-10 分
        })

    return capabilities


def extract_model_support(repo: RepositoryInfo) -> list[str]:
    """提取支持的模型列表"""
    models = []
    all_text = " ".join([
        repo.description or "",
        " ".join(repo.topics),
    ]).lower()

    for model in KNOWN_MODELS:
        if model in all_text:
            # 标准化模型名称
            if "gpt" in model:
                models.append("GPT" if model == "gpt" else model.upper())
            elif "claude" in model:
                models.append("Claude" if model == "claude" else model.title())
            elif "qwen" in model:
                models.append("Qwen" if model == "qwen" else model.title())
            elif "deepseek" in model:
                models.append("DeepSeek" if model == "deepseek" else model.title())
            elif "gemini" in model:
                models.append("Gemini" if model == "gemini" else model.title())
            elif "llama" in model:
                models.append("Llama" if model == "llama" else model.title())
            elif "ollama" in model or "local" in model:
                models.append("Local LLM")
            elif "huggingface" in model:
                models.append("HuggingFace")

    # 去重并返回
    return list(set(models))[:10]  # 最多返回10个


def extract_deployment_methods(repo: RepositoryInfo) -> list[str]:
    """提取部署方式"""
    methods = []
    all_text = " ".join([
        repo.description or "",
        " ".join(repo.topics),
    ]).lower()

    deployment_keywords = {
        "docker": ["docker", "dockerfile", "container"],
        "kubernetes": ["kubernetes", "k8s", "helm"],
        "cloud": ["aws", "azure", "gcp", "cloud"],
        "serverless": ["serverless", "lambda", "vercel", "netlify"],
        "api": ["api", "fastapi", "flask", "express"],
        "saas": ["saas", "hosted", "managed"],
    }

    for method, keywords in deployment_keywords.items():
        if any(kw in all_text for kw in keywords):
            methods.append(method)

    return methods


def calculate_ai_maturity_score(repo: RepositoryInfo) -> AIMaturityScore:
    """计算 AI 成熟度评分

    仅当项目被识别为 AI Platform 类型时调用
    """
    # 检测 AI 能力
    capabilities = detect_ai_capabilities(repo)

    # 计算总分
    detected_capabilities = [c for c in capabilities if c["detected"]]
    if detected_capabilities:
        total_score = sum(c["maturity_score"] for c in detected_capabilities)
        # 归一化到 0-100 (7个能力，满分70，映射到100)
        total_score = min(int(total_score / 7 * 100), 100)
    else:
        total_score = 0

    # 提取支持的模型
    model_support = extract_model_support(repo)

    # 提取部署方式
    deployment_methods = extract_deployment_methods(repo)

    return AIMaturityScore(
        is_ai_project=len(detected_capabilities) >= 1,
        total_score=total_score,
        capabilities=capabilities,
        model_support=model_support,
        deployment_methods=deployment_methods,
    )