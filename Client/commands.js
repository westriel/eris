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
      params: ['--accept p'],
    },
    err => {
      console.log('Update complete!')
    }
  )
}

let commit = (path, user, password, msg) => {
  svnUltimate.commands.commit(
    path,
    {
      username: user,
      password: password,
      params: [`-m "${msg}"`],
    },
    err => {
      console.log('Commit complete!')
    }
  )
}

let add = (files, path, user, password) => {
  files.forEach((file, index) => {
    files[index] = `${path}\\${file}`
  })
  svnUltimate.commands.add(
    files,
    {
      username: user,
      password: password,
    },
    err => {
      console.log('Add complete!')
    }
  )
}

let del = (files, path, user, password) => {
  files.forEach((file, index) => {
    files[index] = `${path}\\${file}`
  })
  svnUltimate.commands.del(
    files,
    {
      username: user,
      password: password,
    },
    err => {
      console.log('Delete complete!')
    }
  )
}
module.exports = { checkout, update, commit, add, del }
