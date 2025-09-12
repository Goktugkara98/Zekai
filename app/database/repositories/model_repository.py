# =============================================================================
# MODEL REPOSITORY
# =============================================================================
# Bu dosya, models tablosu için basit CRUD işlemlerini yönetir.
# =============================================================================

import logging
from app.database.db_connection import get_connection, get_cursor, execute_query

logger = logging.getLogger(__name__)

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
            INSERT INTO models (model_name, model_type, provider_name, provider_type, api_key, base_url, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            model_data.get('model_name'),
            model_data.get('model_type'),
            model_data.get('provider_name'),
            model_data.get('provider_type'),
            model_data.get('api_key'),
            model_data.get('base_url'),
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
            logger.info(f"Model oluşturuldu: {model_data.get('model_name')} (ID: {model_id})")
            return model_id
        except Exception as e:
            logger.error(f"Model oluşturma hatası: {str(e)}")
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
            logger.error(f"Tüm modelleri getirme hatası: {str(e)}")
            return []

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
            logger.error(f"Model ID {model_id} getirme hatası: {str(e)}")
            return None

    @staticmethod
    def update_model(model_id, model_data):
        """
        Belirli bir ID'ye sahip modeli günceller.
        """
        set_clauses = []
        params = []
        for key, value in model_data.items():
            if key in ['model_name', 'model_type', 'provider_name', 'api_key', 'is_active']:
                set_clauses.append(f"{key} = %s")
                params.append(value)
        
        if not set_clauses:
            logger.warning(f"Model ID {model_id} için güncellenecek veri bulunamadı.")
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
            logger.info(f"Model ID {model_id} güncellendi. Etkilenen satır: {affected_rows}")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"Model ID {model_id} güncelleme hatası: {str(e)}")
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
            logger.info(f"Model ID {model_id} silindi. Etkilenen satır: {affected_rows}")
            return affected_rows > 0
        except Exception as e:
            logger.error(f"Model ID {model_id} silme hatası: {str(e)}")
            if connection and connection.is_connected():
                connection.rollback()
                connection.close()
            return False