pipeline {
    agent any

    triggers {
        pollSCM('* * * * *')  // Poll SCM every minute
    }

    stages {
        stage('Cleanup') {
            steps {
                sh '''
                if [ "$(docker ps -q)" ]; then
                   docker stop $(docker ps -q)
                fi
                if [ "$(docker ps -aq)" ]; then
                    docker rm -f $(docker ps -aq)
                fi
                if [ -d "./flask-catexer-app" ]; then rm -rf "./flask-catexer-app"; fi
                if [ "$(docker images -q flask)" ]; then docker rmi -f flask; fi
                '''
                // no [[ ]] !! its sh not bash
            }
        }
        stage('Build') {
            steps {
                sh 'git clone https://github.com/OmriFialkov/flask-catexer-app.git'
                sh 'cd flask-catexer-app && docker build -t flask .'
            }
        }
        stage('Run') {
            steps {
                sh '''
                docker run --rm -d -p 5000:5000 --name flask flask
                docker ps
                '''
            }
        }
        stage('Test') {
            steps {
                sh 'sleep 5'
                sh '''
                if ! docker logs flask; then
                echo "container logs checking failed!"
                exit 1
                fi
                '''
                sh '''
                if ! curl -f http://localhost:5000; then
                    echo "App is not reachable.."
                    exit 1
                fi
                '''
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying.....'
            }
        }
    }
}
