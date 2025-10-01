# SKN14-Final-3Team-AI
Repository for SKN14-Final-3Team-AI

FinAissist 실행방법

1. git clone 을 한다 
2. FinAissist 폴더에 들어가 가상환경을 실행시켜준다 
	a) venv 가상환경 (cmd기준)
		생성 : python -m venv .venv
		실행 : .\.venv\Scripts\Activate 또는 .venv\Scripts\activate.bat 
		설치 : pip install -r requirements.txt
	b) conda 가상환경
		생성 : conda create -n fin_aissist_env python=3.10
		실행 : conda activate fin_aissist_env
		설치 : pip install -r requirements.txt
3. root 경로에 .env 파일 생성
4. .env 에 내용을 저장해준다 
	MODEL_KEY="... open api key 작성"
	MODEL_NAME="gpt-4o-mini"
	PINECONE_KEY="... pinecone api key 작성"
	VECTOR_STORE_INDEX_NAME="fin-aissist-db"
	CHUNK_SIZE="1000"
	CHUNK_OVERLAP="100"
5. ASGI 서버(fast api) 실행 : uvicorn src.main:app --reload
6. 연결 체크 : curl http://localhost:8000/healthcheck -X GET
7. 파일 업로드 : curl http://localhost:8000/upload_docs_to_rag -X POST -F "files=@test_doc.csv"
8. http://localhost:8000/docs 여기에 들어가서 확인 가능
