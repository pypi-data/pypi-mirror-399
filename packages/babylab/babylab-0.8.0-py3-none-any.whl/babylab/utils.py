"""
Util functions for the app.
"""

from collections.abc import Sequence
from copy import deepcopy
from datetime import date, datetime, timedelta
from typing import Generator

import polars as pl

from babylab import api
from babylab.globals import COLNAMES


def is_in_data_dict(variable: str, x: Sequence[str] | str | None = None) -> list[str]:
    """Check that a value is an element in the data dictionary.

    Args:
        variable (str): Key in which to look for.
        x (Sequence[str] | str | None, optional): Value to look up in the data dictionary. Defaults to None (all options are checked for the variable).

    Raises:
        ValueError: If `x` is not an option present in `data_dict`.

    Returns:
        list[str]: Values in data dict.
    """
    options = list(api.DATA_DICT[variable].values())

    if x is None:
        return options

    x = [x] if isinstance(x, str) else list(x)

    for xi in x:
        if xi not in options:
            raise ValueError(f"{xi} is not an option in {variable}")

    return x


def get_ppt_table(
    records: api.Records,
    ppt_id: list[str] | str | None = None,
    study: list[str] | str | None = None,
) -> pl.DataFrame:
    """Get participants table

    Args:
        records (api.Records): REDCap records, as returned by ``api.Records``.
        ppt_id (list[str] | str | None): ID of participant to return. If None (default), all participants are returned.
        study (list[str] | str | None, optional): Study in which the participant in the records must have participated to be kept. Defaults to None.

    Returns:
        pl.DataFrame: Table of partcicipants.
    """
    if not records.participants.records:
        return pl.DataFrame(schema=COLNAMES["participants"])

    if isinstance(ppt_id, str):
        ppt_id = [ppt_id]

    if isinstance(study, str):
        study = [study]

    df = api.to_df(records.participants)

    if study:
        ppt_study = (
            api.to_df(records.appointments)
            .filter(pl.col("study").is_in(study))
            .unique("record_id")
            .get_column("record_id")
            .to_list()
        )
        df = df.filter(pl.col("record_id").is_in(ppt_study))

    if ppt_id:
        df = df.filter(pl.col("record_id").is_in(ppt_id))

    return df


def get_apt_table(
    records: api.Records,
    ppt_id: list[str] | str | None = None,
    study: list[str] | str | None = None,
) -> pl.DataFrame:
    """Get appointments table.

    Args:
        records (api.Records): REDCap records, as returned by ``api.Records``.
        ppt_id (list[str] | str | None, optional): ID of participant to return. If None (default), all participants are returned.
        study (list[str] | str | None, optional): Study to filter for. If None (default) all studies are returned.

    Returns:
        DataFrame: Table of appointments.
    """
    df = api.to_df(deepcopy(records.appointments))

    if len(df) == 0:
        return pl.DataFrame(schema=COLNAMES["appointments"])

    if isinstance(study, str):
        study = [study]

    if isinstance(ppt_id, str):
        ppt_id = [ppt_id]

    if study:
        df = df.filter(pl.col("study").is_in(study))

    if ppt_id:
        df = df.filter(pl.col("record_id").is_in(ppt_id))

    ppt_df = api.to_df(records.participants)

    cols = ["record_id", "age_now_months", "age_now_days"]
    df = df.join(ppt_df.select(cols), on="record_id")
    _, col_1, col_2 = cols

    months, days = [], []
    for rows in df.iter_rows(named=True):
        t = datetime.now() if rows["date"] is None else rows["date"]
        m, d = api.get_age(age=(rows[col_1], rows[col_2]), ts=t)
        months.append(m)
        days.append(d)

    df.insert_column(-1, pl.Series("age_apt_months", months))
    df.insert_column(-1, pl.Series("age_apt_days", days))

    return df


def get_que_table(
    records: api.Records, ppt_id: list[str] | str | None = None
) -> pl.DataFrame:
    """Get questionnaires table.

    Args:
        records (api.Records): REDCap records, as returned by ``api.Records``.
        ppt_id (list[str] | str | None, optional): ID of participant to return. If None (default), all participants are returned.
        relabel (bool): Reformat labels if True (default).

    Returns:
        DataFrame: A formated Pandas DataFrame.
    """
    df = api.to_df(deepcopy(records.questionnaires))

    if len(df) == 0:
        return pl.DataFrame(schema=COLNAMES["questionnaires"])

    if isinstance(ppt_id, str):
        ppt_id = [ppt_id]

    if ppt_id:
        df = df.filter(pl.col("record_id").is_in(ppt_id))

    return df


def count_col(
    x: pl.DataFrame,
    col: str,
    values_sort: bool = False,
    cumulative: bool = False,
    missing_label: str = "Missing",
) -> dict:
    """Count frequencies of column in DataFrame.

    Args:
        x (DataFrame): DataFrame containing the target column.
        col (str): Name of the column.
        values_sort (str, optional): Should the resulting dict be ordered by values? Defaults to False.
        cumulative (bool, optional): Should the counts be cumulative? Defaults to False.
        missing_label (str, optional): Label to associate with missing values. Defaults to "Missing".

    Returns:
        dict: Counts of each category, sorted in descending order.
    """
    counts = x[col].value_counts().to_dict()
    counts = {missing_label if not k else k: v for k, v in counts.items()}

    if values_sort:
        counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))

    if cumulative:
        cumsum = 0
        for key in counts:
            cumsum += counts[key]
            counts[key] = cumsum

    return counts


def get_year_weeks(year: int) -> Generator[datetime, datetime, datetime]:
    """Get week numbers of the year.

    Args:
        year (int): Year to get weeks for.

    Yields:
        Generator[datetime, datetime, datetime]: Number of weeks in the year.
    """
    date_first = date(year, 1, 1)
    date_first += timedelta(days=6 - date_first.weekday())

    while date_first.year == year:
        yield date_first
        date_first += timedelta(days=7)


def get_week_n(timestamp: date) -> int:
    """Get current week number in the year.

    Args:
        timestamp (date): Date to calculate week number for.

    Returns:
        int: Week number of given date.
    """
    weeks = {}

    for wn, d in enumerate(get_year_weeks(timestamp.year)):
        weeks[wn + 1] = [(d + timedelta(days=k)).isoformat() for k in range(7)]

    for k, v in weeks.items():
        if datetime.strftime(timestamp, "%Y-%m-%d") in v:
            return k
    return k


def get_weekly_apts(
    records: api.Records,
    study: Sequence | str | None = None,
    status: Sequence | str | None = None,
) -> int:
    """Get weekly number of appointments.

    Args:
        records (api.Records): REDCap records, as returned by ``api.Records``.
        study (list | None, optional): Study to filter for. Defaults to None.
        status (list | None, optional): Status to filter for. Defaults to None.

    Returns:
        int: Weekly number of appointment with for a given study and/or status.

    Raises:
        ValueError: If `study` or `status` is not available.
    """
    study = is_in_data_dict("appointment_study", study)
    status = is_in_data_dict("appointment_status", status)
    apts = records.appointments.records.values()

    date = get_week_n(datetime.today())

    return sum(
        get_week_n(v.data["date_created"]) == date
        for v in apts
        if v.data["status"] in status and v.data["study"] in study
    )
