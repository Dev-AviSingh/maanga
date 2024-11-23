import requests as rq
from typing import TypedDict, Annotated
import json
import os
from time import sleep
import logging


DATA_FILE:str = "data.json"
logger = logging.getLogger()
logger.setLevel(0)
logging.basicConfig(filename = "painless.log")

class MangaSite(TypedDict):
    name:Annotated[str, "Name of the manga"]
    manga_url_format:Annotated[str, "The url where the manga chapters are released, with the number parameterised."]
    last_chapter:int
    not_existence_message:Annotated[str, "The message showed in the site, when the manga chapter is not released yet."]



def scrape_loop(manga_database:list[MangaSite], interval:Annotated[int, "The time between each search in seconds."] = 1):
    logger.info(f"Starting main loop.")
    # while True:

    #     sleep(interval)
    for manga in manga_database:
        logger.info(f"Scanning {manga['name']}")
        manga["last_chapter"] += 1

        try:
            last_chapter_url = manga["manga_url_format"].format(chapter_number = manga["last_chapter"])
        except KeyError as e:
            logger.error("The chapter url has not key 'chapter_number'")
        
        r = rq.get(last_chapter_url)

        if r.status_code == 404:
            logger.info(f"Site not found: {last_chapter_url}")
            continue
        
        if not manga["not_existence_message"] in r.text:
            logger.info(f"A new {manga['name']} chapter has been released : {manga['manga_url_format'].format(chapter_number = manga['last_chapter'])}")
        else:
            manga["last_chapter"] -= 1
            logger.info(f"No new chapters released for {manga['name']}. Latest chapter : {manga['last_chapter']}")

if __name__ == "__main__":
    database:dict[str, list[MangaSite] | int] = {
        "mangas":[],
        "interval":1,
    }
    if not os.path.exists(DATA_FILE):
        logger.warning("Database does not exist, creating new one.")
        with open(DATA_FILE, "w") as f:
            json.dump(database, f)
    else:
        logger.info("Loading database.")
        with open(DATA_FILE, "r") as f:
            database = json.load(f)

    mangas = database["mangas"]

    logger.info(f"Database : {database}")
    scrape_loop(mangas)
    