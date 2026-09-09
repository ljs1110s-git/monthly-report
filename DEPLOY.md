# Render 배포 방법

## 1. GitHub 저장소 준비

이 폴더의 파일을 GitHub 저장소에 올립니다.

필수 파일:

- `app.py`
- `requirements.txt`
- `templates/index.html`
- `render.yaml`

## 2. Render에서 새 Web Service 만들기

Render 대시보드에서 아래 순서로 진행합니다.

1. `New`를 누릅니다.
2. `Web Service`를 선택합니다.
3. GitHub 저장소를 연결합니다.
4. 아래 값으로 설정합니다.

설정값:

- Language: `Python 3`
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`
- Instance Type: `Free`

`render.yaml`이 인식되면 위 설정이 자동으로 잡힐 수 있습니다.

## 3. 업타임봇 설정

무료 한도를 아끼려면 업타임봇은 끄는 것을 권장합니다.

10분 또는 14분 55초마다 접속하게 하면 서버가 잠들지 않아서 무료 750시간을 거의 전부 사용합니다.

## 4. 중요한 주의사항

Render 무료 Web Service의 로컬 `uploads` 폴더는 영구 저장소가 아닙니다.

슬립, 재시작, 재배포 후 업로드한 파일이 사라질 수 있습니다.

파일을 안정적으로 보존하려면 다음 중 하나가 필요합니다.

- Render 유료 인스턴스와 Persistent Disk 사용
- Google Drive, Supabase Storage, S3 같은 외부 저장소 사용
