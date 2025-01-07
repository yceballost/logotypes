const { test, expect } = require("@playwright/test");
const fs = require("fs");
const path = require("path");

// Generar lista dinámica de nombres de logos
const logosPath = path.join(__dirname, "../static/logos");
const names = fs
  .readdirSync(logosPath)
  .filter((file) => path.extname(file) === ".svg") // Solo archivos SVG
  .map((file) => path.basename(file, ".svg")); // Remover la extensiónç

test.describe.configure({ retries: 2 });
const TIMEOUT = 1000;

// Screenshots tests
test.describe("home-screenshot", () => {
  test("Captura de pantalla completa de la página de inicio", async ({
    page,
  }) => {
    await page.goto("http://127.0.0.1:5000/");
    // await page.waitForTimeout(5000); // because logo grid load is slow (By the moment, I prefer avoid this)
    await page.screenshot({ path: "screenshots/index.png", fullPage: true });
  });
});

test.describe("logos-screenshot", () => {
  for (const name of names) {
    test(`Captura de pantalla de /${name}`, async ({ page }) => {
      await page.goto(`http://127.0.0.1:5000/${name}`, {
        timeout: TIMEOUT,
      });

      const svg = page.locator("svg");
      await svg.screenshot({
        path: `screenshots/${name}.png`,
        omitBackground: true,
      });
    });
  }
});

// Unit tests
test.describe("home-unit", () => {
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

test.describe("logos-unit", () => {
  for (const name of names) {
    test(`La página /${name} responde con un SVG válido`, async ({ page }) => {
      const response = await page.goto(`http://127.0.0.1:5000/${name}`, {
        timeout: TIMEOUT, // Timeout extendido para cada prueba
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

test.describe("random-unit", () => {
  test("La página /random responde con un SVG válido", async ({ page }) => {
    const response = await page.goto("http://127.0.0.1:5000/random", {
      timeout: TIMEOUT,
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
