import requests
from bs4 import BeautifulSoup
request = requests.get('https://www.nerfnow.com/archives')
soup = BeautifulSoup(request.text, 'html.parser')
counter = 0

for link in soup.find_all('a'):
    if 'nerfnow.com/comic' in link.get('href'):
        request = requests.get(link.get('href'))
        sub_soup = BeautifulSoup(request.text, 'html.parser')
        img_tag = sub_soup.find('div', id = 'comic').find('img')
        try:
            img_title = img_tag.attrs['title']
            img_link = img_tag.attrs['src']
        except:
            img_title = img_tag.contents[0].attrs['title']
            img_link = img_tag.contents[0].attrs['src']
        

        request = requests.get(img_link, stream = True)

        with open(str(img_title) + '.jpg','wb') as file:
            for chunk in request:
                file.write(chunk)
        counter +=1

        if counter == 20:
            break




