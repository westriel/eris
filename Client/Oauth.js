// text
const electron = require('electron')
const url = require('url')
const path = require('path')
const e_fetch = require('cross-fetch')

const { BrowserWindow } = electron
const { fetch } = e_fetch

const CLIENT_ID = '888218725810049055'
const CLIENT_SECRET = 'Qm_0_CJrzddppz7TiOOn5Vy0iLNXmY0w'
let login = socketCallback => {
  login = new BrowserWindow({
    webPreferences: {
      nodeIntegration: false,
      webSecurity: false,
    },
  })

  login.loadURL(
    'https://discord.com/api/oauth2/authorize?client_id=888218725810049055&response_type=code&scope=identify'
  )

  // when callback from discord is received
  login.webContents.on('will-navigate', function (event, newUrl) {
    // wait for loading spinner to load
    ;(async () => {
      login.loadURL(
        url.format({
          pathname: path.join(__dirname, 'windows', 'loading.html'),
          protocol: 'file:',
          slashes: true,
        })
      )
      console.log(newUrl)
      if (!newUrl) {
        console.log('error')
      }
      // getting code from url
      const code = newUrl.split('=')[1]
      // creating search paramaters
      const params = new URLSearchParams()
      params.append('client_id', CLIENT_ID)
      params.append('client_secret', CLIENT_SECRET)
      params.append('grant_type', 'authorization_code')
      params.append('code', code)
      params.append('scope', 'identify')

      // fetching access token from discord
      const response = await fetch(`https://discordapp.com/api/oauth2/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: params,
      })
      const json = await response.json()

      // fetching user identity using access token
      const getUser = await fetch('https://discordapp.com/api/users/@me', {
        headers: {
          Authorization: `Bearer ${json.access_token}`,
        },
      })
      const user = await getUser.json()
      console.log(user)

      // starting the websocket
      socketCallback(user)
      // exiting login window
      login.close()
    })()
  })

  login.on('closed', function () {
    login = null
  })
}

module.exports = { login }
