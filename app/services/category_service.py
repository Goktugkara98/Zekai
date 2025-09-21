# =============================================================================
# CATEGORY SERVICE
# =============================================================================
# Kategoriler ve kategoriye göre modeller için servis katmanı
# =============================================================================

from typing import Dict, Any
from app.database.repositories.category_repository import CategoryRepository


class CategoryService:
    def get_all_categories(self) -> Dict[str, Any]:
        try:
            categories = CategoryRepository.get_all_categories()
            return {
                'success': True,
                'data': categories,
                'count': len(categories)
            }
        except Exception as e:
            return { 'success': False, 'error': 'Kategoriler getirilemedi' }

    def get_models_by_category(self, category_id: int) -> Dict[str, Any]:
        try:
            models = CategoryRepository.get_models_by_category(category_id)
            return {
                'success': True,
                'data': models,
                'count': len(models)
            }
        except Exception as e:
            return { 'success': False, 'error': 'Kategori modelleri getirilemedi' }

    def get_category(self, category_id: int) -> Dict[str, Any]:
        try:
            category = CategoryRepository.get_category_by_id(category_id)
            if category:
                return {
                    'success': True,
                    'data': category
                }
            else:
                return { 'success': False, 'error': 'Kategori bulunamadı' }
        except Exception as e:
            return { 'success': False, 'error': 'Kategori getirilemedi' }

    def create_category(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            name = data.get('name', '').strip()
            if not name:
                return { 'success': False, 'error': 'Kategori adı zorunludur' }
            
            description = data.get('description', '').strip()
            slug = data.get('slug', '').strip()
            
            # Slug oluştur (eğer verilmemişse)
            if not slug:
                import re
                slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
            
            category_id = CategoryRepository.create_category(name, slug, description)
            return {
                'success': True,
                'data': { 'category_id': category_id },
                'message': 'Kategori başarıyla oluşturuldu'
            }
        except Exception as e:
            return { 'success': False, 'error': 'Kategori oluşturulamadı' }

    def update_category(self, category_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            name = data.get('name', '').strip()
            if not name:
                return { 'success': False, 'error': 'Kategori adı zorunludur' }
            
            description = data.get('description', '').strip()
            slug = data.get('slug', '').strip()
            
            # Slug oluştur (eğer verilmemişse)
            if not slug:
                import re
                slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
            
            success = CategoryRepository.update_category(category_id, name, slug, description)
            if success:
                return {
                    'success': True,
                    'message': 'Kategori başarıyla güncellendi'
                }
            else:
                return { 'success': False, 'error': 'Kategori güncellenemedi' }
        except Exception as e:
            return { 'success': False, 'error': 'Kategori güncellenemedi' }

    def delete_category(self, category_id: int) -> Dict[str, Any]:
        try:
            success = CategoryRepository.delete_category(category_id)
            if success:
                return {
                    'success': True,
                    'message': 'Kategori başarıyla silindi'
                }
            else:
                return { 'success': False, 'error': 'Kategori silinemedi' }
        except Exception as e:
            return { 'success': False, 'error': 'Kategori silinemedi' }
