
# from django.apps import AppConfig
# from django_q.models import Schedule


# import time
# class MyAppConfig(AppConfig):
#     name = 'rtbolidozor_backend'

#     def ready(self):
#         pass
    #     try:
    #         if not Schedule.objects.filter(func='rtbolidozor_backend.tasks.file_index').exists():
    #             Schedule.objects.create(
    #                 func='rtbolidozor_backend.tasks.file_index',
    #                 schedule_type=Schedule.MINUTES,
    #                 minutes=15,
    #                 repeats=-1,
    #                 timeout=60*14
    #             )
    #     except Exception as e:
    #         print(f"Error: {e}")
    #         pass