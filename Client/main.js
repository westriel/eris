////////////////////////////////////////////////////////////
// ERIS Client-Side App
// Created by Cameron Kim from the ERIS team for fall 2021 capstone project
const WebSocket = require('ws')
const electron = require('electron')
const url = require('url')
const path = require('path')
const fs = require('fs')

const { app, BrowserWindow, Menu, ipcMain, dialog } = electron
const { checkout, update, commit, add, del } = require('./commands')
const { login } = require('./Oauth')

// SVN repository URL
let URL // = 'https://24.210.238.51:8443/svn/ErisTesting/'
// Path to working directory
let PATH
let PASSWORD
let USERNAME

let socket
let discord

/////////////////////////////////////////////////////////////////
// WEBSOCKETS
// Create WebSocket connection.
let getURI = fs.readFileSync('./uri.json')
getURI = JSON.parse(getURI)
const URI = getURI.URI

let startSocket = user => {
  socket = new WebSocket(URI)

  // Connection opened
  socket.addEventListener('open', function (event) {
    //socket.send('Hello Server!')
    console.log('conencted to websocket server!')
    discord = user
    socket.send(user.id)
  })

  socket.on('close', () => {
    mainWindow.loadURL(
      url.format({
        pathname: path.join(__dirname, 'windows', 'login.html'),
        protocol: 'file:',
        slashes: true,
      })
    )
  })

  // Listen for messages
  socket.addEventListener('message', function (event) {
    console.log('message received: ', event.data)
    data = event.data
    jsonData = JSON.parse(data)

    if (jsonData['login_success']) {
      // Makes sure that the window is loaded before the render is sent the username
      ;(async () => {
        await mainWindow.loadURL(
          url.format({
            pathname: path.join(__dirname, 'windows', 'mainWindow.html'),
            protocol: 'file:',
            slashes: true,
          })
        )
        await console.log('login successful')
        await mainWindow.webContents.send('login:user', user.username)
      })()
      // if lagin success is flase, show a failed login popup
    } else if (jsonData['login_success'] == false) {
      dialog.showMessageBox(mainWindow, {
        message: `Invalid Login`,
      })
      console.log('invalid password')
      socket.close()
      console.log('socket closed')
    }

    /////////////////////////////////////////////////////////////////
    // COMMANDS
    let repoInfo
    switch (jsonData['command']) {
      // ping
      case 'ping':
        console.log('pinged!')
        socket.send(JSON.stringify({ command: 'ping_response' }))
        mainWindow.webContents.send('command', 'pinged')
        console.log('pong sent!')
        break

      // Commit
      case 'commit':
        // Check for missing info
        changeRepo(jsonData['repo'])
        repoInfo = checkRepoInfo(jsonData['repo'])
        if (repoInfo.missingInfo) {
          console.log(checkRepoInfo(jsonData['repo']).fields)
          socket.send(
            JSON.stringify({
              command_success: false,
              command: 'commit_response',
              reason: repoInfo.fields,
            })
          )
          break
        } else {
          // complete command and send status to the server
          console.log('commited')
          socket.send(
            JSON.stringify({
              command_success: true,
              command: 'commit_response',
            })
          )
          commit(PATH, USERNAME, PASSWORD, jsonData['message'])
          mainWindow.webContents.send('command', 'SVN commit')
          break
        }

      // Update
      case 'update':
        // Check for missing info
        changeRepo(jsonData['repo'])
        repoInfo = checkRepoInfo(jsonData['repo'])
        if (repoInfo.missingInfo) {
          console.log(checkRepoInfo(jsonData['repo']).fields)
          socket.send(
            JSON.stringify({
              command_success: false,
              command: 'update_response',
              reason: repoInfo.fields,
            })
          )
          break
        } else {
          // complete command and send status to the server
          console.log('updated')
          socket.send(
            JSON.stringify({
              command_success: true,
              command: 'update_response',
            })
          )
          update(PATH, USERNAME, PASSWORD)
          mainWindow.webContents.send('command', 'SVN update')
          break
        }

      // Checkout
      case 'checkout':
        // Check for missing info
        changeRepo(jsonData['repo'])
        repoInfo = checkRepoInfo(jsonData['repo'])
        if (repoInfo.missingInfo) {
          console.log(checkRepoInfo(jsonData['repo']).fields)
          socket.send(
            JSON.stringify({
              command_success: false,
              command: 'checkout_response',
              reason: repoInfo.fields,
            })
          )
          break
        } else {
          // complete command and send status to the server
          console.log('checked out')
          socket.send(
            JSON.stringify({
              command_success: true,
              command: 'checkout_response',
            })
          )
          checkout(URL, PATH, USERNAME, PASSWORD)
          mainWindow.webContents.send('command', 'SVN checkout')
          break
        }

      // Add
      case 'add':
        // Check for missing info
        changeRepo(jsonData['repo'])
        repoInfo = checkRepoInfo(jsonData['repo'])
        if (repoInfo.missingInfo) {
          console.log(checkRepoInfo(jsonData['repo']).fields)
          socket.send(
            JSON.stringify({
              command_success: false,
              command: 'add_response',
              reason: repoInfo.fields,
            })
          )
          break
        } else {
          // complete command and send status to the server
          console.log('files added')
          socket.send(
            JSON.stringify({
              command_success: true,
              command: 'add_response',
            })
          )
          add(jsonData['files'], PATH, USERNAME, PASSWORD)
          mainWindow.webContents.send('command', 'SVN add')
          break
        }

      // Remove
      case 'remove':
        // Check for missing info
        changeRepo(jsonData['repo'])
        repoInfo = checkRepoInfo(jsonData['repo'])
        if (repoInfo.missingInfo) {
          console.log(checkRepoInfo(jsonData['repo']).fields)
          socket.send(
            JSON.stringify({
              command_success: false,
              command: 'remove_response',
              reason: repoInfo.fields,
            })
          )
          break
        } else {
          // complete command and send status to the server
          console.log('files added')
          socket.send(
            JSON.stringify({
              command_success: true,
              command: 'remove_response',
            })
          )
          del(jsonData['files'], PATH, USERNAME, PASSWORD)
          mainWindow.webContents.send('command', 'SVN add')
          break
        }

      // Repo list is sent to client
      case 'send_repo_list':
        let { repos } = jsonData
        let currentSettings = readSettings()
        // Fill in the settings for each repo
        for (repo in repos) {
          // if they exist, fill in info
          if (repo in currentSettings) {
            currentSettings[repo].n_commit = repos[repo].commit
            currentSettings[repo].n_update = repos[repo].update
            currentSettings[repo].autoUpdate = repos[repo].autoUpdate
            // if they are new fill in info and create empty fields
          } else {
            currentSettings[repo] = {
              name: '',
              path: '',
              username: '',
              password: '',
              autoUpdate: repos[repo].autoUpdate,
              n_commit: repos[repo].commit,
              n_update: repos[repo].update,
            }
          }
        }
        fs.writeFileSync('./repoSettings.json', JSON.stringify(currentSettings))
        mainWindow.webContents.send('refresh')
        break

      case 'auto_update':
        // Check for missing info
        changeRepo(jsonData['repo'])
        repoInfo = checkRepoInfo(jsonData['repo'])
        if (repoInfo.missingInfo) {
          console.log(checkRepoInfo(jsonData['repo']).fields)
          socket.send(
            JSON.stringify({
              command_success: false,
              command: 'auto_update_response',
              reason: repoInfo.fields,
            })
          )
          break
        } else {
          // complete command and send status to the server
          console.log('auto updated')
          socket.send(
            JSON.stringify({
              command_success: true,
              command: 'auto_update_response',
              repo: jsonData['repo'],
            })
          )
          update(PATH, USERNAME, PASSWORD)
          mainWindow.webContents.send('command', 'ERIS auto update')
          break
        }
    }
  })
}

//////////////////////////////////////////////////////////////////////////
// ELECTRON
// Declare windows
let mainWindow

// Listen for app to be ready
app.on('ready', () => {
  // Create window
  mainWindow = new BrowserWindow({
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  })

  // Load html into window
  mainWindow.loadURL(
    url.format({
      pathname: path.join(__dirname, 'windows', 'login.html'),
      protocol: 'file:',
      slashes: true,
    })
  )

  // Quit app when closed
  mainWindow.on('closed', () => {
    app.quit()
  })

  Menu.setApplicationMenu(null)
})

//////////////////////////////////////////////////////
// INTERPROCESS COMMUNICATION
ipcMain.on('login', (event, data) => {
  ;(async () => {
    await login(startSocket)
  })()
  //loginWindow.close()
})

// Recieve settings from frontend
ipcMain.on('settings', (event, data) => {
  // store settings in json
  let currentSettings = readSettings()
  let newSettings = currentSettings
  newSettings[URL].autoUpdate = data.autoUpdate
  newSettings[URL].n_commit = data.commit
  newSettings[URL].n_update = data.update
  newSettings[URL].username = data.username
  newSettings[URL].password = data.password
  newSettings[URL].name = data.repoName
  newSettings[URL].path = data.path
  fs.writeFileSync('./repoSettings.json', JSON.stringify(newSettings))

  // update the frontend
  mainWindow.webContents.send('settings_saved')
  // send updated se  ttings to server
  socket.send(
    JSON.stringify({ command: 'update_settings', settings: data, repo: URL })
  )
  console.log('sent')
  refresh()
})

// Logout
ipcMain.on('logout', (event, data) => {
  // close socket connection
  socket.close()
  // Load html into window
  mainWindow.loadURL(
    url.format({
      pathname: path.join(__dirname, 'windows', 'login.html'),
      protocol: 'file:',
      slashes: true,
    })
  )
})

// sets working directory for repo
ipcMain.on('changeDir', (event, data) => {
  saveDir(event)
})

// switches current repo on click
ipcMain.on('change path', (event, data) => {
  changeRepo(data)
})

// handles selecting directory
let saveDir = async e => {
  const fPath = await dialog.showOpenDialog({
    buttonLabel: 'Select Directory',
    properties: ['openDirectory'],
  })
  const { filePaths } = fPath
  // send selected path to the frontend
  e.reply('dirSelected', filePaths[0])
}

// changes the working dir, username, and password for repo
let changeRepo = repo => {
  let repos = readSettings()
  if (repos[repo].path == '') {
    PATH = ''
  } else {
    PATH = repos[repo].path
  }

  PASSWORD = repos[repo].password
  USERNAME = repos[repo].username

  URL = repo
}

// reads the repoSettings.json
let readSettings = () => {
  if (fs.existsSync('./repoSettings.json')) {
    let repos = fs.readFileSync('./repoSettings.json')
    repos = JSON.parse(repos)
    // returns repo's settings as JS object
    return repos
  } else {
    // Creating a blank json if it doesnt exist
    // !!!-NOT WORKING-!!!
    fs.writeFileSync('./repoSettings.json', {}, err => {
      console.log('created file')
    })
    return {}
  }
}

// checks of the repo has a working dir, username, and password
// returns a JS object with a bool representing missing info and a string with what info is missing
let checkRepoInfo = repo => {
  let repos = readSettings()
  let errorFlag = false
  let errors = []
  // checks if username is set
  if (repos[repo].username == '' || repos[repo].username == null) {
    console.log('please fill in username')
    errorFlag = true
    // pushes username to ouput array
    errors.push('username')
  }
  // checks if password is set
  if (repos[repo].password == '' || repos[repo].password == null) {
    console.log('please fill in password')
    errorFlag = true
    // pushes password to ouput array
    errors.push('password')
  }
  // checks if working dir is set
  if (repos[repo].path == '' || repos[repo].path == null) {
    console.log('please fill in working directory')
    errorFlag = true
    // pushes path to ouput array
    errors.push('path')
  }
  // if theres anything missing, send popup that displays whats missing
  if (errorFlag) {
    let errorString = ''
    dialog.showMessageBox(mainWindow, {
      message: `Missing repository settings: ${errors}`,
    })
  }
  let returnString = `Missing repository settings: ${errors}`
  // return missing info bool and return string
  return { missingInfo: errorFlag, fields: returnString }
}

// sends refresh command to frontend
let refresh = () => {
  mainWindow.webContents.send('refresh')
  socket.send(JSON.stringify({ command: 'send_repo_list', id: discord.id }))
}
