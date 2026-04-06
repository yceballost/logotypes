const SNACKBAR_TIMEOUT = 3000;
const ICON_RESET_DELAY = 1500;

let snackbarTimeout;

function showSnackbar(message = "Copied to clipboard!") {
  const snackbar = document.getElementById("snackbar");
  snackbar.textContent = message;

  if (snackbar.classList.contains("show")) {
    clearTimeout(snackbarTimeout);
  } else {
    snackbar.classList.remove("hide");
    snackbar.classList.add("show");
  }

  snackbarTimeout = setTimeout(() => {
    snackbar.classList.remove("show");
    snackbar.classList.add("hide");
  }, SNACKBAR_TIMEOUT);
}

function filterLogos() {
  const searchInput = document.getElementById("search-input");
  if (!searchInput) return;

  const query = searchInput.value.toLowerCase();
  const activeTypeChips = document.querySelectorAll(".chip.active[data-type]");
  const activeColorChips = document.querySelectorAll(
    ".chip.active[data-color]",
  );
  const cells = document.querySelectorAll("#logo-grid .logo-cell");

  cells.forEach((cell) => {
    const name = cell.getAttribute("data-name").toLowerCase();
    const type = cell.getAttribute("data-type");
    const color = cell.getAttribute("data-color");
    const nameMatch = name.includes(query);
    const typeMatch = Array.from(activeTypeChips).some(
      (chip) => chip.dataset.type === type,
    );
    const colorMatch = Array.from(activeColorChips).some(
      (chip) => chip.dataset.color.toLowerCase() === color.toLowerCase(),
    );
    cell.style.display = nameMatch && typeMatch && colorMatch ? "" : "none";
  });
}

function loadLogos() {
  fetch("/all", { headers: { Accept: "application/json" } })
    .then((response) => response.json())
    .then((data) => {
      if (!data.records) {
        console.error("No 'records' key found in the response data");
        return;
      }

      const grid = document.getElementById("logo-grid");
      grid.innerHTML = "";

      const baseUrl = `${window.location.protocol}//${window.location.host}`;

      for (const [name, variants] of Object.entries(data.records)) {
        variants.forEach((logo) => {
          const cell = document.createElement("div");
          cell.className = "logo-cell";
          cell.setAttribute(
            "data-type",
            logo.variant === "wordmark" ? "Wordmark" : "Glyph",
          );
          cell.setAttribute("data-color", logo.version);
          cell.setAttribute("data-name", logo.name);

          const apiUrl = `${baseUrl}/${logo.name}?variant=${logo.variant}&version=${logo.version}`;
          cell.setAttribute("data-api-url", apiUrl);

          cell.innerHTML = `
            <div class="grid-container stack stack-24">
              <div class="grid-logos-container">
                <img class="grid-logos" src="${logo.logo}" alt="${logo.name}">
              </div>
              <div class="stack stack-24" style="align-items: center;">
                <p class="logo-name">${logo.name}</p>
                <div class="inline inline-8">
                  <p class="tag logo-variant">${logo.variant}</p>
                  <p class="tag logo-version">${logo.version}</p>
                </div>
              </div>
            </div>
          `;

          cell.addEventListener("click", () => {
            navigator.clipboard
              .writeText(apiUrl)
              .then(() =>
                showSnackbar(`${logo.name} logo copied to clipboard!`),
              )
              .catch((err) => console.error("Error copying URL:", err));
          });

          grid.appendChild(cell);
        });
      }

      filterLogos();
    })
    .catch((error) => console.error("Error fetching logos:", error));
}

function loadFavicon() {
  fetch("/favicon-list")
    .then((response) => {
      if (!response.ok) throw new Error("Error fetching favicon list");
      return response.json();
    })
    .then((favicons) => {
      if (Array.isArray(favicons) && favicons.length > 0) {
        const randomFavicon = `/static/logos/${
          favicons[Math.floor(Math.random() * favicons.length)]
        }`;
        document.getElementById("dynamic-favicon").href = randomFavicon;
      }
    })
    .catch((error) => console.error("Error setting dynamic favicon:", error));
}

// --- Logo Particle Fountain ---
const PARTICLE_MIN_HEIGHT = 20;
const PARTICLE_MAX_HEIGHT = 20;

function initParticleSystem() {
  const canvas = document.createElement("canvas");
  canvas.id = "particle-canvas";
  canvas.style.cssText =
    "position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:9999";
  document.body.appendChild(canvas);
  const ctx = canvas.getContext("2d");

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener("resize", resize);

  const particles = [];
  let isActive = false;
  let mouseX = 0;
  let mouseY = 0;
  let logoImages = [];
  let spawnTimer = 0;
  const SPAWN_INTERVAL = 40; // ms between particle spawns

  // Collect logo image sources from the grid
  function collectLogoSources() {
    const imgs = document.querySelectorAll("#logo-grid .grid-logos");
    const sources = [];
    const seen = new Set();
    imgs.forEach((img) => {
      if (img.complete && img.naturalWidth > 0 && !seen.has(img.src)) {
        seen.add(img.src);
        sources.push(img);
      }
    });
    return sources;
  }

  function spawnParticle(x, y) {
    if (logoImages.length === 0) return;
    const img = logoImages[Math.floor(Math.random() * logoImages.length)];
    const height =
      PARTICLE_MIN_HEIGHT +
      Math.random() * (PARTICLE_MAX_HEIGHT - PARTICLE_MIN_HEIGHT);
    const aspect = img.naturalWidth / img.naturalHeight;
    const width = height * aspect;
    const angle = -Math.PI / 2 + (Math.random() - 0.5) * 1.4; // upward spread
    const speed = 2 + Math.random() * 4;
    particles.push({
      img,
      x,
      y,
      vx: Math.cos(angle) * speed + (Math.random() - 0.5) * 1.5,
      vy: Math.sin(angle) * speed,
      width,
      height,
      opacity: 1,
      rotation: Math.random() * Math.PI * 2,
      rotationSpeed: (Math.random() - 0.5) * 0.15,
      life: 1,
      decay: 0.008 + Math.random() * 0.008,
      gravity: 0.12,
    });
  }

  function update(dt) {
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.vy += p.gravity;
      p.x += p.vx;
      p.y += p.vy;
      p.rotation += p.rotationSpeed;
      p.life -= p.decay;
      p.opacity = Math.max(0, p.life);
      if (p.life <= 0) {
        particles.splice(i, 1);
      }
    }
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const p of particles) {
      ctx.save();
      ctx.globalAlpha = p.opacity;
      ctx.translate(p.x, p.y);
      ctx.rotate(p.rotation);
      ctx.drawImage(p.img, -p.width / 2, -p.height / 2, p.width, p.height);
      ctx.restore();
    }
  }

  let lastTime = 0;
  let lastSpawn = 0;
  function loop(time) {
    const dt = time - lastTime;
    lastTime = time;

    if (isActive && time - lastSpawn > SPAWN_INTERVAL) {
      spawnParticle(mouseX, mouseY);
      lastSpawn = time;
    }

    update(dt);
    draw();

    if (particles.length > 0 || isActive) {
      requestAnimationFrame(loop);
    }
  }

  function startLoop() {
    lastTime = performance.now();
    lastSpawn = 0;
    requestAnimationFrame(loop);
  }

  // Left-click hold
  document.addEventListener("mousedown", (e) => {
    if (e.button === 0) {
      isActive = true;
      document.body.style.userSelect = "none";
      mouseX = e.clientX;
      mouseY = e.clientY;
      logoImages = collectLogoSources();
      // Burst inicial para que se sienta inmediato
      for (let i = 0; i < 5; i++) {
        spawnParticle(mouseX, mouseY);
      }
      startLoop();
    }
  });

  document.addEventListener("mousemove", (e) => {
    if (isActive) {
      mouseX = e.clientX;
      mouseY = e.clientY;
    }
  });

  document.addEventListener("mouseup", (e) => {
    if (e.button === 0) {
      isActive = false;
      document.body.style.userSelect = "";
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  loadFavicon();
  initParticleSystem();

  // Copy URL buttons (API examples)
  document.querySelectorAll(".icon-button").forEach((button) => {
    button.addEventListener("click", function () {
      const url = this.parentElement.querySelector("a").textContent.trim();
      navigator.clipboard
        .writeText(url)
        .then(() => {
          this.innerHTML =
            '<img src="/static/web/assets/check.svg" class="icon" />';
          this.classList.add("copied");
          setTimeout(() => {
            this.innerHTML =
              '<img src="/static/web/assets/copy.svg" class="icon" />';
            this.classList.remove("copied");
          }, ICON_RESET_DELAY);
        })
        .catch((err) => console.error("Could not copy text:", err));
    });
  });

  // Search input
  document
    .getElementById("search-input")
    .addEventListener("input", filterLogos);

  // Filter chips
  document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      chip.classList.toggle("active");
      filterLogos();
    });
  });

  loadLogos();
});
