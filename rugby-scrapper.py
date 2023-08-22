from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import requests

class MonInternet :
    START_URL = "https://tickets.rugbyworldcup.com/fr"
    # = "https://pypi.org/project/webdriver-manager/"
    
    def __init__(self) -> None:
        """
            Initialize the driver and its options
        """
        
        # Options
        self.options = Options()
        # self.options.add_argument('--headless')
        self.options.add_argument("--incognito")
        self.options.add_argument("--nogpu")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1280,1280")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--enable-javascript")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument('--disable-blink-features=AutomationControlled')

        # User agent
        ua = UserAgent()
        self.userAgent = ua.random

        # Driver
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": self.userAgent})

        # timer to autodestruction
        self.timer = time.time()

    def start(self) :
        """
            Start by looking the first url
        """
        self.driver.get(self.START_URL)
        time.sleep(2)

    def enterQueue(self) :
        """
            Check if there is a button to enter the queue
        """
        # Find the button to enter the queue and if so, click it!
        # print("Entering Queue..")
        try :
            button = self.driver.find_element(By.CLASS_NAME, "btn.btn-primary")
            button.click()
            time.sleep(3)
            # wait until a venue is available (ie we are no longer in queue)
            #TODO timeout error
            element = WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.CLASS_NAME, "venue"))
            )
            time.sleep(3)
            # print("Out of the queue")
        except NoSuchElementException :
            # print("HOLA")
            pass

    def findMatches(self) :
        """
            Find all the matches and their availabilities
        """
        elements = self.driver.find_elements(By.CLASS_NAME, "list-ticket-content")
        all_games = []
        for element in elements :
            if len(text_splitted := element.text.split("\n")) != 3:
                continue
            teams = text_splitted[0].replace("Nouvelle-Zélande", "Nouvelle Zélande").split('-')
            availability = text_splitted[-1]

            all_games.append({
                "teamA" : teams[0],
                "teamB" : teams[1],
                "available" : availability
            })

        return all_games

    def refresh(self) :
        """
            Refresh the page
        """
        time.sleep(30)
        self.driver.refresh()
        time.sleep(5)

    def writeSourceCode(self) :
        """
            Save the page source code in page_source.html
        """
        with open("page_source.html", "w") as file:
            file.write(self.driver.page_source)

    def timeToDestroy(self) :
        return time.time() - self.timer > 10 * 60

    def closeDriver(self) :
        """
            Close the driver
        """
        self.driver.quit()

class SendMessage :
    URL = "https://maker.ifttt.com/trigger/{}/with/key/{}"

    def __init__(self, persons, matches_relevant) -> None:
        self.matches_relevant = matches_relevant
        self.persons = persons
        self.internet = None

    def loop(self) :
        """
            A loop through the whole process
        """
        if self.internet is None :
            self.internet = MonInternet()
            self.internet.start()
            self.internet.enterQueue()

        if self.internet.timeToDestroy() :
            self.internet.closeDriver()
            self.internet = MonInternet()
            self.internet.start()
            self.internet.enterQueue()

        matches = self.internet.findMatches()
        self.process(matches)

    def process(self, matches) :
        """
            matches : dict avec key teamA, teamB, available
            return les matches qui sont dans nos matches à regarder
            envoie une notif à toutes les personnes pour ces matches
        """
        matches_final = [m for m in matches if "{} {}".format(m["teamA"], m["teamB"]) in self.matches_relevant]
        matches_final = [m for m in matches_final if m["available"] != "NON DISPONIBLE"]

        for match in matches_final :
            teamA = match["teamA"]
            teamB = match["teamB"]
            for person in self.persons :
                self.sendNotif(person, "{} vs {}".format(teamA, teamB))

    def sendNotif(self, person, match) :
        """
            person is the key of the user
        """
        data = {"value1" : match}
        url_bis = self.URL.format("matches", person)

        requests.post(url_bis, json=data)

    def mainLoop(self) :
        """
            Mainloop
        """
        i = 0
        while i < 2 :
            self.loop()
            self.internet.refresh()
            i += 1

matches_relevant = ["Italie Namibie", "France Nouvelle Zélande"]
persons = ["f5cnM1-nnRUAQUhYTo9Y6WnUF7yVrB7AA_3pe5Asm87"]

if __name__ == "__main__" :
    x = SendMessage(persons, matches_relevant)
    x.mainLoop()