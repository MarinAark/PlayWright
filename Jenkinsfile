pipeline {
    agent any

    environment {
        VENV_DIR = '.venv'
        ALLURE_RESULTS = 'results/allure-results'
        PYTHON_VERSION = '3.8'
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
                    playwright install
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo '🧪 执行测试用例'
                sh '''
                    source ${VENV_DIR}/bin/activate
                    # 确保结果目录存在
                    mkdir -p results
                    mkdir -p screenshots
                    
                    # 运行所有测试并生成Allure结果
                    pytest tests/ -v --alluredir=${ALLURE_RESULTS} --html=results/report.html --self-contained-html
                    
                    # 显示测试结果摘要
                    echo "测试执行完成，结果保存在: ${ALLURE_RESULTS}"
                    ls -la ${ALLURE_RESULTS} || echo "Allure结果目录为空"
                '''
            }
        }

        stage('Generate Allure Report') {
            steps {
                echo '📊 生成 Allure 报告'
                script {
                    // 检查Allure结果是否存在
                    if (fileExists("${ALLURE_RESULTS}")) {
                        echo "✅ Allure结果文件存在，开始生成报告"
                        allure includeProperties: false, jdk: '', results: [[path: "${ALLURE_RESULTS}"]]
                    } else {
                        echo "❌ Allure结果文件不存在: ${ALLURE_RESULTS}"
                        error "无法生成Allure报告，测试可能失败或未生成结果"
                    }
                }
            }
        }
        
        stage('Archive Test Results') {
            steps {
                echo '📁 归档测试结果'
                script {
                    // 归档HTML报告
                    if (fileExists("results/report.html")) {
                        archiveArtifacts artifacts: 'results/report.html', fingerprint: true
                        echo "✅ HTML报告已归档"
                    }
                    
                    // 归档测试数据
                    if (fileExists("test_data")) {
                        archiveArtifacts artifacts: 'test_data/**/*.json', fingerprint: true
                        echo "✅ 测试数据已归档"
                    }
                    
                    // 归档截图（如果有）
                    if (fileExists("screenshots")) {
                        archiveArtifacts artifacts: 'screenshots/**/*.png', fingerprint: true
                        echo "✅ 测试截图已归档"
                    }
                }
            }
        }
    }

    post {
        always {
            echo '✅ 构建结束，尝试发送邮件'
            
            script {
                // 构建邮件内容
                def emailBody = """
构建结果：${currentBuild.currentResult}
项目名称：${env.JOB_NAME}
构建编号：#${env.BUILD_NUMBER}
构建者：${env.BUILD_USER_ID ?: '未知用户'}
构建链接：${env.BUILD_URL}

测试结果：
- Allure报告：${env.BUILD_URL}allure/
- HTML报告：${env.BUILD_URL}artifact/results/report.html

请登录 Jenkins 查看详情。
                """
                
                try {
                    emailext (
                        to: '330354280@qq.com',
                        subject: "${currentBuild.currentResult}: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                        body: emailBody,
                        mimeType: 'text/plain'
                    )
                    echo "✅ 邮件发送成功"
                } catch (e) {
                    echo "❌ 邮件发送失败: ${e.getMessage()}"
                }
            }
        }
        
        success {
            echo '🎉 构建成功！'
            script {
                if (fileExists("${ALLURE_RESULTS}")) {
                    echo "📊 Allure报告已生成，可在Jenkins中查看"
                }
            }
        }
        
        failure {
            echo '❌ 构建失败！'
            script {
                echo "构建失败原因可能是："
                echo "1. 测试用例执行失败"
                echo "2. 依赖安装失败"
                echo "3. Allure结果生成失败"
                echo "请检查Jenkins控制台输出获取详细信息"
            }
        }
    }
}