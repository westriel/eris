# ERIS
Eris is the integrated SVN and discord version control

# Client Install Instructions
 - Requirements: Node/npm, Subversion CLI
 - NPM Dependencies: electron, cross-fetch, node-svn-ultimate, ws
 1. `git clone https://github.com/westriel/eris.git`
 2. `cd eris/Client`
 3. `npm i electron cross-fetch node-svn-ultimate ws`
 4. Ensure that the `eris/Client/uri.json` points to the correct URI for the server
 5. `npm start`

# Server Install Instructions
 - Requirements: Python
 - Python Dependencies: Discord.py, websockets
 1. `git clone https://github.com/westriel/eris.git`
 3. `cd eris/Server`
 4. `pip install Discord.py websockets`
 5. Setup bot token by editing `TOKEN.txt` and pasting the bot token into the file

# Database Server Instructions
 - 

# Known Issues
 - If `repoSettings.json` does not exist as a properly formatted `.json` file an error occurs.
 - Working Directories cannot have spaces in them
 - Our SVN Library does not provide responses from svn commands (i.e. svn status)
 - SSL certificates are unable to be accepted or rejected and thus are rejected by default
