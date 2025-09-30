#!/usr/bin/env python3
"""
RAG 파이프라인 테스트 도구
- 다양한 RAG 파이프라인 비교 (LLM, Intent, RAG, LangGraph)
- 응답 시간 및 소스 문서 추적
- 개발 및 디버깅용
"""
import requests
import time
import json
import argparse
from typing import Dict, Any, List
from pathlib import Path
import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:8000/api/v1"

class PipelineTester:
    def __init__(self, endpoint_type: str = "intent"):
        self.base_url = BASE_URL
        self.results = []
        self.endpoint_type = endpoint_type
        self.endpoint_map = {
            "intent": "/process_with_intent_routing",
            "rag": "/query_rag",
            "langgraph": "/langgraph/langgraph_rag"
        }
        # OpenAI 평가기 (지연 초기화)
        self.use_openai_eval = False
        self.openai_evaluator = None

    def enable_openai_eval(self):
        """OpenAI 평가 활성화 (config.py의 MODEL_KEY 사용). 실패 시 비활성화."""
        if self.openai_evaluator is not None:
            self.use_openai_eval = True
            return True
        try:
            print("OpenAI 평가기 초기화 중...")
            from evaluation.openai_evaluator import OpenAIAnswerEvaluator
            print("OpenAIAnswerEvaluator import 성공")
            self.openai_evaluator = OpenAIAnswerEvaluator()
            print("OpenAIAnswerEvaluator 인스턴스 생성 성공")
            self.use_openai_eval = True
            print("OpenAI 평가 시스템이 활성화되었습니다.")
            return True
        except Exception as e:
            print(f"OpenAI 평가 시스템 초기화 실패: {e}")
            import traceback
            print(f"상세 오류: {traceback.format_exc()}")
            self.use_openai_eval = False
            self.openai_evaluator = None
            return False

    def _maybe_eval_with_openai(self, query: str, generated_answer: str) -> dict:
        """OpenAI로 답변 품질 평가. expected_answer가 있으면 비교 평가, 없으면 일반 평가."""
        if not self.use_openai_eval or self.openai_evaluator is None:
            return {}
        
        try:
            # dataset에서 해당 query의 expected_answer 찾기
            expected_answer = None
            try:
                from evaluation.test_dataset import dataset
                matched = next((c for c in dataset if c.get("query") == query), None)
                expected_answer = matched.get("expected_answer") if matched else None
            except Exception as e:
                pass

            if expected_answer:
                # expected_answer가 있으면 비교 평가
                eval_result = self.openai_evaluator.evaluate_answer(
                    query, expected_answer, generated_answer
                )
            else:
                # expected_answer가 없으면 일반 품질 평가
                eval_result = self.openai_evaluator.evaluate_answer_quality_only(
                    query, generated_answer
                )
            
            # 표준화된 형태로 리턴
            return {
                "openai_rating": eval_result.get("overall_rating"),
                "openai_scores": eval_result.get("scores"),
                "openai_explanation": eval_result.get("explanation")
            }
        except Exception as e:
            return {"openai_error": str(e)}
    
    def _print_source_details(self, index: int, source: Dict[str, Any]):
        """소스 문서 상세 정보를 출력하는 헬퍼 메서드"""
        if isinstance(source, dict):
            if 'metadata' in source:
                metadata = source.get("metadata", {})
                page_content = source.get('page_content', '')
            else:
                metadata = source
                page_content = ''
        else:
            metadata = {}
            page_content = ''
        
        file_name = metadata.get('file_name', 'Unknown')
        main_category = metadata.get('main_category', 'Unknown')
        sub_category = metadata.get('sub_category', 'Unknown')
        page_number = metadata.get('page_number', 'Unknown')
        chunk_index = metadata.get('chunk_index', 'Unknown')
        
        print(f"  {index}. 파일명: {file_name}")
        print(f"     카테고리: {main_category}/{sub_category}")
        print(f"     청크: {chunk_index}, 페이지: {page_number}")
        if len(page_content) > 0:
            print(f"     내용: {page_content[:100]}...")

    def check_server(self) -> bool:
        """서버 상태 확인"""
        try:
            response = requests.get(f"{self.base_url}/healthcheck", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def save_results(self, filename: str):
        """결과를 JSON 파일로 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            print(f"결과가 {filename}에 저장되었습니다.")
        except Exception as e:
            print(f"결과 저장 실패: {e}")

    def test_llm_only(self, prompt: str) -> Dict[str, Any]:
        """LLM 전용 테스트"""
        print(f"\nLLM 전용 테스트")
        print(f"질문: {prompt}")

        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/answer_with_llm_only",
                json={"prompt": prompt},
                timeout=300
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                
                result = {
                    "type": "LLM_ONLY",
                    "question": prompt,
                    "response_time": round(end_time - start_time, 2),
                    "status": data.get("status"),
                    "answer": data.get("response", "")
                }
                
                print(f"응답 시간: {result['response_time']}초")
                print(f"답변: {result['answer'][:100]}...")
                print("RAG 없이 LLM만 사용 (빠른 응답)")
                
                return result
            else:
                print(f"오류: {response.status_code}")
                return {"type": "LLM_ONLY", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"예외: {e}")
            return {"type": "LLM_ONLY", "error": str(e)}

    def test_intent_routing(self, prompt: str) -> Dict[str, Any]:
        """Intent 라우팅 테스트 (/process_with_intent_routing)"""
        print(f"\nIntent 라우팅 테스트")
        print(f"질문: {prompt}")
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}{self.endpoint_map['intent']}",
                json={"prompt": prompt},
                timeout=300
            )
            elapsed = round(time.time() - start_time, 2)
            
            if response.status_code == 200:
                result = response.json()
                sources = result.get("sources", [])
                category = result.get("category", "unknown")
                
                print(f"응답 시간: {elapsed}초")
                print(f"분류된 카테고리: {category}")
                print(f"소스 문서: {len(sources)}개")
                print(f"답변: {result.get('response', '')[:200]}...")
                
                if category == "company_products":
                    print("처리 흐름: Intent 분류 → 상품명 추출 → 스마트 검색 (파일명 → 키워드 → 폴더)")
                else:
                    print(f"처리 흐름: Intent 분류 → {category} 카테고리별 검색")
                
                # 소스 문서 상세 정보 출력
                if sources:
                    print("소스 문서 상세:")
                    for i, source in enumerate(sources[:3], 1):
                        self._print_source_details(i, source)
                
                eval_payload = self._maybe_eval_with_openai(prompt, result.get('response', ''))

                return {
                    "type": "INTENT_ROUTING",
                    "response_time": elapsed,
                    "response": result.get("response"),
                    "category": category,
                    "sources": sources,
                    "sources_count": len(sources),
                    **({"openai_eval": eval_payload} if eval_payload else {})
                }
            else:
                print(f"오류: {response.status_code}")
                return {"type": "INTENT_ROUTING", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"예외: {e}")
            return {"type": "INTENT_ROUTING", "error": str(e)}

    def test_rag_pipeline(self, prompt: str) -> Dict[str, Any]:
        """RAG 파이프라인 테스트 (기존 호환성용)"""
        return self.test_intent_routing(prompt)

    def test_basic_rag(self, prompt: str) -> Dict[str, Any]:
        """기본 RAG 테스트 (/query_rag)"""
        print(f"\n기본 RAG 테스트")
        print(f"질문: {prompt}")
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}{self.endpoint_map['rag']}",
                json={"prompt": prompt},
                timeout=300
            )
            elapsed = round(time.time() - start_time, 2)
            
            if response.status_code == 200:
                result = response.json()
                sources = result.get("sources", [])
                
                print(f"응답 시간: {elapsed}초")
                print(f"소스 문서: {len(sources)}개")
                print(f"답변: {result.get('response', '')[:200]}...")
                print("처리 흐름: LLM 기반 상품명 추출 → 키워드 검색 (폴백: 일반 검색)")
                
                # 소스 문서 상세 정보 출력
                if sources:
                    print("소스 문서 상세:")
                    for i, source in enumerate(sources[:3], 1):
                        self._print_source_details(i, source)
                
                eval_payload = self._maybe_eval_with_openai(prompt, result.get('response', ''))

                return {
                    "type": "BASIC_RAG",
                    "response_time": elapsed,
                    "response": result.get("response"),
                    "sources": sources,
                    "sources_count": len(sources),
                    **({"openai_eval": eval_payload} if eval_payload else {})
                }
            else:
                print(f"오류: {response.status_code}")
                return {"type": "BASIC_RAG", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"예외: {e}")
            return {"type": "BASIC_RAG", "error": str(e)}
    
    def test_langgraph_rag(self, prompt: str) -> Dict[str, Any]:
        """LangGraph RAG 테스트"""
        print(f"\nLangGraph RAG 테스트")
        print(f"질문: {prompt}")

        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/langgraph/langgraph_rag",
                json={"prompt": prompt},
                timeout=300
            )
            elapsed = round(time.time() - start_time, 2)
            
            if response.status_code == 200:
                result = response.json()
                sources = result.get("sources", [])
                category = result.get("category", "unknown")
                
                print(f"워크플로우 타입: {result.get('workflow_type', 'langgraph')}")
                print(f"분류된 카테고리: {category}")
                print(f"응답 시간: {elapsed}초")
                print(f"소스 문서: {len(sources)}개")
                print(f"답변: {result.get('response', '')[:200]}...")
                print("처리 흐름: 그래프 기반 노드 실행: classify_intent → search_documents → filter_relevance → generate_response")
                
                # 소스 문서 상세 정보 출력
                if sources:
                    print("소스 문서 상세:")
                    for i, source in enumerate(sources[:3], 1):
                        self._print_source_details(i, source)
                
                eval_payload = self._maybe_eval_with_openai(prompt, result.get('response', ''))

                return {
                    "type": "LANGGRAPH_RAG",
                    "response_time": elapsed,
                    "response": result.get("response"),
                    "category": category,
                    "sources": sources,
                    "sources_count": len(sources),
                    **({"openai_eval": eval_payload} if eval_payload else {})
                }
            else:
                print(f"오류: {response.status_code}")
                return {"type": "LANGGRAPH_RAG", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"예외: {e}")
            return {"type": "LANGGRAPH_RAG", "error": str(e)}
    
    def run_comprehensive_test(self, questions: List[str]):
        """종합 테스트 실행"""
        print(f"RAG 시스템 파이프라인 테스트 시작")
        print(f"사용 엔드포인트: {self.endpoint_map.get(self.endpoint_type)} ({self.endpoint_type})")
        print("=" * 60)
        
        if not self.check_server():
            print("서버가 실행되지 않았습니다. 먼저 서버를 시작해주세요.")
            return
        
        print("서버 연결 확인됨")
        
        for i, question in enumerate(questions, 1):
            print(f"\n테스트 {i}/{len(questions)}")
            print("-" * 40)
            
            # endpoint_type에 따라 적절한 테스트 실행
            if self.endpoint_type == "langgraph":
                result = self.test_langgraph_rag(question)
                test_result = {
                    "question": question,
                    "langgraph_rag": result
                }
            elif self.endpoint_type == "intent":
                result = self.test_intent_routing(question)
                test_result = {
                    "question": question,
                    "intent_routing": result
                }
            elif self.endpoint_type == "rag":
                result = self.test_basic_rag(question)
                test_result = {
                    "question": question,
                    "basic_rag": result
                }
            else:
                # 기본값: intent routing
                result = self.test_intent_routing(question)
                test_result = {
                    "question": question,
                    "intent_routing": result
                }
            
            self.results.append(test_result)
            
            # 잠시 대기
            time.sleep(1)
        
        self.print_summary()
    
    def print_summary(self):
        """테스트 결과 요약"""
        print(f"\n{'='*60}")
        print("RAG 파이프라인 테스트 결과 요약")
        print(f"사용된 엔드포인트: {self.endpoint_type}")
        print(f"{'='*60}")
        
        for i, result in enumerate(self.results, 1):
            print(f"\n질문 {i}: {result['question'][:50]}...")
            print("-" * 40)
            
            # 선택된 엔드포인트에 따라 결과 출력
            if self.endpoint_type == "langgraph" and 'langgraph_rag' in result:
                langgraph = result['langgraph_rag']
                if 'error' not in langgraph:
                    category = langgraph.get('category', 'Unknown')
                    sources_count = langgraph.get('sources_count', 0)
                    print(f"LangGraph RAG: {langgraph['response_time']}초 "
                          f"({category}, 소스: {sources_count}개, 그래프 워크플로우)")
                else:
                    print(f"LangGraph RAG: 오류 - {langgraph['error']}")
            elif self.endpoint_type == "intent" and 'intent_routing' in result:
                intent = result['intent_routing']
                if 'error' not in intent:
                    category = intent.get('category', 'Unknown')
                    sources_count = intent.get('sources_count', 0)
                    print(f"Intent Routing: {intent['response_time']}초 "
                          f"({category}, 소스: {sources_count}개)")
                else:
                    print(f"Intent Routing: 오류 - {intent['error']}")
            elif self.endpoint_type == "rag" and 'basic_rag' in result:
                rag = result['basic_rag']
                if 'error' not in rag:
                    sources_count = rag.get('sources_count', 0)
                    print(f"Basic RAG: {rag['response_time']}초 "
                          f"(소스: {sources_count}개)")
                else:
                    print(f"Basic RAG: 오류 - {rag['error']}")

def main():
    """메인 실행 함수 - 대화형 메뉴"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RAG 시스템 파이프라인 테스트 도구")
    parser.add_argument("--quick-test", action="store_true", help="빠른 테스트 실행 (langgraph 엔드포인트)")
    parser.add_argument("--endpoint", choices=["intent", "rag", "langgraph"], default="langgraph", help="사용할 엔드포인트")
    args = parser.parse_args()
    
    print("RAG 시스템 파이프라인 테스트 도구")
    print("=" * 50)
    
    # --quick-test 옵션이 있으면 빠른 테스트 실행
    if args.quick_test:
        print(f"빠른 테스트 실행 (엔드포인트: {args.endpoint})")
        tester = PipelineTester(args.endpoint)
        
        # 간단한 테스트 케이스들
        test_cases = [
            "KB 4대연금 신용대출에 대해 알려주세요",
            "대출 금리는 어떻게 되나요?",
            "신용대출 조건이 뭔가요?"
        ]
        
        for i, query in enumerate(test_cases, 1):
            print(f"\n테스트 {i}/{len(test_cases)}: {query}")
            print("-" * 30)
            
            if args.endpoint == "langgraph":
                result = tester.test_langgraph_rag(query)
            elif args.endpoint == "intent":
                result = tester.test_intent_routing(query)
            elif args.endpoint == "rag":
                result = tester.test_basic_rag(query)
            
            tester.results.append({
                "question": query,
                "result": result
            })
        
        tester.print_summary()
        return
    
    # 엔드포인트 선택
    print("테스트할 엔드포인트를 선택하세요:")
    print("1. process_with_intent_routing (Intent 라우팅)")
    print("2. query_rag (기본 RAG)")
    print("3. langgraph/langgraph_rag (LangGraph V2)")
    print("=" * 50)
    
    endpoint_choice = input("엔드포인트 선택 (1-3): ").strip()
    
    if endpoint_choice == "1":
        endpoint_type = "intent"
        endpoint_name = "process_with_intent_routing"
    elif endpoint_choice == "2":
        endpoint_type = "rag"
        endpoint_name = "query_rag"
    elif endpoint_choice == "3":
        endpoint_type = "langgraph"
        endpoint_name = "langgraph/langgraph_rag"
    else:
        print("잘못된 선택입니다. 기본값(Intent 라우팅)을 사용합니다.")
        endpoint_type = "intent"
        endpoint_name = "process_with_intent_routing"
    
    print(f"선택된 엔드포인트: {endpoint_name}")
    print("=" * 50)
    
    # 테스트 유형 선택
    print("테스트 유형을 선택하세요:")
    print("1. 기본 테스트 (3개 질문)")
    print("2. 카테고리별 테스트")
    print("3. 난이도별 테스트")
    print("4. 직접 질문 입력")
    print("5. 파일에서 질문 읽기")
    print("6. 대량 테스트 (10개 이상)")
    print("=" * 50)
    
    choice = input("테스트 유형 선택 (1-6): ").strip()
    
    tester = PipelineTester(endpoint_type)
    
    # OpenAI 평가 사용 여부 선택
    print("\nOpenAI 평가를 사용하시겠습니까? (config.py의 MODEL_KEY 사용)")
    print("1. 예 (정답과 대답 비교하여 Good/Normal/Bad 점수 출력)")
    print("2. 아니오 (평가 없이 테스트만 실행)")
    eval_choice = input("선택 (1-2): ").strip()
    
    if eval_choice == "1":
        if tester.enable_openai_eval():
            print("OpenAI 평가가 활성화되었습니다.")
        else:
            print("OpenAI 평가 활성화에 실패했습니다. 평가 없이 진행합니다.")
    else:
        print("평가 없이 테스트를 진행합니다.")
    
    # 서버 상태 확인
    if not tester.check_server():
        print("서버가 실행되지 않았습니다.")
        print("다음 명령어로 서버를 시작해주세요:")
        print("python run_server.py")
        return
    
    # 질문 목록 준비
    questions = []
    
    if choice == "4":
        # 직접 질문 입력
        question = input("테스트할 질문을 입력하세요: ").strip()
        if question:
            questions = [question]
        else:
            print("질문이 입력되지 않았습니다.")
            return
    elif choice == "5":
        # 파일에서 질문 읽기
        file_path = input("질문 파일 경로를 입력하세요: ").strip()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                questions = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"파일을 찾을 수 없습니다: {file_path}")
            return
    else:
        # 데이터셋에서 질문 선택
        from evaluation.test_dataset import dataset
        
        if choice == "2":
            # 카테고리별 테스트
            print("\n카테고리를 선택하세요:")
            categories = list(set(case.get("category", "unknown") for case in dataset))
            for i, cat in enumerate(categories, 1):
                print(f"{i}. {cat}")
            
            cat_choice = input("카테고리 선택 (번호): ").strip()
            try:
                selected_category = categories[int(cat_choice) - 1]
                filtered_cases = [case for case in dataset if case.get("category") == selected_category]
                questions = [case["query"] for case in filtered_cases[:10]]
                print(f"선택된 카테고리: {selected_category}")
                print(f"질문 수: {len(questions)}개")
            except (ValueError, IndexError):
                print("잘못된 선택입니다. 기본 테스트를 실행합니다.")
                questions = [case["query"] for case in dataset[:3]]
                
        elif choice == "3":
            # 난이도별 테스트
            print("\n난이도를 선택하세요:")
            print("1. easy (쉬운)")
            print("2. medium (보통)")
            print("3. hard (어려운)")
            
            diff_choice = input("난이도 선택 (1-3): ").strip()
            difficulty_map = {"1": "easy", "2": "medium", "3": "hard"}
            selected_difficulty = difficulty_map.get(diff_choice, "easy")
            
            filtered_cases = [case for case in dataset if case.get("difficulty") == selected_difficulty]
            questions = [case["query"] for case in filtered_cases[:10]]
            print(f"선택된 난이도: {selected_difficulty}")
            print(f"질문 수: {len(questions)}개")
            
        elif choice == "6":
            # 대량 테스트
            num_questions = input("테스트할 질문 수를 입력하세요 (기본값: 10): ").strip()
            try:
                num = int(num_questions) if num_questions else 10
                questions = [case["query"] for case in dataset[:num]]
                print(f"대량 테스트: {len(questions)}개 질문")
            except ValueError:
                questions = [case["query"] for case in dataset[:10]]
                print("잘못된 입력입니다. 기본값 10개로 설정합니다.")
        else:
            # 기본 테스트 (3개)
            questions = [case["query"] for case in dataset[:3]]
            print(f"기본 테스트: {len(questions)}개 질문")

    if not questions:
        print("테스트할 질문이 없습니다.")
        return
    
    # 테스트 실행
    print(f"{endpoint_type.upper()} 파이프라인 테스트 시작")
    print(f"사용 엔드포인트: {endpoint_name}")
    print("=" * 60)
    
    for i, question in enumerate(questions, 1):
        print(f"\n테스트 {i}/{len(questions)}: {question}")
        print("-" * 40)
        
        if endpoint_type == "intent":
            result = tester.test_intent_routing(question)
        elif endpoint_type == "rag":
            result = tester.test_basic_rag(question)
        elif endpoint_type == "langgraph":
            result = tester.test_langgraph_rag(question)
        else:
            print(f"알 수 없는 엔드포인트 타입: {endpoint_type}")
            continue
        
        tester.results.append({
            "question": question,
            "result": result
        })
        
        # 결과 요약 출력
        if "error" not in result:
            print(f"성공: {result.get('response_time', 0)}초")
            if "sources_count" in result:
                print(f"소스 문서: {result['sources_count']}개")
            if "category" in result:
                print(f"카테고리: {result['category']}")
            
            # OpenAI 평가 결과 출력
            if "openai_eval" in result:
                eval_data = result["openai_eval"]
                if "openai_error" in eval_data:
                    print(f"OpenAI 평가 오류: {eval_data['openai_error']}")
                else:
                    rating = eval_data.get("openai_rating", "Unknown")
                    explanation = eval_data.get("openai_explanation", "")
                    
                    # 점수에 따른 이모지와 색상 (대소문자 구분 없이)
                    rating_lower = rating.lower()
                    if rating_lower == "good":
                        print(f"OpenAI 평가: 🟢 Good - {explanation}")
                    elif rating_lower == "normal":
                        print(f"OpenAI 평가: 🟡 Normal - {explanation}")
                    elif rating_lower == "bad":
                        print(f"OpenAI 평가: 🔴 Bad - {explanation}")
                    else:
                        print(f"OpenAI 평가: {rating} - {explanation}")
        else:
            print(f"오류: {result['error']}")
        
    # 최종 결과 요약
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print(f"총 테스트: {len(tester.results)}개")
    
    successful_tests = [r for r in tester.results if "error" not in r["result"]]
    print(f"성공: {len(successful_tests)}개")
    print(f"실패: {len(tester.results) - len(successful_tests)}개")
    
    if successful_tests:
        avg_time = sum(r["result"].get("response_time", 0) for r in successful_tests) / len(successful_tests)
        print(f"평균 응답 시간: {avg_time:.2f}초")
        
        # OpenAI 평가 통계
        openai_evaluated = [r for r in successful_tests if "openai_eval" in r["result"]]
        if openai_evaluated:
            print(f"\nOpenAI 평가 통계 ({len(openai_evaluated)}개):")
            ratings = [r["result"]["openai_eval"].get("openai_rating", "Unknown").lower() for r in openai_evaluated]
            good_count = ratings.count("good")
            normal_count = ratings.count("normal")
            bad_count = ratings.count("bad")
            
            print(f"🟢 Good: {good_count}개 ({good_count/len(openai_evaluated)*100:.1f}%)")
            print(f"🟡 Normal: {normal_count}개 ({normal_count/len(openai_evaluated)*100:.1f}%)")
            print(f"🔴 Bad: {bad_count}개 ({bad_count/len(openai_evaluated)*100:.1f}%)")

if __name__ == "__main__":
    main()
