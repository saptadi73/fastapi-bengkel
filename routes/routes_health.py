from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from models.database import SessionLocal, check_database_connection
from supports.utils_json_response import error_response, success_response

router = APIRouter(tags=["Health Check"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        database_status = check_database_connection(db)
        return success_response(
            data={
                "app": "ok",
                "database": database_status,
            },
            message="Health check passed",
        )
    except Exception as exc:
        return error_response(
            message=f"Health check failed: {str(exc)}",
            status_code=503,
            data={
                "app": "ok",
                "database": {
                    "connected": False,
                },
            },
        )


@router.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    try:
        database_status = check_database_connection(db)
        return success_response(
            data=database_status,
            message="Database connection is healthy",
        )
    except Exception as exc:
        return error_response(
            message=f"Database connection failed: {str(exc)}",
            status_code=503,
            data={
                "connected": False,
            },
        )
