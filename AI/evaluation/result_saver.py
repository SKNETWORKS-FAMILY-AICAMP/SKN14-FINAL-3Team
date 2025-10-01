#!/usr/bin/env python3
"""
테스트 결과를 JSON으로 저장하는 시스템
- 테스트이름_엔드포인트_테스트유형_시간.json 형식으로 저장
- evaluation/test_results/ 폴더에 저장
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

class TestResultSaver:
    def __init__(self, base_dir: str = "evaluation/test_results"):
        """결과 저장기 초기화"""
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_filename(self, test_name: str, endpoint: str, test_type: str) -> str:
        """
        파일명 생성
        
        Args:
            test_name: 테스트 이름 (예: "performance_evaluator", "pipeline_tester")
            endpoint: 엔드포인트 (예: "query_rag", "process_with_intent_routing")
            test_type: 테스트 유형 (예: "빠른테스트", "전체테스트", "카테고리테스트")
            
        Returns:
            생성된 파일명
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{test_name}_{endpoint}_{test_type}_{timestamp}.json"
        return filename
    
    def save_results(self, 
                    test_name: str, 
                    endpoint: str, 
                    test_type: str,
                    results: Dict[str, Any],
                    metadata: Dict[str, Any] = None) -> str:
        """
        테스트 결과를 JSON 파일로 저장
        
        Args:
            test_name: 테스트 이름
            endpoint: 엔드포인트
            test_type: 테스트 유형
            results: 테스트 결과 데이터
            metadata: 추가 메타데이터
            
        Returns:
            저장된 파일 경로
        """
        filename = self.generate_filename(test_name, endpoint, test_type)
        filepath = self.base_dir / filename
        
        # 저장할 데이터 구성
        save_data = {
            "metadata": {
                "test_name": test_name,
                "endpoint": endpoint,
                "test_type": test_type,
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(results.get("test_results", [])),
                **(metadata or {})
            },
            "results": results
        }
        
        # JSON 파일로 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        print(f"테스트 결과가 저장되었습니다: {filepath}")
        return str(filepath)
    
    def load_results(self, filepath: str) -> Dict[str, Any]:
        """
        저장된 결과 파일을 로드
        
        Args:
            filepath: 파일 경로
            
        Returns:
            로드된 데이터
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_saved_results(self) -> List[Dict[str, Any]]:
        """
        저장된 모든 결과 파일 목록 반환
        
        Returns:
            결과 파일 정보 리스트
        """
        results = []
        for filepath in self.base_dir.glob("*.json"):
            try:
                data = self.load_results(str(filepath))
                results.append({
                    "filepath": str(filepath),
                    "filename": filepath.name,
                    "metadata": data.get("metadata", {}),
                    "file_size": filepath.stat().st_size,
                    "modified_time": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
                })
            except Exception as e:
                print(f"파일 로드 실패 {filepath}: {e}")
        
        # 최신 순으로 정렬
        results.sort(key=lambda x: x["modified_time"], reverse=True)
        return results
    
    def get_summary_stats(self, filepath: str) -> Dict[str, Any]:
        """
        결과 파일의 요약 통계 반환
        
        Args:
            filepath: 파일 경로
            
        Returns:
            요약 통계
        """
        data = self.load_results(filepath)
        results = data.get("results", {})
        
        # 기본 통계
        total_tests = len(results.get("test_results", []))
        
        # 답변 품질 통계
        quality_stats = {"good": 0, "normal": 0, "bad": 0}
        avg_scores = {"accuracy": 0, "completeness": 0, "relevance": 0, "usefulness": 0}
        
        for test_result in results.get("test_results", []):
            evaluation = test_result.get("evaluation", {})
            if "overall_rating" in evaluation:
                quality_stats[evaluation["overall_rating"]] += 1
            
            scores = evaluation.get("scores", {})
            for key in avg_scores:
                if key in scores:
                    avg_scores[key] += scores[key]
        
        # 평균 계산
        if total_tests > 0:
            for key in avg_scores:
                avg_scores[key] /= total_tests
        
        return {
            "total_tests": total_tests,
            "quality_distribution": quality_stats,
            "average_scores": avg_scores,
            "metadata": data.get("metadata", {})
        }

# 테스트용 실행
if __name__ == "__main__":
    saver = TestResultSaver()
    
    # 테스트 데이터
    test_results = {
        "test_results": [
            {
                "id": "test_001",
                "query": "KB 4대연금 신용대출의 대출한도는 얼마인가요?",
                "expected_answer": "4대연금 수령액을 기준으로 대출한도가 결정됩니다.",
                "actual_answer": "4대연금 수령액을 기준으로 대출한도가 결정되며, 개인의 연금 수령액에 따라 차등 적용됩니다.",
                "evaluation": {
                    "overall_rating": "good",
                    "scores": {"accuracy": 0.9, "completeness": 0.8, "relevance": 0.9, "usefulness": 0.8},
                    "explanation": "정확하고 유용한 답변입니다."
                }
            }
        ],
        "summary": {
            "total_tests": 1,
            "average_quality": "good"
        }
    }
    
    # 결과 저장
    filepath = saver.save_results(
        test_name="performance_evaluator",
        endpoint="query_rag", 
        test_type="빠른테스트",
        results=test_results,
        metadata={"model": "gpt-3.5-turbo", "temperature": 0.1}
    )
    
    # 저장된 결과 확인
    print(f"\n저장된 파일: {filepath}")
    
    # 요약 통계
    stats = saver.get_summary_stats(filepath)
    print(f"\n요약 통계:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
