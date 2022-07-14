#! python
from random import randrange
from os import listdir
from requests import get
from bs4 import BeautifulSoup
from json import loads
from subprocess import call
from uuid import uuid4

IMAGE_FOLDER = "/mnt/c/Users/Jacob/Pictures/SpaceBackgrounds/"
# requires an index
SOURCE_URL = "https://esahubble.org/images/page/"
SOURCE_URL_STUB = "https://esahubble.org"


def get_source_file():
    # get a valid source page url
    # page_range = randrange(102) + 1  # 1-102
    page_range = randrange(4) + 1  # 1-4

    source_url = f'{SOURCE_URL}{page_range}'

    print(source_url)
    # get the html from a source page
    source_page = get(source_url)

    if not source_page.ok:
        print("call to get image sources failed")
        exit(1)

    return source_page.text


if __name__ == "__main__":
    source_page = get_source_file()

    # just for dev purposes
    # with open("./saved_source.html", "r") as f:
    #     source_page = f.read()

    # parse the html for all valid image links
    # lots of string manipulation because the page didn't run
    # the js so the links were in a script tag
    soup = BeautifulSoup(source_page, "html.parser")

    script_tags = soup.find_all("script")
    script_tag = str(script_tags[1].contents[0])[:-2]

    # get rid of the "var images =" string
    script_tag = script_tag.replace("var images = ", "")

    lines = script_tag.split("\n")
    new_string = []

    for line in lines:
        if ":" in line:
            clean_strings = list(map(lambda x: x.strip(), line.split(":", 1)))
            clean_strings[0] = f"\"{clean_strings[0]}\""
            clean_strings[1] = clean_strings[1].replace("'", "\"")
            new_string.append(":".join(clean_strings))
            continue
        new_string.append(line)

    new_string[-3] = new_string[-3].replace(",", "")  # remove trailing ','
    new_string = "\n".join(new_string)
    json = loads(new_string)

    random_image_page = randrange(len(json)) + 1

    random_image_page_url = f"{SOURCE_URL_STUB}{json[random_image_page]['url']}"

    # get the html for the image page
    image_page_source = get(random_image_page_url)

    if not image_page_source.ok:
        print("failed to get image page source")
        exit(1)

    image_page_source = image_page_source.text

    # with open("./saved_image_page.html", "r") as f:
    #     image_page_source = f.read()

    image_page_soup = BeautifulSoup(image_page_source, "html.parser")
    anchor_tags = image_page_soup.find_all(
        "div", class_="archive_download")[0].find_all("a")

    # get the download link
    # upgrade idea don't download the fullsize image everytime, get the best size for monitor
    download_url = None
    for tag in anchor_tags:
        # get the href for full size image
        if tag.contents[0] == "Fullsize Original":
            download_url = f"{SOURCE_URL_STUB}{tag['href']}"
            break

    if (download_url is None):
        print("couldn't get download url")
        exit(1)

    # download the appropriate image file size
    # get file extension
    extension = download_url.split(".")[-1].strip()
    # make the file name random
    randomness = str(uuid4())
    call(["wget", "-O", f"background-image_{randomness}.{extension}", download_url]) 
    
    # delete current file in the background images folder
    old_background_file = listdir(IMAGE_FOLDER)[0]
    
    call(["rm", f"{IMAGE_FOLDER}{old_background_file}"])

    # mv new file to background images folder 
    call(["mv", f"background-image_{randomness}.{extension}", IMAGE_FOLDER])

    # switch out the current background image with the new image
    print("Successfully changed the background image!!!!")
