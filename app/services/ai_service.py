from typing import Dict, Any, List, Optional, Union
import re
import time
import json
import logging
from datetime import datetime
import asyncio
from contextlib import asynccontextmanager

from app.models.schemas import (
    MessageClassification, AIRequest, AIResponse, SearchRequest,
    SearchResult, QuestionAnsweringRequest, QuestionAnsweringResponse,
    AIStatusResponse, MessageType, LLMProvider, LLMConfig, LLMRequest,
    LLMResponse, AgentPhase, AgentStep, AgentExecution
)
from app.services.data_service import DataService
from app.services.providers import LLMProviderManager, PromptManager
from app.config.settings import app_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
