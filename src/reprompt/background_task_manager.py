import asyncio


class BackgroundTaskManager:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.tasks = []

    def run_background(self, coro):
        """Schedule a coroutine to run in the background."""
        task = self.loop.create_task(coro)
        self.tasks.append(task)

        # Optional: add a callback to handle task completion (e.g., logging or cleanup)
        task.add_done_callback(self._task_done)

    def _task_done(self, task):
        """Handle a task's completion."""
        self.tasks.remove(task)
        if task.exception():
            # Handle exceptions (if any) here
            print(f"Task resulted in exception: {task.exception()}")


# You can keep a global instance or manage lifecycles differently depending on your library's architecture
background_task_manager = BackgroundTaskManager()
