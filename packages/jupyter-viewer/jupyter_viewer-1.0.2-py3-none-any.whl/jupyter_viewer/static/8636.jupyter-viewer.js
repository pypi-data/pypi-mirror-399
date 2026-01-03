"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[8636],{

/***/ 58636
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   dylan: () => (/* binding */ dylan)
/* harmony export */ });
function forEach(arr, f) {
  for (var i = 0; i < arr.length; i++) f(arr[i], i);
}
function some(arr, f) {
  for (var i = 0; i < arr.length; i++) if (f(arr[i], i)) return true;
  return false;
}

// Words
var words = {
  // Words that introduce unnamed definitions like "define interface"
  unnamedDefinition: ["interface"],
  // Words that introduce simple named definitions like "define library"
  namedDefinition: ["module", "library", "macro", "C-struct", "C-union", "C-function", "C-callable-wrapper"],
  // Words that introduce type definitions like "define class".
  // These are also parameterized like "define method" and are
  // appended to otherParameterizedDefinitionWords
  typeParameterizedDefinition: ["class", "C-subtype", "C-mapped-subtype"],
  // Words that introduce trickier definitions like "define method".
  // These require special definitions to be added to startExpressions
  otherParameterizedDefinition: ["method", "function", "C-variable", "C-address"],
  // Words that introduce module constant definitions.
  // These must also be simple definitions and are
  // appended to otherSimpleDefinitionWords
  constantSimpleDefinition: ["constant"],
  // Words that introduce module variable definitions.
  // These must also be simple definitions and are
  // appended to otherSimpleDefinitionWords
  variableSimpleDefinition: ["variable"],
  // Other words that introduce simple definitions
  // (without implicit bodies).
  otherSimpleDefinition: ["generic", "domain", "C-pointer-type", "table"],
  // Words that begin statements with implicit bodies.
  statement: ["if", "block", "begin", "method", "case", "for", "select", "when", "unless", "until", "while", "iterate", "profiling", "dynamic-bind"],
  // Patterns that act as separators in compound statements.
  // This may include any general pattern that must be indented
  // specially.
  separator: ["finally", "exception", "cleanup", "else", "elseif", "afterwards"],
  // Keywords that do not require special indentation handling,
  // but which should be highlighted
  other: ["above", "below", "by", "from", "handler", "in", "instance", "let", "local", "otherwise", "slot", "subclass", "then", "to", "keyed-by", "virtual"],
  // Condition signaling function calls
  signalingCalls: ["signal", "error", "cerror", "break", "check-type", "abort"]
};
words["otherDefinition"] = words["unnamedDefinition"].concat(words["namedDefinition"]).concat(words["otherParameterizedDefinition"]);
words["definition"] = words["typeParameterizedDefinition"].concat(words["otherDefinition"]);
words["parameterizedDefinition"] = words["typeParameterizedDefinition"].concat(words["otherParameterizedDefinition"]);
words["simpleDefinition"] = words["constantSimpleDefinition"].concat(words["variableSimpleDefinition"]).concat(words["otherSimpleDefinition"]);
words["keyword"] = words["statement"].concat(words["separator"]).concat(words["other"]);

// Patterns
var symbolPattern = "[-_a-zA-Z?!*@<>$%]+";
var symbol = new RegExp("^" + symbolPattern);
var patterns = {
  // Symbols with special syntax
  symbolKeyword: symbolPattern + ":",
  symbolClass: "<" + symbolPattern + ">",
  symbolGlobal: "\\*" + symbolPattern + "\\*",
  symbolConstant: "\\$" + symbolPattern
};
var patternStyles = {
  symbolKeyword: "atom",
  symbolClass: "tag",
  symbolGlobal: "variableName.standard",
  symbolConstant: "variableName.constant"
};

// Compile all patterns to regular expressions
for (var patternName in patterns) if (patterns.hasOwnProperty(patternName)) patterns[patternName] = new RegExp("^" + patterns[patternName]);

// Names beginning "with-" and "without-" are commonly
// used as statement macro
patterns["keyword"] = [/^with(?:out)?-[-_a-zA-Z?!*@<>$%]+/];
var styles = {};
styles["keyword"] = "keyword";
styles["definition"] = "def";
styles["simpleDefinition"] = "def";
styles["signalingCalls"] = "builtin";

// protected words lookup table
var wordLookup = {};
var styleLookup = {};
forEach(["keyword", "definition", "simpleDefinition", "signalingCalls"], function (type) {
  forEach(words[type], function (word) {
    wordLookup[word] = type;
    styleLookup[word] = styles[type];
  });
});
function chain(stream, state, f) {
  state.tokenize = f;
  return f(stream, state);
}
function tokenBase(stream, state) {
  // String
  var ch = stream.peek();
  if (ch == "'" || ch == '"') {
    stream.next();
    return chain(stream, state, tokenString(ch, "string"));
  }
  // Comment
  else if (ch == "/") {
    stream.next();
    if (stream.eat("*")) {
      return chain(stream, state, tokenComment);
    } else if (stream.eat("/")) {
      stream.skipToEnd();
      return "comment";
    }
    stream.backUp(1);
  }
  // Decimal
  else if (/[+\-\d\.]/.test(ch)) {
    if (stream.match(/^[+-]?[0-9]*\.[0-9]*([esdx][+-]?[0-9]+)?/i) || stream.match(/^[+-]?[0-9]+([esdx][+-]?[0-9]+)/i) || stream.match(/^[+-]?\d+/)) {
      return "number";
    }
  }
  // Hash
  else if (ch == "#") {
    stream.next();
    // Symbol with string syntax
    ch = stream.peek();
    if (ch == '"') {
      stream.next();
      return chain(stream, state, tokenString('"', "string"));
    }
    // Binary number
    else if (ch == "b") {
      stream.next();
      stream.eatWhile(/[01]/);
      return "number";
    }
    // Hex number
    else if (ch == "x") {
      stream.next();
      stream.eatWhile(/[\da-f]/i);
      return "number";
    }
    // Octal number
    else if (ch == "o") {
      stream.next();
      stream.eatWhile(/[0-7]/);
      return "number";
    }
    // Token concatenation in macros
    else if (ch == '#') {
      stream.next();
      return "punctuation";
    }
    // Sequence literals
    else if (ch == '[' || ch == '(') {
      stream.next();
      return "bracket";
      // Hash symbol
    } else if (stream.match(/f|t|all-keys|include|key|next|rest/i)) {
      return "atom";
    } else {
      stream.eatWhile(/[-a-zA-Z]/);
      return "error";
    }
  } else if (ch == "~") {
    stream.next();
    ch = stream.peek();
    if (ch == "=") {
      stream.next();
      ch = stream.peek();
      if (ch == "=") {
        stream.next();
        return "operator";
      }
      return "operator";
    }
    return "operator";
  } else if (ch == ":") {
    stream.next();
    ch = stream.peek();
    if (ch == "=") {
      stream.next();
      return "operator";
    } else if (ch == ":") {
      stream.next();
      return "punctuation";
    }
  } else if ("[](){}".indexOf(ch) != -1) {
    stream.next();
    return "bracket";
  } else if (".,".indexOf(ch) != -1) {
    stream.next();
    return "punctuation";
  } else if (stream.match("end")) {
    return "keyword";
  }
  for (var name in patterns) {
    if (patterns.hasOwnProperty(name)) {
      var pattern = patterns[name];
      if (pattern instanceof Array && some(pattern, function (p) {
        return stream.match(p);
      }) || stream.match(pattern)) return patternStyles[name];
    }
  }
  if (/[+\-*\/^=<>&|]/.test(ch)) {
    stream.next();
    return "operator";
  }
  if (stream.match("define")) {
    return "def";
  } else {
    stream.eatWhile(/[\w\-]/);
    // Keyword
    if (wordLookup.hasOwnProperty(stream.current())) {
      return styleLookup[stream.current()];
    } else if (stream.current().match(symbol)) {
      return "variable";
    } else {
      stream.next();
      return "variableName.standard";
    }
  }
}
function tokenComment(stream, state) {
  var maybeEnd = false,
    maybeNested = false,
    nestedCount = 0,
    ch;
  while (ch = stream.next()) {
    if (ch == "/" && maybeEnd) {
      if (nestedCount > 0) {
        nestedCount--;
      } else {
        state.tokenize = tokenBase;
        break;
      }
    } else if (ch == "*" && maybeNested) {
      nestedCount++;
    }
    maybeEnd = ch == "*";
    maybeNested = ch == "/";
  }
  return "comment";
}
function tokenString(quote, style) {
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
    if (end || !escaped) {
      state.tokenize = tokenBase;
    }
    return style;
  };
}

// Interface
const dylan = {
  name: "dylan",
  startState: function () {
    return {
      tokenize: tokenBase,
      currentIndent: 0
    };
  },
  token: function (stream, state) {
    if (stream.eatSpace()) return null;
    var style = state.tokenize(stream, state);
    return style;
  },
  languageData: {
    commentTokens: {
      block: {
        open: "/*",
        close: "*/"
      }
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiODYzNi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9keWxhbi5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiBmb3JFYWNoKGFyciwgZikge1xuICBmb3IgKHZhciBpID0gMDsgaSA8IGFyci5sZW5ndGg7IGkrKykgZihhcnJbaV0sIGkpO1xufVxuZnVuY3Rpb24gc29tZShhcnIsIGYpIHtcbiAgZm9yICh2YXIgaSA9IDA7IGkgPCBhcnIubGVuZ3RoOyBpKyspIGlmIChmKGFycltpXSwgaSkpIHJldHVybiB0cnVlO1xuICByZXR1cm4gZmFsc2U7XG59XG5cbi8vIFdvcmRzXG52YXIgd29yZHMgPSB7XG4gIC8vIFdvcmRzIHRoYXQgaW50cm9kdWNlIHVubmFtZWQgZGVmaW5pdGlvbnMgbGlrZSBcImRlZmluZSBpbnRlcmZhY2VcIlxuICB1bm5hbWVkRGVmaW5pdGlvbjogW1wiaW50ZXJmYWNlXCJdLFxuICAvLyBXb3JkcyB0aGF0IGludHJvZHVjZSBzaW1wbGUgbmFtZWQgZGVmaW5pdGlvbnMgbGlrZSBcImRlZmluZSBsaWJyYXJ5XCJcbiAgbmFtZWREZWZpbml0aW9uOiBbXCJtb2R1bGVcIiwgXCJsaWJyYXJ5XCIsIFwibWFjcm9cIiwgXCJDLXN0cnVjdFwiLCBcIkMtdW5pb25cIiwgXCJDLWZ1bmN0aW9uXCIsIFwiQy1jYWxsYWJsZS13cmFwcGVyXCJdLFxuICAvLyBXb3JkcyB0aGF0IGludHJvZHVjZSB0eXBlIGRlZmluaXRpb25zIGxpa2UgXCJkZWZpbmUgY2xhc3NcIi5cbiAgLy8gVGhlc2UgYXJlIGFsc28gcGFyYW1ldGVyaXplZCBsaWtlIFwiZGVmaW5lIG1ldGhvZFwiIGFuZCBhcmVcbiAgLy8gYXBwZW5kZWQgdG8gb3RoZXJQYXJhbWV0ZXJpemVkRGVmaW5pdGlvbldvcmRzXG4gIHR5cGVQYXJhbWV0ZXJpemVkRGVmaW5pdGlvbjogW1wiY2xhc3NcIiwgXCJDLXN1YnR5cGVcIiwgXCJDLW1hcHBlZC1zdWJ0eXBlXCJdLFxuICAvLyBXb3JkcyB0aGF0IGludHJvZHVjZSB0cmlja2llciBkZWZpbml0aW9ucyBsaWtlIFwiZGVmaW5lIG1ldGhvZFwiLlxuICAvLyBUaGVzZSByZXF1aXJlIHNwZWNpYWwgZGVmaW5pdGlvbnMgdG8gYmUgYWRkZWQgdG8gc3RhcnRFeHByZXNzaW9uc1xuICBvdGhlclBhcmFtZXRlcml6ZWREZWZpbml0aW9uOiBbXCJtZXRob2RcIiwgXCJmdW5jdGlvblwiLCBcIkMtdmFyaWFibGVcIiwgXCJDLWFkZHJlc3NcIl0sXG4gIC8vIFdvcmRzIHRoYXQgaW50cm9kdWNlIG1vZHVsZSBjb25zdGFudCBkZWZpbml0aW9ucy5cbiAgLy8gVGhlc2UgbXVzdCBhbHNvIGJlIHNpbXBsZSBkZWZpbml0aW9ucyBhbmQgYXJlXG4gIC8vIGFwcGVuZGVkIHRvIG90aGVyU2ltcGxlRGVmaW5pdGlvbldvcmRzXG4gIGNvbnN0YW50U2ltcGxlRGVmaW5pdGlvbjogW1wiY29uc3RhbnRcIl0sXG4gIC8vIFdvcmRzIHRoYXQgaW50cm9kdWNlIG1vZHVsZSB2YXJpYWJsZSBkZWZpbml0aW9ucy5cbiAgLy8gVGhlc2UgbXVzdCBhbHNvIGJlIHNpbXBsZSBkZWZpbml0aW9ucyBhbmQgYXJlXG4gIC8vIGFwcGVuZGVkIHRvIG90aGVyU2ltcGxlRGVmaW5pdGlvbldvcmRzXG4gIHZhcmlhYmxlU2ltcGxlRGVmaW5pdGlvbjogW1widmFyaWFibGVcIl0sXG4gIC8vIE90aGVyIHdvcmRzIHRoYXQgaW50cm9kdWNlIHNpbXBsZSBkZWZpbml0aW9uc1xuICAvLyAod2l0aG91dCBpbXBsaWNpdCBib2RpZXMpLlxuICBvdGhlclNpbXBsZURlZmluaXRpb246IFtcImdlbmVyaWNcIiwgXCJkb21haW5cIiwgXCJDLXBvaW50ZXItdHlwZVwiLCBcInRhYmxlXCJdLFxuICAvLyBXb3JkcyB0aGF0IGJlZ2luIHN0YXRlbWVudHMgd2l0aCBpbXBsaWNpdCBib2RpZXMuXG4gIHN0YXRlbWVudDogW1wiaWZcIiwgXCJibG9ja1wiLCBcImJlZ2luXCIsIFwibWV0aG9kXCIsIFwiY2FzZVwiLCBcImZvclwiLCBcInNlbGVjdFwiLCBcIndoZW5cIiwgXCJ1bmxlc3NcIiwgXCJ1bnRpbFwiLCBcIndoaWxlXCIsIFwiaXRlcmF0ZVwiLCBcInByb2ZpbGluZ1wiLCBcImR5bmFtaWMtYmluZFwiXSxcbiAgLy8gUGF0dGVybnMgdGhhdCBhY3QgYXMgc2VwYXJhdG9ycyBpbiBjb21wb3VuZCBzdGF0ZW1lbnRzLlxuICAvLyBUaGlzIG1heSBpbmNsdWRlIGFueSBnZW5lcmFsIHBhdHRlcm4gdGhhdCBtdXN0IGJlIGluZGVudGVkXG4gIC8vIHNwZWNpYWxseS5cbiAgc2VwYXJhdG9yOiBbXCJmaW5hbGx5XCIsIFwiZXhjZXB0aW9uXCIsIFwiY2xlYW51cFwiLCBcImVsc2VcIiwgXCJlbHNlaWZcIiwgXCJhZnRlcndhcmRzXCJdLFxuICAvLyBLZXl3b3JkcyB0aGF0IGRvIG5vdCByZXF1aXJlIHNwZWNpYWwgaW5kZW50YXRpb24gaGFuZGxpbmcsXG4gIC8vIGJ1dCB3aGljaCBzaG91bGQgYmUgaGlnaGxpZ2h0ZWRcbiAgb3RoZXI6IFtcImFib3ZlXCIsIFwiYmVsb3dcIiwgXCJieVwiLCBcImZyb21cIiwgXCJoYW5kbGVyXCIsIFwiaW5cIiwgXCJpbnN0YW5jZVwiLCBcImxldFwiLCBcImxvY2FsXCIsIFwib3RoZXJ3aXNlXCIsIFwic2xvdFwiLCBcInN1YmNsYXNzXCIsIFwidGhlblwiLCBcInRvXCIsIFwia2V5ZWQtYnlcIiwgXCJ2aXJ0dWFsXCJdLFxuICAvLyBDb25kaXRpb24gc2lnbmFsaW5nIGZ1bmN0aW9uIGNhbGxzXG4gIHNpZ25hbGluZ0NhbGxzOiBbXCJzaWduYWxcIiwgXCJlcnJvclwiLCBcImNlcnJvclwiLCBcImJyZWFrXCIsIFwiY2hlY2stdHlwZVwiLCBcImFib3J0XCJdXG59O1xud29yZHNbXCJvdGhlckRlZmluaXRpb25cIl0gPSB3b3Jkc1tcInVubmFtZWREZWZpbml0aW9uXCJdLmNvbmNhdCh3b3Jkc1tcIm5hbWVkRGVmaW5pdGlvblwiXSkuY29uY2F0KHdvcmRzW1wib3RoZXJQYXJhbWV0ZXJpemVkRGVmaW5pdGlvblwiXSk7XG53b3Jkc1tcImRlZmluaXRpb25cIl0gPSB3b3Jkc1tcInR5cGVQYXJhbWV0ZXJpemVkRGVmaW5pdGlvblwiXS5jb25jYXQod29yZHNbXCJvdGhlckRlZmluaXRpb25cIl0pO1xud29yZHNbXCJwYXJhbWV0ZXJpemVkRGVmaW5pdGlvblwiXSA9IHdvcmRzW1widHlwZVBhcmFtZXRlcml6ZWREZWZpbml0aW9uXCJdLmNvbmNhdCh3b3Jkc1tcIm90aGVyUGFyYW1ldGVyaXplZERlZmluaXRpb25cIl0pO1xud29yZHNbXCJzaW1wbGVEZWZpbml0aW9uXCJdID0gd29yZHNbXCJjb25zdGFudFNpbXBsZURlZmluaXRpb25cIl0uY29uY2F0KHdvcmRzW1widmFyaWFibGVTaW1wbGVEZWZpbml0aW9uXCJdKS5jb25jYXQod29yZHNbXCJvdGhlclNpbXBsZURlZmluaXRpb25cIl0pO1xud29yZHNbXCJrZXl3b3JkXCJdID0gd29yZHNbXCJzdGF0ZW1lbnRcIl0uY29uY2F0KHdvcmRzW1wic2VwYXJhdG9yXCJdKS5jb25jYXQod29yZHNbXCJvdGhlclwiXSk7XG5cbi8vIFBhdHRlcm5zXG52YXIgc3ltYm9sUGF0dGVybiA9IFwiWy1fYS16QS1aPyEqQDw+JCVdK1wiO1xudmFyIHN5bWJvbCA9IG5ldyBSZWdFeHAoXCJeXCIgKyBzeW1ib2xQYXR0ZXJuKTtcbnZhciBwYXR0ZXJucyA9IHtcbiAgLy8gU3ltYm9scyB3aXRoIHNwZWNpYWwgc3ludGF4XG4gIHN5bWJvbEtleXdvcmQ6IHN5bWJvbFBhdHRlcm4gKyBcIjpcIixcbiAgc3ltYm9sQ2xhc3M6IFwiPFwiICsgc3ltYm9sUGF0dGVybiArIFwiPlwiLFxuICBzeW1ib2xHbG9iYWw6IFwiXFxcXCpcIiArIHN5bWJvbFBhdHRlcm4gKyBcIlxcXFwqXCIsXG4gIHN5bWJvbENvbnN0YW50OiBcIlxcXFwkXCIgKyBzeW1ib2xQYXR0ZXJuXG59O1xudmFyIHBhdHRlcm5TdHlsZXMgPSB7XG4gIHN5bWJvbEtleXdvcmQ6IFwiYXRvbVwiLFxuICBzeW1ib2xDbGFzczogXCJ0YWdcIixcbiAgc3ltYm9sR2xvYmFsOiBcInZhcmlhYmxlTmFtZS5zdGFuZGFyZFwiLFxuICBzeW1ib2xDb25zdGFudDogXCJ2YXJpYWJsZU5hbWUuY29uc3RhbnRcIlxufTtcblxuLy8gQ29tcGlsZSBhbGwgcGF0dGVybnMgdG8gcmVndWxhciBleHByZXNzaW9uc1xuZm9yICh2YXIgcGF0dGVybk5hbWUgaW4gcGF0dGVybnMpIGlmIChwYXR0ZXJucy5oYXNPd25Qcm9wZXJ0eShwYXR0ZXJuTmFtZSkpIHBhdHRlcm5zW3BhdHRlcm5OYW1lXSA9IG5ldyBSZWdFeHAoXCJeXCIgKyBwYXR0ZXJuc1twYXR0ZXJuTmFtZV0pO1xuXG4vLyBOYW1lcyBiZWdpbm5pbmcgXCJ3aXRoLVwiIGFuZCBcIndpdGhvdXQtXCIgYXJlIGNvbW1vbmx5XG4vLyB1c2VkIGFzIHN0YXRlbWVudCBtYWNyb1xucGF0dGVybnNbXCJrZXl3b3JkXCJdID0gWy9ed2l0aCg/Om91dCk/LVstX2EtekEtWj8hKkA8PiQlXSsvXTtcbnZhciBzdHlsZXMgPSB7fTtcbnN0eWxlc1tcImtleXdvcmRcIl0gPSBcImtleXdvcmRcIjtcbnN0eWxlc1tcImRlZmluaXRpb25cIl0gPSBcImRlZlwiO1xuc3R5bGVzW1wic2ltcGxlRGVmaW5pdGlvblwiXSA9IFwiZGVmXCI7XG5zdHlsZXNbXCJzaWduYWxpbmdDYWxsc1wiXSA9IFwiYnVpbHRpblwiO1xuXG4vLyBwcm90ZWN0ZWQgd29yZHMgbG9va3VwIHRhYmxlXG52YXIgd29yZExvb2t1cCA9IHt9O1xudmFyIHN0eWxlTG9va3VwID0ge307XG5mb3JFYWNoKFtcImtleXdvcmRcIiwgXCJkZWZpbml0aW9uXCIsIFwic2ltcGxlRGVmaW5pdGlvblwiLCBcInNpZ25hbGluZ0NhbGxzXCJdLCBmdW5jdGlvbiAodHlwZSkge1xuICBmb3JFYWNoKHdvcmRzW3R5cGVdLCBmdW5jdGlvbiAod29yZCkge1xuICAgIHdvcmRMb29rdXBbd29yZF0gPSB0eXBlO1xuICAgIHN0eWxlTG9va3VwW3dvcmRdID0gc3R5bGVzW3R5cGVdO1xuICB9KTtcbn0pO1xuZnVuY3Rpb24gY2hhaW4oc3RyZWFtLCBzdGF0ZSwgZikge1xuICBzdGF0ZS50b2tlbml6ZSA9IGY7XG4gIHJldHVybiBmKHN0cmVhbSwgc3RhdGUpO1xufVxuZnVuY3Rpb24gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpIHtcbiAgLy8gU3RyaW5nXG4gIHZhciBjaCA9IHN0cmVhbS5wZWVrKCk7XG4gIGlmIChjaCA9PSBcIidcIiB8fCBjaCA9PSAnXCInKSB7XG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICByZXR1cm4gY2hhaW4oc3RyZWFtLCBzdGF0ZSwgdG9rZW5TdHJpbmcoY2gsIFwic3RyaW5nXCIpKTtcbiAgfVxuICAvLyBDb21tZW50XG4gIGVsc2UgaWYgKGNoID09IFwiL1wiKSB7XG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICBpZiAoc3RyZWFtLmVhdChcIipcIikpIHtcbiAgICAgIHJldHVybiBjaGFpbihzdHJlYW0sIHN0YXRlLCB0b2tlbkNvbW1lbnQpO1xuICAgIH0gZWxzZSBpZiAoc3RyZWFtLmVhdChcIi9cIikpIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICB9XG4gICAgc3RyZWFtLmJhY2tVcCgxKTtcbiAgfVxuICAvLyBEZWNpbWFsXG4gIGVsc2UgaWYgKC9bK1xcLVxcZFxcLl0vLnRlc3QoY2gpKSB7XG4gICAgaWYgKHN0cmVhbS5tYXRjaCgvXlsrLV0/WzAtOV0qXFwuWzAtOV0qKFtlc2R4XVsrLV0/WzAtOV0rKT8vaSkgfHwgc3RyZWFtLm1hdGNoKC9eWystXT9bMC05XSsoW2VzZHhdWystXT9bMC05XSspL2kpIHx8IHN0cmVhbS5tYXRjaCgvXlsrLV0/XFxkKy8pKSB7XG4gICAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgICB9XG4gIH1cbiAgLy8gSGFzaFxuICBlbHNlIGlmIChjaCA9PSBcIiNcIikge1xuICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgLy8gU3ltYm9sIHdpdGggc3RyaW5nIHN5bnRheFxuICAgIGNoID0gc3RyZWFtLnBlZWsoKTtcbiAgICBpZiAoY2ggPT0gJ1wiJykge1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIHJldHVybiBjaGFpbihzdHJlYW0sIHN0YXRlLCB0b2tlblN0cmluZygnXCInLCBcInN0cmluZ1wiKSk7XG4gICAgfVxuICAgIC8vIEJpbmFyeSBudW1iZXJcbiAgICBlbHNlIGlmIChjaCA9PSBcImJcIikge1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIHN0cmVhbS5lYXRXaGlsZSgvWzAxXS8pO1xuICAgICAgcmV0dXJuIFwibnVtYmVyXCI7XG4gICAgfVxuICAgIC8vIEhleCBudW1iZXJcbiAgICBlbHNlIGlmIChjaCA9PSBcInhcIikge1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcZGEtZl0vaSk7XG4gICAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgICB9XG4gICAgLy8gT2N0YWwgbnVtYmVyXG4gICAgZWxzZSBpZiAoY2ggPT0gXCJvXCIpIHtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1swLTddLyk7XG4gICAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgICB9XG4gICAgLy8gVG9rZW4gY29uY2F0ZW5hdGlvbiBpbiBtYWNyb3NcbiAgICBlbHNlIGlmIChjaCA9PSAnIycpIHtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICByZXR1cm4gXCJwdW5jdHVhdGlvblwiO1xuICAgIH1cbiAgICAvLyBTZXF1ZW5jZSBsaXRlcmFsc1xuICAgIGVsc2UgaWYgKGNoID09ICdbJyB8fCBjaCA9PSAnKCcpIHtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICByZXR1cm4gXCJicmFja2V0XCI7XG4gICAgICAvLyBIYXNoIHN5bWJvbFxuICAgIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKC9mfHR8YWxsLWtleXN8aW5jbHVkZXxrZXl8bmV4dHxyZXN0L2kpKSB7XG4gICAgICByZXR1cm4gXCJhdG9tXCI7XG4gICAgfSBlbHNlIHtcbiAgICAgIHN0cmVhbS5lYXRXaGlsZSgvWy1hLXpBLVpdLyk7XG4gICAgICByZXR1cm4gXCJlcnJvclwiO1xuICAgIH1cbiAgfSBlbHNlIGlmIChjaCA9PSBcIn5cIikge1xuICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgY2ggPSBzdHJlYW0ucGVlaygpO1xuICAgIGlmIChjaCA9PSBcIj1cIikge1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIGNoID0gc3RyZWFtLnBlZWsoKTtcbiAgICAgIGlmIChjaCA9PSBcIj1cIikge1xuICAgICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgICByZXR1cm4gXCJvcGVyYXRvclwiO1xuICAgICAgfVxuICAgICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgICB9XG4gICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgfSBlbHNlIGlmIChjaCA9PSBcIjpcIikge1xuICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgY2ggPSBzdHJlYW0ucGVlaygpO1xuICAgIGlmIChjaCA9PSBcIj1cIikge1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gICAgfSBlbHNlIGlmIChjaCA9PSBcIjpcIikge1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIHJldHVybiBcInB1bmN0dWF0aW9uXCI7XG4gICAgfVxuICB9IGVsc2UgaWYgKFwiW10oKXt9XCIuaW5kZXhPZihjaCkgIT0gLTEpIHtcbiAgICBzdHJlYW0ubmV4dCgpO1xuICAgIHJldHVybiBcImJyYWNrZXRcIjtcbiAgfSBlbHNlIGlmIChcIi4sXCIuaW5kZXhPZihjaCkgIT0gLTEpIHtcbiAgICBzdHJlYW0ubmV4dCgpO1xuICAgIHJldHVybiBcInB1bmN0dWF0aW9uXCI7XG4gIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKFwiZW5kXCIpKSB7XG4gICAgcmV0dXJuIFwia2V5d29yZFwiO1xuICB9XG4gIGZvciAodmFyIG5hbWUgaW4gcGF0dGVybnMpIHtcbiAgICBpZiAocGF0dGVybnMuaGFzT3duUHJvcGVydHkobmFtZSkpIHtcbiAgICAgIHZhciBwYXR0ZXJuID0gcGF0dGVybnNbbmFtZV07XG4gICAgICBpZiAocGF0dGVybiBpbnN0YW5jZW9mIEFycmF5ICYmIHNvbWUocGF0dGVybiwgZnVuY3Rpb24gKHApIHtcbiAgICAgICAgcmV0dXJuIHN0cmVhbS5tYXRjaChwKTtcbiAgICAgIH0pIHx8IHN0cmVhbS5tYXRjaChwYXR0ZXJuKSkgcmV0dXJuIHBhdHRlcm5TdHlsZXNbbmFtZV07XG4gICAgfVxuICB9XG4gIGlmICgvWytcXC0qXFwvXj08PiZ8XS8udGVzdChjaCkpIHtcbiAgICBzdHJlYW0ubmV4dCgpO1xuICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gIH1cbiAgaWYgKHN0cmVhbS5tYXRjaChcImRlZmluZVwiKSkge1xuICAgIHJldHVybiBcImRlZlwiO1xuICB9IGVsc2Uge1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcLV0vKTtcbiAgICAvLyBLZXl3b3JkXG4gICAgaWYgKHdvcmRMb29rdXAuaGFzT3duUHJvcGVydHkoc3RyZWFtLmN1cnJlbnQoKSkpIHtcbiAgICAgIHJldHVybiBzdHlsZUxvb2t1cFtzdHJlYW0uY3VycmVudCgpXTtcbiAgICB9IGVsc2UgaWYgKHN0cmVhbS5jdXJyZW50KCkubWF0Y2goc3ltYm9sKSkge1xuICAgICAgcmV0dXJuIFwidmFyaWFibGVcIjtcbiAgICB9IGVsc2Uge1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIHJldHVybiBcInZhcmlhYmxlTmFtZS5zdGFuZGFyZFwiO1xuICAgIH1cbiAgfVxufVxuZnVuY3Rpb24gdG9rZW5Db21tZW50KHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIG1heWJlRW5kID0gZmFsc2UsXG4gICAgbWF5YmVOZXN0ZWQgPSBmYWxzZSxcbiAgICBuZXN0ZWRDb3VudCA9IDAsXG4gICAgY2g7XG4gIHdoaWxlIChjaCA9IHN0cmVhbS5uZXh0KCkpIHtcbiAgICBpZiAoY2ggPT0gXCIvXCIgJiYgbWF5YmVFbmQpIHtcbiAgICAgIGlmIChuZXN0ZWRDb3VudCA+IDApIHtcbiAgICAgICAgbmVzdGVkQ291bnQtLTtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICB9IGVsc2UgaWYgKGNoID09IFwiKlwiICYmIG1heWJlTmVzdGVkKSB7XG4gICAgICBuZXN0ZWRDb3VudCsrO1xuICAgIH1cbiAgICBtYXliZUVuZCA9IGNoID09IFwiKlwiO1xuICAgIG1heWJlTmVzdGVkID0gY2ggPT0gXCIvXCI7XG4gIH1cbiAgcmV0dXJuIFwiY29tbWVudFwiO1xufVxuZnVuY3Rpb24gdG9rZW5TdHJpbmcocXVvdGUsIHN0eWxlKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBlc2NhcGVkID0gZmFsc2UsXG4gICAgICBuZXh0LFxuICAgICAgZW5kID0gZmFsc2U7XG4gICAgd2hpbGUgKChuZXh0ID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgICAgaWYgKG5leHQgPT0gcXVvdGUgJiYgIWVzY2FwZWQpIHtcbiAgICAgICAgZW5kID0gdHJ1ZTtcbiAgICAgICAgYnJlYWs7XG4gICAgICB9XG4gICAgICBlc2NhcGVkID0gIWVzY2FwZWQgJiYgbmV4dCA9PSBcIlxcXFxcIjtcbiAgICB9XG4gICAgaWYgKGVuZCB8fCAhZXNjYXBlZCkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgfVxuICAgIHJldHVybiBzdHlsZTtcbiAgfTtcbn1cblxuLy8gSW50ZXJmYWNlXG5leHBvcnQgY29uc3QgZHlsYW4gPSB7XG4gIG5hbWU6IFwiZHlsYW5cIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB7XG4gICAgICB0b2tlbml6ZTogdG9rZW5CYXNlLFxuICAgICAgY3VycmVudEluZGVudDogMFxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkgcmV0dXJuIG51bGw7XG4gICAgdmFyIHN0eWxlID0gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gICAgcmV0dXJuIHN0eWxlO1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBjb21tZW50VG9rZW5zOiB7XG4gICAgICBibG9jazoge1xuICAgICAgICBvcGVuOiBcIi8qXCIsXG4gICAgICAgIGNsb3NlOiBcIiovXCJcbiAgICAgIH1cbiAgICB9XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==