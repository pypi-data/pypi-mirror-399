"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[5492],{

/***/ 25492
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   xQuery: () => (/* binding */ xQuery)
/* harmony export */ });
// The keywords object is set to the result of this self executing
// function. Each keyword is a property of the keywords object whose
// value is {type: atype, style: astyle}
var keywords = function () {
  // convenience functions used to build keywords object
  function kw(type) {
    return {
      type: type,
      style: "keyword"
    };
  }
  var operator = kw("operator"),
    atom = {
      type: "atom",
      style: "atom"
    },
    punctuation = {
      type: "punctuation",
      style: null
    },
    qualifier = {
      type: "axis_specifier",
      style: "qualifier"
    };

  // kwObj is what is return from this function at the end
  var kwObj = {
    ',': punctuation
  };

  // a list of 'basic' keywords. For each add a property to kwObj with the value of
  // {type: basic[i], style: "keyword"} e.g. 'after' --> {type: "after", style: "keyword"}
  var basic = ['after', 'all', 'allowing', 'ancestor', 'ancestor-or-self', 'any', 'array', 'as', 'ascending', 'at', 'attribute', 'base-uri', 'before', 'boundary-space', 'by', 'case', 'cast', 'castable', 'catch', 'child', 'collation', 'comment', 'construction', 'contains', 'content', 'context', 'copy', 'copy-namespaces', 'count', 'decimal-format', 'declare', 'default', 'delete', 'descendant', 'descendant-or-self', 'descending', 'diacritics', 'different', 'distance', 'document', 'document-node', 'element', 'else', 'empty', 'empty-sequence', 'encoding', 'end', 'entire', 'every', 'exactly', 'except', 'external', 'first', 'following', 'following-sibling', 'for', 'from', 'ftand', 'ftnot', 'ft-option', 'ftor', 'function', 'fuzzy', 'greatest', 'group', 'if', 'import', 'in', 'inherit', 'insensitive', 'insert', 'instance', 'intersect', 'into', 'invoke', 'is', 'item', 'language', 'last', 'lax', 'least', 'let', 'levels', 'lowercase', 'map', 'modify', 'module', 'most', 'namespace', 'next', 'no', 'node', 'nodes', 'no-inherit', 'no-preserve', 'not', 'occurs', 'of', 'only', 'option', 'order', 'ordered', 'ordering', 'paragraph', 'paragraphs', 'parent', 'phrase', 'preceding', 'preceding-sibling', 'preserve', 'previous', 'processing-instruction', 'relationship', 'rename', 'replace', 'return', 'revalidation', 'same', 'satisfies', 'schema', 'schema-attribute', 'schema-element', 'score', 'self', 'sensitive', 'sentence', 'sentences', 'sequence', 'skip', 'sliding', 'some', 'stable', 'start', 'stemming', 'stop', 'strict', 'strip', 'switch', 'text', 'then', 'thesaurus', 'times', 'to', 'transform', 'treat', 'try', 'tumbling', 'type', 'typeswitch', 'union', 'unordered', 'update', 'updating', 'uppercase', 'using', 'validate', 'value', 'variable', 'version', 'weight', 'when', 'where', 'wildcards', 'window', 'with', 'without', 'word', 'words', 'xquery'];
  for (var i = 0, l = basic.length; i < l; i++) {
    kwObj[basic[i]] = kw(basic[i]);
  }
  ;

  // a list of types. For each add a property to kwObj with the value of
  // {type: "atom", style: "atom"}
  var types = ['xs:anyAtomicType', 'xs:anySimpleType', 'xs:anyType', 'xs:anyURI', 'xs:base64Binary', 'xs:boolean', 'xs:byte', 'xs:date', 'xs:dateTime', 'xs:dateTimeStamp', 'xs:dayTimeDuration', 'xs:decimal', 'xs:double', 'xs:duration', 'xs:ENTITIES', 'xs:ENTITY', 'xs:float', 'xs:gDay', 'xs:gMonth', 'xs:gMonthDay', 'xs:gYear', 'xs:gYearMonth', 'xs:hexBinary', 'xs:ID', 'xs:IDREF', 'xs:IDREFS', 'xs:int', 'xs:integer', 'xs:item', 'xs:java', 'xs:language', 'xs:long', 'xs:Name', 'xs:NCName', 'xs:negativeInteger', 'xs:NMTOKEN', 'xs:NMTOKENS', 'xs:nonNegativeInteger', 'xs:nonPositiveInteger', 'xs:normalizedString', 'xs:NOTATION', 'xs:numeric', 'xs:positiveInteger', 'xs:precisionDecimal', 'xs:QName', 'xs:short', 'xs:string', 'xs:time', 'xs:token', 'xs:unsignedByte', 'xs:unsignedInt', 'xs:unsignedLong', 'xs:unsignedShort', 'xs:untyped', 'xs:untypedAtomic', 'xs:yearMonthDuration'];
  for (var i = 0, l = types.length; i < l; i++) {
    kwObj[types[i]] = atom;
  }
  ;

  // each operator will add a property to kwObj with value of {type: "operator", style: "keyword"}
  var operators = ['eq', 'ne', 'lt', 'le', 'gt', 'ge', ':=', '=', '>', '>=', '<', '<=', '.', '|', '?', 'and', 'or', 'div', 'idiv', 'mod', '*', '/', '+', '-'];
  for (var i = 0, l = operators.length; i < l; i++) {
    kwObj[operators[i]] = operator;
  }
  ;

  // each axis_specifiers will add a property to kwObj with value of {type: "axis_specifier", style: "qualifier"}
  var axis_specifiers = ["self::", "attribute::", "child::", "descendant::", "descendant-or-self::", "parent::", "ancestor::", "ancestor-or-self::", "following::", "preceding::", "following-sibling::", "preceding-sibling::"];
  for (var i = 0, l = axis_specifiers.length; i < l; i++) {
    kwObj[axis_specifiers[i]] = qualifier;
  }
  ;
  return kwObj;
}();
function chain(stream, state, f) {
  state.tokenize = f;
  return f(stream, state);
}

// the primary mode tokenizer
function tokenBase(stream, state) {
  var ch = stream.next(),
    mightBeFunction = false,
    isEQName = isEQNameAhead(stream);

  // an XML tag (if not in some sub, chained tokenizer)
  if (ch == "<") {
    if (stream.match("!--", true)) return chain(stream, state, tokenXMLComment);
    if (stream.match("![CDATA", false)) {
      state.tokenize = tokenCDATA;
      return "tag";
    }
    if (stream.match("?", false)) {
      return chain(stream, state, tokenPreProcessing);
    }
    var isclose = stream.eat("/");
    stream.eatSpace();
    var tagName = "",
      c;
    while (c = stream.eat(/[^\s\u00a0=<>\"\'\/?]/)) tagName += c;
    return chain(stream, state, tokenTag(tagName, isclose));
  }
  // start code block
  else if (ch == "{") {
    pushStateStack(state, {
      type: "codeblock"
    });
    return null;
  }
  // end code block
  else if (ch == "}") {
    popStateStack(state);
    return null;
  }
  // if we're in an XML block
  else if (isInXmlBlock(state)) {
    if (ch == ">") return "tag";else if (ch == "/" && stream.eat(">")) {
      popStateStack(state);
      return "tag";
    } else return "variable";
  }
  // if a number
  else if (/\d/.test(ch)) {
    stream.match(/^\d*(?:\.\d*)?(?:E[+\-]?\d+)?/);
    return "atom";
  }
  // comment start
  else if (ch === "(" && stream.eat(":")) {
    pushStateStack(state, {
      type: "comment"
    });
    return chain(stream, state, tokenComment);
  }
  // quoted string
  else if (!isEQName && (ch === '"' || ch === "'")) return startString(stream, state, ch);
  // variable
  else if (ch === "$") {
    return chain(stream, state, tokenVariable);
  }
  // assignment
  else if (ch === ":" && stream.eat("=")) {
    return "keyword";
  }
  // open paren
  else if (ch === "(") {
    pushStateStack(state, {
      type: "paren"
    });
    return null;
  }
  // close paren
  else if (ch === ")") {
    popStateStack(state);
    return null;
  }
  // open paren
  else if (ch === "[") {
    pushStateStack(state, {
      type: "bracket"
    });
    return null;
  }
  // close paren
  else if (ch === "]") {
    popStateStack(state);
    return null;
  } else {
    var known = keywords.propertyIsEnumerable(ch) && keywords[ch];

    // if there's a EQName ahead, consume the rest of the string portion, it's likely a function
    if (isEQName && ch === '\"') while (stream.next() !== '"') {}
    if (isEQName && ch === '\'') while (stream.next() !== '\'') {}

    // gobble up a word if the character is not known
    if (!known) stream.eatWhile(/[\w\$_-]/);

    // gobble a colon in the case that is a lib func type call fn:doc
    var foundColon = stream.eat(":");

    // if there's not a second colon, gobble another word. Otherwise, it's probably an axis specifier
    // which should get matched as a keyword
    if (!stream.eat(":") && foundColon) {
      stream.eatWhile(/[\w\$_-]/);
    }
    // if the next non whitespace character is an open paren, this is probably a function (if not a keyword of other sort)
    if (stream.match(/^[ \t]*\(/, false)) {
      mightBeFunction = true;
    }
    // is the word a keyword?
    var word = stream.current();
    known = keywords.propertyIsEnumerable(word) && keywords[word];

    // if we think it's a function call but not yet known,
    // set style to variable for now for lack of something better
    if (mightBeFunction && !known) known = {
      type: "function_call",
      style: "def"
    };

    // if the previous word was element, attribute, axis specifier, this word should be the name of that
    if (isInXmlConstructor(state)) {
      popStateStack(state);
      return "variable";
    }
    // as previously checked, if the word is element,attribute, axis specifier, call it an "xmlconstructor" and
    // push the stack so we know to look for it on the next word
    if (word == "element" || word == "attribute" || known.type == "axis_specifier") pushStateStack(state, {
      type: "xmlconstructor"
    });

    // if the word is known, return the details of that else just call this a generic 'word'
    return known ? known.style : "variable";
  }
}

// handle comments, including nested
function tokenComment(stream, state) {
  var maybeEnd = false,
    maybeNested = false,
    nestedCount = 0,
    ch;
  while (ch = stream.next()) {
    if (ch == ")" && maybeEnd) {
      if (nestedCount > 0) nestedCount--;else {
        popStateStack(state);
        break;
      }
    } else if (ch == ":" && maybeNested) {
      nestedCount++;
    }
    maybeEnd = ch == ":";
    maybeNested = ch == "(";
  }
  return "comment";
}

// tokenizer for string literals
// optionally pass a tokenizer function to set state.tokenize back to when finished
function tokenString(quote, f) {
  return function (stream, state) {
    var ch;
    while (ch = stream.next()) {
      if (ch == quote) {
        popStateStack(state);
        if (f) state.tokenize = f;
        break;
      } else if (stream.match("{", false) && isInXmlAttributeBlock(state)) {
        // if we're in a string and in an XML block, allow an embedded code block in an attribute
        pushStateStack(state, {
          type: "codeblock"
        });
        state.tokenize = tokenBase;
        return "string";
      }
    }
    return "string";
  };
}
function startString(stream, state, quote, f) {
  let tokenize = tokenString(quote, f);
  pushStateStack(state, {
    type: "string",
    name: quote,
    tokenize
  });
  return chain(stream, state, tokenize);
}

// tokenizer for variables
function tokenVariable(stream, state) {
  var isVariableChar = /[\w\$_-]/;

  // a variable may start with a quoted EQName so if the next character is quote, consume to the next quote
  if (stream.eat("\"")) {
    while (stream.next() !== '\"') {}
    ;
    stream.eat(":");
  } else {
    stream.eatWhile(isVariableChar);
    if (!stream.match(":=", false)) stream.eat(":");
  }
  stream.eatWhile(isVariableChar);
  state.tokenize = tokenBase;
  return "variable";
}

// tokenizer for XML tags
function tokenTag(name, isclose) {
  return function (stream, state) {
    stream.eatSpace();
    if (isclose && stream.eat(">")) {
      popStateStack(state);
      state.tokenize = tokenBase;
      return "tag";
    }
    // self closing tag without attributes?
    if (!stream.eat("/")) pushStateStack(state, {
      type: "tag",
      name: name,
      tokenize: tokenBase
    });
    if (!stream.eat(">")) {
      state.tokenize = tokenAttribute;
      return "tag";
    } else {
      state.tokenize = tokenBase;
    }
    return "tag";
  };
}

// tokenizer for XML attributes
function tokenAttribute(stream, state) {
  var ch = stream.next();
  if (ch == "/" && stream.eat(">")) {
    if (isInXmlAttributeBlock(state)) popStateStack(state);
    if (isInXmlBlock(state)) popStateStack(state);
    return "tag";
  }
  if (ch == ">") {
    if (isInXmlAttributeBlock(state)) popStateStack(state);
    return "tag";
  }
  if (ch == "=") return null;
  // quoted string
  if (ch == '"' || ch == "'") return startString(stream, state, ch, tokenAttribute);
  if (!isInXmlAttributeBlock(state)) pushStateStack(state, {
    type: "attribute",
    tokenize: tokenAttribute
  });
  stream.eat(/[a-zA-Z_:]/);
  stream.eatWhile(/[-a-zA-Z0-9_:.]/);
  stream.eatSpace();

  // the case where the attribute has not value and the tag was closed
  if (stream.match(">", false) || stream.match("/", false)) {
    popStateStack(state);
    state.tokenize = tokenBase;
  }
  return "attribute";
}

// handle comments, including nested
function tokenXMLComment(stream, state) {
  var ch;
  while (ch = stream.next()) {
    if (ch == "-" && stream.match("->", true)) {
      state.tokenize = tokenBase;
      return "comment";
    }
  }
}

// handle CDATA
function tokenCDATA(stream, state) {
  var ch;
  while (ch = stream.next()) {
    if (ch == "]" && stream.match("]", true)) {
      state.tokenize = tokenBase;
      return "comment";
    }
  }
}

// handle preprocessing instructions
function tokenPreProcessing(stream, state) {
  var ch;
  while (ch = stream.next()) {
    if (ch == "?" && stream.match(">", true)) {
      state.tokenize = tokenBase;
      return "processingInstruction";
    }
  }
}

// functions to test the current context of the state
function isInXmlBlock(state) {
  return isIn(state, "tag");
}
function isInXmlAttributeBlock(state) {
  return isIn(state, "attribute");
}
function isInXmlConstructor(state) {
  return isIn(state, "xmlconstructor");
}
function isInString(state) {
  return isIn(state, "string");
}
function isEQNameAhead(stream) {
  // assume we've already eaten a quote (")
  if (stream.current() === '"') return stream.match(/^[^\"]+\"\:/, false);else if (stream.current() === '\'') return stream.match(/^[^\"]+\'\:/, false);else return false;
}
function isIn(state, type) {
  return state.stack.length && state.stack[state.stack.length - 1].type == type;
}
function pushStateStack(state, newState) {
  state.stack.push(newState);
}
function popStateStack(state) {
  state.stack.pop();
  var reinstateTokenize = state.stack.length && state.stack[state.stack.length - 1].tokenize;
  state.tokenize = reinstateTokenize || tokenBase;
}

// the interface for the mode API
const xQuery = {
  name: "xquery",
  startState: function () {
    return {
      tokenize: tokenBase,
      cc: [],
      stack: []
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
        open: "(:",
        close: ":)"
      }
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNTQ5Mi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUveHF1ZXJ5LmpzIl0sInNvdXJjZXNDb250ZW50IjpbIi8vIFRoZSBrZXl3b3JkcyBvYmplY3QgaXMgc2V0IHRvIHRoZSByZXN1bHQgb2YgdGhpcyBzZWxmIGV4ZWN1dGluZ1xuLy8gZnVuY3Rpb24uIEVhY2gga2V5d29yZCBpcyBhIHByb3BlcnR5IG9mIHRoZSBrZXl3b3JkcyBvYmplY3Qgd2hvc2Vcbi8vIHZhbHVlIGlzIHt0eXBlOiBhdHlwZSwgc3R5bGU6IGFzdHlsZX1cbnZhciBrZXl3b3JkcyA9IGZ1bmN0aW9uICgpIHtcbiAgLy8gY29udmVuaWVuY2UgZnVuY3Rpb25zIHVzZWQgdG8gYnVpbGQga2V5d29yZHMgb2JqZWN0XG4gIGZ1bmN0aW9uIGt3KHR5cGUpIHtcbiAgICByZXR1cm4ge1xuICAgICAgdHlwZTogdHlwZSxcbiAgICAgIHN0eWxlOiBcImtleXdvcmRcIlxuICAgIH07XG4gIH1cbiAgdmFyIG9wZXJhdG9yID0ga3coXCJvcGVyYXRvclwiKSxcbiAgICBhdG9tID0ge1xuICAgICAgdHlwZTogXCJhdG9tXCIsXG4gICAgICBzdHlsZTogXCJhdG9tXCJcbiAgICB9LFxuICAgIHB1bmN0dWF0aW9uID0ge1xuICAgICAgdHlwZTogXCJwdW5jdHVhdGlvblwiLFxuICAgICAgc3R5bGU6IG51bGxcbiAgICB9LFxuICAgIHF1YWxpZmllciA9IHtcbiAgICAgIHR5cGU6IFwiYXhpc19zcGVjaWZpZXJcIixcbiAgICAgIHN0eWxlOiBcInF1YWxpZmllclwiXG4gICAgfTtcblxuICAvLyBrd09iaiBpcyB3aGF0IGlzIHJldHVybiBmcm9tIHRoaXMgZnVuY3Rpb24gYXQgdGhlIGVuZFxuICB2YXIga3dPYmogPSB7XG4gICAgJywnOiBwdW5jdHVhdGlvblxuICB9O1xuXG4gIC8vIGEgbGlzdCBvZiAnYmFzaWMnIGtleXdvcmRzLiBGb3IgZWFjaCBhZGQgYSBwcm9wZXJ0eSB0byBrd09iaiB3aXRoIHRoZSB2YWx1ZSBvZlxuICAvLyB7dHlwZTogYmFzaWNbaV0sIHN0eWxlOiBcImtleXdvcmRcIn0gZS5nLiAnYWZ0ZXInIC0tPiB7dHlwZTogXCJhZnRlclwiLCBzdHlsZTogXCJrZXl3b3JkXCJ9XG4gIHZhciBiYXNpYyA9IFsnYWZ0ZXInLCAnYWxsJywgJ2FsbG93aW5nJywgJ2FuY2VzdG9yJywgJ2FuY2VzdG9yLW9yLXNlbGYnLCAnYW55JywgJ2FycmF5JywgJ2FzJywgJ2FzY2VuZGluZycsICdhdCcsICdhdHRyaWJ1dGUnLCAnYmFzZS11cmknLCAnYmVmb3JlJywgJ2JvdW5kYXJ5LXNwYWNlJywgJ2J5JywgJ2Nhc2UnLCAnY2FzdCcsICdjYXN0YWJsZScsICdjYXRjaCcsICdjaGlsZCcsICdjb2xsYXRpb24nLCAnY29tbWVudCcsICdjb25zdHJ1Y3Rpb24nLCAnY29udGFpbnMnLCAnY29udGVudCcsICdjb250ZXh0JywgJ2NvcHknLCAnY29weS1uYW1lc3BhY2VzJywgJ2NvdW50JywgJ2RlY2ltYWwtZm9ybWF0JywgJ2RlY2xhcmUnLCAnZGVmYXVsdCcsICdkZWxldGUnLCAnZGVzY2VuZGFudCcsICdkZXNjZW5kYW50LW9yLXNlbGYnLCAnZGVzY2VuZGluZycsICdkaWFjcml0aWNzJywgJ2RpZmZlcmVudCcsICdkaXN0YW5jZScsICdkb2N1bWVudCcsICdkb2N1bWVudC1ub2RlJywgJ2VsZW1lbnQnLCAnZWxzZScsICdlbXB0eScsICdlbXB0eS1zZXF1ZW5jZScsICdlbmNvZGluZycsICdlbmQnLCAnZW50aXJlJywgJ2V2ZXJ5JywgJ2V4YWN0bHknLCAnZXhjZXB0JywgJ2V4dGVybmFsJywgJ2ZpcnN0JywgJ2ZvbGxvd2luZycsICdmb2xsb3dpbmctc2libGluZycsICdmb3InLCAnZnJvbScsICdmdGFuZCcsICdmdG5vdCcsICdmdC1vcHRpb24nLCAnZnRvcicsICdmdW5jdGlvbicsICdmdXp6eScsICdncmVhdGVzdCcsICdncm91cCcsICdpZicsICdpbXBvcnQnLCAnaW4nLCAnaW5oZXJpdCcsICdpbnNlbnNpdGl2ZScsICdpbnNlcnQnLCAnaW5zdGFuY2UnLCAnaW50ZXJzZWN0JywgJ2ludG8nLCAnaW52b2tlJywgJ2lzJywgJ2l0ZW0nLCAnbGFuZ3VhZ2UnLCAnbGFzdCcsICdsYXgnLCAnbGVhc3QnLCAnbGV0JywgJ2xldmVscycsICdsb3dlcmNhc2UnLCAnbWFwJywgJ21vZGlmeScsICdtb2R1bGUnLCAnbW9zdCcsICduYW1lc3BhY2UnLCAnbmV4dCcsICdubycsICdub2RlJywgJ25vZGVzJywgJ25vLWluaGVyaXQnLCAnbm8tcHJlc2VydmUnLCAnbm90JywgJ29jY3VycycsICdvZicsICdvbmx5JywgJ29wdGlvbicsICdvcmRlcicsICdvcmRlcmVkJywgJ29yZGVyaW5nJywgJ3BhcmFncmFwaCcsICdwYXJhZ3JhcGhzJywgJ3BhcmVudCcsICdwaHJhc2UnLCAncHJlY2VkaW5nJywgJ3ByZWNlZGluZy1zaWJsaW5nJywgJ3ByZXNlcnZlJywgJ3ByZXZpb3VzJywgJ3Byb2Nlc3NpbmctaW5zdHJ1Y3Rpb24nLCAncmVsYXRpb25zaGlwJywgJ3JlbmFtZScsICdyZXBsYWNlJywgJ3JldHVybicsICdyZXZhbGlkYXRpb24nLCAnc2FtZScsICdzYXRpc2ZpZXMnLCAnc2NoZW1hJywgJ3NjaGVtYS1hdHRyaWJ1dGUnLCAnc2NoZW1hLWVsZW1lbnQnLCAnc2NvcmUnLCAnc2VsZicsICdzZW5zaXRpdmUnLCAnc2VudGVuY2UnLCAnc2VudGVuY2VzJywgJ3NlcXVlbmNlJywgJ3NraXAnLCAnc2xpZGluZycsICdzb21lJywgJ3N0YWJsZScsICdzdGFydCcsICdzdGVtbWluZycsICdzdG9wJywgJ3N0cmljdCcsICdzdHJpcCcsICdzd2l0Y2gnLCAndGV4dCcsICd0aGVuJywgJ3RoZXNhdXJ1cycsICd0aW1lcycsICd0bycsICd0cmFuc2Zvcm0nLCAndHJlYXQnLCAndHJ5JywgJ3R1bWJsaW5nJywgJ3R5cGUnLCAndHlwZXN3aXRjaCcsICd1bmlvbicsICd1bm9yZGVyZWQnLCAndXBkYXRlJywgJ3VwZGF0aW5nJywgJ3VwcGVyY2FzZScsICd1c2luZycsICd2YWxpZGF0ZScsICd2YWx1ZScsICd2YXJpYWJsZScsICd2ZXJzaW9uJywgJ3dlaWdodCcsICd3aGVuJywgJ3doZXJlJywgJ3dpbGRjYXJkcycsICd3aW5kb3cnLCAnd2l0aCcsICd3aXRob3V0JywgJ3dvcmQnLCAnd29yZHMnLCAneHF1ZXJ5J107XG4gIGZvciAodmFyIGkgPSAwLCBsID0gYmFzaWMubGVuZ3RoOyBpIDwgbDsgaSsrKSB7XG4gICAga3dPYmpbYmFzaWNbaV1dID0ga3coYmFzaWNbaV0pO1xuICB9XG4gIDtcblxuICAvLyBhIGxpc3Qgb2YgdHlwZXMuIEZvciBlYWNoIGFkZCBhIHByb3BlcnR5IHRvIGt3T2JqIHdpdGggdGhlIHZhbHVlIG9mXG4gIC8vIHt0eXBlOiBcImF0b21cIiwgc3R5bGU6IFwiYXRvbVwifVxuICB2YXIgdHlwZXMgPSBbJ3hzOmFueUF0b21pY1R5cGUnLCAneHM6YW55U2ltcGxlVHlwZScsICd4czphbnlUeXBlJywgJ3hzOmFueVVSSScsICd4czpiYXNlNjRCaW5hcnknLCAneHM6Ym9vbGVhbicsICd4czpieXRlJywgJ3hzOmRhdGUnLCAneHM6ZGF0ZVRpbWUnLCAneHM6ZGF0ZVRpbWVTdGFtcCcsICd4czpkYXlUaW1lRHVyYXRpb24nLCAneHM6ZGVjaW1hbCcsICd4czpkb3VibGUnLCAneHM6ZHVyYXRpb24nLCAneHM6RU5USVRJRVMnLCAneHM6RU5USVRZJywgJ3hzOmZsb2F0JywgJ3hzOmdEYXknLCAneHM6Z01vbnRoJywgJ3hzOmdNb250aERheScsICd4czpnWWVhcicsICd4czpnWWVhck1vbnRoJywgJ3hzOmhleEJpbmFyeScsICd4czpJRCcsICd4czpJRFJFRicsICd4czpJRFJFRlMnLCAneHM6aW50JywgJ3hzOmludGVnZXInLCAneHM6aXRlbScsICd4czpqYXZhJywgJ3hzOmxhbmd1YWdlJywgJ3hzOmxvbmcnLCAneHM6TmFtZScsICd4czpOQ05hbWUnLCAneHM6bmVnYXRpdmVJbnRlZ2VyJywgJ3hzOk5NVE9LRU4nLCAneHM6Tk1UT0tFTlMnLCAneHM6bm9uTmVnYXRpdmVJbnRlZ2VyJywgJ3hzOm5vblBvc2l0aXZlSW50ZWdlcicsICd4czpub3JtYWxpemVkU3RyaW5nJywgJ3hzOk5PVEFUSU9OJywgJ3hzOm51bWVyaWMnLCAneHM6cG9zaXRpdmVJbnRlZ2VyJywgJ3hzOnByZWNpc2lvbkRlY2ltYWwnLCAneHM6UU5hbWUnLCAneHM6c2hvcnQnLCAneHM6c3RyaW5nJywgJ3hzOnRpbWUnLCAneHM6dG9rZW4nLCAneHM6dW5zaWduZWRCeXRlJywgJ3hzOnVuc2lnbmVkSW50JywgJ3hzOnVuc2lnbmVkTG9uZycsICd4czp1bnNpZ25lZFNob3J0JywgJ3hzOnVudHlwZWQnLCAneHM6dW50eXBlZEF0b21pYycsICd4czp5ZWFyTW9udGhEdXJhdGlvbiddO1xuICBmb3IgKHZhciBpID0gMCwgbCA9IHR5cGVzLmxlbmd0aDsgaSA8IGw7IGkrKykge1xuICAgIGt3T2JqW3R5cGVzW2ldXSA9IGF0b207XG4gIH1cbiAgO1xuXG4gIC8vIGVhY2ggb3BlcmF0b3Igd2lsbCBhZGQgYSBwcm9wZXJ0eSB0byBrd09iaiB3aXRoIHZhbHVlIG9mIHt0eXBlOiBcIm9wZXJhdG9yXCIsIHN0eWxlOiBcImtleXdvcmRcIn1cbiAgdmFyIG9wZXJhdG9ycyA9IFsnZXEnLCAnbmUnLCAnbHQnLCAnbGUnLCAnZ3QnLCAnZ2UnLCAnOj0nLCAnPScsICc+JywgJz49JywgJzwnLCAnPD0nLCAnLicsICd8JywgJz8nLCAnYW5kJywgJ29yJywgJ2RpdicsICdpZGl2JywgJ21vZCcsICcqJywgJy8nLCAnKycsICctJ107XG4gIGZvciAodmFyIGkgPSAwLCBsID0gb3BlcmF0b3JzLmxlbmd0aDsgaSA8IGw7IGkrKykge1xuICAgIGt3T2JqW29wZXJhdG9yc1tpXV0gPSBvcGVyYXRvcjtcbiAgfVxuICA7XG5cbiAgLy8gZWFjaCBheGlzX3NwZWNpZmllcnMgd2lsbCBhZGQgYSBwcm9wZXJ0eSB0byBrd09iaiB3aXRoIHZhbHVlIG9mIHt0eXBlOiBcImF4aXNfc3BlY2lmaWVyXCIsIHN0eWxlOiBcInF1YWxpZmllclwifVxuICB2YXIgYXhpc19zcGVjaWZpZXJzID0gW1wic2VsZjo6XCIsIFwiYXR0cmlidXRlOjpcIiwgXCJjaGlsZDo6XCIsIFwiZGVzY2VuZGFudDo6XCIsIFwiZGVzY2VuZGFudC1vci1zZWxmOjpcIiwgXCJwYXJlbnQ6OlwiLCBcImFuY2VzdG9yOjpcIiwgXCJhbmNlc3Rvci1vci1zZWxmOjpcIiwgXCJmb2xsb3dpbmc6OlwiLCBcInByZWNlZGluZzo6XCIsIFwiZm9sbG93aW5nLXNpYmxpbmc6OlwiLCBcInByZWNlZGluZy1zaWJsaW5nOjpcIl07XG4gIGZvciAodmFyIGkgPSAwLCBsID0gYXhpc19zcGVjaWZpZXJzLmxlbmd0aDsgaSA8IGw7IGkrKykge1xuICAgIGt3T2JqW2F4aXNfc3BlY2lmaWVyc1tpXV0gPSBxdWFsaWZpZXI7XG4gIH1cbiAgO1xuICByZXR1cm4ga3dPYmo7XG59KCk7XG5mdW5jdGlvbiBjaGFpbihzdHJlYW0sIHN0YXRlLCBmKSB7XG4gIHN0YXRlLnRva2VuaXplID0gZjtcbiAgcmV0dXJuIGYoc3RyZWFtLCBzdGF0ZSk7XG59XG5cbi8vIHRoZSBwcmltYXJ5IG1vZGUgdG9rZW5pemVyXG5mdW5jdGlvbiB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgY2ggPSBzdHJlYW0ubmV4dCgpLFxuICAgIG1pZ2h0QmVGdW5jdGlvbiA9IGZhbHNlLFxuICAgIGlzRVFOYW1lID0gaXNFUU5hbWVBaGVhZChzdHJlYW0pO1xuXG4gIC8vIGFuIFhNTCB0YWcgKGlmIG5vdCBpbiBzb21lIHN1YiwgY2hhaW5lZCB0b2tlbml6ZXIpXG4gIGlmIChjaCA9PSBcIjxcIikge1xuICAgIGlmIChzdHJlYW0ubWF0Y2goXCIhLS1cIiwgdHJ1ZSkpIHJldHVybiBjaGFpbihzdHJlYW0sIHN0YXRlLCB0b2tlblhNTENvbW1lbnQpO1xuICAgIGlmIChzdHJlYW0ubWF0Y2goXCIhW0NEQVRBXCIsIGZhbHNlKSkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkNEQVRBO1xuICAgICAgcmV0dXJuIFwidGFnXCI7XG4gICAgfVxuICAgIGlmIChzdHJlYW0ubWF0Y2goXCI/XCIsIGZhbHNlKSkge1xuICAgICAgcmV0dXJuIGNoYWluKHN0cmVhbSwgc3RhdGUsIHRva2VuUHJlUHJvY2Vzc2luZyk7XG4gICAgfVxuICAgIHZhciBpc2Nsb3NlID0gc3RyZWFtLmVhdChcIi9cIik7XG4gICAgc3RyZWFtLmVhdFNwYWNlKCk7XG4gICAgdmFyIHRhZ05hbWUgPSBcIlwiLFxuICAgICAgYztcbiAgICB3aGlsZSAoYyA9IHN0cmVhbS5lYXQoL1teXFxzXFx1MDBhMD08PlxcXCJcXCdcXC8/XS8pKSB0YWdOYW1lICs9IGM7XG4gICAgcmV0dXJuIGNoYWluKHN0cmVhbSwgc3RhdGUsIHRva2VuVGFnKHRhZ05hbWUsIGlzY2xvc2UpKTtcbiAgfVxuICAvLyBzdGFydCBjb2RlIGJsb2NrXG4gIGVsc2UgaWYgKGNoID09IFwie1wiKSB7XG4gICAgcHVzaFN0YXRlU3RhY2soc3RhdGUsIHtcbiAgICAgIHR5cGU6IFwiY29kZWJsb2NrXCJcbiAgICB9KTtcbiAgICByZXR1cm4gbnVsbDtcbiAgfVxuICAvLyBlbmQgY29kZSBibG9ja1xuICBlbHNlIGlmIChjaCA9PSBcIn1cIikge1xuICAgIHBvcFN0YXRlU3RhY2soc3RhdGUpO1xuICAgIHJldHVybiBudWxsO1xuICB9XG4gIC8vIGlmIHdlJ3JlIGluIGFuIFhNTCBibG9ja1xuICBlbHNlIGlmIChpc0luWG1sQmxvY2soc3RhdGUpKSB7XG4gICAgaWYgKGNoID09IFwiPlwiKSByZXR1cm4gXCJ0YWdcIjtlbHNlIGlmIChjaCA9PSBcIi9cIiAmJiBzdHJlYW0uZWF0KFwiPlwiKSkge1xuICAgICAgcG9wU3RhdGVTdGFjayhzdGF0ZSk7XG4gICAgICByZXR1cm4gXCJ0YWdcIjtcbiAgICB9IGVsc2UgcmV0dXJuIFwidmFyaWFibGVcIjtcbiAgfVxuICAvLyBpZiBhIG51bWJlclxuICBlbHNlIGlmICgvXFxkLy50ZXN0KGNoKSkge1xuICAgIHN0cmVhbS5tYXRjaCgvXlxcZCooPzpcXC5cXGQqKT8oPzpFWytcXC1dP1xcZCspPy8pO1xuICAgIHJldHVybiBcImF0b21cIjtcbiAgfVxuICAvLyBjb21tZW50IHN0YXJ0XG4gIGVsc2UgaWYgKGNoID09PSBcIihcIiAmJiBzdHJlYW0uZWF0KFwiOlwiKSkge1xuICAgIHB1c2hTdGF0ZVN0YWNrKHN0YXRlLCB7XG4gICAgICB0eXBlOiBcImNvbW1lbnRcIlxuICAgIH0pO1xuICAgIHJldHVybiBjaGFpbihzdHJlYW0sIHN0YXRlLCB0b2tlbkNvbW1lbnQpO1xuICB9XG4gIC8vIHF1b3RlZCBzdHJpbmdcbiAgZWxzZSBpZiAoIWlzRVFOYW1lICYmIChjaCA9PT0gJ1wiJyB8fCBjaCA9PT0gXCInXCIpKSByZXR1cm4gc3RhcnRTdHJpbmcoc3RyZWFtLCBzdGF0ZSwgY2gpO1xuICAvLyB2YXJpYWJsZVxuICBlbHNlIGlmIChjaCA9PT0gXCIkXCIpIHtcbiAgICByZXR1cm4gY2hhaW4oc3RyZWFtLCBzdGF0ZSwgdG9rZW5WYXJpYWJsZSk7XG4gIH1cbiAgLy8gYXNzaWdubWVudFxuICBlbHNlIGlmIChjaCA9PT0gXCI6XCIgJiYgc3RyZWFtLmVhdChcIj1cIikpIHtcbiAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gIH1cbiAgLy8gb3BlbiBwYXJlblxuICBlbHNlIGlmIChjaCA9PT0gXCIoXCIpIHtcbiAgICBwdXNoU3RhdGVTdGFjayhzdGF0ZSwge1xuICAgICAgdHlwZTogXCJwYXJlblwiXG4gICAgfSk7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbiAgLy8gY2xvc2UgcGFyZW5cbiAgZWxzZSBpZiAoY2ggPT09IFwiKVwiKSB7XG4gICAgcG9wU3RhdGVTdGFjayhzdGF0ZSk7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbiAgLy8gb3BlbiBwYXJlblxuICBlbHNlIGlmIChjaCA9PT0gXCJbXCIpIHtcbiAgICBwdXNoU3RhdGVTdGFjayhzdGF0ZSwge1xuICAgICAgdHlwZTogXCJicmFja2V0XCJcbiAgICB9KTtcbiAgICByZXR1cm4gbnVsbDtcbiAgfVxuICAvLyBjbG9zZSBwYXJlblxuICBlbHNlIGlmIChjaCA9PT0gXCJdXCIpIHtcbiAgICBwb3BTdGF0ZVN0YWNrKHN0YXRlKTtcbiAgICByZXR1cm4gbnVsbDtcbiAgfSBlbHNlIHtcbiAgICB2YXIga25vd24gPSBrZXl3b3Jkcy5wcm9wZXJ0eUlzRW51bWVyYWJsZShjaCkgJiYga2V5d29yZHNbY2hdO1xuXG4gICAgLy8gaWYgdGhlcmUncyBhIEVRTmFtZSBhaGVhZCwgY29uc3VtZSB0aGUgcmVzdCBvZiB0aGUgc3RyaW5nIHBvcnRpb24sIGl0J3MgbGlrZWx5IGEgZnVuY3Rpb25cbiAgICBpZiAoaXNFUU5hbWUgJiYgY2ggPT09ICdcXFwiJykgd2hpbGUgKHN0cmVhbS5uZXh0KCkgIT09ICdcIicpIHt9XG4gICAgaWYgKGlzRVFOYW1lICYmIGNoID09PSAnXFwnJykgd2hpbGUgKHN0cmVhbS5uZXh0KCkgIT09ICdcXCcnKSB7fVxuXG4gICAgLy8gZ29iYmxlIHVwIGEgd29yZCBpZiB0aGUgY2hhcmFjdGVyIGlzIG5vdCBrbm93blxuICAgIGlmICgha25vd24pIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcJF8tXS8pO1xuXG4gICAgLy8gZ29iYmxlIGEgY29sb24gaW4gdGhlIGNhc2UgdGhhdCBpcyBhIGxpYiBmdW5jIHR5cGUgY2FsbCBmbjpkb2NcbiAgICB2YXIgZm91bmRDb2xvbiA9IHN0cmVhbS5lYXQoXCI6XCIpO1xuXG4gICAgLy8gaWYgdGhlcmUncyBub3QgYSBzZWNvbmQgY29sb24sIGdvYmJsZSBhbm90aGVyIHdvcmQuIE90aGVyd2lzZSwgaXQncyBwcm9iYWJseSBhbiBheGlzIHNwZWNpZmllclxuICAgIC8vIHdoaWNoIHNob3VsZCBnZXQgbWF0Y2hlZCBhcyBhIGtleXdvcmRcbiAgICBpZiAoIXN0cmVhbS5lYXQoXCI6XCIpICYmIGZvdW5kQ29sb24pIHtcbiAgICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcJF8tXS8pO1xuICAgIH1cbiAgICAvLyBpZiB0aGUgbmV4dCBub24gd2hpdGVzcGFjZSBjaGFyYWN0ZXIgaXMgYW4gb3BlbiBwYXJlbiwgdGhpcyBpcyBwcm9iYWJseSBhIGZ1bmN0aW9uIChpZiBub3QgYSBrZXl3b3JkIG9mIG90aGVyIHNvcnQpXG4gICAgaWYgKHN0cmVhbS5tYXRjaCgvXlsgXFx0XSpcXCgvLCBmYWxzZSkpIHtcbiAgICAgIG1pZ2h0QmVGdW5jdGlvbiA9IHRydWU7XG4gICAgfVxuICAgIC8vIGlzIHRoZSB3b3JkIGEga2V5d29yZD9cbiAgICB2YXIgd29yZCA9IHN0cmVhbS5jdXJyZW50KCk7XG4gICAga25vd24gPSBrZXl3b3Jkcy5wcm9wZXJ0eUlzRW51bWVyYWJsZSh3b3JkKSAmJiBrZXl3b3Jkc1t3b3JkXTtcblxuICAgIC8vIGlmIHdlIHRoaW5rIGl0J3MgYSBmdW5jdGlvbiBjYWxsIGJ1dCBub3QgeWV0IGtub3duLFxuICAgIC8vIHNldCBzdHlsZSB0byB2YXJpYWJsZSBmb3Igbm93IGZvciBsYWNrIG9mIHNvbWV0aGluZyBiZXR0ZXJcbiAgICBpZiAobWlnaHRCZUZ1bmN0aW9uICYmICFrbm93bikga25vd24gPSB7XG4gICAgICB0eXBlOiBcImZ1bmN0aW9uX2NhbGxcIixcbiAgICAgIHN0eWxlOiBcImRlZlwiXG4gICAgfTtcblxuICAgIC8vIGlmIHRoZSBwcmV2aW91cyB3b3JkIHdhcyBlbGVtZW50LCBhdHRyaWJ1dGUsIGF4aXMgc3BlY2lmaWVyLCB0aGlzIHdvcmQgc2hvdWxkIGJlIHRoZSBuYW1lIG9mIHRoYXRcbiAgICBpZiAoaXNJblhtbENvbnN0cnVjdG9yKHN0YXRlKSkge1xuICAgICAgcG9wU3RhdGVTdGFjayhzdGF0ZSk7XG4gICAgICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xuICAgIH1cbiAgICAvLyBhcyBwcmV2aW91c2x5IGNoZWNrZWQsIGlmIHRoZSB3b3JkIGlzIGVsZW1lbnQsYXR0cmlidXRlLCBheGlzIHNwZWNpZmllciwgY2FsbCBpdCBhbiBcInhtbGNvbnN0cnVjdG9yXCIgYW5kXG4gICAgLy8gcHVzaCB0aGUgc3RhY2sgc28gd2Uga25vdyB0byBsb29rIGZvciBpdCBvbiB0aGUgbmV4dCB3b3JkXG4gICAgaWYgKHdvcmQgPT0gXCJlbGVtZW50XCIgfHwgd29yZCA9PSBcImF0dHJpYnV0ZVwiIHx8IGtub3duLnR5cGUgPT0gXCJheGlzX3NwZWNpZmllclwiKSBwdXNoU3RhdGVTdGFjayhzdGF0ZSwge1xuICAgICAgdHlwZTogXCJ4bWxjb25zdHJ1Y3RvclwiXG4gICAgfSk7XG5cbiAgICAvLyBpZiB0aGUgd29yZCBpcyBrbm93biwgcmV0dXJuIHRoZSBkZXRhaWxzIG9mIHRoYXQgZWxzZSBqdXN0IGNhbGwgdGhpcyBhIGdlbmVyaWMgJ3dvcmQnXG4gICAgcmV0dXJuIGtub3duID8ga25vd24uc3R5bGUgOiBcInZhcmlhYmxlXCI7XG4gIH1cbn1cblxuLy8gaGFuZGxlIGNvbW1lbnRzLCBpbmNsdWRpbmcgbmVzdGVkXG5mdW5jdGlvbiB0b2tlbkNvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgbWF5YmVFbmQgPSBmYWxzZSxcbiAgICBtYXliZU5lc3RlZCA9IGZhbHNlLFxuICAgIG5lc3RlZENvdW50ID0gMCxcbiAgICBjaDtcbiAgd2hpbGUgKGNoID0gc3RyZWFtLm5leHQoKSkge1xuICAgIGlmIChjaCA9PSBcIilcIiAmJiBtYXliZUVuZCkge1xuICAgICAgaWYgKG5lc3RlZENvdW50ID4gMCkgbmVzdGVkQ291bnQtLTtlbHNlIHtcbiAgICAgICAgcG9wU3RhdGVTdGFjayhzdGF0ZSk7XG4gICAgICAgIGJyZWFrO1xuICAgICAgfVxuICAgIH0gZWxzZSBpZiAoY2ggPT0gXCI6XCIgJiYgbWF5YmVOZXN0ZWQpIHtcbiAgICAgIG5lc3RlZENvdW50Kys7XG4gICAgfVxuICAgIG1heWJlRW5kID0gY2ggPT0gXCI6XCI7XG4gICAgbWF5YmVOZXN0ZWQgPSBjaCA9PSBcIihcIjtcbiAgfVxuICByZXR1cm4gXCJjb21tZW50XCI7XG59XG5cbi8vIHRva2VuaXplciBmb3Igc3RyaW5nIGxpdGVyYWxzXG4vLyBvcHRpb25hbGx5IHBhc3MgYSB0b2tlbml6ZXIgZnVuY3Rpb24gdG8gc2V0IHN0YXRlLnRva2VuaXplIGJhY2sgdG8gd2hlbiBmaW5pc2hlZFxuZnVuY3Rpb24gdG9rZW5TdHJpbmcocXVvdGUsIGYpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGNoO1xuICAgIHdoaWxlIChjaCA9IHN0cmVhbS5uZXh0KCkpIHtcbiAgICAgIGlmIChjaCA9PSBxdW90ZSkge1xuICAgICAgICBwb3BTdGF0ZVN0YWNrKHN0YXRlKTtcbiAgICAgICAgaWYgKGYpIHN0YXRlLnRva2VuaXplID0gZjtcbiAgICAgICAgYnJlYWs7XG4gICAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaChcIntcIiwgZmFsc2UpICYmIGlzSW5YbWxBdHRyaWJ1dGVCbG9jayhzdGF0ZSkpIHtcbiAgICAgICAgLy8gaWYgd2UncmUgaW4gYSBzdHJpbmcgYW5kIGluIGFuIFhNTCBibG9jaywgYWxsb3cgYW4gZW1iZWRkZWQgY29kZSBibG9jayBpbiBhbiBhdHRyaWJ1dGVcbiAgICAgICAgcHVzaFN0YXRlU3RhY2soc3RhdGUsIHtcbiAgICAgICAgICB0eXBlOiBcImNvZGVibG9ja1wiXG4gICAgICAgIH0pO1xuICAgICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gICAgICB9XG4gICAgfVxuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9O1xufVxuZnVuY3Rpb24gc3RhcnRTdHJpbmcoc3RyZWFtLCBzdGF0ZSwgcXVvdGUsIGYpIHtcbiAgbGV0IHRva2VuaXplID0gdG9rZW5TdHJpbmcocXVvdGUsIGYpO1xuICBwdXNoU3RhdGVTdGFjayhzdGF0ZSwge1xuICAgIHR5cGU6IFwic3RyaW5nXCIsXG4gICAgbmFtZTogcXVvdGUsXG4gICAgdG9rZW5pemVcbiAgfSk7XG4gIHJldHVybiBjaGFpbihzdHJlYW0sIHN0YXRlLCB0b2tlbml6ZSk7XG59XG5cbi8vIHRva2VuaXplciBmb3IgdmFyaWFibGVzXG5mdW5jdGlvbiB0b2tlblZhcmlhYmxlKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIGlzVmFyaWFibGVDaGFyID0gL1tcXHdcXCRfLV0vO1xuXG4gIC8vIGEgdmFyaWFibGUgbWF5IHN0YXJ0IHdpdGggYSBxdW90ZWQgRVFOYW1lIHNvIGlmIHRoZSBuZXh0IGNoYXJhY3RlciBpcyBxdW90ZSwgY29uc3VtZSB0byB0aGUgbmV4dCBxdW90ZVxuICBpZiAoc3RyZWFtLmVhdChcIlxcXCJcIikpIHtcbiAgICB3aGlsZSAoc3RyZWFtLm5leHQoKSAhPT0gJ1xcXCInKSB7fVxuICAgIDtcbiAgICBzdHJlYW0uZWF0KFwiOlwiKTtcbiAgfSBlbHNlIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoaXNWYXJpYWJsZUNoYXIpO1xuICAgIGlmICghc3RyZWFtLm1hdGNoKFwiOj1cIiwgZmFsc2UpKSBzdHJlYW0uZWF0KFwiOlwiKTtcbiAgfVxuICBzdHJlYW0uZWF0V2hpbGUoaXNWYXJpYWJsZUNoYXIpO1xuICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgcmV0dXJuIFwidmFyaWFibGVcIjtcbn1cblxuLy8gdG9rZW5pemVyIGZvciBYTUwgdGFnc1xuZnVuY3Rpb24gdG9rZW5UYWcobmFtZSwgaXNjbG9zZSkge1xuICByZXR1cm4gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBzdHJlYW0uZWF0U3BhY2UoKTtcbiAgICBpZiAoaXNjbG9zZSAmJiBzdHJlYW0uZWF0KFwiPlwiKSkge1xuICAgICAgcG9wU3RhdGVTdGFjayhzdGF0ZSk7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICAgIHJldHVybiBcInRhZ1wiO1xuICAgIH1cbiAgICAvLyBzZWxmIGNsb3NpbmcgdGFnIHdpdGhvdXQgYXR0cmlidXRlcz9cbiAgICBpZiAoIXN0cmVhbS5lYXQoXCIvXCIpKSBwdXNoU3RhdGVTdGFjayhzdGF0ZSwge1xuICAgICAgdHlwZTogXCJ0YWdcIixcbiAgICAgIG5hbWU6IG5hbWUsXG4gICAgICB0b2tlbml6ZTogdG9rZW5CYXNlXG4gICAgfSk7XG4gICAgaWYgKCFzdHJlYW0uZWF0KFwiPlwiKSkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkF0dHJpYnV0ZTtcbiAgICAgIHJldHVybiBcInRhZ1wiO1xuICAgIH0gZWxzZSB7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICB9XG4gICAgcmV0dXJuIFwidGFnXCI7XG4gIH07XG59XG5cbi8vIHRva2VuaXplciBmb3IgWE1MIGF0dHJpYnV0ZXNcbmZ1bmN0aW9uIHRva2VuQXR0cmlidXRlKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIGNoID0gc3RyZWFtLm5leHQoKTtcbiAgaWYgKGNoID09IFwiL1wiICYmIHN0cmVhbS5lYXQoXCI+XCIpKSB7XG4gICAgaWYgKGlzSW5YbWxBdHRyaWJ1dGVCbG9jayhzdGF0ZSkpIHBvcFN0YXRlU3RhY2soc3RhdGUpO1xuICAgIGlmIChpc0luWG1sQmxvY2soc3RhdGUpKSBwb3BTdGF0ZVN0YWNrKHN0YXRlKTtcbiAgICByZXR1cm4gXCJ0YWdcIjtcbiAgfVxuICBpZiAoY2ggPT0gXCI+XCIpIHtcbiAgICBpZiAoaXNJblhtbEF0dHJpYnV0ZUJsb2NrKHN0YXRlKSkgcG9wU3RhdGVTdGFjayhzdGF0ZSk7XG4gICAgcmV0dXJuIFwidGFnXCI7XG4gIH1cbiAgaWYgKGNoID09IFwiPVwiKSByZXR1cm4gbnVsbDtcbiAgLy8gcXVvdGVkIHN0cmluZ1xuICBpZiAoY2ggPT0gJ1wiJyB8fCBjaCA9PSBcIidcIikgcmV0dXJuIHN0YXJ0U3RyaW5nKHN0cmVhbSwgc3RhdGUsIGNoLCB0b2tlbkF0dHJpYnV0ZSk7XG4gIGlmICghaXNJblhtbEF0dHJpYnV0ZUJsb2NrKHN0YXRlKSkgcHVzaFN0YXRlU3RhY2soc3RhdGUsIHtcbiAgICB0eXBlOiBcImF0dHJpYnV0ZVwiLFxuICAgIHRva2VuaXplOiB0b2tlbkF0dHJpYnV0ZVxuICB9KTtcbiAgc3RyZWFtLmVhdCgvW2EtekEtWl86XS8pO1xuICBzdHJlYW0uZWF0V2hpbGUoL1stYS16QS1aMC05XzouXS8pO1xuICBzdHJlYW0uZWF0U3BhY2UoKTtcblxuICAvLyB0aGUgY2FzZSB3aGVyZSB0aGUgYXR0cmlidXRlIGhhcyBub3QgdmFsdWUgYW5kIHRoZSB0YWcgd2FzIGNsb3NlZFxuICBpZiAoc3RyZWFtLm1hdGNoKFwiPlwiLCBmYWxzZSkgfHwgc3RyZWFtLm1hdGNoKFwiL1wiLCBmYWxzZSkpIHtcbiAgICBwb3BTdGF0ZVN0YWNrKHN0YXRlKTtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgfVxuICByZXR1cm4gXCJhdHRyaWJ1dGVcIjtcbn1cblxuLy8gaGFuZGxlIGNvbW1lbnRzLCBpbmNsdWRpbmcgbmVzdGVkXG5mdW5jdGlvbiB0b2tlblhNTENvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgY2g7XG4gIHdoaWxlIChjaCA9IHN0cmVhbS5uZXh0KCkpIHtcbiAgICBpZiAoY2ggPT0gXCItXCIgJiYgc3RyZWFtLm1hdGNoKFwiLT5cIiwgdHJ1ZSkpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICAgIH1cbiAgfVxufVxuXG4vLyBoYW5kbGUgQ0RBVEFcbmZ1bmN0aW9uIHRva2VuQ0RBVEEoc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgY2g7XG4gIHdoaWxlIChjaCA9IHN0cmVhbS5uZXh0KCkpIHtcbiAgICBpZiAoY2ggPT0gXCJdXCIgJiYgc3RyZWFtLm1hdGNoKFwiXVwiLCB0cnVlKSkge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgfVxuICB9XG59XG5cbi8vIGhhbmRsZSBwcmVwcm9jZXNzaW5nIGluc3RydWN0aW9uc1xuZnVuY3Rpb24gdG9rZW5QcmVQcm9jZXNzaW5nKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIGNoO1xuICB3aGlsZSAoY2ggPSBzdHJlYW0ubmV4dCgpKSB7XG4gICAgaWYgKGNoID09IFwiP1wiICYmIHN0cmVhbS5tYXRjaChcIj5cIiwgdHJ1ZSkpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgICAgcmV0dXJuIFwicHJvY2Vzc2luZ0luc3RydWN0aW9uXCI7XG4gICAgfVxuICB9XG59XG5cbi8vIGZ1bmN0aW9ucyB0byB0ZXN0IHRoZSBjdXJyZW50IGNvbnRleHQgb2YgdGhlIHN0YXRlXG5mdW5jdGlvbiBpc0luWG1sQmxvY2soc3RhdGUpIHtcbiAgcmV0dXJuIGlzSW4oc3RhdGUsIFwidGFnXCIpO1xufVxuZnVuY3Rpb24gaXNJblhtbEF0dHJpYnV0ZUJsb2NrKHN0YXRlKSB7XG4gIHJldHVybiBpc0luKHN0YXRlLCBcImF0dHJpYnV0ZVwiKTtcbn1cbmZ1bmN0aW9uIGlzSW5YbWxDb25zdHJ1Y3RvcihzdGF0ZSkge1xuICByZXR1cm4gaXNJbihzdGF0ZSwgXCJ4bWxjb25zdHJ1Y3RvclwiKTtcbn1cbmZ1bmN0aW9uIGlzSW5TdHJpbmcoc3RhdGUpIHtcbiAgcmV0dXJuIGlzSW4oc3RhdGUsIFwic3RyaW5nXCIpO1xufVxuZnVuY3Rpb24gaXNFUU5hbWVBaGVhZChzdHJlYW0pIHtcbiAgLy8gYXNzdW1lIHdlJ3ZlIGFscmVhZHkgZWF0ZW4gYSBxdW90ZSAoXCIpXG4gIGlmIChzdHJlYW0uY3VycmVudCgpID09PSAnXCInKSByZXR1cm4gc3RyZWFtLm1hdGNoKC9eW15cXFwiXStcXFwiXFw6LywgZmFsc2UpO2Vsc2UgaWYgKHN0cmVhbS5jdXJyZW50KCkgPT09ICdcXCcnKSByZXR1cm4gc3RyZWFtLm1hdGNoKC9eW15cXFwiXStcXCdcXDovLCBmYWxzZSk7ZWxzZSByZXR1cm4gZmFsc2U7XG59XG5mdW5jdGlvbiBpc0luKHN0YXRlLCB0eXBlKSB7XG4gIHJldHVybiBzdGF0ZS5zdGFjay5sZW5ndGggJiYgc3RhdGUuc3RhY2tbc3RhdGUuc3RhY2subGVuZ3RoIC0gMV0udHlwZSA9PSB0eXBlO1xufVxuZnVuY3Rpb24gcHVzaFN0YXRlU3RhY2soc3RhdGUsIG5ld1N0YXRlKSB7XG4gIHN0YXRlLnN0YWNrLnB1c2gobmV3U3RhdGUpO1xufVxuZnVuY3Rpb24gcG9wU3RhdGVTdGFjayhzdGF0ZSkge1xuICBzdGF0ZS5zdGFjay5wb3AoKTtcbiAgdmFyIHJlaW5zdGF0ZVRva2VuaXplID0gc3RhdGUuc3RhY2subGVuZ3RoICYmIHN0YXRlLnN0YWNrW3N0YXRlLnN0YWNrLmxlbmd0aCAtIDFdLnRva2VuaXplO1xuICBzdGF0ZS50b2tlbml6ZSA9IHJlaW5zdGF0ZVRva2VuaXplIHx8IHRva2VuQmFzZTtcbn1cblxuLy8gdGhlIGludGVyZmFjZSBmb3IgdGhlIG1vZGUgQVBJXG5leHBvcnQgY29uc3QgeFF1ZXJ5ID0ge1xuICBuYW1lOiBcInhxdWVyeVwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiB0b2tlbkJhc2UsXG4gICAgICBjYzogW10sXG4gICAgICBzdGFjazogW11cbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHJldHVybiBudWxsO1xuICAgIHZhciBzdHlsZSA9IHN0YXRlLnRva2VuaXplKHN0cmVhbSwgc3RhdGUpO1xuICAgIHJldHVybiBzdHlsZTtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgYmxvY2s6IHtcbiAgICAgICAgb3BlbjogXCIoOlwiLFxuICAgICAgICBjbG9zZTogXCI6KVwiXG4gICAgICB9XG4gICAgfVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=