import pymysql

#############################################################################
# Class that acts as interface between the Server Prorgam and the Database.
# Every function reopens the connection to prevent the Database from closing
#     the connection over time
#############################################################################

class Database:

    def __init__(self): # Constructor

        print("Creating Database Connection")
        
        self.HOST = "192.168.1.231"
        self.PORT = 3306

        file = open("TOKENS.txt")
        data = eval(file.read())

        # Database login info for the bot
        self.USERNAME = data["username"]
        self.PASSWORD = data["password"]
        
        file.close()          

    # Check if user exists
    def CheckUsername(self,username):
        try:
            conn = pymysql.Connection(host = self.HOST, port = self.PORT, user = self.USERNAME, passwd = self.PASSWORD, db="eris")
            cursor = conn.cursor()
            QUERY = "SELECT * FROM user WHERE user_name = \"{username}\"".format(username=username)
            data = cursor.execute(QUERY)
            return bool(data)
        except pymysql.Error as e:
            print("CheckUsername Error %d: %s" % (e.args[0], e.args[1]))

    # Create user in database
    def CreateUser(self,username):
        try:
            conn = pymysql.Connection(host = self.HOST, port = self.PORT, user = self.USERNAME, passwd = self.PASSWORD, db="eris")
            cursor = conn.cursor()
            QUERY = "INSERT INTO user (user_name, is_admin, current_repo) VALUES (\"{username}\", 0, null)".format(username=username)
            data = cursor.execute(QUERY)
            conn.commit()
            return bool(data)
        except pymysql.Error as e:
            print("CreateUser Error %d: %s" % (e.args[0], e.args[1]))

    # Get a user's username from their Discord ID
    # NOT IN USE - DEPRECIATED
    def GetUsernameFromDiscordID(self,dis_id):
        try:
            conn = pymysql.Connection(host = self.HOST, port = self.PORT, user = self.USERNAME, passwd = self.PASSWORD, db="eris")
            cursor = conn.cursor()
            QUERY = "SELECT user_name FROM user WHERE discord_user_id = \"{dis_id}\";".format(dis_id = dis_id)
            cursor.execute(QUERY)
            data = cursor.fetchall()
            #print(data)
            if(len(data) != 0):
                return data[0][0]
            else:
                return None
        except pymysql.Error as e:
            print("GetUsernameFromDiscordID Error %d: %s" % (e.args[0], e.args[1]))

    # Update a user's notification settings
    def UpdateUserRepoSettings(self,username,repo,settings):
        try:
            conn = pymysql.Connection(host = self.HOST, port = self.PORT, user = self.USERNAME, passwd = self.PASSWORD, db="eris")
            cursor = conn.cursor()
            QUERY = "UPDATE notification_settings SET commit_update = {commit}, update_update = {update}, auto_update = {auto} WHERE user_name = \"{username}\" and address = \"{repo}\"".format(commit = settings["commit"], update = settings["update"],auto = settings["autoUpdate"], username=username, repo = repo)
            status = cursor.execute(QUERY)
            conn.commit()
            return status

        except pymysql.Error as e:
            print("UpdateUserRepoSettings Error %d: %s" % (e.args[0], e.args[1]))

    # Returns true if the repo exists
    def CheckIfRepoExists(self,repo):
        try:
            conn = pymysql.Connection(host = self.HOST, port = self.PORT, user = self.USERNAME, passwd = self.PASSWORD, db="eris")
            cursor = conn.cursor()
            QUERY = "SELECT address FROM svn_repo WHERE address = \"{address}\"".format(address=repo)
            status = cursor.execute(QUERY)
            return bool(len(cursor.fetchall()))
        except pymysql.Error as e:
            print("CheckIfRepoExists Error %d: %s" % (e.args[0], e.args[1]))

    # Returns true if the user can access the specified repo
    def CheckIfUserHasRepoAccess(self,username,repo):
        print(username,repo)
        try:
            conn = pymysql.Connection(host = self.HOST, port = self.PORT, user = self.USERNAME, passwd = self.PASSWORD, db="eris")
            cursor = conn.cursor()
            QUERY = "SELECT * FROM repo_access WHERE user_name = \"{username}\" AND address = \"{repo}\"".format(username=username,repo=repo)
            status = cursor.execute(QUERY)
            return bool(len(cursor.fetchall()))
        except pymysql.Error as e:
            print("CheckIfUserHasRepoAccess Error %d: %s" % (e.args[0], e.args[1]))

    # Sets the user's current repo to the specified repo
    def SetUserCurrentRepo(self,username,repo):
        try:
            conn = pymysql.Connection(host = self.HOST, port = self.PORT, user = self.USERNAME, passwd = self.PASSWORD, db="eris")
            cursor = conn.cursor()
            QUERY = "UPDATE user SET current_repo = \"{repo}\" WHERE user_name = \"{username}\"".format(repo=repo,username=username)
            status = cursor.execute(QUERY)
            conn.commit()
            return bool(status)
        except pymysql.Error as e:
            print("SetUserCurrentRepo Error %d: %s" % (e.args[0], e.args[1]))

    # Returns the user's current set repo
    def GetUserCurrentRepo(self,username):
        try:
            conn = pymysql.Connection(host = self.HOST, port = self.PORT, user = self.USERNAME, passwd = self.PASSWORD, db="eris")
            cursor = conn.cursor()
            QUERY = "SELECT current_repo FROM user WHERE user_name = \"{username}\"".format(username=username)
            status = cursor.execute(QUERY)
            return cursor.fetchall()[0][0]
        except pymysql.Error as e:
            print("GetUserCurrentRepo Error %d: %s" % (e.args[0], e.args[1]))

    # Checks if the user is an admin
    def IsUserAdmin(self,username):
        try:
            conn = pymysql.Connection(host = self.HOST, port = self.PORT, user = self.USERNAME, passwd = self.PASSWORD, db="eris")
            cursor = conn.cursor()
            QUERY = "SELECT is_admin FROM user WHERE user_name = \"{username}\"".format(username=username)
            status = cursor.execute(QUERY)
            return bool(cursor.fetchall()[0][0])
        except pymysql.Error as e:
            print("IsUserAdmin Error %d: %s" % (e.args[0], e.args[1]))

    # Adds a new repo to the database
    def AddNewRepo(self,url):
        try:
            conn = pymysql.Connection(host = self.HOST, port = self.PORT, user = self.USERNAME, passwd = self.PASSWORD, db="eris")
            cursor = conn.cursor()
            QUERY = "INSERT INTO svn_repo (address) VALUES (\"{url}\")".format(url=url)
            status = cursor.execute(QUERY)
            conn.commit()
            return bool(status)
        except pymysql.Error as e:
            print("AddNewRepo Error %d: %s" % (e.args[0], e.args[1]))

    # Checks if user can acces a repo. Duplicate of CheckIfUserHasRepoAccess
    def DoesUserHaveRepoAccess(self,username,repo):
        try:
            conn = pymysql.Connection(host = self.HOST, port = self.PORT, user = self.USERNAME, passwd = self.PASSWORD, db="eris")
            cursor = conn.cursor()
            QUERY = "SELECT * FROM repo_access WHERE address = \"{repo}\" and user_name = \"{username}\"".format(repo=repo,username=username)
            status = cursor.execute(QUERY)
            return bool(status)
        except pymysql.Error as e:
            print("DoesUserHaveRepoAccess Error %d: %s" % (e.args[0], e.args[1]))

    # Gives the user access to the repo
    def GiveUserRepoAccess(self,username,repo):
        try:
            conn = pymysql.Connection(host = self.HOST, port = self.PORT, user = self.USERNAME, passwd = self.PASSWORD, db="eris")
            cursor = conn.cursor()
            QUERY = "INSERT INTO repo_access (address,user_name) VALUES (\"{repo}\",\"{username}\")".format(repo=repo,username=username)
            status = cursor.execute(QUERY)
            conn.commit()
            return bool(status)
        except pymysql.Error as e:
            print("GiveUserRepoAccess Error %d: %s" % (e.args[0], e.args[1]))

    # Returns the list of all repos a user can access
    def GetUserRepoList(self,user):
        try:
            conn = pymysql.Connection(host = self.HOST, port = self.PORT, user = self.USERNAME, passwd = self.PASSWORD, db="eris")
            cursor = conn.cursor()
            QUERY = "SELECT * FROM notification_settings WHERE user_name = \"{username}\"".format(username=user)
            status = cursor.execute(QUERY)
            data = {}
            for line in cursor.fetchall():
                data[line[1]] = {"commit":line[2],"update":line[3],"autoUpdate":line[4]}
            return data
        except pymysql.Error as e:
            print("GetUserRepoList Error %d: %s" % (e.args[0], e.args[1]))

    # Returns a list of users that can access a repo
    def GetAllUsersWithAccessToRepo(self,repo,username_exclude):
        try:
            conn = pymysql.Connection(host = self.HOST, port = self.PORT, user = self.USERNAME, passwd = self.PASSWORD, db="eris")
            cursor = conn.cursor()
            QUERY = "SELECT user_name FROM repo_access WHERE address = \"{repo}\" and user_name <> \"{exclude}\"".format(repo=repo,exclude=username_exclude)
            status = cursor.execute(QUERY)
            users = []
            for line in cursor.fetchall():
                users.append(line[0])
            return users
        except pymysql.Error as e:
            print("GetAllUsersWithAccessToRepo Error %d: %s" % (e.args[0], e.args[1]))

    # Returns the value of the specific setting of the user
    def GetSettingValueFromUserAndRepo(self,username,setting,repo):
        try:
            conn = pymysql.Connection(host = self.HOST, port = self.PORT, user = self.USERNAME, passwd = self.PASSWORD, db="eris")
            cursor = conn.cursor()
            QUERY = "SELECT {setting} FROM notification_settings WHERE user_name = \"{username}\" AND address = \"{repo}\"".format(repo=repo,username=username,setting=setting)
            stauts = cursor.execute(QUERY)
            return cursor.fetchall()[0][0]
        except pymysql.Error as e:
            print("GetSettingValueFromUserAndRepo Error %d: %s" % (e.args[0], e.args[1]))
            
            
