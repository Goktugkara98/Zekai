# =============================================================================
# CHAT SERVICE
# =============================================================================
# Bu dosya, chat işlemlerini yönetir ve veritabanı ile haberleşir.
# =============================================================================

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.database.db_connection import execute_query
from app.services.provider_factory import ProviderFactory

logger = logging.getLogger(__name__)

class ChatService:
    """
    Chat işlemleri servisi
    """
    
    def __init__(self):
        self.provider_factory = ProviderFactory()
        
    def create_chat(self, model_id: int, title: str = None) -> Dict[str, Any]:
        """
        Yeni chat oluştur
        
        Args:
            model_id (int): Model ID'si
            title (str): Chat başlığı (opsiyonel)
            
        Returns:
            Dict[str, Any]: Oluşturulan chat bilgileri
        """
        try:
            chat_id = str(uuid.uuid4())
            
            # Chat'i veritabanına kaydet
            insert_sql = """
                INSERT INTO chats (chat_id, model_id, title, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            execute_query(insert_sql, (
                chat_id,
                model_id,
                title,
                True,
                datetime.now()
            ), fetch=False)
            
            logger.info(f"Yeni chat oluşturuldu: {chat_id}")
            
            return {
                "success": True,
                "chat_id": chat_id,
                "model_id": model_id,
                "title": title,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Chat oluşturma hatası: {str(e)}")
            return {
                "success": False,
                "error": f"Chat oluşturma hatası: {str(e)}"
            }
    
    def get_chat(self, chat_id: str) -> Dict[str, Any]:
        """
        Chat bilgilerini al
        
        Args:
            chat_id (str): Chat ID'si
            
        Returns:
            Dict[str, Any]: Chat bilgileri
        """
        try:
            select_sql = """
                SELECT c.*, m.model_name, m.provider_name, m.provider_type
                FROM chats c
                LEFT JOIN models m ON c.model_id = m.model_id
                WHERE c.chat_id = %s
            """
            
            result = execute_query(select_sql, (chat_id,), fetch=True)
            
            if result:
                chat = result[0]
                return {
                    "success": True,
                    "chat": {
                        "chat_id": chat["chat_id"],
                        "model_id": chat["model_id"],
                        "model_name": chat["model_name"],
                        "provider_name": chat["provider_name"],
                        "provider_type": chat["provider_type"],
                        "title": chat["title"],
                        "is_active": chat["is_active"],
                        "created_at": chat["created_at"].isoformat() if chat["created_at"] else None,
                        "updated_at": chat["updated_at"].isoformat() if chat["updated_at"] else None,
                        "last_message_at": chat["last_message_at"].isoformat() if chat["last_message_at"] else None
                    }
                }
            else:
                return {
                    "success": False,
                    "error": "Chat bulunamadı"
                }
                
        except Exception as e:
            logger.error(f"Chat alma hatası: {str(e)}")
            return {
                "success": False,
                "error": f"Chat alma hatası: {str(e)}"
            }
    
    def get_chat_messages(self, chat_id: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
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
            select_sql = """
                SELECT message_id, content, is_user, timestamp, created_at
                FROM messages
                WHERE chat_id = %s
                ORDER BY created_at ASC
                LIMIT %s OFFSET %s
            """
            
            result = execute_query(select_sql, (chat_id, limit, offset), fetch=True)
            
            messages = []
            for row in result:
                messages.append({
                    "message_id": row["message_id"],
                    "content": row["content"],
                    "is_user": bool(row["is_user"]),
                    "timestamp": row["timestamp"].isoformat() if row["timestamp"] else None,
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None
                })
            
            return {
                "success": True,
                "messages": messages,
                "count": len(messages)
            }
            
        except Exception as e:
            logger.error(f"Mesaj alma hatası: {str(e)}")
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
            insert_sql = """
                INSERT INTO messages (chat_id, model_id, content, is_user, timestamp, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            now = datetime.now()
            execute_query(insert_sql, (
                chat_id,
                model_id,
                content,
                is_user,
                now,
                now
            ), fetch=False)
            
            # Chat'in son mesaj zamanını güncelle
            update_chat_sql = """
                UPDATE chats 
                SET last_message_at = %s, updated_at = %s
                WHERE chat_id = %s
            """
            
            execute_query(update_chat_sql, (now, now, chat_id), fetch=False)
            
            logger.info(f"Mesaj kaydedildi: chat_id={chat_id}, is_user={is_user}")
            
            return {
                "success": True,
                "message": "Mesaj başarıyla kaydedildi"
            }
            
        except Exception as e:
            logger.error(f"Mesaj kaydetme hatası: {str(e)}")
            return {
                "success": False,
                "error": f"Mesaj kaydetme hatası: {str(e)}"
            }
    
    def send_message(self, chat_id: str, user_message: str, model_id: int, api_key: str) -> Dict[str, Any]:
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
            # Model bilgilerini al
            model_sql = """
                SELECT model_name, provider_name 
                FROM models 
                WHERE model_id = %s
            """
            model_result = execute_query(model_sql, (model_id,), fetch=True)
            
            if not model_result:
                return {
                    "success": False,
                    "error": "Model bulunamadı"
                }
            
            model_data = model_result[0]
            model_name = model_data["model_name"]
            provider_name = model_data["provider_name"]
            
            # Provider type'ı provider_name'den belirle
            if provider_name == 'Google':
                provider_type = 'gemini'
            elif provider_name == 'OpenRouter':
                provider_type = 'openrouter'
            else:
                provider_type = 'unknown'
            
            # Provider servisini al
            provider_service = self.provider_factory.get_service(provider_type)
            if not provider_service:
                return {
                    "success": False,
                    "error": f"Desteklenmeyen provider türü: {provider_type}"
                }
            
            # Servisi yapılandır
            provider_service.set_api_key(api_key)
            provider_service.set_model(model_name)
            
            # Kullanıcı mesajını kaydet
            save_result = self.save_message(chat_id, user_message, True, model_id)
            if not save_result["success"]:
                return save_result
            
            # Konuşma geçmişini al
            history_result = self.get_chat_messages(chat_id, limit=20)
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
            
            logger.info(f"Mesaj işlendi: chat_id={chat_id}, provider={provider_name}")
            
            return {
                "success": True,
                "user_message": user_message,
                "ai_response": ai_response,
                "model": model_name,
                "provider": provider_name,
                "usage": ai_result.get("usage", {}),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mesaj gönderme hatası: {str(e)}")
            return {
                "success": False,
                "error": f"Mesaj gönderme hatası: {str(e)}"
            }
    
    def get_user_chats(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """
        Kullanıcının chat'lerini al
        
        Args:
            limit (int): Maksimum chat sayısı
            offset (int): Başlangıç offset'i
            
        Returns:
            Dict[str, Any]: Chat listesi
        """
        try:
            select_sql = """
                SELECT c.*, m.model_name, m.provider_name,
                       (SELECT COUNT(*) FROM messages WHERE chat_id = c.chat_id) as message_count
                FROM chats c
                LEFT JOIN models m ON c.model_id = m.model_id
                WHERE c.is_active = TRUE
                ORDER BY c.last_message_at DESC, c.created_at DESC
                LIMIT %s OFFSET %s
            """
            
            result = execute_query(select_sql, (limit, offset), fetch=True)
            
            chats = []
            for row in result:
                chats.append({
                    "chat_id": row["chat_id"],
                    "model_id": row["model_id"],
                    "model_name": row["model_name"],
                    "provider_name": row["provider_name"],
                    "title": row["title"],
                    "is_active": bool(row["is_active"]),
                    "message_count": row["message_count"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                    "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
                    "last_message_at": row["last_message_at"].isoformat() if row["last_message_at"] else None
                })
            
            return {
                "success": True,
                "chats": chats,
                "count": len(chats)
            }
            
        except Exception as e:
            logger.error(f"Chat listesi alma hatası: {str(e)}")
            return {
                "success": False,
                "error": f"Chat listesi alma hatası: {str(e)}"
            }
    
    def delete_chat(self, chat_id: str) -> Dict[str, Any]:
        """
        Chat'i sil (soft delete)
        
        Args:
            chat_id (str): Chat ID'si
            
        Returns:
            Dict[str, Any]: Silme sonucu
        """
        try:
            # Chat'i deaktive et
            update_sql = "UPDATE chats SET is_active = FALSE, updated_at = %s WHERE chat_id = %s"
            execute_query(update_sql, (datetime.now(), chat_id), fetch=False)
            
            logger.info(f"Chat silindi: {chat_id}")
            
            return {
                "success": True,
                "message": "Chat başarıyla silindi"
            }
            
        except Exception as e:
            logger.error(f"Chat silme hatası: {str(e)}")
            return {
                "success": False,
                "error": f"Chat silme hatası: {str(e)}"
            }
