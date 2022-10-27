import bs4 as bs
import requests
from datetime import date
import os

if __name__ == "__main__":

    #Big topics are stored in a div at the top of the page.

    url = "https://www.bbc.co.uk/news"

    home_page = requests.get(url).text

    da_soup = bs.BeautifulSoup()

    