(function(){
  'use strict';

  function notify(type, message) {
    try {
      if (window.AdminUI && typeof window.AdminUI.showToast === 'function') {
        window.AdminUI.showToast(message, type);
        return;
      }
    } catch (_) {}
    try { alert(message); } catch (_) {}
  }

  async function fetchBranding() {
    const res = await fetch('/admin/api/branding', { credentials: 'same-origin' });
    const data = await res.json().catch(() => ({}));
    if (!res.ok || !data.success) throw new Error(data.error || 'Ayarlar yüklenemedi');
    return data.data || {};
  }

  function getSelectedVariant() {
    var radios = document.getElementsByName('variant');
    for (var i = 0; i < radios.length; i++) {
      if (radios[i] && radios[i].checked) return radios[i].value;
    }
    return 'text';
  }

  function updatePreviewVariant() {
    var variant = getSelectedVariant();
    var logoImg = document.getElementById('previewLogoImg');
    var logoIcon = document.getElementById('previewLogoIcon');
    var text = document.getElementById('previewBrandText');
    if (!logoImg || !logoIcon || !text) return;

    if (variant === 'logo') {
      text.style.display = 'none';
      if (logoImg.src) {
        logoImg.style.display = 'inline-block';
        logoIcon.style.display = 'none';
      } else {
        logoImg.style.display = 'none';
        logoIcon.style.display = 'inline-block';
      }
    } else if (variant === 'logo+text') {
      text.style.display = 'inline-block';
      if (logoImg.src) {
        logoImg.style.display = 'inline-block';
        logoIcon.style.display = 'none';
      } else {
        logoImg.style.display = 'none';
        logoIcon.style.display = 'inline-block';
      }
    } else {
      text.style.display = 'inline-block';
      logoImg.style.display = 'none';
      logoIcon.style.display = 'none';
    }
  }

  function updatePreviewTheme() {
    var isDark = !!(document.getElementById('preview_dark_toggle') && document.getElementById('preview_dark_toggle').checked);
    var wrap = document.getElementById('previewWrap');
    var head = document.getElementById('previewSidebarLogo');
    var txt = document.getElementById('previewBrandText');
    if (!wrap || !head || !txt) return;
    var tLight = (document.getElementById('text_color_light') && document.getElementById('text_color_light').value) || '#0f172a';
    var tDark = (document.getElementById('text_color_dark') && document.getElementById('text_color_dark').value) || '#e8eaf0';
    var bLight = (document.getElementById('border_color_light') && document.getElementById('border_color_light').value) || '#e5e7eb';
    var bDark = (document.getElementById('border_color_dark') && document.getElementById('border_color_dark').value) || '#243049';
    if (isDark) {
      wrap.style.background = '#111a2e';
      wrap.style.borderColor = '#243049';
      head.style.borderBottomColor = bDark;
      txt.style.color = tDark;
    } else {
      wrap.style.background = '#ffffff';
      wrap.style.borderColor = '#e5e7eb';
      head.style.borderBottomColor = bLight;
      txt.style.color = tLight;
    }
  }

  function applyLivePreview() {
    var input = document.getElementById('brand_text');
    var txt = document.getElementById('previewBrandText');
    if (input && txt) {
      txt.textContent = input.value || 'zekai';
    }
    updatePreviewVariant();
    updatePreviewTheme();
  }

  function onVariantChange() {
    var v = getSelectedVariant();
    var row = document.getElementById('brandTextRow');
    if (row) row.style.display = (v === 'text' || v === 'logo+text') ? 'block' : 'none';
    updatePreviewVariant();
    updatePreviewTheme();
  }

  function applyBrandingToForm(b) {
    var variant = b.variant || 'text';
    var vLogo = document.getElementById('variant_logo');
    var vLogoText = document.getElementById('variant_logo_text');
    var vText = document.getElementById('variant_text');
    if (vLogo) vLogo.checked = (variant === 'logo');
    if (vLogoText) vLogoText.checked = (variant === 'logo+text');
    if (vText) vText.checked = (variant === 'text');

    var brandTextEl = document.getElementById('brand_text');
    if (brandTextEl) brandTextEl.value = b.brand_text || 'zekai';
    var tcl = document.getElementById('text_color_light'); if (tcl) tcl.value = b.text_color_light || '#0f172a';
    var tcd = document.getElementById('text_color_dark'); if (tcd) tcd.value = b.text_color_dark || '#e8eaf0';
    var bcl = document.getElementById('border_color_light'); if (bcl) bcl.value = b.border_color_light || '#e5e7eb';
    var bcd = document.getElementById('border_color_dark'); if (bcd) bcd.value = b.border_color_dark || '#243049';

    var prev = document.getElementById('logoPreview');
    var previewLogoImg = document.getElementById('previewLogoImg');
    var previewLogoIcon = document.getElementById('previewLogoIcon');
    if (prev && previewLogoImg && previewLogoIcon) {
      if (b.logo_path) {
        prev.src = '/static/' + String(b.logo_path).replace(/^\/?static\/?/, '');
        prev.style.display = 'inline-block';
        previewLogoImg.src = prev.src;
        previewLogoImg.style.display = 'inline-block';
        previewLogoIcon.style.display = 'none';
      } else {
        prev.src = '';
        prev.style.display = 'none';
        previewLogoImg.src = '';
        previewLogoImg.style.display = 'none';
        previewLogoIcon.style.display = 'inline-block';
      }
    }

    var previewBrandText = document.getElementById('previewBrandText');
    if (previewBrandText) previewBrandText.textContent = b.brand_text || 'zekai';

    var row = document.getElementById('brandTextRow');
    if (row) row.style.display = (variant === 'text' || variant === 'logo+text') ? 'block' : 'none';

    updatePreviewVariant();
    updatePreviewTheme();
  }

  async function uploadLogo() {
    try {
      const fileInput = document.getElementById('logo_file');
      if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
        notify('warning', 'Lütfen bir dosya seçin');
        return;
      }
      const fd = new FormData();
      fd.append('logo', fileInput.files[0]);
      const res = await fetch('/admin/api/branding/logo', { method: 'POST', body: fd, credentials: 'same-origin' });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.success) throw new Error(data.error || 'Yükleme başarısız');
      const url = (data.data && data.data.logo_url) || '';
      var logoPreview = document.getElementById('logoPreview');
      var previewLogoImg = document.getElementById('previewLogoImg');
      var previewLogoIcon = document.getElementById('previewLogoIcon');
      if (logoPreview && previewLogoImg && previewLogoIcon) {
        logoPreview.src = url;
        logoPreview.style.display = 'inline-block';
        previewLogoImg.src = url;
        previewLogoImg.style.display = 'inline-block';
        previewLogoIcon.style.display = 'none';
      }
      notify('success', 'Logo yüklendi');
      updatePreviewVariant();
      updatePreviewTheme();
    } catch (e) {
      notify('error', (e && e.message) || 'Logo yüklenemedi');
    }
  }

  async function saveBranding(ev) {
    if (ev && ev.preventDefault) ev.preventDefault();
    if (window.__savingBranding) return false;
    window.__savingBranding = true;
    const btn = document.getElementById('btnSaveBranding');
    const html = btn ? btn.innerHTML : '';
    let restoreTimer = null;
    if (btn) {
      restoreTimer = setTimeout(function(){
        try { btn.disabled = false; btn.innerHTML = html; } catch(_) {}
        window.__savingBranding = false;
      }, 8000);
    }
    try {
      const payload = {
        variant: getSelectedVariant(),
        brand_text: (document.getElementById('brand_text') && document.getElementById('brand_text').value) || 'zekai',
        text_color_light: (document.getElementById('text_color_light') && document.getElementById('text_color_light').value) || '#0f172a',
        text_color_dark: (document.getElementById('text_color_dark') && document.getElementById('text_color_dark').value) || '#e8eaf0',
        border_color_light: (document.getElementById('border_color_light') && document.getElementById('border_color_light').value) || '#e5e7eb',
        border_color_dark: (document.getElementById('border_color_dark') && document.getElementById('border_color_dark').value) || '#243049',
      };
      if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Kaydediliyor...'; }
      const res = await fetch('/admin/api/branding', { method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'same-origin', body: JSON.stringify(payload) });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.success) throw new Error(data.error || 'Kaydedilemedi');
      notify('success', 'Ayarlar kaydedildi');
      try {
        const latest = await fetchBranding();
        applyBrandingToForm(latest);
      } catch (_) {}
      updatePreviewVariant();
      updatePreviewTheme();
    } catch (e) {
      notify('error', (e && e.message) || 'Kaydetme başarısız');
    } finally {
      if (restoreTimer) { try { clearTimeout(restoreTimer); } catch(_) {} }
      if (btn) { btn.disabled = false; btn.innerHTML = html; }
      window.__savingBranding = false;
    }
    return false;
  }

  function bindEvents() {
    var btnSave = document.getElementById('btnSaveBranding');
    if (btnSave) btnSave.addEventListener('click', saveBranding);

    var darkToggle = document.getElementById('preview_dark_toggle');
    if (darkToggle) darkToggle.addEventListener('change', updatePreviewTheme);

    ['variant_logo','variant_logo_text','variant_text'].forEach(function(id){
      var el = document.getElementById(id);
      if (el) el.addEventListener('change', onVariantChange);
    });

    var brandText = document.getElementById('brand_text');
    if (brandText) brandText.addEventListener('input', applyLivePreview);

    ;['text_color_light','text_color_dark','border_color_light','border_color_dark'].forEach(function(id){
      var el = document.getElementById(id);
      if (el) el.addEventListener('change', applyLivePreview);
    });

    var uploadBtn = document.getElementById('logo_file');
    var uploadTriggerBtn = document.querySelector('button.btn-outline-primary');
    if (uploadTriggerBtn) uploadTriggerBtn.addEventListener('click', function(e){ e.preventDefault(); uploadLogo(); });
  }

  async function initBrandingPage() {
    bindEvents();
    // Initialize from current form values first
    try {
      if (!document.querySelector('input[name="variant"]:checked')) {
        var def = document.getElementById('variant_text');
        if (def) def.checked = true;
      }
    } catch(_) {}
    applyLivePreview();
    // Then fetch saved settings and apply
    try {
      const b = await fetchBranding();
      applyBrandingToForm(b);
    } catch (e) {
      notify('error', (e && e.message) || 'Ayarlar yüklenemedi');
    }
  }

  function runOnce() {
    if (window.__brandingInitDone) return;
    window.__brandingInitDone = true;
    initBrandingPage();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', runOnce);
  } else {
    runOnce();
  }
  window.addEventListener('load', runOnce);

  // Expose to global scope for inline HTML handlers
  try {
    window.onVariantChange = onVariantChange;
    window.applyLivePreview = applyLivePreview;
    window.saveBranding = saveBranding;
    window.uploadLogo = uploadLogo;
  } catch (_) {}
})();
