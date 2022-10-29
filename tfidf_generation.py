from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from os import listdir, getcwd
from os.path import isfile, join
import pandas as pd
import numpy as np
from sklearn.preprocessing import normalize
import pandas as pd

def generate_NMF_components(articles_to_use, n_components):
    #Generates tfidf array and fits the NMF model and normalises them.
    #Articles to use should be a list of the filenames to be read by
    #TfidVectorizer for analysis. Articles which are to be removed
    #from recommendation (user stored articles) should be placed
    #as the last n elements for later simple removal.

    tfidf = TfidfVectorizer(input = "filename", smooth_idf = False, \
        stop_words="english")

    tfidf_array = tfidf.fit_transform(articles_to_use)
    # words = tfidf.get_feature_names_out()

    nmf_model = NMF(n_components, max_iter = 1000)
    nmf_model.fit(tfidf_array)

    nmf_articles = nmf_model.transform(tfidf_array)

    norm_articles = normalize(nmf_articles)

    return norm_articles

def recommend_article(norm_articles, article_names, user_vector, \
    prev_articles = None):
    #Calculates the dot product between the user preference vector with
    #each analysed article. The article with the highest score that is
    #not 95% similar or above in topic space to previous articles is 
    #returned.

    article_df = pd.DataFrame(norm_articles, index = article_names)
    if prev_articles is not None: #numpy arrays dont like being if None'd
        to_compare =  np.column_stack((user_vector, prev_articles))
        similarities = article_df.dot(to_compare)
        cols_to_filter = prev_articles.shape[1]
        for i in range(1, cols_to_filter + 1):
            #0.95 is arbitrary threshhold (related articles but with the 
            #story evolving have about 0.9, so 0.95 may be alright 
            #- will see in testing)
            similarities = similarities[similarities[i] < 0.95]
        print(similarities.head(10))
        return str(similarities.nlargest(1, 0).index.item())
    else:
        similarities = article_df.dot(user_vector)
        print(similarities.head(10))
        return str(similarities.nlargest(1).index.item())


def generate_user_vector(user, article_to_id, norm_articles, dimensions):
    #Finds an average vector in the generated NMF space of the user's 
    #opinions on previous articles and a blank slate user (no opinions).

    user_articles = user.get_articles()

    user_vector = 1/dimensions**0.5 * np.ones(dimensions, dtype = float)

    for article in user_articles:
        article_id = article_to_id[article]
        article_vector = norm_articles[article_id]
        opinion = user.get_opinion(article)

        user_vector += opinion * article_vector

    norm = np.dot(user_vector, user_vector)**0.5
    user_vector = user_vector / norm

    return user_vector

def update_user_vector(user_vector, article_vector, opinion):
    
    user_vector = user_vector + opinion * article_vector
    norm = np.dot(user_vector, user_vector)**0.5
    user_vector = user_vector / norm

    return user_vector

if __name__ == "__main__":

    dims = 14

    # articles_to_use = sky_main()
    my_path = getcwd() + "/Articles/Cached"

    articles_to_use = [my_path + "/" + f for f in listdir(my_path) \
        if isfile(join(my_path, f))]

    pre_path_length = len(my_path) + 1

    index_to_article = {i: articles_to_use[i][pre_path_length:-4]\
        for i in range(len(articles_to_use))}    
    article_to_index = {index_to_article[i]: i for i in \
        range(len(articles_to_use))}

    # print(article_to_index)

    article_1 = "httpsnewsskycomstoryliz-truss-to-resign-as-prime-minister-sky-news-understands-12723236"
    index_1 = article_to_index[article_1]
    article_2 = "httpsnewsskycomstoryliz-truss-resignation-speech-outside-downing-street-in-full-12725499"
    index_2 = article_to_index[article_2]

    norm_articles = generate_NMF_components(articles_to_use, dims)
    print(type(norm_articles), norm_articles.shape)
    user_vector = np.ones(dims, dtype = float)
    user_vector = user_vector / dims**0.5

    prev_articles = np.column_stack((norm_articles[0], norm_articles[1]))
    print(prev_articles.shape)
    print(np.dot(norm_articles[index_1], norm_articles[index_2]))

    next_article = recommend_article(norm_articles, \
        list(article_to_index.keys()), user_vector, prev_articles)
    print(next_article)

    # print(index_to_article[0])
    # print(article_to_index["httpsnewsskycomstoryafghan-refugee-couple-accuse-us-marine-of-abducting-their-baby-12725817.txt"])

    # #Need to include stop words for now due to size of data set I guess.
    # tfidf = TfidfVectorizer(input = "filename", smooth_idf = False, stop_words="english")

    # tfidf_array = tfidf.fit_transform(articles_to_use)

    # words = tfidf.get_feature_names_out()

    # number_of_components = 10
    # nmf_model = NMF(n_components=number_of_components, max_iter = 1000)

    # nmf_model.fit(tfidf_array)

    # nmf_articles = nmf_model.transform(tfidf_array)

    # print(nmf_articles.shape)

    # nmf_articles = nmf_articles[:-15]

    # print(nmf_articles.shape)

    # # for article in nmf_articles:
    # #     norm = np.dot(article, article)**0.5
    # #     article = article / norm

    # # for article in nmf_articles:
    # #     a = np.dot(article, article)
    # #     if a > 0.1:
    # #         print(a)

    # components_df = pd.DataFrame(nmf_model.components_, columns = words)

    # # # Select row 3: component
    # # for i in range(number_of_components):
    # #     component = components_df.iloc[i]

    # #     # Print result of nlargest
    # #     print(component.nlargest(5))
    # #     print("")
