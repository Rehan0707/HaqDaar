// ===== HaqDaar - Application Logic =====

// --- Dynamic Option Data ---
const STATE_CODE_TO_NAME = {
  AP: "Andhra Pradesh", AR: "Arunachal Pradesh", AS: "Assam", BR: "Bihar", CG: "Chhattisgarh",
  DL: "Delhi", GA: "Goa", GJ: "Gujarat", HR: "Haryana", HP: "Himachal Pradesh", JH: "Jharkhand",
  KA: "Karnataka", KL: "Kerala", MP: "Madhya Pradesh", MH: "Maharashtra", MN: "Manipur",
  ML: "Meghalaya", MZ: "Mizoram", NL: "Nagaland", OD: "Odisha", PB: "Punjab", RJ: "Rajasthan",
  SK: "Sikkim", TN: "Tamil Nadu", TS: "Telangana", TR: "Tripura", UP: "Uttar Pradesh",
  UK: "Uttarakhand", WB: "West Bengal"
};
let STATES = Object.keys(STATE_CODE_TO_NAME);
let AGE_GROUPS = ["18-25","26-35","36-45","46-55","55+"];
let SOCIAL_CATEGORIES = ["GEN", "OBC", "SC", "ST", "EWS"];
let OCCUPATIONS = [
  {icon:"🏗️",label:"Construction"},{icon:"🏭",label:"Factory"},{icon:"🌾",label:"Agriculture"},
  {icon:"🏠",label:"Domestic"},{icon:"🚗",label:"Transport"},{icon:"🛍️",label:"Retail"},
  {icon:"💼",label:"Office"},{icon:"📦",label:"Other"}
];
let INCOME_RANGES = ["Below ₹1 Lakh","₹1-3 Lakh","₹3-5 Lakh","₹5-8 Lakh","Above ₹8 Lakh"];
let DOCUMENTS = ["Aadhaar Card","Ration Card","Voter ID","PAN Card","Bank Account","Labour Card","BPL Certificate","Domicile Certificate"];
const LOCALE_MAP = { en: "en-IN", hi: "hi-IN", mr: "mr-IN" };
const I18N = {
  en: {
    navHome: "Home", navAbout: "About", navFeatures: "Features", navSignIn: "Sign In",
    heroBadge: "Unified Welfare Access Layer",
    heroTitle: "Access Your Welfare Benefits <span>Anywhere</span> in India",
    heroSubtitle: "Find, transfer, and claim government schemes seamlessly across states. We bridge the gap for migrant workers.",
    getStarted: "Get Started", learnMore: "Learn More",
    featuresTitle: "Everything you need to stay covered", featuresSubtitle: "Designed for clarity, built for impact.",
    dashboardTitle: "Welfare Dashboard", simpleLanguage: "Simple Language", readAloud: "Read Aloud", logout: "Log Out",
    totalSchemes: "Total Schemes", active: "Active",
    bucketPortable: "You Won't Lose These", bucketEligible: "You Can Get These Here", bucketAlmost: "Almost Eligible", bucketDiscovery: "You May Also Qualify For",
    claimProcess: "Claim Process", viewDetails: "View Details",
    noSchemes: "No schemes found in this category.",
    stepOf: "Step {n} of 6", viewResults: "View Results ->", next: "Next ->", back: "<- Back",
    step1: "Where is your home state?", step2: "Where are you currently working?", step3: "What is your age group?",
    step4: "What is your occupation?", step5: "What is your annual income?", step6: "Category and available documents",
    selectHome: "Select your home state", selectCurrent: "Select your current state", socialCategory: "Social category", availableDocuments: "Available documents",
    carryForward: "Carry Forward", claimLocally: "Claim Locally", newMatch: "New Match", almostThere: "Almost There",
    applyThrough: "Apply Through", documentsNeeded: "Documents Needed", missingDocuments: "Missing Documents", expectedTime: "Expected Time",
    summaryLine1: "You have {count} benefits you can carry forward.", summaryLine2: "{count} benefits you can claim in your current state.",
    summaryLine3: "{count} near matches.", summaryLine4: "{count} newly discovered schemes."
  },
  hi: {
    navHome: "होम", navAbout: "जानकारी", navFeatures: "फीचर्स", navSignIn: "साइन इन",
    heroBadge: "एकीकृत कल्याण पहुंच प्लेटफॉर्म",
    heroTitle: "अपने कल्याण लाभ भारत में <span>कहीं भी</span> पाएं",
    heroSubtitle: "राज्य बदलने पर भी योजनाएं खोजें, ट्रांसफर करें और दावा करें।",
    getStarted: "शुरू करें", learnMore: "और जानें",
    featuresTitle: "कवरेज बनाए रखने के लिए जरूरी सब कुछ", featuresSubtitle: "स्पष्ट, सरल और प्रभावी।",
    dashboardTitle: "कल्याण डैशबोर्ड", simpleLanguage: "सरल भाषा", readAloud: "आवाज में सुनें", logout: "लॉग आउट",
    totalSchemes: "कुल योजनाएं", active: "सक्रिय",
    bucketPortable: "ये लाभ नहीं छूटेंगे", bucketEligible: "ये लाभ यहां मिल सकते हैं", bucketAlmost: "लगभग पात्र", bucketDiscovery: "इनके लिए भी पात्र हो सकते हैं",
    claimProcess: "दावा प्रक्रिया", viewDetails: "विवरण देखें",
    noSchemes: "इस श्रेणी में कोई योजना नहीं मिली।",
    stepOf: "चरण {n} / 6", viewResults: "परिणाम देखें ->", next: "आगे ->", back: "<- पीछे",
    step1: "आपका गृह राज्य कौन सा है?", step2: "आप अभी किस राज्य में काम कर रहे हैं?", step3: "आपका आयु समूह क्या है?",
    step4: "आपका व्यवसाय क्या है?", step5: "आपकी वार्षिक आय क्या है?", step6: "श्रेणी और उपलब्ध दस्तावेज",
    selectHome: "अपना गृह राज्य चुनें", selectCurrent: "वर्तमान राज्य चुनें", socialCategory: "सामाजिक श्रेणी", availableDocuments: "उपलब्ध दस्तावेज",
    carryForward: "साथ ले जाएं", claimLocally: "यहीं दावा करें", newMatch: "नई योजना", almostThere: "करीब हैं",
    applyThrough: "आवेदन माध्यम", documentsNeeded: "जरूरी दस्तावेज", missingDocuments: "कमी वाले दस्तावेज", expectedTime: "अनुमानित समय",
    summaryLine1: "आपके पास {count} लाभ हैं जिन्हें आप साथ ले जा सकते हैं।", summaryLine2: "{count} लाभ यहां दावा किए जा सकते हैं।",
    summaryLine3: "{count} लगभग मैच हैं।", summaryLine4: "{count} नई खोजी गई योजनाएं हैं।"
  },
  mr: {
    navHome: "मुख्यपृष्ठ", navAbout: "माहिती", navFeatures: "वैशिष्ट्ये", navSignIn: "साइन इन",
    heroBadge: "एकत्रित कल्याण प्रवेश स्तर",
    heroTitle: "तुमचे कल्याण लाभ भारतात <span>कुठेही</span> मिळवा",
    heroSubtitle: "राज्य बदलल्यानंतरही योजना शोधा, ट्रान्सफर करा आणि अर्ज करा.",
    getStarted: "सुरू करा", learnMore: "अधिक जाणून घ्या",
    featuresTitle: "कव्हरेज कायम ठेवण्यासाठी आवश्यक सर्व", featuresSubtitle: "स्पष्ट आणि परिणामकारक.",
    dashboardTitle: "कल्याण डॅशबोर्ड", simpleLanguage: "सोपे भाषांतर", readAloud: "मोठ्याने वाचा", logout: "लॉग आउट",
    totalSchemes: "एकूण योजना", active: "सक्रिय",
    bucketPortable: "हे लाभ कायम राहतील", bucketEligible: "हे लाभ इथे मिळू शकतात", bucketAlmost: "जवळपास पात्र", bucketDiscovery: "यासाठीही तुम्ही पात्र असू शकता",
    claimProcess: "अर्ज प्रक्रिया", viewDetails: "तपशील पहा",
    noSchemes: "या विभागात कोणतीही योजना आढळली नाही.",
    stepOf: "पायरी {n} / 6", viewResults: "निकाल पहा ->", next: "पुढे ->", back: "<- मागे",
    step1: "तुमचे मूळ राज्य कोणते?", step2: "तुम्ही सध्या कोणत्या राज्यात काम करता?", step3: "तुमचा वयोगट काय आहे?",
    step4: "तुमचा व्यवसाय काय आहे?", step5: "तुमचे वार्षिक उत्पन्न किती?", step6: "श्रेणी आणि उपलब्ध कागदपत्रे",
    selectHome: "मूळ राज्य निवडा", selectCurrent: "सध्याचे राज्य निवडा", socialCategory: "सामाजिक श्रेणी", availableDocuments: "उपलब्ध कागदपत्रे",
    carryForward: "सोबत ठेवा", claimLocally: "येथे अर्ज करा", newMatch: "नवीन जुळणी", almostThere: "जवळपास",
    applyThrough: "अर्ज मार्ग", documentsNeeded: "आवश्यक कागदपत्रे", missingDocuments: "उणीव कागदपत्रे", expectedTime: "अपेक्षित वेळ",
    summaryLine1: "तुमच्याकडे {count} लाभ आहेत जे सोबत ठेवता येतील।", summaryLine2: "{count} लाभ सध्याच्या राज्यात मिळू शकतात।",
    summaryLine3: "{count} जवळच्या जुळण्या आहेत।", summaryLine4: "{count} नवीन शोधलेल्या योजना आहेत।"
  }
};

// --- App State ---
let currentPage = 'home';
let currentStep = 1;
const totalSteps = 6;
let formData = {
  name: 'Ramesh Kumar',
  homeState:'',
  currentState:'',
  ageGroup:'',
  occupation:'',
  income:'',
  socialCategory:'OBC',
  documents:[]
};
let apiResults = null;
let discoveryResults = [];
let simpleModeEnabled = false;
let currentLanguage = 'en';
const API_BASE = `${window.location.protocol}//127.0.0.1:8000`;

function t(key, vars = {}) {
  const table = I18N[currentLanguage] || I18N.en;
  let text = table[key] || I18N.en[key] || key;
  Object.entries(vars).forEach(([k, v]) => {
    text = text.replace(`{${k}}`, String(v));
  });
  return text;
}

function setLanguage(lang) {
  currentLanguage = I18N[lang] ? lang : 'en';
  const nav = document.getElementById('language-select-nav');
  const dash = document.getElementById('language-select-dashboard');
  if (nav) nav.value = currentLanguage;
  if (dash) dash.value = currentLanguage;
  applyStaticTranslations();
  if (currentPage === 'get-started') renderStep();
  if (apiResults) renderDashboard();
}

function applyStaticTranslations() {
  const setText = (id, value, html = false) => {
    const el = document.getElementById(id);
    if (!el) return;
    if (html) el.innerHTML = value;
    else el.textContent = value;
  };
  setText('nav-home', t('navHome'));
  setText('nav-about', t('navAbout'));
  setText('nav-features', t('navFeatures'));
  setText('nav-signin', t('navSignIn'));
  setText('hero-badge-text', t('heroBadge'));
  setText('hero-title', t('heroTitle'), true);
  setText('hero-subtitle', t('heroSubtitle'));
  setText('hero-get-started', t('getStarted'));
  setText('hero-learn-more', t('learnMore'));
  setText('features-title', t('featuresTitle'));
  setText('features-subtitle', t('featuresSubtitle'));
  setText('dashboard-title', t('dashboardTitle'));
  setText('btn-simple-language', t('simpleLanguage'));
  setText('btn-read-aloud', t('readAloud'));
  setText('btn-logout', t('logout'));
  setText('stat-total-schemes', t('totalSchemes'));
  setText('stat-active', t('active'));
  setText('bucket-portable-title', t('bucketPortable'));
  setText('bucket-eligible-title', t('bucketEligible'));
  setText('bucket-almost-title', t('bucketAlmost'));
  setText('bucket-discovery-title', t('bucketDiscovery'));
  setText('claim-process-title', t('claimProcess'));
}

// --- Router ---
function navigate(page) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const target = document.getElementById('page-' + page);
  if (target) {
    target.classList.add('active');
    currentPage = page;
    
    // Update navbar active state
    document.querySelectorAll('.nav-links a').forEach(a => {
      a.classList.remove('active');
      if (a.getAttribute('onclick') && a.getAttribute('onclick').includes(`'${page}'`)) {
        a.classList.add('active');
      }
    });

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
  nextBtn.textContent = currentStep === totalSteps ? t('viewResults') : t('next');
  document.getElementById('btn-back').textContent = t('back');

  switch(currentStep) {
    case 1:
      label.textContent = t('stepOf', { n: 1 });
      title.textContent = t('step1');
      content.innerHTML = `<div class="select-wrap"><select id="home-state" onchange="formData.homeState=this.value">
        <option value="">${t('selectHome')}</option>
        ${STATES.map(s => `<option value="${s}" ${formData.homeState===s?'selected':''}>${STATE_CODE_TO_NAME[s] || s}</option>`).join('')}
      </select></div>`;
      break;
    case 2:
      label.textContent = t('stepOf', { n: 2 });
      title.textContent = t('step2');
      content.innerHTML = `<div class="select-wrap"><select id="current-state" onchange="formData.currentState=this.value">
        <option value="">${t('selectCurrent')}</option>
        ${STATES.map(s => `<option value="${s}" ${formData.currentState===s?'selected':''}>${STATE_CODE_TO_NAME[s] || s}</option>`).join('')}
      </select></div>`;
      break;
    case 3:
      label.textContent = t('stepOf', { n: 3 });
      title.textContent = t('step3');
      content.innerHTML = `<div class="chip-group">${AGE_GROUPS.map(a =>
        `<div class="chip ${formData.ageGroup===a?'selected':''}" onclick="formData.ageGroup='${a}';renderStep()">${a}</div>`
      ).join('')}</div>`;
      break;
    case 4:
      label.textContent = t('stepOf', { n: 4 });
      title.textContent = t('step4');
      content.innerHTML = `<div class="chip-group">${OCCUPATIONS.map(o =>
        `<div class="chip ${formData.occupation===o.label?'selected':''}" onclick="formData.occupation='${o.label}';renderStep()">${o.icon} ${o.label}</div>`
      ).join('')}</div>`;
      break;
    case 5:
      label.textContent = t('stepOf', { n: 5 });
      title.textContent = t('step5');
      content.innerHTML = `<div class="chip-group">${INCOME_RANGES.map(i =>
        `<div class="chip ${formData.income===i?'selected':''}" onclick="formData.income='${i}';renderStep()">${i}</div>`
      ).join('')}</div>`;
      break;
    case 6:
      label.textContent = t('stepOf', { n: 6 });
      title.textContent = t('step6');
      content.innerHTML = `
      <p style="font-size:0.88rem;color:var(--text-muted);margin-bottom:12px;">${t('socialCategory')}</p>
      <div class="chip-group" style="margin-bottom:18px;">
      ${SOCIAL_CATEGORIES.map(c =>
        `<div class="chip ${formData.socialCategory===c?'selected':''}" onclick="formData.socialCategory='${c}';renderStep()">${c}</div>`
      ).join('')}
      </div>
      <p style="font-size:0.88rem;color:var(--text-muted);margin-bottom:12px;">${t('availableDocuments')}</p>
      <div class="check-group">${DOCUMENTS.map(d =>
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
    const ok = await fetchWelfareData();
    if (!ok) return;
    navigate('dashboard'); 
    renderDashboard(); 
  }
}

function toStateCode(name) {
  return name || "BR";
}

function incomeRangeToAnnual(rangeLabel) {
  const map = {
    "Below ₹1 Lakh": 50000,   // Lower for safer matching
    "₹1-3 Lakh": 150000,
    "₹3-5 Lakh": 350000,
    "₹5-8 Lakh": 550000,
    "Above ₹8 Lakh": 900000
  };
  return map[rangeLabel] || 250000;
}

function normalizeOccupation(label) {
  const value = (label || "").toLowerCase();
  if (value.includes("construction")) return "CONSTRUCTION";
  if (value.includes("factory")) return "FACTORY";
  if (value.includes("agriculture")) return "AGRICULTURE";
  if (value.includes("domestic")) return "DOMESTIC";
  if (value.includes("transport")) return "TRANSPORT";
  if (value.includes("retail")) return "RETAIL";
  if (value.includes("office")) return "OFFICE";
  return "ALL";
}

async function fetchWelfareData() {
  const payload = {
    name: formData.name,
    age: parseInt(formData.ageGroup.split('-')[0]) || 30,
    old_state: toStateCode(formData.homeState),
    new_state: toStateCode(formData.currentState),
    occupation: normalizeOccupation(formData.occupation),
    annual_income: incomeRangeToAnnual(formData.income),
    social_category: formData.socialCategory || "OBC",
    gender: "ANY",
    preferred_language: currentLanguage
  };

  try {
    const res = await fetch(`${API_BASE}/schemes/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.text();
      throw new Error(err || "Search request failed");
    }
    apiResults = await res.json();
    await fetchDiscoveryData(payload);
    return true;
  } catch (e) {
    console.error("API Error:", e);
    alert("API Error. Please ensure backend is running and form details are complete.");
    return false;
  }
}

async function fetchDiscoveryData(basePayload) {
  try {
    const res = await fetch(`${API_BASE}/schemes/discover`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...basePayload,
        available_documents: formData.documents
      })
    });
    if (!res.ok) {
      discoveryResults = [];
      return;
    }
    const data = await res.json();
    discoveryResults = data.recommended || [];
  } catch (_e) {
    discoveryResults = [];
  }
}

function prevStep() {
  if (currentStep > 1) { currentStep--; renderStep(); }
}

// --- Dashboard ---
function renderDashboard() {
  if (!apiResults) return;

  document.getElementById('user-home-state').textContent = STATE_CODE_TO_NAME[formData.homeState] || formData.homeState || 'Bihar';
  document.getElementById('user-current-state').textContent = STATE_CODE_TO_NAME[formData.currentState] || formData.currentState || 'Maharashtra';
  document.getElementById('user-name').textContent = formData.name;
  
  if (formData.picture) {
    const pic = document.getElementById('user-picture');
    pic.src = formData.picture;
    pic.style.display = 'block';
  }
  
  renderBucket('portable-grid', apiResults.buckets.bucket_a, 'portable');
  renderBucket('eligible-grid', apiResults.buckets.bucket_b, 'eligible');
  renderBucket('almost-grid', apiResults.buckets.bucket_c, 'almost');
  renderBucket('discovery-grid', discoveryResults, 'discovery');
  document.getElementById('count-portable').textContent = apiResults.counts.bucket_a ?? 0;
  document.getElementById('count-eligible').textContent = apiResults.counts.bucket_b ?? 0;
  document.getElementById('count-almost').textContent = apiResults.counts.bucket_c ?? 0;
  document.getElementById('count-discovery').textContent = discoveryResults.length;
  document.getElementById('welcome-title').textContent = `Welcome, ${formData.name || 'User'}`;
  document.querySelectorAll('.stat-value')[0].textContent =
    (apiResults.counts.bucket_a || 0) + (apiResults.counts.bucket_b || 0) + (apiResults.counts.bucket_c || 0);
  document.querySelectorAll('.stat-value')[1].textContent = apiResults.counts.bucket_a || 0;
  
  if (window.lucide) lucide.createIcons();
}

function renderBucket(containerId, schemes, type) {
  const container = document.getElementById(containerId);
  const tagClass = type === 'portable' ? 'portable' : type === 'eligible' ? 'eligible' : type === 'discovery' ? 'eligible' : 'almost';
  const tagLabel = type === 'portable'
    ? t('carryForward')
    : type === 'eligible'
      ? t('claimLocally')
      : type === 'discovery'
        ? t('newMatch')
        : t('almostThere');
  
  container.innerHTML = schemes.map((s, i) => `
    <div class="scheme-card" onclick="openModal('${type}',${i})">
      <span class="hc-tag ${tagClass}">${tagLabel}</span>
      <h4>${s.scheme_name}</h4>
      <p>${schemeCardText(s, type)}</p>
      <div class="card-action">${t('viewDetails')} <span>→</span></div>
    </div>
  `).join('') || `<p style="color:var(--text-muted);grid-column:1/-1;text-align:center;padding:20px;">${t('noSchemes')}</p>`;
}

function schemeCardText(scheme, type) {
  if (simpleModeEnabled) {
    if (type === 'portable') return 'You can keep this benefit after moving.';
    if (type === 'eligible') return 'You can apply for this in your current state.';
    if (type === 'discovery') return 'New scheme you may not know about.';
    return 'You are close. One or two details may be missing.';
  }
  return scheme.description ? scheme.description.substring(0, 90) + '...' : 'Access welfare benefits.';
}

// --- Modal ---
function openModal(type, index) {
  const buckets = { portable: 'bucket_a', eligible: 'bucket_b', almost: 'bucket_c' };
  const scheme = type === 'discovery' ? discoveryResults[index] : apiResults.buckets[buckets[type]][index];
  const tagClass = type === 'portable' ? 'portable' : type === 'eligible' ? 'eligible' : type === 'discovery' ? 'eligible' : 'almost';
  const tagLabel = type === 'portable' ? t('carryForward') : type === 'eligible' ? t('claimLocally') : type === 'discovery' ? t('newMatch') : t('almostThere');
  
  document.getElementById('modal-title').textContent = scheme.scheme_name;
  document.getElementById('modal-tag').className = 'hc-tag ' + tagClass;
  document.getElementById('modal-tag').textContent = tagLabel;
  const reason = scheme.discovery_reason ? ` ${scheme.discovery_reason}` : '';
  document.getElementById('modal-desc').textContent = (scheme.description || 'Benefit assistance scheme.') + reason;
  
  const stepsHtml = (scheme.application_steps || []).map((step, idx) => `
    <div class="step-guide-item">
      <div class="step-num">${idx + 1}</div>
      <div><h4>Step ${idx + 1}</h4><p>${step}</p></div>
    </div>
  `).join('');
  const baseCount = (scheme.application_steps || []).length;
  document.getElementById('modal-steps').innerHTML = `
    ${stepsHtml || '<div class="step-guide-item"><div class="step-num">1</div><div><h4>Step 1</h4><p>Visit nearest CSC and verify eligibility.</p></div></div>'}
    <div class="step-guide-item"><div class="step-num">${baseCount + 1}</div><div><h4>${t('applyThrough')}</h4><p>${scheme.claim_channel || 'CSC / welfare portal'}</p></div></div>
    <div class="step-guide-item"><div class="step-num">${baseCount + 2}</div><div><h4>${t('documentsNeeded')}</h4><p>${(scheme.required_documents || []).join(', ') || 'Aadhaar Card, Bank Account Details'}</p></div></div>
    <div class="step-guide-item"><div class="step-num">${baseCount + 3}</div><div><h4>${t('missingDocuments')}</h4><p>${(scheme.missing_documents || []).join(', ') || 'None based on selected documents.'}</p></div></div>
    <div class="step-guide-item"><div class="step-num">${baseCount + 4}</div><div><h4>${t('expectedTime')}</h4><p>${scheme.time_estimate || '10-30 days'}</p></div></div>
  `;
  
  document.getElementById('modal-overlay').classList.add('active');
}

function toggleSimpleMode() {
  simpleModeEnabled = !simpleModeEnabled;
  document.body.classList.toggle('simple-mode', simpleModeEnabled);
  if (apiResults) renderDashboard();
}

function speakDashboardSummary() {
  if (!apiResults || !window.speechSynthesis) return;
  const lines = [
    t('summaryLine1', { count: apiResults.counts.bucket_a || 0 }),
    t('summaryLine2', { count: apiResults.counts.bucket_b || 0 }),
    t('summaryLine3', { count: apiResults.counts.bucket_c || 0 }),
    t('summaryLine4', { count: discoveryResults.length || 0 })
  ];
  const text = lines.join(' ');
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = LOCALE_MAP[currentLanguage] || 'en-IN';
  utterance.rate = 0.95;
  utterance.pitch = 1;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('active');
}

async function handleGoogleLogin(response) {
  const token = response.credential;
  
  try {
    const res = await fetch(`${API_BASE}/auth/google`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token: token })
    });
    
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || "Google auth failed");
    }
    if (data.status === 'success') {
      // Update form data with Google user details
      formData.name = data.user.name;
      formData.email = data.user.email;
      formData.picture = data.user.picture;
      
      // Continue in eligibility flow with authenticated identity.
      navigate('get-started');
      currentStep = 1;
      renderStep();
    } else {
      alert("Login failed: " + (data.detail || "Unknown error"));
    }
  } catch (e) {
    console.error("Auth Error:", e);
    alert("Google authentication failed. Check backend config and authorized origins.");
  }
}

async function initGoogleSignIn() {
  const container = document.getElementById('google-signin-container');
  if (!container || !window.google || !window.google.accounts) return;
  try {
    const res = await fetch(`${API_BASE}/auth/google/config`);
    const cfg = await res.json();
    if (!res.ok || !cfg.configured || !cfg.client_id) {
      container.innerHTML = '<p style="font-size:0.85rem;color:var(--text-muted);">Google Sign-In not configured.</p>';
      return;
    }
    window.google.accounts.id.initialize({
      client_id: cfg.client_id,
      callback: handleGoogleLogin,
      ux_mode: "popup"
    });
    window.google.accounts.id.renderButton(container, {
      type: "standard",
      theme: "outline",
      size: "large",
      width: 320,
      text: "signin_with",
      shape: "pill"
    });
  } catch (error) {
    console.error("Google config load failed:", error);
    container.innerHTML = '<p style="font-size:0.85rem;color:var(--text-muted);">Google Sign-In unavailable right now.</p>';
  }
}

function iconForOccupation(label) {
  const value = (label || "").toLowerCase();
  if (value.includes("construction")) return "🏗️";
  if (value.includes("factory") || value.includes("industry")) return "🏭";
  if (value.includes("agri")) return "🌾";
  if (value.includes("domestic")) return "🏠";
  if (value.includes("transport")) return "🚗";
  if (value.includes("retail") || value.includes("vendor")) return "🛍️";
  if (value.includes("office") || value.includes("clerical")) return "💼";
  return "📦";
}

async function loadDynamicOptions() {
  try {
    const res = await fetch(`${API_BASE}/meta/options`);
    if (!res.ok) return;
    const data = await res.json();
    STATES = (data.states || STATES).filter((s) => s && s !== "ALL");
    AGE_GROUPS = data.age_groups || AGE_GROUPS;
    SOCIAL_CATEGORIES = data.social_categories || SOCIAL_CATEGORIES;
    INCOME_RANGES = data.income_ranges || INCOME_RANGES;
    DOCUMENTS = data.documents || DOCUMENTS;
    const dynamicOccupations = (data.occupations || []).map((label) => ({ icon: iconForOccupation(label), label }));
    OCCUPATIONS = dynamicOccupations.length ? dynamicOccupations : OCCUPATIONS;
  } catch (_e) {
    // Fallback defaults remain in place.
  }
}

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
  navigate('home');
  initGoogleSignIn();
  applyStaticTranslations();
  setLanguage('en');
  loadDynamicOptions();
  document.getElementById('modal-overlay').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeModal();
  });
});
