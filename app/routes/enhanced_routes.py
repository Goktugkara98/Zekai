# =============================================================================
# GELİŞTİRİLMİŞ ANA ROTALAR MODÜLÜ (ENHANCED MAIN ROUTES MODULE)
# =============================================================================
# Bu modül, OpenRouter ve diğer alternatif AI sağlayıcıları ile uyumlu
# gelişmiş API endpoint'lerini tanımlar.
#
# YENİ ÖZELLİKLER:
# - Multi-provider chat API
# - Provider management endpoints
# - Enhanced model management
# - Analytics ve monitoring
# - WebSocket support
# =============================================================================

import json
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any

from flask import Blueprint, request, jsonify, current_app, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import traceback

# Import services
from app.services.unified_ai_service import UnifiedAIService, AIResponse
from app.services.ai_model_service import (
    get_ai_model_api_details,
    fetch_ai_categories_from_db,
    add_ai_model,
    get_all_available_models
)

# Logger konfigürasyonu
logger = logging.getLogger(__name__)

# Blueprint oluştur
enhanced_routes = Blueprint('enhanced_routes', __name__, url_prefix='/api/v2')

# Global unified service instance (gerçek uygulamada dependency injection kullanılmalı)
unified_service: Optional[UnifiedAIService] = None

def get_unified_service() -> UnifiedAIService:
    """Unified AI service instance'ını döndürür."""
    global unified_service
    if unified_service is None:
        # Gerçek uygulamada bu konfigürasyon external source'dan gelmelidir
        from app.services.unified_ai_service import create_unified_ai_service, setup_default_providers
        
        config = current_app.config
        unified_service = create_unified_ai_service(config)
        
        # API key'leri environment'dan al
        api_keys = {}
        if config.get('GEMINI_API_KEY'):
            api_keys['gemini'] = config['GEMINI_API_KEY']
        if config.get('OPENROUTER_API_KEY'):
            api_keys['openrouter'] = config['OPENROUTER_API_KEY']
        
        if api_keys:
            setup_default_providers(unified_service, api_keys)
    
    return unified_service

# =============================================================================
# ENHANCED CHAT API ENDPOINTS
# =============================================================================

@enhanced_routes.route('/chat/completions', methods=['POST'])
def chat_completions():
    """
    OpenAI-compatible chat completions endpoint with multi-provider support.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request body gereklidir',
                'type': 'invalid_request'
            }), 400
        
        # Required fields validation
        model_id = data.get('model')
        messages = data.get('messages', [])
        
        if not model_id:
            return jsonify({
                'error': 'Model ID gereklidir',
                'type': 'invalid_request'
            }), 400
        
        if not messages:
            return jsonify({
                'error': 'Messages array gereklidir',
                'type': 'invalid_request'
            }), 400
        
        # Model entity'sini al
        model_details = get_ai_model_api_details(model_id)
        if not model_details:
            return jsonify({
                'error': f'Model bulunamadı: {model_id}',
                'type': 'model_not_found'
            }), 404
        
        # Model entity'sini oluştur (gerçek uygulamada repository'den gelmelidir)
        from app.models.entities.model import Model
        model_entity = Model.from_dict(model_details)
        
        # Chat history'yi hazırla
        chat_history = []
        chat_message = None
        
        for i, msg in enumerate(messages):
            if i == len(messages) - 1 and msg.get('role') == 'user':
                # Son mesaj user'dan geliyorsa, onu chat_message olarak ayır
                chat_message = msg.get('content', '')
            else:
                chat_history.append({
                    'role': msg.get('role', 'user'),
                    'content': msg.get('content', '')
                })
        
        # Preferred provider'ı kontrol et
        preferred_provider = data.get('provider')
        
        # Unified service ile request gönder
        service = get_unified_service()
        response = service.send_chat_request(
            model_entity, 
            chat_message, 
            chat_history,
            preferred_provider
        )
        
        if response.success:
            # OpenAI-compatible response format
            return jsonify({
                'id': f'chatcmpl-{datetime.utcnow().strftime("%Y%m%d%H%M%S")}',
                'object': 'chat.completion',
                'created': int(datetime.utcnow().timestamp()),
                'model': response.model_used,
                'provider': response.provider_used,
                'choices': [{
                    'index': 0,
                    'message': {
                        'role': 'assistant',
                        'content': response.content
                    },
                    'finish_reason': 'stop'
                }],
                'usage': {
                    'prompt_tokens': response.input_tokens or 0,
                    'completion_tokens': response.output_tokens or 0,
                    'total_tokens': (response.input_tokens or 0) + (response.output_tokens or 0)
                },
                'cost': {
                    'amount': str(response.cost) if response.cost else None,
                    'currency': response.cost_currency
                },
                'processing_time_ms': response.processing_time_ms
            })
        else:
            return jsonify({
                'error': response.error_message or 'Request başarısız',
                'type': 'api_error',
                'provider': response.provider_used,
                'model': response.model_used
            }), 500
            
    except Exception as e:
        logger.error(f"Chat completions error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'type': 'server_error',
            'details': str(e) if current_app.debug else None
        }), 500

@enhanced_routes.route('/chat/stream', methods=['POST'])
def chat_stream():
    """
    Streaming chat completions endpoint.
    """
    # Streaming implementation burada gelecek
    # Şimdilik placeholder
    return jsonify({
        'error': 'Streaming henüz implement edilmedi',
        'type': 'not_implemented'
    }), 501

@enhanced_routes.route('/chat/batch', methods=['POST'])
def chat_batch():
    """
    Batch chat completions endpoint.
    """
    try:
        data = request.get_json()
        requests_data = data.get('requests', [])
        
        if not requests_data:
            return jsonify({
                'error': 'Requests array gereklidir',
                'type': 'invalid_request'
            }), 400
        
        results = []
        service = get_unified_service()
        
        for i, req_data in enumerate(requests_data):
            try:
                # Her request için aynı logic'i uygula
                model_id = req_data.get('model')
                messages = req_data.get('messages', [])
                
                if not model_id or not messages:
                    results.append({
                        'index': i,
                        'error': 'Model ID ve messages gereklidir',
                        'type': 'invalid_request'
                    })
                    continue
                
                model_details = get_ai_model_api_details(model_id)
                if not model_details:
                    results.append({
                        'index': i,
                        'error': f'Model bulunamadı: {model_id}',
                        'type': 'model_not_found'
                    })
                    continue
                
                from app.models.entities.model import Model
                model_entity = Model.from_dict(model_details)
                
                # Messages'ı parse et
                chat_history = messages[:-1] if len(messages) > 1 else []
                chat_message = messages[-1].get('content', '') if messages else None
                
                response = service.send_chat_request(
                    model_entity, 
                    chat_message, 
                    chat_history,
                    req_data.get('provider')
                )
                
                if response.success:
                    results.append({
                        'index': i,
                        'response': {
                            'content': response.content,
                            'model': response.model_used,
                            'provider': response.provider_used,
                            'usage': {
                                'prompt_tokens': response.input_tokens or 0,
                                'completion_tokens': response.output_tokens or 0
                            },
                            'cost': str(response.cost) if response.cost else None
                        }
                    })
                else:
                    results.append({
                        'index': i,
                        'error': response.error_message,
                        'type': 'api_error'
                    })
                    
            except Exception as e:
                results.append({
                    'index': i,
                    'error': str(e),
                    'type': 'processing_error'
                })
        
        return jsonify({
            'results': results,
            'total_requests': len(requests_data),
            'successful_requests': len([r for r in results if 'response' in r])
        })
        
    except Exception as e:
        logger.error(f"Batch chat error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Batch processing failed',
            'type': 'server_error'
        }), 500

# =============================================================================
# PROVIDER MANAGEMENT ENDPOINTS
# =============================================================================

@enhanced_routes.route('/providers', methods=['GET'])
def list_providers():
    """
    Kayıtlı tüm AI sağlayıcılarını listeler.
    """
    try:
        service = get_unified_service()
        stats = service.get_provider_stats()
        health = service.health_check()
        
        providers = []
        for provider_name in stats['providers']:
            provider_stats = stats['providers'][provider_name]
            provider_health = health['providers'].get(provider_name, {})
            
            providers.append({
                'name': provider_name,
                'status': provider_health.get('status', 'unknown'),
                'total_requests': provider_stats['total_requests'],
                'successful_requests': provider_stats['successful_requests'],
                'success_rate': (
                    provider_stats['successful_requests'] / 
                    max(provider_stats['total_requests'], 1)
                ),
                'avg_response_time': provider_stats['avg_response_time'],
                'total_cost': str(provider_stats['total_cost']),
                'last_used': provider_stats['last_used'].isoformat() if provider_stats['last_used'] else None,
                'errors': provider_health.get('errors', [])
            })
        
        return jsonify({
            'providers': providers,
            'total_providers': stats['total_providers'],
            'overall_status': health['overall_status']
        })
        
    except Exception as e:
        logger.error(f"List providers error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Provider listesi alınamadı',
            'type': 'server_error'
        }), 500

@enhanced_routes.route('/providers/<provider_name>/test', methods=['POST'])
def test_provider(provider_name: str):
    """
    Belirli bir sağlayıcının connectivity'sini test eder.
    """
    try:
        service = get_unified_service()
        
        # Test message ile basit bir request gönder
        test_models = service.get_supported_models(provider_name)
        
        if not test_models or provider_name not in test_models:
            return jsonify({
                'error': f'Provider bulunamadı: {provider_name}',
                'type': 'provider_not_found'
            }), 404
        
        # İlk modeli kullanarak test et
        first_model = test_models[provider_name][0] if test_models[provider_name] else None
        
        if not first_model:
            return jsonify({
                'error': f'Provider için model bulunamadı: {provider_name}',
                'type': 'no_models'
            }), 400
        
        # Basit test modeli oluştur
        from app.models.entities.model import Model
        test_model = Model(
            name=f'Test Model - {provider_name}',
            service_provider=provider_name,
            external_model_name=first_model
        )
        
        start_time = datetime.utcnow()
        response = service.send_chat_request(
            test_model,
            "Test message - please respond with 'OK'",
            [],
            provider_name
        )
        end_time = datetime.utcnow()
        
        test_duration = int((end_time - start_time).total_seconds() * 1000)
        
        return jsonify({
            'provider': provider_name,
            'status': 'healthy' if response.success else 'error',
            'test_duration_ms': test_duration,
            'model_tested': first_model,
            'response_preview': response.content[:100] if response.success else None,
            'error': response.error_message if not response.success else None
        })
        
    except Exception as e:
        logger.error(f"Test provider error: {str(e)}", exc_info=True)
        return jsonify({
            'provider': provider_name,
            'status': 'error',
            'error': str(e),
            'type': 'test_failed'
        }), 500

@enhanced_routes.route('/providers/<provider_name>/models', methods=['GET'])
def get_provider_models(provider_name: str):
    """
    Sağlayıcıya ait kullanılabilir modelleri listeler.
    """
    try:
        service = get_unified_service()
        models = service.get_supported_models(provider_name)
        
        if provider_name not in models:
            return jsonify({
                'error': f'Provider bulunamadı: {provider_name}',
                'type': 'provider_not_found'
            }), 404
        
        return jsonify({
            'provider': provider_name,
            'models': models[provider_name],
            'total_models': len(models[provider_name])
        })
        
    except Exception as e:
        logger.error(f"Get provider models error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Model listesi alınamadı',
            'type': 'server_error'
        }), 500

# =============================================================================
# ENHANCED MODEL MANAGEMENT ENDPOINTS
# =============================================================================

@enhanced_routes.route('/models', methods=['GET'])
def list_models():
    """
    Tüm kullanılabilir modelleri listeler.
    """
    try:
        # Query parameters
        provider = request.args.get('provider')
        category = request.args.get('category')
        status = request.args.get('status', 'active')
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 50)), 100)
        
        # Tüm modelleri al
        all_models = get_all_available_models()
        
        # Filtreleme
        filtered_models = []
        for model in all_models:
            if provider and model.get('service_provider') != provider:
                continue
            if category and model.get('category_id') != int(category):
                continue
            if status and model.get('status', 'active') != status:
                continue
            
            filtered_models.append(model)
        
        # Pagination
        total = len(filtered_models)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_models = filtered_models[start:end]
        
        return jsonify({
            'models': paginated_models,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            },
            'filters': {
                'provider': provider,
                'category': category,
                'status': status
            }
        })
        
    except Exception as e:
        logger.error(f"List models error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Model listesi alınamadı',
            'type': 'server_error'
        }), 500

@enhanced_routes.route('/models', methods=['POST'])
def create_model():
    """
    Yeni model kaydı oluşturur.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'Request body gereklidir',
                'type': 'invalid_request'
            }), 400
        
        # Required fields
        required_fields = ['name', 'service_provider', 'external_model_name', 'category_name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'error': f'{field} alanı gereklidir',
                    'type': 'invalid_request'
                }), 400
        
        # Model oluştur
        success, message, model_id = add_ai_model(
            category_name=data['category_name'],
            model_name=data['name'],
            model_icon=data.get('icon'),
            api_url=data.get('api_url'),
            description=data.get('description'),
            details=data.get('details'),
            service_provider=data['service_provider'],
            external_model_name=data['external_model_name'],
            request_method=data.get('request_method', 'POST'),
            request_headers=data.get('request_headers'),
            request_body=data.get('request_body'),
            response_path=data.get('response_path'),
            api_key=data.get('api_key'),
            prompt_template=data.get('prompt_template'),
            status=data.get('status', 'active')
        )
        
        if success:
            return jsonify({
                'id': model_id,
                'message': message,
                'model': data
            }), 201
        else:
            return jsonify({
                'error': message,
                'type': 'creation_failed'
            }), 400
            
    except Exception as e:
        logger.error(f"Create model error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Model oluşturulamadı',
            'type': 'server_error'
        }), 500

# =============================================================================
# ANALYTICS VE MONITORING ENDPOINTS
# =============================================================================

@enhanced_routes.route('/analytics/usage', methods=['GET'])
def get_usage_analytics():
    """
    Token usage ve trend analizi sağlar.
    """
    try:
        # Time range parameters
        hours = int(request.args.get('hours', 24))
        
        service = get_unified_service()
        stats = service.get_provider_stats()
        
        # Basit analytics (gerçek uygulamada daha detaylı olmalı)
        analytics = {
            'time_range_hours': hours,
            'total_requests': stats['total_requests'],
            'recent_requests': stats['recent_requests'],
            'providers': {}
        }
        
        for provider_name, provider_stats in stats['providers'].items():
            analytics['providers'][provider_name] = {
                'requests': provider_stats['total_requests'],
                'success_rate': (
                    provider_stats['successful_requests'] / 
                    max(provider_stats['total_requests'], 1)
                ),
                'avg_response_time': provider_stats['avg_response_time'],
                'total_cost': str(provider_stats['total_cost'])
            }
        
        return jsonify(analytics)
        
    except Exception as e:
        logger.error(f"Usage analytics error: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Analytics alınamadı',
            'type': 'server_error'
        }), 500

@enhanced_routes.route('/health', methods=['GET'])
def health_check():
    """
    Sistem health status'unu döndürür.
    """
    try:
        service = get_unified_service()
        health = service.health_check()
        
        return jsonify(health)
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}", exc_info=True)
        return jsonify({
            'overall_status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@enhanced_routes.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint bulunamadı',
        'type': 'not_found'
    }), 404

@enhanced_routes.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'error': 'HTTP metodu desteklenmiyor',
        'type': 'method_not_allowed'
    }), 405

@enhanced_routes.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'type': 'server_error'
    }), 500

