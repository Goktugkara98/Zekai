'use strict';
// Silence all console output for chat application
(function(){
  try {
    const noop = function(){};
    if (typeof window !== 'undefined' && typeof window.console !== 'undefined') {
      ['log','warn','error','debug','info','trace'].forEach(fn => {
        if (console && typeof console[fn] === 'function') {
          console[fn] = noop;
        }
      });
    }
  } catch (_) {}
})();
