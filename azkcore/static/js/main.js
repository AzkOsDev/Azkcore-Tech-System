/* ==========================================================
   Vantage Point — vanilla JS
   Solo interactividad. Todo el contenido vive en index.html.
   ========================================================== */

document.getElementById('year').textContent = new Date().getFullYear();

/* ---------------------------------------------------------
   1. Header: cambia de estilo al hacer scroll
--------------------------------------------------------- */
const header = document.getElementById('site-header');
const onScrollHeader = () => {
  header.classList.toggle('scrolled', window.scrollY > 12);
};
onScrollHeader();
window.addEventListener('scroll', onScrollHeader, { passive: true });

/* ---------------------------------------------------------
   2. Menú móvil
--------------------------------------------------------- */
const menuBtn = document.getElementById('menu-btn');
const mobileMenu = document.getElementById('mobile-menu');
menuBtn.addEventListener('click', () => {
  mobileMenu.classList.toggle('hidden');
});
mobileMenu.querySelectorAll('a').forEach(a =>
  a.addEventListener('click', () => mobileMenu.classList.add('hidden'))
);

/* ---------------------------------------------------------
   3. Hero: retícula de puntos generada (firma visual del hero)
--------------------------------------------------------- */
(function buildScanGrid() {
  const svg = document.getElementById('scan-grid');
  if (!svg) return;
  const ns = 'http://www.w3.org/2000/svg';
  const cols = 26, rows = 14;
  const w = 1000, h = 560;
  svg.setAttribute('viewBox', `0 0 ${w} ${h}`);

  for (let r = 0; r <= rows; r++) {
    for (let c = 0; c <= cols; c++) {
      const x = (c / cols) * w;
      const y = (r / rows) * h;
      const dot = document.createElementNS(ns, 'circle');
      dot.setAttribute('cx', x);
      dot.setAttribute('cy', y);
      dot.setAttribute('r', 1.15);
      dot.setAttribute('fill', 'currentColor');
      dot.style.color = '#1B2431';
      svg.appendChild(dot);
    }
  }
  // líneas finas de estructura
  [0.25, 0.5, 0.75].forEach(f => {
    const line = document.createElementNS(ns, 'line');
    line.setAttribute('x1', 0); line.setAttribute('x2', w);
    line.setAttribute('y1', h * f); line.setAttribute('y2', h * f);
    line.setAttribute('stroke', '#131B27');
    line.setAttribute('stroke-width', '1');
    svg.appendChild(line);
  });
})();

/* ---------------------------------------------------------
   4. Servicios: expandir / colapsar al hacer clic
--------------------------------------------------------- */
document.querySelectorAll('.service-row').forEach(row => {
  row.addEventListener('click', () => row.classList.toggle('open'));
});

/* ---------------------------------------------------------
   5. FAQ: acordeón (una pregunta abierta a la vez)
--------------------------------------------------------- */
const faqList = document.getElementById('faq-list');
if (faqList) {
  faqList.querySelectorAll('.faq-item').forEach(item => {
    item.querySelector('.faq-q').addEventListener('click', () => {
      const wasOpen = item.classList.contains('open');
      faqList.querySelectorAll('.faq-item.open').forEach(o => o.classList.remove('open'));
      if (!wasOpen) item.classList.add('open');
    });
  });
}

/* ---------------------------------------------------------
   6. Revelado de secciones al hacer scroll
--------------------------------------------------------- */
const revealTargets = document.querySelectorAll('.reveal-on-scroll');
const io = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in-view');
      io.unobserve(entry.target);
    }
  });
}, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });
revealTargets.forEach(t => io.observe(t));
