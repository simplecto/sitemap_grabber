TODO

## 2.0.1 (2024-10-23)

## 2.0.0 (2024-10-18)

### BREAKING CHANGE

- A new exception is raised when sitemap cannot be parsed or other ParseErrors/ExpatErrors happen

### Feat

- **sitemap-parsing**: added custom exception and automatically fix unescaped entities in urls

## 1.0.1 (2024-10-12)

## 1.0.0 (2024-10-12)

### BREAKING CHANGE

- If your code called fetch() you now need to call the direct object properties (eg wk.fetch('/robots.txt') now becomes wk.robots_txt

### Refactor

- refactor well_knowns to handle more responses types

## 0.1.12 (2024-10-12)
