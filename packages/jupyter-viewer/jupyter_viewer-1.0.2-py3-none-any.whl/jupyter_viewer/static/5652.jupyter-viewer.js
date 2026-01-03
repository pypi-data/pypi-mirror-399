"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[5652],{

/***/ 55652
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   shell: () => (/* binding */ shell)
/* harmony export */ });
var words = {};
function define(style, dict) {
  for (var i = 0; i < dict.length; i++) {
    words[dict[i]] = style;
  }
}
;
var commonAtoms = ["true", "false"];
var commonKeywords = ["if", "then", "do", "else", "elif", "while", "until", "for", "in", "esac", "fi", "fin", "fil", "done", "exit", "set", "unset", "export", "function"];
var commonCommands = ["ab", "awk", "bash", "beep", "cat", "cc", "cd", "chown", "chmod", "chroot", "clear", "cp", "curl", "cut", "diff", "echo", "find", "gawk", "gcc", "get", "git", "grep", "hg", "kill", "killall", "ln", "ls", "make", "mkdir", "openssl", "mv", "nc", "nl", "node", "npm", "ping", "ps", "restart", "rm", "rmdir", "sed", "service", "sh", "shopt", "shred", "source", "sort", "sleep", "ssh", "start", "stop", "su", "sudo", "svn", "tee", "telnet", "top", "touch", "vi", "vim", "wall", "wc", "wget", "who", "write", "yes", "zsh"];
define('atom', commonAtoms);
define('keyword', commonKeywords);
define('builtin', commonCommands);
function tokenBase(stream, state) {
  if (stream.eatSpace()) return null;
  var sol = stream.sol();
  var ch = stream.next();
  if (ch === '\\') {
    stream.next();
    return null;
  }
  if (ch === '\'' || ch === '"' || ch === '`') {
    state.tokens.unshift(tokenString(ch, ch === "`" ? "quote" : "string"));
    return tokenize(stream, state);
  }
  if (ch === '#') {
    if (sol && stream.eat('!')) {
      stream.skipToEnd();
      return 'meta'; // 'comment'?
    }
    stream.skipToEnd();
    return 'comment';
  }
  if (ch === '$') {
    state.tokens.unshift(tokenDollar);
    return tokenize(stream, state);
  }
  if (ch === '+' || ch === '=') {
    return 'operator';
  }
  if (ch === '-') {
    stream.eat('-');
    stream.eatWhile(/\w/);
    return 'attribute';
  }
  if (ch == "<") {
    if (stream.match("<<")) return "operator";
    var heredoc = stream.match(/^<-?\s*(?:['"]([^'"]*)['"]|([^'"\s]*))/);
    if (heredoc) {
      state.tokens.unshift(tokenHeredoc(heredoc[1] || heredoc[2]));
      return 'string.special';
    }
  }
  if (/\d/.test(ch)) {
    stream.eatWhile(/\d/);
    if (stream.eol() || !/\w/.test(stream.peek())) {
      return 'number';
    }
  }
  stream.eatWhile(/[\w-]/);
  var cur = stream.current();
  if (stream.peek() === '=' && /\w+/.test(cur)) return 'def';
  return words.hasOwnProperty(cur) ? words[cur] : null;
}
function tokenString(quote, style) {
  var close = quote == "(" ? ")" : quote == "{" ? "}" : quote;
  return function (stream, state) {
    var next,
      escaped = false;
    while ((next = stream.next()) != null) {
      if (next === close && !escaped) {
        state.tokens.shift();
        break;
      } else if (next === '$' && !escaped && quote !== "'" && stream.peek() != close) {
        escaped = true;
        stream.backUp(1);
        state.tokens.unshift(tokenDollar);
        break;
      } else if (!escaped && quote !== close && next === quote) {
        state.tokens.unshift(tokenString(quote, style));
        return tokenize(stream, state);
      } else if (!escaped && /['"]/.test(next) && !/['"]/.test(quote)) {
        state.tokens.unshift(tokenStringStart(next, "string"));
        stream.backUp(1);
        break;
      }
      escaped = !escaped && next === '\\';
    }
    return style;
  };
}
;
function tokenStringStart(quote, style) {
  return function (stream, state) {
    state.tokens[0] = tokenString(quote, style);
    stream.next();
    return tokenize(stream, state);
  };
}
var tokenDollar = function (stream, state) {
  if (state.tokens.length > 1) stream.eat('$');
  var ch = stream.next();
  if (/['"({]/.test(ch)) {
    state.tokens[0] = tokenString(ch, ch == "(" ? "quote" : ch == "{" ? "def" : "string");
    return tokenize(stream, state);
  }
  if (!/\d/.test(ch)) stream.eatWhile(/\w/);
  state.tokens.shift();
  return 'def';
};
function tokenHeredoc(delim) {
  return function (stream, state) {
    if (stream.sol() && stream.string == delim) state.tokens.shift();
    stream.skipToEnd();
    return "string.special";
  };
}
function tokenize(stream, state) {
  return (state.tokens[0] || tokenBase)(stream, state);
}
;
const shell = {
  name: "shell",
  startState: function () {
    return {
      tokens: []
    };
  },
  token: function (stream, state) {
    return tokenize(stream, state);
  },
  languageData: {
    autocomplete: commonAtoms.concat(commonKeywords, commonCommands),
    closeBrackets: {
      brackets: ["(", "[", "{", "'", '"', "`"]
    },
    commentTokens: {
      line: "#"
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNTY1Mi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL3NoZWxsLmpzIl0sInNvdXJjZXNDb250ZW50IjpbInZhciB3b3JkcyA9IHt9O1xuZnVuY3Rpb24gZGVmaW5lKHN0eWxlLCBkaWN0KSB7XG4gIGZvciAodmFyIGkgPSAwOyBpIDwgZGljdC5sZW5ndGg7IGkrKykge1xuICAgIHdvcmRzW2RpY3RbaV1dID0gc3R5bGU7XG4gIH1cbn1cbjtcbnZhciBjb21tb25BdG9tcyA9IFtcInRydWVcIiwgXCJmYWxzZVwiXTtcbnZhciBjb21tb25LZXl3b3JkcyA9IFtcImlmXCIsIFwidGhlblwiLCBcImRvXCIsIFwiZWxzZVwiLCBcImVsaWZcIiwgXCJ3aGlsZVwiLCBcInVudGlsXCIsIFwiZm9yXCIsIFwiaW5cIiwgXCJlc2FjXCIsIFwiZmlcIiwgXCJmaW5cIiwgXCJmaWxcIiwgXCJkb25lXCIsIFwiZXhpdFwiLCBcInNldFwiLCBcInVuc2V0XCIsIFwiZXhwb3J0XCIsIFwiZnVuY3Rpb25cIl07XG52YXIgY29tbW9uQ29tbWFuZHMgPSBbXCJhYlwiLCBcImF3a1wiLCBcImJhc2hcIiwgXCJiZWVwXCIsIFwiY2F0XCIsIFwiY2NcIiwgXCJjZFwiLCBcImNob3duXCIsIFwiY2htb2RcIiwgXCJjaHJvb3RcIiwgXCJjbGVhclwiLCBcImNwXCIsIFwiY3VybFwiLCBcImN1dFwiLCBcImRpZmZcIiwgXCJlY2hvXCIsIFwiZmluZFwiLCBcImdhd2tcIiwgXCJnY2NcIiwgXCJnZXRcIiwgXCJnaXRcIiwgXCJncmVwXCIsIFwiaGdcIiwgXCJraWxsXCIsIFwia2lsbGFsbFwiLCBcImxuXCIsIFwibHNcIiwgXCJtYWtlXCIsIFwibWtkaXJcIiwgXCJvcGVuc3NsXCIsIFwibXZcIiwgXCJuY1wiLCBcIm5sXCIsIFwibm9kZVwiLCBcIm5wbVwiLCBcInBpbmdcIiwgXCJwc1wiLCBcInJlc3RhcnRcIiwgXCJybVwiLCBcInJtZGlyXCIsIFwic2VkXCIsIFwic2VydmljZVwiLCBcInNoXCIsIFwic2hvcHRcIiwgXCJzaHJlZFwiLCBcInNvdXJjZVwiLCBcInNvcnRcIiwgXCJzbGVlcFwiLCBcInNzaFwiLCBcInN0YXJ0XCIsIFwic3RvcFwiLCBcInN1XCIsIFwic3Vkb1wiLCBcInN2blwiLCBcInRlZVwiLCBcInRlbG5ldFwiLCBcInRvcFwiLCBcInRvdWNoXCIsIFwidmlcIiwgXCJ2aW1cIiwgXCJ3YWxsXCIsIFwid2NcIiwgXCJ3Z2V0XCIsIFwid2hvXCIsIFwid3JpdGVcIiwgXCJ5ZXNcIiwgXCJ6c2hcIl07XG5kZWZpbmUoJ2F0b20nLCBjb21tb25BdG9tcyk7XG5kZWZpbmUoJ2tleXdvcmQnLCBjb21tb25LZXl3b3Jkcyk7XG5kZWZpbmUoJ2J1aWx0aW4nLCBjb21tb25Db21tYW5kcyk7XG5mdW5jdGlvbiB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHJldHVybiBudWxsO1xuICB2YXIgc29sID0gc3RyZWFtLnNvbCgpO1xuICB2YXIgY2ggPSBzdHJlYW0ubmV4dCgpO1xuICBpZiAoY2ggPT09ICdcXFxcJykge1xuICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbiAgaWYgKGNoID09PSAnXFwnJyB8fCBjaCA9PT0gJ1wiJyB8fCBjaCA9PT0gJ2AnKSB7XG4gICAgc3RhdGUudG9rZW5zLnVuc2hpZnQodG9rZW5TdHJpbmcoY2gsIGNoID09PSBcImBcIiA/IFwicXVvdGVcIiA6IFwic3RyaW5nXCIpKTtcbiAgICByZXR1cm4gdG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cbiAgaWYgKGNoID09PSAnIycpIHtcbiAgICBpZiAoc29sICYmIHN0cmVhbS5lYXQoJyEnKSkge1xuICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgcmV0dXJuICdtZXRhJzsgLy8gJ2NvbW1lbnQnP1xuICAgIH1cbiAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgcmV0dXJuICdjb21tZW50JztcbiAgfVxuICBpZiAoY2ggPT09ICckJykge1xuICAgIHN0YXRlLnRva2Vucy51bnNoaWZ0KHRva2VuRG9sbGFyKTtcbiAgICByZXR1cm4gdG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cbiAgaWYgKGNoID09PSAnKycgfHwgY2ggPT09ICc9Jykge1xuICAgIHJldHVybiAnb3BlcmF0b3InO1xuICB9XG4gIGlmIChjaCA9PT0gJy0nKSB7XG4gICAgc3RyZWFtLmVhdCgnLScpO1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvXFx3Lyk7XG4gICAgcmV0dXJuICdhdHRyaWJ1dGUnO1xuICB9XG4gIGlmIChjaCA9PSBcIjxcIikge1xuICAgIGlmIChzdHJlYW0ubWF0Y2goXCI8PFwiKSkgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgICB2YXIgaGVyZWRvYyA9IHN0cmVhbS5tYXRjaCgvXjwtP1xccyooPzpbJ1wiXShbXidcIl0qKVsnXCJdfChbXidcIlxcc10qKSkvKTtcbiAgICBpZiAoaGVyZWRvYykge1xuICAgICAgc3RhdGUudG9rZW5zLnVuc2hpZnQodG9rZW5IZXJlZG9jKGhlcmVkb2NbMV0gfHwgaGVyZWRvY1syXSkpO1xuICAgICAgcmV0dXJuICdzdHJpbmcuc3BlY2lhbCc7XG4gICAgfVxuICB9XG4gIGlmICgvXFxkLy50ZXN0KGNoKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZSgvXFxkLyk7XG4gICAgaWYgKHN0cmVhbS5lb2woKSB8fCAhL1xcdy8udGVzdChzdHJlYW0ucGVlaygpKSkge1xuICAgICAgcmV0dXJuICdudW1iZXInO1xuICAgIH1cbiAgfVxuICBzdHJlYW0uZWF0V2hpbGUoL1tcXHctXS8pO1xuICB2YXIgY3VyID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgaWYgKHN0cmVhbS5wZWVrKCkgPT09ICc9JyAmJiAvXFx3Ky8udGVzdChjdXIpKSByZXR1cm4gJ2RlZic7XG4gIHJldHVybiB3b3Jkcy5oYXNPd25Qcm9wZXJ0eShjdXIpID8gd29yZHNbY3VyXSA6IG51bGw7XG59XG5mdW5jdGlvbiB0b2tlblN0cmluZyhxdW90ZSwgc3R5bGUpIHtcbiAgdmFyIGNsb3NlID0gcXVvdGUgPT0gXCIoXCIgPyBcIilcIiA6IHF1b3RlID09IFwie1wiID8gXCJ9XCIgOiBxdW90ZTtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIG5leHQsXG4gICAgICBlc2NhcGVkID0gZmFsc2U7XG4gICAgd2hpbGUgKChuZXh0ID0gc3RyZWFtLm5leHQoKSkgIT0gbnVsbCkge1xuICAgICAgaWYgKG5leHQgPT09IGNsb3NlICYmICFlc2NhcGVkKSB7XG4gICAgICAgIHN0YXRlLnRva2Vucy5zaGlmdCgpO1xuICAgICAgICBicmVhaztcbiAgICAgIH0gZWxzZSBpZiAobmV4dCA9PT0gJyQnICYmICFlc2NhcGVkICYmIHF1b3RlICE9PSBcIidcIiAmJiBzdHJlYW0ucGVlaygpICE9IGNsb3NlKSB7XG4gICAgICAgIGVzY2FwZWQgPSB0cnVlO1xuICAgICAgICBzdHJlYW0uYmFja1VwKDEpO1xuICAgICAgICBzdGF0ZS50b2tlbnMudW5zaGlmdCh0b2tlbkRvbGxhcik7XG4gICAgICAgIGJyZWFrO1xuICAgICAgfSBlbHNlIGlmICghZXNjYXBlZCAmJiBxdW90ZSAhPT0gY2xvc2UgJiYgbmV4dCA9PT0gcXVvdGUpIHtcbiAgICAgICAgc3RhdGUudG9rZW5zLnVuc2hpZnQodG9rZW5TdHJpbmcocXVvdGUsIHN0eWxlKSk7XG4gICAgICAgIHJldHVybiB0b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgICAgIH0gZWxzZSBpZiAoIWVzY2FwZWQgJiYgL1snXCJdLy50ZXN0KG5leHQpICYmICEvWydcIl0vLnRlc3QocXVvdGUpKSB7XG4gICAgICAgIHN0YXRlLnRva2Vucy51bnNoaWZ0KHRva2VuU3RyaW5nU3RhcnQobmV4dCwgXCJzdHJpbmdcIikpO1xuICAgICAgICBzdHJlYW0uYmFja1VwKDEpO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBuZXh0ID09PSAnXFxcXCc7XG4gICAgfVxuICAgIHJldHVybiBzdHlsZTtcbiAgfTtcbn1cbjtcbmZ1bmN0aW9uIHRva2VuU3RyaW5nU3RhcnQocXVvdGUsIHN0eWxlKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHN0YXRlLnRva2Vuc1swXSA9IHRva2VuU3RyaW5nKHF1b3RlLCBzdHlsZSk7XG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICByZXR1cm4gdG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH07XG59XG52YXIgdG9rZW5Eb2xsYXIgPSBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAoc3RhdGUudG9rZW5zLmxlbmd0aCA+IDEpIHN0cmVhbS5lYXQoJyQnKTtcbiAgdmFyIGNoID0gc3RyZWFtLm5leHQoKTtcbiAgaWYgKC9bJ1wiKHtdLy50ZXN0KGNoKSkge1xuICAgIHN0YXRlLnRva2Vuc1swXSA9IHRva2VuU3RyaW5nKGNoLCBjaCA9PSBcIihcIiA/IFwicXVvdGVcIiA6IGNoID09IFwie1wiID8gXCJkZWZcIiA6IFwic3RyaW5nXCIpO1xuICAgIHJldHVybiB0b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgfVxuICBpZiAoIS9cXGQvLnRlc3QoY2gpKSBzdHJlYW0uZWF0V2hpbGUoL1xcdy8pO1xuICBzdGF0ZS50b2tlbnMuc2hpZnQoKTtcbiAgcmV0dXJuICdkZWYnO1xufTtcbmZ1bmN0aW9uIHRva2VuSGVyZWRvYyhkZWxpbSkge1xuICByZXR1cm4gZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLnNvbCgpICYmIHN0cmVhbS5zdHJpbmcgPT0gZGVsaW0pIHN0YXRlLnRva2Vucy5zaGlmdCgpO1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gXCJzdHJpbmcuc3BlY2lhbFwiO1xuICB9O1xufVxuZnVuY3Rpb24gdG9rZW5pemUoc3RyZWFtLCBzdGF0ZSkge1xuICByZXR1cm4gKHN0YXRlLnRva2Vuc1swXSB8fCB0b2tlbkJhc2UpKHN0cmVhbSwgc3RhdGUpO1xufVxuO1xuZXhwb3J0IGNvbnN0IHNoZWxsID0ge1xuICBuYW1lOiBcInNoZWxsXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgdG9rZW5zOiBbXVxuICAgIH07XG4gIH0sXG4gIHRva2VuOiBmdW5jdGlvbiAoc3RyZWFtLCBzdGF0ZSkge1xuICAgIHJldHVybiB0b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgYXV0b2NvbXBsZXRlOiBjb21tb25BdG9tcy5jb25jYXQoY29tbW9uS2V5d29yZHMsIGNvbW1vbkNvbW1hbmRzKSxcbiAgICBjbG9zZUJyYWNrZXRzOiB7XG4gICAgICBicmFja2V0czogW1wiKFwiLCBcIltcIiwgXCJ7XCIsIFwiJ1wiLCAnXCInLCBcImBcIl1cbiAgICB9LFxuICAgIGNvbW1lbnRUb2tlbnM6IHtcbiAgICAgIGxpbmU6IFwiI1wiXG4gICAgfVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=