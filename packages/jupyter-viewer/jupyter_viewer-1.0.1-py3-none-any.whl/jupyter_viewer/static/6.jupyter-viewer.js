"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[6],{

/***/ 6
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   vhdl: () => (/* binding */ vhdl)
/* harmony export */ });
function words(str) {
  var obj = {},
    words = str.split(",");
  for (var i = 0; i < words.length; ++i) {
    var allCaps = words[i].toUpperCase();
    var firstCap = words[i].charAt(0).toUpperCase() + words[i].slice(1);
    obj[words[i]] = true;
    obj[allCaps] = true;
    obj[firstCap] = true;
  }
  return obj;
}
function metaHook(stream) {
  stream.eatWhile(/[\w\$_]/);
  return "meta";
}
var atoms = words("null"),
  hooks = {
    "`": metaHook,
    "$": metaHook
  },
  multiLineStrings = false;
var keywords = words("abs,access,after,alias,all,and,architecture,array,assert,attribute,begin,block," + "body,buffer,bus,case,component,configuration,constant,disconnect,downto,else,elsif,end,end block,end case," + "end component,end for,end generate,end if,end loop,end process,end record,end units,entity,exit,file,for," + "function,generate,generic,generic map,group,guarded,if,impure,in,inertial,inout,is,label,library,linkage," + "literal,loop,map,mod,nand,new,next,nor,null,of,on,open,or,others,out,package,package body,port,port map," + "postponed,procedure,process,pure,range,record,register,reject,rem,report,return,rol,ror,select,severity,signal," + "sla,sll,sra,srl,subtype,then,to,transport,type,unaffected,units,until,use,variable,wait,when,while,with,xnor,xor");
var blockKeywords = words("architecture,entity,begin,case,port,else,elsif,end,for,function,if");
var isOperatorChar = /[&|~><!\)\(*#%@+\/=?\:;}{,\.\^\-\[\]]/;
var curPunc;
function tokenBase(stream, state) {
  var ch = stream.next();
  if (hooks[ch]) {
    var result = hooks[ch](stream, state);
    if (result !== false) return result;
  }
  if (ch == '"') {
    state.tokenize = tokenString2(ch);
    return state.tokenize(stream, state);
  }
  if (ch == "'") {
    state.tokenize = tokenString(ch);
    return state.tokenize(stream, state);
  }
  if (/[\[\]{}\(\),;\:\.]/.test(ch)) {
    curPunc = ch;
    return null;
  }
  if (/[\d']/.test(ch)) {
    stream.eatWhile(/[\w\.']/);
    return "number";
  }
  if (ch == "-") {
    if (stream.eat("-")) {
      stream.skipToEnd();
      return "comment";
    }
  }
  if (isOperatorChar.test(ch)) {
    stream.eatWhile(isOperatorChar);
    return "operator";
  }
  stream.eatWhile(/[\w\$_]/);
  var cur = stream.current();
  if (keywords.propertyIsEnumerable(cur.toLowerCase())) {
    if (blockKeywords.propertyIsEnumerable(cur)) curPunc = "newstatement";
    return "keyword";
  }
  if (atoms.propertyIsEnumerable(cur)) return "atom";
  return "variable";
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
      escaped = !escaped && next == "--";
    }
    if (end || !(escaped || multiLineStrings)) state.tokenize = tokenBase;
    return "string";
  };
}
function tokenString2(quote) {
  return function (stream, state) {
    var escaped = false,
      next,
      end = false;
    while ((next = stream.next()) != null) {
      if (next == quote && !escaped) {
        end = true;
        break;
      }
      escaped = !escaped && next == "--";
    }
    if (end || !(escaped || multiLineStrings)) state.tokenize = tokenBase;
    return "string.special";
  };
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
const vhdl = {
  name: "vhdl",
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
    var firstChar = textAfter && textAfter.charAt(0),
      ctx = state.context,
      closing = firstChar == ctx.type;
    if (ctx.type == "statement") return ctx.indented + (firstChar == "{" ? 0 : cx.unit);else if (ctx.align) return ctx.column + (closing ? 0 : 1);else return ctx.indented + (closing ? 0 : cx.unit);
  },
  languageData: {
    indentOnInput: /^\s*[{}]$/,
    commentTokens: {
      line: "--"
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvdmhkbC5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiB3b3JkcyhzdHIpIHtcbiAgdmFyIG9iaiA9IHt9LFxuICAgIHdvcmRzID0gc3RyLnNwbGl0KFwiLFwiKTtcbiAgZm9yICh2YXIgaSA9IDA7IGkgPCB3b3Jkcy5sZW5ndGg7ICsraSkge1xuICAgIHZhciBhbGxDYXBzID0gd29yZHNbaV0udG9VcHBlckNhc2UoKTtcbiAgICB2YXIgZmlyc3RDYXAgPSB3b3Jkc1tpXS5jaGFyQXQoMCkudG9VcHBlckNhc2UoKSArIHdvcmRzW2ldLnNsaWNlKDEpO1xuICAgIG9ialt3b3Jkc1tpXV0gPSB0cnVlO1xuICAgIG9ialthbGxDYXBzXSA9IHRydWU7XG4gICAgb2JqW2ZpcnN0Q2FwXSA9IHRydWU7XG4gIH1cbiAgcmV0dXJuIG9iajtcbn1cbmZ1bmN0aW9uIG1ldGFIb29rKHN0cmVhbSkge1xuICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXCRfXS8pO1xuICByZXR1cm4gXCJtZXRhXCI7XG59XG52YXIgYXRvbXMgPSB3b3JkcyhcIm51bGxcIiksXG4gIGhvb2tzID0ge1xuICAgIFwiYFwiOiBtZXRhSG9vayxcbiAgICBcIiRcIjogbWV0YUhvb2tcbiAgfSxcbiAgbXVsdGlMaW5lU3RyaW5ncyA9IGZhbHNlO1xudmFyIGtleXdvcmRzID0gd29yZHMoXCJhYnMsYWNjZXNzLGFmdGVyLGFsaWFzLGFsbCxhbmQsYXJjaGl0ZWN0dXJlLGFycmF5LGFzc2VydCxhdHRyaWJ1dGUsYmVnaW4sYmxvY2ssXCIgKyBcImJvZHksYnVmZmVyLGJ1cyxjYXNlLGNvbXBvbmVudCxjb25maWd1cmF0aW9uLGNvbnN0YW50LGRpc2Nvbm5lY3QsZG93bnRvLGVsc2UsZWxzaWYsZW5kLGVuZCBibG9jayxlbmQgY2FzZSxcIiArIFwiZW5kIGNvbXBvbmVudCxlbmQgZm9yLGVuZCBnZW5lcmF0ZSxlbmQgaWYsZW5kIGxvb3AsZW5kIHByb2Nlc3MsZW5kIHJlY29yZCxlbmQgdW5pdHMsZW50aXR5LGV4aXQsZmlsZSxmb3IsXCIgKyBcImZ1bmN0aW9uLGdlbmVyYXRlLGdlbmVyaWMsZ2VuZXJpYyBtYXAsZ3JvdXAsZ3VhcmRlZCxpZixpbXB1cmUsaW4saW5lcnRpYWwsaW5vdXQsaXMsbGFiZWwsbGlicmFyeSxsaW5rYWdlLFwiICsgXCJsaXRlcmFsLGxvb3AsbWFwLG1vZCxuYW5kLG5ldyxuZXh0LG5vcixudWxsLG9mLG9uLG9wZW4sb3Isb3RoZXJzLG91dCxwYWNrYWdlLHBhY2thZ2UgYm9keSxwb3J0LHBvcnQgbWFwLFwiICsgXCJwb3N0cG9uZWQscHJvY2VkdXJlLHByb2Nlc3MscHVyZSxyYW5nZSxyZWNvcmQscmVnaXN0ZXIscmVqZWN0LHJlbSxyZXBvcnQscmV0dXJuLHJvbCxyb3Isc2VsZWN0LHNldmVyaXR5LHNpZ25hbCxcIiArIFwic2xhLHNsbCxzcmEsc3JsLHN1YnR5cGUsdGhlbix0byx0cmFuc3BvcnQsdHlwZSx1bmFmZmVjdGVkLHVuaXRzLHVudGlsLHVzZSx2YXJpYWJsZSx3YWl0LHdoZW4sd2hpbGUsd2l0aCx4bm9yLHhvclwiKTtcbnZhciBibG9ja0tleXdvcmRzID0gd29yZHMoXCJhcmNoaXRlY3R1cmUsZW50aXR5LGJlZ2luLGNhc2UscG9ydCxlbHNlLGVsc2lmLGVuZCxmb3IsZnVuY3Rpb24saWZcIik7XG52YXIgaXNPcGVyYXRvckNoYXIgPSAvWyZ8fj48IVxcKVxcKCojJUArXFwvPT9cXDo7fXssXFwuXFxeXFwtXFxbXFxdXS87XG52YXIgY3VyUHVuYztcbmZ1bmN0aW9uIHRva2VuQmFzZShzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gIGlmIChob29rc1tjaF0pIHtcbiAgICB2YXIgcmVzdWx0ID0gaG9va3NbY2hdKHN0cmVhbSwgc3RhdGUpO1xuICAgIGlmIChyZXN1bHQgIT09IGZhbHNlKSByZXR1cm4gcmVzdWx0O1xuICB9XG4gIGlmIChjaCA9PSAnXCInKSB7XG4gICAgc3RhdGUudG9rZW5pemUgPSB0b2tlblN0cmluZzIoY2gpO1xuICAgIHJldHVybiBzdGF0ZS50b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgfVxuICBpZiAoY2ggPT0gXCInXCIpIHtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuU3RyaW5nKGNoKTtcbiAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cbiAgaWYgKC9bXFxbXFxde31cXChcXCksO1xcOlxcLl0vLnRlc3QoY2gpKSB7XG4gICAgY3VyUHVuYyA9IGNoO1xuICAgIHJldHVybiBudWxsO1xuICB9XG4gIGlmICgvW1xcZCddLy50ZXN0KGNoKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvW1xcd1xcLiddLyk7XG4gICAgcmV0dXJuIFwibnVtYmVyXCI7XG4gIH1cbiAgaWYgKGNoID09IFwiLVwiKSB7XG4gICAgaWYgKHN0cmVhbS5lYXQoXCItXCIpKSB7XG4gICAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gICAgfVxuICB9XG4gIGlmIChpc09wZXJhdG9yQ2hhci50ZXN0KGNoKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZShpc09wZXJhdG9yQ2hhcik7XG4gICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgfVxuICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXCRfXS8pO1xuICB2YXIgY3VyID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgaWYgKGtleXdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1ci50b0xvd2VyQ2FzZSgpKSkge1xuICAgIGlmIChibG9ja0tleXdvcmRzLnByb3BlcnR5SXNFbnVtZXJhYmxlKGN1cikpIGN1clB1bmMgPSBcIm5ld3N0YXRlbWVudFwiO1xuICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgfVxuICBpZiAoYXRvbXMucHJvcGVydHlJc0VudW1lcmFibGUoY3VyKSkgcmV0dXJuIFwiYXRvbVwiO1xuICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xufVxuZnVuY3Rpb24gdG9rZW5TdHJpbmcocXVvdGUpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGVzY2FwZWQgPSBmYWxzZSxcbiAgICAgIG5leHQsXG4gICAgICBlbmQgPSBmYWxzZTtcbiAgICB3aGlsZSAoKG5leHQgPSBzdHJlYW0ubmV4dCgpKSAhPSBudWxsKSB7XG4gICAgICBpZiAobmV4dCA9PSBxdW90ZSAmJiAhZXNjYXBlZCkge1xuICAgICAgICBlbmQgPSB0cnVlO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBuZXh0ID09IFwiLS1cIjtcbiAgICB9XG4gICAgaWYgKGVuZCB8fCAhKGVzY2FwZWQgfHwgbXVsdGlMaW5lU3RyaW5ncykpIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9O1xufVxuZnVuY3Rpb24gdG9rZW5TdHJpbmcyKHF1b3RlKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHZhciBlc2NhcGVkID0gZmFsc2UsXG4gICAgICBuZXh0LFxuICAgICAgZW5kID0gZmFsc2U7XG4gICAgd2hpbGUgKChuZXh0ID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgICAgaWYgKG5leHQgPT0gcXVvdGUgJiYgIWVzY2FwZWQpIHtcbiAgICAgICAgZW5kID0gdHJ1ZTtcbiAgICAgICAgYnJlYWs7XG4gICAgICB9XG4gICAgICBlc2NhcGVkID0gIWVzY2FwZWQgJiYgbmV4dCA9PSBcIi0tXCI7XG4gICAgfVxuICAgIGlmIChlbmQgfHwgIShlc2NhcGVkIHx8IG11bHRpTGluZVN0cmluZ3MpKSBzdGF0ZS50b2tlbml6ZSA9IHRva2VuQmFzZTtcbiAgICByZXR1cm4gXCJzdHJpbmcuc3BlY2lhbFwiO1xuICB9O1xufVxuZnVuY3Rpb24gQ29udGV4dChpbmRlbnRlZCwgY29sdW1uLCB0eXBlLCBhbGlnbiwgcHJldikge1xuICB0aGlzLmluZGVudGVkID0gaW5kZW50ZWQ7XG4gIHRoaXMuY29sdW1uID0gY29sdW1uO1xuICB0aGlzLnR5cGUgPSB0eXBlO1xuICB0aGlzLmFsaWduID0gYWxpZ247XG4gIHRoaXMucHJldiA9IHByZXY7XG59XG5mdW5jdGlvbiBwdXNoQ29udGV4dChzdGF0ZSwgY29sLCB0eXBlKSB7XG4gIHJldHVybiBzdGF0ZS5jb250ZXh0ID0gbmV3IENvbnRleHQoc3RhdGUuaW5kZW50ZWQsIGNvbCwgdHlwZSwgbnVsbCwgc3RhdGUuY29udGV4dCk7XG59XG5mdW5jdGlvbiBwb3BDb250ZXh0KHN0YXRlKSB7XG4gIHZhciB0ID0gc3RhdGUuY29udGV4dC50eXBlO1xuICBpZiAodCA9PSBcIilcIiB8fCB0ID09IFwiXVwiIHx8IHQgPT0gXCJ9XCIpIHN0YXRlLmluZGVudGVkID0gc3RhdGUuY29udGV4dC5pbmRlbnRlZDtcbiAgcmV0dXJuIHN0YXRlLmNvbnRleHQgPSBzdGF0ZS5jb250ZXh0LnByZXY7XG59XG5cbi8vIEludGVyZmFjZVxuZXhwb3J0IGNvbnN0IHZoZGwgPSB7XG4gIG5hbWU6IFwidmhkbFwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoaW5kZW50VW5pdCkge1xuICAgIHJldHVybiB7XG4gICAgICB0b2tlbml6ZTogbnVsbCxcbiAgICAgIGNvbnRleHQ6IG5ldyBDb250ZXh0KC1pbmRlbnRVbml0LCAwLCBcInRvcFwiLCBmYWxzZSksXG4gICAgICBpbmRlbnRlZDogMCxcbiAgICAgIHN0YXJ0T2ZMaW5lOiB0cnVlXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGN0eCA9IHN0YXRlLmNvbnRleHQ7XG4gICAgaWYgKHN0cmVhbS5zb2woKSkge1xuICAgICAgaWYgKGN0eC5hbGlnbiA9PSBudWxsKSBjdHguYWxpZ24gPSBmYWxzZTtcbiAgICAgIHN0YXRlLmluZGVudGVkID0gc3RyZWFtLmluZGVudGF0aW9uKCk7XG4gICAgICBzdGF0ZS5zdGFydE9mTGluZSA9IHRydWU7XG4gICAgfVxuICAgIGlmIChzdHJlYW0uZWF0U3BhY2UoKSkgcmV0dXJuIG51bGw7XG4gICAgY3VyUHVuYyA9IG51bGw7XG4gICAgdmFyIHN0eWxlID0gKHN0YXRlLnRva2VuaXplIHx8IHRva2VuQmFzZSkoc3RyZWFtLCBzdGF0ZSk7XG4gICAgaWYgKHN0eWxlID09IFwiY29tbWVudFwiIHx8IHN0eWxlID09IFwibWV0YVwiKSByZXR1cm4gc3R5bGU7XG4gICAgaWYgKGN0eC5hbGlnbiA9PSBudWxsKSBjdHguYWxpZ24gPSB0cnVlO1xuICAgIGlmICgoY3VyUHVuYyA9PSBcIjtcIiB8fCBjdXJQdW5jID09IFwiOlwiKSAmJiBjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiKSBwb3BDb250ZXh0KHN0YXRlKTtlbHNlIGlmIChjdXJQdW5jID09IFwie1wiKSBwdXNoQ29udGV4dChzdGF0ZSwgc3RyZWFtLmNvbHVtbigpLCBcIn1cIik7ZWxzZSBpZiAoY3VyUHVuYyA9PSBcIltcIikgcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbS5jb2x1bW4oKSwgXCJdXCIpO2Vsc2UgaWYgKGN1clB1bmMgPT0gXCIoXCIpIHB1c2hDb250ZXh0KHN0YXRlLCBzdHJlYW0uY29sdW1uKCksIFwiKVwiKTtlbHNlIGlmIChjdXJQdW5jID09IFwifVwiKSB7XG4gICAgICB3aGlsZSAoY3R4LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIikgY3R4ID0gcG9wQ29udGV4dChzdGF0ZSk7XG4gICAgICBpZiAoY3R4LnR5cGUgPT0gXCJ9XCIpIGN0eCA9IHBvcENvbnRleHQoc3RhdGUpO1xuICAgICAgd2hpbGUgKGN0eC50eXBlID09IFwic3RhdGVtZW50XCIpIGN0eCA9IHBvcENvbnRleHQoc3RhdGUpO1xuICAgIH0gZWxzZSBpZiAoY3VyUHVuYyA9PSBjdHgudHlwZSkgcG9wQ29udGV4dChzdGF0ZSk7ZWxzZSBpZiAoY3R4LnR5cGUgPT0gXCJ9XCIgfHwgY3R4LnR5cGUgPT0gXCJ0b3BcIiB8fCBjdHgudHlwZSA9PSBcInN0YXRlbWVudFwiICYmIGN1clB1bmMgPT0gXCJuZXdzdGF0ZW1lbnRcIikgcHVzaENvbnRleHQoc3RhdGUsIHN0cmVhbS5jb2x1bW4oKSwgXCJzdGF0ZW1lbnRcIik7XG4gICAgc3RhdGUuc3RhcnRPZkxpbmUgPSBmYWxzZTtcbiAgICByZXR1cm4gc3R5bGU7XG4gIH0sXG4gIGluZGVudDogZnVuY3Rpb24gKHN0YXRlLCB0ZXh0QWZ0ZXIsIGN4KSB7XG4gICAgaWYgKHN0YXRlLnRva2VuaXplICE9IHRva2VuQmFzZSAmJiBzdGF0ZS50b2tlbml6ZSAhPSBudWxsKSByZXR1cm4gMDtcbiAgICB2YXIgZmlyc3RDaGFyID0gdGV4dEFmdGVyICYmIHRleHRBZnRlci5jaGFyQXQoMCksXG4gICAgICBjdHggPSBzdGF0ZS5jb250ZXh0LFxuICAgICAgY2xvc2luZyA9IGZpcnN0Q2hhciA9PSBjdHgudHlwZTtcbiAgICBpZiAoY3R4LnR5cGUgPT0gXCJzdGF0ZW1lbnRcIikgcmV0dXJuIGN0eC5pbmRlbnRlZCArIChmaXJzdENoYXIgPT0gXCJ7XCIgPyAwIDogY3gudW5pdCk7ZWxzZSBpZiAoY3R4LmFsaWduKSByZXR1cm4gY3R4LmNvbHVtbiArIChjbG9zaW5nID8gMCA6IDEpO2Vsc2UgcmV0dXJuIGN0eC5pbmRlbnRlZCArIChjbG9zaW5nID8gMCA6IGN4LnVuaXQpO1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBpbmRlbnRPbklucHV0OiAvXlxccypbe31dJC8sXG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgbGluZTogXCItLVwiXG4gICAgfVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=