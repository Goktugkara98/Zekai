# =============================================================================
# CHAT SERVICE
# =============================================================================
# Bu dosya, chat işlemlerini yönetir ve veritabanı ile haberleşir.
# =============================================================================

from datetime import datetime
from typing import Dict, Any, List, Optional
import os
import logging
from app.services.providers.factory import ProviderFactory
from app.database.repositories import ChatRepository, MessageRepository, ModelRepository

class ChatService:
    """
    Chat işlemleri servisi
    """
    
    def __init__(self):
        self.provider_factory = ProviderFactory()
        
    def create_chat(self, model_id: int, title: str = None, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Yeni chat oluştur
        
        Args:
            model_id (int): Model ID'si
            title (str): Chat başlığı (opsiyonel)
            
        Returns:
            Dict[str, Any]: Oluşturulan chat bilgileri
        """
        try:
            chat_id = ChatRepository.create_chat(model_id=model_id, title=title, user_id=user_id)
            if not chat_id:
                return {"success": False, "error": "Chat oluşturulamadı"}
            return {
                "success": True,
                "chat_id": chat_id,
                "model_id": model_id,
                "user_id": user_id,
                "title": title,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Chat oluşturma hatası: {str(e)}"
            }
    
    def get_chat(self, chat_id: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Chat bilgilerini al
        
        Args:
            chat_id (str): Chat ID'si
            
        Returns:
            Dict[str, Any]: Chat bilgileri
        """
        try:
            chat = ChatRepository.get_chat(chat_id, user_id=user_id)
            if not chat:
                return {"success": False, "error": "Chat bulunamadı"}
            return {
                "success": True,
                "chat": {
                    "chat_id": chat["chat_id"],
                    "model_id": chat["model_id"],
                    "model_name": chat.get("model_name"),
                    "provider_name": chat.get("provider_name"),
                    "provider_type": chat.get("provider_type"),
                    "title": chat["title"],
                    "is_active": chat["is_active"],
                    "created_at": chat["created_at"].isoformat() if chat.get("created_at") else None,
                    "updated_at": chat["updated_at"].isoformat() if chat.get("updated_at") else None,
                    "last_message_at": chat["last_message_at"].isoformat() if chat.get("last_message_at") else None
                }
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Chat alma hatası: {str(e)}"
            }
    
    def get_chat_messages(self, chat_id: str, limit: int = 50, offset: int = 0, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Chat mesajlarını al
        
        Args:
            chat_id (str): Chat ID'si
            limit (int): Maksimum mesaj sayısı
            offset (int): Başlangıç offset'i
            
        Returns:
            Dict[str, Any]: Mesaj listesi
        """
        try:
            # Eğer user_id verildiyse, chat sahibini doğrula
            if user_id is not None and not ChatRepository.get_chat(chat_id, user_id=user_id):
                return {"success": False, "error": "Yetkisiz veya chat bulunamadı"}

            rows = MessageRepository.list_by_chat(chat_id, limit=limit, offset=offset)
            messages = []
            for row in (rows or []):
                messages.append({
                    "message_id": row["message_id"],
                    "content": row["content"],
                    "is_user": bool(row["is_user"]),
                    "timestamp": row["timestamp"].isoformat() if row.get("timestamp") else None,
                    "created_at": row["created_at"].isoformat() if row.get("created_at") else None
                })
            return {"success": True, "messages": messages, "count": len(messages)}
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Mesaj alma hatası: {str(e)}"
            }
    
    def save_message(self, chat_id: str, content: str, is_user: bool, model_id: int = None) -> Dict[str, Any]:
        """
        Mesajı veritabanına kaydet
        
        Args:
            chat_id (str): Chat ID'si
            content (str): Mesaj içeriği
            is_user (bool): Kullanıcı mesajı mı?
            model_id (int): Model ID'si (opsiyonel)
            
        Returns:
            Dict[str, Any]: Kayıt sonucu
        """
        try:
            now = datetime.now()
            msg_id = MessageRepository.create_message(chat_id=chat_id, content=content, is_user=is_user, model_id=model_id, when=now)
            if not msg_id:
                return {"success": False, "error": "Mesaj kaydedilemedi"}
            ChatRepository.update_last_message_time(chat_id, when=now)
            return {"success": True, "message": "Mesaj başarıyla kaydedildi"}
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Mesaj kaydetme hatası: {str(e)}"
            }
    
    def send_message(self, chat_id: str, user_message: str, model_id: int, api_key: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Mesaj gönder ve AI yanıtı al
        
        Args:
            chat_id (str): Chat ID'si
            user_message (str): Kullanıcı mesajı
            model_id (int): Model ID'si
            api_key (str): API anahtarı
            
        Returns:
            Dict[str, Any]: Yanıt sonucu
        """
        try:
            # Eğer user_id verildiyse, chat sahibini doğrula
            if user_id is not None and not ChatRepository.get_chat(chat_id, user_id=user_id):
                return {"success": False, "error": "Yetkisiz veya chat bulunamadı"}

            # Model bilgilerini al (Repository üzerinden)
            model = ModelRepository.get_model_by_id(model_id)
            if not model:
                return {
                    "success": False,
                    "error": "Model bulunamadı"
                }
            
            model_name = model.get("model_name")
            provider_name = model.get("provider_name")
            # Backend'de tutulan provider_type bilgisini kullan
            provider_type = (model.get("provider_type") or "").lower()
            # İsteklerde kullanılacak model kimliği (örn. openrouter id). Boş ise model_name'e geri dön.
            request_model_name = model.get("request_model_name") or model_name
            debug = str(os.getenv('PROVIDER_DEBUG', '0')).lower() in ('1','true','yes','on')
            if debug:
                try:
                    logging.warning("[ChatService] provider_type=%s provider_name=%s request_model=%s display_model=%s", provider_type, provider_name, request_model_name, model_name)
                    print(f"[ChatService] provider_type={provider_type} provider_name={provider_name} request_model={request_model_name} display_model={model_name}")
                except Exception:
                    pass
            
            # Provider servisini al
            provider_service = self.provider_factory.get_service(provider_type)
            if not provider_service:
                if debug:
                    try:
                        logging.warning("[ChatService] Unsupported provider_type=%s", provider_type)
                        print(f"[ChatService] Unsupported provider_type={provider_type}")
                    except Exception:
                        pass
                return {
                    "success": False,
                    "error": f"Desteklenmeyen provider türü: {provider_type or 'undefined'}"
                }
            
            # Servisi yapılandır
            provider_service.set_api_key(api_key)
            provider_service.set_model(request_model_name)
            
            # Kullanıcı mesajını kaydet
            save_result = self.save_message(chat_id, user_message, True, model_id)
            if not save_result["success"]:
                return save_result
            
            # Konuşma geçmişini al
            history_result = self.get_chat_messages(chat_id, limit=20, user_id=user_id)
            conversation_history = []
            
            if history_result["success"]:
                # Son mesajı hariç tut (şu anki mesaj)
                messages = history_result["messages"][:-1]
                conversation_history = messages
            
            # Provider'dan yanıt al
            ai_result = provider_service.generate_content(
                prompt=user_message,
                conversation_history=conversation_history
            )
            
            if not ai_result["success"]:
                return {
                    "success": False,
                    "error": f"AI yanıtı alınamadı: {ai_result.get('error', 'Bilinmeyen hata')}"
                }
            
            ai_response = ai_result["content"]
            
            # AI yanıtını kaydet
            save_ai_result = self.save_message(chat_id, ai_response, False, model_id)
            if not save_ai_result["success"]:
                return save_ai_result
            
            
            return {
                "success": True,
                "user_message": user_message,
                "ai_response": ai_response,
                "model": model_name,  # kullanıcıya görünen isim
                "provider": provider_name,
                "usage": ai_result.get("usage", {}),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Mesaj gönderme hatası: {str(e)}"
            }
    
    def get_user_chats(self, user_id: int, active: Optional[bool] = True, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Kullanıcının chat'lerini al
        
        Args:
            limit (int): Maksimum chat sayısı
            offset (int): Başlangıç offset'i
            
        Returns:
            Dict[str, Any]: Chat listesi
        """
        try:
            rows = ChatRepository.list_user_chats(user_id=user_id, active=active, limit=limit, offset=offset)
            chats = []
            for row in (rows or []):
                chats.append({
                    "chat_id": row["chat_id"],
                    "model_id": row["model_id"],
                    "model_name": row.get("model_name"),
                    "provider_name": row.get("provider_name"),
                    "title": row["title"],
                    "is_active": bool(row["is_active"]),
                    "message_count": row.get("message_count"),
                    "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
                    "updated_at": row["updated_at"].isoformat() if row.get("updated_at") else None,
                    "last_message_at": row["last_message_at"].isoformat() if row.get("last_message_at") else None
                })
            return {"success": True, "chats": chats, "count": len(chats)}
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Chat listesi alma hatası: {str(e)}"
            }
    
    def delete_chat(self, chat_id: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Chat'i sil: mesaj yoksa kalıcı sil, varsa soft delete (is_active=FALSE)
        
        Args:
            chat_id (str): Chat ID'si
            
        Returns:
            Dict[str, Any]: Silme sonucu
        """
        try:
            # Önce sahiplik ve varlık kontrolü yap
            chat = ChatRepository.get_chat(chat_id)
            if not chat:
                return {"success": False, "error": "Chat bulunamadı"}
            if user_id is not None and chat.get("user_id") != user_id:
                return {"success": False, "error": "Yetkisiz"}

            msg_count = ChatRepository.count_messages(chat_id)
            if msg_count == 0:
                ok = ChatRepository.hard_delete(chat_id, user_id=user_id)
                if not ok:
                    return {"success": False, "error": "Chat silinemedi"}
            else:
                ok = ChatRepository.soft_delete(chat_id)
                if not ok:
                    return {"success": False, "error": "Chat arşivlenemedi"}

            return {"success": True, "message": "Chat silindi"}
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Chat silme hatası: {str(e)}"
            }
