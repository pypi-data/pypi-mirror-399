"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[5043],{

/***/ 35043
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   rpmChanges: () => (/* binding */ rpmChanges),
/* harmony export */   rpmSpec: () => (/* binding */ rpmSpec)
/* harmony export */ });
var headerSeparator = /^-+$/;
var headerLine = /^(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)  ?\d{1,2} \d{2}:\d{2}(:\d{2})? [A-Z]{3,4} \d{4} - /;
var simpleEmail = /^[\w+.-]+@[\w.-]+/;
const rpmChanges = {
  name: "rpmchanges",
  token: function (stream) {
    if (stream.sol()) {
      if (stream.match(headerSeparator)) {
        return 'tag';
      }
      if (stream.match(headerLine)) {
        return 'tag';
      }
    }
    if (stream.match(simpleEmail)) {
      return 'string';
    }
    stream.next();
    return null;
  }
};

// Quick and dirty spec file highlighting

var arch = /^(i386|i586|i686|x86_64|ppc64le|ppc64|ppc|ia64|s390x|s390|sparc64|sparcv9|sparc|noarch|alphaev6|alpha|hppa|mipsel)/;
var preamble = /^[a-zA-Z0-9()]+:/;
var section = /^%(debug_package|package|description|prep|build|install|files|clean|changelog|preinstall|preun|postinstall|postun|pretrans|posttrans|pre|post|triggerin|triggerun|verifyscript|check|triggerpostun|triggerprein|trigger)/;
var control_flow_complex = /^%(ifnarch|ifarch|if)/; // rpm control flow macros
var control_flow_simple = /^%(else|endif)/; // rpm control flow macros
var operators = /^(\!|\?|\<\=|\<|\>\=|\>|\=\=|\&\&|\|\|)/; // operators in control flow macros

const rpmSpec = {
  name: "rpmspec",
  startState: function () {
    return {
      controlFlow: false,
      macroParameters: false,
      section: false
    };
  },
  token: function (stream, state) {
    var ch = stream.peek();
    if (ch == "#") {
      stream.skipToEnd();
      return "comment";
    }
    if (stream.sol()) {
      if (stream.match(preamble)) {
        return "header";
      }
      if (stream.match(section)) {
        return "atom";
      }
    }
    if (stream.match(/^\$\w+/)) {
      return "def";
    } // Variables like '$RPM_BUILD_ROOT'
    if (stream.match(/^\$\{\w+\}/)) {
      return "def";
    } // Variables like '${RPM_BUILD_ROOT}'

    if (stream.match(control_flow_simple)) {
      return "keyword";
    }
    if (stream.match(control_flow_complex)) {
      state.controlFlow = true;
      return "keyword";
    }
    if (state.controlFlow) {
      if (stream.match(operators)) {
        return "operator";
      }
      if (stream.match(/^(\d+)/)) {
        return "number";
      }
      if (stream.eol()) {
        state.controlFlow = false;
      }
    }
    if (stream.match(arch)) {
      if (stream.eol()) {
        state.controlFlow = false;
      }
      return "number";
    }

    // Macros like '%make_install' or '%attr(0775,root,root)'
    if (stream.match(/^%[\w]+/)) {
      if (stream.match('(')) {
        state.macroParameters = true;
      }
      return "keyword";
    }
    if (state.macroParameters) {
      if (stream.match(/^\d+/)) {
        return "number";
      }
      if (stream.match(')')) {
        state.macroParameters = false;
        return "keyword";
      }
    }

    // Macros like '%{defined fedora}'
    if (stream.match(/^%\{\??[\w \-\:\!]+\}/)) {
      if (stream.eol()) {
        state.controlFlow = false;
      }
      return "def";
    }
    stream.next();
    return null;
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNTA0My5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9ycG0uanMiXSwic291cmNlc0NvbnRlbnQiOlsidmFyIGhlYWRlclNlcGFyYXRvciA9IC9eLSskLztcbnZhciBoZWFkZXJMaW5lID0gL14oTW9ufFR1ZXxXZWR8VGh1fEZyaXxTYXR8U3VuKSAoSmFufEZlYnxNYXJ8QXByfE1heXxKdW58SnVsfEF1Z3xTZXB8T2N0fE5vdnxEZWMpICA/XFxkezEsMn0gXFxkezJ9OlxcZHsyfSg6XFxkezJ9KT8gW0EtWl17Myw0fSBcXGR7NH0gLSAvO1xudmFyIHNpbXBsZUVtYWlsID0gL15bXFx3Ky4tXStAW1xcdy4tXSsvO1xuZXhwb3J0IGNvbnN0IHJwbUNoYW5nZXMgPSB7XG4gIG5hbWU6IFwicnBtY2hhbmdlc1wiLFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSkge1xuICAgIGlmIChzdHJlYW0uc29sKCkpIHtcbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goaGVhZGVyU2VwYXJhdG9yKSkge1xuICAgICAgICByZXR1cm4gJ3RhZyc7XG4gICAgICB9XG4gICAgICBpZiAoc3RyZWFtLm1hdGNoKGhlYWRlckxpbmUpKSB7XG4gICAgICAgIHJldHVybiAndGFnJztcbiAgICAgIH1cbiAgICB9XG4gICAgaWYgKHN0cmVhbS5tYXRjaChzaW1wbGVFbWFpbCkpIHtcbiAgICAgIHJldHVybiAnc3RyaW5nJztcbiAgICB9XG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICByZXR1cm4gbnVsbDtcbiAgfVxufTtcblxuLy8gUXVpY2sgYW5kIGRpcnR5IHNwZWMgZmlsZSBoaWdobGlnaHRpbmdcblxudmFyIGFyY2ggPSAvXihpMzg2fGk1ODZ8aTY4Nnx4ODZfNjR8cHBjNjRsZXxwcGM2NHxwcGN8aWE2NHxzMzkweHxzMzkwfHNwYXJjNjR8c3BhcmN2OXxzcGFyY3xub2FyY2h8YWxwaGFldjZ8YWxwaGF8aHBwYXxtaXBzZWwpLztcbnZhciBwcmVhbWJsZSA9IC9eW2EtekEtWjAtOSgpXSs6LztcbnZhciBzZWN0aW9uID0gL14lKGRlYnVnX3BhY2thZ2V8cGFja2FnZXxkZXNjcmlwdGlvbnxwcmVwfGJ1aWxkfGluc3RhbGx8ZmlsZXN8Y2xlYW58Y2hhbmdlbG9nfHByZWluc3RhbGx8cHJldW58cG9zdGluc3RhbGx8cG9zdHVufHByZXRyYW5zfHBvc3R0cmFuc3xwcmV8cG9zdHx0cmlnZ2VyaW58dHJpZ2dlcnVufHZlcmlmeXNjcmlwdHxjaGVja3x0cmlnZ2VycG9zdHVufHRyaWdnZXJwcmVpbnx0cmlnZ2VyKS87XG52YXIgY29udHJvbF9mbG93X2NvbXBsZXggPSAvXiUoaWZuYXJjaHxpZmFyY2h8aWYpLzsgLy8gcnBtIGNvbnRyb2wgZmxvdyBtYWNyb3NcbnZhciBjb250cm9sX2Zsb3dfc2ltcGxlID0gL14lKGVsc2V8ZW5kaWYpLzsgLy8gcnBtIGNvbnRyb2wgZmxvdyBtYWNyb3NcbnZhciBvcGVyYXRvcnMgPSAvXihcXCF8XFw/fFxcPFxcPXxcXDx8XFw+XFw9fFxcPnxcXD1cXD18XFwmXFwmfFxcfFxcfCkvOyAvLyBvcGVyYXRvcnMgaW4gY29udHJvbCBmbG93IG1hY3Jvc1xuXG5leHBvcnQgY29uc3QgcnBtU3BlYyA9IHtcbiAgbmFtZTogXCJycG1zcGVjXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgY29udHJvbEZsb3c6IGZhbHNlLFxuICAgICAgbWFjcm9QYXJhbWV0ZXJzOiBmYWxzZSxcbiAgICAgIHNlY3Rpb246IGZhbHNlXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGNoID0gc3RyZWFtLnBlZWsoKTtcbiAgICBpZiAoY2ggPT0gXCIjXCIpIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5zb2woKSkge1xuICAgICAgaWYgKHN0cmVhbS5tYXRjaChwcmVhbWJsZSkpIHtcbiAgICAgICAgcmV0dXJuIFwiaGVhZGVyXCI7XG4gICAgICB9XG4gICAgICBpZiAoc3RyZWFtLm1hdGNoKHNlY3Rpb24pKSB7XG4gICAgICAgIHJldHVybiBcImF0b21cIjtcbiAgICAgIH1cbiAgICB9XG4gICAgaWYgKHN0cmVhbS5tYXRjaCgvXlxcJFxcdysvKSkge1xuICAgICAgcmV0dXJuIFwiZGVmXCI7XG4gICAgfSAvLyBWYXJpYWJsZXMgbGlrZSAnJFJQTV9CVUlMRF9ST09UJ1xuICAgIGlmIChzdHJlYW0ubWF0Y2goL15cXCRcXHtcXHcrXFx9LykpIHtcbiAgICAgIHJldHVybiBcImRlZlwiO1xuICAgIH0gLy8gVmFyaWFibGVzIGxpa2UgJyR7UlBNX0JVSUxEX1JPT1R9J1xuXG4gICAgaWYgKHN0cmVhbS5tYXRjaChjb250cm9sX2Zsb3dfc2ltcGxlKSkge1xuICAgICAgcmV0dXJuIFwia2V5d29yZFwiO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLm1hdGNoKGNvbnRyb2xfZmxvd19jb21wbGV4KSkge1xuICAgICAgc3RhdGUuY29udHJvbEZsb3cgPSB0cnVlO1xuICAgICAgcmV0dXJuIFwia2V5d29yZFwiO1xuICAgIH1cbiAgICBpZiAoc3RhdGUuY29udHJvbEZsb3cpIHtcbiAgICAgIGlmIChzdHJlYW0ubWF0Y2gob3BlcmF0b3JzKSkge1xuICAgICAgICByZXR1cm4gXCJvcGVyYXRvclwiO1xuICAgICAgfVxuICAgICAgaWYgKHN0cmVhbS5tYXRjaCgvXihcXGQrKS8pKSB7XG4gICAgICAgIHJldHVybiBcIm51bWJlclwiO1xuICAgICAgfVxuICAgICAgaWYgKHN0cmVhbS5lb2woKSkge1xuICAgICAgICBzdGF0ZS5jb250cm9sRmxvdyA9IGZhbHNlO1xuICAgICAgfVxuICAgIH1cbiAgICBpZiAoc3RyZWFtLm1hdGNoKGFyY2gpKSB7XG4gICAgICBpZiAoc3RyZWFtLmVvbCgpKSB7XG4gICAgICAgIHN0YXRlLmNvbnRyb2xGbG93ID0gZmFsc2U7XG4gICAgICB9XG4gICAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgICB9XG5cbiAgICAvLyBNYWNyb3MgbGlrZSAnJW1ha2VfaW5zdGFsbCcgb3IgJyVhdHRyKDA3NzUscm9vdCxyb290KSdcbiAgICBpZiAoc3RyZWFtLm1hdGNoKC9eJVtcXHddKy8pKSB7XG4gICAgICBpZiAoc3RyZWFtLm1hdGNoKCcoJykpIHtcbiAgICAgICAgc3RhdGUubWFjcm9QYXJhbWV0ZXJzID0gdHJ1ZTtcbiAgICAgIH1cbiAgICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgICB9XG4gICAgaWYgKHN0YXRlLm1hY3JvUGFyYW1ldGVycykge1xuICAgICAgaWYgKHN0cmVhbS5tYXRjaCgvXlxcZCsvKSkge1xuICAgICAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgICAgIH1cbiAgICAgIGlmIChzdHJlYW0ubWF0Y2goJyknKSkge1xuICAgICAgICBzdGF0ZS5tYWNyb1BhcmFtZXRlcnMgPSBmYWxzZTtcbiAgICAgICAgcmV0dXJuIFwia2V5d29yZFwiO1xuICAgICAgfVxuICAgIH1cblxuICAgIC8vIE1hY3JvcyBsaWtlICcle2RlZmluZWQgZmVkb3JhfSdcbiAgICBpZiAoc3RyZWFtLm1hdGNoKC9eJVxce1xcPz9bXFx3IFxcLVxcOlxcIV0rXFx9LykpIHtcbiAgICAgIGlmIChzdHJlYW0uZW9sKCkpIHtcbiAgICAgICAgc3RhdGUuY29udHJvbEZsb3cgPSBmYWxzZTtcbiAgICAgIH1cbiAgICAgIHJldHVybiBcImRlZlwiO1xuICAgIH1cbiAgICBzdHJlYW0ubmV4dCgpO1xuICAgIHJldHVybiBudWxsO1xuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=