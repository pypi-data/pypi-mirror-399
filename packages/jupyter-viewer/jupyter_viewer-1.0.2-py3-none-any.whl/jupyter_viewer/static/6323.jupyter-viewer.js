"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[6323],{

/***/ 66323
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   erlang: () => (/* binding */ erlang)
/* harmony export */ });
/////////////////////////////////////////////////////////////////////////////
// constants

var typeWords = ["-type", "-spec", "-export_type", "-opaque"];
var keywordWords = ["after", "begin", "catch", "case", "cond", "end", "fun", "if", "let", "of", "query", "receive", "try", "when"];
var separatorRE = /[\->,;]/;
var separatorWords = ["->", ";", ","];
var operatorAtomWords = ["and", "andalso", "band", "bnot", "bor", "bsl", "bsr", "bxor", "div", "not", "or", "orelse", "rem", "xor"];
var operatorSymbolRE = /[\+\-\*\/<>=\|:!]/;
var operatorSymbolWords = ["=", "+", "-", "*", "/", ">", ">=", "<", "=<", "=:=", "==", "=/=", "/=", "||", "<-", "!"];
var openParenRE = /[<\(\[\{]/;
var openParenWords = ["<<", "(", "[", "{"];
var closeParenRE = /[>\)\]\}]/;
var closeParenWords = ["}", "]", ")", ">>"];
var guardWords = ["is_atom", "is_binary", "is_bitstring", "is_boolean", "is_float", "is_function", "is_integer", "is_list", "is_number", "is_pid", "is_port", "is_record", "is_reference", "is_tuple", "atom", "binary", "bitstring", "boolean", "function", "integer", "list", "number", "pid", "port", "record", "reference", "tuple"];
var bifWords = ["abs", "adler32", "adler32_combine", "alive", "apply", "atom_to_binary", "atom_to_list", "binary_to_atom", "binary_to_existing_atom", "binary_to_list", "binary_to_term", "bit_size", "bitstring_to_list", "byte_size", "check_process_code", "contact_binary", "crc32", "crc32_combine", "date", "decode_packet", "delete_module", "disconnect_node", "element", "erase", "exit", "float", "float_to_list", "garbage_collect", "get", "get_keys", "group_leader", "halt", "hd", "integer_to_list", "internal_bif", "iolist_size", "iolist_to_binary", "is_alive", "is_atom", "is_binary", "is_bitstring", "is_boolean", "is_float", "is_function", "is_integer", "is_list", "is_number", "is_pid", "is_port", "is_process_alive", "is_record", "is_reference", "is_tuple", "length", "link", "list_to_atom", "list_to_binary", "list_to_bitstring", "list_to_existing_atom", "list_to_float", "list_to_integer", "list_to_pid", "list_to_tuple", "load_module", "make_ref", "module_loaded", "monitor_node", "node", "node_link", "node_unlink", "nodes", "notalive", "now", "open_port", "pid_to_list", "port_close", "port_command", "port_connect", "port_control", "pre_loaded", "process_flag", "process_info", "processes", "purge_module", "put", "register", "registered", "round", "self", "setelement", "size", "spawn", "spawn_link", "spawn_monitor", "spawn_opt", "split_binary", "statistics", "term_to_binary", "time", "throw", "tl", "trunc", "tuple_size", "tuple_to_list", "unlink", "unregister", "whereis"];

// upper case: [A-Z] [Ø-Þ] [À-Ö]
// lower case: [a-z] [ß-ö] [ø-ÿ]
var anumRE = /[\w@Ø-ÞÀ-Öß-öø-ÿ]/;
var escapesRE = /[0-7]{1,3}|[bdefnrstv\\"']|\^[a-zA-Z]|x[0-9a-zA-Z]{2}|x{[0-9a-zA-Z]+}/;

/////////////////////////////////////////////////////////////////////////////
// tokenizer

function tokenizer(stream, state) {
  // in multi-line string
  if (state.in_string) {
    state.in_string = !doubleQuote(stream);
    return rval(state, stream, "string");
  }

  // in multi-line atom
  if (state.in_atom) {
    state.in_atom = !singleQuote(stream);
    return rval(state, stream, "atom");
  }

  // whitespace
  if (stream.eatSpace()) {
    return rval(state, stream, "whitespace");
  }

  // attributes and type specs
  if (!peekToken(state) && stream.match(/-\s*[a-zß-öø-ÿ][\wØ-ÞÀ-Öß-öø-ÿ]*/)) {
    if (is_member(stream.current(), typeWords)) {
      return rval(state, stream, "type");
    } else {
      return rval(state, stream, "attribute");
    }
  }
  var ch = stream.next();

  // comment
  if (ch == '%') {
    stream.skipToEnd();
    return rval(state, stream, "comment");
  }

  // colon
  if (ch == ":") {
    return rval(state, stream, "colon");
  }

  // macro
  if (ch == '?') {
    stream.eatSpace();
    stream.eatWhile(anumRE);
    return rval(state, stream, "macro");
  }

  // record
  if (ch == "#") {
    stream.eatSpace();
    stream.eatWhile(anumRE);
    return rval(state, stream, "record");
  }

  // dollar escape
  if (ch == "$") {
    if (stream.next() == "\\" && !stream.match(escapesRE)) {
      return rval(state, stream, "error");
    }
    return rval(state, stream, "number");
  }

  // dot
  if (ch == ".") {
    return rval(state, stream, "dot");
  }

  // quoted atom
  if (ch == '\'') {
    if (!(state.in_atom = !singleQuote(stream))) {
      if (stream.match(/\s*\/\s*[0-9]/, false)) {
        stream.match(/\s*\/\s*[0-9]/, true);
        return rval(state, stream, "fun"); // 'f'/0 style fun
      }
      if (stream.match(/\s*\(/, false) || stream.match(/\s*:/, false)) {
        return rval(state, stream, "function");
      }
    }
    return rval(state, stream, "atom");
  }

  // string
  if (ch == '"') {
    state.in_string = !doubleQuote(stream);
    return rval(state, stream, "string");
  }

  // variable
  if (/[A-Z_Ø-ÞÀ-Ö]/.test(ch)) {
    stream.eatWhile(anumRE);
    return rval(state, stream, "variable");
  }

  // atom/keyword/BIF/function
  if (/[a-z_ß-öø-ÿ]/.test(ch)) {
    stream.eatWhile(anumRE);
    if (stream.match(/\s*\/\s*[0-9]/, false)) {
      stream.match(/\s*\/\s*[0-9]/, true);
      return rval(state, stream, "fun"); // f/0 style fun
    }
    var w = stream.current();
    if (is_member(w, keywordWords)) {
      return rval(state, stream, "keyword");
    } else if (is_member(w, operatorAtomWords)) {
      return rval(state, stream, "operator");
    } else if (stream.match(/\s*\(/, false)) {
      // 'put' and 'erlang:put' are bifs, 'foo:put' is not
      if (is_member(w, bifWords) && (peekToken(state).token != ":" || peekToken(state, 2).token == "erlang")) {
        return rval(state, stream, "builtin");
      } else if (is_member(w, guardWords)) {
        return rval(state, stream, "guard");
      } else {
        return rval(state, stream, "function");
      }
    } else if (lookahead(stream) == ":") {
      if (w == "erlang") {
        return rval(state, stream, "builtin");
      } else {
        return rval(state, stream, "function");
      }
    } else if (is_member(w, ["true", "false"])) {
      return rval(state, stream, "boolean");
    } else {
      return rval(state, stream, "atom");
    }
  }

  // number
  var digitRE = /[0-9]/;
  var radixRE = /[0-9a-zA-Z]/; // 36#zZ style int
  if (digitRE.test(ch)) {
    stream.eatWhile(digitRE);
    if (stream.eat('#')) {
      // 36#aZ  style integer
      if (!stream.eatWhile(radixRE)) {
        stream.backUp(1); //"36#" - syntax error
      }
    } else if (stream.eat('.')) {
      // float
      if (!stream.eatWhile(digitRE)) {
        stream.backUp(1); // "3." - probably end of function
      } else {
        if (stream.eat(/[eE]/)) {
          // float with exponent
          if (stream.eat(/[-+]/)) {
            if (!stream.eatWhile(digitRE)) {
              stream.backUp(2); // "2e-" - syntax error
            }
          } else {
            if (!stream.eatWhile(digitRE)) {
              stream.backUp(1); // "2e" - syntax error
            }
          }
        }
      }
    }
    return rval(state, stream, "number"); // normal integer
  }

  // open parens
  if (nongreedy(stream, openParenRE, openParenWords)) {
    return rval(state, stream, "open_paren");
  }

  // close parens
  if (nongreedy(stream, closeParenRE, closeParenWords)) {
    return rval(state, stream, "close_paren");
  }

  // separators
  if (greedy(stream, separatorRE, separatorWords)) {
    return rval(state, stream, "separator");
  }

  // operators
  if (greedy(stream, operatorSymbolRE, operatorSymbolWords)) {
    return rval(state, stream, "operator");
  }
  return rval(state, stream, null);
}

/////////////////////////////////////////////////////////////////////////////
// utilities
function nongreedy(stream, re, words) {
  if (stream.current().length == 1 && re.test(stream.current())) {
    stream.backUp(1);
    while (re.test(stream.peek())) {
      stream.next();
      if (is_member(stream.current(), words)) {
        return true;
      }
    }
    stream.backUp(stream.current().length - 1);
  }
  return false;
}
function greedy(stream, re, words) {
  if (stream.current().length == 1 && re.test(stream.current())) {
    while (re.test(stream.peek())) {
      stream.next();
    }
    while (0 < stream.current().length) {
      if (is_member(stream.current(), words)) {
        return true;
      } else {
        stream.backUp(1);
      }
    }
    stream.next();
  }
  return false;
}
function doubleQuote(stream) {
  return quote(stream, '"', '\\');
}
function singleQuote(stream) {
  return quote(stream, '\'', '\\');
}
function quote(stream, quoteChar, escapeChar) {
  while (!stream.eol()) {
    var ch = stream.next();
    if (ch == quoteChar) {
      return true;
    } else if (ch == escapeChar) {
      stream.next();
    }
  }
  return false;
}
function lookahead(stream) {
  var m = stream.match(/^\s*([^\s%])/, false);
  return m ? m[1] : "";
}
function is_member(element, list) {
  return -1 < list.indexOf(element);
}
function rval(state, stream, type) {
  // parse stack
  pushToken(state, realToken(type, stream));

  // map erlang token type to CodeMirror style class
  //     erlang             -> CodeMirror tag
  switch (type) {
    case "atom":
      return "atom";
    case "attribute":
      return "attribute";
    case "boolean":
      return "atom";
    case "builtin":
      return "builtin";
    case "close_paren":
      return null;
    case "colon":
      return null;
    case "comment":
      return "comment";
    case "dot":
      return null;
    case "error":
      return "error";
    case "fun":
      return "meta";
    case "function":
      return "tag";
    case "guard":
      return "property";
    case "keyword":
      return "keyword";
    case "macro":
      return "macroName";
    case "number":
      return "number";
    case "open_paren":
      return null;
    case "operator":
      return "operator";
    case "record":
      return "bracket";
    case "separator":
      return null;
    case "string":
      return "string";
    case "type":
      return "def";
    case "variable":
      return "variable";
    default:
      return null;
  }
}
function aToken(tok, col, ind, typ) {
  return {
    token: tok,
    column: col,
    indent: ind,
    type: typ
  };
}
function realToken(type, stream) {
  return aToken(stream.current(), stream.column(), stream.indentation(), type);
}
function fakeToken(type) {
  return aToken(type, 0, 0, type);
}
function peekToken(state, depth) {
  var len = state.tokenStack.length;
  var dep = depth ? depth : 1;
  if (len < dep) {
    return false;
  } else {
    return state.tokenStack[len - dep];
  }
}
function pushToken(state, token) {
  if (!(token.type == "comment" || token.type == "whitespace")) {
    state.tokenStack = maybe_drop_pre(state.tokenStack, token);
    state.tokenStack = maybe_drop_post(state.tokenStack);
  }
}
function maybe_drop_pre(s, token) {
  var last = s.length - 1;
  if (0 < last && s[last].type === "record" && token.type === "dot") {
    s.pop();
  } else if (0 < last && s[last].type === "group") {
    s.pop();
    s.push(token);
  } else {
    s.push(token);
  }
  return s;
}
function maybe_drop_post(s) {
  if (!s.length) return s;
  var last = s.length - 1;
  if (s[last].type === "dot") {
    return [];
  }
  if (last > 1 && s[last].type === "fun" && s[last - 1].token === "fun") {
    return s.slice(0, last - 1);
  }
  switch (s[last].token) {
    case "}":
      return d(s, {
        g: ["{"]
      });
    case "]":
      return d(s, {
        i: ["["]
      });
    case ")":
      return d(s, {
        i: ["("]
      });
    case ">>":
      return d(s, {
        i: ["<<"]
      });
    case "end":
      return d(s, {
        i: ["begin", "case", "fun", "if", "receive", "try"]
      });
    case ",":
      return d(s, {
        e: ["begin", "try", "when", "->", ",", "(", "[", "{", "<<"]
      });
    case "->":
      return d(s, {
        r: ["when"],
        m: ["try", "if", "case", "receive"]
      });
    case ";":
      return d(s, {
        E: ["case", "fun", "if", "receive", "try", "when"]
      });
    case "catch":
      return d(s, {
        e: ["try"]
      });
    case "of":
      return d(s, {
        e: ["case"]
      });
    case "after":
      return d(s, {
        e: ["receive", "try"]
      });
    default:
      return s;
  }
}
function d(stack, tt) {
  // stack is a stack of Token objects.
  // tt is an object; {type:tokens}
  // type is a char, tokens is a list of token strings.
  // The function returns (possibly truncated) stack.
  // It will descend the stack, looking for a Token such that Token.token
  //  is a member of tokens. If it does not find that, it will normally (but
  //  see "E" below) return stack. If it does find a match, it will remove
  //  all the Tokens between the top and the matched Token.
  // If type is "m", that is all it does.
  // If type is "i", it will also remove the matched Token and the top Token.
  // If type is "g", like "i", but add a fake "group" token at the top.
  // If type is "r", it will remove the matched Token, but not the top Token.
  // If type is "e", it will keep the matched Token but not the top Token.
  // If type is "E", it behaves as for type "e", except if there is no match,
  //  in which case it will return an empty stack.

  for (var type in tt) {
    var len = stack.length - 1;
    var tokens = tt[type];
    for (var i = len - 1; -1 < i; i--) {
      if (is_member(stack[i].token, tokens)) {
        var ss = stack.slice(0, i);
        switch (type) {
          case "m":
            return ss.concat(stack[i]).concat(stack[len]);
          case "r":
            return ss.concat(stack[len]);
          case "i":
            return ss;
          case "g":
            return ss.concat(fakeToken("group"));
          case "E":
            return ss.concat(stack[i]);
          case "e":
            return ss.concat(stack[i]);
        }
      }
    }
  }
  return type == "E" ? [] : stack;
}

/////////////////////////////////////////////////////////////////////////////
// indenter

function indenter(state, textAfter, cx) {
  var t;
  var wordAfter = wordafter(textAfter);
  var currT = peekToken(state, 1);
  var prevT = peekToken(state, 2);
  if (state.in_string || state.in_atom) {
    return null;
  } else if (!prevT) {
    return 0;
  } else if (currT.token == "when") {
    return currT.column + cx.unit;
  } else if (wordAfter === "when" && prevT.type === "function") {
    return prevT.indent + cx.unit;
  } else if (wordAfter === "(" && currT.token === "fun") {
    return currT.column + 3;
  } else if (wordAfter === "catch" && (t = getToken(state, ["try"]))) {
    return t.column;
  } else if (is_member(wordAfter, ["end", "after", "of"])) {
    t = getToken(state, ["begin", "case", "fun", "if", "receive", "try"]);
    return t ? t.column : null;
  } else if (is_member(wordAfter, closeParenWords)) {
    t = getToken(state, openParenWords);
    return t ? t.column : null;
  } else if (is_member(currT.token, [",", "|", "||"]) || is_member(wordAfter, [",", "|", "||"])) {
    t = postcommaToken(state);
    return t ? t.column + t.token.length : cx.unit;
  } else if (currT.token == "->") {
    if (is_member(prevT.token, ["receive", "case", "if", "try"])) {
      return prevT.column + cx.unit + cx.unit;
    } else {
      return prevT.column + cx.unit;
    }
  } else if (is_member(currT.token, openParenWords)) {
    return currT.column + currT.token.length;
  } else {
    t = defaultToken(state);
    return truthy(t) ? t.column + cx.unit : 0;
  }
}
function wordafter(str) {
  var m = str.match(/,|[a-z]+|\}|\]|\)|>>|\|+|\(/);
  return truthy(m) && m.index === 0 ? m[0] : "";
}
function postcommaToken(state) {
  var objs = state.tokenStack.slice(0, -1);
  var i = getTokenIndex(objs, "type", ["open_paren"]);
  return truthy(objs[i]) ? objs[i] : false;
}
function defaultToken(state) {
  var objs = state.tokenStack;
  var stop = getTokenIndex(objs, "type", ["open_paren", "separator", "keyword"]);
  var oper = getTokenIndex(objs, "type", ["operator"]);
  if (truthy(stop) && truthy(oper) && stop < oper) {
    return objs[stop + 1];
  } else if (truthy(stop)) {
    return objs[stop];
  } else {
    return false;
  }
}
function getToken(state, tokens) {
  var objs = state.tokenStack;
  var i = getTokenIndex(objs, "token", tokens);
  return truthy(objs[i]) ? objs[i] : false;
}
function getTokenIndex(objs, propname, propvals) {
  for (var i = objs.length - 1; -1 < i; i--) {
    if (is_member(objs[i][propname], propvals)) {
      return i;
    }
  }
  return false;
}
function truthy(x) {
  return x !== false && x != null;
}

/////////////////////////////////////////////////////////////////////////////
// this object defines the mode

const erlang = {
  name: "erlang",
  startState() {
    return {
      tokenStack: [],
      in_string: false,
      in_atom: false
    };
  },
  token: tokenizer,
  indent: indenter,
  languageData: {
    commentTokens: {
      line: "%"
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNjMyMy5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL2VybGFuZy5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyIvLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vL1xuLy8gY29uc3RhbnRzXG5cbnZhciB0eXBlV29yZHMgPSBbXCItdHlwZVwiLCBcIi1zcGVjXCIsIFwiLWV4cG9ydF90eXBlXCIsIFwiLW9wYXF1ZVwiXTtcbnZhciBrZXl3b3JkV29yZHMgPSBbXCJhZnRlclwiLCBcImJlZ2luXCIsIFwiY2F0Y2hcIiwgXCJjYXNlXCIsIFwiY29uZFwiLCBcImVuZFwiLCBcImZ1blwiLCBcImlmXCIsIFwibGV0XCIsIFwib2ZcIiwgXCJxdWVyeVwiLCBcInJlY2VpdmVcIiwgXCJ0cnlcIiwgXCJ3aGVuXCJdO1xudmFyIHNlcGFyYXRvclJFID0gL1tcXC0+LDtdLztcbnZhciBzZXBhcmF0b3JXb3JkcyA9IFtcIi0+XCIsIFwiO1wiLCBcIixcIl07XG52YXIgb3BlcmF0b3JBdG9tV29yZHMgPSBbXCJhbmRcIiwgXCJhbmRhbHNvXCIsIFwiYmFuZFwiLCBcImJub3RcIiwgXCJib3JcIiwgXCJic2xcIiwgXCJic3JcIiwgXCJieG9yXCIsIFwiZGl2XCIsIFwibm90XCIsIFwib3JcIiwgXCJvcmVsc2VcIiwgXCJyZW1cIiwgXCJ4b3JcIl07XG52YXIgb3BlcmF0b3JTeW1ib2xSRSA9IC9bXFwrXFwtXFwqXFwvPD49XFx8OiFdLztcbnZhciBvcGVyYXRvclN5bWJvbFdvcmRzID0gW1wiPVwiLCBcIitcIiwgXCItXCIsIFwiKlwiLCBcIi9cIiwgXCI+XCIsIFwiPj1cIiwgXCI8XCIsIFwiPTxcIiwgXCI9Oj1cIiwgXCI9PVwiLCBcIj0vPVwiLCBcIi89XCIsIFwifHxcIiwgXCI8LVwiLCBcIiFcIl07XG52YXIgb3BlblBhcmVuUkUgPSAvWzxcXChcXFtcXHtdLztcbnZhciBvcGVuUGFyZW5Xb3JkcyA9IFtcIjw8XCIsIFwiKFwiLCBcIltcIiwgXCJ7XCJdO1xudmFyIGNsb3NlUGFyZW5SRSA9IC9bPlxcKVxcXVxcfV0vO1xudmFyIGNsb3NlUGFyZW5Xb3JkcyA9IFtcIn1cIiwgXCJdXCIsIFwiKVwiLCBcIj4+XCJdO1xudmFyIGd1YXJkV29yZHMgPSBbXCJpc19hdG9tXCIsIFwiaXNfYmluYXJ5XCIsIFwiaXNfYml0c3RyaW5nXCIsIFwiaXNfYm9vbGVhblwiLCBcImlzX2Zsb2F0XCIsIFwiaXNfZnVuY3Rpb25cIiwgXCJpc19pbnRlZ2VyXCIsIFwiaXNfbGlzdFwiLCBcImlzX251bWJlclwiLCBcImlzX3BpZFwiLCBcImlzX3BvcnRcIiwgXCJpc19yZWNvcmRcIiwgXCJpc19yZWZlcmVuY2VcIiwgXCJpc190dXBsZVwiLCBcImF0b21cIiwgXCJiaW5hcnlcIiwgXCJiaXRzdHJpbmdcIiwgXCJib29sZWFuXCIsIFwiZnVuY3Rpb25cIiwgXCJpbnRlZ2VyXCIsIFwibGlzdFwiLCBcIm51bWJlclwiLCBcInBpZFwiLCBcInBvcnRcIiwgXCJyZWNvcmRcIiwgXCJyZWZlcmVuY2VcIiwgXCJ0dXBsZVwiXTtcbnZhciBiaWZXb3JkcyA9IFtcImFic1wiLCBcImFkbGVyMzJcIiwgXCJhZGxlcjMyX2NvbWJpbmVcIiwgXCJhbGl2ZVwiLCBcImFwcGx5XCIsIFwiYXRvbV90b19iaW5hcnlcIiwgXCJhdG9tX3RvX2xpc3RcIiwgXCJiaW5hcnlfdG9fYXRvbVwiLCBcImJpbmFyeV90b19leGlzdGluZ19hdG9tXCIsIFwiYmluYXJ5X3RvX2xpc3RcIiwgXCJiaW5hcnlfdG9fdGVybVwiLCBcImJpdF9zaXplXCIsIFwiYml0c3RyaW5nX3RvX2xpc3RcIiwgXCJieXRlX3NpemVcIiwgXCJjaGVja19wcm9jZXNzX2NvZGVcIiwgXCJjb250YWN0X2JpbmFyeVwiLCBcImNyYzMyXCIsIFwiY3JjMzJfY29tYmluZVwiLCBcImRhdGVcIiwgXCJkZWNvZGVfcGFja2V0XCIsIFwiZGVsZXRlX21vZHVsZVwiLCBcImRpc2Nvbm5lY3Rfbm9kZVwiLCBcImVsZW1lbnRcIiwgXCJlcmFzZVwiLCBcImV4aXRcIiwgXCJmbG9hdFwiLCBcImZsb2F0X3RvX2xpc3RcIiwgXCJnYXJiYWdlX2NvbGxlY3RcIiwgXCJnZXRcIiwgXCJnZXRfa2V5c1wiLCBcImdyb3VwX2xlYWRlclwiLCBcImhhbHRcIiwgXCJoZFwiLCBcImludGVnZXJfdG9fbGlzdFwiLCBcImludGVybmFsX2JpZlwiLCBcImlvbGlzdF9zaXplXCIsIFwiaW9saXN0X3RvX2JpbmFyeVwiLCBcImlzX2FsaXZlXCIsIFwiaXNfYXRvbVwiLCBcImlzX2JpbmFyeVwiLCBcImlzX2JpdHN0cmluZ1wiLCBcImlzX2Jvb2xlYW5cIiwgXCJpc19mbG9hdFwiLCBcImlzX2Z1bmN0aW9uXCIsIFwiaXNfaW50ZWdlclwiLCBcImlzX2xpc3RcIiwgXCJpc19udW1iZXJcIiwgXCJpc19waWRcIiwgXCJpc19wb3J0XCIsIFwiaXNfcHJvY2Vzc19hbGl2ZVwiLCBcImlzX3JlY29yZFwiLCBcImlzX3JlZmVyZW5jZVwiLCBcImlzX3R1cGxlXCIsIFwibGVuZ3RoXCIsIFwibGlua1wiLCBcImxpc3RfdG9fYXRvbVwiLCBcImxpc3RfdG9fYmluYXJ5XCIsIFwibGlzdF90b19iaXRzdHJpbmdcIiwgXCJsaXN0X3RvX2V4aXN0aW5nX2F0b21cIiwgXCJsaXN0X3RvX2Zsb2F0XCIsIFwibGlzdF90b19pbnRlZ2VyXCIsIFwibGlzdF90b19waWRcIiwgXCJsaXN0X3RvX3R1cGxlXCIsIFwibG9hZF9tb2R1bGVcIiwgXCJtYWtlX3JlZlwiLCBcIm1vZHVsZV9sb2FkZWRcIiwgXCJtb25pdG9yX25vZGVcIiwgXCJub2RlXCIsIFwibm9kZV9saW5rXCIsIFwibm9kZV91bmxpbmtcIiwgXCJub2Rlc1wiLCBcIm5vdGFsaXZlXCIsIFwibm93XCIsIFwib3Blbl9wb3J0XCIsIFwicGlkX3RvX2xpc3RcIiwgXCJwb3J0X2Nsb3NlXCIsIFwicG9ydF9jb21tYW5kXCIsIFwicG9ydF9jb25uZWN0XCIsIFwicG9ydF9jb250cm9sXCIsIFwicHJlX2xvYWRlZFwiLCBcInByb2Nlc3NfZmxhZ1wiLCBcInByb2Nlc3NfaW5mb1wiLCBcInByb2Nlc3Nlc1wiLCBcInB1cmdlX21vZHVsZVwiLCBcInB1dFwiLCBcInJlZ2lzdGVyXCIsIFwicmVnaXN0ZXJlZFwiLCBcInJvdW5kXCIsIFwic2VsZlwiLCBcInNldGVsZW1lbnRcIiwgXCJzaXplXCIsIFwic3Bhd25cIiwgXCJzcGF3bl9saW5rXCIsIFwic3Bhd25fbW9uaXRvclwiLCBcInNwYXduX29wdFwiLCBcInNwbGl0X2JpbmFyeVwiLCBcInN0YXRpc3RpY3NcIiwgXCJ0ZXJtX3RvX2JpbmFyeVwiLCBcInRpbWVcIiwgXCJ0aHJvd1wiLCBcInRsXCIsIFwidHJ1bmNcIiwgXCJ0dXBsZV9zaXplXCIsIFwidHVwbGVfdG9fbGlzdFwiLCBcInVubGlua1wiLCBcInVucmVnaXN0ZXJcIiwgXCJ3aGVyZWlzXCJdO1xuXG4vLyB1cHBlciBjYXNlOiBbQS1aXSBbw5gtw55dIFvDgC3Dll1cbi8vIGxvd2VyIGNhc2U6IFthLXpdIFvDny3Dtl0gW8O4LcO/XVxudmFyIGFudW1SRSA9IC9bXFx3QMOYLcOew4Atw5bDny3DtsO4LcO/XS87XG52YXIgZXNjYXBlc1JFID0gL1swLTddezEsM318W2JkZWZucnN0dlxcXFxcIiddfFxcXlthLXpBLVpdfHhbMC05YS16QS1aXXsyfXx4e1swLTlhLXpBLVpdK30vO1xuXG4vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vL1xuLy8gdG9rZW5pemVyXG5cbmZ1bmN0aW9uIHRva2VuaXplcihzdHJlYW0sIHN0YXRlKSB7XG4gIC8vIGluIG11bHRpLWxpbmUgc3RyaW5nXG4gIGlmIChzdGF0ZS5pbl9zdHJpbmcpIHtcbiAgICBzdGF0ZS5pbl9zdHJpbmcgPSAhZG91YmxlUXVvdGUoc3RyZWFtKTtcbiAgICByZXR1cm4gcnZhbChzdGF0ZSwgc3RyZWFtLCBcInN0cmluZ1wiKTtcbiAgfVxuXG4gIC8vIGluIG11bHRpLWxpbmUgYXRvbVxuICBpZiAoc3RhdGUuaW5fYXRvbSkge1xuICAgIHN0YXRlLmluX2F0b20gPSAhc2luZ2xlUXVvdGUoc3RyZWFtKTtcbiAgICByZXR1cm4gcnZhbChzdGF0ZSwgc3RyZWFtLCBcImF0b21cIik7XG4gIH1cblxuICAvLyB3aGl0ZXNwYWNlXG4gIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkge1xuICAgIHJldHVybiBydmFsKHN0YXRlLCBzdHJlYW0sIFwid2hpdGVzcGFjZVwiKTtcbiAgfVxuXG4gIC8vIGF0dHJpYnV0ZXMgYW5kIHR5cGUgc3BlY3NcbiAgaWYgKCFwZWVrVG9rZW4oc3RhdGUpICYmIHN0cmVhbS5tYXRjaCgvLVxccypbYS16w58tw7bDuC3Dv11bXFx3w5gtw57DgC3DlsOfLcO2w7gtw79dKi8pKSB7XG4gICAgaWYgKGlzX21lbWJlcihzdHJlYW0uY3VycmVudCgpLCB0eXBlV29yZHMpKSB7XG4gICAgICByZXR1cm4gcnZhbChzdGF0ZSwgc3RyZWFtLCBcInR5cGVcIik7XG4gICAgfSBlbHNlIHtcbiAgICAgIHJldHVybiBydmFsKHN0YXRlLCBzdHJlYW0sIFwiYXR0cmlidXRlXCIpO1xuICAgIH1cbiAgfVxuICB2YXIgY2ggPSBzdHJlYW0ubmV4dCgpO1xuXG4gIC8vIGNvbW1lbnRcbiAgaWYgKGNoID09ICclJykge1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gcnZhbChzdGF0ZSwgc3RyZWFtLCBcImNvbW1lbnRcIik7XG4gIH1cblxuICAvLyBjb2xvblxuICBpZiAoY2ggPT0gXCI6XCIpIHtcbiAgICByZXR1cm4gcnZhbChzdGF0ZSwgc3RyZWFtLCBcImNvbG9uXCIpO1xuICB9XG5cbiAgLy8gbWFjcm9cbiAgaWYgKGNoID09ICc/Jykge1xuICAgIHN0cmVhbS5lYXRTcGFjZSgpO1xuICAgIHN0cmVhbS5lYXRXaGlsZShhbnVtUkUpO1xuICAgIHJldHVybiBydmFsKHN0YXRlLCBzdHJlYW0sIFwibWFjcm9cIik7XG4gIH1cblxuICAvLyByZWNvcmRcbiAgaWYgKGNoID09IFwiI1wiKSB7XG4gICAgc3RyZWFtLmVhdFNwYWNlKCk7XG4gICAgc3RyZWFtLmVhdFdoaWxlKGFudW1SRSk7XG4gICAgcmV0dXJuIHJ2YWwoc3RhdGUsIHN0cmVhbSwgXCJyZWNvcmRcIik7XG4gIH1cblxuICAvLyBkb2xsYXIgZXNjYXBlXG4gIGlmIChjaCA9PSBcIiRcIikge1xuICAgIGlmIChzdHJlYW0ubmV4dCgpID09IFwiXFxcXFwiICYmICFzdHJlYW0ubWF0Y2goZXNjYXBlc1JFKSkge1xuICAgICAgcmV0dXJuIHJ2YWwoc3RhdGUsIHN0cmVhbSwgXCJlcnJvclwiKTtcbiAgICB9XG4gICAgcmV0dXJuIHJ2YWwoc3RhdGUsIHN0cmVhbSwgXCJudW1iZXJcIik7XG4gIH1cblxuICAvLyBkb3RcbiAgaWYgKGNoID09IFwiLlwiKSB7XG4gICAgcmV0dXJuIHJ2YWwoc3RhdGUsIHN0cmVhbSwgXCJkb3RcIik7XG4gIH1cblxuICAvLyBxdW90ZWQgYXRvbVxuICBpZiAoY2ggPT0gJ1xcJycpIHtcbiAgICBpZiAoIShzdGF0ZS5pbl9hdG9tID0gIXNpbmdsZVF1b3RlKHN0cmVhbSkpKSB7XG4gICAgICBpZiAoc3RyZWFtLm1hdGNoKC9cXHMqXFwvXFxzKlswLTldLywgZmFsc2UpKSB7XG4gICAgICAgIHN0cmVhbS5tYXRjaCgvXFxzKlxcL1xccypbMC05XS8sIHRydWUpO1xuICAgICAgICByZXR1cm4gcnZhbChzdGF0ZSwgc3RyZWFtLCBcImZ1blwiKTsgLy8gJ2YnLzAgc3R5bGUgZnVuXG4gICAgICB9XG4gICAgICBpZiAoc3RyZWFtLm1hdGNoKC9cXHMqXFwoLywgZmFsc2UpIHx8IHN0cmVhbS5tYXRjaCgvXFxzKjovLCBmYWxzZSkpIHtcbiAgICAgICAgcmV0dXJuIHJ2YWwoc3RhdGUsIHN0cmVhbSwgXCJmdW5jdGlvblwiKTtcbiAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIHJ2YWwoc3RhdGUsIHN0cmVhbSwgXCJhdG9tXCIpO1xuICB9XG5cbiAgLy8gc3RyaW5nXG4gIGlmIChjaCA9PSAnXCInKSB7XG4gICAgc3RhdGUuaW5fc3RyaW5nID0gIWRvdWJsZVF1b3RlKHN0cmVhbSk7XG4gICAgcmV0dXJuIHJ2YWwoc3RhdGUsIHN0cmVhbSwgXCJzdHJpbmdcIik7XG4gIH1cblxuICAvLyB2YXJpYWJsZVxuICBpZiAoL1tBLVpfw5gtw57DgC3Dll0vLnRlc3QoY2gpKSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKGFudW1SRSk7XG4gICAgcmV0dXJuIHJ2YWwoc3RhdGUsIHN0cmVhbSwgXCJ2YXJpYWJsZVwiKTtcbiAgfVxuXG4gIC8vIGF0b20va2V5d29yZC9CSUYvZnVuY3Rpb25cbiAgaWYgKC9bYS16X8OfLcO2w7gtw79dLy50ZXN0KGNoKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZShhbnVtUkUpO1xuICAgIGlmIChzdHJlYW0ubWF0Y2goL1xccypcXC9cXHMqWzAtOV0vLCBmYWxzZSkpIHtcbiAgICAgIHN0cmVhbS5tYXRjaCgvXFxzKlxcL1xccypbMC05XS8sIHRydWUpO1xuICAgICAgcmV0dXJuIHJ2YWwoc3RhdGUsIHN0cmVhbSwgXCJmdW5cIik7IC8vIGYvMCBzdHlsZSBmdW5cbiAgICB9XG4gICAgdmFyIHcgPSBzdHJlYW0uY3VycmVudCgpO1xuICAgIGlmIChpc19tZW1iZXIodywga2V5d29yZFdvcmRzKSkge1xuICAgICAgcmV0dXJuIHJ2YWwoc3RhdGUsIHN0cmVhbSwgXCJrZXl3b3JkXCIpO1xuICAgIH0gZWxzZSBpZiAoaXNfbWVtYmVyKHcsIG9wZXJhdG9yQXRvbVdvcmRzKSkge1xuICAgICAgcmV0dXJuIHJ2YWwoc3RhdGUsIHN0cmVhbSwgXCJvcGVyYXRvclwiKTtcbiAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaCgvXFxzKlxcKC8sIGZhbHNlKSkge1xuICAgICAgLy8gJ3B1dCcgYW5kICdlcmxhbmc6cHV0JyBhcmUgYmlmcywgJ2ZvbzpwdXQnIGlzIG5vdFxuICAgICAgaWYgKGlzX21lbWJlcih3LCBiaWZXb3JkcykgJiYgKHBlZWtUb2tlbihzdGF0ZSkudG9rZW4gIT0gXCI6XCIgfHwgcGVla1Rva2VuKHN0YXRlLCAyKS50b2tlbiA9PSBcImVybGFuZ1wiKSkge1xuICAgICAgICByZXR1cm4gcnZhbChzdGF0ZSwgc3RyZWFtLCBcImJ1aWx0aW5cIik7XG4gICAgICB9IGVsc2UgaWYgKGlzX21lbWJlcih3LCBndWFyZFdvcmRzKSkge1xuICAgICAgICByZXR1cm4gcnZhbChzdGF0ZSwgc3RyZWFtLCBcImd1YXJkXCIpO1xuICAgICAgfSBlbHNlIHtcbiAgICAgICAgcmV0dXJuIHJ2YWwoc3RhdGUsIHN0cmVhbSwgXCJmdW5jdGlvblwiKTtcbiAgICAgIH1cbiAgICB9IGVsc2UgaWYgKGxvb2thaGVhZChzdHJlYW0pID09IFwiOlwiKSB7XG4gICAgICBpZiAodyA9PSBcImVybGFuZ1wiKSB7XG4gICAgICAgIHJldHVybiBydmFsKHN0YXRlLCBzdHJlYW0sIFwiYnVpbHRpblwiKTtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIHJldHVybiBydmFsKHN0YXRlLCBzdHJlYW0sIFwiZnVuY3Rpb25cIik7XG4gICAgICB9XG4gICAgfSBlbHNlIGlmIChpc19tZW1iZXIodywgW1widHJ1ZVwiLCBcImZhbHNlXCJdKSkge1xuICAgICAgcmV0dXJuIHJ2YWwoc3RhdGUsIHN0cmVhbSwgXCJib29sZWFuXCIpO1xuICAgIH0gZWxzZSB7XG4gICAgICByZXR1cm4gcnZhbChzdGF0ZSwgc3RyZWFtLCBcImF0b21cIik7XG4gICAgfVxuICB9XG5cbiAgLy8gbnVtYmVyXG4gIHZhciBkaWdpdFJFID0gL1swLTldLztcbiAgdmFyIHJhZGl4UkUgPSAvWzAtOWEtekEtWl0vOyAvLyAzNiN6WiBzdHlsZSBpbnRcbiAgaWYgKGRpZ2l0UkUudGVzdChjaCkpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoZGlnaXRSRSk7XG4gICAgaWYgKHN0cmVhbS5lYXQoJyMnKSkge1xuICAgICAgLy8gMzYjYVogIHN0eWxlIGludGVnZXJcbiAgICAgIGlmICghc3RyZWFtLmVhdFdoaWxlKHJhZGl4UkUpKSB7XG4gICAgICAgIHN0cmVhbS5iYWNrVXAoMSk7IC8vXCIzNiNcIiAtIHN5bnRheCBlcnJvclxuICAgICAgfVxuICAgIH0gZWxzZSBpZiAoc3RyZWFtLmVhdCgnLicpKSB7XG4gICAgICAvLyBmbG9hdFxuICAgICAgaWYgKCFzdHJlYW0uZWF0V2hpbGUoZGlnaXRSRSkpIHtcbiAgICAgICAgc3RyZWFtLmJhY2tVcCgxKTsgLy8gXCIzLlwiIC0gcHJvYmFibHkgZW5kIG9mIGZ1bmN0aW9uXG4gICAgICB9IGVsc2Uge1xuICAgICAgICBpZiAoc3RyZWFtLmVhdCgvW2VFXS8pKSB7XG4gICAgICAgICAgLy8gZmxvYXQgd2l0aCBleHBvbmVudFxuICAgICAgICAgIGlmIChzdHJlYW0uZWF0KC9bLStdLykpIHtcbiAgICAgICAgICAgIGlmICghc3RyZWFtLmVhdFdoaWxlKGRpZ2l0UkUpKSB7XG4gICAgICAgICAgICAgIHN0cmVhbS5iYWNrVXAoMik7IC8vIFwiMmUtXCIgLSBzeW50YXggZXJyb3JcbiAgICAgICAgICAgIH1cbiAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgaWYgKCFzdHJlYW0uZWF0V2hpbGUoZGlnaXRSRSkpIHtcbiAgICAgICAgICAgICAgc3RyZWFtLmJhY2tVcCgxKTsgLy8gXCIyZVwiIC0gc3ludGF4IGVycm9yXG4gICAgICAgICAgICB9XG4gICAgICAgICAgfVxuICAgICAgICB9XG4gICAgICB9XG4gICAgfVxuICAgIHJldHVybiBydmFsKHN0YXRlLCBzdHJlYW0sIFwibnVtYmVyXCIpOyAvLyBub3JtYWwgaW50ZWdlclxuICB9XG5cbiAgLy8gb3BlbiBwYXJlbnNcbiAgaWYgKG5vbmdyZWVkeShzdHJlYW0sIG9wZW5QYXJlblJFLCBvcGVuUGFyZW5Xb3JkcykpIHtcbiAgICByZXR1cm4gcnZhbChzdGF0ZSwgc3RyZWFtLCBcIm9wZW5fcGFyZW5cIik7XG4gIH1cblxuICAvLyBjbG9zZSBwYXJlbnNcbiAgaWYgKG5vbmdyZWVkeShzdHJlYW0sIGNsb3NlUGFyZW5SRSwgY2xvc2VQYXJlbldvcmRzKSkge1xuICAgIHJldHVybiBydmFsKHN0YXRlLCBzdHJlYW0sIFwiY2xvc2VfcGFyZW5cIik7XG4gIH1cblxuICAvLyBzZXBhcmF0b3JzXG4gIGlmIChncmVlZHkoc3RyZWFtLCBzZXBhcmF0b3JSRSwgc2VwYXJhdG9yV29yZHMpKSB7XG4gICAgcmV0dXJuIHJ2YWwoc3RhdGUsIHN0cmVhbSwgXCJzZXBhcmF0b3JcIik7XG4gIH1cblxuICAvLyBvcGVyYXRvcnNcbiAgaWYgKGdyZWVkeShzdHJlYW0sIG9wZXJhdG9yU3ltYm9sUkUsIG9wZXJhdG9yU3ltYm9sV29yZHMpKSB7XG4gICAgcmV0dXJuIHJ2YWwoc3RhdGUsIHN0cmVhbSwgXCJvcGVyYXRvclwiKTtcbiAgfVxuICByZXR1cm4gcnZhbChzdGF0ZSwgc3RyZWFtLCBudWxsKTtcbn1cblxuLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy9cbi8vIHV0aWxpdGllc1xuZnVuY3Rpb24gbm9uZ3JlZWR5KHN0cmVhbSwgcmUsIHdvcmRzKSB7XG4gIGlmIChzdHJlYW0uY3VycmVudCgpLmxlbmd0aCA9PSAxICYmIHJlLnRlc3Qoc3RyZWFtLmN1cnJlbnQoKSkpIHtcbiAgICBzdHJlYW0uYmFja1VwKDEpO1xuICAgIHdoaWxlIChyZS50ZXN0KHN0cmVhbS5wZWVrKCkpKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgaWYgKGlzX21lbWJlcihzdHJlYW0uY3VycmVudCgpLCB3b3JkcykpIHtcbiAgICAgICAgcmV0dXJuIHRydWU7XG4gICAgICB9XG4gICAgfVxuICAgIHN0cmVhbS5iYWNrVXAoc3RyZWFtLmN1cnJlbnQoKS5sZW5ndGggLSAxKTtcbiAgfVxuICByZXR1cm4gZmFsc2U7XG59XG5mdW5jdGlvbiBncmVlZHkoc3RyZWFtLCByZSwgd29yZHMpIHtcbiAgaWYgKHN0cmVhbS5jdXJyZW50KCkubGVuZ3RoID09IDEgJiYgcmUudGVzdChzdHJlYW0uY3VycmVudCgpKSkge1xuICAgIHdoaWxlIChyZS50ZXN0KHN0cmVhbS5wZWVrKCkpKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgIH1cbiAgICB3aGlsZSAoMCA8IHN0cmVhbS5jdXJyZW50KCkubGVuZ3RoKSB7XG4gICAgICBpZiAoaXNfbWVtYmVyKHN0cmVhbS5jdXJyZW50KCksIHdvcmRzKSkge1xuICAgICAgICByZXR1cm4gdHJ1ZTtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIHN0cmVhbS5iYWNrVXAoMSk7XG4gICAgICB9XG4gICAgfVxuICAgIHN0cmVhbS5uZXh0KCk7XG4gIH1cbiAgcmV0dXJuIGZhbHNlO1xufVxuZnVuY3Rpb24gZG91YmxlUXVvdGUoc3RyZWFtKSB7XG4gIHJldHVybiBxdW90ZShzdHJlYW0sICdcIicsICdcXFxcJyk7XG59XG5mdW5jdGlvbiBzaW5nbGVRdW90ZShzdHJlYW0pIHtcbiAgcmV0dXJuIHF1b3RlKHN0cmVhbSwgJ1xcJycsICdcXFxcJyk7XG59XG5mdW5jdGlvbiBxdW90ZShzdHJlYW0sIHF1b3RlQ2hhciwgZXNjYXBlQ2hhcikge1xuICB3aGlsZSAoIXN0cmVhbS5lb2woKSkge1xuICAgIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gICAgaWYgKGNoID09IHF1b3RlQ2hhcikge1xuICAgICAgcmV0dXJuIHRydWU7XG4gICAgfSBlbHNlIGlmIChjaCA9PSBlc2NhcGVDaGFyKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgIH1cbiAgfVxuICByZXR1cm4gZmFsc2U7XG59XG5mdW5jdGlvbiBsb29rYWhlYWQoc3RyZWFtKSB7XG4gIHZhciBtID0gc3RyZWFtLm1hdGNoKC9eXFxzKihbXlxccyVdKS8sIGZhbHNlKTtcbiAgcmV0dXJuIG0gPyBtWzFdIDogXCJcIjtcbn1cbmZ1bmN0aW9uIGlzX21lbWJlcihlbGVtZW50LCBsaXN0KSB7XG4gIHJldHVybiAtMSA8IGxpc3QuaW5kZXhPZihlbGVtZW50KTtcbn1cbmZ1bmN0aW9uIHJ2YWwoc3RhdGUsIHN0cmVhbSwgdHlwZSkge1xuICAvLyBwYXJzZSBzdGFja1xuICBwdXNoVG9rZW4oc3RhdGUsIHJlYWxUb2tlbih0eXBlLCBzdHJlYW0pKTtcblxuICAvLyBtYXAgZXJsYW5nIHRva2VuIHR5cGUgdG8gQ29kZU1pcnJvciBzdHlsZSBjbGFzc1xuICAvLyAgICAgZXJsYW5nICAgICAgICAgICAgIC0+IENvZGVNaXJyb3IgdGFnXG4gIHN3aXRjaCAodHlwZSkge1xuICAgIGNhc2UgXCJhdG9tXCI6XG4gICAgICByZXR1cm4gXCJhdG9tXCI7XG4gICAgY2FzZSBcImF0dHJpYnV0ZVwiOlxuICAgICAgcmV0dXJuIFwiYXR0cmlidXRlXCI7XG4gICAgY2FzZSBcImJvb2xlYW5cIjpcbiAgICAgIHJldHVybiBcImF0b21cIjtcbiAgICBjYXNlIFwiYnVpbHRpblwiOlxuICAgICAgcmV0dXJuIFwiYnVpbHRpblwiO1xuICAgIGNhc2UgXCJjbG9zZV9wYXJlblwiOlxuICAgICAgcmV0dXJuIG51bGw7XG4gICAgY2FzZSBcImNvbG9uXCI6XG4gICAgICByZXR1cm4gbnVsbDtcbiAgICBjYXNlIFwiY29tbWVudFwiOlxuICAgICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICAgIGNhc2UgXCJkb3RcIjpcbiAgICAgIHJldHVybiBudWxsO1xuICAgIGNhc2UgXCJlcnJvclwiOlxuICAgICAgcmV0dXJuIFwiZXJyb3JcIjtcbiAgICBjYXNlIFwiZnVuXCI6XG4gICAgICByZXR1cm4gXCJtZXRhXCI7XG4gICAgY2FzZSBcImZ1bmN0aW9uXCI6XG4gICAgICByZXR1cm4gXCJ0YWdcIjtcbiAgICBjYXNlIFwiZ3VhcmRcIjpcbiAgICAgIHJldHVybiBcInByb3BlcnR5XCI7XG4gICAgY2FzZSBcImtleXdvcmRcIjpcbiAgICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgICBjYXNlIFwibWFjcm9cIjpcbiAgICAgIHJldHVybiBcIm1hY3JvTmFtZVwiO1xuICAgIGNhc2UgXCJudW1iZXJcIjpcbiAgICAgIHJldHVybiBcIm51bWJlclwiO1xuICAgIGNhc2UgXCJvcGVuX3BhcmVuXCI6XG4gICAgICByZXR1cm4gbnVsbDtcbiAgICBjYXNlIFwib3BlcmF0b3JcIjpcbiAgICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gICAgY2FzZSBcInJlY29yZFwiOlxuICAgICAgcmV0dXJuIFwiYnJhY2tldFwiO1xuICAgIGNhc2UgXCJzZXBhcmF0b3JcIjpcbiAgICAgIHJldHVybiBudWxsO1xuICAgIGNhc2UgXCJzdHJpbmdcIjpcbiAgICAgIHJldHVybiBcInN0cmluZ1wiO1xuICAgIGNhc2UgXCJ0eXBlXCI6XG4gICAgICByZXR1cm4gXCJkZWZcIjtcbiAgICBjYXNlIFwidmFyaWFibGVcIjpcbiAgICAgIHJldHVybiBcInZhcmlhYmxlXCI7XG4gICAgZGVmYXVsdDpcbiAgICAgIHJldHVybiBudWxsO1xuICB9XG59XG5mdW5jdGlvbiBhVG9rZW4odG9rLCBjb2wsIGluZCwgdHlwKSB7XG4gIHJldHVybiB7XG4gICAgdG9rZW46IHRvayxcbiAgICBjb2x1bW46IGNvbCxcbiAgICBpbmRlbnQ6IGluZCxcbiAgICB0eXBlOiB0eXBcbiAgfTtcbn1cbmZ1bmN0aW9uIHJlYWxUb2tlbih0eXBlLCBzdHJlYW0pIHtcbiAgcmV0dXJuIGFUb2tlbihzdHJlYW0uY3VycmVudCgpLCBzdHJlYW0uY29sdW1uKCksIHN0cmVhbS5pbmRlbnRhdGlvbigpLCB0eXBlKTtcbn1cbmZ1bmN0aW9uIGZha2VUb2tlbih0eXBlKSB7XG4gIHJldHVybiBhVG9rZW4odHlwZSwgMCwgMCwgdHlwZSk7XG59XG5mdW5jdGlvbiBwZWVrVG9rZW4oc3RhdGUsIGRlcHRoKSB7XG4gIHZhciBsZW4gPSBzdGF0ZS50b2tlblN0YWNrLmxlbmd0aDtcbiAgdmFyIGRlcCA9IGRlcHRoID8gZGVwdGggOiAxO1xuICBpZiAobGVuIDwgZGVwKSB7XG4gICAgcmV0dXJuIGZhbHNlO1xuICB9IGVsc2Uge1xuICAgIHJldHVybiBzdGF0ZS50b2tlblN0YWNrW2xlbiAtIGRlcF07XG4gIH1cbn1cbmZ1bmN0aW9uIHB1c2hUb2tlbihzdGF0ZSwgdG9rZW4pIHtcbiAgaWYgKCEodG9rZW4udHlwZSA9PSBcImNvbW1lbnRcIiB8fCB0b2tlbi50eXBlID09IFwid2hpdGVzcGFjZVwiKSkge1xuICAgIHN0YXRlLnRva2VuU3RhY2sgPSBtYXliZV9kcm9wX3ByZShzdGF0ZS50b2tlblN0YWNrLCB0b2tlbik7XG4gICAgc3RhdGUudG9rZW5TdGFjayA9IG1heWJlX2Ryb3BfcG9zdChzdGF0ZS50b2tlblN0YWNrKTtcbiAgfVxufVxuZnVuY3Rpb24gbWF5YmVfZHJvcF9wcmUocywgdG9rZW4pIHtcbiAgdmFyIGxhc3QgPSBzLmxlbmd0aCAtIDE7XG4gIGlmICgwIDwgbGFzdCAmJiBzW2xhc3RdLnR5cGUgPT09IFwicmVjb3JkXCIgJiYgdG9rZW4udHlwZSA9PT0gXCJkb3RcIikge1xuICAgIHMucG9wKCk7XG4gIH0gZWxzZSBpZiAoMCA8IGxhc3QgJiYgc1tsYXN0XS50eXBlID09PSBcImdyb3VwXCIpIHtcbiAgICBzLnBvcCgpO1xuICAgIHMucHVzaCh0b2tlbik7XG4gIH0gZWxzZSB7XG4gICAgcy5wdXNoKHRva2VuKTtcbiAgfVxuICByZXR1cm4gcztcbn1cbmZ1bmN0aW9uIG1heWJlX2Ryb3BfcG9zdChzKSB7XG4gIGlmICghcy5sZW5ndGgpIHJldHVybiBzO1xuICB2YXIgbGFzdCA9IHMubGVuZ3RoIC0gMTtcbiAgaWYgKHNbbGFzdF0udHlwZSA9PT0gXCJkb3RcIikge1xuICAgIHJldHVybiBbXTtcbiAgfVxuICBpZiAobGFzdCA+IDEgJiYgc1tsYXN0XS50eXBlID09PSBcImZ1blwiICYmIHNbbGFzdCAtIDFdLnRva2VuID09PSBcImZ1blwiKSB7XG4gICAgcmV0dXJuIHMuc2xpY2UoMCwgbGFzdCAtIDEpO1xuICB9XG4gIHN3aXRjaCAoc1tsYXN0XS50b2tlbikge1xuICAgIGNhc2UgXCJ9XCI6XG4gICAgICByZXR1cm4gZChzLCB7XG4gICAgICAgIGc6IFtcIntcIl1cbiAgICAgIH0pO1xuICAgIGNhc2UgXCJdXCI6XG4gICAgICByZXR1cm4gZChzLCB7XG4gICAgICAgIGk6IFtcIltcIl1cbiAgICAgIH0pO1xuICAgIGNhc2UgXCIpXCI6XG4gICAgICByZXR1cm4gZChzLCB7XG4gICAgICAgIGk6IFtcIihcIl1cbiAgICAgIH0pO1xuICAgIGNhc2UgXCI+PlwiOlxuICAgICAgcmV0dXJuIGQocywge1xuICAgICAgICBpOiBbXCI8PFwiXVxuICAgICAgfSk7XG4gICAgY2FzZSBcImVuZFwiOlxuICAgICAgcmV0dXJuIGQocywge1xuICAgICAgICBpOiBbXCJiZWdpblwiLCBcImNhc2VcIiwgXCJmdW5cIiwgXCJpZlwiLCBcInJlY2VpdmVcIiwgXCJ0cnlcIl1cbiAgICAgIH0pO1xuICAgIGNhc2UgXCIsXCI6XG4gICAgICByZXR1cm4gZChzLCB7XG4gICAgICAgIGU6IFtcImJlZ2luXCIsIFwidHJ5XCIsIFwid2hlblwiLCBcIi0+XCIsIFwiLFwiLCBcIihcIiwgXCJbXCIsIFwie1wiLCBcIjw8XCJdXG4gICAgICB9KTtcbiAgICBjYXNlIFwiLT5cIjpcbiAgICAgIHJldHVybiBkKHMsIHtcbiAgICAgICAgcjogW1wid2hlblwiXSxcbiAgICAgICAgbTogW1widHJ5XCIsIFwiaWZcIiwgXCJjYXNlXCIsIFwicmVjZWl2ZVwiXVxuICAgICAgfSk7XG4gICAgY2FzZSBcIjtcIjpcbiAgICAgIHJldHVybiBkKHMsIHtcbiAgICAgICAgRTogW1wiY2FzZVwiLCBcImZ1blwiLCBcImlmXCIsIFwicmVjZWl2ZVwiLCBcInRyeVwiLCBcIndoZW5cIl1cbiAgICAgIH0pO1xuICAgIGNhc2UgXCJjYXRjaFwiOlxuICAgICAgcmV0dXJuIGQocywge1xuICAgICAgICBlOiBbXCJ0cnlcIl1cbiAgICAgIH0pO1xuICAgIGNhc2UgXCJvZlwiOlxuICAgICAgcmV0dXJuIGQocywge1xuICAgICAgICBlOiBbXCJjYXNlXCJdXG4gICAgICB9KTtcbiAgICBjYXNlIFwiYWZ0ZXJcIjpcbiAgICAgIHJldHVybiBkKHMsIHtcbiAgICAgICAgZTogW1wicmVjZWl2ZVwiLCBcInRyeVwiXVxuICAgICAgfSk7XG4gICAgZGVmYXVsdDpcbiAgICAgIHJldHVybiBzO1xuICB9XG59XG5mdW5jdGlvbiBkKHN0YWNrLCB0dCkge1xuICAvLyBzdGFjayBpcyBhIHN0YWNrIG9mIFRva2VuIG9iamVjdHMuXG4gIC8vIHR0IGlzIGFuIG9iamVjdDsge3R5cGU6dG9rZW5zfVxuICAvLyB0eXBlIGlzIGEgY2hhciwgdG9rZW5zIGlzIGEgbGlzdCBvZiB0b2tlbiBzdHJpbmdzLlxuICAvLyBUaGUgZnVuY3Rpb24gcmV0dXJucyAocG9zc2libHkgdHJ1bmNhdGVkKSBzdGFjay5cbiAgLy8gSXQgd2lsbCBkZXNjZW5kIHRoZSBzdGFjaywgbG9va2luZyBmb3IgYSBUb2tlbiBzdWNoIHRoYXQgVG9rZW4udG9rZW5cbiAgLy8gIGlzIGEgbWVtYmVyIG9mIHRva2Vucy4gSWYgaXQgZG9lcyBub3QgZmluZCB0aGF0LCBpdCB3aWxsIG5vcm1hbGx5IChidXRcbiAgLy8gIHNlZSBcIkVcIiBiZWxvdykgcmV0dXJuIHN0YWNrLiBJZiBpdCBkb2VzIGZpbmQgYSBtYXRjaCwgaXQgd2lsbCByZW1vdmVcbiAgLy8gIGFsbCB0aGUgVG9rZW5zIGJldHdlZW4gdGhlIHRvcCBhbmQgdGhlIG1hdGNoZWQgVG9rZW4uXG4gIC8vIElmIHR5cGUgaXMgXCJtXCIsIHRoYXQgaXMgYWxsIGl0IGRvZXMuXG4gIC8vIElmIHR5cGUgaXMgXCJpXCIsIGl0IHdpbGwgYWxzbyByZW1vdmUgdGhlIG1hdGNoZWQgVG9rZW4gYW5kIHRoZSB0b3AgVG9rZW4uXG4gIC8vIElmIHR5cGUgaXMgXCJnXCIsIGxpa2UgXCJpXCIsIGJ1dCBhZGQgYSBmYWtlIFwiZ3JvdXBcIiB0b2tlbiBhdCB0aGUgdG9wLlxuICAvLyBJZiB0eXBlIGlzIFwiclwiLCBpdCB3aWxsIHJlbW92ZSB0aGUgbWF0Y2hlZCBUb2tlbiwgYnV0IG5vdCB0aGUgdG9wIFRva2VuLlxuICAvLyBJZiB0eXBlIGlzIFwiZVwiLCBpdCB3aWxsIGtlZXAgdGhlIG1hdGNoZWQgVG9rZW4gYnV0IG5vdCB0aGUgdG9wIFRva2VuLlxuICAvLyBJZiB0eXBlIGlzIFwiRVwiLCBpdCBiZWhhdmVzIGFzIGZvciB0eXBlIFwiZVwiLCBleGNlcHQgaWYgdGhlcmUgaXMgbm8gbWF0Y2gsXG4gIC8vICBpbiB3aGljaCBjYXNlIGl0IHdpbGwgcmV0dXJuIGFuIGVtcHR5IHN0YWNrLlxuXG4gIGZvciAodmFyIHR5cGUgaW4gdHQpIHtcbiAgICB2YXIgbGVuID0gc3RhY2subGVuZ3RoIC0gMTtcbiAgICB2YXIgdG9rZW5zID0gdHRbdHlwZV07XG4gICAgZm9yICh2YXIgaSA9IGxlbiAtIDE7IC0xIDwgaTsgaS0tKSB7XG4gICAgICBpZiAoaXNfbWVtYmVyKHN0YWNrW2ldLnRva2VuLCB0b2tlbnMpKSB7XG4gICAgICAgIHZhciBzcyA9IHN0YWNrLnNsaWNlKDAsIGkpO1xuICAgICAgICBzd2l0Y2ggKHR5cGUpIHtcbiAgICAgICAgICBjYXNlIFwibVwiOlxuICAgICAgICAgICAgcmV0dXJuIHNzLmNvbmNhdChzdGFja1tpXSkuY29uY2F0KHN0YWNrW2xlbl0pO1xuICAgICAgICAgIGNhc2UgXCJyXCI6XG4gICAgICAgICAgICByZXR1cm4gc3MuY29uY2F0KHN0YWNrW2xlbl0pO1xuICAgICAgICAgIGNhc2UgXCJpXCI6XG4gICAgICAgICAgICByZXR1cm4gc3M7XG4gICAgICAgICAgY2FzZSBcImdcIjpcbiAgICAgICAgICAgIHJldHVybiBzcy5jb25jYXQoZmFrZVRva2VuKFwiZ3JvdXBcIikpO1xuICAgICAgICAgIGNhc2UgXCJFXCI6XG4gICAgICAgICAgICByZXR1cm4gc3MuY29uY2F0KHN0YWNrW2ldKTtcbiAgICAgICAgICBjYXNlIFwiZVwiOlxuICAgICAgICAgICAgcmV0dXJuIHNzLmNvbmNhdChzdGFja1tpXSk7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9XG4gIH1cbiAgcmV0dXJuIHR5cGUgPT0gXCJFXCIgPyBbXSA6IHN0YWNrO1xufVxuXG4vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vL1xuLy8gaW5kZW50ZXJcblxuZnVuY3Rpb24gaW5kZW50ZXIoc3RhdGUsIHRleHRBZnRlciwgY3gpIHtcbiAgdmFyIHQ7XG4gIHZhciB3b3JkQWZ0ZXIgPSB3b3JkYWZ0ZXIodGV4dEFmdGVyKTtcbiAgdmFyIGN1cnJUID0gcGVla1Rva2VuKHN0YXRlLCAxKTtcbiAgdmFyIHByZXZUID0gcGVla1Rva2VuKHN0YXRlLCAyKTtcbiAgaWYgKHN0YXRlLmluX3N0cmluZyB8fCBzdGF0ZS5pbl9hdG9tKSB7XG4gICAgcmV0dXJuIG51bGw7XG4gIH0gZWxzZSBpZiAoIXByZXZUKSB7XG4gICAgcmV0dXJuIDA7XG4gIH0gZWxzZSBpZiAoY3VyclQudG9rZW4gPT0gXCJ3aGVuXCIpIHtcbiAgICByZXR1cm4gY3VyclQuY29sdW1uICsgY3gudW5pdDtcbiAgfSBlbHNlIGlmICh3b3JkQWZ0ZXIgPT09IFwid2hlblwiICYmIHByZXZULnR5cGUgPT09IFwiZnVuY3Rpb25cIikge1xuICAgIHJldHVybiBwcmV2VC5pbmRlbnQgKyBjeC51bml0O1xuICB9IGVsc2UgaWYgKHdvcmRBZnRlciA9PT0gXCIoXCIgJiYgY3VyclQudG9rZW4gPT09IFwiZnVuXCIpIHtcbiAgICByZXR1cm4gY3VyclQuY29sdW1uICsgMztcbiAgfSBlbHNlIGlmICh3b3JkQWZ0ZXIgPT09IFwiY2F0Y2hcIiAmJiAodCA9IGdldFRva2VuKHN0YXRlLCBbXCJ0cnlcIl0pKSkge1xuICAgIHJldHVybiB0LmNvbHVtbjtcbiAgfSBlbHNlIGlmIChpc19tZW1iZXIod29yZEFmdGVyLCBbXCJlbmRcIiwgXCJhZnRlclwiLCBcIm9mXCJdKSkge1xuICAgIHQgPSBnZXRUb2tlbihzdGF0ZSwgW1wiYmVnaW5cIiwgXCJjYXNlXCIsIFwiZnVuXCIsIFwiaWZcIiwgXCJyZWNlaXZlXCIsIFwidHJ5XCJdKTtcbiAgICByZXR1cm4gdCA/IHQuY29sdW1uIDogbnVsbDtcbiAgfSBlbHNlIGlmIChpc19tZW1iZXIod29yZEFmdGVyLCBjbG9zZVBhcmVuV29yZHMpKSB7XG4gICAgdCA9IGdldFRva2VuKHN0YXRlLCBvcGVuUGFyZW5Xb3Jkcyk7XG4gICAgcmV0dXJuIHQgPyB0LmNvbHVtbiA6IG51bGw7XG4gIH0gZWxzZSBpZiAoaXNfbWVtYmVyKGN1cnJULnRva2VuLCBbXCIsXCIsIFwifFwiLCBcInx8XCJdKSB8fCBpc19tZW1iZXIod29yZEFmdGVyLCBbXCIsXCIsIFwifFwiLCBcInx8XCJdKSkge1xuICAgIHQgPSBwb3N0Y29tbWFUb2tlbihzdGF0ZSk7XG4gICAgcmV0dXJuIHQgPyB0LmNvbHVtbiArIHQudG9rZW4ubGVuZ3RoIDogY3gudW5pdDtcbiAgfSBlbHNlIGlmIChjdXJyVC50b2tlbiA9PSBcIi0+XCIpIHtcbiAgICBpZiAoaXNfbWVtYmVyKHByZXZULnRva2VuLCBbXCJyZWNlaXZlXCIsIFwiY2FzZVwiLCBcImlmXCIsIFwidHJ5XCJdKSkge1xuICAgICAgcmV0dXJuIHByZXZULmNvbHVtbiArIGN4LnVuaXQgKyBjeC51bml0O1xuICAgIH0gZWxzZSB7XG4gICAgICByZXR1cm4gcHJldlQuY29sdW1uICsgY3gudW5pdDtcbiAgICB9XG4gIH0gZWxzZSBpZiAoaXNfbWVtYmVyKGN1cnJULnRva2VuLCBvcGVuUGFyZW5Xb3JkcykpIHtcbiAgICByZXR1cm4gY3VyclQuY29sdW1uICsgY3VyclQudG9rZW4ubGVuZ3RoO1xuICB9IGVsc2Uge1xuICAgIHQgPSBkZWZhdWx0VG9rZW4oc3RhdGUpO1xuICAgIHJldHVybiB0cnV0aHkodCkgPyB0LmNvbHVtbiArIGN4LnVuaXQgOiAwO1xuICB9XG59XG5mdW5jdGlvbiB3b3JkYWZ0ZXIoc3RyKSB7XG4gIHZhciBtID0gc3RyLm1hdGNoKC8sfFthLXpdK3xcXH18XFxdfFxcKXw+PnxcXHwrfFxcKC8pO1xuICByZXR1cm4gdHJ1dGh5KG0pICYmIG0uaW5kZXggPT09IDAgPyBtWzBdIDogXCJcIjtcbn1cbmZ1bmN0aW9uIHBvc3Rjb21tYVRva2VuKHN0YXRlKSB7XG4gIHZhciBvYmpzID0gc3RhdGUudG9rZW5TdGFjay5zbGljZSgwLCAtMSk7XG4gIHZhciBpID0gZ2V0VG9rZW5JbmRleChvYmpzLCBcInR5cGVcIiwgW1wib3Blbl9wYXJlblwiXSk7XG4gIHJldHVybiB0cnV0aHkob2Jqc1tpXSkgPyBvYmpzW2ldIDogZmFsc2U7XG59XG5mdW5jdGlvbiBkZWZhdWx0VG9rZW4oc3RhdGUpIHtcbiAgdmFyIG9ianMgPSBzdGF0ZS50b2tlblN0YWNrO1xuICB2YXIgc3RvcCA9IGdldFRva2VuSW5kZXgob2JqcywgXCJ0eXBlXCIsIFtcIm9wZW5fcGFyZW5cIiwgXCJzZXBhcmF0b3JcIiwgXCJrZXl3b3JkXCJdKTtcbiAgdmFyIG9wZXIgPSBnZXRUb2tlbkluZGV4KG9ianMsIFwidHlwZVwiLCBbXCJvcGVyYXRvclwiXSk7XG4gIGlmICh0cnV0aHkoc3RvcCkgJiYgdHJ1dGh5KG9wZXIpICYmIHN0b3AgPCBvcGVyKSB7XG4gICAgcmV0dXJuIG9ianNbc3RvcCArIDFdO1xuICB9IGVsc2UgaWYgKHRydXRoeShzdG9wKSkge1xuICAgIHJldHVybiBvYmpzW3N0b3BdO1xuICB9IGVsc2Uge1xuICAgIHJldHVybiBmYWxzZTtcbiAgfVxufVxuZnVuY3Rpb24gZ2V0VG9rZW4oc3RhdGUsIHRva2Vucykge1xuICB2YXIgb2JqcyA9IHN0YXRlLnRva2VuU3RhY2s7XG4gIHZhciBpID0gZ2V0VG9rZW5JbmRleChvYmpzLCBcInRva2VuXCIsIHRva2Vucyk7XG4gIHJldHVybiB0cnV0aHkob2Jqc1tpXSkgPyBvYmpzW2ldIDogZmFsc2U7XG59XG5mdW5jdGlvbiBnZXRUb2tlbkluZGV4KG9ianMsIHByb3BuYW1lLCBwcm9wdmFscykge1xuICBmb3IgKHZhciBpID0gb2Jqcy5sZW5ndGggLSAxOyAtMSA8IGk7IGktLSkge1xuICAgIGlmIChpc19tZW1iZXIob2Jqc1tpXVtwcm9wbmFtZV0sIHByb3B2YWxzKSkge1xuICAgICAgcmV0dXJuIGk7XG4gICAgfVxuICB9XG4gIHJldHVybiBmYWxzZTtcbn1cbmZ1bmN0aW9uIHRydXRoeSh4KSB7XG4gIHJldHVybiB4ICE9PSBmYWxzZSAmJiB4ICE9IG51bGw7XG59XG5cbi8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vLy8vXG4vLyB0aGlzIG9iamVjdCBkZWZpbmVzIHRoZSBtb2RlXG5cbmV4cG9ydCBjb25zdCBlcmxhbmcgPSB7XG4gIG5hbWU6IFwiZXJsYW5nXCIsXG4gIHN0YXJ0U3RhdGUoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuU3RhY2s6IFtdLFxuICAgICAgaW5fc3RyaW5nOiBmYWxzZSxcbiAgICAgIGluX2F0b206IGZhbHNlXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IHRva2VuaXplcixcbiAgaW5kZW50OiBpbmRlbnRlcixcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgbGluZTogXCIlXCJcbiAgICB9XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==