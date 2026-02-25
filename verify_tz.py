import pytz
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

def test_job():
    print("Job is running!")

def verify():
    tz = pytz.timezone('America/Manaus')
    now = datetime.now(tz)
    print(f"Current time in Manaus: {now.strftime('%H:%M:%S')}")
    
    scheduler = BackgroundScheduler(timezone=tz)
    scheduler.add_job(test_job, 'cron', hour=8, minute=0)
    scheduler.add_job(test_job, 'cron', hour=18, minute=0)
    scheduler.add_job(test_job, 'cron', hour=20, minute=0)
    
    print("Jobs scheduled:")
    for job in scheduler.get_jobs():
        print(f" - {job.id}: next run at {job.next_run_time}")

if __name__ == "__main__":
    verify()
