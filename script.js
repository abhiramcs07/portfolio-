/**
 * Abhiram C S - Portfolio & Client Conversion Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileNav();
  initActiveNavHighlight();
  initProjectFiltering();
  initQuoteEstimator();
  initContactForm();
  initProjectModals();
  initHeaderScroll();
  initBackendStatus();
});

/* ==========================================================================
   Header Scroll State
   ========================================================================== */
function initHeaderScroll() {
  const header = document.getElementById('header');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 30) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  }, { passive: true });
}

/* ==========================================================================
   Mobile Navigation Toggle
   ========================================================================== */
function initMobileNav() {
  const mobileToggle = document.getElementById('mobile-toggle');
  const mainNav = document.getElementById('main-nav');
  const navLinks = document.querySelectorAll('.nav-link');

  if (!mobileToggle || !mainNav) return;

  mobileToggle.addEventListener('click', () => {
    const isOpen = mainNav.classList.toggle('open');
    mobileToggle.classList.toggle('active');
    mobileToggle.setAttribute('aria-expanded', isOpen);
  });

  // Close menu when clicking nav links
  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      mainNav.classList.remove('open');
      mobileToggle.classList.remove('active');
      mobileToggle.setAttribute('aria-expanded', 'false');
    });
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!mainNav.contains(e.target) && !mobileToggle.contains(e.target) && mainNav.classList.contains('open')) {
      mainNav.classList.remove('open');
      mobileToggle.classList.remove('active');
      mobileToggle.setAttribute('aria-expanded', 'false');
    }
  });
}

/* ==========================================================================
   Active Navigation Highlighting on Scroll (Work, Services, Contact)
   ========================================================================== */
function initActiveNavHighlight() {
  const sections = ['work', 'services', 'contact'];
  const navLinks = {
    work: document.getElementById('nav-work'),
    services: document.getElementById('nav-services'),
    contact: document.getElementById('nav-contact')
  };

  const observerOptions = {
    root: null,
    rootMargin: '-20% 0px -60% 0px',
    threshold: 0
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        // Remove active from all
        Object.values(navLinks).forEach(link => link && link.classList.remove('active'));
        // Add active to current
        if (navLinks[id]) {
          navLinks[id].classList.add('active');
        }
      }
    });
  }, observerOptions);

  sections.forEach(id => {
    const el = document.getElementById(id);
    if (el) observer.observe(el);
  });
}

/* ==========================================================================
   Work / Project Filtering Tabs
   ========================================================================== */
function initProjectFiltering() {
  const filterBtns = document.querySelectorAll('.filter-btn');
  const projectCards = document.querySelectorAll('.project-card');

  if (!filterBtns.length || !projectCards.length) return;

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      // Set active button
      filterBtns.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-selected', 'true');

      const filterValue = btn.dataset.filter;

      projectCards.forEach(card => {
        const category = card.dataset.category;
        if (filterValue === 'all' || category === filterValue) {
          card.style.display = 'flex';
          setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
          }, 20);
        } else {
          card.style.opacity = '0';
          card.style.transform = 'translateY(10px)';
          setTimeout(() => {
            card.style.display = 'none';
          }, 200);
        }
      });
    });
  });
}

/* ==========================================================================
   Interactive Quote & WhatsApp Inquiry Generator
   ========================================================================== */
function initQuoteEstimator() {
  const pillBtns = document.querySelectorAll('#business-type-pills .pill-select');
  const featureCheckboxes = document.querySelectorAll('#features-checkboxes input[type="checkbox"]');
  const timelineDisplay = document.getElementById('summary-timeline');
  const launchWhatsAppBtn = document.getElementById('launch-whatsapp-quote');

  let selectedType = 'Local Shop / Store';

  function updateWhatsAppLink() {
    // Collect features
    const selectedFeatures = [];
    featureCheckboxes.forEach(cb => {
      if (cb.checked) {
        selectedFeatures.push(cb.value);
      }
    });

    // Estimate timeline based on count of features
    let timeline = '3 to 5 Days Delivery';
    if (selectedFeatures.length >= 4 || selectedType.includes('E-Commerce')) {
      timeline = '5 to 8 Days Delivery';
    } else if (selectedFeatures.length <= 2) {
      timeline = '2 to 4 Days Delivery';
    }
    if (timelineDisplay) {
      timelineDisplay.textContent = timeline;
    }

    // Build message
    const featuresList = selectedFeatures.length > 0 
      ? selectedFeatures.join(', ') 
      : 'Standard informative pages';

    const text = `Hi Abhiram, I would like to get a quote for my project:
- Website Type: ${selectedType}
- Features Needed: ${featuresList}
- Target Timeline: ${timeline}

Could we discuss pricing and get started?`;

    const encodedText = encodeURIComponent(text);
    if (launchWhatsAppBtn) {
      launchWhatsAppBtn.href = `https://wa.me/919207320236?text=${encodedText}`;
    }
  }

  // Handle pill selections
  pillBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      pillBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectedType = btn.dataset.value;
      updateWhatsAppLink();
    });
  });

  // Handle checkbox toggles
  featureCheckboxes.forEach(cb => {
    cb.addEventListener('change', updateWhatsAppLink);
  });

  // Initial call
  updateWhatsAppLink();
}

/* ==========================================================================
   Contact Form Handling
   ========================================================================== */
function initContactForm() {
  const form = document.getElementById('contact-form');
  const waBtn = document.getElementById('btn-submit-whatsapp');
  const feedback = document.getElementById('form-feedback');
  const submitBtn = document.getElementById('btn-submit-form');

  if (!form) return;

  // "Forward to WhatsApp" Button Click
  if (waBtn) {
    waBtn.addEventListener('click', async () => {
      const name = document.getElementById('client-name').value.trim();
      const phone = document.getElementById('client-phone').value.trim();
      const email = document.getElementById('client-email').value.trim();
      const type = document.getElementById('client-type').value;
      const message = document.getElementById('client-message').value.trim();

      if (!name || !phone) {
        showFeedback('Please provide at least your Name and Phone/WhatsApp number before sending.', 'error');
        return;
      }

      // Proactively save to Python backend in the background if server is running
      try {
        fetch('/api/contact', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, phone, email, website_type: type, message })
        }).catch(() => {});
      } catch (err) {}

      const text = `Hi Abhiram! Website Project Inquiry:
- Name: ${name}
- Phone: ${phone}
- Website Type: ${type}
- Details: ${message || 'No additional details provided'}`;

      const waUrl = `https://wa.me/919207320236?text=${encodeURIComponent(text)}`;
      window.open(waUrl, '_blank');
      showToast('Opening WhatsApp with your project details...');
    });
  }

  // Form Submit Handler (Posts to Python API or triggers direct email fallback)
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = document.getElementById('client-name').value.trim();
    const phone = document.getElementById('client-phone').value.trim();
    const email = document.getElementById('client-email').value.trim();
    const type = document.getElementById('client-type').value;
    const message = document.getElementById('client-message').value.trim();

    if (!name || !phone || !message) {
      showFeedback('Please fill out all required fields.', 'error');
      return;
    }

    // Set button loading state
    const originalBtnHtml = submitBtn ? submitBtn.innerHTML : 'Send Message';
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span>Saving Inquiry...</span>';
    }

    let savedToBackend = false;

    // Try posting to Python Flask Backend (/api/contact)
    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name,
          phone: phone,
          email: email,
          website_type: type,
          message: message
        })
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          savedToBackend = true;
        }
      }
    } catch (netErr) {
      // Backend not running (e.g. static file preview or github pages)
      savedToBackend = false;
    }

    // Restore button state
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = originalBtnHtml;
    }

    if (savedToBackend) {
      showFeedback('✓ Inquiry saved to Python database! Abhiram has been alerted. Opening WhatsApp to chat immediately...', 'success');
      showToast('Lead recorded in Python database! Opening WhatsApp...');
      form.reset();

      // Open WhatsApp chat after brief pause for instant communication
      setTimeout(() => {
        const waText = `Hi Abhiram, I just submitted an inquiry on your website:
- Name: ${name}
- Phone: ${phone}
- Service: ${type}
- Message: ${message}`;
        window.open(`https://wa.me/919207320236?text=${encodeURIComponent(waText)}`, '_blank');
      }, 1200);

    } else {
      // Direct mailto launcher fallback
      const subject = encodeURIComponent(`Website Inquiry from ${name} (${type})`);
      const body = encodeURIComponent(
        `Name: ${name}\nPhone/WhatsApp: ${phone}\nEmail: ${email || 'Not provided'}\nWebsite Type: ${type}\n\nProject Requirements:\n${message}`
      );

      window.location.href = `mailto:abhiramcs05@gmail.com?subject=${subject}&body=${body}`;

      showFeedback('✓ Thank you! Opening your email client to send your message. You can also message directly on WhatsApp (+91 9207320236).', 'success');
      showToast('Inquiry drafted! Reach out directly anytime.');
      form.reset();
    }
  });

  function showFeedback(msg, type) {
    if (!feedback) return;
    feedback.textContent = msg;
    feedback.className = `form-feedback ${type}`;
    feedback.classList.remove('hidden');
    setTimeout(() => {
      feedback.classList.add('hidden');
    }, 7000);
  }
}

/* ==========================================================================
   Backend Status Ping (Verifies Python Flask Backend connectivity)
   ========================================================================== */
function initBackendStatus() {
  fetch('/api/health')
    .then(res => res.json())
    .then(data => {
      if (data && data.status === 'healthy') {
        const badge = document.getElementById('backend-status-badge');
        if (badge) {
          badge.style.display = 'inline-flex';
          badge.innerHTML = `🐍 Python Flask API: Online (${data.python_version}) &bull; <a href="/leads" style="color:var(--accent-cyan); margin-left:4px; text-decoration:underline;">View Leads</a>`;
        }
      }
    })
    .catch(() => {
      // Backend not running, which is completely normal in static mode
    });
}

/* ==========================================================================
   Project Detail Modals Data & Interactions
   ========================================================================== */
const projectData = {
  'modal-shopwave': {
    title: 'ShopWave — WhatsApp Commerce Store',
    category: 'E-Commerce & Retail Storefront',
    tech: 'HTML5, CSS3, Vanilla JavaScript, WhatsApp API',
    liveUrl: 'https://abhiramcs07.github.io/shopWave-/',
    overview: 'A fully functional e-commerce storefront where customers browse products, filter by category, add items to a shopping bag, and send the entire order to the shop owner via WhatsApp in one tap.',
    features: [
      { title: 'Product Catalog with Search', desc: 'Live search and category filter pills let customers instantly find products across the entire store.' },
      { title: '1-Tap WhatsApp Checkout', desc: 'Customers build a bag and tap to auto-send the full order list with quantities to the owner\'s WhatsApp.' },
      { title: 'Shopping Bag with Badge', desc: 'Real-time bag counter in the header updates as customers add or remove items.' },
      { title: 'Secured Owner Portal', desc: 'Password-protected admin view for the store owner to manage product listings without any backend server.' }
    ],
    waMessage: 'Hi Abhiram, I saw the ShopWave project and want a similar WhatsApp commerce store for my business!'
  },
  'modal-jtfarms': {
    title: 'J & T Farms — Broiler Box Booking Portal',
    category: 'Agriculture & B2B Supply Platform',
    tech: 'HTML5, CSS3, JavaScript, Leaflet.js (GPS Maps)',
    liveUrl: 'https://abhiramcs07.github.io/J-T-FARMS/',
    overview: 'A dedicated B2B ordering portal for J & T Farms Chempanoda, allowing registered chicken stall owners across 6 focus areas to book tomorrow\'s broiler chicken supply during the nightly booking window.',
    features: [
      { title: 'Live Market Rate Display', desc: 'Shows the current Kozhikode broiler market rate in real-time so stall owners know exact pricing.' },
      { title: 'Daily Booking Window Countdown', desc: 'Countdown timer tracks the 6 PM–10 PM booking window, automatically opening and closing orders.' },
      { title: 'Stall Registration System', desc: 'Chicken stall owners register once; their shop is saved and auto-selected on future visits.' },
      { title: 'Leaflet GPS Route Tracking', desc: 'Interactive map showing delivery focus areas: Peruvannamuzhi, Chempanoda, Panthirikkara, and more.' }
    ],
    waMessage: 'Hi Abhiram, I saw the J & T Farms portal and want a similar B2B ordering system for my business!'
  },
  'modal-campusevents': {
    title: 'Campus Events — College Event Platform',
    category: 'College & Event Management Portal',
    tech: 'HTML5, CSS3, JavaScript, LocalStorage Auth System',
    liveUrl: 'https://abhiramcs07.github.io/event-/',
    overview: 'A multi-college event management system where each institution creates a secure account, manages their own programs, and tracks student participation — with full data isolation between colleges.',
    features: [
      { title: 'College Account System', desc: 'Each college signs up independently; they can only see and manage their own events and student data.' },
      { title: 'Event Creation & Management', desc: 'Colleges create events with details like date, venue, capacity, and registration deadlines.' },
      { title: 'Student Registration Tracking', desc: 'Track which students have registered for each event with a clean participant list view.' },
      { title: 'Secure Data Isolation', desc: 'Each college\'s events are completely separate — no college can access another institution\'s data.' }
    ],
    waMessage: 'Hi Abhiram, I saw the Campus Events portal and want a similar event management system for my college!'
  }
};

function initProjectModals() {
  const detailButtons = document.querySelectorAll('.btn-card-details');
  const modalBackdrop = document.getElementById('modal-backdrop');
  const modalContainer = document.getElementById('modal-body-container');
  const closeBtn = document.getElementById('modal-close-btn');

  if (!modalBackdrop || !modalContainer) return;

  function openModal(modalKey) {
    const data = projectData[modalKey];
    if (!data) return;

    modalContainer.innerHTML = `
      <div class="modal-header-hero">
        <div class="modal-tag">${data.category}</div>
        <h2 class="modal-title" id="modal-title">${data.title}</h2>
        <div class="tech-tag" style="display:inline-block; margin-bottom: 0.8rem;">Stack: ${data.tech}</div>
        <p class="modal-overview">${data.overview}</p>
      </div>

      <h4 style="color:#ffffff; margin-bottom: 0.8rem;">Key Business Features Implemented:</h4>
      <div class="modal-features-grid">
        ${data.features.map(f => `
          <div class="modal-feature-item">
            <strong>${f.title}</strong>
            <p>${f.desc}</p>
          </div>
        `).join('')}
      </div>

      <div class="modal-actions" style="display:flex;flex-direction:column;gap:0.75rem;">
        ${data.liveUrl ? `<a href="${data.liveUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary" style="width:100%;justify-content:center;display:flex;align-items:center;gap:0.5rem;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          <span>View Live Site</span>
        </a>` : ''}
        <a href="https://wa.me/919207320236?text=${encodeURIComponent(data.waMessage)}" target="_blank" rel="noopener noreferrer" class="btn btn-whatsapp-large" style="width: 100%;">
          <svg class="icon-whatsapp" viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.582 2.128 2.182-.573c.978.58 1.911.928 3.145.929 3.178 0 5.767-2.587 5.768-5.766.001-3.187-2.575-5.77-5.764-5.771zm3.392 8.244c-.144.405-.837.774-1.17.824-.299.045-.677.063-1.092-.069-.252-.08-.575-.187-.988-.365-1.739-.751-2.874-2.502-2.961-2.617-.087-.116-.708-.94-.708-1.793s.448-1.273.607-1.446c.159-.173.346-.217.462-.217l.332.007c.106.005.249-.04.39.299.144.347.491 1.2.534 1.287.043.087.072.188.014.304-.058.116-.087.188-.173.289l-.26.304c-.087.086-.177.18-.076.354.101.174.449.741.964 1.201.662.591 1.221.774 1.394.861.174.086.275.073.376-.044.101-.116.433-.506.549-.68.116-.173.231-.144.39-.086s1.011.477 1.184.564.289.13.332.202c.045.073.045.42-.099.825zm-3.392-12.416c-5.523 0-10 4.477-10 10 0 1.768.459 3.428 1.261 4.872l-1.339 4.89 5.019-1.316c1.397.761 2.997 1.196 4.698 1.196 5.522 0 10-4.477 10-10s-4.478-10-10-10z"/></svg>
          <span>Chat About Building a Similar Project (+91 9207320236)</span>
        </a>
      </div>
    `;

    modalBackdrop.classList.remove('hidden');
    modalBackdrop.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function closeModal() {
    modalBackdrop.classList.add('hidden');
    modalBackdrop.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  }

  detailButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const modalKey = btn.dataset.modal;
      openModal(modalKey);
    });
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', closeModal);
  }

  modalBackdrop.addEventListener('click', (e) => {
    if (e.target === modalBackdrop) {
      closeModal();
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !modalBackdrop.classList.contains('hidden')) {
      closeModal();
    }
  });
}

/* ==========================================================================
   Toast Notification Utility
   ========================================================================== */
function showToast(message) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;

  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 3200);
}
