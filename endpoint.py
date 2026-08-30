from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


app = FastAPI(
    title="Job Board API",
    description="API for posting, browsing, updating and managing jobs",
    version="1.0.0"
)


# ============================================================
# DATABASE (Temporary in-memory storage)
# ============================================================

jobs = []
job_id_counter = 1


# ============================================================
# SCHEMAS
# ============================================================

class JobCreate(BaseModel):
    title: str
    company: str
    description: str
    location: str
    salary: Optional[str] = None
    employment_type: Optional[str] = "Full-time"
    employer_id: int


class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    salary: Optional[str] = None
    employment_type: Optional[str] = None


class JobResponse(JobCreate):
    id: int
    is_visible: bool
    is_featured: bool
    created_at: datetime


# ============================================================
# GET /jobs
# Search and browse jobs
# ============================================================

@app.get("/jobs", response_model=List[JobResponse])
def get_jobs(
    search: Optional[str] = Query(None, description="Search job title or description"),
    location: Optional[str] = Query(None),
    employment_type: Optional[str] = Query(None)
):
    result = jobs

    # Search
    if search:
        search_lower = search.lower()

        result = [
            job for job in result
            if search_lower in job["title"].lower()
            or search_lower in job["description"].lower()
            or search_lower in job["company"].lower()
        ]

    # Filter by location
    if location:
        result = [
            job for job in result
            if job["location"].lower() == location.lower()
        ]

    # Filter by employment type
    if employment_type:
        result = [
            job for job in result
            if job["employment_type"].lower() == employment_type.lower()
        ]

    # Only show visible jobs
    result = [
        job for job in result
        if job["is_visible"] is True
    ]

    return result


# ============================================================
# GET /jobs/{job_id}
# See one job in full
# ============================================================

@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: int):

    for job in jobs:
        if job["id"] == job_id:

            if not job["is_visible"]:
                raise HTTPException(
                    status_code=404,
                    detail="Job is not currently visible"
                )

            return job

    raise HTTPException(
        status_code=404,
        detail="Job not found"
    )


# ============================================================
# POST /jobs
# Post a new job
# ============================================================

@app.post("/jobs", response_model=JobResponse, status_code=201)
def create_job(job: JobCreate):

    global job_id_counter

    new_job = {
        "id": job_id_counter,
        "title": job.title,
        "company": job.company,
        "description": job.description,
        "location": job.location,
        "salary": job.salary,
        "employment_type": job.employment_type,
        "employer_id": job.employer_id,

        # New jobs start hidden
        "is_visible": False,

        # New jobs are not featured
        "is_featured": False,

        "created_at": datetime.now()
    }

    jobs.append(new_job)

    job_id_counter += 1

    return new_job


# ============================================================
# PATCH /jobs/{job_id}
# Update an existing job
# ============================================================

@app.patch("/jobs/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_update: JobUpdate
):

    for job in jobs:

        if job["id"] == job_id:

            update_data = job_update.model_dump(
                exclude_unset=True
            )

            for key, value in update_data.items():
                job[key] = value

            return job

    raise HTTPException(
        status_code=404,
        detail="Job not found"
    )


# ============================================================
# POST /jobs/{job_id}/publish
# Make a job visible on the site
# ============================================================

@app.post("/jobs/{job_id}/publish", response_model=JobResponse)
def publish_job(job_id: int):

    for job in jobs:

        if job["id"] == job_id:

            job["is_visible"] = True

            return job

    raise HTTPException(
        status_code=404,
        detail="Job not found"
    )


# ============================================================
# DELETE /jobs/{job_id}
# Delete a job
# ============================================================

@app.delete("/jobs/{job_id}")
def delete_job(job_id: int):

    for index, job in enumerate(jobs):

        if job["id"] == job_id:

            jobs.pop(index)

            return {
                "message": "Job deleted successfully",
                "job_id": job_id
            }

    raise HTTPException(
        status_code=404,
        detail="Job not found"
    )


# ============================================================
# GET /employers/{employer_id}/jobs
# List everything an employer has posted
# ============================================================

@app.get(
    "/employers/{employer_id}/jobs",
    response_model=List[JobResponse]
)
def get_employer_jobs(employer_id: int):

    employer_jobs = [
        job for job in jobs
        if job["employer_id"] == employer_id
    ]

    return employer_jobs


# ============================================================
# POST /jobs/{job_id}/feature
# Pay to feature/highlight a job
# ============================================================

@app.post("/jobs/{job_id}/feature", response_model=JobResponse)
def feature_job(job_id: int):

    for job in jobs:

        if job["id"] == job_id:

            # In a real application, payment would be
            # processed before setting this to True.

            job["is_featured"] = True

            return job

    raise HTTPException(
        status_code=404,
        detail="Job not found"
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Job Board API is running",
        "docs": "/docs"
    }