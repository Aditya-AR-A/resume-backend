from typing import Dict, Any, List, Optional, Union
import time
from datetime import datetime
from collections import defaultdict, Counter
import re

from app.utils.data_loader import load_json_data
from app.models.schemas import (
    IntroData, JobData, ProjectData, CertificateData,
    LayoutData, PageData, UnifiedSearchResponse, SearchSection,
    SkillsResponse, SkillAggregation, TimelineResponse, TimelineItem,
    StatsSummary, FilterOptions, PaginationMeta, PaginatedProjectsResponse,
    PaginatedJobsResponse, PaginatedCertificatesResponse, APIResponse
)


class DataService:
    """Enhanced service layer for data operations with structured schemas"""

    @staticmethod
    def get_intro_data() -> IntroData:
        """Get introduction data with proper typing"""
        data = load_json_data("intro")
        return IntroData(**data)

    @staticmethod
    def get_jobs_data() -> List[JobData]:
        """Get work experience data with proper typing"""
        data = load_json_data("jobs")
        return [JobData(**job) for job in data]

    @staticmethod
    def get_projects_data() -> List[ProjectData]:
        """Get projects data with proper typing"""
        data = load_json_data("projects")
        return [ProjectData(**project) for project in data]

    @staticmethod
    def get_new_projects_data() -> List[ProjectData]:
        """Get new projects data with proper typing"""
        data = load_json_data("projects_new")
        return [ProjectData(**project) for project in data]

    @staticmethod
    def get_certificates_data() -> List[CertificateData]:
        """Get certificates data with proper typing"""
        data = load_json_data("certificates")
        return [CertificateData(**cert) for cert in data]

    @staticmethod
    def get_layout_data() -> LayoutData:
        """Get layout configuration with proper typing"""
        data = load_json_data("layout")
        return LayoutData(**data)

    @staticmethod
    def get_page_data() -> PageData:
        """Get page configuration with proper typing"""
        data = load_json_data("page")
        return PageData(**data)

    @staticmethod
    def get_project_by_id(project_id: str) -> Optional[ProjectData]:
        """Get individual project by ID"""
        projects = DataService.get_projects_data()
        for project in projects:
            if project.id == project_id:
                return project
        return None

    @staticmethod
    def get_job_by_id(job_id: str) -> Optional[JobData]:
        """Get individual job by ID"""
        jobs = DataService.get_jobs_data()
        for job in jobs:
            if job.id == job_id:
                return job
        return None

    @staticmethod
    def get_certificate_by_id(cert_id: str) -> Optional[CertificateData]:
        """Get individual certificate by ID"""
        certificates = DataService.get_certificates_data()
        for cert in certificates:
            if cert.name.lower().replace(" ", "_") == cert_id.lower():
                return cert
        return None

    @staticmethod
    def get_paginated_projects(
        limit: int = 10,
        offset: int = 0,
        filters: Optional[FilterOptions] = None
    ) -> PaginatedProjectsResponse:
        """Get paginated projects with filtering"""
        projects = DataService.get_projects_data()

        # Apply filters
        if filters:
            filtered_projects = DataService._filter_projects(projects, filters)
        else:
            filtered_projects = projects

        # Apply pagination
        total_count = len(filtered_projects)
        start_idx = offset
        end_idx = offset + limit
        paginated_projects = filtered_projects[start_idx:end_idx]

        pagination = PaginationMeta(
            total_count=total_count,
            limit=limit,
            offset=offset,
            has_more=end_idx < total_count
        )

        return PaginatedProjectsResponse(
            data=paginated_projects,
            pagination=pagination,
            filters=filters
        )

    @staticmethod
    def get_paginated_jobs(
        limit: int = 10,
        offset: int = 0,
        filters: Optional[FilterOptions] = None
    ) -> PaginatedJobsResponse:
        """Get paginated jobs with filtering"""
        jobs = DataService.get_jobs_data()

        # Apply filters
        if filters:
            filtered_jobs = DataService._filter_jobs(jobs, filters)
        else:
            filtered_jobs = jobs

        # Apply pagination
        total_count = len(filtered_jobs)
        start_idx = offset
        end_idx = offset + limit
        paginated_jobs = filtered_jobs[start_idx:end_idx]

        pagination = PaginationMeta(
            total_count=total_count,
            limit=limit,
            offset=offset,
            has_more=end_idx < total_count
        )

        return PaginatedJobsResponse(
            data=paginated_jobs,
            pagination=pagination,
            filters=filters
        )

    @staticmethod
    def get_paginated_certificates(
        limit: int = 10,
        offset: int = 0,
        filters: Optional[FilterOptions] = None
    ) -> PaginatedCertificatesResponse:
        """Get paginated certificates with filtering"""
        certificates = DataService.get_certificates_data()

        # Apply filters
        if filters:
            filtered_certificates = DataService._filter_certificates(certificates, filters)
        else:
            filtered_certificates = certificates

        # Apply pagination
        total_count = len(filtered_certificates)
        start_idx = offset
        end_idx = offset + limit
        paginated_certificates = filtered_certificates[start_idx:end_idx]

        pagination = PaginationMeta(
            total_count=total_count,
            limit=limit,
            offset=offset,
            has_more=end_idx < total_count
        )

        return PaginatedCertificatesResponse(
            data=paginated_certificates,
            pagination=pagination,
            filters=filters
        )

    @staticmethod
    def unified_search(
        query: str,
        include_sections: List[str] = None,
        limit: int = 10
    ) -> UnifiedSearchResponse:
        """Perform unified search across multiple sections"""
        if include_sections is None:
            include_sections = ["projects", "jobs", "certificates"]

        start_time = time.time()
        sections = []

        # Search projects
        if "projects" in include_sections:
            projects = DataService.get_projects_data()
            project_results = DataService._search_projects(query, projects, limit)
            if project_results:
                sections.append(SearchSection(
                    type="projects",
                    items=[project.dict() for project in project_results],
                    count=len(project_results)
                ))

        # Search jobs
        if "jobs" in include_sections:
            jobs = DataService.get_jobs_data()
            job_results = DataService._search_jobs(query, jobs, limit)
            if job_results:
                sections.append(SearchSection(
                    type="jobs",
                    items=[job.dict() for job in job_results],
                    count=len(job_results)
                ))

        # Search certificates
        if "certificates" in include_sections:
            certificates = DataService.get_certificates_data()
            cert_results = DataService._search_certificates(query, certificates, limit)
            if cert_results:
                sections.append(SearchSection(
                    type="certificates",
                    items=[cert.dict() for cert in cert_results],
                    count=len(cert_results)
                ))

        total_count = sum(section.count for section in sections)
        search_time = time.time() - start_time

        return UnifiedSearchResponse(
            query=query,
            sections=sections,
            total_count=total_count,
            search_time=search_time
        )

    @staticmethod
    def get_skills_aggregation() -> SkillsResponse:
        """Aggregate skills across all data sources"""
        projects = DataService.get_projects_data()
        jobs = DataService.get_jobs_data()
        certificates = DataService.get_certificates_data()

        skill_counter = Counter()
        skill_categories = defaultdict(set)
        skill_projects = defaultdict(list)
        skill_jobs = defaultdict(list)
        skill_certificates = defaultdict(list)

        # Process projects
        for project in projects:
            for skill in project.skills:
                skill_counter[skill] += 1
                skill_categories[skill].add(project.category)
                skill_projects[skill].append(project.name)

        # Process jobs
        for job in jobs:
            for skill in job.skills:
                skill_counter[skill] += 1
                skill_categories[skill].add("Experience")
                skill_jobs[skill].append(job.title)

        # Process certificates
        for cert in certificates:
            for skill in cert.skills:
                skill_counter[skill] += 1
                skill_categories[skill].add(cert.field)
                skill_certificates[skill].append(cert.name)

        # Create skill aggregations
        skills = []
        for skill, count in skill_counter.most_common():
            skills.append(SkillAggregation(
                skill=skill,
                count=count,
                categories=list(skill_categories[skill]),
                projects=skill_projects[skill][:5],  # Limit to top 5
                jobs=skill_jobs[skill][:3],  # Limit to top 3
                certificates=skill_certificates[skill][:3]  # Limit to top 3
            ))

        # Get unique categories
        all_categories = set()
        for categories in skill_categories.values():
            all_categories.update(categories)
        categories = sorted(list(all_categories))

        return SkillsResponse(
            skills=skills,
            categories=categories,
            total_unique_skills=len(skills)
        )

    @staticmethod
    def get_timeline() -> TimelineResponse:
        """Create timeline combining jobs and certificates"""
        jobs = DataService.get_jobs_data()
        certificates = DataService.get_certificates_data()

        timeline_items = []

        # Add jobs to timeline
        for job in jobs:
            timeline_items.append(TimelineItem(
                id=job.id,
                type="job",
                title=job.title,
                organization=job.company,
                date=job.startDate,
                endDate=job.endDate,
                isCurrent=job.isCurrent,
                description=job.description,
                skills=job.skills
            ))

        # Add certificates to timeline (using issue date if available)
        for cert in certificates:
            date = cert.issueDate or "2023-01-01"  # Default date if not available
            timeline_items.append(TimelineItem(
                id=cert.name.lower().replace(" ", "_"),
                type="certificate",
                title=cert.name,
                organization=cert.provider,
                date=date,
                description=f"Certification in {cert.field}",
                skills=cert.skills
            ))

        # Sort by date (descending)
        timeline_items.sort(key=lambda x: x.date, reverse=True)

        return TimelineResponse(
            items=timeline_items,
            total_count=len(timeline_items)
        )

    @staticmethod
    def get_stats_summary() -> StatsSummary:
        """Generate portfolio statistics summary"""
        projects = DataService.get_projects_data()
        jobs = DataService.get_jobs_data()
        certificates = DataService.get_certificates_data()
        skills_data = DataService.get_skills_aggregation()

        # Calculate stats
        total_projects = len(projects)
        total_jobs = len(jobs)
        total_certificates = len(certificates)
        featured_projects = len([p for p in projects if p.featured])

        # Get current position
        current_job = next((job for job in jobs if job.isCurrent), None)
        current_position = current_job.title if current_job else None

        # Calculate years of experience (rough estimate)
        years_experience = len(jobs)  # Simple approximation

        # Get top skills
        top_skills = [skill.skill for skill in skills_data.skills[:10]]

        # Category distribution
        categories = defaultdict(int)
        for project in projects:
            categories[project.category] += 1

        return StatsSummary(
            total_projects=total_projects,
            total_jobs=total_jobs,
            total_certificates=total_certificates,
            total_skills=skills_data.total_unique_skills,
            featured_projects=featured_projects,
            current_position=current_position,
            years_experience=years_experience,
            top_skills=top_skills,
            categories=dict(categories)
        )

    # ============================================================================
    # PRIVATE HELPER METHODS
    # ============================================================================

    @staticmethod
    def _filter_projects(projects: List[ProjectData], filters: FilterOptions) -> List[ProjectData]:
        """Filter projects based on criteria"""
        filtered = projects

        if filters.skills:
            filtered = [p for p in filtered if any(skill in p.skills for skill in filters.skills)]

        if filters.featured is not None:
            filtered = [p for p in filtered if p.featured == filters.featured]

        if filters.category:
            filtered = [p for p in filtered if p.category.lower() == filters.category.lower()]

        if filters.status:
            filtered = [p for p in filtered if p.status.lower() == filters.status.lower()]

        return filtered

    @staticmethod
    def _filter_jobs(jobs: List[JobData], filters: FilterOptions) -> List[JobData]:
        """Filter jobs based on criteria"""
        filtered = jobs

        if filters.skills:
            filtered = [j for j in filtered if any(skill in j.skills for skill in filters.skills)]

        return filtered

    @staticmethod
    def _filter_certificates(certificates: List[CertificateData], filters: FilterOptions) -> List[CertificateData]:
        """Filter certificates based on criteria"""
        filtered = certificates

        if filters.skills:
            filtered = [c for c in filtered if any(skill in c.skills for skill in filters.skills)]

        return filtered

    @staticmethod
    def _search_projects(query: str, projects: List[ProjectData], limit: int) -> List[ProjectData]:
        """Search projects by query"""
        query_lower = query.lower()
        results = []

        for project in projects:
            # Search in name, description, skills, category
            searchable_text = f"{project.name} {project.description} {project.shortDescription or ''} {' '.join(project.skills)} {project.category}"
            if query_lower in searchable_text.lower():
                results.append(project)
                if len(results) >= limit:
                    break

        return results

    @staticmethod
    def _search_jobs(query: str, jobs: List[JobData], limit: int) -> List[JobData]:
        """Search jobs by query"""
        query_lower = query.lower()
        results = []

        for job in jobs:
            # Search in title, company, description, skills
            searchable_text = f"{job.title} {job.company} {job.description} {' '.join(job.skills)}"
            if query_lower in searchable_text.lower():
                results.append(job)
                if len(results) >= limit:
                    break

        return results

    @staticmethod
    def _search_certificates(query: str, certificates: List[CertificateData], limit: int) -> List[CertificateData]:
        """Search certificates by query"""
        query_lower = query.lower()
        results = []

        for cert in certificates:
            # Search in name, provider, field, skills
            searchable_text = f"{cert.name} {cert.provider} {cert.field} {' '.join(cert.skills)}"
            if query_lower in searchable_text.lower():
                results.append(cert)
                if len(results) >= limit:
                    break

        return results
