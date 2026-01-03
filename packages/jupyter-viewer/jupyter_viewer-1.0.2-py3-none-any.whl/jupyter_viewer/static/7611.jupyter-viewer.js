"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[7611],{

/***/ 17611
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   yaml: () => (/* binding */ yaml)
/* harmony export */ });
var cons = ['true', 'false', 'on', 'off', 'yes', 'no'];
var keywordRegex = new RegExp("\\b((" + cons.join(")|(") + "))$", 'i');
const yaml = {
  name: "yaml",
  token: function (stream, state) {
    var ch = stream.peek();
    var esc = state.escaped;
    state.escaped = false;
    /* comments */
    if (ch == "#" && (stream.pos == 0 || /\s/.test(stream.string.charAt(stream.pos - 1)))) {
      stream.skipToEnd();
      return "comment";
    }
    if (stream.match(/^('([^']|\\.)*'?|"([^"]|\\.)*"?)/)) return "string";
    if (state.literal && stream.indentation() > state.keyCol) {
      stream.skipToEnd();
      return "string";
    } else if (state.literal) {
      state.literal = false;
    }
    if (stream.sol()) {
      state.keyCol = 0;
      state.pair = false;
      state.pairStart = false;
      /* document start */
      if (stream.match('---')) {
        return "def";
      }
      /* document end */
      if (stream.match('...')) {
        return "def";
      }
      /* array list item */
      if (stream.match(/^\s*-\s+/)) {
        return 'meta';
      }
    }
    /* inline pairs/lists */
    if (stream.match(/^(\{|\}|\[|\])/)) {
      if (ch == '{') state.inlinePairs++;else if (ch == '}') state.inlinePairs--;else if (ch == '[') state.inlineList++;else state.inlineList--;
      return 'meta';
    }

    /* list separator */
    if (state.inlineList > 0 && !esc && ch == ',') {
      stream.next();
      return 'meta';
    }
    /* pairs separator */
    if (state.inlinePairs > 0 && !esc && ch == ',') {
      state.keyCol = 0;
      state.pair = false;
      state.pairStart = false;
      stream.next();
      return 'meta';
    }

    /* start of value of a pair */
    if (state.pairStart) {
      /* block literals */
      if (stream.match(/^\s*(\||\>)\s*/)) {
        state.literal = true;
        return 'meta';
      }
      ;
      /* references */
      if (stream.match(/^\s*(\&|\*)[a-z0-9\._-]+\b/i)) {
        return 'variable';
      }
      /* numbers */
      if (state.inlinePairs == 0 && stream.match(/^\s*-?[0-9\.\,]+\s?$/)) {
        return 'number';
      }
      if (state.inlinePairs > 0 && stream.match(/^\s*-?[0-9\.\,]+\s?(?=(,|}))/)) {
        return 'number';
      }
      /* keywords */
      if (stream.match(keywordRegex)) {
        return 'keyword';
      }
    }

    /* pairs (associative arrays) -> key */
    if (!state.pair && stream.match(/^\s*(?:[,\[\]{}&*!|>'"%@`][^\s'":]|[^,\[\]{}#&*!|>'"%@`])[^#]*?(?=\s*:($|\s))/)) {
      state.pair = true;
      state.keyCol = stream.indentation();
      return "atom";
    }
    if (state.pair && stream.match(/^:\s*/)) {
      state.pairStart = true;
      return 'meta';
    }

    /* nothing found, continue */
    state.pairStart = false;
    state.escaped = ch == '\\';
    stream.next();
    return null;
  },
  startState: function () {
    return {
      pair: false,
      pairStart: false,
      keyCol: 0,
      inlinePairs: 0,
      inlineList: 0,
      literal: false,
      escaped: false
    };
  },
  languageData: {
    commentTokens: {
      line: "#"
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNzYxMS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS95YW1sLmpzIl0sInNvdXJjZXNDb250ZW50IjpbInZhciBjb25zID0gWyd0cnVlJywgJ2ZhbHNlJywgJ29uJywgJ29mZicsICd5ZXMnLCAnbm8nXTtcbnZhciBrZXl3b3JkUmVnZXggPSBuZXcgUmVnRXhwKFwiXFxcXGIoKFwiICsgY29ucy5qb2luKFwiKXwoXCIpICsgXCIpKSRcIiwgJ2knKTtcbmV4cG9ydCBjb25zdCB5YW1sID0ge1xuICBuYW1lOiBcInlhbWxcIixcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGNoID0gc3RyZWFtLnBlZWsoKTtcbiAgICB2YXIgZXNjID0gc3RhdGUuZXNjYXBlZDtcbiAgICBzdGF0ZS5lc2NhcGVkID0gZmFsc2U7XG4gICAgLyogY29tbWVudHMgKi9cbiAgICBpZiAoY2ggPT0gXCIjXCIgJiYgKHN0cmVhbS5wb3MgPT0gMCB8fCAvXFxzLy50ZXN0KHN0cmVhbS5zdHJpbmcuY2hhckF0KHN0cmVhbS5wb3MgLSAxKSkpKSB7XG4gICAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgfVxuICAgIGlmIChzdHJlYW0ubWF0Y2goL14oJyhbXiddfFxcXFwuKSonP3xcIihbXlwiXXxcXFxcLikqXCI/KS8pKSByZXR1cm4gXCJzdHJpbmdcIjtcbiAgICBpZiAoc3RhdGUubGl0ZXJhbCAmJiBzdHJlYW0uaW5kZW50YXRpb24oKSA+IHN0YXRlLmtleUNvbCkge1xuICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gICAgfSBlbHNlIGlmIChzdGF0ZS5saXRlcmFsKSB7XG4gICAgICBzdGF0ZS5saXRlcmFsID0gZmFsc2U7XG4gICAgfVxuICAgIGlmIChzdHJlYW0uc29sKCkpIHtcbiAgICAgIHN0YXRlLmtleUNvbCA9IDA7XG4gICAgICBzdGF0ZS5wYWlyID0gZmFsc2U7XG4gICAgICBzdGF0ZS5wYWlyU3RhcnQgPSBmYWxzZTtcbiAgICAgIC8qIGRvY3VtZW50IHN0YXJ0ICovXG4gICAgICBpZiAoc3RyZWFtLm1hdGNoKCctLS0nKSkge1xuICAgICAgICByZXR1cm4gXCJkZWZcIjtcbiAgICAgIH1cbiAgICAgIC8qIGRvY3VtZW50IGVuZCAqL1xuICAgICAgaWYgKHN0cmVhbS5tYXRjaCgnLi4uJykpIHtcbiAgICAgICAgcmV0dXJuIFwiZGVmXCI7XG4gICAgICB9XG4gICAgICAvKiBhcnJheSBsaXN0IGl0ZW0gKi9cbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goL15cXHMqLVxccysvKSkge1xuICAgICAgICByZXR1cm4gJ21ldGEnO1xuICAgICAgfVxuICAgIH1cbiAgICAvKiBpbmxpbmUgcGFpcnMvbGlzdHMgKi9cbiAgICBpZiAoc3RyZWFtLm1hdGNoKC9eKFxce3xcXH18XFxbfFxcXSkvKSkge1xuICAgICAgaWYgKGNoID09ICd7Jykgc3RhdGUuaW5saW5lUGFpcnMrKztlbHNlIGlmIChjaCA9PSAnfScpIHN0YXRlLmlubGluZVBhaXJzLS07ZWxzZSBpZiAoY2ggPT0gJ1snKSBzdGF0ZS5pbmxpbmVMaXN0Kys7ZWxzZSBzdGF0ZS5pbmxpbmVMaXN0LS07XG4gICAgICByZXR1cm4gJ21ldGEnO1xuICAgIH1cblxuICAgIC8qIGxpc3Qgc2VwYXJhdG9yICovXG4gICAgaWYgKHN0YXRlLmlubGluZUxpc3QgPiAwICYmICFlc2MgJiYgY2ggPT0gJywnKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgcmV0dXJuICdtZXRhJztcbiAgICB9XG4gICAgLyogcGFpcnMgc2VwYXJhdG9yICovXG4gICAgaWYgKHN0YXRlLmlubGluZVBhaXJzID4gMCAmJiAhZXNjICYmIGNoID09ICcsJykge1xuICAgICAgc3RhdGUua2V5Q29sID0gMDtcbiAgICAgIHN0YXRlLnBhaXIgPSBmYWxzZTtcbiAgICAgIHN0YXRlLnBhaXJTdGFydCA9IGZhbHNlO1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIHJldHVybiAnbWV0YSc7XG4gICAgfVxuXG4gICAgLyogc3RhcnQgb2YgdmFsdWUgb2YgYSBwYWlyICovXG4gICAgaWYgKHN0YXRlLnBhaXJTdGFydCkge1xuICAgICAgLyogYmxvY2sgbGl0ZXJhbHMgKi9cbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goL15cXHMqKFxcfHxcXD4pXFxzKi8pKSB7XG4gICAgICAgIHN0YXRlLmxpdGVyYWwgPSB0cnVlO1xuICAgICAgICByZXR1cm4gJ21ldGEnO1xuICAgICAgfVxuICAgICAgO1xuICAgICAgLyogcmVmZXJlbmNlcyAqL1xuICAgICAgaWYgKHN0cmVhbS5tYXRjaCgvXlxccyooXFwmfFxcKilbYS16MC05XFwuXy1dK1xcYi9pKSkge1xuICAgICAgICByZXR1cm4gJ3ZhcmlhYmxlJztcbiAgICAgIH1cbiAgICAgIC8qIG51bWJlcnMgKi9cbiAgICAgIGlmIChzdGF0ZS5pbmxpbmVQYWlycyA9PSAwICYmIHN0cmVhbS5tYXRjaCgvXlxccyotP1swLTlcXC5cXCxdK1xccz8kLykpIHtcbiAgICAgICAgcmV0dXJuICdudW1iZXInO1xuICAgICAgfVxuICAgICAgaWYgKHN0YXRlLmlubGluZVBhaXJzID4gMCAmJiBzdHJlYW0ubWF0Y2goL15cXHMqLT9bMC05XFwuXFwsXStcXHM/KD89KCx8fSkpLykpIHtcbiAgICAgICAgcmV0dXJuICdudW1iZXInO1xuICAgICAgfVxuICAgICAgLyoga2V5d29yZHMgKi9cbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goa2V5d29yZFJlZ2V4KSkge1xuICAgICAgICByZXR1cm4gJ2tleXdvcmQnO1xuICAgICAgfVxuICAgIH1cblxuICAgIC8qIHBhaXJzIChhc3NvY2lhdGl2ZSBhcnJheXMpIC0+IGtleSAqL1xuICAgIGlmICghc3RhdGUucGFpciAmJiBzdHJlYW0ubWF0Y2goL15cXHMqKD86WyxcXFtcXF17fSYqIXw+J1wiJUBgXVteXFxzJ1wiOl18W14sXFxbXFxde30jJiohfD4nXCIlQGBdKVteI10qPyg/PVxccyo6KCR8XFxzKSkvKSkge1xuICAgICAgc3RhdGUucGFpciA9IHRydWU7XG4gICAgICBzdGF0ZS5rZXlDb2wgPSBzdHJlYW0uaW5kZW50YXRpb24oKTtcbiAgICAgIHJldHVybiBcImF0b21cIjtcbiAgICB9XG4gICAgaWYgKHN0YXRlLnBhaXIgJiYgc3RyZWFtLm1hdGNoKC9eOlxccyovKSkge1xuICAgICAgc3RhdGUucGFpclN0YXJ0ID0gdHJ1ZTtcbiAgICAgIHJldHVybiAnbWV0YSc7XG4gICAgfVxuXG4gICAgLyogbm90aGluZyBmb3VuZCwgY29udGludWUgKi9cbiAgICBzdGF0ZS5wYWlyU3RhcnQgPSBmYWxzZTtcbiAgICBzdGF0ZS5lc2NhcGVkID0gY2ggPT0gJ1xcXFwnO1xuICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgcmV0dXJuIG51bGw7XG4gIH0sXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgcGFpcjogZmFsc2UsXG4gICAgICBwYWlyU3RhcnQ6IGZhbHNlLFxuICAgICAga2V5Q29sOiAwLFxuICAgICAgaW5saW5lUGFpcnM6IDAsXG4gICAgICBpbmxpbmVMaXN0OiAwLFxuICAgICAgbGl0ZXJhbDogZmFsc2UsXG4gICAgICBlc2NhcGVkOiBmYWxzZVxuICAgIH07XG4gIH0sXG4gIGxhbmd1YWdlRGF0YToge1xuICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgIGxpbmU6IFwiI1wiXG4gICAgfVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=