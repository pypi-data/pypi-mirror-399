"""Test API."""

import os
from datetime import datetime

import pytest

from babylab import api
from tests import conftest

IS_GIHTUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


def test_get_api_key():
    """Test get_api_key."""
    token = api.get_api_key()
    assert token is not None
    assert isinstance(token, str)

    if not IS_GIHTUB_ACTIONS:
        token = api.get_api_key(path="~/.env")
        assert token is not None
        assert isinstance(token, str)


def test_redcap_version():
    """Test ``redcap_version``."""
    version = api.get_redcap_version()
    assert version
    assert isinstance(version, str)
    assert len(version.split(".")) == 3


def test_dt_to_str():
    """Test ``test_datetimes_to_str`` function."""
    data = {
        "date_now": datetime(2024, 10, 24, 8, 48, 34, 685496),
        "date_today": datetime(2024, 10, 24, 8, 48),
        "date_str": "2024-05-12T5:12",
    }
    result = api.dt_to_str(data)
    assert result["date_now"] == "2024-10-24T08:48:34.685496"
    assert result["date_today"] == "2024-10-24T08:48:00"
    assert result["date_str"] == data["date_str"]


def test_str_to_dt():
    """Test ``test_datetimes_to_str`` function."""
    data = {
        "date_now": "2024-05-12 05:34:15",
        "date_today": "2024-05-12 05:34",
    }
    result = api.str_to_dt(data)
    assert result["date_now"] == datetime(2024, 5, 12, 5, 34, 15)
    assert result["date_today"] == datetime(2024, 5, 12, 5, 34)


def test_get_data_dict():
    """Test ``get_records``."""
    data_dict = api.get_data_dict()
    assert isinstance(data_dict, dict)
    assert all(isinstance(v, dict) for v in data_dict.values())


def test_make_id():
    """Test ``make_id``"""
    assert api.make_id(1, 2) == "1:2"
    assert api.make_id(1) == "1"
    assert api.make_id("1", "2") == "1:2"
    assert api.make_id("1") == "1"
    with pytest.raises(ValueError):
        api.make_id(1, "a")
    with pytest.raises(ValueError):
        api.make_id(1, "1 ")
    with pytest.raises(ValueError):
        api.make_id("a")
    with pytest.raises(ValueError):
        api.make_id("1 ")
    with pytest.raises(ValueError):
        api.make_id("1:1")


def test_get_records():
    """Test ``get_records``."""
    records = api.get_records()
    assert isinstance(records, list)
    assert all(isinstance(r, dict) for r in records)


def test_add_participant():
    """Test adding,modifying, and deleting participants."""
    ppt_record = conftest.create_record_ppt(is_new=True)

    rid = ppt_record["record_id"]
    api.add_participant(ppt_record)
    assert isinstance(api.get_participant(rid), api.Participant)

    old_val = ppt_record["participant_apgar1"]
    new_val = int(old_val) + 1 if old_val != 10 else 1
    ppt_record["participant_apgar1"] = new_val
    api.add_participant(ppt_record, modifying=True)
    new_record = api.get_participant(rid)
    assert new_record.data["apgar1"] == new_val


def test_add_appointment():
    """Test adding appointments."""
    apt_record = conftest.create_record_apt(is_new=True)

    api.add_appointment(apt_record)
    rid = api.make_id(apt_record["record_id"], apt_record["redcap_repeat_instance"])
    assert isinstance(api.get_appointment(rid), api.Appointment)

    old_val = apt_record["appointment_status"]
    new_val = "1" if old_val != "1" else "1"
    apt_record["appointment_status"] = new_val
    api.add_appointment(apt_record)
    new_record = api.get_appointment(rid)
    new_val_label = conftest.DATA_DICT["appointment_status"][new_val]
    assert new_record.data["status"] == new_val_label


def test_add_questionnaire():
    """Test adding questionnaires."""
    que_record = conftest.create_record_que(is_new=True)

    api.add_questionnaire(que_record)
    rid = api.make_id(que_record["record_id"], que_record["redcap_repeat_instance"])
    assert isinstance(api.get_questionnaire(rid), api.Questionnaire)

    old_val = que_record["language_lang1"]
    new_val = str(1 if old_val == "0" else 0)
    que_record["language_lang1"] = new_val
    api.add_questionnaire(que_record)
    new_record = api.get_questionnaire(rid)
    new_val_label = conftest.DATA_DICT["language_lang1"][new_val]
    assert new_record.data["lang1"] == new_val_label


def test_parse_str_date():
    """Test parse_str_date."""
    hms = datetime(2025, 5, 2, 9, 10, 10)
    hm = datetime(2025, 5, 2, 9, 10)
    assert api.parse_str_date("2025-05-02T09:10:10") == hms
    assert api.parse_str_date("2025-05-02 09:10:10") == hms
    assert api.parse_str_date("2025-05-02 09:10") == hm


def test_get_age():
    """Test ``get_age``"""
    ts = datetime(2024, 5, 1, 3, 4)
    ts_new = datetime(2025, 1, 4, 1, 2)
    age = (5, 5)

    # when only birth date is provided
    assert isinstance(api.get_age(age, ts), tuple)
    assert all(isinstance(d, int) for d in api.get_age(age, ts))
    assert len(api.get_age(age, ts)) == 2

    # when birth date AND ts_new are provided
    assert isinstance(api.get_age(age, ts, ts_new=ts_new), tuple)
    assert all(isinstance(d, int) for d in api.get_age(age, ts, ts_new))
    assert len(api.get_age(age, ts, ts_new)) == 2

    assert api.get_age(age, ts, ts_new) == (13, 7)

    assert all(d > 0 for d in api.get_age(age, ts, ts_new))
    with pytest.raises(api.BadAgeFormat):
        api.get_age(age="5, 4", ts=ts)  # ty: ignore[invalid-argument-type]
