"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[4605],{

/***/ 74605
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   commonLisp: () => (/* binding */ commonLisp)
/* harmony export */ });
var specialForm = /^(block|let*|return-from|catch|load-time-value|setq|eval-when|locally|symbol-macrolet|flet|macrolet|tagbody|function|multiple-value-call|the|go|multiple-value-prog1|throw|if|progn|unwind-protect|labels|progv|let|quote)$/;
var assumeBody = /^with|^def|^do|^prog|case$|^cond$|bind$|when$|unless$/;
var numLiteral = /^(?:[+\-]?(?:\d+|\d*\.\d+)(?:[efd][+\-]?\d+)?|[+\-]?\d+(?:\/[+\-]?\d+)?|#b[+\-]?[01]+|#o[+\-]?[0-7]+|#x[+\-]?[\da-f]+)/;
var symbol = /[^\s'`,@()\[\]";]/;
var type;
function readSym(stream) {
  var ch;
  while (ch = stream.next()) {
    if (ch == "\\") stream.next();else if (!symbol.test(ch)) {
      stream.backUp(1);
      break;
    }
  }
  return stream.current();
}
function base(stream, state) {
  if (stream.eatSpace()) {
    type = "ws";
    return null;
  }
  if (stream.match(numLiteral)) return "number";
  var ch = stream.next();
  if (ch == "\\") ch = stream.next();
  if (ch == '"') return (state.tokenize = inString)(stream, state);else if (ch == "(") {
    type = "open";
    return "bracket";
  } else if (ch == ")") {
    type = "close";
    return "bracket";
  } else if (ch == ";") {
    stream.skipToEnd();
    type = "ws";
    return "comment";
  } else if (/['`,@]/.test(ch)) return null;else if (ch == "|") {
    if (stream.skipTo("|")) {
      stream.next();
      return "variableName";
    } else {
      stream.skipToEnd();
      return "error";
    }
  } else if (ch == "#") {
    var ch = stream.next();
    if (ch == "(") {
      type = "open";
      return "bracket";
    } else if (/[+\-=\.']/.test(ch)) return null;else if (/\d/.test(ch) && stream.match(/^\d*#/)) return null;else if (ch == "|") return (state.tokenize = inComment)(stream, state);else if (ch == ":") {
      readSym(stream);
      return "meta";
    } else if (ch == "\\") {
      stream.next();
      readSym(stream);
      return "string.special";
    } else return "error";
  } else {
    var name = readSym(stream);
    if (name == ".") return null;
    type = "symbol";
    if (name == "nil" || name == "t" || name.charAt(0) == ":") return "atom";
    if (state.lastType == "open" && (specialForm.test(name) || assumeBody.test(name))) return "keyword";
    if (name.charAt(0) == "&") return "variableName.special";
    return "variableName";
  }
}
function inString(stream, state) {
  var escaped = false,
    next;
  while (next = stream.next()) {
    if (next == '"' && !escaped) {
      state.tokenize = base;
      break;
    }
    escaped = !escaped && next == "\\";
  }
  return "string";
}
function inComment(stream, state) {
  var next, last;
  while (next = stream.next()) {
    if (next == "#" && last == "|") {
      state.tokenize = base;
      break;
    }
    last = next;
  }
  type = "ws";
  return "comment";
}
const commonLisp = {
  name: "commonlisp",
  startState: function () {
    return {
      ctx: {
        prev: null,
        start: 0,
        indentTo: 0
      },
      lastType: null,
      tokenize: base
    };
  },
  token: function (stream, state) {
    if (stream.sol() && typeof state.ctx.indentTo != "number") state.ctx.indentTo = state.ctx.start + 1;
    type = null;
    var style = state.tokenize(stream, state);
    if (type != "ws") {
      if (state.ctx.indentTo == null) {
        if (type == "symbol" && assumeBody.test(stream.current())) state.ctx.indentTo = state.ctx.start + stream.indentUnit;else state.ctx.indentTo = "next";
      } else if (state.ctx.indentTo == "next") {
        state.ctx.indentTo = stream.column();
      }
      state.lastType = type;
    }
    if (type == "open") state.ctx = {
      prev: state.ctx,
      start: stream.column(),
      indentTo: null
    };else if (type == "close") state.ctx = state.ctx.prev || state.ctx;
    return style;
  },
  indent: function (state) {
    var i = state.ctx.indentTo;
    return typeof i == "number" ? i : state.ctx.start + 1;
  },
  languageData: {
    commentTokens: {
      line: ";;",
      block: {
        open: "#|",
        close: "|#"
      }
    },
    closeBrackets: {
      brackets: ["(", "[", "{", '"']
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNDYwNS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9jb21tb25saXNwLmpzIl0sInNvdXJjZXNDb250ZW50IjpbInZhciBzcGVjaWFsRm9ybSA9IC9eKGJsb2NrfGxldCp8cmV0dXJuLWZyb218Y2F0Y2h8bG9hZC10aW1lLXZhbHVlfHNldHF8ZXZhbC13aGVufGxvY2FsbHl8c3ltYm9sLW1hY3JvbGV0fGZsZXR8bWFjcm9sZXR8dGFnYm9keXxmdW5jdGlvbnxtdWx0aXBsZS12YWx1ZS1jYWxsfHRoZXxnb3xtdWx0aXBsZS12YWx1ZS1wcm9nMXx0aHJvd3xpZnxwcm9nbnx1bndpbmQtcHJvdGVjdHxsYWJlbHN8cHJvZ3Z8bGV0fHF1b3RlKSQvO1xudmFyIGFzc3VtZUJvZHkgPSAvXndpdGh8XmRlZnxeZG98XnByb2d8Y2FzZSR8XmNvbmQkfGJpbmQkfHdoZW4kfHVubGVzcyQvO1xudmFyIG51bUxpdGVyYWwgPSAvXig/OlsrXFwtXT8oPzpcXGQrfFxcZCpcXC5cXGQrKSg/OltlZmRdWytcXC1dP1xcZCspP3xbK1xcLV0/XFxkKyg/OlxcL1srXFwtXT9cXGQrKT98I2JbK1xcLV0/WzAxXSt8I29bK1xcLV0/WzAtN10rfCN4WytcXC1dP1tcXGRhLWZdKykvO1xudmFyIHN5bWJvbCA9IC9bXlxccydgLEAoKVxcW1xcXVwiO10vO1xudmFyIHR5cGU7XG5mdW5jdGlvbiByZWFkU3ltKHN0cmVhbSkge1xuICB2YXIgY2g7XG4gIHdoaWxlIChjaCA9IHN0cmVhbS5uZXh0KCkpIHtcbiAgICBpZiAoY2ggPT0gXCJcXFxcXCIpIHN0cmVhbS5uZXh0KCk7ZWxzZSBpZiAoIXN5bWJvbC50ZXN0KGNoKSkge1xuICAgICAgc3RyZWFtLmJhY2tVcCgxKTtcbiAgICAgIGJyZWFrO1xuICAgIH1cbiAgfVxuICByZXR1cm4gc3RyZWFtLmN1cnJlbnQoKTtcbn1cbmZ1bmN0aW9uIGJhc2Uoc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHtcbiAgICB0eXBlID0gXCJ3c1wiO1xuICAgIHJldHVybiBudWxsO1xuICB9XG4gIGlmIChzdHJlYW0ubWF0Y2gobnVtTGl0ZXJhbCkpIHJldHVybiBcIm51bWJlclwiO1xuICB2YXIgY2ggPSBzdHJlYW0ubmV4dCgpO1xuICBpZiAoY2ggPT0gXCJcXFxcXCIpIGNoID0gc3RyZWFtLm5leHQoKTtcbiAgaWYgKGNoID09ICdcIicpIHJldHVybiAoc3RhdGUudG9rZW5pemUgPSBpblN0cmluZykoc3RyZWFtLCBzdGF0ZSk7ZWxzZSBpZiAoY2ggPT0gXCIoXCIpIHtcbiAgICB0eXBlID0gXCJvcGVuXCI7XG4gICAgcmV0dXJuIFwiYnJhY2tldFwiO1xuICB9IGVsc2UgaWYgKGNoID09IFwiKVwiKSB7XG4gICAgdHlwZSA9IFwiY2xvc2VcIjtcbiAgICByZXR1cm4gXCJicmFja2V0XCI7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCI7XCIpIHtcbiAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgdHlwZSA9IFwid3NcIjtcbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH0gZWxzZSBpZiAoL1snYCxAXS8udGVzdChjaCkpIHJldHVybiBudWxsO2Vsc2UgaWYgKGNoID09IFwifFwiKSB7XG4gICAgaWYgKHN0cmVhbS5za2lwVG8oXCJ8XCIpKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgcmV0dXJuIFwidmFyaWFibGVOYW1lXCI7XG4gICAgfSBlbHNlIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiBcImVycm9yXCI7XG4gICAgfVxuICB9IGVsc2UgaWYgKGNoID09IFwiI1wiKSB7XG4gICAgdmFyIGNoID0gc3RyZWFtLm5leHQoKTtcbiAgICBpZiAoY2ggPT0gXCIoXCIpIHtcbiAgICAgIHR5cGUgPSBcIm9wZW5cIjtcbiAgICAgIHJldHVybiBcImJyYWNrZXRcIjtcbiAgICB9IGVsc2UgaWYgKC9bK1xcLT1cXC4nXS8udGVzdChjaCkpIHJldHVybiBudWxsO2Vsc2UgaWYgKC9cXGQvLnRlc3QoY2gpICYmIHN0cmVhbS5tYXRjaCgvXlxcZCojLykpIHJldHVybiBudWxsO2Vsc2UgaWYgKGNoID09IFwifFwiKSByZXR1cm4gKHN0YXRlLnRva2VuaXplID0gaW5Db21tZW50KShzdHJlYW0sIHN0YXRlKTtlbHNlIGlmIChjaCA9PSBcIjpcIikge1xuICAgICAgcmVhZFN5bShzdHJlYW0pO1xuICAgICAgcmV0dXJuIFwibWV0YVwiO1xuICAgIH0gZWxzZSBpZiAoY2ggPT0gXCJcXFxcXCIpIHtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICByZWFkU3ltKHN0cmVhbSk7XG4gICAgICByZXR1cm4gXCJzdHJpbmcuc3BlY2lhbFwiO1xuICAgIH0gZWxzZSByZXR1cm4gXCJlcnJvclwiO1xuICB9IGVsc2Uge1xuICAgIHZhciBuYW1lID0gcmVhZFN5bShzdHJlYW0pO1xuICAgIGlmIChuYW1lID09IFwiLlwiKSByZXR1cm4gbnVsbDtcbiAgICB0eXBlID0gXCJzeW1ib2xcIjtcbiAgICBpZiAobmFtZSA9PSBcIm5pbFwiIHx8IG5hbWUgPT0gXCJ0XCIgfHwgbmFtZS5jaGFyQXQoMCkgPT0gXCI6XCIpIHJldHVybiBcImF0b21cIjtcbiAgICBpZiAoc3RhdGUubGFzdFR5cGUgPT0gXCJvcGVuXCIgJiYgKHNwZWNpYWxGb3JtLnRlc3QobmFtZSkgfHwgYXNzdW1lQm9keS50ZXN0KG5hbWUpKSkgcmV0dXJuIFwia2V5d29yZFwiO1xuICAgIGlmIChuYW1lLmNoYXJBdCgwKSA9PSBcIiZcIikgcmV0dXJuIFwidmFyaWFibGVOYW1lLnNwZWNpYWxcIjtcbiAgICByZXR1cm4gXCJ2YXJpYWJsZU5hbWVcIjtcbiAgfVxufVxuZnVuY3Rpb24gaW5TdHJpbmcoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgZXNjYXBlZCA9IGZhbHNlLFxuICAgIG5leHQ7XG4gIHdoaWxlIChuZXh0ID0gc3RyZWFtLm5leHQoKSkge1xuICAgIGlmIChuZXh0ID09ICdcIicgJiYgIWVzY2FwZWQpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gYmFzZTtcbiAgICAgIGJyZWFrO1xuICAgIH1cbiAgICBlc2NhcGVkID0gIWVzY2FwZWQgJiYgbmV4dCA9PSBcIlxcXFxcIjtcbiAgfVxuICByZXR1cm4gXCJzdHJpbmdcIjtcbn1cbmZ1bmN0aW9uIGluQ29tbWVudChzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBuZXh0LCBsYXN0O1xuICB3aGlsZSAobmV4dCA9IHN0cmVhbS5uZXh0KCkpIHtcbiAgICBpZiAobmV4dCA9PSBcIiNcIiAmJiBsYXN0ID09IFwifFwiKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IGJhc2U7XG4gICAgICBicmVhaztcbiAgICB9XG4gICAgbGFzdCA9IG5leHQ7XG4gIH1cbiAgdHlwZSA9IFwid3NcIjtcbiAgcmV0dXJuIFwiY29tbWVudFwiO1xufVxuZXhwb3J0IGNvbnN0IGNvbW1vbkxpc3AgPSB7XG4gIG5hbWU6IFwiY29tbW9ubGlzcFwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIGN0eDoge1xuICAgICAgICBwcmV2OiBudWxsLFxuICAgICAgICBzdGFydDogMCxcbiAgICAgICAgaW5kZW50VG86IDBcbiAgICAgIH0sXG4gICAgICBsYXN0VHlwZTogbnVsbCxcbiAgICAgIHRva2VuaXplOiBiYXNlXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHN0cmVhbS5zb2woKSAmJiB0eXBlb2Ygc3RhdGUuY3R4LmluZGVudFRvICE9IFwibnVtYmVyXCIpIHN0YXRlLmN0eC5pbmRlbnRUbyA9IHN0YXRlLmN0eC5zdGFydCArIDE7XG4gICAgdHlwZSA9IG51bGw7XG4gICAgdmFyIHN0eWxlID0gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgaWYgKHR5cGUgIT0gXCJ3c1wiKSB7XG4gICAgICBpZiAoc3RhdGUuY3R4LmluZGVudFRvID09IG51bGwpIHtcbiAgICAgICAgaWYgKHR5cGUgPT0gXCJzeW1ib2xcIiAmJiBhc3N1bWVCb2R5LnRlc3Qoc3RyZWFtLmN1cnJlbnQoKSkpIHN0YXRlLmN0eC5pbmRlbnRUbyA9IHN0YXRlLmN0eC5zdGFydCArIHN0cmVhbS5pbmRlbnRVbml0O2Vsc2Ugc3RhdGUuY3R4LmluZGVudFRvID0gXCJuZXh0XCI7XG4gICAgICB9IGVsc2UgaWYgKHN0YXRlLmN0eC5pbmRlbnRUbyA9PSBcIm5leHRcIikge1xuICAgICAgICBzdGF0ZS5jdHguaW5kZW50VG8gPSBzdHJlYW0uY29sdW1uKCk7XG4gICAgICB9XG4gICAgICBzdGF0ZS5sYXN0VHlwZSA9IHR5cGU7XG4gICAgfVxuICAgIGlmICh0eXBlID09IFwib3BlblwiKSBzdGF0ZS5jdHggPSB7XG4gICAgICBwcmV2OiBzdGF0ZS5jdHgsXG4gICAgICBzdGFydDogc3RyZWFtLmNvbHVtbigpLFxuICAgICAgaW5kZW50VG86IG51bGxcbiAgICB9O2Vsc2UgaWYgKHR5cGUgPT0gXCJjbG9zZVwiKSBzdGF0ZS5jdHggPSBzdGF0ZS5jdHgucHJldiB8fCBzdGF0ZS5jdHg7XG4gICAgcmV0dXJuIHN0eWxlO1xuICB9LFxuICBpbmRlbnQ6IGZ1bmN0aW9uIChzdGF0ZSkge1xuICAgIHZhciBpID0gc3RhdGUuY3R4LmluZGVudFRvO1xuICAgIHJldHVybiB0eXBlb2YgaSA9PSBcIm51bWJlclwiID8gaSA6IHN0YXRlLmN0eC5zdGFydCArIDE7XG4gIH0sXG4gIGxhbmd1YWdlRGF0YToge1xuICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgIGxpbmU6IFwiOztcIixcbiAgICAgIGJsb2NrOiB7XG4gICAgICAgIG9wZW46IFwiI3xcIixcbiAgICAgICAgY2xvc2U6IFwifCNcIlxuICAgICAgfVxuICAgIH0sXG4gICAgY2xvc2VCcmFja2V0czoge1xuICAgICAgYnJhY2tldHM6IFtcIihcIiwgXCJbXCIsIFwie1wiLCAnXCInXVxuICAgIH1cbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9