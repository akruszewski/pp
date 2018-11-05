import datetime
import unittest

import requests
from dateutil import parser

from api import lib
from api import settings


class APITestCase(unittest.TestCase):
    def test_temperature_API(self):
        """Test service temperature API endpoint.
        """
        res = requests.get(
            f"http://{settings.bind}/temperatures?"
            "start=1999-12-03&end=1999-12-05T22:22Z"
        )

        # Check if temperatures endpoint works and if results are in order
        self.assertTrue(res.ok)
        dates = [parser.isoparse(data['date']) for data in res.json()]
        self.assertTrue(dates[0] < dates[1] < dates[2])

        res = requests.get(
            f"http://{settings.bind}/temperatures?"
            "start=1999-12-03&end=1990-12-05T22:22Z"
        )

        # Check if temperatures endpoint returns message and 400 status on
        # invalid data
        self.assertFalse(res.ok)
        self.assertEqual(res.status_code, 400)
        self.assertIn("message", res.json())

    def test_speed_API(self):
        """Test service windspeed API endpoint.
        """
        res = requests.get(
            f"http://{settings.bind}/speeds?"
            "start=1999-12-03&end=1999-12-05T22:22Z"
        )

        # Check if temperatures endpoint works and if results are in order
        self.assertTrue(res.ok)
        dates = [parser.isoparse(data['date']) for data in res.json()]
        self.assertTrue(dates[0] < dates[1] < dates[2])

        res = requests.get(
            f"http://{settings.bind}/speeds?"
            "start=1999-12-03&end=1990-12-05T22:22Z"
        )

        # Check if temperatures endpoint returns message and 400 status on
        # invalid data
        self.assertFalse(res.ok)
        self.assertEqual(res.status_code, 400)
        self.assertIn("message", res.json())

    def test_weather_API(self):
        """Test service weather API endpoint.
        """
        res = requests.get(
            f"http://{settings.bind}/weather?"
            "start=1999-12-03&end=1999-12-05T22:22Z"
        )

        # Check if temperatures endpoint works and if results are in order
        self.assertTrue(res.ok)
        dates = [parser.isoparse(data['date']) for data in res.json()]
        self.assertTrue(dates[0] < dates[1] < dates[2])

        res = requests.get(
            f"http://{settings.bind}/weather?"
            "start=1999-12-03&end=1990-12-05T22:22Z"
        )

        # Check if temperatures endpoint returns message and 400 status on
        # invalid data
        self.assertFalse(res.ok)
        self.assertEqual(res.status_code, 400)
        self.assertIn("message", res.json())

        # check if order is not messed up and also if data is zipped correctly.
        res_w = requests.get(
            f"http://{settings.bind}/weather?"
            "start=1999-12-03&end=1999-12-05T22:22Z"
        ).json()
        res_s = requests.get(
            f"http://{settings.bind}/speeds?"
            "start=1999-12-03&end=1999-12-05T22:22Z"
        ).json()
        res_t = requests.get(
            f"http://{settings.bind}/temperatures?"
            "start=1999-12-03&end=1999-12-05T22:22Z"
        ).json()
        for i in range(len(res_w)):
            self.assertEqual(res_w[i]['temp'], res_t[i]['temp'])

            self.assertEqual(res_w[i]['west'], res_s[i]['west'])
            self.assertEqual(res_w[i]['north'], res_s[i]['north'])

            self.assertEqual(res_w[i]['date'], res_t[i]['date'])
            self.assertEqual(res_w[i]['date'], res_s[i]['date'])

class LibTestCase(unittest.TestCase):
    def test__parse_ISO8601_date(self):
        """Test _parse_ISO8601_date function.
        """
        date_valid = "1989-12-31T23:59:59+00:00"
        date_invalid = "asd"

        date = lib._parse_ISO8601_date(date_valid)
        self.assertEqual(
            date.isoformat(),
            date_valid
        )

        # check if function returns ValidationError if date is invalid
        with self.assertRaises(lib.ValidationError):
            lib._parse_ISO8601_date(date_invalid)

    def test__date_range(self):
        """Test _date_range function.
        """
        date_valid = "1989-12-31T23:59:59+00:00"
        date_valid2 = "1990-01-01T23:59:59+00:00"
        date_before_1990 = "1889-12-31T23:59:59+00:00"
        date_after_now = (
            datetime.datetime.utcnow() + datetime.timedelta(days=1)
        ).isoformat()

        range = list(lib._date_range(date_valid, date_valid2))
        self.assertEqual(range[0], date_valid)
        self.assertEqual(range[1], date_valid2)

        # check if function returns ValidationError if start is grater than end
        with self.assertRaises(lib.ValidationError) as cm:
            lib._date_range(
                datetime.datetime.now().isoformat(), date_valid
            )
        self.assertEqual(
            str(cm.exception),
            "Start date needs to be greater than or equal end date."
        )

        # check if function returns ValidationError if date is before 1990
        with self.assertRaises(lib.ValidationError) as cm:
            lib._date_range(
                date_before_1990, datetime.datetime.now().isoformat()
            )
        self.assertEqual(
            str(cm.exception),
            "Start date needs to be less than 1900-01-01T00:00:00Z and end"
            " date can't be from the feature."
        )

        # check if function returns ValidationError if date is from feature
        with self.assertRaises(lib.ValidationError) as cm:
            lib._date_range(
                datetime.datetime.now().isoformat(), date_after_now
            )
        self.assertEqual(
            str(cm.exception),
            "Start date needs to be less than 1900-01-01T00:00:00Z and end"
            " date can't be from the feature."
        )

    def test__api_request(self):
        """Test _api_request function.
        """
        date_valid = "1989-12-31T23:59:59Z"
        date_before_1990 = "1889-12-31T23:59:59Z"

        # check if function raises ValidationError when 404 occurs in
        # api response and if message is passed.
        with self.assertRaises(lib.ValidationError) as cm:
            lib._api_request(date_before_1990, settings.TEMPERATURE_API_URL)
        self.assertEqual(
           "no sample found for date 1889-12-31T23:59:59Z",
           str(cm.exception)
        )

        # check if function raises ValidationError when 400 occurs in
        # api response and if message is passed.
        with self.assertRaises(lib.ValidationError) as cm:
            lib._api_request("asd", settings.TEMPERATURE_API_URL)
        self.assertEqual(
           "asd is not a valid RFC3339 DateTime",
           str(cm.exception)
        )

        # check if valid data is passed to api, valid response is returned
        res = lib._api_request(date_valid, settings.TEMPERATURE_API_URL)
        self.assertTrue(isinstance(res, dict))
        self.assertIn("temp", res.keys())
        self.assertIn("date", res.keys())


if __name__ == '__main__':
    unittest.main()
