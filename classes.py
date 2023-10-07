import random
import datetime
import urllib.request
from bs4 import BeautifulSoup

platform_styles = {
    "width: 12px; height: 12px; -webkit-mask-image: url(&quot;https://static.xx.fbcdn.net/rsrc.php/v3/yl/r/1IflondRoFA.png&quot;); -webkit-mask-size: 122px 404px; -webkit-mask-position: -104px -270px;": "Facebook",
    "width: 12px; height: 12px; -webkit-mask-image: url(&quot;https://static.xx.fbcdn.net/rsrc.php/v3/y0/r/Phy2uucwc_B.png&quot;); -webkit-mask-size: 30px 668px; -webkit-mask-position: -16px -564px;": "Instagram",
    "width: 12px; height: 12px; -webkit-mask-image: url(&quot;https://static.xx.fbcdn.net/rsrc.php/v3/yl/r/1IflondRoFA.png&quot;); -webkit-mask-size: 122px 404px; -webkit-mask-position: -108px -190px;": "Audience Network",
    "width: 12px; height: 12px; -webkit-mask-image: url(&quot;https://static.xx.fbcdn.net/rsrc.php/v3/yl/r/1IflondRoFA.png&quot;); -webkit-mask-size: 122px 404px; -webkit-mask-position: -108px -308px;": "Messenger",
}

dates = {
    "янв": 1,
    "фев": 2,
    "мар": 3,
    "апр": 4,
    "май": 5,
    "июн": 6,
    "июл": 7,
    "авг": 8,
    "сен": 9,
    "окт": 10,
    "ноя": 11,
    "дек": 12
}


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
            self.media_type = "Photo"
        except:
            try:
                self.download = soup.find("div", class_="x1ywc1zp x78zum5 xl56j7k x1e56ztr xh8yej3").find("video").get(
                    "src")
                urllib.request.urlretrieve(self.download, f'./videos/{self.id}.mp4')
                self.media_type = "Video"
            except:
                print(self.id)
                self.media_type = "Carousel"
                self.download = "bad type media"

        try:
            self.status = soup.find("span", class_="x8t9es0 xw23nyj xo1l8bm x63nzvj x108nfp6 xq9mrsl x1h4wwuj xeuugli "
                                                   "x1i64zmx").get_text()
        except:
            self.status = soup.find("span",
                                    class_="x8t9es0 xw23nyj xo1l8bm x63nzvj x108nfp6 xq9mrsl x1h4wwuj xeuugli x1i64zmx").get_text()

        date = soup.find_all("span", class_="x8t9es0 xw23nyj xo1l8bm x63nzvj x108nfp6 xq9mrsl x1h4wwuj"
                                            " xeuugli")[1].get_text().split(' ')
        day, month, year = int(date[2]), dates[date[3]], int(date[4])
        self.start_date = datetime.date(year, month, day)

        self.duration = datetime.date.today() - self.start_date

        self.platforms = []
        for platform in soup.find_all("div", class_="xtwfq29"):
            if platform in platform_styles.keys():
                self.platforms.append(platform_styles[platform['style']])

    def get_data(self):
        return self.id, self.text, self.buttonText, self.landing, self.download, self.status, str(self.start_date), \
               str(self.duration.days), *self.platforms


class Account:
    def __init__(self, url: str):
        # parse from url
        # как вариант открыть через селениум получить всю дату и закрыть
        self.id = url[url.find("view_all_page_id=") + len("view_all_page_id="):url.find("&sort_data")]
        self.name = "name"
        self.nickname = "@nickname"
        self.image = "image"
        self.total_ads = 0
        self.link = "url"
        self.active_ads = "active"
        self.ads = []

    def get_data(self):
        return self.id, self.name, self.nickname, self.image, self.total_ads, self.link, self.active_ads, self.ads

    def count_active(self):
        count = 0
        for ad in self.ads:
            if ad.status == "Активно":
                count += 1
        return count
