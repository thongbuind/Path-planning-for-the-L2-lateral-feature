/* Lõi: hằng số và hàm dùng chung. Dữ liệu của một lượt chạy đến từng chu kỳ từ server (xem ui.js). */
(() => {
  'use strict';
  const PP = (window.PP = {});

  PP.FN = ['NONE', 'LCC', 'LKA', 'ELK'];
  PP.FN_VAR = ['--none', '--hwa', '--lka', '--elk'];

  PP.clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  PP.lerp = (a, b, u) => a + (b - a) * u;

  // Số kiểu Việt: dấu phẩy thập phân, dấu trừ đúng.
  PP.f = (x, nd = 1) => {
    if (x == null || !isFinite(x)) return '—';
    if (Math.abs(x) < 0.5 * Math.pow(10, -nd)) x = 0;
    return (document.documentElement.lang === 'en' ? x.toFixed(nd) : x.toFixed(nd).replace('.', ',')).replace('-', '−');
  };
  PP.fs = (x, nd = 0) => { // có dấu + khi dương
    const s = PP.f(x, nd);
    return x != null && isFinite(x) && x > 0 && s !== '0' && s !== '0,0' ? '+' + s : s;
  };
  PP.vn = (s) => document.documentElement.lang === 'en' ? String(s).replace(/(\d),(\d)/g, '$1.$2') : String(s).replace(/(\d)\.(\d)/g, '$1,$2');
  PP.limit = (s) => PP.vn(String(s).replace('<=', '≤').replace('>=', '≥'));
})();
