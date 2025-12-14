
# 

# from celery import Celery

# from app.core.config import settings

# 

# celery_app = Celery(

#     "tasks",

#     broker=settings.CELERY_BROKER_URL,

#     backend=settings.CELERY_RESULT_BACKEND,

#     include=["app.integrations.livelaw.scheduler", "app.services.tasks"]

# )

# 

# celery_app.conf.update(

#     task_track_started=True,

# )

# 


