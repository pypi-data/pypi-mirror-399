"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[2412],{

/***/ 62412
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   asterisk: () => (/* binding */ asterisk)
/* harmony export */ });
var atoms = ["exten", "same", "include", "ignorepat", "switch"],
  dpcmd = ["#include", "#exec"],
  apps = ["addqueuemember", "adsiprog", "aelsub", "agentlogin", "agentmonitoroutgoing", "agi", "alarmreceiver", "amd", "answer", "authenticate", "background", "backgrounddetect", "bridge", "busy", "callcompletioncancel", "callcompletionrequest", "celgenuserevent", "changemonitor", "chanisavail", "channelredirect", "chanspy", "clearhash", "confbridge", "congestion", "continuewhile", "controlplayback", "dahdiacceptr2call", "dahdibarge", "dahdiras", "dahdiscan", "dahdisendcallreroutingfacility", "dahdisendkeypadfacility", "datetime", "dbdel", "dbdeltree", "deadagi", "dial", "dictate", "directory", "disa", "dumpchan", "eagi", "echo", "endwhile", "exec", "execif", "execiftime", "exitwhile", "extenspy", "externalivr", "festival", "flash", "followme", "forkcdr", "getcpeid", "gosub", "gosubif", "goto", "gotoif", "gotoiftime", "hangup", "iax2provision", "ices", "importvar", "incomplete", "ivrdemo", "jabberjoin", "jabberleave", "jabbersend", "jabbersendgroup", "jabberstatus", "jack", "log", "macro", "macroexclusive", "macroexit", "macroif", "mailboxexists", "meetme", "meetmeadmin", "meetmechanneladmin", "meetmecount", "milliwatt", "minivmaccmess", "minivmdelete", "minivmgreet", "minivmmwi", "minivmnotify", "minivmrecord", "mixmonitor", "monitor", "morsecode", "mp3player", "mset", "musiconhold", "nbscat", "nocdr", "noop", "odbc", "odbc", "odbcfinish", "originate", "ospauth", "ospfinish", "osplookup", "ospnext", "page", "park", "parkandannounce", "parkedcall", "pausemonitor", "pausequeuemember", "pickup", "pickupchan", "playback", "playtones", "privacymanager", "proceeding", "progress", "queue", "queuelog", "raiseexception", "read", "readexten", "readfile", "receivefax", "receivefax", "receivefax", "record", "removequeuemember", "resetcdr", "retrydial", "return", "ringing", "sayalpha", "saycountedadj", "saycountednoun", "saycountpl", "saydigits", "saynumber", "sayphonetic", "sayunixtime", "senddtmf", "sendfax", "sendfax", "sendfax", "sendimage", "sendtext", "sendurl", "set", "setamaflags", "setcallerpres", "setmusiconhold", "sipaddheader", "sipdtmfmode", "sipremoveheader", "skel", "slastation", "slatrunk", "sms", "softhangup", "speechactivategrammar", "speechbackground", "speechcreate", "speechdeactivategrammar", "speechdestroy", "speechloadgrammar", "speechprocessingsound", "speechstart", "speechunloadgrammar", "stackpop", "startmusiconhold", "stopmixmonitor", "stopmonitor", "stopmusiconhold", "stopplaytones", "system", "testclient", "testserver", "transfer", "tryexec", "trysystem", "unpausemonitor", "unpausequeuemember", "userevent", "verbose", "vmauthenticate", "vmsayname", "voicemail", "voicemailmain", "wait", "waitexten", "waitfornoise", "waitforring", "waitforsilence", "waitmusiconhold", "waituntil", "while", "zapateller"];
function basicToken(stream, state) {
  var cur = '';
  var ch = stream.next();
  // comment
  if (state.blockComment) {
    if (ch == "-" && stream.match("-;", true)) {
      state.blockComment = false;
    } else if (stream.skipTo("--;")) {
      stream.next();
      stream.next();
      stream.next();
      state.blockComment = false;
    } else {
      stream.skipToEnd();
    }
    return "comment";
  }
  if (ch == ";") {
    if (stream.match("--", true)) {
      if (!stream.match("-", false)) {
        // Except ;--- is not a block comment
        state.blockComment = true;
        return "comment";
      }
    }
    stream.skipToEnd();
    return "comment";
  }
  // context
  if (ch == '[') {
    stream.skipTo(']');
    stream.eat(']');
    return "header";
  }
  // string
  if (ch == '"') {
    stream.skipTo('"');
    return "string";
  }
  if (ch == "'") {
    stream.skipTo("'");
    return "string.special";
  }
  // dialplan commands
  if (ch == '#') {
    stream.eatWhile(/\w/);
    cur = stream.current();
    if (dpcmd.indexOf(cur) !== -1) {
      stream.skipToEnd();
      return "strong";
    }
  }
  // application args
  if (ch == '$') {
    var ch1 = stream.peek();
    if (ch1 == '{') {
      stream.skipTo('}');
      stream.eat('}');
      return "variableName.special";
    }
  }
  // extension
  stream.eatWhile(/\w/);
  cur = stream.current();
  if (atoms.indexOf(cur) !== -1) {
    state.extenStart = true;
    switch (cur) {
      case 'same':
        state.extenSame = true;
        break;
      case 'include':
      case 'switch':
      case 'ignorepat':
        state.extenInclude = true;
        break;
      default:
        break;
    }
    return "atom";
  }
}
const asterisk = {
  name: "asterisk",
  startState: function () {
    return {
      blockComment: false,
      extenStart: false,
      extenSame: false,
      extenInclude: false,
      extenExten: false,
      extenPriority: false,
      extenApplication: false
    };
  },
  token: function (stream, state) {
    var cur = '';
    if (stream.eatSpace()) return null;
    // extension started
    if (state.extenStart) {
      stream.eatWhile(/[^\s]/);
      cur = stream.current();
      if (/^=>?$/.test(cur)) {
        state.extenExten = true;
        state.extenStart = false;
        return "strong";
      } else {
        state.extenStart = false;
        stream.skipToEnd();
        return "error";
      }
    } else if (state.extenExten) {
      // set exten and priority
      state.extenExten = false;
      state.extenPriority = true;
      stream.eatWhile(/[^,]/);
      if (state.extenInclude) {
        stream.skipToEnd();
        state.extenPriority = false;
        state.extenInclude = false;
      }
      if (state.extenSame) {
        state.extenPriority = false;
        state.extenSame = false;
        state.extenApplication = true;
      }
      return "tag";
    } else if (state.extenPriority) {
      state.extenPriority = false;
      state.extenApplication = true;
      stream.next(); // get comma
      if (state.extenSame) return null;
      stream.eatWhile(/[^,]/);
      return "number";
    } else if (state.extenApplication) {
      stream.eatWhile(/,/);
      cur = stream.current();
      if (cur === ',') return null;
      stream.eatWhile(/\w/);
      cur = stream.current().toLowerCase();
      state.extenApplication = false;
      if (apps.indexOf(cur) !== -1) {
        return "def";
      }
    } else {
      return basicToken(stream, state);
    }
    return null;
  },
  languageData: {
    commentTokens: {
      line: ";",
      block: {
        open: ";--",
        close: "--;"
      }
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMjQxMi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9hc3Rlcmlzay5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJ2YXIgYXRvbXMgPSBbXCJleHRlblwiLCBcInNhbWVcIiwgXCJpbmNsdWRlXCIsIFwiaWdub3JlcGF0XCIsIFwic3dpdGNoXCJdLFxuICBkcGNtZCA9IFtcIiNpbmNsdWRlXCIsIFwiI2V4ZWNcIl0sXG4gIGFwcHMgPSBbXCJhZGRxdWV1ZW1lbWJlclwiLCBcImFkc2lwcm9nXCIsIFwiYWVsc3ViXCIsIFwiYWdlbnRsb2dpblwiLCBcImFnZW50bW9uaXRvcm91dGdvaW5nXCIsIFwiYWdpXCIsIFwiYWxhcm1yZWNlaXZlclwiLCBcImFtZFwiLCBcImFuc3dlclwiLCBcImF1dGhlbnRpY2F0ZVwiLCBcImJhY2tncm91bmRcIiwgXCJiYWNrZ3JvdW5kZGV0ZWN0XCIsIFwiYnJpZGdlXCIsIFwiYnVzeVwiLCBcImNhbGxjb21wbGV0aW9uY2FuY2VsXCIsIFwiY2FsbGNvbXBsZXRpb25yZXF1ZXN0XCIsIFwiY2VsZ2VudXNlcmV2ZW50XCIsIFwiY2hhbmdlbW9uaXRvclwiLCBcImNoYW5pc2F2YWlsXCIsIFwiY2hhbm5lbHJlZGlyZWN0XCIsIFwiY2hhbnNweVwiLCBcImNsZWFyaGFzaFwiLCBcImNvbmZicmlkZ2VcIiwgXCJjb25nZXN0aW9uXCIsIFwiY29udGludWV3aGlsZVwiLCBcImNvbnRyb2xwbGF5YmFja1wiLCBcImRhaGRpYWNjZXB0cjJjYWxsXCIsIFwiZGFoZGliYXJnZVwiLCBcImRhaGRpcmFzXCIsIFwiZGFoZGlzY2FuXCIsIFwiZGFoZGlzZW5kY2FsbHJlcm91dGluZ2ZhY2lsaXR5XCIsIFwiZGFoZGlzZW5ka2V5cGFkZmFjaWxpdHlcIiwgXCJkYXRldGltZVwiLCBcImRiZGVsXCIsIFwiZGJkZWx0cmVlXCIsIFwiZGVhZGFnaVwiLCBcImRpYWxcIiwgXCJkaWN0YXRlXCIsIFwiZGlyZWN0b3J5XCIsIFwiZGlzYVwiLCBcImR1bXBjaGFuXCIsIFwiZWFnaVwiLCBcImVjaG9cIiwgXCJlbmR3aGlsZVwiLCBcImV4ZWNcIiwgXCJleGVjaWZcIiwgXCJleGVjaWZ0aW1lXCIsIFwiZXhpdHdoaWxlXCIsIFwiZXh0ZW5zcHlcIiwgXCJleHRlcm5hbGl2clwiLCBcImZlc3RpdmFsXCIsIFwiZmxhc2hcIiwgXCJmb2xsb3dtZVwiLCBcImZvcmtjZHJcIiwgXCJnZXRjcGVpZFwiLCBcImdvc3ViXCIsIFwiZ29zdWJpZlwiLCBcImdvdG9cIiwgXCJnb3RvaWZcIiwgXCJnb3RvaWZ0aW1lXCIsIFwiaGFuZ3VwXCIsIFwiaWF4MnByb3Zpc2lvblwiLCBcImljZXNcIiwgXCJpbXBvcnR2YXJcIiwgXCJpbmNvbXBsZXRlXCIsIFwiaXZyZGVtb1wiLCBcImphYmJlcmpvaW5cIiwgXCJqYWJiZXJsZWF2ZVwiLCBcImphYmJlcnNlbmRcIiwgXCJqYWJiZXJzZW5kZ3JvdXBcIiwgXCJqYWJiZXJzdGF0dXNcIiwgXCJqYWNrXCIsIFwibG9nXCIsIFwibWFjcm9cIiwgXCJtYWNyb2V4Y2x1c2l2ZVwiLCBcIm1hY3JvZXhpdFwiLCBcIm1hY3JvaWZcIiwgXCJtYWlsYm94ZXhpc3RzXCIsIFwibWVldG1lXCIsIFwibWVldG1lYWRtaW5cIiwgXCJtZWV0bWVjaGFubmVsYWRtaW5cIiwgXCJtZWV0bWVjb3VudFwiLCBcIm1pbGxpd2F0dFwiLCBcIm1pbml2bWFjY21lc3NcIiwgXCJtaW5pdm1kZWxldGVcIiwgXCJtaW5pdm1ncmVldFwiLCBcIm1pbml2bW13aVwiLCBcIm1pbml2bW5vdGlmeVwiLCBcIm1pbml2bXJlY29yZFwiLCBcIm1peG1vbml0b3JcIiwgXCJtb25pdG9yXCIsIFwibW9yc2Vjb2RlXCIsIFwibXAzcGxheWVyXCIsIFwibXNldFwiLCBcIm11c2ljb25ob2xkXCIsIFwibmJzY2F0XCIsIFwibm9jZHJcIiwgXCJub29wXCIsIFwib2RiY1wiLCBcIm9kYmNcIiwgXCJvZGJjZmluaXNoXCIsIFwib3JpZ2luYXRlXCIsIFwib3NwYXV0aFwiLCBcIm9zcGZpbmlzaFwiLCBcIm9zcGxvb2t1cFwiLCBcIm9zcG5leHRcIiwgXCJwYWdlXCIsIFwicGFya1wiLCBcInBhcmthbmRhbm5vdW5jZVwiLCBcInBhcmtlZGNhbGxcIiwgXCJwYXVzZW1vbml0b3JcIiwgXCJwYXVzZXF1ZXVlbWVtYmVyXCIsIFwicGlja3VwXCIsIFwicGlja3VwY2hhblwiLCBcInBsYXliYWNrXCIsIFwicGxheXRvbmVzXCIsIFwicHJpdmFjeW1hbmFnZXJcIiwgXCJwcm9jZWVkaW5nXCIsIFwicHJvZ3Jlc3NcIiwgXCJxdWV1ZVwiLCBcInF1ZXVlbG9nXCIsIFwicmFpc2VleGNlcHRpb25cIiwgXCJyZWFkXCIsIFwicmVhZGV4dGVuXCIsIFwicmVhZGZpbGVcIiwgXCJyZWNlaXZlZmF4XCIsIFwicmVjZWl2ZWZheFwiLCBcInJlY2VpdmVmYXhcIiwgXCJyZWNvcmRcIiwgXCJyZW1vdmVxdWV1ZW1lbWJlclwiLCBcInJlc2V0Y2RyXCIsIFwicmV0cnlkaWFsXCIsIFwicmV0dXJuXCIsIFwicmluZ2luZ1wiLCBcInNheWFscGhhXCIsIFwic2F5Y291bnRlZGFkalwiLCBcInNheWNvdW50ZWRub3VuXCIsIFwic2F5Y291bnRwbFwiLCBcInNheWRpZ2l0c1wiLCBcInNheW51bWJlclwiLCBcInNheXBob25ldGljXCIsIFwic2F5dW5peHRpbWVcIiwgXCJzZW5kZHRtZlwiLCBcInNlbmRmYXhcIiwgXCJzZW5kZmF4XCIsIFwic2VuZGZheFwiLCBcInNlbmRpbWFnZVwiLCBcInNlbmR0ZXh0XCIsIFwic2VuZHVybFwiLCBcInNldFwiLCBcInNldGFtYWZsYWdzXCIsIFwic2V0Y2FsbGVycHJlc1wiLCBcInNldG11c2ljb25ob2xkXCIsIFwic2lwYWRkaGVhZGVyXCIsIFwic2lwZHRtZm1vZGVcIiwgXCJzaXByZW1vdmVoZWFkZXJcIiwgXCJza2VsXCIsIFwic2xhc3RhdGlvblwiLCBcInNsYXRydW5rXCIsIFwic21zXCIsIFwic29mdGhhbmd1cFwiLCBcInNwZWVjaGFjdGl2YXRlZ3JhbW1hclwiLCBcInNwZWVjaGJhY2tncm91bmRcIiwgXCJzcGVlY2hjcmVhdGVcIiwgXCJzcGVlY2hkZWFjdGl2YXRlZ3JhbW1hclwiLCBcInNwZWVjaGRlc3Ryb3lcIiwgXCJzcGVlY2hsb2FkZ3JhbW1hclwiLCBcInNwZWVjaHByb2Nlc3Npbmdzb3VuZFwiLCBcInNwZWVjaHN0YXJ0XCIsIFwic3BlZWNodW5sb2FkZ3JhbW1hclwiLCBcInN0YWNrcG9wXCIsIFwic3RhcnRtdXNpY29uaG9sZFwiLCBcInN0b3BtaXhtb25pdG9yXCIsIFwic3RvcG1vbml0b3JcIiwgXCJzdG9wbXVzaWNvbmhvbGRcIiwgXCJzdG9wcGxheXRvbmVzXCIsIFwic3lzdGVtXCIsIFwidGVzdGNsaWVudFwiLCBcInRlc3RzZXJ2ZXJcIiwgXCJ0cmFuc2ZlclwiLCBcInRyeWV4ZWNcIiwgXCJ0cnlzeXN0ZW1cIiwgXCJ1bnBhdXNlbW9uaXRvclwiLCBcInVucGF1c2VxdWV1ZW1lbWJlclwiLCBcInVzZXJldmVudFwiLCBcInZlcmJvc2VcIiwgXCJ2bWF1dGhlbnRpY2F0ZVwiLCBcInZtc2F5bmFtZVwiLCBcInZvaWNlbWFpbFwiLCBcInZvaWNlbWFpbG1haW5cIiwgXCJ3YWl0XCIsIFwid2FpdGV4dGVuXCIsIFwid2FpdGZvcm5vaXNlXCIsIFwid2FpdGZvcnJpbmdcIiwgXCJ3YWl0Zm9yc2lsZW5jZVwiLCBcIndhaXRtdXNpY29uaG9sZFwiLCBcIndhaXR1bnRpbFwiLCBcIndoaWxlXCIsIFwiemFwYXRlbGxlclwiXTtcbmZ1bmN0aW9uIGJhc2ljVG9rZW4oc3RyZWFtLCBzdGF0ZSkge1xuICB2YXIgY3VyID0gJyc7XG4gIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gIC8vIGNvbW1lbnRcbiAgaWYgKHN0YXRlLmJsb2NrQ29tbWVudCkge1xuICAgIGlmIChjaCA9PSBcIi1cIiAmJiBzdHJlYW0ubWF0Y2goXCItO1wiLCB0cnVlKSkge1xuICAgICAgc3RhdGUuYmxvY2tDb21tZW50ID0gZmFsc2U7XG4gICAgfSBlbHNlIGlmIChzdHJlYW0uc2tpcFRvKFwiLS07XCIpKSB7XG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICBzdGF0ZS5ibG9ja0NvbW1lbnQgPSBmYWxzZTtcbiAgICB9IGVsc2Uge1xuICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgIH1cbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH1cbiAgaWYgKGNoID09IFwiO1wiKSB7XG4gICAgaWYgKHN0cmVhbS5tYXRjaChcIi0tXCIsIHRydWUpKSB7XG4gICAgICBpZiAoIXN0cmVhbS5tYXRjaChcIi1cIiwgZmFsc2UpKSB7XG4gICAgICAgIC8vIEV4Y2VwdCA7LS0tIGlzIG5vdCBhIGJsb2NrIGNvbW1lbnRcbiAgICAgICAgc3RhdGUuYmxvY2tDb21tZW50ID0gdHJ1ZTtcbiAgICAgICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICAgICAgfVxuICAgIH1cbiAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgcmV0dXJuIFwiY29tbWVudFwiO1xuICB9XG4gIC8vIGNvbnRleHRcbiAgaWYgKGNoID09ICdbJykge1xuICAgIHN0cmVhbS5za2lwVG8oJ10nKTtcbiAgICBzdHJlYW0uZWF0KCddJyk7XG4gICAgcmV0dXJuIFwiaGVhZGVyXCI7XG4gIH1cbiAgLy8gc3RyaW5nXG4gIGlmIChjaCA9PSAnXCInKSB7XG4gICAgc3RyZWFtLnNraXBUbygnXCInKTtcbiAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgfVxuICBpZiAoY2ggPT0gXCInXCIpIHtcbiAgICBzdHJlYW0uc2tpcFRvKFwiJ1wiKTtcbiAgICByZXR1cm4gXCJzdHJpbmcuc3BlY2lhbFwiO1xuICB9XG4gIC8vIGRpYWxwbGFuIGNvbW1hbmRzXG4gIGlmIChjaCA9PSAnIycpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1xcdy8pO1xuICAgIGN1ciA9IHN0cmVhbS5jdXJyZW50KCk7XG4gICAgaWYgKGRwY21kLmluZGV4T2YoY3VyKSAhPT0gLTEpIHtcbiAgICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICAgIHJldHVybiBcInN0cm9uZ1wiO1xuICAgIH1cbiAgfVxuICAvLyBhcHBsaWNhdGlvbiBhcmdzXG4gIGlmIChjaCA9PSAnJCcpIHtcbiAgICB2YXIgY2gxID0gc3RyZWFtLnBlZWsoKTtcbiAgICBpZiAoY2gxID09ICd7Jykge1xuICAgICAgc3RyZWFtLnNraXBUbygnfScpO1xuICAgICAgc3RyZWFtLmVhdCgnfScpO1xuICAgICAgcmV0dXJuIFwidmFyaWFibGVOYW1lLnNwZWNpYWxcIjtcbiAgICB9XG4gIH1cbiAgLy8gZXh0ZW5zaW9uXG4gIHN0cmVhbS5lYXRXaGlsZSgvXFx3Lyk7XG4gIGN1ciA9IHN0cmVhbS5jdXJyZW50KCk7XG4gIGlmIChhdG9tcy5pbmRleE9mKGN1cikgIT09IC0xKSB7XG4gICAgc3RhdGUuZXh0ZW5TdGFydCA9IHRydWU7XG4gICAgc3dpdGNoIChjdXIpIHtcbiAgICAgIGNhc2UgJ3NhbWUnOlxuICAgICAgICBzdGF0ZS5leHRlblNhbWUgPSB0cnVlO1xuICAgICAgICBicmVhaztcbiAgICAgIGNhc2UgJ2luY2x1ZGUnOlxuICAgICAgY2FzZSAnc3dpdGNoJzpcbiAgICAgIGNhc2UgJ2lnbm9yZXBhdCc6XG4gICAgICAgIHN0YXRlLmV4dGVuSW5jbHVkZSA9IHRydWU7XG4gICAgICAgIGJyZWFrO1xuICAgICAgZGVmYXVsdDpcbiAgICAgICAgYnJlYWs7XG4gICAgfVxuICAgIHJldHVybiBcImF0b21cIjtcbiAgfVxufVxuZXhwb3J0IGNvbnN0IGFzdGVyaXNrID0ge1xuICBuYW1lOiBcImFzdGVyaXNrXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgYmxvY2tDb21tZW50OiBmYWxzZSxcbiAgICAgIGV4dGVuU3RhcnQ6IGZhbHNlLFxuICAgICAgZXh0ZW5TYW1lOiBmYWxzZSxcbiAgICAgIGV4dGVuSW5jbHVkZTogZmFsc2UsXG4gICAgICBleHRlbkV4dGVuOiBmYWxzZSxcbiAgICAgIGV4dGVuUHJpb3JpdHk6IGZhbHNlLFxuICAgICAgZXh0ZW5BcHBsaWNhdGlvbjogZmFsc2VcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICB2YXIgY3VyID0gJyc7XG4gICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgICAvLyBleHRlbnNpb24gc3RhcnRlZFxuICAgIGlmIChzdGF0ZS5leHRlblN0YXJ0KSB7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1teXFxzXS8pO1xuICAgICAgY3VyID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgICAgIGlmICgvXj0+PyQvLnRlc3QoY3VyKSkge1xuICAgICAgICBzdGF0ZS5leHRlbkV4dGVuID0gdHJ1ZTtcbiAgICAgICAgc3RhdGUuZXh0ZW5TdGFydCA9IGZhbHNlO1xuICAgICAgICByZXR1cm4gXCJzdHJvbmdcIjtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIHN0YXRlLmV4dGVuU3RhcnQgPSBmYWxzZTtcbiAgICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgICByZXR1cm4gXCJlcnJvclwiO1xuICAgICAgfVxuICAgIH0gZWxzZSBpZiAoc3RhdGUuZXh0ZW5FeHRlbikge1xuICAgICAgLy8gc2V0IGV4dGVuIGFuZCBwcmlvcml0eVxuICAgICAgc3RhdGUuZXh0ZW5FeHRlbiA9IGZhbHNlO1xuICAgICAgc3RhdGUuZXh0ZW5Qcmlvcml0eSA9IHRydWU7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1teLF0vKTtcbiAgICAgIGlmIChzdGF0ZS5leHRlbkluY2x1ZGUpIHtcbiAgICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgICAgICBzdGF0ZS5leHRlblByaW9yaXR5ID0gZmFsc2U7XG4gICAgICAgIHN0YXRlLmV4dGVuSW5jbHVkZSA9IGZhbHNlO1xuICAgICAgfVxuICAgICAgaWYgKHN0YXRlLmV4dGVuU2FtZSkge1xuICAgICAgICBzdGF0ZS5leHRlblByaW9yaXR5ID0gZmFsc2U7XG4gICAgICAgIHN0YXRlLmV4dGVuU2FtZSA9IGZhbHNlO1xuICAgICAgICBzdGF0ZS5leHRlbkFwcGxpY2F0aW9uID0gdHJ1ZTtcbiAgICAgIH1cbiAgICAgIHJldHVybiBcInRhZ1wiO1xuICAgIH0gZWxzZSBpZiAoc3RhdGUuZXh0ZW5Qcmlvcml0eSkge1xuICAgICAgc3RhdGUuZXh0ZW5Qcmlvcml0eSA9IGZhbHNlO1xuICAgICAgc3RhdGUuZXh0ZW5BcHBsaWNhdGlvbiA9IHRydWU7XG4gICAgICBzdHJlYW0ubmV4dCgpOyAvLyBnZXQgY29tbWFcbiAgICAgIGlmIChzdGF0ZS5leHRlblNhbWUpIHJldHVybiBudWxsO1xuICAgICAgc3RyZWFtLmVhdFdoaWxlKC9bXixdLyk7XG4gICAgICByZXR1cm4gXCJudW1iZXJcIjtcbiAgICB9IGVsc2UgaWYgKHN0YXRlLmV4dGVuQXBwbGljYXRpb24pIHtcbiAgICAgIHN0cmVhbS5lYXRXaGlsZSgvLC8pO1xuICAgICAgY3VyID0gc3RyZWFtLmN1cnJlbnQoKTtcbiAgICAgIGlmIChjdXIgPT09ICcsJykgcmV0dXJuIG51bGw7XG4gICAgICBzdHJlYW0uZWF0V2hpbGUoL1xcdy8pO1xuICAgICAgY3VyID0gc3RyZWFtLmN1cnJlbnQoKS50b0xvd2VyQ2FzZSgpO1xuICAgICAgc3RhdGUuZXh0ZW5BcHBsaWNhdGlvbiA9IGZhbHNlO1xuICAgICAgaWYgKGFwcHMuaW5kZXhPZihjdXIpICE9PSAtMSkge1xuICAgICAgICByZXR1cm4gXCJkZWZcIjtcbiAgICAgIH1cbiAgICB9IGVsc2Uge1xuICAgICAgcmV0dXJuIGJhc2ljVG9rZW4oc3RyZWFtLCBzdGF0ZSk7XG4gICAgfVxuICAgIHJldHVybiBudWxsO1xuICB9LFxuICBsYW5ndWFnZURhdGE6IHtcbiAgICBjb21tZW50VG9rZW5zOiB7XG4gICAgICBsaW5lOiBcIjtcIixcbiAgICAgIGJsb2NrOiB7XG4gICAgICAgIG9wZW46IFwiOy0tXCIsXG4gICAgICAgIGNsb3NlOiBcIi0tO1wiXG4gICAgICB9XG4gICAgfVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=