/* ===== PARTICLES ===== */
(function () {
  const canvas = document.getElementById('particles');
  const ctx = canvas.getContext('2d');
  let W, H, particles = [];

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);

  function rand(min, max) { return Math.random() * (max - min) + min; }

  class Particle {
    constructor() { this.reset(); }
    reset() {
      this.x = rand(0, W);
      this.y = rand(0, H);
      this.r = rand(0.3, 1.2);
      this.vx = rand(-0.15, 0.15);
      this.vy = rand(-0.3, -0.05);
      this.alpha = rand(0.2, 0.8);
      this.life = 0;
      this.maxLife = rand(200, 500);
    }
    update() {
      this.x += this.vx;
      this.y += this.vy;
      this.life++;
      if (this.life > this.maxLife || this.y < -5) this.reset();
    }
    draw() {
      const progress = this.life / this.maxLife;
      const a = this.alpha * Math.sin(progress * Math.PI);
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(201,168,76,${a})`;
      ctx.fill();
    }
  }

  for (let i = 0; i < 80; i++) particles.push(new Particle());

  (function loop() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => { p.update(); p.draw(); });
    requestAnimationFrame(loop);
  })();
})();

/* ===== NAV SCROLL ===== */
const nav = document.getElementById('nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 60);
});

/* ===== BURGER ===== */
const burger = document.getElementById('burger');
const mobileMenu = document.getElementById('mobileMenu');
burger.addEventListener('click', () => mobileMenu.classList.toggle('open'));

function closeMobile() { mobileMenu.classList.remove('open'); }

/* ===== REVEAL ON SCROLL ===== */
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
}, { threshold: 0.1 });

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

/* ===== SERVICES ===== */
let allData = [];
let activeSlug = null;

async function loadServices() {
  try {
    const res = await fetch('/api/services');
    allData = await res.json();
    renderTabs();
    if (allData.length > 0) showCategory(allData[0].slug);
  } catch (e) {
    document.getElementById('priceGrid').innerHTML =
      '<p style="color:var(--text-dim);text-align:center;padding:3rem">Не удалось загрузить услуги</p>';
  }
}

function renderTabs() {
  const tabs = document.getElementById('tabs');
  tabs.innerHTML = allData.map(cat => `
    <button class="tab" data-slug="${cat.slug}" onclick="showCategory('${cat.slug}')">
      <span class="tab__icon">${cat.icon}</span>
      ${cat.name}
    </button>
  `).join('');
}

function showCategory(slug) {
  activeSlug = slug;

  document.querySelectorAll('.tab').forEach(t => {
    t.classList.toggle('active', t.dataset.slug === slug);
  });

  const cat = allData.find(c => c.slug === slug);
  if (!cat) return;

  const grid = document.getElementById('priceGrid');
  grid.innerHTML = `
    <div class="price-category active">
      <div class="price-category__title">${cat.icon} ${cat.name}</div>
      <div class="price-category__sub">Цены указаны в рублях</div>
      <div class="price-items">
        ${cat.services.length
          ? cat.services.map((s, i) => `
            <div class="price-item" style="animation-delay:${i * 0.04}s">
              <span class="price-item__name">${s.name}</span>
              <span class="price-item__dots"></span>
              <span class="price-item__price">
                ${s.price_prefix ? `<span class="price-item__prefix">${s.price_prefix}</span>` : ''}
                ${s.price}
                <span class="price-item__rub">₽</span>
              </span>
            </div>
          `).join('')
          : '<p style="color:var(--text-dim);padding:2rem 1.5rem">Услуги не найдены</p>'
        }
      </div>
    </div>
  `;

  // Animate items in
  grid.querySelectorAll('.price-item').forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateX(-15px)';
    setTimeout(() => {
      el.style.transition = 'opacity 0.4s ease, transform 0.4s ease, border-left-color 0.3s, background 0.3s';
      el.style.opacity = '1';
      el.style.transform = 'translateX(0)';
    }, i * 35);
  });

  // Scroll tabs
  const activeTab = document.querySelector(`.tab[data-slug="${slug}"]`);
  if (activeTab) {
    activeTab.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
  }
}

loadServices();

/* ===== REVEAL INIT ===== */
document.querySelectorAll(
  '.services__header, .contacts__info, .contacts__quote, .divider-text'
).forEach(el => el.classList.add('reveal'));
setTimeout(() => {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.1 });
  document.querySelectorAll('.reveal').forEach(el => obs.observe(el));
}, 100);
