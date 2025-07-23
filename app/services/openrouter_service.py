# =============================================================================
# ENHANCED OPENROUTER AI SERVİS MODÜLÜ (ENHANCED OPENROUTER AI SERVICE MODULE)
# =============================================================================
# Bu modül, OpenRouter API'si ile gelişmiş etkileşim kurmak için optimize edilmiş
# servis sınıfı içerir. Routing, fallback, cost tracking ve performance monitoring
# özelliklerini destekler.
#
# YENİ ÖZELLİKLER:
# - Gelişmiş routing ve load balancing
# - Automatic fallback mechanism
# - Cost tracking ve budget management
# - Performance monitoring ve analytics
# - Enhanced error handling ve retry logic
# =============================================================================

import requests
import json
import time
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from dataclasses import dataclass
from enum import Enum

# Logger konfigürasyonu
logger = logging.getLogger(__name__)

class LoadBalancingStrategy(Enum):
    """Load balancing stratejileri"""
    ROUND_ROBIN = "round_robin"
    LEAST_COST = "least_cost"
    FASTEST_RESPONSE = "fastest_response"
    RANDOM = "random"

@dataclass
class RequestMetrics:
    """Request metrikleri için data class"""
    start_time: datetime
    end_time: Optional[datetime] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    cost: Optional[Decimal] = None
    provider_used: Optional[str] = None
    response_time_ms: Optional[int] = None
    success: bool = False
    error_message: Optional[str] = None

class EnhancedOpenRouterService:
    """
    OpenRouter API'si ile gelişmiş etkileşim kurmak için optimize edilmiş servis sınıfı.
    """

    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """
        EnhancedOpenRouterService'i başlatır.

        Args:
            api_key (str): OpenRouter API anahtarı
            config (Optional[Dict]): Uygulama konfigürasyonu
        """
        self.api_key = api_key
        self.config = config or {}
        self.base_url = "https://openrouter.ai/api/v1"
        self.session = requests.Session()
        self._setup_session()
        
        # Performance tracking
        self._request_history: List[RequestMetrics] = []
        self._provider_performance: Dict[str, Dict[str, Any]] = {}
        
        # Rate limiting
        self._last_request_time = 0
        self._min_request_interval = 0.1  # 100ms minimum between requests
        
        if not self.api_key:
            raise ValueError("OpenRouter API anahtarı gereklidir")

    def _setup_session(self):
        """HTTP session'ını yapılandırır."""
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.config.get('APP_SITE_URL', 'http://localhost'),
            "X-Title": self.config.get('APP_NAME', 'Zekai')
        })

    def _apply_rate_limiting(self):
        """Rate limiting uygular."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._min_request_interval:
            sleep_time = self._min_request_interval - time_since_last
            time.sleep(sleep_time)
            
        self._last_request_time = time.time()

    def _select_model_by_strategy(self, 
                                  available_models: List[str], 
                                  strategy: LoadBalancingStrategy) -> str:
        """
        Load balancing stratejisine göre model seçer.
        
        Args:
            available_models: Kullanılabilir model listesi
            strategy: Load balancing stratejisi
            
        Returns:
            str: Seçilen model adı
        """
        if not available_models:
            raise ValueError("Kullanılabilir model bulunamadı")
            
        if len(available_models) == 1:
            return available_models[0]
            
        if strategy == LoadBalancingStrategy.ROUND_ROBIN:
            # Simple round robin implementation
            current_time = int(time.time())
            index = current_time % len(available_models)
            return available_models[index]
            
        elif strategy == LoadBalancingStrategy.LEAST_COST:
            # En düşük maliyetli modeli seç (bu örnekte ilkini döndürüyoruz)
            # Gerçek implementasyonda model pricing bilgisi kullanılmalı
            return available_models[0]
            
        elif strategy == LoadBalancingStrategy.FASTEST_RESPONSE:
            # En hızlı yanıt veren modeli seç
            fastest_model = available_models[0]
            best_time = float('inf')
            
            for model in available_models:
                avg_time = self._provider_performance.get(model, {}).get('avg_response_time', float('inf'))
                if avg_time < best_time:
                    best_time = avg_time
                    fastest_model = model
                    
            return fastest_model
            
        else:  # RANDOM
            import random
            return random.choice(available_models)

    def _build_request_payload(self, 
                              model_name: str,
                              messages: List[Dict[str, str]],
                              model_entity) -> Dict[str, Any]:
        """
        Request payload'ını oluşturur.
        
        Args:
            model_name: Model adı
            messages: Chat mesajları
            model_entity: Model entity'si
            
        Returns:
            Dict: Request payload'ı
        """
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False
        }
        
        # Model-specific konfigürasyonları ekle
        if hasattr(model_entity, 'provider_config') and model_entity.provider_config:
            config = model_entity.provider_config
            
            # Temperature, max_tokens gibi parametreleri ekle
            if 'temperature' in config:
                payload['temperature'] = config['temperature']
            if 'max_tokens' in config:
                payload['max_tokens'] = config['max_tokens']
            if 'top_p' in config:
                payload['top_p'] = config['top_p']
                
        # OpenRouter-specific parametreler
        if hasattr(model_entity, 'routing_config') and model_entity.routing_config:
            routing = model_entity.routing_config
            
            if 'route' in routing:
                payload['route'] = routing['route']
            if 'provider' in routing:
                payload['provider'] = routing['provider']
                
        return payload

    def _calculate_cost(self, 
                       input_tokens: int, 
                       output_tokens: int, 
                       model_entity) -> Optional[Decimal]:
        """
        Request maliyetini hesaplar.
        
        Args:
            input_tokens: Input token sayısı
            output_tokens: Output token sayısı
            model_entity: Model entity'si
            
        Returns:
            Optional[Decimal]: Toplam maliyet
        """
        try:
            if (hasattr(model_entity, 'input_cost_per_token') and 
                hasattr(model_entity, 'output_cost_per_token') and
                model_entity.input_cost_per_token and 
                model_entity.output_cost_per_token):
                
                input_cost = Decimal(str(model_entity.input_cost_per_token)) * input_tokens
                output_cost = Decimal(str(model_entity.output_cost_per_token)) * output_tokens
                
                return input_cost + output_cost
        except (ValueError, TypeError) as e:
            logger.warning(f"Maliyet hesaplama hatası: {e}")
            
        return None

    def _update_performance_metrics(self, 
                                   model_name: str, 
                                   metrics: RequestMetrics):
        """
        Performance metriklerini günceller.
        
        Args:
            model_name: Model adı
            metrics: Request metrikleri
        """
        if model_name not in self._provider_performance:
            self._provider_performance[model_name] = {
                'total_requests': 0,
                'successful_requests': 0,
                'total_response_time': 0,
                'avg_response_time': 0,
                'error_rate': 0,
                'last_used': None
            }
            
        perf = self._provider_performance[model_name]
        perf['total_requests'] += 1
        perf['last_used'] = datetime.utcnow()
        
        if metrics.success:
            perf['successful_requests'] += 1
            if metrics.response_time_ms:
                perf['total_response_time'] += metrics.response_time_ms
                perf['avg_response_time'] = perf['total_response_time'] / perf['successful_requests']
        
        perf['error_rate'] = 1 - (perf['successful_requests'] / perf['total_requests'])
        
        # Request history'ye ekle (son 100 request'i tut)
        self._request_history.append(metrics)
        if len(self._request_history) > 100:
            self._request_history.pop(0)

    def send_chat_request(self, 
                         model_entity, 
                         chat_message: Optional[str], 
                         chat_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        OpenRouter API'sine gelişmiş chat request'i gönderir.

        Args:
            model_entity: Model entity'si
            chat_message: Yeni kullanıcı mesajı
            chat_history: Chat geçmişi

        Returns:
            Dict[str, Any]: API yanıtı
        """
        metrics = RequestMetrics(start_time=datetime.utcnow())
        
        try:
            # Rate limiting uygula
            self._apply_rate_limiting()
            
            # Model adını belirle
            primary_model = getattr(model_entity, 'external_model_name', None)
            fallback_models = getattr(model_entity, 'fallback_models', [])
            
            if not primary_model:
                return {"error": "Model adı bulunamadı", "status_code": 400}
            
            # Kullanılabilir modeller listesi
            available_models = [primary_model] + (fallback_models or [])
            
            # Load balancing stratejisini belirle
            strategy_name = getattr(model_entity, 'load_balancing_strategy', 'round_robin')
            try:
                strategy = LoadBalancingStrategy(strategy_name)
            except ValueError:
                strategy = LoadBalancingStrategy.ROUND_ROBIN
            
            # Mesajları hazırla
            messages = []
            for msg in chat_history:
                messages.append({
                    'role': msg.get('role', 'user'),
                    'content': msg.get('content', '')
                })
            
            if chat_message:
                messages.append({'role': 'user', 'content': chat_message})
            
            if not messages:
                return {"error": "Gönderilecek mesaj bulunamadı", "status_code": 400}
            
            # Model seçimi ve request gönderimi
            last_error = None
            
            for attempt, model_name in enumerate(available_models):
                try:
                    logger.info(f"OpenRouter request - Model: {model_name}, Attempt: {attempt + 1}")
                    
                    # Request payload'ını oluştur
                    payload = self._build_request_payload(model_name, messages, model_entity)
                    
                    # API request'i gönder
                    response = self.session.post(
                        f"{self.base_url}/chat/completions",
                        json=payload,
                        timeout=120
                    )
                    
                    metrics.end_time = datetime.utcnow()
                    metrics.response_time_ms = int((metrics.end_time - metrics.start_time).total_seconds() * 1000)
                    metrics.provider_used = model_name
                    
                    response.raise_for_status()
                    response_data = response.json()
                    
                    # Token usage ve cost hesaplama
                    usage = response_data.get('usage', {})
                    if usage:
                        metrics.input_tokens = usage.get('prompt_tokens', 0)
                        metrics.output_tokens = usage.get('completion_tokens', 0)
                        metrics.cost = self._calculate_cost(
                            metrics.input_tokens, 
                            metrics.output_tokens, 
                            model_entity
                        )
                    
                    # Response'u parse et
                    if response_data.get("choices") and len(response_data["choices"]) > 0:
                        content = response_data["choices"][0]["message"]["content"]
                        
                        metrics.success = True
                        self._update_performance_metrics(model_name, metrics)
                        
                        result = {
                            "response": content.strip(),
                            "status_code": 200,
                            "model_used": model_name,
                            "processing_time": metrics.response_time_ms,
                            "usage": usage
                        }
                        
                        if metrics.cost:
                            result["cost"] = str(metrics.cost)
                            result["cost_currency"] = getattr(model_entity, 'cost_currency', 'USD')
                        
                        logger.info(f"OpenRouter request başarılı - Model: {model_name}, "
                                  f"Süre: {metrics.response_time_ms}ms")
                        
                        return result
                    else:
                        raise ValueError("API yanıtında beklenen 'choices' alanı bulunamadı")
                        
                except requests.exceptions.HTTPError as http_err:
                    error_msg = f"HTTP {http_err.response.status_code}: {http_err.response.text}"
                    logger.warning(f"OpenRouter HTTP hatası (Model: {model_name}): {error_msg}")
                    last_error = error_msg
                    
                    # 4xx hatalarında diğer modelleri deneme
                    if 400 <= http_err.response.status_code < 500:
                        continue
                    else:
                        break
                        
                except requests.exceptions.RequestException as req_err:
                    error_msg = f"Request hatası: {str(req_err)}"
                    logger.warning(f"OpenRouter request hatası (Model: {model_name}): {error_msg}")
                    last_error = error_msg
                    continue
                    
                except Exception as e:
                    error_msg = f"Beklenmedik hata: {str(e)}"
                    logger.warning(f"OpenRouter beklenmedik hata (Model: {model_name}): {error_msg}")
                    last_error = error_msg
                    continue
            
            # Tüm modeller başarısız oldu
            metrics.success = False
            metrics.error_message = last_error
            self._update_performance_metrics(primary_model, metrics)
            
            return {
                "error": f"Tüm modeller başarısız oldu. Son hata: {last_error}",
                "status_code": 500,
                "attempted_models": available_models
            }
            
        except Exception as e:
            error_message = f"OpenRouter service hatası: {str(e)}"
            logger.error(error_message, exc_info=True)
            
            metrics.success = False
            metrics.error_message = error_message
            
            return {
                "error": error_message,
                "status_code": 500
            }

    def get_available_models(self) -> Dict[str, Any]:
        """
        OpenRouter'dan kullanılabilir modelleri getirir.
        
        Returns:
            Dict: Kullanılabilir modeller listesi
        """
        try:
            response = self.session.get(f"{self.base_url}/models", timeout=30)
            response.raise_for_status()
            
            models_data = response.json()
            logger.info(f"OpenRouter'dan {len(models_data.get('data', []))} model bilgisi alındı")
            
            return {
                "models": models_data.get('data', []),
                "status_code": 200
            }
            
        except Exception as e:
            error_message = f"Model listesi alınamadı: {str(e)}"
            logger.error(error_message)
            
            return {
                "error": error_message,
                "status_code": 500
            }

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Performance istatistiklerini döndürür.
        
        Returns:
            Dict: Performance metrikleri
        """
        total_requests = len(self._request_history)
        successful_requests = sum(1 for r in self._request_history if r.success)
        
        stats = {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": successful_requests / total_requests if total_requests > 0 else 0,
            "provider_performance": self._provider_performance,
            "recent_requests": len([r for r in self._request_history 
                                  if r.start_time > datetime.utcnow() - timedelta(hours=1)])
        }
        
        if successful_requests > 0:
            avg_response_time = sum(r.response_time_ms for r in self._request_history 
                                  if r.success and r.response_time_ms) / successful_requests
            stats["avg_response_time_ms"] = int(avg_response_time)
        
        return stats

    def clear_performance_history(self):
        """Performance geçmişini temizler."""
        self._request_history.clear()
        self._provider_performance.clear()
        logger.info("Performance geçmişi temizlendi")

    def __del__(self):
        """Destructor - session'ı kapat."""
        if hasattr(self, 'session'):
            self.session.close()


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def create_enhanced_openrouter_service(api_key: str, 
                                      config: Optional[Dict[str, Any]] = None) -> EnhancedOpenRouterService:
    """
    EnhancedOpenRouterService factory function.
    
    Args:
        api_key: OpenRouter API anahtarı
        config: Konfigürasyon
        
    Returns:
        EnhancedOpenRouterService: Yapılandırılmış servis instance'ı
    """
    try:
        return EnhancedOpenRouterService(api_key, config)
    except Exception as e:
        logger.error(f"EnhancedOpenRouterService oluşturulamadı: {str(e)}")
        raise
