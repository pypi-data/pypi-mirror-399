"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[4183],{

/***/ 44183
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   diff: () => (/* binding */ diff)
/* harmony export */ });
var TOKEN_NAMES = {
  '+': 'inserted',
  '-': 'deleted',
  '@': 'meta'
};
const diff = {
  name: "diff",
  token: function (stream) {
    var tw_pos = stream.string.search(/[\t ]+?$/);
    if (!stream.sol() || tw_pos === 0) {
      stream.skipToEnd();
      return ("error " + (TOKEN_NAMES[stream.string.charAt(0)] || '')).replace(/ $/, '');
    }
    var token_name = TOKEN_NAMES[stream.peek()] || stream.skipToEnd();
    if (tw_pos === -1) {
      stream.skipToEnd();
    } else {
      stream.pos = tw_pos;
    }
    return token_name;
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNDE4My5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvZGlmZi5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJ2YXIgVE9LRU5fTkFNRVMgPSB7XG4gICcrJzogJ2luc2VydGVkJyxcbiAgJy0nOiAnZGVsZXRlZCcsXG4gICdAJzogJ21ldGEnXG59O1xuZXhwb3J0IGNvbnN0IGRpZmYgPSB7XG4gIG5hbWU6IFwiZGlmZlwiLFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSkge1xuICAgIHZhciB0d19wb3MgPSBzdHJlYW0uc3RyaW5nLnNlYXJjaCgvW1xcdCBdKz8kLyk7XG4gICAgaWYgKCFzdHJlYW0uc29sKCkgfHwgdHdfcG9zID09PSAwKSB7XG4gICAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgICByZXR1cm4gKFwiZXJyb3IgXCIgKyAoVE9LRU5fTkFNRVNbc3RyZWFtLnN0cmluZy5jaGFyQXQoMCldIHx8ICcnKSkucmVwbGFjZSgvICQvLCAnJyk7XG4gICAgfVxuICAgIHZhciB0b2tlbl9uYW1lID0gVE9LRU5fTkFNRVNbc3RyZWFtLnBlZWsoKV0gfHwgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgIGlmICh0d19wb3MgPT09IC0xKSB7XG4gICAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgfSBlbHNlIHtcbiAgICAgIHN0cmVhbS5wb3MgPSB0d19wb3M7XG4gICAgfVxuICAgIHJldHVybiB0b2tlbl9uYW1lO1xuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=