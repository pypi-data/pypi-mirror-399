from .rules import apply_payer_rules
from .validation import validate_member_id, validate_group_number
from .specialty import detect_specialty

def extract_fields(text: str) -> dict:
    baseline = {
        "payer": None,
        "specialty": detect_specialty(text),
        "member_id": None,
        "group_number": None,
        "plan_name": None,
        "policy_holder_name": None,
        "extra": {},
    }
    return apply_payer_rules(baseline["payer"], text, baseline)

def validate_fields(data: dict) -> dict:
    payer = data.get("payer")
    data["member_id_validation"] = validate_member_id(payer, data.get("member_id"))
    data["group_number_validation"] = validate_group_number(payer, data.get("group_number"))
    return data