"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[3206],{

/***/ 63206
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   dtd: () => (/* binding */ dtd)
/* harmony export */ });
var type;
function ret(style, tp) {
  type = tp;
  return style;
}
function tokenBase(stream, state) {
  var ch = stream.next();
  if (ch == "<" && stream.eat("!")) {
    if (stream.eatWhile(/[\-]/)) {
      state.tokenize = tokenSGMLComment;
      return tokenSGMLComment(stream, state);
    } else if (stream.eatWhile(/[\w]/)) return ret("keyword", "doindent");
  } else if (ch == "<" && stream.eat("?")) {
    //xml declaration
    state.tokenize = inBlock("meta", "?>");
    return ret("meta", ch);
  } else if (ch == "#" && stream.eatWhile(/[\w]/)) return ret("atom", "tag");else if (ch == "|") return ret("keyword", "separator");else if (ch.match(/[\(\)\[\]\-\.,\+\?>]/)) return ret(null, ch); //if(ch === ">") return ret(null, "endtag"); else
  else if (ch.match(/[\[\]]/)) return ret("rule", ch);else if (ch == "\"" || ch == "'") {
    state.tokenize = tokenString(ch);
    return state.tokenize(stream, state);
  } else if (stream.eatWhile(/[a-zA-Z\?\+\d]/)) {
    var sc = stream.current();
    if (sc.substr(sc.length - 1, sc.length).match(/\?|\+/) !== null) stream.backUp(1);
    return ret("tag", "tag");
  } else if (ch == "%" || ch == "*") return ret("number", "number");else {
    stream.eatWhile(/[\w\\\-_%.{,]/);
    return ret(null, null);
  }
}
function tokenSGMLComment(stream, state) {
  var dashes = 0,
    ch;
  while ((ch = stream.next()) != null) {
    if (dashes >= 2 && ch == ">") {
      state.tokenize = tokenBase;
      break;
    }
    dashes = ch == "-" ? dashes + 1 : 0;
  }
  return ret("comment", "comment");
}
function tokenString(quote) {
  return function (stream, state) {
    var escaped = false,
      ch;
    while ((ch = stream.next()) != null) {
      if (ch == quote && !escaped) {
        state.tokenize = tokenBase;
        break;
      }
      escaped = !escaped && ch == "\\";
    }
    return ret("string", "tag");
  };
}
function inBlock(style, terminator) {
  return function (stream, state) {
    while (!stream.eol()) {
      if (stream.match(terminator)) {
        state.tokenize = tokenBase;
        break;
      }
      stream.next();
    }
    return style;
  };
}
const dtd = {
  name: "dtd",
  startState: function () {
    return {
      tokenize: tokenBase,
      baseIndent: 0,
      stack: []
    };
  },
  token: function (stream, state) {
    if (stream.eatSpace()) return null;
    var style = state.tokenize(stream, state);
    var context = state.stack[state.stack.length - 1];
    if (stream.current() == "[" || type === "doindent" || type == "[") state.stack.push("rule");else if (type === "endtag") state.stack[state.stack.length - 1] = "endtag";else if (stream.current() == "]" || type == "]" || type == ">" && context == "rule") state.stack.pop();else if (type == "[") state.stack.push("[");
    return style;
  },
  indent: function (state, textAfter, cx) {
    var n = state.stack.length;
    if (textAfter.charAt(0) === ']') n--;else if (textAfter.substr(textAfter.length - 1, textAfter.length) === ">") {
      if (textAfter.substr(0, 1) === "<") {} else if (type == "doindent" && textAfter.length > 1) {} else if (type == "doindent") n--;else if (type == ">" && textAfter.length > 1) {} else if (type == "tag" && textAfter !== ">") {} else if (type == "tag" && state.stack[state.stack.length - 1] == "rule") n--;else if (type == "tag") n++;else if (textAfter === ">" && state.stack[state.stack.length - 1] == "rule" && type === ">") n--;else if (textAfter === ">" && state.stack[state.stack.length - 1] == "rule") {} else if (textAfter.substr(0, 1) !== "<" && textAfter.substr(0, 1) === ">") n = n - 1;else if (textAfter === ">") {} else n = n - 1;
      //over rule them all
      if (type == null || type == "]") n--;
    }
    return state.baseIndent + n * cx.unit;
  },
  languageData: {
    indentOnInput: /^\s*[\]>]$/
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMzIwNi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL2R0ZC5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJ2YXIgdHlwZTtcbmZ1bmN0aW9uIHJldChzdHlsZSwgdHApIHtcbiAgdHlwZSA9IHRwO1xuICByZXR1cm4gc3R5bGU7XG59XG5mdW5jdGlvbiB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgY2ggPSBzdHJlYW0ubmV4dCgpO1xuICBpZiAoY2ggPT0gXCI8XCIgJiYgc3RyZWFtLmVhdChcIiFcIikpIHtcbiAgICBpZiAoc3RyZWFtLmVhdFdoaWxlKC9bXFwtXS8pKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuU0dNTENvbW1lbnQ7XG4gICAgICByZXR1cm4gdG9rZW5TR01MQ29tbWVudChzdHJlYW0sIHN0YXRlKTtcbiAgICB9IGVsc2UgaWYgKHN0cmVhbS5lYXRXaGlsZSgvW1xcd10vKSkgcmV0dXJuIHJldChcImtleXdvcmRcIiwgXCJkb2luZGVudFwiKTtcbiAgfSBlbHNlIGlmIChjaCA9PSBcIjxcIiAmJiBzdHJlYW0uZWF0KFwiP1wiKSkge1xuICAgIC8veG1sIGRlY2xhcmF0aW9uXG4gICAgc3RhdGUudG9rZW5pemUgPSBpbkJsb2NrKFwibWV0YVwiLCBcIj8+XCIpO1xuICAgIHJldHVybiByZXQoXCJtZXRhXCIsIGNoKTtcbiAgfSBlbHNlIGlmIChjaCA9PSBcIiNcIiAmJiBzdHJlYW0uZWF0V2hpbGUoL1tcXHddLykpIHJldHVybiByZXQoXCJhdG9tXCIsIFwidGFnXCIpO2Vsc2UgaWYgKGNoID09IFwifFwiKSByZXR1cm4gcmV0KFwia2V5d29yZFwiLCBcInNlcGFyYXRvclwiKTtlbHNlIGlmIChjaC5tYXRjaCgvW1xcKFxcKVxcW1xcXVxcLVxcLixcXCtcXD8+XS8pKSByZXR1cm4gcmV0KG51bGwsIGNoKTsgLy9pZihjaCA9PT0gXCI+XCIpIHJldHVybiByZXQobnVsbCwgXCJlbmR0YWdcIik7IGVsc2VcbiAgZWxzZSBpZiAoY2gubWF0Y2goL1tcXFtcXF1dLykpIHJldHVybiByZXQoXCJydWxlXCIsIGNoKTtlbHNlIGlmIChjaCA9PSBcIlxcXCJcIiB8fCBjaCA9PSBcIidcIikge1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5TdHJpbmcoY2gpO1xuICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgfSBlbHNlIGlmIChzdHJlYW0uZWF0V2hpbGUoL1thLXpBLVpcXD9cXCtcXGRdLykpIHtcbiAgICB2YXIgc2MgPSBzdHJlYW0uY3VycmVudCgpO1xuICAgIGlmIChzYy5zdWJzdHIoc2MubGVuZ3RoIC0gMSwgc2MubGVuZ3RoKS5tYXRjaCgvXFw/fFxcKy8pICE9PSBudWxsKSBzdHJlYW0uYmFja1VwKDEpO1xuICAgIHJldHVybiByZXQoXCJ0YWdcIiwgXCJ0YWdcIik7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCIlXCIgfHwgY2ggPT0gXCIqXCIpIHJldHVybiByZXQoXCJudW1iZXJcIiwgXCJudW1iZXJcIik7ZWxzZSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFxcXFxcLV8lLnssXS8pO1xuICAgIHJldHVybiByZXQobnVsbCwgbnVsbCk7XG4gIH1cbn1cbmZ1bmN0aW9uIHRva2VuU0dNTENvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgZGFzaGVzID0gMCxcbiAgICBjaDtcbiAgd2hpbGUgKChjaCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICBpZiAoZGFzaGVzID49IDIgJiYgY2ggPT0gXCI+XCIpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgICAgYnJlYWs7XG4gICAgfVxuICAgIGRhc2hlcyA9IGNoID09IFwiLVwiID8gZGFzaGVzICsgMSA6IDA7XG4gIH1cbiAgcmV0dXJuIHJldChcImNvbW1lbnRcIiwgXCJjb21tZW50XCIpO1xufVxuZnVuY3Rpb24gdG9rZW5TdHJpbmcocXVvdGUpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGVzY2FwZWQgPSBmYWxzZSxcbiAgICAgIGNoO1xuICAgIHdoaWxlICgoY2ggPSBzdHJlYW0ubmV4dCgpKSAhPSBudWxsKSB7XG4gICAgICBpZiAoY2ggPT0gcXVvdGUgJiYgIWVzY2FwZWQpIHtcbiAgICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgICAgIGJyZWFrO1xuICAgICAgfVxuICAgICAgZXNjYXBlZCA9ICFlc2NhcGVkICYmIGNoID09IFwiXFxcXFwiO1xuICAgIH1cbiAgICByZXR1cm4gcmV0KFwic3RyaW5nXCIsIFwidGFnXCIpO1xuICB9O1xufVxuZnVuY3Rpb24gaW5CbG9jayhzdHlsZSwgdGVybWluYXRvcikge1xuICByZXR1cm4gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB3aGlsZSAoIXN0cmVhbS5lb2woKSkge1xuICAgICAgaWYgKHN0cmVhbS5tYXRjaCh0ZXJtaW5hdG9yKSkge1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgICAgYnJlYWs7XG4gICAgICB9XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgIH1cbiAgICByZXR1cm4gc3R5bGU7XG4gIH07XG59XG5leHBvcnQgY29uc3QgZHRkID0ge1xuICBuYW1lOiBcImR0ZFwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiB0b2tlbkJhc2UsXG4gICAgICBiYXNlSW5kZW50OiAwLFxuICAgICAgc3RhY2s6IFtdXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgICB2YXIgc3R5bGUgPSBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICB2YXIgY29udGV4dCA9IHN0YXRlLnN0YWNrW3N0YXRlLnN0YWNrLmxlbmd0aCAtIDFdO1xuICAgIGlmIChzdHJlYW0uY3VycmVudCgpID09IFwiW1wiIHx8IHR5cGUgPT09IFwiZG9pbmRlbnRcIiB8fCB0eXBlID09IFwiW1wiKSBzdGF0ZS5zdGFjay5wdXNoKFwicnVsZVwiKTtlbHNlIGlmICh0eXBlID09PSBcImVuZHRhZ1wiKSBzdGF0ZS5zdGFja1tzdGF0ZS5zdGFjay5sZW5ndGggLSAxXSA9IFwiZW5kdGFnXCI7ZWxzZSBpZiAoc3RyZWFtLmN1cnJlbnQoKSA9PSBcIl1cIiB8fCB0eXBlID09IFwiXVwiIHx8IHR5cGUgPT0gXCI+XCIgJiYgY29udGV4dCA9PSBcInJ1bGVcIikgc3RhdGUuc3RhY2sucG9wKCk7ZWxzZSBpZiAodHlwZSA9PSBcIltcIikgc3RhdGUuc3RhY2sucHVzaChcIltcIik7XG4gICAgcmV0dXJuIHN0eWxlO1xuICB9LFxuICBpbmRlbnQ6IGZ1bmN0aW9uIChzdGF0ZSwgdGV4dEFmdGVyLCBjeCkge1xuICAgIHZhciBuID0gc3RhdGUuc3RhY2subGVuZ3RoO1xuICAgIGlmICh0ZXh0QWZ0ZXIuY2hhckF0KDApID09PSAnXScpIG4tLTtlbHNlIGlmICh0ZXh0QWZ0ZXIuc3Vic3RyKHRleHRBZnRlci5sZW5ndGggLSAxLCB0ZXh0QWZ0ZXIubGVuZ3RoKSA9PT0gXCI+XCIpIHtcbiAgICAgIGlmICh0ZXh0QWZ0ZXIuc3Vic3RyKDAsIDEpID09PSBcIjxcIikge30gZWxzZSBpZiAodHlwZSA9PSBcImRvaW5kZW50XCIgJiYgdGV4dEFmdGVyLmxlbmd0aCA+IDEpIHt9IGVsc2UgaWYgKHR5cGUgPT0gXCJkb2luZGVudFwiKSBuLS07ZWxzZSBpZiAodHlwZSA9PSBcIj5cIiAmJiB0ZXh0QWZ0ZXIubGVuZ3RoID4gMSkge30gZWxzZSBpZiAodHlwZSA9PSBcInRhZ1wiICYmIHRleHRBZnRlciAhPT0gXCI+XCIpIHt9IGVsc2UgaWYgKHR5cGUgPT0gXCJ0YWdcIiAmJiBzdGF0ZS5zdGFja1tzdGF0ZS5zdGFjay5sZW5ndGggLSAxXSA9PSBcInJ1bGVcIikgbi0tO2Vsc2UgaWYgKHR5cGUgPT0gXCJ0YWdcIikgbisrO2Vsc2UgaWYgKHRleHRBZnRlciA9PT0gXCI+XCIgJiYgc3RhdGUuc3RhY2tbc3RhdGUuc3RhY2subGVuZ3RoIC0gMV0gPT0gXCJydWxlXCIgJiYgdHlwZSA9PT0gXCI+XCIpIG4tLTtlbHNlIGlmICh0ZXh0QWZ0ZXIgPT09IFwiPlwiICYmIHN0YXRlLnN0YWNrW3N0YXRlLnN0YWNrLmxlbmd0aCAtIDFdID09IFwicnVsZVwiKSB7fSBlbHNlIGlmICh0ZXh0QWZ0ZXIuc3Vic3RyKDAsIDEpICE9PSBcIjxcIiAmJiB0ZXh0QWZ0ZXIuc3Vic3RyKDAsIDEpID09PSBcIj5cIikgbiA9IG4gLSAxO2Vsc2UgaWYgKHRleHRBZnRlciA9PT0gXCI+XCIpIHt9IGVsc2UgbiA9IG4gLSAxO1xuICAgICAgLy9vdmVyIHJ1bGUgdGhlbSBhbGxcbiAgICAgIGlmICh0eXBlID09IG51bGwgfHwgdHlwZSA9PSBcIl1cIikgbi0tO1xuICAgIH1cbiAgICByZXR1cm4gc3RhdGUuYmFzZUluZGVudCArIG4gKiBjeC51bml0O1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBpbmRlbnRPbklucHV0OiAvXlxccypbXFxdPl0kL1xuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=