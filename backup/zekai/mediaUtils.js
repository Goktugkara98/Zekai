/**
 * Medya Yardımcıları Modülü
 * =========================
 * @description Resim, ses gibi medya dosyalarını indirme veya
 * görüntüleme gibi işlemleri yapar.
 */
import { log } from './logger.js';

/**
 * Verilen bir URL'deki medyayı indirir.
 * @param {string} mediaSrc - Medyanın data-URL'i veya normal URL'i.
 * @param {string} defaultFileName - Varsayılan dosya adı.
 */
function downloadMedia(mediaSrc, defaultFileName = 'downloaded-media') {
    if (!mediaSrc || typeof mediaSrc !== 'string') {
        alert('İndirilecek medya kaynağı geçersiz.');
        return;
    }
    try {
        const link = document.createElement('a');
        link.href = mediaSrc;
        
        // Dosya adını ve uzantısını belirle
        let fileName = defaultFileName;
        if (mediaSrc.startsWith('data:')) {
            const mimeType = mediaSrc.substring(mediaSrc.indexOf(':') + 1, mediaSrc.indexOf(';'));
            const extension = mimeType.split('/')[1] || 'bin';
            fileName = `${defaultFileName}-${Date.now()}.${extension}`;
        } else {
            try {
                const url = new URL(mediaSrc);
                const pathName = url.pathname;
                const lastSegment = pathName.substring(pathName.lastIndexOf('/') + 1);
                if (lastSegment) fileName = lastSegment;
            } catch (e) { /* URL geçersizse varsayılan adı kullan */ }
        }

        link.download = fileName;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        log('action', 'MediaUtils', 'Medya indirildi.', { source: mediaSrc, fileName });
    } catch (error) {
        log('error', 'MediaUtils', 'Medya indirilirken hata!', error);
        alert(`Medya indirilemedi: ${error.message}`);
    }
}

/**
 * Bir resmi indirir.
 * @param {string} imageData - Resmin data-URL'i.
 */
export function downloadImage(imageData) {
    downloadMedia(imageData, 'ai-image');
}

/**
 * Bir ses dosyasını indirir.
 * @param {string} audioData - Sesin data-URL'i.
 */
export function downloadAudio(audioData) {
    downloadMedia(audioData, 'ai-audio');
}

/**
 * Bir resmi tam ekran modal içinde gösterir.
 * @param {string} imageData - Resmin data-URL'i.
 */
export function viewFullImage(imageData) {
    if (!imageData || typeof imageData !== 'string') {
        alert('Görüntülenecek resim geçersiz.');
        return;
    }
    
    // Mevcut modal varsa kaldır
    document.querySelector('.image-modal-zk')?.remove();

    const modal = document.createElement('div');
    modal.className = 'image-modal-zk';
    modal.style.cssText = `
        position:fixed; top:0; left:0; width:100%; height:100%;
        background-color:rgba(0,0,0,0.85); display:flex; align-items:center;
        justify-content:center; z-index:2000; padding:20px; box-sizing:border-box;
        opacity:0; transition: opacity 0.3s ease;
    `;
    modal.innerHTML = `
        <div style="max-width:90vw; max-height:90vh; position:relative; transform: scale(0.9); transition: transform 0.3s ease;">
            <img src="${imageData}" alt="Tam Ekran Resim" style="max-width:100%; max-height:100%; display:block; border-radius:8px; box-shadow:0 0 25px rgba(0,0,0,0.5);">
            <button title="Kapat (Esc)" style="position:absolute; top: -15px; right: -15px; background:white; color: black; border:none; border-radius:50%; width:30px; height:30px; font-size:20px; cursor:pointer; display:flex; align-items:center; justify-content:center; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">&times;</button>
        </div>
    `;

    const closeModal = () => {
        modal.style.opacity = '0';
        modal.querySelector('div').style.transform = 'scale(0.9)';
        setTimeout(() => {
            modal.remove();
            document.removeEventListener('keydown', handleEscapeKey);
        }, 300);
    };

    const handleEscapeKey = (e) => {
        if (e.key === 'Escape') closeModal();
    };

    modal.addEventListener('click', (e) => {
        // Sadece arka plana veya kapatma butonuna tıklanırsa kapat
        if (e.target === modal || e.target.tagName === 'BUTTON' || e.target.innerHTML === '×') {
            closeModal();
        }
    });

    document.addEventListener('keydown', handleEscapeKey);
    document.body.appendChild(modal);

    // Animasyon için
    requestAnimationFrame(() => {
        modal.style.opacity = '1';
        modal.querySelector('div').style.transform = 'scale(1)';
    });
}
