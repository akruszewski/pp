import json

from bottle import default_app, HTTPResponse, route, run

from .settings import DEBUG, HOST, PORT

from api.lib import (
    ValidationError,
    get_speeds,
    get_start_end_params,
    get_temperatures,
    get_weather,
)


headers = {'Content-type': 'application/json'}


@route('/temperatures')
def temperatures() -> str:
    """Endpoint which utilise `start` and `end` dates in ISO8601 DateTime url
    kwargs and returns json with temperatures with corresponding
    dates in ISO8601 DateTime format. Response list is sorted by date.

    Response format:
    [
        {"temp": TEMPERATURE, "date": ISO8601_DATE_TIME},
        ...
    ]

    Example:

        Request:
          GET /temperatures?start=2018-08-01T00:00:00Z&end=2018-08-07T00:00:00Z
        Response:
          [
            {
              "temp": 10.46941232124016,
              "date": "2018-08-01T00:00:00Z"
            },
            {
              "temp": 13.5353456555445,
              "date": "2018-08-02T00:00:00Z"
            },
            {
              "temp": 8.23423423423344,
              "date": "2018-08-03T00:00:00Z"
            },
            {
              "temp": 11.6456546546454,
              "date": "2018-08-04T00:00:00Z"
            },
            {
              "temp": 5.879879879879889,
              "date": "2018-08-05T00:00:00Z"
            },
            {
              "temp": 15.34354353454353,
              "date": "2018-08-06T00:00:00Z"
            },
            {
              "temp": 9.434534534353345,
              "date": "2018-08-07T00:00:00Z"
            }
          ]
    """
    try:
        return json.dumps(list(get_temperatures(**get_start_end_params())))
    except ValidationError as e:
        data = json.dumps({"message": str(e)})
        raise HTTPResponse(body=data, status=400, headers=headers)


@route('/speeds')
def speeds() -> str:
    """Endpoint which utilise `start` and `end` dates in ISO8601 DateTime url
    kwargs and returns json with wind speed with corresponding
    dates in ISO8601 DateTime format. Response list is sorted by date.

    Response format:
    [
        {
            "north": WIND_ANGLE_NORTH,
            "west": WIND_ANGLE_WEST,
            "date": ISO8601_DATE_TIME
        },
        ...
    ]

    Example:

        Request:
          GET /speeds?start=2018-08-01T00:00:00Z&end=2018-08-04T00:00:00Z
        Response:
          [
            {
              "north": -17.989980201472466,
              "west": 16.300917971882726,
              "date": "2018-08-01T00:00:00Z"
            },
            {
              "north": 5.989980201472466,
              "west": 10.300917971882726,
              "date": "2018-08-02T00:00:00Z"
            },
            {
              "north": -20.989980201472466,
              "west": -16.300917971882726,
              "date": "2018-08-03T00:00:00Z"
            },
            {
              "north": 10.989980201472466,
              "west": -15.300917971882726,
              "date": "2018-08-04T00:00:00Z"
            }
          ]
    """
    try:
        return json.dumps(list(get_speeds(**get_start_end_params())))
    except ValidationError as e:
        data = json.dumps({"message": str(e)})
        raise HTTPResponse(body=data, status=400, headers=headers)


@route('/weather')
def weather() -> str:
    """Endpoint which utilise `start` and `end` dates in ISO8601 DateTime url
    kwargs and returns json with temperatures, wind speeds and corresponding
    dates in ISO8601 DateTime format. Response list is sorted by date.

    Response format:
    [
        {
            "temp": TEMPERATURE_IN_CELSIUS,
            "date": ISO8601_DATE_TIME,
            "north": WIND_ANGLE_NORTH,
            "west": WIND_ANGLE_WEST
        },
        ...
    ]

    Example:

        Request:
          GET /weather?start=2018-08-01T00:00:00Z&end=2018-08-04T00:00:00Z
        Response:
          [
            {
              "north": -17.989980201472466,
              "west": 16.300917971882726,
              "temp": 10.46941232124016,
              "date": "2018-08-01T00:00:00Z"
            },
            {
              "north": 5.989980201472466,
              "west": 10.300917971882726,
              "temp": 13.5353456555445,
              "date": "2018-08-02T00:00:00Z"
            },
            {
              "north": -20.989980201472466,
              "west": -16.300917971882726,
              "temp": 8.23423423423344,
              "date": "2018-08-03T00:00:00Z"
            },
            {
              "north": 10.989980201472466,
              "west": -15.300917971882726,
              "temp": 11.6456546546454,
              "date": "2018-08-04T00:00:00Z"
            }
          ]
    """
    try:
        return json.dumps(list(get_weather(**get_start_end_params())))
    except ValidationError as e:
        data = json.dumps({"message": str(e)})
        raise HTTPResponse(body=data, status=400, headers=headers)


if __name__ == '__main__':
    run(host=HOST, port=PORT, debug=DEBUG)

app = default_app()
