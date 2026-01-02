
function loadES5() {
  var el = document.createElement('script');
  el.src = '/knx_static/frontend_es5/entrypoint.8dd12dce9bb99307.js';
  document.body.appendChild(el);
}
if (/.*Version\/(?:11|12)(?:\.\d+)*.*Safari\//.test(navigator.userAgent)) {
    loadES5();
} else {
  try {
    new Function("import('/knx_static/frontend_latest/entrypoint.a32c292ae6dd6cf9.js')")();
  } catch (err) {
    loadES5();
  }
}
  