pipeline {
    agent any
     environment {
        MYSQL_PASSWORD = credentials('Juserpass')  // Use your actual Jenkins secret ID here
        MYSQL_ROOT_PASSWORD = credentials('Jrootpass')  // Use your actual Jenkins secret ID here
    }
    triggers {
        pollSCM('* * * * *')  // Poll SCM every minute
    }

    stages {
        stage('Cleanup') {
            steps {
                sh '''
                docker-compose down -v
                if [ -d "./flask-catexer-app" ]; then rm -rf "./flask-catexer-app"; fi
                '''
                // no [[ ]] !! its sh not bash!
            }
        }
        stage('Build') {
            steps {
                sh 'git clone https://github.com/OmriFialkov/flask-catexer-app.git'
                sh 'cp /var/lib/.env /var/lib/jenkins/workspace/jenkins'
                sh 'cd flask-catexer-app'
                sh 'docker-compose build --no-cache'
                // dont forget to add push stage between build and run. 
            }
        }
        stage('Run') {
            steps {
                sh '''
                docker-compose up -d
                docker-compose ps
                '''
            }
        }
        stage('Test') {
            steps {
                sh 'sleep 5'
                sh '''
                if ! docker-compose logs; then
                echo "container logs checking failed!"
                exit 1
                fi
                '''
                sh '''
                for i in $(seq 1 5); do
                    if curl -f http://localhost:5002; then
                        echo "App is reachable."
                        break 
                    fi
                    echo "Attempt $i failed."
                    sleep 6
                done
                
                if [ $i -eq 5 ]; then
                    echo "App is not reachable after 5 attempts."
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
