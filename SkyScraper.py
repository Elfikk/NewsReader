import bs4 as bs
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import date

def convert_date_sky(time_string):
    
    month_to_number = {"January": 1,
                       "February": 2,
                       "March": 3,
                       "April": 4,
                       "May": 5,
                       "June": 6,
                       "July": 7,
                       "August": 8,
                       "September": 9,
                       "October": 10,
                       "November": 11,
                       "December": 12                       
                        }
    
    time_list = time_string.split(" ")
    day, month, year = time_list[1], time_list[2], time_list[3]

    month_int = month_to_number[month]

    article_date = date(int(year), month_int, int(day))

    return article_date

def compare_date(conversion_func, time_string):

    article_date = conversion_func(time_string)

    current_date = date.today()

    delta = current_date - article_date

    return delta    

#For Sky News (1-6)
#1. Open home page. x
#2. Select all <a> tags inside the header div - inside the li 
#   <li class="sdc-site-header__menu-item"> ignoring the videos. x
#3. These give /topic so news.sky.com/topic for each. 
#4. For each topic, catch all the links below the header for articles.
#   All hrefs are given relative to news.sky.com so any link to an 
#   external resource should be ignored.
#5. Having compiled a list of all articles currently featured on the
#   site, visit all articles. 
#6. If an article has been published within the last 3 days, compile
#   all the *relevant* text from it (headline, intro, text that is
#   not a link to other media.)
#7. Compiled text then will be passed to form tf-idf word arrays.
#8. tf-idf word arrays to NNMF.
#9. User NNMF profile from previous articles + opinions on articles
#   to give recommended article. If liked, convert tts, and play. 

base_url = "https://news.sky.com"

html_content = requests.get(base_url).text

da_soup = bs.BeautifulSoup(html_content, "html.parser")

# print(da_soup.prettify())

topic_navigation = da_soup.find_all("li", {"class" : "sdc-site-header__menu-item"})

topic_links = set()
excluded_topics = set(("Videos", "Weather"))

for list_element in topic_navigation:
    a_tag = list_element.a
    if a_tag.text not in excluded_topics:
        topic_links.add(a_tag["href"])

print(topic_navigation[0].a["href"])
print(topic_links)

# Criteria for being collected as an article.
# 1. Don't be an external link - must start with "/", but not with a "//".
# 2. Don't be a damn video link - don't start with a "/video".
# 3. Don''t be an info link.
# 4. Don't be one of the header links.
# All of this is summarised by "/story" actually.

# topic_links = ["/uk"]

wanted_links = set()

for topic_url in topic_links:
    url = base_url + topic_url

    html_content = requests.get(url).text

    da_soup = bs.BeautifulSoup(html_content, "html.parser")

    all_link_tags = da_soup.find_all("a")
    # all_link_tags = [all_link_tags[-1]]
    # wanted_links = set()

    # print(all_link_tags)

    for tag in all_link_tags:
        link = tag["href"]
        if link[:6] == "/story":
            # print(link)
            wanted_links.add(link)

print(len(wanted_links))

# Criteria for being stored as an article.
# 1. Date is within the last 3 days. 
# 2. Not a live article - doesn't contain something like:
#   <a class="sdc-article-tags__link" href="/topic/live-7029">LIVE</a>.

count = 0
link_count = 0

for link in wanted_links:
    #Oh boi here we go again.

    link_count += 1

    print(link_count)

    url = base_url + link

    article_text = requests.get(url).text

    da_soup = bs.BeautifulSoup(article_text, "html.parser")

    tag_as = da_soup.find_all("a", {"class": "sdc-article-tags__link"})

    live = False

    for a in tag_as:
        if a.text == "LIVE":
            live = True

    if not live:
        danger_title = "The beautifully simple way to build brand and feature stories for the web."
        if not da_soup.find("a", {"title": danger_title}):
            article_date_tag = da_soup.find("p", {"class": "sdc-article-date__date-time"})
            try:
                article_date = article_date_tag.text
                delta = compare_date(convert_date_sky, article_date)
                if delta.days < 3:
                    count += 1
            except: 
                #Some silly articles don't have a date (these seem
                #to be the ones written in Shorthand)
                #Also newspaper headlines articles. This could be 
                #excluded by doing a text check of <h1>.
                print(url)

print(count)   

#107 articles from 292 articles would have text extracted, initially.

# test_link = "https://news.sky.com/story/ukraine-latest-news-putin-bombs-energy-facilities-across-ukraine-as-30-of-power-stations-wiped-out-12541713"

# test_text = requests.get(test_link).text

# test_soup = bs.BeautifulSoup(test_text, "html.parser")

# test_as = test_soup.find_all("a", {"class": "sdc-article-tags__link"})

# for a in test_as:
#     if a.text == "LIVE":
#         print("Trouble")

# print(test_as)

