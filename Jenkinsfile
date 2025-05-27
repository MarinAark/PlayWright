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
            echo '✅ 构建结束，尝试发送邮件'

            script {
                try {
                    emailext (
                        to: '330354280@qq.com',
                        subject: "${currentBuild.currentResult}: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        body: """
构建结果：${currentBuild.currentResult}
项目名称：${env.JOB_NAME}
构建编号：#${env.BUILD_NUMBER}
构建者：${env.BUILD_USER_ID ?: '未知用户'}
构建链接：${env.BUILD_URL}

请登录 Jenkins 查看详情。
                        """,
                        mimeType: 'text/plain'
                    )
                } catch (e) {
                    echo "❌ 邮件发送失败: ${e.getMessage()}"
                }
            }
        }

        failure {
            echo '❌ 构建失败，请查看日志'
        }
    }
}
