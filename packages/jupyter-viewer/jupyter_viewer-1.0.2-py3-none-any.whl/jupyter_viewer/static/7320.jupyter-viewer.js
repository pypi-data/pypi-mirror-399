"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[7320],{

/***/ 97320
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   fortran: () => (/* binding */ fortran)
/* harmony export */ });
function words(array) {
  var keys = {};
  for (var i = 0; i < array.length; ++i) {
    keys[array[i]] = true;
  }
  return keys;
}
var keywords = words(["abstract", "accept", "allocatable", "allocate", "array", "assign", "asynchronous", "backspace", "bind", "block", "byte", "call", "case", "class", "close", "common", "contains", "continue", "cycle", "data", "deallocate", "decode", "deferred", "dimension", "do", "elemental", "else", "encode", "end", "endif", "entry", "enumerator", "equivalence", "exit", "external", "extrinsic", "final", "forall", "format", "function", "generic", "go", "goto", "if", "implicit", "import", "include", "inquire", "intent", "interface", "intrinsic", "module", "namelist", "non_intrinsic", "non_overridable", "none", "nopass", "nullify", "open", "optional", "options", "parameter", "pass", "pause", "pointer", "print", "private", "program", "protected", "public", "pure", "read", "recursive", "result", "return", "rewind", "save", "select", "sequence", "stop", "subroutine", "target", "then", "to", "type", "use", "value", "volatile", "where", "while", "write"]);
var builtins = words(["abort", "abs", "access", "achar", "acos", "adjustl", "adjustr", "aimag", "aint", "alarm", "all", "allocated", "alog", "amax", "amin", "amod", "and", "anint", "any", "asin", "associated", "atan", "besj", "besjn", "besy", "besyn", "bit_size", "btest", "cabs", "ccos", "ceiling", "cexp", "char", "chdir", "chmod", "clog", "cmplx", "command_argument_count", "complex", "conjg", "cos", "cosh", "count", "cpu_time", "cshift", "csin", "csqrt", "ctime", "c_funloc", "c_loc", "c_associated", "c_null_ptr", "c_null_funptr", "c_f_pointer", "c_null_char", "c_alert", "c_backspace", "c_form_feed", "c_new_line", "c_carriage_return", "c_horizontal_tab", "c_vertical_tab", "dabs", "dacos", "dasin", "datan", "date_and_time", "dbesj", "dbesj", "dbesjn", "dbesy", "dbesy", "dbesyn", "dble", "dcos", "dcosh", "ddim", "derf", "derfc", "dexp", "digits", "dim", "dint", "dlog", "dlog", "dmax", "dmin", "dmod", "dnint", "dot_product", "dprod", "dsign", "dsinh", "dsin", "dsqrt", "dtanh", "dtan", "dtime", "eoshift", "epsilon", "erf", "erfc", "etime", "exit", "exp", "exponent", "extends_type_of", "fdate", "fget", "fgetc", "float", "floor", "flush", "fnum", "fputc", "fput", "fraction", "fseek", "fstat", "ftell", "gerror", "getarg", "get_command", "get_command_argument", "get_environment_variable", "getcwd", "getenv", "getgid", "getlog", "getpid", "getuid", "gmtime", "hostnm", "huge", "iabs", "iachar", "iand", "iargc", "ibclr", "ibits", "ibset", "ichar", "idate", "idim", "idint", "idnint", "ieor", "ierrno", "ifix", "imag", "imagpart", "index", "int", "ior", "irand", "isatty", "ishft", "ishftc", "isign", "iso_c_binding", "is_iostat_end", "is_iostat_eor", "itime", "kill", "kind", "lbound", "len", "len_trim", "lge", "lgt", "link", "lle", "llt", "lnblnk", "loc", "log", "logical", "long", "lshift", "lstat", "ltime", "matmul", "max", "maxexponent", "maxloc", "maxval", "mclock", "merge", "move_alloc", "min", "minexponent", "minloc", "minval", "mod", "modulo", "mvbits", "nearest", "new_line", "nint", "not", "or", "pack", "perror", "precision", "present", "product", "radix", "rand", "random_number", "random_seed", "range", "real", "realpart", "rename", "repeat", "reshape", "rrspacing", "rshift", "same_type_as", "scale", "scan", "second", "selected_int_kind", "selected_real_kind", "set_exponent", "shape", "short", "sign", "signal", "sinh", "sin", "sleep", "sngl", "spacing", "spread", "sqrt", "srand", "stat", "sum", "symlnk", "system", "system_clock", "tan", "tanh", "time", "tiny", "transfer", "transpose", "trim", "ttynam", "ubound", "umask", "unlink", "unpack", "verify", "xor", "zabs", "zcos", "zexp", "zlog", "zsin", "zsqrt"]);
var dataTypes = words(["c_bool", "c_char", "c_double", "c_double_complex", "c_float", "c_float_complex", "c_funptr", "c_int", "c_int16_t", "c_int32_t", "c_int64_t", "c_int8_t", "c_int_fast16_t", "c_int_fast32_t", "c_int_fast64_t", "c_int_fast8_t", "c_int_least16_t", "c_int_least32_t", "c_int_least64_t", "c_int_least8_t", "c_intmax_t", "c_intptr_t", "c_long", "c_long_double", "c_long_double_complex", "c_long_long", "c_ptr", "c_short", "c_signed_char", "c_size_t", "character", "complex", "double", "integer", "logical", "real"]);
var isOperatorChar = /[+\-*&=<>\/\:]/;
var litOperator = /^\.(and|or|eq|lt|le|gt|ge|ne|not|eqv|neqv)\./i;
function tokenBase(stream, state) {
  if (stream.match(litOperator)) {
    return 'operator';
  }
  var ch = stream.next();
  if (ch == "!") {
    stream.skipToEnd();
    return "comment";
  }
  if (ch == '"' || ch == "'") {
    state.tokenize = tokenString(ch);
    return state.tokenize(stream, state);
  }
  if (/[\[\]\(\),]/.test(ch)) {
    return null;
  }
  if (/\d/.test(ch)) {
    stream.eatWhile(/[\w\.]/);
    return "number";
  }
  if (isOperatorChar.test(ch)) {
    stream.eatWhile(isOperatorChar);
    return "operator";
  }
  stream.eatWhile(/[\w\$_]/);
  var word = stream.current().toLowerCase();
  if (keywords.hasOwnProperty(word)) {
    return 'keyword';
  }
  if (builtins.hasOwnProperty(word) || dataTypes.hasOwnProperty(word)) {
    return 'builtin';
  }
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
      escaped = !escaped && next == "\\";
    }
    if (end || !escaped) state.tokenize = null;
    return "string";
  };
}

// Interface

const fortran = {
  name: "fortran",
  startState: function () {
    return {
      tokenize: null
    };
  },
  token: function (stream, state) {
    if (stream.eatSpace()) return null;
    var style = (state.tokenize || tokenBase)(stream, state);
    if (style == "comment" || style == "meta") return style;
    return style;
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNzMyMC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQSIsInNvdXJjZXMiOlsid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvQGNvZGVtaXJyb3IvbGVnYWN5LW1vZGVzL21vZGUvZm9ydHJhbi5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJmdW5jdGlvbiB3b3JkcyhhcnJheSkge1xuICB2YXIga2V5cyA9IHt9O1xuICBmb3IgKHZhciBpID0gMDsgaSA8IGFycmF5Lmxlbmd0aDsgKytpKSB7XG4gICAga2V5c1thcnJheVtpXV0gPSB0cnVlO1xuICB9XG4gIHJldHVybiBrZXlzO1xufVxudmFyIGtleXdvcmRzID0gd29yZHMoW1wiYWJzdHJhY3RcIiwgXCJhY2NlcHRcIiwgXCJhbGxvY2F0YWJsZVwiLCBcImFsbG9jYXRlXCIsIFwiYXJyYXlcIiwgXCJhc3NpZ25cIiwgXCJhc3luY2hyb25vdXNcIiwgXCJiYWNrc3BhY2VcIiwgXCJiaW5kXCIsIFwiYmxvY2tcIiwgXCJieXRlXCIsIFwiY2FsbFwiLCBcImNhc2VcIiwgXCJjbGFzc1wiLCBcImNsb3NlXCIsIFwiY29tbW9uXCIsIFwiY29udGFpbnNcIiwgXCJjb250aW51ZVwiLCBcImN5Y2xlXCIsIFwiZGF0YVwiLCBcImRlYWxsb2NhdGVcIiwgXCJkZWNvZGVcIiwgXCJkZWZlcnJlZFwiLCBcImRpbWVuc2lvblwiLCBcImRvXCIsIFwiZWxlbWVudGFsXCIsIFwiZWxzZVwiLCBcImVuY29kZVwiLCBcImVuZFwiLCBcImVuZGlmXCIsIFwiZW50cnlcIiwgXCJlbnVtZXJhdG9yXCIsIFwiZXF1aXZhbGVuY2VcIiwgXCJleGl0XCIsIFwiZXh0ZXJuYWxcIiwgXCJleHRyaW5zaWNcIiwgXCJmaW5hbFwiLCBcImZvcmFsbFwiLCBcImZvcm1hdFwiLCBcImZ1bmN0aW9uXCIsIFwiZ2VuZXJpY1wiLCBcImdvXCIsIFwiZ290b1wiLCBcImlmXCIsIFwiaW1wbGljaXRcIiwgXCJpbXBvcnRcIiwgXCJpbmNsdWRlXCIsIFwiaW5xdWlyZVwiLCBcImludGVudFwiLCBcImludGVyZmFjZVwiLCBcImludHJpbnNpY1wiLCBcIm1vZHVsZVwiLCBcIm5hbWVsaXN0XCIsIFwibm9uX2ludHJpbnNpY1wiLCBcIm5vbl9vdmVycmlkYWJsZVwiLCBcIm5vbmVcIiwgXCJub3Bhc3NcIiwgXCJudWxsaWZ5XCIsIFwib3BlblwiLCBcIm9wdGlvbmFsXCIsIFwib3B0aW9uc1wiLCBcInBhcmFtZXRlclwiLCBcInBhc3NcIiwgXCJwYXVzZVwiLCBcInBvaW50ZXJcIiwgXCJwcmludFwiLCBcInByaXZhdGVcIiwgXCJwcm9ncmFtXCIsIFwicHJvdGVjdGVkXCIsIFwicHVibGljXCIsIFwicHVyZVwiLCBcInJlYWRcIiwgXCJyZWN1cnNpdmVcIiwgXCJyZXN1bHRcIiwgXCJyZXR1cm5cIiwgXCJyZXdpbmRcIiwgXCJzYXZlXCIsIFwic2VsZWN0XCIsIFwic2VxdWVuY2VcIiwgXCJzdG9wXCIsIFwic3Vicm91dGluZVwiLCBcInRhcmdldFwiLCBcInRoZW5cIiwgXCJ0b1wiLCBcInR5cGVcIiwgXCJ1c2VcIiwgXCJ2YWx1ZVwiLCBcInZvbGF0aWxlXCIsIFwid2hlcmVcIiwgXCJ3aGlsZVwiLCBcIndyaXRlXCJdKTtcbnZhciBidWlsdGlucyA9IHdvcmRzKFtcImFib3J0XCIsIFwiYWJzXCIsIFwiYWNjZXNzXCIsIFwiYWNoYXJcIiwgXCJhY29zXCIsIFwiYWRqdXN0bFwiLCBcImFkanVzdHJcIiwgXCJhaW1hZ1wiLCBcImFpbnRcIiwgXCJhbGFybVwiLCBcImFsbFwiLCBcImFsbG9jYXRlZFwiLCBcImFsb2dcIiwgXCJhbWF4XCIsIFwiYW1pblwiLCBcImFtb2RcIiwgXCJhbmRcIiwgXCJhbmludFwiLCBcImFueVwiLCBcImFzaW5cIiwgXCJhc3NvY2lhdGVkXCIsIFwiYXRhblwiLCBcImJlc2pcIiwgXCJiZXNqblwiLCBcImJlc3lcIiwgXCJiZXN5blwiLCBcImJpdF9zaXplXCIsIFwiYnRlc3RcIiwgXCJjYWJzXCIsIFwiY2Nvc1wiLCBcImNlaWxpbmdcIiwgXCJjZXhwXCIsIFwiY2hhclwiLCBcImNoZGlyXCIsIFwiY2htb2RcIiwgXCJjbG9nXCIsIFwiY21wbHhcIiwgXCJjb21tYW5kX2FyZ3VtZW50X2NvdW50XCIsIFwiY29tcGxleFwiLCBcImNvbmpnXCIsIFwiY29zXCIsIFwiY29zaFwiLCBcImNvdW50XCIsIFwiY3B1X3RpbWVcIiwgXCJjc2hpZnRcIiwgXCJjc2luXCIsIFwiY3NxcnRcIiwgXCJjdGltZVwiLCBcImNfZnVubG9jXCIsIFwiY19sb2NcIiwgXCJjX2Fzc29jaWF0ZWRcIiwgXCJjX251bGxfcHRyXCIsIFwiY19udWxsX2Z1bnB0clwiLCBcImNfZl9wb2ludGVyXCIsIFwiY19udWxsX2NoYXJcIiwgXCJjX2FsZXJ0XCIsIFwiY19iYWNrc3BhY2VcIiwgXCJjX2Zvcm1fZmVlZFwiLCBcImNfbmV3X2xpbmVcIiwgXCJjX2NhcnJpYWdlX3JldHVyblwiLCBcImNfaG9yaXpvbnRhbF90YWJcIiwgXCJjX3ZlcnRpY2FsX3RhYlwiLCBcImRhYnNcIiwgXCJkYWNvc1wiLCBcImRhc2luXCIsIFwiZGF0YW5cIiwgXCJkYXRlX2FuZF90aW1lXCIsIFwiZGJlc2pcIiwgXCJkYmVzalwiLCBcImRiZXNqblwiLCBcImRiZXN5XCIsIFwiZGJlc3lcIiwgXCJkYmVzeW5cIiwgXCJkYmxlXCIsIFwiZGNvc1wiLCBcImRjb3NoXCIsIFwiZGRpbVwiLCBcImRlcmZcIiwgXCJkZXJmY1wiLCBcImRleHBcIiwgXCJkaWdpdHNcIiwgXCJkaW1cIiwgXCJkaW50XCIsIFwiZGxvZ1wiLCBcImRsb2dcIiwgXCJkbWF4XCIsIFwiZG1pblwiLCBcImRtb2RcIiwgXCJkbmludFwiLCBcImRvdF9wcm9kdWN0XCIsIFwiZHByb2RcIiwgXCJkc2lnblwiLCBcImRzaW5oXCIsIFwiZHNpblwiLCBcImRzcXJ0XCIsIFwiZHRhbmhcIiwgXCJkdGFuXCIsIFwiZHRpbWVcIiwgXCJlb3NoaWZ0XCIsIFwiZXBzaWxvblwiLCBcImVyZlwiLCBcImVyZmNcIiwgXCJldGltZVwiLCBcImV4aXRcIiwgXCJleHBcIiwgXCJleHBvbmVudFwiLCBcImV4dGVuZHNfdHlwZV9vZlwiLCBcImZkYXRlXCIsIFwiZmdldFwiLCBcImZnZXRjXCIsIFwiZmxvYXRcIiwgXCJmbG9vclwiLCBcImZsdXNoXCIsIFwiZm51bVwiLCBcImZwdXRjXCIsIFwiZnB1dFwiLCBcImZyYWN0aW9uXCIsIFwiZnNlZWtcIiwgXCJmc3RhdFwiLCBcImZ0ZWxsXCIsIFwiZ2Vycm9yXCIsIFwiZ2V0YXJnXCIsIFwiZ2V0X2NvbW1hbmRcIiwgXCJnZXRfY29tbWFuZF9hcmd1bWVudFwiLCBcImdldF9lbnZpcm9ubWVudF92YXJpYWJsZVwiLCBcImdldGN3ZFwiLCBcImdldGVudlwiLCBcImdldGdpZFwiLCBcImdldGxvZ1wiLCBcImdldHBpZFwiLCBcImdldHVpZFwiLCBcImdtdGltZVwiLCBcImhvc3RubVwiLCBcImh1Z2VcIiwgXCJpYWJzXCIsIFwiaWFjaGFyXCIsIFwiaWFuZFwiLCBcImlhcmdjXCIsIFwiaWJjbHJcIiwgXCJpYml0c1wiLCBcImlic2V0XCIsIFwiaWNoYXJcIiwgXCJpZGF0ZVwiLCBcImlkaW1cIiwgXCJpZGludFwiLCBcImlkbmludFwiLCBcImllb3JcIiwgXCJpZXJybm9cIiwgXCJpZml4XCIsIFwiaW1hZ1wiLCBcImltYWdwYXJ0XCIsIFwiaW5kZXhcIiwgXCJpbnRcIiwgXCJpb3JcIiwgXCJpcmFuZFwiLCBcImlzYXR0eVwiLCBcImlzaGZ0XCIsIFwiaXNoZnRjXCIsIFwiaXNpZ25cIiwgXCJpc29fY19iaW5kaW5nXCIsIFwiaXNfaW9zdGF0X2VuZFwiLCBcImlzX2lvc3RhdF9lb3JcIiwgXCJpdGltZVwiLCBcImtpbGxcIiwgXCJraW5kXCIsIFwibGJvdW5kXCIsIFwibGVuXCIsIFwibGVuX3RyaW1cIiwgXCJsZ2VcIiwgXCJsZ3RcIiwgXCJsaW5rXCIsIFwibGxlXCIsIFwibGx0XCIsIFwibG5ibG5rXCIsIFwibG9jXCIsIFwibG9nXCIsIFwibG9naWNhbFwiLCBcImxvbmdcIiwgXCJsc2hpZnRcIiwgXCJsc3RhdFwiLCBcImx0aW1lXCIsIFwibWF0bXVsXCIsIFwibWF4XCIsIFwibWF4ZXhwb25lbnRcIiwgXCJtYXhsb2NcIiwgXCJtYXh2YWxcIiwgXCJtY2xvY2tcIiwgXCJtZXJnZVwiLCBcIm1vdmVfYWxsb2NcIiwgXCJtaW5cIiwgXCJtaW5leHBvbmVudFwiLCBcIm1pbmxvY1wiLCBcIm1pbnZhbFwiLCBcIm1vZFwiLCBcIm1vZHVsb1wiLCBcIm12Yml0c1wiLCBcIm5lYXJlc3RcIiwgXCJuZXdfbGluZVwiLCBcIm5pbnRcIiwgXCJub3RcIiwgXCJvclwiLCBcInBhY2tcIiwgXCJwZXJyb3JcIiwgXCJwcmVjaXNpb25cIiwgXCJwcmVzZW50XCIsIFwicHJvZHVjdFwiLCBcInJhZGl4XCIsIFwicmFuZFwiLCBcInJhbmRvbV9udW1iZXJcIiwgXCJyYW5kb21fc2VlZFwiLCBcInJhbmdlXCIsIFwicmVhbFwiLCBcInJlYWxwYXJ0XCIsIFwicmVuYW1lXCIsIFwicmVwZWF0XCIsIFwicmVzaGFwZVwiLCBcInJyc3BhY2luZ1wiLCBcInJzaGlmdFwiLCBcInNhbWVfdHlwZV9hc1wiLCBcInNjYWxlXCIsIFwic2NhblwiLCBcInNlY29uZFwiLCBcInNlbGVjdGVkX2ludF9raW5kXCIsIFwic2VsZWN0ZWRfcmVhbF9raW5kXCIsIFwic2V0X2V4cG9uZW50XCIsIFwic2hhcGVcIiwgXCJzaG9ydFwiLCBcInNpZ25cIiwgXCJzaWduYWxcIiwgXCJzaW5oXCIsIFwic2luXCIsIFwic2xlZXBcIiwgXCJzbmdsXCIsIFwic3BhY2luZ1wiLCBcInNwcmVhZFwiLCBcInNxcnRcIiwgXCJzcmFuZFwiLCBcInN0YXRcIiwgXCJzdW1cIiwgXCJzeW1sbmtcIiwgXCJzeXN0ZW1cIiwgXCJzeXN0ZW1fY2xvY2tcIiwgXCJ0YW5cIiwgXCJ0YW5oXCIsIFwidGltZVwiLCBcInRpbnlcIiwgXCJ0cmFuc2ZlclwiLCBcInRyYW5zcG9zZVwiLCBcInRyaW1cIiwgXCJ0dHluYW1cIiwgXCJ1Ym91bmRcIiwgXCJ1bWFza1wiLCBcInVubGlua1wiLCBcInVucGFja1wiLCBcInZlcmlmeVwiLCBcInhvclwiLCBcInphYnNcIiwgXCJ6Y29zXCIsIFwiemV4cFwiLCBcInpsb2dcIiwgXCJ6c2luXCIsIFwienNxcnRcIl0pO1xudmFyIGRhdGFUeXBlcyA9IHdvcmRzKFtcImNfYm9vbFwiLCBcImNfY2hhclwiLCBcImNfZG91YmxlXCIsIFwiY19kb3VibGVfY29tcGxleFwiLCBcImNfZmxvYXRcIiwgXCJjX2Zsb2F0X2NvbXBsZXhcIiwgXCJjX2Z1bnB0clwiLCBcImNfaW50XCIsIFwiY19pbnQxNl90XCIsIFwiY19pbnQzMl90XCIsIFwiY19pbnQ2NF90XCIsIFwiY19pbnQ4X3RcIiwgXCJjX2ludF9mYXN0MTZfdFwiLCBcImNfaW50X2Zhc3QzMl90XCIsIFwiY19pbnRfZmFzdDY0X3RcIiwgXCJjX2ludF9mYXN0OF90XCIsIFwiY19pbnRfbGVhc3QxNl90XCIsIFwiY19pbnRfbGVhc3QzMl90XCIsIFwiY19pbnRfbGVhc3Q2NF90XCIsIFwiY19pbnRfbGVhc3Q4X3RcIiwgXCJjX2ludG1heF90XCIsIFwiY19pbnRwdHJfdFwiLCBcImNfbG9uZ1wiLCBcImNfbG9uZ19kb3VibGVcIiwgXCJjX2xvbmdfZG91YmxlX2NvbXBsZXhcIiwgXCJjX2xvbmdfbG9uZ1wiLCBcImNfcHRyXCIsIFwiY19zaG9ydFwiLCBcImNfc2lnbmVkX2NoYXJcIiwgXCJjX3NpemVfdFwiLCBcImNoYXJhY3RlclwiLCBcImNvbXBsZXhcIiwgXCJkb3VibGVcIiwgXCJpbnRlZ2VyXCIsIFwibG9naWNhbFwiLCBcInJlYWxcIl0pO1xudmFyIGlzT3BlcmF0b3JDaGFyID0gL1srXFwtKiY9PD5cXC9cXDpdLztcbnZhciBsaXRPcGVyYXRvciA9IC9eXFwuKGFuZHxvcnxlcXxsdHxsZXxndHxnZXxuZXxub3R8ZXF2fG5lcXYpXFwuL2k7XG5mdW5jdGlvbiB0b2tlbkJhc2Uoc3RyZWFtLCBzdGF0ZSkge1xuICBpZiAoc3RyZWFtLm1hdGNoKGxpdE9wZXJhdG9yKSkge1xuICAgIHJldHVybiAnb3BlcmF0b3InO1xuICB9XG4gIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gIGlmIChjaCA9PSBcIiFcIikge1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH1cbiAgaWYgKGNoID09ICdcIicgfHwgY2ggPT0gXCInXCIpIHtcbiAgICBzdGF0ZS50b2tlbml6ZSA9IHRva2VuU3RyaW5nKGNoKTtcbiAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cbiAgaWYgKC9bXFxbXFxdXFwoXFwpLF0vLnRlc3QoY2gpKSB7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbiAgaWYgKC9cXGQvLnRlc3QoY2gpKSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFwuXS8pO1xuICAgIHJldHVybiBcIm51bWJlclwiO1xuICB9XG4gIGlmIChpc09wZXJhdG9yQ2hhci50ZXN0KGNoKSkge1xuICAgIHN0cmVhbS5lYXRXaGlsZShpc09wZXJhdG9yQ2hhcik7XG4gICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgfVxuICBzdHJlYW0uZWF0V2hpbGUoL1tcXHdcXCRfXS8pO1xuICB2YXIgd29yZCA9IHN0cmVhbS5jdXJyZW50KCkudG9Mb3dlckNhc2UoKTtcbiAgaWYgKGtleXdvcmRzLmhhc093blByb3BlcnR5KHdvcmQpKSB7XG4gICAgcmV0dXJuICdrZXl3b3JkJztcbiAgfVxuICBpZiAoYnVpbHRpbnMuaGFzT3duUHJvcGVydHkod29yZCkgfHwgZGF0YVR5cGVzLmhhc093blByb3BlcnR5KHdvcmQpKSB7XG4gICAgcmV0dXJuICdidWlsdGluJztcbiAgfVxuICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xufVxuZnVuY3Rpb24gdG9rZW5TdHJpbmcocXVvdGUpIHtcbiAgcmV0dXJuIGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgdmFyIGVzY2FwZWQgPSBmYWxzZSxcbiAgICAgIG5leHQsXG4gICAgICBlbmQgPSBmYWxzZTtcbiAgICB3aGlsZSAoKG5leHQgPSBzdHJlYW0ubmV4dCgpKSAhPSBudWxsKSB7XG4gICAgICBpZiAobmV4dCA9PSBxdW90ZSAmJiAhZXNjYXBlZCkge1xuICAgICAgICBlbmQgPSB0cnVlO1xuICAgICAgICBicmVhaztcbiAgICAgIH1cbiAgICAgIGVzY2FwZWQgPSAhZXNjYXBlZCAmJiBuZXh0ID09IFwiXFxcXFwiO1xuICAgIH1cbiAgICBpZiAoZW5kIHx8ICFlc2NhcGVkKSBzdGF0ZS50b2tlbml6ZSA9IG51bGw7XG4gICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gIH07XG59XG5cbi8vIEludGVyZmFjZVxuXG5leHBvcnQgY29uc3QgZm9ydHJhbiA9IHtcbiAgbmFtZTogXCJmb3J0cmFuXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgdG9rZW5pemU6IG51bGxcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHJldHVybiBudWxsO1xuICAgIHZhciBzdHlsZSA9IChzdGF0ZS50b2tlbml6ZSB8fCB0b2tlbkJhc2UpKHN0cmVhbSwgc3RhdGUpO1xuICAgIGlmIChzdHlsZSA9PSBcImNvbW1lbnRcIiB8fCBzdHlsZSA9PSBcIm1ldGFcIikgcmV0dXJuIHN0eWxlO1xuICAgIHJldHVybiBzdHlsZTtcbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9