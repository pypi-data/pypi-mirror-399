def apply_payer_rules(payer: str, text: str, baseline: dict) -> dict:
    # Dummy logic for now — replace with real parsing
    if "UHC" in text or "UnitedHealthcare" in text:
        baseline["payer"] = "UnitedHealthcare"
        baseline["member_id"] = "999999876"
        baseline["group_number"] = "IB7654"
        baseline["plan_name"] = "Choice Plus"
    elif "Cigna" in text:
        baseline["payer"] = "Cigna"
        baseline["member_id"] = "ABC123456"
        baseline["group_number"] = "789XYZ"
        baseline["plan_name"] = "Open Access Plus"
    return baseline