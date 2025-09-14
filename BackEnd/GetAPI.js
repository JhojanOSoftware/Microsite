/* Esta vaina carga y muestra los planetas en el index.html */
(async function () {
  const API = 'http://127.0.0.1:8000/proyectos/';
  const container = document.getElementById('projects-list');
  if (!container) return;

  function safeText(t) {
    return String(t ?? '').trim();
  }

  function makeCard(proj) {
    const div = document.createElement('article');
    div.className = 'project-card';
    const title = safeText(proj.nombre);
    const desc = safeText(proj.description) || 'Descripción no disponible.';
    const imgSrc = safeText(proj.imagen);
    const github = safeText(proj.linkgithub);
    const video = safeText(proj.linkvideo);
    const fecha = safeText(proj.fecha);

    div.innerHTML = `
      <div class="project-media">
        <img loading="lazy" src="${imgSrc}" alt="${title}" onerror="this.src='Images/placeholder.png'">
      </div>
      <div class="project-body">
        <h3>${title}</h3>
        <p class="project-date">${fecha}</p>
        <p class="project-desc">${desc}</p>
        <div class="project-actions">
          ${github ? `<a class="btn btn-ghost" href="${github}" target="_blank" rel="noopener noreferrer">GitHub</a>` : ''}
          ${video ? `<a class="btn btn-ghost" href="${video}" target="_blank" rel="noopener noreferrer">Video</a>` : ''}
        </div>
      </div>
    `;
    return div;
  }

  try {
    const res = await fetch(API);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const payload = await res.json();
    // backend returns {"message": "...", "data": [...]}
    const list = Array.isArray(payload) ? payload : payload.data ?? [];
    container.innerHTML = '';
    if (!list.length) {
      container.innerHTML = '<p class="muted">No hay proyectos disponibles.</p>';
      return;
    }
    list.forEach(p => container.appendChild(makeCard(p)));
  } catch (err) {
    console.error('Error fetching projects:', err);
    container.innerHTML = '<p class="error">Error cargando proyectos. Verifica que la API esté corriendo en http://127.0.0.1:8000</p>';
  }
})();
(async function AgregarContact() {
  const wrapper = document.getElementById('contacto');
  if (!wrapper) return;

  const form = wrapper.tagName === 'FORM' ? wrapper : wrapper.querySelector('form');
  if (!form) return;

  // ensure there is a status element to show feedback
  let statusEl = wrapper.querySelector('.contact-status');
  if (!statusEl) {
    statusEl = document.createElement('div');
    statusEl.className = 'contact-status';
    statusEl.setAttribute('role', 'status');
    statusEl.setAttribute('aria-live', 'polite');
    statusEl.style.marginTop = '0.75rem';
    wrapper.appendChild(statusEl);
  }

  const submitButtons = Array.from(form.querySelectorAll('button[type="submit"], input[type="submit"]'));

  function setStatus(message, type = 'info') {
    statusEl.textContent = message;
    statusEl.dataset.status = type; // for styling (success / error / info)
    // clear after 6s
    clearTimeout(statusEl._timeout);
    statusEl._timeout = setTimeout(() => {
      statusEl.textContent = '';
      delete statusEl.dataset.status;
    }, 6000);
  }

  function setButtonsDisabled(disabled = true) {
    submitButtons.forEach(b => {
      b.disabled = disabled;
      b.setAttribute('aria-disabled', String(disabled));
    });
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData(form);
    const data = Object.fromEntries(formData);

    setButtonsDisabled(true);
    setStatus('Enviando...', 'info');

    try {
      const res = await fetch('http://127.0.0.1:8000/contactos/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!res.ok) {
        // build a readable error message (avoid [object Object])
        let errText = `HTTP ${res.status}`;
        try {
          const errJson = await res.json();
          if (errJson) {
            if (errJson.detail) {
              // FastAPI validation detail -> make a human readable string
              if (Array.isArray(errJson.detail)) {
                errText = errJson.detail.map(d => {
                  if (typeof d === 'string') return d;
                  // d usually has { loc, msg, type }
                  return d.msg ?? JSON.stringify(d);
                }).join(' | ');
              } else if (typeof errJson.detail === 'string') {
                errText = errJson.detail;
              } else {
                errText = JSON.stringify(errJson.detail);
              }
            } else if (errJson.message) {
              errText = typeof errJson.message === 'string' ? errJson.message : JSON.stringify(errJson.message);
            } else {
              errText = JSON.stringify(errJson);
            }
          }
        } catch (_) {
          // ignore JSON parse errors, keep HTTP status
        }
        throw new Error(errText);
      }

      const payload = await res.json();
      console.log('Contacto agregado:', payload);
      setStatus('Mensaje enviado correctamente. Gracias.', 'success');
      form.reset();
    } catch (err) {
      // ensure a string message
      const msg = err && err.message ? err.message : String(err);
      console.error('Error agregando contacto:', msg);
      setStatus(`Error al enviar: ${msg}`, 'error');
    } finally {
      setButtonsDisabled(false);
    }
  });
})();
// Popover for skill descriptions
(function () {
      const pop = document.getElementById('skill-popover');

      function showPopover(target, text) {
        pop.textContent = text;
        pop.setAttribute('aria-hidden', 'false');
        pop.classList.add('visible');

        const rect = target.getBoundingClientRect();
        const popRect = pop.getBoundingClientRect();
        const margin = 12;

        // preferred position: above the element, otherwise below
        let top = rect.top - popRect.height - margin;
        if (top < 70) { // account for navbar height
          top = rect.bottom + margin;
        }
        let left = rect.left + (rect.width / 2) - (popRect.width / 2);

        // keep within viewport
        left = Math.max(12, Math.min(left, window.innerWidth - popRect.width - 12));

        pop.style.top = (top + window.scrollY) + 'px';
        pop.style.left = (left + window.scrollX) + 'px';

        // remember last target for focus
        pop.dataset.anchorId = target.dataset.skillId || '';
      }

      function hidePopover() {
        pop.setAttribute('aria-hidden', 'true');
        pop.classList.remove('visible');
        pop.textContent = '';
      }

      // attach to skill items
      document.querySelectorAll('.skills ul li').forEach((li, idx) => {
        li.dataset.skillId = 'skill-' + idx;
        li.addEventListener('click', (e) => {
          const desc = li.getAttribute('data-desc') || 'Sin descripción';
          showPopover(li, desc);
        });
        li.addEventListener('keydown', (e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            li.click();
          }
        });
      });

      // close on outside click or Escape
      document.addEventListener('click', (e) => {
        const insideSkill = e.target.closest('.skills ul li');
        const insidePop = e.target.closest('#skill-popover');
        if (!insideSkill && !insidePop) hidePopover();
      });

      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') hidePopover();
      });

      // reposition on resize/scroll
      window.addEventListener('resize', hidePopover);
      window.addEventListener('scroll', () => {
        if (pop.classList.contains('visible')) hidePopover();
      });
    })();