# =============================================================================
# ROUTES PACKAGE
# =============================================================================
# Bu paket, uygulama rotalarını içerir.
# =============================================================================

def register_blueprints(app):
    """
    Tüm blueprint'leri merkezi bir yerden kaydeder.
    import işlemleri fonksiyon içinde yapılır ki dairesel import ve yükleme sırası sorunları oluşmasın.
    """
    # Pages (HTML render eden sayfalar)
    from .pages.home import main_bp
    from .pages.auth import auth_bp
    from .pages.admin import admin_bp
    # API
    from .api.models import models_bp
    from .api.healthcheck import health_bp
    from .api.chats import chats_bp
    from .api.categories import categories_bp
    from .api.recommendations import recommendations_bp
    from .api.admin import admin_api_bp

    # Blueprint'leri kaydet
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(models_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(chats_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_api_bp)

__all__ = ['register_blueprints']