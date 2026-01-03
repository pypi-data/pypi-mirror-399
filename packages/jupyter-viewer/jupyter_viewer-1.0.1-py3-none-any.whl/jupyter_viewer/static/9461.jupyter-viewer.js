"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[9461],{

/***/ 9461
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   tcl: () => (/* binding */ tcl)
/* harmony export */ });
function parseWords(str) {
  var obj = {},
    words = str.split(" ");
  for (var i = 0; i < words.length; ++i) obj[words[i]] = true;
  return obj;
}
var keywords = parseWords("Tcl safe after append array auto_execok auto_import auto_load " + "auto_mkindex auto_mkindex_old auto_qualify auto_reset bgerror " + "binary break catch cd close concat continue dde eof encoding error " + "eval exec exit expr fblocked fconfigure fcopy file fileevent filename " + "filename flush for foreach format gets glob global history http if " + "incr info interp join lappend lindex linsert list llength load lrange " + "lreplace lsearch lset lsort memory msgcat namespace open package parray " + "pid pkg::create pkg_mkIndex proc puts pwd re_syntax read regex regexp " + "registry regsub rename resource return scan seek set socket source split " + "string subst switch tcl_endOfWord tcl_findLibrary tcl_startOfNextWord " + "tcl_wordBreakAfter tcl_startOfPreviousWord tcl_wordBreakBefore tcltest " + "tclvars tell time trace unknown unset update uplevel upvar variable " + "vwait");
var functions = parseWords("if elseif else and not or eq ne in ni for foreach while switch");
var isOperatorChar = /[+\-*&%=<>!?^\/\|]/;
function chain(stream, state, f) {
  state.tokenize = f;
  return f(stream, state);
}
function tokenBase(stream, state) {
  var beforeParams = state.beforeParams;
  state.beforeParams = false;
  var ch = stream.next();
  if ((ch == '"' || ch == "'") && state.inParams) {
    return chain(stream, state, tokenString(ch));
  } else if (/[\[\]{}\(\),;\.]/.test(ch)) {
    if (ch == "(" && beforeParams) state.inParams = true;else if (ch == ")") state.inParams = false;
    return null;
  } else if (/\d/.test(ch)) {
    stream.eatWhile(/[\w\.]/);
    return "number";
  } else if (ch == "#") {
    if (stream.eat("*")) return chain(stream, state, tokenComment);
    if (ch == "#" && stream.match(/ *\[ *\[/)) return chain(stream, state, tokenUnparsed);
    stream.skipToEnd();
    return "comment";
  } else if (ch == '"') {
    stream.skipTo(/"/);
    return "comment";
  } else if (ch == "$") {
    stream.eatWhile(/[$_a-z0-9A-Z\.{:]/);
    stream.eatWhile(/}/);
    state.beforeParams = true;
    return "builtin";
  } else if (isOperatorChar.test(ch)) {
    stream.eatWhile(isOperatorChar);
    return "comment";
  } else {
    stream.eatWhile(/[\w\$_{}\xa1-\uffff]/);
    var word = stream.current().toLowerCase();
    if (keywords && keywords.propertyIsEnumerable(word)) return "keyword";
    if (functions && functions.propertyIsEnumerable(word)) {
      state.beforeParams = true;
      return "keyword";
    }
    return null;
  }
}
function tokenString(quote) {
  return function (stream, state) {
    var escaped = false,
      next,
      end = false;
    while ((next = stream.next()) != null) {
      if (next == quote && !escaped) {
        end = true;
        break;
      }
      escaped = !escaped && next == "\\";
    }
    if (end) state.tokenize = tokenBase;
    return "string";
  };
}
function tokenComment(stream, state) {
  var maybeEnd = false,
    ch;
  while (ch = stream.next()) {
    if (ch == "#" && maybeEnd) {
      state.tokenize = tokenBase;
      break;
    }
    maybeEnd = ch == "*";
  }
  return "comment";
}
function tokenUnparsed(stream, state) {
  var maybeEnd = 0,
    ch;
  while (ch = stream.next()) {
    if (ch == "#" && maybeEnd == 2) {
      state.tokenize = tokenBase;
      break;
    }
    if (ch == "]") maybeEnd++;else if (ch != " ") maybeEnd = 0;
  }
  return "meta";
}
const tcl = {
  name: "tcl",
  startState: function () {
    return {
      tokenize: tokenBase,
      beforeParams: false,
      inParams: false
    };
  },
  token: function (stream, state) {
    if (stream.eatSpace()) return null;
    return state.tokenize(stream, state);
  },
  languageData: {
    commentTokens: {
      line: "#"
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiOTQ2MS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL3RjbC5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiBwYXJzZVdvcmRzKHN0cikge1xuICB2YXIgb2JqID0ge30sXG4gICAgd29yZHMgPSBzdHIuc3BsaXQoXCIgXCIpO1xuICBmb3IgKHZhciBpID0gMDsgaSA8IHdvcmRzLmxlbmd0aDsgKytpKSBvYmpbd29yZHNbaV1dID0gdHJ1ZTtcbiAgcmV0dXJuIG9iajtcbn1cbnZhciBrZXl3b3JkcyA9IHBhcnNlV29yZHMoXCJUY2wgc2FmZSBhZnRlciBhcHBlbmQgYXJyYXkgYXV0b19leGVjb2sgYXV0b19pbXBvcnQgYXV0b19sb2FkIFwiICsgXCJhdXRvX21raW5kZXggYXV0b19ta2luZGV4X29sZCBhdXRvX3F1YWxpZnkgYXV0b19yZXNldCBiZ2Vycm9yIFwiICsgXCJiaW5hcnkgYnJlYWsgY2F0Y2ggY2QgY2xvc2UgY29uY2F0IGNvbnRpbnVlIGRkZSBlb2YgZW5jb2RpbmcgZXJyb3IgXCIgKyBcImV2YWwgZXhlYyBleGl0IGV4cHIgZmJsb2NrZWQgZmNvbmZpZ3VyZSBmY29weSBmaWxlIGZpbGVldmVudCBmaWxlbmFtZSBcIiArIFwiZmlsZW5hbWUgZmx1c2ggZm9yIGZvcmVhY2ggZm9ybWF0IGdldHMgZ2xvYiBnbG9iYWwgaGlzdG9yeSBodHRwIGlmIFwiICsgXCJpbmNyIGluZm8gaW50ZXJwIGpvaW4gbGFwcGVuZCBsaW5kZXggbGluc2VydCBsaXN0IGxsZW5ndGggbG9hZCBscmFuZ2UgXCIgKyBcImxyZXBsYWNlIGxzZWFyY2ggbHNldCBsc29ydCBtZW1vcnkgbXNnY2F0IG5hbWVzcGFjZSBvcGVuIHBhY2thZ2UgcGFycmF5IFwiICsgXCJwaWQgcGtnOjpjcmVhdGUgcGtnX21rSW5kZXggcHJvYyBwdXRzIHB3ZCByZV9zeW50YXggcmVhZCByZWdleCByZWdleHAgXCIgKyBcInJlZ2lzdHJ5IHJlZ3N1YiByZW5hbWUgcmVzb3VyY2UgcmV0dXJuIHNjYW4gc2VlayBzZXQgc29ja2V0IHNvdXJjZSBzcGxpdCBcIiArIFwic3RyaW5nIHN1YnN0IHN3aXRjaCB0Y2xfZW5kT2ZXb3JkIHRjbF9maW5kTGlicmFyeSB0Y2xfc3RhcnRPZk5leHRXb3JkIFwiICsgXCJ0Y2xfd29yZEJyZWFrQWZ0ZXIgdGNsX3N0YXJ0T2ZQcmV2aW91c1dvcmQgdGNsX3dvcmRCcmVha0JlZm9yZSB0Y2x0ZXN0IFwiICsgXCJ0Y2x2YXJzIHRlbGwgdGltZSB0cmFjZSB1bmtub3duIHVuc2V0IHVwZGF0ZSB1cGxldmVsIHVwdmFyIHZhcmlhYmxlIFwiICsgXCJ2d2FpdFwiKTtcbnZhciBmdW5jdGlvbnMgPSBwYXJzZVdvcmRzKFwiaWYgZWxzZWlmIGVsc2UgYW5kIG5vdCBvciBlcSBuZSBpbiBuaSBmb3IgZm9yZWFjaCB3aGlsZSBzd2l0Y2hcIik7XG52YXIgaXNPcGVyYXRvckNoYXIgPSAvWytcXC0qJiU9PD4hP15cXC9cXHxdLztcbmZ1bmN0aW9uIGNoYWluKHN0cmVhbSwgc3RhdGUsIGYpIHtcbiAgc3RhdGUudG9rZW5pemUgPSBmO1xuICByZXR1cm4gZihzdHJlYW0sIHN0YXRlKTtcbn1cbmZ1bmN0aW9uIHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBiZWZvcmVQYXJhbXMgPSBzdGF0ZS5iZWZvcmVQYXJhbXM7XG4gIHN0YXRlLmJlZm9yZVBhcmFtcyA9IGZhbHNlO1xuICB2YXIgY2ggPSBzdHJlYW0ubmV4dCgpO1xuICBpZiAoKGNoID09ICdcIicgfHwgY2ggPT0gXCInXCIpICYmIHN0YXRlLmluUGFyYW1zKSB7XG4gICAgcmV0dXJuIGNoYWluKHN0cmVhbSwgc3RhdGUsIHRva2VuU3RyaW5nKGNoKSk7XG4gIH0gZWxzZSBpZiAoL1tcXFtcXF17fVxcKFxcKSw7XFwuXS8udGVzdChjaCkpIHtcbiAgICBpZiAoY2ggPT0gXCIoXCIgJiYgYmVmb3JlUGFyYW1zKSBzdGF0ZS5pblBhcmFtcyA9IHRydWU7ZWxzZSBpZiAoY2ggPT0gXCIpXCIpIHN0YXRlLmluUGFyYW1zID0gZmFsc2U7XG4gICAgcmV0dXJuIG51bGw7XG4gIH0gZWxzZSBpZiAoL1xcZC8udGVzdChjaCkpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXC5dLyk7XG4gICAgcmV0dXJuIFwibnVtYmVyXCI7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCIjXCIpIHtcbiAgICBpZiAoc3RyZWFtLmVhdChcIipcIikpIHJldHVybiBjaGFpbihzdHJlYW0sIHN0YXRlLCB0b2tlbkNvbW1lbnQpO1xuICAgIGlmIChjaCA9PSBcIiNcIiAmJiBzdHJlYW0ubWF0Y2goLyAqXFxbICpcXFsvKSkgcmV0dXJuIGNoYWluKHN0cmVhbSwgc3RhdGUsIHRva2VuVW5wYXJzZWQpO1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH0gZWxzZSBpZiAoY2ggPT0gJ1wiJykge1xuICAgIHN0cmVhbS5za2lwVG8oL1wiLyk7XG4gICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICB9IGVsc2UgaWYgKGNoID09IFwiJFwiKSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bJF9hLXowLTlBLVpcXC57Ol0vKTtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL30vKTtcbiAgICBzdGF0ZS5iZWZvcmVQYXJhbXMgPSB0cnVlO1xuICAgIHJldHVybiBcImJ1aWx0aW5cIjtcbiAgfSBlbHNlIGlmIChpc09wZXJhdG9yQ2hhci50ZXN0KGNoKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZShpc09wZXJhdG9yQ2hhcik7XG4gICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICB9IGVsc2Uge1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcJF97fVxceGExLVxcdWZmZmZdLyk7XG4gICAgdmFyIHdvcmQgPSBzdHJlYW0uY3VycmVudCgpLnRvTG93ZXJDYXNlKCk7XG4gICAgaWYgKGtleXdvcmRzICYmIGtleXdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKHdvcmQpKSByZXR1cm4gXCJrZXl3b3JkXCI7XG4gICAgaWYgKGZ1bmN0aW9ucyAmJiBmdW5jdGlvbnMucHJvcGVydHlJc0VudW1lcmFibGUod29yZCkpIHtcbiAgICAgIHN0YXRlLmJlZm9yZVBhcmFtcyA9IHRydWU7XG4gICAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gICAgfVxuICAgIHJldHVybiBudWxsO1xuICB9XG59XG5mdW5jdGlvbiB0b2tlblN0cmluZyhxdW90ZSkge1xuICByZXR1cm4gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgZXNjYXBlZCA9IGZhbHNlLFxuICAgICAgbmV4dCxcbiAgICAgIGVuZCA9IGZhbHNlO1xuICAgIHdoaWxlICgobmV4dCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICAgIGlmIChuZXh0ID09IHF1b3RlICYmICFlc2NhcGVkKSB7XG4gICAgICAgIGVuZCA9IHRydWU7XG4gICAgICAgIGJyZWFrO1xuICAgICAgfVxuICAgICAgZXNjYXBlZCA9ICFlc2NhcGVkICYmIG5leHQgPT0gXCJcXFxcXCI7XG4gICAgfVxuICAgIGlmIChlbmQpIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9O1xufVxuZnVuY3Rpb24gdG9rZW5Db21tZW50KHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIG1heWJlRW5kID0gZmFsc2UsXG4gICAgY2g7XG4gIHdoaWxlIChjaCA9IHN0cmVhbS5uZXh0KCkpIHtcbiAgICBpZiAoY2ggPT0gXCIjXCIgJiYgbWF5YmVFbmQpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgICAgYnJlYWs7XG4gICAgfVxuICAgIG1heWJlRW5kID0gY2ggPT0gXCIqXCI7XG4gIH1cbiAgcmV0dXJuIFwiY29tbWVudFwiO1xufVxuZnVuY3Rpb24gdG9rZW5VbnBhcnNlZChzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBtYXliZUVuZCA9IDAsXG4gICAgY2g7XG4gIHdoaWxlIChjaCA9IHN0cmVhbS5uZXh0KCkpIHtcbiAgICBpZiAoY2ggPT0gXCIjXCIgJiYgbWF5YmVFbmQgPT0gMikge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgICBicmVhaztcbiAgICB9XG4gICAgaWYgKGNoID09IFwiXVwiKSBtYXliZUVuZCsrO2Vsc2UgaWYgKGNoICE9IFwiIFwiKSBtYXliZUVuZCA9IDA7XG4gIH1cbiAgcmV0dXJuIFwibWV0YVwiO1xufVxuZXhwb3J0IGNvbnN0IHRjbCA9IHtcbiAgbmFtZTogXCJ0Y2xcIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB7XG4gICAgICB0b2tlbml6ZTogdG9rZW5CYXNlLFxuICAgICAgYmVmb3JlUGFyYW1zOiBmYWxzZSxcbiAgICAgIGluUGFyYW1zOiBmYWxzZVxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkgcmV0dXJuIG51bGw7XG4gICAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBjb21tZW50VG9rZW5zOiB7XG4gICAgICBsaW5lOiBcIiNcIlxuICAgIH1cbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9