"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[2265],{

/***/ 82265
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   webIDL: () => (/* binding */ webIDL)
/* harmony export */ });
function wordRegexp(words) {
  return new RegExp("^((" + words.join(")|(") + "))\\b");
}
;
var builtinArray = ["Clamp", "Constructor", "EnforceRange", "Exposed", "ImplicitThis", "Global", "PrimaryGlobal", "LegacyArrayClass", "LegacyUnenumerableNamedProperties", "LenientThis", "NamedConstructor", "NewObject", "NoInterfaceObject", "OverrideBuiltins", "PutForwards", "Replaceable", "SameObject", "TreatNonObjectAsNull", "TreatNullAs", "EmptyString", "Unforgeable", "Unscopeable"];
var builtins = wordRegexp(builtinArray);
var typeArray = ["unsigned", "short", "long",
// UnsignedIntegerType
"unrestricted", "float", "double",
// UnrestrictedFloatType
"boolean", "byte", "octet",
// Rest of PrimitiveType
"Promise",
// PromiseType
"ArrayBuffer", "DataView", "Int8Array", "Int16Array", "Int32Array", "Uint8Array", "Uint16Array", "Uint32Array", "Uint8ClampedArray", "Float32Array", "Float64Array",
// BufferRelatedType
"ByteString", "DOMString", "USVString", "sequence", "object", "RegExp", "Error", "DOMException", "FrozenArray",
// Rest of NonAnyType
"any",
// Rest of SingleType
"void" // Rest of ReturnType
];
var types = wordRegexp(typeArray);
var keywordArray = ["attribute", "callback", "const", "deleter", "dictionary", "enum", "getter", "implements", "inherit", "interface", "iterable", "legacycaller", "maplike", "partial", "required", "serializer", "setlike", "setter", "static", "stringifier", "typedef",
// ArgumentNameKeyword except
// "unrestricted"
"optional", "readonly", "or"];
var keywords = wordRegexp(keywordArray);
var atomArray = ["true", "false",
// BooleanLiteral
"Infinity", "NaN",
// FloatLiteral
"null" // Rest of ConstValue
];
var atoms = wordRegexp(atomArray);
var startDefArray = ["callback", "dictionary", "enum", "interface"];
var startDefs = wordRegexp(startDefArray);
var endDefArray = ["typedef"];
var endDefs = wordRegexp(endDefArray);
var singleOperators = /^[:<=>?]/;
var integers = /^-?([1-9][0-9]*|0[Xx][0-9A-Fa-f]+|0[0-7]*)/;
var floats = /^-?(([0-9]+\.[0-9]*|[0-9]*\.[0-9]+)([Ee][+-]?[0-9]+)?|[0-9]+[Ee][+-]?[0-9]+)/;
var identifiers = /^_?[A-Za-z][0-9A-Z_a-z-]*/;
var identifiersEnd = /^_?[A-Za-z][0-9A-Z_a-z-]*(?=\s*;)/;
var strings = /^"[^"]*"/;
var multilineComments = /^\/\*.*?\*\//;
var multilineCommentsStart = /^\/\*.*/;
var multilineCommentsEnd = /^.*?\*\//;
function readToken(stream, state) {
  // whitespace
  if (stream.eatSpace()) return null;

  // comment
  if (state.inComment) {
    if (stream.match(multilineCommentsEnd)) {
      state.inComment = false;
      return "comment";
    }
    stream.skipToEnd();
    return "comment";
  }
  if (stream.match("//")) {
    stream.skipToEnd();
    return "comment";
  }
  if (stream.match(multilineComments)) return "comment";
  if (stream.match(multilineCommentsStart)) {
    state.inComment = true;
    return "comment";
  }

  // integer and float
  if (stream.match(/^-?[0-9\.]/, false)) {
    if (stream.match(integers) || stream.match(floats)) return "number";
  }

  // string
  if (stream.match(strings)) return "string";

  // identifier
  if (state.startDef && stream.match(identifiers)) return "def";
  if (state.endDef && stream.match(identifiersEnd)) {
    state.endDef = false;
    return "def";
  }
  if (stream.match(keywords)) return "keyword";
  if (stream.match(types)) {
    var lastToken = state.lastToken;
    var nextToken = (stream.match(/^\s*(.+?)\b/, false) || [])[1];
    if (lastToken === ":" || lastToken === "implements" || nextToken === "implements" || nextToken === "=") {
      // Used as identifier
      return "builtin";
    } else {
      // Used as type
      return "type";
    }
  }
  if (stream.match(builtins)) return "builtin";
  if (stream.match(atoms)) return "atom";
  if (stream.match(identifiers)) return "variable";

  // other
  if (stream.match(singleOperators)) return "operator";

  // unrecognized
  stream.next();
  return null;
}
;
const webIDL = {
  name: "webidl",
  startState: function () {
    return {
      // Is in multiline comment
      inComment: false,
      // Last non-whitespace, matched token
      lastToken: "",
      // Next token is a definition
      startDef: false,
      // Last token of the statement is a definition
      endDef: false
    };
  },
  token: function (stream, state) {
    var style = readToken(stream, state);
    if (style) {
      var cur = stream.current();
      state.lastToken = cur;
      if (style === "keyword") {
        state.startDef = startDefs.test(cur);
        state.endDef = state.endDef || endDefs.test(cur);
      } else {
        state.startDef = false;
      }
    }
    return style;
  },
  languageData: {
    autocomplete: builtinArray.concat(typeArray).concat(keywordArray).concat(atomArray)
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMjI2NS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL3dlYmlkbC5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiB3b3JkUmVnZXhwKHdvcmRzKSB7XG4gIHJldHVybiBuZXcgUmVnRXhwKFwiXigoXCIgKyB3b3Jkcy5qb2luKFwiKXwoXCIpICsgXCIpKVxcXFxiXCIpO1xufVxuO1xudmFyIGJ1aWx0aW5BcnJheSA9IFtcIkNsYW1wXCIsIFwiQ29uc3RydWN0b3JcIiwgXCJFbmZvcmNlUmFuZ2VcIiwgXCJFeHBvc2VkXCIsIFwiSW1wbGljaXRUaGlzXCIsIFwiR2xvYmFsXCIsIFwiUHJpbWFyeUdsb2JhbFwiLCBcIkxlZ2FjeUFycmF5Q2xhc3NcIiwgXCJMZWdhY3lVbmVudW1lcmFibGVOYW1lZFByb3BlcnRpZXNcIiwgXCJMZW5pZW50VGhpc1wiLCBcIk5hbWVkQ29uc3RydWN0b3JcIiwgXCJOZXdPYmplY3RcIiwgXCJOb0ludGVyZmFjZU9iamVjdFwiLCBcIk92ZXJyaWRlQnVpbHRpbnNcIiwgXCJQdXRGb3J3YXJkc1wiLCBcIlJlcGxhY2VhYmxlXCIsIFwiU2FtZU9iamVjdFwiLCBcIlRyZWF0Tm9uT2JqZWN0QXNOdWxsXCIsIFwiVHJlYXROdWxsQXNcIiwgXCJFbXB0eVN0cmluZ1wiLCBcIlVuZm9yZ2VhYmxlXCIsIFwiVW5zY29wZWFibGVcIl07XG52YXIgYnVpbHRpbnMgPSB3b3JkUmVnZXhwKGJ1aWx0aW5BcnJheSk7XG52YXIgdHlwZUFycmF5ID0gW1widW5zaWduZWRcIiwgXCJzaG9ydFwiLCBcImxvbmdcIixcbi8vIFVuc2lnbmVkSW50ZWdlclR5cGVcblwidW5yZXN0cmljdGVkXCIsIFwiZmxvYXRcIiwgXCJkb3VibGVcIixcbi8vIFVucmVzdHJpY3RlZEZsb2F0VHlwZVxuXCJib29sZWFuXCIsIFwiYnl0ZVwiLCBcIm9jdGV0XCIsXG4vLyBSZXN0IG9mIFByaW1pdGl2ZVR5cGVcblwiUHJvbWlzZVwiLFxuLy8gUHJvbWlzZVR5cGVcblwiQXJyYXlCdWZmZXJcIiwgXCJEYXRhVmlld1wiLCBcIkludDhBcnJheVwiLCBcIkludDE2QXJyYXlcIiwgXCJJbnQzMkFycmF5XCIsIFwiVWludDhBcnJheVwiLCBcIlVpbnQxNkFycmF5XCIsIFwiVWludDMyQXJyYXlcIiwgXCJVaW50OENsYW1wZWRBcnJheVwiLCBcIkZsb2F0MzJBcnJheVwiLCBcIkZsb2F0NjRBcnJheVwiLFxuLy8gQnVmZmVyUmVsYXRlZFR5cGVcblwiQnl0ZVN0cmluZ1wiLCBcIkRPTVN0cmluZ1wiLCBcIlVTVlN0cmluZ1wiLCBcInNlcXVlbmNlXCIsIFwib2JqZWN0XCIsIFwiUmVnRXhwXCIsIFwiRXJyb3JcIiwgXCJET01FeGNlcHRpb25cIiwgXCJGcm96ZW5BcnJheVwiLFxuLy8gUmVzdCBvZiBOb25BbnlUeXBlXG5cImFueVwiLFxuLy8gUmVzdCBvZiBTaW5nbGVUeXBlXG5cInZvaWRcIiAvLyBSZXN0IG9mIFJldHVyblR5cGVcbl07XG52YXIgdHlwZXMgPSB3b3JkUmVnZXhwKHR5cGVBcnJheSk7XG52YXIga2V5d29yZEFycmF5ID0gW1wiYXR0cmlidXRlXCIsIFwiY2FsbGJhY2tcIiwgXCJjb25zdFwiLCBcImRlbGV0ZXJcIiwgXCJkaWN0aW9uYXJ5XCIsIFwiZW51bVwiLCBcImdldHRlclwiLCBcImltcGxlbWVudHNcIiwgXCJpbmhlcml0XCIsIFwiaW50ZXJmYWNlXCIsIFwiaXRlcmFibGVcIiwgXCJsZWdhY3ljYWxsZXJcIiwgXCJtYXBsaWtlXCIsIFwicGFydGlhbFwiLCBcInJlcXVpcmVkXCIsIFwic2VyaWFsaXplclwiLCBcInNldGxpa2VcIiwgXCJzZXR0ZXJcIiwgXCJzdGF0aWNcIiwgXCJzdHJpbmdpZmllclwiLCBcInR5cGVkZWZcIixcbi8vIEFyZ3VtZW50TmFtZUtleXdvcmQgZXhjZXB0XG4vLyBcInVucmVzdHJpY3RlZFwiXG5cIm9wdGlvbmFsXCIsIFwicmVhZG9ubHlcIiwgXCJvclwiXTtcbnZhciBrZXl3b3JkcyA9IHdvcmRSZWdleHAoa2V5d29yZEFycmF5KTtcbnZhciBhdG9tQXJyYXkgPSBbXCJ0cnVlXCIsIFwiZmFsc2VcIixcbi8vIEJvb2xlYW5MaXRlcmFsXG5cIkluZmluaXR5XCIsIFwiTmFOXCIsXG4vLyBGbG9hdExpdGVyYWxcblwibnVsbFwiIC8vIFJlc3Qgb2YgQ29uc3RWYWx1ZVxuXTtcbnZhciBhdG9tcyA9IHdvcmRSZWdleHAoYXRvbUFycmF5KTtcbnZhciBzdGFydERlZkFycmF5ID0gW1wiY2FsbGJhY2tcIiwgXCJkaWN0aW9uYXJ5XCIsIFwiZW51bVwiLCBcImludGVyZmFjZVwiXTtcbnZhciBzdGFydERlZnMgPSB3b3JkUmVnZXhwKHN0YXJ0RGVmQXJyYXkpO1xudmFyIGVuZERlZkFycmF5ID0gW1widHlwZWRlZlwiXTtcbnZhciBlbmREZWZzID0gd29yZFJlZ2V4cChlbmREZWZBcnJheSk7XG52YXIgc2luZ2xlT3BlcmF0b3JzID0gL15bOjw9Pj9dLztcbnZhciBpbnRlZ2VycyA9IC9eLT8oWzEtOV1bMC05XSp8MFtYeF1bMC05QS1GYS1mXSt8MFswLTddKikvO1xudmFyIGZsb2F0cyA9IC9eLT8oKFswLTldK1xcLlswLTldKnxbMC05XSpcXC5bMC05XSspKFtFZV1bKy1dP1swLTldKyk/fFswLTldK1tFZV1bKy1dP1swLTldKykvO1xudmFyIGlkZW50aWZpZXJzID0gL15fP1tBLVphLXpdWzAtOUEtWl9hLXotXSovO1xudmFyIGlkZW50aWZpZXJzRW5kID0gL15fP1tBLVphLXpdWzAtOUEtWl9hLXotXSooPz1cXHMqOykvO1xudmFyIHN0cmluZ3MgPSAvXlwiW15cIl0qXCIvO1xudmFyIG11bHRpbGluZUNvbW1lbnRzID0gL15cXC9cXCouKj9cXCpcXC8vO1xudmFyIG11bHRpbGluZUNvbW1lbnRzU3RhcnQgPSAvXlxcL1xcKi4qLztcbnZhciBtdWx0aWxpbmVDb21tZW50c0VuZCA9IC9eLio/XFwqXFwvLztcbmZ1bmN0aW9uIHJlYWRUb2tlbihzdHJlYW0sIHN0YXRlKSB7XG4gIC8vIHdoaXRlc3BhY2VcbiAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcblxuICAvLyBjb21tZW50XG4gIGlmIChzdGF0ZS5pbkNvbW1lbnQpIHtcbiAgICBpZiAoc3RyZWFtLm1hdGNoKG11bHRpbGluZUNvbW1lbnRzRW5kKSkge1xuICAgICAgc3RhdGUuaW5Db21tZW50ID0gZmFsc2U7XG4gICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgfVxuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH1cbiAgaWYgKHN0cmVhbS5tYXRjaChcIi8vXCIpKSB7XG4gICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgfVxuICBpZiAoc3RyZWFtLm1hdGNoKG11bHRpbGluZUNvbW1lbnRzKSkgcmV0dXJuIFwiY29tbWVudFwiO1xuICBpZiAoc3RyZWFtLm1hdGNoKG11bHRpbGluZUNvbW1lbnRzU3RhcnQpKSB7XG4gICAgc3RhdGUuaW5Db21tZW50ID0gdHJ1ZTtcbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH1cblxuICAvLyBpbnRlZ2VyIGFuZCBmbG9hdFxuICBpZiAoc3RyZWFtLm1hdGNoKC9eLT9bMC05XFwuXS8sIGZhbHNlKSkge1xuICAgIGlmIChzdHJlYW0ubWF0Y2goaW50ZWdlcnMpIHx8IHN0cmVhbS5tYXRjaChmbG9hdHMpKSByZXR1cm4gXCJudW1iZXJcIjtcbiAgfVxuXG4gIC8vIHN0cmluZ1xuICBpZiAoc3RyZWFtLm1hdGNoKHN0cmluZ3MpKSByZXR1cm4gXCJzdHJpbmdcIjtcblxuICAvLyBpZGVudGlmaWVyXG4gIGlmIChzdGF0ZS5zdGFydERlZiAmJiBzdHJlYW0ubWF0Y2goaWRlbnRpZmllcnMpKSByZXR1cm4gXCJkZWZcIjtcbiAgaWYgKHN0YXRlLmVuZERlZiAmJiBzdHJlYW0ubWF0Y2goaWRlbnRpZmllcnNFbmQpKSB7XG4gICAgc3RhdGUuZW5kRGVmID0gZmFsc2U7XG4gICAgcmV0dXJuIFwiZGVmXCI7XG4gIH1cbiAgaWYgKHN0cmVhbS5tYXRjaChrZXl3b3JkcykpIHJldHVybiBcImtleXdvcmRcIjtcbiAgaWYgKHN0cmVhbS5tYXRjaCh0eXBlcykpIHtcbiAgICB2YXIgbGFzdFRva2VuID0gc3RhdGUubGFzdFRva2VuO1xuICAgIHZhciBuZXh0VG9rZW4gPSAoc3RyZWFtLm1hdGNoKC9eXFxzKiguKz8pXFxiLywgZmFsc2UpIHx8IFtdKVsxXTtcbiAgICBpZiAobGFzdFRva2VuID09PSBcIjpcIiB8fCBsYXN0VG9rZW4gPT09IFwiaW1wbGVtZW50c1wiIHx8IG5leHRUb2tlbiA9PT0gXCJpbXBsZW1lbnRzXCIgfHwgbmV4dFRva2VuID09PSBcIj1cIikge1xuICAgICAgLy8gVXNlZCBhcyBpZGVudGlmaWVyXG4gICAgICByZXR1cm4gXCJidWlsdGluXCI7XG4gICAgfSBlbHNlIHtcbiAgICAgIC8vIFVzZWQgYXMgdHlwZVxuICAgICAgcmV0dXJuIFwidHlwZVwiO1xuICAgIH1cbiAgfVxuICBpZiAoc3RyZWFtLm1hdGNoKGJ1aWx0aW5zKSkgcmV0dXJuIFwiYnVpbHRpblwiO1xuICBpZiAoc3RyZWFtLm1hdGNoKGF0b21zKSkgcmV0dXJuIFwiYXRvbVwiO1xuICBpZiAoc3RyZWFtLm1hdGNoKGlkZW50aWZpZXJzKSkgcmV0dXJuIFwidmFyaWFibGVcIjtcblxuICAvLyBvdGhlclxuICBpZiAoc3RyZWFtLm1hdGNoKHNpbmdsZU9wZXJhdG9ycykpIHJldHVybiBcIm9wZXJhdG9yXCI7XG5cbiAgLy8gdW5yZWNvZ25pemVkXG4gIHN0cmVhbS5uZXh0KCk7XG4gIHJldHVybiBudWxsO1xufVxuO1xuZXhwb3J0IGNvbnN0IHdlYklETCA9IHtcbiAgbmFtZTogXCJ3ZWJpZGxcIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB7XG4gICAgICAvLyBJcyBpbiBtdWx0aWxpbmUgY29tbWVudFxuICAgICAgaW5Db21tZW50OiBmYWxzZSxcbiAgICAgIC8vIExhc3Qgbm9uLXdoaXRlc3BhY2UsIG1hdGNoZWQgdG9rZW5cbiAgICAgIGxhc3RUb2tlbjogXCJcIixcbiAgICAgIC8vIE5leHQgdG9rZW4gaXMgYSBkZWZpbml0aW9uXG4gICAgICBzdGFydERlZjogZmFsc2UsXG4gICAgICAvLyBMYXN0IHRva2VuIG9mIHRoZSBzdGF0ZW1lbnQgaXMgYSBkZWZpbml0aW9uXG4gICAgICBlbmREZWY6IGZhbHNlXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIHN0eWxlID0gcmVhZFRva2VuKHN0cmVhbSwgc3RhdGUpO1xuICAgIGlmIChzdHlsZSkge1xuICAgICAgdmFyIGN1ciA9IHN0cmVhbS5jdXJyZW50KCk7XG4gICAgICBzdGF0ZS5sYXN0VG9rZW4gPSBjdXI7XG4gICAgICBpZiAoc3R5bGUgPT09IFwia2V5d29yZFwiKSB7XG4gICAgICAgIHN0YXRlLnN0YXJ0RGVmID0gc3RhcnREZWZzLnRlc3QoY3VyKTtcbiAgICAgICAgc3RhdGUuZW5kRGVmID0gc3RhdGUuZW5kRGVmIHx8IGVuZERlZnMudGVzdChjdXIpO1xuICAgICAgfSBlbHNlIHtcbiAgICAgICAgc3RhdGUuc3RhcnREZWYgPSBmYWxzZTtcbiAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIHN0eWxlO1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBhdXRvY29tcGxldGU6IGJ1aWx0aW5BcnJheS5jb25jYXQodHlwZUFycmF5KS5jb25jYXQoa2V5d29yZEFycmF5KS5jb25jYXQoYXRvbUFycmF5KVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=