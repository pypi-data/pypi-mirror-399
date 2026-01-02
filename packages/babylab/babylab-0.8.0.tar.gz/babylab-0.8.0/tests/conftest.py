"""
Fixtures for testing
"""

import os
from datetime import datetime
from random import choice, choices
from string import ascii_lowercase, digits

from babylab import api

IS_GIHTUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"
RECORDS: api.Records = api.Records()
DATA_DICT: dict = api.get_data_dict()


def generate_str(n: int = 7) -> str:
    """Generate random string of ASCII characters.

    Args:
        nchar (int, optional): Number of characters in the string. Defaults to 7.

    Returns:
        str: Random string of characters of length ``n``.
    """
    return "".join(choices(ascii_lowercase + digits, k=n))


def generate_phone() -> str:
    """Generate random phone number (no prefix).

    Returns:
        str: Random phone number.
    """
    return "".join([str(x) for x in choices(range(9), k=9)])


def generate_email() -> str:
    """Generate random e-mail address.

    Returns:
        str: Random e-mail address.
    """
    return generate_str() + "@" + generate_str() + ".com"


def generate_lang_exp():
    """Create vector of language exposures.

    Returns:
        list[float]: Vector of language exposures that adds up to 100.
    """
    nlangs = choice(range(1, 4))
    exp = [0] * 4
    for lang in range(1, nlangs):
        exp[lang] = choice(range(100 - sum(exp)))
    exp[-1] = 100 - sum(exp[:-1])
    exp.sort(reverse=True)
    return exp


def create_record_ppt(is_new: bool = True) -> dict:
    """Create a REDCap participant record.

    Args:
        is_new (bool): Should a new record be created? Defaults to True.

    Returns:
        dict: A REDCap record.
    """
    ppt_id = choice(list(RECORDS.participants.records.keys()))
    return {
        "record_id": api.get_next_id() if is_new else ppt_id,
        "participant_date_created": datetime(2024, 12, 16, 11, 13, 0),
        "participant_date_updated": datetime(2024, 12, 16, 11, 13, 0),
        "participant_name": generate_str(),
        "participant_age_created_months": choice(range(12)),
        "participant_age_created_days": choice(range(31)),
        "participant_sex": str(choice(range(1, 6))),
        "participant_source": str(choice(range(1, 3))),
        "participant_twin": "",
        "participant_parent1_name": generate_str(),
        "participant_parent1_surname": generate_str(),
        "participant_isdropout": choice(["0", "1"]),
        "participant_email1": generate_email(),
        "participant_phone1": generate_phone(),
        "participant_parent2_name": generate_str(),
        "participant_parent2_surname": generate_str(),
        "participant_email2": generate_email(),
        "participant_phone2": generate_str(),
        "participant_address": generate_str(),
        "participant_city": generate_str(),
        "participant_postcode": "".join([str(x) for x in choices(range(9), k=5)]),
        "participant_birth_type": choice(["1", "2"]),
        "participant_gest_weeks": str(choice(range(34, 43))),
        "participant_birth_weight": str(choice(range(2700, 4500))),
        "participant_head_circumference": str(choice(range(32, 38))),
        "participant_apgar1": str(choice(range(10))),
        "participant_apgar2": str(choice(range(10))),
        "participant_apgar3": str(choice(range(10))),
        "participant_hearing": choice(["1", "2"]),
        "participant_diagnoses": generate_str(50),
        "participant_comments": " ".join([generate_str(25) for _ in range(3)]),
        "participants_complete": "2",
    }


def create_record_apt(is_new: bool = True) -> dict:
    """Create a REDCap appointment record.

    Args:
        is_new (bool): Should a new record be created? Defaults to True.

    Returns:
        dict: A REDCap record.
    """
    ppd_id_list = list(RECORDS.participants.records.keys())
    ppt_id = choice(ppd_id_list)
    apt_recs = RECORDS.participants.records[ppt_id].appointments.records

    while not apt_recs:
        ppt_id = choice(ppd_id_list)
        apt_recs = RECORDS.participants.records[ppt_id].appointments.records

    apt_id = choice(list(apt_recs.keys()))

    return {
        "record_id": ppt_id,
        "redcap_repeat_instrument": "appointments",
        "redcap_repeat_instance": (
            api.get_next_id() if is_new else apt_id.split(":")[1]
        ),
        "appointment_study": choice(list(DATA_DICT["appointment_study"].keys())),
        "appointment_date_created": datetime(2024, 12, 12, 14, 9, 0),
        "appointment_date_updated": datetime(2024, 12, 14, 12, 8, 0),
        "appointment_date": datetime(2024, 12, 31, 14, 9, 0),
        "appointment_transport": choice(
            list(DATA_DICT["appointment_transport"].keys())
        ),
        "appointment_taxi_address": generate_str(),
        "appointment_taxi_isbooked": choice(["0", "1"]),
        "appointment_status": choice(list(DATA_DICT["appointment_status"].keys())),
        "appointment_comments": ". ".join([generate_str(25) for _ in range(3)]),
        "appointments_complete": "2",
    }


def create_record_que(is_new: bool = True) -> dict:
    """Create a REDCap questionnaire record.

    Args:
        is_new (bool): Should a new record be created? Defaults to True.

    Returns:
        dict: A REDCap record.
    """
    lang_exp = generate_lang_exp()
    ppt_id_list = list(RECORDS.participants.records.keys())
    ppt_id = choice(ppt_id_list)
    que_recs = RECORDS.participants.records[ppt_id].questionnaires.records

    while not que_recs:
        ppt_id = choice(ppt_id_list)
        que_recs = RECORDS.participants.records[ppt_id].questionnaires.records

    que_id = choice(list(que_recs.keys()))

    date = datetime(2024, 12, 12, 14, 24, 0)

    return {
        "record_id": ppt_id,
        "redcap_repeat_instrument": "language",
        "redcap_repeat_instance": (
            api.get_next_id() if is_new else que_id.split(":")[1]
        ),
        "language_date_created": date,
        "language_date_updated": date,
        "language_isestimated": choice(["0", "1"]),
        "language_lang1": choice(list(DATA_DICT["language_lang1"].keys())),
        "language_lang1_exp": lang_exp[0],
        "language_lang2": choice(list(DATA_DICT["language_lang2"].keys())),
        "language_lang2_exp": lang_exp[1],
        "language_lang3": choice(list(DATA_DICT["language_lang3"].keys())),
        "language_lang3_exp": lang_exp[2],
        "language_lang4": choice(list(DATA_DICT["language_lang4"].keys())),
        "language_lang4_exp": lang_exp[3],
        "language_comments": "",
        "language_complete": "2",
    }
