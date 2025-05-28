import os
import json
from typing import List, Dict

GACHA_LOG_DIR = "gacha_log"
REPEATS_FILE = os.path.join(GACHA_LOG_DIR, "repeats.json")
POINTS_FILE = os.path.join(GACHA_LOG_DIR, "points.json")

class GachaHistoryTracker:
    def __init__(self):
        os.makedirs(GACHA_LOG_DIR, exist_ok=True)
        self.repeats = self._load_json(REPEATS_FILE, default={})
        self.points = self._load_json(POINTS_FILE, default={"points": 0})

    def _load_json(self, path: str, default):
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return default

    def _save_json(self, path: str, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def check_repeat(self, pull: Dict) -> bool:
        key = f"{pull['Type']}::{pull['Element']}"
        if key in self.repeats:
            self.points["points"] += 1
            self._save_json(POINTS_FILE, self.points)
            return True
        self.repeats[key] = True
        self._save_json(REPEATS_FILE, self.repeats)
        return False

    def get_points(self) -> int:
        return self.points.get("points", 0)

    def spend_points(self, cost: int) -> bool:
        if self.points["points"] >= cost:
            self.points["points"] -= cost
            self._save_json(POINTS_FILE, self.points)
            return True
        return False