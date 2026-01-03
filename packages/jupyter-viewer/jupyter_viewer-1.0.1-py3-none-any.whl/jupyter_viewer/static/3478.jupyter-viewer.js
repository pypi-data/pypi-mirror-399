"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[3478],{

/***/ 73478
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   elm: () => (/* binding */ elm)
/* harmony export */ });
function switchState(source, setState, f) {
  setState(f);
  return f(source, setState);
}
var lowerRE = /[a-z]/;
var upperRE = /[A-Z]/;
var innerRE = /[a-zA-Z0-9_]/;
var digitRE = /[0-9]/;
var hexRE = /[0-9A-Fa-f]/;
var symbolRE = /[-&*+.\\/<>=?^|:]/;
var specialRE = /[(),[\]{}]/;
var spacesRE = /[ \v\f]/; // newlines are handled in tokenizer

function normal() {
  return function (source, setState) {
    if (source.eatWhile(spacesRE)) {
      return null;
    }
    var char = source.next();
    if (specialRE.test(char)) {
      return char === '{' && source.eat('-') ? switchState(source, setState, chompMultiComment(1)) : char === '[' && source.match('glsl|') ? switchState(source, setState, chompGlsl) : 'builtin';
    }
    if (char === '\'') {
      return switchState(source, setState, chompChar);
    }
    if (char === '"') {
      return source.eat('"') ? source.eat('"') ? switchState(source, setState, chompMultiString) : 'string' : switchState(source, setState, chompSingleString);
    }
    if (upperRE.test(char)) {
      source.eatWhile(innerRE);
      return 'type';
    }
    if (lowerRE.test(char)) {
      var isDef = source.pos === 1;
      source.eatWhile(innerRE);
      return isDef ? "def" : "variable";
    }
    if (digitRE.test(char)) {
      if (char === '0') {
        if (source.eat(/[xX]/)) {
          source.eatWhile(hexRE); // should require at least 1
          return "number";
        }
      } else {
        source.eatWhile(digitRE);
      }
      if (source.eat('.')) {
        source.eatWhile(digitRE); // should require at least 1
      }
      if (source.eat(/[eE]/)) {
        source.eat(/[-+]/);
        source.eatWhile(digitRE); // should require at least 1
      }
      return "number";
    }
    if (symbolRE.test(char)) {
      if (char === '-' && source.eat('-')) {
        source.skipToEnd();
        return "comment";
      }
      source.eatWhile(symbolRE);
      return "keyword";
    }
    if (char === '_') {
      return "keyword";
    }
    return "error";
  };
}
function chompMultiComment(nest) {
  if (nest == 0) {
    return normal();
  }
  return function (source, setState) {
    while (!source.eol()) {
      var char = source.next();
      if (char == '{' && source.eat('-')) {
        ++nest;
      } else if (char == '-' && source.eat('}')) {
        --nest;
        if (nest === 0) {
          setState(normal());
          return 'comment';
        }
      }
    }
    setState(chompMultiComment(nest));
    return 'comment';
  };
}
function chompMultiString(source, setState) {
  while (!source.eol()) {
    var char = source.next();
    if (char === '"' && source.eat('"') && source.eat('"')) {
      setState(normal());
      return 'string';
    }
  }
  return 'string';
}
function chompSingleString(source, setState) {
  while (source.skipTo('\\"')) {
    source.next();
    source.next();
  }
  if (source.skipTo('"')) {
    source.next();
    setState(normal());
    return 'string';
  }
  source.skipToEnd();
  setState(normal());
  return 'error';
}
function chompChar(source, setState) {
  while (source.skipTo("\\'")) {
    source.next();
    source.next();
  }
  if (source.skipTo("'")) {
    source.next();
    setState(normal());
    return 'string';
  }
  source.skipToEnd();
  setState(normal());
  return 'error';
}
function chompGlsl(source, setState) {
  while (!source.eol()) {
    var char = source.next();
    if (char === '|' && source.eat(']')) {
      setState(normal());
      return 'string';
    }
  }
  return 'string';
}
var wellKnownWords = {
  case: 1,
  of: 1,
  as: 1,
  if: 1,
  then: 1,
  else: 1,
  let: 1,
  in: 1,
  type: 1,
  alias: 1,
  module: 1,
  where: 1,
  import: 1,
  exposing: 1,
  port: 1
};
const elm = {
  name: "elm",
  startState: function () {
    return {
      f: normal()
    };
  },
  copyState: function (s) {
    return {
      f: s.f
    };
  },
  token: function (stream, state) {
    var type = state.f(stream, function (s) {
      state.f = s;
    });
    var word = stream.current();
    return wellKnownWords.hasOwnProperty(word) ? 'keyword' : type;
  },
  languageData: {
    commentTokens: {
      line: "--"
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMzQ3OC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL2VsbS5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiBzd2l0Y2hTdGF0ZShzb3VyY2UsIHNldFN0YXRlLCBmKSB7XG4gIHNldFN0YXRlKGYpO1xuICByZXR1cm4gZihzb3VyY2UsIHNldFN0YXRlKTtcbn1cbnZhciBsb3dlclJFID0gL1thLXpdLztcbnZhciB1cHBlclJFID0gL1tBLVpdLztcbnZhciBpbm5lclJFID0gL1thLXpBLVowLTlfXS87XG52YXIgZGlnaXRSRSA9IC9bMC05XS87XG52YXIgaGV4UkUgPSAvWzAtOUEtRmEtZl0vO1xudmFyIHN5bWJvbFJFID0gL1stJiorLlxcXFwvPD49P158Ol0vO1xudmFyIHNwZWNpYWxSRSA9IC9bKCksW1xcXXt9XS87XG52YXIgc3BhY2VzUkUgPSAvWyBcXHZcXGZdLzsgLy8gbmV3bGluZXMgYXJlIGhhbmRsZWQgaW4gdG9rZW5pemVyXG5cbmZ1bmN0aW9uIG5vcm1hbCgpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzb3VyY2UsIHNldFN0YXRlKSB7XG4gICAgaWYgKHNvdXJjZS5lYXRXaGlsZShzcGFjZXNSRSkpIHtcbiAgICAgIHJldHVybiBudWxsO1xuICAgIH1cbiAgICB2YXIgY2hhciA9IHNvdXJjZS5uZXh0KCk7XG4gICAgaWYgKHNwZWNpYWxSRS50ZXN0KGNoYXIpKSB7XG4gICAgICByZXR1cm4gY2hhciA9PT0gJ3snICYmIHNvdXJjZS5lYXQoJy0nKSA/IHN3aXRjaFN0YXRlKHNvdXJjZSwgc2V0U3RhdGUsIGNob21wTXVsdGlDb21tZW50KDEpKSA6IGNoYXIgPT09ICdbJyAmJiBzb3VyY2UubWF0Y2goJ2dsc2x8JykgPyBzd2l0Y2hTdGF0ZShzb3VyY2UsIHNldFN0YXRlLCBjaG9tcEdsc2wpIDogJ2J1aWx0aW4nO1xuICAgIH1cbiAgICBpZiAoY2hhciA9PT0gJ1xcJycpIHtcbiAgICAgIHJldHVybiBzd2l0Y2hTdGF0ZShzb3VyY2UsIHNldFN0YXRlLCBjaG9tcENoYXIpO1xuICAgIH1cbiAgICBpZiAoY2hhciA9PT0gJ1wiJykge1xuICAgICAgcmV0dXJuIHNvdXJjZS5lYXQoJ1wiJykgPyBzb3VyY2UuZWF0KCdcIicpID8gc3dpdGNoU3RhdGUoc291cmNlLCBzZXRTdGF0ZSwgY2hvbXBNdWx0aVN0cmluZykgOiAnc3RyaW5nJyA6IHN3aXRjaFN0YXRlKHNvdXJjZSwgc2V0U3RhdGUsIGNob21wU2luZ2xlU3RyaW5nKTtcbiAgICB9XG4gICAgaWYgKHVwcGVyUkUudGVzdChjaGFyKSkge1xuICAgICAgc291cmNlLmVhdFdoaWxlKGlubmVyUkUpO1xuICAgICAgcmV0dXJuICd0eXBlJztcbiAgICB9XG4gICAgaWYgKGxvd2VyUkUudGVzdChjaGFyKSkge1xuICAgICAgdmFyIGlzRGVmID0gc291cmNlLnBvcyA9PT0gMTtcbiAgICAgIHNvdXJjZS5lYXRXaGlsZShpbm5lclJFKTtcbiAgICAgIHJldHVybiBpc0RlZiA/IFwiZGVmXCIgOiBcInZhcmlhYmxlXCI7XG4gICAgfVxuICAgIGlmIChkaWdpdFJFLnRlc3QoY2hhcikpIHtcbiAgICAgIGlmIChjaGFyID09PSAnMCcpIHtcbiAgICAgICAgaWYgKHNvdXJjZS5lYXQoL1t4WF0vKSkge1xuICAgICAgICAgIHNvdXJjZS5lYXRXaGlsZShoZXhSRSk7IC8vIHNob3VsZCByZXF1aXJlIGF0IGxlYXN0IDFcbiAgICAgICAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgICAgICAgfVxuICAgICAgfSBlbHNlIHtcbiAgICAgICAgc291cmNlLmVhdFdoaWxlKGRpZ2l0UkUpO1xuICAgICAgfVxuICAgICAgaWYgKHNvdXJjZS5lYXQoJy4nKSkge1xuICAgICAgICBzb3VyY2UuZWF0V2hpbGUoZGlnaXRSRSk7IC8vIHNob3VsZCByZXF1aXJlIGF0IGxlYXN0IDFcbiAgICAgIH1cbiAgICAgIGlmIChzb3VyY2UuZWF0KC9bZUVdLykpIHtcbiAgICAgICAgc291cmNlLmVhdCgvWy0rXS8pO1xuICAgICAgICBzb3VyY2UuZWF0V2hpbGUoZGlnaXRSRSk7IC8vIHNob3VsZCByZXF1aXJlIGF0IGxlYXN0IDFcbiAgICAgIH1cbiAgICAgIHJldHVybiBcIm51bWJlclwiO1xuICAgIH1cbiAgICBpZiAoc3ltYm9sUkUudGVzdChjaGFyKSkge1xuICAgICAgaWYgKGNoYXIgPT09ICctJyAmJiBzb3VyY2UuZWF0KCctJykpIHtcbiAgICAgICAgc291cmNlLnNraXBUb0VuZCgpO1xuICAgICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgICB9XG4gICAgICBzb3VyY2UuZWF0V2hpbGUoc3ltYm9sUkUpO1xuICAgICAgcmV0dXJuIFwia2V5d29yZFwiO1xuICAgIH1cbiAgICBpZiAoY2hhciA9PT0gJ18nKSB7XG4gICAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gICAgfVxuICAgIHJldHVybiBcImVycm9yXCI7XG4gIH07XG59XG5mdW5jdGlvbiBjaG9tcE11bHRpQ29tbWVudChuZXN0KSB7XG4gIGlmIChuZXN0ID09IDApIHtcbiAgICByZXR1cm4gbm9ybWFsKCk7XG4gIH1cbiAgcmV0dXJuIGZ1bmN0aW9uIChzb3VyY2UsIHNldFN0YXRlKSB7XG4gICAgd2hpbGUgKCFzb3VyY2UuZW9sKCkpIHtcbiAgICAgIHZhciBjaGFyID0gc291cmNlLm5leHQoKTtcbiAgICAgIGlmIChjaGFyID09ICd7JyAmJiBzb3VyY2UuZWF0KCctJykpIHtcbiAgICAgICAgKytuZXN0O1xuICAgICAgfSBlbHNlIGlmIChjaGFyID09ICctJyAmJiBzb3VyY2UuZWF0KCd9JykpIHtcbiAgICAgICAgLS1uZXN0O1xuICAgICAgICBpZiAobmVzdCA9PT0gMCkge1xuICAgICAgICAgIHNldFN0YXRlKG5vcm1hbCgpKTtcbiAgICAgICAgICByZXR1cm4gJ2NvbW1lbnQnO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgfVxuICAgIHNldFN0YXRlKGNob21wTXVsdGlDb21tZW50KG5lc3QpKTtcbiAgICByZXR1cm4gJ2NvbW1lbnQnO1xuICB9O1xufVxuZnVuY3Rpb24gY2hvbXBNdWx0aVN0cmluZyhzb3VyY2UsIHNldFN0YXRlKSB7XG4gIHdoaWxlICghc291cmNlLmVvbCgpKSB7XG4gICAgdmFyIGNoYXIgPSBzb3VyY2UubmV4dCgpO1xuICAgIGlmIChjaGFyID09PSAnXCInICYmIHNvdXJjZS5lYXQoJ1wiJykgJiYgc291cmNlLmVhdCgnXCInKSkge1xuICAgICAgc2V0U3RhdGUobm9ybWFsKCkpO1xuICAgICAgcmV0dXJuICdzdHJpbmcnO1xuICAgIH1cbiAgfVxuICByZXR1cm4gJ3N0cmluZyc7XG59XG5mdW5jdGlvbiBjaG9tcFNpbmdsZVN0cmluZyhzb3VyY2UsIHNldFN0YXRlKSB7XG4gIHdoaWxlIChzb3VyY2Uuc2tpcFRvKCdcXFxcXCInKSkge1xuICAgIHNvdXJjZS5uZXh0KCk7XG4gICAgc291cmNlLm5leHQoKTtcbiAgfVxuICBpZiAoc291cmNlLnNraXBUbygnXCInKSkge1xuICAgIHNvdXJjZS5uZXh0KCk7XG4gICAgc2V0U3RhdGUobm9ybWFsKCkpO1xuICAgIHJldHVybiAnc3RyaW5nJztcbiAgfVxuICBzb3VyY2Uuc2tpcFRvRW5kKCk7XG4gIHNldFN0YXRlKG5vcm1hbCgpKTtcbiAgcmV0dXJuICdlcnJvcic7XG59XG5mdW5jdGlvbiBjaG9tcENoYXIoc291cmNlLCBzZXRTdGF0ZSkge1xuICB3aGlsZSAoc291cmNlLnNraXBUbyhcIlxcXFwnXCIpKSB7XG4gICAgc291cmNlLm5leHQoKTtcbiAgICBzb3VyY2UubmV4dCgpO1xuICB9XG4gIGlmIChzb3VyY2Uuc2tpcFRvKFwiJ1wiKSkge1xuICAgIHNvdXJjZS5uZXh0KCk7XG4gICAgc2V0U3RhdGUobm9ybWFsKCkpO1xuICAgIHJldHVybiAnc3RyaW5nJztcbiAgfVxuICBzb3VyY2Uuc2tpcFRvRW5kKCk7XG4gIHNldFN0YXRlKG5vcm1hbCgpKTtcbiAgcmV0dXJuICdlcnJvcic7XG59XG5mdW5jdGlvbiBjaG9tcEdsc2woc291cmNlLCBzZXRTdGF0ZSkge1xuICB3aGlsZSAoIXNvdXJjZS5lb2woKSkge1xuICAgIHZhciBjaGFyID0gc291cmNlLm5leHQoKTtcbiAgICBpZiAoY2hhciA9PT0gJ3wnICYmIHNvdXJjZS5lYXQoJ10nKSkge1xuICAgICAgc2V0U3RhdGUobm9ybWFsKCkpO1xuICAgICAgcmV0dXJuICdzdHJpbmcnO1xuICAgIH1cbiAgfVxuICByZXR1cm4gJ3N0cmluZyc7XG59XG52YXIgd2VsbEtub3duV29yZHMgPSB7XG4gIGNhc2U6IDEsXG4gIG9mOiAxLFxuICBhczogMSxcbiAgaWY6IDEsXG4gIHRoZW46IDEsXG4gIGVsc2U6IDEsXG4gIGxldDogMSxcbiAgaW46IDEsXG4gIHR5cGU6IDEsXG4gIGFsaWFzOiAxLFxuICBtb2R1bGU6IDEsXG4gIHdoZXJlOiAxLFxuICBpbXBvcnQ6IDEsXG4gIGV4cG9zaW5nOiAxLFxuICBwb3J0OiAxXG59O1xuZXhwb3J0IGNvbnN0IGVsbSA9IHtcbiAgbmFtZTogXCJlbG1cIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB7XG4gICAgICBmOiBub3JtYWwoKVxuICAgIH07XG4gIH0sXG4gIGNvcHlTdGF0ZTogZnVuY3Rpb24gKHMpIHtcbiAgICByZXR1cm4ge1xuICAgICAgZjogcy5mXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIHR5cGUgPSBzdGF0ZS5mKHN0cmVhbSwgZnVuY3Rpb24gKHMpIHtcbiAgICAgIHN0YXRlLmYgPSBzO1xuICAgIH0pO1xuICAgIHZhciB3b3JkID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgICByZXR1cm4gd2VsbEtub3duV29yZHMuaGFzT3duUHJvcGVydHkod29yZCkgPyAna2V5d29yZCcgOiB0eXBlO1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBjb21tZW50VG9rZW5zOiB7XG4gICAgICBsaW5lOiBcIi0tXCJcbiAgICB9XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==