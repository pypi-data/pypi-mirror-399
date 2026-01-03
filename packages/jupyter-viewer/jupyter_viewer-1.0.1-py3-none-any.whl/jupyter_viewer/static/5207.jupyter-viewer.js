"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[5207],{

/***/ 45207
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   protobuf: () => (/* binding */ protobuf)
/* harmony export */ });
function wordRegexp(words) {
  return new RegExp("^((" + words.join(")|(") + "))\\b", "i");
}
;
var keywordArray = ["package", "message", "import", "syntax", "required", "optional", "repeated", "reserved", "default", "extensions", "packed", "bool", "bytes", "double", "enum", "float", "string", "int32", "int64", "uint32", "uint64", "sint32", "sint64", "fixed32", "fixed64", "sfixed32", "sfixed64", "option", "service", "rpc", "returns"];
var keywords = wordRegexp(keywordArray);
var identifiers = new RegExp("^[_A-Za-z\xa1-\uffff][_A-Za-z0-9\xa1-\uffff]*");
function tokenBase(stream) {
  // whitespaces
  if (stream.eatSpace()) return null;

  // Handle one line Comments
  if (stream.match("//")) {
    stream.skipToEnd();
    return "comment";
  }

  // Handle Number Literals
  if (stream.match(/^[0-9\.+-]/, false)) {
    if (stream.match(/^[+-]?0x[0-9a-fA-F]+/)) return "number";
    if (stream.match(/^[+-]?\d*\.\d+([EeDd][+-]?\d+)?/)) return "number";
    if (stream.match(/^[+-]?\d+([EeDd][+-]?\d+)?/)) return "number";
  }

  // Handle Strings
  if (stream.match(/^"([^"]|(""))*"/)) {
    return "string";
  }
  if (stream.match(/^'([^']|(''))*'/)) {
    return "string";
  }

  // Handle words
  if (stream.match(keywords)) {
    return "keyword";
  }
  if (stream.match(identifiers)) {
    return "variable";
  }
  ;

  // Handle non-detected items
  stream.next();
  return null;
}
;
const protobuf = {
  name: "protobuf",
  token: tokenBase,
  languageData: {
    autocomplete: keywordArray
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNTIwNy5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9wcm90b2J1Zi5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiB3b3JkUmVnZXhwKHdvcmRzKSB7XG4gIHJldHVybiBuZXcgUmVnRXhwKFwiXigoXCIgKyB3b3Jkcy5qb2luKFwiKXwoXCIpICsgXCIpKVxcXFxiXCIsIFwiaVwiKTtcbn1cbjtcbnZhciBrZXl3b3JkQXJyYXkgPSBbXCJwYWNrYWdlXCIsIFwibWVzc2FnZVwiLCBcImltcG9ydFwiLCBcInN5bnRheFwiLCBcInJlcXVpcmVkXCIsIFwib3B0aW9uYWxcIiwgXCJyZXBlYXRlZFwiLCBcInJlc2VydmVkXCIsIFwiZGVmYXVsdFwiLCBcImV4dGVuc2lvbnNcIiwgXCJwYWNrZWRcIiwgXCJib29sXCIsIFwiYnl0ZXNcIiwgXCJkb3VibGVcIiwgXCJlbnVtXCIsIFwiZmxvYXRcIiwgXCJzdHJpbmdcIiwgXCJpbnQzMlwiLCBcImludDY0XCIsIFwidWludDMyXCIsIFwidWludDY0XCIsIFwic2ludDMyXCIsIFwic2ludDY0XCIsIFwiZml4ZWQzMlwiLCBcImZpeGVkNjRcIiwgXCJzZml4ZWQzMlwiLCBcInNmaXhlZDY0XCIsIFwib3B0aW9uXCIsIFwic2VydmljZVwiLCBcInJwY1wiLCBcInJldHVybnNcIl07XG52YXIga2V5d29yZHMgPSB3b3JkUmVnZXhwKGtleXdvcmRBcnJheSk7XG52YXIgaWRlbnRpZmllcnMgPSBuZXcgUmVnRXhwKFwiXltfQS1aYS16XFx4YTEtXFx1ZmZmZl1bX0EtWmEtejAtOVxceGExLVxcdWZmZmZdKlwiKTtcbmZ1bmN0aW9uIHRva2VuQmFzZShzdHJlYW0pIHtcbiAgLy8gd2hpdGVzcGFjZXNcbiAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcblxuICAvLyBIYW5kbGUgb25lIGxpbmUgQ29tbWVudHNcbiAgaWYgKHN0cmVhbS5tYXRjaChcIi8vXCIpKSB7XG4gICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgfVxuXG4gIC8vIEhhbmRsZSBOdW1iZXIgTGl0ZXJhbHNcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXlswLTlcXC4rLV0vLCBmYWxzZSkpIHtcbiAgICBpZiAoc3RyZWFtLm1hdGNoKC9eWystXT8weFswLTlhLWZBLUZdKy8pKSByZXR1cm4gXCJudW1iZXJcIjtcbiAgICBpZiAoc3RyZWFtLm1hdGNoKC9eWystXT9cXGQqXFwuXFxkKyhbRWVEZF1bKy1dP1xcZCspPy8pKSByZXR1cm4gXCJudW1iZXJcIjtcbiAgICBpZiAoc3RyZWFtLm1hdGNoKC9eWystXT9cXGQrKFtFZURkXVsrLV0/XFxkKyk/LykpIHJldHVybiBcIm51bWJlclwiO1xuICB9XG5cbiAgLy8gSGFuZGxlIFN0cmluZ3NcbiAgaWYgKHN0cmVhbS5tYXRjaCgvXlwiKFteXCJdfChcIlwiKSkqXCIvKSkge1xuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9XG4gIGlmIChzdHJlYW0ubWF0Y2goL14nKFteJ118KCcnKSkqJy8pKSB7XG4gICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gIH1cblxuICAvLyBIYW5kbGUgd29yZHNcbiAgaWYgKHN0cmVhbS5tYXRjaChrZXl3b3JkcykpIHtcbiAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gIH1cbiAgaWYgKHN0cmVhbS5tYXRjaChpZGVudGlmaWVycykpIHtcbiAgICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xuICB9XG4gIDtcblxuICAvLyBIYW5kbGUgbm9uLWRldGVjdGVkIGl0ZW1zXG4gIHN0cmVhbS5uZXh0KCk7XG4gIHJldHVybiBudWxsO1xufVxuO1xuZXhwb3J0IGNvbnN0IHByb3RvYnVmID0ge1xuICBuYW1lOiBcInByb3RvYnVmXCIsXG4gIHRva2VuOiB0b2tlbkJhc2UsXG4gIGxhbmd1YWdlRGF0YToge1xuICAgIGF1dG9jb21wbGV0ZToga2V5d29yZEFycmF5XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==