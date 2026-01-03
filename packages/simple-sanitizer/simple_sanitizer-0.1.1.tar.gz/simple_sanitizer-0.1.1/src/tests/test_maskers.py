from simple_sanitizer import mask_phone_number


def test_mask_phone_number():
    assert mask_phone_number("13800138000") == "138****8000"
    assert mask_phone_number(" +8613800138000 ") == "+86138****8000"
    assert mask_phone_number(None) == ""
    assert mask_phone_number("110") == "110"
