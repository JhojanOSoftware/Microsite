/* Esta vaina carga y muestra los planetas en el index.html */
async function cargarPlanetas() {
  try {
    const response = await fetch('https://dragonball-api.com/api/planets');
    const data = await response.json();
    const planetas = data.items || data; /* reescribe la variable "planets" como "planetas" y carga toda la data de*/
    const lista = document.getElementById('planetasLista');
    if (!lista) return; // Solo ejecuta en index.html

    lista.innerHTML = '';

    planetas.forEach(planeta => { /* absorbe todos los datos de la variable y , por cada planeta, crea una tarjeta con su nombre e imagen */
      const card = document.createElement('div');
      card.className = 'planeta-card';
      card.innerHTML = `
        <a href="planetas.html?id=${planeta.id}">
          <img src="${planeta.image}" alt="${planeta.name}">
          <span>${planeta.name}</span>
        </a>
      `;
      lista.appendChild(card);
    });
  } catch (error) { /*de lo contrario, mostrara un mensaje de error */
    const lista = document.getElementById('planetasLista');
    if (lista) {
      lista.innerHTML = '<p>Error cargando planetas.</p>';
    }
  }
}

cargarPlanetas();

/* Esta vaina muestra la respectiva descripcion de los planetas */
function getPlanetIdFromUrl() {
  const params = new URLSearchParams(window.location.search);
  return parseInt(params.get('id')) || 1;
}

async function loadPlanet(planetId = 1) { /*cargara todos los planetas desde la api y los "invocara" segun su ID */
  try {
    const response = await fetch(`https://dragonball-api.com/api/planets/${planetId}`);
    const data = await response.json();

    const container = document.getElementById("planets");
    if (!container) return; // Solo ejecuta en planetas.html

    container.innerHTML = "";

    // Esta cosa genera la tarjeta con la informacion del planeta
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <h1>${data.name}</h1>
      <img src="${data.image}" alt="${data.name}">
      <p>${data.description || "Sin descripción disponible."}</p>
    `;
    container.appendChild(card);

    // Los controladorees de la paginacion
    const navigation = document.createElement("div");
    navigation.className = "pagination";

    if (planetId > 1) { /*flecha para desplazarse al anterior planeta */
      const prevBtn = document.createElement("button");
      prevBtn.textContent = "⬅️ Anterior";
      prevBtn.onclick = () => {
        window.location.search = `?id=${planetId - 1}`;
      };
      navigation.appendChild(prevBtn);
    }

    const maxPlanets = 20; // Esta vaina ajusta la cantidad maxima de planetas

    if (planetId < maxPlanets) { /*flecha para desplazarse al siguiente planeta */
      const nextBtn = document.createElement("button");
      nextBtn.textContent = "Siguiente ➡️";
      nextBtn.onclick = () => {
        window.location.search = `?id=${planetId + 1}`;
      };
      navigation.appendChild(nextBtn);
    }

    container.appendChild(navigation);

  } catch (error) { /* si no encuentra el planeta, mostrara un mensaje diciendo "Error cargando planeta." */
    const container = document.getElementById("planets");
    if (container) {
      container.innerHTML = "<p>Error cargando planeta.</p>";
    }
  }
}

// Y esto ejecuta la carga de la info del planeta, solo si existe el contenedor
if (document.getElementById("planets")) {
  const planetId = getPlanetIdFromUrl();
  loadPlanet(planetId);
}