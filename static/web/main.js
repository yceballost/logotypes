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
  const activeTypeChips = document.querySelectorAll(
    ".chip.active[data-type]"
  );
  const activeColorChips = document.querySelectorAll(
    ".chip.active[data-color]"
  );
  const cells = document.querySelectorAll("#logo-grid .logo-cell");

  cells.forEach((cell) => {
    const name = cell.getAttribute("data-name").toLowerCase();
    const type = cell.getAttribute("data-type");
    const color = cell.getAttribute("data-color");
    const nameMatch = name.includes(query);
    const typeMatch = Array.from(activeTypeChips).some(
      (chip) => chip.dataset.type === type
    );
    const colorMatch = Array.from(activeColorChips).some(
      (chip) => chip.dataset.color.toLowerCase() === color.toLowerCase()
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
            logo.variant === "wordmark" ? "Wordmark" : "Glyph"
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
                showSnackbar(`${logo.name} logo copied to clipboard!`)
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
    .catch((error) =>
      console.error("Error setting dynamic favicon:", error)
    );
}

document.addEventListener("DOMContentLoaded", () => {
  loadFavicon();

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
