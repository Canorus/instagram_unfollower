from InstaUnfollower import InstagramUnfollower
from time import sleep
from logg import *
import os

def main():

    username = "your_username"
    password = "your_password"

    unfollower = InstagramUnfollower(username,password, 10) #just increase the number to unfollow slower, and decrease to unfollow faster. ( Making too fast may possible shows you as a bot to Instagram )
    unfollower.login() #logins your account
    unfollower.find_username() #finds the username of your account
    unfollower.find_target_users() #finds the target users who we want to unfollow
    uf_status = 1
    fail_count = 0
    while uf_status:
        uf_status = unfollower.unfollow_target_users()  #unfollows the target users who we determined before
        sleep(60 * unfollower.unfollowing_speed)
        if fail_count // 10:
            logger.error('error count reached 10, retrying in 2 hours')
            sleep(7200)
        fail_count += 1
    os.system('sh tail.sh') # clear log file

if __name__ == "__main__":
    main()

