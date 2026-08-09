from pydantic import BaseModel
from typing import Dict, Any, List


class StatsResponse(BaseModel):
    processed: int
    tasks_created: int
    tasks_updated: int
    skipped: int
    spurious_count: int
    spurious_rate: float
    categories: Dict[str, int]
    assignees: Dict[str, int]
    priorities: Dict[str, int]
    total_deal_value_inr: int
    rfps_with_no_stated_value: int
    threads_updated_multiple_times: List[str]
