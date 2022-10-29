class User():

    def __init__(self, name): 
        self.username = name
        user_profile_path = "UserProfiles/" + name + ".txt"
        self.load(user_profile_path)

    def load(self, path: str):
        self.articles_opinions = {}
        with open(path, "r") as file:
            for line in file:
                article_name, rating = line.split(",")
                self.articles_opinions[article_name] = float(rating)

    def get_articles(self):
        return list(self.articles_opinions.keys())

    def get_opinion(self, title):
        return self.articles_opinions[title]

    def save_opinions(self, opinions):
        user_profile_path = "UserProfiles/" + self.username + ".txt"
        with open(user_profile_path, "a") as file:
            for article in opinions:
                line = article + "," + str(opinions[article]) + "\n"
                file.write(line)

if __name__ == "__main__":

    user = User("Elfikk")
    # print(user.get_opinion("article_1"))
    
    opinions = {str(i): 1.0 for i in range(5)}

    user.save_opinions(opinions)