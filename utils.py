from datetime import datetime

import pytz

class TelegramFile:

    def __init__(self, name, type,id,date, media):
        self.name = name
        self.type = type
        self.id = id
        self.date = date
        self.media = media

    def get_message(self):
        return self.name + "," + self.date

    def get_type(self):
        return self.type

    def get_dated_filename(self):
        return self.name + ", " + self.date

    def print(self):
        return self.get_message()

# Date methods
def is_today(dt, tz_name='Atlantic/Canary'):
    tz = pytz.timezone(tz_name)
    now = datetime.now(tz)
    dt_local = dt.astimezone(tz)
    return now.date() == dt_local.date()

def pretty_print_date(date):
    months = ("Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
    day = date.day
    month = months[date.month-1]
    current_date = "{} de {}".format(day, month)

    return str(current_date)

def build_file_message(file_name, file_type, file_id, date, file_media):
    return TelegramFile(file_name, file_type, file_id, pretty_print_date(date), file_media)

def print_results(ok, errors):
    print("\nDone! " + str(ok - len(errors)) + " files downloaded.")
    if (len(errors) > 0):
        print("Files failed: " + str(len(errors)))
        for e in errors:
            print(" * " + e)

# Find char for splitting
def find_separation_char(formatted_msg):
    char = None
    if "+" in formatted_msg:
        char = "+"
    elif "-" in formatted_msg:
        char = "-"
    elif "/" in formatted_msg:
        char = "/"
    return char