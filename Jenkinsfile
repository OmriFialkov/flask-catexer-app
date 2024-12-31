pipeline {
    agent any
     environment {
        MYSQL_PASSWORD = credentials('Juserpass')  // Use your actual Jenkins secret ID here - going to docker compose when running d-c up - finds it.
        MYSQL_ROOT_PASSWORD = credentials('Jrootpass')  // Use your actual Jenkins secret ID here - same here.
    }
    triggers {
        pollSCM('* * * * *')  // Poll SCM every minute
    }

    stages {
        stage('Cleanup') {
            steps {
                 script {
                    sh '''
                    # Navigate to the project directory if it exists
                    if [ -d "./flask-catexer-app" ]; then
                        cd flask-catexer-app
                        docker-compose down -v || true  # Bring down running containers; ignore errors if none exist
                        cd ..
                    fi
                    
                    # Remove the entire workspace directory
                    echo "Cleaning workspace directory: ${WORKSPACE}"
                    cd ${WORKSPACE}
                    rm -rf ./*
                    ls -la
                    '''
                }
                // no [[ ]] !! its sh not bash!
            }
        }
        stage('Build') {
            steps {
                sh """
                git clone https://github.com/OmriFialkov/flask-catexer-app.git
                cp /var/lib/.env /var/lib/jenkins/workspace/jenkins/flask-catexer-app
                cd flask-catexer-app/
                pwd
                docker-compose build --no-cache
                docker image prune -f
                """
                // prune removes untagged images - leftover from previous build's docker-compose build.
            }
        }
        stage('Push Docker') {
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
                cd flask-catexer-app/
                pwd
                docker-compose up -d
                docker-compose ps
                '''
            }
        }
        stage('Test') {
            steps {
                sh 'sleep 3'
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
        stage('Deploy - Setup EC2') {
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
                
                echo "Public IP: \$PUBLIC_IP"
                echo "\$PUBLIC_IP" > /var/lib/jenkins/workspace/jenkins/flask-catexer-app/ip.txt
                """
            }
        }
    }
}
        stage('Deploy - Running project') {
    steps {
        script {
            sshagent(['ec2-ssh']) { // Use Jenkins SSH private key credential
                sh """
                #!/bin/bash
                
                PUBLIC_IP=\$(cat /var/lib/jenkins/workspace/jenkins/flask-catexer-app/ip.txt) #Use \\ for cat to escape \$ so Groovy doesn’t misinterpret it.
                export PUBLIC_IP
                
                echo "checking whether ip fetched successfully to proceed.."
                if [ -z "\${PUBLIC_IP}" ]; then
                    echo "ERROR - Public IP is not set, exiting.."
                    exit 1
                fi

                echo "proceeding when ec2 is accessible over ssh ( checking sshd, ssh server status, whether it is listening on port 22 to connection requests. ).."
                while ! nc -z \${PUBLIC_IP} 22; do
                    echo "waiting for ssh test to succeed.."
                    sleep 3
                done
                
                echo "copying project files to the EC2 instance..."
                scp -o StrictHostKeyChecking=no \
                    /var/lib/jenkins/workspace/jenkins/flask-catexer-app/docker-compose.yaml \
                    /var/lib/jenkins/workspace/jenkins/flask-catexer-app/init.sql \
                    /var/lib/jenkins/workspace/jenkins/.env \
                    ec2-user@\${PUBLIC_IP}:/home/ec2-user/

                # -v for verbose - logging ssh / scp process if got errors.
                echo "using ssh to log to the ec2 machine.."
                ssh -o StrictHostKeyChecking=no ec2-user@\${PUBLIC_IP} << EOF

                echo "now in ec2, waiting for user-data script to end successfully ( installing docker ).."
                while [ ! -f /var/lib/cloud/instance/boot-finished ]; do
                    echo "sadly still waiting.."
                    sleep 3
                done
                
                echo "adding db passwords to .env manually and securely..."
                echo "MYSQL_PASSWORD=\${MYSQL_PASSWORD}" >> /home/ec2-user/.env
                echo "MYSQL_ROOT_PASSWORD=\${MYSQL_ROOT_PASSWORD}" >> /home/ec2-user/.env
                cat /home/ec2-user/.env

                echo "running project now..."
                newgrp docker
                cd /home/ec2-user/
                docker-compose up -d --quiet-pull
                EOF
                
                echo "Project is finally running on the EC2 instance! :("
                """
            }
        }
    }
}

    }
}
