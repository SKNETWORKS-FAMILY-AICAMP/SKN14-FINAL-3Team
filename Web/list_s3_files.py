"""
S3 버킷의 모든 파일 목록을 확인하는 스크립트
"""

import config
import boto3
from botocore.exceptions import ClientError

def list_s3_files():
    """S3 버킷의 모든 파일 목록 조회"""
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
        print("=" * 50)
        
        # 모든 파일 목록 조회
        paginator = s3_client.get_paginator('list_objects_v2')
        page_count = 0
        
        for page in paginator.paginate(Bucket=bucket_name):
            page_count += 1
            print(f"\n📄 페이지 {page_count}:")
            
            if 'Contents' in page:
                for obj in page['Contents']:
                    print(f"   - {obj['Key']} ({obj['Size']} bytes)")
            else:
                print("   (파일 없음)")
                
        print(f"\n총 {page_count} 페이지 조회 완료")
        
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    list_s3_files()
