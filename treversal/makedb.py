from requests import get
from zipfile import ZipFile
from os import unlink, listdir
from sqlite3 import connect
from pandas import read_csv


print("starting download")
with get(
    "https://gtfs.mot.gov.il/gtfsfiles/israel-public-transportation.zip", stream=True
) as stream, open("data/archive/ipt.zip", "wb") as archive:
    stream.raise_for_status()
    for chunk in stream.iter_content(chunk_size=8192):
        archive.write(chunk)
print("downloaded archive")


print("starting unpacking")
with ZipFile("data/archive/ipt.zip", "r") as zip_ref:
    zip_ref.extractall("data/text/")
print("unpacked archive")
unlink("data/archive/ipt.zip")
print("deleted archive")


db = connect("data/data.db")
print("connected to db")
for filename in listdir("data/text/"):
    df = read_csv("data/text/" + filename)
    df.to_sql(filename, db)
    unlink("data/text/" + filename)
    print("proccessed " + filename)

print("done")
