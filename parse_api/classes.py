import datetime
import urllib.request
from bs4 import BeautifulSoup

platform_styles = {
    'width: 12px; height: 12px; -webkit-mask-image: url("https://static.xx.fbcdn.net/rsrc.php/v3/y0/r/QELw80WZC8L.png"); -webkit-mask-position: -51px -335px;': "Facebook",
    'width: 12px; height: 12px; -webkit-mask-image: url("https://static.xx.fbcdn.net/rsrc.php/v3/y7/r/RBY2XQNTT-A.png"); -webkit-mask-position: -14px -545px;': "Instagram",
    'width: 12px; height: 12px; -webkit-mask-image: url("https://static.xx.fbcdn.net/rsrc.php/v3/y0/r/QELw80WZC8L.png"); -webkit-mask-position: -106px -186px;': "Audience Network",
    'width: 12px; height: 12px; -webkit-mask-image: url("https://static.xx.fbcdn.net/rsrc.php/v3/y0/r/QELw80WZC8L.png"); -webkit-mask-position: -64px -335px;': "Messenger",
}

dates = {
    "янв": 1,
    "фев": 2,
    "мар": 3,
    "апр": 4,
    "май": 5,
    "мая": 5,
    "июн": 6,
    "июл": 7,
    "авг": 8,
    "сен": 9,
    "окт": 10,
    "ноя": 11,
    "дек": 12
}

dates_eng = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12
}


class Ad:
    def __init__(self, element):
        self.image = ""
        soup = BeautifulSoup(element, "html.parser")

        self.id = soup.find("span",
                            class_="x8t9es0 xw23nyj xo1l8bm x63nzvj x108nfp6 xq9mrsl x1h4wwuj xeuugli").text.split(" ")[
            -1]

        try:
            self.text = soup.find("div", class_="_7jyr _a25-").get_text()
        except:
            try:
                self.text = soup.find("div", class_="_7jyr").get_text()
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
        try:
            self.landing = soup.find("a", class_="x1hl2dhg x1lku1pv x8t9es0 x1fvot60 xxio538 xjnfcd9 xq9mrsl x1yc453h "
                                                 "x1h4wwuj x1fcty0u x1lliihq").get("href")
        except:
            self.landing = "NO LANDING"
            # print(self.id, self.landing)

        try:

            self.download = soup.find("img", class_="x1ll5gia x19kjcj4 xh8yej3").get("src")
            self.image = self.download
            self.media_type = "Image"
        except:
            try:
                self.image = soup.find("div", class_="x1ywc1zp x78zum5 xl56j7k x1e56ztr xh8yej3").find("video").get(
                    "poster")
                self.download = soup.find("div", class_="x1ywc1zp x78zum5 xl56j7k x1e56ztr xh8yej3").find("video").get(
                    "src")
                # download link ^^^ for .mp4
                # urllib.request.urlretrieve(self.download, f'./videos/{self.id}.mp4')
                # download script ^^^
                self.media_type = "Video"
            except:
                try:
                    self.download = soup.find("img", class_="x1ll5gia x19kjcj4 x642log").get("src")
                    self.image = self.download
                    self.media_type = "Image"

                except:
                    self.download = ""
                    self.image = self.download
                    self.media_type = "Video"
        """
        try:
            self.status = soup.find("span", class_="x8t9es0 xw23nyj xo1l8bm x63nzvj x108nfp6 xq9mrsl x1h4wwuj xeuugli "
                                                   "x1i64zmx").get_text()
        except:
            self.status = soup.find("span",
                                    class_="x8t9es0 xw23nyj xo1l8bm x63nzvj x108nfp6 xq9mrsl x1h4wwuj xeuugli x1i64zmx").get_text()"""
        date = soup.find_all("div", class_="x3nfvp2 x1e56ztr")[2].get_text().split(' ')
        # date parse
        print(date)
        date = [i for i in date if i.isdigit() or i in dates or i in dates_eng or i.isalnum()]
        print(date)
        # print(date)
        if len(date) == 3:
            day, month, year = int(date[0]), dates[date[1]], int(date[2])
            self.start_date = datetime.date(year, month, day)
            self.duration = str((datetime.date.today() - self.start_date).days)
            self.start_date = str(self.start_date)
            self.end_date = "_"
            self.status = "Active"
        elif len(date) == 6:
            day, month, year = int(date[0]), dates[date[1]], int(date[2])
            self.start_date = datetime.date(year, month, day)
            day, month, year = int(date[3]), dates[date[4]], int(date[5])
            self.end_date = datetime.date(year, month, day)

            self.duration = str((self.end_date - self.start_date).days)
            self.start_date = str(self.start_date)
            self.status = "Inactive"
        else:
            self.start_date = datetime.date.today()
            self.duration = str(0)
            self. start_date = str(self.start_date)
            self.end_date = datetime.date.today()
            self.status = "Inactive"
        self.platforms = []
        for platform in soup.find_all("div", class_="xtwfq29"):
            if platform['style'] in platform_styles.keys():
                self.platforms.append(platform_styles[platform['style']])
        self.platforms = ";".join(self.platforms)

    def get_data(self):
        return self.id, self.text, self.buttonText, self.landing, self.download, self.status, self.start_date, \
               self.duration, self.platforms


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
            if ad.status == "Active":
                count += 1
        return count

    def count_inactive(self):
        count = 0
        for ad in self.ads:
            if ad.status == "Inactive":
                count += 1
        return count
