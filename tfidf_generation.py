from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from SkyScraper import sky_main
from os import listdir, getcwd
from os.path import isfile, join
import pandas as pd
import numpy as np

if __name__ == "__main__":

    # articles_to_use = sky_main()
    my_path = getcwd() + "/Articles/Cached"

    articles_to_use = [my_path + "/" + f for f in listdir(my_path) if isfile(join(my_path, f))]

    # print(len(articles_to_use))

    # articles_to_use = articles_to_use[:10]

    #Need to include stop words for now due to size of data set I guess.
    tfidf = TfidfVectorizer(input = "filename", smooth_idf = False, stop_words="english")

    tfidf_array = tfidf.fit_transform(articles_to_use)

    print(tfidf_array.toarray()[:,7835])

    words = tfidf.get_feature_names_out()

    print(np.where(words == "the"))

    number_of_components = 12
    nmf_model = NMF(n_components=number_of_components, max_iter = 1000)

    nmf_model.fit(tfidf_array)

    nmf_articles = nmf_model.transform(tfidf_array)

    # print(nmf_articles.round(2))

    components_df = pd.DataFrame(nmf_model.components_, columns = words)

    # Select row 3: component
    for i in range(number_of_components):
        component = components_df.iloc[i]

        # Print result of nlargest
        print(component.nlargest(5))
        print("")
