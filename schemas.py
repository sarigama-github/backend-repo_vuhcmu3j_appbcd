"""
Database Schemas for Ben Venturing

Each Pydantic model corresponds to a MongoDB collection with the
collection name as the lowercase of the class name.

Examples:
- Course -> "course"
- PortfolioItem -> "portfolioitem"
- Inquiry -> "inquiry"
"""
from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl


# ---------------------------------------------
# Core Content Schemas
# ---------------------------------------------
class Lesson(BaseModel):
    id: str = Field(...)
    title: str = Field(...)
    type: Optional[Literal["video", "article", "quiz", "assignment", "live", "other"]] = Field(
        default=None
    )
    duration: Optional[str] = Field(
        default=None, description="Human-readable duration, e.g., '8m' or '1h 15m'"
    )


class Module(BaseModel):
    id: str
    title: str
    lessons: List[Lesson] = Field(default_factory=list)


class Course(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    price: Optional[str] = None
    modules: List[Module] = Field(default_factory=list)
    instructor: Optional[str] = None
    slug: str
    thumbnail: Optional[HttpUrl | str] = None


class PortfolioItem(BaseModel):
    id: str
    title: str
    category: str
    client: Optional[str] = None
    date: Optional[str] = None
    media: List[str] = Field(default_factory=list)
    caseStudyText: Optional[str] = None
    metrics: Optional[dict] = None
    slug: str


class Inquiry(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    projectType: Optional[str] = None
    budget: Optional[str] = None
    message: Optional[str] = None
    date: Optional[str] = None
    status: Optional[str] = Field(default="new")


# Optional: simple email capture for chatbot
class Lead(BaseModel):
    email: str
    source: Optional[str] = Field(default="chatbot")
    note: Optional[str] = None
