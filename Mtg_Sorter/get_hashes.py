import bs4 as bs
from selenium import webdriver
import time
import requests
import cv2
import os
from PIL import Image
import imagehash

def histogram_equalization(img):
    clahe = cv2.createCLAHE(clipLimit=2.0)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    equalized = clahe.apply(gray)
    return equalized

directory = 'C:/Users/david/PycharmProjects/Mtg_Sorter/Hashes/tempPics'

PATH = "C:\Dev\chromedriver.exe"
driver = webdriver.Chrome(PATH)

page_count = 334
while True:
    link = "https://scryfall.com/search?as=grid&order=name&page=" + str(page_count) + "&q=%28rarity%3Ac+OR+rarity%3Au+OR+rarity%3Ar+OR+rarity%3Am%29&unique=cards"
    driver.get(link)
    time.sleep(3)

    # Get image urls
    page = driver.page_source
    soup = bs.BeautifulSoup(page, 'html.parser')

    container = soup.find("div", {"class": "card-grid-inner"})
    images = container.find_all("img")
    names = container.find_all("span")

    # Download the images
    count = 0
    for image in images:
        image_url = image.attrs['src']
        image_name = names[count].text
        image_name = image_name.replace("/", "")
        image_name = image_name.replace('"', "")
        image_name = image_name.replace('ö', '')
        image_name = image_name.replace('à', 'a')
        image_name = image_name.replace(':', ' ')
        image_name = image_name.replace('â', 'a')
        image_name = image_name.replace('é', 'e')
        image_name = image_name.replace('á', 'a')
        image_name = image_name.replace('í', 'i')
        image_name = image_name.replace('ú', 'u')
        image_name = image_name.replace('û', 'u')
        image_name = image_name.replace('?', '')
        image_name = image_name.replace('®', '')

        if image_url == '':
            image_url = image.attrs['data-src']

        r = requests.get(image_url)

        if r.status_code == 200:  # 200 status code = OK
            open('Hashes/tempPics/' + image_name + '.jpg', 'wb').write(r.content)

        count += 1
        if count == len(names):
            break

    #Crop images
    for image in os.listdir(directory):
        f = os.path.join(directory, image)

        img = cv2.imread(f)
        img = img[77:376, 37:450]

        width = int(img.shape[1] / 1.9)
        height = int(img.shape[0] / 1.9)
        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

        img = histogram_equalization(img)
        cv2.imwrite(f, img)

        # Get perceptual hash of image
        p_hash = imagehash.phash(Image.open(f))
        os.remove(f)

        #Write perceptual hash to file
        with open("C:/Users/david/PycharmProjects/Mtg_Sorter/Hashes/p_hashes", "a") as hash_file:
            f = f.split("/")
            f[-1] = f[-1].split("\\")

            hash_file.write(f"{f[-1][1]}: {p_hash}\n")
    page_count += 1
