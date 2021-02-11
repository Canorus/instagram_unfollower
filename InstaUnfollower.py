from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from logg import *

# successful on 2021. Jan. 25.
# Firefox 84.0.2
# geckodriver 0.28.0
# 5,089 accounts
# may or may not work later
# highly likely you'll need to fix some elements to work properly

class InstagramUnfollower:

    _username = None
    _blacklist = []

    def __init__(self, username, password, unfollowing_speed):
        logger.info('username: ' + str(username))
        self.username = username # the username of your instagram account
        self.password = password # the password of your instagram account
        self.unfollowing_speed = unfollowing_speed
        options = webdriver.FirefoxOptions()
        options.headless = True
        if os.path.isfile('/usr/local/bin/geckodriver'):
            self.driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver', options=options)
        else:
            self.driver = webdriver.Firefox(executable_path='/usr/bin/geckodriver', options=options) #specifies the driver which you want to use)

    def login(self): # method to login into your account
        logger.debug('begin login function')
        driver = self.driver
        driver.get("https://www.instagram.com/")
        time.sleep(2)
        #login_button = driver.find_element_by_xpath("//a[@href='/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div/div[3]']")
        #login_button.click()
        time.sleep(2)
        username_box = driver.find_element_by_xpath("//input[@name='username']")
        username_box.clear()
        username_box.send_keys(self.username)
        password_box = driver.find_element_by_xpath("//input[@name='password']")
        password_box.clear()
        password_box.send_keys(self.password)
        password_box.send_keys(Keys.RETURN)
        time.sleep(3)
        try: # these may or may not happen on other login scenario, I'll just put them in try except condition
            not_now_button =  driver.find_element_by_xpath("/html/body/div[1]/section/main/div/div/div/div/button")
            not_now_button.click()
        except:
            pass
        time.sleep(5)
        try:
            no_noti_button = driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div/div/div/button')
            no_noti_button.click()
        except:
            logger.debug('noti button exception occurred')
            pass
        time.sleep(4)

    def find_username(self): # finds the username in the case of the program user is entered an e-mail adress instead of the username as a login info
        driver = self.driver
        self._username = driver.find_element_by_xpath("/html/body/div[1]/section/main/section/div[3]/div[1]/div/div/div[2]/div[1]/div/div/a").text

    def xpath_exists(self, xpath):
        driver = self.driver
        try:
            driver.find_element_by_xpath(xpath)
            return True
        except:
            return False

    def find_followings(self, driver, buttons, interval) -> int: # this functions finds the accounts who are followed by us
        logger.debug('begin find_followings function')
        # who do we follow
        try:
            self.following_button = [button for button in buttons if 'following' in button.get_attribute('href')]
        except:
            buttons = driver.find_elements_by_xpath("//a[@class='-nal3 ']")
            self.following_button = [button for button in buttons if 'following' in button.get_attribute('href')]
        self.following_button[0].click()
        time.sleep(2)
        #self.following_window = driver.find_element_by_xpath("//div[@role='dialog']//a")
        self.following_window = driver.find_element_by_xpath("//div[@role='dialog']/div/div[2]")
        self.following_number = driver.find_element_by_xpath( "//*[@id='react-root']/section/main/div/header/section/ul/li[3]/a/span").text.replace(',','')
        counter = 0
        while counter < int(self.following_number) / 5: # scrolls 5 account each time approximately, if in your browser it differs, change the value with the passed account per scrolling
            self.following_window.send_keys(Keys.PAGE_DOWN)
            counter = counter + 1
            time.sleep(interval)
            if self.xpath_exists("//div[@data-visualcompletion=‘loading-state’]//svg"):
                logger.debug('spinning detected while getting following list')
                driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div[2]").click()
                return 1
        self.following_accounts = driver.find_elements_by_xpath("//a[@class='FPmhX notranslate _0imsa ']") # TODO
        self.following_accounts = [account.get_attribute('title') for account in self.following_accounts]  # the array of the accounts who we follow
        logger.debug('following_accounts: ' + str(self.following_accounts))
        if len(self.following_accounts) == 0:
            logger.debug('following list empty')
            self.following_accounts = self.following_window.find_elements_by_tag_name("a")    
            self.following_accounts = [account.get_attribute('title') for account in  self.following_accounts if account.get_attribute('title') != '']
            logger.debug('following: ' + str(self.following_accounts))
        # driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div[2]").click() #closes the following window
        return 0

    def find_followers(self, driver, buttons, interval) -> int: # this functions finds the accounts who are following us
        logger.debug('begin find_followers function')
        # who follows us
        try: # in case element is stale
            follower_button = [button for button in buttons if 'followers' in button.get_attribute('href')]
        except:
            buttons = driver.find_elements_by_xpath("//a[@class='-nal3 ']")
            follower_button = [button for button in buttons if 'followers' in button.get_attribute('href')]
        follower_button[0].click()
        time.sleep(2)
        self.follower_window = driver.find_element_by_xpath("//div[@role='dialog']/div/div[2]")
        self.follower_number = driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/header/section/ul/li[2]/a/span").text.replace(',','')
        counter = 0
        while counter < int(self.follower_number) / 5: # scrolls 5 account each time approximately, if in your browser it differs, change the value with the passed account per scrolling
            self.follower_window.send_keys(Keys.PAGE_DOWN)
            counter = counter + 1
            time.sleep(interval)
            if self.xpath_exists("//div[@data-visualcompletion=‘loading-state’]//svg"):
                logger.debug('spinning wheel detected while getting followers list')
                driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div[2]").click()
                return 1
        self.follower_accounts = self.follower_window.find_elements_by_xpath("//a[@class='FPmhX notranslate _0imsa ']") # TODO
        self.follower_accounts = [account.get_attribute('title') for account in  self.follower_accounts]  # the array of the accounts who follows us
        logger.debug('followers: ' + str(self.follower_accounts))
        # somehow self.follower_accounts is empty
        if len(self.follower_accounts) == 0: # alternative follower crawl
            logger.debug('followers list empty')
            self.follower_accounts = self.follower_window.find_elements_by_tag_name("a")
            self.follower_accounts = [account.get_attribute('title') for account in  self.follower_accounts if account.get_attribute('title') != '']
            logger.debug('followers: ' + str(self.follower_accounts))
        # test
        if self.xpath_exists("//div[@role='dialog']"):
            logger.debug('window open')
        driver.find_element_by_xpath("//div[@role='dialog']//button").click()  #closes the follower window
        return 0

    def compare_following_and_followers(self, followers, followings): # this function compare the list of followers and followings, and create a blacklist which will include the list of users who we want to unfollow.
        followers = set(self.follower_accounts)
        followings = set(self.following_accounts)
        targetusers = followings - followers
        for acc in targetusers:
            self._blacklist.append(acc)
            logger.debug('added user to block list: ' + str(acc))
 
    def find_target_users(self): #method to find users who we follow but they don't follow us back
        driver = self.driver
        driver.get("https://www.instagram.com/" + self._username + "/")
        time.sleep(5) 
        buttons = driver.find_elements_by_xpath("//a[@class='-nal3 ']")
        
        time.sleep(2)
        
        t = 2

        # who follows us
        follower_status = 1
        while follower_status:
            follower_status = followers_status = self.find_followers(driver, buttons, t)

        time.sleep(2)

        # who do we follow
        following_status = 1
        while following_status:
            following_status = following_status = self.find_followings(driver, buttons, t)
        
        time.sleep(2)

        self.compare_following_and_followers(self.follower_accounts, self.following_accounts)
        time.sleep(2)

    def unfollow_target_users(self) -> int:
        logger.debug('start unfollow target user function')
        driver = self.driver
        if self.xpath_exists("//div[@role='dialog']//a"):  # check if following window is still open
            win_open = 1
        else:
            win_open = 0
        if not win_open:
            try:
                self.following_button[0].click()
            except:
                buttons = driver.find_elements_by_xpath("//a[@class='-nal3 ']")
                self.following_button = [button for button in buttons if 'following' in button.get_attribute('href')] # retry find following button
                # spinning wheel: //div[@data-visualcompletion=‘loading-state’] # TODO maybe
                self.following_button[0].click()
        self.following_window = driver.find_element_by_xpath("//div[@role='dialog']/div/div[2]")
        self.following_number = driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/header/section/ul/li[3]/a/span").text.replace(',', '')
        # unneccessary to redo scrolling if follow count is done first and then following count is next as following window is still open
        if not win_open:
            counter = 0
            while counter < int(self.following_number) / 5:  # scrolls 5 account each time approximately, if in your browser it differs, change the value with the passed account per scrolling
                self.following_window.send_keys(Keys.PAGE_DOWN)
                counter = counter + 1
                time.sleep(1)
                if self.xpath_exists("//div[@data-visualcompletion=‘loading-state’]//svg"):
                    logger.debug('spinning wheel detected while unfollowing')
                    driver.find_element_by_xpath("/html/body/div[5]/div/div/div[1]/div/div[2]").click()
                    return 1
        t = len(self._blacklist) * self.unfollowing_speed + len(self._blacklist) // 50 * 9
        if t > 60:
            m = t // 60
            s = t % 60
            t = f'{m}m {s}s'
        else:
            t = f'{t}s'
        logger.info(f'expected time remaining: {t} left')
        self.unfollow_buttons = driver.find_elements_by_xpath("//button[@class='sqdOP  L3NKy    _8A5w5    ']")
        for n, account in enumerate(self._blacklist):
            try:
                self.unfollow_buttons[self.following_accounts.index(str(account))].click()  # unfollow requested
            except:
                if self.xpath_exists("//button[@class='aOOlW  bIiDR  ']"):
                    driver.find_element_by_xpath("//button[@class='aOOlW  bIiDR  ']").click()
                logger.error('unfollow request raised an error')
                return 1 # probably instagram returned an error, this loop will be handled in main.py
            time.sleep(1)
            try:
                driver.find_element_by_xpath("//button[@class='aOOlW -Cab_   ']").click() # confirm unfollow
                logger.info('successfully unfollowed: ' + str(account))
            except:
                logger.error('unfollow confirm button not found')
                continue
            time.sleep(self.unfollowing_speed)
            if n // 50:
                self.following_number = driver.find_element_by_xpath("//*[@id='react-root']/section/main/div/header/section/ul/li[3]/a/span").text.replace(',', '')
                logger.info('current following num: ' + str(self.following_number) + ', sleep ' + str(self.unfollowing_speed * 10) + 's')
                time.sleep(self.unfollowing_speed * 10) # instagram stops activities if too many are detected, sleep 10 times every 50 unfollows
        self.following_window.find_element_by_xpath("//div[@role='dialog']//button").click()
        return 0 # this will close the loop in main.py
