// ===== HaqDaar - Application Logic =====

// --- State Data ---
const STATES = [
  "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Delhi",
  "Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala",
  "Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland",
  "Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura",
  "Uttar Pradesh","Uttarakhand","West Bengal"
];

const AGE_GROUPS = ["18-25","26-35","36-45","46-55","55+"];
const OCCUPATIONS = [
  {icon:"🏗️",label:"Construction"},{icon:"🏭",label:"Factory"},{icon:"🌾",label:"Agriculture"},
  {icon:"🏠",label:"Domestic Work"},{icon:"🚗",label:"Transport"},{icon:"🛍️",label:"Retail/Vendor"},
  {icon:"💼",label:"Office/Clerical"},{icon:"📦",label:"Other"}
];
const INCOME_RANGES = ["Below ₹1 Lakh","₹1-3 Lakh","₹3-5 Lakh","₹5-8 Lakh","Above ₹8 Lakh"];
const DOCUMENTS = ["Aadhaar Card","Ration Card","Voter ID","PAN Card","Bank Account","Labour Card","BPL Certificate","Domicile Certificate"];

// --- App State ---
let currentPage = 'home';
let currentStep = 1;
const totalSteps = 6;
let formData = { name: 'Ramesh Kumar', homeState:'', currentState:'', ageGroup:'', occupation:'', income:'', documents:[] };
let apiResults = null;

// --- Router ---
function navigate(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const target = document.getElementById('page-' + page);
  if (target) {
    target.classList.add('active');
    currentPage = page;
    if (page === 'home') {
      document.querySelector('.navbar').style.display = '';
    } else if (page === 'dashboard') {
      document.querySelector('.navbar').style.display = 'none';
    } else {
      document.querySelector('.navbar').style.display = '';
    }
    window.scrollTo(0, 0);
    if (window.lucide) lucide.createIcons();
  }
}

// --- Multi-step Form ---
function renderStep() {
  const content = document.getElementById('step-content');
  const label = document.getElementById('step-label');
  const title = document.getElementById('step-title');
  
  document.querySelectorAll('.progress-step').forEach((s, i) => {
    s.classList.remove('active', 'done');
    if (i + 1 === currentStep) s.classList.add('active');
    if (i + 1 < currentStep) s.classList.add('done');
  });

  document.getElementById('btn-back').style.visibility = currentStep === 1 ? 'hidden' : 'visible';
  
  const nextBtn = document.getElementById('btn-next');
  nextBtn.textContent = currentStep === totalSteps ? 'View Results →' : 'Next →';

  switch(currentStep) {
    case 1:
      label.textContent = 'Step 1 of 6';
      title.textContent = 'Where is your home state?';
      content.innerHTML = `<div class="select-wrap"><select id="home-state" onchange="formData.homeState=this.value">
        <option value="">Select your home state</option>
        ${STATES.map(s => `<option value="${s}" ${formData.homeState===s?'selected':''}>${s}</option>`).join('')}
      </select></div>`;
      break;
    case 2:
      label.textContent = 'Step 2 of 6';
      title.textContent = 'Where are you currently working?';
      content.innerHTML = `<div class="select-wrap"><select id="current-state" onchange="formData.currentState=this.value">
        <option value="">Select your current state</option>
        ${STATES.map(s => `<option value="${s}" ${formData.currentState===s?'selected':''}>${s}</option>`).join('')}
      </select></div>`;
      break;
    case 3:
      label.textContent = 'Step 3 of 6';
      title.textContent = 'What is your age group?';
      content.innerHTML = `<div class="chip-group">${AGE_GROUPS.map(a =>
        `<div class="chip ${formData.ageGroup===a?'selected':''}" onclick="formData.ageGroup='${a}';renderStep()">${a}</div>`
      ).join('')}</div>`;
      break;
    case 4:
      label.textContent = 'Step 4 of 6';
      title.textContent = 'What is your occupation?';
      content.innerHTML = `<div class="chip-group">${OCCUPATIONS.map(o =>
        `<div class="chip ${formData.occupation===o.label?'selected':''}" onclick="formData.occupation='${o.label}';renderStep()">${o.icon} ${o.label}</div>`
      ).join('')}</div>`;
      break;
    case 5:
      label.textContent = 'Step 5 of 6';
      title.textContent = 'What is your annual income?';
      content.innerHTML = `<div class="chip-group">${INCOME_RANGES.map(i =>
        `<div class="chip ${formData.income===i?'selected':''}" onclick="formData.income='${i}';renderStep()">${i}</div>`
      ).join('')}</div>`;
      break;
    case 6:
      label.textContent = 'Step 6 of 6';
      title.textContent = 'Which documents do you have?';
      content.innerHTML = `<div class="check-group">${DOCUMENTS.map(d =>
        `<div class="check-item ${formData.documents.includes(d)?'checked':''}" onclick="toggleDoc('${d}')">
          <div class="check-box">${formData.documents.includes(d)?'✓':''}</div>
          <span>${d}</span>
        </div>`
      ).join('')}</div>`;
      break;
  }
}

function toggleDoc(doc) {
  const idx = formData.documents.indexOf(doc);
  if (idx > -1) formData.documents.splice(idx, 1);
  else formData.documents.push(doc);
  renderStep();
}

async function nextStep() {
  if (currentStep < totalSteps) { currentStep++; renderStep(); }
  else { 
    await fetchWelfareData();
    navigate('dashboard'); 
    renderDashboard(); 
  }
}

async function fetchWelfareData() {
  const stateMapping = {
    "Bihar": "BR", "Maharashtra": "MH", "Uttar Pradesh": "UP", "Goa": "GA", "Gujarat": "GJ", "Karnataka": "KA"
  };

  const payload = {
    name: formData.name,
    age: parseInt(formData.ageGroup.split('-')[0]) || 30,
    old_state: stateMapping[formData.homeState] || "BR",
    new_state: stateMapping[formData.currentState] || "MH",
    occupation: formData.occupation.toLowerCase(),
    annual_income: formData.income.includes('Below') ? 80000 : 250000,
    gender: "ANY"
  };

  try {
    const res = await fetch('http://127.0.0.1:8000/schemes/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    apiResults = await res.json();
  } catch (e) {
    console.error("API Error:", e);
    alert("Backend not responding. Showing demo data.");
  }
}

function prevStep() {
  if (currentStep > 1) { currentStep--; renderStep(); }
}

// --- Dashboard ---
function renderDashboard() {
  if (!apiResults) return;

  document.getElementById('user-home-state').textContent = formData.homeState || 'Bihar';
  document.getElementById('user-current-state').textContent = formData.currentState || 'Maharashtra';
  document.getElementById('user-name').textContent = formData.name;
  
  renderBucket('portable-grid', apiResults.buckets.bucket_a, 'portable');
  renderBucket('eligible-grid', apiResults.buckets.bucket_b, 'eligible');
  renderBucket('almost-grid', apiResults.buckets.bucket_c, 'almost');
  
  if (window.lucide) lucide.createIcons();
}

function renderBucket(containerId, schemes, type) {
  const container = document.getElementById(containerId);
  const tagClass = type === 'portable' ? 'portable' : type === 'eligible' ? 'eligible' : 'almost';
  const tagLabel = type === 'portable' ? 'Carry Forward' : type === 'eligible' ? 'Claim Locally' : 'Almost There';
  
  container.innerHTML = schemes.map((s, i) => `
    <div class="scheme-card" onclick="openModal('${type}',${i})">
      <span class="hc-tag ${tagClass}">${tagLabel}</span>
      <h4>${s.scheme_name}</h4>
      <p>${s.description ? s.description.substring(0, 80) + '...' : 'Access welfare benefits.'}</p>
      <div class="card-action">View Details <span>→</span></div>
    </div>
  `).join('') || '<p style="color:var(--text-muted);grid-column:1/-1;text-align:center;padding:20px;">No schemes found in this category.</p>';
}

// --- Modal ---
function openModal(type, index) {
  const buckets = { portable: 'bucket_a', eligible: 'bucket_b', almost: 'bucket_c' };
  const scheme = apiResults.buckets[buckets[type]][index];
  const tagClass = type === 'portable' ? 'portable' : type === 'eligible' ? 'eligible' : 'almost';
  const tagLabel = type === 'portable' ? 'Carry Forward' : type === 'eligible' ? 'Claim Locally' : 'Almost There';
  
  document.getElementById('modal-title').textContent = scheme.scheme_name;
  document.getElementById('modal-tag').className = 'hc-tag ' + tagClass;
  document.getElementById('modal-tag').textContent = tagLabel;
  document.getElementById('modal-desc').textContent = scheme.description;
  
  document.getElementById('modal-steps').innerHTML = `
    <div class="step-guide-item"><div class="step-num">1</div><div><h4>How to Apply</h4><p>${scheme.application_steps[1] || 'Visit nearest CSC'}</p></div></div>
    <div class="step-guide-item"><div class="step-num">2</div><div><h4>Documents Needed</h4><p>${scheme.required_documents.join(', ')}</p></div></div>
    <div class="step-guide-item"><div class="step-num">3</div><div><h4>Expected Time</h4><p>${scheme.time_estimate}</p></div></div>
  `;
  
  document.getElementById('modal-overlay').classList.add('active');
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('active');
}

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
  navigate('home');
  document.getElementById('modal-overlay').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeModal();
  });
});
