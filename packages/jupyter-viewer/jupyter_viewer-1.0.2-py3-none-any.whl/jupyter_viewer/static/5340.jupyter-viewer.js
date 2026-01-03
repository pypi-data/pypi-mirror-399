"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[5340],{

/***/ 45340
(__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   gherkin: () => (/* binding */ gherkin)
/* harmony export */ });
const gherkin = {
  name: "gherkin",
  startState: function () {
    return {
      lineNumber: 0,
      tableHeaderLine: false,
      allowFeature: true,
      allowBackground: false,
      allowScenario: false,
      allowSteps: false,
      allowPlaceholders: false,
      allowMultilineArgument: false,
      inMultilineString: false,
      inMultilineTable: false,
      inKeywordLine: false
    };
  },
  token: function (stream, state) {
    if (stream.sol()) {
      state.lineNumber++;
      state.inKeywordLine = false;
      if (state.inMultilineTable) {
        state.tableHeaderLine = false;
        if (!stream.match(/\s*\|/, false)) {
          state.allowMultilineArgument = false;
          state.inMultilineTable = false;
        }
      }
    }
    stream.eatSpace();
    if (state.allowMultilineArgument) {
      // STRING
      if (state.inMultilineString) {
        if (stream.match('"""')) {
          state.inMultilineString = false;
          state.allowMultilineArgument = false;
        } else {
          stream.match(/.*/);
        }
        return "string";
      }

      // TABLE
      if (state.inMultilineTable) {
        if (stream.match(/\|\s*/)) {
          return "bracket";
        } else {
          stream.match(/[^\|]*/);
          return state.tableHeaderLine ? "header" : "string";
        }
      }

      // DETECT START
      if (stream.match('"""')) {
        // String
        state.inMultilineString = true;
        return "string";
      } else if (stream.match("|")) {
        // Table
        state.inMultilineTable = true;
        state.tableHeaderLine = true;
        return "bracket";
      }
    }

    // LINE COMMENT
    if (stream.match(/#.*/)) {
      return "comment";

      // TAG
    } else if (!state.inKeywordLine && stream.match(/@\S+/)) {
      return "tag";

      // FEATURE
    } else if (!state.inKeywordLine && state.allowFeature && stream.match(/(機能|功能|フィーチャ|기능|โครงหลัก|ความสามารถ|ความต้องการทางธุรกิจ|ಹೆಚ್ಚಳ|గుణము|ਮੁਹਾਂਦਰਾ|ਨਕਸ਼ ਨੁਹਾਰ|ਖਾਸੀਅਤ|रूप लेख|وِیژگی|خاصية|תכונה|Функціонал|Функция|Функционалност|Функционал|Үзенчәлеклелек|Свойство|Особина|Мөмкинлек|Могућност|Λειτουργία|Δυνατότητα|Właściwość|Vlastnosť|Trajto|Tính năng|Savybė|Pretty much|Požiadavka|Požadavek|Potrzeba biznesowa|Özellik|Osobina|Ominaisuus|Omadus|OH HAI|Mogućnost|Mogucnost|Jellemző|Hwæt|Hwaet|Funzionalità|Funktionalitéit|Funktionalität|Funkcja|Funkcionalnost|Funkcionalitāte|Funkcia|Fungsi|Functionaliteit|Funcționalitate|Funcţionalitate|Functionalitate|Funcionalitat|Funcionalidade|Fonctionnalité|Fitur|Fīča|Feature|Eiginleiki|Egenskap|Egenskab|Característica|Caracteristica|Business Need|Aspekt|Arwedd|Ahoy matey!|Ability):/)) {
      state.allowScenario = true;
      state.allowBackground = true;
      state.allowPlaceholders = false;
      state.allowSteps = false;
      state.allowMultilineArgument = false;
      state.inKeywordLine = true;
      return "keyword";

      // BACKGROUND
    } else if (!state.inKeywordLine && state.allowBackground && stream.match(/(背景|배경|แนวคิด|ಹಿನ್ನೆಲೆ|నేపథ్యం|ਪਿਛੋਕੜ|पृष्ठभूमि|زمینه|الخلفية|רקע|Тарих|Предыстория|Предистория|Позадина|Передумова|Основа|Контекст|Кереш|Υπόβαθρο|Założenia|Yo\-ho\-ho|Tausta|Taust|Situācija|Rerefons|Pozadina|Pozadie|Pozadí|Osnova|Latar Belakang|Kontext|Konteksts|Kontekstas|Kontekst|Háttér|Hannergrond|Grundlage|Geçmiş|Fundo|Fono|First off|Dis is what went down|Dasar|Contexto|Contexte|Context|Contesto|Cenário de Fundo|Cenario de Fundo|Cefndir|Bối cảnh|Bakgrunnur|Bakgrunn|Bakgrund|Baggrund|Background|B4|Antecedents|Antecedentes|Ær|Aer|Achtergrond):/)) {
      state.allowPlaceholders = false;
      state.allowSteps = true;
      state.allowBackground = false;
      state.allowMultilineArgument = false;
      state.inKeywordLine = true;
      return "keyword";

      // SCENARIO OUTLINE
    } else if (!state.inKeywordLine && state.allowScenario && stream.match(/(場景大綱|场景大纲|劇本大綱|剧本大纲|テンプレ|シナリオテンプレート|シナリオテンプレ|シナリオアウトライン|시나리오 개요|สรุปเหตุการณ์|โครงสร้างของเหตุการณ์|ವಿವರಣೆ|కథనం|ਪਟਕਥਾ ਰੂਪ ਰੇਖਾ|ਪਟਕਥਾ ਢਾਂਚਾ|परिदृश्य रूपरेखा|سيناريو مخطط|الگوی سناریو|תבנית תרחיש|Сценарийның төзелеше|Сценарий структураси|Структура сценарію|Структура сценария|Структура сценарија|Скица|Рамка на сценарий|Концепт|Περιγραφή Σεναρίου|Wharrimean is|Template Situai|Template Senario|Template Keadaan|Tapausaihio|Szenariogrundriss|Szablon scenariusza|Swa hwær swa|Swa hwaer swa|Struktura scenarija|Structură scenariu|Structura scenariu|Skica|Skenario konsep|Shiver me timbers|Senaryo taslağı|Schema dello scenario|Scenariomall|Scenariomal|Scenario Template|Scenario Outline|Scenario Amlinellol|Scenārijs pēc parauga|Scenarijaus šablonas|Reckon it's like|Raamstsenaarium|Plang vum Szenario|Plan du Scénario|Plan du scénario|Osnova scénáře|Osnova Scenára|Náčrt Scenáru|Náčrt Scénáře|Náčrt Scenára|MISHUN SRSLY|Menggariskan Senario|Lýsing Dæma|Lýsing Atburðarásar|Konturo de la scenaro|Koncept|Khung tình huống|Khung kịch bản|Forgatókönyv vázlat|Esquema do Cenário|Esquema do Cenario|Esquema del escenario|Esquema de l'escenari|Esbozo do escenario|Delineação do Cenário|Delineacao do Cenario|All y'all|Abstrakt Scenario|Abstract Scenario):/)) {
      state.allowPlaceholders = true;
      state.allowSteps = true;
      state.allowMultilineArgument = false;
      state.inKeywordLine = true;
      return "keyword";

      // EXAMPLES
    } else if (state.allowScenario && stream.match(/(例子|例|サンプル|예|ชุดของเหตุการณ์|ชุดของตัวอย่าง|ಉದಾಹರಣೆಗಳು|ఉదాహరణలు|ਉਦਾਹਰਨਾਂ|उदाहरण|نمونه ها|امثلة|דוגמאות|Үрнәкләр|Сценарији|Примеры|Примери|Приклади|Мисоллар|Мисаллар|Σενάρια|Παραδείγματα|You'll wanna|Voorbeelden|Variantai|Tapaukset|Se þe|Se the|Se ðe|Scenarios|Scenariji|Scenarijai|Przykłady|Primjeri|Primeri|Příklady|Príklady|Piemēri|Példák|Pavyzdžiai|Paraugs|Örnekler|Juhtumid|Exemplos|Exemples|Exemple|Exempel|EXAMPLZ|Examples|Esempi|Enghreifftiau|Ekzemploj|Eksempler|Ejemplos|Dữ liệu|Dead men tell no tales|Dæmi|Contoh|Cenários|Cenarios|Beispiller|Beispiele|Atburðarásir):/)) {
      state.allowPlaceholders = false;
      state.allowSteps = true;
      state.allowBackground = false;
      state.allowMultilineArgument = true;
      return "keyword";

      // SCENARIO
    } else if (!state.inKeywordLine && state.allowScenario && stream.match(/(場景|场景|劇本|剧本|シナリオ|시나리오|เหตุการณ์|ಕಥಾಸಾರಾಂಶ|సన్నివేశం|ਪਟਕਥਾ|परिदृश्य|سيناريو|سناریو|תרחיש|Сценарій|Сценарио|Сценарий|Пример|Σενάριο|Tình huống|The thing of it is|Tapaus|Szenario|Swa|Stsenaarium|Skenario|Situai|Senaryo|Senario|Scenaro|Scenariusz|Scenariu|Scénario|Scenario|Scenarijus|Scenārijs|Scenarij|Scenarie|Scénář|Scenár|Primer|MISHUN|Kịch bản|Keadaan|Heave to|Forgatókönyv|Escenario|Escenari|Cenário|Cenario|Awww, look mate|Atburðarás):/)) {
      state.allowPlaceholders = false;
      state.allowSteps = true;
      state.allowBackground = false;
      state.allowMultilineArgument = false;
      state.inKeywordLine = true;
      return "keyword";

      // STEPS
    } else if (!state.inKeywordLine && state.allowSteps && stream.match(/(那麼|那么|而且|當|当|并且|同時|同时|前提|假设|假設|假定|假如|但是|但し|並且|もし|ならば|ただし|しかし|かつ|하지만|조건|먼저|만일|만약|단|그리고|그러면|และ |เมื่อ |แต่ |ดังนั้น |กำหนดให้ |ಸ್ಥಿತಿಯನ್ನು |ಮತ್ತು |ನೀಡಿದ |ನಂತರ |ಆದರೆ |మరియు |చెప్పబడినది |కాని |ఈ పరిస్థితిలో |అప్పుడు |ਪਰ |ਤਦ |ਜੇਕਰ |ਜਿਵੇਂ ਕਿ |ਜਦੋਂ |ਅਤੇ |यदि |परन्तु |पर |तब |तदा |तथा |जब |चूंकि |किन्तु |कदा |और |अगर |و |هنگامی |متى |لكن |عندما |ثم |بفرض |با فرض |اما |اذاً |آنگاه |כאשר |וגם |בהינתן |אזי |אז |אבל |Якщо |Һәм |Унда |Тоді |Тогда |То |Также |Та |Пусть |Припустимо, що |Припустимо |Онда |Но |Нехай |Нәтиҗәдә |Лекин |Ләкин |Коли |Когда |Когато |Када |Кад |К тому же |І |И |Задато |Задати |Задате |Если |Допустим |Дано |Дадено |Вә |Ва |Бирок |Әмма |Әйтик |Әгәр |Аммо |Али |Але |Агар |А також |А |Τότε |Όταν |Και |Δεδομένου |Αλλά |Þurh |Þegar |Þa þe |Þá |Þa |Zatati |Zakładając |Zadato |Zadate |Zadano |Zadani |Zadan |Za předpokladu |Za predpokladu |Youse know when youse got |Youse know like when |Yna |Yeah nah |Y'know |Y |Wun |Wtedy |When y'all |When |Wenn |WEN |wann |Ve |Và |Und |Un |ugeholl |Too right |Thurh |Thì |Then y'all |Then |Tha the |Tha |Tetapi |Tapi |Tak |Tada |Tad |Stel |Soit |Siis |Și |Şi |Si |Sed |Se |Så |Quando |Quand |Quan |Pryd |Potom |Pokud |Pokiaľ |Però |Pero |Pak |Oraz |Onda |Ond |Oletetaan |Og |Och |O zaman |Niin |Nhưng |När |Når |Mutta |Men |Mas |Maka |Majd |Mając |Mais |Maar |mä |Ma |Lorsque |Lorsqu'|Logo |Let go and haul |Kun |Kuid |Kui |Kiedy |Khi |Ketika |Kemudian |Keď |Když |Kaj |Kai |Kada |Kad |Jeżeli |Jeśli |Ja |It's just unbelievable |Ir |I CAN HAZ |I |Ha |Givun |Givet |Given y'all |Given |Gitt |Gegeven |Gegeben seien |Gegeben sei |Gdy |Gangway! |Fakat |Étant donnés |Etant donnés |Étant données |Etant données |Étant donnée |Etant donnée |Étant donné |Etant donné |Et |És |Entonces |Entón |Então |Entao |En |Eğer ki |Ef |Eeldades |E |Ðurh |Duota |Dun |Donitaĵo |Donat |Donada |Do |Diyelim ki |Diberi |Dengan |Den youse gotta |DEN |De |Dato |Dați fiind |Daţi fiind |Dati fiind |Dati |Date fiind |Date |Data |Dat fiind |Dar |Dann |dann |Dan |Dados |Dado |Dadas |Dada |Ða ðe |Ða |Cuando |Cho |Cando |Când |Cand |Cal |But y'all |But at the end of the day I reckon |BUT |But |Buh |Blimey! |Biết |Bet |Bagi |Aye |awer |Avast! |Atunci |Atesa |Atès |Apabila |Anrhegedig a |Angenommen |And y'all |And |AN |An |an |Amikor |Amennyiben |Ama |Als |Alors |Allora |Ali |Aleshores |Ale |Akkor |Ak |Adott |Ac |Aber |A zároveň |A tiež |A taktiež |A také |A |a |7 |\* )/)) {
      state.inStep = true;
      state.allowPlaceholders = true;
      state.allowMultilineArgument = true;
      state.inKeywordLine = true;
      return "keyword";

      // INLINE STRING
    } else if (stream.match(/"[^"]*"?/)) {
      return "string";

      // PLACEHOLDER
    } else if (state.allowPlaceholders && stream.match(/<[^>]*>?/)) {
      return "variable";

      // Fall through
    } else {
      stream.next();
      stream.eatWhile(/[^@"<#]/);
      return null;
    }
  }
};

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiNTM0MC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL0Bjb2RlbWlycm9yL2xlZ2FjeS1tb2Rlcy9tb2RlL2doZXJraW4uanMiXSwic291cmNlc0NvbnRlbnQiOlsiZXhwb3J0IGNvbnN0IGdoZXJraW4gPSB7XG4gIG5hbWU6IFwiZ2hlcmtpblwiLFxuICBzdGFydFN0YXRlOiBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHtcbiAgICAgIGxpbmVOdW1iZXI6IDAsXG4gICAgICB0YWJsZUhlYWRlckxpbmU6IGZhbHNlLFxuICAgICAgYWxsb3dGZWF0dXJlOiB0cnVlLFxuICAgICAgYWxsb3dCYWNrZ3JvdW5kOiBmYWxzZSxcbiAgICAgIGFsbG93U2NlbmFyaW86IGZhbHNlLFxuICAgICAgYWxsb3dTdGVwczogZmFsc2UsXG4gICAgICBhbGxvd1BsYWNlaG9sZGVyczogZmFsc2UsXG4gICAgICBhbGxvd011bHRpbGluZUFyZ3VtZW50OiBmYWxzZSxcbiAgICAgIGluTXVsdGlsaW5lU3RyaW5nOiBmYWxzZSxcbiAgICAgIGluTXVsdGlsaW5lVGFibGU6IGZhbHNlLFxuICAgICAgaW5LZXl3b3JkTGluZTogZmFsc2VcbiAgICB9O1xuICB9LFxuICB0b2tlbjogZnVuY3Rpb24gKHN0cmVhbSwgc3RhdGUpIHtcbiAgICBpZiAoc3RyZWFtLnNvbCgpKSB7XG4gICAgICBzdGF0ZS5saW5lTnVtYmVyKys7XG4gICAgICBzdGF0ZS5pbktleXdvcmRMaW5lID0gZmFsc2U7XG4gICAgICBpZiAoc3RhdGUuaW5NdWx0aWxpbmVUYWJsZSkge1xuICAgICAgICBzdGF0ZS50YWJsZUhlYWRlckxpbmUgPSBmYWxzZTtcbiAgICAgICAgaWYgKCFzdHJlYW0ubWF0Y2goL1xccypcXHwvLCBmYWxzZSkpIHtcbiAgICAgICAgICBzdGF0ZS5hbGxvd011bHRpbGluZUFyZ3VtZW50ID0gZmFsc2U7XG4gICAgICAgICAgc3RhdGUuaW5NdWx0aWxpbmVUYWJsZSA9IGZhbHNlO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgfVxuICAgIHN0cmVhbS5lYXRTcGFjZSgpO1xuICAgIGlmIChzdGF0ZS5hbGxvd011bHRpbGluZUFyZ3VtZW50KSB7XG4gICAgICAvLyBTVFJJTkdcbiAgICAgIGlmIChzdGF0ZS5pbk11bHRpbGluZVN0cmluZykge1xuICAgICAgICBpZiAoc3RyZWFtLm1hdGNoKCdcIlwiXCInKSkge1xuICAgICAgICAgIHN0YXRlLmluTXVsdGlsaW5lU3RyaW5nID0gZmFsc2U7XG4gICAgICAgICAgc3RhdGUuYWxsb3dNdWx0aWxpbmVBcmd1bWVudCA9IGZhbHNlO1xuICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgIHN0cmVhbS5tYXRjaCgvLiovKTtcbiAgICAgICAgfVxuICAgICAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgICAgIH1cblxuICAgICAgLy8gVEFCTEVcbiAgICAgIGlmIChzdGF0ZS5pbk11bHRpbGluZVRhYmxlKSB7XG4gICAgICAgIGlmIChzdHJlYW0ubWF0Y2goL1xcfFxccyovKSkge1xuICAgICAgICAgIHJldHVybiBcImJyYWNrZXRcIjtcbiAgICAgICAgfSBlbHNlIHtcbiAgICAgICAgICBzdHJlYW0ubWF0Y2goL1teXFx8XSovKTtcbiAgICAgICAgICByZXR1cm4gc3RhdGUudGFibGVIZWFkZXJMaW5lID8gXCJoZWFkZXJcIiA6IFwic3RyaW5nXCI7XG4gICAgICAgIH1cbiAgICAgIH1cblxuICAgICAgLy8gREVURUNUIFNUQVJUXG4gICAgICBpZiAoc3RyZWFtLm1hdGNoKCdcIlwiXCInKSkge1xuICAgICAgICAvLyBTdHJpbmdcbiAgICAgICAgc3RhdGUuaW5NdWx0aWxpbmVTdHJpbmcgPSB0cnVlO1xuICAgICAgICByZXR1cm4gXCJzdHJpbmdcIjtcbiAgICAgIH0gZWxzZSBpZiAoc3RyZWFtLm1hdGNoKFwifFwiKSkge1xuICAgICAgICAvLyBUYWJsZVxuICAgICAgICBzdGF0ZS5pbk11bHRpbGluZVRhYmxlID0gdHJ1ZTtcbiAgICAgICAgc3RhdGUudGFibGVIZWFkZXJMaW5lID0gdHJ1ZTtcbiAgICAgICAgcmV0dXJuIFwiYnJhY2tldFwiO1xuICAgICAgfVxuICAgIH1cblxuICAgIC8vIExJTkUgQ09NTUVOVFxuICAgIGlmIChzdHJlYW0ubWF0Y2goLyMuKi8pKSB7XG4gICAgICByZXR1cm4gXCJjb21tZW50XCI7XG5cbiAgICAgIC8vIFRBR1xuICAgIH0gZWxzZSBpZiAoIXN0YXRlLmluS2V5d29yZExpbmUgJiYgc3RyZWFtLm1hdGNoKC9AXFxTKy8pKSB7XG4gICAgICByZXR1cm4gXCJ0YWdcIjtcblxuICAgICAgLy8gRkVBVFVSRVxuICAgIH0gZWxzZSBpZiAoIXN0YXRlLmluS2V5d29yZExpbmUgJiYgc3RhdGUuYWxsb3dGZWF0dXJlICYmIHN0cmVhbS5tYXRjaCgvKOapn+iDvXzlip/og71844OV44Kj44O844OB44OjfOq4sOuKpXzguYLguITguKPguIfguKvguKXguLHguIF84LiE4Lin4Liy4Lih4Liq4Liy4Lih4Liy4Lij4LiWfOC4hOC4p+C4suC4oeC4leC5ieC4reC4h+C4geC4suC4o+C4l+C4suC4h+C4mOC4uOC4o+C4geC4tOC4iHzgsrngs4bgsprgs43gsprgsrN84LCX4LGB4LCj4LCu4LGBfOCoruCpgeCoueCovuCoguCopuCosOCovnzgqKjgqJXgqLYg4Kio4KmB4Ki54Ki+4KiwfOColuCovuCouOCpgOCoheCopHzgpLDgpYLgpKog4KSy4KWH4KSWfNmI2ZDbjNqY2q/bjHzYrtin2LXZitipfNeq15vXldeg15R80KTRg9C90LrRhtGW0L7QvdCw0Lt80KTRg9C90LrRhtC40Y980KTRg9C90LrRhtC40L7QvdCw0LvQvdC+0YHRgnzQpNGD0L3QutGG0LjQvtC90LDQu3zSrtC30LXQvdGH05nQu9C10LrQu9C10LvQtdC6fNCh0LLQvtC50YHRgtCy0L580J7RgdC+0LHQuNC90LB80JzTqdC80LrQuNC90LvQtdC6fNCc0L7Qs9GD0ZvQvdC+0YHRgnzOm861zrnPhM6/z4XPgc6zzq/OsXzOlM+Fzr3Osc+Ez4zPhM63z4TOsXxXxYJhxZtjaXdvxZvEh3xWbGFzdG5vc8WlfFRyYWp0b3xUw61uaCBuxINuZ3xTYXZ5YsSXfFByZXR0eSBtdWNofFBvxb5pYWRhdmthfFBvxb5hZGF2ZWt8UG90cnplYmEgYml6bmVzb3dhfMOWemVsbGlrfE9zb2JpbmF8T21pbmFpc3V1c3xPbWFkdXN8T0ggSEFJfE1vZ3XEh25vc3R8TW9ndWNub3N0fEplbGxlbXrFkXxId8OmdHxId2FldHxGdW56aW9uYWxpdMOgfEZ1bmt0aW9uYWxpdMOpaXR8RnVua3Rpb25hbGl0w6R0fEZ1bmtjamF8RnVua2Npb25hbG5vc3R8RnVua2Npb25hbGl0xIF0ZXxGdW5rY2lhfEZ1bmdzaXxGdW5jdGlvbmFsaXRlaXR8RnVuY8ibaW9uYWxpdGF0ZXxGdW5jxaNpb25hbGl0YXRlfEZ1bmN0aW9uYWxpdGF0ZXxGdW5jaW9uYWxpdGF0fEZ1bmNpb25hbGlkYWRlfEZvbmN0aW9ubmFsaXTDqXxGaXR1cnxGxKvEjWF8RmVhdHVyZXxFaWdpbmxlaWtpfEVnZW5za2FwfEVnZW5za2FifENhcmFjdGVyw61zdGljYXxDYXJhY3RlcmlzdGljYXxCdXNpbmVzcyBOZWVkfEFzcGVrdHxBcndlZGR8QWhveSBtYXRleSF8QWJpbGl0eSk6LykpIHtcbiAgICAgIHN0YXRlLmFsbG93U2NlbmFyaW8gPSB0cnVlO1xuICAgICAgc3RhdGUuYWxsb3dCYWNrZ3JvdW5kID0gdHJ1ZTtcbiAgICAgIHN0YXRlLmFsbG93UGxhY2Vob2xkZXJzID0gZmFsc2U7XG4gICAgICBzdGF0ZS5hbGxvd1N0ZXBzID0gZmFsc2U7XG4gICAgICBzdGF0ZS5hbGxvd011bHRpbGluZUFyZ3VtZW50ID0gZmFsc2U7XG4gICAgICBzdGF0ZS5pbktleXdvcmRMaW5lID0gdHJ1ZTtcbiAgICAgIHJldHVybiBcImtleXdvcmRcIjtcblxuICAgICAgLy8gQkFDS0dST1VORFxuICAgIH0gZWxzZSBpZiAoIXN0YXRlLmluS2V5d29yZExpbmUgJiYgc3RhdGUuYWxsb3dCYWNrZ3JvdW5kICYmIHN0cmVhbS5tYXRjaCgvKOiDjOaZr3zrsLDqsr184LmB4LiZ4Lin4LiE4Li04LiUfOCyueCyv+CyqOCzjeCyqOCzhuCysuCzhnzgsKjgsYfgsKrgsKXgsY3gsK/gsIJ84Kiq4Ki/4Kib4KmL4KiV4KmcfOCkquClg+Ckt+CljeCkoOCkreClguCkruCkv3zYstmF24zZhtmHfNin2YTYrtmE2YHZitipfNeo16fXonzQotCw0YDQuNGFfNCf0YDQtdC00YvRgdGC0L7RgNC40Y980J/RgNC10LTQuNGB0YLQvtGA0LjRj3zQn9C+0LfQsNC00LjQvdCwfNCf0LXRgNC10LTRg9C80L7QstCwfNCe0YHQvdC+0LLQsHzQmtC+0L3RgtC10LrRgdGCfNCa0LXRgNC10Yh8zqXPgM+MzrLOsc64z4HOv3xaYcWCb8W8ZW5pYXxZb1xcLWhvXFwtaG98VGF1c3RhfFRhdXN0fFNpdHXEgWNpamF8UmVyZWZvbnN8UG96YWRpbmF8UG96YWRpZXxQb3phZMOtfE9zbm92YXxMYXRhciBCZWxha2FuZ3xLb250ZXh0fEtvbnRla3N0c3xLb250ZWtzdGFzfEtvbnRla3N0fEjDoXR0w6lyfEhhbm5lcmdyb25kfEdydW5kbGFnZXxHZcOnbWnFn3xGdW5kb3xGb25vfEZpcnN0IG9mZnxEaXMgaXMgd2hhdCB3ZW50IGRvd258RGFzYXJ8Q29udGV4dG98Q29udGV4dGV8Q29udGV4dHxDb250ZXN0b3xDZW7DoXJpbyBkZSBGdW5kb3xDZW5hcmlvIGRlIEZ1bmRvfENlZm5kaXJ8QuG7kWkgY+G6o25ofEJha2dydW5udXJ8QmFrZ3J1bm58QmFrZ3J1bmR8QmFnZ3J1bmR8QmFja2dyb3VuZHxCNHxBbnRlY2VkZW50c3xBbnRlY2VkZW50ZXN8w4ZyfEFlcnxBY2h0ZXJncm9uZCk6LykpIHtcbiAgICAgIHN0YXRlLmFsbG93UGxhY2Vob2xkZXJzID0gZmFsc2U7XG4gICAgICBzdGF0ZS5hbGxvd1N0ZXBzID0gdHJ1ZTtcbiAgICAgIHN0YXRlLmFsbG93QmFja2dyb3VuZCA9IGZhbHNlO1xuICAgICAgc3RhdGUuYWxsb3dNdWx0aWxpbmVBcmd1bWVudCA9IGZhbHNlO1xuICAgICAgc3RhdGUuaW5LZXl3b3JkTGluZSA9IHRydWU7XG4gICAgICByZXR1cm4gXCJrZXl3b3JkXCI7XG5cbiAgICAgIC8vIFNDRU5BUklPIE9VVExJTkVcbiAgICB9IGVsc2UgaWYgKCFzdGF0ZS5pbktleXdvcmRMaW5lICYmIHN0YXRlLmFsbG93U2NlbmFyaW8gJiYgc3RyZWFtLm1hdGNoKC8o5aC05pmv5aSn57axfOWcuuaZr+Wkp+e6snzliofmnKzlpKfntrF85Ymn5pys5aSn57qyfOODhuODs+ODl+ODrHzjgrfjg4rjg6rjgqrjg4bjg7Pjg5fjg6zjg7zjg4h844K344OK44Oq44Kq44OG44Oz44OX44OsfOOCt+ODiuODquOCquOCouOCpuODiOODqeOCpOODs3zsi5zrgpjrpqzsmKQg6rCc7JqUfOC4quC4o+C4uOC4m+C5gOC4q+C4leC4uOC4geC4suC4o+C4k+C5jHzguYLguITguKPguIfguKrguKPguYnguLLguIfguILguK3guIfguYDguKvguJXguLjguIHguLLguKPguJPguYx84LK14LK/4LK14LKw4LKj4LOGfOCwleCwpeCwqOCwgnzgqKrgqJ/gqJXgqKXgqL4g4Kiw4KmC4KiqIOCosOCph+ColuCovnzgqKrgqJ/gqJXgqKXgqL4g4Kii4Ki+4KiC4Kia4Ki+fOCkquCksOCkv+CkpuClg+CktuCljeCkryDgpLDgpYLgpKrgpLDgpYfgpJbgpL582LPZitmG2KfYsdmK2Ygg2YXYrti32Ld82KfZhNqv2YjbjCDYs9mG2KfYsduM2Yh816rXkdeg15nXqiDXqteo15fXmdepfNCh0YbQtdC90LDRgNC40LnQvdGL0qMg0YLTqdC30LXQu9C10YjQtXzQodGG0LXQvdCw0YDQuNC5INGB0YLRgNGD0LrRgtGD0YDQsNGB0Lh80KHRgtGA0YPQutGC0YPRgNCwINGB0YbQtdC90LDRgNGW0Y580KHRgtGA0YPQutGC0YPRgNCwINGB0YbQtdC90LDRgNC40Y980KHRgtGA0YPQutGC0YPRgNCwINGB0YbQtdC90LDRgNC40ZjQsHzQodC60LjRhtCwfNCg0LDQvNC60LAg0L3QsCDRgdGG0LXQvdCw0YDQuNC5fNCa0L7QvdGG0LXQv9GCfM6gzrXPgc65zrPPgc6xz4bOriDOo861zr3Osc+Bzq/Ov8+FfFdoYXJyaW1lYW4gaXN8VGVtcGxhdGUgU2l0dWFpfFRlbXBsYXRlIFNlbmFyaW98VGVtcGxhdGUgS2VhZGFhbnxUYXBhdXNhaWhpb3xTemVuYXJpb2dydW5kcmlzc3xTemFibG9uIHNjZW5hcml1c3phfFN3YSBod8OmciBzd2F8U3dhIGh3YWVyIHN3YXxTdHJ1a3R1cmEgc2NlbmFyaWphfFN0cnVjdHVyxIMgc2NlbmFyaXV8U3RydWN0dXJhIHNjZW5hcml1fFNraWNhfFNrZW5hcmlvIGtvbnNlcHxTaGl2ZXIgbWUgdGltYmVyc3xTZW5hcnlvIHRhc2xhxJ/EsXxTY2hlbWEgZGVsbG8gc2NlbmFyaW98U2NlbmFyaW9tYWxsfFNjZW5hcmlvbWFsfFNjZW5hcmlvIFRlbXBsYXRlfFNjZW5hcmlvIE91dGxpbmV8U2NlbmFyaW8gQW1saW5lbGxvbHxTY2VuxIFyaWpzIHDEk2MgcGFyYXVnYXxTY2VuYXJpamF1cyDFoWFibG9uYXN8UmVja29uIGl0J3MgbGlrZXxSYWFtc3RzZW5hYXJpdW18UGxhbmcgdnVtIFN6ZW5hcmlvfFBsYW4gZHUgU2PDqW5hcmlvfFBsYW4gZHUgc2PDqW5hcmlvfE9zbm92YSBzY8OpbsOhxZllfE9zbm92YSBTY2Vuw6FyYXxOw6HEjXJ0IFNjZW7DoXJ1fE7DocSNcnQgU2PDqW7DocWZZXxOw6HEjXJ0IFNjZW7DoXJhfE1JU0hVTiBTUlNMWXxNZW5nZ2FyaXNrYW4gU2VuYXJpb3xMw71zaW5nIETDpm1hfEzDvXNpbmcgQXRidXLDsGFyw6FzYXJ8S29udHVybyBkZSBsYSBzY2VuYXJvfEtvbmNlcHR8S2h1bmcgdMOsbmggaHXhu5FuZ3xLaHVuZyBr4buLY2ggYuG6o258Rm9yZ2F0w7Nrw7ZueXYgdsOhemxhdHxFc3F1ZW1hIGRvIENlbsOhcmlvfEVzcXVlbWEgZG8gQ2VuYXJpb3xFc3F1ZW1hIGRlbCBlc2NlbmFyaW98RXNxdWVtYSBkZSBsJ2VzY2VuYXJpfEVzYm96byBkbyBlc2NlbmFyaW98RGVsaW5lYcOnw6NvIGRvIENlbsOhcmlvfERlbGluZWFjYW8gZG8gQ2VuYXJpb3xBbGwgeSdhbGx8QWJzdHJha3QgU2NlbmFyaW98QWJzdHJhY3QgU2NlbmFyaW8pOi8pKSB7XG4gICAgICBzdGF0ZS5hbGxvd1BsYWNlaG9sZGVycyA9IHRydWU7XG4gICAgICBzdGF0ZS5hbGxvd1N0ZXBzID0gdHJ1ZTtcbiAgICAgIHN0YXRlLmFsbG93TXVsdGlsaW5lQXJndW1lbnQgPSBmYWxzZTtcbiAgICAgIHN0YXRlLmluS2V5d29yZExpbmUgPSB0cnVlO1xuICAgICAgcmV0dXJuIFwia2V5d29yZFwiO1xuXG4gICAgICAvLyBFWEFNUExFU1xuICAgIH0gZWxzZSBpZiAoc3RhdGUuYWxsb3dTY2VuYXJpbyAmJiBzdHJlYW0ubWF0Y2goLyjkvovlrZB85L6LfOOCteODs+ODl+ODq3zsmIh84LiK4Li44LiU4LiC4Lit4LiH4LmA4Lir4LiV4Li44LiB4Liy4Lij4LiT4LmMfOC4iuC4uOC4lOC4guC4reC4h+C4leC4seC4p+C4reC4ouC5iOC4suC4h3zgsongsqbgsr7gsrngsrDgsqPgs4bgspfgsrPgs4F84LCJ4LCm4LC+4LC54LCw4LCj4LCy4LGBfOCoieCopuCovuCoueCosOCoqOCovuCognzgpIngpKbgpL7gpLngpLDgpKN82YbZhdmI2YbZhyDZh9infNin2YXYq9mE2Kl815PXldeS157XkNeV16p80q7RgNC905nQutC705nRgHzQodGG0LXQvdCw0YDQuNGY0Lh80J/RgNC40LzQtdGA0Yt80J/RgNC40LzQtdGA0Lh80J/RgNC40LrQu9Cw0LTQuHzQnNC40YHQvtC70LvQsNGAfNCc0LjRgdCw0LvQu9Cw0YB8zqPOtc69zqzPgc65zrF8zqDOsc+BzrHOtM61zq/Os868zrHPhM6xfFlvdSdsbCB3YW5uYXxWb29yYmVlbGRlbnxWYXJpYW50YWl8VGFwYXVrc2V0fFNlIMO+ZXxTZSB0aGV8U2Ugw7BlfFNjZW5hcmlvc3xTY2VuYXJpaml8U2NlbmFyaWphaXxQcnp5a8WCYWR5fFByaW1qZXJpfFByaW1lcml8UMWZw61rbGFkeXxQcsOta2xhZHl8UGllbcSTcml8UMOpbGTDoWt8UGF2eXpkxb5pYWl8UGFyYXVnc3zDlnJuZWtsZXJ8SnVodHVtaWR8RXhlbXBsb3N8RXhlbXBsZXN8RXhlbXBsZXxFeGVtcGVsfEVYQU1QTFp8RXhhbXBsZXN8RXNlbXBpfEVuZ2hyZWlmZnRpYXV8RWt6ZW1wbG9qfEVrc2VtcGxlcnxFamVtcGxvc3xE4buvIGxp4buHdXxEZWFkIG1lbiB0ZWxsIG5vIHRhbGVzfETDpm1pfENvbnRvaHxDZW7DoXJpb3N8Q2VuYXJpb3N8QmVpc3BpbGxlcnxCZWlzcGllbGV8QXRidXLDsGFyw6FzaXIpOi8pKSB7XG4gICAgICBzdGF0ZS5hbGxvd1BsYWNlaG9sZGVycyA9IGZhbHNlO1xuICAgICAgc3RhdGUuYWxsb3dTdGVwcyA9IHRydWU7XG4gICAgICBzdGF0ZS5hbGxvd0JhY2tncm91bmQgPSBmYWxzZTtcbiAgICAgIHN0YXRlLmFsbG93TXVsdGlsaW5lQXJndW1lbnQgPSB0cnVlO1xuICAgICAgcmV0dXJuIFwia2V5d29yZFwiO1xuXG4gICAgICAvLyBTQ0VOQVJJT1xuICAgIH0gZWxzZSBpZiAoIXN0YXRlLmluS2V5d29yZExpbmUgJiYgc3RhdGUuYWxsb3dTY2VuYXJpbyAmJiBzdHJlYW0ubWF0Y2goLyjloLTmma985Zy65pmvfOWKh+acrHzliafmnKx844K344OK44Oq44KqfOyLnOuCmOumrOyYpHzguYDguKvguJXguLjguIHguLLguKPguJPguYx84LKV4LKl4LK+4LK44LK+4LKw4LK+4LKC4LK2fOCwuOCwqOCxjeCwqOCwv+CwteCxh+CwtuCwgnzgqKrgqJ/gqJXgqKXgqL584KSq4KSw4KS/4KSm4KWD4KS24KWN4KSvfNiz2YrZhtin2LHZitmIfNiz2YbYp9ix24zZiHzXqteo15fXmdepfNCh0YbQtdC90LDRgNGW0Ll80KHRhtC10L3QsNGA0LjQvnzQodGG0LXQvdCw0YDQuNC5fNCf0YDQuNC80LXRgHzOo861zr3OrM+BzrnOv3xUw6xuaCBodeG7kW5nfFRoZSB0aGluZyBvZiBpdCBpc3xUYXBhdXN8U3plbmFyaW98U3dhfFN0c2VuYWFyaXVtfFNrZW5hcmlvfFNpdHVhaXxTZW5hcnlvfFNlbmFyaW98U2NlbmFyb3xTY2VuYXJpdXN6fFNjZW5hcml1fFNjw6luYXJpb3xTY2VuYXJpb3xTY2VuYXJpanVzfFNjZW7EgXJpanN8U2NlbmFyaWp8U2NlbmFyaWV8U2PDqW7DocWZfFNjZW7DoXJ8UHJpbWVyfE1JU0hVTnxL4buLY2ggYuG6o258S2VhZGFhbnxIZWF2ZSB0b3xGb3JnYXTDs2vDtm55dnxFc2NlbmFyaW98RXNjZW5hcml8Q2Vuw6FyaW98Q2VuYXJpb3xBd3d3LCBsb29rIG1hdGV8QXRidXLDsGFyw6FzKTovKSkge1xuICAgICAgc3RhdGUuYWxsb3dQbGFjZWhvbGRlcnMgPSBmYWxzZTtcbiAgICAgIHN0YXRlLmFsbG93U3RlcHMgPSB0cnVlO1xuICAgICAgc3RhdGUuYWxsb3dCYWNrZ3JvdW5kID0gZmFsc2U7XG4gICAgICBzdGF0ZS5hbGxvd011bHRpbGluZUFyZ3VtZW50ID0gZmFsc2U7XG4gICAgICBzdGF0ZS5pbktleXdvcmRMaW5lID0gdHJ1ZTtcbiAgICAgIHJldHVybiBcImtleXdvcmRcIjtcblxuICAgICAgLy8gU1RFUFNcbiAgICB9IGVsc2UgaWYgKCFzdGF0ZS5pbktleXdvcmRMaW5lICYmIHN0YXRlLmFsbG93U3RlcHMgJiYgc3RyZWFtLm1hdGNoKC8o6YKj6bq8fOmCo+S5iHzogIzkuJR855W2fOW9k3zlubbkuJR85ZCM5pmCfOWQjOaXtnzliY3mj5B85YGH6K6+fOWBh+iorXzlgYflrpp85YGH5aaCfOS9huaYr3zkvYbjgZd85Lim5LiUfOOCguOBl3zjgarjgonjgbB844Gf44Gg44GXfOOBl+OBi+OBl3zjgYvjgaR87ZWY7KeA66eMfOyhsOqxtHzrqLzsoIB866eM7J28fOunjOyVvXzri6h86re466as6rOgfOq3uOufrOuptHzguYHguKXguLAgfOC5gOC4oeC4t+C5iOC4rSB84LmB4LiV4LmIIHzguJTguLHguIfguJnguLHguYnguJkgfOC4geC4s+C4q+C4meC4lOC5g+C4q+C5iSB84LK44LON4LKl4LK/4LKk4LK/4LKv4LKo4LON4LKo4LOBIHzgsq7gsqTgs43gsqTgs4EgfOCyqOCyv+CzleCyoeCyv+CypiB84LKo4LKC4LKk4LKwIHzgsobgsqbgsrDgs4YgfOCwruCwsOCwv+Cwr+CxgSB84LCa4LGG4LCq4LGN4LCq4LCs4LCh4LC/4LCo4LCm4LC/IHzgsJXgsL7gsKjgsL8gfOCwiCDgsKrgsLDgsL/gsLjgsY3gsKXgsL/gsKTgsL/gsLLgsYsgfOCwheCwquCxjeCwquCxgeCwoeCxgSB84Kiq4KiwIHzgqKTgqKYgfOConOCph+ColeCosCB84Kic4Ki/4Ki14KmH4KiCIOColeCovyB84Kic4Kim4KmL4KiCIHzgqIXgqKTgqYcgfOCkr+CkpuCkvyB84KSq4KSw4KSo4KWN4KSk4KWBIHzgpKrgpLAgfOCkpOCkrCB84KSk4KSm4KS+IHzgpKTgpKXgpL4gfOCknOCkrCB84KSa4KWC4KSC4KSV4KS/IHzgpJXgpL/gpKjgpY3gpKTgpYEgfOCkleCkpuCkviB84KSU4KSwIHzgpIXgpJfgpLAgfNmIIHzZh9mG2q/Yp9mF24wgfNmF2KrZiSB82YTZg9mGIHzYudmG2K/ZhdinIHzYq9mFIHzYqNmB2LHYtiB82KjYpyDZgdix2LYgfNin2YXYpyB82KfYsNin2YsgfNii2Ybar9in2YcgfNeb15DXqdeoIHzXldeS150gfNeR15TXmdeg16rXnyB815DXlteZIHzXkNeWIHzXkNeR15wgfNCv0LrRidC+IHzSutOZ0LwgfNCj0L3QtNCwIHzQotC+0LTRliB80KLQvtCz0LTQsCB80KLQviB80KLQsNC60LbQtSB80KLQsCB80J/Rg9GB0YLRjCB80J/RgNC40L/Rg9GB0YLQuNC80L4sINGJ0L4gfNCf0YDQuNC/0YPRgdGC0LjQvNC+IHzQntC90LTQsCB80J3QviB80J3QtdGF0LDQuSB80J3TmdGC0LjSl9OZ0LTTmSB80JvQtdC60LjQvSB80JvTmdC60LjQvSB80JrQvtC70LggfNCa0L7Qs9C00LAgfNCa0L7Qs9Cw0YLQviB80JrQsNC00LAgfNCa0LDQtCB80Jog0YLQvtC80YMg0LbQtSB80IYgfNCYIHzQl9Cw0LTQsNGC0L4gfNCX0LDQtNCw0YLQuCB80JfQsNC00LDRgtC1IHzQldGB0LvQuCB80JTQvtC/0YPRgdGC0LjQvCB80JTQsNC90L4gfNCU0LDQtNC10L3QviB80JLTmSB80JLQsCB80JHQuNGA0L7QuiB805jQvNC80LAgfNOY0LnRgtC40LogfNOY0LPTmdGAIHzQkNC80LzQviB80JDQu9C4IHzQkNC70LUgfNCQ0LPQsNGAIHzQkCDRgtCw0LrQvtC2IHzQkCB8zqTPjM+EzrUgfM6Mz4TOsc69IHzOms6xzrkgfM6UzrXOtM6/zrzOrc69zr/PhSB8zpHOu867zqwgfMOedXJoIHzDnmVnYXIgfMOeYSDDvmUgfMOew6EgfMOeYSB8WmF0YXRpIHxaYWvFgmFkYWrEhWMgfFphZGF0byB8WmFkYXRlIHxaYWRhbm8gfFphZGFuaSB8WmFkYW4gfFphIHDFmWVkcG9rbGFkdSB8WmEgcHJlZHBva2xhZHUgfFlvdXNlIGtub3cgd2hlbiB5b3VzZSBnb3QgfFlvdXNlIGtub3cgbGlrZSB3aGVuIHxZbmEgfFllYWggbmFoIHxZJ2tub3cgfFkgfFd1biB8V3RlZHkgfFdoZW4geSdhbGwgfFdoZW4gfFdlbm4gfFdFTiB8d2FubiB8VmUgfFbDoCB8VW5kIHxVbiB8dWdlaG9sbCB8VG9vIHJpZ2h0IHxUaHVyaCB8VGjDrCB8VGhlbiB5J2FsbCB8VGhlbiB8VGhhIHRoZSB8VGhhIHxUZXRhcGkgfFRhcGkgfFRhayB8VGFkYSB8VGFkIHxTdGVsIHxTb2l0IHxTaWlzIHzImGkgfMWeaSB8U2kgfFNlZCB8U2UgfFPDpSB8UXVhbmRvIHxRdWFuZCB8UXVhbiB8UHJ5ZCB8UG90b20gfFBva3VkIHxQb2tpYcS+IHxQZXLDsiB8UGVybyB8UGFrIHxPcmF6IHxPbmRhIHxPbmQgfE9sZXRldGFhbiB8T2cgfE9jaCB8TyB6YW1hbiB8TmlpbiB8TmjGsG5nIHxOw6RyIHxOw6VyIHxNdXR0YSB8TWVuIHxNYXMgfE1ha2EgfE1hamQgfE1hasSFYyB8TWFpcyB8TWFhciB8bcOkIHxNYSB8TG9yc3F1ZSB8TG9yc3F1J3xMb2dvIHxMZXQgZ28gYW5kIGhhdWwgfEt1biB8S3VpZCB8S3VpIHxLaWVkeSB8S2hpIHxLZXRpa2EgfEtlbXVkaWFuIHxLZcSPIHxLZHnFviB8S2FqIHxLYWkgfEthZGEgfEthZCB8SmXFvGVsaSB8SmXFm2xpIHxKYSB8SXQncyBqdXN0IHVuYmVsaWV2YWJsZSB8SXIgfEkgQ0FOIEhBWiB8SSB8SGEgfEdpdnVuIHxHaXZldCB8R2l2ZW4geSdhbGwgfEdpdmVuIHxHaXR0IHxHZWdldmVuIHxHZWdlYmVuIHNlaWVuIHxHZWdlYmVuIHNlaSB8R2R5IHxHYW5nd2F5ISB8RmFrYXQgfMOJdGFudCBkb25uw6lzIHxFdGFudCBkb25uw6lzIHzDiXRhbnQgZG9ubsOpZXMgfEV0YW50IGRvbm7DqWVzIHzDiXRhbnQgZG9ubsOpZSB8RXRhbnQgZG9ubsOpZSB8w4l0YW50IGRvbm7DqSB8RXRhbnQgZG9ubsOpIHxFdCB8w4lzIHxFbnRvbmNlcyB8RW50w7NuIHxFbnTDo28gfEVudGFvIHxFbiB8RcSfZXIga2kgfEVmIHxFZWxkYWRlcyB8RSB8w5B1cmggfER1b3RhIHxEdW4gfERvbml0YcS1byB8RG9uYXQgfERvbmFkYSB8RG8gfERpeWVsaW0ga2kgfERpYmVyaSB8RGVuZ2FuIHxEZW4geW91c2UgZ290dGEgfERFTiB8RGUgfERhdG8gfERhyJtpIGZpaW5kIHxEYcWjaSBmaWluZCB8RGF0aSBmaWluZCB8RGF0aSB8RGF0ZSBmaWluZCB8RGF0ZSB8RGF0YSB8RGF0IGZpaW5kIHxEYXIgfERhbm4gfGRhbm4gfERhbiB8RGFkb3MgfERhZG8gfERhZGFzIHxEYWRhIHzDkGEgw7BlIHzDkGEgfEN1YW5kbyB8Q2hvIHxDYW5kbyB8Q8OibmQgfENhbmQgfENhbCB8QnV0IHknYWxsIHxCdXQgYXQgdGhlIGVuZCBvZiB0aGUgZGF5IEkgcmVja29uIHxCVVQgfEJ1dCB8QnVoIHxCbGltZXkhIHxCaeG6v3QgfEJldCB8QmFnaSB8QXllIHxhd2VyIHxBdmFzdCEgfEF0dW5jaSB8QXRlc2EgfEF0w6hzIHxBcGFiaWxhIHxBbnJoZWdlZGlnIGEgfEFuZ2Vub21tZW4gfEFuZCB5J2FsbCB8QW5kIHxBTiB8QW4gfGFuIHxBbWlrb3IgfEFtZW5ueWliZW4gfEFtYSB8QWxzIHxBbG9ycyB8QWxsb3JhIHxBbGkgfEFsZXNob3JlcyB8QWxlIHxBa2tvciB8QWsgfEFkb3R0IHxBYyB8QWJlciB8QSB6w6Fyb3ZlxYggfEEgdGllxb4gfEEgdGFrdGllxb4gfEEgdGFrw6kgfEEgfGEgfDcgfFxcKiApLykpIHtcbiAgICAgIHN0YXRlLmluU3RlcCA9IHRydWU7XG4gICAgICBzdGF0ZS5hbGxvd1BsYWNlaG9sZGVycyA9IHRydWU7XG4gICAgICBzdGF0ZS5hbGxvd011bHRpbGluZUFyZ3VtZW50ID0gdHJ1ZTtcbiAgICAgIHN0YXRlLmluS2V5d29yZExpbmUgPSB0cnVlO1xuICAgICAgcmV0dXJuIFwia2V5d29yZFwiO1xuXG4gICAgICAvLyBJTkxJTkUgU1RSSU5HXG4gICAgfSBlbHNlIGlmIChzdHJlYW0ubWF0Y2goL1wiW15cIl0qXCI/LykpIHtcbiAgICAgIHJldHVybiBcInN0cmluZ1wiO1xuXG4gICAgICAvLyBQTEFDRUhPTERFUlxuICAgIH0gZWxzZSBpZiAoc3RhdGUuYWxsb3dQbGFjZWhvbGRlcnMgJiYgc3RyZWFtLm1hdGNoKC88W14+XSo+Py8pKSB7XG4gICAgICByZXR1cm4gXCJ2YXJpYWJsZVwiO1xuXG4gICAgICAvLyBGYWxsIHRocm91Z2hcbiAgICB9IGVsc2Uge1xuICAgICAgc3RyZWFtLm5leHQoKTtcbiAgICAgIHN0cmVhbS5lYXRXaGlsZSgvW15AXCI8I10vKTtcbiAgICAgIHJldHVybiBudWxsO1xuICAgIH1cbiAgfVxufTsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9