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

const SCHEMES = {
  portable: [
    {name:"PM-KISAN",desc:"Direct income support of ₹6000/year for farmer families",tag:"Portable",docs:"Aadhaar, Bank Account, Land Records",time:"2-3 weeks",where:"Common Service Centre or online portal"},
    {name:"Ayushman Bharat (PM-JAY)",desc:"Health coverage of ₹5 lakh/year per family for hospitalization",tag:"Portable",docs:"Aadhaar, Ration Card",time:"Immediate after verification",where:"Any empanelled hospital nationwide"},
    {name:"PM Ujjwala Yojana",desc:"Free LPG connection for women from BPL households",tag:"Portable",docs:"Aadhaar, BPL Certificate",time:"1-2 weeks",where:"Local LPG distributor"},
  ],
  newlyEligible: [
    {name:"E-Shram Card",desc:"Social security registration for unorganized workers",tag:"Newly Eligible",docs:"Aadhaar, Bank Account, Mobile",time:"Instant (online)",where:"e-Shram portal or CSC"},
    {name:"State Labour Welfare Fund",desc:"Financial assistance for registered construction workers",tag:"Newly Eligible",docs:"Labour Card, Aadhaar, Bank Account",time:"3-4 weeks",where:"Labour Department office"},
    {name:"One Nation One Ration Card",desc:"Access PDS benefits at any Fair Price Shop across India",tag:"Newly Eligible",docs:"Ration Card, Aadhaar (seeded)",time:"Already active if Aadhaar linked",where:"Any Fair Price Shop"},
  ],
  almostEligible: [
    {name:"PM Awas Yojana",desc:"Subsidy for housing construction or purchase",tag:"Almost Eligible",missing:"Missing: Domicile Certificate in current state",docs:"Aadhaar, Income Certificate, Land Docs",time:"6-12 months",where:"Municipal/Panchayat office"},
    {name:"Skill India Mission",desc:"Free vocational training with certification",tag:"Almost Eligible",missing:"Missing: Age proof (must be under 45)",docs:"Aadhaar, Education Certificate",time:"Enrollment-based",where:"Nearest PMKVY Training Centre"},
  ]
};

// --- App State ---
let currentPage = 'home';
let currentStep = 1;
const totalSteps = 6;
let isLoggedIn = false;
let formData = { homeState:'', currentState:'', ageGroup:'', occupation:'', income:'', documents:[] };

// --- Router ---
function navigate(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const target = document.getElementById('page-' + page);
  if (target) {
    target.classList.add('active');
    currentPage = page;
    const profileBtn = document.getElementById('nav-profile');
    if (page === 'dashboard') {
      isLoggedIn = true;
      document.querySelector('.navbar').style.display = 'none';
    } else {
      document.querySelector('.navbar').style.display = '';
    }

    if (profileBtn) {
      profileBtn.style.display = isLoggedIn ? 'flex' : 'none';
    }
    window.scrollTo(0, 0);
    // Re-render icons for the new page
    if (window.lucide) lucide.createIcons();
  }
}

// --- Multi-step Form ---
function renderStep() {
  const content = document.getElementById('step-content');
  const label = document.getElementById('step-label');
  const title = document.getElementById('step-title');
  
  // Update progress bar
  document.querySelectorAll('.progress-step').forEach((s, i) => {
    s.classList.remove('active', 'done');
    if (i + 1 === currentStep) s.classList.add('active');
    if (i + 1 < currentStep) s.classList.add('done');
  });

  // Update back button
  document.getElementById('btn-back').style.visibility = currentStep === 1 ? 'hidden' : 'visible';
  
  // Update next button text
  const nextBtn = document.getElementById('btn-next');
  nextBtn.textContent = currentStep === totalSteps ? 'View Results →' : 'Next →';

  switch(currentStep) {
    case 1:
      label.textContent = 'Step 1 of 6';
      title.textContent = 'Where is your home state?';
      content.innerHTML = `<div class="select-wrap"><select id="home-state" onchange="formData.homeState=this.value">
        <option value="">Select your home state</option>
        ${STATES.map(s => `<option value="${s}" ${formData.homeState===s?'selected':''}>${s}</option>`).join('')}
      </select></div>
      <p style="font-size:0.88rem;color:var(--text-muted);margin-top:12px;">This is the state where you originally registered for benefits.</p>`;
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

function nextStep() {
  if (currentStep < totalSteps) { currentStep++; renderStep(); }
  else { navigate('dashboard'); renderDashboard(); }
}

function prevStep() {
  if (currentStep > 1) { currentStep--; renderStep(); }
}

// --- Dashboard ---
function renderDashboard() {
  const home = formData.homeState || 'Bihar';
  const current = formData.currentState || 'Maharashtra';
  document.getElementById('user-home-state').textContent = home;
  document.getElementById('user-current-state').textContent = current;
  document.getElementById('user-name').textContent = 'Ramesh Kumar';
  
  renderBucket('portable-grid', SCHEMES.portable, 'portable');
  renderBucket('eligible-grid', SCHEMES.newlyEligible, 'eligible');
  renderBucket('almost-grid', SCHEMES.almostEligible, 'almost');
  
  // Update icons in dynamic content
  if (window.lucide) lucide.createIcons();
}

function renderBucket(containerId, schemes, type) {
  const container = document.getElementById(containerId);
  const tagClass = type === 'portable' ? 'portable' : type === 'eligible' ? 'eligible' : 'almost';
  container.innerHTML = schemes.map((s, i) => `
    <div class="scheme-card" onclick="openModal('${type}',${i})">
      <span class="hc-tag ${tagClass}">${s.tag}</span>
      <h4>${s.name}</h4>
      <p>${s.desc}</p>
      ${s.missing ? `<p style="color:#D97706;font-size:0.82rem;font-weight:500;">⚠ ${s.missing}</p>` : ''}
      <div class="card-action">View Details <span>→</span></div>
    </div>
  `).join('');
}

// --- Modal ---
function openModal(type, index) {
  const lists = { portable: SCHEMES.portable, eligible: SCHEMES.newlyEligible, almost: SCHEMES.almostEligible };
  const scheme = lists[type][index];
  const tagClass = type === 'portable' ? 'portable' : type === 'eligible' ? 'eligible' : 'almost';
  
  document.getElementById('modal-title').textContent = scheme.name;
  document.getElementById('modal-tag').className = 'hc-tag ' + tagClass;
  document.getElementById('modal-tag').textContent = scheme.tag;
  document.getElementById('modal-desc').textContent = scheme.desc;
  
  document.getElementById('modal-steps').innerHTML = `
    <div class="step-guide-item"><div class="step-num">1</div><div><h4>Where to Apply</h4><p>${scheme.where}</p></div></div>
    <div class="step-guide-item"><div class="step-num">2</div><div><h4>Documents Needed</h4><p>${scheme.docs}</p></div></div>
    <div class="step-guide-item"><div class="step-num">3</div><div><h4>Expected Time</h4><p>${scheme.time}</p></div></div>
  `;
  
  document.getElementById('modal-overlay').classList.add('active');
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('active');
}

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
  navigate('home');
  
  // Close modal on overlay click
  document.getElementById('modal-overlay').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeModal();
  });
  
  // Navbar scroll effect
  window.addEventListener('scroll', () => {
    const nav = document.querySelector('.navbar');
    if (nav) nav.style.boxShadow = window.scrollY > 10 ? 'var(--shadow-sm)' : 'none';
  });

  // --- India Map: Load SVG and animate ---
  const mapWrapper = document.getElementById('india-map-wrapper');
  if (mapWrapper) {
    fetch('css/india.svg')
      .then(res => res.text())
      .then(svgText => {
        mapWrapper.innerHTML = svgText;
        const paths = mapWrapper.querySelectorAll('.state-path');

        // Start glow animation after a brief delay
        setTimeout(() => {
          paths.forEach((path, i) => {
            setTimeout(() => {
              path.classList.add('glow');
            }, i * 500);
          });
        }, 600);
      })
      .catch(err => console.warn('Could not load India map SVG:', err));
  }
});
