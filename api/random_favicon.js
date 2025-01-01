import fs from "fs";
import path from "path";

export default async function handler(req, res) {
  try {
    const logoDir = path.resolve("static/logos");
    const files = fs.readdirSync(logoDir);

    // Filtrar logos que contienen "glyph" y "color"
    const logos = files.filter(
      (file) =>
        file.includes("glyph") &&
        file.includes("color") &&
        file.endsWith(".svg")
    );

    if (logos.length === 0) {
      res.status(404).send("No valid logos found");
      return;
    }

    const selectedLogo = logos[Math.floor(Math.random() * logos.length)];
    const filePath = path.join(logoDir, selectedLogo);

    // Configurar encabezados para servir el archivo
    res.setHeader("Content-Type", "image/svg+xml");
    res.setHeader("Cache-Control", "static, max-age=3600"); // Cache por 1 hora
    res.status(200).send(fs.readFileSync(filePath));
  } catch (error) {
    console.error("Error serving favicon:", error);
    res.status(500).send("Internal server error");
  }
}
