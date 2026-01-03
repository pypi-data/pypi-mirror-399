"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[1932],{

/***/ 81932
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   toml: () => (/* binding */ toml)
/* harmony export */ });
const toml = {
  name: "toml",
  startState: function () {
    return {
      inString: false,
      stringType: "",
      lhs: true,
      inArray: 0
    };
  },
  token: function (stream, state) {
    //check for state changes
    let quote;
    if (!state.inString && (quote = stream.match(/^('''|"""|'|")/))) {
      state.stringType = quote[0];
      state.inString = true; // Update state
    }
    if (stream.sol() && !state.inString && state.inArray === 0) {
      state.lhs = true;
    }
    //return state
    if (state.inString) {
      while (state.inString) {
        if (stream.match(state.stringType)) {
          state.inString = false; // Clear flag
        } else if (stream.peek() === '\\') {
          stream.next();
          stream.next();
        } else if (stream.eol()) {
          break;
        } else {
          stream.match(/^.[^\\\"\']*/);
        }
      }
      return state.lhs ? "property" : "string"; // Token style
    } else if (state.inArray && stream.peek() === ']') {
      stream.next();
      state.inArray--;
      return 'bracket';
    } else if (state.lhs && stream.peek() === '[' && stream.skipTo(']')) {
      stream.next(); //skip closing ]
      // array of objects has an extra open & close []
      if (stream.peek() === ']') stream.next();
      return "atom";
    } else if (stream.peek() === "#") {
      stream.skipToEnd();
      return "comment";
    } else if (stream.eatSpace()) {
      return null;
    } else if (state.lhs && stream.eatWhile(function (c) {
      return c != '=' && c != ' ';
    })) {
      return "property";
    } else if (state.lhs && stream.peek() === "=") {
      stream.next();
      state.lhs = false;
      return null;
    } else if (!state.lhs && stream.match(/^\d\d\d\d[\d\-\:\.T]*Z/)) {
      return 'atom'; //date
    } else if (!state.lhs && (stream.match('true') || stream.match('false'))) {
      return 'atom';
    } else if (!state.lhs && stream.peek() === '[') {
      state.inArray++;
      stream.next();
      return 'bracket';
    } else if (!state.lhs && stream.match(/^\-?\d+(?:\.\d+)?/)) {
      return 'number';
    } else if (!stream.eatSpace()) {
      stream.next();
    }
    return null;
  },
  languageData: {
    commentTokens: {
      line: '#'
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMTkzMi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL3RvbWwuanMiXSwic291cmNlc0NvbnRlbnQiOlsiZXhwb3J0IGNvbnN0IHRvbWwgPSB7XG4gIG5hbWU6IFwidG9tbFwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIGluU3RyaW5nOiBmYWxzZSxcbiAgICAgIHN0cmluZ1R5cGU6IFwiXCIsXG4gICAgICBsaHM6IHRydWUsXG4gICAgICBpbkFycmF5OiAwXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgLy9jaGVjayBmb3Igc3RhdGUgY2hhbmdlc1xuICAgIGxldCBxdW90ZTtcbiAgICBpZiAoIXN0YXRlLmluU3RyaW5nICYmIChxdW90ZSA9IHN0cmVhbS5tYXRjaCgvXignJyd8XCJcIlwifCd8XCIpLykpKSB7XG4gICAgICBzdGF0ZS5zdHJpbmdUeXBlID0gcXVvdGVbMF07XG4gICAgICBzdGF0ZS5pblN0cmluZyA9IHRydWU7IC8vIFVwZGF0ZSBzdGF0ZVxuICAgIH1cbiAgICBpZiAoc3RyZWFtLnNvbCgpICYmICFzdGF0ZS5pblN0cmluZyAmJiBzdGF0ZS5pbkFycmF5ID09PSAwKSB7XG4gICAgICBzdGF0ZS5saHMgPSB0cnVlO1xuICAgIH1cbiAgICAvL3JldHVybiBzdGF0ZVxuICAgIGlmIChzdGF0ZS5pblN0cmluZykge1xuICAgICAgd2hpbGUgKHN0YXRlLmluU3RyaW5nKSB7XG4gICAgICAgIGlmIChzdHJlYW0ubWF0Y2goc3RhdGUuc3RyaW5nVHlwZSkpIHtcbiAgICAgICAgICBzdGF0ZS5pblN0cmluZyA9IGZhbHNlOyAvLyBDbGVhciBmbGFnXG4gICAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLnBlZWsoKSA9PT0gJ1xcXFwnKSB7XG4gICAgICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgICB9IGVsc2UgaWYgKHN0cmVhbS5lb2woKSkge1xuICAgICAgICAgIGJyZWFrO1xuICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgIHN0cmVhbS5tYXRjaCgvXi5bXlxcXFxcXFwiXFwnXSovKTtcbiAgICAgICAgfVxuICAgICAgfVxuICAgICAgcmV0dXJuIHN0YXRlLmxocyA/IFwicHJvcGVydHlcIiA6IFwic3RyaW5nXCI7IC8vIFRva2VuIHN0eWxlXG4gICAgfSBlbHNlIGlmIChzdGF0ZS5pbkFycmF5ICYmIHN0cmVhbS5wZWVrKCkgPT09ICddJykge1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIHN0YXRlLmluQXJyYXktLTtcbiAgICAgIHJldHVybiAnYnJhY2tldCc7XG4gICAgfSBlbHNlIGlmIChzdGF0ZS5saHMgJiYgc3RyZWFtLnBlZWsoKSA9PT0gJ1snICYmIHN0cmVhbS5za2lwVG8oJ10nKSkge1xuICAgICAgc3RyZWFtLm5leHQoKTsgLy9za2lwIGNsb3NpbmcgXVxuICAgICAgLy8gYXJyYXkgb2Ygb2JqZWN0cyBoYXMgYW4gZXh0cmEgb3BlbiAmIGNsb3NlIFtdXG4gICAgICBpZiAoc3RyZWFtLnBlZWsoKSA9PT0gJ10nKSBzdHJlYW0ubmV4dCgpO1xuICAgICAgcmV0dXJuIFwiYXRvbVwiO1xuICAgIH0gZWxzZSBpZiAoc3RyZWFtLnBlZWsoKSA9PT0gXCIjXCIpIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICB9IGVsc2UgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSB7XG4gICAgICByZXR1cm4gbnVsbDtcbiAgICB9IGVsc2UgaWYgKHN0YXRlLmxocyAmJiBzdHJlYW0uZWF0V2hpbGUoZnVuY3Rpb24gKGMpIHtcbiAgICAgIHJldHVybiBjICE9ICc9JyAmJiBjICE9ICcgJztcbiAgICB9KSkge1xuICAgICAgcmV0dXJuIFwicHJvcGVydHlcIjtcbiAgICB9IGVsc2UgaWYgKHN0YXRlLmxocyAmJiBzdHJlYW0ucGVlaygpID09PSBcIj1cIikge1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIHN0YXRlLmxocyA9IGZhbHNlO1xuICAgICAgcmV0dXJuIG51bGw7XG4gICAgfSBlbHNlIGlmICghc3RhdGUubGhzICYmIHN0cmVhbS5tYXRjaCgvXlxcZFxcZFxcZFxcZFtcXGRcXC1cXDpcXC5UXSpaLykpIHtcbiAgICAgIHJldHVybiAnYXRvbSc7IC8vZGF0ZVxuICAgIH0gZWxzZSBpZiAoIXN0YXRlLmxocyAmJiAoc3RyZWFtLm1hdGNoKCd0cnVlJykgfHwgc3RyZWFtLm1hdGNoKCdmYWxzZScpKSkge1xuICAgICAgcmV0dXJuICdhdG9tJztcbiAgICB9IGVsc2UgaWYgKCFzdGF0ZS5saHMgJiYgc3RyZWFtLnBlZWsoKSA9PT0gJ1snKSB7XG4gICAgICBzdGF0ZS5pbkFycmF5Kys7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgcmV0dXJuICdicmFja2V0JztcbiAgICB9IGVsc2UgaWYgKCFzdGF0ZS5saHMgJiYgc3RyZWFtLm1hdGNoKC9eXFwtP1xcZCsoPzpcXC5cXGQrKT8vKSkge1xuICAgICAgcmV0dXJuICdudW1iZXInO1xuICAgIH0gZWxzZSBpZiAoIXN0cmVhbS5lYXRTcGFjZSgpKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgIH1cbiAgICByZXR1cm4gbnVsbDtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgbGluZTogJyMnXG4gICAgfVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=