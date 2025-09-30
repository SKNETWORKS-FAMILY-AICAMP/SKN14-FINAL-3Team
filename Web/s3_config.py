"""
S3 설정 확인 스크립트
config.py의 설정을 사용하여 S3 설정을 확인합니다.
"""

import config

# S3 설정 확인 함수
def check_s3_config():
    """S3 설정이 올바른지 확인"""
    required_vars = [
        ('AWS_ACCESS_KEY_ID', config.AWS_ACCESS_KEY_ID),
        ('AWS_SECRET_ACCESS_KEY', config.AWS_SECRET_ACCESS_KEY), 
        ('AWS_STORAGE_BUCKET_NAME', config.AWS_STORAGE_BUCKET_NAME)
    ]
    
    missing_vars = []
    for var_name, var_value in required_vars:
        if not var_value or var_value == f'your_{var_name.lower()}':
            missing_vars.append(var_name)
    
    if missing_vars:
        print(f"⚠️  다음 환경변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        print("환경변수를 설정하거나 .env 파일을 생성해주세요.")
        print("\n설정 방법:")
        print("1. .env 파일을 생성하고 다음 내용을 추가:")
        print("   AWS_ACCESS_KEY_ID=your_actual_access_key_id")
        print("   AWS_SECRET_ACCESS_KEY=your_actual_secret_access_key")
        print("   AWS_STORAGE_BUCKET_NAME=your_bucket_name")
        print("   AWS_S3_REGION_NAME=ap-northeast-2")
        print("\n2. 또는 시스템 환경변수로 설정")
        return False
    
    print("✅ S3 설정이 올바르게 구성되었습니다.")
    print(f"   - 버킷: {config.AWS_STORAGE_BUCKET_NAME}")
    print(f"   - 리전: {config.AWS_S3_REGION_NAME}")
    return True

if __name__ == "__main__":
    check_s3_config()
