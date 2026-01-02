def validate_member_id(payer: str, member_id: str) -> bool:
    if payer == "UnitedHealthcare":
        return member_id.isdigit() and len(member_id) == 9
    elif payer == "Cigna":
        return member_id.startswith("ABC")
    return True

def validate_group_number(payer: str, group_number: str) -> bool:
    return group_number is not None and len(group_number) >= 5