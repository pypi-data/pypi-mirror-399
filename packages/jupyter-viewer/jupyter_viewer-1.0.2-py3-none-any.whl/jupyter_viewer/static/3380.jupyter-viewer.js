"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[3380],{

/***/ 3380
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   mbox: () => (/* binding */ mbox)
/* harmony export */ });
var rfc2822 = ["From", "Sender", "Reply-To", "To", "Cc", "Bcc", "Message-ID", "In-Reply-To", "References", "Resent-From", "Resent-Sender", "Resent-To", "Resent-Cc", "Resent-Bcc", "Resent-Message-ID", "Return-Path", "Received"];
var rfc2822NoEmail = ["Date", "Subject", "Comments", "Keywords", "Resent-Date"];
var whitespace = /^[ \t]/;
var separator = /^From /; // See RFC 4155
var rfc2822Header = new RegExp("^(" + rfc2822.join("|") + "): ");
var rfc2822HeaderNoEmail = new RegExp("^(" + rfc2822NoEmail.join("|") + "): ");
var header = /^[^:]+:/; // Optional fields defined in RFC 2822
var email = /^[^ ]+@[^ ]+/;
var untilEmail = /^.*?(?=[^ ]+?@[^ ]+)/;
var bracketedEmail = /^<.*?>/;
var untilBracketedEmail = /^.*?(?=<.*>)/;
function styleForHeader(header) {
  if (header === "Subject") return "header";
  return "string";
}
function readToken(stream, state) {
  if (stream.sol()) {
    // From last line
    state.inSeparator = false;
    if (state.inHeader && stream.match(whitespace)) {
      // Header folding
      return null;
    } else {
      state.inHeader = false;
      state.header = null;
    }
    if (stream.match(separator)) {
      state.inHeaders = true;
      state.inSeparator = true;
      return "atom";
    }
    var match;
    var emailPermitted = false;
    if ((match = stream.match(rfc2822HeaderNoEmail)) || (emailPermitted = true) && (match = stream.match(rfc2822Header))) {
      state.inHeaders = true;
      state.inHeader = true;
      state.emailPermitted = emailPermitted;
      state.header = match[1];
      return "atom";
    }

    // Use vim's heuristics: recognize custom headers only if the line is in a
    // block of legitimate headers.
    if (state.inHeaders && (match = stream.match(header))) {
      state.inHeader = true;
      state.emailPermitted = true;
      state.header = match[1];
      return "atom";
    }
    state.inHeaders = false;
    stream.skipToEnd();
    return null;
  }
  if (state.inSeparator) {
    if (stream.match(email)) return "link";
    if (stream.match(untilEmail)) return "atom";
    stream.skipToEnd();
    return "atom";
  }
  if (state.inHeader) {
    var style = styleForHeader(state.header);
    if (state.emailPermitted) {
      if (stream.match(bracketedEmail)) return style + " link";
      if (stream.match(untilBracketedEmail)) return style;
    }
    stream.skipToEnd();
    return style;
  }
  stream.skipToEnd();
  return null;
}
;
const mbox = {
  name: "mbox",
  startState: function () {
    return {
      // Is in a mbox separator
      inSeparator: false,
      // Is in a mail header
      inHeader: false,
      // If bracketed email is permitted. Only applicable when inHeader
      emailPermitted: false,
      // Name of current header
      header: null,
      // Is in a region of mail headers
      inHeaders: false
    };
  },
  token: readToken,
  blankLine: function (state) {
    state.inHeaders = state.inSeparator = state.inHeader = false;
  },
  languageData: {
    autocomplete: rfc2822.concat(rfc2822NoEmail)
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMzM4MC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL21ib3guanMiXSwic291cmNlc0NvbnRlbnQiOlsidmFyIHJmYzI4MjIgPSBbXCJGcm9tXCIsIFwiU2VuZGVyXCIsIFwiUmVwbHktVG9cIiwgXCJUb1wiLCBcIkNjXCIsIFwiQmNjXCIsIFwiTWVzc2FnZS1JRFwiLCBcIkluLVJlcGx5LVRvXCIsIFwiUmVmZXJlbmNlc1wiLCBcIlJlc2VudC1Gcm9tXCIsIFwiUmVzZW50LVNlbmRlclwiLCBcIlJlc2VudC1Ub1wiLCBcIlJlc2VudC1DY1wiLCBcIlJlc2VudC1CY2NcIiwgXCJSZXNlbnQtTWVzc2FnZS1JRFwiLCBcIlJldHVybi1QYXRoXCIsIFwiUmVjZWl2ZWRcIl07XG52YXIgcmZjMjgyMk5vRW1haWwgPSBbXCJEYXRlXCIsIFwiU3ViamVjdFwiLCBcIkNvbW1lbnRzXCIsIFwiS2V5d29yZHNcIiwgXCJSZXNlbnQtRGF0ZVwiXTtcbnZhciB3aGl0ZXNwYWNlID0gL15bIFxcdF0vO1xudmFyIHNlcGFyYXRvciA9IC9eRnJvbSAvOyAvLyBTZWUgUkZDIDQxNTVcbnZhciByZmMyODIySGVhZGVyID0gbmV3IFJlZ0V4cChcIl4oXCIgKyByZmMyODIyLmpvaW4oXCJ8XCIpICsgXCIpOiBcIik7XG52YXIgcmZjMjgyMkhlYWRlck5vRW1haWwgPSBuZXcgUmVnRXhwKFwiXihcIiArIHJmYzI4MjJOb0VtYWlsLmpvaW4oXCJ8XCIpICsgXCIpOiBcIik7XG52YXIgaGVhZGVyID0gL15bXjpdKzovOyAvLyBPcHRpb25hbCBmaWVsZHMgZGVmaW5lZCBpbiBSRkMgMjgyMlxudmFyIGVtYWlsID0gL15bXiBdK0BbXiBdKy87XG52YXIgdW50aWxFbWFpbCA9IC9eLio/KD89W14gXSs/QFteIF0rKS87XG52YXIgYnJhY2tldGVkRW1haWwgPSAvXjwuKj8+LztcbnZhciB1bnRpbEJyYWNrZXRlZEVtYWlsID0gL14uKj8oPz08Lio+KS87XG5mdW5jdGlvbiBzdHlsZUZvckhlYWRlcihoZWFkZXIpIHtcbiAgaWYgKGhlYWRlciA9PT0gXCJTdWJqZWN0XCIpIHJldHVybiBcImhlYWRlclwiO1xuICByZXR1cm4gXCJzdHJpbmdcIjtcbn1cbmZ1bmN0aW9uIHJlYWRUb2tlbihzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0uc29sKCkpIHtcbiAgICAvLyBGcm9tIGxhc3QgbGluZVxuICAgIHN0YXRlLmluU2VwYXJhdG9yID0gZmFsc2U7XG4gICAgaWYgKHN0YXRlLmluSGVhZGVyICYmIHN0cmVhbS5tYXRjaCh3aGl0ZXNwYWNlKSkge1xuICAgICAgLy8gSGVhZGVyIGZvbGRpbmdcbiAgICAgIHJldHVybiBudWxsO1xuICAgIH0gZWxzZSB7XG4gICAgICBzdGF0ZS5pbkhlYWRlciA9IGZhbHNlO1xuICAgICAgc3RhdGUuaGVhZGVyID0gbnVsbDtcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5tYXRjaChzZXBhcmF0b3IpKSB7XG4gICAgICBzdGF0ZS5pbkhlYWRlcnMgPSB0cnVlO1xuICAgICAgc3RhdGUuaW5TZXBhcmF0b3IgPSB0cnVlO1xuICAgICAgcmV0dXJuIFwiYXRvbVwiO1xuICAgIH1cbiAgICB2YXIgbWF0Y2g7XG4gICAgdmFyIGVtYWlsUGVybWl0dGVkID0gZmFsc2U7XG4gICAgaWYgKChtYXRjaCA9IHN0cmVhbS5tYXRjaChyZmMyODIySGVhZGVyTm9FbWFpbCkpIHx8IChlbWFpbFBlcm1pdHRlZCA9IHRydWUpICYmIChtYXRjaCA9IHN0cmVhbS5tYXRjaChyZmMyODIySGVhZGVyKSkpIHtcbiAgICAgIHN0YXRlLmluSGVhZGVycyA9IHRydWU7XG4gICAgICBzdGF0ZS5pbkhlYWRlciA9IHRydWU7XG4gICAgICBzdGF0ZS5lbWFpbFBlcm1pdHRlZCA9IGVtYWlsUGVybWl0dGVkO1xuICAgICAgc3RhdGUuaGVhZGVyID0gbWF0Y2hbMV07XG4gICAgICByZXR1cm4gXCJhdG9tXCI7XG4gICAgfVxuXG4gICAgLy8gVXNlIHZpbSdzIGhldXJpc3RpY3M6IHJlY29nbml6ZSBjdXN0b20gaGVhZGVycyBvbmx5IGlmIHRoZSBsaW5lIGlzIGluIGFcbiAgICAvLyBibG9jayBvZiBsZWdpdGltYXRlIGhlYWRlcnMuXG4gICAgaWYgKHN0YXRlLmluSGVhZGVycyAmJiAobWF0Y2ggPSBzdHJlYW0ubWF0Y2goaGVhZGVyKSkpIHtcbiAgICAgIHN0YXRlLmluSGVhZGVyID0gdHJ1ZTtcbiAgICAgIHN0YXRlLmVtYWlsUGVybWl0dGVkID0gdHJ1ZTtcbiAgICAgIHN0YXRlLmhlYWRlciA9IG1hdGNoWzFdO1xuICAgICAgcmV0dXJuIFwiYXRvbVwiO1xuICAgIH1cbiAgICBzdGF0ZS5pbkhlYWRlcnMgPSBmYWxzZTtcbiAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbiAgaWYgKHN0YXRlLmluU2VwYXJhdG9yKSB7XG4gICAgaWYgKHN0cmVhbS5tYXRjaChlbWFpbCkpIHJldHVybiBcImxpbmtcIjtcbiAgICBpZiAoc3RyZWFtLm1hdGNoKHVudGlsRW1haWwpKSByZXR1cm4gXCJhdG9tXCI7XG4gICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgIHJldHVybiBcImF0b21cIjtcbiAgfVxuICBpZiAoc3RhdGUuaW5IZWFkZXIpIHtcbiAgICB2YXIgc3R5bGUgPSBzdHlsZUZvckhlYWRlcihzdGF0ZS5oZWFkZXIpO1xuICAgIGlmIChzdGF0ZS5lbWFpbFBlcm1pdHRlZCkge1xuICAgICAgaWYgKHN0cmVhbS5tYXRjaChicmFja2V0ZWRFbWFpbCkpIHJldHVybiBzdHlsZSArIFwiIGxpbmtcIjtcbiAgICAgIGlmIChzdHJlYW0ubWF0Y2godW50aWxCcmFja2V0ZWRFbWFpbCkpIHJldHVybiBzdHlsZTtcbiAgICB9XG4gICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgIHJldHVybiBzdHlsZTtcbiAgfVxuICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gIHJldHVybiBudWxsO1xufVxuO1xuZXhwb3J0IGNvbnN0IG1ib3ggPSB7XG4gIG5hbWU6IFwibWJveFwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIC8vIElzIGluIGEgbWJveCBzZXBhcmF0b3JcbiAgICAgIGluU2VwYXJhdG9yOiBmYWxzZSxcbiAgICAgIC8vIElzIGluIGEgbWFpbCBoZWFkZXJcbiAgICAgIGluSGVhZGVyOiBmYWxzZSxcbiAgICAgIC8vIElmIGJyYWNrZXRlZCBlbWFpbCBpcyBwZXJtaXR0ZWQuIE9ubHkgYXBwbGljYWJsZSB3aGVuIGluSGVhZGVyXG4gICAgICBlbWFpbFBlcm1pdHRlZDogZmFsc2UsXG4gICAgICAvLyBOYW1lIG9mIGN1cnJlbnQgaGVhZGVyXG4gICAgICBoZWFkZXI6IG51bGwsXG4gICAgICAvLyBJcyBpbiBhIHJlZ2lvbiBvZiBtYWlsIGhlYWRlcnNcbiAgICAgIGluSGVhZGVyczogZmFsc2VcbiAgICB9O1xuICB9LFxuICB0b2tlbjogcmVhZFRva2VuLFxuICBibGFua0xpbmU6IGZ1bmN0aW9uIChzdGF0ZSkge1xuICAgIHN0YXRlLmluSGVhZGVycyA9IHN0YXRlLmluU2VwYXJhdG9yID0gc3RhdGUuaW5IZWFkZXIgPSBmYWxzZTtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgYXV0b2NvbXBsZXRlOiByZmMyODIyLmNvbmNhdChyZmMyODIyTm9FbWFpbClcbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9