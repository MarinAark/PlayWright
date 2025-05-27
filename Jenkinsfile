pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        ALLURE_RESULTS = 'tests/results/allure-results'
    }

    stages {

        stage('Clone') {
            steps {
                echo '✅ 拉取代码'
                checkout scm
            }
        }

        stage('Setup Python Env') {
            steps {
                echo '🐍 创建虚拟环境并安装依赖'
                sh '''
                    python3 -m venv ${VENV_DIR}
                    source ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo '🧪 执行测试用例'
                sh '''
                    source ${VENV_DIR}/bin/activate
                    pytest tests/ --alluredir=${ALLURE_RESULTS}
                '''
            }
        }

        stage('Generate Allure Report') {
            steps {
                echo '📊 生成 Allure 报告'
                allure includeProperties: false, jdk: '', results: [[path: "${ALLURE_RESULTS}"]]
            }
        }
    }

    post {
        always {
            echo '✅ 构建结束'

            // 发送邮件通知
            emailext (
                to: '330354280@qq.com',  // TODO: 改成你自己的收件邮箱
                subject: "${currentBuild.currentResult}: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """
构建结果：${currentBuild.currentResult}
项目名称：${env.JOB_NAME}
构建编号：#${env.BUILD_NUMBER}
触发者：${env.BUILD_USER_ID}
构建链接：${env.BUILD_URL}

请登录 Jenkins 查看详情。
                """,
                mimeType: 'text/plain'
            )
        }

        failure {
            echo '❌ 构建失败，请查看日志'
        }
    }
}
