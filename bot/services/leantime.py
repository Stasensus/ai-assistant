import requests
from datetime import date
from bot.config import LEANTIME_URL, LEANTIME_API_KEY, LEANTIME_INBOX_PROJECT_ID

PRIORITY_MAP = {"high": "3", "medium": "2", "low": "1"}


class LeantimeClient:
    def __init__(self, url: str, api_key: str, inbox_project_id: int):
        self.url = url.rstrip("/") + "/api/jsonrpc"
        self.headers = {"x-api-key": api_key, "Content-Type": "application/json"}
        self.inbox_project_id = inbox_project_id

    def _call(self, method: str, params: dict) -> dict:
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        resp = requests.post(self.url, json=payload, headers=self.headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            raise RuntimeError(f"Leantime API error: {data['error']}")
        return data.get("result", {})

    def create_task(self, title: str, project_id: int = None,
                    priority: str = "medium", due_date: str = None,
                    description: str = "", tags: list = None) -> int:
        params = {
            "headline": title,
            "description": description or "",
            "projectId": project_id or self.inbox_project_id,
            "priority": PRIORITY_MAP.get(priority, "2"),
            "status": "new",
            "tags": ",".join(tags) if tags else "",
        }
        if due_date:
            params["dateToFinish"] = due_date
        result = self._call("leantime.rpc.Tickets.addTicket", params)
        return result.get("id") or result

    def complete_task(self, task_id: int) -> None:
        self._call("leantime.rpc.Tickets.patchTicket",
                   {"id": task_id, "status": "done"})

    def set_waiting(self, task_id: int, waiting_for: str) -> None:
        self._call("leantime.rpc.Tickets.patchTicket", {
            "id": task_id,
            "status": "waiting",
            "description": f"Жду ответа от: {waiting_for}",
        })

    def reschedule_task(self, task_id: int, due_date: str) -> None:
        self._call("leantime.rpc.Tickets.patchTicket",
                   {"id": task_id, "dateToFinish": due_date})

    def get_today_tasks(self) -> list:
        today = date.today().isoformat()
        result = self._call("leantime.rpc.Tickets.getAll", {
            "dateToFinish": today,
            "status": "inprogress,new",
        })
        if isinstance(result, list):
            return result
        return result.get("tickets", [])

    def get_last_active_task(self) -> dict | None:
        tasks = self._call("leantime.rpc.Tickets.getAll", {"status": "inprogress"})
        items = tasks if isinstance(tasks, list) else tasks.get("tickets", [])
        return items[0] if items else None


_client = None


def get_leantime() -> LeantimeClient:
    global _client
    if _client is None:
        _client = LeantimeClient(LEANTIME_URL, LEANTIME_API_KEY, LEANTIME_INBOX_PROJECT_ID)
    return _client
