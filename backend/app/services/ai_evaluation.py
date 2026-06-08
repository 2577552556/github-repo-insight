import httpx

from app.core.config import settings
from app.schemas.analyze import RepositoryInfo, LanguageDistribution, AIScore


class AIEvaluationService:
    """Service for AI-powered repository evaluation."""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.api_url = f"{settings.OPENAI_API_URL}/chat/completions"

    async def evaluate(
        self, repository: RepositoryInfo, languages: LanguageDistribution
    ) -> AIScore:
        """Evaluate repository and return AI score.

        If OPENAI_API_KEY is set, use OpenAI API.
        Otherwise, use rule-based fallback.
        """
        if self.api_key:
            return await self._evaluate_with_openai(repository, languages)
        return self._evaluate_with_rules(repository, languages)

    async def _evaluate_with_openai(
        self, repository: RepositoryInfo, languages: LanguageDistribution
    ) -> AIScore:
        """Evaluate using OpenAI API."""
        prompt = self._build_prompt(repository, languages)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a repository evaluation expert. Evaluate GitHub repositories and provide scores.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(self.api_url, json=payload, headers=headers)
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    return self._parse_openai_response(content, repository, languages)
                else:
                    return self._evaluate_with_rules(repository, languages)
        except (httpx.TimeoutException, httpx.RequestError):
            return self._evaluate_with_rules(repository, languages)

    def _build_prompt(
        self, repository: RepositoryInfo, languages: LanguageDistribution
    ) -> str:
        """Build evaluation prompt for OpenAI."""
        lang_str = ", ".join(
            f"{lang} ({pct}%)" for lang, pct in languages.languages.items()
        )
        return f"""Evaluate this GitHub repository and provide a score (0-100), grade (A-F), and summary.

Repository: {repository.full_name}
Description: {repository.description or "No description"}
Stars: {repository.stars}
Forks: {repository.forks}
Open Issues: {repository.open_issues}
Language: {repository.language or "Not specified"}
Last Updated: {repository.updated_at}
Default Branch: {repository.default_branch}

Languages: {lang_str if lang_str else "Not available"}

Provide your response in the following format:
Score: [0-100]
Grade: [A-F]
Summary: [2-3 sentence evaluation]

Scoring Standards:
- A (85-100): Excellent - Highly popular, actively maintained, strong community
- B (70-84): Good - Well maintained with decent community engagement
- C (50-69): Average - Moderate activity and community
- D (30-49): Below Average - Low activity or community
- F (0-29): Poor - New, abandoned, or minimal engagement"""

    def _parse_openai_response(
        self, content: str, repository: RepositoryInfo, languages: LanguageDistribution
    ) -> AIScore:
        """Parse OpenAI response into AIScore."""
        score = 50
        grade = "C"
        summary = content

        lines = content.split("\n")
        for line in lines:
            if line.startswith("Score:"):
                try:
                    score = int(line.split(":")[1].strip())
                except (ValueError, IndexError):
                    pass
            elif line.startswith("Grade:"):
                try:
                    grade = line.split(":")[1].strip()[0].upper()
                    if grade not in "ABCDEF":
                        grade = "C"
                except (ValueError, IndexError):
                    pass

        score = max(0, min(100, score))

        return AIScore(score=score, grade=grade, summary=summary)

    def _evaluate_with_rules(
        self, repository: RepositoryInfo, languages: LanguageDistribution
    ) -> AIScore:
        """Rule-based evaluation fallback."""
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

        return AIScore(
            score=score,
            grade=grade,
            summary=f"Repository '{repository.full_name}' has {stars} stars and {forks} forks. "
            f"Uses {language_count} programming languages. "
            f"Overall assessment: {'Excellent' if score >= 85 else 'Good' if score >= 70 else 'Average' if score >= 50 else 'Below Average' if score >= 30 else 'Needs attention'}.",
        )


ai_evaluation_service = AIEvaluationService()