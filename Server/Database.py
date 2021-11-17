import pymysql

class Database:

    def __init__(self):

        print("Creating Database Connection")
        
        self.HOST = "192.168.1.231"
        self.PORT = 3306

        file = open("TOKENS.txt")
        data = eval(file.read())

        self.USERNAME = data["username"]
        self.PASSWORD = data["password"]


        self.conn = pymysql.Connection(host = self.HOST, port = self.PORT, user = self.USERNAME, passwd = self.PASSWORD, db="eris")
           


    def CheckUsernameAndPassword(self,username,password):
        try:
            cursor = self.conn.cursor()
            QUERY = "SELECT * FROM user WHERE user_name = \"{username}\" and password_hash = \"{password}\";".format(username=username,password=password)
            data = cursor.execute(QUERY)
            for row in cursor:
                print(row)
            print("LEN",data)
            return bool(data)
        except pymysql.Error as e:
            print("CheckUsernameAndPassword Error %d: %s" % (e.args[0], e.args[1]))

    def GetUsernameFromDiscordID(self,dis_id):
        try:
            cursor = self.conn.cursor()
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

    def UpdateUserRepoSettings(self,username,repo,settings):
        try:
            cursor = self.conn.cursor()
            QUERY = "UPDATE notification_settings SET commit_update = {commit}, merge_update = {merge} WHERE user_name = \"{username}\" and address = \"{repo}\"".format(commit = settings["commit"], merge = settings["merge"], username=username, repo = repo)
            status = cursor.execute(QUERY)
            self.conn.commit()
            return status

        except pymysql.Error as e:
            print("UpdateUserRepoSettings Error %d: %s" % (e.args[0], e.args[1]))

    def CheckIfRepoExists(self,repo):
        try:
            cursor = self.conn.cursor()
            QUERY = "SELECT address FROM svn_repo WHERE address = \"{address}\"".format(address=repo)
            status = cursor.execute(QUERY)
            return bool(len(cursor.fetchall()))
        except pymysql.Error as e:
            print("CheckIfRepoExists Error %d: %s" % (e.args[0], e.args[1]))

    def CheckIfUserHasRepoAccess(self,username,repo):
        print(username,repo)
        try:
            cursor = self.conn.cursor()
            QUERY = "SELECT * FROM repo_access WHERE user_name = \"{username}\" AND address = \"{repo}\"".format(username=username,repo=repo)
            status = cursor.execute(QUERY)
            return bool(len(cursor.fetchall()))
        except pymysql.Error as e:
            print("CheckIfUserHasRepoAccess Error %d: %s" % (e.args[0], e.args[1]))

    def SetUserCurrentRepo(self,username,repo):
        try:
            cursor = self.conn.cursor()
            QUERY = "UPDATE user SET current_repo = \"{repo}\" WHERE user_name = \"{username}\"".format(repo=repo,username=username)
            status = cursor.execute(QUERY)
            self.conn.commit()
            return bool(status)
        except pymysql.Error as e:
            print("SetUserCurrentRepo Error %d: %s" % (e.args[0], e.args[1]))

    def GetUserCurrentRepo(self,username):
        try:
            cursor = self.conn.cursor()
            QUERY = "SELECT current_repo FROM user WHERE user_name = \"{username}\"".format(username=username)
            status = cursor.execute(QUERY)
            return cursor.fetchall()[0][0]
        except pymysql.Error as e:
            print("GetUserCurrentRepo Error %d: %s" % (e.args[0], e.args[1]))
            
