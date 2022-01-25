import cv2
import imutils
import numpy as np
import imagehash
from PIL import Image
import vptree

img = cv2.imread('Pictures\\img.png') # Read image
background = cv2.imread('Pictures\\img_1.png')
background = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)

def hamming_distance(str1, str2):
    i = 0
    count = 0

    while (i < len(str1)):
        if str1[i] != str2[i]:
            count += 1
        i += 1
    return count

with open("C:/Users/david/PycharmProjects/Mtg_Sorter/Hashes/p_hashes", "r") as hash_file:
    hashes = []
    for line in hash_file:
        line = line.split(':')
        line[-1] = line[-1].strip('\n')
        line[-1] = line[-1].replace(' ', '')
        hashes.append(line[-1])

tree = vptree.VPTree(hashes, hamming_distance)

def histogram_equalization(img):
    clahe = cv2.createCLAHE(clipLimit=2.0)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    equalized = clahe.apply(gray)
    return equalized

def calculate_aspect_ratio(width, height):
    def gcd(a, b):
        return a if b == 0 else gcd(b, a % b)

    r = gcd(width, height)
    x = int(width / r)
    y = int(height / r)

    return x / y

def find_card_name(filepath, hash):
    with open(filepath, 'r') as f:
        for line in f:
            hash_line = line.split(':')
            hash_line[-1] = hash_line[-1].strip('\n')
            hash_line[-1] = hash_line[-1].replace(' ', '')

            if hash in hash_line:
                line = line.split('.')
                return line[0]



def preprocces(img, background):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # Convert to grayscale
    delta = cv2.absdiff(background, gray)
    thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)

    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnts = imutils.grab_contours(cnts)

    for c in cnts:

        x, y, w, h = cv2.boundingRect(c)

        # If bounded area is greater than 10.000 pixels
        if cv2.contourArea(c) < 10000:
            continue

        # If Aspect ratio between 0.65 and 1
        if calculate_aspect_ratio(w , h) < 0.65 or calculate_aspect_ratio(w , h) > 1:
            continue

        # Draw bounding box
        cv2.rectangle(img, (x, y), (x + w, y + h), (36, 255, 12), 1)

        # Get corners
        approx = cv2.approxPolyDP(c, 0.1 * cv2.arcLength(c, True), True)
        cv2.drawContours(img, c, -1, (0, 255, 0), 2)

        # Coordinates of corners
        bl = approx[0][0]
        br = approx[3][0]
        tr = approx[2][0]
        tl = approx[1][0]

        # Desired size of warped image
        width = 262
        height = 362

        # Construct warped image
        input = np.float32([bl, br, tr, tl])
        output = np.float32([[0,0], [width-1,0], [width-1,height-1], [0,height-1]])

        matrix = cv2.getPerspectiveTransform(input, output)
        imgOutput = cv2.warpPerspective(img, matrix, (width, height), cv2.INTER_LINEAR)

        #Crop art
        img = imgOutput[45:205, 22:240]

        # Equalize
        img = histogram_equalization(img)

        # Write warped image to file
        cv2.imwrite("warped.jpg", img)

        cv2.imshow('s', img)


        p_hash_image = imagehash.phash(Image.open('warped.jpg'))
        closest_match = tree.get_nearest_neighbor(str(p_hash_image))

        name = find_card_name("C:/Users/david/PycharmProjects/Mtg_Sorter/Hashes/p_hashes", closest_match[1])
        print(name)

    return

if __name__ == '__main__':

    preprocces(img, background)


