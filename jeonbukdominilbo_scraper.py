import os
import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_response(url:str):
    response = requests.get(url)

    return response

def get_paragraph(url:str):
    response = get_response(url)
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")

    article_view = soup.find(id="article-view-content-div")
    paragraphs = article_view.get_text().split("저작권자 © 전북도민일보 무단전재 및 수집, 재배포 금지")[0]

    return paragraphs

def get_article_list(page_num:int):
    url_base = f"https://www.domin.co.kr/news/articleList.html?page={page_num}&sc_section_code=&sc_sub_section_code=S2N39&sc_serial_code=&sc_area=&sc_level=&sc_article_type=&sc_view_level=&sc_sdate=&sc_edate=&sc_serial_number=&sc_word=&sc_word2=&sc_andor=&sc_order_by=E&view_type=sm"
    response = get_response(url_base)
    
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
    article_list = soup.find(class_="article-list-content type-sm text-left")
    list_blocks = article_list.find_all(class_="list-block")

    is_done = False
    titles = []
    urls = []
    summaries = []
    bylines_0 = []
    bylines_1 = []
    bylines_2 = []
    articles = []
    for list_block in list_blocks:
        list_title = list_block.find(class_="list-titles")
        title = list_title.find("a").get_text()
        url = "http://www.domin.co.kr" + list_title.find("a").get("href")
        summary = list_block.find(class_="list-summary").get_text()
        bylines = list_block.find(class_="list-dated").get_text().split(" | ")
        byline_0 = bylines[0]
        byline_1 = bylines[1]
        byline_2 = bylines[2]
        article = get_paragraph(url)

        date = datetime.datetime.strptime(byline_2, "%Y-%m-%d %H:%M")
        if date < datetime.datetime(2018, 5, 1):
            is_done = True
            break
        
        titles.append(title)
        urls.append(url)
        summaries.append(summary)
        bylines_0.append(byline_0)
        bylines_1.append(byline_1)
        bylines_2.append(byline_2)
        articles.append(article)
    
    result_df = pd.DataFrame(
        {
            "titles": titles,
            "urls": urls,
            "summaries": summaries,
            "bylines_0": bylines_0,
            "bylines_1": bylines_1,
            "bylines_2": bylines_2,
            "articles": articles,
        }
    )

    return result_df, is_done

if __name__ == "__main__":
    if not os.path.exists("./result"):
        os.makedirs("./result")

    result_dir = os.path.join("./result", "jeonbukdominilbo")
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    page_num = 1

    while True:
        result_df, is_done = get_article_list(page_num)
        result_df.to_csv(os.path.join(result_dir, f"jeonbukdominilbo_opinions_p{page_num}.csv"), encoding="utf-8-sig")
        print(f"{page_num} 페이지 스크랩 완료")

        if is_done:
            break

        page_num+=1