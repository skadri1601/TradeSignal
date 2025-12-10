"""
Job and job application management endpoints.

Super admins can create, update, and delete job postings.
Public users can view active jobs and submit applications.
Support and super admins can review applications.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.database import get_db
from app.models.user import User
from app.models.job import Job
from app.models.job_application import JobApplication, ApplicationStatus
from app.schemas.job import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobListResponse,
    JobApplicationCreate,
    JobApplicationResponse,
    JobApplicationStatusUpdate,
    JobApplicationListResponse,
)
from app.core.security import (
    get_current_superuser,
    get_current_support_or_superuser,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["jobs"])


# Job Management Endpoints (Admin only)


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """
    Create a new job posting (super admin only).

    Args:
        job_data: Job details
        current_user: Authenticated super admin user
        db: Database session

    Returns:
        Created job
    """
    try:
        logger.info(
            f"Creating job posting: title='{job_data.title}', "
            f"department='{job_data.department}', "
            f"created_by_user_id={current_user.id}, "
            f"user_role={current_user.role}, "
            f"is_superuser={current_user.is_superuser}"
        )

        # Create job
        job = Job(**job_data.model_dump(), created_by=current_user.id)

        db.add(job)
        await db.commit()
        await db.refresh(job)

        logger.info(
            f"Successfully created job posting: id={job.id}, title='{job.title}'"
        )

        # Return with application count
        response = JobResponse.model_validate(job)
        response.application_count = 0

        return response

    except IntegrityError as e:
        await db.rollback()
        logger.error(
            f"Database integrity error creating job: {str(e)}, "
            f"user_id={current_user.id}, job_title='{job_data.title}'",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create job. Please check that all required fields are valid and try again.",
        )
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            f"Database error creating job: {str(e)}, "
            f"user_id={current_user.id}, job_title='{job_data.title}'",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the job. Please try again later.",
        )
    except ValueError as e:
        await db.rollback()
        logger.error(
            f"Validation error creating job: {str(e)}, "
            f"user_id={current_user.id}, job_title='{job_data.title}'",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid job data: {str(e)}",
        )
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Unexpected error creating job: {str(e)}, "
            f"user_id={current_user.id}, job_title='{job_data.title}'",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later.",
        )


@router.get("/", response_model=JobListResponse)
async def get_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    active_only: bool = Query(True, description="Only return active jobs"),
    db: AsyncSession = Depends(get_db),
) -> JobListResponse:
    """
    Get list of jobs (public endpoint).

    Args:
        page: Page number
        page_size: Page size
        active_only: Only show active jobs
        db: Database session

    Returns:
        Paginated list of jobs
    """
    # Build query
    query = select(Job)

    if active_only:
        query = query.where(Job.is_active.is_(True))

    # Get total count
    count_query = select(func.count()).select_from(Job)
    if active_only:
        count_query = count_query.where(Job.is_active.is_(True))

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Paginate
    query = query.order_by(Job.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    jobs = result.scalars().all()

    # Get application counts for each job
    job_responses = []
    for job in jobs:
        app_count_query = (
            select(func.count())
            .select_from(JobApplication)
            .where(JobApplication.job_id == job.id)
        )
        app_count_result = await db.execute(app_count_query)
        app_count = app_count_result.scalar_one()

        response = JobResponse.model_validate(job)
        response.application_count = app_count
        job_responses.append(response)

    return JobListResponse(
        jobs=job_responses, total=total, page=page, page_size=page_size
    )


@router.get("/admin", response_model=JobListResponse)
async def get_all_jobs_admin(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> JobListResponse:
    """
    Get all jobs including inactive (super admin only).

    Args:
        page: Page number
        page_size: Page size
        current_user: Authenticated super admin
        db: Database session

    Returns:
        Paginated list of all jobs
    """
    # Get total count
    total_result = await db.execute(select(func.count()).select_from(Job))
    total = total_result.scalar_one()

    # Get jobs
    query = select(Job).order_by(Job.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    jobs = result.scalars().all()

    # Get application counts
    job_responses = []
    for job in jobs:
        app_count_query = (
            select(func.count())
            .select_from(JobApplication)
            .where(JobApplication.job_id == job.id)
        )
        app_count_result = await db.execute(app_count_query)
        app_count = app_count_result.scalar_one()

        response = JobResponse.model_validate(job)
        response.application_count = app_count
        job_responses.append(response)

    return JobListResponse(
        jobs=job_responses, total=total, page=page, page_size=page_size
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)) -> JobResponse:
    """
    Get a single job by ID (public endpoint).

    Args:
        job_id: Job ID
        db: Database session

    Returns:
        Job details
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    # Get application count
    app_count_query = (
        select(func.count())
        .select_from(JobApplication)
        .where(JobApplication.job_id == job.id)
    )
    app_count_result = await db.execute(app_count_query)
    app_count = app_count_result.scalar_one()

    response = JobResponse.model_validate(job)
    response.application_count = app_count

    return response


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """
    Update a job posting (super admin only).

    Args:
        job_id: Job ID
        job_data: Updated job data
        current_user: Authenticated super admin
        db: Database session

    Returns:
        Updated job
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    # Update fields
    update_data = job_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    await db.commit()
    await db.refresh(job)

    # Get application count
    app_count_query = (
        select(func.count())
        .select_from(JobApplication)
        .where(JobApplication.job_id == job.id)
    )
    app_count_result = await db.execute(app_count_query)
    app_count = app_count_result.scalar_one()

    response = JobResponse.model_validate(job)
    response.application_count = app_count

    return response


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a job posting (super admin only).

    Cascades to delete all applications for this job.

    Args:
        job_id: Job ID
        current_user: Authenticated super admin
        db: Database session
    """
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    await db.delete(job)
    await db.commit()


# Job Application Endpoints


@router.post(
    "/{job_id}/apply",
    response_model=JobApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def apply_to_job(
    job_id: int,
    application_data: JobApplicationCreate,
    db: AsyncSession = Depends(get_db),
) -> JobApplicationResponse:
    """
    Submit a job application (public endpoint).

    Args:
        job_id: Job ID to apply for
        application_data: Application details
        db: Database session

    Returns:
        Created application
    """
    # Check if job exists and is active
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    if not job.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This job posting is no longer accepting applications",
        )

    # Create application
    application = JobApplication(job_id=job_id, **application_data.model_dump())

    db.add(application)
    await db.commit()
    await db.refresh(application)

    # Return with job details
    response = JobApplicationResponse.model_validate(application)
    response.job_title = job.title
    response.job_department = job.department

    return response


@router.get("/applications", response_model=JobApplicationListResponse)
async def get_applications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    job_id: int | None = Query(None, description="Filter by job ID"),
    status: str | None = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_support_or_superuser),
    db: AsyncSession = Depends(get_db),
) -> JobApplicationListResponse:
    """
    Get job applications (support/super admin only).

    Args:
        page: Page number
        page_size: Page size
        job_id: Optional job ID filter
        status: Optional status filter
        current_user: Authenticated support/super admin
        db: Database session

    Returns:
        Paginated list of applications
    """
    # Build query
    query = select(JobApplication)
    count_query = select(func.count()).select_from(JobApplication)

    filters = []
    if job_id:
        filters.append(JobApplication.job_id == job_id)
    if status:
        filters.append(JobApplication.status == status)

    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Paginate
    query = query.order_by(JobApplication.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    applications = result.scalars().all()

    # Fetch job details for each application
    application_responses = []
    for app in applications:
        job_result = await db.execute(select(Job).where(Job.id == app.job_id))
        job = job_result.scalar_one_or_none()

        response = JobApplicationResponse.model_validate(app)
        if job:
            response.job_title = job.title
            response.job_department = job.department
        application_responses.append(response)

    return JobApplicationListResponse(
        applications=application_responses, total=total, page=page, page_size=page_size
    )


@router.put(
    "/applications/{application_id}/status", response_model=JobApplicationResponse
)
async def update_application_status(
    application_id: int,
    status_update: JobApplicationStatusUpdate,
    current_user: User = Depends(get_current_support_or_superuser),
    db: AsyncSession = Depends(get_db),
) -> JobApplicationResponse:
    """
    Update job application status (support/super admin only).

    Args:
        application_id: Application ID
        status_update: New status
        current_user: Authenticated support/super admin
        db: Database session

    Returns:
        Updated application
    """
    result = await db.execute(
        select(JobApplication).where(JobApplication.id == application_id)
    )
    application = result.scalar_one_or_none()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )

    # Update status
    application.status = ApplicationStatus(status_update.status)

    await db.commit()
    await db.refresh(application)

    # Get job details
    job_result = await db.execute(select(Job).where(Job.id == application.job_id))
    job = job_result.scalar_one_or_none()

    response = JobApplicationResponse.model_validate(application)
    if job:
        response.job_title = job.title
        response.job_department = job.department

    return response
