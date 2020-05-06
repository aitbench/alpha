pipeline {
  agent any

  stages {

    stage('Info') {
      steps {
        sh '''
          echo Building ${BRANCH_NAME}... in ${WORKSPACE}
          echo Home: $HOME
        '''
      }
    }

    stage('Linting Main App') {
      steps {
        sh '''
          autopep8 --in-place --ignore=E501 --aggressive --aggressive app.py
          flake8 --ignore=E501 app.py
        '''
      }
    }

    stage('Linting Libraries') {
      steps {
        sh '''
          autopep8 --in-place --ignore=E501 --aggressive --aggressive ./aitblib/*.py
          flake8 --ignore=E501 ./aitblib/*.py
        '''
      }
    }

    stage('Push to AITBench') {
      steps {
        sh '''
          comment=$(git log --pretty=format:"%s")
          echo $comment
          cp -r * $HOME/repos/alpha
          cp -r .gitignore $HOME/repos/alpha
          cd $HOME/repos/alpha
        '''
      }
    }

  }
}
