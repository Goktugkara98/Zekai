# =============================================================================
# Google AI Servisi (Google AI Service)
# =============================================================================
# Bu modül, Google AI platformu (örn. Gemini API) ile etkileşim kurmak için
# özel servis mantığını içerir.
# =============================================================================

import requests
import json
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from flask import current_app # Loglama ve yapılandırma erişimi için

if TYPE_CHECKING:
    from app.models.entities.model import Model # Model entity'sinin doğru yolu
    from app.repositories.model_repository import ModelRepository

class GoogleAIService:
    """
    Google AI modelleri (örneğin Gemini) için AI Servis uygulaması.
    """

    def __init__(self, config: Dict[str, Any], model_repository: 'ModelRepository'):
        """
        GoogleAIService'i başlatır.

        Args:
            config (Dict[str, Any]): Uygulama yapılandırma ayarları.
                                     'GOOGLE_API_KEY' gibi anahtarları içerebilir.
            model_repository (ModelRepository): Model verilerine erişim için (şu an doğrudan kullanılmıyor
                                                ancak gelecekteki genişletmeler için tutulabilir).
        """
        self.config = config
        self.model_repository = model_repository
        # Genel bir API anahtarı config'den alınabilir.
        # Modele özgü anahtarlar model_entity üzerinden gelecektir.
        self.default_api_key = self.config.get('GOOGLE_API_KEY')

    def _fill_payload_template(self,
                               payload_template_str: str,
                               conversation_history: List[Dict[str, str]],
                               current_user_message: Optional[str]) -> Dict[str, Any]:
        """
        Verilen payload şablonunu konuşma geçmişi ve mevcut mesajla doldurur.
        Google Gemini API'sinin beklediği 'contents' formatını oluşturur.

        Args:
            payload_template_str (str): JSON formatında payload şablonu.
                                         "$messages" veya "$history" gibi bir yer tutucu içerebilir.
            conversation_history (List[Dict[str, str]]): [{"role": "user/model", "content": "..."}] formatında geçmiş.
                                                          Gemini için "model" rolü "assistant" yerine kullanılır.
            current_user_message (Optional[str]): Kullanıcının en son mesajı.

        Returns:
            Dict[str, Any]: Doldurulmuş payload.

        Raises:
            ValueError: Payload şablonu geçersizse veya doldurulamıyorsa.
        """
        try:
            payload = json.loads(payload_template_str)
        except json.JSONDecodeError as e:
            current_app.logger.error(f"Payload şablonu JSON parse hatası: {e}")
            raise ValueError(f"Payload şablonu geçersiz JSON formatında: {payload_template_str}") from e

        # Gemini API'si için 'contents' listesini oluştur
        gemini_contents: List[Dict[str, Any]] = []
        for msg in conversation_history:
            role = msg.get("role")
            content = msg.get("content")
            if role and content:
                # Gemini 'assistant' yerine 'model' rolünü kullanır
                gemini_role = "model" if role == "assistant" else role
                gemini_contents.append({"role": gemini_role, "parts": [{"text": content}]})

        if current_user_message:
            # Mevcut kullanıcı mesajını da ekle
            gemini_contents.append({"role": "user", "parts": [{"text": current_user_message}]})
        
        # Payload içinde "contents" anahtarını bul ve güncelle
        # Şablonun yapısına göre bu kısım ayarlanabilir.
        # Yaygın bir pattern: payload["contents"] = gemini_contents
        # Veya şablonda özel bir yer tutucu varsa:
        # payload_str_updated = payload_template_str.replace('"$messages"', json.dumps(gemini_contents))
        # payload = json.loads(payload_str_updated)
        
        # En basit yaklaşım, şablonda 'contents' anahtarının olmasını beklemek
        if "contents" in payload:
            payload["contents"] = gemini_contents
        else:
            # Eğer şablonda 'contents' yoksa ve şablon doğrudan bir liste bekliyorsa (daha az olası)
            # Veya şablonun kendisi {"contents": "$messages"} gibi bir şeyse,
            # bu durumda yukarıdaki replace mantığı daha uygun olabilir.
            # Şimdilik, anahtarın varlığını varsayıyoruz.
            current_app.logger.warning("Payload şablonunda 'contents' anahtarı bulunamadı. Gemini formatı için bu gerekli.")
            # Geçici olarak, eğer şablon boş bir sözlükse veya messages bekliyorsa:
            if not payload or "messages" in payload: # Eski bir OpenAI formatına benzerlik varsa
                 payload["contents"] = gemini_contents
                 if "messages" in payload:
                     del payload["messages"]


        # Generation Config gibi diğer ayarlar şablondan gelebilir veya burada eklenebilir.
        # Örneğin: payload.setdefault("generationConfig", {"temperature": 0.7})
        
        return payload

    def _extract_response_by_path(self, response_json: Dict, path: str) -> Optional[str]:
        """
        İç içe bir JSON nesnesinden nokta notasyonlu bir yol kullanarak bir metin değeri çıkarır.
        Örn: "candidates.0.content.parts.0.text"
        """
        try:
            parts = path.split('.')
            current_data = response_json
            for part in parts:
                if part.isdigit(): # Dizi indeksi
                    index = int(part)
                    if not isinstance(current_data, list) or index >= len(current_data):
                        current_app.logger.warning(f"Yanıt yolu hatası: İndeks {index} geçersiz. Veri: {current_data}")
                        return None
                    current_data = current_data[index]
                elif isinstance(current_data, dict): # Sözlük anahtarı
                    if part not in current_data:
                        current_app.logger.warning(f"Yanıt yolu hatası: Anahtar '{part}' bulunamadı. Veri: {current_data}")
                        return None
                    current_data = current_data[part]
                else:
                    current_app.logger.warning(f"Yanıt yolu hatası: Beklenmedik veri tipi. Part: {part}, Veri: {current_data}")
                    return None
            
            if isinstance(current_data, str):
                return current_data
            elif current_data is not None:
                current_app.logger.warning(f"Yanıt yoluyla ulaşılan değer string değil: {type(current_data)}. Path: {path}")
                return str(current_data) # String'e çevirmeyi dene
            return None

        except Exception as e:
            current_app.logger.error(f"Yanıt ayıklanırken hata: {e}. Path: {path}, JSON: {response_json}")
            return None

    def _generate_mock_response(self, user_message: Optional[str], model_name: str) -> str:
        """Sahte (mock) bir AI yanıtı üretir."""
        return (f"Bu, '{model_name}' modelinden mesajınıza sahte bir yanıttır: "
                f"'{user_message if user_message else 'bir mesaj'}'. "
                "Gerçek Google AI servisi şu anda mock modunda.")

    def send_chat_request(self,
                          model_entity: 'Model',
                          chat_message: Optional[str],
                          chat_history: List[Dict[str, str]]
                         ) -> Dict[str, Any]:
        """
        Google AI (Gemini) modeline bir sohbet isteği gönderir.

        Args:
            model_entity (Model): Kullanılacak AI modelinin entity'si.
                                  api_url, api_key, request_method vb. içermelidir.
            chat_message (Optional[str]): Kullanıcının en son mesajı.
            chat_history (List[Dict[str, str]]): Konuşma geçmişi.

        Returns:
            Dict[str, Any]: Yanıtı veya hatayı içeren sözlük.
                            Başarı: {"response": "AI cevabı", "raw_response": {...}, "status_code": 200}
                            Hata: {"error": "hata mesajı", "details": "...", "status_code": http_status_kodu}
        """
        current_app.logger.info(f"GoogleAIService: send_chat_request çağrıldı. Model: {model_entity.name}")

        # Model entity'sinden API detaylarını al
        # Bu alanların Model entity'sinde tanımlı olduğunu varsayıyoruz.
        # Örneğin, `model_entity.api_url`, `model_entity.api_key`, `model_entity.request_body_template` vb.
        # Eğer bu bilgiler `api_config` gibi bir JSON alanında tutuluyorsa, oradan parse edilmeli.
        
        # Örnek olarak, bu bilgilerin doğrudan model_entity üzerinde olduğunu varsayalım:
        api_url = getattr(model_entity, 'api_url', None)
        # API anahtarı önce modelden, sonra genel config'den, sonra environment variable'dan alınabilir.
        api_key = getattr(model_entity, 'api_key', self.default_api_key or self.config.get('GOOGLE_API_KEY'))
        
        request_method = getattr(model_entity, 'request_method', 'POST').upper()
        response_path = getattr(model_entity, 'response_path', "candidates.0.content.parts.0.text") # Gemini için yaygın yol
        
        # request_headers ve request_body_template JSON string olarak saklanıyorsa parse et
        headers_str = getattr(model_entity, 'request_headers', '{}')
        body_template_str = getattr(model_entity, 'request_body_template', '{"contents": []}') # Basit bir Gemini şablonu

        if not api_url:
            current_app.logger.error(f"Model {model_entity.name} için API URL'si yapılandırılmamış.")
            return {"error": "API URL yapılandırması eksik.", "status_code": 500}
        if not api_key:
            # API anahtarı yoksa ve mock API kullanılmıyorsa hata ver
            use_mock_str = self.config.get('USE_MOCK_API', 'false').lower()
            if use_mock_str != 'true':
                current_app.logger.error(f"Model {model_entity.name} için API anahtarı bulunamadı ve mock mod aktif değil.")
                return {"error": "API anahtarı eksik.", "status_code": 500}


        # API URL'sine anahtarı ekle (Google'ın tipik pattern'i)
        # Modelin api_url'si zaten anahtarı içeriyorsa bu adım atlanabilir.
        if api_key and 'generativelanguage.googleapis.com' in api_url and '?key=' not in api_url and '&key=' not in api_url:
            separator = '&' if '?' in api_url else '?'
            api_url = f"{api_url}{separator}key={api_key}"

        try:
            headers = json.loads(headers_str) if isinstance(headers_str, str) else (headers_str if isinstance(headers_str, dict) else {})
        except json.JSONDecodeError:
            current_app.logger.warning(f"Model {model_entity.name} için request_headers JSON parse hatası. Varsayılan kullanılıyor.")
            headers = {}
        
        if not headers.get("Content-Type") and request_method == 'POST':
            headers["Content-Type"] = "application/json"

        # Payload'ı hazırla
        try:
            request_payload = self._fill_payload_template(
                body_template_str,
                chat_history,
                chat_message
            )
        except ValueError as e:
            current_app.logger.error(f"Payload oluşturulurken hata: {e}")
            return {"error": f"Payload oluşturma hatası: {e}", "status_code": 500}

        # Mock API kullanımı (config'den okunabilir)
        if self.config.get('USE_MOCK_API', '').lower() == 'true':
            current_app.logger.info(f"Mock API kullanılıyor. Model: {model_entity.name}")
            mock_text = self._generate_mock_response(chat_message, model_entity.name)
            # Gemini API'sine benzer bir mock yanıt yapısı
            mock_raw_response = {
                "candidates": [{"content": {"parts": [{"text": mock_text}], "role": "model"}}]
            }
            return {"response": mock_text, "raw_response": mock_raw_response, "status_code": 200}

        # Gerçek API çağrısı
        current_app.logger.debug(f"Google AI API isteği: URL={api_url}, Method={request_method}, Payload={request_payload}, Headers={headers}")
        try:
            api_http_response = None
            if request_method == 'POST':
                api_http_response = requests.post(api_url, json=request_payload, headers=headers, timeout=self.config.get("API_TIMEOUT", 60))
            elif request_method == 'GET': # Sohbet için daha az yaygın
                api_http_response = requests.get(api_url, params=request_payload, headers=headers, timeout=self.config.get("API_TIMEOUT", 60))
            else:
                return {"error": f"Desteklenmeyen istek metodu: {request_method}", "status_code": 405}

            api_status_code = api_http_response.status_code
            response_text_content = api_http_response.text # Yanıtı bir kere oku

            current_app.logger.debug(f"Google AI API yanıtı: Status={api_status_code}, Response='{response_text_content[:200]}...'")

            if api_status_code >= 400:
                current_app.logger.error(f"Google AI API Hatası: {api_status_code} - {response_text_content}")
                return {
                    "error": f"AI servisinden hata alındı (HTTP {api_status_code}).",
                    "details": response_text_content,
                    "status_code": api_status_code
                }
            
            # Yanıtı parse et
            try:
                response_json = json.loads(response_text_content)
            except json.JSONDecodeError:
                current_app.logger.error(f"Google AI API yanıtı JSON parse edilemedi: {response_text_content}")
                return {"error": "AI servisinden gelen yanıt JSON formatında değil.", "details": response_text_content, "status_code": 502} # Bad Gateway

            # İstenen veriyi ayıkla
            ai_response_text = self._extract_response_by_path(response_json, response_path)

            if ai_response_text is None:
                current_app.logger.warning(f"Yanıt yolundan ({response_path}) veri alınamadı. Tam yanıt: {response_json}")
                return {"error": "AI yanıtı formatı beklenenden farklı veya boş.", "raw_response": response_json, "status_code": 204} # No Content or structure mismatch

            return {"response": ai_response_text, "raw_response": response_json, "status_code": 200}

        except requests.exceptions.Timeout:
            current_app.logger.error(f"Google AI API isteği zaman aşımına uğradı: {api_url}")
            return {"error": "AI servisine yapılan istek zaman aşımına uğradı.", "status_code": 504} # Gateway Timeout
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Google AI API isteği sırasında hata: {e}")
            return {"error": f"AI servisine ulaşılamadı: {e}", "status_code": 503} # Service Unavailable
        except Exception as e:
            current_app.logger.error(f"Google AI isteği işlenirken beklenmedik hata: {e}", exc_info=True)
            import traceback
            return {
                "error": "AI isteği işlenirken sunucuda beklenmedik bir hata oluştu.",
                "details": str(e),
                "trace": traceback.format_exc(),
                "status_code": 500
            }
