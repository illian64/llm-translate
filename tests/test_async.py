import multiprocessing
import os
import threading
import time
from unittest import TestCase

# gpu - 0, 3. workers - 1, 2.

#[00:07<00:00,  1.09part/s]
#[00:07<00:00,  1.08part/s]

def print_name(param):
    process_id = os.getpid()
    # Получаем имя процесса
    process_name = multiprocessing.current_process().name
    print(f"Обрабатываем {param} в процессе {os.getpid()} ({multiprocessing.current_process().name}) thread: {threading.current_thread().name}")


def calculate_parameter(param):
    print_name(param)

    time.sleep(3)  # Имитация I/O операции
    return param ** 2


class StructTest(TestCase):
    def test_n1(self):
        print_name("main")
        num_processes = 3
        worker_names = [f"CustomWorker-{i}" for i in range(num_processes)]

        pool: multiprocessing.Pool = multiprocessing.Pool(processes=num_processes, initargs=(worker_names[0],))
        results = pool.map(calculate_parameter, range(1,9))
        print(results)



