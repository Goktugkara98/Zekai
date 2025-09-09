# =============================================================================
# MAIN ROUTES
# =============================================================================
# Bu dosya, ana sayfa rotalarını tanımlar.
# =============================================================================

from flask import Blueprint, render_template, request, jsonify
import logging

logger = logging.getLogger(__name__)

# Main Blueprint oluştur
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Ana sayfa.
    """
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Ana sayfa hatası: {str(e)}")
        return "Ana sayfa yüklenirken hata oluştu", 500

@main_bp.route('/chat')
def chat():
    """
    Chat sayfası.
    """
    try:
        return render_template('chat.html')
    except Exception as e:
        logger.error(f"Chat sayfası hatası: {str(e)}")
        return "Chat sayfası yüklenirken hata oluştu", 500
