"""Test database models."""

from datetime import datetime

from polars import DataFrame

from babylab import api
from tests import conftest

PPT_RECORD = conftest.create_record_ppt(is_new=True)
APT_RECORD = conftest.create_record_apt(is_new=True)
QUE_RECORD = conftest.create_record_que(is_new=True)


def test_participant_class():
    """Test participant class."""
    data = api.prepare_data(PPT_RECORD)
    x = api.Participant(data["record_id"], data)

    for att in ["ppt_id", "data"]:
        assert hasattr(x, att)

    assert isinstance(x.ppt_id, str)
    assert isinstance(x.data, dict)


def test_appointment_class():
    """Test appointment class."""
    data = api.prepare_data(APT_RECORD, "apt")
    x = api.Appointment(data["record_id"], data)

    for att in ["ppt_id", "apt_id", "date", "status", "data"]:
        assert hasattr(x, att)

    assert isinstance(x.ppt_id, str)
    assert isinstance(x.apt_id, str)
    assert isinstance(x.date, datetime)
    assert isinstance(x.status, str)
    assert isinstance(x.data, dict)


def test_questionnaire_class():
    """Test questionnaire class."""
    data = api.prepare_data(QUE_RECORD, "que")
    x = api.Questionnaire(data["record_id"], data)

    for att in ["ppt_id", "que_id", "isestimated", "data"]:
        assert hasattr(x, att)

    assert isinstance(x.ppt_id, str)
    assert isinstance(x.que_id, str)
    assert isinstance(x.isestimated, bool)
    assert isinstance(x.data, dict)


def test_records_class():
    """Test participant class."""
    assert hasattr(conftest.RECORDS, "appointments")
    assert hasattr(conftest.RECORDS, "participants")
    assert hasattr(conftest.RECORDS, "questionnaires")

    assert isinstance(conftest.RECORDS.appointments, api.RecordList)
    assert isinstance(conftest.RECORDS.participants, api.RecordList)
    assert isinstance(conftest.RECORDS.questionnaires, api.RecordList)

    assert isinstance(repr(conftest.RECORDS), str)
    assert "REDCap database" in repr(conftest.RECORDS)
    assert isinstance(str(conftest.RECORDS), str)
    assert "REDCap database" in str(conftest.RECORDS)


def test_recordlist_class_participants():
    """Test RecordList class with participants."""
    records = conftest.RECORDS.participants
    assert isinstance(records.records, dict)
    assert isinstance(api.to_df(records), DataFrame)
    assert isinstance(records.kind, str)
    assert records.kind == "participants"


def test_recordlist_class_appointments():
    """Test RecordList class with appointments."""
    records = conftest.RECORDS.appointments

    assert isinstance(records.records, dict)
    assert isinstance(api.to_df(records), DataFrame)
    assert isinstance(records.kind, str)
    assert records.kind == "appointments"


def test_recordlist_class_questionnaires():
    """Test RecordList class with questionnaires."""
    records = conftest.RECORDS.questionnaires

    assert isinstance(records.records, dict)
    assert isinstance(api.to_df(records), DataFrame)
    assert isinstance(records.kind, str)
    assert records.kind == "questionnaires"


def test_records_class_participants():
    """Test records class (Participants)"""
    assert hasattr(conftest.RECORDS.participants, "records")
    assert isinstance(conftest.RECORDS.participants.records, dict)
    assert all(
        isinstance(r, api.Participant)
        for r in conftest.RECORDS.participants.records.values()
    )


def test_records_class_appointments():
    """Test records class (Appointments)"""
    assert hasattr(conftest.RECORDS.appointments, "records")
    assert isinstance(conftest.RECORDS.appointments.records, dict)
    assert all(
        isinstance(r, api.Appointment)
        for r in conftest.RECORDS.appointments.records.values()
    )


def test_records_class_questionnaires():
    """Test records class (Questionnaires)"""
    assert hasattr(conftest.RECORDS.questionnaires, "records")
    assert isinstance(conftest.RECORDS.questionnaires.records, dict)
    assert all(
        isinstance(r, api.Questionnaire)
        for r in conftest.RECORDS.questionnaires.records.values()
    )
