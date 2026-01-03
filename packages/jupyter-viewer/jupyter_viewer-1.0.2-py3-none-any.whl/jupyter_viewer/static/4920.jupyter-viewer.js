"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[4920],{

/***/ 94920
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   z80: () => (/* binding */ z80)
/* harmony export */ });
/* unused harmony export ez80 */
function mkZ80(ez80) {
  var keywords1, keywords2;
  if (ez80) {
    keywords1 = /^(exx?|(ld|cp)([di]r?)?|[lp]ea|pop|push|ad[cd]|cpl|daa|dec|inc|neg|sbc|sub|and|bit|[cs]cf|x?or|res|set|r[lr]c?a?|r[lr]d|s[lr]a|srl|djnz|nop|[de]i|halt|im|in([di]mr?|ir?|irx|2r?)|ot(dmr?|[id]rx|imr?)|out(0?|[di]r?|[di]2r?)|tst(io)?|slp)(\.([sl]?i)?[sl])?\b/i;
    keywords2 = /^(((call|j[pr]|rst|ret[in]?)(\.([sl]?i)?[sl])?)|(rs|st)mix)\b/i;
  } else {
    keywords1 = /^(exx?|(ld|cp|in)([di]r?)?|pop|push|ad[cd]|cpl|daa|dec|inc|neg|sbc|sub|and|bit|[cs]cf|x?or|res|set|r[lr]c?a?|r[lr]d|s[lr]a|srl|djnz|nop|rst|[de]i|halt|im|ot[di]r|out[di]?)\b/i;
    keywords2 = /^(call|j[pr]|ret[in]?|b_?(call|jump))\b/i;
  }
  var variables1 = /^(af?|bc?|c|de?|e|hl?|l|i[xy]?|r|sp)\b/i;
  var variables2 = /^(n?[zc]|p[oe]?|m)\b/i;
  var errors = /^([hl][xy]|i[xy][hl]|slia|sll)\b/i;
  var numbers = /^([\da-f]+h|[0-7]+o|[01]+b|\d+d?)\b/i;
  return {
    name: "z80",
    startState: function () {
      return {
        context: 0
      };
    },
    token: function (stream, state) {
      if (!stream.column()) state.context = 0;
      if (stream.eatSpace()) return null;
      var w;
      if (stream.eatWhile(/\w/)) {
        if (ez80 && stream.eat('.')) {
          stream.eatWhile(/\w/);
        }
        w = stream.current();
        if (stream.indentation()) {
          if ((state.context == 1 || state.context == 4) && variables1.test(w)) {
            state.context = 4;
            return 'variable';
          }
          if (state.context == 2 && variables2.test(w)) {
            state.context = 4;
            return 'variableName.special';
          }
          if (keywords1.test(w)) {
            state.context = 1;
            return 'keyword';
          } else if (keywords2.test(w)) {
            state.context = 2;
            return 'keyword';
          } else if (state.context == 4 && numbers.test(w)) {
            return 'number';
          }
          if (errors.test(w)) return 'error';
        } else if (stream.match(numbers)) {
          return 'number';
        } else {
          return null;
        }
      } else if (stream.eat(';')) {
        stream.skipToEnd();
        return 'comment';
      } else if (stream.eat('"')) {
        while (w = stream.next()) {
          if (w == '"') break;
          if (w == '\\') stream.next();
        }
        return 'string';
      } else if (stream.eat('\'')) {
        if (stream.match(/\\?.'/)) return 'number';
      } else if (stream.eat('.') || stream.sol() && stream.eat('#')) {
        state.context = 5;
        if (stream.eatWhile(/\w/)) return 'def';
      } else if (stream.eat('$')) {
        if (stream.eatWhile(/[\da-f]/i)) return 'number';
      } else if (stream.eat('%')) {
        if (stream.eatWhile(/[01]/)) return 'number';
      } else {
        stream.next();
      }
      return null;
    }
  };
}
;
const z80 = mkZ80(false);
const ez80 = mkZ80(true);

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNDkyMC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS96ODAuanMiXSwic291cmNlc0NvbnRlbnQiOlsiZnVuY3Rpb24gbWtaODAoZXo4MCkge1xuICB2YXIga2V5d29yZHMxLCBrZXl3b3JkczI7XG4gIGlmIChlejgwKSB7XG4gICAga2V5d29yZHMxID0gL14oZXh4P3wobGR8Y3ApKFtkaV1yPyk/fFtscF1lYXxwb3B8cHVzaHxhZFtjZF18Y3BsfGRhYXxkZWN8aW5jfG5lZ3xzYmN8c3VifGFuZHxiaXR8W2NzXWNmfHg/b3J8cmVzfHNldHxyW2xyXWM/YT98cltscl1kfHNbbHJdYXxzcmx8ZGpuenxub3B8W2RlXWl8aGFsdHxpbXxpbihbZGldbXI/fGlyP3xpcnh8MnI/KXxvdChkbXI/fFtpZF1yeHxpbXI/KXxvdXQoMD98W2RpXXI/fFtkaV0ycj8pfHRzdChpbyk/fHNscCkoXFwuKFtzbF0/aSk/W3NsXSk/XFxiL2k7XG4gICAga2V5d29yZHMyID0gL14oKChjYWxsfGpbcHJdfHJzdHxyZXRbaW5dPykoXFwuKFtzbF0/aSk/W3NsXSk/KXwocnN8c3QpbWl4KVxcYi9pO1xuICB9IGVsc2Uge1xuICAgIGtleXdvcmRzMSA9IC9eKGV4eD98KGxkfGNwfGluKShbZGldcj8pP3xwb3B8cHVzaHxhZFtjZF18Y3BsfGRhYXxkZWN8aW5jfG5lZ3xzYmN8c3VifGFuZHxiaXR8W2NzXWNmfHg/b3J8cmVzfHNldHxyW2xyXWM/YT98cltscl1kfHNbbHJdYXxzcmx8ZGpuenxub3B8cnN0fFtkZV1pfGhhbHR8aW18b3RbZGldcnxvdXRbZGldPylcXGIvaTtcbiAgICBrZXl3b3JkczIgPSAvXihjYWxsfGpbcHJdfHJldFtpbl0/fGJfPyhjYWxsfGp1bXApKVxcYi9pO1xuICB9XG4gIHZhciB2YXJpYWJsZXMxID0gL14oYWY/fGJjP3xjfGRlP3xlfGhsP3xsfGlbeHldP3xyfHNwKVxcYi9pO1xuICB2YXIgdmFyaWFibGVzMiA9IC9eKG4/W3pjXXxwW29lXT98bSlcXGIvaTtcbiAgdmFyIGVycm9ycyA9IC9eKFtobF1beHldfGlbeHldW2hsXXxzbGlhfHNsbClcXGIvaTtcbiAgdmFyIG51bWJlcnMgPSAvXihbXFxkYS1mXStofFswLTddK298WzAxXStifFxcZCtkPylcXGIvaTtcbiAgcmV0dXJuIHtcbiAgICBuYW1lOiBcIno4MFwiLFxuICAgIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICAgIHJldHVybiB7XG4gICAgICAgIGNvbnRleHQ6IDBcbiAgICAgIH07XG4gICAgfSxcbiAgICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICAgIGlmICghc3RyZWFtLmNvbHVtbigpKSBzdGF0ZS5jb250ZXh0ID0gMDtcbiAgICAgIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkgcmV0dXJuIG51bGw7XG4gICAgICB2YXIgdztcbiAgICAgIGlmIChzdHJlYW0uZWF0V2hpbGUoL1xcdy8pKSB7XG4gICAgICAgIGlmIChlejgwICYmIHN0cmVhbS5lYXQoJy4nKSkge1xuICAgICAgICAgIHN0cmVhbS5lYXRXaGlsZSgvXFx3Lyk7XG4gICAgICAgIH1cbiAgICAgICAgdyA9IHN0cmVhbS5jdXJyZW50KCk7XG4gICAgICAgIGlmIChzdHJlYW0uaW5kZW50YXRpb24oKSkge1xuICAgICAgICAgIGlmICgoc3RhdGUuY29udGV4dCA9PSAxIHx8IHN0YXRlLmNvbnRleHQgPT0gNCkgJiYgdmFyaWFibGVzMS50ZXN0KHcpKSB7XG4gICAgICAgICAgICBzdGF0ZS5jb250ZXh0ID0gNDtcbiAgICAgICAgICAgIHJldHVybiAndmFyaWFibGUnO1xuICAgICAgICAgIH1cbiAgICAgICAgICBpZiAoc3RhdGUuY29udGV4dCA9PSAyICYmIHZhcmlhYmxlczIudGVzdCh3KSkge1xuICAgICAgICAgICAgc3RhdGUuY29udGV4dCA9IDQ7XG4gICAgICAgICAgICByZXR1cm4gJ3ZhcmlhYmxlTmFtZS5zcGVjaWFsJztcbiAgICAgICAgICB9XG4gICAgICAgICAgaWYgKGtleXdvcmRzMS50ZXN0KHcpKSB7XG4gICAgICAgICAgICBzdGF0ZS5jb250ZXh0ID0gMTtcbiAgICAgICAgICAgIHJldHVybiAna2V5d29yZCc7XG4gICAgICAgICAgfSBlbHNlIGlmIChrZXl3b3JkczIudGVzdCh3KSkge1xuICAgICAgICAgICAgc3RhdGUuY29udGV4dCA9IDI7XG4gICAgICAgICAgICByZXR1cm4gJ2tleXdvcmQnO1xuICAgICAgICAgIH0gZWxzZSBpZiAoc3RhdGUuY29udGV4dCA9PSA0ICYmIG51bWJlcnMudGVzdCh3KSkge1xuICAgICAgICAgICAgcmV0dXJuICdudW1iZXInO1xuICAgICAgICAgIH1cbiAgICAgICAgICBpZiAoZXJyb3JzLnRlc3QodykpIHJldHVybiAnZXJyb3InO1xuICAgICAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaChudW1iZXJzKSkge1xuICAgICAgICAgIHJldHVybiAnbnVtYmVyJztcbiAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICByZXR1cm4gbnVsbDtcbiAgICAgICAgfVxuICAgICAgfSBlbHNlIGlmIChzdHJlYW0uZWF0KCc7JykpIHtcbiAgICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgICByZXR1cm4gJ2NvbW1lbnQnO1xuICAgICAgfSBlbHNlIGlmIChzdHJlYW0uZWF0KCdcIicpKSB7XG4gICAgICAgIHdoaWxlICh3ID0gc3RyZWFtLm5leHQoKSkge1xuICAgICAgICAgIGlmICh3ID09ICdcIicpIGJyZWFrO1xuICAgICAgICAgIGlmICh3ID09ICdcXFxcJykgc3RyZWFtLm5leHQoKTtcbiAgICAgICAgfVxuICAgICAgICByZXR1cm4gJ3N0cmluZyc7XG4gICAgICB9IGVsc2UgaWYgKHN0cmVhbS5lYXQoJ1xcJycpKSB7XG4gICAgICAgIGlmIChzdHJlYW0ubWF0Y2goL1xcXFw/LicvKSkgcmV0dXJuICdudW1iZXInO1xuICAgICAgfSBlbHNlIGlmIChzdHJlYW0uZWF0KCcuJykgfHwgc3RyZWFtLnNvbCgpICYmIHN0cmVhbS5lYXQoJyMnKSkge1xuICAgICAgICBzdGF0ZS5jb250ZXh0ID0gNTtcbiAgICAgICAgaWYgKHN0cmVhbS5lYXRXaGlsZSgvXFx3LykpIHJldHVybiAnZGVmJztcbiAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLmVhdCgnJCcpKSB7XG4gICAgICAgIGlmIChzdHJlYW0uZWF0V2hpbGUoL1tcXGRhLWZdL2kpKSByZXR1cm4gJ251bWJlcic7XG4gICAgICB9IGVsc2UgaWYgKHN0cmVhbS5lYXQoJyUnKSkge1xuICAgICAgICBpZiAoc3RyZWFtLmVhdFdoaWxlKC9bMDFdLykpIHJldHVybiAnbnVtYmVyJztcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICB9XG4gICAgICByZXR1cm4gbnVsbDtcbiAgICB9XG4gIH07XG59XG47XG5leHBvcnQgY29uc3QgejgwID0gbWtaODAoZmFsc2UpO1xuZXhwb3J0IGNvbnN0IGV6ODAgPSBta1o4MCh0cnVlKTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9