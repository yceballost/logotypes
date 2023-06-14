# Logotypes.dev

An open-source project that offers a wide range of logos for your projects through an API.

## Usage

**All logos**

```
https://www.logotypes.dev/all (json structure)
```

**Random logo**

<img src="https://logotypes.dev/random" height="40" />

```
https://www.logotypes.dev/random
```

**Random logo with defined props**

<img src="https://logotypes.dev/random?variant=glyph" height="40" />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://logotypes.dev/random?version=black" height="40" />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://logotypes.dev/random?variant=wordmark&version=black" height="40" />

```
https://www.logotypes.dev/random?variant=glyph
https://www.logotypes.dev/random?version=black
https://www.logotypes.dev/random?variant=wordmark&version=black
```

**By logo name**

<img src="https://logotypes.dev/spotify" height="40" />

```
https://www.logotypes.dev/spotify
```

**By logo name with defined props**

<img src="https://logotypes.dev/airbnb?variant=glyph" height="40" />&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<img src="https://logotypes.dev/airbnb?variant=wordmark" height="40" />

```
https://www.logotypes.dev/airbnb?variant=wordmark
https://www.logotypes.dev/airbnb?version=black
https://www.logotypes.dev/airbnb?variant=wordmark&version=black
```

## Contribution

Help me enhance this project by adding brand logotypes. Your contributions to open-source initiative will contribute to a more comprehensive collection of logos. Join it in making this project complete by incorporating logos from various brands. Together, let's create a valuable resource for designers and developers worldwide.

I have tried to conceive this project from pure simplicity, from development to the contribution model.

### Adding new logotypes as a designer

1. The file names must follow a specific structure.

   I have created a naming structure for the files that automatically generates the API.

   `logoName-variant-version.svg`

   variant: `wordmark` / `glyph`  
   version: `color` / `black` / `white`

   For example: `nike-wordmark-black.svg`

2. Simply make a pull request including the logos in the [static/images](static/images) folder with the correct naming structure and in .svg format, and you're good to go!

### Improving the project as a developer

This project has been built by an inexperienced designer in coding and assisted by ChatGPT. (😬). Please feel free to enhance or add any features to this project by submitting a pull request (PR). I welcome your contributions and appreciate any improvements you can make.

## FAQs

### When to use wordmark or glyph in variants?

|                                 Example                                 | Type     | Description                                         |
| :---------------------------------------------------------------------: | -------- | --------------------------------------------------- |
| <img src="https://logotypes.dev/reddit?variant=wordmark" width="112" /> | Wordmark | a logo format that is made up of a symbol and text. |
|  <img src="https://logotypes.dev/reddit?variant=glyph" height="40" />   | Glyph    | consists of only one symbol or drawing.             |
