const sidenav = document.querySelector('.sidenav')
const fs = require('fs')
// Read repoSettings.json
const repos = JSON.parse(
  fs.readFileSync('./repoSettings.json', err => {
    if (err) throw err
  })
)

// Triggers whe the user clicks on a repo
let selectRepo = event => {
  id = event.target.id

  // get settings from settings json
  const currentSettings = JSON.parse(
    fs.readFileSync('./repoSettings.json', err => {
      if (err) throw err
    })
  )
  // changes the current working directory to the repo that was clicked
  ipcRenderer.send('change path', id)

  document.querySelector('form').reset()
  // load json into form
  let commit = document.querySelector('#commit')
  let update = document.querySelector('#update')
  let autoUpdate = document.querySelector('#autoupdate')
  let pword = document.querySelector('#password')
  let uname = document.querySelector('#username')
  let repoName = document.querySelector('#name')
  let dirName = document.querySelector('#dir')
  dirName.setAttribute('value', currentSettings[id].path)
  pword.setAttribute('value', currentSettings[id].password)
  uname.setAttribute('value', currentSettings[id].username)
  repoName.setAttribute('value', currentSettings[id].name)
  dirName.setAttribute('value', currentSettings[id].path)

  // sets checkboxes to right value
  currentSettings[id].autoUpdate
    ? autoUpdate.setAttribute('checked', '')
    : autoUpdate.removeAttribute('checked')
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
  // if there is a nickname set, have it be displayed
  if (repos[repo].name != '') {
    name = repos[repo].name
  }
  const repoItem = document.createElement('a')
  // truncate repo names
  repoItem.className = 'collection-item truncate repo'
  repoItem.id = repo
  const textItem = document.createTextNode(name)
  // if username, password, or dir is not set, display warning
  if (
    repos[repo].username == '' ||
    repos[repo].password == '' ||
    repos[repo].path == ''
  ) {
    const icon = document.createElement('i')
    icon.className = 'material-icons left'
    icon.append('error')
    repoItem.appendChild(icon)
  }
  repoItem.appendChild(textItem)
  sidenav.appendChild(repoItem)
  // add click listener for each repo
  repoItem.addEventListener('click', selectRepo)
}

const { ipcRenderer } = require('electron')

const log = document.querySelector('#log')
// receive commands from main process
ipcRenderer.on('command', (event, command) => {
  // log the command, and the time it was sent
  const time = new Date()
  const p = document.createElement('p')
  p.className = 'collection-item '
  const textItem = document.createTextNode(
    // if the minuites are less than 10, format it so there is a leading 0
    `${time.getHours()}:${
      time.getMinutes() < 10 ? '0' + time.getMinutes() : time.getMinutes()
    } | ${command}`
  )
  p.appendChild(textItem)
  log.appendChild(p)
})

// set login display
const loginDisplay = document.querySelector('#loginDisplay')
// set login display with discord name
ipcRenderer.on('login:user', (event, username) => {
  const userText = document.createTextNode(`logged in as: ${username}`)
  loginDisplay.appendChild(userText)
})

// logout
let closeSocket = () => {
  ipcRenderer.send('logout')
  loginDisplay.innerText = ''
}

// Send form info to main process
let submitForm = event => {
  event.preventDefault()
  const autoUpdate = document.querySelector('#autoupdate').checked
  const commit = document.querySelector('#commit').checked
  const update = document.querySelector('#update').checked
  let password = document.querySelector('#password').value
  let username = document.querySelector('#username').value
  let repName = document.querySelector('#name').value
  let path = document.querySelector('#dir').value
  ipcRenderer.send('settings', {
    autoUpdate: autoUpdate,
    commit: commit,
    update: update,
    username: username,
    password: password,
    repoName: repName,
    path: path,
  })
}

// have backend bring up directory dialog
ipcRenderer.on('dirSelected', (event, data) => {
  document.querySelector('#dir').setAttribute('value', data)
})
let saveDir = () => {
  ipcRenderer.send('changeDir')
}

// updates repositories list in sidenav
let refresh = () => {
  console.log('clicked!')
  let updatedRepos = JSON.parse(fs.readFileSync('./repoSettings.json'))
  // repo list parent
  let repoList = document.querySelector('.sidenav')

  // clear repo list
  while (repoList.lastChild) {
    if (repoList.lastChild.className == 'collection-header') {
      console.log('cleared')
      break
    } else {
      repoList.removeChild(repoList.lastChild)
    }
  }
  console.log(updatedRepos)

  // repopulate repo list
  for (repo in updatedRepos) {
    let name = repo
    if (updatedRepos[repo].name != '') {
      name = updatedRepos[repo].name
    }
    const repoItem = document.createElement('a')
    repoItem.className = 'collection-item truncate repo'
    repoItem.id = repo
    const textItem = document.createTextNode(name)
    if (
      updatedRepos[repo].username == '' ||
      updatedRepos[repo].password == '' ||
      updatedRepos[repo].path == ''
    ) {
      const icon = document.createElement('i')
      icon.className = 'material-icons left'
      icon.append('error')
      repoItem.appendChild(icon)
    }
    repoItem.appendChild(textItem)
    sidenav.appendChild(repoItem)
    repoItem.addEventListener('click', selectRepo)
  }
}

// send refresh command back to backend
ipcRenderer.on('refresh', (event, data) => {
  refresh()
})

// add click listeners
const dirBtn = document.querySelector('#changeDir')
dirBtn.addEventListener('click', saveDir)
const logout = document.querySelector('#logout')
logout.addEventListener('click', closeSocket)
const form = document.querySelector('form')
form.addEventListener('submit', submitForm)
const refreshButton = document.querySelector('#refresh')
refreshButton.addEventListener('click', refresh)
// // Fill sidenav with list of available repos
