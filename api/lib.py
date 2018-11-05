import datetime
import json
from typing import Dict, List, Generator
from urllib.parse import quote
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from bottle import request
from dateutil import parser
from dateutil.rrule import DAILY, rrule

from api.settings import TEMPERATURE_API_URL, WINDSPEED_API_URL


class ValidationError(Exception):
    pass


def get_start_end_params() -> Dict[str, str]:
    start = request.params.get('start')
    end = request.params.get('end')
    if not (start and end):
        raise ValidationError(
            "Both, start and end parameters needs to be provided."
        )
    return {"start": start, "end": end}


def _parse_ISO8601_date(date: str) -> datetime.datetime:
    """Return datetime object parsed from given ISO8601 DateTime string.

    @param date: date to validate
    @return datetime.datetime: parsed date
    """
    try:
        dt = parser.isoparse(date)
        if dt.tzinfo is not None and dt.tzinfo.utcoffset(dt) is not None:
            return dt
        return dt.astimezone()
    except ValueError:
        raise ValidationError(
            "Expecting date in ISO8601 format, eg. 2018-08-01T00:00:00Z, "
            f"gets {date} instead."
        )


def _date_range(start: str, end: str) -> List[str]:
    """Generate datetime range, one date ISO8601 per date.
    Minimal start date can be 1900-01-01T00:00:00Z, maximal current date.

    @param start: string with ISO8601 datetime in which range starts.
    @param end: string with ISO8601 datetime in which range ends (inclusive).
    """
    start_dt = _parse_ISO8601_date(start)
    end_dt = _parse_ISO8601_date(end)
    if start_dt > end_dt:
        raise ValidationError(
            "Start date needs to be greater than or equal end date."
        )
    if (
        start_dt < _parse_ISO8601_date('1900') or
        end_dt > datetime.datetime.now().astimezone()
    ):
        raise ValidationError(
            "Start date needs to be less than 1900-01-01T00:00:00Z and end"
            " date can't be from the feature."
        )
    return map(lambda date: date.isoformat(), rrule(
        freq=DAILY,
        dtstart=start_dt,
        until=end_dt,
        cache=True
    ))


def _api_request(date: str, api_url: str) -> Dict[str, str]:
    """Get data from api for given api_url and date.

    @param date: date for which api request is perform
    @param api_url: api url
    @return dict: dict with response data from api
    """
    try:
        data = json.loads(urlopen(
            Request(f"{api_url}?at={quote(date)}")
        ).read().decode('utf-8'))
    except HTTPError as e:
        data = json.loads(e.file.read().decode('utf-8'))
        if "message" in data:
            raise ValidationError(data["message"])
        else:
            raise ValidationError(f"Service unavailable ({e}")
    return data


def get_temperatures(
    start: str, end: str
) -> Generator[Dict[str, str], None, None]:
    """Get temperatures for given date range, return generator with dicts with
    temperature and date.
    """
    return map(
        lambda date: _api_request(date, TEMPERATURE_API_URL),
        _date_range(start, end)
    )


def get_speeds(start: str, end: str) -> Generator[Dict[str, str], None, None]:
    """Get temperatures for given date range, return generator with dicts with
    wind speed and date.

    @param start: string with ISO8601 datetime in which range starts.
    @param end: string with ISO8601 datetime in which range ends (inclusive).
    """
    return map(
        lambda date: _api_request(date, WINDSPEED_API_URL),
        _date_range(start, end)
    )


def get_weather(start: str, end: str) -> Generator[Dict[str, str], None, None]:
    """Get temperatures and speeds for given date range, return list with
    dicts with temperature, wind speeds and date.

    @param start: string with ISO8601 datetime in which range starts.
    @param end: string with ISO8601 datetime in which range ends (inclusive).
    """
    speeds = get_speeds(start, end)
    for data in get_temperatures(start, end):
        data.update(next(speeds))
        yield data
