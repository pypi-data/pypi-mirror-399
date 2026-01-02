"""Test util functions"""

from datetime import date, datetime
from random import choice, sample
from typing import Generator, Sequence

import polars as pl
from pytest import raises

from babylab import api, utils
from tests import conftest


def test_fmt_labels_dict():
    x = {
        "source": "1",
        "sex": "2",
        "isdropout": "0",
        "age_now_months": "2",
        "birth_type": None,
    }

    o = api.fmt_labels(x)

    assert isinstance(o, dict)
    assert all(k in o for k in x)
    assert isinstance(o["source"], str)
    assert isinstance(o["sex"], str)
    assert isinstance(o["isdropout"], bool)
    assert isinstance(o["age_now_months"], int)

    assert o["source"] == "SJD Àrea de la Dona"
    assert o["sex"] == "Male"
    assert o["isdropout"] is False
    assert o["age_now_months"] == 2
    assert o["birth_type"] is None


def test_fmt_labels_polars():
    x = pl.DataFrame(
        data={
            "source": "1",
            "sex": "2",
            "isdropout": "0",
            "age_now_months": "2",
            "birth_type": None,
        },
    )

    o = api.fmt_labels(x)

    assert isinstance(o, pl.DataFrame)
    assert all(k in o for k in x.columns)

    assert o["source"][0] == "SJD Àrea de la Dona"
    assert o["sex"][0] == "Male"
    assert not o["isdropout"][0]
    assert o["age_now_months"][0] == 2
    assert o["birth_type"][0] is None


def test_get_ppt_table():
    df = utils.get_ppt_table(conftest.RECORDS)

    assert isinstance(df, pl.DataFrame)
    assert all(c in df.columns for c in utils.COLNAMES["participants"])


def test_get_ppt_table_study():
    for k in conftest.DATA_DICT["appointment_study"].items():
        df = utils.get_ppt_table(conftest.RECORDS, study=k)

        assert isinstance(df, pl.DataFrame)
        assert all(c in df.columns for c in utils.COLNAMES["participants"])


def test_get_ppt_table_id_list(ppt_id: str | list[str] | None = None, k: int = 100):
    if ppt_id is None:
        ppt_id = list(conftest.RECORDS.participants.records.keys())

    if isinstance(ppt_id, str):
        ppt_id = [ppt_id]

    df = utils.get_ppt_table(conftest.RECORDS, ppt_id=sample(ppt_id, k=k))

    assert isinstance(df, pl.DataFrame)
    assert all(c in df.columns for c in utils.COLNAMES["participants"])
    assert all(p in ppt_id for p in df["record_id"].unique().to_list())


def test_get_apt_table():
    df = utils.get_apt_table(conftest.RECORDS)

    assert isinstance(df, pl.DataFrame)


def test_get_apt_table_study():
    for k, v in conftest.DATA_DICT["appointment_study"].items():
        df = utils.get_apt_table(conftest.RECORDS, study=k)

        assert isinstance(df, pl.DataFrame)
        assert all(df["study"] == v)


def test_get_apt_table_id(ppt_id: str | None = None):
    if ppt_id is None:
        ppt_id = choice(list(conftest.RECORDS.participants.records.keys()))

    df = utils.get_apt_table(conftest.RECORDS, ppt_id=ppt_id)

    assert isinstance(df, pl.DataFrame)


def test_get_apt_table_id_list(apt_id: str | Sequence[str] | None = None, k: int = 100):
    if apt_id is None:
        apt_id = list(conftest.RECORDS.appointments.records.keys())

    if isinstance(apt_id, str):
        apt_id = [apt_id]

    ppt_id = set(i.split(":")[0] for i in apt_id)

    if k > len(ppt_id):
        k = len(ppt_id)

    df = utils.get_apt_table(conftest.RECORDS, ppt_id=sample(list(ppt_id), k=k))

    assert isinstance(df, pl.DataFrame)
    assert all(p in ppt_id for p in df["record_id"].unique().to_list())


def test_get_que_table():
    df = utils.get_que_table(conftest.RECORDS)

    assert isinstance(df, pl.DataFrame)


def test_get_que_table_id(ppt_id: str | list[str] | None = None):
    if ppt_id is None:
        ppt_id = choice(list(conftest.RECORDS.participants.records.keys()))

    df = utils.get_que_table(conftest.RECORDS, ppt_id=ppt_id)

    assert isinstance(df, pl.DataFrame)


def test_get_que_table_id_list(que_id: str | list[str] | None = None, k: int = 100):
    if que_id is None:
        que_id = list(conftest.RECORDS.appointments.records.keys())

    if isinstance(que_id, str):
        que_id = [que_id]

    ppt_id = set(i.split(":")[0] for i in que_id)

    if k > len(ppt_id):
        k = len(ppt_id)

    df = utils.get_apt_table(conftest.RECORDS, ppt_id=sample(list(ppt_id), k=k))
    assert isinstance(df, pl.DataFrame)
    assert all(p in ppt_id for p in df["record_id"].unique().to_list())


def test_is_in_data_dict():
    """Test is_in_datadict."""

    assert utils.is_in_data_dict("appointment_status", ["Successful"]) == ["Successful"]

    assert utils.is_in_data_dict(
        "appointment_status",
        ["Successful", "Confirmed"],
    ) == [
        "Successful",
        "Confirmed",
    ]

    assert utils.is_in_data_dict("appointment_status", "Successful") == ["Successful"]

    assert utils.is_in_data_dict("appointment_study", ["mop_newborns_1_nirs"]) == [
        "mop_newborns_1_nirs"
    ]

    assert utils.is_in_data_dict(
        "appointment_study", ["mop_newborns_1_nirs", "mop_infants_1_hpp"]
    ) == ["mop_newborns_1_nirs", "mop_infants_1_hpp"]

    assert utils.is_in_data_dict("appointment_study", "mop_newborns_1_nirs") == [
        "mop_newborns_1_nirs"
    ]

    with raises(ValueError):
        utils.is_in_data_dict("appointment_status", ["Badname"])
        utils.is_in_data_dict("appointment_status", ["Badname", "Successful"])
        utils.is_in_data_dict("appointment_status", "Badname")


def test_get_year_weeks():
    """Test get_year_weeks."""
    assert isinstance(utils.get_year_weeks(2025), Generator)
    assert isinstance(next(utils.get_year_weeks(2025)), date)


def test_get_week_n():
    """Test get_week_n."""
    assert isinstance(utils.get_week_n(datetime.today()), int)


def test_get_weekly_apts():
    """Test get_weekly_apts."""
    assert isinstance(
        utils.get_weekly_apts(records=conftest.RECORDS),
        int,
    )
    assert isinstance(
        utils.get_weekly_apts(records=conftest.RECORDS, study="mop_newborns_1_nirs"),
        int,
    )
    assert isinstance(
        utils.get_weekly_apts(
            records=conftest.RECORDS, study="mop_newborns_1_nirs", status="Successful"
        ),
        int,
    )
    assert isinstance(
        utils.get_weekly_apts(
            records=conftest.RECORDS,
            study=["mop_newborns_1_nirs", "mop_infants_1_hpp"],
        ),
        int,
    )
    assert isinstance(
        utils.get_weekly_apts(
            records=conftest.RECORDS,
            study=["mop_newborns_1_nirs", "mop_infants_1_hpp"],
            status=["Successful", "Confirmed"],
        ),
        int,
    )
