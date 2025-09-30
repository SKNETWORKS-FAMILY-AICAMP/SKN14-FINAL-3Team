"""
LangGraph Tools
==============
RAG 워크플로우에서 사용하는 도구들
"""

from langchain_core.tools import tool


@tool(parse_docstring=True)
def general_faq(thought: str, query: str):
    """
    Answer general banking FAQ questions.
    
    Args:
        thought: Reasoning for using this tool (1-3 sentences)
        query: User's general banking question
    """

@tool(parse_docstring=True)
def rag_search(thought: str, query: str):
    """
    Search documents using RAG for specific information.
    
    Args:
        thought: Reasoning for using this tool (1-3 sentences)
        query: Search query for document retrieval
    """

@tool(parse_docstring=True)
def product_extraction(thought: str, query: str):
    """
    Extract product name from user query.
    
    Args:
        thought: Reasoning for using this tool (1-3 sentences)
        query: User query to extract product name from
    """

@tool(parse_docstring=True)
def product_search(thought: str, product_name: str, query: str):
    """
    Search for specific product information.
    
    Args:
        thought: Reasoning for using this tool (1-3 sentences)
        product_name: Extracted product name
        query: User's question about the product
    """

@tool(parse_docstring=True)
def session_summary(thought: str, query: str):
    """
    Generate session summary for first conversation turn.
    
    Args:
        thought: Reasoning for using this tool (1-3 sentences)
        query: User's first message to summarize
    """

@tool(parse_docstring=True)
def guardrail_check(thought: str, response: str):
    """
    Check response against guardrails for compliance.
    
    Args:
        thought: Reasoning for using this tool (1-3 sentences)
        response: Generated response to check
    """


@tool(parse_docstring=True)
def intent_classification(thought: str, query: str):
    """
    Classify user intent for routing.
    
    Args:
        thought: Reasoning for using this tool (1-3 sentences)
        query: User query to classify
    """

@tool(parse_docstring=True)
def answer(thought: str):
    """
    Generate final answer when sufficient information is available.
    
    Args:
        thought: Extremely concise reason why ready to answer (3-5 words maximum)
    """
    # FAQ 답변 생성 로직이 필요함
    # 현재는 빈 함수이므로 실제 답변이 생성되지 않음

@tool(parse_docstring=True)
def context_answer(thought: str):
    """
    Generate answer based on previous conversation context.
    
    Args:
        thought: Reasoning for using context-based answer (1-2 sentences)
    """
