"""
The background worker (SPEC §2, "Background work"). One process, one loop:
claim a pending row with SELECT ... FOR UPDATE SKIP LOCKED, do the work, repeat.
Datasets are ingested and chart revisions generated here.
"""

import logging
import signal
import time

from django.core.management.base import BaseCommand

from datasets.tasks import process_one_dataset
from generation.tasks import process_one_revision

log = logging.getLogger("charter.worker")


class Command(BaseCommand):
    help = "Process pending datasets and chart revisions until stopped."

    def add_arguments(self, parser):
        parser.add_argument(
            "--once", action="store_true", help="Process at most one item, then exit."
        )
        parser.add_argument(
            "--interval", type=float, default=1.0, help="Idle poll interval, seconds."
        )

    def handle(self, *args, once: bool = False, interval: float = 1.0, **options):
        stop = False

        def on_signal(signum, frame):
            nonlocal stop
            stop = True

        signal.signal(signal.SIGTERM, on_signal)
        signal.signal(signal.SIGINT, on_signal)
        log.info("worker started")

        while not stop:
            did_work = process_one_dataset() or process_one_revision()
            if once:
                break
            if not did_work:
                time.sleep(interval)

        log.info("worker stopped")
