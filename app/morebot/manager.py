import requests
import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from app.db.models import Admin, User
from app.config import MOREBOT_LICENSE, MOREBOT_SECRET

logger = logging.getLogger("uvicorn.error")


class Morebot:
    _base_url = f"https://{MOREBOT_LICENSE}.morebot.top/api/subscriptions/{MOREBOT_SECRET}"
    _timeout = 3
    _failed_reports = defaultdict(int)

    @classmethod
    def get_users_limit(cls, username: str) -> Optional[int]:
        try:
            response = requests.get(
                url=f"{cls._base_url}/{username}/users_limit",
                timeout=cls._timeout,
            )
            logger.info(
                f"Morebot response: {response.status_code}, {response.text}"
            )
            response.raise_for_status()
            data = response.json()
            return data.get("users_limit", 0)
        except requests.RequestException:
            return 0

    @classmethod
    def report_admin_usage(
        cls, db: Session, users_usage: List[Dict[str, Any]]
    ) -> bool:
        if not users_usage:
            return True
        admin_usage = defaultdict(int)
        user_admin_map = dict(db.query(User.id, User.admin_id).all())
        for user_usage in users_usage:
            user_id = int(user_usage["id"])
            admin_id = user_admin_map.get(user_id)
            if admin_id:
                admin_usage[admin_id] += user_usage["value"]

        for admin_id, failed_usage in cls._failed_reports.items():
            admin_usage[admin_id] += failed_usage

        admins = dict(db.query(Admin.id, Admin.username).all())

        report_data = [
            {"username": admins.get(admin_id, "Unknown"), "usage": int(value)}
            for admin_id, value in admin_usage.items()
            if value > 0
        ]

        if not report_data:
            return True

        try:
            response = requests.post(
                f"{cls._base_url}/usages",
                json=report_data,
                timeout=cls._timeout,
            )
            response.raise_for_status()
            logger.info("Admin usage report successfully.")
            cls._failed_reports.clear()
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to upsert admin usage report: {str(e)}")
            cls._failed_reports = admin_usage
            return False
