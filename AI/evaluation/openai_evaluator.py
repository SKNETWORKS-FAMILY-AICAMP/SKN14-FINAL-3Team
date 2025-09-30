#!/usr/bin/env python3
"""
OpenAI를 이용한 답변 품질 평가 시스템
- Good/Normal/Bad 3단계 평가
- 답변의 정확성, 완성도, 관련성 평가
"""
import openai
import json
from typing import Dict, List, Any
from datetime import datetime
import os
import sys

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class OpenAIAnswerEvaluator:
    def __init__(self, api_key: str = None):
        """OpenAI 평가기 초기화"""
        if api_key:
            openai.api_key = api_key
        else:
            try:
                # config.py에서 MODEL_KEY 가져오기
                from src.config import MODEL_KEY
                openai.api_key = MODEL_KEY
            except ImportError:
                # config를 사용할 수 없으면 환경변수에서 직접 가져오기
                openai.api_key = os.getenv('MODEL_KEY') or os.getenv('OPENAI_API_KEY')
        
        if not openai.api_key:
            raise ValueError("OpenAI API 키가 필요합니다. config.py의 MODEL_KEY 또는 환경변수 MODEL_KEY/OPENAI_API_KEY를 설정하거나 api_key 파라미터를 제공하세요.")
    
    def evaluate_answer(self, query: str, expected_answer: str, actual_answer: str) -> Dict[str, Any]:
        """
        답변 품질을 평가합니다.
        
        Args:
            query: 사용자 질문
            expected_answer: 예상 답변
            actual_answer: 실제 생성된 답변
            
        Returns:
            평가 결과 딕셔너리
        """
        evaluation_prompt = f"""
            다음은 KB금융 RAG 시스템의 답변 평가입니다.

            사용자 질문: {query}

            예상 답변: {expected_answer}

            실제 생성된 답변: {actual_answer}

            다음 기준으로 답변 품질을 평가해주세요:

            1. 정확성 (Accuracy): 답변이 사실적으로 정확한가?
            2. 완성도 (Completeness): 질문에 대한 답변이 충분히 완성되었는가?
            3. 관련성 (Relevance): 답변이 질문과 관련성이 있는가?
            4. 유용성 (Usefulness): 사용자에게 도움이 되는 답변인가?

            평가 결과를 다음 JSON 형식으로만 응답해주세요:
            {{
                "overall_rating": "good|normal|bad",
                "accuracy_score": 1-10,
                "completeness_score": 1-10,
                "relevance_score": 1-10,
                "usefulness_score": 1-10,
                "explanation": "평가 근거를 간단히 설명"
            }}
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "당신은 KB금융 RAG 시스템의 답변 품질을 평가하는 전문가입니다. 객관적이고 정확한 평가를 해주세요."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # JSON 응답 파싱
            evaluation_text = response.choices[0].message.content.strip()
            
            # JSON 부분만 추출 (```json ... ``` 형태일 수 있음)
            if "```json" in evaluation_text:
                evaluation_text = evaluation_text.split("```json")[1].split("```")[0].strip()
            elif "```" in evaluation_text:
                evaluation_text = evaluation_text.split("```")[1].split("```")[0].strip()
            
            evaluation_result = json.loads(evaluation_text)
            
            # 점수 정규화 (1-10 -> 0-1)
            normalized_scores = {
                "accuracy": evaluation_result["accuracy_score"] / 10,
                "completeness": evaluation_result["completeness_score"] / 10,
                "relevance": evaluation_result["relevance_score"] / 10,
                "usefulness": evaluation_result["usefulness_score"] / 10
            }
            
            return {
                "overall_rating": evaluation_result["overall_rating"],
                "scores": normalized_scores,
                "explanation": evaluation_result["explanation"],
                "raw_scores": {
                    "accuracy": evaluation_result["accuracy_score"],
                    "completeness": evaluation_result["completeness_score"],
                    "relevance": evaluation_result["relevance_score"],
                    "usefulness": evaluation_result["usefulness_score"]
                }
            }
            
        except Exception as e:
            print(f"OpenAI 평가 중 오류 발생: {e}")
            return {
                "overall_rating": "bad",
                "scores": {"accuracy": 0, "completeness": 0, "relevance": 0, "usefulness": 0},
                "explanation": f"평가 중 오류 발생: {str(e)}",
                "raw_scores": {"accuracy": 0, "completeness": 0, "relevance": 0, "usefulness": 0}
            }
    
    def batch_evaluate(self, evaluations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        여러 답변을 일괄 평가합니다.
        
        Args:
            evaluations: [{"query": str, "expected": str, "actual": str}, ...] 형태의 리스트
            
        Returns:
            평가 결과 리스트
        """
        results = []
        for i, eval_data in enumerate(evaluations):
            print(f"평가 진행 중: {i+1}/{len(evaluations)}")
            result = self.evaluate_answer(
                eval_data["query"],
                eval_data["expected"],
                eval_data["actual"]
            )
            results.append({
                "index": i,
                "query": eval_data["query"],
                "expected_answer": eval_data["expected"],
                "actual_answer": eval_data["actual"],
                "evaluation": result
            })
        return results
    
    def evaluate_answer_quality_only(self, query: str, actual_answer: str) -> Dict[str, Any]:
        """
        정답 없이 답변의 품질만 평가합니다.
        
        Args:
            query: 사용자 질문
            actual_answer: 실제 생성된 답변
            
        Returns:
            평가 결과 딕셔너리
        """
        prompt = f"""
            다음 질문에 대한 답변의 품질을 평가해주세요.

            질문: {query}

            답변: {actual_answer}

            다음 기준으로 평가해주세요:
            1. 정확성 (Accuracy): 답변이 사실적으로 정확한가?
            2. 완성도 (Completeness): 질문에 충분히 답했는가?
            3. 관련성 (Relevance): 질문과 관련된 내용인가?
            4. 명확성 (Clarity): 이해하기 쉽게 설명되었는가?

            각 기준을 1-10점으로 평가하고, 전체적으로 Good/Normal/Bad 중 하나로 평가해주세요.

            응답 형식:
            정확성: X점
            완성도: X점
            관련성: X점
            명확성: X점
            전체 평가: Good/Normal/Bad
            설명: [간단한 설명]
        """

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # 결과 파싱
            lines = result_text.split('\n')
            scores = {}
            overall_rating = "Normal"
            explanation = ""
            
            for line in lines:
                line = line.strip()
                if "정확성:" in line:
                    scores["accuracy"] = self._extract_score(line)
                elif "완성도:" in line:
                    scores["completeness"] = self._extract_score(line)
                elif "관련성:" in line:
                    scores["relevance"] = self._extract_score(line)
                elif "명확성:" in line:
                    scores["clarity"] = self._extract_score(line)
                elif "전체 평가:" in line:
                    overall_rating = self._extract_rating(line)
                elif "설명:" in line:
                    explanation = line.replace("설명:", "").strip()
            
            return {
                "overall_rating": overall_rating,
                "scores": scores,
                "explanation": explanation,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "overall_rating": "Normal",
                "scores": {"accuracy": 5, "completeness": 5, "relevance": 5, "clarity": 5},
                "explanation": f"평가 중 오류 발생: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_score(self, line: str) -> float:
        """점수 추출 헬퍼 메서드"""
        import re
        match = re.search(r'(\d+(?:\.\d+)?)', line)
        if match:
            return float(match.group(1)) / 10.0  # 10점 만점을 1점 만점으로 변환
        return 0.5  # 기본값
    
    def _extract_rating(self, line: str) -> str:
        """평가 등급 추출 헬퍼 메서드"""
        line = line.lower()
        if "good" in line:
            return "Good"
        elif "bad" in line:
            return "Bad"
        else:
            return "Normal"

# 테스트용 실행
if __name__ == "__main__":
    evaluator = OpenAIAnswerEvaluator()
    
    # 테스트 케이스
    test_query = "KB 4대연금 신용대출의 대출한도는 얼마인가요?"
    test_expected = "4대연금(국민연금, 공무원연금, 사학연금, 군인연금) 수령액을 기준으로 대출한도가 결정됩니다."
    test_actual = "4대연금 수령액을 기준으로 대출한도가 결정되며, 개인의 연금 수령액에 따라 차등 적용됩니다."
    
    result = evaluator.evaluate_answer(test_query, test_expected, test_actual)
    print("평가 결과:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
