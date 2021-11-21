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

/////////////////////////////////////////////////////////////////
// WEBSOCKETS
// Create WebSocket connection.
const URI = 'ws://24.210.238.51:6969'

let startSocket = user => {
  socket = new WebSocket(URI)

  // Connection opened
  socket.addEventListener('open', function (event) {
    //socket.send('Hello Server!')
    console.log('conencted to websocket server!')
    socket.send(user.id)
  })

  // Listen for messages
  socket.addEventListener('message', function (event) {
    console.log('message received: ', event.data)
    data = event.data
    jsonData = JSON.parse(data)

    // Verify username
    // if (jsonData['connected']) {
    //   console.log('valid username')
    //   socket.send(password)
    // } else if (jsonData['connected'] == false) {
    //   console.log('invalid username!')
    // } else
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
    } else if (jsonData['login_success'] == false) {
      console.log('invalid password')
      socket.close()
      console.log('socket closed')
    }

    /////////////////////////////////////////////////////////////////
    // COMMANDS
    let repoInfo
    switch (jsonData['command']) {
      case 'ping':
        console.log('pinged!')
        socket.send(JSON.stringify({ command: 'ping_response' }))
        mainWindow.webContents.send('command', 'pinged')
        console.log('pong sent!')
        break

      case 'commit':
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

      case 'update':
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

      case 'checkout':
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

      case 'add':
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

      case 'remove':
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

  const mainMenu = Menu.buildFromTemplate(mainMenuTemplate)
  Menu.setApplicationMenu(mainMenu)
})

//////////////////////////////////////////////////////
// INTERPROCESS COMMUNICATION
ipcMain.on('login', (event, data) => {
  ;(async () => {
    await login(startSocket)
  })()
  //loginWindow.close()
})

ipcMain.on('settings', (event, data) => {
  //console.log(data)
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
  //console.log(newSettings)
  mainWindow.webContents.send('settings_saved')
  socket.send(
    JSON.stringify({ command: 'update_settings', settings: data, repo: URL })
  )
  console.log('sent')
  refresh()
})

ipcMain.on('logout', (event, data) => {
  socket.close()
  console.log('socket closed')
  // Load html into window
  mainWindow.loadURL(
    url.format({
      pathname: path.join(__dirname, 'windows', 'login.html'),
      protocol: 'file:',
      slashes: true,
    })
  )
})

ipcMain.on('changeDir', (event, data) => {
  saveDir(event)
})

ipcMain.on('change path', (event, data) => {
  changeRepo(data)
  console.log(`path changed to ${PATH}`)
  console.log(`repo changed to ${URL}`)
  console.log(`username changed to ${USERNAME}`)
  console.log(`password changed to ${PASSWORD}`)
})

let saveDir = async e => {
  const fPath = await dialog.showOpenDialog({
    buttonLabel: 'Select Directory',
    properties: ['openDirectory'],
  })
  const { filePaths } = fPath
  e.reply('dirSelected', filePaths[0])
}

// Main menu template
const mainMenuTemplate = []

// Add dev tools item if not in production
if (process.env.NODE_ENV !== 'production') {
  mainMenuTemplate.push({
    label: 'Developer Tools',
    submenu: [
      {
        label: 'Toggle DevTools',
        accelerator: process.platform == 'darwin' ? 'Command+I' : 'Ctrl+I',
        click(item, focusedWindow) {
          focusedWindow.toggleDevTools()
        },
      },
      {
        role: 'reload',
      },
    ],
  })
}

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

let readSettings = () => {
  if (fs.existsSync('./repoSettings.json')) {
    let repos = fs.readFileSync('./repoSettings.json')
    repos = JSON.parse(repos)
    return repos
  } else {
    // Creating a blank json if it doesnt exist
    fs.writeFileSync('./repoSettings.json', {})
    return {}
  }
}

// {"command": "checkout", "id": 181459954144772096, "target": "Cam", "repo": "https://24.210.238.51:8443/svn/ErisTesting/"}
let checkRepoInfo = repo => {
  let repos = readSettings()
  let errorFlag = false
  let errors = []
  if (repos[repo].username == '') {
    console.log('please fill in username')
    errorFlag = true
    errors.push('username')
  }
  if (repos[repo].password == '') {
    console.log('please fill in password')
    errorFlag = true
    errors.push('password')
  }
  if (repos[repo].path == '') {
    console.log('please fill in working directory')
    errorFlag = true
    errors.push('path')
  }
  return { missingInfo: errorFlag, fields: errors }

  // repoError = new BrowserWindow({
  //   webPreferences: {
  //     nodeIntegration: true,
  //     contextIsolation: false,
  //   },
  // })

  // // Load html into window
  // repoError.loadURL(
  //   url.format({
  //     pathname: path.join(__dirname, 'windows', 'repoLogin.html'),
  //     protocol: 'file:',
  //     slashes: true,
  //   })
  // )

  // // Quit app when closed
  // repoError.on('closed', () => {
  //   app.quit()
  // })
}

let refresh = () => {
  mainWindow.webContents.send('refresh')
}
