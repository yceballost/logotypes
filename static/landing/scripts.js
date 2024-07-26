[...document.querySelectorAll("[data-fit-text]")].forEach((el) => {
  // We just need the length of the string as a CSS variable...
  el.style.setProperty("--length", el.innerText.length);
});
