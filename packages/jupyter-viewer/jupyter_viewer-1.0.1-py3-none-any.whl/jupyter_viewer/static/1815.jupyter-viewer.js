"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[1815],{

/***/ 31815
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   sas: () => (/* binding */ sas)
/* harmony export */ });
var words = {};
var isDoubleOperatorSym = {
  eq: 'operator',
  lt: 'operator',
  le: 'operator',
  gt: 'operator',
  ge: 'operator',
  "in": 'operator',
  ne: 'operator',
  or: 'operator'
};
var isDoubleOperatorChar = /(<=|>=|!=|<>)/;
var isSingleOperatorChar = /[=\(:\),{}.*<>+\-\/^\[\]]/;

// Takes a string of words separated by spaces and adds them as
// keys with the value of the first argument 'style'
function define(style, string, context) {
  if (context) {
    var split = string.split(' ');
    for (var i = 0; i < split.length; i++) {
      words[split[i]] = {
        style: style,
        state: context
      };
    }
  }
}
//datastep
define('def', 'stack pgm view source debug nesting nolist', ['inDataStep']);
define('def', 'if while until for do do; end end; then else cancel', ['inDataStep']);
define('def', 'label format _n_ _error_', ['inDataStep']);
define('def', 'ALTER BUFNO BUFSIZE CNTLLEV COMPRESS DLDMGACTION ENCRYPT ENCRYPTKEY EXTENDOBSCOUNTER GENMAX GENNUM INDEX LABEL OBSBUF OUTREP PW PWREQ READ REPEMPTY REPLACE REUSE ROLE SORTEDBY SPILL TOBSNO TYPE WRITE FILECLOSE FIRSTOBS IN OBS POINTOBS WHERE WHEREUP IDXNAME IDXWHERE DROP KEEP RENAME', ['inDataStep']);
define('def', 'filevar finfo finv fipname fipnamel fipstate first firstobs floor', ['inDataStep']);
define('def', 'varfmt varinfmt varlabel varlen varname varnum varray varrayx vartype verify vformat vformatd vformatdx vformatn vformatnx vformatw vformatwx vformatx vinarray vinarrayx vinformat vinformatd vinformatdx vinformatn vinformatnx vinformatw vinformatwx vinformatx vlabel vlabelx vlength vlengthx vname vnamex vnferr vtype vtypex weekday', ['inDataStep']);
define('def', 'zipfips zipname zipnamel zipstate', ['inDataStep']);
define('def', 'put putc putn', ['inDataStep']);
define('builtin', 'data run', ['inDataStep']);

//proc
define('def', 'data', ['inProc']);

// flow control for macros
define('def', '%if %end %end; %else %else; %do %do; %then', ['inMacro']);

//everywhere
define('builtin', 'proc run; quit; libname filename %macro %mend option options', ['ALL']);
define('def', 'footnote title libname ods', ['ALL']);
define('def', '%let %put %global %sysfunc %eval ', ['ALL']);
// automatic macro variables http://support.sas.com/documentation/cdl/en/mcrolref/61885/HTML/default/viewer.htm#a003167023.htm
define('variable', '&sysbuffr &syscc &syscharwidth &syscmd &sysdate &sysdate9 &sysday &sysdevic &sysdmg &sysdsn &sysencoding &sysenv &syserr &syserrortext &sysfilrc &syshostname &sysindex &sysinfo &sysjobid &syslast &syslckrc &syslibrc &syslogapplname &sysmacroname &sysmenv &sysmsg &sysncpu &sysodspath &sysparm &syspbuff &sysprocessid &sysprocessname &sysprocname &sysrc &sysscp &sysscpl &sysscpl &syssite &sysstartid &sysstartname &systcpiphostname &systime &sysuserid &sysver &sysvlong &sysvlong4 &syswarningtext', ['ALL']);

//footnote[1-9]? title[1-9]?

//options statement
define('def', 'source2 nosource2 page pageno pagesize', ['ALL']);

//proc and datastep
define('def', '_all_ _character_ _cmd_ _freq_ _i_ _infile_ _last_ _msg_ _null_ _numeric_ _temporary_ _type_ abort abs addr adjrsq airy alpha alter altlog altprint and arcos array arsin as atan attrc attrib attrn authserver autoexec awscontrol awsdef awsmenu awsmenumerge awstitle backward band base betainv between blocksize blshift bnot bor brshift bufno bufsize bxor by byerr byline byte calculated call cards cards4 catcache cbufno cdf ceil center cexist change chisq cinv class cleanup close cnonct cntllev coalesce codegen col collate collin column comamid comaux1 comaux2 comdef compbl compound compress config continue convert cos cosh cpuid create cross crosstab css curobs cv daccdb daccdbsl daccsl daccsyd dacctab dairy datalines datalines4 datejul datepart datetime day dbcslang dbcstype dclose ddfm ddm delete delimiter depdb depdbsl depsl depsyd deptab dequote descending descript design= device dflang dhms dif digamma dim dinfo display distinct dkricond dkrocond dlm dnum do dopen doptname doptnum dread drop dropnote dsname dsnferr echo else emaildlg emailid emailpw emailserver emailsys encrypt end endsas engine eof eov erf erfc error errorcheck errors exist exp fappend fclose fcol fdelete feedback fetch fetchobs fexist fget file fileclose fileexist filefmt filename fileref  fmterr fmtsearch fnonct fnote font fontalias  fopen foptname foptnum force formatted formchar formdelim formdlim forward fpoint fpos fput fread frewind frlen from fsep fuzz fwrite gaminv gamma getoption getvarc getvarn go goto group gwindow hbar hbound helpenv helploc hms honorappearance hosthelp hostprint hour hpct html hvar ibessel ibr id if index indexc indexw initcmd initstmt inner input inputc inputn inr insert int intck intnx into intrr invaliddata irr is jbessel join juldate keep kentb kurtosis label lag last lbound leave left length levels lgamma lib  library libref line linesize link list log log10 log2 logpdf logpmf logsdf lostcard lowcase lrecl ls macro macrogen maps mautosource max maxdec maxr mdy mean measures median memtype merge merror min minute missing missover mlogic mod mode model modify month mopen mort mprint mrecall msglevel msymtabmax mvarsize myy n nest netpv new news nmiss no nobatch nobs nocaps nocardimage nocenter nocharcode nocmdmac nocol nocum nodate nodbcs nodetails nodmr nodms nodmsbatch nodup nodupkey noduplicates noechoauto noequals noerrorabend noexitwindows nofullstimer noicon noimplmac noint nolist noloadlist nomiss nomlogic nomprint nomrecall nomsgcase nomstored nomultenvappl nonotes nonumber noobs noovp nopad nopercent noprint noprintinit normal norow norsasuser nosetinit  nosplash nosymbolgen note notes notitle notitles notsorted noverbose noxsync noxwait npv null number numkeys nummousekeys nway obs  on open     order ordinal otherwise out outer outp= output over ovp p(1 5 10 25 50 75 90 95 99) pad pad2  paired parm parmcards path pathdll pathname pdf peek peekc pfkey pmf point poisson poke position printer probbeta probbnml probchi probf probgam probhypr probit probnegb probnorm probsig probt procleave prt ps  pw pwreq qtr quote r ranbin rancau random ranexp rangam range ranks rannor ranpoi rantbl rantri ranuni rcorr read recfm register regr remote remove rename repeat repeated replace resolve retain return reuse reverse rewind right round rsquare rtf rtrace rtraceloc s s2 samploc sasautos sascontrol sasfrscr sasmsg sasmstore sasscript sasuser saving scan sdf second select selection separated seq serror set setcomm setot sign simple sin sinh siteinfo skewness skip sle sls sortedby sortpgm sortseq sortsize soundex  spedis splashlocation split spool sqrt start std stderr stdin stfips stimer stname stnamel stop stopover sub subgroup subpopn substr sum sumwgt symbol symbolgen symget symput sysget sysin sysleave sysmsg sysparm sysprint sysprintfont sysprod sysrc system t table tables tan tanh tapeclose tbufsize terminal test then timepart tinv  tnonct to today tol tooldef totper transformout translate trantab tranwrd trigamma trim trimn trunc truncover type unformatted uniform union until upcase update user usericon uss validate value var  weight when where while wincharset window work workinit workterm write wsum xsync xwait yearcutoff yes yyq  min max', ['inDataStep', 'inProc']);
define('operator', 'and not ', ['inDataStep', 'inProc']);

// Main function
function tokenize(stream, state) {
  // Finally advance the stream
  var ch = stream.next();

  // BLOCKCOMMENT
  if (ch === '/' && stream.eat('*')) {
    state.continueComment = true;
    return "comment";
  } else if (state.continueComment === true) {
    // in comment block
    //comment ends at the beginning of the line
    if (ch === '*' && stream.peek() === '/') {
      stream.next();
      state.continueComment = false;
    } else if (stream.skipTo('*')) {
      //comment is potentially later in line
      stream.skipTo('*');
      stream.next();
      if (stream.eat('/')) state.continueComment = false;
    } else {
      stream.skipToEnd();
    }
    return "comment";
  }
  if (ch == "*" && stream.column() == stream.indentation()) {
    stream.skipToEnd();
    return "comment";
  }

  // DoubleOperator match
  var doubleOperator = ch + stream.peek();
  if ((ch === '"' || ch === "'") && !state.continueString) {
    state.continueString = ch;
    return "string";
  } else if (state.continueString) {
    if (state.continueString == ch) {
      state.continueString = null;
    } else if (stream.skipTo(state.continueString)) {
      // quote found on this line
      stream.next();
      state.continueString = null;
    } else {
      stream.skipToEnd();
    }
    return "string";
  } else if (state.continueString !== null && stream.eol()) {
    stream.skipTo(state.continueString) || stream.skipToEnd();
    return "string";
  } else if (/[\d\.]/.test(ch)) {
    //find numbers
    if (ch === ".") stream.match(/^[0-9]+([eE][\-+]?[0-9]+)?/);else if (ch === "0") stream.match(/^[xX][0-9a-fA-F]+/) || stream.match(/^0[0-7]+/);else stream.match(/^[0-9]*\.?[0-9]*([eE][\-+]?[0-9]+)?/);
    return "number";
  } else if (isDoubleOperatorChar.test(ch + stream.peek())) {
    // TWO SYMBOL TOKENS
    stream.next();
    return "operator";
  } else if (isDoubleOperatorSym.hasOwnProperty(doubleOperator)) {
    stream.next();
    if (stream.peek() === ' ') return isDoubleOperatorSym[doubleOperator.toLowerCase()];
  } else if (isSingleOperatorChar.test(ch)) {
    // SINGLE SYMBOL TOKENS
    return "operator";
  }

  // Matches one whole word -- even if the word is a character
  var word;
  if (stream.match(/[%&;\w]+/, false) != null) {
    word = ch + stream.match(/[%&;\w]+/, true);
    if (/&/.test(word)) return 'variable';
  } else {
    word = ch;
  }
  // the word after DATA PROC or MACRO
  if (state.nextword) {
    stream.match(/[\w]+/);
    // match memname.libname
    if (stream.peek() === '.') stream.skipTo(' ');
    state.nextword = false;
    return 'variableName.special';
  }
  word = word.toLowerCase();
  // Are we in a DATA Step?
  if (state.inDataStep) {
    if (word === 'run;' || stream.match(/run\s;/)) {
      state.inDataStep = false;
      return 'builtin';
    }
    // variable formats
    if (word && stream.next() === '.') {
      //either a format or libname.memname
      if (/\w/.test(stream.peek())) return 'variableName.special';else return 'variable';
    }
    // do we have a DATA Step keyword
    if (word && words.hasOwnProperty(word) && (words[word].state.indexOf("inDataStep") !== -1 || words[word].state.indexOf("ALL") !== -1)) {
      //backup to the start of the word
      if (stream.start < stream.pos) stream.backUp(stream.pos - stream.start);
      //advance the length of the word and return
      for (var i = 0; i < word.length; ++i) stream.next();
      return words[word].style;
    }
  }
  // Are we in an Proc statement?
  if (state.inProc) {
    if (word === 'run;' || word === 'quit;') {
      state.inProc = false;
      return 'builtin';
    }
    // do we have a proc keyword
    if (word && words.hasOwnProperty(word) && (words[word].state.indexOf("inProc") !== -1 || words[word].state.indexOf("ALL") !== -1)) {
      stream.match(/[\w]+/);
      return words[word].style;
    }
  }
  // Are we in a Macro statement?
  if (state.inMacro) {
    if (word === '%mend') {
      if (stream.peek() === ';') stream.next();
      state.inMacro = false;
      return 'builtin';
    }
    if (word && words.hasOwnProperty(word) && (words[word].state.indexOf("inMacro") !== -1 || words[word].state.indexOf("ALL") !== -1)) {
      stream.match(/[\w]+/);
      return words[word].style;
    }
    return 'atom';
  }
  // Do we have Keywords specific words?
  if (word && words.hasOwnProperty(word)) {
    // Negates the initial next()
    stream.backUp(1);
    // Actually move the stream
    stream.match(/[\w]+/);
    if (word === 'data' && /=/.test(stream.peek()) === false) {
      state.inDataStep = true;
      state.nextword = true;
      return 'builtin';
    }
    if (word === 'proc') {
      state.inProc = true;
      state.nextword = true;
      return 'builtin';
    }
    if (word === '%macro') {
      state.inMacro = true;
      state.nextword = true;
      return 'builtin';
    }
    if (/title[1-9]/.test(word)) return 'def';
    if (word === 'footnote') {
      stream.eat(/[1-9]/);
      return 'def';
    }

    // Returns their value as state in the prior define methods
    if (state.inDataStep === true && words[word].state.indexOf("inDataStep") !== -1) return words[word].style;
    if (state.inProc === true && words[word].state.indexOf("inProc") !== -1) return words[word].style;
    if (state.inMacro === true && words[word].state.indexOf("inMacro") !== -1) return words[word].style;
    if (words[word].state.indexOf("ALL") !== -1) return words[word].style;
    return null;
  }
  // Unrecognized syntax
  return null;
}
const sas = {
  name: "sas",
  startState: function () {
    return {
      inDataStep: false,
      inProc: false,
      inMacro: false,
      nextword: false,
      continueString: null,
      continueComment: false
    };
  },
  token: function (stream, state) {
    // Strip the spaces, but regex will account for them either way
    if (stream.eatSpace()) return null;
    // Go through the main process
    return tokenize(stream, state);
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
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMTgxNS5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9AY29kZW1pcnJvci9sZWdhY3ktbW9kZXMvbW9kZS9zYXMuanMiXSwic291cmNlc0NvbnRlbnQiOlsidmFyIHdvcmRzID0ge307XG52YXIgaXNEb3VibGVPcGVyYXRvclN5bSA9IHtcbiAgZXE6ICdvcGVyYXRvcicsXG4gIGx0OiAnb3BlcmF0b3InLFxuICBsZTogJ29wZXJhdG9yJyxcbiAgZ3Q6ICdvcGVyYXRvcicsXG4gIGdlOiAnb3BlcmF0b3InLFxuICBcImluXCI6ICdvcGVyYXRvcicsXG4gIG5lOiAnb3BlcmF0b3InLFxuICBvcjogJ29wZXJhdG9yJ1xufTtcbnZhciBpc0RvdWJsZU9wZXJhdG9yQ2hhciA9IC8oPD18Pj18IT18PD4pLztcbnZhciBpc1NpbmdsZU9wZXJhdG9yQ2hhciA9IC9bPVxcKDpcXCkse30uKjw+K1xcLVxcL15cXFtcXF1dLztcblxuLy8gVGFrZXMgYSBzdHJpbmcgb2Ygd29yZHMgc2VwYXJhdGVkIGJ5IHNwYWNlcyBhbmQgYWRkcyB0aGVtIGFzXG4vLyBrZXlzIHdpdGggdGhlIHZhbHVlIG9mIHRoZSBmaXJzdCBhcmd1bWVudCAnc3R5bGUnXG5mdW5jdGlvbiBkZWZpbmUoc3R5bGUsIHN0cmluZywgY29udGV4dCkge1xuICBpZiAoY29udGV4dCkge1xuICAgIHZhciBzcGxpdCA9IHN0cmluZy5zcGxpdCgnICcpO1xuICAgIGZvciAodmFyIGkgPSAwOyBpIDwgc3BsaXQubGVuZ3RoOyBpKyspIHtcbiAgICAgIHdvcmRzW3NwbGl0W2ldXSA9IHtcbiAgICAgICAgc3R5bGU6IHN0eWxlLFxuICAgICAgICBzdGF0ZTogY29udGV4dFxuICAgICAgfTtcbiAgICB9XG4gIH1cbn1cbi8vZGF0YXN0ZXBcbmRlZmluZSgnZGVmJywgJ3N0YWNrIHBnbSB2aWV3IHNvdXJjZSBkZWJ1ZyBuZXN0aW5nIG5vbGlzdCcsIFsnaW5EYXRhU3RlcCddKTtcbmRlZmluZSgnZGVmJywgJ2lmIHdoaWxlIHVudGlsIGZvciBkbyBkbzsgZW5kIGVuZDsgdGhlbiBlbHNlIGNhbmNlbCcsIFsnaW5EYXRhU3RlcCddKTtcbmRlZmluZSgnZGVmJywgJ2xhYmVsIGZvcm1hdCBfbl8gX2Vycm9yXycsIFsnaW5EYXRhU3RlcCddKTtcbmRlZmluZSgnZGVmJywgJ0FMVEVSIEJVRk5PIEJVRlNJWkUgQ05UTExFViBDT01QUkVTUyBETERNR0FDVElPTiBFTkNSWVBUIEVOQ1JZUFRLRVkgRVhURU5ET0JTQ09VTlRFUiBHRU5NQVggR0VOTlVNIElOREVYIExBQkVMIE9CU0JVRiBPVVRSRVAgUFcgUFdSRVEgUkVBRCBSRVBFTVBUWSBSRVBMQUNFIFJFVVNFIFJPTEUgU09SVEVEQlkgU1BJTEwgVE9CU05PIFRZUEUgV1JJVEUgRklMRUNMT1NFIEZJUlNUT0JTIElOIE9CUyBQT0lOVE9CUyBXSEVSRSBXSEVSRVVQIElEWE5BTUUgSURYV0hFUkUgRFJPUCBLRUVQIFJFTkFNRScsIFsnaW5EYXRhU3RlcCddKTtcbmRlZmluZSgnZGVmJywgJ2ZpbGV2YXIgZmluZm8gZmludiBmaXBuYW1lIGZpcG5hbWVsIGZpcHN0YXRlIGZpcnN0IGZpcnN0b2JzIGZsb29yJywgWydpbkRhdGFTdGVwJ10pO1xuZGVmaW5lKCdkZWYnLCAndmFyZm10IHZhcmluZm10IHZhcmxhYmVsIHZhcmxlbiB2YXJuYW1lIHZhcm51bSB2YXJyYXkgdmFycmF5eCB2YXJ0eXBlIHZlcmlmeSB2Zm9ybWF0IHZmb3JtYXRkIHZmb3JtYXRkeCB2Zm9ybWF0biB2Zm9ybWF0bnggdmZvcm1hdHcgdmZvcm1hdHd4IHZmb3JtYXR4IHZpbmFycmF5IHZpbmFycmF5eCB2aW5mb3JtYXQgdmluZm9ybWF0ZCB2aW5mb3JtYXRkeCB2aW5mb3JtYXRuIHZpbmZvcm1hdG54IHZpbmZvcm1hdHcgdmluZm9ybWF0d3ggdmluZm9ybWF0eCB2bGFiZWwgdmxhYmVseCB2bGVuZ3RoIHZsZW5ndGh4IHZuYW1lIHZuYW1leCB2bmZlcnIgdnR5cGUgdnR5cGV4IHdlZWtkYXknLCBbJ2luRGF0YVN0ZXAnXSk7XG5kZWZpbmUoJ2RlZicsICd6aXBmaXBzIHppcG5hbWUgemlwbmFtZWwgemlwc3RhdGUnLCBbJ2luRGF0YVN0ZXAnXSk7XG5kZWZpbmUoJ2RlZicsICdwdXQgcHV0YyBwdXRuJywgWydpbkRhdGFTdGVwJ10pO1xuZGVmaW5lKCdidWlsdGluJywgJ2RhdGEgcnVuJywgWydpbkRhdGFTdGVwJ10pO1xuXG4vL3Byb2NcbmRlZmluZSgnZGVmJywgJ2RhdGEnLCBbJ2luUHJvYyddKTtcblxuLy8gZmxvdyBjb250cm9sIGZvciBtYWNyb3NcbmRlZmluZSgnZGVmJywgJyVpZiAlZW5kICVlbmQ7ICVlbHNlICVlbHNlOyAlZG8gJWRvOyAldGhlbicsIFsnaW5NYWNybyddKTtcblxuLy9ldmVyeXdoZXJlXG5kZWZpbmUoJ2J1aWx0aW4nLCAncHJvYyBydW47IHF1aXQ7IGxpYm5hbWUgZmlsZW5hbWUgJW1hY3JvICVtZW5kIG9wdGlvbiBvcHRpb25zJywgWydBTEwnXSk7XG5kZWZpbmUoJ2RlZicsICdmb290bm90ZSB0aXRsZSBsaWJuYW1lIG9kcycsIFsnQUxMJ10pO1xuZGVmaW5lKCdkZWYnLCAnJWxldCAlcHV0ICVnbG9iYWwgJXN5c2Z1bmMgJWV2YWwgJywgWydBTEwnXSk7XG4vLyBhdXRvbWF0aWMgbWFjcm8gdmFyaWFibGVzIGh0dHA6Ly9zdXBwb3J0LnNhcy5jb20vZG9jdW1lbnRhdGlvbi9jZGwvZW4vbWNyb2xyZWYvNjE4ODUvSFRNTC9kZWZhdWx0L3ZpZXdlci5odG0jYTAwMzE2NzAyMy5odG1cbmRlZmluZSgndmFyaWFibGUnLCAnJnN5c2J1ZmZyICZzeXNjYyAmc3lzY2hhcndpZHRoICZzeXNjbWQgJnN5c2RhdGUgJnN5c2RhdGU5ICZzeXNkYXkgJnN5c2RldmljICZzeXNkbWcgJnN5c2RzbiAmc3lzZW5jb2RpbmcgJnN5c2VudiAmc3lzZXJyICZzeXNlcnJvcnRleHQgJnN5c2ZpbHJjICZzeXNob3N0bmFtZSAmc3lzaW5kZXggJnN5c2luZm8gJnN5c2pvYmlkICZzeXNsYXN0ICZzeXNsY2tyYyAmc3lzbGlicmMgJnN5c2xvZ2FwcGxuYW1lICZzeXNtYWNyb25hbWUgJnN5c21lbnYgJnN5c21zZyAmc3lzbmNwdSAmc3lzb2RzcGF0aCAmc3lzcGFybSAmc3lzcGJ1ZmYgJnN5c3Byb2Nlc3NpZCAmc3lzcHJvY2Vzc25hbWUgJnN5c3Byb2NuYW1lICZzeXNyYyAmc3lzc2NwICZzeXNzY3BsICZzeXNzY3BsICZzeXNzaXRlICZzeXNzdGFydGlkICZzeXNzdGFydG5hbWUgJnN5c3RjcGlwaG9zdG5hbWUgJnN5c3RpbWUgJnN5c3VzZXJpZCAmc3lzdmVyICZzeXN2bG9uZyAmc3lzdmxvbmc0ICZzeXN3YXJuaW5ndGV4dCcsIFsnQUxMJ10pO1xuXG4vL2Zvb3Rub3RlWzEtOV0/IHRpdGxlWzEtOV0/XG5cbi8vb3B0aW9ucyBzdGF0ZW1lbnRcbmRlZmluZSgnZGVmJywgJ3NvdXJjZTIgbm9zb3VyY2UyIHBhZ2UgcGFnZW5vIHBhZ2VzaXplJywgWydBTEwnXSk7XG5cbi8vcHJvYyBhbmQgZGF0YXN0ZXBcbmRlZmluZSgnZGVmJywgJ19hbGxfIF9jaGFyYWN0ZXJfIF9jbWRfIF9mcmVxXyBfaV8gX2luZmlsZV8gX2xhc3RfIF9tc2dfIF9udWxsXyBfbnVtZXJpY18gX3RlbXBvcmFyeV8gX3R5cGVfIGFib3J0IGFicyBhZGRyIGFkanJzcSBhaXJ5IGFscGhhIGFsdGVyIGFsdGxvZyBhbHRwcmludCBhbmQgYXJjb3MgYXJyYXkgYXJzaW4gYXMgYXRhbiBhdHRyYyBhdHRyaWIgYXR0cm4gYXV0aHNlcnZlciBhdXRvZXhlYyBhd3Njb250cm9sIGF3c2RlZiBhd3NtZW51IGF3c21lbnVtZXJnZSBhd3N0aXRsZSBiYWNrd2FyZCBiYW5kIGJhc2UgYmV0YWludiBiZXR3ZWVuIGJsb2Nrc2l6ZSBibHNoaWZ0IGJub3QgYm9yIGJyc2hpZnQgYnVmbm8gYnVmc2l6ZSBieG9yIGJ5IGJ5ZXJyIGJ5bGluZSBieXRlIGNhbGN1bGF0ZWQgY2FsbCBjYXJkcyBjYXJkczQgY2F0Y2FjaGUgY2J1Zm5vIGNkZiBjZWlsIGNlbnRlciBjZXhpc3QgY2hhbmdlIGNoaXNxIGNpbnYgY2xhc3MgY2xlYW51cCBjbG9zZSBjbm9uY3QgY250bGxldiBjb2FsZXNjZSBjb2RlZ2VuIGNvbCBjb2xsYXRlIGNvbGxpbiBjb2x1bW4gY29tYW1pZCBjb21hdXgxIGNvbWF1eDIgY29tZGVmIGNvbXBibCBjb21wb3VuZCBjb21wcmVzcyBjb25maWcgY29udGludWUgY29udmVydCBjb3MgY29zaCBjcHVpZCBjcmVhdGUgY3Jvc3MgY3Jvc3N0YWIgY3NzIGN1cm9icyBjdiBkYWNjZGIgZGFjY2Ric2wgZGFjY3NsIGRhY2NzeWQgZGFjY3RhYiBkYWlyeSBkYXRhbGluZXMgZGF0YWxpbmVzNCBkYXRlanVsIGRhdGVwYXJ0IGRhdGV0aW1lIGRheSBkYmNzbGFuZyBkYmNzdHlwZSBkY2xvc2UgZGRmbSBkZG0gZGVsZXRlIGRlbGltaXRlciBkZXBkYiBkZXBkYnNsIGRlcHNsIGRlcHN5ZCBkZXB0YWIgZGVxdW90ZSBkZXNjZW5kaW5nIGRlc2NyaXB0IGRlc2lnbj0gZGV2aWNlIGRmbGFuZyBkaG1zIGRpZiBkaWdhbW1hIGRpbSBkaW5mbyBkaXNwbGF5IGRpc3RpbmN0IGRrcmljb25kIGRrcm9jb25kIGRsbSBkbnVtIGRvIGRvcGVuIGRvcHRuYW1lIGRvcHRudW0gZHJlYWQgZHJvcCBkcm9wbm90ZSBkc25hbWUgZHNuZmVyciBlY2hvIGVsc2UgZW1haWxkbGcgZW1haWxpZCBlbWFpbHB3IGVtYWlsc2VydmVyIGVtYWlsc3lzIGVuY3J5cHQgZW5kIGVuZHNhcyBlbmdpbmUgZW9mIGVvdiBlcmYgZXJmYyBlcnJvciBlcnJvcmNoZWNrIGVycm9ycyBleGlzdCBleHAgZmFwcGVuZCBmY2xvc2UgZmNvbCBmZGVsZXRlIGZlZWRiYWNrIGZldGNoIGZldGNob2JzIGZleGlzdCBmZ2V0IGZpbGUgZmlsZWNsb3NlIGZpbGVleGlzdCBmaWxlZm10IGZpbGVuYW1lIGZpbGVyZWYgIGZtdGVyciBmbXRzZWFyY2ggZm5vbmN0IGZub3RlIGZvbnQgZm9udGFsaWFzICBmb3BlbiBmb3B0bmFtZSBmb3B0bnVtIGZvcmNlIGZvcm1hdHRlZCBmb3JtY2hhciBmb3JtZGVsaW0gZm9ybWRsaW0gZm9yd2FyZCBmcG9pbnQgZnBvcyBmcHV0IGZyZWFkIGZyZXdpbmQgZnJsZW4gZnJvbSBmc2VwIGZ1enogZndyaXRlIGdhbWludiBnYW1tYSBnZXRvcHRpb24gZ2V0dmFyYyBnZXR2YXJuIGdvIGdvdG8gZ3JvdXAgZ3dpbmRvdyBoYmFyIGhib3VuZCBoZWxwZW52IGhlbHBsb2MgaG1zIGhvbm9yYXBwZWFyYW5jZSBob3N0aGVscCBob3N0cHJpbnQgaG91ciBocGN0IGh0bWwgaHZhciBpYmVzc2VsIGliciBpZCBpZiBpbmRleCBpbmRleGMgaW5kZXh3IGluaXRjbWQgaW5pdHN0bXQgaW5uZXIgaW5wdXQgaW5wdXRjIGlucHV0biBpbnIgaW5zZXJ0IGludCBpbnRjayBpbnRueCBpbnRvIGludHJyIGludmFsaWRkYXRhIGlyciBpcyBqYmVzc2VsIGpvaW4ganVsZGF0ZSBrZWVwIGtlbnRiIGt1cnRvc2lzIGxhYmVsIGxhZyBsYXN0IGxib3VuZCBsZWF2ZSBsZWZ0IGxlbmd0aCBsZXZlbHMgbGdhbW1hIGxpYiAgbGlicmFyeSBsaWJyZWYgbGluZSBsaW5lc2l6ZSBsaW5rIGxpc3QgbG9nIGxvZzEwIGxvZzIgbG9ncGRmIGxvZ3BtZiBsb2dzZGYgbG9zdGNhcmQgbG93Y2FzZSBscmVjbCBscyBtYWNybyBtYWNyb2dlbiBtYXBzIG1hdXRvc291cmNlIG1heCBtYXhkZWMgbWF4ciBtZHkgbWVhbiBtZWFzdXJlcyBtZWRpYW4gbWVtdHlwZSBtZXJnZSBtZXJyb3IgbWluIG1pbnV0ZSBtaXNzaW5nIG1pc3NvdmVyIG1sb2dpYyBtb2QgbW9kZSBtb2RlbCBtb2RpZnkgbW9udGggbW9wZW4gbW9ydCBtcHJpbnQgbXJlY2FsbCBtc2dsZXZlbCBtc3ltdGFibWF4IG12YXJzaXplIG15eSBuIG5lc3QgbmV0cHYgbmV3IG5ld3Mgbm1pc3Mgbm8gbm9iYXRjaCBub2JzIG5vY2FwcyBub2NhcmRpbWFnZSBub2NlbnRlciBub2NoYXJjb2RlIG5vY21kbWFjIG5vY29sIG5vY3VtIG5vZGF0ZSBub2RiY3Mgbm9kZXRhaWxzIG5vZG1yIG5vZG1zIG5vZG1zYmF0Y2ggbm9kdXAgbm9kdXBrZXkgbm9kdXBsaWNhdGVzIG5vZWNob2F1dG8gbm9lcXVhbHMgbm9lcnJvcmFiZW5kIG5vZXhpdHdpbmRvd3Mgbm9mdWxsc3RpbWVyIG5vaWNvbiBub2ltcGxtYWMgbm9pbnQgbm9saXN0IG5vbG9hZGxpc3Qgbm9taXNzIG5vbWxvZ2ljIG5vbXByaW50IG5vbXJlY2FsbCBub21zZ2Nhc2Ugbm9tc3RvcmVkIG5vbXVsdGVudmFwcGwgbm9ub3RlcyBub251bWJlciBub29icyBub292cCBub3BhZCBub3BlcmNlbnQgbm9wcmludCBub3ByaW50aW5pdCBub3JtYWwgbm9yb3cgbm9yc2FzdXNlciBub3NldGluaXQgIG5vc3BsYXNoIG5vc3ltYm9sZ2VuIG5vdGUgbm90ZXMgbm90aXRsZSBub3RpdGxlcyBub3Rzb3J0ZWQgbm92ZXJib3NlIG5veHN5bmMgbm94d2FpdCBucHYgbnVsbCBudW1iZXIgbnVta2V5cyBudW1tb3VzZWtleXMgbndheSBvYnMgIG9uIG9wZW4gICAgIG9yZGVyIG9yZGluYWwgb3RoZXJ3aXNlIG91dCBvdXRlciBvdXRwPSBvdXRwdXQgb3ZlciBvdnAgcCgxIDUgMTAgMjUgNTAgNzUgOTAgOTUgOTkpIHBhZCBwYWQyICBwYWlyZWQgcGFybSBwYXJtY2FyZHMgcGF0aCBwYXRoZGxsIHBhdGhuYW1lIHBkZiBwZWVrIHBlZWtjIHBma2V5IHBtZiBwb2ludCBwb2lzc29uIHBva2UgcG9zaXRpb24gcHJpbnRlciBwcm9iYmV0YSBwcm9iYm5tbCBwcm9iY2hpIHByb2JmIHByb2JnYW0gcHJvYmh5cHIgcHJvYml0IHByb2JuZWdiIHByb2Jub3JtIHByb2JzaWcgcHJvYnQgcHJvY2xlYXZlIHBydCBwcyAgcHcgcHdyZXEgcXRyIHF1b3RlIHIgcmFuYmluIHJhbmNhdSByYW5kb20gcmFuZXhwIHJhbmdhbSByYW5nZSByYW5rcyByYW5ub3IgcmFucG9pIHJhbnRibCByYW50cmkgcmFudW5pIHJjb3JyIHJlYWQgcmVjZm0gcmVnaXN0ZXIgcmVnciByZW1vdGUgcmVtb3ZlIHJlbmFtZSByZXBlYXQgcmVwZWF0ZWQgcmVwbGFjZSByZXNvbHZlIHJldGFpbiByZXR1cm4gcmV1c2UgcmV2ZXJzZSByZXdpbmQgcmlnaHQgcm91bmQgcnNxdWFyZSBydGYgcnRyYWNlIHJ0cmFjZWxvYyBzIHMyIHNhbXBsb2Mgc2FzYXV0b3Mgc2FzY29udHJvbCBzYXNmcnNjciBzYXNtc2cgc2FzbXN0b3JlIHNhc3NjcmlwdCBzYXN1c2VyIHNhdmluZyBzY2FuIHNkZiBzZWNvbmQgc2VsZWN0IHNlbGVjdGlvbiBzZXBhcmF0ZWQgc2VxIHNlcnJvciBzZXQgc2V0Y29tbSBzZXRvdCBzaWduIHNpbXBsZSBzaW4gc2luaCBzaXRlaW5mbyBza2V3bmVzcyBza2lwIHNsZSBzbHMgc29ydGVkYnkgc29ydHBnbSBzb3J0c2VxIHNvcnRzaXplIHNvdW5kZXggIHNwZWRpcyBzcGxhc2hsb2NhdGlvbiBzcGxpdCBzcG9vbCBzcXJ0IHN0YXJ0IHN0ZCBzdGRlcnIgc3RkaW4gc3RmaXBzIHN0aW1lciBzdG5hbWUgc3RuYW1lbCBzdG9wIHN0b3BvdmVyIHN1YiBzdWJncm91cCBzdWJwb3BuIHN1YnN0ciBzdW0gc3Vtd2d0IHN5bWJvbCBzeW1ib2xnZW4gc3ltZ2V0IHN5bXB1dCBzeXNnZXQgc3lzaW4gc3lzbGVhdmUgc3lzbXNnIHN5c3Bhcm0gc3lzcHJpbnQgc3lzcHJpbnRmb250IHN5c3Byb2Qgc3lzcmMgc3lzdGVtIHQgdGFibGUgdGFibGVzIHRhbiB0YW5oIHRhcGVjbG9zZSB0YnVmc2l6ZSB0ZXJtaW5hbCB0ZXN0IHRoZW4gdGltZXBhcnQgdGludiAgdG5vbmN0IHRvIHRvZGF5IHRvbCB0b29sZGVmIHRvdHBlciB0cmFuc2Zvcm1vdXQgdHJhbnNsYXRlIHRyYW50YWIgdHJhbndyZCB0cmlnYW1tYSB0cmltIHRyaW1uIHRydW5jIHRydW5jb3ZlciB0eXBlIHVuZm9ybWF0dGVkIHVuaWZvcm0gdW5pb24gdW50aWwgdXBjYXNlIHVwZGF0ZSB1c2VyIHVzZXJpY29uIHVzcyB2YWxpZGF0ZSB2YWx1ZSB2YXIgIHdlaWdodCB3aGVuIHdoZXJlIHdoaWxlIHdpbmNoYXJzZXQgd2luZG93IHdvcmsgd29ya2luaXQgd29ya3Rlcm0gd3JpdGUgd3N1bSB4c3luYyB4d2FpdCB5ZWFyY3V0b2ZmIHllcyB5eXEgIG1pbiBtYXgnLCBbJ2luRGF0YVN0ZXAnLCAnaW5Qcm9jJ10pO1xuZGVmaW5lKCdvcGVyYXRvcicsICdhbmQgbm90ICcsIFsnaW5EYXRhU3RlcCcsICdpblByb2MnXSk7XG5cbi8vIE1haW4gZnVuY3Rpb25cbmZ1bmN0aW9uIHRva2VuaXplKHN0cmVhbSwgc3RhdGUpIHtcbiAgLy8gRmluYWxseSBhZHZhbmNlIHRoZSBzdHJlYW1cbiAgdmFyIGNoID0gc3RyZWFtLm5leHQoKTtcblxuICAvLyBCTE9DS0NPTU1FTlRcbiAgaWYgKGNoID09PSAnLycgJiYgc3RyZWFtLmVhdCgnKicpKSB7XG4gICAgc3RhdGUuY29udGludWVDb21tZW50ID0gdHJ1ZTtcbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH0gZWxzZSBpZiAoc3RhdGUuY29udGludWVDb21tZW50ID09PSB0cnVlKSB7XG4gICAgLy8gaW4gY29tbWVudCBibG9ja1xuICAgIC8vY29tbWVudCBlbmRzIGF0IHRoZSBiZWdpbm5pbmcgb2YgdGhlIGxpbmVcbiAgICBpZiAoY2ggPT09ICcqJyAmJiBzdHJlYW0ucGVlaygpID09PSAnLycpIHtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICBzdGF0ZS5jb250aW51ZUNvbW1lbnQgPSBmYWxzZTtcbiAgICB9IGVsc2UgaWYgKHN0cmVhbS5za2lwVG8oJyonKSkge1xuICAgICAgLy9jb21tZW50IGlzIHBvdGVudGlhbGx5IGxhdGVyIGluIGxpbmVcbiAgICAgIHN0cmVhbS5za2lwVG8oJyonKTtcbiAgICAgIHN0cmVhbS5uZXh0KCk7XG4gICAgICBpZiAoc3RyZWFtLmVhdCgnLycpKSBzdGF0ZS5jb250aW51ZUNvbW1lbnQgPSBmYWxzZTtcbiAgICB9IGVsc2Uge1xuICAgICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgIH1cbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH1cbiAgaWYgKGNoID09IFwiKlwiICYmIHN0cmVhbS5jb2x1bW4oKSA9PSBzdHJlYW0uaW5kZW50YXRpb24oKSkge1xuICAgIHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gXCJjb21tZW50XCI7XG4gIH1cblxuICAvLyBEb3VibGVPcGVyYXRvciBtYXRjaFxuICB2YXIgZG91YmxlT3BlcmF0b3IgPSBjaCArIHN0cmVhbS5wZWVrKCk7XG4gIGlmICgoY2ggPT09ICdcIicgfHwgY2ggPT09IFwiJ1wiKSAmJiAhc3RhdGUuY29udGludWVTdHJpbmcpIHtcbiAgICBzdGF0ZS5jb250aW51ZVN0cmluZyA9IGNoO1xuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9IGVsc2UgaWYgKHN0YXRlLmNvbnRpbnVlU3RyaW5nKSB7XG4gICAgaWYgKHN0YXRlLmNvbnRpbnVlU3RyaW5nID09IGNoKSB7XG4gICAgICBzdGF0ZS5jb250aW51ZVN0cmluZyA9IG51bGw7XG4gICAgfSBlbHNlIGlmIChzdHJlYW0uc2tpcFRvKHN0YXRlLmNvbnRpbnVlU3RyaW5nKSkge1xuICAgICAgLy8gcXVvdGUgZm91bmQgb24gdGhpcyBsaW5lXG4gICAgICBzdHJlYW0ubmV4dCgpO1xuICAgICAgc3RhdGUuY29udGludWVTdHJpbmcgPSBudWxsO1xuICAgIH0gZWxzZSB7XG4gICAgICBzdHJlYW0uc2tpcFRvRW5kKCk7XG4gICAgfVxuICAgIHJldHVybiBcInN0cmluZ1wiO1xuICB9IGVsc2UgaWYgKHN0YXRlLmNvbnRpbnVlU3RyaW5nICE9PSBudWxsICYmIHN0cmVhbS5lb2woKSkge1xuICAgIHN0cmVhbS5za2lwVG8oc3RhdGUuY29udGludWVTdHJpbmcpIHx8IHN0cmVhbS5za2lwVG9FbmQoKTtcbiAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgfSBlbHNlIGlmICgvW1xcZFxcLl0vLnRlc3QoY2gpKSB7XG4gICAgLy9maW5kIG51bWJlcnNcbiAgICBpZiAoY2ggPT09IFwiLlwiKSBzdHJlYW0ubWF0Y2goL15bMC05XSsoW2VFXVtcXC0rXT9bMC05XSspPy8pO2Vsc2UgaWYgKGNoID09PSBcIjBcIikgc3RyZWFtLm1hdGNoKC9eW3hYXVswLTlhLWZBLUZdKy8pIHx8IHN0cmVhbS5tYXRjaCgvXjBbMC03XSsvKTtlbHNlIHN0cmVhbS5tYXRjaCgvXlswLTldKlxcLj9bMC05XSooW2VFXVtcXC0rXT9bMC05XSspPy8pO1xuICAgIHJldHVybiBcIm51bWJlclwiO1xuICB9IGVsc2UgaWYgKGlzRG91YmxlT3BlcmF0b3JDaGFyLnRlc3QoY2ggKyBzdHJlYW0ucGVlaygpKSkge1xuICAgIC8vIFRXTyBTWU1CT0wgVE9LRU5TXG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICByZXR1cm4gXCJvcGVyYXRvclwiO1xuICB9IGVsc2UgaWYgKGlzRG91YmxlT3BlcmF0b3JTeW0uaGFzT3duUHJvcGVydHkoZG91YmxlT3BlcmF0b3IpKSB7XG4gICAgc3RyZWFtLm5leHQoKTtcbiAgICBpZiAoc3RyZWFtLnBlZWsoKSA9PT0gJyAnKSByZXR1cm4gaXNEb3VibGVPcGVyYXRvclN5bVtkb3VibGVPcGVyYXRvci50b0xvd2VyQ2FzZSgpXTtcbiAgfSBlbHNlIGlmIChpc1NpbmdsZU9wZXJhdG9yQ2hhci50ZXN0KGNoKSkge1xuICAgIC8vIFNJTkdMRSBTWU1CT0wgVE9LRU5TXG4gICAgcmV0dXJuIFwib3BlcmF0b3JcIjtcbiAgfVxuXG4gIC8vIE1hdGNoZXMgb25lIHdob2xlIHdvcmQgLS0gZXZlbiBpZiB0aGUgd29yZCBpcyBhIGNoYXJhY3RlclxuICB2YXIgd29yZDtcbiAgaWYgKHN0cmVhbS5tYXRjaCgvWyUmO1xcd10rLywgZmFsc2UpICE9IG51bGwpIHtcbiAgICB3b3JkID0gY2ggKyBzdHJlYW0ubWF0Y2goL1slJjtcXHddKy8sIHRydWUpO1xuICAgIGlmICgvJi8udGVzdCh3b3JkKSkgcmV0dXJuICd2YXJpYWJsZSc7XG4gIH0gZWxzZSB7XG4gICAgd29yZCA9IGNoO1xuICB9XG4gIC8vIHRoZSB3b3JkIGFmdGVyIERBVEEgUFJPQyBvciBNQUNST1xuICBpZiAoc3RhdGUubmV4dHdvcmQpIHtcbiAgICBzdHJlYW0ubWF0Y2goL1tcXHddKy8pO1xuICAgIC8vIG1hdGNoIG1lbW5hbWUubGlibmFtZVxuICAgIGlmIChzdHJlYW0ucGVlaygpID09PSAnLicpIHN0cmVhbS5za2lwVG8oJyAnKTtcbiAgICBzdGF0ZS5uZXh0d29yZCA9IGZhbHNlO1xuICAgIHJldHVybiAndmFyaWFibGVOYW1lLnNwZWNpYWwnO1xuICB9XG4gIHdvcmQgPSB3b3JkLnRvTG93ZXJDYXNlKCk7XG4gIC8vIEFyZSB3ZSBpbiBhIERBVEEgU3RlcD9cbiAgaWYgKHN0YXRlLmluRGF0YVN0ZXApIHtcbiAgICBpZiAod29yZCA9PT0gJ3J1bjsnIHx8IHN0cmVhbS5tYXRjaCgvcnVuXFxzOy8pKSB7XG4gICAgICBzdGF0ZS5pbkRhdGFTdGVwID0gZmFsc2U7XG4gICAgICByZXR1cm4gJ2J1aWx0aW4nO1xuICAgIH1cbiAgICAvLyB2YXJpYWJsZSBmb3JtYXRzXG4gICAgaWYgKHdvcmQgJiYgc3RyZWFtLm5leHQoKSA9PT0gJy4nKSB7XG4gICAgICAvL2VpdGhlciBhIGZvcm1hdCBvciBsaWJuYW1lLm1lbW5hbWVcbiAgICAgIGlmICgvXFx3Ly50ZXN0KHN0cmVhbS5wZWVrKCkpKSByZXR1cm4gJ3ZhcmlhYmxlTmFtZS5zcGVjaWFsJztlbHNlIHJldHVybiAndmFyaWFibGUnO1xuICAgIH1cbiAgICAvLyBkbyB3ZSBoYXZlIGEgREFUQSBTdGVwIGtleXdvcmRcbiAgICBpZiAod29yZCAmJiB3b3Jkcy5oYXNPd25Qcm9wZXJ0eSh3b3JkKSAmJiAod29yZHNbd29yZF0uc3RhdGUuaW5kZXhPZihcImluRGF0YVN0ZXBcIikgIT09IC0xIHx8IHdvcmRzW3dvcmRdLnN0YXRlLmluZGV4T2YoXCJBTExcIikgIT09IC0xKSkge1xuICAgICAgLy9iYWNrdXAgdG8gdGhlIHN0YXJ0IG9mIHRoZSB3b3JkXG4gICAgICBpZiAoc3RyZWFtLnN0YXJ0IDwgc3RyZWFtLnBvcykgc3RyZWFtLmJhY2tVcChzdHJlYW0ucG9zIC0gc3RyZWFtLnN0YXJ0KTtcbiAgICAgIC8vYWR2YW5jZSB0aGUgbGVuZ3RoIG9mIHRoZSB3b3JkIGFuZCByZXR1cm5cbiAgICAgIGZvciAodmFyIGkgPSAwOyBpIDwgd29yZC5sZW5ndGg7ICsraSkgc3RyZWFtLm5leHQoKTtcbiAgICAgIHJldHVybiB3b3Jkc1t3b3JkXS5zdHlsZTtcbiAgICB9XG4gIH1cbiAgLy8gQXJlIHdlIGluIGFuIFByb2Mgc3RhdGVtZW50P1xuICBpZiAoc3RhdGUuaW5Qcm9jKSB7XG4gICAgaWYgKHdvcmQgPT09ICdydW47JyB8fCB3b3JkID09PSAncXVpdDsnKSB7XG4gICAgICBzdGF0ZS5pblByb2MgPSBmYWxzZTtcbiAgICAgIHJldHVybiAnYnVpbHRpbic7XG4gICAgfVxuICAgIC8vIGRvIHdlIGhhdmUgYSBwcm9jIGtleXdvcmRcbiAgICBpZiAod29yZCAmJiB3b3Jkcy5oYXNPd25Qcm9wZXJ0eSh3b3JkKSAmJiAod29yZHNbd29yZF0uc3RhdGUuaW5kZXhPZihcImluUHJvY1wiKSAhPT0gLTEgfHwgd29yZHNbd29yZF0uc3RhdGUuaW5kZXhPZihcIkFMTFwiKSAhPT0gLTEpKSB7XG4gICAgICBzdHJlYW0ubWF0Y2goL1tcXHddKy8pO1xuICAgICAgcmV0dXJuIHdvcmRzW3dvcmRdLnN0eWxlO1xuICAgIH1cbiAgfVxuICAvLyBBcmUgd2UgaW4gYSBNYWNybyBzdGF0ZW1lbnQ/XG4gIGlmIChzdGF0ZS5pbk1hY3JvKSB7XG4gICAgaWYgKHdvcmQgPT09ICclbWVuZCcpIHtcbiAgICAgIGlmIChzdHJlYW0ucGVlaygpID09PSAnOycpIHN0cmVhbS5uZXh0KCk7XG4gICAgICBzdGF0ZS5pbk1hY3JvID0gZmFsc2U7XG4gICAgICByZXR1cm4gJ2J1aWx0aW4nO1xuICAgIH1cbiAgICBpZiAod29yZCAmJiB3b3Jkcy5oYXNPd25Qcm9wZXJ0eSh3b3JkKSAmJiAod29yZHNbd29yZF0uc3RhdGUuaW5kZXhPZihcImluTWFjcm9cIikgIT09IC0xIHx8IHdvcmRzW3dvcmRdLnN0YXRlLmluZGV4T2YoXCJBTExcIikgIT09IC0xKSkge1xuICAgICAgc3RyZWFtLm1hdGNoKC9bXFx3XSsvKTtcbiAgICAgIHJldHVybiB3b3Jkc1t3b3JkXS5zdHlsZTtcbiAgICB9XG4gICAgcmV0dXJuICdhdG9tJztcbiAgfVxuICAvLyBEbyB3ZSBoYXZlIEtleXdvcmRzIHNwZWNpZmljIHdvcmRzP1xuICBpZiAod29yZCAmJiB3b3Jkcy5oYXNPd25Qcm9wZXJ0eSh3b3JkKSkge1xuICAgIC8vIE5lZ2F0ZXMgdGhlIGluaXRpYWwgbmV4dCgpXG4gICAgc3RyZWFtLmJhY2tVcCgxKTtcbiAgICAvLyBBY3R1YWxseSBtb3ZlIHRoZSBzdHJlYW1cbiAgICBzdHJlYW0ubWF0Y2goL1tcXHddKy8pO1xuICAgIGlmICh3b3JkID09PSAnZGF0YScgJiYgLz0vLnRlc3Qoc3RyZWFtLnBlZWsoKSkgPT09IGZhbHNlKSB7XG4gICAgICBzdGF0ZS5pbkRhdGFTdGVwID0gdHJ1ZTtcbiAgICAgIHN0YXRlLm5leHR3b3JkID0gdHJ1ZTtcbiAgICAgIHJldHVybiAnYnVpbHRpbic7XG4gICAgfVxuICAgIGlmICh3b3JkID09PSAncHJvYycpIHtcbiAgICAgIHN0YXRlLmluUHJvYyA9IHRydWU7XG4gICAgICBzdGF0ZS5uZXh0d29yZCA9IHRydWU7XG4gICAgICByZXR1cm4gJ2J1aWx0aW4nO1xuICAgIH1cbiAgICBpZiAod29yZCA9PT0gJyVtYWNybycpIHtcbiAgICAgIHN0YXRlLmluTWFjcm8gPSB0cnVlO1xuICAgICAgc3RhdGUubmV4dHdvcmQgPSB0cnVlO1xuICAgICAgcmV0dXJuICdidWlsdGluJztcbiAgICB9XG4gICAgaWYgKC90aXRsZVsxLTldLy50ZXN0KHdvcmQpKSByZXR1cm4gJ2RlZic7XG4gICAgaWYgKHdvcmQgPT09ICdmb290bm90ZScpIHtcbiAgICAgIHN0cmVhbS5lYXQoL1sxLTldLyk7XG4gICAgICByZXR1cm4gJ2RlZic7XG4gICAgfVxuXG4gICAgLy8gUmV0dXJucyB0aGVpciB2YWx1ZSBhcyBzdGF0ZSBpbiB0aGUgcHJpb3IgZGVmaW5lIG1ldGhvZHNcbiAgICBpZiAoc3RhdGUuaW5EYXRhU3RlcCA9PT0gdHJ1ZSAmJiB3b3Jkc1t3b3JkXS5zdGF0ZS5pbmRleE9mKFwiaW5EYXRhU3RlcFwiKSAhPT0gLTEpIHJldHVybiB3b3Jkc1t3b3JkXS5zdHlsZTtcbiAgICBpZiAoc3RhdGUuaW5Qcm9jID09PSB0cnVlICYmIHdvcmRzW3dvcmRdLnN0YXRlLmluZGV4T2YoXCJpblByb2NcIikgIT09IC0xKSByZXR1cm4gd29yZHNbd29yZF0uc3R5bGU7XG4gICAgaWYgKHN0YXRlLmluTWFjcm8gPT09IHRydWUgJiYgd29yZHNbd29yZF0uc3RhdGUuaW5kZXhPZihcImluTWFjcm9cIikgIT09IC0xKSByZXR1cm4gd29yZHNbd29yZF0uc3R5bGU7XG4gICAgaWYgKHdvcmRzW3dvcmRdLnN0YXRlLmluZGV4T2YoXCJBTExcIikgIT09IC0xKSByZXR1cm4gd29yZHNbd29yZF0uc3R5bGU7XG4gICAgcmV0dXJuIG51bGw7XG4gIH1cbiAgLy8gVW5yZWNvZ25pemVkIHN5bnRheFxuICByZXR1cm4gbnVsbDtcbn1cbmV4cG9ydCBjb25zdCBzYXMgPSB7XG4gIG5hbWU6IFwic2FzXCIsXG4gIHN0YXJ0U3RhdGU6IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4ge1xuICAgICAgaW5EYXRhU3RlcDogZmFsc2UsXG4gICAgICBpblByb2M6IGZhbHNlLFxuICAgICAgaW5NYWNybzogZmFsc2UsXG4gICAgICBuZXh0d29yZDogZmFsc2UsXG4gICAgICBjb250aW51ZVN0cmluZzogbnVsbCxcbiAgICAgIGNvbnRpbnVlQ29tbWVudDogZmFsc2VcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICAvLyBTdHJpcCB0aGUgc3BhY2VzLCBidXQgcmVnZXggd2lsbCBhY2NvdW50IGZvciB0aGVtIGVpdGhlciB3YXlcbiAgICBpZiAoc3RyZWFtLmVhdFNwYWNlKCkpIHJldHVybiBudWxsO1xuICAgIC8vIEdvIHRocm91Z2ggdGhlIG1haW4gcHJvY2Vzc1xuICAgIHJldHVybiB0b2tlbml6ZShzdHJlYW0sIHN0YXRlKTtcbiAgfSxcbiAgbGFuZ3VhZ2VEYXRhOiB7XG4gICAgY29tbWVudFRva2Vuczoge1xuICAgICAgYmxvY2s6IHtcbiAgICAgICAgb3BlbjogXCIvKlwiLFxuICAgICAgICBjbG9zZTogXCIqL1wiXG4gICAgICB9XG4gICAgfVxuICB9XG59OyJdLCJuYW1lcyI6W10sImlnbm9yZUxpc3QiOltdLCJzb3VyY2VSb290IjoiIn0=