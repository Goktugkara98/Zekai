(function(){
  'use strict';
  function fitLogoBox(box, img, maxW = 180, maxH = 56) {
    if (!box) return;
    function compute() {
      try {
        if (!img || !img.naturalWidth || !img.naturalHeight) {
          // fallback to square box
          box.style.width = maxH + 'px';
          box.style.height = maxH + 'px';
          return;
        }
        const r = img.naturalWidth / img.naturalHeight;
        // Try height-limited first (preferred)
        let w = Math.min(maxW, (maxH - 2) * r + 2);
        let h = maxH;
        if (w > maxW) {
          // Fall back to width-limited
          w = maxW;
          h = Math.min(maxH, (maxW - 2) / r + 2);
        }
        box.style.width = Math.round(w) + 'px';
        box.style.height = Math.round(h) + 'px';
      } catch (_) {}
    }
    if (img && !img.complete) {
      img.addEventListener('load', compute, { once: true });
    }
    compute();
    window.addEventListener('resize', compute);
  }
  window.LogoFit = { fitLogoBox };
})();
