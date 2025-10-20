/* Esta vaina carga y muestra los planetas en el index.html */
(async function () {
  const API = 'http://127.0.0.1:8000/proyectos/';
  const container = document.getElementById('projects-list');
  if (!container) return;

  function safeText(t) {
    return String(t ?? '').trim();
  }

  // resuelve las imagenes dentro del html
function resolveImageSrc(proj) {
  let img = safeText(proj.imagen) || '';
  if (/^https?:\/\//i.test(img)) return img;
  return 'http://127.0.0.1:8000/images/' + img;  // 🔹 asegúrate que arme la URL completa
}


  function makeCard(proj) {
    const div = document.createElement('article');
    div.className = 'project-card';
    const title = safeText(proj.nombre);
    const desc = safeText(proj.description) || 'Descripción no disponible.';
    const imgSrc = resolveImageSrc(proj);
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
/* Render projects as collapsible title-cards */
(async function renderProjects() {
  const API = 'http://127.0.0.1:8000/proyectos/';
  const container = document.getElementById('projects-list');
  if (!container) return;

  function safeText(t) { return String(t ?? '').trim(); }

// Resolve image URL -> Always return a usable URL
function resolveImageSrc(proj) {
  const img = safeText(proj.imagen || proj.imagen_url || proj.image) || '';

  // Empty -> placeholder (ruta relativa dentro de tu frontend)
  if (!img) return 'Images/placeholder.png';

  // Si ya es absoluta, la devolvemos tal cual
  if (/^https?:\/\//i.test(img)) return img;

  // Normalize: remove leading slashes and build the URL that FastAPI sirve
  const filename = img.replace(/^\/+/, '');                     // "weakpass.png"
  return `http://127.0.0.1:8000/images/${filename}`;            // http://127.0.0.1:8000/images/weakpass.png
}
  function makeCard(proj) {
    const article = document.createElement('article');
    article.className = 'project-card';
    article.tabIndex = 0;

    const title = safeText(proj.nombre) || 'Proyecto';
    const desc = safeText(proj.description) || '';
    const imgSrc = resolveImageSrc(proj);
    const github = safeText(proj.linkgithub);
    const video = safeText(proj.linkvideo);
    const fecha = safeText(proj.fecha);

    article.innerHTML = `
      <div class="card-header" role="button" aria-expanded="false">
        <div class="project-title">${title}</div>
        <div class="chev">▼</div>
      </div>
      <div class="card-body" aria-hidden="true">
        <div class="project-media">
          <img src="${imgSrc}" alt="${title}" onerror="this.src='Images/placeholder.png'">
          <div class="img-path" style="font-size:0.8em;color:#888;margin-top:4px;">${safeText(proj.imagen)}</div>
        </div>
        <p class="project-date">${fecha}</p>
        <p class="project-desc">${desc}</p>
        <div class="project-actions">
          ${github ? `<a class="btn-icon" href="${github}" target="_blank" rel="noopener noreferrer" data-label="GitHub">GH</a>` : ''}
          ${video ? `<a class="btn-icon" href="${video}" target="_blank" rel="noopener noreferrer" data-label="Video">▶</a>` : ''}
        </div>
      </div>
    `;
    // toggle behavior
    const header = article.querySelector('.card-header');
    const body = article.querySelector('.card-body');
    function setExpanded(exp) {
      article.classList.toggle('expanded', exp);
      header.setAttribute('aria-expanded', String(exp));
      body.setAttribute('aria-hidden', String(!exp));
    }
    header.addEventListener('click', () => setExpanded(!article.classList.contains('expanded')));
    // keyboard toggle
    article.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        setExpanded(!article.classList.contains('expanded'));
      }
      if (e.key === 'Escape') setExpanded(false);
    });
    return article;
  }

  try {
    const res = await fetch(API);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const payload = await res.json();
    const list = Array.isArray(payload) ? payload : (payload.data ?? payload);
    container.innerHTML = '';
    if (!list || !list.length) {
      container.innerHTML = '<p class="muted">No hay proyectos disponibles.</p>';
      return;
    }
    list.forEach(p => container.appendChild(makeCard(p)));
  } catch (err) {
    console.error('Error fetching projects:', err);
    container.innerHTML = '<p class="error">Error cargando proyectos. Verifica que la API esté corriendo en http://127.0.0.1:8000</p>';
  }
})();
(async function loadMapas() {
  const API = "http://127.0.0.1:8000/mapas/"; // tu endpoint FastAPI
  


  try {
    // 1. Llamar a la API
    const res = await fetch(API);
    if (!res.ok) throw new Error("Error HTTP " + res.status);
    const payload = await res.json();
    const lugares = payload.data ?? [];


    
    // 2. Crear mapa
    const mapitas = L.map("map").setView([lugares[0].latitud, lugares[0].longitud], 11);

    // 3. Capa base
    // Añadir capa base
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(mapitas);

    

   // 5. Añadir marcadores al mapa
    const markers = [];
    lugares.forEach((lugar) => {
      const lat = parseFloat(lugar.latitud);
      const lon = parseFloat(lugar.longitud);

      const marker = L.marker([lat, lon]).addTo(mapitas);

      marker.bindPopup(`
        <b>${lugar.placename}</b><br>
        ${lugar.description}<br>
        <small><i>${lugar.addresplace}</i></small><br>
        ⭐ Puntaje: ${lugar.score ?? "N/A"}<br>
      `);
      

      marker.on("click", function () {
        // acercamiento suave al marcador
        mapitas.flyTo(marker.getLatLng(), 17, {
          animate: true,
          duration: 5 // duración en segundos (ajusta a tu gusto: 3 = rápido, 5+ = más lento)
        });

        // abrir popup al llegar
        marker.openPopup();
      });

      markers.push(marker);
    });

    // 6. Cambiar vista con el selector
    selector.addEventListener("change", (e) => {
      const idx = parseInt(e.target.value, 10);
      const lugar = lugares[idx];
      const lat = parseFloat(lugar.latitud);
      const lon = parseFloat(lugar.longitud);

      map.setView([lat, lon], 15);
      markers[idx].openPopup();
    });
  } catch (err) {
    console.error("Error cargando mapas:", err);
  }
})();



/* --- Chat integration: UI behavior + POST to backend Chat endpoint --- */
(function initChat() {
  const toggle = document.getElementById('chatbot-toggle') || document.querySelector('.chatbot-toggler');
  const widget = document.getElementById('chatbot');
  const closeBtn = document.getElementById('chatbot-close');
  const sendBtn = document.getElementById('chat-send');
  const input = document.getElementById('chat-input');
  const messages = document.getElementById('chat-messages');

  if (!toggle || !widget || !sendBtn || !input || !messages) return;

  function append(text, who = 'bot') {
    const d = document.createElement('div');
    d.className = 'message ' + (who === 'user' ? 'user' : 'bot');
    d.textContent = text;
    messages.appendChild(d);
    messages.scrollTop = messages.scrollHeight;
    return d;
  }

  function setOpen(open) {
    widget.setAttribute('aria-hidden', open ? 'false' : 'true');
    if (open) input.focus();
  }

  toggle.addEventListener('click', () => {
    const hidden = widget.getAttribute('aria-hidden') === 'true';
    setOpen(hidden);
  });
  if (closeBtn) closeBtn.addEventListener('click', () => setOpen(false));

  async function sendToBackend(text) {
  const url = 'http://127.0.0.1:8000/chat-simple/';
  const body = new URLSearchParams({ mensaje: text }); // <-- clave "mensaje" (Form)
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json' },
    body: body.toString()
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const j = await res.json();
  return j.respuesta ?? j.significado ?? j.answer ?? j.result ?? j.message ?? JSON.stringify(j);
}

  async function handleSend() {
    const text = input.value.trim();
    if (!text) return;
    append(text, 'user');
    input.value = '';
    input.disabled = true;
    const typing = append('Escribiendo...', 'bot');

    try {
      const reply = await sendToBackend(text);
      typing.textContent = String(reply);
    } catch (err) {
      console.error('Chat error:', err);
      typing.textContent = 'Error al contactar el servidor. Revisa la consola.';
    } finally {
      input.disabled = false;
      input.focus();
      messages.scrollTop = messages.scrollHeight;
    }
  }

  sendBtn.addEventListener('click', handleSend);
  input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') { e.preventDefault(); handleSend(); }
  });
})();
(async function () {
  const API = 'http://127.0.0.1:8000/coffee/'; // tu endpoint FastAPI
  const container = document.getElementById('coffeid1'); // el div en tu HTML
  if (!container) return;

  function safeText(t) {
    return String(t ?? '').trim();
  }

  // resolver la ruta de la imagen
  function resolveImageSrc(cafe) {
    let img = safeText(cafe.coffe_image) || '';
    if (/^https?:\/\//i.test(img)) return img; 
    return 'http://127.0.0.1:8000/images/' + img; // carpeta donde montaste las imágenes
  }

  function makeCard(cafe) {
    const div = document.createElement('article');
    div.className = 'coffe-card';
    const title = safeText(cafe.coffee_type);
    const desc = safeText(cafe.description) || 'Descripción no disponible.';
    const imgSrc = resolveImageSrc(cafe);
    const video = safeText(cafe.video);

    div.innerHTML = `
      <div class="coffe-media">
        <img loading="lazy" src="${imgSrc}" alt="${title}" onerror="this.src='Images/placeholder.png'">
      </div>
      <div class="coffe-body">
        <h3>${title}</h3>
        <p class="coffe-desc">${desc}</p>
        <div class="coffe-actions">
          ${video ? `<a class="btn btn-ghost" href="${video}" target="_blank" rel="noopener noreferrer">Ver Video</a>` : ''}
        </div>
      </div>
    `;
    return div;
  }

  try {
    const res = await fetch(API);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const payload = await res.json();
    const list = Array.isArray(payload) ? payload : payload.data ?? [];
    container.innerHTML = '';
    if (!list.length) {
      container.innerHTML = '<p class="muted">No hay cafés disponibles.</p>';
      return;
    }
    list.forEach(c => container.appendChild(makeCard(c)));
  } catch (err) {
    console.error('Error fetching coffee:', err);
    container.innerHTML = '<p class="error">Error cargando cafés. Verifica que la API esté corriendo en http://127.0.0.1:8000</p>';
  }
})();

