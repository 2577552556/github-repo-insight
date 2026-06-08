from fastapi import HTTPException


class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)


class InvalidURLError(AppException):
    def __init__(self, detail: str = "Invalid GitHub URL format"):
        super().__init__(status_code=400, detail=detail)


class RepositoryNotFoundError(AppException):
    def __init__(self, detail: str = "Repository not found"):
        super().__init__(status_code=404, detail=detail)


class RateLimitError(AppException):
    def __init__(self, detail: str = "GitHub API rate limit exceeded"):
        super().__init__(status_code=429, detail=detail)


class GitHubAPIError(AppException):
    def __init__(self, detail: str = "Failed to fetch repository data"):
        super().__init__(status_code=502, detail=detail)


class NetworkError(AppException):
    def __init__(self, detail: str = "Service temporarily unavailable"):
        super().__init__(status_code=503, detail=detail)


class InternalServerError(AppException):
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(status_code=500, detail=detail)