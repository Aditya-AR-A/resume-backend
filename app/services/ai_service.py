import asyncio
import json
import re
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.models.schemas import (
    MessageClassification, AIRequest, AIResponse, SearchRequest,
    SearchResult, QuestionAnsweringRequest, QuestionAnsweringResponse,
    AIStatusResponse, MessageType, LLMProvider, LLMConfig, LLMRequest,
    LLMResponse, AgentPhase, AgentStep, AgentExecution, PaginationMeta,
    SearchSection, SearchResultItem, SearchSummary
)
from app.services.data_service import DataService
from app.services.providers import LLMProviderManager, PromptManager
from app.config.settings import app_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MessageClassifier:
    """Enhanced message classifier with better accuracy"""

    @staticmethod
    def classify_message(message: str) -> MessageClassification:
        """Classify a message with improved accuracy"""
        message_lower = message.lower().strip()
        start_time = time.time()

        # Extract keywords
        keywords = MessageClassifier._extract_keywords(message)

        # Determine message type with improved logic
        message_type = MessageClassifier._determine_message_type(message_lower)

        # Determine intent
        intent = MessageClassifier._determine_intent(message_lower, message_type)

        # Extract entities
        entities = MessageClassifier._extract_entities(message, keywords)

        # Calculate confidence with better scoring
        confidence = MessageClassifier._calculate_confidence(message_lower, message_type, keywords)

        processing_time = time.time() - start_time

        return MessageClassification(
            message_type=message_type,
            confidence=confidence,
            keywords=keywords,
            intent=intent,
            entities=entities,
            processing_time=processing_time
        )

    @staticmethod
    def _determine_message_type(message: str) -> MessageType:
        """Determine message type with improved patterns"""
        # Question patterns
        question_patterns = [
            r'^(what|who|when|where|why|how|which|whose|whom)\s',
            r'\?$',
            r'^(tell me|explain|describe|can you|could you)',
            r'^(is|are|was|were|do|does|did|can|could|should|would|will)\s.*\?',
            r'^(find|search|get|show).*\?'
        ]

        # Search patterns
        search_patterns = [
            r'^(find|search|look for|get|show me|list|display)',
            r'^(filter|sort).*(by|with)',
            r'^(containing|related to|about|with skill)',
            r'\b(project|experience|certificate|skill|technology)\b'
        ]

        # Command patterns
        command_patterns = [
            r'^(update|change|modify|edit|delete|remove|add|create)',
            r'^(set|configure|enable|disable)',
            r'^(start|stop|restart|run|execute)'
        ]

        # Check patterns in order of specificity
        for pattern in question_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return MessageType.QUESTION

        for pattern in search_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return MessageType.SEARCH_REQUEST

        for pattern in command_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return MessageType.COMMAND

        return MessageType.CONVERSATION

    @staticmethod
    def _determine_intent(message: str, message_type: MessageType) -> str:
        """Determine specific intent"""
        if message_type == MessageType.QUESTION:
            if any(word in message for word in ["project", "work", "portfolio", "application"]):
                return "project_inquiry"
            elif any(word in message for word in ["experience", "job", "work", "career"]):
                return "experience_inquiry"
            elif any(word in message for word in ["certificate", "certification", "course"]):
                return "certificate_inquiry"
            elif any(word in message for word in ["skill", "technology", "language", "framework"]):
                return "skill_inquiry"
            elif any(word in message for word in ["contact", "email", "phone", "reach"]):
                return "contact_inquiry"
            else:
                return "general_inquiry"

        elif message_type == MessageType.SEARCH_REQUEST:
            if "project" in message:
                return "search_projects"
            elif any(word in message for word in ["experience", "job"]):
                return "search_experience"
            elif "certificate" in message:
                return "search_certificates"
            elif "skill" in message:
                return "search_skills"
            else:
                return "general_search"

        elif message_type == MessageType.COMMAND:
            return "system_command"

        else:
            return "general_conversation"

    @staticmethod
    def _extract_keywords(message: str) -> List[str]:
        """Extract keywords with improved logic"""
        portfolio_keywords = [
            "project", "projects", "experience", "job", "work", "certificate",
            "certificates", "skill", "skills", "education", "contact", "email",
            "phone", "github", "linkedin", "website", "portfolio", "resume",
            "technology", "framework", "language", "tool", "database", "api",
            "web", "mobile", "data", "science", "machine", "learning", "ai",
            "artificial", "intelligence", "deep", "neural", "network"
        ]

        keywords = []
        message_lower = message.lower()

        # Extract exact matches
        for keyword in portfolio_keywords:
            if keyword in message_lower:
                keywords.append(keyword)

        # Extract technology names
        technologies = [
            "python", "javascript", "typescript", "react", "vue", "angular",
            "node", "express", "fastapi", "django", "flask", "postgresql",
            "mysql", "mongodb", "redis", "docker", "kubernetes", "aws",
            "gcp", "azure", "tensorflow", "pytorch", "scikit", "pandas",
            "numpy", "matplotlib", "seaborn", "plotly"
        ]

        for tech in technologies:
            if tech in message_lower:
                keywords.append(tech)

        return list(set(keywords))

    @staticmethod
    def _extract_entities(message: str, keywords: List[str]) -> Dict[str, Any]:
        """Extract entities with improved logic"""
        entities = {}

        # Extract technology names
        technologies = [
            "python", "javascript", "react", "node", "fastapi", "django",
            "postgresql", "mongodb", "docker", "kubernetes", "aws", "gcp",
            "tensorflow", "pytorch", "scikit", "pandas", "numpy"
        ]

        found_tech = [tech for tech in technologies if tech.lower() in message.lower()]
        if found_tech:
            entities["technologies"] = found_tech

        # Extract years
        years = re.findall(r'\b(19|20)\d{2}\b', message)
        if years:
            entities["years"] = years

        # Extract email-like patterns
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', message)
        if emails:
            entities["emails"] = emails

        return entities

    @staticmethod
    def _calculate_confidence(message: str, message_type: MessageType, keywords: List[str]) -> float:
        """Calculate confidence with improved scoring"""
        confidence = 0.5  # Base confidence

        # Increase confidence based on clear patterns
        if message.endswith("?"):
            confidence += 0.3
        if any(message.startswith(word) for word in ["what", "who", "when", "where", "why", "how"]):
            confidence += 0.2
        if any(word in message.lower() for word in ["find", "search", "get", "show", "list"]):
            confidence += 0.2

        # Increase confidence based on keywords
        if keywords:
            confidence += min(len(keywords) * 0.1, 0.3)

        # Increase confidence for clear question words
        question_words = ["what", "who", "when", "where", "why", "how", "which", "whose", "whom"]
        if any(word in message.lower() for word in question_words):
            confidence += 0.2

        return min(confidence, 1.0)


class LLMAgent:
    """Multi-phase LLM Agent for processing requests"""

    def __init__(self):
        self.provider_manager = LLMProviderManager()
        self.prompt_manager = PromptManager()
        self.classifier = MessageClassifier()
        self.data_service = DataService()

        # Initialize providers from settings
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize LLM providers from settings"""
        # Initialize Groq provider
        if hasattr(app_settings, 'groq_api_key') and app_settings.groq_api_key:
            groq_config = LLMConfig(
                provider=LLMProvider.GROQ,
                api_key=app_settings.groq_api_key,
                model="llama3-8b-8192",  # Updated to current Groq model
                temperature=0.7,
                max_tokens=1024
            )
            self.provider_manager.add_provider(groq_config)

        # Initialize OpenAI provider
        if hasattr(app_settings, 'openai_api_key') and app_settings.openai_api_key:
            openai_config = LLMConfig(
                provider=LLMProvider.OPENAI,
                api_key=app_settings.openai_api_key,
                model="gpt-3.5-turbo",
                temperature=0.7,
                max_tokens=1024
            )
            self.provider_manager.add_provider(openai_config)

        # Initialize Anthropic provider
        if hasattr(app_settings, 'anthropic_api_key') and app_settings.anthropic_api_key:
            anthropic_config = LLMConfig(
                provider=LLMProvider.ANTHROPIC,
                api_key=app_settings.anthropic_api_key,
                model="claude-3-sonnet-20240229",
                temperature=0.7,
                max_tokens=1024
            )
            self.provider_manager.add_provider(anthropic_config)

    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process request through multi-phase LLM agent"""
        start_time = time.time()

        # Phase 1: Categorization
        categorization_step = await self._phase_categorization(request)

        # Phase 2: Response Generation
        generation_step = await self._phase_response_generation(request, categorization_step)

        # Phase 3: Validation
        validation_step = await self._phase_validation(generation_step)

        # Phase 4: Implementation
        implementation_step = await self._phase_implementation(validation_step)

        # Create execution trace
        execution = AgentExecution(
            request=LLMRequest(
                message=request.message,
                context=request.context,
                user_id=request.user_id,
                session_id=request.session_id,
                metadata=request.metadata
            ),
            classification=categorization_step["classification"],
            steps=[
                AgentStep(
                    phase=AgentPhase.CATEGORIZATION,
                    input={"message": request.message},
                    output=categorization_step,
                    success=True,
                    processing_time=categorization_step["processing_time"]
                ),
                AgentStep(
                    phase=AgentPhase.RESPONSE_GENERATION,
                    input={"message": request.message, "classification": categorization_step},
                    output=generation_step,
                    success=True,
                    processing_time=generation_step["processing_time"]
                ),
                AgentStep(
                    phase=AgentPhase.VALIDATION,
                    input={"response": generation_step["response"]},
                    output=validation_step,
                    success=True,
                    processing_time=validation_step["processing_time"]
                ),
                AgentStep(
                    phase=AgentPhase.IMPLEMENTATION,
                    input={"validated_response": validation_step["validated_response"]},
                    output=implementation_step,
                    success=True,
                    processing_time=implementation_step["processing_time"]
                )
            ],
            final_response=implementation_step["llm_response"],
            total_time=time.time() - start_time,
            success=True
        )

        # Log execution for debugging
        logger.info(f"Agent execution completed in {execution.total_time:.2f}s")

        # Return final response
        final_response = implementation_step["llm_response"]
        return AIResponse(
            response=final_response.response,
            message_type=execution.classification.message_type,
            confidence=final_response.confidence,
            sources=final_response.sources,
            suggestions=final_response.suggestions,
            metadata={
                "agent_execution": execution.dict(),
                "provider": final_response.provider.value,
                "model": final_response.model,
                "processing_time": final_response.processing_time
            },
            processing_time=execution.total_time,
            provider=final_response.provider,
            model=final_response.model
        )

    async def _phase_categorization(self, request: AIRequest) -> Dict[str, Any]:
        """Phase 1: Categorize and classify the message"""
        start_time = time.time()

        classification = self.classifier.classify_message(request.message)

        return {
            "classification": classification,
            "processing_time": time.time() - start_time
        }

    async def _phase_response_generation(self, request: AIRequest, categorization: Dict) -> Dict[str, Any]:
        """Phase 2: Generate response based on classification"""
        start_time = time.time()
        classification = categorization["classification"]

        # Create context-aware prompt
        prompt = self._create_prompt(request, classification)

        # Generate response using LLM
        llm_response = await self.provider_manager.generate_response(
            prompt,
            preferred_provider=request.provider
        )

        return {
            "response": llm_response.response,
            "llm_response": llm_response,
            "processing_time": time.time() - start_time
        }

    async def _phase_validation(self, generation: Dict) -> Dict[str, Any]:
        """Phase 3: Validate the generated response"""
        start_time = time.time()

        response = generation["response"]
        llm_response = generation["llm_response"]

        # Basic validation - check if response is meaningful
        is_valid = len(response.strip()) > 10 and not response.isspace()

        # If response is too short or empty, generate a fallback
        if not is_valid:
            fallback_prompt = "Please provide a helpful response about the portfolio."
            llm_response = await self.provider_manager.generate_response(fallback_prompt)
            response = llm_response.response

        return {
            "validated_response": response,
            "llm_response": llm_response,
            "is_valid": is_valid,
            "processing_time": time.time() - start_time
        }

    async def _phase_implementation(self, validation: Dict) -> Dict[str, Any]:
        """Phase 4: Final implementation and formatting"""
        start_time = time.time()

        # Get validated response
        response = validation["validated_response"]
        llm_response = validation["llm_response"]

        # Add sources if this was a search/question
        sources = []
        if "search" in response.lower() or "project" in response.lower():
            # Add relevant data sources
            sources = [
                {"type": "projects", "count": len(self.data_service.get_projects_data())},
                {"type": "experience", "count": len(self.data_service.get_jobs_data())},
                {"type": "certificates", "count": len(self.data_service.get_certificates_data())}
            ]

        # Update LLM response with sources
        llm_response.sources = sources

        return {
            "llm_response": llm_response,
            "processing_time": time.time() - start_time
        }

    def _create_prompt(self, request: AIRequest, classification: MessageClassification) -> str:
        """Create context-aware prompt for LLM using PromptManager"""
        # Get base context
        base_context = self.prompt_manager.get_base_context(
            message_type=classification.message_type.value,
            intent=classification.intent,
            keywords=', '.join(classification.keywords),
            entities=classification.entities,
            user_message=request.message
        )

        # Add specific context based on message type and intent
        if classification.message_type == MessageType.QUESTION:
            if "project" in classification.intent:
                projects = self.data_service.get_projects_data()
                project_context = self.prompt_manager.get_prompt("question_project",
                    project_count=len(projects),
                    project_categories=set(p.category for p in projects),
                    featured_projects=[p.name for p in projects if p.featured]
                )
                base_context += "\n" + project_context

            elif "experience" in classification.intent:
                jobs = self.data_service.get_jobs_data()
                experience_context = self.prompt_manager.get_prompt("question_experience",
                    job_count=len(jobs),
                    current_position=next((j.title for j in jobs if j.isCurrent), 'N/A')
                )
                base_context += "\n" + experience_context

            elif "certificate" in classification.intent:
                certificates = self.data_service.get_certificates_data()
                certificate_context = self.prompt_manager.get_prompt("question_certificate",
                    certificate_count=len(certificates),
                    certificate_fields=set(c.field for c in certificates)
                )
                base_context += "\n" + certificate_context

        elif classification.message_type == MessageType.SEARCH_REQUEST:
            search_context = self.prompt_manager.get_prompt("search_request")
            base_context += "\n" + search_context

        # Add fallback prompt
        base_context += "\n" + self.prompt_manager.get_fallback_prompt()

        return base_context


class EnhancedAIService:
    """Enhanced AI service with LLM agent integration"""

    def __init__(self):
        self.agent = LLMAgent()
        self.classifier = MessageClassifier()
        self.data_service = DataService()

    async def process_request(self, request: AIRequest) -> AIResponse:
        """Process AI request using LLM agent"""
        return await self.agent.process_request(request)

    async def semantic_search(self, request: SearchRequest) -> SearchResult:
        """Perform semantic search backed by portfolio data and LLM summarization"""
        start_time = time.time()

        classification = self.classifier.classify_message(request.query)

        unified_result = self.data_service.unified_search(
            query=request.query,
            include_sections=request.include_sections,
            limit=request.limit
        )

        priority_order = request.include_sections or ["projects", "jobs", "certificates"]
        priority_index = {section: idx for idx, section in enumerate(priority_order)}

        ordered_sections: List[SearchSection] = sorted(
            unified_result.sections,
            key=lambda section: priority_index.get(section.type, len(priority_order))
        ) if unified_result.sections else []

        aggregated_items = self._flatten_sections_to_items(ordered_sections)
        total_count = len(aggregated_items)

        fallback_used = False
        if total_count == 0:
            per_section_limit = min(3, max(1, request.limit))
            fallback_sections = self._build_fallback_sections(
                include_sections=request.include_sections,
                per_section_limit=per_section_limit
            )
            if fallback_sections:
                ordered_sections = sorted(
                    fallback_sections,
                    key=lambda section: priority_index.get(section.type, len(priority_order))
                )
                aggregated_items = self._flatten_sections_to_items(ordered_sections)
                total_count = len(aggregated_items)
                fallback_used = total_count > 0
                if fallback_used:
                    logger.debug("Using global fallback sections for query '%s'", request.query)

        safe_offset = min(request.offset, total_count)
        end_index = min(total_count, safe_offset + request.limit)
        paginated_items = aggregated_items[safe_offset:end_index]

        pagination = PaginationMeta(
            total_count=total_count,
            limit=request.limit,
            offset=safe_offset,
            has_more=end_index < total_count
        )

        is_navigation_query = self._is_navigation_query(request.query, classification)

        summary_payload: Optional[SearchSummary] = None
        llm_response: Optional[str] = None
        resolved_search_type = "navigation" if is_navigation_query else "information"

        if is_navigation_query:
            summary_payload = await self._build_navigation_summary(
                query=request.query,
                sections=ordered_sections
            )
        else:
            llm_response = await self._build_information_answer(
                query=request.query,
                sections=ordered_sections,
                include_global_profile=fallback_used
            )

        search_time = time.time() - start_time

        return SearchResult(
            items=paginated_items,
            total_count=total_count,
            search_time=search_time,
            query=request.query,
            search_type=resolved_search_type,
            pagination=pagination,
            summary=summary_payload,
            sections=ordered_sections,
            llm_response=llm_response,
            intent=classification.intent
        )

    def _is_navigation_query(self, query: str, classification: MessageClassification) -> bool:
        nav_intents = {
            "search_projects",
            "search_experience",
            "search_certificates",
            "search_skills",
            "general_search",
        }

        if classification.message_type == MessageType.SEARCH_REQUEST:
            return True

        if classification.intent in nav_intents:
            return True

        lowered = query.lower().strip()

        if classification.message_type == MessageType.COMMAND and any(
            keyword in lowered for keyword in ("show", "open", "go to", "goto", "take me", "view", "list")
        ):
            return True

        if lowered.startswith(("show ", "open ", "view ", "list ", "see ", "go to ", "goto ")):
            return True

        section_terms = {
            "project", "projects", "experience", "job", "jobs",
            "certificate", "certificates", "skill", "skills",
            "contact", "about"
        }
        tokens = lowered.split()
        if 0 < len(tokens) <= 3 and any(term in section_terms for term in tokens):
            return True

        return False

    @staticmethod
    def _flatten_sections_to_items(sections: List[SearchSection]) -> List[SearchResultItem]:
        flattened: List[SearchResultItem] = []

        for section in sections:
            if not section.items:
                continue
            for item in section.items:
                flattened.append(SearchResultItem(type=section.type, data=item))

        return flattened

    def _build_fallback_sections(
        self,
        include_sections: Optional[List[str]],
        per_section_limit: int = 3
    ) -> List[SearchSection]:
        sections: List[SearchSection] = []
        include_sections = include_sections or ["projects", "jobs", "certificates"]
        per_section_limit = max(1, per_section_limit)

        if "projects" in include_sections:
            try:
                projects = self.data_service.get_new_projects_data()
                if not projects:
                    projects = self.data_service.get_projects_data()
                projects_sorted = sorted(
                    projects,
                    key=lambda project: (not project.featured, project.name.lower())
                ) if projects else []
                project_items = [project.dict() for project in projects_sorted[:per_section_limit]]
                if project_items:
                    sections.append(SearchSection(
                        type="projects",
                        items=project_items,
                        count=len(project_items)
                    ))
            except Exception as exc:
                logger.debug("Fallback projects load failed: %s", exc)

        if "jobs" in include_sections:
            try:
                jobs = self.data_service.get_jobs_data()
                if jobs:
                    current_jobs = [job for job in jobs if job.isCurrent]
                    past_jobs = [job for job in jobs if not job.isCurrent]
                    jobs_sequence = current_jobs + past_jobs
                    job_items = [job.dict() for job in jobs_sequence[:per_section_limit]]
                    if job_items:
                        sections.append(SearchSection(
                            type="jobs",
                            items=job_items,
                            count=len(job_items)
                        ))
            except Exception as exc:
                logger.debug("Fallback jobs load failed: %s", exc)

        if "certificates" in include_sections:
            try:
                certificates = self.data_service.get_certificates_data()
                certificate_items = [certificate.dict() for certificate in certificates[:per_section_limit]]
                if certificate_items:
                    sections.append(SearchSection(
                        type="certificates",
                        items=certificate_items,
                        count=len(certificate_items)
                    ))
            except Exception as exc:
                logger.debug("Fallback certificates load failed: %s", exc)

        return sections

    def _extract_section_context(
        self,
        sections: List[SearchSection],
        per_section_limit: int = 3,
    ) -> Tuple[List[str], Dict[str, List[str]]]:
        context_lines: List[str] = []
        highlights: Dict[str, List[str]] = {}

        for section in sections:
            if not section.items:
                continue

            highlights.setdefault(section.type, [])
            for item in section.items[:per_section_limit]:
                label = section.type
                if label == "projects":
                    name = item.get("name") or item.get("title") or "Unnamed project"
                    description = item.get("shortDescription") or item.get("description") or ""
                    skills = ", ".join(item.get("skills", [])[:6])
                    context_lines.append(
                        f"Project — {name}: {description}. Skills: {skills}".strip()
                    )
                    if name:
                        highlights[label].append(name)
                elif label == "jobs":
                    title = item.get("title") or "Role"
                    company = item.get("company") or ""
                    summary = item.get("description", "")
                    skills = ", ".join(item.get("skills", [])[:6])
                    context_lines.append(
                        f"Experience — {title} at {company}: {summary}. Skills: {skills}".strip()
                    )
                    if title:
                        display = f"{title} · {company}".strip(" ·") if company else title
                        highlights[label].append(display)
                elif label == "certificates":
                    name = item.get("name") or "Certificate"
                    provider = item.get("provider") or ""
                    field = item.get("field") or ""
                    context_lines.append(
                        f"Certificate — {name} from {provider} in {field}.".strip()
                    )
                    if name:
                        highlights[label].append(name)
                else:
                    name = item.get("name") or item.get("title") or "Record"
                    context_lines.append(f"{label.title()} — {name}.")
                    if name:
                        highlights[label].append(name)

        for key, values in highlights.items():
            highlights[key] = list(dict.fromkeys(values))

        return context_lines, highlights

    def _compose_navigation_fallback(self, query: str, highlights: Dict[str, List[str]]) -> str:
        summary_parts: List[str] = []
        project_names = highlights.get("projects", [])
        job_names = highlights.get("jobs", [])
        certificate_names = highlights.get("certificates", [])

        if project_names:
            summary_parts.append(
                f"I have worked on projects such as {', '.join(project_names[:3])} that showcase {query or 'these capabilities'}."
            )
        if job_names:
            summary_parts.append(
                f"My experience includes roles like {', '.join(job_names[:2])} where I applied {query or 'these skills'} in practice."
            )
        if certificate_names:
            summary_parts.append(
                f"I have also earned certifications including {', '.join(certificate_names[:3])} that reinforce this expertise."
            )

        if not summary_parts:
            if query:
                summary_parts.append(
                    f"I could not find specific portfolio records for '{query}', but feel free to explore the sections below for more details."
                )
            else:
                summary_parts.append("Here are the most relevant highlights from my portfolio.")

        return " ".join(summary_parts)

    def _compose_information_fallback(self, query: str, context_lines: List[str]) -> str:
        if context_lines:
            bullet_list = "\n".join(f"• {line}" for line in context_lines[:5])
            intro = (
                f"Here’s a curated snapshot from my portfolio tailored to \"{query}\":"
                if query
                else "Here’s a curated snapshot from across my portfolio:"
            )
            outro = (
                "Browse the sections below to dive into the full write-ups and related work."
            )
            return f"{intro}\n\n{bullet_list}\n\n{outro}"

        if query:
            return (
                f"I couldn’t assemble a richer AI summary for \"{query}\" just yet. Try exploring the sections below or rephrasing your question for more context."
            )

        return (
            "I couldn’t assemble a richer AI summary right now. Feel free to browse the sections below or ask another question for more context."
        )

    async def _build_navigation_summary(self, query: str, sections: List[SearchSection]) -> SearchSummary:
        context_lines, highlights = self._extract_section_context(sections)

        context_blob = "\n".join(line for line in context_lines if line)[:4000]
        summary_text: Optional[str] = None

        if context_blob:
            prompt = self.agent.prompt_manager.get_prompt(
                "search_summary",
                query=query,
                context=context_blob
            )
            try:
                llm_summary = await self.agent.provider_manager.generate_response(prompt)
                summary_text = llm_summary.response.strip()
            except Exception as exc:
                logger.warning("Navigation summary generation failed: %s", exc)

        filtered_highlights = {
            key: values[:5]
            for key, values in highlights.items()
            if values
        }

        if not summary_text:
            summary_text = self._compose_navigation_fallback(query, filtered_highlights)

        if not summary_text:
            summary_text = "Explore the sections below to learn more about my work."

        title = f"{query.title()} Highlights" if query else "Portfolio Highlights"

        return SearchSummary(
            title=title,
            body=summary_text,
            highlights=filtered_highlights or None
        )

    async def _build_information_answer(
        self,
        query: str,
        sections: List[SearchSection],
        include_global_profile: bool = False
    ) -> str:
        context_lines, _ = self._extract_section_context(sections, per_section_limit=4)

        if include_global_profile:
            global_context = self._build_global_context()
            if global_context:
                merged: List[str] = []
                seen = set()
                for line in global_context + context_lines:
                    if line and line not in seen:
                        merged.append(line)
                        seen.add(line)
                context_lines = merged

        if not context_lines:
            context_lines = self._build_global_context()

        context_blob = "\n".join(line for line in context_lines if line)[:4000]

        if not context_blob:
            context_blob = "No direct matches were found in the portfolio."

        prompt = self.agent.prompt_manager.get_prompt(
            "search_information_answer",
            query=query,
            context=context_blob
        )

        try:
            llm_response = await self.agent.provider_manager.generate_response(prompt)
            answer = llm_response.response.strip()
            if answer:
                return answer
        except Exception as exc:
            logger.warning("Information answer generation failed: %s", exc)

        return self._compose_information_fallback(query, context_lines)

    @staticmethod
    def _truncate_text(text: str, max_length: int = 220) -> str:
        sanitized = (text or "").strip()
        if len(sanitized) <= max_length:
            return sanitized
        truncated = sanitized[:max_length].rsplit(" ", 1)[0]
        return truncated + "…"

    def _build_global_context(self) -> List[str]:
        context_lines: List[str] = []

        try:
            intro = self.data_service.get_intro_data()
            about_snippet = self._truncate_text(intro.about, 260)
            context_lines.append(
                f"Profile — {intro.name}, {intro.title}: {about_snippet}"
            )
        except Exception as exc:
            logger.debug("Global context intro load failed: %s", exc)

        try:
            jobs = self.data_service.get_jobs_data()
            current_jobs = [job for job in jobs if job.isCurrent]
            past_jobs = [job for job in jobs if not job.isCurrent]
            jobs_sequence = current_jobs + past_jobs
            for job in jobs_sequence[:3]:
                description = self._truncate_text(job.description, 200)
                context_lines.append(
                    f"Experience — {job.title} at {job.company}: {description}"
                )
        except Exception as exc:
            logger.debug("Global context jobs load failed: %s", exc)

        try:
            projects = self.data_service.get_new_projects_data()
            if not projects:
                projects = self.data_service.get_projects_data()
            projects_sorted = sorted(
                projects,
                key=lambda project: (not project.featured, project.name.lower())
            )
            for project in projects_sorted[:3]:
                description = self._truncate_text(project.shortDescription or project.description, 200)
                skills = ", ".join(project.skills[:5])
                context_lines.append(
                    f"Project — {project.name}: {description}. Skills: {skills}"
                )
        except Exception as exc:
            logger.debug("Global context projects load failed: %s", exc)

        try:
            certificates = self.data_service.get_certificates_data()
            for certificate in certificates[:3]:
                context_lines.append(
                    f"Certificate — {certificate.name} from {certificate.provider} in {certificate.field}."
                )
        except Exception as exc:
            logger.debug("Global context certificates load failed: %s", exc)

        return context_lines

    def classify_message(self, message: str) -> MessageClassification:
        """Classify message (synchronous wrapper)"""
        return self.classifier.classify_message(message)

    def get_ai_status(self) -> AIStatusResponse:
        """Get AI system status"""
        available_providers = self.agent.provider_manager.get_available_providers()

        return AIStatusResponse(
            status="active" if available_providers else "limited",
            components={
                "llm_agent": "active",
                "message_classifier": "active",
                "provider_manager": "active",
                "data_service": "active",
                "prompt_manager": "active"
            },
            providers={
                provider.value: (provider in available_providers)
                for provider in LLMProvider
            }
        )


# Global AI service instance
ai_service = EnhancedAIService()
