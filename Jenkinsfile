node {
  stage('Init') {
    checkout scm
    // sh 'cp /home/jenkins/hotmaps/secrets.py ./api/app/secrets.py'
    sh 'cp /home/jenkins/hotmaps/toolbox-service.env ./.env'
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
      sh 'docker-compose -f docker-compose-run-api-only.yml down'
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
}
