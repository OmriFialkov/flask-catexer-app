pipeline {
    agent any
     environment {
        MYSQL_PASSWORD = credentials('Juserpass')  // Use your actual Jenkins secret ID here
        MYSQL_ROOT_PASSWORD = credentials('Jrootpass')  // Use your actual Jenkins secret ID here
        PUBLIC_IP = ''  // Define a blank PUBLIC_IP variable to see between stages.
    }
    triggers {
        pollSCM('* * * * *')  // Poll SCM every minute
    }

    stages {
        stage('Cleanup') {
            steps {
                // prune removes none-none images' leftovers from previous runs and builds..
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
                sh 'docker image prune -f'
            }
        }
        stage('Push') {
    steps {
        script {
            withCredentials([usernamePassword(credentialsId: 'docker-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                sh '''
                echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                docker push crazyguy888/flask-compose-catproject:latest
                '''
            }
        }
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
        script {
            withCredentials([usernamePassword(credentialsId: 'aws-creds', usernameVariable: 'AWS_ACCESS_KEY_ID', passwordVariable: 'AWS_SECRET_ACCESS_KEY')]) {
                sh """
                #!/bin/bash
                
                export AWS_ACCESS_KEY_ID=\$AWS_ACCESS_KEY_ID
                export AWS_SECRET_ACCESS_KEY=\$AWS_SECRET_ACCESS_KEY
                
                INSTANCE_ID=\$(aws ec2 run-instances \
                    --region us-east-1 \
                    --image-id ami-01816d07b1128cd2d \
                    --instance-type t2.micro \
                    --key-name privatekey \
                    --security-groups flask-mysql \
                    --iam-instance-profile Name=access-to-s3 \
                    --user-data file:///var/lib/jenkins/scripts/userdata.sh \
                    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=project}]' \
                    --query 'Instances[0].InstanceId' \
                    --output text)
                
                echo "instance-id: \$INSTANCE_ID"
                echo ""
                
                # Wait for the instance to be running, added region parameter for wait because of error.
                echo "Waiting for machine to run for fetching IP address..."
                aws ec2 wait instance-running --instance-ids "\$INSTANCE_ID" --region us-east-1
                
                # Check if INSTANCE_ID is empty
                if [ -z "\$INSTANCE_ID" ]; then 
                    echo "Error: INSTANCE_ID is empty"
                    exit 1
                fi
                
                # Fetch the public IP address of the instance
                PUBLIC_IP=\$(aws ec2 describe-instances \
                    --region us-east-1 \
                    --instance-ids "\$INSTANCE_ID" \
                    --query 'Reservations[0].Instances[0].PublicIpAddress' \
                    --output text)
                
                echo ""
                echo "Public IP: \$PUBLIC_IP"
                """
            }
        }
    }
}
        stage('Configure and Run Docker') {
    steps {
        script {
            sshagent(['ec2-ssh']) { // Use Jenkins SSH private key credential
                sh """
                #!/bin/bash
                
                echo "Copying project files to the EC2 instance..."
                scp /var/lib/jenkins/workspace/jenkins/docker-compose.yaml ec2-user@\${PUBLIC_IP}:/home/ec2-user/
                scp /var/lib/jenkins/workspace/jenkins/init.sql ec2-user@\${PUBLIC_IP}:/home/ec2-user/
                
                echo "Running docker-compose on the EC2 instance..."
                ssh ec2-user@\${PUBLIC_IP} << EOF
                cd /home/ec2-user/
                ls
    
                echo "Running project..."
                docker-compose up -d
                docker-compose ps
                EOF
                
                echo "Project is now running on the EC2 instance."
                """
            }
        }
    }
}

    }
}
