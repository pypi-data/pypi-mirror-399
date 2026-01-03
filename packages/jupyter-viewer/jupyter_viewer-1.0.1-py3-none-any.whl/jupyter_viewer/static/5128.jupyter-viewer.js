"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[5128],{

/***/ 35128
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   pascal: () => (/* binding */ pascal)
/* harmony export */ });
function words(str) {
  var obj = {},
    words = str.split(" ");
  for (var i = 0; i < words.length; ++i) obj[words[i]] = true;
  return obj;
}
var keywords = words("absolute and array asm begin case const constructor destructor div do " + "downto else end file for function goto if implementation in inherited " + "inline interface label mod nil not object of operator or packed procedure " + "program record reintroduce repeat self set shl shr string then to type " + "unit until uses var while with xor as class dispinterface except exports " + "finalization finally initialization inline is library on out packed " + "property raise resourcestring threadvar try absolute abstract alias " + "assembler bitpacked break cdecl continue cppdecl cvar default deprecated " + "dynamic enumerator experimental export external far far16 forward generic " + "helper implements index interrupt iocheck local message name near " + "nodefault noreturn nostackframe oldfpccall otherwise overload override " + "pascal platform private protected public published read register " + "reintroduce result safecall saveregisters softfloat specialize static " + "stdcall stored strict unaligned unimplemented varargs virtual write");
var atoms = {
  "null": true
};
var isOperatorChar = /[+\-*&%=<>!?|\/]/;
function tokenBase(stream, state) {
  var ch = stream.next();
  if (ch == "#" && state.startOfLine) {
    stream.skipToEnd();
    return "meta";
  }
  if (ch == '"' || ch == "'") {
    state.tokenize = tokenString(ch);
    return state.tokenize(stream, state);
  }
  if (ch == "(" && stream.eat("*")) {
    state.tokenize = tokenComment;
    return tokenComment(stream, state);
  }
  if (ch == "{") {
    state.tokenize = tokenCommentBraces;
    return tokenCommentBraces(stream, state);
  }
  if (/[\[\]\(\),;\:\.]/.test(ch)) {
    return null;
  }
  if (/\d/.test(ch)) {
    stream.eatWhile(/[\w\.]/);
    return "number";
  }
  if (ch == "/") {
    if (stream.eat("/")) {
      stream.skipToEnd();
      return "comment";
    }
  }
  if (isOperatorChar.test(ch)) {
    stream.eatWhile(isOperatorChar);
    return "operator";
  }
  stream.eatWhile(/[\w\$_]/);
  var cur = stream.current().toLowerCase();
  if (keywords.propertyIsEnumerable(cur)) return "keyword";
  if (atoms.propertyIsEnumerable(cur)) return "atom";
  return "variable";
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
    if (end || !escaped) state.tokenize = null;
    return "string";
  };
}
function tokenComment(stream, state) {
  var maybeEnd = false,
    ch;
  while (ch = stream.next()) {
    if (ch == ")" && maybeEnd) {
      state.tokenize = null;
      break;
    }
    maybeEnd = ch == "*";
  }
  return "comment";
}
function tokenCommentBraces(stream, state) {
  var ch;
  while (ch = stream.next()) {
    if (ch == "}") {
      state.tokenize = null;
      break;
    }
  }
  return "comment";
}

// Interface

const pascal = {
  name: "pascal",
  startState: function () {
    return {
      tokenize: null
    };
  },
  token: function (stream, state) {
    if (stream.eatSpace()) return null;
    var style = (state.tokenize || tokenBase)(stream, state);
    if (style == "comment" || style == "meta") return style;
    return style;
  },
  languageData: {
    indentOnInput: /^\s*[{}]$/,
    commentTokens: {
      block: {
        open: "(*",
        close: "*)"
      }
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNTEyOC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9wYXNjYWwuanMiXSwic291cmNlc0NvbnRlbnQiOlsiZnVuY3Rpb24gd29yZHMoc3RyKSB7XG4gIHZhciBvYmogPSB7fSxcbiAgICB3b3JkcyA9IHN0ci5zcGxpdChcIiBcIik7XG4gIGZvciAodmFyIGkgPSAwOyBpIDwgd29yZHMubGVuZ3RoOyArK2kpIG9ialt3b3Jkc1tpXV0gPSB0cnVlO1xuICByZXR1cm4gb2JqO1xufVxudmFyIGtleXdvcmRzID0gd29yZHMoXCJhYnNvbHV0ZSBhbmQgYXJyYXkgYXNtIGJlZ2luIGNhc2UgY29uc3QgY29uc3RydWN0b3IgZGVzdHJ1Y3RvciBkaXYgZG8gXCIgKyBcImRvd250byBlbHNlIGVuZCBmaWxlIGZvciBmdW5jdGlvbiBnb3RvIGlmIGltcGxlbWVudGF0aW9uIGluIGluaGVyaXRlZCBcIiArIFwiaW5saW5lIGludGVyZmFjZSBsYWJlbCBtb2QgbmlsIG5vdCBvYmplY3Qgb2Ygb3BlcmF0b3Igb3IgcGFja2VkIHByb2NlZHVyZSBcIiArIFwicHJvZ3JhbSByZWNvcmQgcmVpbnRyb2R1Y2UgcmVwZWF0IHNlbGYgc2V0IHNobCBzaHIgc3RyaW5nIHRoZW4gdG8gdHlwZSBcIiArIFwidW5pdCB1bnRpbCB1c2VzIHZhciB3aGlsZSB3aXRoIHhvciBhcyBjbGFzcyBkaXNwaW50ZXJmYWNlIGV4Y2VwdCBleHBvcnRzIFwiICsgXCJmaW5hbGl6YXRpb24gZmluYWxseSBpbml0aWFsaXphdGlvbiBpbmxpbmUgaXMgbGlicmFyeSBvbiBvdXQgcGFja2VkIFwiICsgXCJwcm9wZXJ0eSByYWlzZSByZXNvdXJjZXN0cmluZyB0aHJlYWR2YXIgdHJ5IGFic29sdXRlIGFic3RyYWN0IGFsaWFzIFwiICsgXCJhc3NlbWJsZXIgYml0cGFja2VkIGJyZWFrIGNkZWNsIGNvbnRpbnVlIGNwcGRlY2wgY3ZhciBkZWZhdWx0IGRlcHJlY2F0ZWQgXCIgKyBcImR5bmFtaWMgZW51bWVyYXRvciBleHBlcmltZW50YWwgZXhwb3J0IGV4dGVybmFsIGZhciBmYXIxNiBmb3J3YXJkIGdlbmVyaWMgXCIgKyBcImhlbHBlciBpbXBsZW1lbnRzIGluZGV4IGludGVycnVwdCBpb2NoZWNrIGxvY2FsIG1lc3NhZ2UgbmFtZSBuZWFyIFwiICsgXCJub2RlZmF1bHQgbm9yZXR1cm4gbm9zdGFja2ZyYW1lIG9sZGZwY2NhbGwgb3RoZXJ3aXNlIG92ZXJsb2FkIG92ZXJyaWRlIFwiICsgXCJwYXNjYWwgcGxhdGZvcm0gcHJpdmF0ZSBwcm90ZWN0ZWQgcHVibGljIHB1Ymxpc2hlZCByZWFkIHJlZ2lzdGVyIFwiICsgXCJyZWludHJvZHVjZSByZXN1bHQgc2FmZWNhbGwgc2F2ZXJlZ2lzdGVycyBzb2Z0ZmxvYXQgc3BlY2lhbGl6ZSBzdGF0aWMgXCIgKyBcInN0ZGNhbGwgc3RvcmVkIHN0cmljdCB1bmFsaWduZWQgdW5pbXBsZW1lbnRlZCB2YXJhcmdzIHZpcnR1YWwgd3JpdGVcIik7XG52YXIgYXRvbXMgPSB7XG4gIFwibnVsbFwiOiB0cnVlXG59O1xudmFyIGlzT3BlcmF0b3JDaGFyID0gL1srXFwtKiYlPTw+IT98XFwvXS87XG5mdW5jdGlvbiB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgY2ggPSBzdHJlYW0ubmV4dCgpO1xuICBpZiAoY2ggPT0gXCIjXCIgJiYgc3RhdGUuc3RhcnRPZkxpbmUpIHtcbiAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgcmV0dXJuIFwibWV0YVwiO1xuICB9XG4gIGlmIChjaCA9PSAnXCInIHx8IGNoID09IFwiJ1wiKSB7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlblN0cmluZyhjaCk7XG4gICAgcmV0dXJuIHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICB9XG4gIGlmIChjaCA9PSBcIihcIiAmJiBzdHJlYW0uZWF0KFwiKlwiKSkge1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5Db21tZW50O1xuICAgIHJldHVybiB0b2tlbkNvbW1lbnQoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cbiAgaWYgKGNoID09IFwie1wiKSB7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkNvbW1lbnRCcmFjZXM7XG4gICAgcmV0dXJuIHRva2VuQ29tbWVudEJyYWNlcyhzdHJlYW0sIHN0YXRlKTtcbiAgfVxuICBpZiAoL1tcXFtcXF1cXChcXCksO1xcOlxcLl0vLnRlc3QoY2gpKSB7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbiAgaWYgKC9cXGQvLnRlc3QoY2gpKSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFwuXS8pO1xuICAgIHJldHVybiBcIm51bWJlclwiO1xuICB9XG4gIGlmIChjaCA9PSBcIi9cIikge1xuICAgIGlmIChzdHJlYW0uZWF0KFwiL1wiKSkge1xuICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICAgIH1cbiAgfVxuICBpZiAoaXNPcGVyYXRvckNoYXIudGVzdChjaCkpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoaXNPcGVyYXRvckNoYXIpO1xuICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gIH1cbiAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFwkX10vKTtcbiAgdmFyIGN1ciA9IHN0cmVhbS5jdXJyZW50KCkudG9Mb3dlckNhc2UoKTtcbiAgaWYgKGtleXdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIHJldHVybiBcImtleXdvcmRcIjtcbiAgaWYgKGF0b21zLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIHJldHVybiBcImF0b21cIjtcbiAgcmV0dXJuIFwidmFyaWFibGVcIjtcbn1cbmZ1bmN0aW9uIHRva2VuU3RyaW5nKHF1b3RlKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBlc2NhcGVkID0gZmFsc2UsXG4gICAgICBuZXh0LFxuICAgICAgZW5kID0gZmFsc2U7XG4gICAgd2hpbGUgKChuZXh0ID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgICAgaWYgKG5leHQgPT0gcXVvdGUgJiYgIWVzY2FwZWQpIHtcbiAgICAgICAgZW5kID0gdHJ1ZTtcbiAgICAgICAgYnJlYWs7XG4gICAgICB9XG4gICAgICBlc2NhcGVkID0gIWVzY2FwZWQgJiYgbmV4dCA9PSBcIlxcXFxcIjtcbiAgICB9XG4gICAgaWYgKGVuZCB8fCAhZXNjYXBlZCkgc3RhdGUudG9rZW5pemUgPSBudWxsO1xuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9O1xufVxuZnVuY3Rpb24gdG9rZW5Db21tZW50KHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIG1heWJlRW5kID0gZmFsc2UsXG4gICAgY2g7XG4gIHdoaWxlIChjaCA9IHN0cmVhbS5uZXh0KCkpIHtcbiAgICBpZiAoY2ggPT0gXCIpXCIgJiYgbWF5YmVFbmQpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gbnVsbDtcbiAgICAgIGJyZWFrO1xuICAgIH1cbiAgICBtYXliZUVuZCA9IGNoID09IFwiKlwiO1xuICB9XG4gIHJldHVybiBcImNvbW1lbnRcIjtcbn1cbmZ1bmN0aW9uIHRva2VuQ29tbWVudEJyYWNlcyhzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBjaDtcbiAgd2hpbGUgKGNoID0gc3RyZWFtLm5leHQoKSkge1xuICAgIGlmIChjaCA9PSBcIn1cIikge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSBudWxsO1xuICAgICAgYnJlYWs7XG4gICAgfVxuICB9XG4gIHJldHVybiBcImNvbW1lbnRcIjtcbn1cblxuLy8gSW50ZXJmYWNlXG5cbmV4cG9ydCBjb25zdCBwYXNjYWwgPSB7XG4gIG5hbWU6IFwicGFzY2FsXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgdG9rZW5pemU6IG51bGxcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHJldHVybiBudWxsO1xuICAgIHZhciBzdHlsZSA9IChzdGF0ZS50b2tlbml6ZSB8fCB0b2tlbkJhc2UpKHN0cmVhbSwgc3RhdGUpO1xuICAgIGlmIChzdHlsZSA9PSBcImNvbW1lbnRcIiB8fCBzdHlsZSA9PSBcIm1ldGFcIikgcmV0dXJuIHN0eWxlO1xuICAgIHJldHVybiBzdHlsZTtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgaW5kZW50T25JbnB1dDogL15cXHMqW3t9XSQvLFxuICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgIGJsb2NrOiB7XG4gICAgICAgIG9wZW46IFwiKCpcIixcbiAgICAgICAgY2xvc2U6IFwiKilcIlxuICAgICAgfVxuICAgIH1cbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9