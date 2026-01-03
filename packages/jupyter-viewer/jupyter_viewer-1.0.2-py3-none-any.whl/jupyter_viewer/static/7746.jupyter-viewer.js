"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[7746],{

/***/ 47746
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   haskell: () => (/* binding */ haskell)
/* harmony export */ });
function switchState(source, setState, f) {
  setState(f);
  return f(source, setState);
}

// These should all be Unicode extended, as per the Haskell 2010 report
var smallRE = /[a-z_]/;
var largeRE = /[A-Z]/;
var digitRE = /\d/;
var hexitRE = /[0-9A-Fa-f]/;
var octitRE = /[0-7]/;
var idRE = /[a-z_A-Z0-9'\xa1-\uffff]/;
var symbolRE = /[-!#$%&*+.\/<=>?@\\^|~:]/;
var specialRE = /[(),;[\]`{}]/;
var whiteCharRE = /[ \t\v\f]/; // newlines are handled in tokenizer

function normal(source, setState) {
  if (source.eatWhile(whiteCharRE)) {
    return null;
  }
  var ch = source.next();
  if (specialRE.test(ch)) {
    if (ch == '{' && source.eat('-')) {
      var t = "comment";
      if (source.eat('#')) {
        t = "meta";
      }
      return switchState(source, setState, ncomment(t, 1));
    }
    return null;
  }
  if (ch == '\'') {
    if (source.eat('\\')) {
      source.next(); // should handle other escapes here
    } else {
      source.next();
    }
    if (source.eat('\'')) {
      return "string";
    }
    return "error";
  }
  if (ch == '"') {
    return switchState(source, setState, stringLiteral);
  }
  if (largeRE.test(ch)) {
    source.eatWhile(idRE);
    if (source.eat('.')) {
      return "qualifier";
    }
    return "type";
  }
  if (smallRE.test(ch)) {
    source.eatWhile(idRE);
    return "variable";
  }
  if (digitRE.test(ch)) {
    if (ch == '0') {
      if (source.eat(/[xX]/)) {
        source.eatWhile(hexitRE); // should require at least 1
        return "integer";
      }
      if (source.eat(/[oO]/)) {
        source.eatWhile(octitRE); // should require at least 1
        return "number";
      }
    }
    source.eatWhile(digitRE);
    var t = "number";
    if (source.match(/^\.\d+/)) {
      t = "number";
    }
    if (source.eat(/[eE]/)) {
      t = "number";
      source.eat(/[-+]/);
      source.eatWhile(digitRE); // should require at least 1
    }
    return t;
  }
  if (ch == "." && source.eat(".")) return "keyword";
  if (symbolRE.test(ch)) {
    if (ch == '-' && source.eat(/-/)) {
      source.eatWhile(/-/);
      if (!source.eat(symbolRE)) {
        source.skipToEnd();
        return "comment";
      }
    }
    source.eatWhile(symbolRE);
    return "variable";
  }
  return "error";
}
function ncomment(type, nest) {
  if (nest == 0) {
    return normal;
  }
  return function (source, setState) {
    var currNest = nest;
    while (!source.eol()) {
      var ch = source.next();
      if (ch == '{' && source.eat('-')) {
        ++currNest;
      } else if (ch == '-' && source.eat('}')) {
        --currNest;
        if (currNest == 0) {
          setState(normal);
          return type;
        }
      }
    }
    setState(ncomment(type, currNest));
    return type;
  };
}
function stringLiteral(source, setState) {
  while (!source.eol()) {
    var ch = source.next();
    if (ch == '"') {
      setState(normal);
      return "string";
    }
    if (ch == '\\') {
      if (source.eol() || source.eat(whiteCharRE)) {
        setState(stringGap);
        return "string";
      }
      if (source.eat('&')) {} else {
        source.next(); // should handle other escapes here
      }
    }
  }
  setState(normal);
  return "error";
}
function stringGap(source, setState) {
  if (source.eat('\\')) {
    return switchState(source, setState, stringLiteral);
  }
  source.next();
  setState(normal);
  return "error";
}
var wellKnownWords = function () {
  var wkw = {};
  function setType(t) {
    return function () {
      for (var i = 0; i < arguments.length; i++) wkw[arguments[i]] = t;
    };
  }
  setType("keyword")("case", "class", "data", "default", "deriving", "do", "else", "foreign", "if", "import", "in", "infix", "infixl", "infixr", "instance", "let", "module", "newtype", "of", "then", "type", "where", "_");
  setType("keyword")("\.\.", ":", "::", "=", "\\", "<-", "->", "@", "~", "=>");
  setType("builtin")("!!", "$!", "$", "&&", "+", "++", "-", ".", "/", "/=", "<", "<*", "<=", "<$>", "<*>", "=<<", "==", ">", ">=", ">>", ">>=", "^", "^^", "||", "*", "*>", "**");
  setType("builtin")("Applicative", "Bool", "Bounded", "Char", "Double", "EQ", "Either", "Enum", "Eq", "False", "FilePath", "Float", "Floating", "Fractional", "Functor", "GT", "IO", "IOError", "Int", "Integer", "Integral", "Just", "LT", "Left", "Maybe", "Monad", "Nothing", "Num", "Ord", "Ordering", "Rational", "Read", "ReadS", "Real", "RealFloat", "RealFrac", "Right", "Show", "ShowS", "String", "True");
  setType("builtin")("abs", "acos", "acosh", "all", "and", "any", "appendFile", "asTypeOf", "asin", "asinh", "atan", "atan2", "atanh", "break", "catch", "ceiling", "compare", "concat", "concatMap", "const", "cos", "cosh", "curry", "cycle", "decodeFloat", "div", "divMod", "drop", "dropWhile", "either", "elem", "encodeFloat", "enumFrom", "enumFromThen", "enumFromThenTo", "enumFromTo", "error", "even", "exp", "exponent", "fail", "filter", "flip", "floatDigits", "floatRadix", "floatRange", "floor", "fmap", "foldl", "foldl1", "foldr", "foldr1", "fromEnum", "fromInteger", "fromIntegral", "fromRational", "fst", "gcd", "getChar", "getContents", "getLine", "head", "id", "init", "interact", "ioError", "isDenormalized", "isIEEE", "isInfinite", "isNaN", "isNegativeZero", "iterate", "last", "lcm", "length", "lex", "lines", "log", "logBase", "lookup", "map", "mapM", "mapM_", "max", "maxBound", "maximum", "maybe", "min", "minBound", "minimum", "mod", "negate", "not", "notElem", "null", "odd", "or", "otherwise", "pi", "pred", "print", "product", "properFraction", "pure", "putChar", "putStr", "putStrLn", "quot", "quotRem", "read", "readFile", "readIO", "readList", "readLn", "readParen", "reads", "readsPrec", "realToFrac", "recip", "rem", "repeat", "replicate", "return", "reverse", "round", "scaleFloat", "scanl", "scanl1", "scanr", "scanr1", "seq", "sequence", "sequence_", "show", "showChar", "showList", "showParen", "showString", "shows", "showsPrec", "significand", "signum", "sin", "sinh", "snd", "span", "splitAt", "sqrt", "subtract", "succ", "sum", "tail", "take", "takeWhile", "tan", "tanh", "toEnum", "toInteger", "toRational", "truncate", "uncurry", "undefined", "unlines", "until", "unwords", "unzip", "unzip3", "userError", "words", "writeFile", "zip", "zip3", "zipWith", "zipWith3");
  return wkw;
}();
const haskell = {
  name: "haskell",
  startState: function () {
    return {
      f: normal
    };
  },
  copyState: function (s) {
    return {
      f: s.f
    };
  },
  token: function (stream, state) {
    var t = state.f(stream, function (s) {
      state.f = s;
    });
    var w = stream.current();
    return wellKnownWords.hasOwnProperty(w) ? wellKnownWords[w] : t;
  },
  languageData: {
    commentTokens: {
      line: "--",
      block: {
        open: "{-",
        close: "-}"
      }
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNzc0Ni5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL2hhc2tlbGwuanMiXSwic291cmNlc0NvbnRlbnQiOlsiZnVuY3Rpb24gc3dpdGNoU3RhdGUoc291cmNlLCBzZXRTdGF0ZSwgZikge1xuICBzZXRTdGF0ZShmKTtcbiAgcmV0dXJuIGYoc291cmNlLCBzZXRTdGF0ZSk7XG59XG5cbi8vIFRoZXNlIHNob3VsZCBhbGwgYmUgVW5pY29kZSBleHRlbmRlZCwgYXMgcGVyIHRoZSBIYXNrZWxsIDIwMTAgcmVwb3J0XG52YXIgc21hbGxSRSA9IC9bYS16X10vO1xudmFyIGxhcmdlUkUgPSAvW0EtWl0vO1xudmFyIGRpZ2l0UkUgPSAvXFxkLztcbnZhciBoZXhpdFJFID0gL1swLTlBLUZhLWZdLztcbnZhciBvY3RpdFJFID0gL1swLTddLztcbnZhciBpZFJFID0gL1thLXpfQS1aMC05J1xceGExLVxcdWZmZmZdLztcbnZhciBzeW1ib2xSRSA9IC9bLSEjJCUmKisuXFwvPD0+P0BcXFxcXnx+Ol0vO1xudmFyIHNwZWNpYWxSRSA9IC9bKCksO1tcXF1ge31dLztcbnZhciB3aGl0ZUNoYXJSRSA9IC9bIFxcdFxcdlxcZl0vOyAvLyBuZXdsaW5lcyBhcmUgaGFuZGxlZCBpbiB0b2tlbml6ZXJcblxuZnVuY3Rpb24gbm9ybWFsKHNvdXJjZSwgc2V0U3RhdGUpIHtcbiAgaWYgKHNvdXJjZS5lYXRXaGlsZSh3aGl0ZUNoYXJSRSkpIHtcbiAgICByZXR1cm4gbnVsbDtcbiAgfVxuICB2YXIgY2ggPSBzb3VyY2UubmV4dCgpO1xuICBpZiAoc3BlY2lhbFJFLnRlc3QoY2gpKSB7XG4gICAgaWYgKGNoID09ICd7JyAmJiBzb3VyY2UuZWF0KCctJykpIHtcbiAgICAgIHZhciB0ID0gXCJjb21tZW50XCI7XG4gICAgICBpZiAoc291cmNlLmVhdCgnIycpKSB7XG4gICAgICAgIHQgPSBcIm1ldGFcIjtcbiAgICAgIH1cbiAgICAgIHJldHVybiBzd2l0Y2hTdGF0ZShzb3VyY2UsIHNldFN0YXRlLCBuY29tbWVudCh0LCAxKSk7XG4gICAgfVxuICAgIHJldHVybiBudWxsO1xuICB9XG4gIGlmIChjaCA9PSAnXFwnJykge1xuICAgIGlmIChzb3VyY2UuZWF0KCdcXFxcJykpIHtcbiAgICAgIHNvdXJjZS5uZXh0KCk7IC8vIHNob3VsZCBoYW5kbGUgb3RoZXIgZXNjYXBlcyBoZXJlXG4gICAgfSBlbHNlIHtcbiAgICAgIHNvdXJjZS5uZXh0KCk7XG4gICAgfVxuICAgIGlmIChzb3VyY2UuZWF0KCdcXCcnKSkge1xuICAgICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gICAgfVxuICAgIHJldHVybiBcImVycm9yXCI7XG4gIH1cbiAgaWYgKGNoID09ICdcIicpIHtcbiAgICByZXR1cm4gc3dpdGNoU3RhdGUoc291cmNlLCBzZXRTdGF0ZSwgc3RyaW5nTGl0ZXJhbCk7XG4gIH1cbiAgaWYgKGxhcmdlUkUudGVzdChjaCkpIHtcbiAgICBzb3VyY2UuZWF0V2hpbGUoaWRSRSk7XG4gICAgaWYgKHNvdXJjZS5lYXQoJy4nKSkge1xuICAgICAgcmV0dXJuIFwicXVhbGlmaWVyXCI7XG4gICAgfVxuICAgIHJldHVybiBcInR5cGVcIjtcbiAgfVxuICBpZiAoc21hbGxSRS50ZXN0KGNoKSkge1xuICAgIHNvdXJjZS5lYXRXaGlsZShpZFJFKTtcbiAgICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xuICB9XG4gIGlmIChkaWdpdFJFLnRlc3QoY2gpKSB7XG4gICAgaWYgKGNoID09ICcwJykge1xuICAgICAgaWYgKHNvdXJjZS5lYXQoL1t4WF0vKSkge1xuICAgICAgICBzb3VyY2UuZWF0V2hpbGUoaGV4aXRSRSk7IC8vIHNob3VsZCByZXF1aXJlIGF0IGxlYXN0IDFcbiAgICAgICAgcmV0dXJuIFwiaW50ZWdlclwiO1xuICAgICAgfVxuICAgICAgaWYgKHNvdXJjZS5lYXQoL1tvT10vKSkge1xuICAgICAgICBzb3VyY2UuZWF0V2hpbGUob2N0aXRSRSk7IC8vIHNob3VsZCByZXF1aXJlIGF0IGxlYXN0IDFcbiAgICAgICAgcmV0dXJuIFwibnVtYmVyXCI7XG4gICAgICB9XG4gICAgfVxuICAgIHNvdXJjZS5lYXRXaGlsZShkaWdpdFJFKTtcbiAgICB2YXIgdCA9IFwibnVtYmVyXCI7XG4gICAgaWYgKHNvdXJjZS5tYXRjaCgvXlxcLlxcZCsvKSkge1xuICAgICAgdCA9IFwibnVtYmVyXCI7XG4gICAgfVxuICAgIGlmIChzb3VyY2UuZWF0KC9bZUVdLykpIHtcbiAgICAgIHQgPSBcIm51bWJlclwiO1xuICAgICAgc291cmNlLmVhdCgvWy0rXS8pO1xuICAgICAgc291cmNlLmVhdFdoaWxlKGRpZ2l0UkUpOyAvLyBzaG91bGQgcmVxdWlyZSBhdCBsZWFzdCAxXG4gICAgfVxuICAgIHJldHVybiB0O1xuICB9XG4gIGlmIChjaCA9PSBcIi5cIiAmJiBzb3VyY2UuZWF0KFwiLlwiKSkgcmV0dXJuIFwia2V5d29yZFwiO1xuICBpZiAoc3ltYm9sUkUudGVzdChjaCkpIHtcbiAgICBpZiAoY2ggPT0gJy0nICYmIHNvdXJjZS5lYXQoLy0vKSkge1xuICAgICAgc291cmNlLmVhdFdoaWxlKC8tLyk7XG4gICAgICBpZiAoIXNvdXJjZS5lYXQoc3ltYm9sUkUpKSB7XG4gICAgICAgIHNvdXJjZS5za2lwVG9FbmQoKTtcbiAgICAgICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICAgICAgfVxuICAgIH1cbiAgICBzb3VyY2UuZWF0V2hpbGUoc3ltYm9sUkUpO1xuICAgIHJldHVybiBcInZhcmlhYmxlXCI7XG4gIH1cbiAgcmV0dXJuIFwiZXJyb3JcIjtcbn1cbmZ1bmN0aW9uIG5jb21tZW50KHR5cGUsIG5lc3QpIHtcbiAgaWYgKG5lc3QgPT0gMCkge1xuICAgIHJldHVybiBub3JtYWw7XG4gIH1cbiAgcmV0dXJuIGZ1bmN0aW9uIChzb3VyY2UsIHNldFN0YXRlKSB7XG4gICAgdmFyIGN1cnJOZXN0ID0gbmVzdDtcbiAgICB3aGlsZSAoIXNvdXJjZS5lb2woKSkge1xuICAgICAgdmFyIGNoID0gc291cmNlLm5leHQoKTtcbiAgICAgIGlmIChjaCA9PSAneycgJiYgc291cmNlLmVhdCgnLScpKSB7XG4gICAgICAgICsrY3Vyck5lc3Q7XG4gICAgICB9IGVsc2UgaWYgKGNoID09ICctJyAmJiBzb3VyY2UuZWF0KCd9JykpIHtcbiAgICAgICAgLS1jdXJyTmVzdDtcbiAgICAgICAgaWYgKGN1cnJOZXN0ID09IDApIHtcbiAgICAgICAgICBzZXRTdGF0ZShub3JtYWwpO1xuICAgICAgICAgIHJldHVybiB0eXBlO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgfVxuICAgIHNldFN0YXRlKG5jb21tZW50KHR5cGUsIGN1cnJOZXN0KSk7XG4gICAgcmV0dXJuIHR5cGU7XG4gIH07XG59XG5mdW5jdGlvbiBzdHJpbmdMaXRlcmFsKHNvdXJjZSwgc2V0U3RhdGUpIHtcbiAgd2hpbGUgKCFzb3VyY2UuZW9sKCkpIHtcbiAgICB2YXIgY2ggPSBzb3VyY2UubmV4dCgpO1xuICAgIGlmIChjaCA9PSAnXCInKSB7XG4gICAgICBzZXRTdGF0ZShub3JtYWwpO1xuICAgICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gICAgfVxuICAgIGlmIChjaCA9PSAnXFxcXCcpIHtcbiAgICAgIGlmIChzb3VyY2UuZW9sKCkgfHwgc291cmNlLmVhdCh3aGl0ZUNoYXJSRSkpIHtcbiAgICAgICAgc2V0U3RhdGUoc3RyaW5nR2FwKTtcbiAgICAgICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gICAgICB9XG4gICAgICBpZiAoc291cmNlLmVhdCgnJicpKSB7fSBlbHNlIHtcbiAgICAgICAgc291cmNlLm5leHQoKTsgLy8gc2hvdWxkIGhhbmRsZSBvdGhlciBlc2NhcGVzIGhlcmVcbiAgICAgIH1cbiAgICB9XG4gIH1cbiAgc2V0U3RhdGUobm9ybWFsKTtcbiAgcmV0dXJuIFwiZXJyb3JcIjtcbn1cbmZ1bmN0aW9uIHN0cmluZ0dhcChzb3VyY2UsIHNldFN0YXRlKSB7XG4gIGlmIChzb3VyY2UuZWF0KCdcXFxcJykpIHtcbiAgICByZXR1cm4gc3dpdGNoU3RhdGUoc291cmNlLCBzZXRTdGF0ZSwgc3RyaW5nTGl0ZXJhbCk7XG4gIH1cbiAgc291cmNlLm5leHQoKTtcbiAgc2V0U3RhdGUobm9ybWFsKTtcbiAgcmV0dXJuIFwiZXJyb3JcIjtcbn1cbnZhciB3ZWxsS25vd25Xb3JkcyA9IGZ1bmN0aW9uICgpIHtcbiAgdmFyIHdrdyA9IHt9O1xuICBmdW5jdGlvbiBzZXRUeXBlKHQpIHtcbiAgICByZXR1cm4gZnVuY3Rpb24gKCkge1xuICAgICAgZm9yICh2YXIgaSA9IDA7IGkgPCBhcmd1bWVudHMubGVuZ3RoOyBpKyspIHdrd1thcmd1bWVudHNbaV1dID0gdDtcbiAgICB9O1xuICB9XG4gIHNldFR5cGUoXCJrZXl3b3JkXCIpKFwiY2FzZVwiLCBcImNsYXNzXCIsIFwiZGF0YVwiLCBcImRlZmF1bHRcIiwgXCJkZXJpdmluZ1wiLCBcImRvXCIsIFwiZWxzZVwiLCBcImZvcmVpZ25cIiwgXCJpZlwiLCBcImltcG9ydFwiLCBcImluXCIsIFwiaW5maXhcIiwgXCJpbmZpeGxcIiwgXCJpbmZpeHJcIiwgXCJpbnN0YW5jZVwiLCBcImxldFwiLCBcIm1vZHVsZVwiLCBcIm5ld3R5cGVcIiwgXCJvZlwiLCBcInRoZW5cIiwgXCJ0eXBlXCIsIFwid2hlcmVcIiwgXCJfXCIpO1xuICBzZXRUeXBlKFwia2V5d29yZFwiKShcIlxcLlxcLlwiLCBcIjpcIiwgXCI6OlwiLCBcIj1cIiwgXCJcXFxcXCIsIFwiPC1cIiwgXCItPlwiLCBcIkBcIiwgXCJ+XCIsIFwiPT5cIik7XG4gIHNldFR5cGUoXCJidWlsdGluXCIpKFwiISFcIiwgXCIkIVwiLCBcIiRcIiwgXCImJlwiLCBcIitcIiwgXCIrK1wiLCBcIi1cIiwgXCIuXCIsIFwiL1wiLCBcIi89XCIsIFwiPFwiLCBcIjwqXCIsIFwiPD1cIiwgXCI8JD5cIiwgXCI8Kj5cIiwgXCI9PDxcIiwgXCI9PVwiLCBcIj5cIiwgXCI+PVwiLCBcIj4+XCIsIFwiPj49XCIsIFwiXlwiLCBcIl5eXCIsIFwifHxcIiwgXCIqXCIsIFwiKj5cIiwgXCIqKlwiKTtcbiAgc2V0VHlwZShcImJ1aWx0aW5cIikoXCJBcHBsaWNhdGl2ZVwiLCBcIkJvb2xcIiwgXCJCb3VuZGVkXCIsIFwiQ2hhclwiLCBcIkRvdWJsZVwiLCBcIkVRXCIsIFwiRWl0aGVyXCIsIFwiRW51bVwiLCBcIkVxXCIsIFwiRmFsc2VcIiwgXCJGaWxlUGF0aFwiLCBcIkZsb2F0XCIsIFwiRmxvYXRpbmdcIiwgXCJGcmFjdGlvbmFsXCIsIFwiRnVuY3RvclwiLCBcIkdUXCIsIFwiSU9cIiwgXCJJT0Vycm9yXCIsIFwiSW50XCIsIFwiSW50ZWdlclwiLCBcIkludGVncmFsXCIsIFwiSnVzdFwiLCBcIkxUXCIsIFwiTGVmdFwiLCBcIk1heWJlXCIsIFwiTW9uYWRcIiwgXCJOb3RoaW5nXCIsIFwiTnVtXCIsIFwiT3JkXCIsIFwiT3JkZXJpbmdcIiwgXCJSYXRpb25hbFwiLCBcIlJlYWRcIiwgXCJSZWFkU1wiLCBcIlJlYWxcIiwgXCJSZWFsRmxvYXRcIiwgXCJSZWFsRnJhY1wiLCBcIlJpZ2h0XCIsIFwiU2hvd1wiLCBcIlNob3dTXCIsIFwiU3RyaW5nXCIsIFwiVHJ1ZVwiKTtcbiAgc2V0VHlwZShcImJ1aWx0aW5cIikoXCJhYnNcIiwgXCJhY29zXCIsIFwiYWNvc2hcIiwgXCJhbGxcIiwgXCJhbmRcIiwgXCJhbnlcIiwgXCJhcHBlbmRGaWxlXCIsIFwiYXNUeXBlT2ZcIiwgXCJhc2luXCIsIFwiYXNpbmhcIiwgXCJhdGFuXCIsIFwiYXRhbjJcIiwgXCJhdGFuaFwiLCBcImJyZWFrXCIsIFwiY2F0Y2hcIiwgXCJjZWlsaW5nXCIsIFwiY29tcGFyZVwiLCBcImNvbmNhdFwiLCBcImNvbmNhdE1hcFwiLCBcImNvbnN0XCIsIFwiY29zXCIsIFwiY29zaFwiLCBcImN1cnJ5XCIsIFwiY3ljbGVcIiwgXCJkZWNvZGVGbG9hdFwiLCBcImRpdlwiLCBcImRpdk1vZFwiLCBcImRyb3BcIiwgXCJkcm9wV2hpbGVcIiwgXCJlaXRoZXJcIiwgXCJlbGVtXCIsIFwiZW5jb2RlRmxvYXRcIiwgXCJlbnVtRnJvbVwiLCBcImVudW1Gcm9tVGhlblwiLCBcImVudW1Gcm9tVGhlblRvXCIsIFwiZW51bUZyb21Ub1wiLCBcImVycm9yXCIsIFwiZXZlblwiLCBcImV4cFwiLCBcImV4cG9uZW50XCIsIFwiZmFpbFwiLCBcImZpbHRlclwiLCBcImZsaXBcIiwgXCJmbG9hdERpZ2l0c1wiLCBcImZsb2F0UmFkaXhcIiwgXCJmbG9hdFJhbmdlXCIsIFwiZmxvb3JcIiwgXCJmbWFwXCIsIFwiZm9sZGxcIiwgXCJmb2xkbDFcIiwgXCJmb2xkclwiLCBcImZvbGRyMVwiLCBcImZyb21FbnVtXCIsIFwiZnJvbUludGVnZXJcIiwgXCJmcm9tSW50ZWdyYWxcIiwgXCJmcm9tUmF0aW9uYWxcIiwgXCJmc3RcIiwgXCJnY2RcIiwgXCJnZXRDaGFyXCIsIFwiZ2V0Q29udGVudHNcIiwgXCJnZXRMaW5lXCIsIFwiaGVhZFwiLCBcImlkXCIsIFwiaW5pdFwiLCBcImludGVyYWN0XCIsIFwiaW9FcnJvclwiLCBcImlzRGVub3JtYWxpemVkXCIsIFwiaXNJRUVFXCIsIFwiaXNJbmZpbml0ZVwiLCBcImlzTmFOXCIsIFwiaXNOZWdhdGl2ZVplcm9cIiwgXCJpdGVyYXRlXCIsIFwibGFzdFwiLCBcImxjbVwiLCBcImxlbmd0aFwiLCBcImxleFwiLCBcImxpbmVzXCIsIFwibG9nXCIsIFwibG9nQmFzZVwiLCBcImxvb2t1cFwiLCBcIm1hcFwiLCBcIm1hcE1cIiwgXCJtYXBNX1wiLCBcIm1heFwiLCBcIm1heEJvdW5kXCIsIFwibWF4aW11bVwiLCBcIm1heWJlXCIsIFwibWluXCIsIFwibWluQm91bmRcIiwgXCJtaW5pbXVtXCIsIFwibW9kXCIsIFwibmVnYXRlXCIsIFwibm90XCIsIFwibm90RWxlbVwiLCBcIm51bGxcIiwgXCJvZGRcIiwgXCJvclwiLCBcIm90aGVyd2lzZVwiLCBcInBpXCIsIFwicHJlZFwiLCBcInByaW50XCIsIFwicHJvZHVjdFwiLCBcInByb3BlckZyYWN0aW9uXCIsIFwicHVyZVwiLCBcInB1dENoYXJcIiwgXCJwdXRTdHJcIiwgXCJwdXRTdHJMblwiLCBcInF1b3RcIiwgXCJxdW90UmVtXCIsIFwicmVhZFwiLCBcInJlYWRGaWxlXCIsIFwicmVhZElPXCIsIFwicmVhZExpc3RcIiwgXCJyZWFkTG5cIiwgXCJyZWFkUGFyZW5cIiwgXCJyZWFkc1wiLCBcInJlYWRzUHJlY1wiLCBcInJlYWxUb0ZyYWNcIiwgXCJyZWNpcFwiLCBcInJlbVwiLCBcInJlcGVhdFwiLCBcInJlcGxpY2F0ZVwiLCBcInJldHVyblwiLCBcInJldmVyc2VcIiwgXCJyb3VuZFwiLCBcInNjYWxlRmxvYXRcIiwgXCJzY2FubFwiLCBcInNjYW5sMVwiLCBcInNjYW5yXCIsIFwic2NhbnIxXCIsIFwic2VxXCIsIFwic2VxdWVuY2VcIiwgXCJzZXF1ZW5jZV9cIiwgXCJzaG93XCIsIFwic2hvd0NoYXJcIiwgXCJzaG93TGlzdFwiLCBcInNob3dQYXJlblwiLCBcInNob3dTdHJpbmdcIiwgXCJzaG93c1wiLCBcInNob3dzUHJlY1wiLCBcInNpZ25pZmljYW5kXCIsIFwic2lnbnVtXCIsIFwic2luXCIsIFwic2luaFwiLCBcInNuZFwiLCBcInNwYW5cIiwgXCJzcGxpdEF0XCIsIFwic3FydFwiLCBcInN1YnRyYWN0XCIsIFwic3VjY1wiLCBcInN1bVwiLCBcInRhaWxcIiwgXCJ0YWtlXCIsIFwidGFrZVdoaWxlXCIsIFwidGFuXCIsIFwidGFuaFwiLCBcInRvRW51bVwiLCBcInRvSW50ZWdlclwiLCBcInRvUmF0aW9uYWxcIiwgXCJ0cnVuY2F0ZVwiLCBcInVuY3VycnlcIiwgXCJ1bmRlZmluZWRcIiwgXCJ1bmxpbmVzXCIsIFwidW50aWxcIiwgXCJ1bndvcmRzXCIsIFwidW56aXBcIiwgXCJ1bnppcDNcIiwgXCJ1c2VyRXJyb3JcIiwgXCJ3b3Jkc1wiLCBcIndyaXRlRmlsZVwiLCBcInppcFwiLCBcInppcDNcIiwgXCJ6aXBXaXRoXCIsIFwiemlwV2l0aDNcIik7XG4gIHJldHVybiB3a3c7XG59KCk7XG5leHBvcnQgY29uc3QgaGFza2VsbCA9IHtcbiAgbmFtZTogXCJoYXNrZWxsXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgZjogbm9ybWFsXG4gICAgfTtcbiAgfSxcbiAgY29weVN0YXRlOiBmdW5jdGlvbiAocykge1xuICAgIHJldHVybiB7XG4gICAgICBmOiBzLmZcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgdCA9IHN0YXRlLmYoc3RyZWFtLCBmdW5jdGlvbiAocykge1xuICAgICAgc3RhdGUuZiA9IHM7XG4gICAgfSk7XG4gICAgdmFyIHcgPSBzdHJlYW0uY3VycmVudCgpO1xuICAgIHJldHVybiB3ZWxsS25vd25Xb3Jkcy5oYXNPd25Qcm9wZXJ0eSh3KSA/IHdlbGxLbm93bldvcmRzW3ddIDogdDtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgbGluZTogXCItLVwiLFxuICAgICAgYmxvY2s6IHtcbiAgICAgICAgb3BlbjogXCJ7LVwiLFxuICAgICAgICBjbG9zZTogXCItfVwiXG4gICAgICB9XG4gICAgfVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=