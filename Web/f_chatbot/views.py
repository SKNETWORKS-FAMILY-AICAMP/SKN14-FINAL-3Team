from django.shortcuts import render
from django.http import JsonResponse, FileResponse, Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.db import transaction
from f_user.models import User
from f_chatbot.models import UChatbotHistory, UChatbotSession, ChatbotPDFReference
import json
import logging
import os
from datetime import datetime
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import urllib.parse
import config

from .ai_service import AIService

logger = logging.getLogger(__name__)

# Create your views here.
def chatbot(request) : 
    return render(request, 'chatbot/chatbot.html')

@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """채팅 API 엔드포인트"""
    try:
        # 로그인한 사용자 확인
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({
                'success': False,
                'response': '로그인이 필요합니다.',
                'sources': [],
                'category': 'error'
            })
        
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        chat_id = data.get('chat_id', None)
        
        logger.info(f"User ID: {user_id}, Received chat_id: {chat_id}")
        logger.info(f"Chat ID type: {type(chat_id)}")
        
        # 사용자 정보 조회
        try:
            user = User.objects.get(seq_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'response': '사용자 정보를 찾을 수 없습니다.',
                'sources': [],
                'category': 'error'
            })
        
        # 빈 메시지인 경우 새 채팅 히스토리만 생성
        if not message:
            # 새 채팅 히스토리 생성
            chatbot_history = UChatbotHistory.objects.create(
                user=user,
                title="새 채팅"
            )
            logger.info(f"Created new empty chat history: {chatbot_history.seq_id}")
            
            return JsonResponse({
                'success': True,
                'response': '',
                'sources': [],
                'category': '',
                'chat_history_id': chatbot_history.seq_id
            })
        
        # 채팅 히스토리 조회 또는 생성
        chatbot_history = None
        if chat_id and not (isinstance(chat_id, str) and chat_id.startswith('temp_')):
            try:
                # 기존 채팅 히스토리 조회 (숫자 ID인 경우만)
                chatbot_history = UChatbotHistory.objects.get(
                    user=user, 
                    seq_id=int(chat_id)
                )
                logger.info(f"Found existing chat history: {chat_id}")
            except (UChatbotHistory.DoesNotExist, ValueError):
                logger.info(f"Chat history not found or invalid ID: {chat_id}")
        
        # 새 채팅 히스토리 생성 (chat_id가 없거나 임시 ID이거나 기존 히스토리를 찾을 수 없는 경우)
        if not chatbot_history:
            chatbot_history = UChatbotHistory.objects.create(
                user=user,
                title="새 채팅"
            )
            logger.info(f"Created new chat history: {chatbot_history.seq_id}")
        
        # 기존 대화 히스토리 조회 (AI 서버용)
        existing_messages = UChatbotSession.objects.filter(
            chatbot_history=chatbot_history
        ).order_by('sent_at')[:20]  # 최근 20개만
        
        chat_history = []
        for msg in existing_messages:
            chat_history.append({
                'role': 'user' if msg.content_from == 'USER' else 'assistant',
                'content': msg.content,
                'timestamp': msg.sent_at.isoformat()
            })
        
        # 현재 사용자 메시지를 데이터베이스에 저장
        user_message = UChatbotSession.objects.create(
            chatbot_history=chatbot_history,
            content_from='USER',
            content=message,
            sent_at=datetime.now()
        )
        
        # AI 서비스 호출
        ai_service = AIService()
        result = ai_service.send_message_with_langgraph_rag(message, str(chatbot_history.seq_id), chat_history)
        
        # AI 응답 결과 로깅
        logger.info(f"initial_topic_summary: {result.get('initial_topic_summary', 'NOT_FOUND')}")
        
        # AI 응답을 데이터베이스에 저장
        if result.get('success'):
            ai_message = UChatbotSession.objects.create(
                chatbot_history=chatbot_history,
                content_from='AI',
                content=result.get('response', ''),
                sent_at=datetime.now()
            )
            
            # 채팅 제목 업데이트 (첫 번째 메시지인 경우)
            if chatbot_history.title == "새 채팅" and result.get('initial_topic_summary'):
                chatbot_history.title = result.get('initial_topic_summary', '새 채팅')
                chatbot_history.save()
                logger.info(f"Updated chat title: {chatbot_history.title}")
        
        # 응답에 채팅 히스토리 ID와 AI 메시지 ID 포함
        result['chat_history_id'] = chatbot_history.seq_id
        if result.get('success') and 'ai_message' in locals():
            result['session_msg_id'] = ai_message.seq_id
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'response': '잘못된 요청 형식입니다.',
            'sources': [],
            'category': 'error'
        })
    except Exception as e:
        logger.error(f"채팅 API 오류: {e}")
        return JsonResponse({
            'success': False,
            'response': '서버 오류가 발생했습니다.',
            'sources': [],
            'category': 'error'
        })

@require_http_methods(["GET"])
def health_check(request):
    """AI 서버 연결 상태 확인"""
    ai_service = AIService()
    is_connected = ai_service.check_connection()
    
    return JsonResponse({
        'status': 'healthy' if is_connected else 'unhealthy',
        'connected': is_connected
    })

@require_http_methods(["GET"])
def get_chat_histories(request):
    """사용자별 채팅 히스토리 목록 조회"""
    try:
        # 로그인한 사용자 확인
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({
                'success': False,
                'message': '로그인이 필요합니다.'
            })
        
        # 사용자 정보 조회
        try:
            user = User.objects.get(seq_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '사용자 정보를 찾을 수 없습니다.'
            })
        
        # 사용자의 채팅 히스토리 조회 (메시지가 있는 것만)
        chat_histories = UChatbotHistory.objects.filter(
            user=user
        ).order_by('-updated_at')
        
        # 응답 데이터 구성
        histories = []
        for history in chat_histories:
            # 해당 히스토리의 메시지 개수 확인
            message_count = UChatbotSession.objects.filter(
                chatbot_history=history
            ).count()
            
            # 메시지가 있는 히스토리 또는 "새 채팅" 제목의 빈 채팅 포함
            if message_count > 0 or history.title == "새 채팅":
                # 마지막 메시지 시간 조회
                last_message = UChatbotSession.objects.filter(
                    chatbot_history=history
                ).order_by('-sent_at').first()
                
                histories.append({
                    'id': history.seq_id,
                    'title': history.title,
                    'created_at': history.created_at.isoformat(),
                    'updated_at': history.updated_at.isoformat(),
                    'last_message_time': last_message.sent_at.isoformat() if last_message else history.created_at.isoformat()
                })
            else:
                # 메시지가 없는 일반 채팅 히스토리는 삭제 (새 채팅 제외)
                history.delete()
                logger.info(f"Deleted empty chat history: {history.seq_id}")
        
        return JsonResponse({
            'success': True,
            'histories': histories
        })
        
    except Exception as e:
        logger.error(f"채팅 히스토리 조회 오류: {e}")
        return JsonResponse({
            'success': False,
            'message': '채팅 히스토리를 조회할 수 없습니다.'
        })

@require_http_methods(["GET"])
def get_chat_messages(request, chat_history_id):
    """특정 채팅 히스토리의 메시지 목록 조회"""
    try:
        # 로그인한 사용자 확인
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({
                'success': False,
                'message': '로그인이 필요합니다.'
            })
        
        # 사용자 정보 조회
        try:
            user = User.objects.get(seq_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '사용자 정보를 찾을 수 없습니다.'
            })
        
        # 채팅 히스토리 조회 (사용자 소유 확인)
        try:
            chat_history = UChatbotHistory.objects.get(
                seq_id=chat_history_id,
                user=user
            )
        except UChatbotHistory.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '채팅 히스토리를 찾을 수 없습니다.'
            })
        
        # 메시지 목록 조회
        messages = UChatbotSession.objects.filter(
            chatbot_history=chat_history
        ).order_by('sent_at')
        
        # 응답 데이터 구성
        message_list = []
        for message in messages:
            message_list.append({
                'id': message.seq_id,
                'content': message.content,
                'from': message.content_from,
                'sent_at': message.sent_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'chat_history': {
                'id': chat_history.seq_id,
                'title': chat_history.title,
                'created_at': chat_history.created_at.isoformat(),
                'updated_at': chat_history.updated_at.isoformat()
            },
            'messages': message_list
        })
        
    except Exception as e:
        logger.error(f"채팅 메시지 조회 오류: {e}")
        return JsonResponse({
            'success': False,
            'message': '채팅 메시지를 조회할 수 없습니다.'
        })

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_chat_history(request, chat_history_id):
    """채팅 히스토리 삭제 (소프트 삭제)"""
    try:
        # 로그인한 사용자 확인
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({
                'success': False,
                'message': '로그인이 필요합니다.'
            })
        
        # 사용자 정보 조회
        try:
            user = User.objects.get(seq_id=user_id)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '사용자 정보를 찾을 수 없습니다.'
            })
        
        # 채팅 히스토리 조회 (사용자 소유 확인)
        try:
            chat_history = UChatbotHistory.objects.get(
                seq_id=chat_history_id,
                user=user
            )
        except UChatbotHistory.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '채팅 히스토리를 찾을 수 없습니다.'
            })
        
        # 완전 삭제 (데이터베이스에서 영구 삭제)
        chat_history.delete()
        
        logger.info(f"Chat history {chat_history_id} permanently deleted by user {user_id}")
        
        return JsonResponse({
            'success': True,
            'message': '채팅 히스토리가 완전히 삭제되었습니다.'
        })
        
    except Exception as e:
        logger.error(f"채팅 히스토리 삭제 오류: {e}")
        return JsonResponse({
            'success': False,
            'message': '채팅 히스토리 삭제 중 오류가 발생했습니다.'
        })

@require_http_methods(["GET"])
def session_info(request, session_id):
    """세션 정보 조회"""
    try:
        ai_service = AIService()
        result = ai_service.get_session_info(session_id)
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"세션 정보 조회 오류: {e}")
        return JsonResponse({
            'status': 'error',
            'message': '세션 정보 조회 중 오류가 발생했습니다.'
        })

@require_http_methods(["DELETE"])
def delete_session(request, session_id):
    """세션 삭제"""
    try:
        ai_service = AIService()
        result = ai_service.delete_session(session_id)
        
        # Django 세션에서도 해당 채팅 히스토리 삭제
        session_key = f'chat_history_{session_id}'
        if session_key in request.session:
            del request.session[session_key]
        
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"세션 삭제 오류: {e}")
        return JsonResponse({
            'status': 'error',
            'message': '세션 삭제 중 오류가 발생했습니다.'
        })

@require_http_methods(["GET"])
def session_stats(request):
    """세션 통계 조회"""
    try:
        ai_service = AIService()
        result = ai_service.get_session_stats()
        return JsonResponse(result)
    except Exception as e:
        logger.error(f"세션 통계 조회 오류: {e}")
        return JsonResponse({
            'status': 'error',
            'message': '세션 통계 조회 중 오류가 발생했습니다.'
        })

@require_http_methods(["GET"])
def serve_pdf(request, file_path):
    """S3에서 PDF 파일을 서빙하는 뷰"""
    try:
        # URL 디코딩
        decoded_file_path = urllib.parse.unquote(file_path)
        
        # S3 경로에 pdf/ 접두사 추가
        s3_file_path = f"pdf/{decoded_file_path}"
        
        # S3 클라이언트 생성
        s3_client = boto3.client(
            's3',
            aws_access_key_id=config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
            region_name=config.AWS_S3_REGION_NAME
        )
        
        bucket_name = config.AWS_STORAGE_BUCKET_NAME
        if not bucket_name:
            logger.error("AWS_STORAGE_BUCKET_NAME 환경변수가 설정되지 않았습니다.")
            raise Http404("S3 설정이 올바르지 않습니다.")
        
        # S3에서 파일 존재 확인
        try:
            s3_client.head_object(Bucket=bucket_name, Key=s3_file_path)
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                logger.error(f"S3에서 PDF 파일을 찾을 수 없습니다: {s3_file_path}")
                raise Http404("PDF 파일을 찾을 수 없습니다.")
            else:
                logger.error(f"S3 파일 확인 오류: {e}")
                raise Http404("PDF 파일을 불러올 수 없습니다.")
        
        # S3에서 파일 다운로드
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=s3_file_path)
            file_content = response['Body'].read()
            
            # 파일명 추출
            filename = os.path.basename(decoded_file_path)
            
            # PDF 파일 응답
            http_response = HttpResponse(
                file_content,
                content_type='application/pdf'
            )
            http_response['Content-Disposition'] = f'inline; filename="{filename}"'
            http_response['Content-Length'] = len(file_content)
            
            return http_response
            
        except ClientError as e:
            logger.error(f"S3 파일 다운로드 오류: {e}")
            raise Http404("PDF 파일을 불러올 수 없습니다.")
        
    except NoCredentialsError:
        logger.error("AWS 자격 증명이 올바르지 않습니다.")
        raise Http404("S3 접근 권한이 없습니다.")
    except Exception as e:
        logger.error(f"PDF 파일 서빙 오류: {e}")
        raise Http404("PDF 파일을 불러올 수 없습니다.")

@csrf_exempt
@require_http_methods(["POST"])
def save_pdf_references(request):
    """PDF 참조 정보를 저장하는 API"""
    try:
        # 로그인한 사용자 확인
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({
                'success': False,
                'message': '로그인이 필요합니다.'
            })
        
        data = json.loads(request.body)
        session_msg_id = data.get('session_msg_id')
        pdf_references = data.get('pdf_references', [])
        
        if not session_msg_id:
            return JsonResponse({
                'success': False,
                'message': '세션 메시지 ID가 필요합니다.'
            })
        
        # 세션 메시지 확인
        try:
            session_msg = UChatbotSession.objects.get(seq_id=session_msg_id)
        except UChatbotSession.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '세션 메시지를 찾을 수 없습니다.'
            })
        
        # 기존 PDF 참조 정보 삭제
        ChatbotPDFReference.objects.filter(session_msg=session_msg).delete()
        
        # 새로운 PDF 참조 정보 저장 (CURRENT_PDF만)
        saved_references = []
        for ref in pdf_references:
            # CURRENT_PDF만 저장
            if ref.get('item_type') == 'CURRENT_PDF':
                pdf_ref = ChatbotPDFReference.objects.create(
                    session_msg=session_msg,
                    item_type=ref.get('item_type', 'CURRENT_PDF'),
                    file_name=ref.get('file_name', ''),
                    file_path=ref.get('file_path', ''),
                    page_number=ref.get('page_number'),
                    content=ref.get('content', ''),
                    score=ref.get('score'),
                    product_name=ref.get('product_name', ''),
                    category=ref.get('category', '')
                )
                saved_references.append({
                    'id': pdf_ref.seq_id,
                    'item_type': pdf_ref.item_type,
                    'file_name': pdf_ref.file_name,
                    'file_path': pdf_ref.file_path,
                    'page_number': pdf_ref.page_number,
                    'content': pdf_ref.content,
                    'score': pdf_ref.score,
                    'product_name': pdf_ref.product_name,
                    'category': pdf_ref.category
                })
        
        return JsonResponse({
            'success': True,
            'message': 'PDF 참조 정보가 저장되었습니다.',
            'references': saved_references
        })
        
    except Exception as e:
        logger.error(f"PDF 참조 정보 저장 오류: {e}")
        return JsonResponse({
            'success': False,
            'message': f'PDF 참조 정보 저장 중 오류가 발생했습니다: {str(e)}'
        })

@require_http_methods(["GET"])
def get_pdf_references(request, session_msg_id):
    """특정 세션 메시지의 PDF 참조 정보를 조회하는 API"""
    try:
        # 로그인한 사용자 확인
        user_id = request.session.get('user_id')
        if not user_id:
            return JsonResponse({
                'success': False,
                'message': '로그인이 필요합니다.'
            })
        
        # 세션 메시지 확인
        try:
            session_msg = UChatbotSession.objects.get(seq_id=session_msg_id)
        except UChatbotSession.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '세션 메시지를 찾을 수 없습니다.'
            })
        
        # PDF 참조 정보 조회
        pdf_references = ChatbotPDFReference.objects.filter(session_msg=session_msg).order_by('-created_at')
        
        references = []
        for ref in pdf_references:
            references.append({
                'id': ref.seq_id,
                'item_type': ref.item_type,
                'file_name': ref.file_name,
                'file_path': ref.file_path,
                'page_number': ref.page_number,
                'content': ref.content,
                'score': ref.score,
                'product_name': ref.product_name,
                'category': ref.category,
                'created_at': ref.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'references': references
        })
        
    except Exception as e:
        logger.error(f"PDF 참조 정보 조회 오류: {e}")
        return JsonResponse({
            'success': False,
            'message': f'PDF 참조 정보 조회 중 오류가 발생했습니다: {str(e)}'
        })
