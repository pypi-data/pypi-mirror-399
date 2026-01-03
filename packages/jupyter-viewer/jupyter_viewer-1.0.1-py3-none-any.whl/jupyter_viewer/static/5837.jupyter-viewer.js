"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[5837],{

/***/ 95837
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   properties: () => (/* binding */ properties)
/* harmony export */ });
const properties = {
  name: "properties",
  token: function (stream, state) {
    var sol = stream.sol() || state.afterSection;
    var eol = stream.eol();
    state.afterSection = false;
    if (sol) {
      if (state.nextMultiline) {
        state.inMultiline = true;
        state.nextMultiline = false;
      } else {
        state.position = "def";
      }
    }
    if (eol && !state.nextMultiline) {
      state.inMultiline = false;
      state.position = "def";
    }
    if (sol) {
      while (stream.eatSpace()) {}
    }
    var ch = stream.next();
    if (sol && (ch === "#" || ch === "!" || ch === ";")) {
      state.position = "comment";
      stream.skipToEnd();
      return "comment";
    } else if (sol && ch === "[") {
      state.afterSection = true;
      stream.skipTo("]");
      stream.eat("]");
      return "header";
    } else if (ch === "=" || ch === ":") {
      state.position = "quote";
      return null;
    } else if (ch === "\\" && state.position === "quote") {
      if (stream.eol()) {
        // end of line?
        // Multiline value
        state.nextMultiline = true;
      }
    }
    return state.position;
  },
  startState: function () {
    return {
      position: "def",
      // Current position, "def", "quote" or "comment"
      nextMultiline: false,
      // Is the next line multiline value
      inMultiline: false,
      // Is the current line a multiline value
      afterSection: false // Did we just open a section
    };
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNTgzNy5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvcHJvcGVydGllcy5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJleHBvcnQgY29uc3QgcHJvcGVydGllcyA9IHtcbiAgbmFtZTogXCJwcm9wZXJ0aWVzXCIsXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBzb2wgPSBzdHJlYW0uc29sKCkgfHwgc3RhdGUuYWZ0ZXJTZWN0aW9uO1xuICAgIHZhciBlb2wgPSBzdHJlYW0uZW9sKCk7XG4gICAgc3RhdGUuYWZ0ZXJTZWN0aW9uID0gZmFsc2U7XG4gICAgaWYgKHNvbCkge1xuICAgICAgaWYgKHN0YXRlLm5leHRNdWx0aWxpbmUpIHtcbiAgICAgICAgc3RhdGUuaW5NdWx0aWxpbmUgPSB0cnVlO1xuICAgICAgICBzdGF0ZS5uZXh0TXVsdGlsaW5lID0gZmFsc2U7XG4gICAgICB9IGVsc2Uge1xuICAgICAgICBzdGF0ZS5wb3NpdGlvbiA9IFwiZGVmXCI7XG4gICAgICB9XG4gICAgfVxuICAgIGlmIChlb2wgJiYgIXN0YXRlLm5leHRNdWx0aWxpbmUpIHtcbiAgICAgIHN0YXRlLmluTXVsdGlsaW5lID0gZmFsc2U7XG4gICAgICBzdGF0ZS5wb3NpdGlvbiA9IFwiZGVmXCI7XG4gICAgfVxuICAgIGlmIChzb2wpIHtcbiAgICAgIHdoaWxlIChzdHJlYW0uZWF0U3BhY2UoKSkge31cbiAgICB9XG4gICAgdmFyIGNoID0gc3RyZWFtLm5leHQoKTtcbiAgICBpZiAoc29sICYmIChjaCA9PT0gXCIjXCIgfHwgY2ggPT09IFwiIVwiIHx8IGNoID09PSBcIjtcIikpIHtcbiAgICAgIHN0YXRlLnBvc2l0aW9uID0gXCJjb21tZW50XCI7XG4gICAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgfSBlbHNlIGlmIChzb2wgJiYgY2ggPT09IFwiW1wiKSB7XG4gICAgICBzdGF0ZS5hZnRlclNlY3Rpb24gPSB0cnVlO1xuICAgICAgc3RyZWFtLnNraXBUbyhcIl1cIik7XG4gICAgICBzdHJlYW0uZWF0KFwiXVwiKTtcbiAgICAgIHJldHVybiBcImhlYWRlclwiO1xuICAgIH0gZWxzZSBpZiAoY2ggPT09IFwiPVwiIHx8IGNoID09PSBcIjpcIikge1xuICAgICAgc3RhdGUucG9zaXRpb24gPSBcInF1b3RlXCI7XG4gICAgICByZXR1cm4gbnVsbDtcbiAgICB9IGVsc2UgaWYgKGNoID09PSBcIlxcXFxcIiAmJiBzdGF0ZS5wb3NpdGlvbiA9PT0gXCJxdW90ZVwiKSB7XG4gICAgICBpZiAoc3RyZWFtLmVvbCgpKSB7XG4gICAgICAgIC8vIGVuZCBvZiBsaW5lP1xuICAgICAgICAvLyBNdWx0aWxpbmUgdmFsdWVcbiAgICAgICAgc3RhdGUubmV4dE11bHRpbGluZSA9IHRydWU7XG4gICAgICB9XG4gICAgfVxuICAgIHJldHVybiBzdGF0ZS5wb3NpdGlvbjtcbiAgfSxcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB7XG4gICAgICBwb3NpdGlvbjogXCJkZWZcIixcbiAgICAgIC8vIEN1cnJlbnQgcG9zaXRpb24sIFwiZGVmXCIsIFwicXVvdGVcIiBvciBcImNvbW1lbnRcIlxuICAgICAgbmV4dE11bHRpbGluZTogZmFsc2UsXG4gICAgICAvLyBJcyB0aGUgbmV4dCBsaW5lIG11bHRpbGluZSB2YWx1ZVxuICAgICAgaW5NdWx0aWxpbmU6IGZhbHNlLFxuICAgICAgLy8gSXMgdGhlIGN1cnJlbnQgbGluZSBhIG11bHRpbGluZSB2YWx1ZVxuICAgICAgYWZ0ZXJTZWN0aW9uOiBmYWxzZSAvLyBEaWQgd2UganVzdCBvcGVuIGEgc2VjdGlvblxuICAgIH07XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==