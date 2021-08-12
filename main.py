from api.alldebrid import Alldebrid
from datetime import datetime
from resources.config import AlldebridConfig
import requests, glob, os, configparser

errors = ""

def current_date(date):
    months = ("Enero", "Febrero", "Marzo", "Abri", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre")
    day = date.day
    month = months[date.month - 1]
    current_date = "{} de {}".format(day, month)

    return current_date

def download_file(url,filename):
    if not os.path.isfile(filename):
        open(filename,"wb").write(requests.get(url).content)

def obtain_daily_filename(filename):
    filename = str(filename + " - " + current_date(datetime.now()) + ".pdf")
    return filename

def open_link_file(path):
    return open(path, "r")

def print_results(lines, errors):
    print("\nDone! " + str(len(lines) - len(errors)) + " files downloaded.")
    if (len(errors) > 0):
        print("Files failed: " + str(len(errors)))
        for e in errors:
            print(" * " + e)

def download():
    print("Welcome to Alldebrid miniAPI\n")
    link_file = open_link_file("resources/links.txt")
    os.chdir(downloads_path)
    lines = link_file.readlines()
    alldebrid = Alldebrid()
    errors = list()

    for line in lines:
        filename, base_url = line.split(",")
        http_response = alldebrid.download_link(base_url)
        filename = obtain_daily_filename(filename)

        if http_response["status"] != "error":
            converted_link = http_response["data"]["link"]
            print("Saving " + filename + " ...")
            download_file(converted_link, filename)
        else:
            errors.append(filename)
    print_results(lines,errors)



def main():
    download()

# Config zone
telegram_token = AlldebridConfig.telegram_token
channel_id = AlldebridConfig.channel_id
downloads_path = AlldebridConfig.downloads_path

main()
