import os
import json
import re
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
    def clear_all(self):
            self.repeats = {}
            self.points = {"points": 0}
            self._save_json(REPEATS_FILE, self.repeats)
            self._save_json(POINTS_FILE, self.points)
    def load_from_log(self, log: List[Dict]):
        self.repeats = {f"{entry['Type']}::{entry['Element']}": True for entry in log}
        self._save_json(REPEATS_FILE, self.repeats)

        total_points = 0
        for entry in log:
            notes = str(entry.get("Notes", "")).strip()

        # Aceptar variantes de "Repeated" aunque el emoji esté dañado
            if "Repeated" in notes:
                total_points += 1

        # Aceptar cualquier "- X TP"
            match = re.search(r"-\s*(\d+)\s*TP", notes)
            if match:
                total_points -= int(match.group(1))

        self.points = {"points": total_points}
        self._save_json(POINTS_FILE, self.points)
