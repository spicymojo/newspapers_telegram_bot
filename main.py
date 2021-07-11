from alldebrid import Alldebrid
import json

alldebrid = Alldebrid()
print("Welcome to Alldebrid miniAPI")
link = input("Please enter the link that do you want to unlock:\n")
link = "https://uploaded.net/file/11wa1vsi"
http_response = alldebrid.download_link(link)

if http_response["status"] != "error":
    print("Link sucesfully converted:\n")
    print(http_response["data"]["link"])
else:
    print("Error with link " + link)