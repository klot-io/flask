pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'make build'
            }
        }
        stage('Test') {
            steps {
                sh 'make build'
            }
        }
        stage('Setup') {
            steps {
                sh 'make setup'
            }
        }
        stage('Push') {
            when {
                branch 'master'
            }
            steps {
                sh 'make push'
            }
        }
    }
}
