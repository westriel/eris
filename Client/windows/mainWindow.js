const sidenav = document.querySelector('.sidenav')
const fs = require('fs')
// Read repoSettings.json
const repos = JSON.parse(
  fs.readFileSync('./repoSettings.json', err => {
    if (err) throw err
  })
)

let selectRepo = event => {
  id = event.target.id

  const currentSettings = JSON.parse(
    fs.readFileSync('./repoSettings.json', err => {
      if (err) throw err
    })
  )
  ipcRenderer.send('change path', id)
  // load json into form
  let commit = document.querySelector('#commit')
  let update = document.querySelector('#update')
  let pword = document.querySelector('#password')
  let uname = document.querySelector('#username')
  let repoName = document.querySelector('#name')
  let dirName = document.querySelector('#dir')
  dirName.setAttribute('value', currentSettings[id].path)
  pword.setAttribute('value', currentSettings[id].password)
  uname.setAttribute('value', currentSettings[id].username)
  repoName.setAttribute('value', currentSettings[id].name)
  dirName.setAttribute('value', currentSettings[id].path)

  console.log(currentSettings[id].n_commit)
  currentSettings[id].n_commit
    ? commit.setAttribute('checked', '')
    : commit.removeAttribute('checked')
  currentSettings[id].n_update
    ? update.setAttribute('checked', '')
    : update.removeAttribute('checked')
}

// Fill sidenav with list of available repos
for (repo in repos) {
  let name = repo
  if (repos[repo].name != '') {
    name = repos[repo].name
  }
  const repoItem = document.createElement('a')
  repoItem.className = 'collection-item truncate repo'
  repoItem.id = repo
  const textItem = document.createTextNode(name)
  if (
    repos[repo].username == '' ||
    repos[repo].password == '' ||
    repos[repo].path == ''
  ) {
    const icon = document.createElement('i')
    icon.className = 'material-icons'
    icon.append('error')
    repoItem.appendChild(icon)
  }
  repoItem.appendChild(textItem)
  sidenav.appendChild(repoItem)
  repoItem.addEventListener('click', selectRepo)
}

const { ipcRenderer } = require('electron')

const log = document.querySelector('#log')
// receive commands from main process
ipcRenderer.on('command', (event, command) => {
  console.log(command)
  const time = new Date()
  const p = document.createElement('p')
  p.className = 'collection-item '
  const textItem = document.createTextNode(
    `${time.getHours()}:${time.getMinutes()} | ${command}`
  )
  p.appendChild(textItem)
  log.appendChild(p)
})

// set login display
const loginDisplay = document.querySelector('#loginDisplay')
ipcRenderer.on('login:user', (event, username) => {
  console.log('test test')
  const userText = document.createTextNode(`logged in as: ${username}`)
  loginDisplay.appendChild(userText)
})

let closeSocket = () => {
  ipcRenderer.send('logout')
  loginDisplay.innerText = ''
}

// Send form info to main process
let submitForm = event => {
  event.preventDefault()
  const commit = document.querySelector('#commit').checked
  const merge = document.querySelector('#merge').checked
  let password = document.querySelector('#password').value
  let username = document.querySelector('#username').value
  let repName = document.querySelector('#name').value
  let path = document.querySelector('#dir').value
  ipcRenderer.send('settings', {
    commit: commit,
    merge: merge,
    username: username,
    password: password,
    repoName: repName,
    path: path,
  })
}

ipcRenderer.on('dirSelected', (event, data) => {
  document.querySelector('#dir').setAttribute('value', data)
})
let saveDir = () => {
  ipcRenderer.send('changeDir')
}

const dirBtn = document.querySelector('#changeDir')
dirBtn.addEventListener('click', saveDir)
const logout = document.querySelector('#logout')
logout.addEventListener('click', closeSocket)
const form = document.querySelector('form')
form.addEventListener('submit', submitForm)
