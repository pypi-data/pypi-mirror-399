"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[7818],{

/***/ 97818
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   asciiArmor: () => (/* binding */ asciiArmor)
/* harmony export */ });
function errorIfNotEmpty(stream) {
  var nonWS = stream.match(/^\s*\S/);
  stream.skipToEnd();
  return nonWS ? "error" : null;
}
const asciiArmor = {
  name: "asciiarmor",
  token: function (stream, state) {
    var m;
    if (state.state == "top") {
      if (stream.sol() && (m = stream.match(/^-----BEGIN (.*)?-----\s*$/))) {
        state.state = "headers";
        state.type = m[1];
        return "tag";
      }
      return errorIfNotEmpty(stream);
    } else if (state.state == "headers") {
      if (stream.sol() && stream.match(/^\w+:/)) {
        state.state = "header";
        return "atom";
      } else {
        var result = errorIfNotEmpty(stream);
        if (result) state.state = "body";
        return result;
      }
    } else if (state.state == "header") {
      stream.skipToEnd();
      state.state = "headers";
      return "string";
    } else if (state.state == "body") {
      if (stream.sol() && (m = stream.match(/^-----END (.*)?-----\s*$/))) {
        if (m[1] != state.type) return "error";
        state.state = "end";
        return "tag";
      } else {
        if (stream.eatWhile(/[A-Za-z0-9+\/=]/)) {
          return null;
        } else {
          stream.next();
          return "error";
        }
      }
    } else if (state.state == "end") {
      return errorIfNotEmpty(stream);
    }
  },
  blankLine: function (state) {
    if (state.state == "headers") state.state = "body";
  },
  startState: function () {
    return {
      state: "top",
      type: null
    };
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNzgxOC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9hc2NpaWFybW9yLmpzIl0sInNvdXJjZXNDb250ZW50IjpbImZ1bmN0aW9uIGVycm9ySWZOb3RFbXB0eShzdHJlYW0pIHtcbiAgdmFyIG5vbldTID0gc3RyZWFtLm1hdGNoKC9eXFxzKlxcUy8pO1xuICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gIHJldHVybiBub25XUyA/IFwiZXJyb3JcIiA6IG51bGw7XG59XG5leHBvcnQgY29uc3QgYXNjaWlBcm1vciA9IHtcbiAgbmFtZTogXCJhc2NpaWFybW9yXCIsXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBtO1xuICAgIGlmIChzdGF0ZS5zdGF0ZSA9PSBcInRvcFwiKSB7XG4gICAgICBpZiAoc3RyZWFtLnNvbCgpICYmIChtID0gc3RyZWFtLm1hdGNoKC9eLS0tLS1CRUdJTiAoLiopPy0tLS0tXFxzKiQvKSkpIHtcbiAgICAgICAgc3RhdGUuc3RhdGUgPSBcImhlYWRlcnNcIjtcbiAgICAgICAgc3RhdGUudHlwZSA9IG1bMV07XG4gICAgICAgIHJldHVybiBcInRhZ1wiO1xuICAgICAgfVxuICAgICAgcmV0dXJuIGVycm9ySWZOb3RFbXB0eShzdHJlYW0pO1xuICAgIH0gZWxzZSBpZiAoc3RhdGUuc3RhdGUgPT0gXCJoZWFkZXJzXCIpIHtcbiAgICAgIGlmIChzdHJlYW0uc29sKCkgJiYgc3RyZWFtLm1hdGNoKC9eXFx3KzovKSkge1xuICAgICAgICBzdGF0ZS5zdGF0ZSA9IFwiaGVhZGVyXCI7XG4gICAgICAgIHJldHVybiBcImF0b21cIjtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIHZhciByZXN1bHQgPSBlcnJvcklmTm90RW1wdHkoc3RyZWFtKTtcbiAgICAgICAgaWYgKHJlc3VsdCkgc3RhdGUuc3RhdGUgPSBcImJvZHlcIjtcbiAgICAgICAgcmV0dXJuIHJlc3VsdDtcbiAgICAgIH1cbiAgICB9IGVsc2UgaWYgKHN0YXRlLnN0YXRlID09IFwiaGVhZGVyXCIpIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHN0YXRlLnN0YXRlID0gXCJoZWFkZXJzXCI7XG4gICAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgICB9IGVsc2UgaWYgKHN0YXRlLnN0YXRlID09IFwiYm9keVwiKSB7XG4gICAgICBpZiAoc3RyZWFtLnNvbCgpICYmIChtID0gc3RyZWFtLm1hdGNoKC9eLS0tLS1FTkQgKC4qKT8tLS0tLVxccyokLykpKSB7XG4gICAgICAgIGlmIChtWzFdICE9IHN0YXRlLnR5cGUpIHJldHVybiBcImVycm9yXCI7XG4gICAgICAgIHN0YXRlLnN0YXRlID0gXCJlbmRcIjtcbiAgICAgICAgcmV0dXJuIFwidGFnXCI7XG4gICAgICB9IGVsc2Uge1xuICAgICAgICBpZiAoc3RyZWFtLmVhdFdoaWxlKC9bQS1aYS16MC05K1xcLz1dLykpIHtcbiAgICAgICAgICByZXR1cm4gbnVsbDtcbiAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgICAgIHJldHVybiBcImVycm9yXCI7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9IGVsc2UgaWYgKHN0YXRlLnN0YXRlID09IFwiZW5kXCIpIHtcbiAgICAgIHJldHVybiBlcnJvcklmTm90RW1wdHkoc3RyZWFtKTtcbiAgICB9XG4gIH0sXG4gIGJsYW5rTGluZTogZnVuY3Rpb24gKHN0YXRlKSB7XG4gICAgaWYgKHN0YXRlLnN0YXRlID09IFwiaGVhZGVyc1wiKSBzdGF0ZS5zdGF0ZSA9IFwiYm9keVwiO1xuICB9LFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHN0YXRlOiBcInRvcFwiLFxuICAgICAgdHlwZTogbnVsbFxuICAgIH07XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==