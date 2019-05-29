node {
  stage('Init') {
    checkout scm
    sh 'cp /home/jenkins/hotmaps/secrets.py ./api/app/secrets.py'
    sh 'cp -Rf /home/jenkins/hotmaps/pytest_suit .'
    sh 'cp /home/jenkins/hotmaps/online_status.sh .'
  }
    
  stage('Build') {
    try {
      sh 'docker-compose -f docker-compose-run-api-only.yml up -d --build'
      // let some time for the server (API) to start
      sleep 10
      // run script that checks if the API is reachable
      sh './online_status.sh'
    }
    catch (error) {
      // stop services
      sh 'docker-compose down'  
      throw exception
    }
  }

  stage('Test') {
    try {
      // run API tests
      sh '''#!/bin/bash
        export WORKSPACE=`pwd`
        virtualenv testenv -p /usr/bin/python3
        source testenv/bin/activate
        pip install -U pytest requests
        mkdir pytest_reports
        pytest --junitxml=pytest_reports/results.xml pytest_suit/
      '''
    }
    finally {
      // stop services
      sh 'docker-compose -f docker-compose-run-api-only.yml down' 
    }
  }
  
  // get commit id
  env.COMMIT_ID = sh(returnStdout: true, script: 'git rev-parse HEAD')
  
  stage('Deploy') {
    if (env.BRANCH_NAME == 'develop') {
      echo "Deploying to DEV platform"
      commitId = sh(returnStdout: true, script: 'git rev-parse HEAD')
      sshagent(['sshhotmapsdev']) {
        sh 'ssh -o StrictHostKeyChecking=no -l iig hotmapsdev.hevs.ch "./deploy_backend.sh \$COMMIT_ID"'
      }
    } else if (env.BRANCH_NAME == 'master') {
      echo "Deploying to PROD platform"
      echo "Deployment to PROD is currently disabled"
    } else {
      echo "${env.BRANCH_NAME}: not deploying"
    }
  }
}