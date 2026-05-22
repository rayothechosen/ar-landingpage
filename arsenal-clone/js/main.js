// =============================================
// ARSENAL SECRETO — CLONE JS
// =============================================

// --- COUNTDOWN TIMER ---
function startCountdown(seconds, el1, el2) {
  let remaining = seconds;
  function update() {
    const m = String(Math.floor(remaining / 60)).padStart(2,'0');
    const s = String(remaining % 60).padStart(2,'0');
    const display = `${m}:${s}`;
    if (el1) el1.textContent = display;
    if (el2) el2.textContent = display;
    if (remaining > 0) {
      remaining--;
      setTimeout(update, 1000);
    } else {
      remaining = 599; // reinicia em 9:59
      setTimeout(update, 1000);
    }
  }
  update();
}

document.addEventListener('DOMContentLoaded', () => {
  const t1 = document.getElementById('timer');
  const t2 = document.getElementById('timer2');
  startCountdown(587, t1, t2);

  // --- FAQ TOGGLE ---
  document.querySelectorAll('.faq-q').forEach(btn => {
    btn.addEventListener('click', () => {
      const answer = btn.nextElementSibling;
      const span = btn.querySelector('span');
      const isOpen = answer.classList.contains('open');
      // fecha todos
      document.querySelectorAll('.faq-a').forEach(a => a.classList.remove('open'));
      document.querySelectorAll('.faq-q span').forEach(s => s.textContent = '+');
      // abre este se estava fechado
      if (!isOpen) {
        answer.classList.add('open');
        span.textContent = '−';
      }
    });
  });
});

// --- MÓDULOS SCROLL ---
function scrollMod(dir) {
  const track = document.getElementById('modulosTrack');
  if (track) track.scrollBy({ left: dir * 280, behavior: 'smooth' });
}

// --- SCROLL ANIMATIONS ---
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.addEventListener('DOMContentLoaded', () => {
  const animEls = document.querySelectorAll('.card, .modulo-card, .inc-item, .tools-col, .top3-card, .depo-card, .faq-item, .compare-box');
  animEls.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });
});
