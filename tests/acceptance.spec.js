const { test, expect } = require("@playwright/test");

test.describe("Pruebas para la página de inicio", () => {
  test("La página de inicio carga correctamente", async ({ page }) => {
    const response = await page.goto("http://127.0.0.1:5000/");

    // Validar estado HTTP
    expect(response.status()).toBe(200);

    // Validar elementos clave
    const header = page.locator("header");
    await expect(header).toBeVisible();

    const mainContent = page.locator("main");
    await expect(mainContent).toBeVisible();
  });
});

test.describe("Pruebas para rutas específicas", () => {
  const names = ["spotify", "apple", "microsoft"];

  for (const name of names) {
    test(`La página /${name} responde con un SVG válido`, async ({ page }) => {
      const response = await page.goto(`http://127.0.0.1:5000/${name}`, {
        timeout: 60000,
      });

      // Validar estado HTTP
      expect(response.status()).toBe(200);

      // Verificar tipo de contenido
      expect(response.headers()["content-type"]).toContain("image/svg+xml");

      // Validar contenido del SVG
      const body = await response.text();
      expect(body).toContain("<svg");
      expect(body).toContain("</svg>");
    });
  }
});

test.describe("Pruebas para rutas aleatorias", () => {
  test("La página /random responde con un SVG válido", async ({ page }) => {
    const response = await page.goto("http://127.0.0.1:5000/random", {
      timeout: 60000,
    });

    // Validar estado HTTP
    expect(response.status()).toBe(200);

    // Verificar tipo de contenido
    expect(response.headers()["content-type"]).toContain("image/svg+xml");

    // Validar contenido del SVG
    const body = await response.text();
    expect(body).toContain("<svg");
    expect(body).toContain("</svg>");
  });

  test("La página /random/data responde con JSON válido", async ({ page }) => {
    const response = await page.goto("http://127.0.0.1:5000/random/data");

    // Validar estado HTTP
    expect(response.status()).toBe(200);

    // Verificar tipo de contenido
    expect(response.headers()["content-type"]).toContain("application/json");

    // Validar contenido del JSON
    const body = await response.json();
    expect(body).toBeDefined();
    expect(typeof body).toBe("object");
  });
});

// Screenshots
test.describe("Capturas de pantalla para la página de inicio", () => {
  test("Captura de pantalla completa de la página de inicio", async ({
    page,
  }) => {
    await page.goto("http://127.0.0.1:5000/");
    await page.screenshot({ path: "screenshots/index.png", fullPage: true });
  });
});

test.describe("Capturas de pantalla para rutas específicas", () => {
  const names = ["spotify", "apple", "microsoft"];

  for (const name of names) {
    test(`Captura de pantalla de /${name}`, async ({ page }) => {
      await page.goto(`http://127.0.0.1:5000/${name}`);

      // Localiza el SVG y captura su pantalla
      const svg = page.locator("svg");
      await svg.screenshot({ path: `screenshots/${name}.png` });
    });
  }
});
