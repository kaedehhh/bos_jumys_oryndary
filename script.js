const $ = (s, root=document) => root.querySelector(s);
const money = n => `${Number(n || 0).toLocaleString("ru-RU")} ₸`;
const esc = value => String(value ?? "").replace(/[&<>"']/g, ch => ({
  "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"
}[ch]));
const skillsHTML = value => (value || "").split(",").filter(Boolean).slice(0, 4)
  .map(x => `<span>${esc(x.trim())}</span>`).join("");
const localApplications = () => {
  try { return JSON.parse(localStorage.getItem("careerhubApplications") || "[]"); }
  catch { return []; }
};
const saveApplications = rows => localStorage.setItem("careerhubApplications", JSON.stringify(rows));

function vacancyCard(v, preview=false) {
  return `<article class="vacancy-card">
    <div class="card-top"><span class="company-icon">${esc((v.company_name || "C").slice(0,1))}</span>
    <span class="card-city">⌖ ${esc(v.city || "Қала көрсетілмеген")}</span></div>
    <h3>${esc(v.title)}</h3>
    <p class="company-name">${esc(v.company_name || "Компания")}${preview ? "" : " · " + esc(v.industry || "Сала көрсетілмеген")}</p>
    ${preview ? "" : `<p class="description-preview">${esc((v.description || "Толық ақпарат вакансия бетінде.").slice(0,125))}${(v.description || "").length > 125 ? "…" : ""}</p>`}
    <div class="skill-tags">${skillsHTML(v.skills)}</div>
    <div class="card-bottom"><div><strong>${money(v.salary)}</strong><small>/ айына</small></div>
    <a href="vacancy.html?id=${encodeURIComponent(v.vacancy_id)}">${preview ? "↗" : "Толығырақ ↗"}</a></div>
  </article>`;
}
function renderHome(data) {
  const s = data.stats;
  $("#app").innerHTML = `
  <section class="hero"><div class="container hero-grid"><div>
    <div class="eyebrow"><span class="pulse"></span> Мансапқа апарар жол осы жерден басталады</div>
    <h1>Өзіңе лайық<br><em>жұмысты</em> тап.</h1>
    <p class="hero-copy">Мүмкіндіктерді зертте, дағдыларыңа сай вакансияны таңда және келесі қадамыңды жаса.</p>
    <div class="hero-actions"><a class="btn btn-primary" href="vacancies.html">Вакансияларды көру <span>→</span></a>
    <a class="text-link" href="companies.html">Компаниялармен танысу</a></div>
    <div class="hero-note">✦ Жаңа мүмкіндіктер · Нақты компаниялар · Оңай өтінім</div>
  </div><div class="hero-art"><div class="art-orbit orbit-one"></div><div class="art-orbit orbit-two"></div>
    <div class="art-card"><div class="art-top"><span class="mini-logo">CH</span><span class="tag-live">● LIVE</span></div>
    <div class="art-avatar">✦</div><div class="art-lines"><b>Сенің келесі қадамың</b><span>Мүмкіндіктер әлеміне қош келдің</span></div>
    <div class="art-progress"><i></i></div><div class="art-bottom"><span>CAREER PATH</span><strong>01 / 04</strong></div></div>
    <div class="float-chip chip-top">✧ Жаңа мүмкіндіктер</div><div class="float-chip chip-bottom">↗ Өсуге дайынсың ба?</div>
  </div></div></section>
  <section class="stats-band"><div class="container stats-grid">
    <div><strong>${s.vacancies}</strong><span>Ашық вакансия</span></div>
    <div><strong>${s.companies}</strong><span>Компания</span></div>
    <div><strong>${s.users}</strong><span>Үміткер</span></div>
    <div><strong>${s.applications + localApplications().length}</strong><span>Өтінім (база + осы браузер)</span></div>
  </div></section>
  <section class="section container"><div class="section-heading"><div><div class="eyebrow">МҮМКІНДІКТЕР</div>
    <h2>Таңдаулы вакансиялар</h2><p>Саған қызықты болуы мүмкін ұсыныстар.</p></div>
    <a class="text-link" href="vacancies.html">Барлық вакансиялар ↗</a></div>
    <div class="cards-grid">${data.vacancies.slice(0,6).map(v=>vacancyCard(v,true)).join("") || '<div class="empty-state">Әзірге вакансиялар жоқ.</div>'}</div>
  </section>
  <section class="cta-section"><div class="container cta-inner"><div><div class="eyebrow">КЕЛЕСІ ҚАДАМ СЕНІҢ ҚОЛЫҢДА</div>
    <h2>Мансабыңды бүгін баста.</h2><p>Өзіңе сәйкес вакансияны тауып, өтініміңді жібер.</p></div>
    <a class="btn btn-light" href="vacancies.html">Іздеуді бастау ↗</a></div></section>`;
}
function renderVacancies(data) {
  const params = new URLSearchParams(location.search);
  const q = params.get("q") || "", city = params.get("city") || "";
  const salary = params.get("salary") || "", exp = params.get("experience") || "";
  const cities = [...new Set(data.vacancies.map(v=>v.city).filter(Boolean))].sort();
  const filtered = data.vacancies.filter(v => {
    const term = `${v.title} ${v.company_name || ""} ${v.description || ""}`.toLowerCase();
    return (!q || term.includes(q.toLowerCase())) &&
      (!city || v.city === city) &&
      (!salary || Number(v.salary || 0) >= Number(salary)) &&
      (!exp || Number(v.experience_years || 0) <= Number(exp));
  });
  $("#app").innerHTML = `<section class="page-hero"><div class="container"><div class="eyebrow">МҮМКІНДІКТЕР КАТАЛОГЫ</div>
    <h1>Вакансиялар</h1><p>Өзіңе лайық жұмысты ізде және келесі қадамыңды жаса.</p></div></section>
    <section class="container content-section"><form class="filter-panel" id="filterForm">
      <div class="field field-wide"><label>Лауазым немесе компания</label><input name="q" value="${esc(q)}" placeholder="Мысалы, Python Developer"></div>
      <div class="field"><label>Қала</label><select name="city"><option value="">Барлық қала</option>${cities.map(c=>`<option ${city===c?"selected":""} value="${esc(c)}">${esc(c)}</option>`).join("")}</select></div>
      <div class="field"><label>Жалақы, кемінде (₸)</label><input name="salary" type="number" min="0" value="${esc(salary)}" placeholder="300000"></div>
      <div class="field"><label>Тәжірибе, ең көбі (жыл)</label><input name="experience" type="number" min="0" value="${esc(exp)}" placeholder="2"></div>
      <button class="btn btn-primary filter-btn">Іздеу ↗</button><a class="reset-link" href="vacancies.html">Тазарту</a>
    </form><div class="results-line"><b>${filtered.length} нәтиже</b><span>Жалақы бойынша жоғарыдан төмен</span></div>
    <div class="cards-grid">${filtered.map(v=>vacancyCard(v)).join("") || '<div class="empty-state">Сүзгіге сәйкес вакансия табылмады. Іздеу шарттарын өзгертіп көріңіз.</div>'}</div></section>`;
  $("#filterForm").addEventListener("submit", e => {
    e.preventDefault();
    const p = new URLSearchParams(new FormData(e.currentTarget));
    location.href = "vacancies.html?" + p.toString();
  });
}
function renderDetail(data) {
  const id = new URLSearchParams(location.search).get("id");
  const v = data.vacancies.find(x=>String(x.vacancy_id)===String(id));
  if (!v) { $("#app").innerHTML = `<section class="container not-found"><h1>Вакансия табылмады</h1><a class="btn btn-primary" href="vacancies.html">Вакансияларға оралу</a></section>`; return; }
  $("#app").innerHTML = `<section class="page-hero"><div class="container"><a class="back-link" href="vacancies.html">← Вакансияларға оралу</a>
    <div class="eyebrow">ВАКАНСИЯ ТУРАЛЫ</div><h1>${esc(v.title)}</h1><p>${esc(v.company_name || "Компания")} · ${esc(v.city || "Қала көрсетілмеген")}</p></div></section>
    <section class="container detail-layout"><div class="detail-main"><article class="detail-card">
      <div class="detail-heading"><span class="company-icon large">${esc((v.company_name || "C").slice(0,1))}</span><div><h2>${esc(v.title)}</h2><p>${esc(v.company_name || "Компания")} · ${esc(v.industry || "Сала көрсетілмеген")}</p></div></div>
      <div class="detail-meta"><div><small>Жалақы</small><b>${money(v.salary)} / ай</b></div><div><small>Қала</small><b>${esc(v.city || "Көрсетілмеген")}</b></div><div><small>Тәжірибе</small><b>${Number(v.experience_years || 0)} жыл</b></div></div>
      <h3>Жұмыс сипаттамасы</h3><p class="detail-description">${esc(v.description || "Сипаттама әзірге берілмеген.")}</p>
      <h3>Қажетті дағдылар</h3><div class="skill-tags">${skillsHTML(v.skills) || "<span>Дағдылар көрсетілмеген</span>"}</div>
    </article></div><aside class="apply-card" id="apply"><div class="eyebrow">ҚЫЗЫҚТЫРА МА?</div><h2>Өтінім жібер</h2>
      <p>Байланыс ақпаратыңды толтыр. Демонстрациялық өтінім осы браузерде сақталады.</p>
      <form id="applyForm"><div class="field"><label>Аты-жөніңіз *</label><input name="full_name" required maxlength="120" placeholder="Аты-жөніңіз"></div>
      <div class="field"><label>Email *</label><input name="email" type="email" required maxlength="120" placeholder="name@example.com"></div>
      <div class="field"><label>Телефон</label><input name="phone" maxlength="40" placeholder="+7 700 000 00 00"></div>
      <div class="field"><label>Қала</label><input name="city" maxlength="80" placeholder="Астана"></div>
      <button class="btn btn-primary full-width">Өтінім жіберу ↗</button><small class="privacy-note">* Міндетті өрістер. Бұл демо-нұсқада деректер тек осы браузерде сақталады.</small></form>
      <div id="applyMessage" aria-live="polite"></div></aside></section>`;
  $("#applyForm").addEventListener("submit", e => {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const name = String(form.get("full_name") || "").trim();
    const email = String(form.get("email") || "").trim().toLowerCase();
    if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      $("#applyMessage").innerHTML = '<div class="flash error">Аты-жөніңізді және дұрыс email мекенжайын енгізіңіз.</div>'; return;
    }
    const apps = localApplications();
    if (apps.some(a=>a.vacancy_id===v.vacancy_id && a.email===email)) {
      $("#applyMessage").innerHTML = '<div class="flash error">Сіз бұл вакансияға өтінімді бұрын жібергенсіз.</div>'; return;
    }
    apps.unshift({vacancy_id:v.vacancy_id, vacancy_title:v.title, full_name:name, email,
      phone:String(form.get("phone")||"").trim(), city:String(form.get("city")||"").trim(),
      application_date:new Date().toISOString().slice(0,10), status:"Қаралуда"});
    saveApplications(apps);
    $("#applyMessage").innerHTML = '<div class="flash success">Өтініміңіз осы браузерде сақталды! Рақмет.</div>';
    e.currentTarget.reset();
  });
}
function renderCompanies(data) {
  $("#app").innerHTML = `<section class="page-hero"><div class="container"><div class="eyebrow">СЕНІҢ БОЛАШАҚ КОМАНДАҢ</div><h1>Компаниялар</h1><p>Вакансия жариялаған ұйымдармен таныс.</p></div></section>
  <section class="container content-section"><div class="company-grid">${data.companies.map(c=>`<article class="company-card"><span class="company-icon large">${esc((c.company_name||"C").slice(0,1))}</span>
  <h3>${esc(c.company_name)}</h3><p>${esc(c.industry || "Сала көрсетілмеген")}</p><div class="company-card-bottom"><span>⌖ ${esc(c.city || "Қала көрсетілмеген")}</span><b>${c.vacancy_count} вакансия</b></div></article>`).join("") || '<div class="empty-state">Компаниялар табылмады.</div>'}</div></section>`;
}
function renderSkills(data) {
  $("#app").innerHTML = `<section class="page-hero"><div class="container"><div class="eyebrow">КӘСІБИ ҚҰЗЫРЕТТЕР</div><h1>Дағдылар</h1><p>Вакансияларда сұранысқа ие білім мен технологиялар.</p></div></section>
  <section class="container content-section"><div class="skill-grid">${data.skills.map(s=>`<article class="skill-card"><div class="skill-icon">✳</div><div><h3>${esc(s.skill_name)}</h3><p>${esc(s.category || "Жалпы")}</p></div><span class="skill-count">${s.vacancy_count} вакансия</span></article>`).join("") || '<div class="empty-state">Дағдылар табылмады.</div>'}</div></section>`;
}
function renderApplications(data) {
  const apps = localApplications();
  $("#app").innerHTML = `<section class="page-hero"><div class="container"><div class="eyebrow">ӨТІНІМДЕР ТІЗІМІ</div><h1>Өтінімдер</h1><p>Бұл бетте осы браузерден жіберілген демонстрациялық өтінімдер көрсетіледі. SQLite базасындағы өтінімдер бөлек сақталған.</p></div></section>
  <section class="container content-section"><div class="table-wrap"><table><thead><tr><th>ID</th><th>Вакансия</th><th>Күні</th><th>Мәртебесі</th></tr></thead><tbody>
  ${apps.map((a,i)=>`<tr><td>#${i+1}</td><td>${esc(a.vacancy_title)}</td><td>${esc(a.application_date)}</td><td><span class="status">${esc(a.status)}</span></td></tr>`).join("") || '<tr><td colspan="4" class="empty-cell">Әзірге осы браузерде өтінімдер жоқ.</td></tr>'}
  </tbody></table></div></section>`;
}
function renderNotFound() {
  $("#app").innerHTML = `<section class="container not-found"><div class="eyebrow">404 — ҚАТЕ</div><h1>Бет табылмады</h1><p>Мүмкін, сілтеме өзгерген немесе бет жойылған.</p><a class="btn btn-primary" href="index.html">Басты бетке оралу</a></section>`;
}
document.addEventListener("DOMContentLoaded", async () => {
  const toggle = $("#menuToggle");
  if (toggle) toggle.addEventListener("click", () => {
    const nav = $("#navLinks"); nav.classList.toggle("open");
    toggle.setAttribute("aria-expanded", nav.classList.contains("open") ? "true" : "false");
  });
  try {
    const response = await fetch("data.json");
    if (!response.ok) throw new Error("data.json жүктелмеді");
    const data = await response.json();
    const page = document.body.dataset.page;
    ({home:renderHome, vacancies:renderVacancies, detail:renderDetail,
      companies:renderCompanies, skills:renderSkills, applications:renderApplications,
      notfound:renderNotFound}[page] || renderNotFound)(data);
  } catch (error) {
    $("#app").innerHTML = `<section class="container content-section"><div class="flash error">Деректер жүктелмеді. Сайтты GitHub Pages арқылы ашып көріңіз.</div></section>`;
  }
});
