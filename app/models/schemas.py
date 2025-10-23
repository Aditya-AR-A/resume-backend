from pydantic import BaseModel, Field, model_validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


# ============================================================================
# BASE MODELS & COMMON SCHEMAS
# ============================================================================

class APIResponse(BaseModel):
    """Base API response model with standardized structure"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    meta: Optional[Dict[str, Any]] = None


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    total_count: int
    limit: int
    offset: int
    has_more: bool


class FilterOptions(BaseModel):
    """Common filter options"""
    skills: Optional[List[str]] = None
    featured: Optional[bool] = None
    category: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class CacheHeaders(BaseModel):
    """Cache control headers"""
    cache_control: Optional[str] = None
    etag: Optional[str] = None
    last_modified: Optional[str] = None


# ============================================================================
# DATA MODELS - STRUCTURED SCHEMAS
# ============================================================================

class SocialLinks(BaseModel):
    """Structured social/contact links"""
    email: str
    github: str
    linkedin: str
    additional: Optional[Dict[str, str]] = None


class IntroData(BaseModel):
    """Introduction/Profile data model"""
    profileImage: Optional[Dict[str, str]] = None
    name: str
    title: str
    about: str
    socialLinks: SocialLinks
    styles: Optional[Dict[str, Any]] = None


class JobData(BaseModel):
    """Job/Work experience data model"""
    id: str
    title: str
    company: str
    companyLogo: Optional[str] = None
    position: str
    location: str
    startDate: str
    endDate: Optional[str] = None
    isCurrent: bool = False
    description: str
    responsibilities: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    achievements: Optional[List[str]] = None
    links: Optional[Dict[str, str]] = None
    featured: bool = False
    projectIds: List[str] = Field(default_factory=list)


class AssetDisplayMode(str, Enum):
    """Rendering behaviour for embedded assets"""

    SCROLLABLE = "scrollable"
    UNSCROLLABLE = "unscrollable"


class ProjectAsset(BaseModel):
    """Metadata describing a tangible project asset or attachment"""

    title: str
    file: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    sourceUrl: Optional[str] = None
    automated: bool = False
    displayMode: Optional[AssetDisplayMode] = None
    embedCode: Optional[str] = None


class ProjectData(BaseModel):
    """Project data model"""
    id: str
    name: str
    type: str
    description: str
    shortDescription: Optional[str] = None
    thumbnail: Optional[str] = None
    category: str
    featured: bool = False
    startDate: str
    endDate: Optional[str] = None
    status: str
    skills: List[str]
    jobId: Optional[str] = None
    relatedJobIds: List[str] = Field(default_factory=list)
    links: Optional[Dict[str, str]] = None
    demoUrl: Optional[str] = None
    githubUrl: Optional[str] = None
    demo: Optional[Dict[str, Any]] = None
    model: Optional[Dict[str, Any]] = None
    research: Optional[Dict[str, Any]] = None
    highlights: List[str] = Field(default_factory=list)
    metrics: Optional[Dict[str, str]] = None
    assets: Optional[Dict[str, List["ProjectAsset"]]] = None

    @model_validator(mode="before")
    @classmethod
    def _normalize_links(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        links = values.get("links")
        # Allow list-form links but convert to simple dict for consistency
        if isinstance(links, list):
            link_map: Dict[str, str] = {}
            for item in links:
                if not isinstance(item, dict):
                    continue
                link_type = item.get("type") or item.get("label")
                url = item.get("url")
                if link_type and url:
                    link_map[str(link_type).lower()] = str(url)
            values["links"] = link_map or None
            links = values.get("links")

        if isinstance(links, dict):
            demo_fallbacks = [
                "demo",
                "live",
                "marketplace",
                "notebook",
                "preview",
                "article"
            ]
            for key in demo_fallbacks:
                if not values.get("demoUrl") and links.get(key):
                    values["demoUrl"] = links.get(key)
            if not values.get("githubUrl") and links.get("source"):
                values["githubUrl"] = links.get("source")
            values.setdefault("githubUrl", links.get("github"))

        return values


class CertificateData(BaseModel):
    """Certificate data model"""
    name: str
    file: str
    provider: str
    field: str
    skills: List[str]
    issueDate: Optional[str] = None
    expiryDate: Optional[str] = None
    credentialId: Optional[str] = None
    credentialUrl: Optional[str] = None
    description: Optional[str] = None
    featured: bool = False


class ContactLink(BaseModel):
    """Contact or social link displayed in layout/footer"""
    platform: str
    url: str
    className: Optional[str] = None
    icon: Optional[str] = None


class LayoutData(BaseModel):
    """Layout configuration model"""
    metadata: Optional[Dict[str, Any]] = None
    footer: Optional[Dict[str, Any]] = None
    viewport: Optional[Dict[str, Any]] = None
    contact: Optional[List[ContactLink]] = None
    sections: Optional[List[str]] = None
    theme: Optional[str] = None
    animations: Optional[Dict[str, Any]] = None


class PageData(BaseModel):
    """Page configuration model"""
    title: str
    meta: Dict[str, Any]
    scripts: Optional[List[str]] = None
    stylesheets: Optional[List[str]] = None


# ============================================================================
# UNIFIED SEARCH & AGGREGATION MODELS
# ============================================================================

class SearchSection(BaseModel):
    """Search result section"""
    type: str  # "projects", "jobs", "certificates", "skills"
    items: List[Dict[str, Any]]
    count: int
    highlights: Optional[List[Dict[str, Any]]] = None


class SearchResultItem(BaseModel):
    """Flattened search result item with type metadata"""
    type: str
    data: Dict[str, Any]


class SearchSummary(BaseModel):
    """LLM-generated search summary"""
    title: str
    body: str
    highlights: Optional[Dict[str, List[str]]] = None


class UnifiedSearchResponse(BaseModel):
    """Unified search response with sections"""
    query: str
    sections: List[SearchSection]
    total_count: int
    search_time: float
    suggestions: Optional[List[str]] = None


class SkillAggregation(BaseModel):
    """Skill aggregation data"""
    skill: str
    count: int
    categories: List[str]
    proficiency: Optional[str] = None
    projects: List[str]
    jobs: List[str]
    certificates: List[str]


class SkillsResponse(BaseModel):
    """Skills aggregation response"""
    skills: List[SkillAggregation]
    categories: List[str]
    total_unique_skills: int


class TimelineItem(BaseModel):
    """Timeline item combining jobs and certificates"""
    id: str
    type: str  # "job" or "certificate"
    title: str
    organization: str
    date: str
    endDate: Optional[str] = None
    isCurrent: bool = False
    description: str
    skills: List[str]


class TimelineResponse(BaseModel):
    """Timeline response"""
    items: List[TimelineItem]
    total_count: int


class StatsSummary(BaseModel):
    """Portfolio statistics summary"""
    total_projects: int
    total_jobs: int
    total_certificates: int
    total_skills: int
    featured_projects: int
    current_position: Optional[str] = None
    years_experience: Optional[int] = None
    top_skills: List[str]
    categories: Dict[str, int]


# ============================================================================
# LLM AGENT MODELS - MULTI-PHASE SYSTEM
# ============================================================================

class MessageType(str, Enum):
    """Message classification types"""
    QUESTION = "question"
    SEARCH_REQUEST = "search_request"
    STATEMENT = "statement"
    COMMAND = "command"
    CONVERSATION = "conversation"


class MessageClassification(BaseModel):
    """Message classification result"""
    message_type: MessageType
    confidence: float = Field(ge=0.0, le=1.0)
    keywords: List[str]
    intent: str
    entities: Dict[str, Any]
    processing_time: float


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    GROQ = "groq"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class LLMConfig(BaseModel):
    """LLM provider configuration"""
    provider: LLMProvider
    api_key: Optional[str] = None
    model: str
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, gt=0)
    base_url: Optional[str] = None
    timeout: int = Field(default=30, gt=0)


class LLMRequest(BaseModel):
    """LLM request model"""
    message: str
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMResponse(BaseModel):
    """LLM response model"""
    response: str
    provider: LLMProvider
    model: str
    confidence: float = Field(ge=0.0, le=1.0)
    sources: Optional[List[Dict[str, Any]]] = None
    suggestions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    processing_time: float
    tokens_used: Optional[int] = None


class AgentPhase(str, Enum):
    """LLM Agent processing phases"""
    CATEGORIZATION = "categorization"
    RESPONSE_GENERATION = "response_generation"
    VALIDATION = "validation"
    IMPLEMENTATION = "implementation"


class AgentStep(BaseModel):
    """Individual agent processing step"""
    phase: AgentPhase
    input: Dict[str, Any]
    output: Dict[str, Any]
    success: bool
    processing_time: float
    error: Optional[str] = None


class AgentExecution(BaseModel):
    """Complete agent execution trace"""
    request: LLMRequest
    classification: MessageClassification
    steps: List[AgentStep]
    final_response: LLMResponse
    total_time: float
    success: bool


# ============================================================================
# AI SYSTEM MODELS
# ============================================================================

class AIRequest(BaseModel):
    """Enhanced AI request model"""
    message: str
    context: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    provider: Optional[LLMProvider] = None


class AIResponse(BaseModel):
    """Enhanced AI response model"""
    response: str
    message_type: MessageType
    confidence: float
    sources: Optional[List[Dict[str, Any]]] = None
    suggestions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    processing_time: float
    provider: LLMProvider
    model: str


class SearchRequest(BaseModel):
    """Search request model"""
    query: str
    search_type: str = "general"
    filters: Optional[FilterOptions] = None
    limit: int = Field(default=10, gt=0, le=100)
    offset: int = Field(default=0, ge=0)
    include_sections: List[str] = Field(default_factory=lambda: ["projects", "jobs", "certificates"])


class SearchResult(BaseModel):
    """Search result model"""
    items: List[SearchResultItem]
    total_count: int
    search_time: float
    query: str
    search_type: str
    pagination: PaginationMeta
    summary: Optional[SearchSummary] = None
    sections: Optional[List[SearchSection]] = None
    llm_response: Optional[str] = None
    intent: Optional[str] = None


class QuestionAnsweringRequest(BaseModel):
    """Question answering request model"""
    question: str
    context: Optional[str] = None
    domain: str = "portfolio"


class QuestionAnsweringResponse(BaseModel):
    """Question answering response model"""
    answer: str
    confidence: float
    sources: List[Dict[str, Any]]
    related_questions: Optional[List[str]] = None
    processing_time: float


# ============================================================================
# CONFIGURATION MODELS
# ============================================================================

class AppConfig(BaseModel):
    """Application configuration"""
    name: str = "Resume Backend API"
    version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False


class DatabaseConfig(BaseModel):
    """Database configuration"""
    url: str = "sqlite:///./resume.db"
    pool_size: int = 10
    max_overflow: int = 20


class CacheConfig(BaseModel):
    """Cache configuration"""
    enabled: bool = True
    ttl: int = 3600
    max_size: int = 1000


class AIConfig(BaseModel):
    """AI system configuration"""
    primary_provider: LLMProvider = LLMProvider.GROQ
    providers: Dict[LLMProvider, LLMConfig]
    enable_caching: bool = True
    cache_ttl: int = 3600
    max_retries: int = 3
    timeout: int = 30


class Settings(BaseModel):
    """Main application settings"""
    app: AppConfig
    database: DatabaseConfig
    cache: CacheConfig
    ai: AIConfig


# ============================================================================
# ERROR MODELS
# ============================================================================

class ErrorDetail(BaseModel):
    """Error detail model"""
    field: str
    message: str
    error_code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standardized error response"""
    success: bool = False
    error: str
    error_code: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None


# ============================================================================
# HEALTH & STATUS MODELS
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    version: str
    uptime: Optional[float] = None


class AIStatusResponse(BaseModel):
    """AI system status response"""
    status: str
    components: Dict[str, str]
    providers: Dict[str, bool]
    timestamp: datetime = Field(default_factory=datetime.now)


# ============================================================================
# PAGINATED RESPONSE MODELS
# ============================================================================

class PaginatedProjectsResponse(BaseModel):
    """Paginated projects response"""
    data: List[ProjectData]
    pagination: PaginationMeta
    filters: Optional[FilterOptions] = None


class PaginatedJobsResponse(BaseModel):
    """Paginated jobs response"""
    data: List[JobData]
    pagination: PaginationMeta
    filters: Optional[FilterOptions] = None


class PaginatedCertificatesResponse(BaseModel):
    """Paginated certificates response"""
    data: List[CertificateData]
    pagination: PaginationMeta
    filters: Optional[FilterOptions] = None
