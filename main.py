from alldebrid import Alldebrid
from datetime import datetime
import requests
import os.path



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

def main():
    print("Welcome to Alldebrid miniAPI\n")
    link_file = open_link_file("links.txt")
    lines = link_file.readlines()
    alldebrid = Alldebrid()

    for line in lines:
        filename, base_url = line.split(",")
        http_response = alldebrid.download_link(base_url)
        filename = obtain_daily_filename(filename)

        if http_response["status"] != "error":
            converted_link = http_response["data"]["link"]
            print("Saving " + filename + " ...")
            download_file(converted_link, filename)
        else:
            print("Error with link " + base_url)
    print("\nDone! " + str(len(lines)) + " files downloaded.")

main()
