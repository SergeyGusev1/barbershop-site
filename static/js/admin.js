const API = '';
let token = localStorage.getItem('pfb_token') || '';
let allCategories = [];
let allServices = [];
let currentPage = 'services';
let deleteCallback = null;

function headers() {
  return { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };
}

/* ===== AUTH ===== */
async function checkAuth() {
  if (!token) { showLogin(); return; }
  try {
    await fetch('/api/admin/services', { headers: headers() });
    showApp();
  } catch { showLogin(); }
}

function showLogin() {
  document.getElementById('loginScreen').classList.remove('hidden');
  document.getElementById('adminApp').classList.add('hidden');
}

function showApp() {
  document.getElementById('loginScreen').classList.add('hidden');
  document.getElementById('adminApp').classList.remove('hidden');
  loadData();
}

document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const user = document.getElementById('loginUser').value;
  const pass = document.getElementById('loginPass').value;
  const err = document.getElementById('loginError');
  err.textContent = '';
  try {
    const res = await fetch('/api/admin/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: user, password: pass })
    });
    const data = await res.json();
    if (!res.ok) { err.textContent = data.detail || 'Ошибка входа'; return; }
    token = data.access_token;
    localStorage.setItem('pfb_token', token);
    showApp();
  } catch { err.textContent = 'Ошибка соединения'; }
});

function logout() {
  token = '';
  localStorage.removeItem('pfb_token');
  showLogin();
}

/* ===== DATA ===== */
async function loadData() {
  const [cats, services] = await Promise.all([
    fetch('/api/admin/categories', { headers: headers() }).then(r => r.json()),
    fetch('/api/admin/services', { headers: headers() }).then(r => r.json()),
  ]);
  allCategories = cats;
  allServices = services;
  populateCatFilter();
  populateCatSelects();
  renderPage();
}

function populateCatFilter() {
  const sel = document.getElementById('catFilter');
  sel.innerHTML = '<option value="">Все категории</option>' +
    allCategories.map(c => `<option value="${c.id}">${c.icon} ${c.name}</option>`).join('');
}

function populateCatSelects() {
  const sel = document.getElementById('serviceCatId');
  sel.innerHTML = allCategories.map(c =>
    `<option value="${c.id}">${c.icon} ${c.name}</option>`
  ).join('');
}

/* ===== PAGES ===== */
function showPage(page) {
  currentPage = page;
  document.querySelectorAll('.sidebar__link').forEach(l => l.classList.remove('active'));
  event.currentTarget.classList.add('active');

  const titles = { services: ['Управление услугами', 'Добавляйте, редактируйте и удаляйте услуги'],
                   categories: ['Категории', 'Управление категориями прайс-листа'] };
  document.getElementById('pageTitle').textContent = titles[page][0];
  document.getElementById('pageDesc').textContent = titles[page][1];

  document.getElementById('servicesPage').classList.toggle('hidden', page !== 'services');
  document.getElementById('categoriesPage').classList.toggle('hidden', page !== 'categories');
  document.getElementById('addBtn').onclick = page === 'services' ? openAddModal : openAddCatModal;

  renderPage();
}

function renderPage() {
  if (currentPage === 'services') renderServices();
  else renderCategories();
}

/* ===== SERVICES ===== */
function filterServices() {
  renderServices();
}

function renderServices() {
  const catFilter = document.getElementById('catFilter').value;
  const search = document.getElementById('searchInput').value.toLowerCase().trim();

  const list = document.getElementById('servicesList');
  list.innerHTML = '';

  const filtered = allServices.filter(cat => {
    if (catFilter && String(cat.id) !== catFilter) return false;
    return true;
  });

  filtered.forEach(cat => {
    const services = cat.services.filter(s =>
      !search || s.name.toLowerCase().includes(search)
    );
    if (!services.length) return;

    const block = document.createElement('div');
    block.className = 'category-block';
    block.innerHTML = `
      <div class="category-block__header" onclick="toggleBlock(this)">
        <span class="category-block__name">${cat.icon} ${cat.name}
          <span class="category-block__count">${services.length} услуг</span>
        </span>
        <div class="category-block__actions" onclick="event.stopPropagation()">
          <button class="btn-icon" title="Добавить услугу" onclick="openAddModalForCat(${cat.id})">+ Добавить</button>
        </div>
      </div>
      <div class="service-rows">
        ${services.map(s => `
          <div class="service-row ${s.is_active ? '' : 'inactive'}" data-id="${s.id}">
            <span class="service-row__name">${s.name}</span>
            <span class="service-row__price">
              ${s.price_prefix ? `<span class="service-row__prefix">${s.price_prefix}</span>` : ''}
              ${s.price} ₽
            </span>
            <span class="badge ${s.is_active ? 'badge--active' : 'badge--inactive'}">${s.is_active ? 'Активна' : 'Скрыта'}</span>
            <div class="service-row__btns">
              <button class="btn-icon" title="Редактировать" onclick="openEditModal(${s.id})">✎</button>
              <button class="btn-icon btn-icon--danger" title="Удалить" onclick="confirmDelete('service', ${s.id}, '${s.name.replace(/'/g, "\\'")}')">✕</button>
            </div>
          </div>
        `).join('')}
      </div>
    `;
    list.appendChild(block);
  });

  if (!list.innerHTML) {
    list.innerHTML = '<p style="color:var(--text-dim);padding:2rem;text-align:center">Ничего не найдено</p>';
  }
}

function toggleBlock(header) {
  const rows = header.nextElementSibling;
  rows.style.display = rows.style.display === 'none' ? '' : 'none';
}

/* ===== CATEGORIES ===== */
function renderCategories() {
  const list = document.getElementById('categoriesList');
  list.innerHTML = '';
  allCategories.forEach(cat => {
    const block = document.createElement('div');
    block.className = 'category-block';
    block.innerHTML = `
      <div class="category-block__header">
        <span class="category-block__name">${cat.icon} ${cat.name}
          <span class="category-block__count">slug: ${cat.slug} · порядок: ${cat.order}</span>
        </span>
        <div class="category-block__actions">
          <button class="btn-icon" onclick="openEditCatModal(${cat.id})">✎</button>
          <button class="btn-icon btn-icon--danger" onclick="confirmDelete('category', ${cat.id}, '${cat.name.replace(/'/g, "\\'")}')">✕</button>
        </div>
      </div>
    `;
    list.appendChild(block);
  });
}

/* ===== ADD/EDIT SERVICE ===== */
function openAddModal() {
  openAddModalForCat(allCategories[0]?.id);
}

function openAddModalForCat(catId) {
  document.getElementById('serviceModalTitle').textContent = 'Добавить услугу';
  document.getElementById('serviceId').value = '';
  document.getElementById('serviceForm').reset();
  if (catId) document.getElementById('serviceCatId').value = catId;
  document.getElementById('serviceActive').checked = true;
  document.getElementById('serviceModal').classList.remove('hidden');
}

function openEditModal(id) {
  const service = allServices.flatMap(c => c.services).find(s => s.id === id);
  if (!service) return;
  document.getElementById('serviceModalTitle').textContent = 'Редактировать услугу';
  document.getElementById('serviceId').value = id;
  document.getElementById('serviceCatId').value = service.category_id;
  document.getElementById('serviceName').value = service.name;
  document.getElementById('servicePrefix').value = service.price_prefix || '';
  document.getElementById('servicePrice').value = service.price;
  document.getElementById('serviceDesc').value = service.description || '';
  document.getElementById('serviceOrder').value = service.order || 0;
  document.getElementById('serviceActive').checked = service.is_active;
  document.getElementById('serviceModal').classList.remove('hidden');
}

document.getElementById('serviceForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = document.getElementById('serviceId').value;
  const data = {
    category_id: parseInt(document.getElementById('serviceCatId').value),
    name: document.getElementById('serviceName').value,
    price_prefix: document.getElementById('servicePrefix').value,
    price: document.getElementById('servicePrice').value,
    description: document.getElementById('serviceDesc').value,
    order: parseInt(document.getElementById('serviceOrder').value) || 0,
    is_active: document.getElementById('serviceActive').checked,
  };

  try {
    const url = id ? `/api/admin/services/${id}` : '/api/admin/services';
    const method = id ? 'PUT' : 'POST';
    const res = await fetch(url, { method, headers: headers(), body: JSON.stringify(data) });
    if (!res.ok) throw new Error();
    closeModal('serviceModal');
    showToast(id ? 'Услуга обновлена' : 'Услуга добавлена');
    await loadData();
  } catch { showToast('Ошибка сохранения', true); }
});

/* ===== ADD/EDIT CATEGORY ===== */
function openAddCatModal() {
  document.getElementById('catModalTitle').textContent = 'Добавить категорию';
  document.getElementById('catId').value = '';
  document.getElementById('catForm').reset();
  document.getElementById('catModal').classList.remove('hidden');
}

function openEditCatModal(id) {
  const cat = allCategories.find(c => c.id === id);
  if (!cat) return;
  document.getElementById('catModalTitle').textContent = 'Редактировать категорию';
  document.getElementById('catId').value = id;
  document.getElementById('catName').value = cat.name;
  document.getElementById('catSlug').value = cat.slug;
  document.getElementById('catIcon').value = cat.icon;
  document.getElementById('catOrder').value = cat.order;
  document.getElementById('catModal').classList.remove('hidden');
}

document.getElementById('catForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const id = document.getElementById('catId').value;
  const data = {
    name: document.getElementById('catName').value,
    slug: document.getElementById('catSlug').value || document.getElementById('catName').value.toLowerCase().replace(/\s+/g, '-'),
    icon: document.getElementById('catIcon').value || '✨',
    order: parseInt(document.getElementById('catOrder').value) || 0,
  };
  try {
    const url = id ? `/api/admin/categories/${id}` : '/api/admin/categories';
    const method = id ? 'PUT' : 'POST';
    const res = await fetch(url, { method, headers: headers(), body: JSON.stringify(data) });
    if (!res.ok) throw new Error();
    closeModal('catModal');
    showToast(id ? 'Категория обновлена' : 'Категория добавлена');
    await loadData();
  } catch { showToast('Ошибка сохранения', true); }
});

/* ===== DELETE ===== */
function confirmDelete(type, id, name) {
  const texts = { service: `Удалить услугу «${name}»?`, category: `Удалить категорию «${name}» и все её услуги?` };
  document.getElementById('confirmText').textContent = texts[type];
  document.getElementById('confirmModal').classList.remove('hidden');
  deleteCallback = async () => {
    const url = type === 'service' ? `/api/admin/services/${id}` : `/api/admin/categories/${id}`;
    try {
      const res = await fetch(url, { method: 'DELETE', headers: headers() });
      if (!res.ok) throw new Error();
      closeModal('confirmModal');
      showToast('Удалено');
      await loadData();
    } catch { showToast('Ошибка удаления', true); }
  };
}

document.getElementById('confirmBtn').addEventListener('click', () => {
  if (deleteCallback) deleteCallback();
});

/* ===== UTILS ===== */
function closeModal(id) {
  document.getElementById(id).classList.add('hidden');
}

let toastTimer;
function showToast(msg, isError = false) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast' + (isError ? ' error' : '');
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 3000);
}

/* ===== INIT ===== */
checkAuth();
