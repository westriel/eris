////////////////////////////////////////////////////////////
// ERIS Client-Side App
// Created by Cameron Kim from the ERIS team for fall 2021 capstone project
const WebSocket = require('ws')
const electron = require('electron')
const url = require('url')
const path = require('path')

const { app, BrowserWindow, Menu, ipcMain, dialog } = electron
const { checkout, update, commit } = require('./commands')

// SVN repository URL
const URL = 'https://24.210.238.51:8443/svn/ErisTesting/'
// Path to working directory
let PATH //= 'E:/Capstone/testSVN'

// SVN username and password
let USER //= 'Cam'
let PASSWORD //= 'ErisSVN'

let socket;

/////////////////////////////////////////////////////////////////
// WEBSOCKETS
// Create WebSocket connection.
const URI = 'ws://24.210.238.51:6969'

let startSocket = (user, password) => {
  socket = new WebSocket(URI)

  // Connection opened
  socket.addEventListener('open', function (event) {
    //socket.send('Hello Server!')
    console.log('conencted to websocket server!')
    socket.send(USER)
  })

  // Listen for messages
  socket.addEventListener('message', function (event) {
    console.log('message received: ', event.data)
    data = event.data
    jsonData = JSON.parse(data)

    // Verify username
    if (jsonData['connected']) {
      console.log('valid username')
      socket.send(PASSWORD)
    }
    else if (!jsonData['connected']) {
      console.log('invalid username!')
    }
    else if (jsonData['login_success']) {
      console.log('login successful')
    }
    else if (!jsonData['login_success']) {
      console.log('invalid password')
    }
    /////////////////////////////////////////////////////////////////
    // COMMANDS
    switch (jsonData['command']) {
      case 'ping':
        console.log('pinged!')
        socket.send(JSON.stringify({ command: 'ping_response' }))
        mainWindow.webContents.send('command', 'pinged')
        console.log('pong sent!')
        break

      case 'commit':
        console.log('commited')
        socket.send(
          JSON.stringify({ command_success: true, command: 'commit_response' })
        )
        commit(PATH, USER, PASSWORD)
        mainWindow.webContents.send('command', 'SVN commit')
        break

      case 'update':
        console.log('updated')
        socket.send(
          JSON.stringify({ command_success: true, command: 'update_response' })
        )
        update(PATH, USER, PASSWORD)
        mainWindow.webContents.send('command', 'SVN update')
        break

      case 'checkout':
        console.log('checked out')
        socket.send(
          JSON.stringify({
            command_success: true,
            command: 'checkout_response',
          })
        )
        checkout(URL, PATH, USER, PASSWORD)
        mainWindow.webContents.send('command', 'SVN checkout')
        break
    }
  })
}

//////////////////////////////////////////////////////////////////////////
// ELECTRON
// Declare windows
let mainWindow
let loginWindow

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
      pathname: path.join(__dirname, 'windows', 'mainWindow.html'),
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

// Handle create login window
let createLoginWindow = () => {
  // Create Window
  loginWindow = new BrowserWindow({
    width: 300,
    height: 500,
    title: 'Login',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  })

  // Load HTML file into window
  loginWindow.loadURL(
    url.format({
      pathname: path.join(__dirname, 'windows', 'login.html'),
      protocol: 'file:',
      slashes: true,
    })
  )

  // Garbage collection ahndle
  loginWindow.on('close', () => {
    loginWindow = null
  })
}

ipcMain.on('login', (event, data) => {
  let { username, password } = data
  console.log(username)
  USER = username
  PASSWORD = password
  startSocket(USER, PASSWORD)
  loginWindow.close()
})
ipcMain.on('settings', (event, data) => {
  console.log(data)
  socket.send(JSON.stringify({settings: data}))
})

let saveDir = async () => {
  const fPath = await dialog.showOpenDialog({
    buttonLabel: 'Select Directory',
    properties: ['openDirectory'],
  })
  const { filePaths } = fPath
  PATH = filePaths[0]
}

// Main menu template
const mainMenuTemplate = [
  {
    label: 'File',
    submenu: [
      {
        label: 'Login',
        click() {
          createLoginWindow()
        },
      },
      {
        label: 'Select working directory',
        click() {
          saveDir()
        },
      },
      {
        label: 'Quit',
        accelerator: process.platform == 'darwin' ? 'Command+Q' : 'Ctrl+Q',
      },
    ],
  },
]

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
