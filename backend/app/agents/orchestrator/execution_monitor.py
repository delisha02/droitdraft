
from collections import defaultdict
import time

class ExecutionMonitor:
    def __init__(self):
        self.executions = defaultdict(list)

    def start_execution(self, workflow_name: str):
        execution_id = f"{workflow_name}-{int(time.time())}"
        self.executions[execution_id].append({"status": "started", "timestamp": time.time()})
        return execution_id

    def log_step(self, execution_id: str, step_name: str, status: str):
        self.executions[execution_id].append({"step": step_name, "status": status, "timestamp": time.time()})

    def end_execution(self, execution_id: str, status: str):
        self.executions[execution_id].append({"status": status, "timestamp": time.time()})

    def get_execution_history(self, execution_id: str):
        return self.executions.get(execution_id)

execution_monitor = ExecutionMonitor()
