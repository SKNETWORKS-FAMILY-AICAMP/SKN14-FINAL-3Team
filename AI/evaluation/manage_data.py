#!/usr/bin/env python3
"""
KB RAG 시스템 데이터 관리 도구
- 데이터 업로드
- 벡터 스토어 관리  
- 시스템 상태 확인
"""
import requests
import time
import json
from pathlib import Path
import argparse

BASE_URL = "http://localhost:8000/api/v1"

class DataManager:
    def __init__(self):
        self.base_url = BASE_URL
    
    def check_server(self):
        """서버 상태 확인"""
        try:
            response = requests.get(f"{self.base_url}/healthcheck", timeout=5)
            if response.status_code == 200:
                print("✅ 서버가 정상적으로 실행 중입니다.")
                return True
            else:
                print(f"❌ 서버 오류: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 서버 연결 실패: {e}")
            return False
    
    def get_vector_store_stats(self):
        """벡터 스토어 통계 조회"""
        try:
            response = requests.get(f"{self.base_url}/vector_store_stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("📊 벡터 스토어 통계")
                print("=" * 30)
                print(f"총 벡터 수: {data.get('total_vectors', 0):,}")
                print(f"인덱스 차원: {data.get('dimension', 0)}")
                print(f"인덱스 사용률: {data.get('index_fullness', 0):.2%}")
                
                namespaces = data.get('namespaces', {})
                if namespaces:
                    print(f"네임스페이스: {len(namespaces)}개")
                    for ns_name, ns_data in namespaces.items():
                        if isinstance(ns_data, dict):
                            vector_count = ns_data.get('vector_count', 0)
                            print(f"  - {ns_name}: {vector_count:,}개 벡터")
                return True
            else:
                print(f"❌ 통계 조회 실패: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 통계 조회 오류: {e}")
            return False
    
    def upload_folder(self, folder_path: str):
        """폴더 업로드"""
        print(f"📁 폴더 업로드 시작: {folder_path}")
        
        try:
            response = requests.post(
                f"{self.base_url}/ingest_folder",
                json={"root_folder_path": folder_path},
                timeout=600  # 10분 타임아웃
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 폴더 업로드 완료")
                print(f"업로드된 청크 수: {data.get('uploaded_chunk_ids_count', 0):,}")
                print(f"처리된 경로: {data.get('resolved_target', folder_path)}")
                return True
            else:
                print(f"❌ 업로드 실패: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"오류 상세: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"응답 내용: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 업로드 오류: {e}")
            return False
    
    def upload_files(self, file_paths: list):
        """개별 파일들 업로드"""
        print(f"📄 파일 업로드 시작: {len(file_paths)}개 파일")
        
        files = []
        try:
            # 파일들을 열어서 준비
            for file_path in file_paths:
                path = Path(file_path)
                if not path.exists():
                    print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
                    continue
                
                files.append(('files', (path.name, open(path, 'rb'), 'application/octet-stream')))
            
            if not files:
                print("❌ 업로드할 유효한 파일이 없습니다.")
                return False
            
            response = requests.post(
                f"{self.base_url}/upload_docs_to_rag",
                files=files,
                timeout=600
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 파일 업로드 완료")
                print(f"업로드된 청크 수: {data.get('uploaded_chunk_ids_count', 0):,}")
                return True
            else:
                print(f"❌ 업로드 실패: HTTP {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"오류 상세: {error_data.get('detail', 'Unknown error')}")
                except:
                    print(f"응답 내용: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 업로드 오류: {e}")
            return False
        finally:
            # 열었던 파일들 닫기
            for file_tuple in files:
                try:
                    file_tuple[1][1].close()  # (name, file_obj, content_type)에서 file_obj 닫기
                except:
                    pass
    
    def delete_all_vectors(self):
        """모든 벡터 삭제"""
        print("⚠️  모든 벡터를 삭제하시겠습니까?")
        confirm = input("삭제하려면 'DELETE'를 입력하세요: ")
        
        if confirm != "DELETE":
            print("❌ 삭제가 취소되었습니다.")
            return False
        
        try:
            response = requests.delete(f"{self.base_url}/delete_all_vectors", timeout=60)
            
            if response.status_code == 200:
                print("✅ 모든 벡터가 삭제되었습니다.")
                return True
            else:
                print(f"❌ 삭제 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 삭제 오류: {e}")
            return False
    
    def delete_vectors_by_condition(self, field: str, value: str):
        """조건부 벡터 삭제"""
        print(f"⚠️  조건 '{field}={value}'에 해당하는 벡터를 삭제하시겠습니까?")
        confirm = input("삭제하려면 'DELETE'를 입력하세요: ")
        
        if confirm != "DELETE":
            print("❌ 삭제가 취소되었습니다.")
            return False
        
        try:
            response = requests.delete(
                f"{self.base_url}/delete_vectors_by_condition",
                json={"field": field, "value": value},
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                deleted_count = data.get("deleted_count", 0)
                print(f"✅ {deleted_count:,}개의 벡터가 삭제되었습니다.")
                return True
            else:
                print(f"❌ 삭제 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 삭제 오류: {e}")
            return False
    
    def quick_test(self):
        """빠른 테스트"""
        print("🧪 빠른 RAG 테스트")
        test_query = "KB 4대연금 신용대출에 대해 알려주세요"
        
        try:
            response = requests.post(
                f"{self.base_url}/query_rag",
                json={"prompt": test_query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", "")
                sources = data.get("sources", [])
                
                print(f"✅ 테스트 성공")
                print(f"질문: {test_query}")
                print(f"답변: {answer[:200]}...")
                print(f"소스 문서: {len(sources)}개")
                
                if sources:
                    print("📄 주요 소스:")
                    for i, source in enumerate(sources[:3], 1):
                        file_name = source.get("file_name", "Unknown")
                        main_category = source.get("main_category", "Unknown")
                        print(f"  {i}. {file_name} ({main_category})")
                
                return True
            else:
                print(f"❌ 테스트 실패: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 테스트 오류: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="KB RAG 시스템 데이터 관리 도구")
    parser.add_argument("--action", "-a", 
                       choices=["status", "stats", "upload-folder", "upload-files", "delete-all", "delete-condition", "test"],
                       required=True,
                       help="수행할 작업")
    parser.add_argument("--path", "-p", help="업로드할 폴더 경로 또는 파일 경로들 (쉼표로 구분)")
    parser.add_argument("--field", help="삭제 조건 필드명")
    parser.add_argument("--value", help="삭제 조건 값")
    
    args = parser.parse_args()
    
    manager = DataManager()
    
    print("🔧 KB RAG 시스템 데이터 관리 도구")
    print("=" * 40)
    
    if args.action == "status":
        manager.check_server()
        
    elif args.action == "stats":
        if manager.check_server():
            manager.get_vector_store_stats()
            
    elif args.action == "upload-folder":
        if not args.path:
            print("❌ --path 옵션으로 폴더 경로를 지정해주세요.")
            return
        
        if manager.check_server():
            manager.upload_folder(args.path)
            
    elif args.action == "upload-files":
        if not args.path:
            print("❌ --path 옵션으로 파일 경로들을 지정해주세요. (쉼표로 구분)")
            return
        
        file_paths = [p.strip() for p in args.path.split(",")]
        
        if manager.check_server():
            manager.upload_files(file_paths)
            
    elif args.action == "delete-all":
        if manager.check_server():
            manager.delete_all_vectors()
            
    elif args.action == "delete-condition":
        if not args.field or not args.value:
            print("❌ --field와 --value 옵션을 모두 지정해주세요.")
            return
        
        if manager.check_server():
            manager.delete_vectors_by_condition(args.field, args.value)
            
    elif args.action == "test":
        if manager.check_server():
            manager.quick_test()

if __name__ == "__main__":
    main()
