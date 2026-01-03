"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[7945],{

/***/ 57945
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   brainfuck: () => (/* binding */ brainfuck)
/* harmony export */ });
var reserve = "><+-.,[]".split("");
/*
  comments can be either:
  placed behind lines

  +++    this is a comment

  where reserved characters cannot be used
  or in a loop
  [
  this is ok to use [ ] and stuff
  ]
  or preceded by #
*/
const brainfuck = {
  name: "brainfuck",
  startState: function () {
    return {
      commentLine: false,
      left: 0,
      right: 0,
      commentLoop: false
    };
  },
  token: function (stream, state) {
    if (stream.eatSpace()) return null;
    if (stream.sol()) {
      state.commentLine = false;
    }
    var ch = stream.next().toString();
    if (reserve.indexOf(ch) !== -1) {
      if (state.commentLine === true) {
        if (stream.eol()) {
          state.commentLine = false;
        }
        return "comment";
      }
      if (ch === "]" || ch === "[") {
        if (ch === "[") {
          state.left++;
        } else {
          state.right++;
        }
        return "bracket";
      } else if (ch === "+" || ch === "-") {
        return "keyword";
      } else if (ch === "<" || ch === ">") {
        return "atom";
      } else if (ch === "." || ch === ",") {
        return "def";
      }
    } else {
      state.commentLine = true;
      if (stream.eol()) {
        state.commentLine = false;
      }
      return "comment";
    }
    if (stream.eol()) {
      state.commentLine = false;
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNzk0NS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL2JyYWluZnVjay5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJ2YXIgcmVzZXJ2ZSA9IFwiPjwrLS4sW11cIi5zcGxpdChcIlwiKTtcbi8qXG4gIGNvbW1lbnRzIGNhbiBiZSBlaXRoZXI6XG4gIHBsYWNlZCBiZWhpbmQgbGluZXNcblxuICArKysgICAgdGhpcyBpcyBhIGNvbW1lbnRcblxuICB3aGVyZSByZXNlcnZlZCBjaGFyYWN0ZXJzIGNhbm5vdCBiZSB1c2VkXG4gIG9yIGluIGEgbG9vcFxuICBbXG4gIHRoaXMgaXMgb2sgdG8gdXNlIFsgXSBhbmQgc3R1ZmZcbiAgXVxuICBvciBwcmVjZWRlZCBieSAjXG4qL1xuZXhwb3J0IGNvbnN0IGJyYWluZnVjayA9IHtcbiAgbmFtZTogXCJicmFpbmZ1Y2tcIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB7XG4gICAgICBjb21tZW50TGluZTogZmFsc2UsXG4gICAgICBsZWZ0OiAwLFxuICAgICAgcmlnaHQ6IDAsXG4gICAgICBjb21tZW50TG9vcDogZmFsc2VcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHJldHVybiBudWxsO1xuICAgIGlmIChzdHJlYW0uc29sKCkpIHtcbiAgICAgIHN0YXRlLmNvbW1lbnRMaW5lID0gZmFsc2U7XG4gICAgfVxuICAgIHZhciBjaCA9IHN0cmVhbS5uZXh0KCkudG9TdHJpbmcoKTtcbiAgICBpZiAocmVzZXJ2ZS5pbmRleE9mKGNoKSAhPT0gLTEpIHtcbiAgICAgIGlmIChzdGF0ZS5jb21tZW50TGluZSA9PT0gdHJ1ZSkge1xuICAgICAgICBpZiAoc3RyZWFtLmVvbCgpKSB7XG4gICAgICAgICAgc3RhdGUuY29tbWVudExpbmUgPSBmYWxzZTtcbiAgICAgICAgfVxuICAgICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgICB9XG4gICAgICBpZiAoY2ggPT09IFwiXVwiIHx8IGNoID09PSBcIltcIikge1xuICAgICAgICBpZiAoY2ggPT09IFwiW1wiKSB7XG4gICAgICAgICAgc3RhdGUubGVmdCsrO1xuICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgIHN0YXRlLnJpZ2h0Kys7XG4gICAgICAgIH1cbiAgICAgICAgcmV0dXJuIFwiYnJhY2tldFwiO1xuICAgICAgfSBlbHNlIGlmIChjaCA9PT0gXCIrXCIgfHwgY2ggPT09IFwiLVwiKSB7XG4gICAgICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgICAgIH0gZWxzZSBpZiAoY2ggPT09IFwiPFwiIHx8IGNoID09PSBcIj5cIikge1xuICAgICAgICByZXR1cm4gXCJhdG9tXCI7XG4gICAgICB9IGVsc2UgaWYgKGNoID09PSBcIi5cIiB8fCBjaCA9PT0gXCIsXCIpIHtcbiAgICAgICAgcmV0dXJuIFwiZGVmXCI7XG4gICAgICB9XG4gICAgfSBlbHNlIHtcbiAgICAgIHN0YXRlLmNvbW1lbnRMaW5lID0gdHJ1ZTtcbiAgICAgIGlmIChzdHJlYW0uZW9sKCkpIHtcbiAgICAgICAgc3RhdGUuY29tbWVudExpbmUgPSBmYWxzZTtcbiAgICAgIH1cbiAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5lb2woKSkge1xuICAgICAgc3RhdGUuY29tbWVudExpbmUgPSBmYWxzZTtcbiAgICB9XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==