
from django_q.tasks import async_task
import time 

def file_index(param1, param2):
    for i in range(10):
        print(f"Task1: {param1} {param2} {i}")
        time.sleep(10)
    return "Task1 done"

# def spustit_uloha():
#     async_task('rtbolidozor_backend.tasks.file_index', 'param1', 'param2')