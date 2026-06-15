from pydantic import BaseModel, Field


class ScoreTrendItem(BaseModel):
    date: str
    score: float
    grade: str | None = None


class SeverityCounts(BaseModel):
    critical: int
    high: int
    medium: int
    low: int


class RecentScanItem(BaseModel):
    scanId: str
    targetUrl: str
    grade: str | None = None
    createdAt: str


class ScanQuotaInfo(BaseModel):
    used: int
    limit: int


class DashboardSummaryResponse(BaseModel):
    scoreTrend: list[ScoreTrendItem]
    severityCounts: SeverityCounts
    recentScans: list[RecentScanItem]
    scanQuota: ScanQuotaInfo
