# =============================================================================
# MODEL SERVICE
# =============================================================================
# Bu dosya, model işlemleri için servis sınıfını tanımlar.
# =============================================================================

from typing import List, Dict, Any, Optional
from app.database.repositories.model_repository import ModelRepository

class ModelService:
    """
    Model işlemleri için servis sınıfı.
    """
    
    def get_all_models(self) -> Dict[str, Any]:
        """
        Tüm modelleri getirir.
        
        Returns:
            Dict[str, Any]: Başarı durumu ve model listesi
        """
        try:
            models = ModelRepository.get_all_models_with_categories()
            return {
                'success': True,
                'data': models,
                'count': len(models)
            }
        except Exception as e:
            return {
                'success': False,
                'error': 'Modeller getirilemedi'
            }
    
    def get_model_by_id(self, model_id: int) -> Dict[str, Any]:
        """
        ID'ye göre model getirir.
        
        Args:
            model_id: Model ID'si
            
        Returns:
            Dict[str, Any]: Başarı durumu ve model verisi
        """
        try:
            model = ModelRepository.get_model_by_id(model_id)
            if model:
                return {
                    'success': True,
                    'data': model
                }
            else:
                return {
                    'success': False,
                    'error': 'Model bulunamadı'
                }
        except Exception as e:
            return {
                'success': False,
                'error': 'Model getirilemedi'
            }
    
    def create_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Yeni model oluşturur.
        
        Args:
            data: Model verisi
            
        Returns:
            Dict[str, Any]: Başarı durumu ve sonuç
        """
        try:
            # Gerekli alanları kontrol et
            if not data or 'model_name' not in data:
                return {
                    'success': False,
                    'error': 'model_name alanı gereklidir'
                }
            
            # Model oluştur
            model_id = ModelRepository.create_model(data)
            
            if model_id:
                return {
                    'success': True,
                    'data': {'model_id': model_id},
                    'message': 'Model başarıyla oluşturuldu'
                }
            else:
                return {
                    'success': False,
                    'error': 'Model oluşturulamadı'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': 'Model oluşturulamadı'
            }
    
    def update_model(self, model_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Model günceller.
        
        Args:
            model_id: Model ID'si
            data: Güncellenecek veri
            
        Returns:
            Dict[str, Any]: Başarı durumu ve sonuç
        """
        try:
            if not data:
                return {
                    'success': False,
                    'error': 'Güncellenecek veri gönderilmedi'
                }
            
            # Model güncelle
            success = ModelRepository.update_model(model_id, data)
            
            if success:
                return {
                    'success': True,
                    'message': 'Model başarıyla güncellendi'
                }
            else:
                return {
                    'success': False,
                    'error': 'Model güncellenemedi'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': 'Model güncellenemedi'
            }
    
    def delete_model(self, model_id: int) -> Dict[str, Any]:
        """
        Model siler.
        
        Args:
            model_id: Model ID'si
            
        Returns:
            Dict[str, Any]: Başarı durumu ve sonuç
        """
        try:
            success = ModelRepository.delete_model(model_id)
            
            if success:
                return {
                    'success': True,
                    'message': 'Model başarıyla silindi'
                }
            else:
                return {
                    'success': False,
                    'error': 'Model silinemedi'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': 'Model silinemedi'
            }
