pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'manjunadhreddy'
        IMAGE_NAME = 'aqi-prediction-api'
        IMAGE_TAG = "v${BUILD_NUMBER}"
        EC2_HOST = '13.201.43.179'
        EC2_USER = 'ubuntu'
    }

    stages {

        stage('Checkout') {
            steps {
                echo '📥 Pulling code from GitHub...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                sh """
                    docker build -t ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG} .
                    docker tag ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG} \
                               ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest
                """
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo '📤 Pushing image to Docker Hub...'
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker push ${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${DOCKER_HUB_USER}/${IMAGE_NAME}:latest
                    """
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                echo '🚀 Deploying to Kubernetes...'
                sh """
                    sudo kubectl set image deployment/aqi-prediction-deployment \
                        aqi-prediction-api=${DOCKER_HUB_USER}/${IMAGE_NAME}:${IMAGE_TAG}
                    sudo kubectl rollout status deployment/aqi-prediction-deployment
                """
            }
        }

        stage('Verify Deployment') {
            steps {
                echo '✅ Verifying deployment...'
                sh """
                    sudo kubectl get pods
                    sudo kubectl get services
                    curl -f http://localhost:30080/health
                """
            }
        }
    }

    post {
        success {
            echo '🎉 Pipeline completed successfully! AQI API is live.'
        }
        failure {
            echo '❌ Pipeline failed! Check the logs above.'
        }
        always {
            sh 'docker logout'
        }
    }
}