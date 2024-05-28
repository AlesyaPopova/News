import requests
from bs4 import BeautifulSoup
import re
from dateutil import parser
from datetime import datetime, timedelta
from time import sleep

URL = "https://www.usatoday.com/news/politics/"
# заголовки запроса
HEADERS = {
    "Accept": "text/html",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"
}
# поисковая фраза
PHRASE = "Trump"
# длительность запуска, в 10-минутных интервалах
DURATION: int = 4 * 6
# время ожидания новостей, в секундах
SLEEP_TIME = 60 * 10


def get_news(date_from: datetime) -> datetime:
    req = requests.get(URL, HEADERS)

    # считываем текст HTML-документа
    soup = BeautifulSoup(req.text, 'lxml')

    # основной контейнер с блоком новостей
    results = soup.find("div", class_="gnt_m_flm")

    # контейнеры с новостями
    elements = results.find_all("a", class_="gnt_m_flm_a")

    # поисковая фраза
    my_regex = re.compile(".*" + PHRASE + ".*", re.IGNORECASE)

    last_datetime = date_from

    for element in elements:
        # пример контейнера с новостью:
        # <a class="gnt_m_flm_a" data-c-br="The president said while his son did not perish on the battlefield, it was a consequence of being in the army and working next to a burnfield." data-t-l=":list|o|c|1" href="/story/news/politics/2024/05/27/biden-memorial-day-message-arlington-national-cemetery/73868766007/">
        #  <img alt="" class="gnt_m_flm_i" data-g-r="lazy_c" data-gl-src="/gcdn/authoring/authoring-images/2024/05/27/USAT/73868829007-biden-m-day.jpg?crop=5504,5503,x1651,y0&amp;width=120&amp;height=120&amp;format=pjpg&amp;auto=webp" data-gl-srcset="/gcdn/authoring/authoring-images/2024/05/27/USAT/73868829007-biden-m-day.jpg?crop=5504,5503,x1651,y0&amp;width=240&amp;height=240&amp;format=pjpg&amp;auto=webp 2x" decoding="async"/>
        #  Memory can 'reopen that black hole': Biden says at Memorial Day tribute
        #  <div class="gnt_m_flm_sbt gnt_sbt gnt_sbt__ms gnt_sbt__ts" data-c-dt="2:27 p.m. ET May 27" data-c-ms="POLITICS" style="--gnt-bc:#626262">
        #  </div>
        # </a>

        annotation = element["data-c-br"]
        title = element.text
        link = element["href"]
        datetime_element = element.find(class_="gnt_sbt__ts")
        datetime_str = datetime_element["data-c-dt"]

        # "2:27 p.m. ET May 27" -> в datetime
        news_datetime = parser.parse(datetime_str.replace("ET", ""))

        if my_regex.match(title) or my_regex.match(annotation):
            if news_datetime > date_from:
                print(news_datetime, "\ntitle:", title, "\nannotation: ", annotation, "\nlink: ", link, "\n")
                if news_datetime > last_datetime:
                    last_datetime = news_datetime

    return last_datetime


from_date = datetime.now() - timedelta(hours=24*4)

for x in range(0, DURATION):
    from_date = get_news(from_date)

    print(datetime.now(), "last news date: ", from_date)
    sleep(SLEEP_TIME)

print("done")
