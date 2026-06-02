from django.apps import AppConfig


class RtbolidozorBackendConfig(AppConfig):
    name = 'rtbolidozor_backend'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from django_q.models import Schedule
        try:
            if not Schedule.objects.filter(func='rtbolidozor_backend.tasks.file_index').exists():
                Schedule.objects.create(
                    func='rtbolidozor_backend.tasks.file_index',
                    kwargs='{"duration": 2}',
                    schedule_type=Schedule.MINUTES,
                    minutes=15,
                    repeats=-1,
                    timeout=60 * 14,
                )
                print("Scheduled: file_index (kazdych 15 minut, posledni 2 hodiny)")

            if not Schedule.objects.filter(func='rtbolidozor_backend.tasks.run_meteor_clusterer').exists():
                Schedule.objects.create(
                    func='rtbolidozor_backend.tasks.run_meteor_clusterer',
                    schedule_type=Schedule.MINUTES,
                    minutes=15,
                    repeats=-1,
                )
                print("Scheduled: run_meteor_clusterer (kazdych 15 minut)")

        except Exception as e:
            print(f"Chyba pri registraci scheduled tasku: {e}")
