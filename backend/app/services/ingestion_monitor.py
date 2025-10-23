
from collections import defaultdict

class IngestionMonitor:
    def __init__(self):
        self.stats = defaultdict(lambda: defaultdict(int))

    def log_success(self, source: str):
        self.stats[source]["success"] += 1

    def log_failure(self, source: str):
        self.stats[source]["failure"] += 1

    def get_stats(self):
        return self.stats

ingestion_monitor = IngestionMonitor()
