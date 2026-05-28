from requests import get

with get("https://gtfs.mot.gov.il/gtfsfiles/israel-public-transportation.zip", stream=True) as stream, open("treversal/data/ipt.zip", "wb") as archive:
    stream.raise_for_status()
    for chunk in stream.iter_content(chunk_size=8192):
        archive.write(chunk)
