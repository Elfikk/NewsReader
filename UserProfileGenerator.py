class User():

    def __init__(self, name): 
        user_profile_path = "UserProfiles/" + name + ".txt"
        self.load(user_profile_path)

    def load(self, path: str):
        self.articles_opinions = {}
        with open(path, "r") as file:
            for line in file:
                article_name, rating = line.split(",")
                self.articles_opinions[article_name] = rating

    def get_articles(self):
        return list(self.articles_opinions.keys())

    
    


if __name__ == "__main__":

    user = User("Elfikk")
    