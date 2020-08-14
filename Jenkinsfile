pipeline {
    agent any

    stages {
        stage('build') {
            steps {
                sh 'make build'
            }
        }
        stage('test') {
            steps {
                sh 'make test'
            }
        }
        stage('verify') {
            steps {
                sh 'make verify'
            }
        }
        stage('push') {
            when {
                branch 'master'
            }
            steps {
                sh 'make push'
            }
        }
    }
}
