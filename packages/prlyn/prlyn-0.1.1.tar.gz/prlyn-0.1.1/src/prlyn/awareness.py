import json
import os
from typing import Optional
from prlyn.models import AnalysisResult


def apply_model_awareness(
    result: AnalysisResult, model_name: Optional[str] = None
) -> AnalysisResult:
    if not model_name:
        return result

    profiles_path = os.path.join(os.path.dirname(__file__), "model_profiles.json")
    if not os.path.exists(profiles_path):
        return result

    with open(profiles_path, "r") as f:
        profiles = json.load(f)

    profile = profiles.get(model_name.lower())
    if not profile:
        return result

    # Adjust Position Score based on model's middle context retrieval
    if result.position_score:
        retrieval = profile.get("middle_context_retrieval", "average")
        if retrieval == "poor" and result.position_score.buried_instructions:
            # Penalize the score further for models that "lose" the middle
            penalty = len(result.position_score.buried_instructions) * 0.1
            result.position_score.score = max(
                0.0, result.position_score.score - penalty
            )

    result.model_name = model_name
    return result
