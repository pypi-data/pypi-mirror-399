"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[5452],{

/***/ 5452
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   tiddlyWiki: () => (/* binding */ tiddlyWiki)
/* harmony export */ });
// Tokenizer
var textwords = {};
var keywords = {
  "allTags": true,
  "closeAll": true,
  "list": true,
  "newJournal": true,
  "newTiddler": true,
  "permaview": true,
  "saveChanges": true,
  "search": true,
  "slider": true,
  "tabs": true,
  "tag": true,
  "tagging": true,
  "tags": true,
  "tiddler": true,
  "timeline": true,
  "today": true,
  "version": true,
  "option": true,
  "with": true,
  "filter": true
};
var isSpaceName = /[\w_\-]/i,
  reHR = /^\-\-\-\-+$/,
  // <hr>
  reWikiCommentStart = /^\/\*\*\*$/,
  // /***
  reWikiCommentStop = /^\*\*\*\/$/,
  // ***/
  reBlockQuote = /^<<<$/,
  reJsCodeStart = /^\/\/\{\{\{$/,
  // //{{{ js block start
  reJsCodeStop = /^\/\/\}\}\}$/,
  // //}}} js stop
  reXmlCodeStart = /^<!--\{\{\{-->$/,
  // xml block start
  reXmlCodeStop = /^<!--\}\}\}-->$/,
  // xml stop

  reCodeBlockStart = /^\{\{\{$/,
  // {{{ TW text div block start
  reCodeBlockStop = /^\}\}\}$/,
  // }}} TW text stop

  reUntilCodeStop = /.*?\}\}\}/;
function chain(stream, state, f) {
  state.tokenize = f;
  return f(stream, state);
}
function tokenBase(stream, state) {
  var sol = stream.sol(),
    ch = stream.peek();
  state.block = false; // indicates the start of a code block.

  // check start of  blocks
  if (sol && /[<\/\*{}\-]/.test(ch)) {
    if (stream.match(reCodeBlockStart)) {
      state.block = true;
      return chain(stream, state, twTokenCode);
    }
    if (stream.match(reBlockQuote)) return 'quote';
    if (stream.match(reWikiCommentStart) || stream.match(reWikiCommentStop)) return 'comment';
    if (stream.match(reJsCodeStart) || stream.match(reJsCodeStop) || stream.match(reXmlCodeStart) || stream.match(reXmlCodeStop)) return 'comment';
    if (stream.match(reHR)) return 'contentSeparator';
  }
  stream.next();
  if (sol && /[\/\*!#;:>|]/.test(ch)) {
    if (ch == "!") {
      // tw header
      stream.skipToEnd();
      return "header";
    }
    if (ch == "*") {
      // tw list
      stream.eatWhile('*');
      return "comment";
    }
    if (ch == "#") {
      // tw numbered list
      stream.eatWhile('#');
      return "comment";
    }
    if (ch == ";") {
      // definition list, term
      stream.eatWhile(';');
      return "comment";
    }
    if (ch == ":") {
      // definition list, description
      stream.eatWhile(':');
      return "comment";
    }
    if (ch == ">") {
      // single line quote
      stream.eatWhile(">");
      return "quote";
    }
    if (ch == '|') return 'header';
  }
  if (ch == '{' && stream.match('{{')) return chain(stream, state, twTokenCode);

  // rudimentary html:// file:// link matching. TW knows much more ...
  if (/[hf]/i.test(ch) && /[ti]/i.test(stream.peek()) && stream.match(/\b(ttps?|tp|ile):\/\/[\-A-Z0-9+&@#\/%?=~_|$!:,.;]*[A-Z0-9+&@#\/%=~_|$]/i)) return "link";

  // just a little string indicator, don't want to have the whole string covered
  if (ch == '"') return 'string';
  if (ch == '~')
    // _no_ CamelCase indicator should be bold
    return 'brace';
  if (/[\[\]]/.test(ch) && stream.match(ch))
    // check for [[..]]
    return 'brace';
  if (ch == "@") {
    // check for space link. TODO fix @@...@@ highlighting
    stream.eatWhile(isSpaceName);
    return "link";
  }
  if (/\d/.test(ch)) {
    // numbers
    stream.eatWhile(/\d/);
    return "number";
  }
  if (ch == "/") {
    // tw invisible comment
    if (stream.eat("%")) {
      return chain(stream, state, twTokenComment);
    } else if (stream.eat("/")) {
      //
      return chain(stream, state, twTokenEm);
    }
  }
  if (ch == "_" && stream.eat("_"))
    // tw underline
    return chain(stream, state, twTokenUnderline);

  // strikethrough and mdash handling
  if (ch == "-" && stream.eat("-")) {
    // if strikethrough looks ugly, change CSS.
    if (stream.peek() != ' ') return chain(stream, state, twTokenStrike);
    // mdash
    if (stream.peek() == ' ') return 'brace';
  }
  if (ch == "'" && stream.eat("'"))
    // tw bold
    return chain(stream, state, twTokenStrong);
  if (ch == "<" && stream.eat("<"))
    // tw macro
    return chain(stream, state, twTokenMacro);

  // core macro handling
  stream.eatWhile(/[\w\$_]/);
  return textwords.propertyIsEnumerable(stream.current()) ? "keyword" : null;
}

// tw invisible comment
function twTokenComment(stream, state) {
  var maybeEnd = false,
    ch;
  while (ch = stream.next()) {
    if (ch == "/" && maybeEnd) {
      state.tokenize = tokenBase;
      break;
    }
    maybeEnd = ch == "%";
  }
  return "comment";
}

// tw strong / bold
function twTokenStrong(stream, state) {
  var maybeEnd = false,
    ch;
  while (ch = stream.next()) {
    if (ch == "'" && maybeEnd) {
      state.tokenize = tokenBase;
      break;
    }
    maybeEnd = ch == "'";
  }
  return "strong";
}

// tw code
function twTokenCode(stream, state) {
  var sb = state.block;
  if (sb && stream.current()) {
    return "comment";
  }
  if (!sb && stream.match(reUntilCodeStop)) {
    state.tokenize = tokenBase;
    return "comment";
  }
  if (sb && stream.sol() && stream.match(reCodeBlockStop)) {
    state.tokenize = tokenBase;
    return "comment";
  }
  stream.next();
  return "comment";
}

// tw em / italic
function twTokenEm(stream, state) {
  var maybeEnd = false,
    ch;
  while (ch = stream.next()) {
    if (ch == "/" && maybeEnd) {
      state.tokenize = tokenBase;
      break;
    }
    maybeEnd = ch == "/";
  }
  return "emphasis";
}

// tw underlined text
function twTokenUnderline(stream, state) {
  var maybeEnd = false,
    ch;
  while (ch = stream.next()) {
    if (ch == "_" && maybeEnd) {
      state.tokenize = tokenBase;
      break;
    }
    maybeEnd = ch == "_";
  }
  return "link";
}

// tw strike through text looks ugly
// change CSS if needed
function twTokenStrike(stream, state) {
  var maybeEnd = false,
    ch;
  while (ch = stream.next()) {
    if (ch == "-" && maybeEnd) {
      state.tokenize = tokenBase;
      break;
    }
    maybeEnd = ch == "-";
  }
  return "deleted";
}

// macro
function twTokenMacro(stream, state) {
  if (stream.current() == '<<') {
    return 'meta';
  }
  var ch = stream.next();
  if (!ch) {
    state.tokenize = tokenBase;
    return null;
  }
  if (ch == ">") {
    if (stream.peek() == '>') {
      stream.next();
      state.tokenize = tokenBase;
      return "meta";
    }
  }
  stream.eatWhile(/[\w\$_]/);
  return keywords.propertyIsEnumerable(stream.current()) ? "keyword" : null;
}

// Interface
const tiddlyWiki = {
  name: "tiddlywiki",
  startState: function () {
    return {
      tokenize: tokenBase
    };
  },
  token: function (stream, state) {
    if (stream.eatSpace()) return null;
    var style = state.tokenize(stream, state);
    return style;
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNTQ1Mi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvdGlkZGx5d2lraS5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyIvLyBUb2tlbml6ZXJcbnZhciB0ZXh0d29yZHMgPSB7fTtcbnZhciBrZXl3b3JkcyA9IHtcbiAgXCJhbGxUYWdzXCI6IHRydWUsXG4gIFwiY2xvc2VBbGxcIjogdHJ1ZSxcbiAgXCJsaXN0XCI6IHRydWUsXG4gIFwibmV3Sm91cm5hbFwiOiB0cnVlLFxuICBcIm5ld1RpZGRsZXJcIjogdHJ1ZSxcbiAgXCJwZXJtYXZpZXdcIjogdHJ1ZSxcbiAgXCJzYXZlQ2hhbmdlc1wiOiB0cnVlLFxuICBcInNlYXJjaFwiOiB0cnVlLFxuICBcInNsaWRlclwiOiB0cnVlLFxuICBcInRhYnNcIjogdHJ1ZSxcbiAgXCJ0YWdcIjogdHJ1ZSxcbiAgXCJ0YWdnaW5nXCI6IHRydWUsXG4gIFwidGFnc1wiOiB0cnVlLFxuICBcInRpZGRsZXJcIjogdHJ1ZSxcbiAgXCJ0aW1lbGluZVwiOiB0cnVlLFxuICBcInRvZGF5XCI6IHRydWUsXG4gIFwidmVyc2lvblwiOiB0cnVlLFxuICBcIm9wdGlvblwiOiB0cnVlLFxuICBcIndpdGhcIjogdHJ1ZSxcbiAgXCJmaWx0ZXJcIjogdHJ1ZVxufTtcbnZhciBpc1NwYWNlTmFtZSA9IC9bXFx3X1xcLV0vaSxcbiAgcmVIUiA9IC9eXFwtXFwtXFwtXFwtKyQvLFxuICAvLyA8aHI+XG4gIHJlV2lraUNvbW1lbnRTdGFydCA9IC9eXFwvXFwqXFwqXFwqJC8sXG4gIC8vIC8qKipcbiAgcmVXaWtpQ29tbWVudFN0b3AgPSAvXlxcKlxcKlxcKlxcLyQvLFxuICAvLyAqKiovXG4gIHJlQmxvY2tRdW90ZSA9IC9ePDw8JC8sXG4gIHJlSnNDb2RlU3RhcnQgPSAvXlxcL1xcL1xce1xce1xceyQvLFxuICAvLyAvL3t7eyBqcyBibG9jayBzdGFydFxuICByZUpzQ29kZVN0b3AgPSAvXlxcL1xcL1xcfVxcfVxcfSQvLFxuICAvLyAvL319fSBqcyBzdG9wXG4gIHJlWG1sQ29kZVN0YXJ0ID0gL148IS0tXFx7XFx7XFx7LS0+JC8sXG4gIC8vIHhtbCBibG9jayBzdGFydFxuICByZVhtbENvZGVTdG9wID0gL148IS0tXFx9XFx9XFx9LS0+JC8sXG4gIC8vIHhtbCBzdG9wXG5cbiAgcmVDb2RlQmxvY2tTdGFydCA9IC9eXFx7XFx7XFx7JC8sXG4gIC8vIHt7eyBUVyB0ZXh0IGRpdiBibG9jayBzdGFydFxuICByZUNvZGVCbG9ja1N0b3AgPSAvXlxcfVxcfVxcfSQvLFxuICAvLyB9fX0gVFcgdGV4dCBzdG9wXG5cbiAgcmVVbnRpbENvZGVTdG9wID0gLy4qP1xcfVxcfVxcfS87XG5mdW5jdGlvbiBjaGFpbihzdHJlYW0sIHN0YXRlLCBmKSB7XG4gIHN0YXRlLnRva2VuaXplID0gZjtcbiAgcmV0dXJuIGYoc3RyZWFtLCBzdGF0ZSk7XG59XG5mdW5jdGlvbiB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgc29sID0gc3RyZWFtLnNvbCgpLFxuICAgIGNoID0gc3RyZWFtLnBlZWsoKTtcbiAgc3RhdGUuYmxvY2sgPSBmYWxzZTsgLy8gaW5kaWNhdGVzIHRoZSBzdGFydCBvZiBhIGNvZGUgYmxvY2suXG5cbiAgLy8gY2hlY2sgc3RhcnQgb2YgIGJsb2Nrc1xuICBpZiAoc29sICYmIC9bPFxcL1xcKnt9XFwtXS8udGVzdChjaCkpIHtcbiAgICBpZiAoc3RyZWFtLm1hdGNoKHJlQ29kZUJsb2NrU3RhcnQpKSB7XG4gICAgICBzdGF0ZS5ibG9jayA9IHRydWU7XG4gICAgICByZXR1cm4gY2hhaW4oc3RyZWFtLCBzdGF0ZSwgdHdUb2tlbkNvZGUpO1xuICAgIH1cbiAgICBpZiAoc3RyZWFtLm1hdGNoKHJlQmxvY2tRdW90ZSkpIHJldHVybiAncXVvdGUnO1xuICAgIGlmIChzdHJlYW0ubWF0Y2gocmVXaWtpQ29tbWVudFN0YXJ0KSB8fCBzdHJlYW0ubWF0Y2gocmVXaWtpQ29tbWVudFN0b3ApKSByZXR1cm4gJ2NvbW1lbnQnO1xuICAgIGlmIChzdHJlYW0ubWF0Y2gocmVKc0NvZGVTdGFydCkgfHwgc3RyZWFtLm1hdGNoKHJlSnNDb2RlU3RvcCkgfHwgc3RyZWFtLm1hdGNoKHJlWG1sQ29kZVN0YXJ0KSB8fCBzdHJlYW0ubWF0Y2gocmVYbWxDb2RlU3RvcCkpIHJldHVybiAnY29tbWVudCc7XG4gICAgaWYgKHN0cmVhbS5tYXRjaChyZUhSKSkgcmV0dXJuICdjb250ZW50U2VwYXJhdG9yJztcbiAgfVxuICBzdHJlYW0ubmV4dCgpO1xuICBpZiAoc29sICYmIC9bXFwvXFwqISM7Oj58XS8udGVzdChjaCkpIHtcbiAgICBpZiAoY2ggPT0gXCIhXCIpIHtcbiAgICAgIC8vIHR3IGhlYWRlclxuICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgcmV0dXJuIFwiaGVhZGVyXCI7XG4gICAgfVxuICAgIGlmIChjaCA9PSBcIipcIikge1xuICAgICAgLy8gdHcgbGlzdFxuICAgICAgc3RyZWFtLmVhdFdoaWxlKCcqJyk7XG4gICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgfVxuICAgIGlmIChjaCA9PSBcIiNcIikge1xuICAgICAgLy8gdHcgbnVtYmVyZWQgbGlzdFxuICAgICAgc3RyZWFtLmVhdFdoaWxlKCcjJyk7XG4gICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgfVxuICAgIGlmIChjaCA9PSBcIjtcIikge1xuICAgICAgLy8gZGVmaW5pdGlvbiBsaXN0LCB0ZXJtXG4gICAgICBzdHJlYW0uZWF0V2hpbGUoJzsnKTtcbiAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICB9XG4gICAgaWYgKGNoID09IFwiOlwiKSB7XG4gICAgICAvLyBkZWZpbml0aW9uIGxpc3QsIGRlc2NyaXB0aW9uXG4gICAgICBzdHJlYW0uZWF0V2hpbGUoJzonKTtcbiAgICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgICB9XG4gICAgaWYgKGNoID09IFwiPlwiKSB7XG4gICAgICAvLyBzaW5nbGUgbGluZSBxdW90ZVxuICAgICAgc3RyZWFtLmVhdFdoaWxlKFwiPlwiKTtcbiAgICAgIHJldHVybiBcInF1b3RlXCI7XG4gICAgfVxuICAgIGlmIChjaCA9PSAnfCcpIHJldHVybiAnaGVhZGVyJztcbiAgfVxuICBpZiAoY2ggPT0gJ3snICYmIHN0cmVhbS5tYXRjaCgne3snKSkgcmV0dXJuIGNoYWluKHN0cmVhbSwgc3RhdGUsIHR3VG9rZW5Db2RlKTtcblxuICAvLyBydWRpbWVudGFyeSBodG1sOi8vIGZpbGU6Ly8gbGluayBtYXRjaGluZy4gVFcga25vd3MgbXVjaCBtb3JlIC4uLlxuICBpZiAoL1toZl0vaS50ZXN0KGNoKSAmJiAvW3RpXS9pLnRlc3Qoc3RyZWFtLnBlZWsoKSkgJiYgc3RyZWFtLm1hdGNoKC9cXGIodHRwcz98dHB8aWxlKTpcXC9cXC9bXFwtQS1aMC05KyZAI1xcLyU/PX5ffCQhOiwuO10qW0EtWjAtOSsmQCNcXC8lPX5ffCRdL2kpKSByZXR1cm4gXCJsaW5rXCI7XG5cbiAgLy8ganVzdCBhIGxpdHRsZSBzdHJpbmcgaW5kaWNhdG9yLCBkb24ndCB3YW50IHRvIGhhdmUgdGhlIHdob2xlIHN0cmluZyBjb3ZlcmVkXG4gIGlmIChjaCA9PSAnXCInKSByZXR1cm4gJ3N0cmluZyc7XG4gIGlmIChjaCA9PSAnficpXG4gICAgLy8gX25vXyBDYW1lbENhc2UgaW5kaWNhdG9yIHNob3VsZCBiZSBib2xkXG4gICAgcmV0dXJuICdicmFjZSc7XG4gIGlmICgvW1xcW1xcXV0vLnRlc3QoY2gpICYmIHN0cmVhbS5tYXRjaChjaCkpXG4gICAgLy8gY2hlY2sgZm9yIFtbLi5dXVxuICAgIHJldHVybiAnYnJhY2UnO1xuICBpZiAoY2ggPT0gXCJAXCIpIHtcbiAgICAvLyBjaGVjayBmb3Igc3BhY2UgbGluay4gVE9ETyBmaXggQEAuLi5AQCBoaWdobGlnaHRpbmdcbiAgICBzdHJlYW0uZWF0V2hpbGUoaXNTcGFjZU5hbWUpO1xuICAgIHJldHVybiBcImxpbmtcIjtcbiAgfVxuICBpZiAoL1xcZC8udGVzdChjaCkpIHtcbiAgICAvLyBudW1iZXJzXG4gICAgc3RyZWFtLmVhdFdoaWxlKC9cXGQvKTtcbiAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgfVxuICBpZiAoY2ggPT0gXCIvXCIpIHtcbiAgICAvLyB0dyBpbnZpc2libGUgY29tbWVudFxuICAgIGlmIChzdHJlYW0uZWF0KFwiJVwiKSkge1xuICAgICAgcmV0dXJuIGNoYWluKHN0cmVhbSwgc3RhdGUsIHR3VG9rZW5Db21tZW50KTtcbiAgICB9IGVsc2UgaWYgKHN0cmVhbS5lYXQoXCIvXCIpKSB7XG4gICAgICAvL1xuICAgICAgcmV0dXJuIGNoYWluKHN0cmVhbSwgc3RhdGUsIHR3VG9rZW5FbSk7XG4gICAgfVxuICB9XG4gIGlmIChjaCA9PSBcIl9cIiAmJiBzdHJlYW0uZWF0KFwiX1wiKSlcbiAgICAvLyB0dyB1bmRlcmxpbmVcbiAgICByZXR1cm4gY2hhaW4oc3RyZWFtLCBzdGF0ZSwgdHdUb2tlblVuZGVybGluZSk7XG5cbiAgLy8gc3RyaWtldGhyb3VnaCBhbmQgbWRhc2ggaGFuZGxpbmdcbiAgaWYgKGNoID09IFwiLVwiICYmIHN0cmVhbS5lYXQoXCItXCIpKSB7XG4gICAgLy8gaWYgc3RyaWtldGhyb3VnaCBsb29rcyB1Z2x5LCBjaGFuZ2UgQ1NTLlxuICAgIGlmIChzdHJlYW0ucGVlaygpICE9ICcgJykgcmV0dXJuIGNoYWluKHN0cmVhbSwgc3RhdGUsIHR3VG9rZW5TdHJpa2UpO1xuICAgIC8vIG1kYXNoXG4gICAgaWYgKHN0cmVhbS5wZWVrKCkgPT0gJyAnKSByZXR1cm4gJ2JyYWNlJztcbiAgfVxuICBpZiAoY2ggPT0gXCInXCIgJiYgc3RyZWFtLmVhdChcIidcIikpXG4gICAgLy8gdHcgYm9sZFxuICAgIHJldHVybiBjaGFpbihzdHJlYW0sIHN0YXRlLCB0d1Rva2VuU3Ryb25nKTtcbiAgaWYgKGNoID09IFwiPFwiICYmIHN0cmVhbS5lYXQoXCI8XCIpKVxuICAgIC8vIHR3IG1hY3JvXG4gICAgcmV0dXJuIGNoYWluKHN0cmVhbSwgc3RhdGUsIHR3VG9rZW5NYWNybyk7XG5cbiAgLy8gY29yZSBtYWNybyBoYW5kbGluZ1xuICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXCRfXS8pO1xuICByZXR1cm4gdGV4dHdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKHN0cmVhbS5jdXJyZW50KCkpID8gXCJrZXl3b3JkXCIgOiBudWxsO1xufVxuXG4vLyB0dyBpbnZpc2libGUgY29tbWVudFxuZnVuY3Rpb24gdHdUb2tlbkNvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgbWF5YmVFbmQgPSBmYWxzZSxcbiAgICBjaDtcbiAgd2hpbGUgKGNoID0gc3RyZWFtLm5leHQoKSkge1xuICAgIGlmIChjaCA9PSBcIi9cIiAmJiBtYXliZUVuZCkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgICBicmVhaztcbiAgICB9XG4gICAgbWF5YmVFbmQgPSBjaCA9PSBcIiVcIjtcbiAgfVxuICByZXR1cm4gXCJjb21tZW50XCI7XG59XG5cbi8vIHR3IHN0cm9uZyAvIGJvbGRcbmZ1bmN0aW9uIHR3VG9rZW5TdHJvbmcoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgbWF5YmVFbmQgPSBmYWxzZSxcbiAgICBjaDtcbiAgd2hpbGUgKGNoID0gc3RyZWFtLm5leHQoKSkge1xuICAgIGlmIChjaCA9PSBcIidcIiAmJiBtYXliZUVuZCkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgICBicmVhaztcbiAgICB9XG4gICAgbWF5YmVFbmQgPSBjaCA9PSBcIidcIjtcbiAgfVxuICByZXR1cm4gXCJzdHJvbmdcIjtcbn1cblxuLy8gdHcgY29kZVxuZnVuY3Rpb24gdHdUb2tlbkNvZGUoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgc2IgPSBzdGF0ZS5ibG9jaztcbiAgaWYgKHNiICYmIHN0cmVhbS5jdXJyZW50KCkpIHtcbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH1cbiAgaWYgKCFzYiAmJiBzdHJlYW0ubWF0Y2gocmVVbnRpbENvZGVTdG9wKSkge1xuICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgfVxuICBpZiAoc2IgJiYgc3RyZWFtLnNvbCgpICYmIHN0cmVhbS5tYXRjaChyZUNvZGVCbG9ja1N0b3ApKSB7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICB9XG4gIHN0cmVhbS5uZXh0KCk7XG4gIHJldHVybiBcImNvbW1lbnRcIjtcbn1cblxuLy8gdHcgZW0gLyBpdGFsaWNcbmZ1bmN0aW9uIHR3VG9rZW5FbShzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBtYXliZUVuZCA9IGZhbHNlLFxuICAgIGNoO1xuICB3aGlsZSAoY2ggPSBzdHJlYW0ubmV4dCgpKSB7XG4gICAgaWYgKGNoID09IFwiL1wiICYmIG1heWJlRW5kKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgIGJyZWFrO1xuICAgIH1cbiAgICBtYXliZUVuZCA9IGNoID09IFwiL1wiO1xuICB9XG4gIHJldHVybiBcImVtcGhhc2lzXCI7XG59XG5cbi8vIHR3IHVuZGVybGluZWQgdGV4dFxuZnVuY3Rpb24gdHdUb2tlblVuZGVybGluZShzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBtYXliZUVuZCA9IGZhbHNlLFxuICAgIGNoO1xuICB3aGlsZSAoY2ggPSBzdHJlYW0ubmV4dCgpKSB7XG4gICAgaWYgKGNoID09IFwiX1wiICYmIG1heWJlRW5kKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgIGJyZWFrO1xuICAgIH1cbiAgICBtYXliZUVuZCA9IGNoID09IFwiX1wiO1xuICB9XG4gIHJldHVybiBcImxpbmtcIjtcbn1cblxuLy8gdHcgc3RyaWtlIHRocm91Z2ggdGV4dCBsb29rcyB1Z2x5XG4vLyBjaGFuZ2UgQ1NTIGlmIG5lZWRlZFxuZnVuY3Rpb24gdHdUb2tlblN0cmlrZShzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBtYXliZUVuZCA9IGZhbHNlLFxuICAgIGNoO1xuICB3aGlsZSAoY2ggPSBzdHJlYW0ubmV4dCgpKSB7XG4gICAgaWYgKGNoID09IFwiLVwiICYmIG1heWJlRW5kKSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgIGJyZWFrO1xuICAgIH1cbiAgICBtYXliZUVuZCA9IGNoID09IFwiLVwiO1xuICB9XG4gIHJldHVybiBcImRlbGV0ZWRcIjtcbn1cblxuLy8gbWFjcm9cbmZ1bmN0aW9uIHR3VG9rZW5NYWNybyhzdHJlYW0sIHN0YXRlKSB7XG4gIGlmIChzdHJlYW0uY3VycmVudCgpID09ICc8PCcpIHtcbiAgICByZXR1cm4gJ21ldGEnO1xuICB9XG4gIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gIGlmICghY2gpIHtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICByZXR1cm4gbnVsbDtcbiAgfVxuICBpZiAoY2ggPT0gXCI+XCIpIHtcbiAgICBpZiAoc3RyZWFtLnBlZWsoKSA9PSAnPicpIHtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgIHJldHVybiBcIm1ldGFcIjtcbiAgICB9XG4gIH1cbiAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFwkX10vKTtcbiAgcmV0dXJuIGtleXdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKHN0cmVhbS5jdXJyZW50KCkpID8gXCJrZXl3b3JkXCIgOiBudWxsO1xufVxuXG4vLyBJbnRlcmZhY2VcbmV4cG9ydCBjb25zdCB0aWRkbHlXaWtpID0ge1xuICBuYW1lOiBcInRpZGRseXdpa2lcIixcbiAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB7XG4gICAgICB0b2tlbml6ZTogdG9rZW5CYXNlXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgICB2YXIgc3R5bGUgPSBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICByZXR1cm4gc3R5bGU7XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==