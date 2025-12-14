"""
Background scheduler untuk mengirim maintenance reminder WhatsApp secara otomatis.
Menggunakan APScheduler untuk menjalankan job di background.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from models.database import SessionLocal
from services.services_customer import send_maintenance_reminder_whatsapp
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = BackgroundScheduler()


def maintenance_reminder_job():
    """
    Job yang dijalankan oleh scheduler untuk mengirim maintenance reminder.
    Job ini berjalan di background thread.
    """
    db = SessionLocal()
    try:
        logger.info(f"[{datetime.now()}] Memulai job send_maintenance_reminder...")
        result = send_maintenance_reminder_whatsapp(db)
        logger.info(f"[{datetime.now()}] Job selesai. Reminder terkirim: {result['reminder_sent']}/{result['total_customers']}")
        return result
    except Exception as e:
        logger.error(f"[{datetime.now()}] Error dalam maintenance_reminder_job: {str(e)}")
    finally:
        db.close()


def start_scheduler(hour: int = 7, minute: int = 0):
    """
    Mulai scheduler untuk mengirim maintenance reminder setiap hari pada jam yang ditentukan.
    
    Args:
        hour: Jam untuk menjalankan job (default: 7, berarti jam 7 pagi)
        minute: Menit untuk menjalankan job (default: 0)
    
    Returns:
        BackgroundScheduler instance
    """
    global scheduler
    
    if scheduler.running:
        logger.warning("Scheduler sudah running")
        return scheduler
    
    # Tambahkan job dengan trigger cron (setiap hari pada jam yang ditentukan)
    scheduler.add_job(
        maintenance_reminder_job,
        CronTrigger(hour=hour, minute=minute),
        id='maintenance_reminder_job',
        name='Maintenance Reminder WhatsApp',
        replace_existing=True,
        max_instances=1  # Pastikan hanya ada satu instance job yang running
    )
    
    scheduler.start()
    logger.info(f"Scheduler dimulai. Job akan berjalan setiap hari jam {hour:02d}:{minute:02d}")
    
    return scheduler


def stop_scheduler():
    """
    Hentikan scheduler.
    """
    global scheduler
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler dihentikan")


def get_scheduler_status():
    """
    Dapatkan status scheduler.
    
    Returns:
        Dict berisi status scheduler dan job-job yang terdaftar.
    """
    global scheduler
    
    jobs = []
    if scheduler.running:
        for job in scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
    
    return {
        "running": scheduler.running,
        "jobs": jobs
    }
