from sqlalchemy.orm import Session

from .models import Job
from .schemas.job import JobCreate, JobUpdate


# ============================================================
# CREATE JOB
# ============================================================

def create_job(db: Session, job_data: JobCreate):

    new_job = Job(
        title=job_data.title,
        company=job_data.company,
        description=job_data.description,
        location=job_data.location,
        salary=job_data.salary,
        employment_type=job_data.employment_type,
        employer_id=job_data.employer_id,
        is_visible=False,
        is_featured=False
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job


# ============================================================
# GET ALL VISIBLE JOBS
# ============================================================

def get_jobs(
    db: Session,
    search: str | None = None,
    location: str | None = None,
    employment_type: str | None = None
):

    query = db.query(Job).filter(
        Job.is_visible == True
    )

    if search:
        search = f"%{search}%"

        query = query.filter(
            (Job.title.ilike(search)) |
            (Job.company.ilike(search)) |
            (Job.description.ilike(search))
        )

    if location:
        query = query.filter(
            Job.location.ilike(f"%{location}%")
        )

    if employment_type:
        query = query.filter(
            Job.employment_type.ilike(
                f"%{employment_type}%"
            )
        )

    return query.all()


# ============================================================
# GET ONE JOB
# ============================================================

def get_job(db: Session, job_id: int):

    return db.query(Job).filter(
        Job.id == job_id,
        Job.is_visible == True
    ).first()


# ============================================================
# UPDATE JOB
# ============================================================

def update_job(
    db: Session,
    job_id: int,
    job_data: JobUpdate
):

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        return None

    update_data = job_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)

    return job


# ============================================================
# DELETE JOB
# ============================================================

def delete_job(
    db: Session,
    job_id: int
):

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        return None

    db.delete(job)
    db.commit()

    return job


# ============================================================
# PUBLISH JOB
# ============================================================

def publish_job(
    db: Session,
    job_id: int
):

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        return None

    job.is_visible = True

    db.commit()
    db.refresh(job)

    return job


# ============================================================
# GET EMPLOYER'S JOBS
# ============================================================

def get_employer_jobs(
    db: Session,
    employer_id: int
):

    return db.query(Job).filter(
        Job.employer_id == employer_id
    ).all()


# ============================================================
# FEATURE JOB
# ============================================================

def feature_job(
    db: Session,
    job_id: int
):

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if not job:
        return None

    job.is_featured = True

    db.commit()
    db.refresh(job)

    return job