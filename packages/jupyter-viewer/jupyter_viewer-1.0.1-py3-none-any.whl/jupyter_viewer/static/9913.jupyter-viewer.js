"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[9913],{

/***/ 59913
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   mirc: () => (/* binding */ mirc)
/* harmony export */ });
function parseWords(str) {
  var obj = {},
    words = str.split(" ");
  for (var i = 0; i < words.length; ++i) obj[words[i]] = true;
  return obj;
}
var specials = parseWords("$! $$ $& $? $+ $abook $abs $active $activecid " + "$activewid $address $addtok $agent $agentname $agentstat $agentver " + "$alias $and $anick $ansi2mirc $aop $appactive $appstate $asc $asctime " + "$asin $atan $avoice $away $awaymsg $awaytime $banmask $base $bfind " + "$binoff $biton $bnick $bvar $bytes $calc $cb $cd $ceil $chan $chanmodes " + "$chantypes $chat $chr $cid $clevel $click $cmdbox $cmdline $cnick $color " + "$com $comcall $comchan $comerr $compact $compress $comval $cos $count " + "$cr $crc $creq $crlf $ctime $ctimer $ctrlenter $date $day $daylight " + "$dbuh $dbuw $dccignore $dccport $dde $ddename $debug $decode $decompress " + "$deltok $devent $dialog $did $didreg $didtok $didwm $disk $dlevel $dll " + "$dllcall $dname $dns $duration $ebeeps $editbox $emailaddr $encode $error " + "$eval $event $exist $feof $ferr $fgetc $file $filename $filtered $finddir " + "$finddirn $findfile $findfilen $findtok $fline $floor $fopen $fread $fserve " + "$fulladdress $fulldate $fullname $fullscreen $get $getdir $getdot $gettok $gmt " + "$group $halted $hash $height $hfind $hget $highlight $hnick $hotline " + "$hotlinepos $ial $ialchan $ibl $idle $iel $ifmatch $ignore $iif $iil " + "$inelipse $ini $inmidi $inpaste $inpoly $input $inrect $inroundrect " + "$insong $instok $int $inwave $ip $isalias $isbit $isdde $isdir $isfile " + "$isid $islower $istok $isupper $keychar $keyrpt $keyval $knick $lactive " + "$lactivecid $lactivewid $left $len $level $lf $line $lines $link $lock " + "$lock $locked $log $logstamp $logstampfmt $longfn $longip $lower $ltimer " + "$maddress $mask $matchkey $matchtok $md5 $me $menu $menubar $menucontext " + "$menutype $mid $middir $mircdir $mircexe $mircini $mklogfn $mnick $mode " + "$modefirst $modelast $modespl $mouse $msfile $network $newnick $nick $nofile " + "$nopath $noqt $not $notags $notify $null $numeric $numok $oline $onpoly " + "$opnick $or $ord $os $passivedcc $pic $play $pnick $port $portable $portfree " + "$pos $prefix $prop $protect $puttok $qt $query $rand $r $rawmsg $read $readomo " + "$readn $regex $regml $regsub $regsubex $remove $remtok $replace $replacex " + "$reptok $result $rgb $right $round $scid $scon $script $scriptdir $scriptline " + "$sdir $send $server $serverip $sfile $sha1 $shortfn $show $signal $sin " + "$site $sline $snick $snicks $snotify $sock $sockbr $sockerr $sockname " + "$sorttok $sound $sqrt $ssl $sreq $sslready $status $strip $str $stripped " + "$syle $submenu $switchbar $tan $target $ticks $time $timer $timestamp " + "$timestampfmt $timezone $tip $titlebar $toolbar $treebar $trust $ulevel " + "$ulist $upper $uptime $url $usermode $v1 $v2 $var $vcmd $vcmdstat $vcmdver " + "$version $vnick $vol $wid $width $wildsite $wildtok $window $wrap $xor");
var keywords = parseWords("abook ajinvite alias aline ame amsg anick aop auser autojoin avoice " + "away background ban bcopy beep bread break breplace bset btrunc bunset bwrite " + "channel clear clearall cline clipboard close cnick color comclose comopen " + "comreg continue copy creq ctcpreply ctcps dcc dccserver dde ddeserver " + "debug dec describe dialog did didtok disable disconnect dlevel dline dll " + "dns dqwindow drawcopy drawdot drawfill drawline drawpic drawrect drawreplace " + "drawrot drawsave drawscroll drawtext ebeeps echo editbox emailaddr enable " + "events exit fclose filter findtext finger firewall flash flist flood flush " + "flushini font fopen fseek fsend fserve fullname fwrite ghide gload gmove " + "gopts goto gplay gpoint gqreq groups gshow gsize gstop gtalk gunload hadd " + "halt haltdef hdec hdel help hfree hinc hload hmake hop hsave ial ialclear " + "ialmark identd if ignore iline inc invite iuser join kick linesep links list " + "load loadbuf localinfo log mdi me menubar mkdir mnick mode msg nick noop notice " + "notify omsg onotice part partall pdcc perform play playctrl pop protect pvoice " + "qme qmsg query queryn quit raw reload remini remote remove rename renwin " + "reseterror resetidle return rlevel rline rmdir run ruser save savebuf saveini " + "say scid scon server set showmirc signam sline sockaccept sockclose socklist " + "socklisten sockmark sockopen sockpause sockread sockrename sockudp sockwrite " + "sound speak splay sreq strip switchbar timer timestamp titlebar tnick tokenize " + "toolbar topic tray treebar ulist unload unset unsetall updatenl url uwho " + "var vcadd vcmd vcrem vol while whois window winhelp write writeint if isalnum " + "isalpha isaop isavoice isban ischan ishop isignore isin isincs isletter islower " + "isnotify isnum ison isop isprotect isreg isupper isvoice iswm iswmcs " + "elseif else goto menu nicklist status title icon size option text edit " + "button check radio box scroll list combo link tab item");
var functions = parseWords("if elseif else and not or eq ne in ni for foreach while switch");
var isOperatorChar = /[+\-*&%=<>!?^\/\|]/;
function chain(stream, state, f) {
  state.tokenize = f;
  return f(stream, state);
}
function tokenBase(stream, state) {
  var beforeParams = state.beforeParams;
  state.beforeParams = false;
  var ch = stream.next();
  if (/[\[\]{}\(\),\.]/.test(ch)) {
    if (ch == "(" && beforeParams) state.inParams = true;else if (ch == ")") state.inParams = false;
    return null;
  } else if (/\d/.test(ch)) {
    stream.eatWhile(/[\w\.]/);
    return "number";
  } else if (ch == "\\") {
    stream.eat("\\");
    stream.eat(/./);
    return "number";
  } else if (ch == "/" && stream.eat("*")) {
    return chain(stream, state, tokenComment);
  } else if (ch == ";" && stream.match(/ *\( *\(/)) {
    return chain(stream, state, tokenUnparsed);
  } else if (ch == ";" && !state.inParams) {
    stream.skipToEnd();
    return "comment";
  } else if (ch == '"') {
    stream.eat(/"/);
    return "keyword";
  } else if (ch == "$") {
    stream.eatWhile(/[$_a-z0-9A-Z\.:]/);
    if (specials && specials.propertyIsEnumerable(stream.current().toLowerCase())) {
      return "keyword";
    } else {
      state.beforeParams = true;
      return "builtin";
    }
  } else if (ch == "%") {
    stream.eatWhile(/[^,\s()]/);
    state.beforeParams = true;
    return "string";
  } else if (isOperatorChar.test(ch)) {
    stream.eatWhile(isOperatorChar);
    return "operator";
  } else {
    stream.eatWhile(/[\w\$_{}]/);
    var word = stream.current().toLowerCase();
    if (keywords && keywords.propertyIsEnumerable(word)) return "keyword";
    if (functions && functions.propertyIsEnumerable(word)) {
      state.beforeParams = true;
      return "keyword";
    }
    return null;
  }
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
function tokenUnparsed(stream, state) {
  var maybeEnd = 0,
    ch;
  while (ch = stream.next()) {
    if (ch == ";" && maybeEnd == 2) {
      state.tokenize = tokenBase;
      break;
    }
    if (ch == ")") maybeEnd++;else if (ch != " ") maybeEnd = 0;
  }
  return "meta";
}
const mirc = {
  name: "mirc",
  startState: function () {
    return {
      tokenize: tokenBase,
      beforeParams: false,
      inParams: false
    };
  },
  token: function (stream, state) {
    if (stream.eatSpace()) return null;
    return state.tokenize(stream, state);
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiOTkxMy5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL21pcmMuanMiXSwic291cmNlc0NvbnRlbnQiOlsiZnVuY3Rpb24gcGFyc2VXb3JkcyhzdHIpIHtcbiAgdmFyIG9iaiA9IHt9LFxuICAgIHdvcmRzID0gc3RyLnNwbGl0KFwiIFwiKTtcbiAgZm9yICh2YXIgaSA9IDA7IGkgPCB3b3Jkcy5sZW5ndGg7ICsraSkgb2JqW3dvcmRzW2ldXSA9IHRydWU7XG4gIHJldHVybiBvYmo7XG59XG52YXIgc3BlY2lhbHMgPSBwYXJzZVdvcmRzKFwiJCEgJCQgJCYgJD8gJCsgJGFib29rICRhYnMgJGFjdGl2ZSAkYWN0aXZlY2lkIFwiICsgXCIkYWN0aXZld2lkICRhZGRyZXNzICRhZGR0b2sgJGFnZW50ICRhZ2VudG5hbWUgJGFnZW50c3RhdCAkYWdlbnR2ZXIgXCIgKyBcIiRhbGlhcyAkYW5kICRhbmljayAkYW5zaTJtaXJjICRhb3AgJGFwcGFjdGl2ZSAkYXBwc3RhdGUgJGFzYyAkYXNjdGltZSBcIiArIFwiJGFzaW4gJGF0YW4gJGF2b2ljZSAkYXdheSAkYXdheW1zZyAkYXdheXRpbWUgJGJhbm1hc2sgJGJhc2UgJGJmaW5kIFwiICsgXCIkYmlub2ZmICRiaXRvbiAkYm5pY2sgJGJ2YXIgJGJ5dGVzICRjYWxjICRjYiAkY2QgJGNlaWwgJGNoYW4gJGNoYW5tb2RlcyBcIiArIFwiJGNoYW50eXBlcyAkY2hhdCAkY2hyICRjaWQgJGNsZXZlbCAkY2xpY2sgJGNtZGJveCAkY21kbGluZSAkY25pY2sgJGNvbG9yIFwiICsgXCIkY29tICRjb21jYWxsICRjb21jaGFuICRjb21lcnIgJGNvbXBhY3QgJGNvbXByZXNzICRjb212YWwgJGNvcyAkY291bnQgXCIgKyBcIiRjciAkY3JjICRjcmVxICRjcmxmICRjdGltZSAkY3RpbWVyICRjdHJsZW50ZXIgJGRhdGUgJGRheSAkZGF5bGlnaHQgXCIgKyBcIiRkYnVoICRkYnV3ICRkY2NpZ25vcmUgJGRjY3BvcnQgJGRkZSAkZGRlbmFtZSAkZGVidWcgJGRlY29kZSAkZGVjb21wcmVzcyBcIiArIFwiJGRlbHRvayAkZGV2ZW50ICRkaWFsb2cgJGRpZCAkZGlkcmVnICRkaWR0b2sgJGRpZHdtICRkaXNrICRkbGV2ZWwgJGRsbCBcIiArIFwiJGRsbGNhbGwgJGRuYW1lICRkbnMgJGR1cmF0aW9uICRlYmVlcHMgJGVkaXRib3ggJGVtYWlsYWRkciAkZW5jb2RlICRlcnJvciBcIiArIFwiJGV2YWwgJGV2ZW50ICRleGlzdCAkZmVvZiAkZmVyciAkZmdldGMgJGZpbGUgJGZpbGVuYW1lICRmaWx0ZXJlZCAkZmluZGRpciBcIiArIFwiJGZpbmRkaXJuICRmaW5kZmlsZSAkZmluZGZpbGVuICRmaW5kdG9rICRmbGluZSAkZmxvb3IgJGZvcGVuICRmcmVhZCAkZnNlcnZlIFwiICsgXCIkZnVsbGFkZHJlc3MgJGZ1bGxkYXRlICRmdWxsbmFtZSAkZnVsbHNjcmVlbiAkZ2V0ICRnZXRkaXIgJGdldGRvdCAkZ2V0dG9rICRnbXQgXCIgKyBcIiRncm91cCAkaGFsdGVkICRoYXNoICRoZWlnaHQgJGhmaW5kICRoZ2V0ICRoaWdobGlnaHQgJGhuaWNrICRob3RsaW5lIFwiICsgXCIkaG90bGluZXBvcyAkaWFsICRpYWxjaGFuICRpYmwgJGlkbGUgJGllbCAkaWZtYXRjaCAkaWdub3JlICRpaWYgJGlpbCBcIiArIFwiJGluZWxpcHNlICRpbmkgJGlubWlkaSAkaW5wYXN0ZSAkaW5wb2x5ICRpbnB1dCAkaW5yZWN0ICRpbnJvdW5kcmVjdCBcIiArIFwiJGluc29uZyAkaW5zdG9rICRpbnQgJGlud2F2ZSAkaXAgJGlzYWxpYXMgJGlzYml0ICRpc2RkZSAkaXNkaXIgJGlzZmlsZSBcIiArIFwiJGlzaWQgJGlzbG93ZXIgJGlzdG9rICRpc3VwcGVyICRrZXljaGFyICRrZXlycHQgJGtleXZhbCAka25pY2sgJGxhY3RpdmUgXCIgKyBcIiRsYWN0aXZlY2lkICRsYWN0aXZld2lkICRsZWZ0ICRsZW4gJGxldmVsICRsZiAkbGluZSAkbGluZXMgJGxpbmsgJGxvY2sgXCIgKyBcIiRsb2NrICRsb2NrZWQgJGxvZyAkbG9nc3RhbXAgJGxvZ3N0YW1wZm10ICRsb25nZm4gJGxvbmdpcCAkbG93ZXIgJGx0aW1lciBcIiArIFwiJG1hZGRyZXNzICRtYXNrICRtYXRjaGtleSAkbWF0Y2h0b2sgJG1kNSAkbWUgJG1lbnUgJG1lbnViYXIgJG1lbnVjb250ZXh0IFwiICsgXCIkbWVudXR5cGUgJG1pZCAkbWlkZGlyICRtaXJjZGlyICRtaXJjZXhlICRtaXJjaW5pICRta2xvZ2ZuICRtbmljayAkbW9kZSBcIiArIFwiJG1vZGVmaXJzdCAkbW9kZWxhc3QgJG1vZGVzcGwgJG1vdXNlICRtc2ZpbGUgJG5ldHdvcmsgJG5ld25pY2sgJG5pY2sgJG5vZmlsZSBcIiArIFwiJG5vcGF0aCAkbm9xdCAkbm90ICRub3RhZ3MgJG5vdGlmeSAkbnVsbCAkbnVtZXJpYyAkbnVtb2sgJG9saW5lICRvbnBvbHkgXCIgKyBcIiRvcG5pY2sgJG9yICRvcmQgJG9zICRwYXNzaXZlZGNjICRwaWMgJHBsYXkgJHBuaWNrICRwb3J0ICRwb3J0YWJsZSAkcG9ydGZyZWUgXCIgKyBcIiRwb3MgJHByZWZpeCAkcHJvcCAkcHJvdGVjdCAkcHV0dG9rICRxdCAkcXVlcnkgJHJhbmQgJHIgJHJhd21zZyAkcmVhZCAkcmVhZG9tbyBcIiArIFwiJHJlYWRuICRyZWdleCAkcmVnbWwgJHJlZ3N1YiAkcmVnc3ViZXggJHJlbW92ZSAkcmVtdG9rICRyZXBsYWNlICRyZXBsYWNleCBcIiArIFwiJHJlcHRvayAkcmVzdWx0ICRyZ2IgJHJpZ2h0ICRyb3VuZCAkc2NpZCAkc2NvbiAkc2NyaXB0ICRzY3JpcHRkaXIgJHNjcmlwdGxpbmUgXCIgKyBcIiRzZGlyICRzZW5kICRzZXJ2ZXIgJHNlcnZlcmlwICRzZmlsZSAkc2hhMSAkc2hvcnRmbiAkc2hvdyAkc2lnbmFsICRzaW4gXCIgKyBcIiRzaXRlICRzbGluZSAkc25pY2sgJHNuaWNrcyAkc25vdGlmeSAkc29jayAkc29ja2JyICRzb2NrZXJyICRzb2NrbmFtZSBcIiArIFwiJHNvcnR0b2sgJHNvdW5kICRzcXJ0ICRzc2wgJHNyZXEgJHNzbHJlYWR5ICRzdGF0dXMgJHN0cmlwICRzdHIgJHN0cmlwcGVkIFwiICsgXCIkc3lsZSAkc3VibWVudSAkc3dpdGNoYmFyICR0YW4gJHRhcmdldCAkdGlja3MgJHRpbWUgJHRpbWVyICR0aW1lc3RhbXAgXCIgKyBcIiR0aW1lc3RhbXBmbXQgJHRpbWV6b25lICR0aXAgJHRpdGxlYmFyICR0b29sYmFyICR0cmVlYmFyICR0cnVzdCAkdWxldmVsIFwiICsgXCIkdWxpc3QgJHVwcGVyICR1cHRpbWUgJHVybCAkdXNlcm1vZGUgJHYxICR2MiAkdmFyICR2Y21kICR2Y21kc3RhdCAkdmNtZHZlciBcIiArIFwiJHZlcnNpb24gJHZuaWNrICR2b2wgJHdpZCAkd2lkdGggJHdpbGRzaXRlICR3aWxkdG9rICR3aW5kb3cgJHdyYXAgJHhvclwiKTtcbnZhciBrZXl3b3JkcyA9IHBhcnNlV29yZHMoXCJhYm9vayBhamludml0ZSBhbGlhcyBhbGluZSBhbWUgYW1zZyBhbmljayBhb3AgYXVzZXIgYXV0b2pvaW4gYXZvaWNlIFwiICsgXCJhd2F5IGJhY2tncm91bmQgYmFuIGJjb3B5IGJlZXAgYnJlYWQgYnJlYWsgYnJlcGxhY2UgYnNldCBidHJ1bmMgYnVuc2V0IGJ3cml0ZSBcIiArIFwiY2hhbm5lbCBjbGVhciBjbGVhcmFsbCBjbGluZSBjbGlwYm9hcmQgY2xvc2UgY25pY2sgY29sb3IgY29tY2xvc2UgY29tb3BlbiBcIiArIFwiY29tcmVnIGNvbnRpbnVlIGNvcHkgY3JlcSBjdGNwcmVwbHkgY3RjcHMgZGNjIGRjY3NlcnZlciBkZGUgZGRlc2VydmVyIFwiICsgXCJkZWJ1ZyBkZWMgZGVzY3JpYmUgZGlhbG9nIGRpZCBkaWR0b2sgZGlzYWJsZSBkaXNjb25uZWN0IGRsZXZlbCBkbGluZSBkbGwgXCIgKyBcImRucyBkcXdpbmRvdyBkcmF3Y29weSBkcmF3ZG90IGRyYXdmaWxsIGRyYXdsaW5lIGRyYXdwaWMgZHJhd3JlY3QgZHJhd3JlcGxhY2UgXCIgKyBcImRyYXdyb3QgZHJhd3NhdmUgZHJhd3Njcm9sbCBkcmF3dGV4dCBlYmVlcHMgZWNobyBlZGl0Ym94IGVtYWlsYWRkciBlbmFibGUgXCIgKyBcImV2ZW50cyBleGl0IGZjbG9zZSBmaWx0ZXIgZmluZHRleHQgZmluZ2VyIGZpcmV3YWxsIGZsYXNoIGZsaXN0IGZsb29kIGZsdXNoIFwiICsgXCJmbHVzaGluaSBmb250IGZvcGVuIGZzZWVrIGZzZW5kIGZzZXJ2ZSBmdWxsbmFtZSBmd3JpdGUgZ2hpZGUgZ2xvYWQgZ21vdmUgXCIgKyBcImdvcHRzIGdvdG8gZ3BsYXkgZ3BvaW50IGdxcmVxIGdyb3VwcyBnc2hvdyBnc2l6ZSBnc3RvcCBndGFsayBndW5sb2FkIGhhZGQgXCIgKyBcImhhbHQgaGFsdGRlZiBoZGVjIGhkZWwgaGVscCBoZnJlZSBoaW5jIGhsb2FkIGhtYWtlIGhvcCBoc2F2ZSBpYWwgaWFsY2xlYXIgXCIgKyBcImlhbG1hcmsgaWRlbnRkIGlmIGlnbm9yZSBpbGluZSBpbmMgaW52aXRlIGl1c2VyIGpvaW4ga2ljayBsaW5lc2VwIGxpbmtzIGxpc3QgXCIgKyBcImxvYWQgbG9hZGJ1ZiBsb2NhbGluZm8gbG9nIG1kaSBtZSBtZW51YmFyIG1rZGlyIG1uaWNrIG1vZGUgbXNnIG5pY2sgbm9vcCBub3RpY2UgXCIgKyBcIm5vdGlmeSBvbXNnIG9ub3RpY2UgcGFydCBwYXJ0YWxsIHBkY2MgcGVyZm9ybSBwbGF5IHBsYXljdHJsIHBvcCBwcm90ZWN0IHB2b2ljZSBcIiArIFwicW1lIHFtc2cgcXVlcnkgcXVlcnluIHF1aXQgcmF3IHJlbG9hZCByZW1pbmkgcmVtb3RlIHJlbW92ZSByZW5hbWUgcmVud2luIFwiICsgXCJyZXNldGVycm9yIHJlc2V0aWRsZSByZXR1cm4gcmxldmVsIHJsaW5lIHJtZGlyIHJ1biBydXNlciBzYXZlIHNhdmVidWYgc2F2ZWluaSBcIiArIFwic2F5IHNjaWQgc2NvbiBzZXJ2ZXIgc2V0IHNob3dtaXJjIHNpZ25hbSBzbGluZSBzb2NrYWNjZXB0IHNvY2tjbG9zZSBzb2NrbGlzdCBcIiArIFwic29ja2xpc3RlbiBzb2NrbWFyayBzb2Nrb3BlbiBzb2NrcGF1c2Ugc29ja3JlYWQgc29ja3JlbmFtZSBzb2NrdWRwIHNvY2t3cml0ZSBcIiArIFwic291bmQgc3BlYWsgc3BsYXkgc3JlcSBzdHJpcCBzd2l0Y2hiYXIgdGltZXIgdGltZXN0YW1wIHRpdGxlYmFyIHRuaWNrIHRva2VuaXplIFwiICsgXCJ0b29sYmFyIHRvcGljIHRyYXkgdHJlZWJhciB1bGlzdCB1bmxvYWQgdW5zZXQgdW5zZXRhbGwgdXBkYXRlbmwgdXJsIHV3aG8gXCIgKyBcInZhciB2Y2FkZCB2Y21kIHZjcmVtIHZvbCB3aGlsZSB3aG9pcyB3aW5kb3cgd2luaGVscCB3cml0ZSB3cml0ZWludCBpZiBpc2FsbnVtIFwiICsgXCJpc2FscGhhIGlzYW9wIGlzYXZvaWNlIGlzYmFuIGlzY2hhbiBpc2hvcCBpc2lnbm9yZSBpc2luIGlzaW5jcyBpc2xldHRlciBpc2xvd2VyIFwiICsgXCJpc25vdGlmeSBpc251bSBpc29uIGlzb3AgaXNwcm90ZWN0IGlzcmVnIGlzdXBwZXIgaXN2b2ljZSBpc3dtIGlzd21jcyBcIiArIFwiZWxzZWlmIGVsc2UgZ290byBtZW51IG5pY2tsaXN0IHN0YXR1cyB0aXRsZSBpY29uIHNpemUgb3B0aW9uIHRleHQgZWRpdCBcIiArIFwiYnV0dG9uIGNoZWNrIHJhZGlvIGJveCBzY3JvbGwgbGlzdCBjb21ibyBsaW5rIHRhYiBpdGVtXCIpO1xudmFyIGZ1bmN0aW9ucyA9IHBhcnNlV29yZHMoXCJpZiBlbHNlaWYgZWxzZSBhbmQgbm90IG9yIGVxIG5lIGluIG5pIGZvciBmb3JlYWNoIHdoaWxlIHN3aXRjaFwiKTtcbnZhciBpc09wZXJhdG9yQ2hhciA9IC9bK1xcLSomJT08PiE/XlxcL1xcfF0vO1xuZnVuY3Rpb24gY2hhaW4oc3RyZWFtLCBzdGF0ZSwgZikge1xuICBzdGF0ZS50b2tlbml6ZSA9IGY7XG4gIHJldHVybiBmKHN0cmVhbSwgc3RhdGUpO1xufVxuZnVuY3Rpb24gdG9rZW5CYXNlKHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIGJlZm9yZVBhcmFtcyA9IHN0YXRlLmJlZm9yZVBhcmFtcztcbiAgc3RhdGUuYmVmb3JlUGFyYW1zID0gZmFsc2U7XG4gIHZhciBjaCA9IHN0cmVhbS5uZXh0KCk7XG4gIGlmICgvW1xcW1xcXXt9XFwoXFwpLFxcLl0vLnRlc3QoY2gpKSB7XG4gICAgaWYgKGNoID09IFwiKFwiICYmIGJlZm9yZVBhcmFtcykgc3RhdGUuaW5QYXJhbXMgPSB0cnVlO2Vsc2UgaWYgKGNoID09IFwiKVwiKSBzdGF0ZS5pblBhcmFtcyA9IGZhbHNlO1xuICAgIHJldHVybiBudWxsO1xuICB9IGVsc2UgaWYgKC9cXGQvLnRlc3QoY2gpKSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFwuXS8pO1xuICAgIHJldHVybiBcIm51bWJlclwiO1xuICB9IGVsc2UgaWYgKGNoID09IFwiXFxcXFwiKSB7XG4gICAgc3RyZWFtLmVhdChcIlxcXFxcIik7XG4gICAgc3RyZWFtLmVhdCgvLi8pO1xuICAgIHJldHVybiBcIm51bWJlclwiO1xuICB9IGVsc2UgaWYgKGNoID09IFwiL1wiICYmIHN0cmVhbS5lYXQoXCIqXCIpKSB7XG4gICAgcmV0dXJuIGNoYWluKHN0cmVhbSwgc3RhdGUsIHRva2VuQ29tbWVudCk7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCI7XCIgJiYgc3RyZWFtLm1hdGNoKC8gKlxcKCAqXFwoLykpIHtcbiAgICByZXR1cm4gY2hhaW4oc3RyZWFtLCBzdGF0ZSwgdG9rZW5VbnBhcnNlZCk7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCI7XCIgJiYgIXN0YXRlLmluUGFyYW1zKSB7XG4gICAgc3RyZWFtLnNraXBUb0VuZCgpO1xuICAgIHJldHVybiBcImNvbW1lbnRcIjtcbiAgfSBlbHNlIGlmIChjaCA9PSAnXCInKSB7XG4gICAgc3RyZWFtLmVhdCgvXCIvKTtcbiAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCIkXCIpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1skX2EtejAtOUEtWlxcLjpdLyk7XG4gICAgaWYgKHNwZWNpYWxzICYmIHNwZWNpYWxzLnByb3BlcnR5SXNFbnVtZXJhYmxlKHN0cmVhbS5jdXJyZW50KCkudG9Mb3dlckNhc2UoKSkpIHtcbiAgICAgIHJldHVybiBcImtleXdvcmRcIjtcbiAgICB9IGVsc2Uge1xuICAgICAgc3RhdGUuYmVmb3JlUGFyYW1zID0gdHJ1ZTtcbiAgICAgIHJldHVybiBcImJ1aWx0aW5cIjtcbiAgICB9XG4gIH0gZWxzZSBpZiAoY2ggPT0gXCIlXCIpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoL1teLFxccygpXS8pO1xuICAgIHN0YXRlLmJlZm9yZVBhcmFtcyA9IHRydWU7XG4gICAgcmV0dXJuIFwic3RyaW5nXCI7XG4gIH0gZWxzZSBpZiAoaXNPcGVyYXRvckNoYXIudGVzdChjaCkpIHtcbiAgICBzdHJlYW0uZWF0V2hpbGUoaXNPcGVyYXRvckNoYXIpO1xuICAgIHJldHVybiBcIm9wZXJhdG9yXCI7XG4gIH0gZWxzZSB7XG4gICAgc3RyZWFtLmVhdFdoaWxlKC9bXFx3XFwkX3t9XS8pO1xuICAgIHZhciB3b3JkID0gc3RyZWFtLmN1cnJlbnQoKS50b0xvd2VyQ2FzZSgpO1xuICAgIGlmIChrZXl3b3JkcyAmJiBrZXl3b3Jkcy5wcm9wZXJ0eUlzRW51bWVyYWJsZSh3b3JkKSkgcmV0dXJuIFwia2V5d29yZFwiO1xuICAgIGlmIChmdW5jdGlvbnMgJiYgZnVuY3Rpb25zLnByb3BlcnR5SXNFbnVtZXJhYmxlKHdvcmQpKSB7XG4gICAgICBzdGF0ZS5iZWZvcmVQYXJhbXMgPSB0cnVlO1xuICAgICAgcmV0dXJuIFwia2V5d29yZFwiO1xuICAgIH1cbiAgICByZXR1cm4gbnVsbDtcbiAgfVxufVxuZnVuY3Rpb24gdG9rZW5Db21tZW50KHN0cmVhbSwgc3RhdGUpIHtcbiAgdmFyIG1heWJlRW5kID0gZmFsc2UsXG4gICAgY2g7XG4gIHdoaWxlIChjaCA9IHN0cmVhbS5uZXh0KCkpIHtcbiAgICBpZiAoY2ggPT0gXCIvXCIgJiYgbWF5YmVFbmQpIHtcbiAgICAgIHN0YXRlLnRva2VuaXplID0gdG9rZW5CYXNlO1xuICAgICAgYnJlYWs7XG4gICAgfVxuICAgIG1heWJlRW5kID0gY2ggPT0gXCIqXCI7XG4gIH1cbiAgcmV0dXJuIFwiY29tbWVudFwiO1xufVxuZnVuY3Rpb24gdG9rZW5VbnBhcnNlZChzdHJlYW0sIHN0YXRlKSB7XG4gIHZhciBtYXliZUVuZCA9IDAsXG4gICAgY2g7XG4gIHdoaWxlIChjaCA9IHN0cmVhbS5uZXh0KCkpIHtcbiAgICBpZiAoY2ggPT0gXCI7XCIgJiYgbWF5YmVFbmQgPT0gMikge1xuICAgICAgc3RhdGUudG9rZW5pemUgPSB0b2tlbkJhc2U7XG4gICAgICBicmVhaztcbiAgICB9XG4gICAgaWYgKGNoID09IFwiKVwiKSBtYXliZUVuZCsrO2Vsc2UgaWYgKGNoICE9IFwiIFwiKSBtYXliZUVuZCA9IDA7XG4gIH1cbiAgcmV0dXJuIFwibWV0YVwiO1xufVxuZXhwb3J0IGNvbnN0IG1pcmMgPSB7XG4gIG5hbWU6IFwibWlyY1wiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIHRva2VuaXplOiB0b2tlbkJhc2UsXG4gICAgICBiZWZvcmVQYXJhbXM6IGZhbHNlLFxuICAgICAgaW5QYXJhbXM6IGZhbHNlXG4gICAgfTtcbiAgfSxcbiAgdG9rZW46IGZ1bmN0aW9uIChzdHJlYW0sIHN0YXRlKSB7XG4gICAgaWYgKHN0cmVhbS5lYXRTcGFjZSgpKSByZXR1cm4gbnVsbDtcbiAgICByZXR1cm4gc3RhdGUudG9rZW5pemUoc3RyZWFtLCBzdGF0ZSk7XG4gIH1cbn07Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==