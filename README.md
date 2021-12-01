# ERIS
Eris is the integrated SVN and Discord version control

# Client Install Instructions
 - Requirements: Node/npm, Subversion CLI
 - NPM Dependencies: electron, cross-fetch, node-svn-ultimate, ws
 1. `git clone https://github.com/westriel/eris.git`
 2. `cd eris/Client`
 3. `npm i electron cross-fetch node-svn-ultimate ws`
 4. Ensure that the `eris/Client/uri.json` points to the correct websocket URI for the server
 5. `npm start` to run the Client

# Bot Install Instructions
 - Requirements: Python <= 3.8
 - Python Dependencies: Discord.py, websockets
 1. `git clone https://github.com/westriel/eris.git`
 2. `cd eris/Chat-Integration`
 3. `pip install discord.py websockets`
 4. Setup bot token by editing `TOKEN.txt` and pasting the bot token into the file
    - A Discord account is required. You can make one [here](https://discord.com/)
    - To setup a Discord bot, follow the instructions [here](https://web.cs.kent.edu/~jbehler1/python_programs/lesson18.py)
    - If you do not wish to go through the hassle of creating your own bot application, you can join our testing server REDACTED
 5. Run `Bot.py` and the the bot should now be online

# Server Install Instructions
 - Requirements: Python <= 3.8
 - Python Dependencies: websockets, pymysql
 1. `git clone https://github.com/westriel/eris.git`
 2. `cd eris/Server`
 3. `pip install websockets pymysql`
 4. Setup environment variables by editing `SETTINGS.txt`
    - You will have to create a public port for the server by port forwarding on your router/system
    - If you do not wish to do this, an already running server is currently being ran on REDACTED
 5. Run the Server.py file

# Database Install Instructions
 - Eris requires a MySQL Database to function
 - We used an Apache XAMPP Database. Instructions to set this up can be found [here](https://www.geeksforgeeks.org/how-to-install-xampp-on-windows/)
 - You may use the provided `SETUP.sql` file to create the database.
 - If you do not wish to create your own Database, our Database can be accessed at REDACTED

# Known Issues
 - If `repoSettings.json` does not exist as a properly formatted `.json` file an error occurs.
 - Working Directories cannot have spaces in them
 - Our SVN Library does not provide responses from svn commands (i.e. svn status)
 - SSL certificates are unable to be accepted or rejected and thus are rejected by default
