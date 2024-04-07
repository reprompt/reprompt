from datetime import datetime


class FunctionTrace:
    def __init__(self, func_name, request_details):
        self.func_name = func_name
        self.start_time = datetime.now()
        self.end_time = None
        self.duration = None
        self.request_details = request_details
        self.response_details = None

    def end_trace(self, response_details):
        self.response_details = response_details
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()

    def get_trace_info(self):
        return {
            "function_name": self.func_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.duration,
            "request_details": self.request_details,
            "response_details": self.response_details,
        }
