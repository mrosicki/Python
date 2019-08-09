import requests, os

IMG_PATH = os.path.join(os.getcwd(), 'img')
LIMIT = 29492
DIR = 1

for img in range(1, LIMIT):
    r = requests.get("http://demotywatory.com/i/w/" + str(DIR) + "/" + str(img) + ".jpg", stream=True)

    with open(IMG_PATH + '\\' + str(img) + '.jpg', 'wb') as file:
        for chunk in r:
            file.write(chunk)
    if img%10 == 0:
        print("Done: " + str(img))
    if img%500 == 0:
        DIR += 1
