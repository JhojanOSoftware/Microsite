/* Apple HIG Project Loading with Search & Filter
   Principles Applied:
   - CLARITY: Immediate visual feedback on search/filter
   - RESPONSIVENESS: Smooth transitions, no jarring updates
   - FEEDBACK: Clear empty states and loading indicators
*/
(async function () {
  const API = 'http://127.0.0.1:8000/proyectos/';
  const container = document.getElementById('projects-list');
  if (!container) return;

  // Store all projects for filtering
  let allProjects = [];
  let currentSort = 'recent';
  let currentSearch = '';

  function safeText(t) {
    return String(t ?? '').trim();
  }

  // resuelve las imagenes dentro del html
  function resolveImageSrc(proj) {
    let img = safeText(proj.imagen) || '';
    if (/^https?:\/\//i.test(img)) return img;
    return 'http://127.0.0.1:8000/images/' + img;
  }

  function makeCard(proj) {
    const div = document.createElement('article');
    div.className = 'project-card';
    div.dataset.projectName = safeText(proj.nombre).toLowerCase();
    div.dataset.projectDesc = safeText(proj.description).toLowerCase();
    
    const title = safeText(proj.nombre);
    const desc = safeText(proj.description) || 'Descripción no disponible.';
    const imgSrc = resolveImageSrc(proj);
    const github = safeText(proj.linkgithub);
    const video = safeText(proj.linkvideo);
    const fecha = safeText(proj.fecha);
    
    // Extract technologies from description or use defaults
    const getTechnologies = () => {
      const techKeywords = {
        'python': 'Python', 'mysql': 'MySQL', 'javascript': 'JavaScript',
        'html': 'HTML', 'css': 'CSS', 'react': 'React', 'node': 'Node.js',
        'uvicorn': 'UVICORN', 'fastapi': 'FastAPI', 'asgi': 'ASGI',
        'pdf': 'PDF', 'api': 'API', 'rest': 'REST'
      };
      const foundTechs = [];
      const searchText = (title + ' ' + desc).toLowerCase();
      for (const [key, label] of Object.entries(techKeywords)) {
        if (searchText.includes(key) && foundTechs.length < 4) {
          foundTechs.push(label);
        }
      }
      return foundTechs.length > 0 ? foundTechs : ['Desarrollo Web'];
    };
    const technologies = getTechnologies();

    div.innerHTML = `
      <div class="project-media">
        <img loading="lazy" src="${imgSrc}" alt="${title}" onerror="this.src='Frontend/Images/placeholder.png'">
      </div>
      <div class="project-body">
        <div class="project-header">
          <h3>${title}</h3>
          <span class="project-date">${fecha}</span>
        </div>
        <p class="project-desc">${desc}</p>
        <div class="project-tags">
          ${technologies.map(tech => `<span class="project-tag">${tech}</span>`).join('')}
        </div>
        <div class="project-actions">
          ${video ? `<a class="btn" href="${video}" target="_blank" rel="noopener noreferrer" aria-label="Ver demostración">
            <svg aria-hidden="true" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z"/>
              <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
            </svg>
            Ver Demo
          </a>` : ''}
          ${github ? `<a class="btn-ghost" href="${github}" target="_blank" rel="noopener noreferrer" aria-label="Ver código en GitHub">
            <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
            </svg>
            Código
          </a>` : ''}
        </div>
      </div>
    `;
    return div;
  }

  // Sort projects based on current filter
  function sortProjects(projects, sortType) {
    const sorted = [...projects];
    switch (sortType) {
      case 'recent':
        return sorted.sort((a, b) => {
          const dateA = new Date(a.fecha || '1970-01-01');
          const dateB = new Date(b.fecha || '1970-01-01');
          return dateB - dateA;
        });
      case 'oldest':
        return sorted.sort((a, b) => {
          const dateA = new Date(a.fecha || '1970-01-01');
          const dateB = new Date(b.fecha || '1970-01-01');
          return dateA - dateB;
        });
      case 'name':
        return sorted.sort((a, b) => 
          safeText(a.nombre).localeCompare(safeText(b.nombre))
        );
      default:
        return sorted;
    }
  }

  // Filter projects by search query
  function filterProjects(projects, query) {
    if (!query) return projects;
    const lowerQuery = query.toLowerCase();
    return projects.filter(proj => {
      const title = safeText(proj.nombre).toLowerCase();
      const desc = safeText(proj.description).toLowerCase();
      return title.includes(lowerQuery) || desc.includes(lowerQuery);
    });
  }

  // Render projects to DOM
  function renderProjects() {
    let filtered = filterProjects(allProjects, currentSearch);
    let sorted = sortProjects(filtered, currentSort);

    container.innerHTML = '';
    
    if (!sorted.length) {
      const noResults = document.createElement('div');
      noResults.style.cssText = 'grid-column: 1/-1; text-align: center; padding: 60px 20px;';
      noResults.innerHTML = `
        <p style="font-size: 18px; color: var(--text-secondary); margin: 0 0 8px;">
          ${currentSearch ? 'No se encontraron proyectos' : 'No hay proyectos disponibles'}
        </p>
        ${currentSearch ? `<p style="font-size: 14px; color: var(--text-tertiary); margin: 0;">Intenta con otros términos de búsqueda</p>` : ''}
      `;
      container.appendChild(noResults);
      return;
    }

    sorted.forEach(p => container.appendChild(makeCard(p)));
  }

  // Search functionality
  const searchInput = document.getElementById('project-search');
  const clearBtn = document.getElementById('clear-search');

  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      currentSearch = e.target.value.trim();
      renderProjects();
      
      // Show/hide clear button
      if (clearBtn) {
        if (currentSearch) {
          clearBtn.style.display = 'flex';
          clearBtn.classList.add('visible');
        } else {
          clearBtn.classList.remove('visible');
          setTimeout(() => clearBtn.style.display = 'none', 200);
        }
      }
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      searchInput.value = '';
      currentSearch = '';
      renderProjects();
      clearBtn.classList.remove('visible');
      setTimeout(() => clearBtn.style.display = 'none', 200);
      searchInput.focus();
    });
  }

  // Filter buttons
  const filterBtns = document.querySelectorAll('.filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      // Update active state
      filterBtns.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');
      
      currentSort = btn.dataset.sort;
      renderProjects();
    });
  });

  // Initial load
  try {
    const res = await fetch(API);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const payload = await res.json();
    allProjects = Array.isArray(payload) ? payload : payload.data ?? [];
    renderProjects();
  } catch (err) {
    console.error('Error fetching projects:', err);
    container.innerHTML = '<p class="error" style="grid-column: 1/-1; text-align: center; padding: 40px;">Error cargando proyectos. Verifica que la API esté corriendo en http://127.0.0.1:8000</p>';
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
// Map handling: global instance + safe init
let mapitas = null;

function initMap(centerLat, centerLon) {
  if (!document.getElementById('map')) {
    console.warn('Contenedor #map no encontrado en el DOM');
    return;
  }

  if (!mapitas) {
    mapitas = L.map('map').setView([centerLat, centerLon], 11);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(mapitas);
  } else {
    try { mapitas.setView([centerLat, centerLon], 11); } catch (e) { console.warn(e); }
  }

  // Forzar recalculo de tamaño al mostrarse (evita mapa colapsado si el contenedor estaba oculto)
  setTimeout(() => {
    try { mapitas.invalidateSize(); } catch (e) { /* noop */ }
  }, 200);
}

(async function loadMapas() {
  const API = "http://127.0.0.1:8000/mapas/";

  try {
    const res = await fetch(API);
    if (!res.ok) throw new Error("Error HTTP " + res.status);
    const payload = await res.json();
    const lugares = Array.isArray(payload) ? payload : (payload.data ?? []);

    if (!Array.isArray(lugares) || lugares.length === 0) {
      console.warn('No hay lugares devueltos por /mapas/');
      return;
    }

    // Buscar la primera coordenada válida
    let center = null;
    for (const lugar of lugares) {
      const lat = parseFloat(lugar.latitud);
      const lon = parseFloat(lugar.longitud);
      if (Number.isFinite(lat) && Number.isFinite(lon)) { center = { lat, lon }; break; }
    }

    if (!center) {
      console.warn('No se encontraron coordenadas válidas en los lugares recibidos');
      return;
    }

    initMap(center.lat, center.lon);

    const markers = [];
    lugares.forEach((lugar) => {
      const lat = parseFloat(lugar.latitud);
      const lon = parseFloat(lugar.longitud);
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) return; // ignorar entradas inválidas

      const marker = L.marker([lat, lon]).addTo(mapitas);

      const popupContent = `
        <div class="map-popup-compact">
          <div class="popup-header">
            <h5>${lugar.placename || ''}</h5>
            <span class="score-badge">⭐ ${lugar.score || "N/A"}</span>
          </div>
          <div class="popup-content">
            <p class="address">📍 ${lugar.addresplace || ''}</p>
            <p class="description">${truncateText(String(lugar.description || ''), 60)}</p>
            ${lugar.coffee_type ? `
              <div class="coffee-info">
                <span class="coffee-type">☕ ${lugar.coffee_type}</span>
              </div>
            ` : ''}
          </div>
          <div class="popup-actions">
            <button class="btn-more-info" onclick="mostrarDetallesCompletos(${lugar.id})">
              🔍 Más info
            </button>
            <div class="action-buttons">
              <button class="btn-delete" onclick="eliminarMapa(${lugar.id})">
                🗑️
              </button>
              <button class="btn-edit" onclick="abrirFormularioActualizar(${lugar.id})">
                ✏️
              </button>
            </div>
          </div>
        </div>
      `;

      marker.bindPopup(popupContent, { maxWidth: 250, minWidth: 200 });

      marker.on('click', function () {
        try {
          mapitas.flyTo(marker.getLatLng(), 17, { animate: true, duration: 1.5 });
        } catch (e) { /* noop */ }
        marker.openPopup();
      });

      markers.push(marker);
    });

  } catch (err) {
    console.error("Error cargando mapas:", err);
  }
})();

// Función para truncar texto
function truncateText(text, maxLength) {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

// Función para mostrar detalles completos en un modal
function mostrarDetallesCompletos(mapaId) {
  // Cerrar popup actual si existe
  if (typeof mapitas !== 'undefined') {
    mapitas.closePopup();
  }

  // Mostrar estado de carga
  const loadingModal = crearModalCarga();
  
  // Hacer llamada directa a la API para obtener los datos específicos del mapa
  fetch(`http://127.0.0.1:8000/mapas/${mapaId}`)
    .then(res => {
      if (!res.ok) {
        throw new Error(`Error HTTP ${res.status}`);
      }
      return res.json();
    })
    .then(payload => {
      // Remover modal de carga
      loadingModal.remove();
      
      const lugar = payload.data;
      if (!lugar) {
        throw new Error('No se encontraron datos del lugar');
      }
      
      console.log('Datos del lugar cargados:', lugar);
      crearModalDetalles(lugar);
    })
    .catch(err => {
      console.error('Error cargando detalles:', err);
      // Remover modal de carga
      loadingModal.remove();
      
      // Mostrar error al usuario
      alert(`Error al cargar los detalles: ${err.message}`);
    });
}

// Función para crear modal de carga
function crearModalCarga() {
  const modal = document.createElement('div');
  modal.className = 'loading-modal';
  modal.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    z-index: 1000;
    text-align: center;
  `;

  modal.innerHTML = `
    <div class="loading-spinner" style="
      width: 40px;
      height: 40px;
      border: 4px solid #f3f3f3;
      border-top: 4px solid #007bff;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 15px;
    "></div>
    <p>Cargando detalles del lugar...</p>
  `;

  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 999;
  `;

  document.body.appendChild(overlay);
  document.body.appendChild(modal);

  return modal;
}

function crearModalDetalles(lugar) {
  const modal = document.createElement('div');
  modal.className = 'details-modal';
  modal.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    z-index: 1000;
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
  `;

  modal.innerHTML = `
    <div class="modal-header">
      <h3 style="margin: 0; color: #000000ff;">${lugar.placename || 'Sin nombre'}</h3>
      <button onclick="abrirFormularioActualizar(${lugar.id})" class="close-btn" style="
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #000000ff;
      ">&times;</button>
    </div>
    <div class="modal-content" style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #000000ff;">
      <p><strong>📍 Dirección:</strong> ${lugar.addresplace || 'No especificada'}</p>
      <p><strong>📝 Descripción:</strong> ${lugar.description || 'Sin descripción'}</p>
      <p><strong>⭐ Puntaje:</strong> ${lugar.score || "N/A"}</p>
      <p><strong>🌐 Coordenadas:</strong> ${lugar.latitud || 'N/A'}, ${lugar.longitud || 'N/A'}</p>
      
      ${lugar.coffee_type ? `
        <div class="coffee-details" style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #000000ff;">
          <h4 style="margin: 0 0 10px 0; color: #000000ff;">☕ Información del Café</h4>
          <p><strong>Tipo:</strong> ${lugar.coffee_type}</p>
          ${lugar.coffee_description ? `<p><strong>Descripción:</strong> ${lugar.coffee_description}</p>` : ''}
          ${lugar.video ? `<p><a href="${lugar.video}" target="_blank" style="color: #7ebcffff; text-decoration: none;">🎬 Ver video del café</a></p>` : ''}
          ${lugar.coffe_image ? `<img src="http://127.0.0.1:8000/static/${lugar.coffe_image}" alt="${lugar.coffee_type}" style="max-width: 100%; border-radius: 4px; margin-top: 10px;" onerror="this.style.display='none'">` : ''}
        </div>
      ` : `
        <div class="coffee-details" style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee;">
          <p><em>Sin tipo de café asociado</em></p>
        </div>
      `}
      
      <div class="modal-actions" style="margin-top: 20px; display: flex; gap: 10px; flex-wrap: wrap;">
        <button class="btn-primary" onclick="abrirFormularioActualizar(${lugar.id})" style="
          padding: 10px 15px;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          flex: 1;
          min-width: 120px;
        ">
          ✏️ Editar Lugar
        </button>
        <button class="btn-danger" onclick="eliminarMapa(${lugar.id})" style="
          padding: 10px 15px;
          background: #dc3545;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          flex: 1;
          min-width: 120px;
        ">
          🗑️ Eliminar Lugar
        </button>
      </div>
    </div>
  `;

  // Overlay
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 999;
  `;
  overlay.onclick = cerrarModal;

  document.body.appendChild(overlay);
  document.body.appendChild(modal);
}

// Función para cerrar modal
function cerrarModal() {
  const modals = document.querySelectorAll('.details-modal, .loading-modal, .update-modal');
  const overlays = document.querySelectorAll('.modal-overlay');
  
  modals.forEach(modal => modal.remove());
  overlays.forEach(overlay => overlay.remove());
}



function crearFormularioActualizar(mapaId, lugar) {
  const modal = document.createElement('div');
  modal.className = 'update-modal';
  modal.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    z-index: 1000;
    max-width: 400px;
    width: 90%;
  `;

  modal.innerHTML = `
    <div class="modal-header">
      <h3>Editar Lugar #${mapaId}</h3>
      <button onclick="cerrarModal()" class="close-btn">&times;</button>
    </div>
    <form id="update-form-${mapaId}" onsubmit="event.preventDefault(); actualizarMapa(${mapaId});">
      <div class="form-group">
        <label>Nombre del lugar:</label>
        <input type="text" name="placename" value="${lugar.placename || ''}" placeholder="Nombre del lugar" required>
      </div>
      <div class="form-group">
        <label>Descripción:</label>
        <textarea name="description" placeholder="Descripción" required>${lugar.description || ''}</textarea>
      </div>
      <div class="form-group">
        <label>Dirección:</label>
        <input type="text" name="addresplace" value="${lugar.addresplace || ''}" placeholder="Dirección" required>
      </div>
      <div class="form-group">
        <label>Puntaje (1-5):</label>
        <input type="number" name="score" min="1" max="5" value="${lugar.score || 1}" required>
      </div>
      <div class="form-actions">
        <button type="submit" class="btn-primary">💾 Guardar Cambios</button>
        <button type="button" onclick="cerrarModal()" class="btn-secondary">Cancelar</button>
      </div>
    </form>
  `;

  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 999;
  `;
  overlay.onclick = cerrarModal;

  document.body.appendChild(overlay);
  document.body.appendChild(modal);
}

// Función para actualizar mapa
async function actualizarMapa(mapaId) {
  const form = document.getElementById(`update-form-${mapaId}`);
  const formData = new FormData(form);
  
  const data = {
    placename: formData.get('placename'),
    description: formData.get('description'),
    addresplace: formData.get('addresplace'),
    score: parseInt(formData.get('score'))
  };

  try {
    const res = await fetch(`http://127.0.0.1:8000/mapas/${mapaId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || `Error HTTP ${res.status}`);
    }

    const result = await res.json();
    console.log('Mapa actualizado:', result);
    
    alert('✅ Lugar actualizado correctamente');
    cerrarModal();
    location.reload();

  } catch (err) {
    console.error('Error actualizando mapa:', err);
    alert(` Error al actualizar: ${err.message}`);
  }
}

// Función para cerrar modal
function cerrarModal() {
  const modals = document.querySelectorAll('.details-modal, .update-modal');
  const overlays = document.querySelectorAll('.modal-overlay');
  
  modals.forEach(modal => modal.remove());
  overlays.forEach(overlay => overlay.remove());
}



// Manejar tecla Escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    cerrarModal();
  }
});


// Función para eliminar un mapa (con debug mejorado)
async function eliminarMapa(mapa_id) {
  console.log(' eliminarMapa llamado con ID:', mapa_id);
  
  if (!confirm('¿Estás seguro de que quieres eliminar este lugar del mapa?\nEsta acción no se puede deshacer.')) {
    console.log(' Usuario canceló la eliminación');
    return;
  }

  try {
    console.log(` Intentando eliminar mapa ID: ${mapa_id}`);
    console.log(` URL: http://127.0.0.1:8000/mapas/${mapa_id}`);
    
    const res = await fetch(`http://127.0.0.1:8000/mapas/${mapa_id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log('📡 Response status:', res.status);
    console.log('📡 Response ok:', res.ok);

    if (!res.ok) {
      let errorMsg = `Error HTTP ${res.status}`;
      try {
        const errorData = await res.json();
        console.log('📡 Error data:', errorData);
        errorMsg = errorData.detail || errorMsg;
      } catch (parseError) {
        console.log('📡 Error parseando respuesta:', parseError);
        // Ignorar errores de parseo
      }
      throw new Error(errorMsg);
    }

    const result = await res.json();
    console.log('✅ Mapa eliminado - Respuesta:', result);
    
    // Cerrar el modal actual
    cerrarModal();
    
    // Mostrar mensaje de éxito
    alert('✅ Lugar eliminado correctamente');
    
    // Recargar la página después de 1 segundo para ver los cambios
    setTimeout(() => {
      location.reload();
    }, 1000);

  } catch (err) {
    console.error(' Error eliminando mapa:', err);
    console.error(' Stack trace:', err.stack);
    alert(` Error al eliminar: ${err.message}`);
  }
}


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
          ${video ? `<a class="btn btn-ghost" href="${video}" target="_blank" rel="noopener noreferrer" aria-label="Ver video sobre ${title}">
            <svg aria-hidden="true" viewBox="0 0 24 24" fill="currentColor">
              <path d="M8 5v14l11-7z"/>
              <circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="2"/>
            </svg>
            Ver Video
          </a>` : ''}
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

async function AgregarProyecto(event) {
  // Prevenir el comportamiento por defecto del formulario
  if (event) event.preventDefault();

  const form = document.querySelector('form[action="#"]');
  if (!form) {
    console.error('No se encontró el formulario de proyectos');
    return;
  }

  // Crear o encontrar el elemento de estado
  let statusEl = form.querySelector('.project-status');
  if (!statusEl) {
    statusEl = document.createElement('div');
    statusEl.className = 'project-status';
    statusEl.setAttribute('role', 'status');
    statusEl.setAttribute('aria-live', 'polite');
    statusEl.style.marginTop = '0.75rem';
    form.appendChild(statusEl);
  }

  const submitButton = form.querySelector('button[type="submit"]');

  function setStatus(message, type = 'info') {
    statusEl.textContent = message;
    statusEl.dataset.status = type;
    clearTimeout(statusEl._timeout);
    statusEl._timeout = setTimeout(() => {
      statusEl.textContent = '';
      delete statusEl.dataset.status;
    }, 6000);
  }

  function setButtonDisabled(disabled = true) {
    if (submitButton) {
      submitButton.disabled = disabled;
      submitButton.setAttribute('aria-disabled', String(disabled));
      submitButton.textContent = disabled ? 'Enviando...' : 'Enviar';
    }
  }

  // Deshabilitar el botón inmediatamente
  setButtonDisabled(true);
  setStatus('Enviando proyecto...', 'info');

  try {
    // Obtener los datos del formulario
    const formData = new FormData(form);
    const data = {
      nombre: formData.get('id_p') || '', // Asumiendo que id_p es el nombre
      description: formData.get('dep_p') || '',
      imagen: formData.get('imag_p') || '',
      fecha: formData.get('date_p') || '',
      linkgithub: formData.get('giturl') || '',
      linkvideo: formData.get('yturl') || ''
    };

    console.log('Datos a enviar:', data);

    // Validar campos requeridos
    if (!data.nombre || !data.description || !data.fecha) {
      throw new Error('Por favor completa todos los campos requeridos');
    }

    const res = await fetch('http://127.0.0.1:8000/proyectos/', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      let errText = `HTTP ${res.status}`;
      try {
        const errJson = await res.json();
        if (errJson) {
          if (errJson.detail) {
            if (Array.isArray(errJson.detail)) {
              errText = errJson.detail.map(d => {
                if (typeof d === 'string') return d;
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
        // ignora errores parseo
      }
      throw new Error(errText);
    }

    const payload = await res.json();
    console.log('Proyecto agregado:', payload);
    
    setStatus('¡Proyecto agregado correctamente! ID: ' + payload.id, 'success');
    
    // Limpiar el formulario
    form.reset();
    
    //Recargar proyectos
    setTimeout(() => {
      if (typeof cargarProyectos === 'function') {
        cargarProyectos();
      }
    }, 2000);

  } catch (err) {
    const msg = err && err.message ? err.message : String(err);
    console.error('Error agregando proyecto:', msg);
    setStatus(`Error al enviar: ${msg}`, 'error');
  } finally {
    setButtonDisabled(false);
  }
}

// escucha el event liste en el form
document.addEventListener('DOMContentLoaded', function() {
  const form = document.querySelector('form[action="#"]');
  if (form) {
    form.addEventListener('submit', AgregarProyecto);
    
    // remueve el html on click
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
      submitButton.removeAttribute('onclick');
    }
  }
});




// Función para crear modal de carga
function crearModalCarga() {
  const modal = document.createElement('div');
  modal.className = 'loading-modal';
  modal.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    z-index: 1000;
    text-align: center;
  `;

  modal.innerHTML = `
    <div class="loading-spinner" style="
      width: 40px;
      height: 40px;
      border: 4px solid #f3f3f3;
      border-top: 4px solid #007bff;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin: 0 auto 15px;
    "></div>
    <p>Cargando detalles del lugar...</p>
  `;

  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 999;
  `;

  document.body.appendChild(overlay);
  document.body.appendChild(modal);

  return modal;
}

function crearModalDetalles(lugar) {
  const modal = document.createElement('div');
  modal.className = 'details-modal';
  modal.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    z-index: 1000;
    max-width: 500px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
  `;

  modal.innerHTML = `
    <div class="modal-header">
      <h3 style="margin: 0; color: #000000ff;">${lugar.placename || 'Sin nombre'}</h3>
      <button onclick="abrirFormularioActualizar(${lugar.id})" class="close-btn" style="
        background: none;
        border: none;
        font-size: 24px;
        cursor: pointer;
        color: #000000ff;
      ">&times;</button>
    </div>
    <div class="modal-content" style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #000000ff;">
      <p><strong>📍 Dirección:</strong> ${lugar.addresplace || 'No especificada'}</p>
      <p><strong>📝 Descripción:</strong> ${lugar.description || 'Sin descripción'}</p>
      <p><strong>⭐ Puntaje:</strong> ${lugar.score || "N/A"}</p>
      <p><strong>🌐 Coordenadas:</strong> ${lugar.latitud || 'N/A'}, ${lugar.longitud || 'N/A'}</p>
      
      ${lugar.coffee_type ? `
        <div class="coffee-details" style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #000000ff;">
          <h4 style="margin: 0 0 10px 0; color: #000000ff;">☕ Información del Café</h4>
          <p><strong>Tipo:</strong> ${lugar.coffee_type}</p>
          ${lugar.coffee_description ? `<p><strong>Descripción:</strong> ${lugar.coffee_description}</p>` : ''}
          ${lugar.video ? `<p><a href="${lugar.video}" target="_blank" style="color: #7ebcffff; text-decoration: none;">🎬 Ver video del café</a></p>` : ''}
          ${lugar.coffe_image ? `<img src="http://127.0.0.1:8000/static/${lugar.coffe_image}" alt="${lugar.coffee_type}" style="max-width: 100%; border-radius: 4px; margin-top: 10px;" onerror="this.style.display='none'">` : ''}
        </div>
      ` : `
        <div class="coffee-details" style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee;">
          <p><em>Sin tipo de café asociado</em></p>
        </div>
      `}
      
      <div class="modal-actions" style="margin-top: 20px; display: flex; gap: 10px; flex-wrap: wrap;">
        <button class="btn-primary" onclick="abrirFormularioActualizar(${lugar.id})" style="
          padding: 10px 15px;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          flex: 1;
          min-width: 120px;
        ">
          ✏️ Editar Lugar
        </button>
        <button class="btn-danger" onclick="eliminarMapa(${lugar.id})" style="
          padding: 10px 15px;
          background: #dc3545;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          flex: 1;
          min-width: 120px;
        ">
          🗑️ Eliminar Lugar
        </button>
      </div>
    </div>
  `;

  // Overlay
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 999;
  `;
  overlay.onclick = cerrarModal;

  document.body.appendChild(overlay);
  document.body.appendChild(modal);
}

// Función para cerrar modal
function cerrarModal() {
  const modals = document.querySelectorAll('.details-modal, .loading-modal, .update-modal');
  const overlays = document.querySelectorAll('.modal-overlay');
  
  modals.forEach(modal => modal.remove());
  overlays.forEach(overlay => overlay.remove());
}

// Agregar estilos de animación para el spinner
const spinnerStyles = `
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-modal {
  font-family: Arial, sans-serif;
}

.details-modal {
  font-family: Arial, sans-serif;
}

.close-btn:hover {
  color: #0e0404ff;
}

.btn-primary:hover {
  background: #0056b3 !important;
}

.btn-danger:hover {
  background: #c82333 !important;
}
`;

// Insertar estilos si no existen
if (!document.querySelector('#modal-styles')) {
  const styleSheet = document.createElement('style');
  styleSheet.id = 'modal-styles';
  styleSheet.textContent = spinnerStyles;
  document.head.appendChild(styleSheet);
}

function crearFormularioActualizar(mapaId, lugar) {
  const modal = document.createElement('div');
  modal.className = 'update-modal';
  modal.style.cssText = `
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    z-index: 1000;
    max-width: 400px;
    width: 90%;
  `;

  modal.innerHTML = `
    <div class="modal-header">
      <h3>Editar Lugar #${mapaId}</h3>
      <button onclick="cerrarModal()" class="close-btn">&times;</button>
    </div>
    <form id="update-form-${mapaId}" onsubmit="event.preventDefault(); actualizarMapa(${mapaId});">
      <div class="form-group">
        <label>Nombre del lugar:</label>
        <input type="text" name="placename" value="${lugar.placename || ''}" placeholder="Nombre del lugar" required>
      </div>
      <div class="form-group">
        <label>Descripción:</label>
        <textarea name="description" placeholder="Descripción" required>${lugar.description || ''}</textarea>
      </div>
      <div class="form-group">
        <label>Dirección:</label>
        <input type="text" name="addresplace" value="${lugar.addresplace || ''}" placeholder="Dirección" required>
      </div>
      <div class="form-group">
        <label>Puntaje (1-5):</label>
        <input type="number" name="score" min="1" max="5" value="${lugar.score || 1}" required>
      </div>
      <div class="form-actions">
        <button type="submit" class="btn-primary">💾 Guardar Cambios</button>
        <button type="button" onclick="cerrarModal()" class="btn-secondary">Cancelar</button>
      </div>
    </form>
  `;

  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay';
  overlay.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 999;
  `;
  overlay.onclick = cerrarModal;

  document.body.appendChild(overlay);
  document.body.appendChild(modal);
}

// Función para actualizar mapa
async function actualizarMapa(mapaId) {
  const form = document.getElementById(`update-form-${mapaId}`);
  const formData = new FormData(form);
  
  const data = {
    placename: formData.get('placename'),
    description: formData.get('description'),
    addresplace: formData.get('addresplace'),
    score: parseInt(formData.get('score'))
  };

  try {
    const res = await fetch(`http://127.0.0.1:8000/mapas/${mapaId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || `Error HTTP ${res.status}`);
    }

    const result = await res.json();
    console.log('Mapa actualizado:', result);
    
    alert('✅ Lugar actualizado correctamente');
    cerrarModal();
    location.reload();

  } catch (err) {
    console.error('Error actualizando mapa:', err);
    alert(` Error al actualizar: ${err.message}`);
  }
}

// Función para cerrar modal
function cerrarModal() {
  const modals = document.querySelectorAll('.details-modal, .update-modal');
  const overlays = document.querySelectorAll('.modal-overlay');
  
  modals.forEach(modal => modal.remove());
  overlays.forEach(overlay => overlay.remove());
}

// Agregar estilos CSS optimizados
const optimizedStyles = `
/* Popup compacto */
.map-popup-compact {
  font-family: Arial, sans-serif;
  font-size: 12px;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.popup-header h5 {
  margin: 0;
  font-size: 14px;
  color: #2c5530;
  flex: 1;
}

.score-badge {
  background: #ffd700;
  color: #000;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: bold;
}

.popup-content {
  margin-bottom: 10px;
}

.popup-content .address {
  font-size: 11px;
  color: #666;
  margin: 2px 0;
}

.popup-content .description {
  font-size: 11px;
  color: #333;
  margin: 4px 0;
  line-height: 1.3;
}

.coffee-info {
  margin-top: 4px;
}

.coffee-type {
  font-size: 11px;
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  display: inline-block;
}

.popup-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 5px;
}

.btn-more-info {
  background: #007bff;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  cursor: pointer;
  flex: 1;
}

.action-buttons {
  display: flex;
  gap: 4px;
}

.btn-delete, .btn-edit {
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.btn-delete {
  background: #dc3545;
  color: white;
}

.btn-edit {
  background: #ffc107;
  color: #000;
}

/* Modales */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.modal-header h3 {
  margin: 0;
  color: #2c5530;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  font-size: 14px;
}

.form-group input, .form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group textarea {
  height: 80px;
  resize: vertical;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.btn-primary, .btn-secondary, .btn-danger {
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  flex: 1;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.video-link {
  color: #007bff;
  text-decoration: none;
}

.video-link:hover {
  text-decoration: underline;
}
`;

// Insertar estilos
if (!document.querySelector('#optimized-map-styles')) {
  const styleSheet = document.createElement('style');
  styleSheet.id = 'optimized-map-styles';
  styleSheet.textContent = optimizedStyles;
  document.head.appendChild(styleSheet);
}

// Manejar tecla Escape
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    cerrarModal();
  }
});


// Función para eliminar un mapa (con debug mejorado)
async function eliminarMapa(mapa_id) {
  console.log(' eliminarMapa llamado con ID:', mapa_id);
  
  if (!confirm('¿Estás seguro de que quieres eliminar este lugar del mapa?\nEsta acción no se puede deshacer.')) {
    console.log(' Usuario canceló la eliminación');
    return;
  }

  try {
    console.log(` Intentando eliminar mapa ID: ${mapa_id}`);
    console.log(` URL: http://127.0.0.1:8000/mapas/${mapa_id}`);
    
    const res = await fetch(`http://127.0.0.1:8000/mapas/${mapa_id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log('📡 Response status:', res.status);
    console.log('📡 Response ok:', res.ok);

    if (!res.ok) {
      let errorMsg = `Error HTTP ${res.status}`;
      try {
        const errorData = await res.json();
        console.log('📡 Error data:', errorData);
        errorMsg = errorData.detail || errorMsg;
      } catch (parseError) {
        console.log('📡 Error parseando respuesta:', parseError);
        // Ignorar errores de parseo
      }
      throw new Error(errorMsg);
    }

    const result = await res.json();
    console.log('✅ Mapa eliminado - Respuesta:', result);
    
    // Cerrar el modal actual
    cerrarModal();
    
    // Mostrar mensaje de éxito
    alert('✅ Lugar eliminado correctamente');
    
    // Recargar la página después de 1 segundo para ver los cambios
    setTimeout(() => {
      location.reload();
    }, 1000);

  } catch (err) {
    console.error(' Error eliminando mapa:', err);
    console.error(' Stack trace:', err.stack);
    alert(` Error al eliminar: ${err.message}`);
  }
}

/* --- Chat integration removed per request --- */