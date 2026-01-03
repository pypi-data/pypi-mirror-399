"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[8036],{

/***/ 68036
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   verilog: () => (/* binding */ verilog)
/* harmony export */ });
/* unused harmony export tlv */
function mkVerilog(parserConfig) {
  var statementIndentUnit = parserConfig.statementIndentUnit,
    dontAlignCalls = parserConfig.dontAlignCalls,
    noIndentKeywords = parserConfig.noIndentKeywords || [],
    multiLineStrings = parserConfig.multiLineStrings,
    hooks = parserConfig.hooks || {};
  function words(str) {
    var obj = {},
      words = str.split(" ");
    for (var i = 0; i < words.length; ++i) obj[words[i]] = true;
    return obj;
  }

  /**
   * Keywords from IEEE 1800-2012
   */
  var keywords = words("accept_on alias always always_comb always_ff always_latch and assert assign assume automatic before begin bind " + "bins binsof bit break buf bufif0 bufif1 byte case casex casez cell chandle checker class clocking cmos config " + "const constraint context continue cover covergroup coverpoint cross deassign default defparam design disable " + "dist do edge else end endcase endchecker endclass endclocking endconfig endfunction endgenerate endgroup " + "endinterface endmodule endpackage endprimitive endprogram endproperty endspecify endsequence endtable endtask " + "enum event eventually expect export extends extern final first_match for force foreach forever fork forkjoin " + "function generate genvar global highz0 highz1 if iff ifnone ignore_bins illegal_bins implements implies import " + "incdir include initial inout input inside instance int integer interconnect interface intersect join join_any " + "join_none large let liblist library local localparam logic longint macromodule matches medium modport module " + "nand negedge nettype new nexttime nmos nor noshowcancelled not notif0 notif1 null or output package packed " + "parameter pmos posedge primitive priority program property protected pull0 pull1 pulldown pullup " + "pulsestyle_ondetect pulsestyle_onevent pure rand randc randcase randsequence rcmos real realtime ref reg " + "reject_on release repeat restrict return rnmos rpmos rtran rtranif0 rtranif1 s_always s_eventually s_nexttime " + "s_until s_until_with scalared sequence shortint shortreal showcancelled signed small soft solve specify " + "specparam static string strong strong0 strong1 struct super supply0 supply1 sync_accept_on sync_reject_on " + "table tagged task this throughout time timeprecision timeunit tran tranif0 tranif1 tri tri0 tri1 triand trior " + "trireg type typedef union unique unique0 unsigned until until_with untyped use uwire var vectored virtual void " + "wait wait_order wand weak weak0 weak1 while wildcard wire with within wor xnor xor");

  /** Operators from IEEE 1800-2012
      unary_operator ::=
      + | - | ! | ~ | & | ~& | | | ~| | ^ | ~^ | ^~
      binary_operator ::=
      + | - | * | / | % | == | != | === | !== | ==? | !=? | && | || | **
      | < | <= | > | >= | & | | | ^ | ^~ | ~^ | >> | << | >>> | <<<
      | -> | <->
      inc_or_dec_operator ::= ++ | --
      unary_module_path_operator ::=
      ! | ~ | & | ~& | | | ~| | ^ | ~^ | ^~
      binary_module_path_operator ::=
      == | != | && | || | & | | | ^ | ^~ | ~^
  */
  var isOperatorChar = /[\+\-\*\/!~&|^%=?:]/;
  var isBracketChar = /[\[\]{}()]/;
  var unsignedNumber = /\d[0-9_]*/;
  var decimalLiteral = /\d*\s*'s?d\s*\d[0-9_]*/i;
  var binaryLiteral = /\d*\s*'s?b\s*[xz01][xz01_]*/i;
  var octLiteral = /\d*\s*'s?o\s*[xz0-7][xz0-7_]*/i;
  var hexLiteral = /\d*\s*'s?h\s*[0-9a-fxz?][0-9a-fxz?_]*/i;
  var realLiteral = /(\d[\d_]*(\.\d[\d_]*)?E-?[\d_]+)|(\d[\d_]*\.\d[\d_]*)/i;
  var closingBracketOrWord = /^((\w+)|[)}\]])/;
  var closingBracket = /[)}\]]/;
  var curPunc;
  var curKeyword;

  // Block openings which are closed by a matching keyword in the form of ("end" + keyword)
  // E.g. "task" => "endtask"
  var blockKeywords = words("case checker class clocking config function generate interface module package " + "primitive program property specify sequence table task");

  // Opening/closing pairs
  var openClose = {};
  for (var keyword in blockKeywords) {
    openClose[keyword] = "end" + keyword;
  }
  openClose["begin"] = "end";
  openClose["casex"] = "endcase";
  openClose["casez"] = "endcase";
  openClose["do"] = "while";
  openClose["fork"] = "join;join_any;join_none";
  openClose["covergroup"] = "endgroup";
  for (var i in noIndentKeywords) {
    var keyword = noIndentKeywords[i];
    if (openClose[keyword]) {
      openClose[keyword] = undefined;
    }
  }

  // Keywords which open statements that are ended with a semi-colon
  var statementKeywords = words("always always_comb always_ff always_latch assert assign assume else export for foreach forever if import initial repeat while");
  function tokenBase(stream, state) {
    var ch = stream.peek(),
      style;
    if (hooks[ch] && (style = hooks[ch](stream, state)) != false) return style;
    if (hooks.tokenBase && (style = hooks.tokenBase(stream, state)) != false) return style;
    if (/[,;:\.]/.test(ch)) {
      curPunc = stream.next();
      return null;
    }
    if (isBracketChar.test(ch)) {
      curPunc = stream.next();
      return "bracket";
    }
    // Macros (tick-defines)
    if (ch == '`') {
      stream.next();
      if (stream.eatWhile(/[\w\$_]/)) {
        return "def";
      } else {
        return null;
      }
    }
    // System calls
    if (ch == '$') {
      stream.next();
      if (stream.eatWhile(/[\w\$_]/)) {
        return "meta";
      } else {
        return null;
      }
    }
    // Time literals
    if (ch == '#') {
      stream.next();
      stream.eatWhile(/[\d_.]/);
      return "def";
    }
    // Strings
    if (ch == '"') {
      stream.next();
      state.tokenize = tokenString(ch);
      return state.tokenize(stream, state);
    }
    // Comments
    if (ch == "/") {
      stream.next();
      if (stream.eat("*")) {
        state.tokenize = tokenComment;
        return tokenComment(stream, state);
      }
      if (stream.eat("/")) {
        stream.skipToEnd();
        return "comment";
      }
      stream.backUp(1);
    }

    // Numeric literals
    if (stream.match(realLiteral) || stream.match(decimalLiteral) || stream.match(binaryLiteral) || stream.match(octLiteral) || stream.match(hexLiteral) || stream.match(unsignedNumber) || stream.match(realLiteral)) {
      return "number";
    }

    // Operators
    if (stream.eatWhile(isOperatorChar)) {
      return "meta";
    }

    // Keywords / plain variables
    if (stream.eatWhile(/[\w\$_]/)) {
      var cur = stream.current();
      if (keywords[cur]) {
        if (openClose[cur]) {
          curPunc = "newblock";
        }
        if (statementKeywords[cur]) {
          curPunc = "newstatement";
        }
        curKeyword = cur;
        return "keyword";
      }
      return "variable";
    }
    stream.next();
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
      if (end || !(escaped || multiLineStrings)) state.tokenize = tokenBase;
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
    var indent = state.indented;
    var c = new Context(indent, col, type, null, state.context);
    return state.context = c;
  }
  function popContext(state) {
    var t = state.context.type;
    if (t == ")" || t == "]" || t == "}") {
      state.indented = state.context.indented;
    }
    return state.context = state.context.prev;
  }
  function isClosing(text, contextClosing) {
    if (text == contextClosing) {
      return true;
    } else {
      // contextClosing may be multiple keywords separated by ;
      var closingKeywords = contextClosing.split(";");
      for (var i in closingKeywords) {
        if (text == closingKeywords[i]) {
          return true;
        }
      }
      return false;
    }
  }
  function buildElectricInputRegEx() {
    // Reindentation should occur on any bracket char: {}()[]
    // or on a match of any of the block closing keywords, at
    // the end of a line
    var allClosings = [];
    for (var i in openClose) {
      if (openClose[i]) {
        var closings = openClose[i].split(";");
        for (var j in closings) {
          allClosings.push(closings[j]);
        }
      }
    }
    var re = new RegExp("[{}()\\[\\]]|(" + allClosings.join("|") + ")$");
    return re;
  }

  // Interface
  return {
    name: "verilog",
    startState: function (indentUnit) {
      var state = {
        tokenize: null,
        context: new Context(-indentUnit, 0, "top", false),
        indented: 0,
        startOfLine: true
      };
      if (hooks.startState) hooks.startState(state);
      return state;
    },
    token: function (stream, state) {
      var ctx = state.context;
      if (stream.sol()) {
        if (ctx.align == null) ctx.align = false;
        state.indented = stream.indentation();
        state.startOfLine = true;
      }
      if (hooks.token) {
        // Call hook, with an optional return value of a style to override verilog styling.
        var style = hooks.token(stream, state);
        if (style !== undefined) {
          return style;
        }
      }
      if (stream.eatSpace()) return null;
      curPunc = null;
      curKeyword = null;
      var style = (state.tokenize || tokenBase)(stream, state);
      if (style == "comment" || style == "meta" || style == "variable") return style;
      if (ctx.align == null) ctx.align = true;
      if (curPunc == ctx.type) {
        popContext(state);
      } else if (curPunc == ";" && ctx.type == "statement" || ctx.type && isClosing(curKeyword, ctx.type)) {
        ctx = popContext(state);
        while (ctx && ctx.type == "statement") ctx = popContext(state);
      } else if (curPunc == "{") {
        pushContext(state, stream.column(), "}");
      } else if (curPunc == "[") {
        pushContext(state, stream.column(), "]");
      } else if (curPunc == "(") {
        pushContext(state, stream.column(), ")");
      } else if (ctx && ctx.type == "endcase" && curPunc == ":") {
        pushContext(state, stream.column(), "statement");
      } else if (curPunc == "newstatement") {
        pushContext(state, stream.column(), "statement");
      } else if (curPunc == "newblock") {
        if (curKeyword == "function" && ctx && (ctx.type == "statement" || ctx.type == "endgroup")) {
          // The 'function' keyword can appear in some other contexts where it actually does not
          // indicate a function (import/export DPI and covergroup definitions).
          // Do nothing in this case
        } else if (curKeyword == "task" && ctx && ctx.type == "statement") {
          // Same thing for task
        } else {
          var close = openClose[curKeyword];
          pushContext(state, stream.column(), close);
        }
      }
      state.startOfLine = false;
      return style;
    },
    indent: function (state, textAfter, cx) {
      if (state.tokenize != tokenBase && state.tokenize != null) return null;
      if (hooks.indent) {
        var fromHook = hooks.indent(state);
        if (fromHook >= 0) return fromHook;
      }
      var ctx = state.context,
        firstChar = textAfter && textAfter.charAt(0);
      if (ctx.type == "statement" && firstChar == "}") ctx = ctx.prev;
      var closing = false;
      var possibleClosing = textAfter.match(closingBracketOrWord);
      if (possibleClosing) closing = isClosing(possibleClosing[0], ctx.type);
      if (ctx.type == "statement") return ctx.indented + (firstChar == "{" ? 0 : statementIndentUnit || cx.unit);else if (closingBracket.test(ctx.type) && ctx.align && !dontAlignCalls) return ctx.column + (closing ? 0 : 1);else if (ctx.type == ")" && !closing) return ctx.indented + (statementIndentUnit || cx.unit);else return ctx.indented + (closing ? 0 : cx.unit);
    },
    languageData: {
      indentOnInput: buildElectricInputRegEx(),
      commentTokens: {
        line: "//",
        block: {
          open: "/*",
          close: "*/"
        }
      }
    }
  };
}
;
const verilog = mkVerilog({});

// TL-Verilog mode.
// See tl-x.org for language spec.
// See the mode in action at makerchip.com.
// Contact: steve.hoover@redwoodeda.com

// TLV Identifier prefixes.
// Note that sign is not treated separately, so "+/-" versions of numeric identifiers
// are included.
var tlvIdentifierStyle = {
  "|": "link",
  ">": "property",
  // Should condition this off for > TLV 1c.
  "$": "variable",
  "$$": "variable",
  "?$": "qualifier",
  "?*": "qualifier",
  "-": "contentSeparator",
  "/": "property",
  "/-": "property",
  "@": "variableName.special",
  "@-": "variableName.special",
  "@++": "variableName.special",
  "@+=": "variableName.special",
  "@+=-": "variableName.special",
  "@--": "variableName.special",
  "@-=": "variableName.special",
  "%+": "tag",
  "%-": "tag",
  "%": "tag",
  ">>": "tag",
  "<<": "tag",
  "<>": "tag",
  "#": "tag",
  // Need to choose a style for this.
  "^": "attribute",
  "^^": "attribute",
  "^!": "attribute",
  "*": "variable",
  "**": "variable",
  "\\": "keyword",
  "\"": "comment"
};

// Lines starting with these characters define scope (result in indentation).
var tlvScopePrefixChars = {
  "/": "beh-hier",
  ">": "beh-hier",
  "-": "phys-hier",
  "|": "pipe",
  "?": "when",
  "@": "stage",
  "\\": "keyword"
};
var tlvIndentUnit = 3;
var tlvTrackStatements = false;
var tlvIdentMatch = /^([~!@#\$%\^&\*-\+=\?\/\\\|'"<>]+)([\d\w_]*)/; // Matches an identifier.
// Note that ':' is excluded, because of it's use in [:].
var tlvLineIndentationMatch = /^[! ] */;
var tlvCommentMatch = /^\/[\/\*]/;
const tlv = mkVerilog({
  hooks: {
    electricInput: false,
    // Return undefined for verilog tokenizing, or style for TLV token (null not used).
    // Standard CM styles are used for most formatting, but some TL-Verilog-specific highlighting
    // can be enabled with the definition of cm-tlv-* styles, including highlighting for:
    //   - M4 tokens
    //   - TLV scope indentation
    //   - Statement delimitation (enabled by tlvTrackStatements)
    token: function (stream, state) {
      var style = undefined;
      var match; // Return value of pattern matches.

      // Set highlighting mode based on code region (TLV or SV).
      if (stream.sol() && !state.tlvInBlockComment) {
        // Process region.
        if (stream.peek() == '\\') {
          style = "def";
          stream.skipToEnd();
          if (stream.string.match(/\\SV/)) {
            state.tlvCodeActive = false;
          } else if (stream.string.match(/\\TLV/)) {
            state.tlvCodeActive = true;
          }
        }
        // Correct indentation in the face of a line prefix char.
        if (state.tlvCodeActive && stream.pos == 0 && state.indented == 0 && (match = stream.match(tlvLineIndentationMatch, false))) {
          state.indented = match[0].length;
        }

        // Compute indentation state:
        //   o Auto indentation on next line
        //   o Indentation scope styles
        var indented = state.indented;
        var depth = indented / tlvIndentUnit;
        if (depth <= state.tlvIndentationStyle.length) {
          // not deeper than current scope

          var blankline = stream.string.length == indented;
          var chPos = depth * tlvIndentUnit;
          if (chPos < stream.string.length) {
            var bodyString = stream.string.slice(chPos);
            var ch = bodyString[0];
            if (tlvScopePrefixChars[ch] && (match = bodyString.match(tlvIdentMatch)) && tlvIdentifierStyle[match[1]]) {
              // This line begins scope.
              // Next line gets indented one level.
              indented += tlvIndentUnit;
              // Style the next level of indentation (except non-region keyword identifiers,
              //   which are statements themselves)
              if (!(ch == "\\" && chPos > 0)) {
                state.tlvIndentationStyle[depth] = tlvScopePrefixChars[ch];
                if (tlvTrackStatements) {
                  state.statementComment = false;
                }
                depth++;
              }
            }
          }
          // Clear out deeper indentation levels unless line is blank.
          if (!blankline) {
            while (state.tlvIndentationStyle.length > depth) {
              state.tlvIndentationStyle.pop();
            }
          }
        }
        // Set next level of indentation.
        state.tlvNextIndent = indented;
      }
      if (state.tlvCodeActive) {
        // Highlight as TLV.

        var beginStatement = false;
        if (tlvTrackStatements) {
          // This starts a statement if the position is at the scope level
          // and we're not within a statement leading comment.
          beginStatement = stream.peek() != " " &&
          // not a space
          style === undefined &&
          // not a region identifier
          !state.tlvInBlockComment &&
          // not in block comment
          //!stream.match(tlvCommentMatch, false) && // not comment start
          stream.column() == state.tlvIndentationStyle.length * tlvIndentUnit; // at scope level
          if (beginStatement) {
            if (state.statementComment) {
              // statement already started by comment
              beginStatement = false;
            }
            state.statementComment = stream.match(tlvCommentMatch, false); // comment start
          }
        }
        var match;
        if (style !== undefined) {} else if (state.tlvInBlockComment) {
          // In a block comment.
          if (stream.match(/^.*?\*\//)) {
            // Exit block comment.
            state.tlvInBlockComment = false;
            if (tlvTrackStatements && !stream.eol()) {
              // Anything after comment is assumed to be real statement content.
              state.statementComment = false;
            }
          } else {
            stream.skipToEnd();
          }
          style = "comment";
        } else if ((match = stream.match(tlvCommentMatch)) && !state.tlvInBlockComment) {
          // Start comment.
          if (match[0] == "//") {
            // Line comment.
            stream.skipToEnd();
          } else {
            // Block comment.
            state.tlvInBlockComment = true;
          }
          style = "comment";
        } else if (match = stream.match(tlvIdentMatch)) {
          // looks like an identifier (or identifier prefix)
          var prefix = match[1];
          var mnemonic = match[2];
          if (
          // is identifier prefix
          tlvIdentifierStyle.hasOwnProperty(prefix) && (
          // has mnemonic or we're at the end of the line (maybe it hasn't been typed yet)
          mnemonic.length > 0 || stream.eol())) {
            style = tlvIdentifierStyle[prefix];
          } else {
            // Just swallow one character and try again.
            // This enables subsequent identifier match with preceding symbol character, which
            //   is legal within a statement.  (Eg, !$reset).  It also enables detection of
            //   comment start with preceding symbols.
            stream.backUp(stream.current().length - 1);
          }
        } else if (stream.match(/^\t+/)) {
          // Highlight tabs, which are illegal.
          style = "invalid";
        } else if (stream.match(/^[\[\]{}\(\);\:]+/)) {
          // [:], (), {}, ;.
          style = "meta";
        } else if (match = stream.match(/^[mM]4([\+_])?[\w\d_]*/)) {
          // m4 pre proc
          style = match[1] == "+" ? "keyword.special" : "keyword";
        } else if (stream.match(/^ +/)) {
          // Skip over spaces.
          if (stream.eol()) {
            // Trailing spaces.
            style = "error";
          }
        } else if (stream.match(/^[\w\d_]+/)) {
          // alpha-numeric token.
          style = "number";
        } else {
          // Eat the next char w/ no formatting.
          stream.next();
        }
      } else {
        if (stream.match(/^[mM]4([\w\d_]*)/)) {
          // m4 pre proc
          style = "keyword";
        }
      }
      return style;
    },
    indent: function (state) {
      return state.tlvCodeActive == true ? state.tlvNextIndent : -1;
    },
    startState: function (state) {
      state.tlvIndentationStyle = []; // Styles to use for each level of indentation.
      state.tlvCodeActive = true; // True when we're in a TLV region (and at beginning of file).
      state.tlvNextIndent = -1; // The number of spaces to autoindent the next line if tlvCodeActive.
      state.tlvInBlockComment = false; // True inside /**/ comment.
      if (tlvTrackStatements) {
        state.statementComment = false; // True inside a statement's header comment.
      }
    }
  }
});

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiODAzNi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7O0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS92ZXJpbG9nLmpzIl0sInNvdXJjZXNDb250ZW50IjpbImZ1bmN0aW9uIG1rVmVyaWxvZyhwYXJzZXJDb25maWcpIHtcbiAgdmFyIHN0YXRlbWVudEluZGVudFVuaXQgPSBwYXJzZXJDb25maWcuc3RhdGVtZW50SW5kZW50VW5pdCxcbiAgICBkb250QWxpZ25DYWxscyA9IHBhcnNlckNvbmZpZy5kb250QWxpZ25DYWxscyxcbiAgICBub0luZGVudEtleXdvcmRzID0gcGFyc2VyQ29uZmlnLm5vSW5kZW50S2V5d29yZHMgfHwgW10sXG4gICAgbXVsdGlMaW5lU3RyaW5ncyA9IHBhcnNlckNvbmZpZy5tdWx0aUxpbmVTdHJpbmdzLFxuICAgIGhvb2tzID0gcGFyc2VyQ29uZmlnLmhvb2tzIHx8IHt9O1xuICBmdW5jdGlvbiB3b3JkcyhzdHIpIHtcbiAgICB2YXIgb2JqID0ge30sXG4gICAgICB3b3JkcyA9IHN0ci5zcGxpdChcIiBcIik7XG4gICAgZm9yICh2YXIgaSA9IDA7IGkgPCB3b3Jkcy5sZW5ndGg7ICsraSkgb2JqW3dvcmRzW2ldXSA9IHRydWU7XG4gICAgcmV0dXJuIG9iajtcbiAgfVxuXG4gIC8qKlxuICAgKiBLZXl3b3JkcyBmcm9tIElFRUUgMTgwMC0yMDEyXG4gICAqL1xuICB2YXIga2V5d29yZHMgPSB3b3JkcyhcImFjY2VwdF9vbiBhbGlhcyBhbHdheXMgYWx3YXlzX2NvbWIgYWx3YXlzX2ZmIGFsd2F5c19sYXRjaCBhbmQgYXNzZXJ0IGFzc2lnbiBhc3N1bWUgYXV0b21hdGljIGJlZm9yZSBiZWdpbiBiaW5kIFwiICsgXCJiaW5zIGJpbnNvZiBiaXQgYnJlYWsgYnVmIGJ1ZmlmMCBidWZpZjEgYnl0ZSBjYXNlIGNhc2V4IGNhc2V6IGNlbGwgY2hhbmRsZSBjaGVja2VyIGNsYXNzIGNsb2NraW5nIGNtb3MgY29uZmlnIFwiICsgXCJjb25zdCBjb25zdHJhaW50IGNvbnRleHQgY29udGludWUgY292ZXIgY292ZXJncm91cCBjb3ZlcnBvaW50IGNyb3NzIGRlYXNzaWduIGRlZmF1bHQgZGVmcGFyYW0gZGVzaWduIGRpc2FibGUgXCIgKyBcImRpc3QgZG8gZWRnZSBlbHNlIGVuZCBlbmRjYXNlIGVuZGNoZWNrZXIgZW5kY2xhc3MgZW5kY2xvY2tpbmcgZW5kY29uZmlnIGVuZGZ1bmN0aW9uIGVuZGdlbmVyYXRlIGVuZGdyb3VwIFwiICsgXCJlbmRpbnRlcmZhY2UgZW5kbW9kdWxlIGVuZHBhY2thZ2UgZW5kcHJpbWl0aXZlIGVuZHByb2dyYW0gZW5kcHJvcGVydHkgZW5kc3BlY2lmeSBlbmRzZXF1ZW5jZSBlbmR0YWJsZSBlbmR0YXNrIFwiICsgXCJlbnVtIGV2ZW50IGV2ZW50dWFsbHkgZXhwZWN0IGV4cG9ydCBleHRlbmRzIGV4dGVybiBmaW5hbCBmaXJzdF9tYXRjaCBmb3IgZm9yY2UgZm9yZWFjaCBmb3JldmVyIGZvcmsgZm9ya2pvaW4gXCIgKyBcImZ1bmN0aW9uIGdlbmVyYXRlIGdlbnZhciBnbG9iYWwgaGlnaHowIGhpZ2h6MSBpZiBpZmYgaWZub25lIGlnbm9yZV9iaW5zIGlsbGVnYWxfYmlucyBpbXBsZW1lbnRzIGltcGxpZXMgaW1wb3J0IFwiICsgXCJpbmNkaXIgaW5jbHVkZSBpbml0aWFsIGlub3V0IGlucHV0IGluc2lkZSBpbnN0YW5jZSBpbnQgaW50ZWdlciBpbnRlcmNvbm5lY3QgaW50ZXJmYWNlIGludGVyc2VjdCBqb2luIGpvaW5fYW55IFwiICsgXCJqb2luX25vbmUgbGFyZ2UgbGV0IGxpYmxpc3QgbGlicmFyeSBsb2NhbCBsb2NhbHBhcmFtIGxvZ2ljIGxvbmdpbnQgbWFjcm9tb2R1bGUgbWF0Y2hlcyBtZWRpdW0gbW9kcG9ydCBtb2R1bGUgXCIgKyBcIm5hbmQgbmVnZWRnZSBuZXR0eXBlIG5ldyBuZXh0dGltZSBubW9zIG5vciBub3Nob3djYW5jZWxsZWQgbm90IG5vdGlmMCBub3RpZjEgbnVsbCBvciBvdXRwdXQgcGFja2FnZSBwYWNrZWQgXCIgKyBcInBhcmFtZXRlciBwbW9zIHBvc2VkZ2UgcHJpbWl0aXZlIHByaW9yaXR5IHByb2dyYW0gcHJvcGVydHkgcHJvdGVjdGVkIHB1bGwwIHB1bGwxIHB1bGxkb3duIHB1bGx1cCBcIiArIFwicHVsc2VzdHlsZV9vbmRldGVjdCBwdWxzZXN0eWxlX29uZXZlbnQgcHVyZSByYW5kIHJhbmRjIHJhbmRjYXNlIHJhbmRzZXF1ZW5jZSByY21vcyByZWFsIHJlYWx0aW1lIHJlZiByZWcgXCIgKyBcInJlamVjdF9vbiByZWxlYXNlIHJlcGVhdCByZXN0cmljdCByZXR1cm4gcm5tb3MgcnBtb3MgcnRyYW4gcnRyYW5pZjAgcnRyYW5pZjEgc19hbHdheXMgc19ldmVudHVhbGx5IHNfbmV4dHRpbWUgXCIgKyBcInNfdW50aWwgc191bnRpbF93aXRoIHNjYWxhcmVkIHNlcXVlbmNlIHNob3J0aW50IHNob3J0cmVhbCBzaG93Y2FuY2VsbGVkIHNpZ25lZCBzbWFsbCBzb2Z0IHNvbHZlIHNwZWNpZnkgXCIgKyBcInNwZWNwYXJhbSBzdGF0aWMgc3RyaW5nIHN0cm9uZyBzdHJvbmcwIHN0cm9uZzEgc3RydWN0IHN1cGVyIHN1cHBseTAgc3VwcGx5MSBzeW5jX2FjY2VwdF9vbiBzeW5jX3JlamVjdF9vbiBcIiArIFwidGFibGUgdGFnZ2VkIHRhc2sgdGhpcyB0aHJvdWdob3V0IHRpbWUgdGltZXByZWNpc2lvbiB0aW1ldW5pdCB0cmFuIHRyYW5pZjAgdHJhbmlmMSB0cmkgdHJpMCB0cmkxIHRyaWFuZCB0cmlvciBcIiArIFwidHJpcmVnIHR5cGUgdHlwZWRlZiB1bmlvbiB1bmlxdWUgdW5pcXVlMCB1bnNpZ25lZCB1bnRpbCB1bnRpbF93aXRoIHVudHlwZWQgdXNlIHV3aXJlIHZhciB2ZWN0b3JlZCB2aXJ0dWFsIHZvaWQgXCIgKyBcIndhaXQgd2FpdF9vcmRlciB3YW5kIHdlYWsgd2VhazAgd2VhazEgd2hpbGUgd2lsZGNhcmQgd2lyZSB3aXRoIHdpdGhpbiB3b3IgeG5vciB4b3JcIik7XG5cbiAgLyoqIE9wZXJhdG9ycyBmcm9tIElFRUUgMTgwMC0yMDEyXG4gICAgICB1bmFyeV9vcGVyYXRvciA6Oj1cbiAgICAgICsgfCAtIHwgISB8IH4gfCAmIHwgfiYgfCB8IHwgfnwgfCBeIHwgfl4gfCBeflxuICAgICAgYmluYXJ5X29wZXJhdG9yIDo6PVxuICAgICAgKyB8IC0gfCAqIHwgLyB8ICUgfCA9PSB8ICE9IHwgPT09IHwgIT09IHwgPT0/IHwgIT0/IHwgJiYgfCB8fCB8ICoqXG4gICAgICB8IDwgfCA8PSB8ID4gfCA+PSB8ICYgfCB8IHwgXiB8IF5+IHwgfl4gfCA+PiB8IDw8IHwgPj4+IHwgPDw8XG4gICAgICB8IC0+IHwgPC0+XG4gICAgICBpbmNfb3JfZGVjX29wZXJhdG9yIDo6PSArKyB8IC0tXG4gICAgICB1bmFyeV9tb2R1bGVfcGF0aF9vcGVyYXRvciA6Oj1cbiAgICAgICEgfCB+IHwgJiB8IH4mIHwgfCB8IH58IHwgXiB8IH5eIHwgXn5cbiAgICAgIGJpbmFyeV9tb2R1bGVfcGF0aF9vcGVyYXRvciA6Oj1cbiAgICAgID09IHwgIT0gfCAmJiB8IHx8IHwgJiB8IHwgfCBeIHwgXn4gfCB+XlxuICAqL1xuICB2YXIgaXNPcGVyYXRvckNoYXIgPSAvW1xcK1xcLVxcKlxcLyF+JnxeJT0/Ol0vO1xuICB2YXIgaXNCcmFja2V0Q2hhciA9IC9bXFxbXFxde30oKV0vO1xuICB2YXIgdW5zaWduZWROdW1iZXIgPSAvXFxkWzAtOV9dKi87XG4gIHZhciBkZWNpbWFsTGl0ZXJhbCA9IC9cXGQqXFxzKidzP2RcXHMqXFxkWzAtOV9dKi9pO1xuICB2YXIgYmluYXJ5TGl0ZXJhbCA9IC9cXGQqXFxzKidzP2JcXHMqW3h6MDFdW3h6MDFfXSovaTtcbiAgdmFyIG9jdExpdGVyYWwgPSAvXFxkKlxccyoncz9vXFxzKlt4ejAtN11beHowLTdfXSovaTtcbiAgdmFyIGhleExpdGVyYWwgPSAvXFxkKlxccyoncz9oXFxzKlswLTlhLWZ4ej9dWzAtOWEtZnh6P19dKi9pO1xuICB2YXIgcmVhbExpdGVyYWwgPSAvKFxcZFtcXGRfXSooXFwuXFxkW1xcZF9dKik/RS0/W1xcZF9dKyl8KFxcZFtcXGRfXSpcXC5cXGRbXFxkX10qKS9pO1xuICB2YXIgY2xvc2luZ0JyYWNrZXRPcldvcmQgPSAvXigoXFx3Kyl8Wyl9XFxdXSkvO1xuICB2YXIgY2xvc2luZ0JyYWNrZXQgPSAvWyl9XFxdXS87XG4gIHZhciBjdXJQdW5jO1xuICB2YXIgY3VyS2V5d29yZDtcblxuICAvLyBCbG9jayBvcGVuaW5ncyB3aGljaCBhcmUgY2xvc2VkIGJ5IGEgbWF0Y2hpbmcga2V5d29yZCBpbiB0aGUgZm9ybSBvZiAoXCJlbmRcIiArIGtleXdvcmQpXG4gIC8vIEUuZy4gXCJ0YXNrXCIgPT4gXCJlbmR0YXNrXCJcbiAgdmFyIGJsb2NrS2V5d29yZHMgPSB3b3JkcyhcImNhc2UgY2hlY2tlciBjbGFzcyBjbG9ja2luZyBjb25maWcgZnVuY3Rpb24gZ2VuZXJhdGUgaW50ZXJmYWNlIG1vZHVsZSBwYWNrYWdlIFwiICsgXCJwcmltaXRpdmUgcHJvZ3JhbSBwcm9wZXJ0eSBzcGVjaWZ5IHNlcXVlbmNlIHRhYmxlIHRhc2tcIik7XG5cbiAgLy8gT3BlbmluZy9jbG9zaW5nIHBhaXJzXG4gIHZhciBvcGVuQ2xvc2UgPSB7fTtcbiAgZm9yICh2YXIga2V5d29yZCBpbiBibG9ja0tleXdvcmRzKSB7XG4gICAgb3BlbkNsb3NlW2tleXdvcmRdID0gXCJlbmRcIiArIGtleXdvcmQ7XG4gIH1cbiAgb3BlbkNsb3NlW1wiYmVnaW5cIl0gPSBcImVuZFwiO1xuICBvcGVuQ2xvc2VbXCJjYXNleFwiXSA9IFwiZW5kY2FzZVwiO1xuICBvcGVuQ2xvc2VbXCJjYXNlelwiXSA9IFwiZW5kY2FzZVwiO1xuICBvcGVuQ2xvc2VbXCJkb1wiXSA9IFwid2hpbGVcIjtcbiAgb3BlbkNsb3NlW1wiZm9ya1wiXSA9IFwiam9pbjtqb2luX2FueTtqb2luX25vbmVcIjtcbiAgb3BlbkNsb3NlW1wiY292ZXJncm91cFwiXSA9IFwiZW5kZ3JvdXBcIjtcbiAgZm9yICh2YXIgaSBpbiBub0luZGVudEtleXdvcmRzKSB7XG4gICAgdmFyIGtleXdvcmQgPSBub0luZGVudEtleXdvcmRzW2ldO1xuICAgIGlmIChvcGVuQ2xvc2Vba2V5d29yZF0pIHtcbiAgICAgIG9wZW5DbG9zZVtrZXl3b3JkXSA9IHVuZGVmaW5lZDtcbiAgICB9XG4gIH1cblxuICAvLyBLZXl3b3JkcyB3aGljaCBvcGVuIHN0YXRlbWVudHMgdGhhdCBhcmUgZW5kZWQgd2l0aCBhIHNlbWktY29sb25cbiAgdmFyIHN0YXRlbWVudEtleXdvcmRzID0gd29yZHMoXCJhbHdheXMgYWx3YXlzX2NvbWIgYWx3YXlzX2ZmIGFsd2F5c19sYXRjaCBhc3NlcnQgYXNzaWduIGFzc3VtZSBlbHNlIGV4cG9ydCBmb3IgZm9yZWFjaCBmb3JldmVyIGlmIGltcG9ydCBpbml0aWFsIHJlcGVhdCB3aGlsZVwiKTtcbiAgZnVuY3Rpb24gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgY2ggPSBzdHJlYW0ucGVlaygpLFxuICAgICAgc3R5bGU7XG4gICAgaWYgKGhvb2tzW2NoXSAmJiAoc3R5bGUgPSBob29rc1tjaF0oc3RyZWFtLCBzdGF0ZSkpICE9IGZhbHNlKSByZXR1cm4gc3R5bGU7XG4gICAgaWYgKGhvb2tzLnRva2VuQmFzZSAmJiAoc3R5bGUgPSBob29rcy50b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSkpICE9IGZhbHNlKSByZXR1cm4gc3R5bGU7XG4gICAgaWYgKC9bLDs6XFwuXS8udGVzdChjaCkpIHtcbiAgICAgIGN1clB1bmMgPSBzdHJlYW0ubmV4dCgpO1xuICAgICAgcmV0dXJuIG51bGw7XG4gICAgfVxuICAgIGlmIChpc0JyYWNrZXRDaGFyLnRlc3QoY2gpKSB7XG4gICAgICBjdXJQdW5jID0gc3RyZWFtLm5leHQoKTtcbiAgICAgIHJldHVybiBcImJyYWNrZXRcIjtcbiAgICB9XG4gICAgLy8gTWFjcm9zICh0aWNrLWRlZmluZXMpXG4gICAgaWYgKGNoID09ICdgJykge1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIGlmIChzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXCRfXS8pKSB7XG4gICAgICAgIHJldHVybiBcImRlZlwiO1xuICAgICAgfSBlbHNlIHtcbiAgICAgICAgcmV0dXJuIG51bGw7XG4gICAgICB9XG4gICAgfVxuICAgIC8vIFN5c3RlbSBjYWxsc1xuICAgIGlmIChjaCA9PSAnJCcpIHtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICBpZiAoc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFwkX10vKSkge1xuICAgICAgICByZXR1cm4gXCJtZXRhXCI7XG4gICAgICB9IGVsc2Uge1xuICAgICAgICByZXR1cm4gbnVsbDtcbiAgICAgIH1cbiAgICB9XG4gICAgLy8gVGltZSBsaXRlcmFsc1xuICAgIGlmIChjaCA9PSAnIycpIHtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1tcXGRfLl0vKTtcbiAgICAgIHJldHVybiBcImRlZlwiO1xuICAgIH1cbiAgICAvLyBTdHJpbmdzXG4gICAgaWYgKGNoID09ICdcIicpIHtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuU3RyaW5nKGNoKTtcbiAgICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICB9XG4gICAgLy8gQ29tbWVudHNcbiAgICBpZiAoY2ggPT0gXCIvXCIpIHtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICBpZiAoc3RyZWFtLmVhdChcIipcIikpIHtcbiAgICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkNvbW1lbnQ7XG4gICAgICAgIHJldHVybiB0b2tlbkNvbW1lbnQoc3RyZWFtLCBzdGF0ZSk7XG4gICAgICB9XG4gICAgICBpZiAoc3RyZWFtLmVhdChcIi9cIikpIHtcbiAgICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgICB9XG4gICAgICBzdHJlYW0uYmFja1VwKDEpO1xuICAgIH1cblxuICAgIC8vIE51bWVyaWMgbGl0ZXJhbHNcbiAgICBpZiAoc3RyZWFtLm1hdGNoKHJlYWxMaXRlcmFsKSB8fCBzdHJlYW0ubWF0Y2goZGVjaW1hbExpdGVyYWwpIHx8IHN0cmVhbS5tYXRjaChiaW5hcnlMaXRlcmFsKSB8fCBzdHJlYW0ubWF0Y2gob2N0TGl0ZXJhbCkgfHwgc3RyZWFtLm1hdGNoKGhleExpdGVyYWwpIHx8IHN0cmVhbS5tYXRjaCh1bnNpZ25lZE51bWJlcikgfHwgc3RyZWFtLm1hdGNoKHJlYWxMaXRlcmFsKSkge1xuICAgICAgcmV0dXJuIFwibnVtYmVyXCI7XG4gICAgfVxuXG4gICAgLy8gT3BlcmF0b3JzXG4gICAgaWYgKHN0cmVhbS5lYXRXaGlsZShpc09wZXJhdG9yQ2hhcikpIHtcbiAgICAgIHJldHVybiBcIm1ldGFcIjtcbiAgICB9XG5cbiAgICAvLyBLZXl3b3JkcyAvIHBsYWluIHZhcmlhYmxlc1xuICAgIGlmIChzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXCRfXS8pKSB7XG4gICAgICB2YXIgY3VyID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgICAgIGlmIChrZXl3b3Jkc1tjdXJdKSB7XG4gICAgICAgIGlmIChvcGVuQ2xvc2VbY3VyXSkge1xuICAgICAgICAgIGN1clB1bmMgPSBcIm5ld2Jsb2NrXCI7XG4gICAgICAgIH1cbiAgICAgICAgaWYgKHN0YXRlbWVudEtleXdvcmRzW2N1cl0pIHtcbiAgICAgICAgICBjdXJQdW5jID0gXCJuZXdzdGF0ZW1lbnRcIjtcbiAgICAgICAgfVxuICAgICAgICBjdXJLZXl3b3JkID0gY3VyO1xuICAgICAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gICAgICB9XG4gICAgICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xuICAgIH1cbiAgICBzdHJlYW0ubmV4dCgpO1xuICAgIHJldHVybiBudWxsO1xuICB9XG4gIGZ1bmN0aW9uIHRva2VuU3RyaW5nKHF1b3RlKSB7XG4gICAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgICB2YXIgZXNjYXBlZCA9IGZhbHNlLFxuICAgICAgICBuZXh0LFxuICAgICAgICBlbmQgPSBmYWxzZTtcbiAgICAgIHdoaWxlICgobmV4dCA9IHN0cmVhbS5uZXh0KCkpICE9IG51bGwpIHtcbiAgICAgICAgaWYgKG5leHQgPT0gcXVvdGUgJiYgIWVzY2FwZWQpIHtcbiAgICAgICAgICBlbmQgPSB0cnVlO1xuICAgICAgICAgIGJyZWFrO1xuICAgICAgICB9XG4gICAgICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBuZXh0ID09IFwiXFxcXFwiO1xuICAgICAgfVxuICAgICAgaWYgKGVuZCB8fCAhKGVzY2FwZWQgfHwgbXVsdGlMaW5lU3RyaW5ncykpIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gICAgfTtcbiAgfVxuICBmdW5jdGlvbiB0b2tlbkNvbW1lbnQoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBtYXliZUVuZCA9IGZhbHNlLFxuICAgICAgY2g7XG4gICAgd2hpbGUgKGNoID0gc3RyZWFtLm5leHQoKSkge1xuICAgICAgaWYgKGNoID09IFwiL1wiICYmIG1heWJlRW5kKSB7XG4gICAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICAgIG1heWJlRW5kID0gY2ggPT0gXCIqXCI7XG4gICAgfVxuICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgfVxuICBmdW5jdGlvbiBDb250ZXh0KGluZGVudGVkLCBjb2x1bW4sIHR5cGUsIGFsaWduLCBwcmV2KSB7XG4gICAgdGhpcy5pbmRlbnRlZCA9IGluZGVudGVkO1xuICAgIHRoaXMuY29sdW1uID0gY29sdW1uO1xuICAgIHRoaXMudHlwZSA9IHR5cGU7XG4gICAgdGhpcy5hbGlnbiA9IGFsaWduO1xuICAgIHRoaXMucHJldiA9IHByZXY7XG4gIH1cbiAgZnVuY3Rpb24gcHVzaENvbnRleHQoc3RhdGUsIGNvbCwgdHlwZSkge1xuICAgIHZhciBpbmRlbnQgPSBzdGF0ZS5pbmRlbnRlZDtcbiAgICB2YXIgYyA9IG5ldyBDb250ZXh0KGluZGVudCwgY29sLCB0eXBlLCBudWxsLCBzdGF0ZS5jb250ZXh0KTtcbiAgICByZXR1cm4gc3RhdGUuY29udGV4dCA9IGM7XG4gIH1cbiAgZnVuY3Rpb24gcG9wQ29udGV4dChzdGF0ZSkge1xuICAgIHZhciB0ID0gc3RhdGUuY29udGV4dC50eXBlO1xuICAgIGlmICh0ID09IFwiKVwiIHx8IHQgPT0gXCJdXCIgfHwgdCA9PSBcIn1cIikge1xuICAgICAgc3RhdGUuaW5kZW50ZWQgPSBzdGF0ZS5jb250ZXh0LmluZGVudGVkO1xuICAgIH1cbiAgICByZXR1cm4gc3RhdGUuY29udGV4dCA9IHN0YXRlLmNvbnRleHQucHJldjtcbiAgfVxuICBmdW5jdGlvbiBpc0Nsb3NpbmcodGV4dCwgY29udGV4dENsb3NpbmcpIHtcbiAgICBpZiAodGV4dCA9PSBjb250ZXh0Q2xvc2luZykge1xuICAgICAgcmV0dXJuIHRydWU7XG4gICAgfSBlbHNlIHtcbiAgICAgIC8vIGNvbnRleHRDbG9zaW5nIG1heSBiZSBtdWx0aXBsZSBrZXl3b3JkcyBzZXBhcmF0ZWQgYnkgO1xuICAgICAgdmFyIGNsb3NpbmdLZXl3b3JkcyA9IGNvbnRleHRDbG9zaW5nLnNwbGl0KFwiO1wiKTtcbiAgICAgIGZvciAodmFyIGkgaW4gY2xvc2luZ0tleXdvcmRzKSB7XG4gICAgICAgIGlmICh0ZXh0ID09IGNsb3NpbmdLZXl3b3Jkc1tpXSkge1xuICAgICAgICAgIHJldHVybiB0cnVlO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgICByZXR1cm4gZmFsc2U7XG4gICAgfVxuICB9XG4gIGZ1bmN0aW9uIGJ1aWxkRWxlY3RyaWNJbnB1dFJlZ0V4KCkge1xuICAgIC8vIFJlaW5kZW50YXRpb24gc2hvdWxkIG9jY3VyIG9uIGFueSBicmFja2V0IGNoYXI6IHt9KClbXVxuICAgIC8vIG9yIG9uIGEgbWF0Y2ggb2YgYW55IG9mIHRoZSBibG9jayBjbG9zaW5nIGtleXdvcmRzLCBhdFxuICAgIC8vIHRoZSBlbmQgb2YgYSBsaW5lXG4gICAgdmFyIGFsbENsb3NpbmdzID0gW107XG4gICAgZm9yICh2YXIgaSBpbiBvcGVuQ2xvc2UpIHtcbiAgICAgIGlmIChvcGVuQ2xvc2VbaV0pIHtcbiAgICAgICAgdmFyIGNsb3NpbmdzID0gb3BlbkNsb3NlW2ldLnNwbGl0KFwiO1wiKTtcbiAgICAgICAgZm9yICh2YXIgaiBpbiBjbG9zaW5ncykge1xuICAgICAgICAgIGFsbENsb3NpbmdzLnB1c2goY2xvc2luZ3Nbal0pO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgfVxuICAgIHZhciByZSA9IG5ldyBSZWdFeHAoXCJbe30oKVxcXFxbXFxcXF1dfChcIiArIGFsbENsb3NpbmdzLmpvaW4oXCJ8XCIpICsgXCIpJFwiKTtcbiAgICByZXR1cm4gcmU7XG4gIH1cblxuICAvLyBJbnRlcmZhY2VcbiAgcmV0dXJuIHtcbiAgICBuYW1lOiBcInZlcmlsb2dcIixcbiAgICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoaW5kZW50VW5pdCkge1xuICAgICAgdmFyIHN0YXRlID0ge1xuICAgICAgICB0b2tlbml6ZTogbnVsbCxcbiAgICAgICAgY29udGV4dDogbmV3IENvbnRleHQoLWluZGVudFVuaXQsIDAsIFwidG9wXCIsIGZhbHNlKSxcbiAgICAgICAgaW5kZW50ZWQ6IDAsXG4gICAgICAgIHN0YXJ0T2ZMaW5lOiB0cnVlXG4gICAgICB9O1xuICAgICAgaWYgKGhvb2tzLnN0YXJ0U3RhdGUpIGhvb2tzLnN0YXJ0U3RhdGUoc3RhdGUpO1xuICAgICAgcmV0dXJuIHN0YXRlO1xuICAgIH0sXG4gICAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgICB2YXIgY3R4ID0gc3RhdGUuY29udGV4dDtcbiAgICAgIGlmIChzdHJlYW0uc29sKCkpIHtcbiAgICAgICAgaWYgKGN0eC5hbGlnbiA9PSBudWxsKSBjdHguYWxpZ24gPSBmYWxzZTtcbiAgICAgICAgc3RhdGUuaW5kZW50ZWQgPSBzdHJlYW0uaW5kZW50YXRpb24oKTtcbiAgICAgICAgc3RhdGUuc3RhcnRPZkxpbmUgPSB0cnVlO1xuICAgICAgfVxuICAgICAgaWYgKGhvb2tzLnRva2VuKSB7XG4gICAgICAgIC8vIENhbGwgaG9vaywgd2l0aCBhbiBvcHRpb25hbCByZXR1cm4gdmFsdWUgb2YgYSBzdHlsZSB0byBvdmVycmlkZSB2ZXJpbG9nIHN0eWxpbmcuXG4gICAgICAgIHZhciBzdHlsZSA9IGhvb2tzLnRva2VuKHN0cmVhbSwgc3RhdGUpO1xuICAgICAgICBpZiAoc3R5bGUgIT09IHVuZGVmaW5lZCkge1xuICAgICAgICAgIHJldHVybiBzdHlsZTtcbiAgICAgICAgfVxuICAgICAgfVxuICAgICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgICAgIGN1clB1bmMgPSBudWxsO1xuICAgICAgY3VyS2V5d29yZCA9IG51bGw7XG4gICAgICB2YXIgc3R5bGUgPSAoc3RhdGUudG9rZW5pemUgfHwgdG9rZW5CYXNlKShzdHJlYW0sIHN0YXRlKTtcbiAgICAgIGlmIChzdHlsZSA9PSBcImNvbW1lbnRcIiB8fCBzdHlsZSA9PSBcIm1ldGFcIiB8fCBzdHlsZSA9PSBcInZhcmlhYmxlXCIpIHJldHVybiBzdHlsZTtcbiAgICAgIGlmIChjdHguYWxpZ24gPT0gbnVsbCkgY3R4LmFsaWduID0gdHJ1ZTtcbiAgICAgIGlmIChjdXJQdW5jID09IGN0eC50eXBlKSB7XG4gICAgICAgIHBvcENvbnRleHQoc3RhdGUpO1xuICAgICAgfSBlbHNlIGlmIChjdXJQdW5jID09IFwiO1wiICYmIGN0eC50eXBlID09IFwic3RhdGVtZW50XCIgfHwgY3R4LnR5cGUgJiYgaXNDbG9zaW5nKGN1cktleXdvcmQsIGN0eC50eXBlKSkge1xuICAgICAgICBjdHggPSBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICAgICAgd2hpbGUgKGN0eCAmJiBjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiKSBjdHggPSBwb3BDb250ZXh0KHN0YXRlKTtcbiAgICAgIH0gZWxzZSBpZiAoY3VyUHVuYyA9PSBcIntcIikge1xuICAgICAgICBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLmNvbHVtbigpLCBcIn1cIik7XG4gICAgICB9IGVsc2UgaWYgKGN1clB1bmMgPT0gXCJbXCIpIHtcbiAgICAgICAgcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbS5jb2x1bW4oKSwgXCJdXCIpO1xuICAgICAgfSBlbHNlIGlmIChjdXJQdW5jID09IFwiKFwiKSB7XG4gICAgICAgIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0uY29sdW1uKCksIFwiKVwiKTtcbiAgICAgIH0gZWxzZSBpZiAoY3R4ICYmIGN0eC50eXBlID09IFwiZW5kY2FzZVwiICYmIGN1clB1bmMgPT0gXCI6XCIpIHtcbiAgICAgICAgcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbS5jb2x1bW4oKSwgXCJzdGF0ZW1lbnRcIik7XG4gICAgICB9IGVsc2UgaWYgKGN1clB1bmMgPT0gXCJuZXdzdGF0ZW1lbnRcIikge1xuICAgICAgICBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLmNvbHVtbigpLCBcInN0YXRlbWVudFwiKTtcbiAgICAgIH0gZWxzZSBpZiAoY3VyUHVuYyA9PSBcIm5ld2Jsb2NrXCIpIHtcbiAgICAgICAgaWYgKGN1cktleXdvcmQgPT0gXCJmdW5jdGlvblwiICYmIGN0eCAmJiAoY3R4LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIiB8fCBjdHgudHlwZSA9PSBcImVuZGdyb3VwXCIpKSB7XG4gICAgICAgICAgLy8gVGhlICdmdW5jdGlvbicga2V5d29yZCBjYW4gYXBwZWFyIGluIHNvbWUgb3RoZXIgY29udGV4dHMgd2hlcmUgaXQgYWN0dWFsbHkgZG9lcyBub3RcbiAgICAgICAgICAvLyBpbmRpY2F0ZSBhIGZ1bmN0aW9uIChpbXBvcnQvZXhwb3J0IERQSSBhbmQgY292ZXJncm91cCBkZWZpbml0aW9ucykuXG4gICAgICAgICAgLy8gRG8gbm90aGluZyBpbiB0aGlzIGNhc2VcbiAgICAgICAgfSBlbHNlIGlmIChjdXJLZXl3b3JkID09IFwidGFza1wiICYmIGN0eCAmJiBjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiKSB7XG4gICAgICAgICAgLy8gU2FtZSB0aGluZyBmb3IgdGFza1xuICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgIHZhciBjbG9zZSA9IG9wZW5DbG9zZVtjdXJLZXl3b3JkXTtcbiAgICAgICAgICBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLmNvbHVtbigpLCBjbG9zZSk7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICAgIHN0YXRlLnN0YXJ0T2ZMaW5lID0gZmFsc2U7XG4gICAgICByZXR1cm4gc3R5bGU7XG4gICAgfSxcbiAgICBpbmRlbnQ6IGZ1bmN0aW9uIChzdGF0ZSwgdGV4dEFmdGVyLCBjeCkge1xuICAgICAgaWYgKHN0YXRlLnRva2VuaXplICE9IHRva2VuQmFzZSAmJiBzdGF0ZS50b2tlbml6ZSAhPSBudWxsKSByZXR1cm4gbnVsbDtcbiAgICAgIGlmIChob29rcy5pbmRlbnQpIHtcbiAgICAgICAgdmFyIGZyb21Ib29rID0gaG9va3MuaW5kZW50KHN0YXRlKTtcbiAgICAgICAgaWYgKGZyb21Ib29rID49IDApIHJldHVybiBmcm9tSG9vaztcbiAgICAgIH1cbiAgICAgIHZhciBjdHggPSBzdGF0ZS5jb250ZXh0LFxuICAgICAgICBmaXJzdENoYXIgPSB0ZXh0QWZ0ZXIgJiYgdGV4dEFmdGVyLmNoYXJBdCgwKTtcbiAgICAgIGlmIChjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiICYmIGZpcnN0Q2hhciA9PSBcIn1cIikgY3R4ID0gY3R4LnByZXY7XG4gICAgICB2YXIgY2xvc2luZyA9IGZhbHNlO1xuICAgICAgdmFyIHBvc3NpYmxlQ2xvc2luZyA9IHRleHRBZnRlci5tYXRjaChjbG9zaW5nQnJhY2tldE9yV29yZCk7XG4gICAgICBpZiAocG9zc2libGVDbG9zaW5nKSBjbG9zaW5nID0gaXNDbG9zaW5nKHBvc3NpYmxlQ2xvc2luZ1swXSwgY3R4LnR5cGUpO1xuICAgICAgaWYgKGN0eC50eXBlID09IFwic3RhdGVtZW50XCIpIHJldHVybiBjdHguaW5kZW50ZWQgKyAoZmlyc3RDaGFyID09IFwie1wiID8gMCA6IHN0YXRlbWVudEluZGVudFVuaXQgfHwgY3gudW5pdCk7ZWxzZSBpZiAoY2xvc2luZ0JyYWNrZXQudGVzdChjdHgudHlwZSkgJiYgY3R4LmFsaWduICYmICFkb250QWxpZ25DYWxscykgcmV0dXJuIGN0eC5jb2x1bW4gKyAoY2xvc2luZyA/IDAgOiAxKTtlbHNlIGlmIChjdHgudHlwZSA9PSBcIilcIiAmJiAhY2xvc2luZykgcmV0dXJuIGN0eC5pbmRlbnRlZCArIChzdGF0ZW1lbnRJbmRlbnRVbml0IHx8IGN4LnVuaXQpO2Vsc2UgcmV0dXJuIGN0eC5pbmRlbnRlZCArIChjbG9zaW5nID8gMCA6IGN4LnVuaXQpO1xuICAgIH0sXG4gICAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgICBpbmRlbnRPbklucHV0OiBidWlsZEVsZWN0cmljSW5wdXRSZWdFeCgpLFxuICAgICAgY29tbWVudFRva2Vuczoge1xuICAgICAgICBsaW5lOiBcIi8vXCIsXG4gICAgICAgIGJsb2NrOiB7XG4gICAgICAgICAgb3BlbjogXCIvKlwiLFxuICAgICAgICAgIGNsb3NlOiBcIiovXCJcbiAgICAgICAgfVxuICAgICAgfVxuICAgIH1cbiAgfTtcbn1cbjtcbmV4cG9ydCBjb25zdCB2ZXJpbG9nID0gbWtWZXJpbG9nKHt9KTtcblxuLy8gVEwtVmVyaWxvZyBtb2RlLlxuLy8gU2VlIHRsLXgub3JnIGZvciBsYW5ndWFnZSBzcGVjLlxuLy8gU2VlIHRoZSBtb2RlIGluIGFjdGlvbiBhdCBtYWtlcmNoaXAuY29tLlxuLy8gQ29udGFjdDogc3RldmUuaG9vdmVyQHJlZHdvb2RlZGEuY29tXG5cbi8vIFRMViBJZGVudGlmaWVyIHByZWZpeGVzLlxuLy8gTm90ZSB0aGF0IHNpZ24gaXMgbm90IHRyZWF0ZWQgc2VwYXJhdGVseSwgc28gXCIrLy1cIiB2ZXJzaW9ucyBvZiBudW1lcmljIGlkZW50aWZpZXJzXG4vLyBhcmUgaW5jbHVkZWQuXG52YXIgdGx2SWRlbnRpZmllclN0eWxlID0ge1xuICBcInxcIjogXCJsaW5rXCIsXG4gIFwiPlwiOiBcInByb3BlcnR5XCIsXG4gIC8vIFNob3VsZCBjb25kaXRpb24gdGhpcyBvZmYgZm9yID4gVExWIDFjLlxuICBcIiRcIjogXCJ2YXJpYWJsZVwiLFxuICBcIiQkXCI6IFwidmFyaWFibGVcIixcbiAgXCI/JFwiOiBcInF1YWxpZmllclwiLFxuICBcIj8qXCI6IFwicXVhbGlmaWVyXCIsXG4gIFwiLVwiOiBcImNvbnRlbnRTZXBhcmF0b3JcIixcbiAgXCIvXCI6IFwicHJvcGVydHlcIixcbiAgXCIvLVwiOiBcInByb3BlcnR5XCIsXG4gIFwiQFwiOiBcInZhcmlhYmxlTmFtZS5zcGVjaWFsXCIsXG4gIFwiQC1cIjogXCJ2YXJpYWJsZU5hbWUuc3BlY2lhbFwiLFxuICBcIkArK1wiOiBcInZhcmlhYmxlTmFtZS5zcGVjaWFsXCIsXG4gIFwiQCs9XCI6IFwidmFyaWFibGVOYW1lLnNwZWNpYWxcIixcbiAgXCJAKz0tXCI6IFwidmFyaWFibGVOYW1lLnNwZWNpYWxcIixcbiAgXCJALS1cIjogXCJ2YXJpYWJsZU5hbWUuc3BlY2lhbFwiLFxuICBcIkAtPVwiOiBcInZhcmlhYmxlTmFtZS5zcGVjaWFsXCIsXG4gIFwiJStcIjogXCJ0YWdcIixcbiAgXCIlLVwiOiBcInRhZ1wiLFxuICBcIiVcIjogXCJ0YWdcIixcbiAgXCI+PlwiOiBcInRhZ1wiLFxuICBcIjw8XCI6IFwidGFnXCIsXG4gIFwiPD5cIjogXCJ0YWdcIixcbiAgXCIjXCI6IFwidGFnXCIsXG4gIC8vIE5lZWQgdG8gY2hvb3NlIGEgc3R5bGUgZm9yIHRoaXMuXG4gIFwiXlwiOiBcImF0dHJpYnV0ZVwiLFxuICBcIl5eXCI6IFwiYXR0cmlidXRlXCIsXG4gIFwiXiFcIjogXCJhdHRyaWJ1dGVcIixcbiAgXCIqXCI6IFwidmFyaWFibGVcIixcbiAgXCIqKlwiOiBcInZhcmlhYmxlXCIsXG4gIFwiXFxcXFwiOiBcImtleXdvcmRcIixcbiAgXCJcXFwiXCI6IFwiY29tbWVudFwiXG59O1xuXG4vLyBMaW5lcyBzdGFydGluZyB3aXRoIHRoZXNlIGNoYXJhY3RlcnMgZGVmaW5lIHNjb3BlIChyZXN1bHQgaW4gaW5kZW50YXRpb24pLlxudmFyIHRsdlNjb3BlUHJlZml4Q2hhcnMgPSB7XG4gIFwiL1wiOiBcImJlaC1oaWVyXCIsXG4gIFwiPlwiOiBcImJlaC1oaWVyXCIsXG4gIFwiLVwiOiBcInBoeXMtaGllclwiLFxuICBcInxcIjogXCJwaXBlXCIsXG4gIFwiP1wiOiBcIndoZW5cIixcbiAgXCJAXCI6IFwic3RhZ2VcIixcbiAgXCJcXFxcXCI6IFwia2V5d29yZFwiXG59O1xudmFyIHRsdkluZGVudFVuaXQgPSAzO1xudmFyIHRsdlRyYWNrU3RhdGVtZW50cyA9IGZhbHNlO1xudmFyIHRsdklkZW50TWF0Y2ggPSAvXihbfiFAI1xcJCVcXF4mXFwqLVxcKz1cXD9cXC9cXFxcXFx8J1wiPD5dKykoW1xcZFxcd19dKikvOyAvLyBNYXRjaGVzIGFuIGlkZW50aWZpZXIuXG4vLyBOb3RlIHRoYXQgJzonIGlzIGV4Y2x1ZGVkLCBiZWNhdXNlIG9mIGl0J3MgdXNlIGluIFs6XS5cbnZhciB0bHZMaW5lSW5kZW50YXRpb25NYXRjaCA9IC9eWyEgXSAqLztcbnZhciB0bHZDb21tZW50TWF0Y2ggPSAvXlxcL1tcXC9cXCpdLztcbmV4cG9ydCBjb25zdCB0bHYgPSBta1Zlcmlsb2coe1xuICBob29rczoge1xuICAgIGVsZWN0cmljSW5wdXQ6IGZhbHNlLFxuICAgIC8vIFJldHVybiB1bmRlZmluZWQgZm9yIHZlcmlsb2cgdG9rZW5pemluZywgb3Igc3R5bGUgZm9yIFRMViB0b2tlbiAobnVsbCBub3QgdXNlZCkuXG4gICAgLy8gU3RhbmRhcmQgQ00gc3R5bGVzIGFyZSB1c2VkIGZvciBtb3N0IGZvcm1hdHRpbmcsIGJ1dCBzb21lIFRMLVZlcmlsb2ctc3BlY2lmaWMgaGlnaGxpZ2h0aW5nXG4gICAgLy8gY2FuIGJlIGVuYWJsZWQgd2l0aCB0aGUgZGVmaW5pdGlvbiBvZiBjbS10bHYtKiBzdHlsZXMsIGluY2x1ZGluZyBoaWdobGlnaHRpbmcgZm9yOlxuICAgIC8vICAgLSBNNCB0b2tlbnNcbiAgICAvLyAgIC0gVExWIHNjb3BlIGluZGVudGF0aW9uXG4gICAgLy8gICAtIFN0YXRlbWVudCBkZWxpbWl0YXRpb24gKGVuYWJsZWQgYnkgdGx2VHJhY2tTdGF0ZW1lbnRzKVxuICAgIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgICAgdmFyIHN0eWxlID0gdW5kZWZpbmVkO1xuICAgICAgdmFyIG1hdGNoOyAvLyBSZXR1cm4gdmFsdWUgb2YgcGF0dGVybiBtYXRjaGVzLlxuXG4gICAgICAvLyBTZXQgaGlnaGxpZ2h0aW5nIG1vZGUgYmFzZWQgb24gY29kZSByZWdpb24gKFRMViBvciBTVikuXG4gICAgICBpZiAoc3RyZWFtLnNvbCgpICYmICFzdGF0ZS50bHZJbkJsb2NrQ29tbWVudCkge1xuICAgICAgICAvLyBQcm9jZXNzIHJlZ2lvbi5cbiAgICAgICAgaWYgKHN0cmVhbS5wZWVrKCkgPT0gJ1xcXFwnKSB7XG4gICAgICAgICAgc3R5bGUgPSBcImRlZlwiO1xuICAgICAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgICAgICBpZiAoc3RyZWFtLnN0cmluZy5tYXRjaCgvXFxcXFNWLykpIHtcbiAgICAgICAgICAgIHN0YXRlLnRsdkNvZGVBY3RpdmUgPSBmYWxzZTtcbiAgICAgICAgICB9IGVsc2UgaWYgKHN0cmVhbS5zdHJpbmcubWF0Y2goL1xcXFxUTFYvKSkge1xuICAgICAgICAgICAgc3RhdGUudGx2Q29kZUFjdGl2ZSA9IHRydWU7XG4gICAgICAgICAgfVxuICAgICAgICB9XG4gICAgICAgIC8vIENvcnJlY3QgaW5kZW50YXRpb24gaW4gdGhlIGZhY2Ugb2YgYSBsaW5lIHByZWZpeCBjaGFyLlxuICAgICAgICBpZiAoc3RhdGUudGx2Q29kZUFjdGl2ZSAmJiBzdHJlYW0ucG9zID09IDAgJiYgc3RhdGUuaW5kZW50ZWQgPT0gMCAmJiAobWF0Y2ggPSBzdHJlYW0ubWF0Y2godGx2TGluZUluZGVudGF0aW9uTWF0Y2gsIGZhbHNlKSkpIHtcbiAgICAgICAgICBzdGF0ZS5pbmRlbnRlZCA9IG1hdGNoWzBdLmxlbmd0aDtcbiAgICAgICAgfVxuXG4gICAgICAgIC8vIENvbXB1dGUgaW5kZW50YXRpb24gc3RhdGU6XG4gICAgICAgIC8vICAgbyBBdXRvIGluZGVudGF0aW9uIG9uIG5leHQgbGluZVxuICAgICAgICAvLyAgIG8gSW5kZW50YXRpb24gc2NvcGUgc3R5bGVzXG4gICAgICAgIHZhciBpbmRlbnRlZCA9IHN0YXRlLmluZGVudGVkO1xuICAgICAgICB2YXIgZGVwdGggPSBpbmRlbnRlZCAvIHRsdkluZGVudFVuaXQ7XG4gICAgICAgIGlmIChkZXB0aCA8PSBzdGF0ZS50bHZJbmRlbnRhdGlvblN0eWxlLmxlbmd0aCkge1xuICAgICAgICAgIC8vIG5vdCBkZWVwZXIgdGhhbiBjdXJyZW50IHNjb3BlXG5cbiAgICAgICAgICB2YXIgYmxhbmtsaW5lID0gc3RyZWFtLnN0cmluZy5sZW5ndGggPT0gaW5kZW50ZWQ7XG4gICAgICAgICAgdmFyIGNoUG9zID0gZGVwdGggKiB0bHZJbmRlbnRVbml0O1xuICAgICAgICAgIGlmIChjaFBvcyA8IHN0cmVhbS5zdHJpbmcubGVuZ3RoKSB7XG4gICAgICAgICAgICB2YXIgYm9keVN0cmluZyA9IHN0cmVhbS5zdHJpbmcuc2xpY2UoY2hQb3MpO1xuICAgICAgICAgICAgdmFyIGNoID0gYm9keVN0cmluZ1swXTtcbiAgICAgICAgICAgIGlmICh0bHZTY29wZVByZWZpeENoYXJzW2NoXSAmJiAobWF0Y2ggPSBib2R5U3RyaW5nLm1hdGNoKHRsdklkZW50TWF0Y2gpKSAmJiB0bHZJZGVudGlmaWVyU3R5bGVbbWF0Y2hbMV1dKSB7XG4gICAgICAgICAgICAgIC8vIFRoaXMgbGluZSBiZWdpbnMgc2NvcGUuXG4gICAgICAgICAgICAgIC8vIE5leHQgbGluZSBnZXRzIGluZGVudGVkIG9uZSBsZXZlbC5cbiAgICAgICAgICAgICAgaW5kZW50ZWQgKz0gdGx2SW5kZW50VW5pdDtcbiAgICAgICAgICAgICAgLy8gU3R5bGUgdGhlIG5leHQgbGV2ZWwgb2YgaW5kZW50YXRpb24gKGV4Y2VwdCBub24tcmVnaW9uIGtleXdvcmQgaWRlbnRpZmllcnMsXG4gICAgICAgICAgICAgIC8vICAgd2hpY2ggYXJlIHN0YXRlbWVudHMgdGhlbXNlbHZlcylcbiAgICAgICAgICAgICAgaWYgKCEoY2ggPT0gXCJcXFxcXCIgJiYgY2hQb3MgPiAwKSkge1xuICAgICAgICAgICAgICAgIHN0YXRlLnRsdkluZGVudGF0aW9uU3R5bGVbZGVwdGhdID0gdGx2U2NvcGVQcmVmaXhDaGFyc1tjaF07XG4gICAgICAgICAgICAgICAgaWYgKHRsdlRyYWNrU3RhdGVtZW50cykge1xuICAgICAgICAgICAgICAgICAgc3RhdGUuc3RhdGVtZW50Q29tbWVudCA9IGZhbHNlO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICBkZXB0aCsrO1xuICAgICAgICAgICAgICB9XG4gICAgICAgICAgICB9XG4gICAgICAgICAgfVxuICAgICAgICAgIC8vIENsZWFyIG91dCBkZWVwZXIgaW5kZW50YXRpb24gbGV2ZWxzIHVubGVzcyBsaW5lIGlzIGJsYW5rLlxuICAgICAgICAgIGlmICghYmxhbmtsaW5lKSB7XG4gICAgICAgICAgICB3aGlsZSAoc3RhdGUudGx2SW5kZW50YXRpb25TdHlsZS5sZW5ndGggPiBkZXB0aCkge1xuICAgICAgICAgICAgICBzdGF0ZS50bHZJbmRlbnRhdGlvblN0eWxlLnBvcCgpO1xuICAgICAgICAgICAgfVxuICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgICAgICAvLyBTZXQgbmV4dCBsZXZlbCBvZiBpbmRlbnRhdGlvbi5cbiAgICAgICAgc3RhdGUudGx2TmV4dEluZGVudCA9IGluZGVudGVkO1xuICAgICAgfVxuICAgICAgaWYgKHN0YXRlLnRsdkNvZGVBY3RpdmUpIHtcbiAgICAgICAgLy8gSGlnaGxpZ2h0IGFzIFRMVi5cblxuICAgICAgICB2YXIgYmVnaW5TdGF0ZW1lbnQgPSBmYWxzZTtcbiAgICAgICAgaWYgKHRsdlRyYWNrU3RhdGVtZW50cykge1xuICAgICAgICAgIC8vIFRoaXMgc3RhcnRzIGEgc3RhdGVtZW50IGlmIHRoZSBwb3NpdGlvbiBpcyBhdCB0aGUgc2NvcGUgbGV2ZWxcbiAgICAgICAgICAvLyBhbmQgd2UncmUgbm90IHdpdGhpbiBhIHN0YXRlbWVudCBsZWFkaW5nIGNvbW1lbnQuXG4gICAgICAgICAgYmVnaW5TdGF0ZW1lbnQgPSBzdHJlYW0ucGVlaygpICE9IFwiIFwiICYmXG4gICAgICAgICAgLy8gbm90IGEgc3BhY2VcbiAgICAgICAgICBzdHlsZSA9PT0gdW5kZWZpbmVkICYmXG4gICAgICAgICAgLy8gbm90IGEgcmVnaW9uIGlkZW50aWZpZXJcbiAgICAgICAgICAhc3RhdGUudGx2SW5CbG9ja0NvbW1lbnQgJiZcbiAgICAgICAgICAvLyBub3QgaW4gYmxvY2sgY29tbWVudFxuICAgICAgICAgIC8vIXN0cmVhbS5tYXRjaCh0bHZDb21tZW50TWF0Y2gsIGZhbHNlKSAmJiAvLyBub3QgY29tbWVudCBzdGFydFxuICAgICAgICAgIHN0cmVhbS5jb2x1bW4oKSA9PSBzdGF0ZS50bHZJbmRlbnRhdGlvblN0eWxlLmxlbmd0aCAqIHRsdkluZGVudFVuaXQ7IC8vIGF0IHNjb3BlIGxldmVsXG4gICAgICAgICAgaWYgKGJlZ2luU3RhdGVtZW50KSB7XG4gICAgICAgICAgICBpZiAoc3RhdGUuc3RhdGVtZW50Q29tbWVudCkge1xuICAgICAgICAgICAgICAvLyBzdGF0ZW1lbnQgYWxyZWFkeSBzdGFydGVkIGJ5IGNvbW1lbnRcbiAgICAgICAgICAgICAgYmVnaW5TdGF0ZW1lbnQgPSBmYWxzZTtcbiAgICAgICAgICAgIH1cbiAgICAgICAgICAgIHN0YXRlLnN0YXRlbWVudENvbW1lbnQgPSBzdHJlYW0ubWF0Y2godGx2Q29tbWVudE1hdGNoLCBmYWxzZSk7IC8vIGNvbW1lbnQgc3RhcnRcbiAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgICAgdmFyIG1hdGNoO1xuICAgICAgICBpZiAoc3R5bGUgIT09IHVuZGVmaW5lZCkge30gZWxzZSBpZiAoc3RhdGUudGx2SW5CbG9ja0NvbW1lbnQpIHtcbiAgICAgICAgICAvLyBJbiBhIGJsb2NrIGNvbW1lbnQuXG4gICAgICAgICAgaWYgKHN0cmVhbS5tYXRjaCgvXi4qP1xcKlxcLy8pKSB7XG4gICAgICAgICAgICAvLyBFeGl0IGJsb2NrIGNvbW1lbnQuXG4gICAgICAgICAgICBzdGF0ZS50bHZJbkJsb2NrQ29tbWVudCA9IGZhbHNlO1xuICAgICAgICAgICAgaWYgKHRsdlRyYWNrU3RhdGVtZW50cyAmJiAhc3RyZWFtLmVvbCgpKSB7XG4gICAgICAgICAgICAgIC8vIEFueXRoaW5nIGFmdGVyIGNvbW1lbnQgaXMgYXNzdW1lZCB0byBiZSByZWFsIHN0YXRlbWVudCBjb250ZW50LlxuICAgICAgICAgICAgICBzdGF0ZS5zdGF0ZW1lbnRDb21tZW50ID0gZmFsc2U7XG4gICAgICAgICAgICB9XG4gICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgICAgICB9XG4gICAgICAgICAgc3R5bGUgPSBcImNvbW1lbnRcIjtcbiAgICAgICAgfSBlbHNlIGlmICgobWF0Y2ggPSBzdHJlYW0ubWF0Y2godGx2Q29tbWVudE1hdGNoKSkgJiYgIXN0YXRlLnRsdkluQmxvY2tDb21tZW50KSB7XG4gICAgICAgICAgLy8gU3RhcnQgY29tbWVudC5cbiAgICAgICAgICBpZiAobWF0Y2hbMF0gPT0gXCIvL1wiKSB7XG4gICAgICAgICAgICAvLyBMaW5lIGNvbW1lbnQuXG4gICAgICAgICAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgIC8vIEJsb2NrIGNvbW1lbnQuXG4gICAgICAgICAgICBzdGF0ZS50bHZJbkJsb2NrQ29tbWVudCA9IHRydWU7XG4gICAgICAgICAgfVxuICAgICAgICAgIHN0eWxlID0gXCJjb21tZW50XCI7XG4gICAgICAgIH0gZWxzZSBpZiAobWF0Y2ggPSBzdHJlYW0ubWF0Y2godGx2SWRlbnRNYXRjaCkpIHtcbiAgICAgICAgICAvLyBsb29rcyBsaWtlIGFuIGlkZW50aWZpZXIgKG9yIGlkZW50aWZpZXIgcHJlZml4KVxuICAgICAgICAgIHZhciBwcmVmaXggPSBtYXRjaFsxXTtcbiAgICAgICAgICB2YXIgbW5lbW9uaWMgPSBtYXRjaFsyXTtcbiAgICAgICAgICBpZiAoXG4gICAgICAgICAgLy8gaXMgaWRlbnRpZmllciBwcmVmaXhcbiAgICAgICAgICB0bHZJZGVudGlmaWVyU3R5bGUuaGFzT3duUHJvcGVydHkocHJlZml4KSAmJiAoXG4gICAgICAgICAgLy8gaGFzIG1uZW1vbmljIG9yIHdlJ3JlIGF0IHRoZSBlbmQgb2YgdGhlIGxpbmUgKG1heWJlIGl0IGhhc24ndCBiZWVuIHR5cGVkIHlldClcbiAgICAgICAgICBtbmVtb25pYy5sZW5ndGggPiAwIHx8IHN0cmVhbS5lb2woKSkpIHtcbiAgICAgICAgICAgIHN0eWxlID0gdGx2SWRlbnRpZmllclN0eWxlW3ByZWZpeF07XG4gICAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICAgIC8vIEp1c3Qgc3dhbGxvdyBvbmUgY2hhcmFjdGVyIGFuZCB0cnkgYWdhaW4uXG4gICAgICAgICAgICAvLyBUaGlzIGVuYWJsZXMgc3Vic2VxdWVudCBpZGVudGlmaWVyIG1hdGNoIHdpdGggcHJlY2VkaW5nIHN5bWJvbCBjaGFyYWN0ZXIsIHdoaWNoXG4gICAgICAgICAgICAvLyAgIGlzIGxlZ2FsIHdpdGhpbiBhIHN0YXRlbWVudC4gIChFZywgISRyZXNldCkuICBJdCBhbHNvIGVuYWJsZXMgZGV0ZWN0aW9uIG9mXG4gICAgICAgICAgICAvLyAgIGNvbW1lbnQgc3RhcnQgd2l0aCBwcmVjZWRpbmcgc3ltYm9scy5cbiAgICAgICAgICAgIHN0cmVhbS5iYWNrVXAoc3RyZWFtLmN1cnJlbnQoKS5sZW5ndGggLSAxKTtcbiAgICAgICAgICB9XG4gICAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKC9eXFx0Ky8pKSB7XG4gICAgICAgICAgLy8gSGlnaGxpZ2h0IHRhYnMsIHdoaWNoIGFyZSBpbGxlZ2FsLlxuICAgICAgICAgIHN0eWxlID0gXCJpbnZhbGlkXCI7XG4gICAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKC9eW1xcW1xcXXt9XFwoXFwpO1xcOl0rLykpIHtcbiAgICAgICAgICAvLyBbOl0sICgpLCB7fSwgOy5cbiAgICAgICAgICBzdHlsZSA9IFwibWV0YVwiO1xuICAgICAgICB9IGVsc2UgaWYgKG1hdGNoID0gc3RyZWFtLm1hdGNoKC9eW21NXTQoW1xcK19dKT9bXFx3XFxkX10qLykpIHtcbiAgICAgICAgICAvLyBtNCBwcmUgcHJvY1xuICAgICAgICAgIHN0eWxlID0gbWF0Y2hbMV0gPT0gXCIrXCIgPyBcImtleXdvcmQuc3BlY2lhbFwiIDogXCJrZXl3b3JkXCI7XG4gICAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKC9eICsvKSkge1xuICAgICAgICAgIC8vIFNraXAgb3ZlciBzcGFjZXMuXG4gICAgICAgICAgaWYgKHN0cmVhbS5lb2woKSkge1xuICAgICAgICAgICAgLy8gVHJhaWxpbmcgc3BhY2VzLlxuICAgICAgICAgICAgc3R5bGUgPSBcImVycm9yXCI7XG4gICAgICAgICAgfVxuICAgICAgICB9IGVsc2UgaWYgKHN0cmVhbS5tYXRjaCgvXltcXHdcXGRfXSsvKSkge1xuICAgICAgICAgIC8vIGFscGhhLW51bWVyaWMgdG9rZW4uXG4gICAgICAgICAgc3R5bGUgPSBcIm51bWJlclwiO1xuICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgIC8vIEVhdCB0aGUgbmV4dCBjaGFyIHcvIG5vIGZvcm1hdHRpbmcuXG4gICAgICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgICAgfVxuICAgICAgfSBlbHNlIHtcbiAgICAgICAgaWYgKHN0cmVhbS5tYXRjaCgvXlttTV00KFtcXHdcXGRfXSopLykpIHtcbiAgICAgICAgICAvLyBtNCBwcmUgcHJvY1xuICAgICAgICAgIHN0eWxlID0gXCJrZXl3b3JkXCI7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICAgIHJldHVybiBzdHlsZTtcbiAgICB9LFxuICAgIGluZGVudDogZnVuY3Rpb24gKHN0YXRlKSB7XG4gICAgICByZXR1cm4gc3RhdGUudGx2Q29kZUFjdGl2ZSA9PSB0cnVlID8gc3RhdGUudGx2TmV4dEluZGVudCA6IC0xO1xuICAgIH0sXG4gICAgc3RhcnRTdGF0ZTogZnVuY3Rpb24gKHN0YXRlKSB7XG4gICAgICBzdGF0ZS50bHZJbmRlbnRhdGlvblN0eWxlID0gW107IC8vIFN0eWxlcyB0byB1c2UgZm9yIGVhY2ggbGV2ZWwgb2YgaW5kZW50YXRpb24uXG4gICAgICBzdGF0ZS50bHZDb2RlQWN0aXZlID0gdHJ1ZTsgLy8gVHJ1ZSB3aGVuIHdlJ3JlIGluIGEgVExWIHJlZ2lvbiAoYW5kIGF0IGJlZ2lubmluZyBvZiBmaWxlKS5cbiAgICAgIHN0YXRlLnRsdk5leHRJbmRlbnQgPSAtMTsgLy8gVGhlIG51bWJlciBvZiBzcGFjZXMgdG8gYXV0b2luZGVudCB0aGUgbmV4dCBsaW5lIGlmIHRsdkNvZGVBY3RpdmUuXG4gICAgICBzdGF0ZS50bHZJbkJsb2NrQ29tbWVudCA9IGZhbHNlOyAvLyBUcnVlIGluc2lkZSAvKiovIGNvbW1lbnQuXG4gICAgICBpZiAodGx2VHJhY2tTdGF0ZW1lbnRzKSB7XG4gICAgICAgIHN0YXRlLnN0YXRlbWVudENvbW1lbnQgPSBmYWxzZTsgLy8gVHJ1ZSBpbnNpZGUgYSBzdGF0ZW1lbnQncyBoZWFkZXIgY29tbWVudC5cbiAgICAgIH1cbiAgICB9XG4gIH1cbn0pOyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=