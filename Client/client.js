const svnUltimate = require('node-svn-ultimate')
const WebSocket = require('ws')

// SVN repository URL
const URL = 'https://24.210.238.51:8443/svn/ErisTesting/'
// Path to working directory
const PATH = 'E:/Capstone/testSVN'

// SVN username and password
const USER = 'Cam'
const PASSWORD = 'ErisSVN'

let checkout = (url, path) => {
  svnUltimate.commands.checkout(
    url,
    path,
    {
      username: USER,
      password: PASSWORD,
      params: ['-m "commit works!"'],
    },
    err => {
      console.log('Checkout complete!')
    }
  )
}

let update = path => {
  svnUltimate.commands.update(
    path,
    {
      username: USER,
      password: PASSWORD,
      params: ['-m "commit works!"'],
    },
    err => {
      console.log('Update complete!')
    }
  )
}

let commit = path => {
  svnUltimate.commands.commit(
    path,
    {
      username: USER,
      password: PASSWORD,
      params: ['-m "commit works!"'],
    },
    err => {
      console.log('Commit complete!')
    }
  )
}

/////////////////////////////////////////////////////////////////
// WEBSOCKETS STUFF
// Create WebSocket connection.
const URI = 'ws://24.210.238.51:6969'

const socket = new WebSocket(URI)

// Connection opened
socket.addEventListener('open', function (event) {
  //socket.send('Hello Server!')
  console.log('conencted to websocket server!')
  socket.send('Cam')
})

// Listen for messages
socket.addEventListener('message', function (event) {
  console.log('message received: ', event.data)
  data = event.data
  jsonData = JSON.parse(data)

  if (!jsonData['username_valid']) {
    console.log('invalid username!')
  } else {
    console.log('valid')
    socket.send('password')
    //socket.send(JSON.stringify({ command: 'ping' }))
  }
  if (jsonData['command'] === 'ping') {
    console.log('pinged!')
    socket.send(JSON.stringify({ command: 'ping_response' }))
    console.log('pong sent!')
  }

  // Commit command
  if (jsonData['command'] === 'commit') {
    console.log('commited')
    socket.send(
      JSON.stringify({ command_success: true, command: 'commit_response' })
    )
    commit(PATH)
  }

  // Update command
  if (jsonData['command'] === 'update') {
    console.log('updated')
    socket.send(
      JSON.stringify({ command_success: true, command: 'update_response' })
    )
    update(PATH)
  }

  // Checkout command
  if (jsonData['command'] === 'checkout') {
    console.log('checked out')
    socket.send(
      JSON.stringify({ command_success: true, command: 'checkout_response' })
    )
    checkout(URL, PATH)
  }
})
