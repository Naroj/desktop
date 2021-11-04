#!/home/pi/.venv/bin/python

DESCR = """
Exchange cal, mail fetcher for conky/anything else
"""

import sys
import pprint
import json
import logging
import datetime
import argparse
import os
from exchangelib import Credentials, Account, EWSDateTime, EWSTimeZone

ITEM_LIMIT = 10
SUBJ_LIMIT = 20
TMP_PREFIX = "essi_"
TMP_DIR = f"{os.getenv('HOME')}/.tmp"


def parse_argv(argvs: list) -> dict:
    type_choice = ["cal", "mail"]
    day_choice = ["today", "tomorrow", "yesterday"]
    parser = argparse.ArgumentParser(description=DESCR)
    parser.add_argument(
        "--type",
        choices=type_choice,
        required=True,
        default=None,
        help="calendar {day} events",
    )
    parser.add_argument(
        "--day", choices=day_choice, required=True, default=None, help="define a day"
    )
    parser.add_argument(
        "--show", required=False, default=False, help="show (earlier fetched) items"
    )
    cli_args = parser.parse_args(argvs)
    return cli_args.__dict__


def init_exchange() -> Account:
    """ """
    my_account = "****"
    my_email = "****nt.nl"
    passw = "******"
    try:
        creds = Credentials(my_account, passw)
        account = Account(my_email, credentials=creds, autodiscover=True)
    except Exception:
        return False
    return account


def str_limit(string: str = "", limit=20) -> str:
    """ cut a string to 'limit' if its length exceeds this number """
    if len(str(string)) > limit:
        return f"{str(string[:-limit])}.."
    else:
        return str(string)


def conv_from_utc(dt: datetime.datetime) -> str:
    local_tz = dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
    return f"{local_tz.hour}:{local_tz.minute}"


def get_yymmdd(day: str = "today") -> tuple:
    now = datetime.datetime.now()
    if day == "today":
        y, m, d = now.year, now.month, now.day
    elif day == "tomorrow":
        tom = now + datetime.timedelta(days=1)
        y, m, d = tom.year, tom.month, tom.day
    elif day == "yesterday":
        yest = now - datetime.timedelta(days=1)
        y, m, d = yest.year, yest.month, yest.day
    else:
        raise UserWarning(f"calendar_events: day, {day} is not accepted")
    return y, m, d


def calendar_events(account: Account, day: str = "today") -> list:
    """ expect an established account session """
    tz = EWSTimeZone("UTC")
    start = EWSDateTime(*get_yymmdd(day), 5, tzinfo=tz)
    end = EWSDateTime(*get_yymmdd(day), 23, tzinfo=tz)
    events = account.calendar.filter(start__range=(start, end))
    output = []
    for event in events:
        # opt_att = event.optional_attendees
        # req_att = event.required_attendees
        item = {
            "organizer": event.organizer.name,
            "subject": event.subject,
            "location": event.location,
            "start": conv_from_utc(event.start),
            "end": conv_from_utc(event.end),
        }
        output.append(item)
    order = sorted(output, key=lambda k: k["start"])
    return order


def get_day_name(day: str):
    """ get day name based on day as keywords """
    today = datetime.datetime.now()
    delta = datetime.timedelta(days=1)
    opts = {
        "today": today.strftime("%A"),
        "yesterday": (today - delta).strftime("%A"),
        "tomorrow": (today + delta).strftime("%A"),
    }
    try:
        return opts[day].lower()
    except KeyError:
        raise UserWarning(f"unacceptable day input: {day}")


def write_event(event: dict, num: int, kind: str, day: str):
    """ event data to temp file """
    weekday = get_day_name(day)
    ev_file = f"{TMP_DIR}/{TMP_PREFIX}{kind}_{weekday}_{num}"
    content = json.dumps(event)
    with open(f"{ev_file}", "wb") as fp:
        fp.write(content.encode())


def read_event(kind: str, day: str, num: int) -> dict:
    """ read a single event file """
    weekday = get_day_name(day)
    ev_file = f"{TMP_DIR}/{TMP_PREFIX}{kind}_{weekday}_{num}"
    try:
        with open(ev_file, "r") as fp:
            data = json.loads(fp.read())
    except (IOError, KeyError):
        return ""
    if len(data['subject']) > SUBJ_LIMIT:
        #subject = f"{data['subject'][:-SUBJ_LIMIT]}.."
        subject = data['subject']
    else:
        subject = data['subject']
    return (
        f"organizer: {data['organizer']}\n"
        f"location: {data['location']}\n"
        f"subject: {subject}\n"
        f"time: {data['start']} / {data['end']}"
    )


def main():
    params = parse_argv(sys.argv[1:])
    my_account = init_exchange()
    if params.get("show"):
        kind = params.get("type")
        day = params.get("day")
        num = params.get("show")
        event = read_event(kind, day, num)
        sys.stdout.write(event)
        sys.stdout.flush()
    elif params["type"] == "cal":
        day = params["day"]
        events = calendar_events(my_account, day=day)
        for num, event in enumerate(events):
            write_event(event, num, params["type"], day)


if __name__ == "__main__":
    if not os.path.isdir(TMP_DIR):
        logging.error(f'tmp folder "{TMP_DIR}" does not exist')
        sys.exit(1)
    elif not sys.argv[1:]:
        logging.error("no arguments means no action, use --help to find out more")
        sys.exit(1)
    main()
