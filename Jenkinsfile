// Jenkinsfile untuk agent Windows (Jenkins di Windows + Docker Desktop)
pipeline {
  agent any

  environment {
    IMAGE_NAME           = 'khaila766/simple-notes-app'
    REGISTRY_CREDENTIALS = 'dockerhub-credentials'
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Build') {
      steps { bat 'echo Mulai build aplikasi simple-notes-app' }
    }

    stage('Build Docker Image') {
      steps { bat "docker build -t %IMAGE_NAME%:%BUILD_NUMBER% -t %IMAGE_NAME%:latest ." }
    }

    stage('Deploy + Test Database') {
      steps {
        bat '''
          set IMAGE_NAME=%IMAGE_NAME%
          set IMAGE_TAG=%BUILD_NUMBER%
          docker compose down
          docker compose up -d
        '''
        powershell '''
          $ok = $false
          for ($i = 0; $i -lt 30; $i++) {
            try {
              $r = Invoke-RestMethod -Uri http://localhost:5000/health -TimeoutSec 5
              if ($r.status -eq "ok") { $ok = $true; break }
            } catch { }
            Start-Sleep -Seconds 5
          }
          if (-not $ok) { Write-Error "Aplikasi/database tidak sehat"; exit 1 }
          Write-Output "Health check OK (database connected)"
        '''
      }
    }

    stage('Push Docker Image') {
      steps {
        withCredentials([usernamePassword(credentialsId: REGISTRY_CREDENTIALS,
            usernameVariable: 'USER', passwordVariable: 'PASS')]) {
          bat 'echo %PASS%| docker login -u %USER% --password-stdin'
          bat "docker push %IMAGE_NAME%:%BUILD_NUMBER%"
          bat "docker push %IMAGE_NAME%:latest"
        }
      }
    }
  }

  post {
    success { echo 'Pipeline sukses. Aplikasi berjalan di http://localhost:5000' }
    failure { bat 'docker compose logs --tail=50' }
    always  { echo 'Selesai build' }
  }
}
