from SkyScraper import sky_main
from tfidf_generation import generate_NMF_components,\
                             recommend_article, \
                             generate_user_vector, update_user_vector
from UserProfileGenerator import User
import pyttsx3
from os import getcwd, listdir
from os.path import isfile, join
from article_utils import generate_title, copy_new_user_articles
import numpy as np

#Log user in (I mean do you really need a password here?)
user_name = input("Username: ")
my_path = getcwd() + "/UserProfiles/"
user_file = my_path + user_name + ".txt"
if isfile(user_file):
    user = User(user_name)
else:
    new_user_file = "UserProfiles/" + user_name + ".txt"
    with open(new_user_file, "w") as file:
        pass
    user = User(user_name)

print("User loaded")

#Scrape latest news. Currently only Sky News.
latest_news = sky_main()

print("Articles scraped")

#Generate article paths for NMF analysis.
user_articles = user.get_articles()

#Do not want to pass the same article twice to NMF + articles that a
#user already has an opinion on shouldn't be shown to them again 
#(they have already interacted with them!)
user_articles_files = set([article + ".txt" for article in user_articles])

cached_path = getcwd() + "/Articles/Cached/"
latest_news_paths = [cached_path + f for f in listdir(cached_path) \
    if isfile(join(cached_path, f)) and f not in user_articles_files]

user_path = getcwd() + "/Articles/Users/"
user_articles_paths = [user_path + f for f in listdir(user_path) \
                       if isfile(join(user_path, f))]
N_user_articles = len(user_articles_paths)

articles_to_use = latest_news_paths + user_articles_paths

fudge_factor = {i: 0 if articles_to_use[i][len(user_path)] == "h" \
    else 1 for i in range(len(articles_to_use))}
index_to_article = {i: articles_to_use[i][len(user_path) + fudge_factor[i]:-4]\
    for i in range(len(articles_to_use))}    
article_to_index = {index_to_article[i]: i for i in range(len(articles_to_use))}

print(fudge_factor)
print(article_to_index)

article_names = [index_to_article[i] for i in range(len(fudge_factor)) \
                 if fudge_factor[i] == 1]

print(article_names)

#NMF'd articles:
dimensions = len(articles_to_use) // 20
norm_articles = generate_NMF_components(articles_to_use, dimensions)
if N_user_articles != 0:
    norm_cached_articles = norm_articles[:len(norm_articles)-N_user_articles]
else:
    norm_cached_articles = norm_articles
user_vector = generate_user_vector(user, article_to_index, norm_articles,\
    dimensions)

print(norm_articles)
print(norm_cached_articles)

print("NMF complete")

#Initialise tts engine.
engine = pyttsx3.init()
voices = engine.getProperty("voices")
rate = engine.getProperty("rate")   
# print(rate)
# print(voices)

#French voice is kind of comical. (that's number 2)
engine.setProperty("voice", voices[0].id)
engine.setProperty("rate", 150) #Above 160 wpm is too fast to absorb information.

print("TTS initialisation complete")

#Main loop setup.
not_quit = True
prev_articles = None
article_opinions = {}

#Main loop.
while not_quit:

    article = recommend_article(norm_cached_articles, article_names, \
                                user_vector, prev_articles)

    article_title = generate_title(article)

    print(article_title)

    valid_input = False

    while not valid_input:

        read_article = input("Read article? Y/N")

        if read_article.upper() == "Y":
            
            valid_input = True
            article_path = "Articles/Cached/" + article + ".txt"

            to_read = ""

            with open(article_path, "r", encoding="utf8") as f:
                for line in f:
                    to_read = line

            engine.say(to_read)
            engine.runAndWait()

            opinion = input("Did you like the article? Y/N")
            if opinion.upper() == "Y":
                article_opinions[article] = 1.0
            elif opinion.lower() == "N":
                article_opinions[article] = -1.0

        elif read_article.upper() == "N": 
            valid_input = True
            article_opinions[article] = -1.0
        
        else:
            print("invalid input")

    article_vector = norm_cached_articles[article_to_index[article]]
    user_vector = update_user_vector(user_vector, article_vector, \
        article_opinions[article])

    if prev_articles is not None:
        prev_articles = np.column_stack([prev_articles, article_vector])
    else:
        prev_articles = article_vector.reshape((-1, 1))

    wanna_quit = input("Quit? Y/N")

    if wanna_quit.upper() == "Y" :
        not_quit = False
    
#User Profile updates having finished the session.
user.save_opinions(article_opinions)
copy_new_user_articles(article_opinions)