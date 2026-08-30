from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime

from .schemas.job import JobCreate, JobUpdate, JobResponse


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


# Temporary database
jobs = []
job_id_counter = 1


# GET /jobs
# Search and browse jobs
@router.get("/", response_model=List[JobResponse])
def get_jobs(
    search: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    employment_type: Optional[str] = Query(None)
):
    result = jobs

    if search:
        search = search.lower()

        result = [
            job for job in result
            if search in job["title"].lower()
            or search in job["company"].lower()
            or search in job["description"].lower()
        ]

    if location:
        result = [
            job for job in result
            if job["location"].lower() == location.lower()
        ]

    if employment_type:
        result = [
            job for job in result
            if job["employment_type"].lower()
            == employment_type.lower()
        ]

    return [
        job for job in result
        if job["is_visible"]
    ]


# GET /jobs/{job_id}
# See one job in full
@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int):

    for job in jobs:
        if job["id"] == job_id:

            if not job["is_visible"]:
                raise HTTPException(
                    status_code=404,
                    detail="Job is not visible"
                )

            return job

    raise HTTPException(
        status_code=404,
        detail="Job not found"
    )


# POST /jobs
# Post a new job
@router.post("/", response_model=JobResponse, status_code=201)
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
        "is_visible": False,
        "is_featured": False,
        "created_at": datetime.now()
    }

    jobs.append(new_job)
    job_id_counter += 1

    return new_job


# PATCH /jobs/{job_id}
# Edit a job
@router.patch("/{job_id}", response_model=JobResponse)
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


# POST /jobs/{job_id}/publish
# Make job visible on website
@router.post("/{job_id}/publish")
def publish_job(job_id: int):

    for job in jobs:

        if job["id"] == job_id:

            job["is_visible"] = True

            return {
                "message": "Job is now visible on the site",
                "job": job
            }

    raise HTTPException(
        status_code=404,
        detail="Job not found"
    )


# DELETE /jobs/{job_id}
# Delete a job
@router.delete("/{job_id}")
def delete_job(job_id: int):

    for index, job in enumerate(jobs):

        if job["id"] == job_id:

            jobs.pop(index)

            return {
                "message": "Job deleted successfully"
            }

    raise HTTPException(
        status_code=404,
        detail="Job not found"
    )


# GET /jobs/employer/{employer_id}
# List everything an employer has posted
@router.get(
    "/employer/{employer_id}",
    response_model=List[JobResponse]
)
def get_employer_jobs(employer_id: int):

    return [
        job for job in jobs
        if job["employer_id"] == employer_id
    ]


# POST /jobs/{job_id}/feature
# Pay to feature/highlight a job
@router.post("/{job_id}/feature")
def feature_job(job_id: int):

    for job in jobs:

        if job["id"] == job_id:

            # Payment verification would go here.
            job["is_featured"] = True

            return {
                "message": "Job featured successfully",
                "job": job
            }

    raise HTTPException(
        status_code=404,
        detail="Job not found"
    )