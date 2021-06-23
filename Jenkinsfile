node {
    def image_name = "tutano-bot"
    def image = null

    stage('Checkout') {
        checkout scm
    }

    stage('Build') {
        image = docker.build("${image_name}:${env.BUILD_ID}")
    }

    stage('Deploy'){
        try{
            sh "docker stop ${image_name} && docker rm ${image_name}"
        }catch(Exception e){
            echo e.getMessage()
        }
        withCredentials([string(credentialsId: 'tutano-telegram-bot-token', variable: 'token')]) {
                    def runArgs = '\
-e "TELEGRAM_TOKEN=$token" \
--restart unless-stopped \
--name ' + image_name

                    def container = image.run(runArgs)
        }
    }
}