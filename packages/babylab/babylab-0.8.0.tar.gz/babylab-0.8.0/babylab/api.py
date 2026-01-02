#!/usr/bin/env python

"""
Functions to interact with the REDCap API.
"""

from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import singledispatch
from json import dump, dumps, loads
from os import environ, getenv, walk
from os.path import join
from pathlib import Path
from typing import Sequence
from warnings import warn
from zipfile import ZIP_DEFLATED, ZipFile

import polars as pl
import pytz
import requests
from dateutil.relativedelta import relativedelta as rdelta
from dotenv import find_dotenv, load_dotenv

from babylab.globals import COLNAMES, FIELDS_TO_RENAME, INT_FIELDS, SCHEMA, URI


class MissingEnvFile(Exception):
    """.env file is not found in user folder"""


class MissingEnvToken(Exception):
    """Token is not provided as key in .env"""


class MissingRecord(Exception):
    """Record is not found"""


class BadToken(Exception):
    """Token is ill-formed"""


class BadAgeFormat(Exception):
    """If age does not follow the right format"""


@dataclass
class RecordList:
    """List of REDCap records."""

    records: dict = field(default_factory=dict)
    kind: str | None = None

    def __len__(self) -> int:
        return len(self.records)


@dataclass
class Record:
    ppt_id: str
    data: dict


@dataclass
class Participant(Record):
    appointments: RecordList = field(default_factory=list)
    questionnaires: RecordList = field(default_factory=list)


@dataclass
class Appointment(Record):
    def __post_init__(self):
        apt_id = self.data["redcap_repeat_instance"]
        self.apt_id = make_id(self.ppt_id, apt_id)
        self.status: str = self.data["status"]
        self.date: str = parse_str_date(self.data["date"])


@dataclass
class Questionnaire(Record):
    def __post_init__(self):
        que_id = self.data["redcap_repeat_instance"]
        self.que_id = make_id(self.ppt_id, que_id)
        self.isestimated = self.data["isestimated"]


def get_api_key(path: Path | str | None = None, name: str = "API_KEY") -> str:
    """Retrieve API credentials.

    Args:
        path (Path | str | None, optional): Path to the .env file with global variables. Defaults to ``Path.home()``.
        name (str, optional): Name of the variable to import. Defaults to "API_KEY".

    Returns:
        str: API key token.

    Raises:
        MissingEnvFile: If .env file is not found  in ``path``.
        MissingEnvToken: If requested environmental variable key is not found.
        BadToken: If token contains any non-alphanumeric character.
    """
    if name in environ or getenv("GITHUB_ACTIONS") == "true":
        token = getenv(name)
    else:
        path = Path(find_dotenv()) if not path else Path(path)

        if not path.exists():
            raise MissingEnvFile(f".env file not found in {path}")

        load_dotenv(path, override=True)
        token = getenv(name)

    if token is None:
        raise MissingEnvToken(f"No environment variable named '{name}' found")

    if not isinstance(token, str) or not token.isalnum():
        raise BadToken("Token must be str with no non-alphanumeric characters")

    return token


def post_request(fields: dict, timeout: Sequence[int] = (5, 10)) -> requests.Response:
    """Make a POST request to the REDCap database.

    Args:
        fields (dict): Fields to retrieve.
        timeout (Sequence[int], optional): Timeout of HTTP request in seconds. Defaults to 10.

    Raises:
        requests.exceptions.HTTPError: If HTTP request fails.
        BadToken: If API token contains non-alphanumeric characters.

    Returns:
        requests.Response: HTTP request response in JSON format.
    """
    t = get_api_key()

    if t is None:
        raise MissingEnvToken("No key found in your .env file")

    fields = OrderedDict(fields)
    fields["token"] = t
    fields.move_to_end("token", last=False)

    r = requests.post(URI, data=fields, timeout=timeout)
    r.raise_for_status()

    return r


def get_data_dict() -> dict:
    """Get data dictionaries for categorical variables.

    Returns:
        dict: Data dictionary.
    """
    fields = {"content": "metadata", "format": "json", "returnFormat": "json"}

    for idx, i in enumerate(FIELDS_TO_RENAME):
        fields[f"fields[{idx}]"] = i

    r = loads(post_request(fields=fields).text)
    items_ordered = [i["field_name"] for i in r]
    dicts = {}

    for k, v in zip(items_ordered, r, strict=False):
        options = v["select_choices_or_calculations"].split("|")
        options = [tuple(o.strip().split(", ")) for o in options]

        if k.startswith("language_"):
            options = sorted(options, key=lambda x: x[1])

        dicts[k] = dict(options)

    return dicts


DATA_DICT: dict = get_data_dict()


def get_redcap_version() -> str:
    """Get REDCap version.

    Returns:
        str: REDCAp version number.
    """
    fields = {"content": "version"}
    r = post_request(fields=fields)

    return r.content.decode("utf-8")


def to_df(x: RecordList) -> pl.DataFrame:
    """Transforms a RecordList to a Polars DataFrame.

    Returns:
        pl.DataFrame: Tabular data frame.
    """
    recs = [p.data for p in x.records.values()]
    names = COLNAMES[x.kind]

    if not recs:
        return pl.DataFrame(schema=names)

    id_lookup = {
        "participants": "none",
        "appointments": "apt_id",
        "questionnaires": "que_id",
    }

    df = (
        pl.DataFrame(recs, schema=SCHEMA[x.kind])
        .rename({"redcap_repeat_instance": id_lookup[x.kind]}, strict=False)
        .with_columns(
            pl.when(pl.col(pl.String).str.len_chars() == 0)
            .then(None)
            .otherwise(pl.col(pl.String))
            .name.keep()
        )
        .with_columns(
            pl.col(
                [f for f in INT_FIELDS if f in names],
            ).cast(pl.Int128)
        )
    )

    return df


def filter_fields(data: dict, prefix: str, fields: list[str]) -> dict:
    """Filter a data dictionary based on a prefix and field names.

    Args:
        records (dict): Record data dictionary.
        prefix (str): Prefix to look for.
        fields (list[str]): Field names to look for.

    Returns:
        dict: Filtered records.
    """
    return {
        k.replace(prefix, ""): v
        for k, v in data.items()
        if k.startswith(prefix) or k in fields
    }


@singledispatch
def fmt_labels(x: dict | pl.DataFrame):
    """Reformat dataframe.

    Args:
        x (dict | DataFrame): Dataframe to reformat.
        prefixes (list[str]): List of prefixes to look for in variable names.

    Returns:
        DataFrame: A reformated Dataframe.
    """
    raise TypeError("`x` must be a dict or a DataFrame")


@fmt_labels.register(dict)
def _(x: dict) -> dict:
    """Reformat dictionary.

    Args:
        x (dict): dictionary to reformat.

    Returns:
        dict: A reformatted dictionary.
    """
    fields = ["participant_", "appointment_", "language_"]
    y = dict(x)

    for k, v in y.items():
        for f in fields:
            if f + k in DATA_DICT and v:
                y[k] = DATA_DICT[f + k][v]

        if "exp" in k:
            y[k] = round(float(v), None) if v else None

        for c in ["taxi_isbooked", "isdropout", "isestimated"]:
            if c in k:
                y[k] = y[c] == "1"

        y[k] = y[k] if y[k] != "" else None

    y = {k: (int(v) if v and k in INT_FIELDS else v) for k, v in y.items()}

    return y


@fmt_labels.register(pl.DataFrame)
def _(x: pl.DataFrame) -> pl.DataFrame:
    """Reformat DataFrame.

    Args:
        x (dict): dictionary to reformat.

    Returns:
        DataFrame: A reformatted DataFrame.
    """
    cols = {k.rsplit("_", 1)[1]: v for k, v in DATA_DICT.items()}

    for k, v in {ck: cv for ck, cv in cols.items() if ck in x.columns}.items():
        x = x.with_columns(pl.col(k).replace_strict(v, default=None))

    for c in ["isestimated", "isdropout"]:
        if c in x.columns:
            x = x.with_columns(pl.col(c).eq("1"))

    x = x.with_columns(
        pl.when(pl.col(pl.String).str.len_chars() == 0)
        .then(None)
        .otherwise(pl.col(pl.String))
        .name.keep()
    ).cast({c: pl.Int64 for c in [f for f in INT_FIELDS if f in x.columns]})

    return x


def str_to_dt(data: dict) -> dict:
    """Parse strings in a dictionary as formatted datetimes.

    It first tries to format the date as "Y-m-d H:M:S". If error, it assumes the "Y-m-d H:M" is due and tries to format it accordingly.

    Args:
        data (dict): Dictionary that may contain string formatted datetimes.

    Returns:
        dict: Dictionary with strings parsed as datetimes.
    """
    for k, v in data.items():
        if v and "date" in k:
            try:
                data[k] = datetime.strptime(data[k], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                data[k] = datetime.strptime(data[k], "%Y-%m-%d %H:%M")

    return data


def dt_to_str(data: dict) -> dict:
    """Format datatimes in a dictionary as strings following the ISO 8061 date format.

    Args:
        data (dict): Dictionary that may contain datetimes.

    Returns:
        dict: Dictionary with datetimes formatted as strings.
    """
    for k, v in data.items():
        if isinstance(v, datetime):
            data[k] = data[k].isoformat()

    return data


def get_next_id() -> str:
    """Get next record_id in REDCap database.

    Returns:
        str: record_id of next record.
    """
    fields = {"content": "generateNextRecordName"}

    return str(post_request(fields=fields).json())


def prepare_data(x: dict, kind: str = "ppt") -> dict:
    """Prepare data for class.

    Args:
        x (dict): Participant data retrieved from REDCap.
        kind (str): Type of data to process. Takes "ppt" (default), "apt" or "que".

    Returns:
        dict: Formatted data.

    Raises:
        ValueError: If ``kind`` is not one of 'ppt', 'apt', or 'que'.
    """
    if kind not in ["ppt", "apt", "que"]:
        raise ValueError("`kind` must be one of 'ppt', 'apt', or 'que'")

    if kind == "apt":
        names = ["record_id", "redcap_repeat_instance"]
        x = filter_fields(x, "appointment_", names)

    if kind == "que":
        names = ["record_id", "redcap_repeat_instance"]
        x = filter_fields(x, "language_", names)
        for i in range(1, 5):
            lang = f"lang{i}_exp"
            x[lang] = int(x[lang]) if x[lang] else 0

    if kind == "ppt":
        names = ["record_id"]
        x = filter_fields(x, "participant_", names)
        age_created = (x["age_created_months"], x["age_created_days"])
        months, days = get_age(age_created, x["date_created"])
        x["age_now_months"], x["age_now_days"] = months, days

    return fmt_labels(x)


def make_id(ppt_id: str | int, repeat_id: str | int | None = None) -> str:
    """Make a record ID.

    Args:
        ppt_id (str | int): Participant ID.
        repeat_id (str | int | None, optional): Appointment or Questionnaire ID, or ``redcap_repeated_id``. Defaults to None.

    Returns:
        str: Record ID.
    """
    ppt_id = str(ppt_id)

    if not ppt_id.isdigit():
        raise ValueError(f"`ppt_id`` must be a digit, but '{ppt_id}' was provided")

    if not repeat_id:
        return ppt_id

    repeat_id = str(repeat_id)

    if not repeat_id.isdigit():
        raise ValueError(
            f"`repeat_id`` must be a digit, but '{repeat_id}' was provided"
        )

    return ppt_id + ":" + repeat_id


def get_records(record_id: str | list | None = None) -> dict:
    """Return records as JSON.

    Args:
        record_id  (str): ID of record to retrieve. Defaults to None.

    Returns:
        list[dict[str, str]]: REDCap records in JSON format.
    """
    fields = {"content": "record", "format": "json", "type": "flat"}

    if record_id and isinstance(record_id, list):
        fields["records[0]"] = record_id

        for r in record_id:
            fields[f"records[{record_id}]"] = r

    return post_request(fields=fields).json()


def get_participant(ppt_id: str) -> Participant:
    """Get participant record.

    Args:
        ppt_id: ID of participant (record_id).

    Returns:
        Participant: Participant object.

    Raises:
        MissingRecord: If requested recording is missing in the database.
    """
    fields = {
        "content": "record",
        "action": "export",
        "format": "json",
        "type": "flat",
        "csvDelimiter": "",
        "records[0]": ppt_id,
        "rawOrLabel": "raw",
        "rawOrLabelHeaders": "raw",
        "exportCheckboxLabel": "false",
        "exportSurveyFields": "false",
        "exportDataAccessGroups": "false",
        "returnFormat": "json",
    }

    for i, f in enumerate(["participants", "appointments", "language"]):
        fields[f"forms[{i}]"] = f

    recs = [str_to_dt(r) for r in post_request(fields).json()]
    apt, que = {}, {}

    for r in recs:
        ppt_id = r["record_id"]
        repeat_id = make_id(ppt_id, r["redcap_repeat_instance"])

        if r["redcap_repeat_instrument"] == "appointments":
            data = prepare_data(r, "apt")
            apt[repeat_id] = Appointment(ppt_id=ppt_id, data=data)

        if r["redcap_repeat_instrument"] == "language":
            data = prepare_data(r, "que")
            que[repeat_id] = Questionnaire(ppt_id=ppt_id, data=data)

    try:
        data = prepare_data(recs[0])

        return Participant(
            ppt_id=data["record_id"],
            data=data,
            appointments=RecordList(apt, kind="appointments"),
            questionnaires=RecordList(que, kind="questionnaires"),
        )
    except IndexError as e:
        raise MissingRecord(f"Record {ppt_id} not found") from e


def get_appointment(apt_id: str) -> Appointment:
    """Get appointment record.

    Args:
        apt_id (str): ID of appointment (``redcap_repeated_id``).

    Returns:
        Appointment: Appointment object.

    Raises:
        MissingRecord: If requested record is missing from database.
    """
    ppt_id, _ = apt_id.split(":")
    ppt = get_participant(ppt_id)

    try:
        return ppt.appointments.records[apt_id]
    except KeyError as e:
        raise MissingRecord(f"Record {apt_id} not found") from e


def get_questionnaire(que_id: str) -> Questionnaire:
    """Get questionnaire record.

    Args:
        que_id (str): ID of appointment (``redcap_repeated_id``).

    Returns:
        Questionnaire: Appointment object.
    """
    ppt_id, _ = que_id.split(":")
    ppt = get_participant(ppt_id)

    try:
        return ppt.questionnaires.records[que_id]
    except KeyError as e:
        raise MissingRecord(f"Record {que_id} not found") from e


def add_participant(data: dict, modifying: bool = False):
    """Add new participant to REDCap database.

    Args:
        data (dict): Participant data.
        modifying (bool, optional): Modifying existent participant?
    """
    fields = {
        "content": "record",
        "action": "import",
        "format": "json",
        "type": "flat",
        "overwriteBehavior": "normal" if modifying else "overwrite",
        "forceAutoNumber": "false" if modifying else "true",
        "data": f"[{dumps(dt_to_str(data))}]",
    }

    return post_request(fields=fields)


def delete_participant(data: dict):
    """Delete participant from REDCap database.

    Args:
        data (dict): Participant data.
        modifying (bool, optional): Modifying existent participant?
    """
    fields = {
        "content": "record",
        "action": "delete",
        "returnFormat": "json",
        "instrument": "",
        "records[0]": f"{data['record_id']}",
    }

    r = post_request(fields=fields)
    try:
        r.raise_for_status()
        return r
    except requests.exceptions.HTTPError as e:
        rid = make_id(data["record_id"])
        raise MissingRecord(f"Record {rid} not found") from e


def add_appointment(data: dict):
    """Add new appointment to REDCap database.

    Args:
        record_id (dict): ID of participant.
        data (dict): Appointment data.
    """
    fields = {
        "content": "record",
        "action": "import",
        "format": "json",
        "type": "flat",
        "overwriteBehavior": "overwrite",
        "forceAutoNumber": "false",
        "data": f"[{dumps(dt_to_str(data))}]",
    }

    return post_request(fields=fields)


def delete_appointment(data: dict):
    """Delete appointment from REDCap database.

    Args:
        data (dict): Participant data.
        modifying (bool, optional): Modifying existent participant?
    """
    fields = {
        "content": "record",
        "action": "delete",
        "returnFormat": "json",
        "instrument": "appointments",
        "repeat_instance": int(data["redcap_repeat_instance"]),
        f"records[{data['record_id']}]": f"{data['record_id']}",
    }

    r = post_request(fields=fields)
    warn_missing_record(r)

    return r


def add_questionnaire(data: dict):
    """Add new questionnaire to REDCap database.

    Args:
        data (dict): Questionnaire data.
    """
    fields = {
        "content": "record",
        "action": "import",
        "format": "json",
        "type": "flat",
        "overwriteBehavior": "overwrite",
        "forceAutoNumber": "false",
        "data": f"[{dumps(dt_to_str(data))}]",
    }

    return post_request(fields=fields)


def delete_questionnaire(data: dict):
    """Delete questionnaire from REDCap database.

    Args:
        data (dict): Participant data.
        modifying (bool, optional): Modifying existent participant?
    """
    fields = {
        "content": "record",
        "action": "delete",
        "returnFormat": "json",
        "instrument": "language",
        "repeat_instance": int(data["redcap_repeat_instance"]),
        f"records[{data['record_id']}]": f"{data['record_id']}",
    }

    r = post_request(fields=fields)
    warn_missing_record(r)
    return r


def warn_missing_record(r: requests.models.Response):
    """Warn user about absent record.

    Args:
        r (requests.models.Response): HTTPS response.
    """
    if "registros proporcionados no existen" in r.content.decode():
        warn("Record does not exist!", stacklevel=2)


def redcap_backup(path: Path | str = Path("tmp")) -> Path:
    """Download a backup of the REDCap database

    Args:
        path (Path | str, optional): Output directory. Defaults to ``Path("tmp")``.

    Returns:
        Path: Path to the generated file with data and metadata of the project.
    """
    path = Path(path)
    path.mkdir(exist_ok=True)

    p = {}
    for k in ["project", "metadata", "instrument"]:
        p[k] = {"format": "json", "returnFormat": "json", "content": k}

    d = {k: loads(post_request(v).text) for k, v in p.items()}

    with open(path / "records.csv", "w+", encoding="utf-8") as f:
        fields = {
            "content": "record",
            "action": "export",
            "format": "csv",
            "csvDelimiter": ",",
            "returnFormat": "json",
        }
        records = post_request(fields).content.decode().split("\n")
        records = [r + "\n" for r in records]
        f.writelines(records)

    b = {
        "project": d["project"],
        "instruments": d["instrument"],
        "fields": d["metadata"],
    }

    for k, v in b.items():
        with open(path / (k + ".json"), "w", encoding="utf-8") as f:
            dump(v, f)

    timestamp = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M")
    file = path / ("backup_" + timestamp + ".zip")

    for root, _, files in walk(str(path), topdown=False):
        with ZipFile(file, "w", ZIP_DEFLATED) as z:
            for f in files:
                z.write(join(root, f))

    return file


class Records:
    """REDCap records"""

    def __init__(self, record_id: str | list | None = None):
        records = get_records(record_id)
        records = [str_to_dt(r) for r in records]
        ppt, apt, que = {}, {}, {}

        for r in records:
            ppt_id = r["record_id"]
            repeat_id = r["redcap_repeat_instance"]

            if repeat_id and r["appointment_status"]:
                apt_id = make_id(ppt_id, repeat_id)
                r["appointment_id"] = apt_id
                data = prepare_data(r, "apt")

                apt[apt_id] = Appointment(ppt_id=data["record_id"], data=data)

            if repeat_id and r["language_lang1"]:
                que_id = make_id(ppt_id, repeat_id)
                r["questionnaire_id"] = que_id
                data = prepare_data(r, "que")

                que[que_id] = Questionnaire(ppt_id=ppt_id, data=data)

            if not r["redcap_repeat_instrument"]:
                data = prepare_data(r)
                ppt[ppt_id] = Participant(r["record_id"], data)

        # add appointments and questionnaires to each participant
        for p, v in ppt.items():
            apts = {k: v for k, v in apt.items() if v.ppt_id == p}
            v.appointments = RecordList(apts, kind="appointments")
            ques = {k: v for k, v in que.items() if v.ppt_id == p}
            v.questionnaires = RecordList(ques, kind="questionnaires")

        self.participants = RecordList(ppt, kind="participants")
        self.appointments = RecordList(apt, kind="appointments")
        self.questionnaires = RecordList(que, kind="questionnaires")

    def __repr__(self) -> str:
        return (
            "REDCap database:"
            + f"\n- {len(self.participants.records)} participants"
            + f"\n- {len(self.appointments.records)} appointments"
            + f"\n- {len(self.questionnaires.records)} questionnaires"
        )

    def __str__(self) -> str:
        return (
            "REDCap database:"
            + f"\n- {len(self.participants.records)} participants"
            + f"\n- {len(self.appointments.records)} appointments"
            + f"\n- {len(self.questionnaires.records)} questionnaires"
        )


def parse_age(age: tuple) -> tuple[int, int]:
    """Validate age string or tuple.

    Args:
        age (tuple): Age of the participant as a tuple in the ``(months, days)`` format.

    Raises:
        ValueError: If age is not str or tuple.
        BadAgeFormat: If age is ill-formatted.

    Returns:
        tuple[int, int]: Age of the participant in the ``(months, days)`` format.
    """
    try:
        assert isinstance(age, tuple)
        assert len(age) == 2

        return int(age[0]), int(age[1])
    except AssertionError as e:
        raise BadAgeFormat("age must be in (months, age) format") from e


def parse_str_date(x: str | datetime) -> datetime:
    """Parse string data to datetime.

    Args:
        x (str | datetime): String date to parse.

    Returns:
        datetime: Parsed datetime.
    """
    if isinstance(x, datetime):
        return x

    try:
        return datetime.strptime(x, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        try:
            return datetime.strptime(x, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.strptime(x, "%Y-%m-%d %H:%M")


def get_age(
    age: tuple, ts: datetime | str, ts_new: datetime | None = None, tz: str = "UTC"
):
    """Calculate the age of a person in months and days at a new timestamp.

    Args:
        age (tuple): Age in months and days as a tuple of type (months, days).
        ts (datetime | str): Birth date as ``datetime.datetime`` type.
        ts_new (datetime.datetime | None, optional): Time for which the age is calculated. Defaults to current date (``datetime.datetime.now()``).

    Returns:
        tuple: Age in at ``new_timestamp``.
    """
    tz = pytz.timezone(tz)
    ts = tz.localize(parse_str_date(ts))
    ts_new = datetime.now() if ts_new is None else ts_new
    ts_new = tz.localize(ts_new)

    tdiff = rdelta(ts_new, ts)
    months, days = parse_age(age)
    new_age_months = months + tdiff.years * 12 + tdiff.months
    new_age_days = days + tdiff.days

    if new_age_days >= 30:
        additional_months = new_age_days // 30
        new_age_months += additional_months
        new_age_days %= 30

    return new_age_months, new_age_days


if __name__ == "__main__":
    r = Records()
