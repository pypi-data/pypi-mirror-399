from ksero_payer_rules import extract_fields, validate_fields

def test_uhc_card():
    text = "UHC Member ID: 999999876 Group: IB7654"
    baseline = extract_fields(text)
    validated = validate_fields(baseline)

    assert validated["payer"] == "UnitedHealthcare"
    assert validated["member_id_validation"] is True
    assert validated["group_number_validation"] is True