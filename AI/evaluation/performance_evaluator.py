#!/usr/bin/env python3
"""
RAG 성능 평가 도구
- 문서 검색 성능: MRR, MAP, NDCG, Precision, Recall, F1
- 답변 생성 품질: 정확성, 완전성, 관련성
- 빠른 테스트, 기본 테스트, 종합 평가 통합
- 전체 시스템 성능 분석
"""

# ================================
# 설정 상수 (쉽게 변경 가능)
# ================================

# API 엔드포인트 설정
BASE_URL = "http://localhost:8000/api/v1"
USE_INTENT_ROUTING = True  # True: process_with_intent_routing, False: query_rag
ENDPOINT_OPTIONS = {
    "intent": "/process_with_intent_routing",
    "rag": "/query_rag",
    "langgraph": "/langgraph/langgraph_rag"
}

# 테스트 설정
REQUEST_TIMEOUT = 30  # 요청 타임아웃 (초)
API_DELAY = 1  # API 호출 간 대기 시간 (초)
MAX_DISPLAY_SOURCES = 3  # 표시할 최대 소스 문서 수

# 성능 평가 기준
MEANINGFUL_THRESHOLD = 0.1  # 의미있는 답변 판정 기준 (Precision/Recall)
PERFORMANCE_GRADE_EXCELLENT = 0.8  # 우수 등급 기준
PERFORMANCE_GRADE_GOOD = 0.6  # 양호 등급 기준  
PERFORMANCE_GRADE_FAIR = 0.4  # 보통 등급 기준

# ================================

import requests
import time
import math
import re
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict
import sys
import os

# 프로젝트 루트 경로를 Python path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.test_dataset import dataset, get_dataset_stats
from evaluation.openai_evaluator import OpenAIAnswerEvaluator
from evaluation.result_saver import TestResultSaver

# 동적 엔드포인트 설정
ENDPOINT = "/langgraph" if USE_INTENT_ROUTING else "/query_rag"

class RAGMetrics:
    """RAG 평가 지표 계산 클래스"""
    
    @staticmethod
    def calculate_precision_at_k(retrieved_files: List[str], expected_files: List[str], k: int) -> float:
        """Precision@K 계산"""
        if not retrieved_files or k <= 0:
            return 0.0
        
        retrieved_at_k = retrieved_files[:k]
        # 중복 제거하여 고유한 관련 문서 수 계산
        unique_relevant_retrieved = len(set(retrieved_at_k) & set(expected_files))
        
        return unique_relevant_retrieved / min(k, len(retrieved_at_k))
    
    @staticmethod
    def calculate_recall_at_k(retrieved_files: List[str], expected_files: List[str], k: int) -> float:
        """Recall@K 계산"""
        if not expected_files or k <= 0:
            return 0.0
        
        retrieved_at_k = retrieved_files[:k]
        # 중복 제거하여 고유한 관련 문서 수 계산
        unique_relevant_retrieved = len(set(retrieved_at_k) & set(expected_files))
        
        return unique_relevant_retrieved / len(expected_files)
    
    @staticmethod
    def calculate_f1_at_k(retrieved_files: List[str], expected_files: List[str], k: int) -> float:
        """F1@K 계산"""
        precision = RAGMetrics.calculate_precision_at_k(retrieved_files, expected_files, k)
        recall = RAGMetrics.calculate_recall_at_k(retrieved_files, expected_files, k)
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)
    
    @staticmethod
    def calculate_mrr(retrieved_files: List[str], expected_files: List[str]) -> float:
        """Mean Reciprocal Rank 계산"""
        if not retrieved_files or not expected_files:
            return 0.0
        
        for i, retrieved_file in enumerate(retrieved_files, 1):
            if retrieved_file in expected_files:
                return 1.0 / i
        
        return 0.0
    
    @staticmethod
    def calculate_ap(retrieved_files: List[str], expected_files: List[str]) -> float:
        """Average Precision 계산"""
        if not retrieved_files or not expected_files:
            return 0.0
        
        relevant_retrieved = 0
        precision_sum = 0.0
        
        for i, retrieved_file in enumerate(retrieved_files, 1):
            if retrieved_file in expected_files:
                relevant_retrieved += 1
                precision_at_i = relevant_retrieved / i
                precision_sum += precision_at_i
        
        if relevant_retrieved == 0:
            return 0.0
        
        return precision_sum / len(expected_files)
    
    @staticmethod
    def calculate_ndcg_at_k(retrieved_files: List[str], expected_files: List[str], k: int) -> float:
        """NDCG@K 계산"""
        if not retrieved_files or not expected_files or k <= 0:
            return 0.0
        
        # DCG 계산
        dcg = 0.0
        for i, retrieved_file in enumerate(retrieved_files[:k], 1):
            relevance = 1 if retrieved_file in expected_files else 0
            dcg += relevance / math.log2(i + 1)
        
        # IDCG 계산 (이상적인 순서)
        ideal_relevances = [1] * min(len(expected_files), k) + [0] * max(0, k - len(expected_files))
        idcg = sum(rel / math.log2(i + 2) for i, rel in enumerate(ideal_relevances))
        
        if idcg == 0:
            return 0.0
        
        return dcg / idcg

class AnswerQualityEvaluator:
    """답변 품질 평가 클래스"""
    
    @staticmethod
    def calculate_keyword_overlap(generated_answer: str, expected_answer: str) -> Dict[str, Any]:
        """키워드 겹침 기반 유사도 계산"""
        # 한글 키워드 추출 (2글자 이상)
        generated_keywords = set(re.findall(r'[가-힣]{2,}', generated_answer.lower()))
        expected_keywords = set(re.findall(r'[가-힣]{2,}', expected_answer.lower()))
        
        if not expected_keywords:
            return {"overlap_ratio": 0.0, "matched_keywords": [], "total_expected": 0}
        
        matched_keywords = generated_keywords.intersection(expected_keywords)
        overlap_ratio = len(matched_keywords) / len(expected_keywords)
        
        return {
            "overlap_ratio": round(overlap_ratio, 3),
            "matched_keywords": list(matched_keywords),
            "total_expected": len(expected_keywords),
            "total_generated": len(generated_keywords)
        }
    
    @staticmethod
    def calculate_semantic_similarity(generated_answer: str, expected_answer: str) -> float:
        """의미적 유사도 계산 (간단한 버전)"""
        # 문장 길이 기반 유사도
        gen_len = len(generated_answer.strip())
        exp_len = len(expected_answer.strip())
        
        if gen_len == 0 or exp_len == 0:
            return 0.0
        
        # 길이 유사도
        length_similarity = 1 - abs(gen_len - exp_len) / max(gen_len, exp_len)
        
        # 키워드 유사도
        keyword_result = AnswerQualityEvaluator.calculate_keyword_overlap(generated_answer, expected_answer)
        keyword_similarity = keyword_result["overlap_ratio"]
        
        # 가중 평균
        semantic_similarity = 0.3 * length_similarity + 0.7 * keyword_similarity
        
        return round(semantic_similarity, 3)
    
    @staticmethod
    def calculate_completeness(generated_answer: str, expected_answer: str) -> float:
        """답변 완전성 평가"""
        if not expected_answer.strip():
            return 1.0
        
        # 예상 답변의 주요 구성 요소 추출
        expected_sentences = [s.strip() for s in expected_answer.split('.') if s.strip()]
        
        if not expected_sentences:
            return 1.0
        
        # 생성된 답변에서 각 구성 요소의 존재 여부 확인
        covered_components = 0
        for sentence in expected_sentences:
            keywords = re.findall(r'[가-힣]{2,}', sentence)
            if keywords:
                # 주요 키워드가 생성된 답변에 포함되어 있는지 확인
                main_keyword = keywords[0]  # 첫 번째 키워드를 주요 키워드로 간주
                if main_keyword in generated_answer:
                    covered_components += 1
        
        completeness = covered_components / len(expected_sentences)
        return round(completeness, 3)
    
    @staticmethod
    def calculate_relevance(generated_answer: str, query: str) -> float:
        """질의 관련성 평가"""
        query_keywords = set(re.findall(r'[가-힣]{2,}', query.lower()))
        answer_keywords = set(re.findall(r'[가-힣]{2,}', generated_answer.lower()))
        
        if not query_keywords:
            return 1.0
        
        matched_keywords = query_keywords.intersection(answer_keywords)
        relevance = len(matched_keywords) / len(query_keywords)
        
        return round(relevance, 3)
    
    @staticmethod
    def evaluate_answer_quality(generated_answer: str, expected_answer: str, query: str) -> Dict[str, Any]:
        """종합 답변 품질 평가"""
        keyword_overlap = AnswerQualityEvaluator.calculate_keyword_overlap(generated_answer, expected_answer)
        semantic_similarity = AnswerQualityEvaluator.calculate_semantic_similarity(generated_answer, expected_answer)
        completeness = AnswerQualityEvaluator.calculate_completeness(generated_answer, expected_answer)
        relevance = AnswerQualityEvaluator.calculate_relevance(generated_answer, query)
        
        # 종합 점수 계산 (가중 평균)
        overall_score = (
            0.3 * semantic_similarity +
            0.3 * completeness +
            0.2 * relevance +
            0.2 * keyword_overlap["overlap_ratio"]
        )
        
        return {
            "keyword_overlap": keyword_overlap,
            "semantic_similarity": semantic_similarity,
            "completeness": completeness,
            "relevance": relevance,
            "overall_score": round(overall_score, 3)
        }

class QuickTester:
    """빠른 테스트 클래스"""
    
    def __init__(self, endpoint_type: str = "intent"):
        self.base_url = BASE_URL
        self.results = []
        self.endpoint_type = endpoint_type
        self.endpoint = ENDPOINT_OPTIONS.get(endpoint_type, ENDPOINT_OPTIONS["intent"])
    
    def check_server(self) -> bool:
        """서버 상태 확인"""
        try:
            response = requests.get(f"{self.base_url}/healthcheck", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def run_quick_test(self):
        """빠른 테스트 실행"""
        print("빠른 테스트 시작")
        print(f"사용 엔드포인트: {self.endpoint} ({self.endpoint_type})")
        print("=" * 50)
        
        if not self.check_server():
            print("서버가 실행되지 않았습니다.")
            return
        
        print("서버 연결 확인됨")
        
        # 간단한 테스트 케이스들
        test_cases = [
            "KB 4대연금 신용대출에 대해 알려주세요",
            "대출 금리는 어떻게 되나요?",
            "신용대출 조건이 뭔가요?",
            "담보대출과 신용대출의 차이점은?"
        ]
        
        for i, query in enumerate(test_cases, 1):
            print(f"\n테스트 {i}/{len(test_cases)}: {query}")
            print("-" * 30)
            
            start_time = time.time()
            try:
                response = requests.post(
                    f"{self.base_url}{self.endpoint}",
                    json={"prompt": query},
                    timeout=REQUEST_TIMEOUT
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    response_time = round(end_time - start_time, 2)
                    answer = data.get("response", "")
                    sources = data.get("sources", [])
                    
                    print(f"응답 시간: {response_time}초")
                    print(f"소스 문서: {len(sources)}개")
                    print(f"답변: {answer[:100]}...")
                    
                    self.results.append({
                        "query": query,
                        "response_time": response_time,
                        "answer": answer,
                        "sources_count": len(sources),
                        "success": True
                    })
                else:
                    print(f"오류: HTTP {response.status_code}")
                    self.results.append({
                        "query": query,
                        "success": False,
                        "error": f"HTTP {response.status_code}"
                    })
            
            except Exception as e:
                print(f"예외: {e}")
                self.results.append({
                    "query": query,
                    "success": False,
                    "error": str(e)
                })
            
            time.sleep(API_DELAY)
        
        self.print_summary()
    
    def print_summary(self):
        """결과 요약 출력"""
        print(f"\n{'='*50}")
        print("빠른 테스트 결과 요약")
        print(f"{'='*50}")
        
        successful_tests = [r for r in self.results if r.get("success", False)]
        
        if successful_tests:
            avg_response_time = sum(r["response_time"] for r in successful_tests) / len(successful_tests)
            avg_sources = sum(r["sources_count"] for r in successful_tests) / len(successful_tests)
            
            print(f"성공한 테스트: {len(successful_tests)}/{len(self.results)}")
            print(f"평균 응답 시간: {avg_response_time:.2f}초")
            print(f"평균 소스 문서 수: {avg_sources:.1f}개")
        else:
            print("모든 테스트가 실패했습니다.")
        
        failed_tests = [r for r in self.results if not r.get("success", False)]
        if failed_tests:
            print(f"실패한 테스트: {len(failed_tests)}개")
            for test in failed_tests:
                print(f"  - {test['query']}: {test.get('error', 'Unknown error')}")

class BasicTester:
    """기본 테스트 클래스"""
    
    def __init__(self, endpoint_type: str = "intent"):
        self.base_url = BASE_URL
        self.metrics = RAGMetrics()
        self.answer_evaluator = AnswerQualityEvaluator()
        self.results = []
        self.endpoint_type = endpoint_type
        self.endpoint = ENDPOINT_OPTIONS.get(endpoint_type, ENDPOINT_OPTIONS["intent"])
    
    def check_server(self) -> bool:
        """서버 상태 확인"""
        try:
            response = requests.get(f"{self.base_url}/healthcheck", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def run_basic_test(self):
        """기본 테스트 실행"""
        print("기본 테스트 시작")
        print(f"사용 엔드포인트: {self.endpoint} ({self.endpoint_type})")
        print("=" * 50)
        
        if not self.check_server():
            print("서버가 실행되지 않았습니다.")
            return
        
        print("서버 연결 확인됨")
        
        # 기본 테스트 케이스들 (expected_answer와 expected_file 포함)
        test_cases = [
            {
                "id": "basic_001",
                "query": "KB 4대연금 신용대출의 대출 한도는 얼마인가요?",
                "expected_answer": "4대연금(국민연금, 공무원연금, 사학연금, 군인연금) 수령액을 기준으로 대출한도가 결정됩니다.",
                "expected_file": ["KB_4대연금_신용대출.pdf"]
            },
            {
                "id": "basic_002", 
                "query": "중도상환수수료란 무엇인가요?",
                "expected_answer": "중도상환수수료는 대출 기간 중 대출금을 조기상환할 때 부과되는 수수료로, 계약 조건에 따라 부과 기간(보통 최초 실행일부터 최장 3년 등)과 계산 방식이 달라집니다.",
                "expected_file": ["중도상환수수료_변경으로_부담이_줄어들어요.pdf"]
            },
            {
                "id": "basic_003",
                "query": "대출 갈아타기(대환대출)란 무엇인가요?",
                "expected_answer": "대출 갈아타기(대환대출)는 기존 대출을 더 유리한 조건의 대출로 옮기는 서비스로, 모바일로 간편하게 이전 대출을 상환하고 새로운 대출로 전환할 수 있는 제도입니다.",
                "expected_file": ["대출_갈아타기_총정리.pdf"]
            },
            {
                "id": "basic_004",
                "query": "원금균등 상환 방식의 장단점은 무엇인가요?",
                "expected_answer": "원금균등 상환은 매달 동일한 원금을 갚고 이자는 잔존원금에 따라 줄어드는 방식으로 총 이자액이 적지만 초기 상환 부담이 큽니다.",
                "expected_file": ["대출_상환_방식_원금_균등vs.원리금_균등_차이_알아보기.pdf"]
            },
            {
                "id": "basic_005",
                "query": "금리인하요구권은 무엇인가요?",
                "expected_answer": "은행여신약정에서 고객의 신용상태가 객관적으로 개선되었다고 판단되는 경우 고객이 은행에 금리인하를 요구할 수 있는 권리입니다.",
                "expected_file": ["KB_금리인하요구권.pdf"]
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n테스트 {i}/{len(test_cases)}: {test_case['id']}")
            print(f"질의: {test_case['query']}")
            print("-" * 40)
            
            result = self.evaluate_single_query(test_case)
            self.results.append(result)
            
            time.sleep(API_DELAY)
        
        self.print_summary(self.results)
    
    def evaluate_single_query(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """단일 질의 평가"""
        query = test_case["query"]
        expected_answer = test_case["expected_answer"]
        expected_files = test_case.get("expected_file", [])
        
        if isinstance(expected_files, str):
            expected_files = [expected_files]
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}{self.endpoint}",
                json={"prompt": query},
                timeout=REQUEST_TIMEOUT
            )
            end_time = time.time()
            
            if response.status_code != 200:
                return {
                    "test_id": test_case["id"],
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
            
            data = response.json()
            generated_answer = data.get("response", "")
            sources = data.get("sources", [])
            
            # 검색된 파일명 추출
            retrieved_files = [source.get("file_name", "") for source in sources]
            
            # === 문서 검색 성능 평가 ===
            retrieval_metrics = {
                "precision_at_3": self.metrics.calculate_precision_at_k(retrieved_files, expected_files, 3),
                "precision_at_5": self.metrics.calculate_precision_at_k(retrieved_files, expected_files, 5),
                "recall_at_3": self.metrics.calculate_recall_at_k(retrieved_files, expected_files, 3),
                "recall_at_5": self.metrics.calculate_recall_at_k(retrieved_files, expected_files, 5),
                "f1_at_3": self.metrics.calculate_f1_at_k(retrieved_files, expected_files, 3),
                "f1_at_5": self.metrics.calculate_f1_at_k(retrieved_files, expected_files, 5),
                "mrr": self.metrics.calculate_mrr(retrieved_files, expected_files),
                "map": self.metrics.calculate_ap(retrieved_files, expected_files),
                "ndcg_at_3": self.metrics.calculate_ndcg_at_k(retrieved_files, expected_files, 3),
                "ndcg_at_5": self.metrics.calculate_ndcg_at_k(retrieved_files, expected_files, 5)
            }
            
            # === 답변 품질 평가 ===
            answer_quality = self.answer_evaluator.evaluate_answer_quality(
                generated_answer, expected_answer, query
            )
            
            # 결과 출력
            response_time = round(end_time - start_time, 2)
            print(f"응답 시간: {response_time}초")
            print(f"검색된 문서: {len(retrieved_files)}개")
            print(f"Precision@3: {retrieval_metrics['precision_at_3']:.3f}")
            print(f"Recall@3: {retrieval_metrics['recall_at_3']:.3f}")
            print(f"F1@3: {retrieval_metrics['f1_at_3']:.3f}")
            print(f"MRR: {retrieval_metrics['mrr']:.3f}")
            print(f"답변 품질: {answer_quality['overall_score']:.3f}")
            print(f"생성된 답변: {generated_answer[:100]}...")
            
            if retrieved_files:
                print(f"검색된 파일: {', '.join(retrieved_files[:3])}")
            
            return {
                "test_id": test_case["id"],
                "query": query,
                "response_time": response_time,
                "generated_answer": generated_answer,
                "retrieval_metrics": retrieval_metrics,
                "answer_quality": answer_quality,
                "retrieved_files": retrieved_files,
                "expected_files": expected_files,
                "success": True
            }
            
        except Exception as e:
            print(f"오류: {e}")
            return {
                "test_id": test_case["id"],
                "success": False,
                "error": str(e)
            }

    def print_summary(self, results: List[Dict]):
        """결과 요약 출력"""
        print(f"\n{'='*60}")
        print("기본 테스트 결과 요약")
        print(f"{'='*60}")
        
        successful_results = [r for r in results if r.get("success", False)]
        
        if not successful_results:
            print("성공한 테스트가 없습니다.")
            return
        
        # 평균 성능 계산
        avg_metrics = {}
        metric_keys = ["precision_at_3", "recall_at_3", "f1_at_3", "mrr", "map", "ndcg_at_3"]
        
        for key in metric_keys:
            values = [r["retrieval_metrics"][key] for r in successful_results if "retrieval_metrics" in r]
            avg_metrics[key] = sum(values) / len(values) if values else 0.0
        
        avg_answer_quality = sum(r["answer_quality"]["overall_score"] for r in successful_results if "answer_quality" in r) / len(successful_results)
        avg_response_time = sum(r["response_time"] for r in successful_results) / len(successful_results)
        
        print(f"성공한 테스트: {len(successful_results)}/{len(results)}")
        print(f"평균 응답 시간: {avg_response_time:.2f}초")
        print()
        print("검색 성능 지표:")
        print(f"  Precision@3: {avg_metrics['precision_at_3']:.3f}")
        print(f"  Recall@3: {avg_metrics['recall_at_3']:.3f}")
        print(f"  F1@3: {avg_metrics['f1_at_3']:.3f}")
        print(f"  MRR: {avg_metrics['mrr']:.3f}")
        print(f"  MAP: {avg_metrics['map']:.3f}")
        print(f"  NDCG@3: {avg_metrics['ndcg_at_3']:.3f}")
        print()
        print(f"평균 답변 품질: {avg_answer_quality:.3f}")
        
        print(f"\n테스트 완료!")

class ComprehensiveRAGEvaluator:
    """종합 RAG 평가 시스템"""
    
    def __init__(self, endpoint_type: str = "intent", use_openai_eval: bool = True):
        self.base_url = BASE_URL
        self.metrics = RAGMetrics()
        self.answer_evaluator = AnswerQualityEvaluator()
        self.results = []
        self.endpoint_type = endpoint_type
        self.endpoint = ENDPOINT_OPTIONS.get(endpoint_type, ENDPOINT_OPTIONS["intent"])
        self.use_openai_eval = use_openai_eval
        
        # OpenAI 평가기 초기화
        if use_openai_eval:
            try:
                self.openai_evaluator = OpenAIAnswerEvaluator()
                print("OpenAI 평가 시스템이 활성화되었습니다.")
            except Exception as e:
                print(f"OpenAI 평가 시스템 초기화 실패: {e}")
                print("기본 평가 방식으로 전환합니다.")
                self.use_openai_eval = False
                self.openai_evaluator = None
        else:
            self.openai_evaluator = None
        
        # 결과 저장기 초기화
        self.result_saver = TestResultSaver()
    
    def check_server(self) -> bool:
        """서버 상태 확인"""
        try:
            response = requests.get(f"{self.base_url}/healthcheck", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def evaluate_single_query(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """단일 질의에 대한 종합 평가"""
        test_id = test_case.get("id", "unknown")
        query = test_case["query"]
        expected_answer = test_case["expected_answer"]
        expected_files = test_case.get("expected_file", [])
        
        if isinstance(expected_files, str):
            expected_files = [expected_files]
        
        print(f"평가 중: {test_id}")
        print(f"질의: {query}")
        
        try:
            # RAG 시스템에 질의
            response = requests.post(
                f"{self.base_url}{self.endpoint}",
                json={"prompt": query},
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code != 200:
                return {
                    "test_id": test_id,
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
            
            data = response.json()
            generated_answer = data.get("response", "")
            sources = data.get("sources", [])
            
            # 검색된 파일명 추출
            retrieved_files = [source.get("file_name", "") for source in sources]
            
            # === 문서 검색 성능 평가 ===
            retrieval_metrics = {
                "precision_at_3": self.metrics.calculate_precision_at_k(retrieved_files, expected_files, 3),
                "precision_at_5": self.metrics.calculate_precision_at_k(retrieved_files, expected_files, 5),
                "recall_at_3": self.metrics.calculate_recall_at_k(retrieved_files, expected_files, 3),
                "recall_at_5": self.metrics.calculate_recall_at_k(retrieved_files, expected_files, 5),
                "f1_at_3": self.metrics.calculate_f1_at_k(retrieved_files, expected_files, 3),
                "f1_at_5": self.metrics.calculate_f1_at_k(retrieved_files, expected_files, 5),
                "mrr": self.metrics.calculate_mrr(retrieved_files, expected_files),
                "map": self.metrics.calculate_ap(retrieved_files, expected_files),
                "ndcg_at_3": self.metrics.calculate_ndcg_at_k(retrieved_files, expected_files, 3),
                "ndcg_at_5": self.metrics.calculate_ndcg_at_k(retrieved_files, expected_files, 5)
            }
            
            # === 답변 품질 평가 ===
            if self.use_openai_eval and self.openai_evaluator:
                # OpenAI 평가 사용
                openai_evaluation = self.openai_evaluator.evaluate_answer(
                    query, expected_answer, generated_answer
                )
                answer_quality = {
                    "overall_score": sum(openai_evaluation["scores"].values()) / 4,  # 평균 점수
                    "openai_rating": openai_evaluation["overall_rating"],
                    "openai_scores": openai_evaluation["scores"],
                    "openai_explanation": openai_evaluation["explanation"]
                }
            else:
                # 기본 평가 사용
                answer_quality = self.answer_evaluator.evaluate_answer_quality(
                    generated_answer, expected_answer, query
                )
            
            # 검색된 문서 상세 정보
            source_details = []
            for i, source in enumerate(sources[:MAX_DISPLAY_SOURCES]):
                source_info = {
                    "file_name": source.get("file_name", "Unknown"),
                    "main_category": source.get("main_category", "Unknown"),
                    "sub_category": source.get("sub_category", "Unknown"),
                    "chunk_index": source.get("chunk_index", "Unknown")
                }
                source_details.append(source_info)
            
            # 결과 출력
            print(f"검색된 문서: {len(retrieved_files)}개")
            print(f"Precision@3: {retrieval_metrics['precision_at_3']:.3f}")
            print(f"Recall@3: {retrieval_metrics['recall_at_3']:.3f}")
            print(f"F1@3: {retrieval_metrics['f1_at_3']:.3f}")
            print(f"MRR: {retrieval_metrics['mrr']:.3f}")
            
            if self.use_openai_eval and self.openai_evaluator:
                print(f"답변 품질: {answer_quality['overall_score']:.3f} ({answer_quality['openai_rating']})")
                print(f"OpenAI 평가: {answer_quality['openai_explanation']}")
            else:
                print(f"답변 품질: {answer_quality['overall_score']:.3f}")
            
            print(f"생성된 답변: {generated_answer[:150]}...")
            
            if source_details:
                print("검색된 문서 상세:")
                for i, detail in enumerate(source_details, 1):
                    print(f"  {i}. {detail['file_name']} ({detail['main_category']}/{detail['sub_category']})")
            
            print("-" * 50)
            
            return {
                "test_id": test_id,
                "query": query,
                "generated_answer": generated_answer,
                "expected_answer": expected_answer,
                "retrieval_metrics": retrieval_metrics,
                "answer_quality": answer_quality,
                "retrieved_files": retrieved_files,
                "expected_files": expected_files,
                "source_details": source_details,
                "success": True
            }
            
        except Exception as e:
            print(f"평가 실패: {e}")
            return {
                "test_id": test_id,
                "success": False,
                "error": str(e)
            }
    
    def run_comprehensive_evaluation(self, test_cases: List[Dict[str, Any]] = None, category_filter: str = None, difficulty_filter: str = None):
        """종합 평가 실행"""
        print("종합 RAG 성능 평가 시작")
        print("=" * 60)
        
        if not self.check_server():
            print("서버가 실행되지 않았습니다.")
            print("서버를 시작한 후 다시 시도해주세요: python run_server.py")
            return
        
        print("서버 연결 확인됨")
        
        # 테스트 케이스 설정
        if test_cases is None:
            test_cases = dataset  # enhanced_rag_test_dataset.py의 데이터셋 사용
        
        # 필터 적용
        if category_filter:
            test_cases = [case for case in test_cases if case.get("category") == category_filter]
            print(f"카테고리 필터 적용: {category_filter}")
            self._category_filter = category_filter
        else:
            self._category_filter = None
        
        if difficulty_filter:
            test_cases = [case for case in test_cases if case.get("difficulty") == difficulty_filter]
            print(f"난이도 필터 적용: {difficulty_filter}")
            self._difficulty_filter = difficulty_filter
        else:
            self._difficulty_filter = None
        
        print(f"총 {len(test_cases)}개 테스트 케이스 평가 시작")
        print(f"사용 엔드포인트: {self.endpoint} ({self.endpoint_type})")
        print("-" * 60)
        
        # 각 테스트 케이스 평가
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n테스트 {i}/{len(test_cases)} - {test_case.get('id', 'unknown')}")
            result = self.evaluate_single_query(test_case)
            self.results.append(result)
            
            # API 호출 간 대기
            if i < len(test_cases):
                time.sleep(API_DELAY)
        
        # 종합 결과 분석
        self.analyze_comprehensive_results()
    
    def analyze_comprehensive_results(self):
        """종합 결과 분석 및 출력"""
        print(f"\n{'='*80}")
        print("종합 RAG 성능 평가 결과")
        print(f"{'='*80}")
        
        successful_results = [r for r in self.results if r.get("success", False)]
        
        if not successful_results:
            print("성공한 평가가 없습니다.")
            return
        
        total_tests = len(self.results)
        successful_tests = len(successful_results)
        
        print(f"전체 통계:")
        print(f"  성공한 테스트: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
        
        # === 검색 성능 평균 계산 ===
        retrieval_metrics_avg = {}
        metric_keys = [
            "precision_at_3", "precision_at_5", "recall_at_3", "recall_at_5",
            "f1_at_3", "f1_at_5", "mrr", "map", "ndcg_at_3", "ndcg_at_5"
        ]
        
        for key in metric_keys:
            values = [r["retrieval_metrics"][key] for r in successful_results if "retrieval_metrics" in r]
            retrieval_metrics_avg[key] = sum(values) / len(values) if values else 0.0
        
        # === 답변 품질 평균 계산 ===
        answer_quality_keys = ["semantic_similarity", "completeness", "relevance", "overall_score"]
        answer_quality_avg = {}
        
        for key in answer_quality_keys:
            values = [r["answer_quality"][key] for r in successful_results if "answer_quality" in r]
            answer_quality_avg[key] = sum(values) / len(values) if values else 0.0
        
        # === 결과 출력 ===
        print(f"\n문서 검색 성능:")
        print(f"  Precision@3: {retrieval_metrics_avg['precision_at_3']:.3f}")
        print(f"  Precision@5: {retrieval_metrics_avg['precision_at_5']:.3f}")
        print(f"  Recall@3: {retrieval_metrics_avg['recall_at_3']:.3f}")
        print(f"  Recall@5: {retrieval_metrics_avg['recall_at_5']:.3f}")
        print(f"  F1@3: {retrieval_metrics_avg['f1_at_3']:.3f}")
        print(f"  F1@5: {retrieval_metrics_avg['f1_at_5']:.3f}")
        print(f"  MRR: {retrieval_metrics_avg['mrr']:.3f}")
        print(f"  MAP: {retrieval_metrics_avg['map']:.3f}")
        print(f"  NDCG@3: {retrieval_metrics_avg['ndcg_at_3']:.3f}")
        print(f"  NDCG@5: {retrieval_metrics_avg['ndcg_at_5']:.3f}")
        
        print(f"\n답변 생성 품질:")
        print(f"  의미적 유사도: {answer_quality_avg['semantic_similarity']:.3f}")
        print(f"  완전성: {answer_quality_avg['completeness']:.3f}")
        print(f"  관련성: {answer_quality_avg['relevance']:.3f}")
        print(f"  종합 점수: {answer_quality_avg['overall_score']:.3f}")
        
        # === 성능 등급 평가 ===
        overall_performance = (
            retrieval_metrics_avg['f1_at_3'] * 0.4 +
            retrieval_metrics_avg['mrr'] * 0.3 +
            answer_quality_avg['overall_score'] * 0.3
        )
        
        print(f"\n종합 성능 등급:")
        print(f"  종합 점수: {overall_performance:.3f}")
        
        if overall_performance >= PERFORMANCE_GRADE_EXCELLENT:
            grade = "우수 (Excellent)"
            recommendation = "현재 성능이 매우 우수합니다. 이 수준을 유지하세요."
        elif overall_performance >= PERFORMANCE_GRADE_GOOD:
            grade = "양호 (Good)"
            recommendation = "좋은 성능입니다. 세부적인 튜닝으로 더 개선할 수 있습니다."
        elif overall_performance >= PERFORMANCE_GRADE_FAIR:
            grade = "보통 (Fair)"
            recommendation = "기본적인 성능은 확보되었으나 개선이 필요합니다."
        else:
            grade = "개선 필요 (Needs Improvement)"
            recommendation = "성능 개선이 시급합니다. 검색 알고리즘과 답변 생성 로직을 점검하세요."
        
        print(f"  등급: {grade}")
        print(f"  권장사항: {recommendation}")
        
        # === 상세 분석 ===
        print(f"\n상세 분석:")
        
        # 검색 성능 분석
        if retrieval_metrics_avg['precision_at_3'] < MEANINGFUL_THRESHOLD:
            print("  경고: 검색 정확도가 낮습니다. 임베딩 모델이나 검색 알고리즘을 개선하세요.")
        
        if retrieval_metrics_avg['recall_at_3'] < MEANINGFUL_THRESHOLD:
            print("  경고: 검색 재현율이 낮습니다. 검색 범위를 확대하거나 쿼리 확장을 고려하세요.")
        
        # 답변 품질 분석
        if answer_quality_avg['completeness'] < MEANINGFUL_THRESHOLD:
            print("  경고: 답변 완전성이 낮습니다. 더 많은 컨텍스트를 제공하거나 답변 생성 프롬프트를 개선하세요.")
        
        if answer_quality_avg['relevance'] < MEANINGFUL_THRESHOLD:
            print("  경고: 답변 관련성이 낮습니다. 질의 이해 능력을 향상시키세요.")
        
        print(f"\n평가 완료! 총 {successful_tests}개 테스트 케이스를 성공적으로 평가했습니다.")
        
        # === 결과 저장 ===
        try:
            # 저장할 결과 데이터 구성
            save_results = {
                "test_results": self.results,
                "summary": {
                    "total_tests": total_tests,
                    "successful_tests": successful_tests,
                    "retrieval_metrics_avg": retrieval_metrics_avg,
                    "answer_quality_avg": answer_quality_avg,
                    "overall_performance": overall_performance,
                    "grade": grade,
                    "recommendation": recommendation
                }
            }
            
            # 테스트 유형 결정
            test_type = "전체테스트"
            if hasattr(self, '_category_filter') and self._category_filter:
                test_type = f"카테고리테스트_{self._category_filter}"
            elif hasattr(self, '_difficulty_filter') and self._difficulty_filter:
                test_type = f"난이도테스트_{self._difficulty_filter}"
            
            # 결과 저장
            saved_file = self.result_saver.save_results(
                test_name="performance_evaluator",
                endpoint=self.endpoint_type,
                test_type=test_type,
                results=save_results,
                metadata={
                    "use_openai_eval": self.use_openai_eval,
                    "total_cases": len(self.results),
                    "successful_cases": successful_tests
                }
            )
            
            print(f"\n결과가 저장되었습니다: {saved_file}")
            
        except Exception as e:
            print(f"\n결과 저장 중 오류 발생: {e}")

def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RAG 시스템 성능 평가 도구")
    parser.add_argument("--quick-test", action="store_true", help="빠른 테스트 실행 (langgraph 엔드포인트)")
    parser.add_argument("--endpoint", choices=["intent", "rag", "langgraph"], default="langgraph", help="사용할 엔드포인트")
    args = parser.parse_args()
    
    print("RAG 시스템 성능 평가 도구")
    print("=" * 50)
    
    # --quick-test 옵션이 있으면 빠른 테스트 실행
    if args.quick_test:
        print(f"빠른 테스트 실행 (엔드포인트: {args.endpoint})")
        tester = QuickTester(args.endpoint)
        tester.run_quick_test()
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
    print("1. 빠른 테스트 (4개 기본 케이스)")
    print("2. 기본 테스트 (5개 상세 케이스)")
    print("3. 전체 종합 평가 (120개 케이스)")
    print("4. 카테고리별 평가")
    print("5. 난이도별 평가")
    print("6. 빠른 질의 테스트 (직접 입력)")
    print("=" * 50)
    
    try:
        choice = input("테스트 유형 선택 (1-6): ").strip()
        
        if choice == "1":
            tester = QuickTester(endpoint_type)
            tester.run_quick_test()
            
        elif choice == "2":
            tester = BasicTester(endpoint_type)
            tester.run_basic_test()
            
        elif choice == "3":
            # 전체 데이터셋 평가
            stats = get_dataset_stats()
            print(f"\n테스트 데이터셋 정보:")
            print(f"  총 테스트 케이스: {stats['total_cases']}개")
            print(f"  카테고리별 분포: {stats['category_distribution']}")
            print(f"  난이도별 분포: {stats['difficulty_distribution']}")
            print()
            
            # OpenAI 평가 사용 여부 선택
            use_openai = input("OpenAI 평가를 사용하시겠습니까? (y/n, 기본값: y): ").strip().lower()
            use_openai_eval = use_openai != 'n'
            
            evaluator = ComprehensiveRAGEvaluator(endpoint_type, use_openai_eval)
            evaluator.run_comprehensive_evaluation()
            
        elif choice == "4":
            # 카테고리별 평가
            stats = get_dataset_stats()
            print(f"\n사용 가능한 카테고리:")
            categories = list(stats['category_distribution'].keys())
            for i, cat in enumerate(categories, 1):
                count = stats['category_distribution'][cat]
                print(f"  {i}. {cat} ({count}개)")
            
            cat_choice = input(f"카테고리를 선택하세요 (1-{len(categories)}): ").strip()
            try:
                cat_idx = int(cat_choice) - 1
                if 0 <= cat_idx < len(categories):
                    selected_category = categories[cat_idx]
                    print(f"\n선택된 카테고리: {selected_category}")
                    
                    # OpenAI 평가 사용 여부 선택
                    use_openai = input("OpenAI 평가를 사용하시겠습니까? (y/n, 기본값: y): ").strip().lower()
                    use_openai_eval = use_openai != 'n'
                    
                    evaluator = ComprehensiveRAGEvaluator(endpoint_type, use_openai_eval)
                    evaluator.run_comprehensive_evaluation(category_filter=selected_category)
                else:
                    print("잘못된 선택입니다.")
            except ValueError:
                print("숫자를 입력해주세요.")
                
        elif choice == "5":
            # 난이도별 평가
            stats = get_dataset_stats()
            print(f"\n사용 가능한 난이도:")
            difficulties = list(stats['difficulty_distribution'].keys())
            for i, diff in enumerate(difficulties, 1):
                count = stats['difficulty_distribution'][diff]
                print(f"  {i}. {diff} ({count}개)")
            
            diff_choice = input(f"난이도를 선택하세요 (1-{len(difficulties)}): ").strip()
            try:
                diff_idx = int(diff_choice) - 1
                if 0 <= diff_idx < len(difficulties):
                    selected_difficulty = difficulties[diff_idx]
                    print(f"\n선택된 난이도: {selected_difficulty}")
                    
                    # OpenAI 평가 사용 여부 선택
                    use_openai = input("OpenAI 평가를 사용하시겠습니까? (y/n, 기본값: y): ").strip().lower()
                    use_openai_eval = use_openai != 'n'
                    
                    evaluator = ComprehensiveRAGEvaluator(endpoint_type, use_openai_eval)
                    evaluator.run_comprehensive_evaluation(difficulty_filter=selected_difficulty)
                else:
                    print("잘못된 선택입니다.")
            except ValueError:
                print("숫자를 입력해주세요.")
                
        elif choice == "6":
            # 직접 질의 테스트
            query = input("테스트할 질문을 입력하세요: ").strip()
            if query:
                print(f"\n질의: {query}")
                print("-" * 30)
                
                try:
                    endpoint = ENDPOINT_OPTIONS.get(endpoint_type, ENDPOINT_OPTIONS["intent"])
                    print(f"사용 엔드포인트: {endpoint} ({endpoint_type})")
                    
                    response = requests.post(
                        f"{BASE_URL}{endpoint}",
                        json={"prompt": query},
                        timeout=REQUEST_TIMEOUT
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("response", "")
                        sources = data.get("sources", [])
                        
                        print(f"답변: {answer}")
                        print(f"소스 문서: {len(sources)}개")
                        
                        if sources:
                            print("검색된 문서:")
                            for i, source in enumerate(sources[:3], 1):
                                file_name = source.get("file_name", "Unknown")
                                main_category = source.get("main_category", "Unknown")
                                print(f"  {i}. {file_name} ({main_category})")
                    else:
                        print(f"오류: HTTP {response.status_code}")
                        
                except Exception as e:
                    print(f"요청 실패: {e}")
            else:
                print("질문이 입력되지 않았습니다.")
        
        else:
            print("잘못된 선택입니다. 1-6 중에서 선택해주세요.")
            
    except KeyboardInterrupt:
        print("\n\n사용자가 테스트를 중단했습니다.")
    except Exception as e:
        print(f"\n예상치 못한 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()
