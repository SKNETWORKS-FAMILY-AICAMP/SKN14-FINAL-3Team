"""
S3에서 특정 파일이 존재하는지 확인하는 스크립트
"""

import config
import boto3
from botocore.exceptions import ClientError
import urllib.parse

def check_s3_file(file_path):
    """S3에서 파일 존재 여부 확인"""
    try:
        # S3 클라이언트 생성
        s3_client = boto3.client(
            's3',
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_S3_REGION_NAME
        )
        
        bucket_name = config.AWS_STORAGE_BUCKET_NAME
        print(f"버킷: {bucket_name}")
        print(f"파일 경로: {file_path}")
        
        # 파일 존재 확인
        try:
            response = s3_client.head_object(Bucket=bucket_name, Key=file_path)
            print("✅ 파일이 존재합니다!")
            print(f"   - 파일 크기: {response['ContentLength']} bytes")
            print(f"   - 마지막 수정: {response['LastModified']}")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print("❌ 파일을 찾을 수 없습니다.")
                
                # 비슷한 파일명이 있는지 확인
                print("\n🔍 비슷한 파일명 검색 중...")
                try:
                    response = s3_client.list_objects_v2(
                        Bucket=bucket_name,
                        Prefix=file_path.rsplit('/', 1)[0] if '/' in file_path else '',
                        MaxKeys=10
                    )
                    
                    if 'Contents' in response:
                        print("   발견된 파일들:")
                        for obj in response['Contents']:
                            print(f"   - {obj['Key']}")
                    else:
                        print("   해당 디렉토리에 파일이 없습니다.")
                        
                except Exception as list_error:
                    print(f"   파일 목록 조회 오류: {list_error}")
                
                return False
            else:
                print(f"❌ S3 오류: {e}")
                return False
                
    except Exception as e:
        print(f"❌ 연결 오류: {e}")
        return False

if __name__ == "__main__":
    # 테스트할 파일 경로 (URL에서 디코딩된 경로)
    test_file_path = "상품/개인_신용대출/KB_햇살론뱅크.pdf"
    # S3 경로에 pdf/ 접두사 추가
    s3_file_path = f"pdf/{test_file_path}"
    print(f"원본 경로: {test_file_path}")
    print(f"S3 경로: {s3_file_path}")
    check_s3_file(s3_file_path)
