from fastapi import APIRouter, Depends
from supports.utils_json_response import success_response, error_response
from middleware.jwt_required import jwt_required
from services.scheduler_maintenance_reminder import (
    start_scheduler,
    stop_scheduler,
    maintenance_reminder_job,
    get_scheduler_status
)

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])


@router.post("/maintenance-reminder/start", dependencies=[Depends(jwt_required)])
def start_maintenance_reminder_scheduler(hour: int = 7, minute: int = 0):
    """
    Mulai scheduler untuk mengirim maintenance reminder setiap hari.
    
    Query parameters:
    - hour: Jam untuk menjalankan job (0-23, default: 7)
    - minute: Menit untuk menjalankan job (0-59, default: 0)
    
    Example:
    POST /scheduler/maintenance-reminder/start?hour=7&minute=0
    """
    try:
        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            return error_response(
                message="Hour harus 0-23 dan minute harus 0-59",
                status_code=400
            )
        
        start_scheduler(hour=hour, minute=minute)
        return success_response(
            data={"message": f"Scheduler dimulai. Job akan berjalan setiap hari jam {hour:02d}:{minute:02d}"}
        )
    except Exception as e:
        return error_response(message=str(e), status_code=500)


@router.post("/maintenance-reminder/stop", dependencies=[Depends(jwt_required)])
def stop_maintenance_reminder_scheduler():
    """
    Hentikan scheduler maintenance reminder.
    """
    try:
        stop_scheduler()
        return success_response(data={"message": "Scheduler dihentikan"})
    except Exception as e:
        return error_response(message=str(e), status_code=500)


@router.get("/maintenance-reminder/status", dependencies=[Depends(jwt_required)])
def get_maintenance_reminder_scheduler_status():
    """
    Dapatkan status scheduler maintenance reminder.
    """
    try:
        status = get_scheduler_status()
        return success_response(data=status)
    except Exception as e:
        return error_response(message=str(e), status_code=500)


@router.post("/maintenance-reminder/run-now", dependencies=[Depends(jwt_required)])
def run_maintenance_reminder_now():
    """
    Jalankan maintenance reminder job sekarang (manual trigger).
    """
    try:
        result = maintenance_reminder_job()
        return success_response(data=result)
    except Exception as e:
        return error_response(message=str(e), status_code=500)
