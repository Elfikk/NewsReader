from SkyScraper import generate_title_sky
import shutil

def generate_title(file_name):
    #Shortcut method to not have to worry which exact title conversion 
    #for some file name. Expected file name without extension, though
    #likely implementations will work fine with one.

    openings = {
        "httpsnewsskycomstory" : generate_title_sky
    }

    for opening in openings:
        opening_length = len(opening)
        if file_name[:opening_length] == opening:
            return openings[opening](file_name)

    return file_name

def copy_new_user_articles(opinions):
    #Articles which have been rated by the user are copied to the Users 
    #folder at the end of a session.

    for article in opinions:
        source = "Articles/Cached/" + article + ".txt"
        destination = "Articles/Users"
        shutil.copy(source, destination)

if __name__ == "__main__":
    
    # articles = [
    #     "httpsnewsskycomstoryherschel-walker-former-nfl-star-and-senate-candidate-accused-by-second-woman-of-pressuring-her-to-have-abortion-12731153",
    #     "httpsnewsskycomstoryolivia-pratt-korbel-new-arrest-by-detectives-investigating-murder-of-nine-year-old-in-liverpool-12732727",
    #     "httpsnewsskycomstorycelebrities-and-sports-stars-named-as-uks-most-influential-black-people-but-trailblazing-businesswoman-takes-top-spot-12731849",
    #     "httpsnewsskycomstoryeu-interest-rates-at-decade-high-fuelling-european-recession-fears-12731414",
    #     "httpsnewsskycomstorysassy-penguins-thoughtful-bears-and-less-than-impressed-lions-the-comedy-wildlife-photography-awards-12724593"    
    # ]

    # opinions = {article: 1.0 for article in articles}

    # save_new_user_articles(opinions) #Works as intended!

    pass