document.querySelectorAll('[data-copy]').forEach(function (b) {
  b.addEventListener('click', function () {
    navigator.clipboard.writeText(b.dataset.copy).then(function () {
      var o = b.innerHTML; b.textContent = 'Copied!'; setTimeout(function () { b.innerHTML = o; }, 1500);
    });
  });
});
(function () {
  var links = document.querySelectorAll('.tp-toc a'); if (!links.length || !('IntersectionObserver' in window)) return;
  var map = {}; links.forEach(function (l) { map[l.getAttribute('href').slice(1)] = l; });
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { links.forEach(function (l) { l.classList.remove('active'); }); map[e.target.id].classList.add('active'); } });
  }, { rootMargin: '-80px 0px -70% 0px' });
  Object.keys(map).forEach(function (id) { var el = document.getElementById(id); if (el) io.observe(el); });
})();
