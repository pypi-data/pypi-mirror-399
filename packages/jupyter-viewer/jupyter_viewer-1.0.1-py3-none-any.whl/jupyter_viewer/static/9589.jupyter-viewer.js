"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[9589],{

/***/ 39589
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   mscgen: () => (/* binding */ mscgen),
/* harmony export */   msgenny: () => (/* binding */ msgenny),
/* harmony export */   xu: () => (/* binding */ xu)
/* harmony export */ });
function mkParser(lang) {
  return {
    name: "mscgen",
    startState: startStateFn,
    copyState: copyStateFn,
    token: produceTokenFunction(lang),
    languageData: {
      commentTokens: {
        line: "#",
        block: {
          open: "/*",
          close: "*/"
        }
      }
    }
  };
}
const mscgen = mkParser({
  "keywords": ["msc"],
  "options": ["hscale", "width", "arcgradient", "wordwraparcs"],
  "constants": ["true", "false", "on", "off"],
  "attributes": ["label", "idurl", "id", "url", "linecolor", "linecolour", "textcolor", "textcolour", "textbgcolor", "textbgcolour", "arclinecolor", "arclinecolour", "arctextcolor", "arctextcolour", "arctextbgcolor", "arctextbgcolour", "arcskip"],
  "brackets": ["\\{", "\\}"],
  // [ and  ] are brackets too, but these get handled in with lists
  "arcsWords": ["note", "abox", "rbox", "box"],
  "arcsOthers": ["\\|\\|\\|", "\\.\\.\\.", "---", "--", "<->", "==", "<<=>>", "<=>", "\\.\\.", "<<>>", "::", "<:>", "->", "=>>", "=>", ">>", ":>", "<-", "<<=", "<=", "<<", "<:", "x-", "-x"],
  "singlecomment": ["//", "#"],
  "operators": ["="]
});
const msgenny = mkParser({
  "keywords": null,
  "options": ["hscale", "width", "arcgradient", "wordwraparcs", "wordwrapentities", "watermark"],
  "constants": ["true", "false", "on", "off", "auto"],
  "attributes": null,
  "brackets": ["\\{", "\\}"],
  "arcsWords": ["note", "abox", "rbox", "box", "alt", "else", "opt", "break", "par", "seq", "strict", "neg", "critical", "ignore", "consider", "assert", "loop", "ref", "exc"],
  "arcsOthers": ["\\|\\|\\|", "\\.\\.\\.", "---", "--", "<->", "==", "<<=>>", "<=>", "\\.\\.", "<<>>", "::", "<:>", "->", "=>>", "=>", ">>", ":>", "<-", "<<=", "<=", "<<", "<:", "x-", "-x"],
  "singlecomment": ["//", "#"],
  "operators": ["="]
});
const xu = mkParser({
  "keywords": ["msc", "xu"],
  "options": ["hscale", "width", "arcgradient", "wordwraparcs", "wordwrapentities", "watermark"],
  "constants": ["true", "false", "on", "off", "auto"],
  "attributes": ["label", "idurl", "id", "url", "linecolor", "linecolour", "textcolor", "textcolour", "textbgcolor", "textbgcolour", "arclinecolor", "arclinecolour", "arctextcolor", "arctextcolour", "arctextbgcolor", "arctextbgcolour", "arcskip", "title", "deactivate", "activate", "activation"],
  "brackets": ["\\{", "\\}"],
  // [ and  ] are brackets too, but these get handled in with lists
  "arcsWords": ["note", "abox", "rbox", "box", "alt", "else", "opt", "break", "par", "seq", "strict", "neg", "critical", "ignore", "consider", "assert", "loop", "ref", "exc"],
  "arcsOthers": ["\\|\\|\\|", "\\.\\.\\.", "---", "--", "<->", "==", "<<=>>", "<=>", "\\.\\.", "<<>>", "::", "<:>", "->", "=>>", "=>", ">>", ":>", "<-", "<<=", "<=", "<<", "<:", "x-", "-x"],
  "singlecomment": ["//", "#"],
  "operators": ["="]
});
function wordRegexpBoundary(pWords) {
  return new RegExp("^\\b(" + pWords.join("|") + ")\\b", "i");
}
function wordRegexp(pWords) {
  return new RegExp("^(?:" + pWords.join("|") + ")", "i");
}
function startStateFn() {
  return {
    inComment: false,
    inString: false,
    inAttributeList: false,
    inScript: false
  };
}
function copyStateFn(pState) {
  return {
    inComment: pState.inComment,
    inString: pState.inString,
    inAttributeList: pState.inAttributeList,
    inScript: pState.inScript
  };
}
function produceTokenFunction(pConfig) {
  return function (pStream, pState) {
    if (pStream.match(wordRegexp(pConfig.brackets), true, true)) {
      return "bracket";
    }
    /* comments */
    if (!pState.inComment) {
      if (pStream.match(/\/\*[^\*\/]*/, true, true)) {
        pState.inComment = true;
        return "comment";
      }
      if (pStream.match(wordRegexp(pConfig.singlecomment), true, true)) {
        pStream.skipToEnd();
        return "comment";
      }
    }
    if (pState.inComment) {
      if (pStream.match(/[^\*\/]*\*\//, true, true)) pState.inComment = false;else pStream.skipToEnd();
      return "comment";
    }
    /* strings */
    if (!pState.inString && pStream.match(/\"(\\\"|[^\"])*/, true, true)) {
      pState.inString = true;
      return "string";
    }
    if (pState.inString) {
      if (pStream.match(/[^\"]*\"/, true, true)) pState.inString = false;else pStream.skipToEnd();
      return "string";
    }
    /* keywords & operators */
    if (!!pConfig.keywords && pStream.match(wordRegexpBoundary(pConfig.keywords), true, true)) return "keyword";
    if (pStream.match(wordRegexpBoundary(pConfig.options), true, true)) return "keyword";
    if (pStream.match(wordRegexpBoundary(pConfig.arcsWords), true, true)) return "keyword";
    if (pStream.match(wordRegexp(pConfig.arcsOthers), true, true)) return "keyword";
    if (!!pConfig.operators && pStream.match(wordRegexp(pConfig.operators), true, true)) return "operator";
    if (!!pConfig.constants && pStream.match(wordRegexp(pConfig.constants), true, true)) return "variable";

    /* attribute lists */
    if (!pConfig.inAttributeList && !!pConfig.attributes && pStream.match('[', true, true)) {
      pConfig.inAttributeList = true;
      return "bracket";
    }
    if (pConfig.inAttributeList) {
      if (pConfig.attributes !== null && pStream.match(wordRegexpBoundary(pConfig.attributes), true, true)) {
        return "attribute";
      }
      if (pStream.match(']', true, true)) {
        pConfig.inAttributeList = false;
        return "bracket";
      }
    }
    pStream.next();
    return null;
  };
}

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiOTU4OS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7OztBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvbXNjZ2VuLmpzIl0sInNvdXJjZXNDb250ZW50IjpbImZ1bmN0aW9uIG1rUGFyc2VyKGxhbmcpIHtcbiAgcmV0dXJuIHtcbiAgICBuYW1lOiBcIm1zY2dlblwiLFxuICAgIHN0YXJ0U3RhdGU6IHN0YXJ0U3RhdGVGbixcbiAgICBjb3B5U3RhdGU6IGNvcHlTdGF0ZUZuLFxuICAgIHRva2VuOiBwcm9kdWNlVG9rZW5GdW5jdGlvbihsYW5nKSxcbiAgICBsYW5ndWFnZURhdGE6IHtcbiAgICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgICAgbGluZTogXCIjXCIsXG4gICAgICAgIGJsb2NrOiB7XG4gICAgICAgICAgb3BlbjogXCIvKlwiLFxuICAgICAgICAgIGNsb3NlOiBcIiovXCJcbiAgICAgICAgfVxuICAgICAgfVxuICAgIH1cbiAgfTtcbn1cbmV4cG9ydCBjb25zdCBtc2NnZW4gPSBta1BhcnNlcih7XG4gIFwia2V5d29yZHNcIjogW1wibXNjXCJdLFxuICBcIm9wdGlvbnNcIjogW1wiaHNjYWxlXCIsIFwid2lkdGhcIiwgXCJhcmNncmFkaWVudFwiLCBcIndvcmR3cmFwYXJjc1wiXSxcbiAgXCJjb25zdGFudHNcIjogW1widHJ1ZVwiLCBcImZhbHNlXCIsIFwib25cIiwgXCJvZmZcIl0sXG4gIFwiYXR0cmlidXRlc1wiOiBbXCJsYWJlbFwiLCBcImlkdXJsXCIsIFwiaWRcIiwgXCJ1cmxcIiwgXCJsaW5lY29sb3JcIiwgXCJsaW5lY29sb3VyXCIsIFwidGV4dGNvbG9yXCIsIFwidGV4dGNvbG91clwiLCBcInRleHRiZ2NvbG9yXCIsIFwidGV4dGJnY29sb3VyXCIsIFwiYXJjbGluZWNvbG9yXCIsIFwiYXJjbGluZWNvbG91clwiLCBcImFyY3RleHRjb2xvclwiLCBcImFyY3RleHRjb2xvdXJcIiwgXCJhcmN0ZXh0Ymdjb2xvclwiLCBcImFyY3RleHRiZ2NvbG91clwiLCBcImFyY3NraXBcIl0sXG4gIFwiYnJhY2tldHNcIjogW1wiXFxcXHtcIiwgXCJcXFxcfVwiXSxcbiAgLy8gWyBhbmQgIF0gYXJlIGJyYWNrZXRzIHRvbywgYnV0IHRoZXNlIGdldCBoYW5kbGVkIGluIHdpdGggbGlzdHNcbiAgXCJhcmNzV29yZHNcIjogW1wibm90ZVwiLCBcImFib3hcIiwgXCJyYm94XCIsIFwiYm94XCJdLFxuICBcImFyY3NPdGhlcnNcIjogW1wiXFxcXHxcXFxcfFxcXFx8XCIsIFwiXFxcXC5cXFxcLlxcXFwuXCIsIFwiLS0tXCIsIFwiLS1cIiwgXCI8LT5cIiwgXCI9PVwiLCBcIjw8PT4+XCIsIFwiPD0+XCIsIFwiXFxcXC5cXFxcLlwiLCBcIjw8Pj5cIiwgXCI6OlwiLCBcIjw6PlwiLCBcIi0+XCIsIFwiPT4+XCIsIFwiPT5cIiwgXCI+PlwiLCBcIjo+XCIsIFwiPC1cIiwgXCI8PD1cIiwgXCI8PVwiLCBcIjw8XCIsIFwiPDpcIiwgXCJ4LVwiLCBcIi14XCJdLFxuICBcInNpbmdsZWNvbW1lbnRcIjogW1wiLy9cIiwgXCIjXCJdLFxuICBcIm9wZXJhdG9yc1wiOiBbXCI9XCJdXG59KTtcbmV4cG9ydCBjb25zdCBtc2dlbm55ID0gbWtQYXJzZXIoe1xuICBcImtleXdvcmRzXCI6IG51bGwsXG4gIFwib3B0aW9uc1wiOiBbXCJoc2NhbGVcIiwgXCJ3aWR0aFwiLCBcImFyY2dyYWRpZW50XCIsIFwid29yZHdyYXBhcmNzXCIsIFwid29yZHdyYXBlbnRpdGllc1wiLCBcIndhdGVybWFya1wiXSxcbiAgXCJjb25zdGFudHNcIjogW1widHJ1ZVwiLCBcImZhbHNlXCIsIFwib25cIiwgXCJvZmZcIiwgXCJhdXRvXCJdLFxuICBcImF0dHJpYnV0ZXNcIjogbnVsbCxcbiAgXCJicmFja2V0c1wiOiBbXCJcXFxce1wiLCBcIlxcXFx9XCJdLFxuICBcImFyY3NXb3Jkc1wiOiBbXCJub3RlXCIsIFwiYWJveFwiLCBcInJib3hcIiwgXCJib3hcIiwgXCJhbHRcIiwgXCJlbHNlXCIsIFwib3B0XCIsIFwiYnJlYWtcIiwgXCJwYXJcIiwgXCJzZXFcIiwgXCJzdHJpY3RcIiwgXCJuZWdcIiwgXCJjcml0aWNhbFwiLCBcImlnbm9yZVwiLCBcImNvbnNpZGVyXCIsIFwiYXNzZXJ0XCIsIFwibG9vcFwiLCBcInJlZlwiLCBcImV4Y1wiXSxcbiAgXCJhcmNzT3RoZXJzXCI6IFtcIlxcXFx8XFxcXHxcXFxcfFwiLCBcIlxcXFwuXFxcXC5cXFxcLlwiLCBcIi0tLVwiLCBcIi0tXCIsIFwiPC0+XCIsIFwiPT1cIiwgXCI8PD0+PlwiLCBcIjw9PlwiLCBcIlxcXFwuXFxcXC5cIiwgXCI8PD4+XCIsIFwiOjpcIiwgXCI8Oj5cIiwgXCItPlwiLCBcIj0+PlwiLCBcIj0+XCIsIFwiPj5cIiwgXCI6PlwiLCBcIjwtXCIsIFwiPDw9XCIsIFwiPD1cIiwgXCI8PFwiLCBcIjw6XCIsIFwieC1cIiwgXCIteFwiXSxcbiAgXCJzaW5nbGVjb21tZW50XCI6IFtcIi8vXCIsIFwiI1wiXSxcbiAgXCJvcGVyYXRvcnNcIjogW1wiPVwiXVxufSk7XG5leHBvcnQgY29uc3QgeHUgPSBta1BhcnNlcih7XG4gIFwia2V5d29yZHNcIjogW1wibXNjXCIsIFwieHVcIl0sXG4gIFwib3B0aW9uc1wiOiBbXCJoc2NhbGVcIiwgXCJ3aWR0aFwiLCBcImFyY2dyYWRpZW50XCIsIFwid29yZHdyYXBhcmNzXCIsIFwid29yZHdyYXBlbnRpdGllc1wiLCBcIndhdGVybWFya1wiXSxcbiAgXCJjb25zdGFudHNcIjogW1widHJ1ZVwiLCBcImZhbHNlXCIsIFwib25cIiwgXCJvZmZcIiwgXCJhdXRvXCJdLFxuICBcImF0dHJpYnV0ZXNcIjogW1wibGFiZWxcIiwgXCJpZHVybFwiLCBcImlkXCIsIFwidXJsXCIsIFwibGluZWNvbG9yXCIsIFwibGluZWNvbG91clwiLCBcInRleHRjb2xvclwiLCBcInRleHRjb2xvdXJcIiwgXCJ0ZXh0Ymdjb2xvclwiLCBcInRleHRiZ2NvbG91clwiLCBcImFyY2xpbmVjb2xvclwiLCBcImFyY2xpbmVjb2xvdXJcIiwgXCJhcmN0ZXh0Y29sb3JcIiwgXCJhcmN0ZXh0Y29sb3VyXCIsIFwiYXJjdGV4dGJnY29sb3JcIiwgXCJhcmN0ZXh0Ymdjb2xvdXJcIiwgXCJhcmNza2lwXCIsIFwidGl0bGVcIiwgXCJkZWFjdGl2YXRlXCIsIFwiYWN0aXZhdGVcIiwgXCJhY3RpdmF0aW9uXCJdLFxuICBcImJyYWNrZXRzXCI6IFtcIlxcXFx7XCIsIFwiXFxcXH1cIl0sXG4gIC8vIFsgYW5kICBdIGFyZSBicmFja2V0cyB0b28sIGJ1dCB0aGVzZSBnZXQgaGFuZGxlZCBpbiB3aXRoIGxpc3RzXG4gIFwiYXJjc1dvcmRzXCI6IFtcIm5vdGVcIiwgXCJhYm94XCIsIFwicmJveFwiLCBcImJveFwiLCBcImFsdFwiLCBcImVsc2VcIiwgXCJvcHRcIiwgXCJicmVha1wiLCBcInBhclwiLCBcInNlcVwiLCBcInN0cmljdFwiLCBcIm5lZ1wiLCBcImNyaXRpY2FsXCIsIFwiaWdub3JlXCIsIFwiY29uc2lkZXJcIiwgXCJhc3NlcnRcIiwgXCJsb29wXCIsIFwicmVmXCIsIFwiZXhjXCJdLFxuICBcImFyY3NPdGhlcnNcIjogW1wiXFxcXHxcXFxcfFxcXFx8XCIsIFwiXFxcXC5cXFxcLlxcXFwuXCIsIFwiLS0tXCIsIFwiLS1cIiwgXCI8LT5cIiwgXCI9PVwiLCBcIjw8PT4+XCIsIFwiPD0+XCIsIFwiXFxcXC5cXFxcLlwiLCBcIjw8Pj5cIiwgXCI6OlwiLCBcIjw6PlwiLCBcIi0+XCIsIFwiPT4+XCIsIFwiPT5cIiwgXCI+PlwiLCBcIjo+XCIsIFwiPC1cIiwgXCI8PD1cIiwgXCI8PVwiLCBcIjw8XCIsIFwiPDpcIiwgXCJ4LVwiLCBcIi14XCJdLFxuICBcInNpbmdsZWNvbW1lbnRcIjogW1wiLy9cIiwgXCIjXCJdLFxuICBcIm9wZXJhdG9yc1wiOiBbXCI9XCJdXG59KTtcbmZ1bmN0aW9uIHdvcmRSZWdleHBCb3VuZGFyeShwV29yZHMpIHtcbiAgcmV0dXJuIG5ldyBSZWdFeHAoXCJeXFxcXGIoXCIgKyBwV29yZHMuam9pbihcInxcIikgKyBcIilcXFxcYlwiLCBcImlcIik7XG59XG5mdW5jdGlvbiB3b3JkUmVnZXhwKHBXb3Jkcykge1xuICByZXR1cm4gbmV3IFJlZ0V4cChcIl4oPzpcIiArIHBXb3Jkcy5qb2luKFwifFwiKSArIFwiKVwiLCBcImlcIik7XG59XG5mdW5jdGlvbiBzdGFydFN0YXRlRm4oKSB7XG4gIHJldHVybiB7XG4gICAgaW5Db21tZW50OiBmYWxzZSxcbiAgICBpblN0cmluZzogZmFsc2UsXG4gICAgaW5BdHRyaWJ1dGVMaXN0OiBmYWxzZSxcbiAgICBpblNjcmlwdDogZmFsc2VcbiAgfTtcbn1cbmZ1bmN0aW9uIGNvcHlTdGF0ZUZuKHBTdGF0ZSkge1xuICByZXR1cm4ge1xuICAgIGluQ29tbWVudDogcFN0YXRlLmluQ29tbWVudCxcbiAgICBpblN0cmluZzogcFN0YXRlLmluU3RyaW5nLFxuICAgIGluQXR0cmlidXRlTGlzdDogcFN0YXRlLmluQXR0cmlidXRlTGlzdCxcbiAgICBpblNjcmlwdDogcFN0YXRlLmluU2NyaXB0XG4gIH07XG59XG5mdW5jdGlvbiBwcm9kdWNlVG9rZW5GdW5jdGlvbihwQ29uZmlnKSB7XG4gIHJldHVybiBmdW5jdGlvbiAocFN0cmVhbSwgcFN0YXRlKSB7XG4gICAgaWYgKHBTdHJlYW0ubWF0Y2god29yZFJlZ2V4cChwQ29uZmlnLmJyYWNrZXRzKSwgdHJ1ZSwgdHJ1ZSkpIHtcbiAgICAgIHJldHVybiBcImJyYWNrZXRcIjtcbiAgICB9XG4gICAgLyogY29tbWVudHMgKi9cbiAgICBpZiAoIXBTdGF0ZS5pbkNvbW1lbnQpIHtcbiAgICAgIGlmIChwU3RyZWFtLm1hdGNoKC9cXC9cXCpbXlxcKlxcL10qLywgdHJ1ZSwgdHJ1ZSkpIHtcbiAgICAgICAgcFN0YXRlLmluQ29tbWVudCA9IHRydWU7XG4gICAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICAgIH1cbiAgICAgIGlmIChwU3RyZWFtLm1hdGNoKHdvcmRSZWdleHAocENvbmZpZy5zaW5nbGVjb21tZW50KSwgdHJ1ZSwgdHJ1ZSkpIHtcbiAgICAgICAgcFN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICAgICAgfVxuICAgIH1cbiAgICBpZiAocFN0YXRlLmluQ29tbWVudCkge1xuICAgICAgaWYgKHBTdHJlYW0ubWF0Y2goL1teXFwqXFwvXSpcXCpcXC8vLCB0cnVlLCB0cnVlKSkgcFN0YXRlLmluQ29tbWVudCA9IGZhbHNlO2Vsc2UgcFN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICB9XG4gICAgLyogc3RyaW5ncyAqL1xuICAgIGlmICghcFN0YXRlLmluU3RyaW5nICYmIHBTdHJlYW0ubWF0Y2goL1xcXCIoXFxcXFxcXCJ8W15cXFwiXSkqLywgdHJ1ZSwgdHJ1ZSkpIHtcbiAgICAgIHBTdGF0ZS5pblN0cmluZyA9IHRydWU7XG4gICAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgICB9XG4gICAgaWYgKHBTdGF0ZS5pblN0cmluZykge1xuICAgICAgaWYgKHBTdHJlYW0ubWF0Y2goL1teXFxcIl0qXFxcIi8sIHRydWUsIHRydWUpKSBwU3RhdGUuaW5TdHJpbmcgPSBmYWxzZTtlbHNlIHBTdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgICB9XG4gICAgLyoga2V5d29yZHMgJiBvcGVyYXRvcnMgKi9cbiAgICBpZiAoISFwQ29uZmlnLmtleXdvcmRzICYmIHBTdHJlYW0ubWF0Y2god29yZFJlZ2V4cEJvdW5kYXJ5KHBDb25maWcua2V5d29yZHMpLCB0cnVlLCB0cnVlKSkgcmV0dXJuIFwia2V5d29yZFwiO1xuICAgIGlmIChwU3RyZWFtLm1hdGNoKHdvcmRSZWdleHBCb3VuZGFyeShwQ29uZmlnLm9wdGlvbnMpLCB0cnVlLCB0cnVlKSkgcmV0dXJuIFwia2V5d29yZFwiO1xuICAgIGlmIChwU3RyZWFtLm1hdGNoKHdvcmRSZWdleHBCb3VuZGFyeShwQ29uZmlnLmFyY3NXb3JkcyksIHRydWUsIHRydWUpKSByZXR1cm4gXCJrZXl3b3JkXCI7XG4gICAgaWYgKHBTdHJlYW0ubWF0Y2god29yZFJlZ2V4cChwQ29uZmlnLmFyY3NPdGhlcnMpLCB0cnVlLCB0cnVlKSkgcmV0dXJuIFwia2V5d29yZFwiO1xuICAgIGlmICghIXBDb25maWcub3BlcmF0b3JzICYmIHBTdHJlYW0ubWF0Y2god29yZFJlZ2V4cChwQ29uZmlnLm9wZXJhdG9ycyksIHRydWUsIHRydWUpKSByZXR1cm4gXCJvcGVyYXRvclwiO1xuICAgIGlmICghIXBDb25maWcuY29uc3RhbnRzICYmIHBTdHJlYW0ubWF0Y2god29yZFJlZ2V4cChwQ29uZmlnLmNvbnN0YW50cyksIHRydWUsIHRydWUpKSByZXR1cm4gXCJ2YXJpYWJsZVwiO1xuXG4gICAgLyogYXR0cmlidXRlIGxpc3RzICovXG4gICAgaWYgKCFwQ29uZmlnLmluQXR0cmlidXRlTGlzdCAmJiAhIXBDb25maWcuYXR0cmlidXRlcyAmJiBwU3RyZWFtLm1hdGNoKCdbJywgdHJ1ZSwgdHJ1ZSkpIHtcbiAgICAgIHBDb25maWcuaW5BdHRyaWJ1dGVMaXN0ID0gdHJ1ZTtcbiAgICAgIHJldHVybiBcImJyYWNrZXRcIjtcbiAgICB9XG4gICAgaWYgKHBDb25maWcuaW5BdHRyaWJ1dGVMaXN0KSB7XG4gICAgICBpZiAocENvbmZpZy5hdHRyaWJ1dGVzICE9PSBudWxsICYmIHBTdHJlYW0ubWF0Y2god29yZFJlZ2V4cEJvdW5kYXJ5KHBDb25maWcuYXR0cmlidXRlcyksIHRydWUsIHRydWUpKSB7XG4gICAgICAgIHJldHVybiBcImF0dHJpYnV0ZVwiO1xuICAgICAgfVxuICAgICAgaWYgKHBTdHJlYW0ubWF0Y2goJ10nLCB0cnVlLCB0cnVlKSkge1xuICAgICAgICBwQ29uZmlnLmluQXR0cmlidXRlTGlzdCA9IGZhbHNlO1xuICAgICAgICByZXR1cm4gXCJicmFja2V0XCI7XG4gICAgICB9XG4gICAgfVxuICAgIHBTdHJlYW0ubmV4dCgpO1xuICAgIHJldHVybiBudWxsO1xuICB9O1xufSJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=