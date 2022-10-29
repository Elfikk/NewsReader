import bs4 as bs
import requests
from datetime import date
import os

#Get it? Its like a tall building, but its the web scraping for Sky News!
#Hilarious, I know.

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

def generate_scrape_links(base_url, tag_type, tag_attribute, tag_attribute_content, excluded_topics):

    html_content = requests.get(base_url).text
    da_soup = bs.BeautifulSoup(html_content, "html.parser")
    topic_navigation = da_soup.find_all(tag_type, {tag_attribute: tag_attribute_content})

    topic_links = set()

    for topic_tag in topic_navigation:
        a_tag = topic_tag.a
        if a_tag.text not in excluded_topics:
            topic_links.add(a_tag["href"])

    return topic_links

def sky_scrape_links():
    return generate_scrape_links("https://news.sky.com",
                                 "li",
                                 "class",
                                 "sdc-site-header__menu-item",
                                 set(("Videos", "Weather"))
                                )

def generate_article_links(topic_urls, collection_criterion_func):

    wanted_links = set()

    for topic_url in topic_urls:

        html_content = requests.get(topic_url).text

        da_soup = bs.BeautifulSoup(html_content, "html.parser")

        all_link_tags = da_soup.find_all("a")

        for tag in all_link_tags:
            if collection_criterion_func(tag):
                wanted_links.add(tag["href"])

    return wanted_links

def sky_collection_criterion(tag):
    link = tag["href"]
    return link[:6] == "/story"

def generate_file_name(url):

    excluded_characters = set((":", "/", "."))

    file_name_list = []
    for character in url:
        if character not in excluded_characters:
            file_name_list.append(character)

    file_name = "".join(file_name_list)

    return file_name

def check_article_cached(url):

    file_name = generate_file_name(url)
    current_path = os.getcwd()
    to_check_path = current_path + "/Articles/Cached/" + file_name + ".txt"

    return os.path.isfile(to_check_path)

def sky_main():

    base_url = "https://news.sky.com"

    topic_links_relative = sky_scrape_links()
    topic_links = set([base_url + relative_path for relative_path in topic_links_relative])
    print(topic_links)

    # Criteria for being collected as an article.
    # 1. Don't be an external link - must start with "/", but not with a "//".
    # 2. Don't be a damn video link - don't start with a "/video".
    # 3. Don''t be an info link.
    # 4. Don't be one of the header links.
    # All of this is summarised by "/story" actually.

    wanted_links = generate_article_links(topic_links, sky_collection_criterion)

    print(len(wanted_links))

    # Criteria for being stored as an article.
    # 1. Date is within the last 3 days. 
    # 2. Not a live article - doesn't contain something like:
    #   <a class="sdc-article-tags__link" href="/topic/live-7029">LIVE</a>.

    count = 0
    link_count = 0

    used_articles = set()

    for link in wanted_links:
        #Oh boi here we go again.

        link_count += 1

        url = base_url + link

        if not check_article_cached(url):
            article_text = requests.get(url).text
            da_soup = bs.BeautifulSoup(article_text, "html.parser")

            tag_as = da_soup.find_all("a", {"class": "sdc-article-tags__link"})

            #Dont want "live" articles to be scraped.
            live = False
            for a in tag_as:
                if a.text == "LIVE":
                    live = True

            if not live:
                # Articles with a completely different style to most (only 4 
                # in 300 pulled)
                danger_title = "The beautifully simple way to build brand and feature stories for the web."
                if not da_soup.find("a", {"title": danger_title}):
                    article_date_tag = da_soup.find("p", {"class": "sdc-article-date__date-time"})
                    try:
                        article_date = article_date_tag.text
                        delta = compare_date(convert_date_sky, article_date)
                        if delta.days <= 3:
                            count += 1
                            file_name = generate_file_name(url)
                            p_tags = da_soup.find_all("p")
                            title = da_soup.h1.text
                            news_text_list = [title]

                            excluded_classes = set(("sdc-article-related-stories__link-text",
                                                    "sdc-article-date__date-time",
                                                    "sdc-news-footer__list-logo",
                                                    "sdc-site-video__accessibility-message",
                                                    "sdc-article-author__role"))

                            for p in p_tags:
                                class_tags = p.get("class")
                                not_excluded_class = True
                                if class_tags: #Possible to not have a tag, returning a None object - gives False
                                    for class_tag in class_tags:
                                        if class_tag in excluded_classes:
                                            not_excluded_class = False
                                if not_excluded_class:
                                    text = p.text
                                    if text[:9].lower() != "read more":
                                        news_text_list.append(p.text)

                            news_text = " ".join(news_text_list)

                            file_name = generate_file_name(url)

                            with open("Articles/Cached/" + file_name + ".txt", "w", encoding="utf-8") as f:
                                f.write(news_text)

                            used_articles.add(file_name)
                
                    except: 
                        #Some silly articles don't have a date (these seem
                        #to be the ones written in Shorthand)
                        #Also newspaper headlines articles. This could be 
                        #excluded by doing a text check of <h1>.
                        print(url)
        else:
            file_name = generate_file_name(url) + ".txt"
            used_articles.add(file_name)

        # print(link_count, count)

    return used_articles

    #107 articles from 292 articles would have text extracted, initially.
    #Actually that was the last 2 days' news, so a few more (122 from 296 the next day!)

def generate_title_sky(file_name):
    opener_length = len("httpsnewsskycomstory")
    split_name = file_name.split("-")[:-1] #Last part is a unique ID for the article.
    split_name[0] = split_name[0][opener_length:]

    split_title = [title_part.capitalize() for title_part in split_name]

    return " ".join(split_title)

#For Sky News (1-6)
#1. Open home page. x
#2. Select all <a> tags inside the header div - inside the li 
#   <li class="sdc-site-header__menu-item"> ignoring the videos. x
#3. These give /topic so news.sky.com/topic for each. x
#4. For each topic, catch all the links below the header for articles.
#   All hrefs are given relative to news.sky.com so any link to an 
#   external resource should be ignored. x
#5. Having compiled a list of all articles currently featured on the
#   site, visit all articles. x
#6. If an article has been published within the last 3 days, compile
#   all the *relevant* text from it (headline, intro, text that is
#   not a link to other media.) x
#7. Compiled text then will be passed to form tf-idf word arrays.
#8. tf-idf word arrays to NNMF.
#9. User NNMF profile from previous articles + opinions on articles
#   to give recommended article. If liked, convert tts, and play. 

if __name__ == "__main__":

    # sky_title = "httpsnewsskycomstoryherschel-walker-former-nfl-star-and-senate-candidate-accused-by-second-woman-of-pressuring-her-to-have-abortion-12731153"

    # print(generate_title_sky(sky_title)) #as intended

    sky_main()

