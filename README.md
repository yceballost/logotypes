# Logotypes.dev

An open-source project that offers a wide range of logos for your projects through an API.

## Basic usage

**All logos**

```
https://www.logotypes.dev/all
```

**Random logo**

```
https://www.logotypes.dev/random
```

**Random logo with defined props**

```
https://www.logotypes.dev/random?variant=imagotype
https://www.logotypes.dev/random?version=black
https://www.logotypes.dev/random?variant=imagotype&version=black
```

**By logo name**

```
https://www.logotypes.dev/nike
```

**Random logo with defined props**

```
https://www.logotypes.dev/nike?variant=imagotype
https://www.logotypes.dev/nike?version=black
https://www.logotypes.dev/nike?variant=imagotype&version=black
```

## Contribution

Help me enhance this project by adding brand logotypes. Your contributions to open-source initiative will contribute to a more comprehensive collection of logos. Join it in making this project complete by incorporating logos from various brands. Together, let's create a valuable resource for designers and developers worldwide.

I have tried to conceive this project from pure simplicity, from development to the contribution model.

### Add new logotypes

1. The file names must follow a specific structure.

   I have created a naming structure for the files that automatically generates the API.

   `logoName-variant-version.svg`

   variant: `imagotype` / `isotype` / `logotype`  
   version: `color` / `black` / `white`

   For example: `nike-imagotype-black.svg`

2. Simply make a pull request including the logos in the [static/images](static/images) folder with the correct naming structure and in .svg format, and you're good to go!

## FAQs

### When to use imagotype, isotype or logotype in variants?

**imagotype**: a logo format that is made up of a symbol and text.  
**isotype**: consists of only one symbol or drawing.  
**logotype**: a logo that uses only the brand's name.
