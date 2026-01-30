module.exports = {
  plugins: [
    { name: "inlineStyles", params: { onlyMatchedOnce: false } },
    "convertStyleToAttrs",
    "removeStyleElement",
    {
      name: "preset-default",
      params: {
        overrides: {
          removeDimensions: false, // keep width/height added by resize script
        },
      },
    },
  ],
};
