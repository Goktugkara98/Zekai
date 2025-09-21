# =============================================================================
# MODEL REPOSITORY
# =============================================================================
# Bu dosya, models tablosu için basit CRUD işlemlerini yönetir.
# =============================================================================

from app.database.db_connection import get_connection, get_cursor, execute_query

class ModelRepository:
    """
    Models tablosu için CRUD operasyonlarını yönetir.
    """

    @staticmethod
    def create_model(model_data):
        """
        Yeni bir model kaydı oluşturur.
        """
        query = """
            INSERT INTO models (model_name, request_model_name, model_type, provider_name, provider_type, api_key, base_url, logo_path, description, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            model_data.get('model_name'),  # display name
            model_data.get('request_model_name'),  # provider'a gönderilecek gerçek model id
            model_data.get('model_type'),
            model_data.get('provider_name'),
            model_data.get('provider_type'),
            model_data.get('api_key'),
            model_data.get('base_url'),
            model_data.get('logo_path'),
            model_data.get('description'),
            model_data.get('is_active', True)
        )
        try:
            connection = get_connection()
            cursor = get_cursor(connection)
            cursor.execute(query, params)
            connection.commit()
            model_id = cursor.lastrowid
            cursor.close()
            connection.close()
            return model_id
        except Exception as e:
            if connection and connection.is_connected():
                connection.rollback()
                connection.close()
            return None

    @staticmethod
    def get_all_models():
        """
        Tüm modelleri getirir.
        """
        query = "SELECT * FROM models"
        try:
            return execute_query(query)
        except Exception as e:
            return []

    @staticmethod
    def get_all_models_with_categories():
        """
        Tüm modelleri kategorileri ile birlikte getirir.
        Dönüş: [{...model cols..., categories: [{category_id, name}], primary_category: {category_id, name} | None }]
        """
        models = ModelRepository.get_all_models()
        if not models:
            return []

        model_ids = [row['model_id'] for row in models]
        cat_map = ModelRepository._get_categories_for_model_ids(model_ids)

        for m in models:
            m_categories = cat_map.get(m['model_id'], [])
            m['categories'] = m_categories
            # primary_category_id varsa nesnesini doldur
            primary = None
            try:
                pid = m.get('primary_category_id')
                if pid:
                    primary = next((c for c in m_categories if c['category_id'] == pid), None)
            except Exception:
                primary = None
            m['primary_category'] = primary
        return models

    @staticmethod
    def _get_categories_for_model_ids(model_ids):
        """
        Verilen model_id listesi için kategori listesini döndürür.
        Dönüş: { model_id: [ {category_id, name} ] }
        """
        if not model_ids:
            return {}
        # IN parametreleri için placeholder oluştur
        placeholders = ','.join(['%s'] * len(model_ids))
        query = f"""
            SELECT mc.model_id, c.category_id, c.name
            FROM model_categories mc
            INNER JOIN categories c ON c.category_id = mc.category_id
            WHERE mc.model_id IN ({placeholders})
            ORDER BY c.name ASC
        """
        try:
            rows = execute_query(query, tuple(model_ids), fetch=True)
            mapping = {}
            for r in rows:
                mid = r['model_id']
                mapping.setdefault(mid, []).append({
                    'category_id': r['category_id'],
                    'name': r['name']
                })
            return mapping
        except Exception as e:
            return {}

    @staticmethod
    def get_model_by_id(model_id):
        """
        Belirli bir ID'ye sahip modeli getirir.
        """
        query = "SELECT * FROM models WHERE model_id = %s"
        params = (model_id,)
        try:
            result = execute_query(query, params)
            return result[0] if result else None
        except Exception as e:
            return None

    @staticmethod
    def update_model(model_id, model_data):
        """
        Belirli bir ID'ye sahip modeli günceller.
        """
        set_clauses = []
        params = []
        for key, value in model_data.items():
            if key in ['model_name', 'request_model_name', 'model_type', 'provider_name', 'provider_type', 'api_key', 'base_url', 'logo_path', 'description', 'is_active']:
                set_clauses.append(f"{key} = %s")
                params.append(value)
        
        if not set_clauses:
            return False

        query = f"UPDATE models SET {', '.join(set_clauses)} WHERE model_id = %s"
        params.append(model_id)

        try:
            connection = get_connection()
            cursor = get_cursor(connection)
            cursor.execute(query, tuple(params))
            connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            connection.close()
            # rowcount 0 olabilir (değerler değişmemiş), bu durumda da işlem başarılı kabul edilir
            return affected_rows >= 0
        except Exception as e:
            if connection and connection.is_connected():
                connection.rollback()
                connection.close()
            return False

    @staticmethod
    def delete_model(model_id):
        """
        Belirli bir ID'ye sahip modeli siler.
        """
        query = "DELETE FROM models WHERE model_id = %s"
        params = (model_id,)
        try:
            connection = get_connection()
            cursor = get_cursor(connection)
            cursor.execute(query, params)
            connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            connection.close()
            return affected_rows > 0
        except Exception as e:
            if connection and connection.is_connected():
                connection.rollback()
                connection.close()
            return False