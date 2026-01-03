"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[9362],{

/***/ 1371
(__unused_webpack_module, exports, __webpack_require__) {



var __extends = this && this.__extends || function () {
  var extendStatics = function (d, b) {
    extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.AbstractMathList = void 0;
var LinkedList_js_1 = __webpack_require__(78541);
var AbstractMathList = function (_super) {
  __extends(AbstractMathList, _super);
  function AbstractMathList() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  AbstractMathList.prototype.isBefore = function (a, b) {
    return a.start.i < b.start.i || a.start.i === b.start.i && a.start.n < b.start.n;
  };
  return AbstractMathList;
}(LinkedList_js_1.LinkedList);
exports.AbstractMathList = AbstractMathList;

/***/ },

/***/ 15282
(__unused_webpack_module, exports, __webpack_require__) {



Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.AbstractInputJax = void 0;
var Options_js_1 = __webpack_require__(53588);
var FunctionList_js_1 = __webpack_require__(58872);
var AbstractInputJax = function () {
  function AbstractInputJax(options) {
    if (options === void 0) {
      options = {};
    }
    this.adaptor = null;
    this.mmlFactory = null;
    var CLASS = this.constructor;
    this.options = (0, Options_js_1.userOptions)((0, Options_js_1.defaultOptions)({}, CLASS.OPTIONS), options);
    this.preFilters = new FunctionList_js_1.FunctionList();
    this.postFilters = new FunctionList_js_1.FunctionList();
  }
  Object.defineProperty(AbstractInputJax.prototype, "name", {
    get: function () {
      return this.constructor.NAME;
    },
    enumerable: false,
    configurable: true
  });
  AbstractInputJax.prototype.setAdaptor = function (adaptor) {
    this.adaptor = adaptor;
  };
  AbstractInputJax.prototype.setMmlFactory = function (mmlFactory) {
    this.mmlFactory = mmlFactory;
  };
  AbstractInputJax.prototype.initialize = function () {};
  AbstractInputJax.prototype.reset = function () {
    var _args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
      _args[_i] = arguments[_i];
    }
  };
  Object.defineProperty(AbstractInputJax.prototype, "processStrings", {
    get: function () {
      return true;
    },
    enumerable: false,
    configurable: true
  });
  AbstractInputJax.prototype.findMath = function (_node, _options) {
    return [];
  };
  AbstractInputJax.prototype.executeFilters = function (filters, math, document, data) {
    var args = {
      math: math,
      document: document,
      data: data
    };
    filters.execute(args);
    return args.data;
  };
  AbstractInputJax.NAME = 'generic';
  AbstractInputJax.OPTIONS = {};
  return AbstractInputJax;
}();
exports.AbstractInputJax = AbstractInputJax;

/***/ },

/***/ 30457
(__unused_webpack_module, exports) {



Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.PrioritizedList = void 0;
var PrioritizedList = function () {
  function PrioritizedList() {
    this.items = [];
    this.items = [];
  }
  PrioritizedList.prototype[Symbol.iterator] = function () {
    var i = 0;
    var items = this.items;
    return {
      next: function () {
        return {
          value: items[i++],
          done: i > items.length
        };
      }
    };
  };
  PrioritizedList.prototype.add = function (item, priority) {
    if (priority === void 0) {
      priority = PrioritizedList.DEFAULTPRIORITY;
    }
    var i = this.items.length;
    do {
      i--;
    } while (i >= 0 && priority < this.items[i].priority);
    this.items.splice(i + 1, 0, {
      item: item,
      priority: priority
    });
    return item;
  };
  PrioritizedList.prototype.remove = function (item) {
    var i = this.items.length;
    do {
      i--;
    } while (i >= 0 && this.items[i].item !== item);
    if (i >= 0) {
      this.items.splice(i, 1);
    }
  };
  PrioritizedList.DEFAULTPRIORITY = 5;
  return PrioritizedList;
}();
exports.PrioritizedList = PrioritizedList;

/***/ },

/***/ 32182
(__unused_webpack_module, exports, __webpack_require__) {



var __extends = this && this.__extends || function () {
  var extendStatics = function (d, b) {
    extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
var __values = this && this.__values || function (o) {
  var s = typeof Symbol === "function" && Symbol.iterator,
    m = s && o[s],
    i = 0;
  if (m) return m.call(o);
  if (o && typeof o.length === "number") return {
    next: function () {
      if (o && i >= o.length) o = void 0;
      return {
        value: o && o[i++],
        done: !o
      };
    }
  };
  throw new TypeError(s ? "Object is not iterable." : "Symbol.iterator is not defined.");
};
var __read = this && this.__read || function (o, n) {
  var m = typeof Symbol === "function" && o[Symbol.iterator];
  if (!m) return o;
  var i = m.call(o),
    r,
    ar = [],
    e;
  try {
    while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
  } catch (error) {
    e = {
      error: error
    };
  } finally {
    try {
      if (r && !r.done && (m = i["return"])) m.call(i);
    } finally {
      if (e) throw e.error;
    }
  }
  return ar;
};
var __spreadArray = this && this.__spreadArray || function (to, from, pack) {
  if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
    if (ar || !(i in from)) {
      if (!ar) ar = Array.prototype.slice.call(from, 0, i);
      ar[i] = from[i];
    }
  }
  return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.AbstractMathDocument = exports.resetAllOptions = exports.resetOptions = exports.RenderList = void 0;
var Options_js_1 = __webpack_require__(53588);
var InputJax_js_1 = __webpack_require__(15282);
var OutputJax_js_1 = __webpack_require__(80481);
var MathList_js_1 = __webpack_require__(1371);
var MathItem_js_1 = __webpack_require__(52016);
var MmlFactory_js_1 = __webpack_require__(13962);
var BitField_js_1 = __webpack_require__(74717);
var PrioritizedList_js_1 = __webpack_require__(30457);
var RenderList = function (_super) {
  __extends(RenderList, _super);
  function RenderList() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  RenderList.create = function (actions) {
    var e_1, _a;
    var list = new this();
    try {
      for (var _b = __values(Object.keys(actions)), _c = _b.next(); !_c.done; _c = _b.next()) {
        var id = _c.value;
        var _d = __read(this.action(id, actions[id]), 2),
          action = _d[0],
          priority = _d[1];
        if (priority) {
          list.add(action, priority);
        }
      }
    } catch (e_1_1) {
      e_1 = {
        error: e_1_1
      };
    } finally {
      try {
        if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
      } finally {
        if (e_1) throw e_1.error;
      }
    }
    return list;
  };
  RenderList.action = function (id, action) {
    var _a, _b, _c, _d;
    var renderDoc, renderMath;
    var convert = true;
    var priority = action[0];
    if (action.length === 1 || typeof action[1] === 'boolean') {
      action.length === 2 && (convert = action[1]);
      _a = __read(this.methodActions(id), 2), renderDoc = _a[0], renderMath = _a[1];
    } else if (typeof action[1] === 'string') {
      if (typeof action[2] === 'string') {
        action.length === 4 && (convert = action[3]);
        var _e = __read(action.slice(1), 2),
          method1 = _e[0],
          method2 = _e[1];
        _b = __read(this.methodActions(method1, method2), 2), renderDoc = _b[0], renderMath = _b[1];
      } else {
        action.length === 3 && (convert = action[2]);
        _c = __read(this.methodActions(action[1]), 2), renderDoc = _c[0], renderMath = _c[1];
      }
    } else {
      action.length === 4 && (convert = action[3]);
      _d = __read(action.slice(1), 2), renderDoc = _d[0], renderMath = _d[1];
    }
    return [{
      id: id,
      renderDoc: renderDoc,
      renderMath: renderMath,
      convert: convert
    }, priority];
  };
  RenderList.methodActions = function (method1, method2) {
    if (method2 === void 0) {
      method2 = method1;
    }
    return [function (document) {
      method1 && document[method1]();
      return false;
    }, function (math, document) {
      method2 && math[method2](document);
      return false;
    }];
  };
  RenderList.prototype.renderDoc = function (document, start) {
    var e_2, _a;
    if (start === void 0) {
      start = MathItem_js_1.STATE.UNPROCESSED;
    }
    try {
      for (var _b = __values(this.items), _c = _b.next(); !_c.done; _c = _b.next()) {
        var item = _c.value;
        if (item.priority >= start) {
          if (item.item.renderDoc(document)) return;
        }
      }
    } catch (e_2_1) {
      e_2 = {
        error: e_2_1
      };
    } finally {
      try {
        if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
      } finally {
        if (e_2) throw e_2.error;
      }
    }
  };
  RenderList.prototype.renderMath = function (math, document, start) {
    var e_3, _a;
    if (start === void 0) {
      start = MathItem_js_1.STATE.UNPROCESSED;
    }
    try {
      for (var _b = __values(this.items), _c = _b.next(); !_c.done; _c = _b.next()) {
        var item = _c.value;
        if (item.priority >= start) {
          if (item.item.renderMath(math, document)) return;
        }
      }
    } catch (e_3_1) {
      e_3 = {
        error: e_3_1
      };
    } finally {
      try {
        if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
      } finally {
        if (e_3) throw e_3.error;
      }
    }
  };
  RenderList.prototype.renderConvert = function (math, document, end) {
    var e_4, _a;
    if (end === void 0) {
      end = MathItem_js_1.STATE.LAST;
    }
    try {
      for (var _b = __values(this.items), _c = _b.next(); !_c.done; _c = _b.next()) {
        var item = _c.value;
        if (item.priority > end) return;
        if (item.item.convert) {
          if (item.item.renderMath(math, document)) return;
        }
      }
    } catch (e_4_1) {
      e_4 = {
        error: e_4_1
      };
    } finally {
      try {
        if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
      } finally {
        if (e_4) throw e_4.error;
      }
    }
  };
  RenderList.prototype.findID = function (id) {
    var e_5, _a;
    try {
      for (var _b = __values(this.items), _c = _b.next(); !_c.done; _c = _b.next()) {
        var item = _c.value;
        if (item.item.id === id) {
          return item.item;
        }
      }
    } catch (e_5_1) {
      e_5 = {
        error: e_5_1
      };
    } finally {
      try {
        if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
      } finally {
        if (e_5) throw e_5.error;
      }
    }
    return null;
  };
  return RenderList;
}(PrioritizedList_js_1.PrioritizedList);
exports.RenderList = RenderList;
exports.resetOptions = {
  all: false,
  processed: false,
  inputJax: null,
  outputJax: null
};
exports.resetAllOptions = {
  all: true,
  processed: true,
  inputJax: [],
  outputJax: []
};
var DefaultInputJax = function (_super) {
  __extends(DefaultInputJax, _super);
  function DefaultInputJax() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  DefaultInputJax.prototype.compile = function (_math) {
    return null;
  };
  return DefaultInputJax;
}(InputJax_js_1.AbstractInputJax);
var DefaultOutputJax = function (_super) {
  __extends(DefaultOutputJax, _super);
  function DefaultOutputJax() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  DefaultOutputJax.prototype.typeset = function (_math, _document) {
    if (_document === void 0) {
      _document = null;
    }
    return null;
  };
  DefaultOutputJax.prototype.escaped = function (_math, _document) {
    return null;
  };
  return DefaultOutputJax;
}(OutputJax_js_1.AbstractOutputJax);
var DefaultMathList = function (_super) {
  __extends(DefaultMathList, _super);
  function DefaultMathList() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  return DefaultMathList;
}(MathList_js_1.AbstractMathList);
var DefaultMathItem = function (_super) {
  __extends(DefaultMathItem, _super);
  function DefaultMathItem() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  return DefaultMathItem;
}(MathItem_js_1.AbstractMathItem);
var AbstractMathDocument = function () {
  function AbstractMathDocument(document, adaptor, options) {
    var _this = this;
    var CLASS = this.constructor;
    this.document = document;
    this.options = (0, Options_js_1.userOptions)((0, Options_js_1.defaultOptions)({}, CLASS.OPTIONS), options);
    this.math = new (this.options['MathList'] || DefaultMathList)();
    this.renderActions = RenderList.create(this.options['renderActions']);
    this.processed = new AbstractMathDocument.ProcessBits();
    this.outputJax = this.options['OutputJax'] || new DefaultOutputJax();
    var inputJax = this.options['InputJax'] || [new DefaultInputJax()];
    if (!Array.isArray(inputJax)) {
      inputJax = [inputJax];
    }
    this.inputJax = inputJax;
    this.adaptor = adaptor;
    this.outputJax.setAdaptor(adaptor);
    this.inputJax.map(function (jax) {
      return jax.setAdaptor(adaptor);
    });
    this.mmlFactory = this.options['MmlFactory'] || new MmlFactory_js_1.MmlFactory();
    this.inputJax.map(function (jax) {
      return jax.setMmlFactory(_this.mmlFactory);
    });
    this.outputJax.initialize();
    this.inputJax.map(function (jax) {
      return jax.initialize();
    });
  }
  Object.defineProperty(AbstractMathDocument.prototype, "kind", {
    get: function () {
      return this.constructor.KIND;
    },
    enumerable: false,
    configurable: true
  });
  AbstractMathDocument.prototype.addRenderAction = function (id) {
    var action = [];
    for (var _i = 1; _i < arguments.length; _i++) {
      action[_i - 1] = arguments[_i];
    }
    var _a = __read(RenderList.action(id, action), 2),
      fn = _a[0],
      p = _a[1];
    this.renderActions.add(fn, p);
  };
  AbstractMathDocument.prototype.removeRenderAction = function (id) {
    var action = this.renderActions.findID(id);
    if (action) {
      this.renderActions.remove(action);
    }
  };
  AbstractMathDocument.prototype.render = function () {
    this.renderActions.renderDoc(this);
    return this;
  };
  AbstractMathDocument.prototype.rerender = function (start) {
    if (start === void 0) {
      start = MathItem_js_1.STATE.RERENDER;
    }
    this.state(start - 1);
    this.render();
    return this;
  };
  AbstractMathDocument.prototype.convert = function (math, options) {
    if (options === void 0) {
      options = {};
    }
    var _a = (0, Options_js_1.userOptions)({
        format: this.inputJax[0].name,
        display: true,
        end: MathItem_js_1.STATE.LAST,
        em: 16,
        ex: 8,
        containerWidth: null,
        lineWidth: 1000000,
        scale: 1,
        family: ''
      }, options),
      format = _a.format,
      display = _a.display,
      end = _a.end,
      ex = _a.ex,
      em = _a.em,
      containerWidth = _a.containerWidth,
      lineWidth = _a.lineWidth,
      scale = _a.scale,
      family = _a.family;
    if (containerWidth === null) {
      containerWidth = 80 * ex;
    }
    var jax = this.inputJax.reduce(function (jax, ijax) {
      return ijax.name === format ? ijax : jax;
    }, null);
    var mitem = new this.options.MathItem(math, jax, display);
    mitem.start.node = this.adaptor.body(this.document);
    mitem.setMetrics(em, ex, containerWidth, lineWidth, scale);
    if (this.outputJax.options.mtextInheritFont) {
      mitem.outputData.mtextFamily = family;
    }
    if (this.outputJax.options.merrorInheritFont) {
      mitem.outputData.merrorFamily = family;
    }
    mitem.convert(this, end);
    return mitem.typesetRoot || mitem.root;
  };
  AbstractMathDocument.prototype.findMath = function (_options) {
    if (_options === void 0) {
      _options = null;
    }
    this.processed.set('findMath');
    return this;
  };
  AbstractMathDocument.prototype.compile = function () {
    var e_6, _a, e_7, _b;
    if (!this.processed.isSet('compile')) {
      var recompile = [];
      try {
        for (var _c = __values(this.math), _d = _c.next(); !_d.done; _d = _c.next()) {
          var math = _d.value;
          this.compileMath(math);
          if (math.inputData.recompile !== undefined) {
            recompile.push(math);
          }
        }
      } catch (e_6_1) {
        e_6 = {
          error: e_6_1
        };
      } finally {
        try {
          if (_d && !_d.done && (_a = _c.return)) _a.call(_c);
        } finally {
          if (e_6) throw e_6.error;
        }
      }
      try {
        for (var recompile_1 = __values(recompile), recompile_1_1 = recompile_1.next(); !recompile_1_1.done; recompile_1_1 = recompile_1.next()) {
          var math = recompile_1_1.value;
          var data = math.inputData.recompile;
          math.state(data.state);
          math.inputData.recompile = data;
          this.compileMath(math);
        }
      } catch (e_7_1) {
        e_7 = {
          error: e_7_1
        };
      } finally {
        try {
          if (recompile_1_1 && !recompile_1_1.done && (_b = recompile_1.return)) _b.call(recompile_1);
        } finally {
          if (e_7) throw e_7.error;
        }
      }
      this.processed.set('compile');
    }
    return this;
  };
  AbstractMathDocument.prototype.compileMath = function (math) {
    try {
      math.compile(this);
    } catch (err) {
      if (err.retry || err.restart) {
        throw err;
      }
      this.options['compileError'](this, math, err);
      math.inputData['error'] = err;
    }
  };
  AbstractMathDocument.prototype.compileError = function (math, err) {
    math.root = this.mmlFactory.create('math', null, [this.mmlFactory.create('merror', {
      'data-mjx-error': err.message,
      title: err.message
    }, [this.mmlFactory.create('mtext', null, [this.mmlFactory.create('text').setText('Math input error')])])]);
    if (math.display) {
      math.root.attributes.set('display', 'block');
    }
    math.inputData.error = err.message;
  };
  AbstractMathDocument.prototype.typeset = function () {
    var e_8, _a;
    if (!this.processed.isSet('typeset')) {
      try {
        for (var _b = __values(this.math), _c = _b.next(); !_c.done; _c = _b.next()) {
          var math = _c.value;
          try {
            math.typeset(this);
          } catch (err) {
            if (err.retry || err.restart) {
              throw err;
            }
            this.options['typesetError'](this, math, err);
            math.outputData['error'] = err;
          }
        }
      } catch (e_8_1) {
        e_8 = {
          error: e_8_1
        };
      } finally {
        try {
          if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
        } finally {
          if (e_8) throw e_8.error;
        }
      }
      this.processed.set('typeset');
    }
    return this;
  };
  AbstractMathDocument.prototype.typesetError = function (math, err) {
    math.typesetRoot = this.adaptor.node('mjx-container', {
      class: 'MathJax mjx-output-error',
      jax: this.outputJax.name
    }, [this.adaptor.node('span', {
      'data-mjx-error': err.message,
      title: err.message,
      style: {
        color: 'red',
        'background-color': 'yellow',
        'line-height': 'normal'
      }
    }, [this.adaptor.text('Math output error')])]);
    if (math.display) {
      this.adaptor.setAttributes(math.typesetRoot, {
        style: {
          display: 'block',
          margin: '1em 0',
          'text-align': 'center'
        }
      });
    }
    math.outputData.error = err.message;
  };
  AbstractMathDocument.prototype.getMetrics = function () {
    if (!this.processed.isSet('getMetrics')) {
      this.outputJax.getMetrics(this);
      this.processed.set('getMetrics');
    }
    return this;
  };
  AbstractMathDocument.prototype.updateDocument = function () {
    var e_9, _a;
    if (!this.processed.isSet('updateDocument')) {
      try {
        for (var _b = __values(this.math.reversed()), _c = _b.next(); !_c.done; _c = _b.next()) {
          var math = _c.value;
          math.updateDocument(this);
        }
      } catch (e_9_1) {
        e_9 = {
          error: e_9_1
        };
      } finally {
        try {
          if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
        } finally {
          if (e_9) throw e_9.error;
        }
      }
      this.processed.set('updateDocument');
    }
    return this;
  };
  AbstractMathDocument.prototype.removeFromDocument = function (_restore) {
    if (_restore === void 0) {
      _restore = false;
    }
    return this;
  };
  AbstractMathDocument.prototype.state = function (state, restore) {
    var e_10, _a;
    if (restore === void 0) {
      restore = false;
    }
    try {
      for (var _b = __values(this.math), _c = _b.next(); !_c.done; _c = _b.next()) {
        var math = _c.value;
        math.state(state, restore);
      }
    } catch (e_10_1) {
      e_10 = {
        error: e_10_1
      };
    } finally {
      try {
        if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
      } finally {
        if (e_10) throw e_10.error;
      }
    }
    if (state < MathItem_js_1.STATE.INSERTED) {
      this.processed.clear('updateDocument');
    }
    if (state < MathItem_js_1.STATE.TYPESET) {
      this.processed.clear('typeset');
      this.processed.clear('getMetrics');
    }
    if (state < MathItem_js_1.STATE.COMPILED) {
      this.processed.clear('compile');
    }
    return this;
  };
  AbstractMathDocument.prototype.reset = function (options) {
    var _a;
    if (options === void 0) {
      options = {
        processed: true
      };
    }
    options = (0, Options_js_1.userOptions)(Object.assign({}, exports.resetOptions), options);
    options.all && Object.assign(options, exports.resetAllOptions);
    options.processed && this.processed.reset();
    options.inputJax && this.inputJax.forEach(function (jax) {
      return jax.reset.apply(jax, __spreadArray([], __read(options.inputJax), false));
    });
    options.outputJax && (_a = this.outputJax).reset.apply(_a, __spreadArray([], __read(options.outputJax), false));
    return this;
  };
  AbstractMathDocument.prototype.clear = function () {
    this.reset();
    this.math.clear();
    return this;
  };
  AbstractMathDocument.prototype.concat = function (list) {
    this.math.merge(list);
    return this;
  };
  AbstractMathDocument.prototype.clearMathItemsWithin = function (containers) {
    var _a;
    var items = this.getMathItemsWithin(containers);
    (_a = this.math).remove.apply(_a, __spreadArray([], __read(items), false));
    return items;
  };
  AbstractMathDocument.prototype.getMathItemsWithin = function (elements) {
    var e_11, _a, e_12, _b;
    if (!Array.isArray(elements)) {
      elements = [elements];
    }
    var adaptor = this.adaptor;
    var items = [];
    var containers = adaptor.getElements(elements, this.document);
    try {
      ITEMS: for (var _c = __values(this.math), _d = _c.next(); !_d.done; _d = _c.next()) {
        var item = _d.value;
        try {
          for (var containers_1 = (e_12 = void 0, __values(containers)), containers_1_1 = containers_1.next(); !containers_1_1.done; containers_1_1 = containers_1.next()) {
            var container = containers_1_1.value;
            if (item.start.node && adaptor.contains(container, item.start.node)) {
              items.push(item);
              continue ITEMS;
            }
          }
        } catch (e_12_1) {
          e_12 = {
            error: e_12_1
          };
        } finally {
          try {
            if (containers_1_1 && !containers_1_1.done && (_b = containers_1.return)) _b.call(containers_1);
          } finally {
            if (e_12) throw e_12.error;
          }
        }
      }
    } catch (e_11_1) {
      e_11 = {
        error: e_11_1
      };
    } finally {
      try {
        if (_d && !_d.done && (_a = _c.return)) _a.call(_c);
      } finally {
        if (e_11) throw e_11.error;
      }
    }
    return items;
  };
  AbstractMathDocument.KIND = 'MathDocument';
  AbstractMathDocument.OPTIONS = {
    OutputJax: null,
    InputJax: null,
    MmlFactory: null,
    MathList: DefaultMathList,
    MathItem: DefaultMathItem,
    compileError: function (doc, math, err) {
      doc.compileError(math, err);
    },
    typesetError: function (doc, math, err) {
      doc.typesetError(math, err);
    },
    renderActions: (0, Options_js_1.expandable)({
      find: [MathItem_js_1.STATE.FINDMATH, 'findMath', '', false],
      compile: [MathItem_js_1.STATE.COMPILED],
      metrics: [MathItem_js_1.STATE.METRICS, 'getMetrics', '', false],
      typeset: [MathItem_js_1.STATE.TYPESET],
      update: [MathItem_js_1.STATE.INSERTED, 'updateDocument', false]
    })
  };
  AbstractMathDocument.ProcessBits = (0, BitField_js_1.BitFieldClass)('findMath', 'compile', 'getMetrics', 'typeset', 'updateDocument');
  return AbstractMathDocument;
}();
exports.AbstractMathDocument = AbstractMathDocument;

/***/ },

/***/ 37277
(__unused_webpack_module, exports, __webpack_require__) {



var __extends = this && this.__extends || function () {
  var extendStatics = function (d, b) {
    extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
var __assign = this && this.__assign || function () {
  __assign = Object.assign || function (t) {
    for (var s, i = 1, n = arguments.length; i < n; i++) {
      s = arguments[i];
      for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p)) t[p] = s[p];
    }
    return t;
  };
  return __assign.apply(this, arguments);
};
var __read = this && this.__read || function (o, n) {
  var m = typeof Symbol === "function" && o[Symbol.iterator];
  if (!m) return o;
  var i = m.call(o),
    r,
    ar = [],
    e;
  try {
    while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
  } catch (error) {
    e = {
      error: error
    };
  } finally {
    try {
      if (r && !r.done && (m = i["return"])) m.call(i);
    } finally {
      if (e) throw e.error;
    }
  }
  return ar;
};
var __values = this && this.__values || function (o) {
  var s = typeof Symbol === "function" && Symbol.iterator,
    m = s && o[s],
    i = 0;
  if (m) return m.call(o);
  if (o && typeof o.length === "number") return {
    next: function () {
      if (o && i >= o.length) o = void 0;
      return {
        value: o && o[i++],
        done: !o
      };
    }
  };
  throw new TypeError(s ? "Object is not iterable." : "Symbol.iterator is not defined.");
};
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.HTMLDocument = void 0;
var MathDocument_js_1 = __webpack_require__(32182);
var Options_js_1 = __webpack_require__(53588);
var HTMLMathItem_js_1 = __webpack_require__(44573);
var HTMLMathList_js_1 = __webpack_require__(75110);
var HTMLDomStrings_js_1 = __webpack_require__(56562);
var MathItem_js_1 = __webpack_require__(52016);
var HTMLDocument = function (_super) {
  __extends(HTMLDocument, _super);
  function HTMLDocument(document, adaptor, options) {
    var _this = this;
    var _a = __read((0, Options_js_1.separateOptions)(options, HTMLDomStrings_js_1.HTMLDomStrings.OPTIONS), 2),
      html = _a[0],
      dom = _a[1];
    _this = _super.call(this, document, adaptor, html) || this;
    _this.domStrings = _this.options['DomStrings'] || new HTMLDomStrings_js_1.HTMLDomStrings(dom);
    _this.domStrings.adaptor = adaptor;
    _this.styles = [];
    return _this;
  }
  HTMLDocument.prototype.findPosition = function (N, index, delim, nodes) {
    var e_1, _a;
    var adaptor = this.adaptor;
    try {
      for (var _b = __values(nodes[N]), _c = _b.next(); !_c.done; _c = _b.next()) {
        var list = _c.value;
        var _d = __read(list, 2),
          node = _d[0],
          n = _d[1];
        if (index <= n && adaptor.kind(node) === '#text') {
          return {
            node: node,
            n: Math.max(index, 0),
            delim: delim
          };
        }
        index -= n;
      }
    } catch (e_1_1) {
      e_1 = {
        error: e_1_1
      };
    } finally {
      try {
        if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
      } finally {
        if (e_1) throw e_1.error;
      }
    }
    return {
      node: null,
      n: 0,
      delim: delim
    };
  };
  HTMLDocument.prototype.mathItem = function (item, jax, nodes) {
    var math = item.math;
    var start = this.findPosition(item.n, item.start.n, item.open, nodes);
    var end = this.findPosition(item.n, item.end.n, item.close, nodes);
    return new this.options.MathItem(math, jax, item.display, start, end);
  };
  HTMLDocument.prototype.findMath = function (options) {
    var e_2, _a, e_3, _b, _c, e_4, _d, e_5, _e;
    if (!this.processed.isSet('findMath')) {
      this.adaptor.document = this.document;
      options = (0, Options_js_1.userOptions)({
        elements: this.options.elements || [this.adaptor.body(this.document)]
      }, options);
      try {
        for (var _f = __values(this.adaptor.getElements(options['elements'], this.document)), _g = _f.next(); !_g.done; _g = _f.next()) {
          var container = _g.value;
          var _h = __read([null, null], 2),
            strings = _h[0],
            nodes = _h[1];
          try {
            for (var _j = (e_3 = void 0, __values(this.inputJax)), _k = _j.next(); !_k.done; _k = _j.next()) {
              var jax = _k.value;
              var list = new this.options['MathList']();
              if (jax.processStrings) {
                if (strings === null) {
                  _c = __read(this.domStrings.find(container), 2), strings = _c[0], nodes = _c[1];
                }
                try {
                  for (var _l = (e_4 = void 0, __values(jax.findMath(strings))), _m = _l.next(); !_m.done; _m = _l.next()) {
                    var math = _m.value;
                    list.push(this.mathItem(math, jax, nodes));
                  }
                } catch (e_4_1) {
                  e_4 = {
                    error: e_4_1
                  };
                } finally {
                  try {
                    if (_m && !_m.done && (_d = _l.return)) _d.call(_l);
                  } finally {
                    if (e_4) throw e_4.error;
                  }
                }
              } else {
                try {
                  for (var _o = (e_5 = void 0, __values(jax.findMath(container))), _p = _o.next(); !_p.done; _p = _o.next()) {
                    var math = _p.value;
                    var item = new this.options.MathItem(math.math, jax, math.display, math.start, math.end);
                    list.push(item);
                  }
                } catch (e_5_1) {
                  e_5 = {
                    error: e_5_1
                  };
                } finally {
                  try {
                    if (_p && !_p.done && (_e = _o.return)) _e.call(_o);
                  } finally {
                    if (e_5) throw e_5.error;
                  }
                }
              }
              this.math.merge(list);
            }
          } catch (e_3_1) {
            e_3 = {
              error: e_3_1
            };
          } finally {
            try {
              if (_k && !_k.done && (_b = _j.return)) _b.call(_j);
            } finally {
              if (e_3) throw e_3.error;
            }
          }
        }
      } catch (e_2_1) {
        e_2 = {
          error: e_2_1
        };
      } finally {
        try {
          if (_g && !_g.done && (_a = _f.return)) _a.call(_f);
        } finally {
          if (e_2) throw e_2.error;
        }
      }
      this.processed.set('findMath');
    }
    return this;
  };
  HTMLDocument.prototype.updateDocument = function () {
    if (!this.processed.isSet('updateDocument')) {
      this.addPageElements();
      this.addStyleSheet();
      _super.prototype.updateDocument.call(this);
      this.processed.set('updateDocument');
    }
    return this;
  };
  HTMLDocument.prototype.addPageElements = function () {
    var body = this.adaptor.body(this.document);
    var node = this.documentPageElements();
    if (node) {
      this.adaptor.append(body, node);
    }
  };
  HTMLDocument.prototype.addStyleSheet = function () {
    var sheet = this.documentStyleSheet();
    var adaptor = this.adaptor;
    if (sheet && !adaptor.parent(sheet)) {
      var head = adaptor.head(this.document);
      var styles = this.findSheet(head, adaptor.getAttribute(sheet, 'id'));
      if (styles) {
        adaptor.replace(sheet, styles);
      } else {
        adaptor.append(head, sheet);
      }
    }
  };
  HTMLDocument.prototype.findSheet = function (head, id) {
    var e_6, _a;
    if (id) {
      try {
        for (var _b = __values(this.adaptor.tags(head, 'style')), _c = _b.next(); !_c.done; _c = _b.next()) {
          var sheet = _c.value;
          if (this.adaptor.getAttribute(sheet, 'id') === id) {
            return sheet;
          }
        }
      } catch (e_6_1) {
        e_6 = {
          error: e_6_1
        };
      } finally {
        try {
          if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
        } finally {
          if (e_6) throw e_6.error;
        }
      }
    }
    return null;
  };
  HTMLDocument.prototype.removeFromDocument = function (restore) {
    var e_7, _a;
    if (restore === void 0) {
      restore = false;
    }
    if (this.processed.isSet('updateDocument')) {
      try {
        for (var _b = __values(this.math), _c = _b.next(); !_c.done; _c = _b.next()) {
          var math = _c.value;
          if (math.state() >= MathItem_js_1.STATE.INSERTED) {
            math.state(MathItem_js_1.STATE.TYPESET, restore);
          }
        }
      } catch (e_7_1) {
        e_7 = {
          error: e_7_1
        };
      } finally {
        try {
          if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
        } finally {
          if (e_7) throw e_7.error;
        }
      }
    }
    this.processed.clear('updateDocument');
    return this;
  };
  HTMLDocument.prototype.documentStyleSheet = function () {
    return this.outputJax.styleSheet(this);
  };
  HTMLDocument.prototype.documentPageElements = function () {
    return this.outputJax.pageElements(this);
  };
  HTMLDocument.prototype.addStyles = function (styles) {
    this.styles.push(styles);
  };
  HTMLDocument.prototype.getStyles = function () {
    return this.styles;
  };
  HTMLDocument.KIND = 'HTML';
  HTMLDocument.OPTIONS = __assign(__assign({}, MathDocument_js_1.AbstractMathDocument.OPTIONS), {
    renderActions: (0, Options_js_1.expandable)(__assign(__assign({}, MathDocument_js_1.AbstractMathDocument.OPTIONS.renderActions), {
      styles: [MathItem_js_1.STATE.INSERTED + 1, '', 'updateStyleSheet', false]
    })),
    MathList: HTMLMathList_js_1.HTMLMathList,
    MathItem: HTMLMathItem_js_1.HTMLMathItem,
    DomStrings: null
  });
  return HTMLDocument;
}(MathDocument_js_1.AbstractMathDocument);
exports.HTMLDocument = HTMLDocument;

/***/ },

/***/ 44573
(__unused_webpack_module, exports, __webpack_require__) {



var __extends = this && this.__extends || function () {
  var extendStatics = function (d, b) {
    extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.HTMLMathItem = void 0;
var MathItem_js_1 = __webpack_require__(52016);
var HTMLMathItem = function (_super) {
  __extends(HTMLMathItem, _super);
  function HTMLMathItem(math, jax, display, start, end) {
    if (display === void 0) {
      display = true;
    }
    if (start === void 0) {
      start = {
        node: null,
        n: 0,
        delim: ''
      };
    }
    if (end === void 0) {
      end = {
        node: null,
        n: 0,
        delim: ''
      };
    }
    return _super.call(this, math, jax, display, start, end) || this;
  }
  Object.defineProperty(HTMLMathItem.prototype, "adaptor", {
    get: function () {
      return this.inputJax.adaptor;
    },
    enumerable: false,
    configurable: true
  });
  HTMLMathItem.prototype.updateDocument = function (_html) {
    if (this.state() < MathItem_js_1.STATE.INSERTED) {
      if (this.inputJax.processStrings) {
        var node = this.start.node;
        if (node === this.end.node) {
          if (this.end.n && this.end.n < this.adaptor.value(this.end.node).length) {
            this.adaptor.split(this.end.node, this.end.n);
          }
          if (this.start.n) {
            node = this.adaptor.split(this.start.node, this.start.n);
          }
          this.adaptor.replace(this.typesetRoot, node);
        } else {
          if (this.start.n) {
            node = this.adaptor.split(node, this.start.n);
          }
          while (node !== this.end.node) {
            var next = this.adaptor.next(node);
            this.adaptor.remove(node);
            node = next;
          }
          this.adaptor.insert(this.typesetRoot, node);
          if (this.end.n < this.adaptor.value(node).length) {
            this.adaptor.split(node, this.end.n);
          }
          this.adaptor.remove(node);
        }
      } else {
        this.adaptor.replace(this.typesetRoot, this.start.node);
      }
      this.start.node = this.end.node = this.typesetRoot;
      this.start.n = this.end.n = 0;
      this.state(MathItem_js_1.STATE.INSERTED);
    }
  };
  HTMLMathItem.prototype.updateStyleSheet = function (document) {
    document.addStyleSheet();
  };
  HTMLMathItem.prototype.removeFromDocument = function (restore) {
    if (restore === void 0) {
      restore = false;
    }
    if (this.state() >= MathItem_js_1.STATE.TYPESET) {
      var adaptor = this.adaptor;
      var node = this.start.node;
      var math = adaptor.text('');
      if (restore) {
        var text = this.start.delim + this.math + this.end.delim;
        if (this.inputJax.processStrings) {
          math = adaptor.text(text);
        } else {
          var doc = adaptor.parse(text, 'text/html');
          math = adaptor.firstChild(adaptor.body(doc));
        }
      }
      if (adaptor.parent(node)) {
        adaptor.replace(math, node);
      }
      this.start.node = this.end.node = math;
      this.start.n = this.end.n = 0;
    }
  };
  return HTMLMathItem;
}(MathItem_js_1.AbstractMathItem);
exports.HTMLMathItem = HTMLMathItem;

/***/ },

/***/ 49362
(__unused_webpack_module, exports, __webpack_require__) {



var __extends = this && this.__extends || function () {
  var extendStatics = function (d, b) {
    extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.HTMLHandler = void 0;
var Handler_js_1 = __webpack_require__(77177);
var HTMLDocument_js_1 = __webpack_require__(37277);
var HTMLHandler = function (_super) {
  __extends(HTMLHandler, _super);
  function HTMLHandler() {
    var _this = _super !== null && _super.apply(this, arguments) || this;
    _this.documentClass = HTMLDocument_js_1.HTMLDocument;
    return _this;
  }
  HTMLHandler.prototype.handlesDocument = function (document) {
    var adaptor = this.adaptor;
    if (typeof document === 'string') {
      try {
        document = adaptor.parse(document, 'text/html');
      } catch (err) {}
    }
    if (document instanceof adaptor.window.Document || document instanceof adaptor.window.HTMLElement || document instanceof adaptor.window.DocumentFragment) {
      return true;
    }
    return false;
  };
  HTMLHandler.prototype.create = function (document, options) {
    var adaptor = this.adaptor;
    if (typeof document === 'string') {
      document = adaptor.parse(document, 'text/html');
    } else if (document instanceof adaptor.window.HTMLElement || document instanceof adaptor.window.DocumentFragment) {
      var child = document;
      document = adaptor.parse('', 'text/html');
      adaptor.append(adaptor.body(document), child);
    }
    return _super.prototype.create.call(this, document, options);
  };
  return HTMLHandler;
}(Handler_js_1.AbstractHandler);
exports.HTMLHandler = HTMLHandler;

/***/ },

/***/ 56562
(__unused_webpack_module, exports, __webpack_require__) {



var __read = this && this.__read || function (o, n) {
  var m = typeof Symbol === "function" && o[Symbol.iterator];
  if (!m) return o;
  var i = m.call(o),
    r,
    ar = [],
    e;
  try {
    while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
  } catch (error) {
    e = {
      error: error
    };
  } finally {
    try {
      if (r && !r.done && (m = i["return"])) m.call(i);
    } finally {
      if (e) throw e.error;
    }
  }
  return ar;
};
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.HTMLDomStrings = void 0;
var Options_js_1 = __webpack_require__(53588);
var HTMLDomStrings = function () {
  function HTMLDomStrings(options) {
    if (options === void 0) {
      options = null;
    }
    var CLASS = this.constructor;
    this.options = (0, Options_js_1.userOptions)((0, Options_js_1.defaultOptions)({}, CLASS.OPTIONS), options);
    this.init();
    this.getPatterns();
  }
  HTMLDomStrings.prototype.init = function () {
    this.strings = [];
    this.string = '';
    this.snodes = [];
    this.nodes = [];
    this.stack = [];
  };
  HTMLDomStrings.prototype.getPatterns = function () {
    var skip = (0, Options_js_1.makeArray)(this.options['skipHtmlTags']);
    var ignore = (0, Options_js_1.makeArray)(this.options['ignoreHtmlClass']);
    var process = (0, Options_js_1.makeArray)(this.options['processHtmlClass']);
    this.skipHtmlTags = new RegExp('^(?:' + skip.join('|') + ')$', 'i');
    this.ignoreHtmlClass = new RegExp('(?:^| )(?:' + ignore.join('|') + ')(?: |$)');
    this.processHtmlClass = new RegExp('(?:^| )(?:' + process + ')(?: |$)');
  };
  HTMLDomStrings.prototype.pushString = function () {
    if (this.string.match(/\S/)) {
      this.strings.push(this.string);
      this.nodes.push(this.snodes);
    }
    this.string = '';
    this.snodes = [];
  };
  HTMLDomStrings.prototype.extendString = function (node, text) {
    this.snodes.push([node, text.length]);
    this.string += text;
  };
  HTMLDomStrings.prototype.handleText = function (node, ignore) {
    if (!ignore) {
      this.extendString(node, this.adaptor.value(node));
    }
    return this.adaptor.next(node);
  };
  HTMLDomStrings.prototype.handleTag = function (node, ignore) {
    if (!ignore) {
      var text = this.options['includeHtmlTags'][this.adaptor.kind(node)];
      this.extendString(node, text);
    }
    return this.adaptor.next(node);
  };
  HTMLDomStrings.prototype.handleContainer = function (node, ignore) {
    this.pushString();
    var cname = this.adaptor.getAttribute(node, 'class') || '';
    var tname = this.adaptor.kind(node) || '';
    var process = this.processHtmlClass.exec(cname);
    var next = node;
    if (this.adaptor.firstChild(node) && !this.adaptor.getAttribute(node, 'data-MJX') && (process || !this.skipHtmlTags.exec(tname))) {
      if (this.adaptor.next(node)) {
        this.stack.push([this.adaptor.next(node), ignore]);
      }
      next = this.adaptor.firstChild(node);
      ignore = (ignore || this.ignoreHtmlClass.exec(cname)) && !process;
    } else {
      next = this.adaptor.next(node);
    }
    return [next, ignore];
  };
  HTMLDomStrings.prototype.handleOther = function (node, _ignore) {
    this.pushString();
    return this.adaptor.next(node);
  };
  HTMLDomStrings.prototype.find = function (node) {
    var _a, _b;
    this.init();
    var stop = this.adaptor.next(node);
    var ignore = false;
    var include = this.options['includeHtmlTags'];
    while (node && node !== stop) {
      var kind = this.adaptor.kind(node);
      if (kind === '#text') {
        node = this.handleText(node, ignore);
      } else if (include.hasOwnProperty(kind)) {
        node = this.handleTag(node, ignore);
      } else if (kind) {
        _a = __read(this.handleContainer(node, ignore), 2), node = _a[0], ignore = _a[1];
      } else {
        node = this.handleOther(node, ignore);
      }
      if (!node && this.stack.length) {
        this.pushString();
        _b = __read(this.stack.pop(), 2), node = _b[0], ignore = _b[1];
      }
    }
    this.pushString();
    var result = [this.strings, this.nodes];
    this.init();
    return result;
  };
  HTMLDomStrings.OPTIONS = {
    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code', 'annotation', 'annotation-xml'],
    includeHtmlTags: {
      br: '\n',
      wbr: '',
      '#comment': ''
    },
    ignoreHtmlClass: 'mathjax_ignore',
    processHtmlClass: 'mathjax_process'
  };
  return HTMLDomStrings;
}();
exports.HTMLDomStrings = HTMLDomStrings;

/***/ },

/***/ 58872
(__unused_webpack_module, exports, __webpack_require__) {



var __extends = this && this.__extends || function () {
  var extendStatics = function (d, b) {
    extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
var __values = this && this.__values || function (o) {
  var s = typeof Symbol === "function" && Symbol.iterator,
    m = s && o[s],
    i = 0;
  if (m) return m.call(o);
  if (o && typeof o.length === "number") return {
    next: function () {
      if (o && i >= o.length) o = void 0;
      return {
        value: o && o[i++],
        done: !o
      };
    }
  };
  throw new TypeError(s ? "Object is not iterable." : "Symbol.iterator is not defined.");
};
var __read = this && this.__read || function (o, n) {
  var m = typeof Symbol === "function" && o[Symbol.iterator];
  if (!m) return o;
  var i = m.call(o),
    r,
    ar = [],
    e;
  try {
    while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
  } catch (error) {
    e = {
      error: error
    };
  } finally {
    try {
      if (r && !r.done && (m = i["return"])) m.call(i);
    } finally {
      if (e) throw e.error;
    }
  }
  return ar;
};
var __spreadArray = this && this.__spreadArray || function (to, from, pack) {
  if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
    if (ar || !(i in from)) {
      if (!ar) ar = Array.prototype.slice.call(from, 0, i);
      ar[i] = from[i];
    }
  }
  return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.FunctionList = void 0;
var PrioritizedList_js_1 = __webpack_require__(30457);
var FunctionList = function (_super) {
  __extends(FunctionList, _super);
  function FunctionList() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  FunctionList.prototype.execute = function () {
    var e_1, _a;
    var data = [];
    for (var _i = 0; _i < arguments.length; _i++) {
      data[_i] = arguments[_i];
    }
    try {
      for (var _b = __values(this), _c = _b.next(); !_c.done; _c = _b.next()) {
        var item = _c.value;
        var result = item.item.apply(item, __spreadArray([], __read(data), false));
        if (result === false) {
          return false;
        }
      }
    } catch (e_1_1) {
      e_1 = {
        error: e_1_1
      };
    } finally {
      try {
        if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
      } finally {
        if (e_1) throw e_1.error;
      }
    }
    return true;
  };
  FunctionList.prototype.asyncExecute = function () {
    var data = [];
    for (var _i = 0; _i < arguments.length; _i++) {
      data[_i] = arguments[_i];
    }
    var i = -1;
    var items = this.items;
    return new Promise(function (ok, fail) {
      (function execute() {
        var _a;
        while (++i < items.length) {
          var result = (_a = items[i]).item.apply(_a, __spreadArray([], __read(data), false));
          if (result instanceof Promise) {
            result.then(execute).catch(function (err) {
              return fail(err);
            });
            return;
          }
          if (result === false) {
            ok(false);
            return;
          }
        }
        ok(true);
      })();
    });
  };
  return FunctionList;
}(PrioritizedList_js_1.PrioritizedList);
exports.FunctionList = FunctionList;

/***/ },

/***/ 74717
(__unused_webpack_module, exports) {



var __extends = this && this.__extends || function () {
  var extendStatics = function (d, b) {
    extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
var __values = this && this.__values || function (o) {
  var s = typeof Symbol === "function" && Symbol.iterator,
    m = s && o[s],
    i = 0;
  if (m) return m.call(o);
  if (o && typeof o.length === "number") return {
    next: function () {
      if (o && i >= o.length) o = void 0;
      return {
        value: o && o[i++],
        done: !o
      };
    }
  };
  throw new TypeError(s ? "Object is not iterable." : "Symbol.iterator is not defined.");
};
var __read = this && this.__read || function (o, n) {
  var m = typeof Symbol === "function" && o[Symbol.iterator];
  if (!m) return o;
  var i = m.call(o),
    r,
    ar = [],
    e;
  try {
    while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
  } catch (error) {
    e = {
      error: error
    };
  } finally {
    try {
      if (r && !r.done && (m = i["return"])) m.call(i);
    } finally {
      if (e) throw e.error;
    }
  }
  return ar;
};
var __spreadArray = this && this.__spreadArray || function (to, from, pack) {
  if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
    if (ar || !(i in from)) {
      if (!ar) ar = Array.prototype.slice.call(from, 0, i);
      ar[i] = from[i];
    }
  }
  return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.BitFieldClass = exports.BitField = void 0;
var BitField = function () {
  function BitField() {
    this.bits = 0;
  }
  BitField.allocate = function () {
    var e_1, _a;
    var names = [];
    for (var _i = 0; _i < arguments.length; _i++) {
      names[_i] = arguments[_i];
    }
    try {
      for (var names_1 = __values(names), names_1_1 = names_1.next(); !names_1_1.done; names_1_1 = names_1.next()) {
        var name_1 = names_1_1.value;
        if (this.has(name_1)) {
          throw new Error('Bit already allocated for ' + name_1);
        }
        if (this.next === BitField.MAXBIT) {
          throw new Error('Maximum number of bits already allocated');
        }
        this.names.set(name_1, this.next);
        this.next <<= 1;
      }
    } catch (e_1_1) {
      e_1 = {
        error: e_1_1
      };
    } finally {
      try {
        if (names_1_1 && !names_1_1.done && (_a = names_1.return)) _a.call(names_1);
      } finally {
        if (e_1) throw e_1.error;
      }
    }
  };
  BitField.has = function (name) {
    return this.names.has(name);
  };
  BitField.prototype.set = function (name) {
    this.bits |= this.getBit(name);
  };
  BitField.prototype.clear = function (name) {
    this.bits &= ~this.getBit(name);
  };
  BitField.prototype.isSet = function (name) {
    return !!(this.bits & this.getBit(name));
  };
  BitField.prototype.reset = function () {
    this.bits = 0;
  };
  BitField.prototype.getBit = function (name) {
    var bit = this.constructor.names.get(name);
    if (!bit) {
      throw new Error('Unknown bit-field name: ' + name);
    }
    return bit;
  };
  BitField.MAXBIT = 1 << 31;
  BitField.next = 1;
  BitField.names = new Map();
  return BitField;
}();
exports.BitField = BitField;
function BitFieldClass() {
  var names = [];
  for (var _i = 0; _i < arguments.length; _i++) {
    names[_i] = arguments[_i];
  }
  var Bits = function (_super) {
    __extends(Bits, _super);
    function Bits() {
      return _super !== null && _super.apply(this, arguments) || this;
    }
    return Bits;
  }(BitField);
  Bits.allocate.apply(Bits, __spreadArray([], __read(names), false));
  return Bits;
}
exports.BitFieldClass = BitFieldClass;

/***/ },

/***/ 75110
(__unused_webpack_module, exports, __webpack_require__) {



var __extends = this && this.__extends || function () {
  var extendStatics = function (d, b) {
    extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.HTMLMathList = void 0;
var MathList_js_1 = __webpack_require__(1371);
var HTMLMathList = function (_super) {
  __extends(HTMLMathList, _super);
  function HTMLMathList() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  return HTMLMathList;
}(MathList_js_1.AbstractMathList);
exports.HTMLMathList = HTMLMathList;

/***/ },

/***/ 77177
(__unused_webpack_module, exports, __webpack_require__) {



var __extends = this && this.__extends || function () {
  var extendStatics = function (d, b) {
    extendStatics = Object.setPrototypeOf || {
      __proto__: []
    } instanceof Array && function (d, b) {
      d.__proto__ = b;
    } || function (d, b) {
      for (var p in b) if (Object.prototype.hasOwnProperty.call(b, p)) d[p] = b[p];
    };
    return extendStatics(d, b);
  };
  return function (d, b) {
    if (typeof b !== "function" && b !== null) throw new TypeError("Class extends value " + String(b) + " is not a constructor or null");
    extendStatics(d, b);
    function __() {
      this.constructor = d;
    }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
  };
}();
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.AbstractHandler = void 0;
var MathDocument_js_1 = __webpack_require__(32182);
var DefaultMathDocument = function (_super) {
  __extends(DefaultMathDocument, _super);
  function DefaultMathDocument() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  return DefaultMathDocument;
}(MathDocument_js_1.AbstractMathDocument);
var AbstractHandler = function () {
  function AbstractHandler(adaptor, priority) {
    if (priority === void 0) {
      priority = 5;
    }
    this.documentClass = DefaultMathDocument;
    this.adaptor = adaptor;
    this.priority = priority;
  }
  Object.defineProperty(AbstractHandler.prototype, "name", {
    get: function () {
      return this.constructor.NAME;
    },
    enumerable: false,
    configurable: true
  });
  AbstractHandler.prototype.handlesDocument = function (_document) {
    return false;
  };
  AbstractHandler.prototype.create = function (document, options) {
    return new this.documentClass(document, this.adaptor, options);
  };
  AbstractHandler.NAME = 'generic';
  return AbstractHandler;
}();
exports.AbstractHandler = AbstractHandler;

/***/ },

/***/ 78541
(__unused_webpack_module, exports) {



var __generator = this && this.__generator || function (thisArg, body) {
  var _ = {
      label: 0,
      sent: function () {
        if (t[0] & 1) throw t[1];
        return t[1];
      },
      trys: [],
      ops: []
    },
    f,
    y,
    t,
    g;
  return g = {
    next: verb(0),
    "throw": verb(1),
    "return": verb(2)
  }, typeof Symbol === "function" && (g[Symbol.iterator] = function () {
    return this;
  }), g;
  function verb(n) {
    return function (v) {
      return step([n, v]);
    };
  }
  function step(op) {
    if (f) throw new TypeError("Generator is already executing.");
    while (_) try {
      if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
      if (y = 0, t) op = [op[0] & 2, t.value];
      switch (op[0]) {
        case 0:
        case 1:
          t = op;
          break;
        case 4:
          _.label++;
          return {
            value: op[1],
            done: false
          };
        case 5:
          _.label++;
          y = op[1];
          op = [0];
          continue;
        case 7:
          op = _.ops.pop();
          _.trys.pop();
          continue;
        default:
          if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) {
            _ = 0;
            continue;
          }
          if (op[0] === 3 && (!t || op[1] > t[0] && op[1] < t[3])) {
            _.label = op[1];
            break;
          }
          if (op[0] === 6 && _.label < t[1]) {
            _.label = t[1];
            t = op;
            break;
          }
          if (t && _.label < t[2]) {
            _.label = t[2];
            _.ops.push(op);
            break;
          }
          if (t[2]) _.ops.pop();
          _.trys.pop();
          continue;
      }
      op = body.call(thisArg, _);
    } catch (e) {
      op = [6, e];
      y = 0;
    } finally {
      f = t = 0;
    }
    if (op[0] & 5) throw op[1];
    return {
      value: op[0] ? op[1] : void 0,
      done: true
    };
  }
};
var __read = this && this.__read || function (o, n) {
  var m = typeof Symbol === "function" && o[Symbol.iterator];
  if (!m) return o;
  var i = m.call(o),
    r,
    ar = [],
    e;
  try {
    while ((n === void 0 || n-- > 0) && !(r = i.next()).done) ar.push(r.value);
  } catch (error) {
    e = {
      error: error
    };
  } finally {
    try {
      if (r && !r.done && (m = i["return"])) m.call(i);
    } finally {
      if (e) throw e.error;
    }
  }
  return ar;
};
var __spreadArray = this && this.__spreadArray || function (to, from, pack) {
  if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
    if (ar || !(i in from)) {
      if (!ar) ar = Array.prototype.slice.call(from, 0, i);
      ar[i] = from[i];
    }
  }
  return to.concat(ar || Array.prototype.slice.call(from));
};
var __values = this && this.__values || function (o) {
  var s = typeof Symbol === "function" && Symbol.iterator,
    m = s && o[s],
    i = 0;
  if (m) return m.call(o);
  if (o && typeof o.length === "number") return {
    next: function () {
      if (o && i >= o.length) o = void 0;
      return {
        value: o && o[i++],
        done: !o
      };
    }
  };
  throw new TypeError(s ? "Object is not iterable." : "Symbol.iterator is not defined.");
};
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.LinkedList = exports.ListItem = exports.END = void 0;
exports.END = Symbol();
var ListItem = function () {
  function ListItem(data) {
    if (data === void 0) {
      data = null;
    }
    this.next = null;
    this.prev = null;
    this.data = data;
  }
  return ListItem;
}();
exports.ListItem = ListItem;
var LinkedList = function () {
  function LinkedList() {
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
      args[_i] = arguments[_i];
    }
    this.list = new ListItem(exports.END);
    this.list.next = this.list.prev = this.list;
    this.push.apply(this, __spreadArray([], __read(args), false));
  }
  LinkedList.prototype.isBefore = function (a, b) {
    return a < b;
  };
  LinkedList.prototype.push = function () {
    var e_1, _a;
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
      args[_i] = arguments[_i];
    }
    try {
      for (var args_1 = __values(args), args_1_1 = args_1.next(); !args_1_1.done; args_1_1 = args_1.next()) {
        var data = args_1_1.value;
        var item = new ListItem(data);
        item.next = this.list;
        item.prev = this.list.prev;
        this.list.prev = item;
        item.prev.next = item;
      }
    } catch (e_1_1) {
      e_1 = {
        error: e_1_1
      };
    } finally {
      try {
        if (args_1_1 && !args_1_1.done && (_a = args_1.return)) _a.call(args_1);
      } finally {
        if (e_1) throw e_1.error;
      }
    }
    return this;
  };
  LinkedList.prototype.pop = function () {
    var item = this.list.prev;
    if (item.data === exports.END) {
      return null;
    }
    this.list.prev = item.prev;
    item.prev.next = this.list;
    item.next = item.prev = null;
    return item.data;
  };
  LinkedList.prototype.unshift = function () {
    var e_2, _a;
    var args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
      args[_i] = arguments[_i];
    }
    try {
      for (var _b = __values(args.slice(0).reverse()), _c = _b.next(); !_c.done; _c = _b.next()) {
        var data = _c.value;
        var item = new ListItem(data);
        item.next = this.list.next;
        item.prev = this.list;
        this.list.next = item;
        item.next.prev = item;
      }
    } catch (e_2_1) {
      e_2 = {
        error: e_2_1
      };
    } finally {
      try {
        if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
      } finally {
        if (e_2) throw e_2.error;
      }
    }
    return this;
  };
  LinkedList.prototype.shift = function () {
    var item = this.list.next;
    if (item.data === exports.END) {
      return null;
    }
    this.list.next = item.next;
    item.next.prev = this.list;
    item.next = item.prev = null;
    return item.data;
  };
  LinkedList.prototype.remove = function () {
    var e_3, _a;
    var items = [];
    for (var _i = 0; _i < arguments.length; _i++) {
      items[_i] = arguments[_i];
    }
    var map = new Map();
    try {
      for (var items_1 = __values(items), items_1_1 = items_1.next(); !items_1_1.done; items_1_1 = items_1.next()) {
        var item_1 = items_1_1.value;
        map.set(item_1, true);
      }
    } catch (e_3_1) {
      e_3 = {
        error: e_3_1
      };
    } finally {
      try {
        if (items_1_1 && !items_1_1.done && (_a = items_1.return)) _a.call(items_1);
      } finally {
        if (e_3) throw e_3.error;
      }
    }
    var item = this.list.next;
    while (item.data !== exports.END) {
      var next = item.next;
      if (map.has(item.data)) {
        item.prev.next = item.next;
        item.next.prev = item.prev;
        item.next = item.prev = null;
      }
      item = next;
    }
  };
  LinkedList.prototype.clear = function () {
    this.list.next.prev = this.list.prev.next = null;
    this.list.next = this.list.prev = this.list;
    return this;
  };
  LinkedList.prototype[Symbol.iterator] = function () {
    var current;
    return __generator(this, function (_a) {
      switch (_a.label) {
        case 0:
          current = this.list.next;
          _a.label = 1;
        case 1:
          if (!(current.data !== exports.END)) return [3, 3];
          return [4, current.data];
        case 2:
          _a.sent();
          current = current.next;
          return [3, 1];
        case 3:
          return [2];
      }
    });
  };
  LinkedList.prototype.reversed = function () {
    var current;
    return __generator(this, function (_a) {
      switch (_a.label) {
        case 0:
          current = this.list.prev;
          _a.label = 1;
        case 1:
          if (!(current.data !== exports.END)) return [3, 3];
          return [4, current.data];
        case 2:
          _a.sent();
          current = current.prev;
          return [3, 1];
        case 3:
          return [2];
      }
    });
  };
  LinkedList.prototype.insert = function (data, isBefore) {
    if (isBefore === void 0) {
      isBefore = null;
    }
    if (isBefore === null) {
      isBefore = this.isBefore.bind(this);
    }
    var item = new ListItem(data);
    var cur = this.list.next;
    while (cur.data !== exports.END && isBefore(cur.data, item.data)) {
      cur = cur.next;
    }
    item.prev = cur.prev;
    item.next = cur;
    cur.prev.next = cur.prev = item;
    return this;
  };
  LinkedList.prototype.sort = function (isBefore) {
    var e_4, _a;
    if (isBefore === void 0) {
      isBefore = null;
    }
    if (isBefore === null) {
      isBefore = this.isBefore.bind(this);
    }
    var lists = [];
    try {
      for (var _b = __values(this), _c = _b.next(); !_c.done; _c = _b.next()) {
        var item = _c.value;
        lists.push(new LinkedList(item));
      }
    } catch (e_4_1) {
      e_4 = {
        error: e_4_1
      };
    } finally {
      try {
        if (_c && !_c.done && (_a = _b.return)) _a.call(_b);
      } finally {
        if (e_4) throw e_4.error;
      }
    }
    this.list.next = this.list.prev = this.list;
    while (lists.length > 1) {
      var l1 = lists.shift();
      var l2 = lists.shift();
      l1.merge(l2, isBefore);
      lists.push(l1);
    }
    if (lists.length) {
      this.list = lists[0].list;
    }
    return this;
  };
  LinkedList.prototype.merge = function (list, isBefore) {
    var _a, _b, _c, _d, _e;
    if (isBefore === void 0) {
      isBefore = null;
    }
    if (isBefore === null) {
      isBefore = this.isBefore.bind(this);
    }
    var lcur = this.list.next;
    var mcur = list.list.next;
    while (lcur.data !== exports.END && mcur.data !== exports.END) {
      if (isBefore(mcur.data, lcur.data)) {
        _a = __read([lcur, mcur], 2), mcur.prev.next = _a[0], lcur.prev.next = _a[1];
        _b = __read([lcur.prev, mcur.prev], 2), mcur.prev = _b[0], lcur.prev = _b[1];
        _c = __read([list.list, this.list], 2), this.list.prev.next = _c[0], list.list.prev.next = _c[1];
        _d = __read([list.list.prev, this.list.prev], 2), this.list.prev = _d[0], list.list.prev = _d[1];
        _e = __read([mcur.next, lcur], 2), lcur = _e[0], mcur = _e[1];
      } else {
        lcur = lcur.next;
      }
    }
    if (mcur.data !== exports.END) {
      this.list.prev.next = list.list.next;
      list.list.next.prev = this.list.prev;
      list.list.prev.next = this.list;
      this.list.prev = list.list.prev;
      list.list.next = list.list.prev = list.list;
    }
    return this;
  };
  return LinkedList;
}();
exports.LinkedList = LinkedList;

/***/ },

/***/ 80481
(__unused_webpack_module, exports, __webpack_require__) {



Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.AbstractOutputJax = void 0;
var Options_js_1 = __webpack_require__(53588);
var FunctionList_js_1 = __webpack_require__(58872);
var AbstractOutputJax = function () {
  function AbstractOutputJax(options) {
    if (options === void 0) {
      options = {};
    }
    this.adaptor = null;
    var CLASS = this.constructor;
    this.options = (0, Options_js_1.userOptions)((0, Options_js_1.defaultOptions)({}, CLASS.OPTIONS), options);
    this.postFilters = new FunctionList_js_1.FunctionList();
  }
  Object.defineProperty(AbstractOutputJax.prototype, "name", {
    get: function () {
      return this.constructor.NAME;
    },
    enumerable: false,
    configurable: true
  });
  AbstractOutputJax.prototype.setAdaptor = function (adaptor) {
    this.adaptor = adaptor;
  };
  AbstractOutputJax.prototype.initialize = function () {};
  AbstractOutputJax.prototype.reset = function () {
    var _args = [];
    for (var _i = 0; _i < arguments.length; _i++) {
      _args[_i] = arguments[_i];
    }
  };
  AbstractOutputJax.prototype.getMetrics = function (_document) {};
  AbstractOutputJax.prototype.styleSheet = function (_document) {
    return null;
  };
  AbstractOutputJax.prototype.pageElements = function (_document) {
    return null;
  };
  AbstractOutputJax.prototype.executeFilters = function (filters, math, document, data) {
    var args = {
      math: math,
      document: document,
      data: data
    };
    filters.execute(args);
    return args.data;
  };
  AbstractOutputJax.NAME = 'generic';
  AbstractOutputJax.OPTIONS = {};
  return AbstractOutputJax;
}();
exports.AbstractOutputJax = AbstractOutputJax;

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiOTM2Mi5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7Ozs7O0FDckNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7Ozs7O0FDL0RBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7QUNqREE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7Ozs7O0FDbnNCQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7QUNuVUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7QUN4SEE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7QUM1REE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7Ozs7OztBQzNJQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7Ozs7OztBQ3ZJQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7Ozs7OztBQ3RKQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7Ozs7O0FDbENBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTs7Ozs7OztBQzNEQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7Ozs7O0FDdFpBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL21hdGhqYXgtZnVsbC9qcy9jb3JlL01hdGhMaXN0LmpzIiwid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvbWF0aGpheC1mdWxsL2pzL2NvcmUvSW5wdXRKYXguanMiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9tYXRoamF4LWZ1bGwvanMvdXRpbC9Qcmlvcml0aXplZExpc3QuanMiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9tYXRoamF4LWZ1bGwvanMvY29yZS9NYXRoRG9jdW1lbnQuanMiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9tYXRoamF4LWZ1bGwvanMvaGFuZGxlcnMvaHRtbC9IVE1MRG9jdW1lbnQuanMiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9tYXRoamF4LWZ1bGwvanMvaGFuZGxlcnMvaHRtbC9IVE1MTWF0aEl0ZW0uanMiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9tYXRoamF4LWZ1bGwvanMvaGFuZGxlcnMvaHRtbC9IVE1MSGFuZGxlci5qcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL21hdGhqYXgtZnVsbC9qcy9oYW5kbGVycy9odG1sL0hUTUxEb21TdHJpbmdzLmpzIiwid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvbWF0aGpheC1mdWxsL2pzL3V0aWwvRnVuY3Rpb25MaXN0LmpzIiwid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvbWF0aGpheC1mdWxsL2pzL3V0aWwvQml0RmllbGQuanMiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9tYXRoamF4LWZ1bGwvanMvaGFuZGxlcnMvaHRtbC9IVE1MTWF0aExpc3QuanMiLCJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9tYXRoamF4LWZ1bGwvanMvY29yZS9IYW5kbGVyLmpzIiwid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvbWF0aGpheC1mdWxsL2pzL3V0aWwvTGlua2VkTGlzdC5qcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL21hdGhqYXgtZnVsbC9qcy9jb3JlL091dHB1dEpheC5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJcInVzZSBzdHJpY3RcIjtcblxudmFyIF9fZXh0ZW5kcyA9IHRoaXMgJiYgdGhpcy5fX2V4dGVuZHMgfHwgZnVuY3Rpb24gKCkge1xuICB2YXIgZXh0ZW5kU3RhdGljcyA9IGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgZXh0ZW5kU3RhdGljcyA9IE9iamVjdC5zZXRQcm90b3R5cGVPZiB8fCB7XG4gICAgICBfX3Byb3RvX186IFtdXG4gICAgfSBpbnN0YW5jZW9mIEFycmF5ICYmIGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgICBkLl9fcHJvdG9fXyA9IGI7XG4gICAgfSB8fCBmdW5jdGlvbiAoZCwgYikge1xuICAgICAgZm9yICh2YXIgcCBpbiBiKSBpZiAoT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsKGIsIHApKSBkW3BdID0gYltwXTtcbiAgICB9O1xuICAgIHJldHVybiBleHRlbmRTdGF0aWNzKGQsIGIpO1xuICB9O1xuICByZXR1cm4gZnVuY3Rpb24gKGQsIGIpIHtcbiAgICBpZiAodHlwZW9mIGIgIT09IFwiZnVuY3Rpb25cIiAmJiBiICE9PSBudWxsKSB0aHJvdyBuZXcgVHlwZUVycm9yKFwiQ2xhc3MgZXh0ZW5kcyB2YWx1ZSBcIiArIFN0cmluZyhiKSArIFwiIGlzIG5vdCBhIGNvbnN0cnVjdG9yIG9yIG51bGxcIik7XG4gICAgZXh0ZW5kU3RhdGljcyhkLCBiKTtcbiAgICBmdW5jdGlvbiBfXygpIHtcbiAgICAgIHRoaXMuY29uc3RydWN0b3IgPSBkO1xuICAgIH1cbiAgICBkLnByb3RvdHlwZSA9IGIgPT09IG51bGwgPyBPYmplY3QuY3JlYXRlKGIpIDogKF9fLnByb3RvdHlwZSA9IGIucHJvdG90eXBlLCBuZXcgX18oKSk7XG4gIH07XG59KCk7XG5PYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgXCJfX2VzTW9kdWxlXCIsIHtcbiAgdmFsdWU6IHRydWVcbn0pO1xuZXhwb3J0cy5BYnN0cmFjdE1hdGhMaXN0ID0gdm9pZCAwO1xudmFyIExpbmtlZExpc3RfanNfMSA9IHJlcXVpcmUoXCIuLi91dGlsL0xpbmtlZExpc3QuanNcIik7XG52YXIgQWJzdHJhY3RNYXRoTGlzdCA9IGZ1bmN0aW9uIChfc3VwZXIpIHtcbiAgX19leHRlbmRzKEFic3RyYWN0TWF0aExpc3QsIF9zdXBlcik7XG4gIGZ1bmN0aW9uIEFic3RyYWN0TWF0aExpc3QoKSB7XG4gICAgcmV0dXJuIF9zdXBlciAhPT0gbnVsbCAmJiBfc3VwZXIuYXBwbHkodGhpcywgYXJndW1lbnRzKSB8fCB0aGlzO1xuICB9XG4gIEFic3RyYWN0TWF0aExpc3QucHJvdG90eXBlLmlzQmVmb3JlID0gZnVuY3Rpb24gKGEsIGIpIHtcbiAgICByZXR1cm4gYS5zdGFydC5pIDwgYi5zdGFydC5pIHx8IGEuc3RhcnQuaSA9PT0gYi5zdGFydC5pICYmIGEuc3RhcnQubiA8IGIuc3RhcnQubjtcbiAgfTtcbiAgcmV0dXJuIEFic3RyYWN0TWF0aExpc3Q7XG59KExpbmtlZExpc3RfanNfMS5MaW5rZWRMaXN0KTtcbmV4cG9ydHMuQWJzdHJhY3RNYXRoTGlzdCA9IEFic3RyYWN0TWF0aExpc3Q7IiwiXCJ1c2Ugc3RyaWN0XCI7XG5cbk9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBcIl9fZXNNb2R1bGVcIiwge1xuICB2YWx1ZTogdHJ1ZVxufSk7XG5leHBvcnRzLkFic3RyYWN0SW5wdXRKYXggPSB2b2lkIDA7XG52YXIgT3B0aW9uc19qc18xID0gcmVxdWlyZShcIi4uL3V0aWwvT3B0aW9ucy5qc1wiKTtcbnZhciBGdW5jdGlvbkxpc3RfanNfMSA9IHJlcXVpcmUoXCIuLi91dGlsL0Z1bmN0aW9uTGlzdC5qc1wiKTtcbnZhciBBYnN0cmFjdElucHV0SmF4ID0gZnVuY3Rpb24gKCkge1xuICBmdW5jdGlvbiBBYnN0cmFjdElucHV0SmF4KG9wdGlvbnMpIHtcbiAgICBpZiAob3B0aW9ucyA9PT0gdm9pZCAwKSB7XG4gICAgICBvcHRpb25zID0ge307XG4gICAgfVxuICAgIHRoaXMuYWRhcHRvciA9IG51bGw7XG4gICAgdGhpcy5tbWxGYWN0b3J5ID0gbnVsbDtcbiAgICB2YXIgQ0xBU1MgPSB0aGlzLmNvbnN0cnVjdG9yO1xuICAgIHRoaXMub3B0aW9ucyA9ICgwLCBPcHRpb25zX2pzXzEudXNlck9wdGlvbnMpKCgwLCBPcHRpb25zX2pzXzEuZGVmYXVsdE9wdGlvbnMpKHt9LCBDTEFTUy5PUFRJT05TKSwgb3B0aW9ucyk7XG4gICAgdGhpcy5wcmVGaWx0ZXJzID0gbmV3IEZ1bmN0aW9uTGlzdF9qc18xLkZ1bmN0aW9uTGlzdCgpO1xuICAgIHRoaXMucG9zdEZpbHRlcnMgPSBuZXcgRnVuY3Rpb25MaXN0X2pzXzEuRnVuY3Rpb25MaXN0KCk7XG4gIH1cbiAgT2JqZWN0LmRlZmluZVByb3BlcnR5KEFic3RyYWN0SW5wdXRKYXgucHJvdG90eXBlLCBcIm5hbWVcIiwge1xuICAgIGdldDogZnVuY3Rpb24gKCkge1xuICAgICAgcmV0dXJuIHRoaXMuY29uc3RydWN0b3IuTkFNRTtcbiAgICB9LFxuICAgIGVudW1lcmFibGU6IGZhbHNlLFxuICAgIGNvbmZpZ3VyYWJsZTogdHJ1ZVxuICB9KTtcbiAgQWJzdHJhY3RJbnB1dEpheC5wcm90b3R5cGUuc2V0QWRhcHRvciA9IGZ1bmN0aW9uIChhZGFwdG9yKSB7XG4gICAgdGhpcy5hZGFwdG9yID0gYWRhcHRvcjtcbiAgfTtcbiAgQWJzdHJhY3RJbnB1dEpheC5wcm90b3R5cGUuc2V0TW1sRmFjdG9yeSA9IGZ1bmN0aW9uIChtbWxGYWN0b3J5KSB7XG4gICAgdGhpcy5tbWxGYWN0b3J5ID0gbW1sRmFjdG9yeTtcbiAgfTtcbiAgQWJzdHJhY3RJbnB1dEpheC5wcm90b3R5cGUuaW5pdGlhbGl6ZSA9IGZ1bmN0aW9uICgpIHt9O1xuICBBYnN0cmFjdElucHV0SmF4LnByb3RvdHlwZS5yZXNldCA9IGZ1bmN0aW9uICgpIHtcbiAgICB2YXIgX2FyZ3MgPSBbXTtcbiAgICBmb3IgKHZhciBfaSA9IDA7IF9pIDwgYXJndW1lbnRzLmxlbmd0aDsgX2krKykge1xuICAgICAgX2FyZ3NbX2ldID0gYXJndW1lbnRzW19pXTtcbiAgICB9XG4gIH07XG4gIE9iamVjdC5kZWZpbmVQcm9wZXJ0eShBYnN0cmFjdElucHV0SmF4LnByb3RvdHlwZSwgXCJwcm9jZXNzU3RyaW5nc1wiLCB7XG4gICAgZ2V0OiBmdW5jdGlvbiAoKSB7XG4gICAgICByZXR1cm4gdHJ1ZTtcbiAgICB9LFxuICAgIGVudW1lcmFibGU6IGZhbHNlLFxuICAgIGNvbmZpZ3VyYWJsZTogdHJ1ZVxuICB9KTtcbiAgQWJzdHJhY3RJbnB1dEpheC5wcm90b3R5cGUuZmluZE1hdGggPSBmdW5jdGlvbiAoX25vZGUsIF9vcHRpb25zKSB7XG4gICAgcmV0dXJuIFtdO1xuICB9O1xuICBBYnN0cmFjdElucHV0SmF4LnByb3RvdHlwZS5leGVjdXRlRmlsdGVycyA9IGZ1bmN0aW9uIChmaWx0ZXJzLCBtYXRoLCBkb2N1bWVudCwgZGF0YSkge1xuICAgIHZhciBhcmdzID0ge1xuICAgICAgbWF0aDogbWF0aCxcbiAgICAgIGRvY3VtZW50OiBkb2N1bWVudCxcbiAgICAgIGRhdGE6IGRhdGFcbiAgICB9O1xuICAgIGZpbHRlcnMuZXhlY3V0ZShhcmdzKTtcbiAgICByZXR1cm4gYXJncy5kYXRhO1xuICB9O1xuICBBYnN0cmFjdElucHV0SmF4Lk5BTUUgPSAnZ2VuZXJpYyc7XG4gIEFic3RyYWN0SW5wdXRKYXguT1BUSU9OUyA9IHt9O1xuICByZXR1cm4gQWJzdHJhY3RJbnB1dEpheDtcbn0oKTtcbmV4cG9ydHMuQWJzdHJhY3RJbnB1dEpheCA9IEFic3RyYWN0SW5wdXRKYXg7IiwiXCJ1c2Ugc3RyaWN0XCI7XG5cbk9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBcIl9fZXNNb2R1bGVcIiwge1xuICB2YWx1ZTogdHJ1ZVxufSk7XG5leHBvcnRzLlByaW9yaXRpemVkTGlzdCA9IHZvaWQgMDtcbnZhciBQcmlvcml0aXplZExpc3QgPSBmdW5jdGlvbiAoKSB7XG4gIGZ1bmN0aW9uIFByaW9yaXRpemVkTGlzdCgpIHtcbiAgICB0aGlzLml0ZW1zID0gW107XG4gICAgdGhpcy5pdGVtcyA9IFtdO1xuICB9XG4gIFByaW9yaXRpemVkTGlzdC5wcm90b3R5cGVbU3ltYm9sLml0ZXJhdG9yXSA9IGZ1bmN0aW9uICgpIHtcbiAgICB2YXIgaSA9IDA7XG4gICAgdmFyIGl0ZW1zID0gdGhpcy5pdGVtcztcbiAgICByZXR1cm4ge1xuICAgICAgbmV4dDogZnVuY3Rpb24gKCkge1xuICAgICAgICByZXR1cm4ge1xuICAgICAgICAgIHZhbHVlOiBpdGVtc1tpKytdLFxuICAgICAgICAgIGRvbmU6IGkgPiBpdGVtcy5sZW5ndGhcbiAgICAgICAgfTtcbiAgICAgIH1cbiAgICB9O1xuICB9O1xuICBQcmlvcml0aXplZExpc3QucHJvdG90eXBlLmFkZCA9IGZ1bmN0aW9uIChpdGVtLCBwcmlvcml0eSkge1xuICAgIGlmIChwcmlvcml0eSA9PT0gdm9pZCAwKSB7XG4gICAgICBwcmlvcml0eSA9IFByaW9yaXRpemVkTGlzdC5ERUZBVUxUUFJJT1JJVFk7XG4gICAgfVxuICAgIHZhciBpID0gdGhpcy5pdGVtcy5sZW5ndGg7XG4gICAgZG8ge1xuICAgICAgaS0tO1xuICAgIH0gd2hpbGUgKGkgPj0gMCAmJiBwcmlvcml0eSA8IHRoaXMuaXRlbXNbaV0ucHJpb3JpdHkpO1xuICAgIHRoaXMuaXRlbXMuc3BsaWNlKGkgKyAxLCAwLCB7XG4gICAgICBpdGVtOiBpdGVtLFxuICAgICAgcHJpb3JpdHk6IHByaW9yaXR5XG4gICAgfSk7XG4gICAgcmV0dXJuIGl0ZW07XG4gIH07XG4gIFByaW9yaXRpemVkTGlzdC5wcm90b3R5cGUucmVtb3ZlID0gZnVuY3Rpb24gKGl0ZW0pIHtcbiAgICB2YXIgaSA9IHRoaXMuaXRlbXMubGVuZ3RoO1xuICAgIGRvIHtcbiAgICAgIGktLTtcbiAgICB9IHdoaWxlIChpID49IDAgJiYgdGhpcy5pdGVtc1tpXS5pdGVtICE9PSBpdGVtKTtcbiAgICBpZiAoaSA+PSAwKSB7XG4gICAgICB0aGlzLml0ZW1zLnNwbGljZShpLCAxKTtcbiAgICB9XG4gIH07XG4gIFByaW9yaXRpemVkTGlzdC5ERUZBVUxUUFJJT1JJVFkgPSA1O1xuICByZXR1cm4gUHJpb3JpdGl6ZWRMaXN0O1xufSgpO1xuZXhwb3J0cy5Qcmlvcml0aXplZExpc3QgPSBQcmlvcml0aXplZExpc3Q7IiwiXCJ1c2Ugc3RyaWN0XCI7XG5cbnZhciBfX2V4dGVuZHMgPSB0aGlzICYmIHRoaXMuX19leHRlbmRzIHx8IGZ1bmN0aW9uICgpIHtcbiAgdmFyIGV4dGVuZFN0YXRpY3MgPSBmdW5jdGlvbiAoZCwgYikge1xuICAgIGV4dGVuZFN0YXRpY3MgPSBPYmplY3Quc2V0UHJvdG90eXBlT2YgfHwge1xuICAgICAgX19wcm90b19fOiBbXVxuICAgIH0gaW5zdGFuY2VvZiBBcnJheSAmJiBmdW5jdGlvbiAoZCwgYikge1xuICAgICAgZC5fX3Byb3RvX18gPSBiO1xuICAgIH0gfHwgZnVuY3Rpb24gKGQsIGIpIHtcbiAgICAgIGZvciAodmFyIHAgaW4gYikgaWYgKE9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbChiLCBwKSkgZFtwXSA9IGJbcF07XG4gICAgfTtcbiAgICByZXR1cm4gZXh0ZW5kU3RhdGljcyhkLCBiKTtcbiAgfTtcbiAgcmV0dXJuIGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgaWYgKHR5cGVvZiBiICE9PSBcImZ1bmN0aW9uXCIgJiYgYiAhPT0gbnVsbCkgdGhyb3cgbmV3IFR5cGVFcnJvcihcIkNsYXNzIGV4dGVuZHMgdmFsdWUgXCIgKyBTdHJpbmcoYikgKyBcIiBpcyBub3QgYSBjb25zdHJ1Y3RvciBvciBudWxsXCIpO1xuICAgIGV4dGVuZFN0YXRpY3MoZCwgYik7XG4gICAgZnVuY3Rpb24gX18oKSB7XG4gICAgICB0aGlzLmNvbnN0cnVjdG9yID0gZDtcbiAgICB9XG4gICAgZC5wcm90b3R5cGUgPSBiID09PSBudWxsID8gT2JqZWN0LmNyZWF0ZShiKSA6IChfXy5wcm90b3R5cGUgPSBiLnByb3RvdHlwZSwgbmV3IF9fKCkpO1xuICB9O1xufSgpO1xudmFyIF9fdmFsdWVzID0gdGhpcyAmJiB0aGlzLl9fdmFsdWVzIHx8IGZ1bmN0aW9uIChvKSB7XG4gIHZhciBzID0gdHlwZW9mIFN5bWJvbCA9PT0gXCJmdW5jdGlvblwiICYmIFN5bWJvbC5pdGVyYXRvcixcbiAgICBtID0gcyAmJiBvW3NdLFxuICAgIGkgPSAwO1xuICBpZiAobSkgcmV0dXJuIG0uY2FsbChvKTtcbiAgaWYgKG8gJiYgdHlwZW9mIG8ubGVuZ3RoID09PSBcIm51bWJlclwiKSByZXR1cm4ge1xuICAgIG5leHQ6IGZ1bmN0aW9uICgpIHtcbiAgICAgIGlmIChvICYmIGkgPj0gby5sZW5ndGgpIG8gPSB2b2lkIDA7XG4gICAgICByZXR1cm4ge1xuICAgICAgICB2YWx1ZTogbyAmJiBvW2krK10sXG4gICAgICAgIGRvbmU6ICFvXG4gICAgICB9O1xuICAgIH1cbiAgfTtcbiAgdGhyb3cgbmV3IFR5cGVFcnJvcihzID8gXCJPYmplY3QgaXMgbm90IGl0ZXJhYmxlLlwiIDogXCJTeW1ib2wuaXRlcmF0b3IgaXMgbm90IGRlZmluZWQuXCIpO1xufTtcbnZhciBfX3JlYWQgPSB0aGlzICYmIHRoaXMuX19yZWFkIHx8IGZ1bmN0aW9uIChvLCBuKSB7XG4gIHZhciBtID0gdHlwZW9mIFN5bWJvbCA9PT0gXCJmdW5jdGlvblwiICYmIG9bU3ltYm9sLml0ZXJhdG9yXTtcbiAgaWYgKCFtKSByZXR1cm4gbztcbiAgdmFyIGkgPSBtLmNhbGwobyksXG4gICAgcixcbiAgICBhciA9IFtdLFxuICAgIGU7XG4gIHRyeSB7XG4gICAgd2hpbGUgKChuID09PSB2b2lkIDAgfHwgbi0tID4gMCkgJiYgIShyID0gaS5uZXh0KCkpLmRvbmUpIGFyLnB1c2goci52YWx1ZSk7XG4gIH0gY2F0Y2ggKGVycm9yKSB7XG4gICAgZSA9IHtcbiAgICAgIGVycm9yOiBlcnJvclxuICAgIH07XG4gIH0gZmluYWxseSB7XG4gICAgdHJ5IHtcbiAgICAgIGlmIChyICYmICFyLmRvbmUgJiYgKG0gPSBpW1wicmV0dXJuXCJdKSkgbS5jYWxsKGkpO1xuICAgIH0gZmluYWxseSB7XG4gICAgICBpZiAoZSkgdGhyb3cgZS5lcnJvcjtcbiAgICB9XG4gIH1cbiAgcmV0dXJuIGFyO1xufTtcbnZhciBfX3NwcmVhZEFycmF5ID0gdGhpcyAmJiB0aGlzLl9fc3ByZWFkQXJyYXkgfHwgZnVuY3Rpb24gKHRvLCBmcm9tLCBwYWNrKSB7XG4gIGlmIChwYWNrIHx8IGFyZ3VtZW50cy5sZW5ndGggPT09IDIpIGZvciAodmFyIGkgPSAwLCBsID0gZnJvbS5sZW5ndGgsIGFyOyBpIDwgbDsgaSsrKSB7XG4gICAgaWYgKGFyIHx8ICEoaSBpbiBmcm9tKSkge1xuICAgICAgaWYgKCFhcikgYXIgPSBBcnJheS5wcm90b3R5cGUuc2xpY2UuY2FsbChmcm9tLCAwLCBpKTtcbiAgICAgIGFyW2ldID0gZnJvbVtpXTtcbiAgICB9XG4gIH1cbiAgcmV0dXJuIHRvLmNvbmNhdChhciB8fCBBcnJheS5wcm90b3R5cGUuc2xpY2UuY2FsbChmcm9tKSk7XG59O1xuT2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFwiX19lc01vZHVsZVwiLCB7XG4gIHZhbHVlOiB0cnVlXG59KTtcbmV4cG9ydHMuQWJzdHJhY3RNYXRoRG9jdW1lbnQgPSBleHBvcnRzLnJlc2V0QWxsT3B0aW9ucyA9IGV4cG9ydHMucmVzZXRPcHRpb25zID0gZXhwb3J0cy5SZW5kZXJMaXN0ID0gdm9pZCAwO1xudmFyIE9wdGlvbnNfanNfMSA9IHJlcXVpcmUoXCIuLi91dGlsL09wdGlvbnMuanNcIik7XG52YXIgSW5wdXRKYXhfanNfMSA9IHJlcXVpcmUoXCIuL0lucHV0SmF4LmpzXCIpO1xudmFyIE91dHB1dEpheF9qc18xID0gcmVxdWlyZShcIi4vT3V0cHV0SmF4LmpzXCIpO1xudmFyIE1hdGhMaXN0X2pzXzEgPSByZXF1aXJlKFwiLi9NYXRoTGlzdC5qc1wiKTtcbnZhciBNYXRoSXRlbV9qc18xID0gcmVxdWlyZShcIi4vTWF0aEl0ZW0uanNcIik7XG52YXIgTW1sRmFjdG9yeV9qc18xID0gcmVxdWlyZShcIi4uL2NvcmUvTW1sVHJlZS9NbWxGYWN0b3J5LmpzXCIpO1xudmFyIEJpdEZpZWxkX2pzXzEgPSByZXF1aXJlKFwiLi4vdXRpbC9CaXRGaWVsZC5qc1wiKTtcbnZhciBQcmlvcml0aXplZExpc3RfanNfMSA9IHJlcXVpcmUoXCIuLi91dGlsL1ByaW9yaXRpemVkTGlzdC5qc1wiKTtcbnZhciBSZW5kZXJMaXN0ID0gZnVuY3Rpb24gKF9zdXBlcikge1xuICBfX2V4dGVuZHMoUmVuZGVyTGlzdCwgX3N1cGVyKTtcbiAgZnVuY3Rpb24gUmVuZGVyTGlzdCgpIHtcbiAgICByZXR1cm4gX3N1cGVyICE9PSBudWxsICYmIF9zdXBlci5hcHBseSh0aGlzLCBhcmd1bWVudHMpIHx8IHRoaXM7XG4gIH1cbiAgUmVuZGVyTGlzdC5jcmVhdGUgPSBmdW5jdGlvbiAoYWN0aW9ucykge1xuICAgIHZhciBlXzEsIF9hO1xuICAgIHZhciBsaXN0ID0gbmV3IHRoaXMoKTtcbiAgICB0cnkge1xuICAgICAgZm9yICh2YXIgX2IgPSBfX3ZhbHVlcyhPYmplY3Qua2V5cyhhY3Rpb25zKSksIF9jID0gX2IubmV4dCgpOyAhX2MuZG9uZTsgX2MgPSBfYi5uZXh0KCkpIHtcbiAgICAgICAgdmFyIGlkID0gX2MudmFsdWU7XG4gICAgICAgIHZhciBfZCA9IF9fcmVhZCh0aGlzLmFjdGlvbihpZCwgYWN0aW9uc1tpZF0pLCAyKSxcbiAgICAgICAgICBhY3Rpb24gPSBfZFswXSxcbiAgICAgICAgICBwcmlvcml0eSA9IF9kWzFdO1xuICAgICAgICBpZiAocHJpb3JpdHkpIHtcbiAgICAgICAgICBsaXN0LmFkZChhY3Rpb24sIHByaW9yaXR5KTtcbiAgICAgICAgfVxuICAgICAgfVxuICAgIH0gY2F0Y2ggKGVfMV8xKSB7XG4gICAgICBlXzEgPSB7XG4gICAgICAgIGVycm9yOiBlXzFfMVxuICAgICAgfTtcbiAgICB9IGZpbmFsbHkge1xuICAgICAgdHJ5IHtcbiAgICAgICAgaWYgKF9jICYmICFfYy5kb25lICYmIChfYSA9IF9iLnJldHVybikpIF9hLmNhbGwoX2IpO1xuICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgaWYgKGVfMSkgdGhyb3cgZV8xLmVycm9yO1xuICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gbGlzdDtcbiAgfTtcbiAgUmVuZGVyTGlzdC5hY3Rpb24gPSBmdW5jdGlvbiAoaWQsIGFjdGlvbikge1xuICAgIHZhciBfYSwgX2IsIF9jLCBfZDtcbiAgICB2YXIgcmVuZGVyRG9jLCByZW5kZXJNYXRoO1xuICAgIHZhciBjb252ZXJ0ID0gdHJ1ZTtcbiAgICB2YXIgcHJpb3JpdHkgPSBhY3Rpb25bMF07XG4gICAgaWYgKGFjdGlvbi5sZW5ndGggPT09IDEgfHwgdHlwZW9mIGFjdGlvblsxXSA9PT0gJ2Jvb2xlYW4nKSB7XG4gICAgICBhY3Rpb24ubGVuZ3RoID09PSAyICYmIChjb252ZXJ0ID0gYWN0aW9uWzFdKTtcbiAgICAgIF9hID0gX19yZWFkKHRoaXMubWV0aG9kQWN0aW9ucyhpZCksIDIpLCByZW5kZXJEb2MgPSBfYVswXSwgcmVuZGVyTWF0aCA9IF9hWzFdO1xuICAgIH0gZWxzZSBpZiAodHlwZW9mIGFjdGlvblsxXSA9PT0gJ3N0cmluZycpIHtcbiAgICAgIGlmICh0eXBlb2YgYWN0aW9uWzJdID09PSAnc3RyaW5nJykge1xuICAgICAgICBhY3Rpb24ubGVuZ3RoID09PSA0ICYmIChjb252ZXJ0ID0gYWN0aW9uWzNdKTtcbiAgICAgICAgdmFyIF9lID0gX19yZWFkKGFjdGlvbi5zbGljZSgxKSwgMiksXG4gICAgICAgICAgbWV0aG9kMSA9IF9lWzBdLFxuICAgICAgICAgIG1ldGhvZDIgPSBfZVsxXTtcbiAgICAgICAgX2IgPSBfX3JlYWQodGhpcy5tZXRob2RBY3Rpb25zKG1ldGhvZDEsIG1ldGhvZDIpLCAyKSwgcmVuZGVyRG9jID0gX2JbMF0sIHJlbmRlck1hdGggPSBfYlsxXTtcbiAgICAgIH0gZWxzZSB7XG4gICAgICAgIGFjdGlvbi5sZW5ndGggPT09IDMgJiYgKGNvbnZlcnQgPSBhY3Rpb25bMl0pO1xuICAgICAgICBfYyA9IF9fcmVhZCh0aGlzLm1ldGhvZEFjdGlvbnMoYWN0aW9uWzFdKSwgMiksIHJlbmRlckRvYyA9IF9jWzBdLCByZW5kZXJNYXRoID0gX2NbMV07XG4gICAgICB9XG4gICAgfSBlbHNlIHtcbiAgICAgIGFjdGlvbi5sZW5ndGggPT09IDQgJiYgKGNvbnZlcnQgPSBhY3Rpb25bM10pO1xuICAgICAgX2QgPSBfX3JlYWQoYWN0aW9uLnNsaWNlKDEpLCAyKSwgcmVuZGVyRG9jID0gX2RbMF0sIHJlbmRlck1hdGggPSBfZFsxXTtcbiAgICB9XG4gICAgcmV0dXJuIFt7XG4gICAgICBpZDogaWQsXG4gICAgICByZW5kZXJEb2M6IHJlbmRlckRvYyxcbiAgICAgIHJlbmRlck1hdGg6IHJlbmRlck1hdGgsXG4gICAgICBjb252ZXJ0OiBjb252ZXJ0XG4gICAgfSwgcHJpb3JpdHldO1xuICB9O1xuICBSZW5kZXJMaXN0Lm1ldGhvZEFjdGlvbnMgPSBmdW5jdGlvbiAobWV0aG9kMSwgbWV0aG9kMikge1xuICAgIGlmIChtZXRob2QyID09PSB2b2lkIDApIHtcbiAgICAgIG1ldGhvZDIgPSBtZXRob2QxO1xuICAgIH1cbiAgICByZXR1cm4gW2Z1bmN0aW9uIChkb2N1bWVudCkge1xuICAgICAgbWV0aG9kMSAmJiBkb2N1bWVudFttZXRob2QxXSgpO1xuICAgICAgcmV0dXJuIGZhbHNlO1xuICAgIH0sIGZ1bmN0aW9uIChtYXRoLCBkb2N1bWVudCkge1xuICAgICAgbWV0aG9kMiAmJiBtYXRoW21ldGhvZDJdKGRvY3VtZW50KTtcbiAgICAgIHJldHVybiBmYWxzZTtcbiAgICB9XTtcbiAgfTtcbiAgUmVuZGVyTGlzdC5wcm90b3R5cGUucmVuZGVyRG9jID0gZnVuY3Rpb24gKGRvY3VtZW50LCBzdGFydCkge1xuICAgIHZhciBlXzIsIF9hO1xuICAgIGlmIChzdGFydCA9PT0gdm9pZCAwKSB7XG4gICAgICBzdGFydCA9IE1hdGhJdGVtX2pzXzEuU1RBVEUuVU5QUk9DRVNTRUQ7XG4gICAgfVxuICAgIHRyeSB7XG4gICAgICBmb3IgKHZhciBfYiA9IF9fdmFsdWVzKHRoaXMuaXRlbXMpLCBfYyA9IF9iLm5leHQoKTsgIV9jLmRvbmU7IF9jID0gX2IubmV4dCgpKSB7XG4gICAgICAgIHZhciBpdGVtID0gX2MudmFsdWU7XG4gICAgICAgIGlmIChpdGVtLnByaW9yaXR5ID49IHN0YXJ0KSB7XG4gICAgICAgICAgaWYgKGl0ZW0uaXRlbS5yZW5kZXJEb2MoZG9jdW1lbnQpKSByZXR1cm47XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9IGNhdGNoIChlXzJfMSkge1xuICAgICAgZV8yID0ge1xuICAgICAgICBlcnJvcjogZV8yXzFcbiAgICAgIH07XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIHRyeSB7XG4gICAgICAgIGlmIChfYyAmJiAhX2MuZG9uZSAmJiAoX2EgPSBfYi5yZXR1cm4pKSBfYS5jYWxsKF9iKTtcbiAgICAgIH0gZmluYWxseSB7XG4gICAgICAgIGlmIChlXzIpIHRocm93IGVfMi5lcnJvcjtcbiAgICAgIH1cbiAgICB9XG4gIH07XG4gIFJlbmRlckxpc3QucHJvdG90eXBlLnJlbmRlck1hdGggPSBmdW5jdGlvbiAobWF0aCwgZG9jdW1lbnQsIHN0YXJ0KSB7XG4gICAgdmFyIGVfMywgX2E7XG4gICAgaWYgKHN0YXJ0ID09PSB2b2lkIDApIHtcbiAgICAgIHN0YXJ0ID0gTWF0aEl0ZW1fanNfMS5TVEFURS5VTlBST0NFU1NFRDtcbiAgICB9XG4gICAgdHJ5IHtcbiAgICAgIGZvciAodmFyIF9iID0gX192YWx1ZXModGhpcy5pdGVtcyksIF9jID0gX2IubmV4dCgpOyAhX2MuZG9uZTsgX2MgPSBfYi5uZXh0KCkpIHtcbiAgICAgICAgdmFyIGl0ZW0gPSBfYy52YWx1ZTtcbiAgICAgICAgaWYgKGl0ZW0ucHJpb3JpdHkgPj0gc3RhcnQpIHtcbiAgICAgICAgICBpZiAoaXRlbS5pdGVtLnJlbmRlck1hdGgobWF0aCwgZG9jdW1lbnQpKSByZXR1cm47XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9IGNhdGNoIChlXzNfMSkge1xuICAgICAgZV8zID0ge1xuICAgICAgICBlcnJvcjogZV8zXzFcbiAgICAgIH07XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIHRyeSB7XG4gICAgICAgIGlmIChfYyAmJiAhX2MuZG9uZSAmJiAoX2EgPSBfYi5yZXR1cm4pKSBfYS5jYWxsKF9iKTtcbiAgICAgIH0gZmluYWxseSB7XG4gICAgICAgIGlmIChlXzMpIHRocm93IGVfMy5lcnJvcjtcbiAgICAgIH1cbiAgICB9XG4gIH07XG4gIFJlbmRlckxpc3QucHJvdG90eXBlLnJlbmRlckNvbnZlcnQgPSBmdW5jdGlvbiAobWF0aCwgZG9jdW1lbnQsIGVuZCkge1xuICAgIHZhciBlXzQsIF9hO1xuICAgIGlmIChlbmQgPT09IHZvaWQgMCkge1xuICAgICAgZW5kID0gTWF0aEl0ZW1fanNfMS5TVEFURS5MQVNUO1xuICAgIH1cbiAgICB0cnkge1xuICAgICAgZm9yICh2YXIgX2IgPSBfX3ZhbHVlcyh0aGlzLml0ZW1zKSwgX2MgPSBfYi5uZXh0KCk7ICFfYy5kb25lOyBfYyA9IF9iLm5leHQoKSkge1xuICAgICAgICB2YXIgaXRlbSA9IF9jLnZhbHVlO1xuICAgICAgICBpZiAoaXRlbS5wcmlvcml0eSA+IGVuZCkgcmV0dXJuO1xuICAgICAgICBpZiAoaXRlbS5pdGVtLmNvbnZlcnQpIHtcbiAgICAgICAgICBpZiAoaXRlbS5pdGVtLnJlbmRlck1hdGgobWF0aCwgZG9jdW1lbnQpKSByZXR1cm47XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9IGNhdGNoIChlXzRfMSkge1xuICAgICAgZV80ID0ge1xuICAgICAgICBlcnJvcjogZV80XzFcbiAgICAgIH07XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIHRyeSB7XG4gICAgICAgIGlmIChfYyAmJiAhX2MuZG9uZSAmJiAoX2EgPSBfYi5yZXR1cm4pKSBfYS5jYWxsKF9iKTtcbiAgICAgIH0gZmluYWxseSB7XG4gICAgICAgIGlmIChlXzQpIHRocm93IGVfNC5lcnJvcjtcbiAgICAgIH1cbiAgICB9XG4gIH07XG4gIFJlbmRlckxpc3QucHJvdG90eXBlLmZpbmRJRCA9IGZ1bmN0aW9uIChpZCkge1xuICAgIHZhciBlXzUsIF9hO1xuICAgIHRyeSB7XG4gICAgICBmb3IgKHZhciBfYiA9IF9fdmFsdWVzKHRoaXMuaXRlbXMpLCBfYyA9IF9iLm5leHQoKTsgIV9jLmRvbmU7IF9jID0gX2IubmV4dCgpKSB7XG4gICAgICAgIHZhciBpdGVtID0gX2MudmFsdWU7XG4gICAgICAgIGlmIChpdGVtLml0ZW0uaWQgPT09IGlkKSB7XG4gICAgICAgICAgcmV0dXJuIGl0ZW0uaXRlbTtcbiAgICAgICAgfVxuICAgICAgfVxuICAgIH0gY2F0Y2ggKGVfNV8xKSB7XG4gICAgICBlXzUgPSB7XG4gICAgICAgIGVycm9yOiBlXzVfMVxuICAgICAgfTtcbiAgICB9IGZpbmFsbHkge1xuICAgICAgdHJ5IHtcbiAgICAgICAgaWYgKF9jICYmICFfYy5kb25lICYmIChfYSA9IF9iLnJldHVybikpIF9hLmNhbGwoX2IpO1xuICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgaWYgKGVfNSkgdGhyb3cgZV81LmVycm9yO1xuICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4gbnVsbDtcbiAgfTtcbiAgcmV0dXJuIFJlbmRlckxpc3Q7XG59KFByaW9yaXRpemVkTGlzdF9qc18xLlByaW9yaXRpemVkTGlzdCk7XG5leHBvcnRzLlJlbmRlckxpc3QgPSBSZW5kZXJMaXN0O1xuZXhwb3J0cy5yZXNldE9wdGlvbnMgPSB7XG4gIGFsbDogZmFsc2UsXG4gIHByb2Nlc3NlZDogZmFsc2UsXG4gIGlucHV0SmF4OiBudWxsLFxuICBvdXRwdXRKYXg6IG51bGxcbn07XG5leHBvcnRzLnJlc2V0QWxsT3B0aW9ucyA9IHtcbiAgYWxsOiB0cnVlLFxuICBwcm9jZXNzZWQ6IHRydWUsXG4gIGlucHV0SmF4OiBbXSxcbiAgb3V0cHV0SmF4OiBbXVxufTtcbnZhciBEZWZhdWx0SW5wdXRKYXggPSBmdW5jdGlvbiAoX3N1cGVyKSB7XG4gIF9fZXh0ZW5kcyhEZWZhdWx0SW5wdXRKYXgsIF9zdXBlcik7XG4gIGZ1bmN0aW9uIERlZmF1bHRJbnB1dEpheCgpIHtcbiAgICByZXR1cm4gX3N1cGVyICE9PSBudWxsICYmIF9zdXBlci5hcHBseSh0aGlzLCBhcmd1bWVudHMpIHx8IHRoaXM7XG4gIH1cbiAgRGVmYXVsdElucHV0SmF4LnByb3RvdHlwZS5jb21waWxlID0gZnVuY3Rpb24gKF9tYXRoKSB7XG4gICAgcmV0dXJuIG51bGw7XG4gIH07XG4gIHJldHVybiBEZWZhdWx0SW5wdXRKYXg7XG59KElucHV0SmF4X2pzXzEuQWJzdHJhY3RJbnB1dEpheCk7XG52YXIgRGVmYXVsdE91dHB1dEpheCA9IGZ1bmN0aW9uIChfc3VwZXIpIHtcbiAgX19leHRlbmRzKERlZmF1bHRPdXRwdXRKYXgsIF9zdXBlcik7XG4gIGZ1bmN0aW9uIERlZmF1bHRPdXRwdXRKYXgoKSB7XG4gICAgcmV0dXJuIF9zdXBlciAhPT0gbnVsbCAmJiBfc3VwZXIuYXBwbHkodGhpcywgYXJndW1lbnRzKSB8fCB0aGlzO1xuICB9XG4gIERlZmF1bHRPdXRwdXRKYXgucHJvdG90eXBlLnR5cGVzZXQgPSBmdW5jdGlvbiAoX21hdGgsIF9kb2N1bWVudCkge1xuICAgIGlmIChfZG9jdW1lbnQgPT09IHZvaWQgMCkge1xuICAgICAgX2RvY3VtZW50ID0gbnVsbDtcbiAgICB9XG4gICAgcmV0dXJuIG51bGw7XG4gIH07XG4gIERlZmF1bHRPdXRwdXRKYXgucHJvdG90eXBlLmVzY2FwZWQgPSBmdW5jdGlvbiAoX21hdGgsIF9kb2N1bWVudCkge1xuICAgIHJldHVybiBudWxsO1xuICB9O1xuICByZXR1cm4gRGVmYXVsdE91dHB1dEpheDtcbn0oT3V0cHV0SmF4X2pzXzEuQWJzdHJhY3RPdXRwdXRKYXgpO1xudmFyIERlZmF1bHRNYXRoTGlzdCA9IGZ1bmN0aW9uIChfc3VwZXIpIHtcbiAgX19leHRlbmRzKERlZmF1bHRNYXRoTGlzdCwgX3N1cGVyKTtcbiAgZnVuY3Rpb24gRGVmYXVsdE1hdGhMaXN0KCkge1xuICAgIHJldHVybiBfc3VwZXIgIT09IG51bGwgJiYgX3N1cGVyLmFwcGx5KHRoaXMsIGFyZ3VtZW50cykgfHwgdGhpcztcbiAgfVxuICByZXR1cm4gRGVmYXVsdE1hdGhMaXN0O1xufShNYXRoTGlzdF9qc18xLkFic3RyYWN0TWF0aExpc3QpO1xudmFyIERlZmF1bHRNYXRoSXRlbSA9IGZ1bmN0aW9uIChfc3VwZXIpIHtcbiAgX19leHRlbmRzKERlZmF1bHRNYXRoSXRlbSwgX3N1cGVyKTtcbiAgZnVuY3Rpb24gRGVmYXVsdE1hdGhJdGVtKCkge1xuICAgIHJldHVybiBfc3VwZXIgIT09IG51bGwgJiYgX3N1cGVyLmFwcGx5KHRoaXMsIGFyZ3VtZW50cykgfHwgdGhpcztcbiAgfVxuICByZXR1cm4gRGVmYXVsdE1hdGhJdGVtO1xufShNYXRoSXRlbV9qc18xLkFic3RyYWN0TWF0aEl0ZW0pO1xudmFyIEFic3RyYWN0TWF0aERvY3VtZW50ID0gZnVuY3Rpb24gKCkge1xuICBmdW5jdGlvbiBBYnN0cmFjdE1hdGhEb2N1bWVudChkb2N1bWVudCwgYWRhcHRvciwgb3B0aW9ucykge1xuICAgIHZhciBfdGhpcyA9IHRoaXM7XG4gICAgdmFyIENMQVNTID0gdGhpcy5jb25zdHJ1Y3RvcjtcbiAgICB0aGlzLmRvY3VtZW50ID0gZG9jdW1lbnQ7XG4gICAgdGhpcy5vcHRpb25zID0gKDAsIE9wdGlvbnNfanNfMS51c2VyT3B0aW9ucykoKDAsIE9wdGlvbnNfanNfMS5kZWZhdWx0T3B0aW9ucykoe30sIENMQVNTLk9QVElPTlMpLCBvcHRpb25zKTtcbiAgICB0aGlzLm1hdGggPSBuZXcgKHRoaXMub3B0aW9uc1snTWF0aExpc3QnXSB8fCBEZWZhdWx0TWF0aExpc3QpKCk7XG4gICAgdGhpcy5yZW5kZXJBY3Rpb25zID0gUmVuZGVyTGlzdC5jcmVhdGUodGhpcy5vcHRpb25zWydyZW5kZXJBY3Rpb25zJ10pO1xuICAgIHRoaXMucHJvY2Vzc2VkID0gbmV3IEFic3RyYWN0TWF0aERvY3VtZW50LlByb2Nlc3NCaXRzKCk7XG4gICAgdGhpcy5vdXRwdXRKYXggPSB0aGlzLm9wdGlvbnNbJ091dHB1dEpheCddIHx8IG5ldyBEZWZhdWx0T3V0cHV0SmF4KCk7XG4gICAgdmFyIGlucHV0SmF4ID0gdGhpcy5vcHRpb25zWydJbnB1dEpheCddIHx8IFtuZXcgRGVmYXVsdElucHV0SmF4KCldO1xuICAgIGlmICghQXJyYXkuaXNBcnJheShpbnB1dEpheCkpIHtcbiAgICAgIGlucHV0SmF4ID0gW2lucHV0SmF4XTtcbiAgICB9XG4gICAgdGhpcy5pbnB1dEpheCA9IGlucHV0SmF4O1xuICAgIHRoaXMuYWRhcHRvciA9IGFkYXB0b3I7XG4gICAgdGhpcy5vdXRwdXRKYXguc2V0QWRhcHRvcihhZGFwdG9yKTtcbiAgICB0aGlzLmlucHV0SmF4Lm1hcChmdW5jdGlvbiAoamF4KSB7XG4gICAgICByZXR1cm4gamF4LnNldEFkYXB0b3IoYWRhcHRvcik7XG4gICAgfSk7XG4gICAgdGhpcy5tbWxGYWN0b3J5ID0gdGhpcy5vcHRpb25zWydNbWxGYWN0b3J5J10gfHwgbmV3IE1tbEZhY3RvcnlfanNfMS5NbWxGYWN0b3J5KCk7XG4gICAgdGhpcy5pbnB1dEpheC5tYXAoZnVuY3Rpb24gKGpheCkge1xuICAgICAgcmV0dXJuIGpheC5zZXRNbWxGYWN0b3J5KF90aGlzLm1tbEZhY3RvcnkpO1xuICAgIH0pO1xuICAgIHRoaXMub3V0cHV0SmF4LmluaXRpYWxpemUoKTtcbiAgICB0aGlzLmlucHV0SmF4Lm1hcChmdW5jdGlvbiAoamF4KSB7XG4gICAgICByZXR1cm4gamF4LmluaXRpYWxpemUoKTtcbiAgICB9KTtcbiAgfVxuICBPYmplY3QuZGVmaW5lUHJvcGVydHkoQWJzdHJhY3RNYXRoRG9jdW1lbnQucHJvdG90eXBlLCBcImtpbmRcIiwge1xuICAgIGdldDogZnVuY3Rpb24gKCkge1xuICAgICAgcmV0dXJuIHRoaXMuY29uc3RydWN0b3IuS0lORDtcbiAgICB9LFxuICAgIGVudW1lcmFibGU6IGZhbHNlLFxuICAgIGNvbmZpZ3VyYWJsZTogdHJ1ZVxuICB9KTtcbiAgQWJzdHJhY3RNYXRoRG9jdW1lbnQucHJvdG90eXBlLmFkZFJlbmRlckFjdGlvbiA9IGZ1bmN0aW9uIChpZCkge1xuICAgIHZhciBhY3Rpb24gPSBbXTtcbiAgICBmb3IgKHZhciBfaSA9IDE7IF9pIDwgYXJndW1lbnRzLmxlbmd0aDsgX2krKykge1xuICAgICAgYWN0aW9uW19pIC0gMV0gPSBhcmd1bWVudHNbX2ldO1xuICAgIH1cbiAgICB2YXIgX2EgPSBfX3JlYWQoUmVuZGVyTGlzdC5hY3Rpb24oaWQsIGFjdGlvbiksIDIpLFxuICAgICAgZm4gPSBfYVswXSxcbiAgICAgIHAgPSBfYVsxXTtcbiAgICB0aGlzLnJlbmRlckFjdGlvbnMuYWRkKGZuLCBwKTtcbiAgfTtcbiAgQWJzdHJhY3RNYXRoRG9jdW1lbnQucHJvdG90eXBlLnJlbW92ZVJlbmRlckFjdGlvbiA9IGZ1bmN0aW9uIChpZCkge1xuICAgIHZhciBhY3Rpb24gPSB0aGlzLnJlbmRlckFjdGlvbnMuZmluZElEKGlkKTtcbiAgICBpZiAoYWN0aW9uKSB7XG4gICAgICB0aGlzLnJlbmRlckFjdGlvbnMucmVtb3ZlKGFjdGlvbik7XG4gICAgfVxuICB9O1xuICBBYnN0cmFjdE1hdGhEb2N1bWVudC5wcm90b3R5cGUucmVuZGVyID0gZnVuY3Rpb24gKCkge1xuICAgIHRoaXMucmVuZGVyQWN0aW9ucy5yZW5kZXJEb2ModGhpcyk7XG4gICAgcmV0dXJuIHRoaXM7XG4gIH07XG4gIEFic3RyYWN0TWF0aERvY3VtZW50LnByb3RvdHlwZS5yZXJlbmRlciA9IGZ1bmN0aW9uIChzdGFydCkge1xuICAgIGlmIChzdGFydCA9PT0gdm9pZCAwKSB7XG4gICAgICBzdGFydCA9IE1hdGhJdGVtX2pzXzEuU1RBVEUuUkVSRU5ERVI7XG4gICAgfVxuICAgIHRoaXMuc3RhdGUoc3RhcnQgLSAxKTtcbiAgICB0aGlzLnJlbmRlcigpO1xuICAgIHJldHVybiB0aGlzO1xuICB9O1xuICBBYnN0cmFjdE1hdGhEb2N1bWVudC5wcm90b3R5cGUuY29udmVydCA9IGZ1bmN0aW9uIChtYXRoLCBvcHRpb25zKSB7XG4gICAgaWYgKG9wdGlvbnMgPT09IHZvaWQgMCkge1xuICAgICAgb3B0aW9ucyA9IHt9O1xuICAgIH1cbiAgICB2YXIgX2EgPSAoMCwgT3B0aW9uc19qc18xLnVzZXJPcHRpb25zKSh7XG4gICAgICAgIGZvcm1hdDogdGhpcy5pbnB1dEpheFswXS5uYW1lLFxuICAgICAgICBkaXNwbGF5OiB0cnVlLFxuICAgICAgICBlbmQ6IE1hdGhJdGVtX2pzXzEuU1RBVEUuTEFTVCxcbiAgICAgICAgZW06IDE2LFxuICAgICAgICBleDogOCxcbiAgICAgICAgY29udGFpbmVyV2lkdGg6IG51bGwsXG4gICAgICAgIGxpbmVXaWR0aDogMTAwMDAwMCxcbiAgICAgICAgc2NhbGU6IDEsXG4gICAgICAgIGZhbWlseTogJydcbiAgICAgIH0sIG9wdGlvbnMpLFxuICAgICAgZm9ybWF0ID0gX2EuZm9ybWF0LFxuICAgICAgZGlzcGxheSA9IF9hLmRpc3BsYXksXG4gICAgICBlbmQgPSBfYS5lbmQsXG4gICAgICBleCA9IF9hLmV4LFxuICAgICAgZW0gPSBfYS5lbSxcbiAgICAgIGNvbnRhaW5lcldpZHRoID0gX2EuY29udGFpbmVyV2lkdGgsXG4gICAgICBsaW5lV2lkdGggPSBfYS5saW5lV2lkdGgsXG4gICAgICBzY2FsZSA9IF9hLnNjYWxlLFxuICAgICAgZmFtaWx5ID0gX2EuZmFtaWx5O1xuICAgIGlmIChjb250YWluZXJXaWR0aCA9PT0gbnVsbCkge1xuICAgICAgY29udGFpbmVyV2lkdGggPSA4MCAqIGV4O1xuICAgIH1cbiAgICB2YXIgamF4ID0gdGhpcy5pbnB1dEpheC5yZWR1Y2UoZnVuY3Rpb24gKGpheCwgaWpheCkge1xuICAgICAgcmV0dXJuIGlqYXgubmFtZSA9PT0gZm9ybWF0ID8gaWpheCA6IGpheDtcbiAgICB9LCBudWxsKTtcbiAgICB2YXIgbWl0ZW0gPSBuZXcgdGhpcy5vcHRpb25zLk1hdGhJdGVtKG1hdGgsIGpheCwgZGlzcGxheSk7XG4gICAgbWl0ZW0uc3RhcnQubm9kZSA9IHRoaXMuYWRhcHRvci5ib2R5KHRoaXMuZG9jdW1lbnQpO1xuICAgIG1pdGVtLnNldE1ldHJpY3MoZW0sIGV4LCBjb250YWluZXJXaWR0aCwgbGluZVdpZHRoLCBzY2FsZSk7XG4gICAgaWYgKHRoaXMub3V0cHV0SmF4Lm9wdGlvbnMubXRleHRJbmhlcml0Rm9udCkge1xuICAgICAgbWl0ZW0ub3V0cHV0RGF0YS5tdGV4dEZhbWlseSA9IGZhbWlseTtcbiAgICB9XG4gICAgaWYgKHRoaXMub3V0cHV0SmF4Lm9wdGlvbnMubWVycm9ySW5oZXJpdEZvbnQpIHtcbiAgICAgIG1pdGVtLm91dHB1dERhdGEubWVycm9yRmFtaWx5ID0gZmFtaWx5O1xuICAgIH1cbiAgICBtaXRlbS5jb252ZXJ0KHRoaXMsIGVuZCk7XG4gICAgcmV0dXJuIG1pdGVtLnR5cGVzZXRSb290IHx8IG1pdGVtLnJvb3Q7XG4gIH07XG4gIEFic3RyYWN0TWF0aERvY3VtZW50LnByb3RvdHlwZS5maW5kTWF0aCA9IGZ1bmN0aW9uIChfb3B0aW9ucykge1xuICAgIGlmIChfb3B0aW9ucyA9PT0gdm9pZCAwKSB7XG4gICAgICBfb3B0aW9ucyA9IG51bGw7XG4gICAgfVxuICAgIHRoaXMucHJvY2Vzc2VkLnNldCgnZmluZE1hdGgnKTtcbiAgICByZXR1cm4gdGhpcztcbiAgfTtcbiAgQWJzdHJhY3RNYXRoRG9jdW1lbnQucHJvdG90eXBlLmNvbXBpbGUgPSBmdW5jdGlvbiAoKSB7XG4gICAgdmFyIGVfNiwgX2EsIGVfNywgX2I7XG4gICAgaWYgKCF0aGlzLnByb2Nlc3NlZC5pc1NldCgnY29tcGlsZScpKSB7XG4gICAgICB2YXIgcmVjb21waWxlID0gW107XG4gICAgICB0cnkge1xuICAgICAgICBmb3IgKHZhciBfYyA9IF9fdmFsdWVzKHRoaXMubWF0aCksIF9kID0gX2MubmV4dCgpOyAhX2QuZG9uZTsgX2QgPSBfYy5uZXh0KCkpIHtcbiAgICAgICAgICB2YXIgbWF0aCA9IF9kLnZhbHVlO1xuICAgICAgICAgIHRoaXMuY29tcGlsZU1hdGgobWF0aCk7XG4gICAgICAgICAgaWYgKG1hdGguaW5wdXREYXRhLnJlY29tcGlsZSAhPT0gdW5kZWZpbmVkKSB7XG4gICAgICAgICAgICByZWNvbXBpbGUucHVzaChtYXRoKTtcbiAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgIH0gY2F0Y2ggKGVfNl8xKSB7XG4gICAgICAgIGVfNiA9IHtcbiAgICAgICAgICBlcnJvcjogZV82XzFcbiAgICAgICAgfTtcbiAgICAgIH0gZmluYWxseSB7XG4gICAgICAgIHRyeSB7XG4gICAgICAgICAgaWYgKF9kICYmICFfZC5kb25lICYmIChfYSA9IF9jLnJldHVybikpIF9hLmNhbGwoX2MpO1xuICAgICAgICB9IGZpbmFsbHkge1xuICAgICAgICAgIGlmIChlXzYpIHRocm93IGVfNi5lcnJvcjtcbiAgICAgICAgfVxuICAgICAgfVxuICAgICAgdHJ5IHtcbiAgICAgICAgZm9yICh2YXIgcmVjb21waWxlXzEgPSBfX3ZhbHVlcyhyZWNvbXBpbGUpLCByZWNvbXBpbGVfMV8xID0gcmVjb21waWxlXzEubmV4dCgpOyAhcmVjb21waWxlXzFfMS5kb25lOyByZWNvbXBpbGVfMV8xID0gcmVjb21waWxlXzEubmV4dCgpKSB7XG4gICAgICAgICAgdmFyIG1hdGggPSByZWNvbXBpbGVfMV8xLnZhbHVlO1xuICAgICAgICAgIHZhciBkYXRhID0gbWF0aC5pbnB1dERhdGEucmVjb21waWxlO1xuICAgICAgICAgIG1hdGguc3RhdGUoZGF0YS5zdGF0ZSk7XG4gICAgICAgICAgbWF0aC5pbnB1dERhdGEucmVjb21waWxlID0gZGF0YTtcbiAgICAgICAgICB0aGlzLmNvbXBpbGVNYXRoKG1hdGgpO1xuICAgICAgICB9XG4gICAgICB9IGNhdGNoIChlXzdfMSkge1xuICAgICAgICBlXzcgPSB7XG4gICAgICAgICAgZXJyb3I6IGVfN18xXG4gICAgICAgIH07XG4gICAgICB9IGZpbmFsbHkge1xuICAgICAgICB0cnkge1xuICAgICAgICAgIGlmIChyZWNvbXBpbGVfMV8xICYmICFyZWNvbXBpbGVfMV8xLmRvbmUgJiYgKF9iID0gcmVjb21waWxlXzEucmV0dXJuKSkgX2IuY2FsbChyZWNvbXBpbGVfMSk7XG4gICAgICAgIH0gZmluYWxseSB7XG4gICAgICAgICAgaWYgKGVfNykgdGhyb3cgZV83LmVycm9yO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgICB0aGlzLnByb2Nlc3NlZC5zZXQoJ2NvbXBpbGUnKTtcbiAgICB9XG4gICAgcmV0dXJuIHRoaXM7XG4gIH07XG4gIEFic3RyYWN0TWF0aERvY3VtZW50LnByb3RvdHlwZS5jb21waWxlTWF0aCA9IGZ1bmN0aW9uIChtYXRoKSB7XG4gICAgdHJ5IHtcbiAgICAgIG1hdGguY29tcGlsZSh0aGlzKTtcbiAgICB9IGNhdGNoIChlcnIpIHtcbiAgICAgIGlmIChlcnIucmV0cnkgfHwgZXJyLnJlc3RhcnQpIHtcbiAgICAgICAgdGhyb3cgZXJyO1xuICAgICAgfVxuICAgICAgdGhpcy5vcHRpb25zWydjb21waWxlRXJyb3InXSh0aGlzLCBtYXRoLCBlcnIpO1xuICAgICAgbWF0aC5pbnB1dERhdGFbJ2Vycm9yJ10gPSBlcnI7XG4gICAgfVxuICB9O1xuICBBYnN0cmFjdE1hdGhEb2N1bWVudC5wcm90b3R5cGUuY29tcGlsZUVycm9yID0gZnVuY3Rpb24gKG1hdGgsIGVycikge1xuICAgIG1hdGgucm9vdCA9IHRoaXMubW1sRmFjdG9yeS5jcmVhdGUoJ21hdGgnLCBudWxsLCBbdGhpcy5tbWxGYWN0b3J5LmNyZWF0ZSgnbWVycm9yJywge1xuICAgICAgJ2RhdGEtbWp4LWVycm9yJzogZXJyLm1lc3NhZ2UsXG4gICAgICB0aXRsZTogZXJyLm1lc3NhZ2VcbiAgICB9LCBbdGhpcy5tbWxGYWN0b3J5LmNyZWF0ZSgnbXRleHQnLCBudWxsLCBbdGhpcy5tbWxGYWN0b3J5LmNyZWF0ZSgndGV4dCcpLnNldFRleHQoJ01hdGggaW5wdXQgZXJyb3InKV0pXSldKTtcbiAgICBpZiAobWF0aC5kaXNwbGF5KSB7XG4gICAgICBtYXRoLnJvb3QuYXR0cmlidXRlcy5zZXQoJ2Rpc3BsYXknLCAnYmxvY2snKTtcbiAgICB9XG4gICAgbWF0aC5pbnB1dERhdGEuZXJyb3IgPSBlcnIubWVzc2FnZTtcbiAgfTtcbiAgQWJzdHJhY3RNYXRoRG9jdW1lbnQucHJvdG90eXBlLnR5cGVzZXQgPSBmdW5jdGlvbiAoKSB7XG4gICAgdmFyIGVfOCwgX2E7XG4gICAgaWYgKCF0aGlzLnByb2Nlc3NlZC5pc1NldCgndHlwZXNldCcpKSB7XG4gICAgICB0cnkge1xuICAgICAgICBmb3IgKHZhciBfYiA9IF9fdmFsdWVzKHRoaXMubWF0aCksIF9jID0gX2IubmV4dCgpOyAhX2MuZG9uZTsgX2MgPSBfYi5uZXh0KCkpIHtcbiAgICAgICAgICB2YXIgbWF0aCA9IF9jLnZhbHVlO1xuICAgICAgICAgIHRyeSB7XG4gICAgICAgICAgICBtYXRoLnR5cGVzZXQodGhpcyk7XG4gICAgICAgICAgfSBjYXRjaCAoZXJyKSB7XG4gICAgICAgICAgICBpZiAoZXJyLnJldHJ5IHx8IGVyci5yZXN0YXJ0KSB7XG4gICAgICAgICAgICAgIHRocm93IGVycjtcbiAgICAgICAgICAgIH1cbiAgICAgICAgICAgIHRoaXMub3B0aW9uc1sndHlwZXNldEVycm9yJ10odGhpcywgbWF0aCwgZXJyKTtcbiAgICAgICAgICAgIG1hdGgub3V0cHV0RGF0YVsnZXJyb3InXSA9IGVycjtcbiAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgIH0gY2F0Y2ggKGVfOF8xKSB7XG4gICAgICAgIGVfOCA9IHtcbiAgICAgICAgICBlcnJvcjogZV84XzFcbiAgICAgICAgfTtcbiAgICAgIH0gZmluYWxseSB7XG4gICAgICAgIHRyeSB7XG4gICAgICAgICAgaWYgKF9jICYmICFfYy5kb25lICYmIChfYSA9IF9iLnJldHVybikpIF9hLmNhbGwoX2IpO1xuICAgICAgICB9IGZpbmFsbHkge1xuICAgICAgICAgIGlmIChlXzgpIHRocm93IGVfOC5lcnJvcjtcbiAgICAgICAgfVxuICAgICAgfVxuICAgICAgdGhpcy5wcm9jZXNzZWQuc2V0KCd0eXBlc2V0Jyk7XG4gICAgfVxuICAgIHJldHVybiB0aGlzO1xuICB9O1xuICBBYnN0cmFjdE1hdGhEb2N1bWVudC5wcm90b3R5cGUudHlwZXNldEVycm9yID0gZnVuY3Rpb24gKG1hdGgsIGVycikge1xuICAgIG1hdGgudHlwZXNldFJvb3QgPSB0aGlzLmFkYXB0b3Iubm9kZSgnbWp4LWNvbnRhaW5lcicsIHtcbiAgICAgIGNsYXNzOiAnTWF0aEpheCBtangtb3V0cHV0LWVycm9yJyxcbiAgICAgIGpheDogdGhpcy5vdXRwdXRKYXgubmFtZVxuICAgIH0sIFt0aGlzLmFkYXB0b3Iubm9kZSgnc3BhbicsIHtcbiAgICAgICdkYXRhLW1qeC1lcnJvcic6IGVyci5tZXNzYWdlLFxuICAgICAgdGl0bGU6IGVyci5tZXNzYWdlLFxuICAgICAgc3R5bGU6IHtcbiAgICAgICAgY29sb3I6ICdyZWQnLFxuICAgICAgICAnYmFja2dyb3VuZC1jb2xvcic6ICd5ZWxsb3cnLFxuICAgICAgICAnbGluZS1oZWlnaHQnOiAnbm9ybWFsJ1xuICAgICAgfVxuICAgIH0sIFt0aGlzLmFkYXB0b3IudGV4dCgnTWF0aCBvdXRwdXQgZXJyb3InKV0pXSk7XG4gICAgaWYgKG1hdGguZGlzcGxheSkge1xuICAgICAgdGhpcy5hZGFwdG9yLnNldEF0dHJpYnV0ZXMobWF0aC50eXBlc2V0Um9vdCwge1xuICAgICAgICBzdHlsZToge1xuICAgICAgICAgIGRpc3BsYXk6ICdibG9jaycsXG4gICAgICAgICAgbWFyZ2luOiAnMWVtIDAnLFxuICAgICAgICAgICd0ZXh0LWFsaWduJzogJ2NlbnRlcidcbiAgICAgICAgfVxuICAgICAgfSk7XG4gICAgfVxuICAgIG1hdGgub3V0cHV0RGF0YS5lcnJvciA9IGVyci5tZXNzYWdlO1xuICB9O1xuICBBYnN0cmFjdE1hdGhEb2N1bWVudC5wcm90b3R5cGUuZ2V0TWV0cmljcyA9IGZ1bmN0aW9uICgpIHtcbiAgICBpZiAoIXRoaXMucHJvY2Vzc2VkLmlzU2V0KCdnZXRNZXRyaWNzJykpIHtcbiAgICAgIHRoaXMub3V0cHV0SmF4LmdldE1ldHJpY3ModGhpcyk7XG4gICAgICB0aGlzLnByb2Nlc3NlZC5zZXQoJ2dldE1ldHJpY3MnKTtcbiAgICB9XG4gICAgcmV0dXJuIHRoaXM7XG4gIH07XG4gIEFic3RyYWN0TWF0aERvY3VtZW50LnByb3RvdHlwZS51cGRhdGVEb2N1bWVudCA9IGZ1bmN0aW9uICgpIHtcbiAgICB2YXIgZV85LCBfYTtcbiAgICBpZiAoIXRoaXMucHJvY2Vzc2VkLmlzU2V0KCd1cGRhdGVEb2N1bWVudCcpKSB7XG4gICAgICB0cnkge1xuICAgICAgICBmb3IgKHZhciBfYiA9IF9fdmFsdWVzKHRoaXMubWF0aC5yZXZlcnNlZCgpKSwgX2MgPSBfYi5uZXh0KCk7ICFfYy5kb25lOyBfYyA9IF9iLm5leHQoKSkge1xuICAgICAgICAgIHZhciBtYXRoID0gX2MudmFsdWU7XG4gICAgICAgICAgbWF0aC51cGRhdGVEb2N1bWVudCh0aGlzKTtcbiAgICAgICAgfVxuICAgICAgfSBjYXRjaCAoZV85XzEpIHtcbiAgICAgICAgZV85ID0ge1xuICAgICAgICAgIGVycm9yOiBlXzlfMVxuICAgICAgICB9O1xuICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgdHJ5IHtcbiAgICAgICAgICBpZiAoX2MgJiYgIV9jLmRvbmUgJiYgKF9hID0gX2IucmV0dXJuKSkgX2EuY2FsbChfYik7XG4gICAgICAgIH0gZmluYWxseSB7XG4gICAgICAgICAgaWYgKGVfOSkgdGhyb3cgZV85LmVycm9yO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgICB0aGlzLnByb2Nlc3NlZC5zZXQoJ3VwZGF0ZURvY3VtZW50Jyk7XG4gICAgfVxuICAgIHJldHVybiB0aGlzO1xuICB9O1xuICBBYnN0cmFjdE1hdGhEb2N1bWVudC5wcm90b3R5cGUucmVtb3ZlRnJvbURvY3VtZW50ID0gZnVuY3Rpb24gKF9yZXN0b3JlKSB7XG4gICAgaWYgKF9yZXN0b3JlID09PSB2b2lkIDApIHtcbiAgICAgIF9yZXN0b3JlID0gZmFsc2U7XG4gICAgfVxuICAgIHJldHVybiB0aGlzO1xuICB9O1xuICBBYnN0cmFjdE1hdGhEb2N1bWVudC5wcm90b3R5cGUuc3RhdGUgPSBmdW5jdGlvbiAoc3RhdGUsIHJlc3RvcmUpIHtcbiAgICB2YXIgZV8xMCwgX2E7XG4gICAgaWYgKHJlc3RvcmUgPT09IHZvaWQgMCkge1xuICAgICAgcmVzdG9yZSA9IGZhbHNlO1xuICAgIH1cbiAgICB0cnkge1xuICAgICAgZm9yICh2YXIgX2IgPSBfX3ZhbHVlcyh0aGlzLm1hdGgpLCBfYyA9IF9iLm5leHQoKTsgIV9jLmRvbmU7IF9jID0gX2IubmV4dCgpKSB7XG4gICAgICAgIHZhciBtYXRoID0gX2MudmFsdWU7XG4gICAgICAgIG1hdGguc3RhdGUoc3RhdGUsIHJlc3RvcmUpO1xuICAgICAgfVxuICAgIH0gY2F0Y2ggKGVfMTBfMSkge1xuICAgICAgZV8xMCA9IHtcbiAgICAgICAgZXJyb3I6IGVfMTBfMVxuICAgICAgfTtcbiAgICB9IGZpbmFsbHkge1xuICAgICAgdHJ5IHtcbiAgICAgICAgaWYgKF9jICYmICFfYy5kb25lICYmIChfYSA9IF9iLnJldHVybikpIF9hLmNhbGwoX2IpO1xuICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgaWYgKGVfMTApIHRocm93IGVfMTAuZXJyb3I7XG4gICAgICB9XG4gICAgfVxuICAgIGlmIChzdGF0ZSA8IE1hdGhJdGVtX2pzXzEuU1RBVEUuSU5TRVJURUQpIHtcbiAgICAgIHRoaXMucHJvY2Vzc2VkLmNsZWFyKCd1cGRhdGVEb2N1bWVudCcpO1xuICAgIH1cbiAgICBpZiAoc3RhdGUgPCBNYXRoSXRlbV9qc18xLlNUQVRFLlRZUEVTRVQpIHtcbiAgICAgIHRoaXMucHJvY2Vzc2VkLmNsZWFyKCd0eXBlc2V0Jyk7XG4gICAgICB0aGlzLnByb2Nlc3NlZC5jbGVhcignZ2V0TWV0cmljcycpO1xuICAgIH1cbiAgICBpZiAoc3RhdGUgPCBNYXRoSXRlbV9qc18xLlNUQVRFLkNPTVBJTEVEKSB7XG4gICAgICB0aGlzLnByb2Nlc3NlZC5jbGVhcignY29tcGlsZScpO1xuICAgIH1cbiAgICByZXR1cm4gdGhpcztcbiAgfTtcbiAgQWJzdHJhY3RNYXRoRG9jdW1lbnQucHJvdG90eXBlLnJlc2V0ID0gZnVuY3Rpb24gKG9wdGlvbnMpIHtcbiAgICB2YXIgX2E7XG4gICAgaWYgKG9wdGlvbnMgPT09IHZvaWQgMCkge1xuICAgICAgb3B0aW9ucyA9IHtcbiAgICAgICAgcHJvY2Vzc2VkOiB0cnVlXG4gICAgICB9O1xuICAgIH1cbiAgICBvcHRpb25zID0gKDAsIE9wdGlvbnNfanNfMS51c2VyT3B0aW9ucykoT2JqZWN0LmFzc2lnbih7fSwgZXhwb3J0cy5yZXNldE9wdGlvbnMpLCBvcHRpb25zKTtcbiAgICBvcHRpb25zLmFsbCAmJiBPYmplY3QuYXNzaWduKG9wdGlvbnMsIGV4cG9ydHMucmVzZXRBbGxPcHRpb25zKTtcbiAgICBvcHRpb25zLnByb2Nlc3NlZCAmJiB0aGlzLnByb2Nlc3NlZC5yZXNldCgpO1xuICAgIG9wdGlvbnMuaW5wdXRKYXggJiYgdGhpcy5pbnB1dEpheC5mb3JFYWNoKGZ1bmN0aW9uIChqYXgpIHtcbiAgICAgIHJldHVybiBqYXgucmVzZXQuYXBwbHkoamF4LCBfX3NwcmVhZEFycmF5KFtdLCBfX3JlYWQob3B0aW9ucy5pbnB1dEpheCksIGZhbHNlKSk7XG4gICAgfSk7XG4gICAgb3B0aW9ucy5vdXRwdXRKYXggJiYgKF9hID0gdGhpcy5vdXRwdXRKYXgpLnJlc2V0LmFwcGx5KF9hLCBfX3NwcmVhZEFycmF5KFtdLCBfX3JlYWQob3B0aW9ucy5vdXRwdXRKYXgpLCBmYWxzZSkpO1xuICAgIHJldHVybiB0aGlzO1xuICB9O1xuICBBYnN0cmFjdE1hdGhEb2N1bWVudC5wcm90b3R5cGUuY2xlYXIgPSBmdW5jdGlvbiAoKSB7XG4gICAgdGhpcy5yZXNldCgpO1xuICAgIHRoaXMubWF0aC5jbGVhcigpO1xuICAgIHJldHVybiB0aGlzO1xuICB9O1xuICBBYnN0cmFjdE1hdGhEb2N1bWVudC5wcm90b3R5cGUuY29uY2F0ID0gZnVuY3Rpb24gKGxpc3QpIHtcbiAgICB0aGlzLm1hdGgubWVyZ2UobGlzdCk7XG4gICAgcmV0dXJuIHRoaXM7XG4gIH07XG4gIEFic3RyYWN0TWF0aERvY3VtZW50LnByb3RvdHlwZS5jbGVhck1hdGhJdGVtc1dpdGhpbiA9IGZ1bmN0aW9uIChjb250YWluZXJzKSB7XG4gICAgdmFyIF9hO1xuICAgIHZhciBpdGVtcyA9IHRoaXMuZ2V0TWF0aEl0ZW1zV2l0aGluKGNvbnRhaW5lcnMpO1xuICAgIChfYSA9IHRoaXMubWF0aCkucmVtb3ZlLmFwcGx5KF9hLCBfX3NwcmVhZEFycmF5KFtdLCBfX3JlYWQoaXRlbXMpLCBmYWxzZSkpO1xuICAgIHJldHVybiBpdGVtcztcbiAgfTtcbiAgQWJzdHJhY3RNYXRoRG9jdW1lbnQucHJvdG90eXBlLmdldE1hdGhJdGVtc1dpdGhpbiA9IGZ1bmN0aW9uIChlbGVtZW50cykge1xuICAgIHZhciBlXzExLCBfYSwgZV8xMiwgX2I7XG4gICAgaWYgKCFBcnJheS5pc0FycmF5KGVsZW1lbnRzKSkge1xuICAgICAgZWxlbWVudHMgPSBbZWxlbWVudHNdO1xuICAgIH1cbiAgICB2YXIgYWRhcHRvciA9IHRoaXMuYWRhcHRvcjtcbiAgICB2YXIgaXRlbXMgPSBbXTtcbiAgICB2YXIgY29udGFpbmVycyA9IGFkYXB0b3IuZ2V0RWxlbWVudHMoZWxlbWVudHMsIHRoaXMuZG9jdW1lbnQpO1xuICAgIHRyeSB7XG4gICAgICBJVEVNUzogZm9yICh2YXIgX2MgPSBfX3ZhbHVlcyh0aGlzLm1hdGgpLCBfZCA9IF9jLm5leHQoKTsgIV9kLmRvbmU7IF9kID0gX2MubmV4dCgpKSB7XG4gICAgICAgIHZhciBpdGVtID0gX2QudmFsdWU7XG4gICAgICAgIHRyeSB7XG4gICAgICAgICAgZm9yICh2YXIgY29udGFpbmVyc18xID0gKGVfMTIgPSB2b2lkIDAsIF9fdmFsdWVzKGNvbnRhaW5lcnMpKSwgY29udGFpbmVyc18xXzEgPSBjb250YWluZXJzXzEubmV4dCgpOyAhY29udGFpbmVyc18xXzEuZG9uZTsgY29udGFpbmVyc18xXzEgPSBjb250YWluZXJzXzEubmV4dCgpKSB7XG4gICAgICAgICAgICB2YXIgY29udGFpbmVyID0gY29udGFpbmVyc18xXzEudmFsdWU7XG4gICAgICAgICAgICBpZiAoaXRlbS5zdGFydC5ub2RlICYmIGFkYXB0b3IuY29udGFpbnMoY29udGFpbmVyLCBpdGVtLnN0YXJ0Lm5vZGUpKSB7XG4gICAgICAgICAgICAgIGl0ZW1zLnB1c2goaXRlbSk7XG4gICAgICAgICAgICAgIGNvbnRpbnVlIElURU1TO1xuICAgICAgICAgICAgfVxuICAgICAgICAgIH1cbiAgICAgICAgfSBjYXRjaCAoZV8xMl8xKSB7XG4gICAgICAgICAgZV8xMiA9IHtcbiAgICAgICAgICAgIGVycm9yOiBlXzEyXzFcbiAgICAgICAgICB9O1xuICAgICAgICB9IGZpbmFsbHkge1xuICAgICAgICAgIHRyeSB7XG4gICAgICAgICAgICBpZiAoY29udGFpbmVyc18xXzEgJiYgIWNvbnRhaW5lcnNfMV8xLmRvbmUgJiYgKF9iID0gY29udGFpbmVyc18xLnJldHVybikpIF9iLmNhbGwoY29udGFpbmVyc18xKTtcbiAgICAgICAgICB9IGZpbmFsbHkge1xuICAgICAgICAgICAgaWYgKGVfMTIpIHRocm93IGVfMTIuZXJyb3I7XG4gICAgICAgICAgfVxuICAgICAgICB9XG4gICAgICB9XG4gICAgfSBjYXRjaCAoZV8xMV8xKSB7XG4gICAgICBlXzExID0ge1xuICAgICAgICBlcnJvcjogZV8xMV8xXG4gICAgICB9O1xuICAgIH0gZmluYWxseSB7XG4gICAgICB0cnkge1xuICAgICAgICBpZiAoX2QgJiYgIV9kLmRvbmUgJiYgKF9hID0gX2MucmV0dXJuKSkgX2EuY2FsbChfYyk7XG4gICAgICB9IGZpbmFsbHkge1xuICAgICAgICBpZiAoZV8xMSkgdGhyb3cgZV8xMS5lcnJvcjtcbiAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIGl0ZW1zO1xuICB9O1xuICBBYnN0cmFjdE1hdGhEb2N1bWVudC5LSU5EID0gJ01hdGhEb2N1bWVudCc7XG4gIEFic3RyYWN0TWF0aERvY3VtZW50Lk9QVElPTlMgPSB7XG4gICAgT3V0cHV0SmF4OiBudWxsLFxuICAgIElucHV0SmF4OiBudWxsLFxuICAgIE1tbEZhY3Rvcnk6IG51bGwsXG4gICAgTWF0aExpc3Q6IERlZmF1bHRNYXRoTGlzdCxcbiAgICBNYXRoSXRlbTogRGVmYXVsdE1hdGhJdGVtLFxuICAgIGNvbXBpbGVFcnJvcjogZnVuY3Rpb24gKGRvYywgbWF0aCwgZXJyKSB7XG4gICAgICBkb2MuY29tcGlsZUVycm9yKG1hdGgsIGVycik7XG4gICAgfSxcbiAgICB0eXBlc2V0RXJyb3I6IGZ1bmN0aW9uIChkb2MsIG1hdGgsIGVycikge1xuICAgICAgZG9jLnR5cGVzZXRFcnJvcihtYXRoLCBlcnIpO1xuICAgIH0sXG4gICAgcmVuZGVyQWN0aW9uczogKDAsIE9wdGlvbnNfanNfMS5leHBhbmRhYmxlKSh7XG4gICAgICBmaW5kOiBbTWF0aEl0ZW1fanNfMS5TVEFURS5GSU5ETUFUSCwgJ2ZpbmRNYXRoJywgJycsIGZhbHNlXSxcbiAgICAgIGNvbXBpbGU6IFtNYXRoSXRlbV9qc18xLlNUQVRFLkNPTVBJTEVEXSxcbiAgICAgIG1ldHJpY3M6IFtNYXRoSXRlbV9qc18xLlNUQVRFLk1FVFJJQ1MsICdnZXRNZXRyaWNzJywgJycsIGZhbHNlXSxcbiAgICAgIHR5cGVzZXQ6IFtNYXRoSXRlbV9qc18xLlNUQVRFLlRZUEVTRVRdLFxuICAgICAgdXBkYXRlOiBbTWF0aEl0ZW1fanNfMS5TVEFURS5JTlNFUlRFRCwgJ3VwZGF0ZURvY3VtZW50JywgZmFsc2VdXG4gICAgfSlcbiAgfTtcbiAgQWJzdHJhY3RNYXRoRG9jdW1lbnQuUHJvY2Vzc0JpdHMgPSAoMCwgQml0RmllbGRfanNfMS5CaXRGaWVsZENsYXNzKSgnZmluZE1hdGgnLCAnY29tcGlsZScsICdnZXRNZXRyaWNzJywgJ3R5cGVzZXQnLCAndXBkYXRlRG9jdW1lbnQnKTtcbiAgcmV0dXJuIEFic3RyYWN0TWF0aERvY3VtZW50O1xufSgpO1xuZXhwb3J0cy5BYnN0cmFjdE1hdGhEb2N1bWVudCA9IEFic3RyYWN0TWF0aERvY3VtZW50OyIsIlwidXNlIHN0cmljdFwiO1xuXG52YXIgX19leHRlbmRzID0gdGhpcyAmJiB0aGlzLl9fZXh0ZW5kcyB8fCBmdW5jdGlvbiAoKSB7XG4gIHZhciBleHRlbmRTdGF0aWNzID0gZnVuY3Rpb24gKGQsIGIpIHtcbiAgICBleHRlbmRTdGF0aWNzID0gT2JqZWN0LnNldFByb3RvdHlwZU9mIHx8IHtcbiAgICAgIF9fcHJvdG9fXzogW11cbiAgICB9IGluc3RhbmNlb2YgQXJyYXkgJiYgZnVuY3Rpb24gKGQsIGIpIHtcbiAgICAgIGQuX19wcm90b19fID0gYjtcbiAgICB9IHx8IGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgICBmb3IgKHZhciBwIGluIGIpIGlmIChPYmplY3QucHJvdG90eXBlLmhhc093blByb3BlcnR5LmNhbGwoYiwgcCkpIGRbcF0gPSBiW3BdO1xuICAgIH07XG4gICAgcmV0dXJuIGV4dGVuZFN0YXRpY3MoZCwgYik7XG4gIH07XG4gIHJldHVybiBmdW5jdGlvbiAoZCwgYikge1xuICAgIGlmICh0eXBlb2YgYiAhPT0gXCJmdW5jdGlvblwiICYmIGIgIT09IG51bGwpIHRocm93IG5ldyBUeXBlRXJyb3IoXCJDbGFzcyBleHRlbmRzIHZhbHVlIFwiICsgU3RyaW5nKGIpICsgXCIgaXMgbm90IGEgY29uc3RydWN0b3Igb3IgbnVsbFwiKTtcbiAgICBleHRlbmRTdGF0aWNzKGQsIGIpO1xuICAgIGZ1bmN0aW9uIF9fKCkge1xuICAgICAgdGhpcy5jb25zdHJ1Y3RvciA9IGQ7XG4gICAgfVxuICAgIGQucHJvdG90eXBlID0gYiA9PT0gbnVsbCA/IE9iamVjdC5jcmVhdGUoYikgOiAoX18ucHJvdG90eXBlID0gYi5wcm90b3R5cGUsIG5ldyBfXygpKTtcbiAgfTtcbn0oKTtcbnZhciBfX2Fzc2lnbiA9IHRoaXMgJiYgdGhpcy5fX2Fzc2lnbiB8fCBmdW5jdGlvbiAoKSB7XG4gIF9fYXNzaWduID0gT2JqZWN0LmFzc2lnbiB8fCBmdW5jdGlvbiAodCkge1xuICAgIGZvciAodmFyIHMsIGkgPSAxLCBuID0gYXJndW1lbnRzLmxlbmd0aDsgaSA8IG47IGkrKykge1xuICAgICAgcyA9IGFyZ3VtZW50c1tpXTtcbiAgICAgIGZvciAodmFyIHAgaW4gcykgaWYgKE9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbChzLCBwKSkgdFtwXSA9IHNbcF07XG4gICAgfVxuICAgIHJldHVybiB0O1xuICB9O1xuICByZXR1cm4gX19hc3NpZ24uYXBwbHkodGhpcywgYXJndW1lbnRzKTtcbn07XG52YXIgX19yZWFkID0gdGhpcyAmJiB0aGlzLl9fcmVhZCB8fCBmdW5jdGlvbiAobywgbikge1xuICB2YXIgbSA9IHR5cGVvZiBTeW1ib2wgPT09IFwiZnVuY3Rpb25cIiAmJiBvW1N5bWJvbC5pdGVyYXRvcl07XG4gIGlmICghbSkgcmV0dXJuIG87XG4gIHZhciBpID0gbS5jYWxsKG8pLFxuICAgIHIsXG4gICAgYXIgPSBbXSxcbiAgICBlO1xuICB0cnkge1xuICAgIHdoaWxlICgobiA9PT0gdm9pZCAwIHx8IG4tLSA+IDApICYmICEociA9IGkubmV4dCgpKS5kb25lKSBhci5wdXNoKHIudmFsdWUpO1xuICB9IGNhdGNoIChlcnJvcikge1xuICAgIGUgPSB7XG4gICAgICBlcnJvcjogZXJyb3JcbiAgICB9O1xuICB9IGZpbmFsbHkge1xuICAgIHRyeSB7XG4gICAgICBpZiAociAmJiAhci5kb25lICYmIChtID0gaVtcInJldHVyblwiXSkpIG0uY2FsbChpKTtcbiAgICB9IGZpbmFsbHkge1xuICAgICAgaWYgKGUpIHRocm93IGUuZXJyb3I7XG4gICAgfVxuICB9XG4gIHJldHVybiBhcjtcbn07XG52YXIgX192YWx1ZXMgPSB0aGlzICYmIHRoaXMuX192YWx1ZXMgfHwgZnVuY3Rpb24gKG8pIHtcbiAgdmFyIHMgPSB0eXBlb2YgU3ltYm9sID09PSBcImZ1bmN0aW9uXCIgJiYgU3ltYm9sLml0ZXJhdG9yLFxuICAgIG0gPSBzICYmIG9bc10sXG4gICAgaSA9IDA7XG4gIGlmIChtKSByZXR1cm4gbS5jYWxsKG8pO1xuICBpZiAobyAmJiB0eXBlb2Ygby5sZW5ndGggPT09IFwibnVtYmVyXCIpIHJldHVybiB7XG4gICAgbmV4dDogZnVuY3Rpb24gKCkge1xuICAgICAgaWYgKG8gJiYgaSA+PSBvLmxlbmd0aCkgbyA9IHZvaWQgMDtcbiAgICAgIHJldHVybiB7XG4gICAgICAgIHZhbHVlOiBvICYmIG9baSsrXSxcbiAgICAgICAgZG9uZTogIW9cbiAgICAgIH07XG4gICAgfVxuICB9O1xuICB0aHJvdyBuZXcgVHlwZUVycm9yKHMgPyBcIk9iamVjdCBpcyBub3QgaXRlcmFibGUuXCIgOiBcIlN5bWJvbC5pdGVyYXRvciBpcyBub3QgZGVmaW5lZC5cIik7XG59O1xuT2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFwiX19lc01vZHVsZVwiLCB7XG4gIHZhbHVlOiB0cnVlXG59KTtcbmV4cG9ydHMuSFRNTERvY3VtZW50ID0gdm9pZCAwO1xudmFyIE1hdGhEb2N1bWVudF9qc18xID0gcmVxdWlyZShcIi4uLy4uL2NvcmUvTWF0aERvY3VtZW50LmpzXCIpO1xudmFyIE9wdGlvbnNfanNfMSA9IHJlcXVpcmUoXCIuLi8uLi91dGlsL09wdGlvbnMuanNcIik7XG52YXIgSFRNTE1hdGhJdGVtX2pzXzEgPSByZXF1aXJlKFwiLi9IVE1MTWF0aEl0ZW0uanNcIik7XG52YXIgSFRNTE1hdGhMaXN0X2pzXzEgPSByZXF1aXJlKFwiLi9IVE1MTWF0aExpc3QuanNcIik7XG52YXIgSFRNTERvbVN0cmluZ3NfanNfMSA9IHJlcXVpcmUoXCIuL0hUTUxEb21TdHJpbmdzLmpzXCIpO1xudmFyIE1hdGhJdGVtX2pzXzEgPSByZXF1aXJlKFwiLi4vLi4vY29yZS9NYXRoSXRlbS5qc1wiKTtcbnZhciBIVE1MRG9jdW1lbnQgPSBmdW5jdGlvbiAoX3N1cGVyKSB7XG4gIF9fZXh0ZW5kcyhIVE1MRG9jdW1lbnQsIF9zdXBlcik7XG4gIGZ1bmN0aW9uIEhUTUxEb2N1bWVudChkb2N1bWVudCwgYWRhcHRvciwgb3B0aW9ucykge1xuICAgIHZhciBfdGhpcyA9IHRoaXM7XG4gICAgdmFyIF9hID0gX19yZWFkKCgwLCBPcHRpb25zX2pzXzEuc2VwYXJhdGVPcHRpb25zKShvcHRpb25zLCBIVE1MRG9tU3RyaW5nc19qc18xLkhUTUxEb21TdHJpbmdzLk9QVElPTlMpLCAyKSxcbiAgICAgIGh0bWwgPSBfYVswXSxcbiAgICAgIGRvbSA9IF9hWzFdO1xuICAgIF90aGlzID0gX3N1cGVyLmNhbGwodGhpcywgZG9jdW1lbnQsIGFkYXB0b3IsIGh0bWwpIHx8IHRoaXM7XG4gICAgX3RoaXMuZG9tU3RyaW5ncyA9IF90aGlzLm9wdGlvbnNbJ0RvbVN0cmluZ3MnXSB8fCBuZXcgSFRNTERvbVN0cmluZ3NfanNfMS5IVE1MRG9tU3RyaW5ncyhkb20pO1xuICAgIF90aGlzLmRvbVN0cmluZ3MuYWRhcHRvciA9IGFkYXB0b3I7XG4gICAgX3RoaXMuc3R5bGVzID0gW107XG4gICAgcmV0dXJuIF90aGlzO1xuICB9XG4gIEhUTUxEb2N1bWVudC5wcm90b3R5cGUuZmluZFBvc2l0aW9uID0gZnVuY3Rpb24gKE4sIGluZGV4LCBkZWxpbSwgbm9kZXMpIHtcbiAgICB2YXIgZV8xLCBfYTtcbiAgICB2YXIgYWRhcHRvciA9IHRoaXMuYWRhcHRvcjtcbiAgICB0cnkge1xuICAgICAgZm9yICh2YXIgX2IgPSBfX3ZhbHVlcyhub2Rlc1tOXSksIF9jID0gX2IubmV4dCgpOyAhX2MuZG9uZTsgX2MgPSBfYi5uZXh0KCkpIHtcbiAgICAgICAgdmFyIGxpc3QgPSBfYy52YWx1ZTtcbiAgICAgICAgdmFyIF9kID0gX19yZWFkKGxpc3QsIDIpLFxuICAgICAgICAgIG5vZGUgPSBfZFswXSxcbiAgICAgICAgICBuID0gX2RbMV07XG4gICAgICAgIGlmIChpbmRleCA8PSBuICYmIGFkYXB0b3Iua2luZChub2RlKSA9PT0gJyN0ZXh0Jykge1xuICAgICAgICAgIHJldHVybiB7XG4gICAgICAgICAgICBub2RlOiBub2RlLFxuICAgICAgICAgICAgbjogTWF0aC5tYXgoaW5kZXgsIDApLFxuICAgICAgICAgICAgZGVsaW06IGRlbGltXG4gICAgICAgICAgfTtcbiAgICAgICAgfVxuICAgICAgICBpbmRleCAtPSBuO1xuICAgICAgfVxuICAgIH0gY2F0Y2ggKGVfMV8xKSB7XG4gICAgICBlXzEgPSB7XG4gICAgICAgIGVycm9yOiBlXzFfMVxuICAgICAgfTtcbiAgICB9IGZpbmFsbHkge1xuICAgICAgdHJ5IHtcbiAgICAgICAgaWYgKF9jICYmICFfYy5kb25lICYmIChfYSA9IF9iLnJldHVybikpIF9hLmNhbGwoX2IpO1xuICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgaWYgKGVfMSkgdGhyb3cgZV8xLmVycm9yO1xuICAgICAgfVxuICAgIH1cbiAgICByZXR1cm4ge1xuICAgICAgbm9kZTogbnVsbCxcbiAgICAgIG46IDAsXG4gICAgICBkZWxpbTogZGVsaW1cbiAgICB9O1xuICB9O1xuICBIVE1MRG9jdW1lbnQucHJvdG90eXBlLm1hdGhJdGVtID0gZnVuY3Rpb24gKGl0ZW0sIGpheCwgbm9kZXMpIHtcbiAgICB2YXIgbWF0aCA9IGl0ZW0ubWF0aDtcbiAgICB2YXIgc3RhcnQgPSB0aGlzLmZpbmRQb3NpdGlvbihpdGVtLm4sIGl0ZW0uc3RhcnQubiwgaXRlbS5vcGVuLCBub2Rlcyk7XG4gICAgdmFyIGVuZCA9IHRoaXMuZmluZFBvc2l0aW9uKGl0ZW0ubiwgaXRlbS5lbmQubiwgaXRlbS5jbG9zZSwgbm9kZXMpO1xuICAgIHJldHVybiBuZXcgdGhpcy5vcHRpb25zLk1hdGhJdGVtKG1hdGgsIGpheCwgaXRlbS5kaXNwbGF5LCBzdGFydCwgZW5kKTtcbiAgfTtcbiAgSFRNTERvY3VtZW50LnByb3RvdHlwZS5maW5kTWF0aCA9IGZ1bmN0aW9uIChvcHRpb25zKSB7XG4gICAgdmFyIGVfMiwgX2EsIGVfMywgX2IsIF9jLCBlXzQsIF9kLCBlXzUsIF9lO1xuICAgIGlmICghdGhpcy5wcm9jZXNzZWQuaXNTZXQoJ2ZpbmRNYXRoJykpIHtcbiAgICAgIHRoaXMuYWRhcHRvci5kb2N1bWVudCA9IHRoaXMuZG9jdW1lbnQ7XG4gICAgICBvcHRpb25zID0gKDAsIE9wdGlvbnNfanNfMS51c2VyT3B0aW9ucykoe1xuICAgICAgICBlbGVtZW50czogdGhpcy5vcHRpb25zLmVsZW1lbnRzIHx8IFt0aGlzLmFkYXB0b3IuYm9keSh0aGlzLmRvY3VtZW50KV1cbiAgICAgIH0sIG9wdGlvbnMpO1xuICAgICAgdHJ5IHtcbiAgICAgICAgZm9yICh2YXIgX2YgPSBfX3ZhbHVlcyh0aGlzLmFkYXB0b3IuZ2V0RWxlbWVudHMob3B0aW9uc1snZWxlbWVudHMnXSwgdGhpcy5kb2N1bWVudCkpLCBfZyA9IF9mLm5leHQoKTsgIV9nLmRvbmU7IF9nID0gX2YubmV4dCgpKSB7XG4gICAgICAgICAgdmFyIGNvbnRhaW5lciA9IF9nLnZhbHVlO1xuICAgICAgICAgIHZhciBfaCA9IF9fcmVhZChbbnVsbCwgbnVsbF0sIDIpLFxuICAgICAgICAgICAgc3RyaW5ncyA9IF9oWzBdLFxuICAgICAgICAgICAgbm9kZXMgPSBfaFsxXTtcbiAgICAgICAgICB0cnkge1xuICAgICAgICAgICAgZm9yICh2YXIgX2ogPSAoZV8zID0gdm9pZCAwLCBfX3ZhbHVlcyh0aGlzLmlucHV0SmF4KSksIF9rID0gX2oubmV4dCgpOyAhX2suZG9uZTsgX2sgPSBfai5uZXh0KCkpIHtcbiAgICAgICAgICAgICAgdmFyIGpheCA9IF9rLnZhbHVlO1xuICAgICAgICAgICAgICB2YXIgbGlzdCA9IG5ldyB0aGlzLm9wdGlvbnNbJ01hdGhMaXN0J10oKTtcbiAgICAgICAgICAgICAgaWYgKGpheC5wcm9jZXNzU3RyaW5ncykge1xuICAgICAgICAgICAgICAgIGlmIChzdHJpbmdzID09PSBudWxsKSB7XG4gICAgICAgICAgICAgICAgICBfYyA9IF9fcmVhZCh0aGlzLmRvbVN0cmluZ3MuZmluZChjb250YWluZXIpLCAyKSwgc3RyaW5ncyA9IF9jWzBdLCBub2RlcyA9IF9jWzFdO1xuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgICB0cnkge1xuICAgICAgICAgICAgICAgICAgZm9yICh2YXIgX2wgPSAoZV80ID0gdm9pZCAwLCBfX3ZhbHVlcyhqYXguZmluZE1hdGgoc3RyaW5ncykpKSwgX20gPSBfbC5uZXh0KCk7ICFfbS5kb25lOyBfbSA9IF9sLm5leHQoKSkge1xuICAgICAgICAgICAgICAgICAgICB2YXIgbWF0aCA9IF9tLnZhbHVlO1xuICAgICAgICAgICAgICAgICAgICBsaXN0LnB1c2godGhpcy5tYXRoSXRlbShtYXRoLCBqYXgsIG5vZGVzKSk7XG4gICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgfSBjYXRjaCAoZV80XzEpIHtcbiAgICAgICAgICAgICAgICAgIGVfNCA9IHtcbiAgICAgICAgICAgICAgICAgICAgZXJyb3I6IGVfNF8xXG4gICAgICAgICAgICAgICAgICB9O1xuICAgICAgICAgICAgICAgIH0gZmluYWxseSB7XG4gICAgICAgICAgICAgICAgICB0cnkge1xuICAgICAgICAgICAgICAgICAgICBpZiAoX20gJiYgIV9tLmRvbmUgJiYgKF9kID0gX2wucmV0dXJuKSkgX2QuY2FsbChfbCk7XG4gICAgICAgICAgICAgICAgICB9IGZpbmFsbHkge1xuICAgICAgICAgICAgICAgICAgICBpZiAoZV80KSB0aHJvdyBlXzQuZXJyb3I7XG4gICAgICAgICAgICAgICAgICB9XG4gICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICB9IGVsc2Uge1xuICAgICAgICAgICAgICAgIHRyeSB7XG4gICAgICAgICAgICAgICAgICBmb3IgKHZhciBfbyA9IChlXzUgPSB2b2lkIDAsIF9fdmFsdWVzKGpheC5maW5kTWF0aChjb250YWluZXIpKSksIF9wID0gX28ubmV4dCgpOyAhX3AuZG9uZTsgX3AgPSBfby5uZXh0KCkpIHtcbiAgICAgICAgICAgICAgICAgICAgdmFyIG1hdGggPSBfcC52YWx1ZTtcbiAgICAgICAgICAgICAgICAgICAgdmFyIGl0ZW0gPSBuZXcgdGhpcy5vcHRpb25zLk1hdGhJdGVtKG1hdGgubWF0aCwgamF4LCBtYXRoLmRpc3BsYXksIG1hdGguc3RhcnQsIG1hdGguZW5kKTtcbiAgICAgICAgICAgICAgICAgICAgbGlzdC5wdXNoKGl0ZW0pO1xuICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgIH0gY2F0Y2ggKGVfNV8xKSB7XG4gICAgICAgICAgICAgICAgICBlXzUgPSB7XG4gICAgICAgICAgICAgICAgICAgIGVycm9yOiBlXzVfMVxuICAgICAgICAgICAgICAgICAgfTtcbiAgICAgICAgICAgICAgICB9IGZpbmFsbHkge1xuICAgICAgICAgICAgICAgICAgdHJ5IHtcbiAgICAgICAgICAgICAgICAgICAgaWYgKF9wICYmICFfcC5kb25lICYmIChfZSA9IF9vLnJldHVybikpIF9lLmNhbGwoX28pO1xuICAgICAgICAgICAgICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgICAgICAgICAgICAgaWYgKGVfNSkgdGhyb3cgZV81LmVycm9yO1xuICAgICAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICAgIH1cbiAgICAgICAgICAgICAgfVxuICAgICAgICAgICAgICB0aGlzLm1hdGgubWVyZ2UobGlzdCk7XG4gICAgICAgICAgICB9XG4gICAgICAgICAgfSBjYXRjaCAoZV8zXzEpIHtcbiAgICAgICAgICAgIGVfMyA9IHtcbiAgICAgICAgICAgICAgZXJyb3I6IGVfM18xXG4gICAgICAgICAgICB9O1xuICAgICAgICAgIH0gZmluYWxseSB7XG4gICAgICAgICAgICB0cnkge1xuICAgICAgICAgICAgICBpZiAoX2sgJiYgIV9rLmRvbmUgJiYgKF9iID0gX2oucmV0dXJuKSkgX2IuY2FsbChfaik7XG4gICAgICAgICAgICB9IGZpbmFsbHkge1xuICAgICAgICAgICAgICBpZiAoZV8zKSB0aHJvdyBlXzMuZXJyb3I7XG4gICAgICAgICAgICB9XG4gICAgICAgICAgfVxuICAgICAgICB9XG4gICAgICB9IGNhdGNoIChlXzJfMSkge1xuICAgICAgICBlXzIgPSB7XG4gICAgICAgICAgZXJyb3I6IGVfMl8xXG4gICAgICAgIH07XG4gICAgICB9IGZpbmFsbHkge1xuICAgICAgICB0cnkge1xuICAgICAgICAgIGlmIChfZyAmJiAhX2cuZG9uZSAmJiAoX2EgPSBfZi5yZXR1cm4pKSBfYS5jYWxsKF9mKTtcbiAgICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgICBpZiAoZV8yKSB0aHJvdyBlXzIuZXJyb3I7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICAgIHRoaXMucHJvY2Vzc2VkLnNldCgnZmluZE1hdGgnKTtcbiAgICB9XG4gICAgcmV0dXJuIHRoaXM7XG4gIH07XG4gIEhUTUxEb2N1bWVudC5wcm90b3R5cGUudXBkYXRlRG9jdW1lbnQgPSBmdW5jdGlvbiAoKSB7XG4gICAgaWYgKCF0aGlzLnByb2Nlc3NlZC5pc1NldCgndXBkYXRlRG9jdW1lbnQnKSkge1xuICAgICAgdGhpcy5hZGRQYWdlRWxlbWVudHMoKTtcbiAgICAgIHRoaXMuYWRkU3R5bGVTaGVldCgpO1xuICAgICAgX3N1cGVyLnByb3RvdHlwZS51cGRhdGVEb2N1bWVudC5jYWxsKHRoaXMpO1xuICAgICAgdGhpcy5wcm9jZXNzZWQuc2V0KCd1cGRhdGVEb2N1bWVudCcpO1xuICAgIH1cbiAgICByZXR1cm4gdGhpcztcbiAgfTtcbiAgSFRNTERvY3VtZW50LnByb3RvdHlwZS5hZGRQYWdlRWxlbWVudHMgPSBmdW5jdGlvbiAoKSB7XG4gICAgdmFyIGJvZHkgPSB0aGlzLmFkYXB0b3IuYm9keSh0aGlzLmRvY3VtZW50KTtcbiAgICB2YXIgbm9kZSA9IHRoaXMuZG9jdW1lbnRQYWdlRWxlbWVudHMoKTtcbiAgICBpZiAobm9kZSkge1xuICAgICAgdGhpcy5hZGFwdG9yLmFwcGVuZChib2R5LCBub2RlKTtcbiAgICB9XG4gIH07XG4gIEhUTUxEb2N1bWVudC5wcm90b3R5cGUuYWRkU3R5bGVTaGVldCA9IGZ1bmN0aW9uICgpIHtcbiAgICB2YXIgc2hlZXQgPSB0aGlzLmRvY3VtZW50U3R5bGVTaGVldCgpO1xuICAgIHZhciBhZGFwdG9yID0gdGhpcy5hZGFwdG9yO1xuICAgIGlmIChzaGVldCAmJiAhYWRhcHRvci5wYXJlbnQoc2hlZXQpKSB7XG4gICAgICB2YXIgaGVhZCA9IGFkYXB0b3IuaGVhZCh0aGlzLmRvY3VtZW50KTtcbiAgICAgIHZhciBzdHlsZXMgPSB0aGlzLmZpbmRTaGVldChoZWFkLCBhZGFwdG9yLmdldEF0dHJpYnV0ZShzaGVldCwgJ2lkJykpO1xuICAgICAgaWYgKHN0eWxlcykge1xuICAgICAgICBhZGFwdG9yLnJlcGxhY2Uoc2hlZXQsIHN0eWxlcyk7XG4gICAgICB9IGVsc2Uge1xuICAgICAgICBhZGFwdG9yLmFwcGVuZChoZWFkLCBzaGVldCk7XG4gICAgICB9XG4gICAgfVxuICB9O1xuICBIVE1MRG9jdW1lbnQucHJvdG90eXBlLmZpbmRTaGVldCA9IGZ1bmN0aW9uIChoZWFkLCBpZCkge1xuICAgIHZhciBlXzYsIF9hO1xuICAgIGlmIChpZCkge1xuICAgICAgdHJ5IHtcbiAgICAgICAgZm9yICh2YXIgX2IgPSBfX3ZhbHVlcyh0aGlzLmFkYXB0b3IudGFncyhoZWFkLCAnc3R5bGUnKSksIF9jID0gX2IubmV4dCgpOyAhX2MuZG9uZTsgX2MgPSBfYi5uZXh0KCkpIHtcbiAgICAgICAgICB2YXIgc2hlZXQgPSBfYy52YWx1ZTtcbiAgICAgICAgICBpZiAodGhpcy5hZGFwdG9yLmdldEF0dHJpYnV0ZShzaGVldCwgJ2lkJykgPT09IGlkKSB7XG4gICAgICAgICAgICByZXR1cm4gc2hlZXQ7XG4gICAgICAgICAgfVxuICAgICAgICB9XG4gICAgICB9IGNhdGNoIChlXzZfMSkge1xuICAgICAgICBlXzYgPSB7XG4gICAgICAgICAgZXJyb3I6IGVfNl8xXG4gICAgICAgIH07XG4gICAgICB9IGZpbmFsbHkge1xuICAgICAgICB0cnkge1xuICAgICAgICAgIGlmIChfYyAmJiAhX2MuZG9uZSAmJiAoX2EgPSBfYi5yZXR1cm4pKSBfYS5jYWxsKF9iKTtcbiAgICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgICBpZiAoZV82KSB0aHJvdyBlXzYuZXJyb3I7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIG51bGw7XG4gIH07XG4gIEhUTUxEb2N1bWVudC5wcm90b3R5cGUucmVtb3ZlRnJvbURvY3VtZW50ID0gZnVuY3Rpb24gKHJlc3RvcmUpIHtcbiAgICB2YXIgZV83LCBfYTtcbiAgICBpZiAocmVzdG9yZSA9PT0gdm9pZCAwKSB7XG4gICAgICByZXN0b3JlID0gZmFsc2U7XG4gICAgfVxuICAgIGlmICh0aGlzLnByb2Nlc3NlZC5pc1NldCgndXBkYXRlRG9jdW1lbnQnKSkge1xuICAgICAgdHJ5IHtcbiAgICAgICAgZm9yICh2YXIgX2IgPSBfX3ZhbHVlcyh0aGlzLm1hdGgpLCBfYyA9IF9iLm5leHQoKTsgIV9jLmRvbmU7IF9jID0gX2IubmV4dCgpKSB7XG4gICAgICAgICAgdmFyIG1hdGggPSBfYy52YWx1ZTtcbiAgICAgICAgICBpZiAobWF0aC5zdGF0ZSgpID49IE1hdGhJdGVtX2pzXzEuU1RBVEUuSU5TRVJURUQpIHtcbiAgICAgICAgICAgIG1hdGguc3RhdGUoTWF0aEl0ZW1fanNfMS5TVEFURS5UWVBFU0VULCByZXN0b3JlKTtcbiAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgIH0gY2F0Y2ggKGVfN18xKSB7XG4gICAgICAgIGVfNyA9IHtcbiAgICAgICAgICBlcnJvcjogZV83XzFcbiAgICAgICAgfTtcbiAgICAgIH0gZmluYWxseSB7XG4gICAgICAgIHRyeSB7XG4gICAgICAgICAgaWYgKF9jICYmICFfYy5kb25lICYmIChfYSA9IF9iLnJldHVybikpIF9hLmNhbGwoX2IpO1xuICAgICAgICB9IGZpbmFsbHkge1xuICAgICAgICAgIGlmIChlXzcpIHRocm93IGVfNy5lcnJvcjtcbiAgICAgICAgfVxuICAgICAgfVxuICAgIH1cbiAgICB0aGlzLnByb2Nlc3NlZC5jbGVhcigndXBkYXRlRG9jdW1lbnQnKTtcbiAgICByZXR1cm4gdGhpcztcbiAgfTtcbiAgSFRNTERvY3VtZW50LnByb3RvdHlwZS5kb2N1bWVudFN0eWxlU2hlZXQgPSBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHRoaXMub3V0cHV0SmF4LnN0eWxlU2hlZXQodGhpcyk7XG4gIH07XG4gIEhUTUxEb2N1bWVudC5wcm90b3R5cGUuZG9jdW1lbnRQYWdlRWxlbWVudHMgPSBmdW5jdGlvbiAoKSB7XG4gICAgcmV0dXJuIHRoaXMub3V0cHV0SmF4LnBhZ2VFbGVtZW50cyh0aGlzKTtcbiAgfTtcbiAgSFRNTERvY3VtZW50LnByb3RvdHlwZS5hZGRTdHlsZXMgPSBmdW5jdGlvbiAoc3R5bGVzKSB7XG4gICAgdGhpcy5zdHlsZXMucHVzaChzdHlsZXMpO1xuICB9O1xuICBIVE1MRG9jdW1lbnQucHJvdG90eXBlLmdldFN0eWxlcyA9IGZ1bmN0aW9uICgpIHtcbiAgICByZXR1cm4gdGhpcy5zdHlsZXM7XG4gIH07XG4gIEhUTUxEb2N1bWVudC5LSU5EID0gJ0hUTUwnO1xuICBIVE1MRG9jdW1lbnQuT1BUSU9OUyA9IF9fYXNzaWduKF9fYXNzaWduKHt9LCBNYXRoRG9jdW1lbnRfanNfMS5BYnN0cmFjdE1hdGhEb2N1bWVudC5PUFRJT05TKSwge1xuICAgIHJlbmRlckFjdGlvbnM6ICgwLCBPcHRpb25zX2pzXzEuZXhwYW5kYWJsZSkoX19hc3NpZ24oX19hc3NpZ24oe30sIE1hdGhEb2N1bWVudF9qc18xLkFic3RyYWN0TWF0aERvY3VtZW50Lk9QVElPTlMucmVuZGVyQWN0aW9ucyksIHtcbiAgICAgIHN0eWxlczogW01hdGhJdGVtX2pzXzEuU1RBVEUuSU5TRVJURUQgKyAxLCAnJywgJ3VwZGF0ZVN0eWxlU2hlZXQnLCBmYWxzZV1cbiAgICB9KSksXG4gICAgTWF0aExpc3Q6IEhUTUxNYXRoTGlzdF9qc18xLkhUTUxNYXRoTGlzdCxcbiAgICBNYXRoSXRlbTogSFRNTE1hdGhJdGVtX2pzXzEuSFRNTE1hdGhJdGVtLFxuICAgIERvbVN0cmluZ3M6IG51bGxcbiAgfSk7XG4gIHJldHVybiBIVE1MRG9jdW1lbnQ7XG59KE1hdGhEb2N1bWVudF9qc18xLkFic3RyYWN0TWF0aERvY3VtZW50KTtcbmV4cG9ydHMuSFRNTERvY3VtZW50ID0gSFRNTERvY3VtZW50OyIsIlwidXNlIHN0cmljdFwiO1xuXG52YXIgX19leHRlbmRzID0gdGhpcyAmJiB0aGlzLl9fZXh0ZW5kcyB8fCBmdW5jdGlvbiAoKSB7XG4gIHZhciBleHRlbmRTdGF0aWNzID0gZnVuY3Rpb24gKGQsIGIpIHtcbiAgICBleHRlbmRTdGF0aWNzID0gT2JqZWN0LnNldFByb3RvdHlwZU9mIHx8IHtcbiAgICAgIF9fcHJvdG9fXzogW11cbiAgICB9IGluc3RhbmNlb2YgQXJyYXkgJiYgZnVuY3Rpb24gKGQsIGIpIHtcbiAgICAgIGQuX19wcm90b19fID0gYjtcbiAgICB9IHx8IGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgICBmb3IgKHZhciBwIGluIGIpIGlmIChPYmplY3QucHJvdG90eXBlLmhhc093blByb3BlcnR5LmNhbGwoYiwgcCkpIGRbcF0gPSBiW3BdO1xuICAgIH07XG4gICAgcmV0dXJuIGV4dGVuZFN0YXRpY3MoZCwgYik7XG4gIH07XG4gIHJldHVybiBmdW5jdGlvbiAoZCwgYikge1xuICAgIGlmICh0eXBlb2YgYiAhPT0gXCJmdW5jdGlvblwiICYmIGIgIT09IG51bGwpIHRocm93IG5ldyBUeXBlRXJyb3IoXCJDbGFzcyBleHRlbmRzIHZhbHVlIFwiICsgU3RyaW5nKGIpICsgXCIgaXMgbm90IGEgY29uc3RydWN0b3Igb3IgbnVsbFwiKTtcbiAgICBleHRlbmRTdGF0aWNzKGQsIGIpO1xuICAgIGZ1bmN0aW9uIF9fKCkge1xuICAgICAgdGhpcy5jb25zdHJ1Y3RvciA9IGQ7XG4gICAgfVxuICAgIGQucHJvdG90eXBlID0gYiA9PT0gbnVsbCA/IE9iamVjdC5jcmVhdGUoYikgOiAoX18ucHJvdG90eXBlID0gYi5wcm90b3R5cGUsIG5ldyBfXygpKTtcbiAgfTtcbn0oKTtcbk9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBcIl9fZXNNb2R1bGVcIiwge1xuICB2YWx1ZTogdHJ1ZVxufSk7XG5leHBvcnRzLkhUTUxNYXRoSXRlbSA9IHZvaWQgMDtcbnZhciBNYXRoSXRlbV9qc18xID0gcmVxdWlyZShcIi4uLy4uL2NvcmUvTWF0aEl0ZW0uanNcIik7XG52YXIgSFRNTE1hdGhJdGVtID0gZnVuY3Rpb24gKF9zdXBlcikge1xuICBfX2V4dGVuZHMoSFRNTE1hdGhJdGVtLCBfc3VwZXIpO1xuICBmdW5jdGlvbiBIVE1MTWF0aEl0ZW0obWF0aCwgamF4LCBkaXNwbGF5LCBzdGFydCwgZW5kKSB7XG4gICAgaWYgKGRpc3BsYXkgPT09IHZvaWQgMCkge1xuICAgICAgZGlzcGxheSA9IHRydWU7XG4gICAgfVxuICAgIGlmIChzdGFydCA9PT0gdm9pZCAwKSB7XG4gICAgICBzdGFydCA9IHtcbiAgICAgICAgbm9kZTogbnVsbCxcbiAgICAgICAgbjogMCxcbiAgICAgICAgZGVsaW06ICcnXG4gICAgICB9O1xuICAgIH1cbiAgICBpZiAoZW5kID09PSB2b2lkIDApIHtcbiAgICAgIGVuZCA9IHtcbiAgICAgICAgbm9kZTogbnVsbCxcbiAgICAgICAgbjogMCxcbiAgICAgICAgZGVsaW06ICcnXG4gICAgICB9O1xuICAgIH1cbiAgICByZXR1cm4gX3N1cGVyLmNhbGwodGhpcywgbWF0aCwgamF4LCBkaXNwbGF5LCBzdGFydCwgZW5kKSB8fCB0aGlzO1xuICB9XG4gIE9iamVjdC5kZWZpbmVQcm9wZXJ0eShIVE1MTWF0aEl0ZW0ucHJvdG90eXBlLCBcImFkYXB0b3JcIiwge1xuICAgIGdldDogZnVuY3Rpb24gKCkge1xuICAgICAgcmV0dXJuIHRoaXMuaW5wdXRKYXguYWRhcHRvcjtcbiAgICB9LFxuICAgIGVudW1lcmFibGU6IGZhbHNlLFxuICAgIGNvbmZpZ3VyYWJsZTogdHJ1ZVxuICB9KTtcbiAgSFRNTE1hdGhJdGVtLnByb3RvdHlwZS51cGRhdGVEb2N1bWVudCA9IGZ1bmN0aW9uIChfaHRtbCkge1xuICAgIGlmICh0aGlzLnN0YXRlKCkgPCBNYXRoSXRlbV9qc18xLlNUQVRFLklOU0VSVEVEKSB7XG4gICAgICBpZiAodGhpcy5pbnB1dEpheC5wcm9jZXNzU3RyaW5ncykge1xuICAgICAgICB2YXIgbm9kZSA9IHRoaXMuc3RhcnQubm9kZTtcbiAgICAgICAgaWYgKG5vZGUgPT09IHRoaXMuZW5kLm5vZGUpIHtcbiAgICAgICAgICBpZiAodGhpcy5lbmQubiAmJiB0aGlzLmVuZC5uIDwgdGhpcy5hZGFwdG9yLnZhbHVlKHRoaXMuZW5kLm5vZGUpLmxlbmd0aCkge1xuICAgICAgICAgICAgdGhpcy5hZGFwdG9yLnNwbGl0KHRoaXMuZW5kLm5vZGUsIHRoaXMuZW5kLm4pO1xuICAgICAgICAgIH1cbiAgICAgICAgICBpZiAodGhpcy5zdGFydC5uKSB7XG4gICAgICAgICAgICBub2RlID0gdGhpcy5hZGFwdG9yLnNwbGl0KHRoaXMuc3RhcnQubm9kZSwgdGhpcy5zdGFydC5uKTtcbiAgICAgICAgICB9XG4gICAgICAgICAgdGhpcy5hZGFwdG9yLnJlcGxhY2UodGhpcy50eXBlc2V0Um9vdCwgbm9kZSk7XG4gICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgaWYgKHRoaXMuc3RhcnQubikge1xuICAgICAgICAgICAgbm9kZSA9IHRoaXMuYWRhcHRvci5zcGxpdChub2RlLCB0aGlzLnN0YXJ0Lm4pO1xuICAgICAgICAgIH1cbiAgICAgICAgICB3aGlsZSAobm9kZSAhPT0gdGhpcy5lbmQubm9kZSkge1xuICAgICAgICAgICAgdmFyIG5leHQgPSB0aGlzLmFkYXB0b3IubmV4dChub2RlKTtcbiAgICAgICAgICAgIHRoaXMuYWRhcHRvci5yZW1vdmUobm9kZSk7XG4gICAgICAgICAgICBub2RlID0gbmV4dDtcbiAgICAgICAgICB9XG4gICAgICAgICAgdGhpcy5hZGFwdG9yLmluc2VydCh0aGlzLnR5cGVzZXRSb290LCBub2RlKTtcbiAgICAgICAgICBpZiAodGhpcy5lbmQubiA8IHRoaXMuYWRhcHRvci52YWx1ZShub2RlKS5sZW5ndGgpIHtcbiAgICAgICAgICAgIHRoaXMuYWRhcHRvci5zcGxpdChub2RlLCB0aGlzLmVuZC5uKTtcbiAgICAgICAgICB9XG4gICAgICAgICAgdGhpcy5hZGFwdG9yLnJlbW92ZShub2RlKTtcbiAgICAgICAgfVxuICAgICAgfSBlbHNlIHtcbiAgICAgICAgdGhpcy5hZGFwdG9yLnJlcGxhY2UodGhpcy50eXBlc2V0Um9vdCwgdGhpcy5zdGFydC5ub2RlKTtcbiAgICAgIH1cbiAgICAgIHRoaXMuc3RhcnQubm9kZSA9IHRoaXMuZW5kLm5vZGUgPSB0aGlzLnR5cGVzZXRSb290O1xuICAgICAgdGhpcy5zdGFydC5uID0gdGhpcy5lbmQubiA9IDA7XG4gICAgICB0aGlzLnN0YXRlKE1hdGhJdGVtX2pzXzEuU1RBVEUuSU5TRVJURUQpO1xuICAgIH1cbiAgfTtcbiAgSFRNTE1hdGhJdGVtLnByb3RvdHlwZS51cGRhdGVTdHlsZVNoZWV0ID0gZnVuY3Rpb24gKGRvY3VtZW50KSB7XG4gICAgZG9jdW1lbnQuYWRkU3R5bGVTaGVldCgpO1xuICB9O1xuICBIVE1MTWF0aEl0ZW0ucHJvdG90eXBlLnJlbW92ZUZyb21Eb2N1bWVudCA9IGZ1bmN0aW9uIChyZXN0b3JlKSB7XG4gICAgaWYgKHJlc3RvcmUgPT09IHZvaWQgMCkge1xuICAgICAgcmVzdG9yZSA9IGZhbHNlO1xuICAgIH1cbiAgICBpZiAodGhpcy5zdGF0ZSgpID49IE1hdGhJdGVtX2pzXzEuU1RBVEUuVFlQRVNFVCkge1xuICAgICAgdmFyIGFkYXB0b3IgPSB0aGlzLmFkYXB0b3I7XG4gICAgICB2YXIgbm9kZSA9IHRoaXMuc3RhcnQubm9kZTtcbiAgICAgIHZhciBtYXRoID0gYWRhcHRvci50ZXh0KCcnKTtcbiAgICAgIGlmIChyZXN0b3JlKSB7XG4gICAgICAgIHZhciB0ZXh0ID0gdGhpcy5zdGFydC5kZWxpbSArIHRoaXMubWF0aCArIHRoaXMuZW5kLmRlbGltO1xuICAgICAgICBpZiAodGhpcy5pbnB1dEpheC5wcm9jZXNzU3RyaW5ncykge1xuICAgICAgICAgIG1hdGggPSBhZGFwdG9yLnRleHQodGV4dCk7XG4gICAgICAgIH0gZWxzZSB7XG4gICAgICAgICAgdmFyIGRvYyA9IGFkYXB0b3IucGFyc2UodGV4dCwgJ3RleHQvaHRtbCcpO1xuICAgICAgICAgIG1hdGggPSBhZGFwdG9yLmZpcnN0Q2hpbGQoYWRhcHRvci5ib2R5KGRvYykpO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgICBpZiAoYWRhcHRvci5wYXJlbnQobm9kZSkpIHtcbiAgICAgICAgYWRhcHRvci5yZXBsYWNlKG1hdGgsIG5vZGUpO1xuICAgICAgfVxuICAgICAgdGhpcy5zdGFydC5ub2RlID0gdGhpcy5lbmQubm9kZSA9IG1hdGg7XG4gICAgICB0aGlzLnN0YXJ0Lm4gPSB0aGlzLmVuZC5uID0gMDtcbiAgICB9XG4gIH07XG4gIHJldHVybiBIVE1MTWF0aEl0ZW07XG59KE1hdGhJdGVtX2pzXzEuQWJzdHJhY3RNYXRoSXRlbSk7XG5leHBvcnRzLkhUTUxNYXRoSXRlbSA9IEhUTUxNYXRoSXRlbTsiLCJcInVzZSBzdHJpY3RcIjtcblxudmFyIF9fZXh0ZW5kcyA9IHRoaXMgJiYgdGhpcy5fX2V4dGVuZHMgfHwgZnVuY3Rpb24gKCkge1xuICB2YXIgZXh0ZW5kU3RhdGljcyA9IGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgZXh0ZW5kU3RhdGljcyA9IE9iamVjdC5zZXRQcm90b3R5cGVPZiB8fCB7XG4gICAgICBfX3Byb3RvX186IFtdXG4gICAgfSBpbnN0YW5jZW9mIEFycmF5ICYmIGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgICBkLl9fcHJvdG9fXyA9IGI7XG4gICAgfSB8fCBmdW5jdGlvbiAoZCwgYikge1xuICAgICAgZm9yICh2YXIgcCBpbiBiKSBpZiAoT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsKGIsIHApKSBkW3BdID0gYltwXTtcbiAgICB9O1xuICAgIHJldHVybiBleHRlbmRTdGF0aWNzKGQsIGIpO1xuICB9O1xuICByZXR1cm4gZnVuY3Rpb24gKGQsIGIpIHtcbiAgICBpZiAodHlwZW9mIGIgIT09IFwiZnVuY3Rpb25cIiAmJiBiICE9PSBudWxsKSB0aHJvdyBuZXcgVHlwZUVycm9yKFwiQ2xhc3MgZXh0ZW5kcyB2YWx1ZSBcIiArIFN0cmluZyhiKSArIFwiIGlzIG5vdCBhIGNvbnN0cnVjdG9yIG9yIG51bGxcIik7XG4gICAgZXh0ZW5kU3RhdGljcyhkLCBiKTtcbiAgICBmdW5jdGlvbiBfXygpIHtcbiAgICAgIHRoaXMuY29uc3RydWN0b3IgPSBkO1xuICAgIH1cbiAgICBkLnByb3RvdHlwZSA9IGIgPT09IG51bGwgPyBPYmplY3QuY3JlYXRlKGIpIDogKF9fLnByb3RvdHlwZSA9IGIucHJvdG90eXBlLCBuZXcgX18oKSk7XG4gIH07XG59KCk7XG5PYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgXCJfX2VzTW9kdWxlXCIsIHtcbiAgdmFsdWU6IHRydWVcbn0pO1xuZXhwb3J0cy5IVE1MSGFuZGxlciA9IHZvaWQgMDtcbnZhciBIYW5kbGVyX2pzXzEgPSByZXF1aXJlKFwiLi4vLi4vY29yZS9IYW5kbGVyLmpzXCIpO1xudmFyIEhUTUxEb2N1bWVudF9qc18xID0gcmVxdWlyZShcIi4vSFRNTERvY3VtZW50LmpzXCIpO1xudmFyIEhUTUxIYW5kbGVyID0gZnVuY3Rpb24gKF9zdXBlcikge1xuICBfX2V4dGVuZHMoSFRNTEhhbmRsZXIsIF9zdXBlcik7XG4gIGZ1bmN0aW9uIEhUTUxIYW5kbGVyKCkge1xuICAgIHZhciBfdGhpcyA9IF9zdXBlciAhPT0gbnVsbCAmJiBfc3VwZXIuYXBwbHkodGhpcywgYXJndW1lbnRzKSB8fCB0aGlzO1xuICAgIF90aGlzLmRvY3VtZW50Q2xhc3MgPSBIVE1MRG9jdW1lbnRfanNfMS5IVE1MRG9jdW1lbnQ7XG4gICAgcmV0dXJuIF90aGlzO1xuICB9XG4gIEhUTUxIYW5kbGVyLnByb3RvdHlwZS5oYW5kbGVzRG9jdW1lbnQgPSBmdW5jdGlvbiAoZG9jdW1lbnQpIHtcbiAgICB2YXIgYWRhcHRvciA9IHRoaXMuYWRhcHRvcjtcbiAgICBpZiAodHlwZW9mIGRvY3VtZW50ID09PSAnc3RyaW5nJykge1xuICAgICAgdHJ5IHtcbiAgICAgICAgZG9jdW1lbnQgPSBhZGFwdG9yLnBhcnNlKGRvY3VtZW50LCAndGV4dC9odG1sJyk7XG4gICAgICB9IGNhdGNoIChlcnIpIHt9XG4gICAgfVxuICAgIGlmIChkb2N1bWVudCBpbnN0YW5jZW9mIGFkYXB0b3Iud2luZG93LkRvY3VtZW50IHx8IGRvY3VtZW50IGluc3RhbmNlb2YgYWRhcHRvci53aW5kb3cuSFRNTEVsZW1lbnQgfHwgZG9jdW1lbnQgaW5zdGFuY2VvZiBhZGFwdG9yLndpbmRvdy5Eb2N1bWVudEZyYWdtZW50KSB7XG4gICAgICByZXR1cm4gdHJ1ZTtcbiAgICB9XG4gICAgcmV0dXJuIGZhbHNlO1xuICB9O1xuICBIVE1MSGFuZGxlci5wcm90b3R5cGUuY3JlYXRlID0gZnVuY3Rpb24gKGRvY3VtZW50LCBvcHRpb25zKSB7XG4gICAgdmFyIGFkYXB0b3IgPSB0aGlzLmFkYXB0b3I7XG4gICAgaWYgKHR5cGVvZiBkb2N1bWVudCA9PT0gJ3N0cmluZycpIHtcbiAgICAgIGRvY3VtZW50ID0gYWRhcHRvci5wYXJzZShkb2N1bWVudCwgJ3RleHQvaHRtbCcpO1xuICAgIH0gZWxzZSBpZiAoZG9jdW1lbnQgaW5zdGFuY2VvZiBhZGFwdG9yLndpbmRvdy5IVE1MRWxlbWVudCB8fCBkb2N1bWVudCBpbnN0YW5jZW9mIGFkYXB0b3Iud2luZG93LkRvY3VtZW50RnJhZ21lbnQpIHtcbiAgICAgIHZhciBjaGlsZCA9IGRvY3VtZW50O1xuICAgICAgZG9jdW1lbnQgPSBhZGFwdG9yLnBhcnNlKCcnLCAndGV4dC9odG1sJyk7XG4gICAgICBhZGFwdG9yLmFwcGVuZChhZGFwdG9yLmJvZHkoZG9jdW1lbnQpLCBjaGlsZCk7XG4gICAgfVxuICAgIHJldHVybiBfc3VwZXIucHJvdG90eXBlLmNyZWF0ZS5jYWxsKHRoaXMsIGRvY3VtZW50LCBvcHRpb25zKTtcbiAgfTtcbiAgcmV0dXJuIEhUTUxIYW5kbGVyO1xufShIYW5kbGVyX2pzXzEuQWJzdHJhY3RIYW5kbGVyKTtcbmV4cG9ydHMuSFRNTEhhbmRsZXIgPSBIVE1MSGFuZGxlcjsiLCJcInVzZSBzdHJpY3RcIjtcblxudmFyIF9fcmVhZCA9IHRoaXMgJiYgdGhpcy5fX3JlYWQgfHwgZnVuY3Rpb24gKG8sIG4pIHtcbiAgdmFyIG0gPSB0eXBlb2YgU3ltYm9sID09PSBcImZ1bmN0aW9uXCIgJiYgb1tTeW1ib2wuaXRlcmF0b3JdO1xuICBpZiAoIW0pIHJldHVybiBvO1xuICB2YXIgaSA9IG0uY2FsbChvKSxcbiAgICByLFxuICAgIGFyID0gW10sXG4gICAgZTtcbiAgdHJ5IHtcbiAgICB3aGlsZSAoKG4gPT09IHZvaWQgMCB8fCBuLS0gPiAwKSAmJiAhKHIgPSBpLm5leHQoKSkuZG9uZSkgYXIucHVzaChyLnZhbHVlKTtcbiAgfSBjYXRjaCAoZXJyb3IpIHtcbiAgICBlID0ge1xuICAgICAgZXJyb3I6IGVycm9yXG4gICAgfTtcbiAgfSBmaW5hbGx5IHtcbiAgICB0cnkge1xuICAgICAgaWYgKHIgJiYgIXIuZG9uZSAmJiAobSA9IGlbXCJyZXR1cm5cIl0pKSBtLmNhbGwoaSk7XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIGlmIChlKSB0aHJvdyBlLmVycm9yO1xuICAgIH1cbiAgfVxuICByZXR1cm4gYXI7XG59O1xuT2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFwiX19lc01vZHVsZVwiLCB7XG4gIHZhbHVlOiB0cnVlXG59KTtcbmV4cG9ydHMuSFRNTERvbVN0cmluZ3MgPSB2b2lkIDA7XG52YXIgT3B0aW9uc19qc18xID0gcmVxdWlyZShcIi4uLy4uL3V0aWwvT3B0aW9ucy5qc1wiKTtcbnZhciBIVE1MRG9tU3RyaW5ncyA9IGZ1bmN0aW9uICgpIHtcbiAgZnVuY3Rpb24gSFRNTERvbVN0cmluZ3Mob3B0aW9ucykge1xuICAgIGlmIChvcHRpb25zID09PSB2b2lkIDApIHtcbiAgICAgIG9wdGlvbnMgPSBudWxsO1xuICAgIH1cbiAgICB2YXIgQ0xBU1MgPSB0aGlzLmNvbnN0cnVjdG9yO1xuICAgIHRoaXMub3B0aW9ucyA9ICgwLCBPcHRpb25zX2pzXzEudXNlck9wdGlvbnMpKCgwLCBPcHRpb25zX2pzXzEuZGVmYXVsdE9wdGlvbnMpKHt9LCBDTEFTUy5PUFRJT05TKSwgb3B0aW9ucyk7XG4gICAgdGhpcy5pbml0KCk7XG4gICAgdGhpcy5nZXRQYXR0ZXJucygpO1xuICB9XG4gIEhUTUxEb21TdHJpbmdzLnByb3RvdHlwZS5pbml0ID0gZnVuY3Rpb24gKCkge1xuICAgIHRoaXMuc3RyaW5ncyA9IFtdO1xuICAgIHRoaXMuc3RyaW5nID0gJyc7XG4gICAgdGhpcy5zbm9kZXMgPSBbXTtcbiAgICB0aGlzLm5vZGVzID0gW107XG4gICAgdGhpcy5zdGFjayA9IFtdO1xuICB9O1xuICBIVE1MRG9tU3RyaW5ncy5wcm90b3R5cGUuZ2V0UGF0dGVybnMgPSBmdW5jdGlvbiAoKSB7XG4gICAgdmFyIHNraXAgPSAoMCwgT3B0aW9uc19qc18xLm1ha2VBcnJheSkodGhpcy5vcHRpb25zWydza2lwSHRtbFRhZ3MnXSk7XG4gICAgdmFyIGlnbm9yZSA9ICgwLCBPcHRpb25zX2pzXzEubWFrZUFycmF5KSh0aGlzLm9wdGlvbnNbJ2lnbm9yZUh0bWxDbGFzcyddKTtcbiAgICB2YXIgcHJvY2VzcyA9ICgwLCBPcHRpb25zX2pzXzEubWFrZUFycmF5KSh0aGlzLm9wdGlvbnNbJ3Byb2Nlc3NIdG1sQ2xhc3MnXSk7XG4gICAgdGhpcy5za2lwSHRtbFRhZ3MgPSBuZXcgUmVnRXhwKCdeKD86JyArIHNraXAuam9pbignfCcpICsgJykkJywgJ2knKTtcbiAgICB0aGlzLmlnbm9yZUh0bWxDbGFzcyA9IG5ldyBSZWdFeHAoJyg/Ol58ICkoPzonICsgaWdub3JlLmpvaW4oJ3wnKSArICcpKD86IHwkKScpO1xuICAgIHRoaXMucHJvY2Vzc0h0bWxDbGFzcyA9IG5ldyBSZWdFeHAoJyg/Ol58ICkoPzonICsgcHJvY2VzcyArICcpKD86IHwkKScpO1xuICB9O1xuICBIVE1MRG9tU3RyaW5ncy5wcm90b3R5cGUucHVzaFN0cmluZyA9IGZ1bmN0aW9uICgpIHtcbiAgICBpZiAodGhpcy5zdHJpbmcubWF0Y2goL1xcUy8pKSB7XG4gICAgICB0aGlzLnN0cmluZ3MucHVzaCh0aGlzLnN0cmluZyk7XG4gICAgICB0aGlzLm5vZGVzLnB1c2godGhpcy5zbm9kZXMpO1xuICAgIH1cbiAgICB0aGlzLnN0cmluZyA9ICcnO1xuICAgIHRoaXMuc25vZGVzID0gW107XG4gIH07XG4gIEhUTUxEb21TdHJpbmdzLnByb3RvdHlwZS5leHRlbmRTdHJpbmcgPSBmdW5jdGlvbiAobm9kZSwgdGV4dCkge1xuICAgIHRoaXMuc25vZGVzLnB1c2goW25vZGUsIHRleHQubGVuZ3RoXSk7XG4gICAgdGhpcy5zdHJpbmcgKz0gdGV4dDtcbiAgfTtcbiAgSFRNTERvbVN0cmluZ3MucHJvdG90eXBlLmhhbmRsZVRleHQgPSBmdW5jdGlvbiAobm9kZSwgaWdub3JlKSB7XG4gICAgaWYgKCFpZ25vcmUpIHtcbiAgICAgIHRoaXMuZXh0ZW5kU3RyaW5nKG5vZGUsIHRoaXMuYWRhcHRvci52YWx1ZShub2RlKSk7XG4gICAgfVxuICAgIHJldHVybiB0aGlzLmFkYXB0b3IubmV4dChub2RlKTtcbiAgfTtcbiAgSFRNTERvbVN0cmluZ3MucHJvdG90eXBlLmhhbmRsZVRhZyA9IGZ1bmN0aW9uIChub2RlLCBpZ25vcmUpIHtcbiAgICBpZiAoIWlnbm9yZSkge1xuICAgICAgdmFyIHRleHQgPSB0aGlzLm9wdGlvbnNbJ2luY2x1ZGVIdG1sVGFncyddW3RoaXMuYWRhcHRvci5raW5kKG5vZGUpXTtcbiAgICAgIHRoaXMuZXh0ZW5kU3RyaW5nKG5vZGUsIHRleHQpO1xuICAgIH1cbiAgICByZXR1cm4gdGhpcy5hZGFwdG9yLm5leHQobm9kZSk7XG4gIH07XG4gIEhUTUxEb21TdHJpbmdzLnByb3RvdHlwZS5oYW5kbGVDb250YWluZXIgPSBmdW5jdGlvbiAobm9kZSwgaWdub3JlKSB7XG4gICAgdGhpcy5wdXNoU3RyaW5nKCk7XG4gICAgdmFyIGNuYW1lID0gdGhpcy5hZGFwdG9yLmdldEF0dHJpYnV0ZShub2RlLCAnY2xhc3MnKSB8fCAnJztcbiAgICB2YXIgdG5hbWUgPSB0aGlzLmFkYXB0b3Iua2luZChub2RlKSB8fCAnJztcbiAgICB2YXIgcHJvY2VzcyA9IHRoaXMucHJvY2Vzc0h0bWxDbGFzcy5leGVjKGNuYW1lKTtcbiAgICB2YXIgbmV4dCA9IG5vZGU7XG4gICAgaWYgKHRoaXMuYWRhcHRvci5maXJzdENoaWxkKG5vZGUpICYmICF0aGlzLmFkYXB0b3IuZ2V0QXR0cmlidXRlKG5vZGUsICdkYXRhLU1KWCcpICYmIChwcm9jZXNzIHx8ICF0aGlzLnNraXBIdG1sVGFncy5leGVjKHRuYW1lKSkpIHtcbiAgICAgIGlmICh0aGlzLmFkYXB0b3IubmV4dChub2RlKSkge1xuICAgICAgICB0aGlzLnN0YWNrLnB1c2goW3RoaXMuYWRhcHRvci5uZXh0KG5vZGUpLCBpZ25vcmVdKTtcbiAgICAgIH1cbiAgICAgIG5leHQgPSB0aGlzLmFkYXB0b3IuZmlyc3RDaGlsZChub2RlKTtcbiAgICAgIGlnbm9yZSA9IChpZ25vcmUgfHwgdGhpcy5pZ25vcmVIdG1sQ2xhc3MuZXhlYyhjbmFtZSkpICYmICFwcm9jZXNzO1xuICAgIH0gZWxzZSB7XG4gICAgICBuZXh0ID0gdGhpcy5hZGFwdG9yLm5leHQobm9kZSk7XG4gICAgfVxuICAgIHJldHVybiBbbmV4dCwgaWdub3JlXTtcbiAgfTtcbiAgSFRNTERvbVN0cmluZ3MucHJvdG90eXBlLmhhbmRsZU90aGVyID0gZnVuY3Rpb24gKG5vZGUsIF9pZ25vcmUpIHtcbiAgICB0aGlzLnB1c2hTdHJpbmcoKTtcbiAgICByZXR1cm4gdGhpcy5hZGFwdG9yLm5leHQobm9kZSk7XG4gIH07XG4gIEhUTUxEb21TdHJpbmdzLnByb3RvdHlwZS5maW5kID0gZnVuY3Rpb24gKG5vZGUpIHtcbiAgICB2YXIgX2EsIF9iO1xuICAgIHRoaXMuaW5pdCgpO1xuICAgIHZhciBzdG9wID0gdGhpcy5hZGFwdG9yLm5leHQobm9kZSk7XG4gICAgdmFyIGlnbm9yZSA9IGZhbHNlO1xuICAgIHZhciBpbmNsdWRlID0gdGhpcy5vcHRpb25zWydpbmNsdWRlSHRtbFRhZ3MnXTtcbiAgICB3aGlsZSAobm9kZSAmJiBub2RlICE9PSBzdG9wKSB7XG4gICAgICB2YXIga2luZCA9IHRoaXMuYWRhcHRvci5raW5kKG5vZGUpO1xuICAgICAgaWYgKGtpbmQgPT09ICcjdGV4dCcpIHtcbiAgICAgICAgbm9kZSA9IHRoaXMuaGFuZGxlVGV4dChub2RlLCBpZ25vcmUpO1xuICAgICAgfSBlbHNlIGlmIChpbmNsdWRlLmhhc093blByb3BlcnR5KGtpbmQpKSB7XG4gICAgICAgIG5vZGUgPSB0aGlzLmhhbmRsZVRhZyhub2RlLCBpZ25vcmUpO1xuICAgICAgfSBlbHNlIGlmIChraW5kKSB7XG4gICAgICAgIF9hID0gX19yZWFkKHRoaXMuaGFuZGxlQ29udGFpbmVyKG5vZGUsIGlnbm9yZSksIDIpLCBub2RlID0gX2FbMF0sIGlnbm9yZSA9IF9hWzFdO1xuICAgICAgfSBlbHNlIHtcbiAgICAgICAgbm9kZSA9IHRoaXMuaGFuZGxlT3RoZXIobm9kZSwgaWdub3JlKTtcbiAgICAgIH1cbiAgICAgIGlmICghbm9kZSAmJiB0aGlzLnN0YWNrLmxlbmd0aCkge1xuICAgICAgICB0aGlzLnB1c2hTdHJpbmcoKTtcbiAgICAgICAgX2IgPSBfX3JlYWQodGhpcy5zdGFjay5wb3AoKSwgMiksIG5vZGUgPSBfYlswXSwgaWdub3JlID0gX2JbMV07XG4gICAgICB9XG4gICAgfVxuICAgIHRoaXMucHVzaFN0cmluZygpO1xuICAgIHZhciByZXN1bHQgPSBbdGhpcy5zdHJpbmdzLCB0aGlzLm5vZGVzXTtcbiAgICB0aGlzLmluaXQoKTtcbiAgICByZXR1cm4gcmVzdWx0O1xuICB9O1xuICBIVE1MRG9tU3RyaW5ncy5PUFRJT05TID0ge1xuICAgIHNraXBIdG1sVGFnczogWydzY3JpcHQnLCAnbm9zY3JpcHQnLCAnc3R5bGUnLCAndGV4dGFyZWEnLCAncHJlJywgJ2NvZGUnLCAnYW5ub3RhdGlvbicsICdhbm5vdGF0aW9uLXhtbCddLFxuICAgIGluY2x1ZGVIdG1sVGFnczoge1xuICAgICAgYnI6ICdcXG4nLFxuICAgICAgd2JyOiAnJyxcbiAgICAgICcjY29tbWVudCc6ICcnXG4gICAgfSxcbiAgICBpZ25vcmVIdG1sQ2xhc3M6ICdtYXRoamF4X2lnbm9yZScsXG4gICAgcHJvY2Vzc0h0bWxDbGFzczogJ21hdGhqYXhfcHJvY2VzcydcbiAgfTtcbiAgcmV0dXJuIEhUTUxEb21TdHJpbmdzO1xufSgpO1xuZXhwb3J0cy5IVE1MRG9tU3RyaW5ncyA9IEhUTUxEb21TdHJpbmdzOyIsIlwidXNlIHN0cmljdFwiO1xuXG52YXIgX19leHRlbmRzID0gdGhpcyAmJiB0aGlzLl9fZXh0ZW5kcyB8fCBmdW5jdGlvbiAoKSB7XG4gIHZhciBleHRlbmRTdGF0aWNzID0gZnVuY3Rpb24gKGQsIGIpIHtcbiAgICBleHRlbmRTdGF0aWNzID0gT2JqZWN0LnNldFByb3RvdHlwZU9mIHx8IHtcbiAgICAgIF9fcHJvdG9fXzogW11cbiAgICB9IGluc3RhbmNlb2YgQXJyYXkgJiYgZnVuY3Rpb24gKGQsIGIpIHtcbiAgICAgIGQuX19wcm90b19fID0gYjtcbiAgICB9IHx8IGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgICBmb3IgKHZhciBwIGluIGIpIGlmIChPYmplY3QucHJvdG90eXBlLmhhc093blByb3BlcnR5LmNhbGwoYiwgcCkpIGRbcF0gPSBiW3BdO1xuICAgIH07XG4gICAgcmV0dXJuIGV4dGVuZFN0YXRpY3MoZCwgYik7XG4gIH07XG4gIHJldHVybiBmdW5jdGlvbiAoZCwgYikge1xuICAgIGlmICh0eXBlb2YgYiAhPT0gXCJmdW5jdGlvblwiICYmIGIgIT09IG51bGwpIHRocm93IG5ldyBUeXBlRXJyb3IoXCJDbGFzcyBleHRlbmRzIHZhbHVlIFwiICsgU3RyaW5nKGIpICsgXCIgaXMgbm90IGEgY29uc3RydWN0b3Igb3IgbnVsbFwiKTtcbiAgICBleHRlbmRTdGF0aWNzKGQsIGIpO1xuICAgIGZ1bmN0aW9uIF9fKCkge1xuICAgICAgdGhpcy5jb25zdHJ1Y3RvciA9IGQ7XG4gICAgfVxuICAgIGQucHJvdG90eXBlID0gYiA9PT0gbnVsbCA/IE9iamVjdC5jcmVhdGUoYikgOiAoX18ucHJvdG90eXBlID0gYi5wcm90b3R5cGUsIG5ldyBfXygpKTtcbiAgfTtcbn0oKTtcbnZhciBfX3ZhbHVlcyA9IHRoaXMgJiYgdGhpcy5fX3ZhbHVlcyB8fCBmdW5jdGlvbiAobykge1xuICB2YXIgcyA9IHR5cGVvZiBTeW1ib2wgPT09IFwiZnVuY3Rpb25cIiAmJiBTeW1ib2wuaXRlcmF0b3IsXG4gICAgbSA9IHMgJiYgb1tzXSxcbiAgICBpID0gMDtcbiAgaWYgKG0pIHJldHVybiBtLmNhbGwobyk7XG4gIGlmIChvICYmIHR5cGVvZiBvLmxlbmd0aCA9PT0gXCJudW1iZXJcIikgcmV0dXJuIHtcbiAgICBuZXh0OiBmdW5jdGlvbiAoKSB7XG4gICAgICBpZiAobyAmJiBpID49IG8ubGVuZ3RoKSBvID0gdm9pZCAwO1xuICAgICAgcmV0dXJuIHtcbiAgICAgICAgdmFsdWU6IG8gJiYgb1tpKytdLFxuICAgICAgICBkb25lOiAhb1xuICAgICAgfTtcbiAgICB9XG4gIH07XG4gIHRocm93IG5ldyBUeXBlRXJyb3IocyA/IFwiT2JqZWN0IGlzIG5vdCBpdGVyYWJsZS5cIiA6IFwiU3ltYm9sLml0ZXJhdG9yIGlzIG5vdCBkZWZpbmVkLlwiKTtcbn07XG52YXIgX19yZWFkID0gdGhpcyAmJiB0aGlzLl9fcmVhZCB8fCBmdW5jdGlvbiAobywgbikge1xuICB2YXIgbSA9IHR5cGVvZiBTeW1ib2wgPT09IFwiZnVuY3Rpb25cIiAmJiBvW1N5bWJvbC5pdGVyYXRvcl07XG4gIGlmICghbSkgcmV0dXJuIG87XG4gIHZhciBpID0gbS5jYWxsKG8pLFxuICAgIHIsXG4gICAgYXIgPSBbXSxcbiAgICBlO1xuICB0cnkge1xuICAgIHdoaWxlICgobiA9PT0gdm9pZCAwIHx8IG4tLSA+IDApICYmICEociA9IGkubmV4dCgpKS5kb25lKSBhci5wdXNoKHIudmFsdWUpO1xuICB9IGNhdGNoIChlcnJvcikge1xuICAgIGUgPSB7XG4gICAgICBlcnJvcjogZXJyb3JcbiAgICB9O1xuICB9IGZpbmFsbHkge1xuICAgIHRyeSB7XG4gICAgICBpZiAociAmJiAhci5kb25lICYmIChtID0gaVtcInJldHVyblwiXSkpIG0uY2FsbChpKTtcbiAgICB9IGZpbmFsbHkge1xuICAgICAgaWYgKGUpIHRocm93IGUuZXJyb3I7XG4gICAgfVxuICB9XG4gIHJldHVybiBhcjtcbn07XG52YXIgX19zcHJlYWRBcnJheSA9IHRoaXMgJiYgdGhpcy5fX3NwcmVhZEFycmF5IHx8IGZ1bmN0aW9uICh0bywgZnJvbSwgcGFjaykge1xuICBpZiAocGFjayB8fCBhcmd1bWVudHMubGVuZ3RoID09PSAyKSBmb3IgKHZhciBpID0gMCwgbCA9IGZyb20ubGVuZ3RoLCBhcjsgaSA8IGw7IGkrKykge1xuICAgIGlmIChhciB8fCAhKGkgaW4gZnJvbSkpIHtcbiAgICAgIGlmICghYXIpIGFyID0gQXJyYXkucHJvdG90eXBlLnNsaWNlLmNhbGwoZnJvbSwgMCwgaSk7XG4gICAgICBhcltpXSA9IGZyb21baV07XG4gICAgfVxuICB9XG4gIHJldHVybiB0by5jb25jYXQoYXIgfHwgQXJyYXkucHJvdG90eXBlLnNsaWNlLmNhbGwoZnJvbSkpO1xufTtcbk9iamVjdC5kZWZpbmVQcm9wZXJ0eShleHBvcnRzLCBcIl9fZXNNb2R1bGVcIiwge1xuICB2YWx1ZTogdHJ1ZVxufSk7XG5leHBvcnRzLkZ1bmN0aW9uTGlzdCA9IHZvaWQgMDtcbnZhciBQcmlvcml0aXplZExpc3RfanNfMSA9IHJlcXVpcmUoXCIuL1ByaW9yaXRpemVkTGlzdC5qc1wiKTtcbnZhciBGdW5jdGlvbkxpc3QgPSBmdW5jdGlvbiAoX3N1cGVyKSB7XG4gIF9fZXh0ZW5kcyhGdW5jdGlvbkxpc3QsIF9zdXBlcik7XG4gIGZ1bmN0aW9uIEZ1bmN0aW9uTGlzdCgpIHtcbiAgICByZXR1cm4gX3N1cGVyICE9PSBudWxsICYmIF9zdXBlci5hcHBseSh0aGlzLCBhcmd1bWVudHMpIHx8IHRoaXM7XG4gIH1cbiAgRnVuY3Rpb25MaXN0LnByb3RvdHlwZS5leGVjdXRlID0gZnVuY3Rpb24gKCkge1xuICAgIHZhciBlXzEsIF9hO1xuICAgIHZhciBkYXRhID0gW107XG4gICAgZm9yICh2YXIgX2kgPSAwOyBfaSA8IGFyZ3VtZW50cy5sZW5ndGg7IF9pKyspIHtcbiAgICAgIGRhdGFbX2ldID0gYXJndW1lbnRzW19pXTtcbiAgICB9XG4gICAgdHJ5IHtcbiAgICAgIGZvciAodmFyIF9iID0gX192YWx1ZXModGhpcyksIF9jID0gX2IubmV4dCgpOyAhX2MuZG9uZTsgX2MgPSBfYi5uZXh0KCkpIHtcbiAgICAgICAgdmFyIGl0ZW0gPSBfYy52YWx1ZTtcbiAgICAgICAgdmFyIHJlc3VsdCA9IGl0ZW0uaXRlbS5hcHBseShpdGVtLCBfX3NwcmVhZEFycmF5KFtdLCBfX3JlYWQoZGF0YSksIGZhbHNlKSk7XG4gICAgICAgIGlmIChyZXN1bHQgPT09IGZhbHNlKSB7XG4gICAgICAgICAgcmV0dXJuIGZhbHNlO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgfSBjYXRjaCAoZV8xXzEpIHtcbiAgICAgIGVfMSA9IHtcbiAgICAgICAgZXJyb3I6IGVfMV8xXG4gICAgICB9O1xuICAgIH0gZmluYWxseSB7XG4gICAgICB0cnkge1xuICAgICAgICBpZiAoX2MgJiYgIV9jLmRvbmUgJiYgKF9hID0gX2IucmV0dXJuKSkgX2EuY2FsbChfYik7XG4gICAgICB9IGZpbmFsbHkge1xuICAgICAgICBpZiAoZV8xKSB0aHJvdyBlXzEuZXJyb3I7XG4gICAgICB9XG4gICAgfVxuICAgIHJldHVybiB0cnVlO1xuICB9O1xuICBGdW5jdGlvbkxpc3QucHJvdG90eXBlLmFzeW5jRXhlY3V0ZSA9IGZ1bmN0aW9uICgpIHtcbiAgICB2YXIgZGF0YSA9IFtdO1xuICAgIGZvciAodmFyIF9pID0gMDsgX2kgPCBhcmd1bWVudHMubGVuZ3RoOyBfaSsrKSB7XG4gICAgICBkYXRhW19pXSA9IGFyZ3VtZW50c1tfaV07XG4gICAgfVxuICAgIHZhciBpID0gLTE7XG4gICAgdmFyIGl0ZW1zID0gdGhpcy5pdGVtcztcbiAgICByZXR1cm4gbmV3IFByb21pc2UoZnVuY3Rpb24gKG9rLCBmYWlsKSB7XG4gICAgICAoZnVuY3Rpb24gZXhlY3V0ZSgpIHtcbiAgICAgICAgdmFyIF9hO1xuICAgICAgICB3aGlsZSAoKytpIDwgaXRlbXMubGVuZ3RoKSB7XG4gICAgICAgICAgdmFyIHJlc3VsdCA9IChfYSA9IGl0ZW1zW2ldKS5pdGVtLmFwcGx5KF9hLCBfX3NwcmVhZEFycmF5KFtdLCBfX3JlYWQoZGF0YSksIGZhbHNlKSk7XG4gICAgICAgICAgaWYgKHJlc3VsdCBpbnN0YW5jZW9mIFByb21pc2UpIHtcbiAgICAgICAgICAgIHJlc3VsdC50aGVuKGV4ZWN1dGUpLmNhdGNoKGZ1bmN0aW9uIChlcnIpIHtcbiAgICAgICAgICAgICAgcmV0dXJuIGZhaWwoZXJyKTtcbiAgICAgICAgICAgIH0pO1xuICAgICAgICAgICAgcmV0dXJuO1xuICAgICAgICAgIH1cbiAgICAgICAgICBpZiAocmVzdWx0ID09PSBmYWxzZSkge1xuICAgICAgICAgICAgb2soZmFsc2UpO1xuICAgICAgICAgICAgcmV0dXJuO1xuICAgICAgICAgIH1cbiAgICAgICAgfVxuICAgICAgICBvayh0cnVlKTtcbiAgICAgIH0pKCk7XG4gICAgfSk7XG4gIH07XG4gIHJldHVybiBGdW5jdGlvbkxpc3Q7XG59KFByaW9yaXRpemVkTGlzdF9qc18xLlByaW9yaXRpemVkTGlzdCk7XG5leHBvcnRzLkZ1bmN0aW9uTGlzdCA9IEZ1bmN0aW9uTGlzdDsiLCJcInVzZSBzdHJpY3RcIjtcblxudmFyIF9fZXh0ZW5kcyA9IHRoaXMgJiYgdGhpcy5fX2V4dGVuZHMgfHwgZnVuY3Rpb24gKCkge1xuICB2YXIgZXh0ZW5kU3RhdGljcyA9IGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgZXh0ZW5kU3RhdGljcyA9IE9iamVjdC5zZXRQcm90b3R5cGVPZiB8fCB7XG4gICAgICBfX3Byb3RvX186IFtdXG4gICAgfSBpbnN0YW5jZW9mIEFycmF5ICYmIGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgICBkLl9fcHJvdG9fXyA9IGI7XG4gICAgfSB8fCBmdW5jdGlvbiAoZCwgYikge1xuICAgICAgZm9yICh2YXIgcCBpbiBiKSBpZiAoT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsKGIsIHApKSBkW3BdID0gYltwXTtcbiAgICB9O1xuICAgIHJldHVybiBleHRlbmRTdGF0aWNzKGQsIGIpO1xuICB9O1xuICByZXR1cm4gZnVuY3Rpb24gKGQsIGIpIHtcbiAgICBpZiAodHlwZW9mIGIgIT09IFwiZnVuY3Rpb25cIiAmJiBiICE9PSBudWxsKSB0aHJvdyBuZXcgVHlwZUVycm9yKFwiQ2xhc3MgZXh0ZW5kcyB2YWx1ZSBcIiArIFN0cmluZyhiKSArIFwiIGlzIG5vdCBhIGNvbnN0cnVjdG9yIG9yIG51bGxcIik7XG4gICAgZXh0ZW5kU3RhdGljcyhkLCBiKTtcbiAgICBmdW5jdGlvbiBfXygpIHtcbiAgICAgIHRoaXMuY29uc3RydWN0b3IgPSBkO1xuICAgIH1cbiAgICBkLnByb3RvdHlwZSA9IGIgPT09IG51bGwgPyBPYmplY3QuY3JlYXRlKGIpIDogKF9fLnByb3RvdHlwZSA9IGIucHJvdG90eXBlLCBuZXcgX18oKSk7XG4gIH07XG59KCk7XG52YXIgX192YWx1ZXMgPSB0aGlzICYmIHRoaXMuX192YWx1ZXMgfHwgZnVuY3Rpb24gKG8pIHtcbiAgdmFyIHMgPSB0eXBlb2YgU3ltYm9sID09PSBcImZ1bmN0aW9uXCIgJiYgU3ltYm9sLml0ZXJhdG9yLFxuICAgIG0gPSBzICYmIG9bc10sXG4gICAgaSA9IDA7XG4gIGlmIChtKSByZXR1cm4gbS5jYWxsKG8pO1xuICBpZiAobyAmJiB0eXBlb2Ygby5sZW5ndGggPT09IFwibnVtYmVyXCIpIHJldHVybiB7XG4gICAgbmV4dDogZnVuY3Rpb24gKCkge1xuICAgICAgaWYgKG8gJiYgaSA+PSBvLmxlbmd0aCkgbyA9IHZvaWQgMDtcbiAgICAgIHJldHVybiB7XG4gICAgICAgIHZhbHVlOiBvICYmIG9baSsrXSxcbiAgICAgICAgZG9uZTogIW9cbiAgICAgIH07XG4gICAgfVxuICB9O1xuICB0aHJvdyBuZXcgVHlwZUVycm9yKHMgPyBcIk9iamVjdCBpcyBub3QgaXRlcmFibGUuXCIgOiBcIlN5bWJvbC5pdGVyYXRvciBpcyBub3QgZGVmaW5lZC5cIik7XG59O1xudmFyIF9fcmVhZCA9IHRoaXMgJiYgdGhpcy5fX3JlYWQgfHwgZnVuY3Rpb24gKG8sIG4pIHtcbiAgdmFyIG0gPSB0eXBlb2YgU3ltYm9sID09PSBcImZ1bmN0aW9uXCIgJiYgb1tTeW1ib2wuaXRlcmF0b3JdO1xuICBpZiAoIW0pIHJldHVybiBvO1xuICB2YXIgaSA9IG0uY2FsbChvKSxcbiAgICByLFxuICAgIGFyID0gW10sXG4gICAgZTtcbiAgdHJ5IHtcbiAgICB3aGlsZSAoKG4gPT09IHZvaWQgMCB8fCBuLS0gPiAwKSAmJiAhKHIgPSBpLm5leHQoKSkuZG9uZSkgYXIucHVzaChyLnZhbHVlKTtcbiAgfSBjYXRjaCAoZXJyb3IpIHtcbiAgICBlID0ge1xuICAgICAgZXJyb3I6IGVycm9yXG4gICAgfTtcbiAgfSBmaW5hbGx5IHtcbiAgICB0cnkge1xuICAgICAgaWYgKHIgJiYgIXIuZG9uZSAmJiAobSA9IGlbXCJyZXR1cm5cIl0pKSBtLmNhbGwoaSk7XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIGlmIChlKSB0aHJvdyBlLmVycm9yO1xuICAgIH1cbiAgfVxuICByZXR1cm4gYXI7XG59O1xudmFyIF9fc3ByZWFkQXJyYXkgPSB0aGlzICYmIHRoaXMuX19zcHJlYWRBcnJheSB8fCBmdW5jdGlvbiAodG8sIGZyb20sIHBhY2spIHtcbiAgaWYgKHBhY2sgfHwgYXJndW1lbnRzLmxlbmd0aCA9PT0gMikgZm9yICh2YXIgaSA9IDAsIGwgPSBmcm9tLmxlbmd0aCwgYXI7IGkgPCBsOyBpKyspIHtcbiAgICBpZiAoYXIgfHwgIShpIGluIGZyb20pKSB7XG4gICAgICBpZiAoIWFyKSBhciA9IEFycmF5LnByb3RvdHlwZS5zbGljZS5jYWxsKGZyb20sIDAsIGkpO1xuICAgICAgYXJbaV0gPSBmcm9tW2ldO1xuICAgIH1cbiAgfVxuICByZXR1cm4gdG8uY29uY2F0KGFyIHx8IEFycmF5LnByb3RvdHlwZS5zbGljZS5jYWxsKGZyb20pKTtcbn07XG5PYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgXCJfX2VzTW9kdWxlXCIsIHtcbiAgdmFsdWU6IHRydWVcbn0pO1xuZXhwb3J0cy5CaXRGaWVsZENsYXNzID0gZXhwb3J0cy5CaXRGaWVsZCA9IHZvaWQgMDtcbnZhciBCaXRGaWVsZCA9IGZ1bmN0aW9uICgpIHtcbiAgZnVuY3Rpb24gQml0RmllbGQoKSB7XG4gICAgdGhpcy5iaXRzID0gMDtcbiAgfVxuICBCaXRGaWVsZC5hbGxvY2F0ZSA9IGZ1bmN0aW9uICgpIHtcbiAgICB2YXIgZV8xLCBfYTtcbiAgICB2YXIgbmFtZXMgPSBbXTtcbiAgICBmb3IgKHZhciBfaSA9IDA7IF9pIDwgYXJndW1lbnRzLmxlbmd0aDsgX2krKykge1xuICAgICAgbmFtZXNbX2ldID0gYXJndW1lbnRzW19pXTtcbiAgICB9XG4gICAgdHJ5IHtcbiAgICAgIGZvciAodmFyIG5hbWVzXzEgPSBfX3ZhbHVlcyhuYW1lcyksIG5hbWVzXzFfMSA9IG5hbWVzXzEubmV4dCgpOyAhbmFtZXNfMV8xLmRvbmU7IG5hbWVzXzFfMSA9IG5hbWVzXzEubmV4dCgpKSB7XG4gICAgICAgIHZhciBuYW1lXzEgPSBuYW1lc18xXzEudmFsdWU7XG4gICAgICAgIGlmICh0aGlzLmhhcyhuYW1lXzEpKSB7XG4gICAgICAgICAgdGhyb3cgbmV3IEVycm9yKCdCaXQgYWxyZWFkeSBhbGxvY2F0ZWQgZm9yICcgKyBuYW1lXzEpO1xuICAgICAgICB9XG4gICAgICAgIGlmICh0aGlzLm5leHQgPT09IEJpdEZpZWxkLk1BWEJJVCkge1xuICAgICAgICAgIHRocm93IG5ldyBFcnJvcignTWF4aW11bSBudW1iZXIgb2YgYml0cyBhbHJlYWR5IGFsbG9jYXRlZCcpO1xuICAgICAgICB9XG4gICAgICAgIHRoaXMubmFtZXMuc2V0KG5hbWVfMSwgdGhpcy5uZXh0KTtcbiAgICAgICAgdGhpcy5uZXh0IDw8PSAxO1xuICAgICAgfVxuICAgIH0gY2F0Y2ggKGVfMV8xKSB7XG4gICAgICBlXzEgPSB7XG4gICAgICAgIGVycm9yOiBlXzFfMVxuICAgICAgfTtcbiAgICB9IGZpbmFsbHkge1xuICAgICAgdHJ5IHtcbiAgICAgICAgaWYgKG5hbWVzXzFfMSAmJiAhbmFtZXNfMV8xLmRvbmUgJiYgKF9hID0gbmFtZXNfMS5yZXR1cm4pKSBfYS5jYWxsKG5hbWVzXzEpO1xuICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgaWYgKGVfMSkgdGhyb3cgZV8xLmVycm9yO1xuICAgICAgfVxuICAgIH1cbiAgfTtcbiAgQml0RmllbGQuaGFzID0gZnVuY3Rpb24gKG5hbWUpIHtcbiAgICByZXR1cm4gdGhpcy5uYW1lcy5oYXMobmFtZSk7XG4gIH07XG4gIEJpdEZpZWxkLnByb3RvdHlwZS5zZXQgPSBmdW5jdGlvbiAobmFtZSkge1xuICAgIHRoaXMuYml0cyB8PSB0aGlzLmdldEJpdChuYW1lKTtcbiAgfTtcbiAgQml0RmllbGQucHJvdG90eXBlLmNsZWFyID0gZnVuY3Rpb24gKG5hbWUpIHtcbiAgICB0aGlzLmJpdHMgJj0gfnRoaXMuZ2V0Qml0KG5hbWUpO1xuICB9O1xuICBCaXRGaWVsZC5wcm90b3R5cGUuaXNTZXQgPSBmdW5jdGlvbiAobmFtZSkge1xuICAgIHJldHVybiAhISh0aGlzLmJpdHMgJiB0aGlzLmdldEJpdChuYW1lKSk7XG4gIH07XG4gIEJpdEZpZWxkLnByb3RvdHlwZS5yZXNldCA9IGZ1bmN0aW9uICgpIHtcbiAgICB0aGlzLmJpdHMgPSAwO1xuICB9O1xuICBCaXRGaWVsZC5wcm90b3R5cGUuZ2V0Qml0ID0gZnVuY3Rpb24gKG5hbWUpIHtcbiAgICB2YXIgYml0ID0gdGhpcy5jb25zdHJ1Y3Rvci5uYW1lcy5nZXQobmFtZSk7XG4gICAgaWYgKCFiaXQpIHtcbiAgICAgIHRocm93IG5ldyBFcnJvcignVW5rbm93biBiaXQtZmllbGQgbmFtZTogJyArIG5hbWUpO1xuICAgIH1cbiAgICByZXR1cm4gYml0O1xuICB9O1xuICBCaXRGaWVsZC5NQVhCSVQgPSAxIDw8IDMxO1xuICBCaXRGaWVsZC5uZXh0ID0gMTtcbiAgQml0RmllbGQubmFtZXMgPSBuZXcgTWFwKCk7XG4gIHJldHVybiBCaXRGaWVsZDtcbn0oKTtcbmV4cG9ydHMuQml0RmllbGQgPSBCaXRGaWVsZDtcbmZ1bmN0aW9uIEJpdEZpZWxkQ2xhc3MoKSB7XG4gIHZhciBuYW1lcyA9IFtdO1xuICBmb3IgKHZhciBfaSA9IDA7IF9pIDwgYXJndW1lbnRzLmxlbmd0aDsgX2krKykge1xuICAgIG5hbWVzW19pXSA9IGFyZ3VtZW50c1tfaV07XG4gIH1cbiAgdmFyIEJpdHMgPSBmdW5jdGlvbiAoX3N1cGVyKSB7XG4gICAgX19leHRlbmRzKEJpdHMsIF9zdXBlcik7XG4gICAgZnVuY3Rpb24gQml0cygpIHtcbiAgICAgIHJldHVybiBfc3VwZXIgIT09IG51bGwgJiYgX3N1cGVyLmFwcGx5KHRoaXMsIGFyZ3VtZW50cykgfHwgdGhpcztcbiAgICB9XG4gICAgcmV0dXJuIEJpdHM7XG4gIH0oQml0RmllbGQpO1xuICBCaXRzLmFsbG9jYXRlLmFwcGx5KEJpdHMsIF9fc3ByZWFkQXJyYXkoW10sIF9fcmVhZChuYW1lcyksIGZhbHNlKSk7XG4gIHJldHVybiBCaXRzO1xufVxuZXhwb3J0cy5CaXRGaWVsZENsYXNzID0gQml0RmllbGRDbGFzczsiLCJcInVzZSBzdHJpY3RcIjtcblxudmFyIF9fZXh0ZW5kcyA9IHRoaXMgJiYgdGhpcy5fX2V4dGVuZHMgfHwgZnVuY3Rpb24gKCkge1xuICB2YXIgZXh0ZW5kU3RhdGljcyA9IGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgZXh0ZW5kU3RhdGljcyA9IE9iamVjdC5zZXRQcm90b3R5cGVPZiB8fCB7XG4gICAgICBfX3Byb3RvX186IFtdXG4gICAgfSBpbnN0YW5jZW9mIEFycmF5ICYmIGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgICBkLl9fcHJvdG9fXyA9IGI7XG4gICAgfSB8fCBmdW5jdGlvbiAoZCwgYikge1xuICAgICAgZm9yICh2YXIgcCBpbiBiKSBpZiAoT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsKGIsIHApKSBkW3BdID0gYltwXTtcbiAgICB9O1xuICAgIHJldHVybiBleHRlbmRTdGF0aWNzKGQsIGIpO1xuICB9O1xuICByZXR1cm4gZnVuY3Rpb24gKGQsIGIpIHtcbiAgICBpZiAodHlwZW9mIGIgIT09IFwiZnVuY3Rpb25cIiAmJiBiICE9PSBudWxsKSB0aHJvdyBuZXcgVHlwZUVycm9yKFwiQ2xhc3MgZXh0ZW5kcyB2YWx1ZSBcIiArIFN0cmluZyhiKSArIFwiIGlzIG5vdCBhIGNvbnN0cnVjdG9yIG9yIG51bGxcIik7XG4gICAgZXh0ZW5kU3RhdGljcyhkLCBiKTtcbiAgICBmdW5jdGlvbiBfXygpIHtcbiAgICAgIHRoaXMuY29uc3RydWN0b3IgPSBkO1xuICAgIH1cbiAgICBkLnByb3RvdHlwZSA9IGIgPT09IG51bGwgPyBPYmplY3QuY3JlYXRlKGIpIDogKF9fLnByb3RvdHlwZSA9IGIucHJvdG90eXBlLCBuZXcgX18oKSk7XG4gIH07XG59KCk7XG5PYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgXCJfX2VzTW9kdWxlXCIsIHtcbiAgdmFsdWU6IHRydWVcbn0pO1xuZXhwb3J0cy5IVE1MTWF0aExpc3QgPSB2b2lkIDA7XG52YXIgTWF0aExpc3RfanNfMSA9IHJlcXVpcmUoXCIuLi8uLi9jb3JlL01hdGhMaXN0LmpzXCIpO1xudmFyIEhUTUxNYXRoTGlzdCA9IGZ1bmN0aW9uIChfc3VwZXIpIHtcbiAgX19leHRlbmRzKEhUTUxNYXRoTGlzdCwgX3N1cGVyKTtcbiAgZnVuY3Rpb24gSFRNTE1hdGhMaXN0KCkge1xuICAgIHJldHVybiBfc3VwZXIgIT09IG51bGwgJiYgX3N1cGVyLmFwcGx5KHRoaXMsIGFyZ3VtZW50cykgfHwgdGhpcztcbiAgfVxuICByZXR1cm4gSFRNTE1hdGhMaXN0O1xufShNYXRoTGlzdF9qc18xLkFic3RyYWN0TWF0aExpc3QpO1xuZXhwb3J0cy5IVE1MTWF0aExpc3QgPSBIVE1MTWF0aExpc3Q7IiwiXCJ1c2Ugc3RyaWN0XCI7XG5cbnZhciBfX2V4dGVuZHMgPSB0aGlzICYmIHRoaXMuX19leHRlbmRzIHx8IGZ1bmN0aW9uICgpIHtcbiAgdmFyIGV4dGVuZFN0YXRpY3MgPSBmdW5jdGlvbiAoZCwgYikge1xuICAgIGV4dGVuZFN0YXRpY3MgPSBPYmplY3Quc2V0UHJvdG90eXBlT2YgfHwge1xuICAgICAgX19wcm90b19fOiBbXVxuICAgIH0gaW5zdGFuY2VvZiBBcnJheSAmJiBmdW5jdGlvbiAoZCwgYikge1xuICAgICAgZC5fX3Byb3RvX18gPSBiO1xuICAgIH0gfHwgZnVuY3Rpb24gKGQsIGIpIHtcbiAgICAgIGZvciAodmFyIHAgaW4gYikgaWYgKE9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbChiLCBwKSkgZFtwXSA9IGJbcF07XG4gICAgfTtcbiAgICByZXR1cm4gZXh0ZW5kU3RhdGljcyhkLCBiKTtcbiAgfTtcbiAgcmV0dXJuIGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgaWYgKHR5cGVvZiBiICE9PSBcImZ1bmN0aW9uXCIgJiYgYiAhPT0gbnVsbCkgdGhyb3cgbmV3IFR5cGVFcnJvcihcIkNsYXNzIGV4dGVuZHMgdmFsdWUgXCIgKyBTdHJpbmcoYikgKyBcIiBpcyBub3QgYSBjb25zdHJ1Y3RvciBvciBudWxsXCIpO1xuICAgIGV4dGVuZFN0YXRpY3MoZCwgYik7XG4gICAgZnVuY3Rpb24gX18oKSB7XG4gICAgICB0aGlzLmNvbnN0cnVjdG9yID0gZDtcbiAgICB9XG4gICAgZC5wcm90b3R5cGUgPSBiID09PSBudWxsID8gT2JqZWN0LmNyZWF0ZShiKSA6IChfXy5wcm90b3R5cGUgPSBiLnByb3RvdHlwZSwgbmV3IF9fKCkpO1xuICB9O1xufSgpO1xuT2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFwiX19lc01vZHVsZVwiLCB7XG4gIHZhbHVlOiB0cnVlXG59KTtcbmV4cG9ydHMuQWJzdHJhY3RIYW5kbGVyID0gdm9pZCAwO1xudmFyIE1hdGhEb2N1bWVudF9qc18xID0gcmVxdWlyZShcIi4vTWF0aERvY3VtZW50LmpzXCIpO1xudmFyIERlZmF1bHRNYXRoRG9jdW1lbnQgPSBmdW5jdGlvbiAoX3N1cGVyKSB7XG4gIF9fZXh0ZW5kcyhEZWZhdWx0TWF0aERvY3VtZW50LCBfc3VwZXIpO1xuICBmdW5jdGlvbiBEZWZhdWx0TWF0aERvY3VtZW50KCkge1xuICAgIHJldHVybiBfc3VwZXIgIT09IG51bGwgJiYgX3N1cGVyLmFwcGx5KHRoaXMsIGFyZ3VtZW50cykgfHwgdGhpcztcbiAgfVxuICByZXR1cm4gRGVmYXVsdE1hdGhEb2N1bWVudDtcbn0oTWF0aERvY3VtZW50X2pzXzEuQWJzdHJhY3RNYXRoRG9jdW1lbnQpO1xudmFyIEFic3RyYWN0SGFuZGxlciA9IGZ1bmN0aW9uICgpIHtcbiAgZnVuY3Rpb24gQWJzdHJhY3RIYW5kbGVyKGFkYXB0b3IsIHByaW9yaXR5KSB7XG4gICAgaWYgKHByaW9yaXR5ID09PSB2b2lkIDApIHtcbiAgICAgIHByaW9yaXR5ID0gNTtcbiAgICB9XG4gICAgdGhpcy5kb2N1bWVudENsYXNzID0gRGVmYXVsdE1hdGhEb2N1bWVudDtcbiAgICB0aGlzLmFkYXB0b3IgPSBhZGFwdG9yO1xuICAgIHRoaXMucHJpb3JpdHkgPSBwcmlvcml0eTtcbiAgfVxuICBPYmplY3QuZGVmaW5lUHJvcGVydHkoQWJzdHJhY3RIYW5kbGVyLnByb3RvdHlwZSwgXCJuYW1lXCIsIHtcbiAgICBnZXQ6IGZ1bmN0aW9uICgpIHtcbiAgICAgIHJldHVybiB0aGlzLmNvbnN0cnVjdG9yLk5BTUU7XG4gICAgfSxcbiAgICBlbnVtZXJhYmxlOiBmYWxzZSxcbiAgICBjb25maWd1cmFibGU6IHRydWVcbiAgfSk7XG4gIEFic3RyYWN0SGFuZGxlci5wcm90b3R5cGUuaGFuZGxlc0RvY3VtZW50ID0gZnVuY3Rpb24gKF9kb2N1bWVudCkge1xuICAgIHJldHVybiBmYWxzZTtcbiAgfTtcbiAgQWJzdHJhY3RIYW5kbGVyLnByb3RvdHlwZS5jcmVhdGUgPSBmdW5jdGlvbiAoZG9jdW1lbnQsIG9wdGlvbnMpIHtcbiAgICByZXR1cm4gbmV3IHRoaXMuZG9jdW1lbnRDbGFzcyhkb2N1bWVudCwgdGhpcy5hZGFwdG9yLCBvcHRpb25zKTtcbiAgfTtcbiAgQWJzdHJhY3RIYW5kbGVyLk5BTUUgPSAnZ2VuZXJpYyc7XG4gIHJldHVybiBBYnN0cmFjdEhhbmRsZXI7XG59KCk7XG5leHBvcnRzLkFic3RyYWN0SGFuZGxlciA9IEFic3RyYWN0SGFuZGxlcjsiLCJcInVzZSBzdHJpY3RcIjtcblxudmFyIF9fZ2VuZXJhdG9yID0gdGhpcyAmJiB0aGlzLl9fZ2VuZXJhdG9yIHx8IGZ1bmN0aW9uICh0aGlzQXJnLCBib2R5KSB7XG4gIHZhciBfID0ge1xuICAgICAgbGFiZWw6IDAsXG4gICAgICBzZW50OiBmdW5jdGlvbiAoKSB7XG4gICAgICAgIGlmICh0WzBdICYgMSkgdGhyb3cgdFsxXTtcbiAgICAgICAgcmV0dXJuIHRbMV07XG4gICAgICB9LFxuICAgICAgdHJ5czogW10sXG4gICAgICBvcHM6IFtdXG4gICAgfSxcbiAgICBmLFxuICAgIHksXG4gICAgdCxcbiAgICBnO1xuICByZXR1cm4gZyA9IHtcbiAgICBuZXh0OiB2ZXJiKDApLFxuICAgIFwidGhyb3dcIjogdmVyYigxKSxcbiAgICBcInJldHVyblwiOiB2ZXJiKDIpXG4gIH0sIHR5cGVvZiBTeW1ib2wgPT09IFwiZnVuY3Rpb25cIiAmJiAoZ1tTeW1ib2wuaXRlcmF0b3JdID0gZnVuY3Rpb24gKCkge1xuICAgIHJldHVybiB0aGlzO1xuICB9KSwgZztcbiAgZnVuY3Rpb24gdmVyYihuKSB7XG4gICAgcmV0dXJuIGZ1bmN0aW9uICh2KSB7XG4gICAgICByZXR1cm4gc3RlcChbbiwgdl0pO1xuICAgIH07XG4gIH1cbiAgZnVuY3Rpb24gc3RlcChvcCkge1xuICAgIGlmIChmKSB0aHJvdyBuZXcgVHlwZUVycm9yKFwiR2VuZXJhdG9yIGlzIGFscmVhZHkgZXhlY3V0aW5nLlwiKTtcbiAgICB3aGlsZSAoXykgdHJ5IHtcbiAgICAgIGlmIChmID0gMSwgeSAmJiAodCA9IG9wWzBdICYgMiA/IHlbXCJyZXR1cm5cIl0gOiBvcFswXSA/IHlbXCJ0aHJvd1wiXSB8fCAoKHQgPSB5W1wicmV0dXJuXCJdKSAmJiB0LmNhbGwoeSksIDApIDogeS5uZXh0KSAmJiAhKHQgPSB0LmNhbGwoeSwgb3BbMV0pKS5kb25lKSByZXR1cm4gdDtcbiAgICAgIGlmICh5ID0gMCwgdCkgb3AgPSBbb3BbMF0gJiAyLCB0LnZhbHVlXTtcbiAgICAgIHN3aXRjaCAob3BbMF0pIHtcbiAgICAgICAgY2FzZSAwOlxuICAgICAgICBjYXNlIDE6XG4gICAgICAgICAgdCA9IG9wO1xuICAgICAgICAgIGJyZWFrO1xuICAgICAgICBjYXNlIDQ6XG4gICAgICAgICAgXy5sYWJlbCsrO1xuICAgICAgICAgIHJldHVybiB7XG4gICAgICAgICAgICB2YWx1ZTogb3BbMV0sXG4gICAgICAgICAgICBkb25lOiBmYWxzZVxuICAgICAgICAgIH07XG4gICAgICAgIGNhc2UgNTpcbiAgICAgICAgICBfLmxhYmVsKys7XG4gICAgICAgICAgeSA9IG9wWzFdO1xuICAgICAgICAgIG9wID0gWzBdO1xuICAgICAgICAgIGNvbnRpbnVlO1xuICAgICAgICBjYXNlIDc6XG4gICAgICAgICAgb3AgPSBfLm9wcy5wb3AoKTtcbiAgICAgICAgICBfLnRyeXMucG9wKCk7XG4gICAgICAgICAgY29udGludWU7XG4gICAgICAgIGRlZmF1bHQ6XG4gICAgICAgICAgaWYgKCEodCA9IF8udHJ5cywgdCA9IHQubGVuZ3RoID4gMCAmJiB0W3QubGVuZ3RoIC0gMV0pICYmIChvcFswXSA9PT0gNiB8fCBvcFswXSA9PT0gMikpIHtcbiAgICAgICAgICAgIF8gPSAwO1xuICAgICAgICAgICAgY29udGludWU7XG4gICAgICAgICAgfVxuICAgICAgICAgIGlmIChvcFswXSA9PT0gMyAmJiAoIXQgfHwgb3BbMV0gPiB0WzBdICYmIG9wWzFdIDwgdFszXSkpIHtcbiAgICAgICAgICAgIF8ubGFiZWwgPSBvcFsxXTtcbiAgICAgICAgICAgIGJyZWFrO1xuICAgICAgICAgIH1cbiAgICAgICAgICBpZiAob3BbMF0gPT09IDYgJiYgXy5sYWJlbCA8IHRbMV0pIHtcbiAgICAgICAgICAgIF8ubGFiZWwgPSB0WzFdO1xuICAgICAgICAgICAgdCA9IG9wO1xuICAgICAgICAgICAgYnJlYWs7XG4gICAgICAgICAgfVxuICAgICAgICAgIGlmICh0ICYmIF8ubGFiZWwgPCB0WzJdKSB7XG4gICAgICAgICAgICBfLmxhYmVsID0gdFsyXTtcbiAgICAgICAgICAgIF8ub3BzLnB1c2gob3ApO1xuICAgICAgICAgICAgYnJlYWs7XG4gICAgICAgICAgfVxuICAgICAgICAgIGlmICh0WzJdKSBfLm9wcy5wb3AoKTtcbiAgICAgICAgICBfLnRyeXMucG9wKCk7XG4gICAgICAgICAgY29udGludWU7XG4gICAgICB9XG4gICAgICBvcCA9IGJvZHkuY2FsbCh0aGlzQXJnLCBfKTtcbiAgICB9IGNhdGNoIChlKSB7XG4gICAgICBvcCA9IFs2LCBlXTtcbiAgICAgIHkgPSAwO1xuICAgIH0gZmluYWxseSB7XG4gICAgICBmID0gdCA9IDA7XG4gICAgfVxuICAgIGlmIChvcFswXSAmIDUpIHRocm93IG9wWzFdO1xuICAgIHJldHVybiB7XG4gICAgICB2YWx1ZTogb3BbMF0gPyBvcFsxXSA6IHZvaWQgMCxcbiAgICAgIGRvbmU6IHRydWVcbiAgICB9O1xuICB9XG59O1xudmFyIF9fcmVhZCA9IHRoaXMgJiYgdGhpcy5fX3JlYWQgfHwgZnVuY3Rpb24gKG8sIG4pIHtcbiAgdmFyIG0gPSB0eXBlb2YgU3ltYm9sID09PSBcImZ1bmN0aW9uXCIgJiYgb1tTeW1ib2wuaXRlcmF0b3JdO1xuICBpZiAoIW0pIHJldHVybiBvO1xuICB2YXIgaSA9IG0uY2FsbChvKSxcbiAgICByLFxuICAgIGFyID0gW10sXG4gICAgZTtcbiAgdHJ5IHtcbiAgICB3aGlsZSAoKG4gPT09IHZvaWQgMCB8fCBuLS0gPiAwKSAmJiAhKHIgPSBpLm5leHQoKSkuZG9uZSkgYXIucHVzaChyLnZhbHVlKTtcbiAgfSBjYXRjaCAoZXJyb3IpIHtcbiAgICBlID0ge1xuICAgICAgZXJyb3I6IGVycm9yXG4gICAgfTtcbiAgfSBmaW5hbGx5IHtcbiAgICB0cnkge1xuICAgICAgaWYgKHIgJiYgIXIuZG9uZSAmJiAobSA9IGlbXCJyZXR1cm5cIl0pKSBtLmNhbGwoaSk7XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIGlmIChlKSB0aHJvdyBlLmVycm9yO1xuICAgIH1cbiAgfVxuICByZXR1cm4gYXI7XG59O1xudmFyIF9fc3ByZWFkQXJyYXkgPSB0aGlzICYmIHRoaXMuX19zcHJlYWRBcnJheSB8fCBmdW5jdGlvbiAodG8sIGZyb20sIHBhY2spIHtcbiAgaWYgKHBhY2sgfHwgYXJndW1lbnRzLmxlbmd0aCA9PT0gMikgZm9yICh2YXIgaSA9IDAsIGwgPSBmcm9tLmxlbmd0aCwgYXI7IGkgPCBsOyBpKyspIHtcbiAgICBpZiAoYXIgfHwgIShpIGluIGZyb20pKSB7XG4gICAgICBpZiAoIWFyKSBhciA9IEFycmF5LnByb3RvdHlwZS5zbGljZS5jYWxsKGZyb20sIDAsIGkpO1xuICAgICAgYXJbaV0gPSBmcm9tW2ldO1xuICAgIH1cbiAgfVxuICByZXR1cm4gdG8uY29uY2F0KGFyIHx8IEFycmF5LnByb3RvdHlwZS5zbGljZS5jYWxsKGZyb20pKTtcbn07XG52YXIgX192YWx1ZXMgPSB0aGlzICYmIHRoaXMuX192YWx1ZXMgfHwgZnVuY3Rpb24gKG8pIHtcbiAgdmFyIHMgPSB0eXBlb2YgU3ltYm9sID09PSBcImZ1bmN0aW9uXCIgJiYgU3ltYm9sLml0ZXJhdG9yLFxuICAgIG0gPSBzICYmIG9bc10sXG4gICAgaSA9IDA7XG4gIGlmIChtKSByZXR1cm4gbS5jYWxsKG8pO1xuICBpZiAobyAmJiB0eXBlb2Ygby5sZW5ndGggPT09IFwibnVtYmVyXCIpIHJldHVybiB7XG4gICAgbmV4dDogZnVuY3Rpb24gKCkge1xuICAgICAgaWYgKG8gJiYgaSA+PSBvLmxlbmd0aCkgbyA9IHZvaWQgMDtcbiAgICAgIHJldHVybiB7XG4gICAgICAgIHZhbHVlOiBvICYmIG9baSsrXSxcbiAgICAgICAgZG9uZTogIW9cbiAgICAgIH07XG4gICAgfVxuICB9O1xuICB0aHJvdyBuZXcgVHlwZUVycm9yKHMgPyBcIk9iamVjdCBpcyBub3QgaXRlcmFibGUuXCIgOiBcIlN5bWJvbC5pdGVyYXRvciBpcyBub3QgZGVmaW5lZC5cIik7XG59O1xuT2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFwiX19lc01vZHVsZVwiLCB7XG4gIHZhbHVlOiB0cnVlXG59KTtcbmV4cG9ydHMuTGlua2VkTGlzdCA9IGV4cG9ydHMuTGlzdEl0ZW0gPSBleHBvcnRzLkVORCA9IHZvaWQgMDtcbmV4cG9ydHMuRU5EID0gU3ltYm9sKCk7XG52YXIgTGlzdEl0ZW0gPSBmdW5jdGlvbiAoKSB7XG4gIGZ1bmN0aW9uIExpc3RJdGVtKGRhdGEpIHtcbiAgICBpZiAoZGF0YSA9PT0gdm9pZCAwKSB7XG4gICAgICBkYXRhID0gbnVsbDtcbiAgICB9XG4gICAgdGhpcy5uZXh0ID0gbnVsbDtcbiAgICB0aGlzLnByZXYgPSBudWxsO1xuICAgIHRoaXMuZGF0YSA9IGRhdGE7XG4gIH1cbiAgcmV0dXJuIExpc3RJdGVtO1xufSgpO1xuZXhwb3J0cy5MaXN0SXRlbSA9IExpc3RJdGVtO1xudmFyIExpbmtlZExpc3QgPSBmdW5jdGlvbiAoKSB7XG4gIGZ1bmN0aW9uIExpbmtlZExpc3QoKSB7XG4gICAgdmFyIGFyZ3MgPSBbXTtcbiAgICBmb3IgKHZhciBfaSA9IDA7IF9pIDwgYXJndW1lbnRzLmxlbmd0aDsgX2krKykge1xuICAgICAgYXJnc1tfaV0gPSBhcmd1bWVudHNbX2ldO1xuICAgIH1cbiAgICB0aGlzLmxpc3QgPSBuZXcgTGlzdEl0ZW0oZXhwb3J0cy5FTkQpO1xuICAgIHRoaXMubGlzdC5uZXh0ID0gdGhpcy5saXN0LnByZXYgPSB0aGlzLmxpc3Q7XG4gICAgdGhpcy5wdXNoLmFwcGx5KHRoaXMsIF9fc3ByZWFkQXJyYXkoW10sIF9fcmVhZChhcmdzKSwgZmFsc2UpKTtcbiAgfVxuICBMaW5rZWRMaXN0LnByb3RvdHlwZS5pc0JlZm9yZSA9IGZ1bmN0aW9uIChhLCBiKSB7XG4gICAgcmV0dXJuIGEgPCBiO1xuICB9O1xuICBMaW5rZWRMaXN0LnByb3RvdHlwZS5wdXNoID0gZnVuY3Rpb24gKCkge1xuICAgIHZhciBlXzEsIF9hO1xuICAgIHZhciBhcmdzID0gW107XG4gICAgZm9yICh2YXIgX2kgPSAwOyBfaSA8IGFyZ3VtZW50cy5sZW5ndGg7IF9pKyspIHtcbiAgICAgIGFyZ3NbX2ldID0gYXJndW1lbnRzW19pXTtcbiAgICB9XG4gICAgdHJ5IHtcbiAgICAgIGZvciAodmFyIGFyZ3NfMSA9IF9fdmFsdWVzKGFyZ3MpLCBhcmdzXzFfMSA9IGFyZ3NfMS5uZXh0KCk7ICFhcmdzXzFfMS5kb25lOyBhcmdzXzFfMSA9IGFyZ3NfMS5uZXh0KCkpIHtcbiAgICAgICAgdmFyIGRhdGEgPSBhcmdzXzFfMS52YWx1ZTtcbiAgICAgICAgdmFyIGl0ZW0gPSBuZXcgTGlzdEl0ZW0oZGF0YSk7XG4gICAgICAgIGl0ZW0ubmV4dCA9IHRoaXMubGlzdDtcbiAgICAgICAgaXRlbS5wcmV2ID0gdGhpcy5saXN0LnByZXY7XG4gICAgICAgIHRoaXMubGlzdC5wcmV2ID0gaXRlbTtcbiAgICAgICAgaXRlbS5wcmV2Lm5leHQgPSBpdGVtO1xuICAgICAgfVxuICAgIH0gY2F0Y2ggKGVfMV8xKSB7XG4gICAgICBlXzEgPSB7XG4gICAgICAgIGVycm9yOiBlXzFfMVxuICAgICAgfTtcbiAgICB9IGZpbmFsbHkge1xuICAgICAgdHJ5IHtcbiAgICAgICAgaWYgKGFyZ3NfMV8xICYmICFhcmdzXzFfMS5kb25lICYmIChfYSA9IGFyZ3NfMS5yZXR1cm4pKSBfYS5jYWxsKGFyZ3NfMSk7XG4gICAgICB9IGZpbmFsbHkge1xuICAgICAgICBpZiAoZV8xKSB0aHJvdyBlXzEuZXJyb3I7XG4gICAgICB9XG4gICAgfVxuICAgIHJldHVybiB0aGlzO1xuICB9O1xuICBMaW5rZWRMaXN0LnByb3RvdHlwZS5wb3AgPSBmdW5jdGlvbiAoKSB7XG4gICAgdmFyIGl0ZW0gPSB0aGlzLmxpc3QucHJldjtcbiAgICBpZiAoaXRlbS5kYXRhID09PSBleHBvcnRzLkVORCkge1xuICAgICAgcmV0dXJuIG51bGw7XG4gICAgfVxuICAgIHRoaXMubGlzdC5wcmV2ID0gaXRlbS5wcmV2O1xuICAgIGl0ZW0ucHJldi5uZXh0ID0gdGhpcy5saXN0O1xuICAgIGl0ZW0ubmV4dCA9IGl0ZW0ucHJldiA9IG51bGw7XG4gICAgcmV0dXJuIGl0ZW0uZGF0YTtcbiAgfTtcbiAgTGlua2VkTGlzdC5wcm90b3R5cGUudW5zaGlmdCA9IGZ1bmN0aW9uICgpIHtcbiAgICB2YXIgZV8yLCBfYTtcbiAgICB2YXIgYXJncyA9IFtdO1xuICAgIGZvciAodmFyIF9pID0gMDsgX2kgPCBhcmd1bWVudHMubGVuZ3RoOyBfaSsrKSB7XG4gICAgICBhcmdzW19pXSA9IGFyZ3VtZW50c1tfaV07XG4gICAgfVxuICAgIHRyeSB7XG4gICAgICBmb3IgKHZhciBfYiA9IF9fdmFsdWVzKGFyZ3Muc2xpY2UoMCkucmV2ZXJzZSgpKSwgX2MgPSBfYi5uZXh0KCk7ICFfYy5kb25lOyBfYyA9IF9iLm5leHQoKSkge1xuICAgICAgICB2YXIgZGF0YSA9IF9jLnZhbHVlO1xuICAgICAgICB2YXIgaXRlbSA9IG5ldyBMaXN0SXRlbShkYXRhKTtcbiAgICAgICAgaXRlbS5uZXh0ID0gdGhpcy5saXN0Lm5leHQ7XG4gICAgICAgIGl0ZW0ucHJldiA9IHRoaXMubGlzdDtcbiAgICAgICAgdGhpcy5saXN0Lm5leHQgPSBpdGVtO1xuICAgICAgICBpdGVtLm5leHQucHJldiA9IGl0ZW07XG4gICAgICB9XG4gICAgfSBjYXRjaCAoZV8yXzEpIHtcbiAgICAgIGVfMiA9IHtcbiAgICAgICAgZXJyb3I6IGVfMl8xXG4gICAgICB9O1xuICAgIH0gZmluYWxseSB7XG4gICAgICB0cnkge1xuICAgICAgICBpZiAoX2MgJiYgIV9jLmRvbmUgJiYgKF9hID0gX2IucmV0dXJuKSkgX2EuY2FsbChfYik7XG4gICAgICB9IGZpbmFsbHkge1xuICAgICAgICBpZiAoZV8yKSB0aHJvdyBlXzIuZXJyb3I7XG4gICAgICB9XG4gICAgfVxuICAgIHJldHVybiB0aGlzO1xuICB9O1xuICBMaW5rZWRMaXN0LnByb3RvdHlwZS5zaGlmdCA9IGZ1bmN0aW9uICgpIHtcbiAgICB2YXIgaXRlbSA9IHRoaXMubGlzdC5uZXh0O1xuICAgIGlmIChpdGVtLmRhdGEgPT09IGV4cG9ydHMuRU5EKSB7XG4gICAgICByZXR1cm4gbnVsbDtcbiAgICB9XG4gICAgdGhpcy5saXN0Lm5leHQgPSBpdGVtLm5leHQ7XG4gICAgaXRlbS5uZXh0LnByZXYgPSB0aGlzLmxpc3Q7XG4gICAgaXRlbS5uZXh0ID0gaXRlbS5wcmV2ID0gbnVsbDtcbiAgICByZXR1cm4gaXRlbS5kYXRhO1xuICB9O1xuICBMaW5rZWRMaXN0LnByb3RvdHlwZS5yZW1vdmUgPSBmdW5jdGlvbiAoKSB7XG4gICAgdmFyIGVfMywgX2E7XG4gICAgdmFyIGl0ZW1zID0gW107XG4gICAgZm9yICh2YXIgX2kgPSAwOyBfaSA8IGFyZ3VtZW50cy5sZW5ndGg7IF9pKyspIHtcbiAgICAgIGl0ZW1zW19pXSA9IGFyZ3VtZW50c1tfaV07XG4gICAgfVxuICAgIHZhciBtYXAgPSBuZXcgTWFwKCk7XG4gICAgdHJ5IHtcbiAgICAgIGZvciAodmFyIGl0ZW1zXzEgPSBfX3ZhbHVlcyhpdGVtcyksIGl0ZW1zXzFfMSA9IGl0ZW1zXzEubmV4dCgpOyAhaXRlbXNfMV8xLmRvbmU7IGl0ZW1zXzFfMSA9IGl0ZW1zXzEubmV4dCgpKSB7XG4gICAgICAgIHZhciBpdGVtXzEgPSBpdGVtc18xXzEudmFsdWU7XG4gICAgICAgIG1hcC5zZXQoaXRlbV8xLCB0cnVlKTtcbiAgICAgIH1cbiAgICB9IGNhdGNoIChlXzNfMSkge1xuICAgICAgZV8zID0ge1xuICAgICAgICBlcnJvcjogZV8zXzFcbiAgICAgIH07XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIHRyeSB7XG4gICAgICAgIGlmIChpdGVtc18xXzEgJiYgIWl0ZW1zXzFfMS5kb25lICYmIChfYSA9IGl0ZW1zXzEucmV0dXJuKSkgX2EuY2FsbChpdGVtc18xKTtcbiAgICAgIH0gZmluYWxseSB7XG4gICAgICAgIGlmIChlXzMpIHRocm93IGVfMy5lcnJvcjtcbiAgICAgIH1cbiAgICB9XG4gICAgdmFyIGl0ZW0gPSB0aGlzLmxpc3QubmV4dDtcbiAgICB3aGlsZSAoaXRlbS5kYXRhICE9PSBleHBvcnRzLkVORCkge1xuICAgICAgdmFyIG5leHQgPSBpdGVtLm5leHQ7XG4gICAgICBpZiAobWFwLmhhcyhpdGVtLmRhdGEpKSB7XG4gICAgICAgIGl0ZW0ucHJldi5uZXh0ID0gaXRlbS5uZXh0O1xuICAgICAgICBpdGVtLm5leHQucHJldiA9IGl0ZW0ucHJldjtcbiAgICAgICAgaXRlbS5uZXh0ID0gaXRlbS5wcmV2ID0gbnVsbDtcbiAgICAgIH1cbiAgICAgIGl0ZW0gPSBuZXh0O1xuICAgIH1cbiAgfTtcbiAgTGlua2VkTGlzdC5wcm90b3R5cGUuY2xlYXIgPSBmdW5jdGlvbiAoKSB7XG4gICAgdGhpcy5saXN0Lm5leHQucHJldiA9IHRoaXMubGlzdC5wcmV2Lm5leHQgPSBudWxsO1xuICAgIHRoaXMubGlzdC5uZXh0ID0gdGhpcy5saXN0LnByZXYgPSB0aGlzLmxpc3Q7XG4gICAgcmV0dXJuIHRoaXM7XG4gIH07XG4gIExpbmtlZExpc3QucHJvdG90eXBlW1N5bWJvbC5pdGVyYXRvcl0gPSBmdW5jdGlvbiAoKSB7XG4gICAgdmFyIGN1cnJlbnQ7XG4gICAgcmV0dXJuIF9fZ2VuZXJhdG9yKHRoaXMsIGZ1bmN0aW9uIChfYSkge1xuICAgICAgc3dpdGNoIChfYS5sYWJlbCkge1xuICAgICAgICBjYXNlIDA6XG4gICAgICAgICAgY3VycmVudCA9IHRoaXMubGlzdC5uZXh0O1xuICAgICAgICAgIF9hLmxhYmVsID0gMTtcbiAgICAgICAgY2FzZSAxOlxuICAgICAgICAgIGlmICghKGN1cnJlbnQuZGF0YSAhPT0gZXhwb3J0cy5FTkQpKSByZXR1cm4gWzMsIDNdO1xuICAgICAgICAgIHJldHVybiBbNCwgY3VycmVudC5kYXRhXTtcbiAgICAgICAgY2FzZSAyOlxuICAgICAgICAgIF9hLnNlbnQoKTtcbiAgICAgICAgICBjdXJyZW50ID0gY3VycmVudC5uZXh0O1xuICAgICAgICAgIHJldHVybiBbMywgMV07XG4gICAgICAgIGNhc2UgMzpcbiAgICAgICAgICByZXR1cm4gWzJdO1xuICAgICAgfVxuICAgIH0pO1xuICB9O1xuICBMaW5rZWRMaXN0LnByb3RvdHlwZS5yZXZlcnNlZCA9IGZ1bmN0aW9uICgpIHtcbiAgICB2YXIgY3VycmVudDtcbiAgICByZXR1cm4gX19nZW5lcmF0b3IodGhpcywgZnVuY3Rpb24gKF9hKSB7XG4gICAgICBzd2l0Y2ggKF9hLmxhYmVsKSB7XG4gICAgICAgIGNhc2UgMDpcbiAgICAgICAgICBjdXJyZW50ID0gdGhpcy5saXN0LnByZXY7XG4gICAgICAgICAgX2EubGFiZWwgPSAxO1xuICAgICAgICBjYXNlIDE6XG4gICAgICAgICAgaWYgKCEoY3VycmVudC5kYXRhICE9PSBleHBvcnRzLkVORCkpIHJldHVybiBbMywgM107XG4gICAgICAgICAgcmV0dXJuIFs0LCBjdXJyZW50LmRhdGFdO1xuICAgICAgICBjYXNlIDI6XG4gICAgICAgICAgX2Euc2VudCgpO1xuICAgICAgICAgIGN1cnJlbnQgPSBjdXJyZW50LnByZXY7XG4gICAgICAgICAgcmV0dXJuIFszLCAxXTtcbiAgICAgICAgY2FzZSAzOlxuICAgICAgICAgIHJldHVybiBbMl07XG4gICAgICB9XG4gICAgfSk7XG4gIH07XG4gIExpbmtlZExpc3QucHJvdG90eXBlLmluc2VydCA9IGZ1bmN0aW9uIChkYXRhLCBpc0JlZm9yZSkge1xuICAgIGlmIChpc0JlZm9yZSA9PT0gdm9pZCAwKSB7XG4gICAgICBpc0JlZm9yZSA9IG51bGw7XG4gICAgfVxuICAgIGlmIChpc0JlZm9yZSA9PT0gbnVsbCkge1xuICAgICAgaXNCZWZvcmUgPSB0aGlzLmlzQmVmb3JlLmJpbmQodGhpcyk7XG4gICAgfVxuICAgIHZhciBpdGVtID0gbmV3IExpc3RJdGVtKGRhdGEpO1xuICAgIHZhciBjdXIgPSB0aGlzLmxpc3QubmV4dDtcbiAgICB3aGlsZSAoY3VyLmRhdGEgIT09IGV4cG9ydHMuRU5EICYmIGlzQmVmb3JlKGN1ci5kYXRhLCBpdGVtLmRhdGEpKSB7XG4gICAgICBjdXIgPSBjdXIubmV4dDtcbiAgICB9XG4gICAgaXRlbS5wcmV2ID0gY3VyLnByZXY7XG4gICAgaXRlbS5uZXh0ID0gY3VyO1xuICAgIGN1ci5wcmV2Lm5leHQgPSBjdXIucHJldiA9IGl0ZW07XG4gICAgcmV0dXJuIHRoaXM7XG4gIH07XG4gIExpbmtlZExpc3QucHJvdG90eXBlLnNvcnQgPSBmdW5jdGlvbiAoaXNCZWZvcmUpIHtcbiAgICB2YXIgZV80LCBfYTtcbiAgICBpZiAoaXNCZWZvcmUgPT09IHZvaWQgMCkge1xuICAgICAgaXNCZWZvcmUgPSBudWxsO1xuICAgIH1cbiAgICBpZiAoaXNCZWZvcmUgPT09IG51bGwpIHtcbiAgICAgIGlzQmVmb3JlID0gdGhpcy5pc0JlZm9yZS5iaW5kKHRoaXMpO1xuICAgIH1cbiAgICB2YXIgbGlzdHMgPSBbXTtcbiAgICB0cnkge1xuICAgICAgZm9yICh2YXIgX2IgPSBfX3ZhbHVlcyh0aGlzKSwgX2MgPSBfYi5uZXh0KCk7ICFfYy5kb25lOyBfYyA9IF9iLm5leHQoKSkge1xuICAgICAgICB2YXIgaXRlbSA9IF9jLnZhbHVlO1xuICAgICAgICBsaXN0cy5wdXNoKG5ldyBMaW5rZWRMaXN0KGl0ZW0pKTtcbiAgICAgIH1cbiAgICB9IGNhdGNoIChlXzRfMSkge1xuICAgICAgZV80ID0ge1xuICAgICAgICBlcnJvcjogZV80XzFcbiAgICAgIH07XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIHRyeSB7XG4gICAgICAgIGlmIChfYyAmJiAhX2MuZG9uZSAmJiAoX2EgPSBfYi5yZXR1cm4pKSBfYS5jYWxsKF9iKTtcbiAgICAgIH0gZmluYWxseSB7XG4gICAgICAgIGlmIChlXzQpIHRocm93IGVfNC5lcnJvcjtcbiAgICAgIH1cbiAgICB9XG4gICAgdGhpcy5saXN0Lm5leHQgPSB0aGlzLmxpc3QucHJldiA9IHRoaXMubGlzdDtcbiAgICB3aGlsZSAobGlzdHMubGVuZ3RoID4gMSkge1xuICAgICAgdmFyIGwxID0gbGlzdHMuc2hpZnQoKTtcbiAgICAgIHZhciBsMiA9IGxpc3RzLnNoaWZ0KCk7XG4gICAgICBsMS5tZXJnZShsMiwgaXNCZWZvcmUpO1xuICAgICAgbGlzdHMucHVzaChsMSk7XG4gICAgfVxuICAgIGlmIChsaXN0cy5sZW5ndGgpIHtcbiAgICAgIHRoaXMubGlzdCA9IGxpc3RzWzBdLmxpc3Q7XG4gICAgfVxuICAgIHJldHVybiB0aGlzO1xuICB9O1xuICBMaW5rZWRMaXN0LnByb3RvdHlwZS5tZXJnZSA9IGZ1bmN0aW9uIChsaXN0LCBpc0JlZm9yZSkge1xuICAgIHZhciBfYSwgX2IsIF9jLCBfZCwgX2U7XG4gICAgaWYgKGlzQmVmb3JlID09PSB2b2lkIDApIHtcbiAgICAgIGlzQmVmb3JlID0gbnVsbDtcbiAgICB9XG4gICAgaWYgKGlzQmVmb3JlID09PSBudWxsKSB7XG4gICAgICBpc0JlZm9yZSA9IHRoaXMuaXNCZWZvcmUuYmluZCh0aGlzKTtcbiAgICB9XG4gICAgdmFyIGxjdXIgPSB0aGlzLmxpc3QubmV4dDtcbiAgICB2YXIgbWN1ciA9IGxpc3QubGlzdC5uZXh0O1xuICAgIHdoaWxlIChsY3VyLmRhdGEgIT09IGV4cG9ydHMuRU5EICYmIG1jdXIuZGF0YSAhPT0gZXhwb3J0cy5FTkQpIHtcbiAgICAgIGlmIChpc0JlZm9yZShtY3VyLmRhdGEsIGxjdXIuZGF0YSkpIHtcbiAgICAgICAgX2EgPSBfX3JlYWQoW2xjdXIsIG1jdXJdLCAyKSwgbWN1ci5wcmV2Lm5leHQgPSBfYVswXSwgbGN1ci5wcmV2Lm5leHQgPSBfYVsxXTtcbiAgICAgICAgX2IgPSBfX3JlYWQoW2xjdXIucHJldiwgbWN1ci5wcmV2XSwgMiksIG1jdXIucHJldiA9IF9iWzBdLCBsY3VyLnByZXYgPSBfYlsxXTtcbiAgICAgICAgX2MgPSBfX3JlYWQoW2xpc3QubGlzdCwgdGhpcy5saXN0XSwgMiksIHRoaXMubGlzdC5wcmV2Lm5leHQgPSBfY1swXSwgbGlzdC5saXN0LnByZXYubmV4dCA9IF9jWzFdO1xuICAgICAgICBfZCA9IF9fcmVhZChbbGlzdC5saXN0LnByZXYsIHRoaXMubGlzdC5wcmV2XSwgMiksIHRoaXMubGlzdC5wcmV2ID0gX2RbMF0sIGxpc3QubGlzdC5wcmV2ID0gX2RbMV07XG4gICAgICAgIF9lID0gX19yZWFkKFttY3VyLm5leHQsIGxjdXJdLCAyKSwgbGN1ciA9IF9lWzBdLCBtY3VyID0gX2VbMV07XG4gICAgICB9IGVsc2Uge1xuICAgICAgICBsY3VyID0gbGN1ci5uZXh0O1xuICAgICAgfVxuICAgIH1cbiAgICBpZiAobWN1ci5kYXRhICE9PSBleHBvcnRzLkVORCkge1xuICAgICAgdGhpcy5saXN0LnByZXYubmV4dCA9IGxpc3QubGlzdC5uZXh0O1xuICAgICAgbGlzdC5saXN0Lm5leHQucHJldiA9IHRoaXMubGlzdC5wcmV2O1xuICAgICAgbGlzdC5saXN0LnByZXYubmV4dCA9IHRoaXMubGlzdDtcbiAgICAgIHRoaXMubGlzdC5wcmV2ID0gbGlzdC5saXN0LnByZXY7XG4gICAgICBsaXN0Lmxpc3QubmV4dCA9IGxpc3QubGlzdC5wcmV2ID0gbGlzdC5saXN0O1xuICAgIH1cbiAgICByZXR1cm4gdGhpcztcbiAgfTtcbiAgcmV0dXJuIExpbmtlZExpc3Q7XG59KCk7XG5leHBvcnRzLkxpbmtlZExpc3QgPSBMaW5rZWRMaXN0OyIsIlwidXNlIHN0cmljdFwiO1xuXG5PYmplY3QuZGVmaW5lUHJvcGVydHkoZXhwb3J0cywgXCJfX2VzTW9kdWxlXCIsIHtcbiAgdmFsdWU6IHRydWVcbn0pO1xuZXhwb3J0cy5BYnN0cmFjdE91dHB1dEpheCA9IHZvaWQgMDtcbnZhciBPcHRpb25zX2pzXzEgPSByZXF1aXJlKFwiLi4vdXRpbC9PcHRpb25zLmpzXCIpO1xudmFyIEZ1bmN0aW9uTGlzdF9qc18xID0gcmVxdWlyZShcIi4uL3V0aWwvRnVuY3Rpb25MaXN0LmpzXCIpO1xudmFyIEFic3RyYWN0T3V0cHV0SmF4ID0gZnVuY3Rpb24gKCkge1xuICBmdW5jdGlvbiBBYnN0cmFjdE91dHB1dEpheChvcHRpb25zKSB7XG4gICAgaWYgKG9wdGlvbnMgPT09IHZvaWQgMCkge1xuICAgICAgb3B0aW9ucyA9IHt9O1xuICAgIH1cbiAgICB0aGlzLmFkYXB0b3IgPSBudWxsO1xuICAgIHZhciBDTEFTUyA9IHRoaXMuY29uc3RydWN0b3I7XG4gICAgdGhpcy5vcHRpb25zID0gKDAsIE9wdGlvbnNfanNfMS51c2VyT3B0aW9ucykoKDAsIE9wdGlvbnNfanNfMS5kZWZhdWx0T3B0aW9ucykoe30sIENMQVNTLk9QVElPTlMpLCBvcHRpb25zKTtcbiAgICB0aGlzLnBvc3RGaWx0ZXJzID0gbmV3IEZ1bmN0aW9uTGlzdF9qc18xLkZ1bmN0aW9uTGlzdCgpO1xuICB9XG4gIE9iamVjdC5kZWZpbmVQcm9wZXJ0eShBYnN0cmFjdE91dHB1dEpheC5wcm90b3R5cGUsIFwibmFtZVwiLCB7XG4gICAgZ2V0OiBmdW5jdGlvbiAoKSB7XG4gICAgICByZXR1cm4gdGhpcy5jb25zdHJ1Y3Rvci5OQU1FO1xuICAgIH0sXG4gICAgZW51bWVyYWJsZTogZmFsc2UsXG4gICAgY29uZmlndXJhYmxlOiB0cnVlXG4gIH0pO1xuICBBYnN0cmFjdE91dHB1dEpheC5wcm90b3R5cGUuc2V0QWRhcHRvciA9IGZ1bmN0aW9uIChhZGFwdG9yKSB7XG4gICAgdGhpcy5hZGFwdG9yID0gYWRhcHRvcjtcbiAgfTtcbiAgQWJzdHJhY3RPdXRwdXRKYXgucHJvdG90eXBlLmluaXRpYWxpemUgPSBmdW5jdGlvbiAoKSB7fTtcbiAgQWJzdHJhY3RPdXRwdXRKYXgucHJvdG90eXBlLnJlc2V0ID0gZnVuY3Rpb24gKCkge1xuICAgIHZhciBfYXJncyA9IFtdO1xuICAgIGZvciAodmFyIF9pID0gMDsgX2kgPCBhcmd1bWVudHMubGVuZ3RoOyBfaSsrKSB7XG4gICAgICBfYXJnc1tfaV0gPSBhcmd1bWVudHNbX2ldO1xuICAgIH1cbiAgfTtcbiAgQWJzdHJhY3RPdXRwdXRKYXgucHJvdG90eXBlLmdldE1ldHJpY3MgPSBmdW5jdGlvbiAoX2RvY3VtZW50KSB7fTtcbiAgQWJzdHJhY3RPdXRwdXRKYXgucHJvdG90eXBlLnN0eWxlU2hlZXQgPSBmdW5jdGlvbiAoX2RvY3VtZW50KSB7XG4gICAgcmV0dXJuIG51bGw7XG4gIH07XG4gIEFic3RyYWN0T3V0cHV0SmF4LnByb3RvdHlwZS5wYWdlRWxlbWVudHMgPSBmdW5jdGlvbiAoX2RvY3VtZW50KSB7XG4gICAgcmV0dXJuIG51bGw7XG4gIH07XG4gIEFic3RyYWN0T3V0cHV0SmF4LnByb3RvdHlwZS5leGVjdXRlRmlsdGVycyA9IGZ1bmN0aW9uIChmaWx0ZXJzLCBtYXRoLCBkb2N1bWVudCwgZGF0YSkge1xuICAgIHZhciBhcmdzID0ge1xuICAgICAgbWF0aDogbWF0aCxcbiAgICAgIGRvY3VtZW50OiBkb2N1bWVudCxcbiAgICAgIGRhdGE6IGRhdGFcbiAgICB9O1xuICAgIGZpbHRlcnMuZXhlY3V0ZShhcmdzKTtcbiAgICByZXR1cm4gYXJncy5kYXRhO1xuICB9O1xuICBBYnN0cmFjdE91dHB1dEpheC5OQU1FID0gJ2dlbmVyaWMnO1xuICBBYnN0cmFjdE91dHB1dEpheC5PUFRJT05TID0ge307XG4gIHJldHVybiBBYnN0cmFjdE91dHB1dEpheDtcbn0oKTtcbmV4cG9ydHMuQWJzdHJhY3RPdXRwdXRKYXggPSBBYnN0cmFjdE91dHB1dEpheDsiXSwibmFtZXMiOltdLCJpZ25vcmVMaXN0IjpbXSwic291cmNlUm9vdCI6IiJ9