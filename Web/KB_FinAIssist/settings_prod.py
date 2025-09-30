from .settings import *   # 베이스 설정 불러오기
import os

DEBUG = False # 운영환경 디버깅 (임시)

# CSRF 신뢰 오리진 설정
# Django 4.0부터 CSRF_TRUSTED_ORIGINS는 'https://' 또는 'http://'와 같은 스킴을 포함해야 합니다.
CSRF_TRUSTED_ORIGINS = [
  "https://finaissist.com",
  "https://www.finaissist.com",
  "http://FinAissistWeb2-env.eba-ppiwmga8.ap-northeast-2.elasticbeanstalk.com",
  "https://FinAissistWeb2-env.eba-ppiwmga8.ap-northeast-2.elasticbeanstalk.com",
]
# ALLOWED_HOSTS = ['.elasticbeanstalk.com']
ALLOWED_HOSTS = [
  "FinAissistWeb2-env.eba-ppiwmga8.ap-northeast-2.elasticbeanstalk.com",
  ".elasticbeanstalk.com",
  "finaissist.com",
  "www.finaissist.com",
  "localhost", "127.0.0.1"
]
