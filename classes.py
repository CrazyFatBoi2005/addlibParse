import random
import urllib.request
from bs4 import BeautifulSoup


class Ad:
    def __init__(self, element):
        soup = BeautifulSoup(element, "html.parser")

        self.id = soup.find("span",
                            class_="x8t9es0 xw23nyj xo1l8bm x63nzvj x108nfp6 xq9mrsl x1h4wwuj xeuugli").text.split(" ")[
            -1]

        try:
            self.text = soup.find("div", class_="_7jyr _a25-").get_text()
        except:
            self.text = "no text"

        try:
            self.buttonText = soup.find("div", class_="_8jh0").find("div", class_="x8t9es0 x1fvot60 xxio538 x1heor9g "
                                                                                  "xuxw1ft "
                                                                                  "x6ikm8r x10wlt62 xlyipyv x1h4wwuj "
                                                                                  "x1pd3egz "
                                                                                  "xeuugli").text
        except:
            self.buttonText = "no button text"
        self.landing = soup.find("a", class_="x1hl2dhg x1lku1pv x8t9es0 x1fvot60 xxio538 xjnfcd9 xq9mrsl x1yc453h "
                                             "x1h4wwuj x1fcty0u x1lliihq").get("href")

        try:
            self.download = soup.find("img", class_="x1ll5gia x19kjcj4 xh8yej3").get("src")
        except:
            try:
                self.download = soup.find("div", class_="x1ywc1zp x78zum5 xl56j7k x1e56ztr xh8yej3").find("video").get(
                    "src")
                urllib.request.urlretrieve(self.download, f'./videos/{self.id}.mp4')
            except:
                print(self.id)
                self.download = "bad type media"

        try:
            self.status = soup.find("span", class_="x8t9es0 xw23nyj xo1l8bm x63nzvj x108nfp6 xq9mrsl x1h4wwuj xeuugli "
                                                  "x1i64zmx").get_text()
        except:
            self.status = soup.find("span",
                                    class_="x8t9es0 xw23nyj xo1l8bm x63nzvj x108nfp6 xq9mrsl x1h4wwuj xeuugli x1i64zmx").get_text()

    def get_data(self):
        return self.id, self.text, self.buttonText, self.landing, self.download


class Account:
    def __init__(self, url: str):
        # parse from url
        # как вариант открыть через селениум получить всю дату и закрыть
        self.id = url[url.find("view_all_page_id=") + len("view_all_page_id="):url.find("&sort_data")]
        self.name = "name"
        self.nickname = "@nickname"
        self.picture = "image"
        self.total_ads = "total"
        self.link = "url"
        self.active_ads = "active"
        self.ads = []
