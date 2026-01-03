"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[7542],{

/***/ 87542
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ecl: () => (/* binding */ ecl)
/* harmony export */ });
function words(str) {
  var obj = {},
    words = str.split(" ");
  for (var i = 0; i < words.length; ++i) obj[words[i]] = true;
  return obj;
}
function metaHook(stream, state) {
  if (!state.startOfLine) return false;
  stream.skipToEnd();
  return "meta";
}
var keyword = words("abs acos allnodes ascii asin asstring atan atan2 ave case choose choosen choosesets clustersize combine correlation cos cosh count covariance cron dataset dedup define denormalize distribute distributed distribution ebcdic enth error evaluate event eventextra eventname exists exp failcode failmessage fetch fromunicode getisvalid global graph group hash hash32 hash64 hashcrc hashmd5 having if index intformat isvalid iterate join keyunicode length library limit ln local log loop map matched matchlength matchposition matchtext matchunicode max merge mergejoin min nolocal nonempty normalize parse pipe power preload process project pull random range rank ranked realformat recordof regexfind regexreplace regroup rejected rollup round roundup row rowdiff sample set sin sinh sizeof soapcall sort sorted sqrt stepped stored sum table tan tanh thisnode topn tounicode transfer trim truncate typeof ungroup unicodeorder variance which workunit xmldecode xmlencode xmltext xmlunicode");
var variable = words("apply assert build buildindex evaluate fail keydiff keypatch loadxml nothor notify output parallel sequential soapcall wait");
var variable_2 = words("__compressed__ all and any as atmost before beginc++ best between case const counter csv descend encrypt end endc++ endmacro except exclusive expire export extend false few first flat from full function group header heading hole ifblock import in interface joined keep keyed last left limit load local locale lookup macro many maxcount maxlength min skew module named nocase noroot noscan nosort not of only opt or outer overwrite packed partition penalty physicallength pipe quote record relationship repeat return right scan self separator service shared skew skip sql store terminator thor threshold token transform trim true type unicodeorder unsorted validate virtual whole wild within xml xpath");
var variable_3 = words("ascii big_endian boolean data decimal ebcdic integer pattern qstring real record rule set of string token udecimal unicode unsigned varstring varunicode");
var builtin = words("checkpoint deprecated failcode failmessage failure global independent onwarning persist priority recovery stored success wait when");
var blockKeywords = words("catch class do else finally for if switch try while");
var atoms = words("true false null");
var hooks = {
  "#": metaHook
};
var isOperatorChar = /[+\-*&%=<>!?|\/]/;
var curPunc;
function tokenBase(stream, state) {
  var ch = stream.next();
  if (hooks[ch]) {
    var result = hooks[ch](stream, state);
    if (result !== false) return result;
  }
  if (ch == '"' || ch == "'") {
    state.tokenize = tokenString(ch);
    return state.tokenize(stream, state);
  }
  if (/[\[\]{}\(\),;\:\.]/.test(ch)) {
    curPunc = ch;
    return null;
  }
  if (/\d/.test(ch)) {
    stream.eatWhile(/[\w\.]/);
    return "number";
  }
  if (ch == "/") {
    if (stream.eat("*")) {
      state.tokenize = tokenComment;
      return tokenComment(stream, state);
    }
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
  if (keyword.propertyIsEnumerable(cur)) {
    if (blockKeywords.propertyIsEnumerable(cur)) curPunc = "newstatement";
    return "keyword";
  } else if (variable.propertyIsEnumerable(cur)) {
    if (blockKeywords.propertyIsEnumerable(cur)) curPunc = "newstatement";
    return "variable";
  } else if (variable_2.propertyIsEnumerable(cur)) {
    if (blockKeywords.propertyIsEnumerable(cur)) curPunc = "newstatement";
    return "modifier";
  } else if (variable_3.propertyIsEnumerable(cur)) {
    if (blockKeywords.propertyIsEnumerable(cur)) curPunc = "newstatement";
    return "type";
  } else if (builtin.propertyIsEnumerable(cur)) {
    if (blockKeywords.propertyIsEnumerable(cur)) curPunc = "newstatement";
    return "builtin";
  } else {
    //Data types are of from KEYWORD##
    var i = cur.length - 1;
    while (i >= 0 && (!isNaN(cur[i]) || cur[i] == '_')) --i;
    if (i > 0) {
      var cur2 = cur.substr(0, i + 1);
      if (variable_3.propertyIsEnumerable(cur2)) {
        if (blockKeywords.propertyIsEnumerable(cur2)) curPunc = "newstatement";
        return "type";
      }
    }
  }
  if (atoms.propertyIsEnumerable(cur)) return "atom";
  return null;
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
    if (end || !escaped) state.tokenize = tokenBase;
    return "string";
  };
}
function tokenComment(stream, state) {
  var maybeEnd = false,
    ch;
  while (ch = stream.next()) {
    if (ch == "/" && maybeEnd) {
      state.tokenize = tokenBase;
      break;
    }
    maybeEnd = ch == "*";
  }
  return "comment";
}
function Context(indented, column, type, align, prev) {
  this.indented = indented;
  this.column = column;
  this.type = type;
  this.align = align;
  this.prev = prev;
}
function pushContext(state, col, type) {
  return state.context = new Context(state.indented, col, type, null, state.context);
}
function popContext(state) {
  var t = state.context.type;
  if (t == ")" || t == "]" || t == "}") state.indented = state.context.indented;
  return state.context = state.context.prev;
}

// Interface

const ecl = {
  name: "ecl",
  startState: function (indentUnit) {
    return {
      tokenize: null,
      context: new Context(-indentUnit, 0, "top", false),
      indented: 0,
      startOfLine: true
    };
  },
  token: function (stream, state) {
    var ctx = state.context;
    if (stream.sol()) {
      if (ctx.align == null) ctx.align = false;
      state.indented = stream.indentation();
      state.startOfLine = true;
    }
    if (stream.eatSpace()) return null;
    curPunc = null;
    var style = (state.tokenize || tokenBase)(stream, state);
    if (style == "comment" || style == "meta") return style;
    if (ctx.align == null) ctx.align = true;
    if ((curPunc == ";" || curPunc == ":") && ctx.type == "statement") popContext(state);else if (curPunc == "{") pushContext(state, stream.column(), "}");else if (curPunc == "[") pushContext(state, stream.column(), "]");else if (curPunc == "(") pushContext(state, stream.column(), ")");else if (curPunc == "}") {
      while (ctx.type == "statement") ctx = popContext(state);
      if (ctx.type == "}") ctx = popContext(state);
      while (ctx.type == "statement") ctx = popContext(state);
    } else if (curPunc == ctx.type) popContext(state);else if (ctx.type == "}" || ctx.type == "top" || ctx.type == "statement" && curPunc == "newstatement") pushContext(state, stream.column(), "statement");
    state.startOfLine = false;
    return style;
  },
  indent: function (state, textAfter, cx) {
    if (state.tokenize != tokenBase && state.tokenize != null) return 0;
    var ctx = state.context,
      firstChar = textAfter && textAfter.charAt(0);
    if (ctx.type == "statement" && firstChar == "}") ctx = ctx.prev;
    var closing = firstChar == ctx.type;
    if (ctx.type == "statement") return ctx.indented + (firstChar == "{" ? 0 : cx.unit);else if (ctx.align) return ctx.column + (closing ? 0 : 1);else return ctx.indented + (closing ? 0 : cx.unit);
  },
  languageData: {
    indentOnInput: /^\s*[{}]$/
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNzU0Mi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvZWNsLmpzIl0sInNvdXJjZXNDb250ZW50IjpbImZ1bmN0aW9uIHdvcmRzKHN0cikge1xuICB2YXIgb2JqID0ge30sXG4gICAgd29yZHMgPSBzdHIuc3BsaXQoXCIgXCIpO1xuICBmb3IgKHZhciBpID0gMDsgaSA8IHdvcmRzLmxlbmd0aDsgKytpKSBvYmpbd29yZHNbaV1dID0gdHJ1ZTtcbiAgcmV0dXJuIG9iajtcbn1cbmZ1bmN0aW9uIG1ldGFIb29rKHN0cmVhbSwgc3RhdGUpIHtcbiAgaWYgKCFzdGF0ZS5zdGFydE9mTGluZSkgcmV0dXJuIGZhbHNlO1xuICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gIHJldHVybiBcIm1ldGFcIjtcbn1cbnZhciBrZXl3b3JkID0gd29yZHMoXCJhYnMgYWNvcyBhbGxub2RlcyBhc2NpaSBhc2luIGFzc3RyaW5nIGF0YW4gYXRhbjIgYXZlIGNhc2UgY2hvb3NlIGNob29zZW4gY2hvb3Nlc2V0cyBjbHVzdGVyc2l6ZSBjb21iaW5lIGNvcnJlbGF0aW9uIGNvcyBjb3NoIGNvdW50IGNvdmFyaWFuY2UgY3JvbiBkYXRhc2V0IGRlZHVwIGRlZmluZSBkZW5vcm1hbGl6ZSBkaXN0cmlidXRlIGRpc3RyaWJ1dGVkIGRpc3RyaWJ1dGlvbiBlYmNkaWMgZW50aCBlcnJvciBldmFsdWF0ZSBldmVudCBldmVudGV4dHJhIGV2ZW50bmFtZSBleGlzdHMgZXhwIGZhaWxjb2RlIGZhaWxtZXNzYWdlIGZldGNoIGZyb211bmljb2RlIGdldGlzdmFsaWQgZ2xvYmFsIGdyYXBoIGdyb3VwIGhhc2ggaGFzaDMyIGhhc2g2NCBoYXNoY3JjIGhhc2htZDUgaGF2aW5nIGlmIGluZGV4IGludGZvcm1hdCBpc3ZhbGlkIGl0ZXJhdGUgam9pbiBrZXl1bmljb2RlIGxlbmd0aCBsaWJyYXJ5IGxpbWl0IGxuIGxvY2FsIGxvZyBsb29wIG1hcCBtYXRjaGVkIG1hdGNobGVuZ3RoIG1hdGNocG9zaXRpb24gbWF0Y2h0ZXh0IG1hdGNodW5pY29kZSBtYXggbWVyZ2UgbWVyZ2Vqb2luIG1pbiBub2xvY2FsIG5vbmVtcHR5IG5vcm1hbGl6ZSBwYXJzZSBwaXBlIHBvd2VyIHByZWxvYWQgcHJvY2VzcyBwcm9qZWN0IHB1bGwgcmFuZG9tIHJhbmdlIHJhbmsgcmFua2VkIHJlYWxmb3JtYXQgcmVjb3Jkb2YgcmVnZXhmaW5kIHJlZ2V4cmVwbGFjZSByZWdyb3VwIHJlamVjdGVkIHJvbGx1cCByb3VuZCByb3VuZHVwIHJvdyByb3dkaWZmIHNhbXBsZSBzZXQgc2luIHNpbmggc2l6ZW9mIHNvYXBjYWxsIHNvcnQgc29ydGVkIHNxcnQgc3RlcHBlZCBzdG9yZWQgc3VtIHRhYmxlIHRhbiB0YW5oIHRoaXNub2RlIHRvcG4gdG91bmljb2RlIHRyYW5zZmVyIHRyaW0gdHJ1bmNhdGUgdHlwZW9mIHVuZ3JvdXAgdW5pY29kZW9yZGVyIHZhcmlhbmNlIHdoaWNoIHdvcmt1bml0IHhtbGRlY29kZSB4bWxlbmNvZGUgeG1sdGV4dCB4bWx1bmljb2RlXCIpO1xudmFyIHZhcmlhYmxlID0gd29yZHMoXCJhcHBseSBhc3NlcnQgYnVpbGQgYnVpbGRpbmRleCBldmFsdWF0ZSBmYWlsIGtleWRpZmYga2V5cGF0Y2ggbG9hZHhtbCBub3Rob3Igbm90aWZ5IG91dHB1dCBwYXJhbGxlbCBzZXF1ZW50aWFsIHNvYXBjYWxsIHdhaXRcIik7XG52YXIgdmFyaWFibGVfMiA9IHdvcmRzKFwiX19jb21wcmVzc2VkX18gYWxsIGFuZCBhbnkgYXMgYXRtb3N0IGJlZm9yZSBiZWdpbmMrKyBiZXN0IGJldHdlZW4gY2FzZSBjb25zdCBjb3VudGVyIGNzdiBkZXNjZW5kIGVuY3J5cHQgZW5kIGVuZGMrKyBlbmRtYWNybyBleGNlcHQgZXhjbHVzaXZlIGV4cGlyZSBleHBvcnQgZXh0ZW5kIGZhbHNlIGZldyBmaXJzdCBmbGF0IGZyb20gZnVsbCBmdW5jdGlvbiBncm91cCBoZWFkZXIgaGVhZGluZyBob2xlIGlmYmxvY2sgaW1wb3J0IGluIGludGVyZmFjZSBqb2luZWQga2VlcCBrZXllZCBsYXN0IGxlZnQgbGltaXQgbG9hZCBsb2NhbCBsb2NhbGUgbG9va3VwIG1hY3JvIG1hbnkgbWF4Y291bnQgbWF4bGVuZ3RoIG1pbiBza2V3IG1vZHVsZSBuYW1lZCBub2Nhc2Ugbm9yb290IG5vc2NhbiBub3NvcnQgbm90IG9mIG9ubHkgb3B0IG9yIG91dGVyIG92ZXJ3cml0ZSBwYWNrZWQgcGFydGl0aW9uIHBlbmFsdHkgcGh5c2ljYWxsZW5ndGggcGlwZSBxdW90ZSByZWNvcmQgcmVsYXRpb25zaGlwIHJlcGVhdCByZXR1cm4gcmlnaHQgc2NhbiBzZWxmIHNlcGFyYXRvciBzZXJ2aWNlIHNoYXJlZCBza2V3IHNraXAgc3FsIHN0b3JlIHRlcm1pbmF0b3IgdGhvciB0aHJlc2hvbGQgdG9rZW4gdHJhbnNmb3JtIHRyaW0gdHJ1ZSB0eXBlIHVuaWNvZGVvcmRlciB1bnNvcnRlZCB2YWxpZGF0ZSB2aXJ0dWFsIHdob2xlIHdpbGQgd2l0aGluIHhtbCB4cGF0aFwiKTtcbnZhciB2YXJpYWJsZV8zID0gd29yZHMoXCJhc2NpaSBiaWdfZW5kaWFuIGJvb2xlYW4gZGF0YSBkZWNpbWFsIGViY2RpYyBpbnRlZ2VyIHBhdHRlcm4gcXN0cmluZyByZWFsIHJlY29yZCBydWxlIHNldCBvZiBzdHJpbmcgdG9rZW4gdWRlY2ltYWwgdW5pY29kZSB1bnNpZ25lZCB2YXJzdHJpbmcgdmFydW5pY29kZVwiKTtcbnZhciBidWlsdGluID0gd29yZHMoXCJjaGVja3BvaW50IGRlcHJlY2F0ZWQgZmFpbGNvZGUgZmFpbG1lc3NhZ2UgZmFpbHVyZSBnbG9iYWwgaW5kZXBlbmRlbnQgb253YXJuaW5nIHBlcnNpc3QgcHJpb3JpdHkgcmVjb3Zlcnkgc3RvcmVkIHN1Y2Nlc3Mgd2FpdCB3aGVuXCIpO1xudmFyIGJsb2NrS2V5d29yZHMgPSB3b3JkcyhcImNhdGNoIGNsYXNzIGRvIGVsc2UgZmluYWxseSBmb3IgaWYgc3dpdGNoIHRyeSB3aGlsZVwiKTtcbnZhciBhdG9tcyA9IHdvcmRzKFwidHJ1ZSBmYWxzZSBudWxsXCIpO1xudmFyIGhvb2tzID0ge1xuICBcIiNcIjogbWV0YUhvb2tcbn07XG52YXIgaXNPcGVyYXRvckNoYXIgPSAvWytcXC0qJiU9PD4hP3xcXC9dLztcbnZhciBjdXJQdW5jO1xuZnVuY3Rpb24gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIGNoID0gc3RyZWFtLm5leHQoKTtcbiAgaWYgKGhvb2tzW2NoXSkge1xuICAgIHZhciByZXN1bHQgPSBob29rc1tjaF0oc3RyZWFtLCBzdGF0ZSk7XG4gICAgaWYgKHJlc3VsdCAhPT0gZmFsc2UpIHJldHVybiByZXN1bHQ7XG4gIH1cbiAgaWYgKGNoID09ICdcIicgfHwgY2ggPT0gXCInXCIpIHtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuU3RyaW5nKGNoKTtcbiAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cbiAgaWYgKC9bXFxbXFxde31cXChcXCksO1xcOlxcLl0vLnRlc3QoY2gpKSB7XG4gICAgY3VyUHVuYyA9IGNoO1xuICAgIHJldHVybiBudWxsO1xuICB9XG4gIGlmICgvXFxkLy50ZXN0KGNoKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcLl0vKTtcbiAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgfVxuICBpZiAoY2ggPT0gXCIvXCIpIHtcbiAgICBpZiAoc3RyZWFtLmVhdChcIipcIikpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5Db21tZW50O1xuICAgICAgcmV0dXJuIHRva2VuQ29tbWVudChzdHJlYW0sIHN0YXRlKTtcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5lYXQoXCIvXCIpKSB7XG4gICAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgfVxuICB9XG4gIGlmIChpc09wZXJhdG9yQ2hhci50ZXN0KGNoKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZShpc09wZXJhdG9yQ2hhcik7XG4gICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgfVxuICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXCRfXS8pO1xuICB2YXIgY3VyID0gc3RyZWFtLmN1cnJlbnQoKS50b0xvd2VyQ2FzZSgpO1xuICBpZiAoa2V5d29yZC5wcm9wZXJ0eUlzRW51bWVyYWJsZShjdXIpKSB7XG4gICAgaWYgKGJsb2NrS2V5d29yZHMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgY3VyUHVuYyA9IFwibmV3c3RhdGVtZW50XCI7XG4gICAgcmV0dXJuIFwia2V5d29yZFwiO1xuICB9IGVsc2UgaWYgKHZhcmlhYmxlLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIHtcbiAgICBpZiAoYmxvY2tLZXl3b3Jkcy5wcm9wZXJ0eUlzRW51bWVyYWJsZShjdXIpKSBjdXJQdW5jID0gXCJuZXdzdGF0ZW1lbnRcIjtcbiAgICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xuICB9IGVsc2UgaWYgKHZhcmlhYmxlXzIucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkge1xuICAgIGlmIChibG9ja0tleXdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIGN1clB1bmMgPSBcIm5ld3N0YXRlbWVudFwiO1xuICAgIHJldHVybiBcIm1vZGlmaWVyXCI7XG4gIH0gZWxzZSBpZiAodmFyaWFibGVfMy5wcm9wZXJ0eUlzRW51bWVyYWJsZShjdXIpKSB7XG4gICAgaWYgKGJsb2NrS2V5d29yZHMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgY3VyUHVuYyA9IFwibmV3c3RhdGVtZW50XCI7XG4gICAgcmV0dXJuIFwidHlwZVwiO1xuICB9IGVsc2UgaWYgKGJ1aWx0aW4ucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkge1xuICAgIGlmIChibG9ja0tleXdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIGN1clB1bmMgPSBcIm5ld3N0YXRlbWVudFwiO1xuICAgIHJldHVybiBcImJ1aWx0aW5cIjtcbiAgfSBlbHNlIHtcbiAgICAvL0RhdGEgdHlwZXMgYXJlIG9mIGZyb20gS0VZV09SRCMjXG4gICAgdmFyIGkgPSBjdXIubGVuZ3RoIC0gMTtcbiAgICB3aGlsZSAoaSA+PSAwICYmICghaXNOYU4oY3VyW2ldKSB8fCBjdXJbaV0gPT0gJ18nKSkgLS1pO1xuICAgIGlmIChpID4gMCkge1xuICAgICAgdmFyIGN1cjIgPSBjdXIuc3Vic3RyKDAsIGkgKyAxKTtcbiAgICAgIGlmICh2YXJpYWJsZV8zLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cjIpKSB7XG4gICAgICAgIGlmIChibG9ja0tleXdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cjIpKSBjdXJQdW5jID0gXCJuZXdzdGF0ZW1lbnRcIjtcbiAgICAgICAgcmV0dXJuIFwidHlwZVwiO1xuICAgICAgfVxuICAgIH1cbiAgfVxuICBpZiAoYXRvbXMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwiYXRvbVwiO1xuICByZXR1cm4gbnVsbDtcbn1cbmZ1bmN0aW9uIHRva2VuU3RyaW5nKHF1b3RlKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBlc2NhcGVkID0gZmFsc2UsXG4gICAgICBuZXh0LFxuICAgICAgZW5kID0gZmFsc2U7XG4gICAgd2hpbGUgKChuZXh0ID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgICAgaWYgKG5leHQgPT0gcXVvdGUgJiYgIWVzY2FwZWQpIHtcbiAgICAgICAgZW5kID0gdHJ1ZTtcbiAgICAgICAgYnJlYWs7XG4gICAgICB9XG4gICAgICBlc2NhcGVkID0gIWVzY2FwZWQgJiYgbmV4dCA9PSBcIlxcXFxcIjtcbiAgICB9XG4gICAgaWYgKGVuZCB8fCAhZXNjYXBlZCkgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gIH07XG59XG5mdW5jdGlvbiB0b2tlbkNvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgbWF5YmVFbmQgPSBmYWxzZSxcbiAgICBjaDtcbiAgd2hpbGUgKGNoID0gc3RyZWFtLm5leHQoKSkge1xuICAgIGlmIChjaCA9PSBcIi9cIiAmJiBtYXliZUVuZCkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgICBicmVhaztcbiAgICB9XG4gICAgbWF5YmVFbmQgPSBjaCA9PSBcIipcIjtcbiAgfVxuICByZXR1cm4gXCJjb21tZW50XCI7XG59XG5mdW5jdGlvbiBDb250ZXh0KGluZGVudGVkLCBjb2x1bW4sIHR5cGUsIGFsaWduLCBwcmV2KSB7XG4gIHRoaXMuaW5kZW50ZWQgPSBpbmRlbnRlZDtcbiAgdGhpcy5jb2x1bW4gPSBjb2x1bW47XG4gIHRoaXMudHlwZSA9IHR5cGU7XG4gIHRoaXMuYWxpZ24gPSBhbGlnbjtcbiAgdGhpcy5wcmV2ID0gcHJldjtcbn1cbmZ1bmN0aW9uIHB1c2hDb250ZXh0KHN0YXRlLCBjb2wsIHR5cGUpIHtcbiAgcmV0dXJuIHN0YXRlLmNvbnRleHQgPSBuZXcgQ29udGV4dChzdGF0ZS5pbmRlbnRlZCwgY29sLCB0eXBlLCBudWxsLCBzdGF0ZS5jb250ZXh0KTtcbn1cbmZ1bmN0aW9uIHBvcENvbnRleHQoc3RhdGUpIHtcbiAgdmFyIHQgPSBzdGF0ZS5jb250ZXh0LnR5cGU7XG4gIGlmICh0ID09IFwiKVwiIHx8IHQgPT0gXCJdXCIgfHwgdCA9PSBcIn1cIikgc3RhdGUuaW5kZW50ZWQgPSBzdGF0ZS5jb250ZXh0LmluZGVudGVkO1xuICByZXR1cm4gc3RhdGUuY29udGV4dCA9IHN0YXRlLmNvbnRleHQucHJldjtcbn1cblxuLy8gSW50ZXJmYWNlXG5cbmV4cG9ydCBjb25zdCBlY2wgPSB7XG4gIG5hbWU6IFwiZWNsXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uIChpbmRlbnRVbml0KSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiBudWxsLFxuICAgICAgY29udGV4dDogbmV3IENvbnRleHQoLWluZGVudFVuaXQsIDAsIFwidG9wXCIsIGZhbHNlKSxcbiAgICAgIGluZGVudGVkOiAwLFxuICAgICAgc3RhcnRPZkxpbmU6IHRydWVcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgY3R4ID0gc3RhdGUuY29udGV4dDtcbiAgICBpZiAoc3RyZWFtLnNvbCgpKSB7XG4gICAgICBpZiAoY3R4LmFsaWduID09IG51bGwpIGN0eC5hbGlnbiA9IGZhbHNlO1xuICAgICAgc3RhdGUuaW5kZW50ZWQgPSBzdHJlYW0uaW5kZW50YXRpb24oKTtcbiAgICAgIHN0YXRlLnN0YXJ0T2ZMaW5lID0gdHJ1ZTtcbiAgICB9XG4gICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgICBjdXJQdW5jID0gbnVsbDtcbiAgICB2YXIgc3R5bGUgPSAoc3RhdGUudG9rZW5pemUgfHwgdG9rZW5CYXNlKShzdHJlYW0sIHN0YXRlKTtcbiAgICBpZiAoc3R5bGUgPT0gXCJjb21tZW50XCIgfHwgc3R5bGUgPT0gXCJtZXRhXCIpIHJldHVybiBzdHlsZTtcbiAgICBpZiAoY3R4LmFsaWduID09IG51bGwpIGN0eC5hbGlnbiA9IHRydWU7XG4gICAgaWYgKChjdXJQdW5jID09IFwiO1wiIHx8IGN1clB1bmMgPT0gXCI6XCIpICYmIGN0eC50eXBlID09IFwic3RhdGVtZW50XCIpIHBvcENvbnRleHQoc3RhdGUpO2Vsc2UgaWYgKGN1clB1bmMgPT0gXCJ7XCIpIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0uY29sdW1uKCksIFwifVwiKTtlbHNlIGlmIChjdXJQdW5jID09IFwiW1wiKSBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLmNvbHVtbigpLCBcIl1cIik7ZWxzZSBpZiAoY3VyUHVuYyA9PSBcIihcIikgcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbS5jb2x1bW4oKSwgXCIpXCIpO2Vsc2UgaWYgKGN1clB1bmMgPT0gXCJ9XCIpIHtcbiAgICAgIHdoaWxlIChjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiKSBjdHggPSBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICAgIGlmIChjdHgudHlwZSA9PSBcIn1cIikgY3R4ID0gcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgICB3aGlsZSAoY3R4LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIikgY3R4ID0gcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgfSBlbHNlIGlmIChjdXJQdW5jID09IGN0eC50eXBlKSBwb3BDb250ZXh0KHN0YXRlKTtlbHNlIGlmIChjdHgudHlwZSA9PSBcIn1cIiB8fCBjdHgudHlwZSA9PSBcInRvcFwiIHx8IGN0eC50eXBlID09IFwic3RhdGVtZW50XCIgJiYgY3VyUHVuYyA9PSBcIm5ld3N0YXRlbWVudFwiKSBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLmNvbHVtbigpLCBcInN0YXRlbWVudFwiKTtcbiAgICBzdGF0ZS5zdGFydE9mTGluZSA9IGZhbHNlO1xuICAgIHJldHVybiBzdHlsZTtcbiAgfSxcbiAgaW5kZW50OiBmdW5jdGlvbiAoc3RhdGUsIHRleHRBZnRlciwgY3gpIHtcbiAgICBpZiAoc3RhdGUudG9rZW5pemUgIT0gdG9rZW5CYXNlICYmIHN0YXRlLnRva2VuaXplICE9IG51bGwpIHJldHVybiAwO1xuICAgIHZhciBjdHggPSBzdGF0ZS5jb250ZXh0LFxuICAgICAgZmlyc3RDaGFyID0gdGV4dEFmdGVyICYmIHRleHRBZnRlci5jaGFyQXQoMCk7XG4gICAgaWYgKGN0eC50eXBlID09IFwic3RhdGVtZW50XCIgJiYgZmlyc3RDaGFyID09IFwifVwiKSBjdHggPSBjdHgucHJldjtcbiAgICB2YXIgY2xvc2luZyA9IGZpcnN0Q2hhciA9PSBjdHgudHlwZTtcbiAgICBpZiAoY3R4LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIikgcmV0dXJuIGN0eC5pbmRlbnRlZCArIChmaXJzdENoYXIgPT0gXCJ7XCIgPyAwIDogY3gudW5pdCk7ZWxzZSBpZiAoY3R4LmFsaWduKSByZXR1cm4gY3R4LmNvbHVtbiArIChjbG9zaW5nID8gMCA6IDEpO2Vsc2UgcmV0dXJuIGN0eC5pbmRlbnRlZCArIChjbG9zaW5nID8gMCA6IGN4LnVuaXQpO1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBpbmRlbnRPbklucHV0OiAvXlxccypbe31dJC9cbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9