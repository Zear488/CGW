import random
from .tracker import GachaHistoryTracker
from .utils import run_gacha, get_tier_and_color
from logic.tracker import GachaHistoryTracker
tracker = GachaHistoryTracker()

def perform_gacha_draw(mode, min_val, avg, max_val, boost_transcendent=False):
    if boost_transcendent and tracker.get_points() < 5:
        boost_transcendent = False

    # Tirada normal
    result = run_gacha(mode, min_val, avg, max_val)

    if result:
        tier, color = get_tier_and_color(result["rarity"])
        pull_data = {
            "Type": result["type"],
            "Element": result["element"],
            "Rarity": f"{result['rarity']:.2f}",
            "Tier": tier,
            "Luck": f"{result['luck']:.2f}%",
            "Description": result["description"],
            "Color": color
        }

        # Comprobar repetición
        repeated = tracker.check_repeat(pull_data)
        pull_data["Repeated"] = repeated

        # Aplicar boost si hay puntos suficientes
        if boost_transcendent and not repeated:
            success = random.random() < 0.25  # 25% de chance de convertir a "Transcendent"
            if success:
                pull_data["Tier"] = "Transcendent"
                pull_data["Rarity"] = "10.00"
                pull_data["Color"] = "#ff0000"
                tracker.spend_points(5)

        return pull_data
    return None