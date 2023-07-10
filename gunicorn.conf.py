from os import getenv
import multiprocessing

bind = f'0.0.0.0:{getenv("APP_PORT", default=8080)}'

workers = multiprocessing.cpu_count() * 2 + 1

preload_app = True

accesslog = "-"
