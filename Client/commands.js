const svnUltimate = require('node-svn-ultimate')

// SVN username and password

let checkout = (url, path, user, password) => {
  svnUltimate.commands.checkout(
    url,
    path,
    {
      username: user,
      password: password,
    },
    err => {
      console.log('Checkout complete!')
    }
  )
}

let update = (path, user, password) => {
  svnUltimate.commands.update(
    path,
    {
      username: user,
      password: password,
    },
    err => {
      console.log('Update complete!')
    }
  )
}

let commit = (path, user, password) => {
  svnUltimate.commands.commit(
    path,
    {
      username: user,
      password: password,
      params: ['-m "commit works!"'],
    },
    err => {
      console.log('Commit complete!')
    }
  )
}

module.exports = { checkout, update, commit }
