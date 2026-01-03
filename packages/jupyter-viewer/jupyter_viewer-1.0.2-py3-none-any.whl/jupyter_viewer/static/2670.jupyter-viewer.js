"use strict";
(self["webpackChunk_datalayer_jupyter_viewer"] = self["webpackChunk_datalayer_jupyter_viewer"] || []).push([[2670],{

/***/ 5476
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
Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports.SerializedMmlVisitor = exports.toEntity = exports.DATAMJX = void 0;
var MmlVisitor_js_1 = __webpack_require__(86505);
var MmlNode_js_1 = __webpack_require__(90698);
var mi_js_1 = __webpack_require__(74298);
exports.DATAMJX = 'data-mjx-';
var toEntity = function (c) {
  return '&#x' + c.codePointAt(0).toString(16).toUpperCase() + ';';
};
exports.toEntity = toEntity;
var SerializedMmlVisitor = function (_super) {
  __extends(SerializedMmlVisitor, _super);
  function SerializedMmlVisitor() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  SerializedMmlVisitor.prototype.visitTree = function (node) {
    return this.visitNode(node, '');
  };
  SerializedMmlVisitor.prototype.visitTextNode = function (node, _space) {
    return this.quoteHTML(node.getText());
  };
  SerializedMmlVisitor.prototype.visitXMLNode = function (node, space) {
    return space + node.getSerializedXML();
  };
  SerializedMmlVisitor.prototype.visitInferredMrowNode = function (node, space) {
    var e_1, _a;
    var mml = [];
    try {
      for (var _b = __values(node.childNodes), _c = _b.next(); !_c.done; _c = _b.next()) {
        var child = _c.value;
        mml.push(this.visitNode(child, space));
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
    return mml.join('\n');
  };
  SerializedMmlVisitor.prototype.visitTeXAtomNode = function (node, space) {
    var children = this.childNodeMml(node, space + '  ', '\n');
    var mml = space + '<mrow' + this.getAttributes(node) + '>' + (children.match(/\S/) ? '\n' + children + space : '') + '</mrow>';
    return mml;
  };
  SerializedMmlVisitor.prototype.visitAnnotationNode = function (node, space) {
    return space + '<annotation' + this.getAttributes(node) + '>' + this.childNodeMml(node, '', '') + '</annotation>';
  };
  SerializedMmlVisitor.prototype.visitDefault = function (node, space) {
    var kind = node.kind;
    var _a = __read(node.isToken || node.childNodes.length === 0 ? ['', ''] : ['\n', space], 2),
      nl = _a[0],
      endspace = _a[1];
    var children = this.childNodeMml(node, space + '  ', nl);
    return space + '<' + kind + this.getAttributes(node) + '>' + (children.match(/\S/) ? nl + children + endspace : '') + '</' + kind + '>';
  };
  SerializedMmlVisitor.prototype.childNodeMml = function (node, space, nl) {
    var e_2, _a;
    var mml = '';
    try {
      for (var _b = __values(node.childNodes), _c = _b.next(); !_c.done; _c = _b.next()) {
        var child = _c.value;
        mml += this.visitNode(child, space) + nl;
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
    return mml;
  };
  SerializedMmlVisitor.prototype.getAttributes = function (node) {
    var e_3, _a;
    var attr = [];
    var defaults = this.constructor.defaultAttributes[node.kind] || {};
    var attributes = Object.assign({}, defaults, this.getDataAttributes(node), node.attributes.getAllAttributes());
    var variants = this.constructor.variants;
    if (attributes.hasOwnProperty('mathvariant') && variants.hasOwnProperty(attributes.mathvariant)) {
      attributes.mathvariant = variants[attributes.mathvariant];
    }
    try {
      for (var _b = __values(Object.keys(attributes)), _c = _b.next(); !_c.done; _c = _b.next()) {
        var name_1 = _c.value;
        var value = String(attributes[name_1]);
        if (value === undefined) continue;
        attr.push(name_1 + '="' + this.quoteHTML(value) + '"');
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
    return attr.length ? ' ' + attr.join(' ') : '';
  };
  SerializedMmlVisitor.prototype.getDataAttributes = function (node) {
    var data = {};
    var variant = node.attributes.getExplicit('mathvariant');
    var variants = this.constructor.variants;
    variant && variants.hasOwnProperty(variant) && this.setDataAttribute(data, 'variant', variant);
    node.getProperty('variantForm') && this.setDataAttribute(data, 'alternate', '1');
    node.getProperty('pseudoscript') && this.setDataAttribute(data, 'pseudoscript', 'true');
    node.getProperty('autoOP') === false && this.setDataAttribute(data, 'auto-op', 'false');
    var scriptalign = node.getProperty('scriptalign');
    scriptalign && this.setDataAttribute(data, 'script-align', scriptalign);
    var texclass = node.getProperty('texClass');
    if (texclass !== undefined) {
      var setclass = true;
      if (texclass === MmlNode_js_1.TEXCLASS.OP && node.isKind('mi')) {
        var name_2 = node.getText();
        setclass = !(name_2.length > 1 && name_2.match(mi_js_1.MmlMi.operatorName));
      }
      setclass && this.setDataAttribute(data, 'texclass', texclass < 0 ? 'NONE' : MmlNode_js_1.TEXCLASSNAMES[texclass]);
    }
    node.getProperty('scriptlevel') && node.getProperty('useHeight') === false && this.setDataAttribute(data, 'smallmatrix', 'true');
    return data;
  };
  SerializedMmlVisitor.prototype.setDataAttribute = function (data, name, value) {
    data[exports.DATAMJX + name] = value;
  };
  SerializedMmlVisitor.prototype.quoteHTML = function (value) {
    return value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\"/g, '&quot;').replace(/[\uD800-\uDBFF]./g, exports.toEntity).replace(/[\u0080-\uD7FF\uE000-\uFFFF]/g, exports.toEntity);
  };
  SerializedMmlVisitor.variants = {
    '-tex-calligraphic': 'script',
    '-tex-bold-calligraphic': 'bold-script',
    '-tex-oldstyle': 'normal',
    '-tex-bold-oldstyle': 'bold',
    '-tex-mathit': 'italic'
  };
  SerializedMmlVisitor.defaultAttributes = {
    math: {
      xmlns: 'http://www.w3.org/1998/Math/MathML'
    }
  };
  return SerializedMmlVisitor;
}(MmlVisitor_js_1.MmlVisitor);
exports.SerializedMmlVisitor = SerializedMmlVisitor;

/***/ },

/***/ 22670
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
exports.AssistiveMmlHandler = exports.AssistiveMmlMathDocumentMixin = exports.AssistiveMmlMathItemMixin = exports.LimitedMmlVisitor = void 0;
var MathItem_js_1 = __webpack_require__(52016);
var SerializedMmlVisitor_js_1 = __webpack_require__(5476);
var Options_js_1 = __webpack_require__(53588);
var LimitedMmlVisitor = function (_super) {
  __extends(LimitedMmlVisitor, _super);
  function LimitedMmlVisitor() {
    return _super !== null && _super.apply(this, arguments) || this;
  }
  LimitedMmlVisitor.prototype.getAttributes = function (node) {
    return _super.prototype.getAttributes.call(this, node).replace(/ ?id=".*?"/, '');
  };
  return LimitedMmlVisitor;
}(SerializedMmlVisitor_js_1.SerializedMmlVisitor);
exports.LimitedMmlVisitor = LimitedMmlVisitor;
(0, MathItem_js_1.newState)('ASSISTIVEMML', 153);
function AssistiveMmlMathItemMixin(BaseMathItem) {
  return function (_super) {
    __extends(class_1, _super);
    function class_1() {
      return _super !== null && _super.apply(this, arguments) || this;
    }
    class_1.prototype.assistiveMml = function (document, force) {
      if (force === void 0) {
        force = false;
      }
      if (this.state() >= MathItem_js_1.STATE.ASSISTIVEMML) return;
      if (!this.isEscaped && (document.options.enableAssistiveMml || force)) {
        var adaptor = document.adaptor;
        var mml = document.toMML(this.root).replace(/\n */g, '').replace(/<!--.*?-->/g, '');
        var mmlNodes = adaptor.firstChild(adaptor.body(adaptor.parse(mml, 'text/html')));
        var node = adaptor.node('mjx-assistive-mml', {
          unselectable: 'on',
          display: this.display ? 'block' : 'inline'
        }, [mmlNodes]);
        adaptor.setAttribute(adaptor.firstChild(this.typesetRoot), 'aria-hidden', 'true');
        adaptor.setStyle(this.typesetRoot, 'position', 'relative');
        adaptor.append(this.typesetRoot, node);
      }
      this.state(MathItem_js_1.STATE.ASSISTIVEMML);
    };
    return class_1;
  }(BaseMathItem);
}
exports.AssistiveMmlMathItemMixin = AssistiveMmlMathItemMixin;
function AssistiveMmlMathDocumentMixin(BaseDocument) {
  var _a;
  return _a = function (_super) {
    __extends(BaseClass, _super);
    function BaseClass() {
      var args = [];
      for (var _i = 0; _i < arguments.length; _i++) {
        args[_i] = arguments[_i];
      }
      var _this = _super.apply(this, __spreadArray([], __read(args), false)) || this;
      var CLASS = _this.constructor;
      var ProcessBits = CLASS.ProcessBits;
      if (!ProcessBits.has('assistive-mml')) {
        ProcessBits.allocate('assistive-mml');
      }
      _this.visitor = new LimitedMmlVisitor(_this.mmlFactory);
      _this.options.MathItem = AssistiveMmlMathItemMixin(_this.options.MathItem);
      if ('addStyles' in _this) {
        _this.addStyles(CLASS.assistiveStyles);
      }
      return _this;
    }
    BaseClass.prototype.toMML = function (node) {
      return this.visitor.visitTree(node);
    };
    BaseClass.prototype.assistiveMml = function () {
      var e_1, _a;
      if (!this.processed.isSet('assistive-mml')) {
        try {
          for (var _b = __values(this.math), _c = _b.next(); !_c.done; _c = _b.next()) {
            var math = _c.value;
            math.assistiveMml(this);
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
        this.processed.set('assistive-mml');
      }
      return this;
    };
    BaseClass.prototype.state = function (state, restore) {
      if (restore === void 0) {
        restore = false;
      }
      _super.prototype.state.call(this, state, restore);
      if (state < MathItem_js_1.STATE.ASSISTIVEMML) {
        this.processed.clear('assistive-mml');
      }
      return this;
    };
    return BaseClass;
  }(BaseDocument), _a.OPTIONS = __assign(__assign({}, BaseDocument.OPTIONS), {
    enableAssistiveMml: true,
    renderActions: (0, Options_js_1.expandable)(__assign(__assign({}, BaseDocument.OPTIONS.renderActions), {
      assistiveMml: [MathItem_js_1.STATE.ASSISTIVEMML]
    }))
  }), _a.assistiveStyles = {
    'mjx-assistive-mml': {
      position: 'absolute !important',
      top: '0px',
      left: '0px',
      clip: 'rect(1px, 1px, 1px, 1px)',
      padding: '1px 0px 0px 0px !important',
      border: '0px !important',
      display: 'block !important',
      width: 'auto !important',
      overflow: 'hidden !important',
      '-webkit-touch-callout': 'none',
      '-webkit-user-select': 'none',
      '-khtml-user-select': 'none',
      '-moz-user-select': 'none',
      '-ms-user-select': 'none',
      'user-select': 'none'
    },
    'mjx-assistive-mml[display="block"]': {
      width: '100% !important'
    }
  }, _a;
}
exports.AssistiveMmlMathDocumentMixin = AssistiveMmlMathDocumentMixin;
function AssistiveMmlHandler(handler) {
  handler.documentClass = AssistiveMmlMathDocumentMixin(handler.documentClass);
  return handler;
}
exports.AssistiveMmlHandler = AssistiveMmlHandler;

/***/ },

/***/ 79252
(__unused_webpack_module, exports, __webpack_require__) {



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
exports.AbstractVisitor = void 0;
var Node_js_1 = __webpack_require__(98452);
var AbstractVisitor = function () {
  function AbstractVisitor(factory) {
    var e_1, _a;
    this.nodeHandlers = new Map();
    try {
      for (var _b = __values(factory.getKinds()), _c = _b.next(); !_c.done; _c = _b.next()) {
        var kind = _c.value;
        var method = this[AbstractVisitor.methodName(kind)];
        if (method) {
          this.nodeHandlers.set(kind, method);
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
  }
  AbstractVisitor.methodName = function (kind) {
    return 'visit' + (kind.charAt(0).toUpperCase() + kind.substr(1)).replace(/[^a-z0-9_]/ig, '_') + 'Node';
  };
  AbstractVisitor.prototype.visitTree = function (tree) {
    var args = [];
    for (var _i = 1; _i < arguments.length; _i++) {
      args[_i - 1] = arguments[_i];
    }
    return this.visitNode.apply(this, __spreadArray([tree], __read(args), false));
  };
  AbstractVisitor.prototype.visitNode = function (node) {
    var args = [];
    for (var _i = 1; _i < arguments.length; _i++) {
      args[_i - 1] = arguments[_i];
    }
    var handler = this.nodeHandlers.get(node.kind) || this.visitDefault;
    return handler.call.apply(handler, __spreadArray([this, node], __read(args), false));
  };
  AbstractVisitor.prototype.visitDefault = function (node) {
    var e_2, _a;
    var args = [];
    for (var _i = 1; _i < arguments.length; _i++) {
      args[_i - 1] = arguments[_i];
    }
    if (node instanceof Node_js_1.AbstractNode) {
      try {
        for (var _b = __values(node.childNodes), _c = _b.next(); !_c.done; _c = _b.next()) {
          var child = _c.value;
          this.visitNode.apply(this, __spreadArray([child], __read(args), false));
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
    }
  };
  AbstractVisitor.prototype.setNodeHandler = function (kind, handler) {
    this.nodeHandlers.set(kind, handler);
  };
  AbstractVisitor.prototype.removeNodeHandler = function (kind) {
    this.nodeHandlers.delete(kind);
  };
  return AbstractVisitor;
}();
exports.AbstractVisitor = AbstractVisitor;

/***/ },

/***/ 86505
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
exports.MmlVisitor = void 0;
var MmlFactory_js_1 = __webpack_require__(13962);
var Visitor_js_1 = __webpack_require__(79252);
var MmlVisitor = function (_super) {
  __extends(MmlVisitor, _super);
  function MmlVisitor(factory) {
    if (factory === void 0) {
      factory = null;
    }
    if (!factory) {
      factory = new MmlFactory_js_1.MmlFactory();
    }
    return _super.call(this, factory) || this;
  }
  MmlVisitor.prototype.visitTextNode = function (_node) {
    var _args = [];
    for (var _i = 1; _i < arguments.length; _i++) {
      _args[_i - 1] = arguments[_i];
    }
  };
  MmlVisitor.prototype.visitXMLNode = function (_node) {
    var _args = [];
    for (var _i = 1; _i < arguments.length; _i++) {
      _args[_i - 1] = arguments[_i];
    }
  };
  return MmlVisitor;
}(Visitor_js_1.AbstractVisitor);
exports.MmlVisitor = MmlVisitor;

/***/ }

}]);
//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiMjY3MC5qdXB5dGVyLXZpZXdlci5qcyIsIm1hcHBpbmdzIjoiOzs7Ozs7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7QUN2TkE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7QUMzTkE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7Ozs7Ozs7QUNqSUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vQGRhdGFsYXllci9qdXB5dGVyLXZpZXdlci8uL25vZGVfbW9kdWxlcy9tYXRoamF4LWZ1bGwvanMvY29yZS9NbWxUcmVlL1NlcmlhbGl6ZWRNbWxWaXNpdG9yLmpzIiwid2VicGFjazovL0BkYXRhbGF5ZXIvanVweXRlci12aWV3ZXIvLi9ub2RlX21vZHVsZXMvbWF0aGpheC1mdWxsL2pzL2ExMXkvYXNzaXN0aXZlLW1tbC5qcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL21hdGhqYXgtZnVsbC9qcy9jb3JlL1RyZWUvVmlzaXRvci5qcyIsIndlYnBhY2s6Ly9AZGF0YWxheWVyL2p1cHl0ZXItdmlld2VyLy4vbm9kZV9tb2R1bGVzL21hdGhqYXgtZnVsbC9qcy9jb3JlL01tbFRyZWUvTW1sVmlzaXRvci5qcyJdLCJzb3VyY2VzQ29udGVudCI6WyJcInVzZSBzdHJpY3RcIjtcblxudmFyIF9fZXh0ZW5kcyA9IHRoaXMgJiYgdGhpcy5fX2V4dGVuZHMgfHwgZnVuY3Rpb24gKCkge1xuICB2YXIgZXh0ZW5kU3RhdGljcyA9IGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgZXh0ZW5kU3RhdGljcyA9IE9iamVjdC5zZXRQcm90b3R5cGVPZiB8fCB7XG4gICAgICBfX3Byb3RvX186IFtdXG4gICAgfSBpbnN0YW5jZW9mIEFycmF5ICYmIGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgICBkLl9fcHJvdG9fXyA9IGI7XG4gICAgfSB8fCBmdW5jdGlvbiAoZCwgYikge1xuICAgICAgZm9yICh2YXIgcCBpbiBiKSBpZiAoT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsKGIsIHApKSBkW3BdID0gYltwXTtcbiAgICB9O1xuICAgIHJldHVybiBleHRlbmRTdGF0aWNzKGQsIGIpO1xuICB9O1xuICByZXR1cm4gZnVuY3Rpb24gKGQsIGIpIHtcbiAgICBpZiAodHlwZW9mIGIgIT09IFwiZnVuY3Rpb25cIiAmJiBiICE9PSBudWxsKSB0aHJvdyBuZXcgVHlwZUVycm9yKFwiQ2xhc3MgZXh0ZW5kcyB2YWx1ZSBcIiArIFN0cmluZyhiKSArIFwiIGlzIG5vdCBhIGNvbnN0cnVjdG9yIG9yIG51bGxcIik7XG4gICAgZXh0ZW5kU3RhdGljcyhkLCBiKTtcbiAgICBmdW5jdGlvbiBfXygpIHtcbiAgICAgIHRoaXMuY29uc3RydWN0b3IgPSBkO1xuICAgIH1cbiAgICBkLnByb3RvdHlwZSA9IGIgPT09IG51bGwgPyBPYmplY3QuY3JlYXRlKGIpIDogKF9fLnByb3RvdHlwZSA9IGIucHJvdG90eXBlLCBuZXcgX18oKSk7XG4gIH07XG59KCk7XG52YXIgX192YWx1ZXMgPSB0aGlzICYmIHRoaXMuX192YWx1ZXMgfHwgZnVuY3Rpb24gKG8pIHtcbiAgdmFyIHMgPSB0eXBlb2YgU3ltYm9sID09PSBcImZ1bmN0aW9uXCIgJiYgU3ltYm9sLml0ZXJhdG9yLFxuICAgIG0gPSBzICYmIG9bc10sXG4gICAgaSA9IDA7XG4gIGlmIChtKSByZXR1cm4gbS5jYWxsKG8pO1xuICBpZiAobyAmJiB0eXBlb2Ygby5sZW5ndGggPT09IFwibnVtYmVyXCIpIHJldHVybiB7XG4gICAgbmV4dDogZnVuY3Rpb24gKCkge1xuICAgICAgaWYgKG8gJiYgaSA+PSBvLmxlbmd0aCkgbyA9IHZvaWQgMDtcbiAgICAgIHJldHVybiB7XG4gICAgICAgIHZhbHVlOiBvICYmIG9baSsrXSxcbiAgICAgICAgZG9uZTogIW9cbiAgICAgIH07XG4gICAgfVxuICB9O1xuICB0aHJvdyBuZXcgVHlwZUVycm9yKHMgPyBcIk9iamVjdCBpcyBub3QgaXRlcmFibGUuXCIgOiBcIlN5bWJvbC5pdGVyYXRvciBpcyBub3QgZGVmaW5lZC5cIik7XG59O1xudmFyIF9fcmVhZCA9IHRoaXMgJiYgdGhpcy5fX3JlYWQgfHwgZnVuY3Rpb24gKG8sIG4pIHtcbiAgdmFyIG0gPSB0eXBlb2YgU3ltYm9sID09PSBcImZ1bmN0aW9uXCIgJiYgb1tTeW1ib2wuaXRlcmF0b3JdO1xuICBpZiAoIW0pIHJldHVybiBvO1xuICB2YXIgaSA9IG0uY2FsbChvKSxcbiAgICByLFxuICAgIGFyID0gW10sXG4gICAgZTtcbiAgdHJ5IHtcbiAgICB3aGlsZSAoKG4gPT09IHZvaWQgMCB8fCBuLS0gPiAwKSAmJiAhKHIgPSBpLm5leHQoKSkuZG9uZSkgYXIucHVzaChyLnZhbHVlKTtcbiAgfSBjYXRjaCAoZXJyb3IpIHtcbiAgICBlID0ge1xuICAgICAgZXJyb3I6IGVycm9yXG4gICAgfTtcbiAgfSBmaW5hbGx5IHtcbiAgICB0cnkge1xuICAgICAgaWYgKHIgJiYgIXIuZG9uZSAmJiAobSA9IGlbXCJyZXR1cm5cIl0pKSBtLmNhbGwoaSk7XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIGlmIChlKSB0aHJvdyBlLmVycm9yO1xuICAgIH1cbiAgfVxuICByZXR1cm4gYXI7XG59O1xuT2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFwiX19lc01vZHVsZVwiLCB7XG4gIHZhbHVlOiB0cnVlXG59KTtcbmV4cG9ydHMuU2VyaWFsaXplZE1tbFZpc2l0b3IgPSBleHBvcnRzLnRvRW50aXR5ID0gZXhwb3J0cy5EQVRBTUpYID0gdm9pZCAwO1xudmFyIE1tbFZpc2l0b3JfanNfMSA9IHJlcXVpcmUoXCIuL01tbFZpc2l0b3IuanNcIik7XG52YXIgTW1sTm9kZV9qc18xID0gcmVxdWlyZShcIi4vTW1sTm9kZS5qc1wiKTtcbnZhciBtaV9qc18xID0gcmVxdWlyZShcIi4vTW1sTm9kZXMvbWkuanNcIik7XG5leHBvcnRzLkRBVEFNSlggPSAnZGF0YS1tangtJztcbnZhciB0b0VudGl0eSA9IGZ1bmN0aW9uIChjKSB7XG4gIHJldHVybiAnJiN4JyArIGMuY29kZVBvaW50QXQoMCkudG9TdHJpbmcoMTYpLnRvVXBwZXJDYXNlKCkgKyAnOyc7XG59O1xuZXhwb3J0cy50b0VudGl0eSA9IHRvRW50aXR5O1xudmFyIFNlcmlhbGl6ZWRNbWxWaXNpdG9yID0gZnVuY3Rpb24gKF9zdXBlcikge1xuICBfX2V4dGVuZHMoU2VyaWFsaXplZE1tbFZpc2l0b3IsIF9zdXBlcik7XG4gIGZ1bmN0aW9uIFNlcmlhbGl6ZWRNbWxWaXNpdG9yKCkge1xuICAgIHJldHVybiBfc3VwZXIgIT09IG51bGwgJiYgX3N1cGVyLmFwcGx5KHRoaXMsIGFyZ3VtZW50cykgfHwgdGhpcztcbiAgfVxuICBTZXJpYWxpemVkTW1sVmlzaXRvci5wcm90b3R5cGUudmlzaXRUcmVlID0gZnVuY3Rpb24gKG5vZGUpIHtcbiAgICByZXR1cm4gdGhpcy52aXNpdE5vZGUobm9kZSwgJycpO1xuICB9O1xuICBTZXJpYWxpemVkTW1sVmlzaXRvci5wcm90b3R5cGUudmlzaXRUZXh0Tm9kZSA9IGZ1bmN0aW9uIChub2RlLCBfc3BhY2UpIHtcbiAgICByZXR1cm4gdGhpcy5xdW90ZUhUTUwobm9kZS5nZXRUZXh0KCkpO1xuICB9O1xuICBTZXJpYWxpemVkTW1sVmlzaXRvci5wcm90b3R5cGUudmlzaXRYTUxOb2RlID0gZnVuY3Rpb24gKG5vZGUsIHNwYWNlKSB7XG4gICAgcmV0dXJuIHNwYWNlICsgbm9kZS5nZXRTZXJpYWxpemVkWE1MKCk7XG4gIH07XG4gIFNlcmlhbGl6ZWRNbWxWaXNpdG9yLnByb3RvdHlwZS52aXNpdEluZmVycmVkTXJvd05vZGUgPSBmdW5jdGlvbiAobm9kZSwgc3BhY2UpIHtcbiAgICB2YXIgZV8xLCBfYTtcbiAgICB2YXIgbW1sID0gW107XG4gICAgdHJ5IHtcbiAgICAgIGZvciAodmFyIF9iID0gX192YWx1ZXMobm9kZS5jaGlsZE5vZGVzKSwgX2MgPSBfYi5uZXh0KCk7ICFfYy5kb25lOyBfYyA9IF9iLm5leHQoKSkge1xuICAgICAgICB2YXIgY2hpbGQgPSBfYy52YWx1ZTtcbiAgICAgICAgbW1sLnB1c2godGhpcy52aXNpdE5vZGUoY2hpbGQsIHNwYWNlKSk7XG4gICAgICB9XG4gICAgfSBjYXRjaCAoZV8xXzEpIHtcbiAgICAgIGVfMSA9IHtcbiAgICAgICAgZXJyb3I6IGVfMV8xXG4gICAgICB9O1xuICAgIH0gZmluYWxseSB7XG4gICAgICB0cnkge1xuICAgICAgICBpZiAoX2MgJiYgIV9jLmRvbmUgJiYgKF9hID0gX2IucmV0dXJuKSkgX2EuY2FsbChfYik7XG4gICAgICB9IGZpbmFsbHkge1xuICAgICAgICBpZiAoZV8xKSB0aHJvdyBlXzEuZXJyb3I7XG4gICAgICB9XG4gICAgfVxuICAgIHJldHVybiBtbWwuam9pbignXFxuJyk7XG4gIH07XG4gIFNlcmlhbGl6ZWRNbWxWaXNpdG9yLnByb3RvdHlwZS52aXNpdFRlWEF0b21Ob2RlID0gZnVuY3Rpb24gKG5vZGUsIHNwYWNlKSB7XG4gICAgdmFyIGNoaWxkcmVuID0gdGhpcy5jaGlsZE5vZGVNbWwobm9kZSwgc3BhY2UgKyAnICAnLCAnXFxuJyk7XG4gICAgdmFyIG1tbCA9IHNwYWNlICsgJzxtcm93JyArIHRoaXMuZ2V0QXR0cmlidXRlcyhub2RlKSArICc+JyArIChjaGlsZHJlbi5tYXRjaCgvXFxTLykgPyAnXFxuJyArIGNoaWxkcmVuICsgc3BhY2UgOiAnJykgKyAnPC9tcm93Pic7XG4gICAgcmV0dXJuIG1tbDtcbiAgfTtcbiAgU2VyaWFsaXplZE1tbFZpc2l0b3IucHJvdG90eXBlLnZpc2l0QW5ub3RhdGlvbk5vZGUgPSBmdW5jdGlvbiAobm9kZSwgc3BhY2UpIHtcbiAgICByZXR1cm4gc3BhY2UgKyAnPGFubm90YXRpb24nICsgdGhpcy5nZXRBdHRyaWJ1dGVzKG5vZGUpICsgJz4nICsgdGhpcy5jaGlsZE5vZGVNbWwobm9kZSwgJycsICcnKSArICc8L2Fubm90YXRpb24+JztcbiAgfTtcbiAgU2VyaWFsaXplZE1tbFZpc2l0b3IucHJvdG90eXBlLnZpc2l0RGVmYXVsdCA9IGZ1bmN0aW9uIChub2RlLCBzcGFjZSkge1xuICAgIHZhciBraW5kID0gbm9kZS5raW5kO1xuICAgIHZhciBfYSA9IF9fcmVhZChub2RlLmlzVG9rZW4gfHwgbm9kZS5jaGlsZE5vZGVzLmxlbmd0aCA9PT0gMCA/IFsnJywgJyddIDogWydcXG4nLCBzcGFjZV0sIDIpLFxuICAgICAgbmwgPSBfYVswXSxcbiAgICAgIGVuZHNwYWNlID0gX2FbMV07XG4gICAgdmFyIGNoaWxkcmVuID0gdGhpcy5jaGlsZE5vZGVNbWwobm9kZSwgc3BhY2UgKyAnICAnLCBubCk7XG4gICAgcmV0dXJuIHNwYWNlICsgJzwnICsga2luZCArIHRoaXMuZ2V0QXR0cmlidXRlcyhub2RlKSArICc+JyArIChjaGlsZHJlbi5tYXRjaCgvXFxTLykgPyBubCArIGNoaWxkcmVuICsgZW5kc3BhY2UgOiAnJykgKyAnPC8nICsga2luZCArICc+JztcbiAgfTtcbiAgU2VyaWFsaXplZE1tbFZpc2l0b3IucHJvdG90eXBlLmNoaWxkTm9kZU1tbCA9IGZ1bmN0aW9uIChub2RlLCBzcGFjZSwgbmwpIHtcbiAgICB2YXIgZV8yLCBfYTtcbiAgICB2YXIgbW1sID0gJyc7XG4gICAgdHJ5IHtcbiAgICAgIGZvciAodmFyIF9iID0gX192YWx1ZXMobm9kZS5jaGlsZE5vZGVzKSwgX2MgPSBfYi5uZXh0KCk7ICFfYy5kb25lOyBfYyA9IF9iLm5leHQoKSkge1xuICAgICAgICB2YXIgY2hpbGQgPSBfYy52YWx1ZTtcbiAgICAgICAgbW1sICs9IHRoaXMudmlzaXROb2RlKGNoaWxkLCBzcGFjZSkgKyBubDtcbiAgICAgIH1cbiAgICB9IGNhdGNoIChlXzJfMSkge1xuICAgICAgZV8yID0ge1xuICAgICAgICBlcnJvcjogZV8yXzFcbiAgICAgIH07XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIHRyeSB7XG4gICAgICAgIGlmIChfYyAmJiAhX2MuZG9uZSAmJiAoX2EgPSBfYi5yZXR1cm4pKSBfYS5jYWxsKF9iKTtcbiAgICAgIH0gZmluYWxseSB7XG4gICAgICAgIGlmIChlXzIpIHRocm93IGVfMi5lcnJvcjtcbiAgICAgIH1cbiAgICB9XG4gICAgcmV0dXJuIG1tbDtcbiAgfTtcbiAgU2VyaWFsaXplZE1tbFZpc2l0b3IucHJvdG90eXBlLmdldEF0dHJpYnV0ZXMgPSBmdW5jdGlvbiAobm9kZSkge1xuICAgIHZhciBlXzMsIF9hO1xuICAgIHZhciBhdHRyID0gW107XG4gICAgdmFyIGRlZmF1bHRzID0gdGhpcy5jb25zdHJ1Y3Rvci5kZWZhdWx0QXR0cmlidXRlc1tub2RlLmtpbmRdIHx8IHt9O1xuICAgIHZhciBhdHRyaWJ1dGVzID0gT2JqZWN0LmFzc2lnbih7fSwgZGVmYXVsdHMsIHRoaXMuZ2V0RGF0YUF0dHJpYnV0ZXMobm9kZSksIG5vZGUuYXR0cmlidXRlcy5nZXRBbGxBdHRyaWJ1dGVzKCkpO1xuICAgIHZhciB2YXJpYW50cyA9IHRoaXMuY29uc3RydWN0b3IudmFyaWFudHM7XG4gICAgaWYgKGF0dHJpYnV0ZXMuaGFzT3duUHJvcGVydHkoJ21hdGh2YXJpYW50JykgJiYgdmFyaWFudHMuaGFzT3duUHJvcGVydHkoYXR0cmlidXRlcy5tYXRodmFyaWFudCkpIHtcbiAgICAgIGF0dHJpYnV0ZXMubWF0aHZhcmlhbnQgPSB2YXJpYW50c1thdHRyaWJ1dGVzLm1hdGh2YXJpYW50XTtcbiAgICB9XG4gICAgdHJ5IHtcbiAgICAgIGZvciAodmFyIF9iID0gX192YWx1ZXMoT2JqZWN0LmtleXMoYXR0cmlidXRlcykpLCBfYyA9IF9iLm5leHQoKTsgIV9jLmRvbmU7IF9jID0gX2IubmV4dCgpKSB7XG4gICAgICAgIHZhciBuYW1lXzEgPSBfYy52YWx1ZTtcbiAgICAgICAgdmFyIHZhbHVlID0gU3RyaW5nKGF0dHJpYnV0ZXNbbmFtZV8xXSk7XG4gICAgICAgIGlmICh2YWx1ZSA9PT0gdW5kZWZpbmVkKSBjb250aW51ZTtcbiAgICAgICAgYXR0ci5wdXNoKG5hbWVfMSArICc9XCInICsgdGhpcy5xdW90ZUhUTUwodmFsdWUpICsgJ1wiJyk7XG4gICAgICB9XG4gICAgfSBjYXRjaCAoZV8zXzEpIHtcbiAgICAgIGVfMyA9IHtcbiAgICAgICAgZXJyb3I6IGVfM18xXG4gICAgICB9O1xuICAgIH0gZmluYWxseSB7XG4gICAgICB0cnkge1xuICAgICAgICBpZiAoX2MgJiYgIV9jLmRvbmUgJiYgKF9hID0gX2IucmV0dXJuKSkgX2EuY2FsbChfYik7XG4gICAgICB9IGZpbmFsbHkge1xuICAgICAgICBpZiAoZV8zKSB0aHJvdyBlXzMuZXJyb3I7XG4gICAgICB9XG4gICAgfVxuICAgIHJldHVybiBhdHRyLmxlbmd0aCA/ICcgJyArIGF0dHIuam9pbignICcpIDogJyc7XG4gIH07XG4gIFNlcmlhbGl6ZWRNbWxWaXNpdG9yLnByb3RvdHlwZS5nZXREYXRhQXR0cmlidXRlcyA9IGZ1bmN0aW9uIChub2RlKSB7XG4gICAgdmFyIGRhdGEgPSB7fTtcbiAgICB2YXIgdmFyaWFudCA9IG5vZGUuYXR0cmlidXRlcy5nZXRFeHBsaWNpdCgnbWF0aHZhcmlhbnQnKTtcbiAgICB2YXIgdmFyaWFudHMgPSB0aGlzLmNvbnN0cnVjdG9yLnZhcmlhbnRzO1xuICAgIHZhcmlhbnQgJiYgdmFyaWFudHMuaGFzT3duUHJvcGVydHkodmFyaWFudCkgJiYgdGhpcy5zZXREYXRhQXR0cmlidXRlKGRhdGEsICd2YXJpYW50JywgdmFyaWFudCk7XG4gICAgbm9kZS5nZXRQcm9wZXJ0eSgndmFyaWFudEZvcm0nKSAmJiB0aGlzLnNldERhdGFBdHRyaWJ1dGUoZGF0YSwgJ2FsdGVybmF0ZScsICcxJyk7XG4gICAgbm9kZS5nZXRQcm9wZXJ0eSgncHNldWRvc2NyaXB0JykgJiYgdGhpcy5zZXREYXRhQXR0cmlidXRlKGRhdGEsICdwc2V1ZG9zY3JpcHQnLCAndHJ1ZScpO1xuICAgIG5vZGUuZ2V0UHJvcGVydHkoJ2F1dG9PUCcpID09PSBmYWxzZSAmJiB0aGlzLnNldERhdGFBdHRyaWJ1dGUoZGF0YSwgJ2F1dG8tb3AnLCAnZmFsc2UnKTtcbiAgICB2YXIgc2NyaXB0YWxpZ24gPSBub2RlLmdldFByb3BlcnR5KCdzY3JpcHRhbGlnbicpO1xuICAgIHNjcmlwdGFsaWduICYmIHRoaXMuc2V0RGF0YUF0dHJpYnV0ZShkYXRhLCAnc2NyaXB0LWFsaWduJywgc2NyaXB0YWxpZ24pO1xuICAgIHZhciB0ZXhjbGFzcyA9IG5vZGUuZ2V0UHJvcGVydHkoJ3RleENsYXNzJyk7XG4gICAgaWYgKHRleGNsYXNzICE9PSB1bmRlZmluZWQpIHtcbiAgICAgIHZhciBzZXRjbGFzcyA9IHRydWU7XG4gICAgICBpZiAodGV4Y2xhc3MgPT09IE1tbE5vZGVfanNfMS5URVhDTEFTUy5PUCAmJiBub2RlLmlzS2luZCgnbWknKSkge1xuICAgICAgICB2YXIgbmFtZV8yID0gbm9kZS5nZXRUZXh0KCk7XG4gICAgICAgIHNldGNsYXNzID0gIShuYW1lXzIubGVuZ3RoID4gMSAmJiBuYW1lXzIubWF0Y2gobWlfanNfMS5NbWxNaS5vcGVyYXRvck5hbWUpKTtcbiAgICAgIH1cbiAgICAgIHNldGNsYXNzICYmIHRoaXMuc2V0RGF0YUF0dHJpYnV0ZShkYXRhLCAndGV4Y2xhc3MnLCB0ZXhjbGFzcyA8IDAgPyAnTk9ORScgOiBNbWxOb2RlX2pzXzEuVEVYQ0xBU1NOQU1FU1t0ZXhjbGFzc10pO1xuICAgIH1cbiAgICBub2RlLmdldFByb3BlcnR5KCdzY3JpcHRsZXZlbCcpICYmIG5vZGUuZ2V0UHJvcGVydHkoJ3VzZUhlaWdodCcpID09PSBmYWxzZSAmJiB0aGlzLnNldERhdGFBdHRyaWJ1dGUoZGF0YSwgJ3NtYWxsbWF0cml4JywgJ3RydWUnKTtcbiAgICByZXR1cm4gZGF0YTtcbiAgfTtcbiAgU2VyaWFsaXplZE1tbFZpc2l0b3IucHJvdG90eXBlLnNldERhdGFBdHRyaWJ1dGUgPSBmdW5jdGlvbiAoZGF0YSwgbmFtZSwgdmFsdWUpIHtcbiAgICBkYXRhW2V4cG9ydHMuREFUQU1KWCArIG5hbWVdID0gdmFsdWU7XG4gIH07XG4gIFNlcmlhbGl6ZWRNbWxWaXNpdG9yLnByb3RvdHlwZS5xdW90ZUhUTUwgPSBmdW5jdGlvbiAodmFsdWUpIHtcbiAgICByZXR1cm4gdmFsdWUucmVwbGFjZSgvJi9nLCAnJmFtcDsnKS5yZXBsYWNlKC88L2csICcmbHQ7JykucmVwbGFjZSgvPi9nLCAnJmd0OycpLnJlcGxhY2UoL1xcXCIvZywgJyZxdW90OycpLnJlcGxhY2UoL1tcXHVEODAwLVxcdURCRkZdLi9nLCBleHBvcnRzLnRvRW50aXR5KS5yZXBsYWNlKC9bXFx1MDA4MC1cXHVEN0ZGXFx1RTAwMC1cXHVGRkZGXS9nLCBleHBvcnRzLnRvRW50aXR5KTtcbiAgfTtcbiAgU2VyaWFsaXplZE1tbFZpc2l0b3IudmFyaWFudHMgPSB7XG4gICAgJy10ZXgtY2FsbGlncmFwaGljJzogJ3NjcmlwdCcsXG4gICAgJy10ZXgtYm9sZC1jYWxsaWdyYXBoaWMnOiAnYm9sZC1zY3JpcHQnLFxuICAgICctdGV4LW9sZHN0eWxlJzogJ25vcm1hbCcsXG4gICAgJy10ZXgtYm9sZC1vbGRzdHlsZSc6ICdib2xkJyxcbiAgICAnLXRleC1tYXRoaXQnOiAnaXRhbGljJ1xuICB9O1xuICBTZXJpYWxpemVkTW1sVmlzaXRvci5kZWZhdWx0QXR0cmlidXRlcyA9IHtcbiAgICBtYXRoOiB7XG4gICAgICB4bWxuczogJ2h0dHA6Ly93d3cudzMub3JnLzE5OTgvTWF0aC9NYXRoTUwnXG4gICAgfVxuICB9O1xuICByZXR1cm4gU2VyaWFsaXplZE1tbFZpc2l0b3I7XG59KE1tbFZpc2l0b3JfanNfMS5NbWxWaXNpdG9yKTtcbmV4cG9ydHMuU2VyaWFsaXplZE1tbFZpc2l0b3IgPSBTZXJpYWxpemVkTW1sVmlzaXRvcjsiLCJcInVzZSBzdHJpY3RcIjtcblxudmFyIF9fZXh0ZW5kcyA9IHRoaXMgJiYgdGhpcy5fX2V4dGVuZHMgfHwgZnVuY3Rpb24gKCkge1xuICB2YXIgZXh0ZW5kU3RhdGljcyA9IGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgZXh0ZW5kU3RhdGljcyA9IE9iamVjdC5zZXRQcm90b3R5cGVPZiB8fCB7XG4gICAgICBfX3Byb3RvX186IFtdXG4gICAgfSBpbnN0YW5jZW9mIEFycmF5ICYmIGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgICBkLl9fcHJvdG9fXyA9IGI7XG4gICAgfSB8fCBmdW5jdGlvbiAoZCwgYikge1xuICAgICAgZm9yICh2YXIgcCBpbiBiKSBpZiAoT2JqZWN0LnByb3RvdHlwZS5oYXNPd25Qcm9wZXJ0eS5jYWxsKGIsIHApKSBkW3BdID0gYltwXTtcbiAgICB9O1xuICAgIHJldHVybiBleHRlbmRTdGF0aWNzKGQsIGIpO1xuICB9O1xuICByZXR1cm4gZnVuY3Rpb24gKGQsIGIpIHtcbiAgICBpZiAodHlwZW9mIGIgIT09IFwiZnVuY3Rpb25cIiAmJiBiICE9PSBudWxsKSB0aHJvdyBuZXcgVHlwZUVycm9yKFwiQ2xhc3MgZXh0ZW5kcyB2YWx1ZSBcIiArIFN0cmluZyhiKSArIFwiIGlzIG5vdCBhIGNvbnN0cnVjdG9yIG9yIG51bGxcIik7XG4gICAgZXh0ZW5kU3RhdGljcyhkLCBiKTtcbiAgICBmdW5jdGlvbiBfXygpIHtcbiAgICAgIHRoaXMuY29uc3RydWN0b3IgPSBkO1xuICAgIH1cbiAgICBkLnByb3RvdHlwZSA9IGIgPT09IG51bGwgPyBPYmplY3QuY3JlYXRlKGIpIDogKF9fLnByb3RvdHlwZSA9IGIucHJvdG90eXBlLCBuZXcgX18oKSk7XG4gIH07XG59KCk7XG52YXIgX19hc3NpZ24gPSB0aGlzICYmIHRoaXMuX19hc3NpZ24gfHwgZnVuY3Rpb24gKCkge1xuICBfX2Fzc2lnbiA9IE9iamVjdC5hc3NpZ24gfHwgZnVuY3Rpb24gKHQpIHtcbiAgICBmb3IgKHZhciBzLCBpID0gMSwgbiA9IGFyZ3VtZW50cy5sZW5ndGg7IGkgPCBuOyBpKyspIHtcbiAgICAgIHMgPSBhcmd1bWVudHNbaV07XG4gICAgICBmb3IgKHZhciBwIGluIHMpIGlmIChPYmplY3QucHJvdG90eXBlLmhhc093blByb3BlcnR5LmNhbGwocywgcCkpIHRbcF0gPSBzW3BdO1xuICAgIH1cbiAgICByZXR1cm4gdDtcbiAgfTtcbiAgcmV0dXJuIF9fYXNzaWduLmFwcGx5KHRoaXMsIGFyZ3VtZW50cyk7XG59O1xudmFyIF9fcmVhZCA9IHRoaXMgJiYgdGhpcy5fX3JlYWQgfHwgZnVuY3Rpb24gKG8sIG4pIHtcbiAgdmFyIG0gPSB0eXBlb2YgU3ltYm9sID09PSBcImZ1bmN0aW9uXCIgJiYgb1tTeW1ib2wuaXRlcmF0b3JdO1xuICBpZiAoIW0pIHJldHVybiBvO1xuICB2YXIgaSA9IG0uY2FsbChvKSxcbiAgICByLFxuICAgIGFyID0gW10sXG4gICAgZTtcbiAgdHJ5IHtcbiAgICB3aGlsZSAoKG4gPT09IHZvaWQgMCB8fCBuLS0gPiAwKSAmJiAhKHIgPSBpLm5leHQoKSkuZG9uZSkgYXIucHVzaChyLnZhbHVlKTtcbiAgfSBjYXRjaCAoZXJyb3IpIHtcbiAgICBlID0ge1xuICAgICAgZXJyb3I6IGVycm9yXG4gICAgfTtcbiAgfSBmaW5hbGx5IHtcbiAgICB0cnkge1xuICAgICAgaWYgKHIgJiYgIXIuZG9uZSAmJiAobSA9IGlbXCJyZXR1cm5cIl0pKSBtLmNhbGwoaSk7XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIGlmIChlKSB0aHJvdyBlLmVycm9yO1xuICAgIH1cbiAgfVxuICByZXR1cm4gYXI7XG59O1xudmFyIF9fc3ByZWFkQXJyYXkgPSB0aGlzICYmIHRoaXMuX19zcHJlYWRBcnJheSB8fCBmdW5jdGlvbiAodG8sIGZyb20sIHBhY2spIHtcbiAgaWYgKHBhY2sgfHwgYXJndW1lbnRzLmxlbmd0aCA9PT0gMikgZm9yICh2YXIgaSA9IDAsIGwgPSBmcm9tLmxlbmd0aCwgYXI7IGkgPCBsOyBpKyspIHtcbiAgICBpZiAoYXIgfHwgIShpIGluIGZyb20pKSB7XG4gICAgICBpZiAoIWFyKSBhciA9IEFycmF5LnByb3RvdHlwZS5zbGljZS5jYWxsKGZyb20sIDAsIGkpO1xuICAgICAgYXJbaV0gPSBmcm9tW2ldO1xuICAgIH1cbiAgfVxuICByZXR1cm4gdG8uY29uY2F0KGFyIHx8IEFycmF5LnByb3RvdHlwZS5zbGljZS5jYWxsKGZyb20pKTtcbn07XG52YXIgX192YWx1ZXMgPSB0aGlzICYmIHRoaXMuX192YWx1ZXMgfHwgZnVuY3Rpb24gKG8pIHtcbiAgdmFyIHMgPSB0eXBlb2YgU3ltYm9sID09PSBcImZ1bmN0aW9uXCIgJiYgU3ltYm9sLml0ZXJhdG9yLFxuICAgIG0gPSBzICYmIG9bc10sXG4gICAgaSA9IDA7XG4gIGlmIChtKSByZXR1cm4gbS5jYWxsKG8pO1xuICBpZiAobyAmJiB0eXBlb2Ygby5sZW5ndGggPT09IFwibnVtYmVyXCIpIHJldHVybiB7XG4gICAgbmV4dDogZnVuY3Rpb24gKCkge1xuICAgICAgaWYgKG8gJiYgaSA+PSBvLmxlbmd0aCkgbyA9IHZvaWQgMDtcbiAgICAgIHJldHVybiB7XG4gICAgICAgIHZhbHVlOiBvICYmIG9baSsrXSxcbiAgICAgICAgZG9uZTogIW9cbiAgICAgIH07XG4gICAgfVxuICB9O1xuICB0aHJvdyBuZXcgVHlwZUVycm9yKHMgPyBcIk9iamVjdCBpcyBub3QgaXRlcmFibGUuXCIgOiBcIlN5bWJvbC5pdGVyYXRvciBpcyBub3QgZGVmaW5lZC5cIik7XG59O1xuT2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFwiX19lc01vZHVsZVwiLCB7XG4gIHZhbHVlOiB0cnVlXG59KTtcbmV4cG9ydHMuQXNzaXN0aXZlTW1sSGFuZGxlciA9IGV4cG9ydHMuQXNzaXN0aXZlTW1sTWF0aERvY3VtZW50TWl4aW4gPSBleHBvcnRzLkFzc2lzdGl2ZU1tbE1hdGhJdGVtTWl4aW4gPSBleHBvcnRzLkxpbWl0ZWRNbWxWaXNpdG9yID0gdm9pZCAwO1xudmFyIE1hdGhJdGVtX2pzXzEgPSByZXF1aXJlKFwiLi4vY29yZS9NYXRoSXRlbS5qc1wiKTtcbnZhciBTZXJpYWxpemVkTW1sVmlzaXRvcl9qc18xID0gcmVxdWlyZShcIi4uL2NvcmUvTW1sVHJlZS9TZXJpYWxpemVkTW1sVmlzaXRvci5qc1wiKTtcbnZhciBPcHRpb25zX2pzXzEgPSByZXF1aXJlKFwiLi4vdXRpbC9PcHRpb25zLmpzXCIpO1xudmFyIExpbWl0ZWRNbWxWaXNpdG9yID0gZnVuY3Rpb24gKF9zdXBlcikge1xuICBfX2V4dGVuZHMoTGltaXRlZE1tbFZpc2l0b3IsIF9zdXBlcik7XG4gIGZ1bmN0aW9uIExpbWl0ZWRNbWxWaXNpdG9yKCkge1xuICAgIHJldHVybiBfc3VwZXIgIT09IG51bGwgJiYgX3N1cGVyLmFwcGx5KHRoaXMsIGFyZ3VtZW50cykgfHwgdGhpcztcbiAgfVxuICBMaW1pdGVkTW1sVmlzaXRvci5wcm90b3R5cGUuZ2V0QXR0cmlidXRlcyA9IGZ1bmN0aW9uIChub2RlKSB7XG4gICAgcmV0dXJuIF9zdXBlci5wcm90b3R5cGUuZ2V0QXR0cmlidXRlcy5jYWxsKHRoaXMsIG5vZGUpLnJlcGxhY2UoLyA/aWQ9XCIuKj9cIi8sICcnKTtcbiAgfTtcbiAgcmV0dXJuIExpbWl0ZWRNbWxWaXNpdG9yO1xufShTZXJpYWxpemVkTW1sVmlzaXRvcl9qc18xLlNlcmlhbGl6ZWRNbWxWaXNpdG9yKTtcbmV4cG9ydHMuTGltaXRlZE1tbFZpc2l0b3IgPSBMaW1pdGVkTW1sVmlzaXRvcjtcbigwLCBNYXRoSXRlbV9qc18xLm5ld1N0YXRlKSgnQVNTSVNUSVZFTU1MJywgMTUzKTtcbmZ1bmN0aW9uIEFzc2lzdGl2ZU1tbE1hdGhJdGVtTWl4aW4oQmFzZU1hdGhJdGVtKSB7XG4gIHJldHVybiBmdW5jdGlvbiAoX3N1cGVyKSB7XG4gICAgX19leHRlbmRzKGNsYXNzXzEsIF9zdXBlcik7XG4gICAgZnVuY3Rpb24gY2xhc3NfMSgpIHtcbiAgICAgIHJldHVybiBfc3VwZXIgIT09IG51bGwgJiYgX3N1cGVyLmFwcGx5KHRoaXMsIGFyZ3VtZW50cykgfHwgdGhpcztcbiAgICB9XG4gICAgY2xhc3NfMS5wcm90b3R5cGUuYXNzaXN0aXZlTW1sID0gZnVuY3Rpb24gKGRvY3VtZW50LCBmb3JjZSkge1xuICAgICAgaWYgKGZvcmNlID09PSB2b2lkIDApIHtcbiAgICAgICAgZm9yY2UgPSBmYWxzZTtcbiAgICAgIH1cbiAgICAgIGlmICh0aGlzLnN0YXRlKCkgPj0gTWF0aEl0ZW1fanNfMS5TVEFURS5BU1NJU1RJVkVNTUwpIHJldHVybjtcbiAgICAgIGlmICghdGhpcy5pc0VzY2FwZWQgJiYgKGRvY3VtZW50Lm9wdGlvbnMuZW5hYmxlQXNzaXN0aXZlTW1sIHx8IGZvcmNlKSkge1xuICAgICAgICB2YXIgYWRhcHRvciA9IGRvY3VtZW50LmFkYXB0b3I7XG4gICAgICAgIHZhciBtbWwgPSBkb2N1bWVudC50b01NTCh0aGlzLnJvb3QpLnJlcGxhY2UoL1xcbiAqL2csICcnKS5yZXBsYWNlKC88IS0tLio/LS0+L2csICcnKTtcbiAgICAgICAgdmFyIG1tbE5vZGVzID0gYWRhcHRvci5maXJzdENoaWxkKGFkYXB0b3IuYm9keShhZGFwdG9yLnBhcnNlKG1tbCwgJ3RleHQvaHRtbCcpKSk7XG4gICAgICAgIHZhciBub2RlID0gYWRhcHRvci5ub2RlKCdtangtYXNzaXN0aXZlLW1tbCcsIHtcbiAgICAgICAgICB1bnNlbGVjdGFibGU6ICdvbicsXG4gICAgICAgICAgZGlzcGxheTogdGhpcy5kaXNwbGF5ID8gJ2Jsb2NrJyA6ICdpbmxpbmUnXG4gICAgICAgIH0sIFttbWxOb2Rlc10pO1xuICAgICAgICBhZGFwdG9yLnNldEF0dHJpYnV0ZShhZGFwdG9yLmZpcnN0Q2hpbGQodGhpcy50eXBlc2V0Um9vdCksICdhcmlhLWhpZGRlbicsICd0cnVlJyk7XG4gICAgICAgIGFkYXB0b3Iuc2V0U3R5bGUodGhpcy50eXBlc2V0Um9vdCwgJ3Bvc2l0aW9uJywgJ3JlbGF0aXZlJyk7XG4gICAgICAgIGFkYXB0b3IuYXBwZW5kKHRoaXMudHlwZXNldFJvb3QsIG5vZGUpO1xuICAgICAgfVxuICAgICAgdGhpcy5zdGF0ZShNYXRoSXRlbV9qc18xLlNUQVRFLkFTU0lTVElWRU1NTCk7XG4gICAgfTtcbiAgICByZXR1cm4gY2xhc3NfMTtcbiAgfShCYXNlTWF0aEl0ZW0pO1xufVxuZXhwb3J0cy5Bc3Npc3RpdmVNbWxNYXRoSXRlbU1peGluID0gQXNzaXN0aXZlTW1sTWF0aEl0ZW1NaXhpbjtcbmZ1bmN0aW9uIEFzc2lzdGl2ZU1tbE1hdGhEb2N1bWVudE1peGluKEJhc2VEb2N1bWVudCkge1xuICB2YXIgX2E7XG4gIHJldHVybiBfYSA9IGZ1bmN0aW9uIChfc3VwZXIpIHtcbiAgICBfX2V4dGVuZHMoQmFzZUNsYXNzLCBfc3VwZXIpO1xuICAgIGZ1bmN0aW9uIEJhc2VDbGFzcygpIHtcbiAgICAgIHZhciBhcmdzID0gW107XG4gICAgICBmb3IgKHZhciBfaSA9IDA7IF9pIDwgYXJndW1lbnRzLmxlbmd0aDsgX2krKykge1xuICAgICAgICBhcmdzW19pXSA9IGFyZ3VtZW50c1tfaV07XG4gICAgICB9XG4gICAgICB2YXIgX3RoaXMgPSBfc3VwZXIuYXBwbHkodGhpcywgX19zcHJlYWRBcnJheShbXSwgX19yZWFkKGFyZ3MpLCBmYWxzZSkpIHx8IHRoaXM7XG4gICAgICB2YXIgQ0xBU1MgPSBfdGhpcy5jb25zdHJ1Y3RvcjtcbiAgICAgIHZhciBQcm9jZXNzQml0cyA9IENMQVNTLlByb2Nlc3NCaXRzO1xuICAgICAgaWYgKCFQcm9jZXNzQml0cy5oYXMoJ2Fzc2lzdGl2ZS1tbWwnKSkge1xuICAgICAgICBQcm9jZXNzQml0cy5hbGxvY2F0ZSgnYXNzaXN0aXZlLW1tbCcpO1xuICAgICAgfVxuICAgICAgX3RoaXMudmlzaXRvciA9IG5ldyBMaW1pdGVkTW1sVmlzaXRvcihfdGhpcy5tbWxGYWN0b3J5KTtcbiAgICAgIF90aGlzLm9wdGlvbnMuTWF0aEl0ZW0gPSBBc3Npc3RpdmVNbWxNYXRoSXRlbU1peGluKF90aGlzLm9wdGlvbnMuTWF0aEl0ZW0pO1xuICAgICAgaWYgKCdhZGRTdHlsZXMnIGluIF90aGlzKSB7XG4gICAgICAgIF90aGlzLmFkZFN0eWxlcyhDTEFTUy5hc3Npc3RpdmVTdHlsZXMpO1xuICAgICAgfVxuICAgICAgcmV0dXJuIF90aGlzO1xuICAgIH1cbiAgICBCYXNlQ2xhc3MucHJvdG90eXBlLnRvTU1MID0gZnVuY3Rpb24gKG5vZGUpIHtcbiAgICAgIHJldHVybiB0aGlzLnZpc2l0b3IudmlzaXRUcmVlKG5vZGUpO1xuICAgIH07XG4gICAgQmFzZUNsYXNzLnByb3RvdHlwZS5hc3Npc3RpdmVNbWwgPSBmdW5jdGlvbiAoKSB7XG4gICAgICB2YXIgZV8xLCBfYTtcbiAgICAgIGlmICghdGhpcy5wcm9jZXNzZWQuaXNTZXQoJ2Fzc2lzdGl2ZS1tbWwnKSkge1xuICAgICAgICB0cnkge1xuICAgICAgICAgIGZvciAodmFyIF9iID0gX192YWx1ZXModGhpcy5tYXRoKSwgX2MgPSBfYi5uZXh0KCk7ICFfYy5kb25lOyBfYyA9IF9iLm5leHQoKSkge1xuICAgICAgICAgICAgdmFyIG1hdGggPSBfYy52YWx1ZTtcbiAgICAgICAgICAgIG1hdGguYXNzaXN0aXZlTW1sKHRoaXMpO1xuICAgICAgICAgIH1cbiAgICAgICAgfSBjYXRjaCAoZV8xXzEpIHtcbiAgICAgICAgICBlXzEgPSB7XG4gICAgICAgICAgICBlcnJvcjogZV8xXzFcbiAgICAgICAgICB9O1xuICAgICAgICB9IGZpbmFsbHkge1xuICAgICAgICAgIHRyeSB7XG4gICAgICAgICAgICBpZiAoX2MgJiYgIV9jLmRvbmUgJiYgKF9hID0gX2IucmV0dXJuKSkgX2EuY2FsbChfYik7XG4gICAgICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgICAgIGlmIChlXzEpIHRocm93IGVfMS5lcnJvcjtcbiAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgICAgdGhpcy5wcm9jZXNzZWQuc2V0KCdhc3Npc3RpdmUtbW1sJyk7XG4gICAgICB9XG4gICAgICByZXR1cm4gdGhpcztcbiAgICB9O1xuICAgIEJhc2VDbGFzcy5wcm90b3R5cGUuc3RhdGUgPSBmdW5jdGlvbiAoc3RhdGUsIHJlc3RvcmUpIHtcbiAgICAgIGlmIChyZXN0b3JlID09PSB2b2lkIDApIHtcbiAgICAgICAgcmVzdG9yZSA9IGZhbHNlO1xuICAgICAgfVxuICAgICAgX3N1cGVyLnByb3RvdHlwZS5zdGF0ZS5jYWxsKHRoaXMsIHN0YXRlLCByZXN0b3JlKTtcbiAgICAgIGlmIChzdGF0ZSA8IE1hdGhJdGVtX2pzXzEuU1RBVEUuQVNTSVNUSVZFTU1MKSB7XG4gICAgICAgIHRoaXMucHJvY2Vzc2VkLmNsZWFyKCdhc3Npc3RpdmUtbW1sJyk7XG4gICAgICB9XG4gICAgICByZXR1cm4gdGhpcztcbiAgICB9O1xuICAgIHJldHVybiBCYXNlQ2xhc3M7XG4gIH0oQmFzZURvY3VtZW50KSwgX2EuT1BUSU9OUyA9IF9fYXNzaWduKF9fYXNzaWduKHt9LCBCYXNlRG9jdW1lbnQuT1BUSU9OUyksIHtcbiAgICBlbmFibGVBc3Npc3RpdmVNbWw6IHRydWUsXG4gICAgcmVuZGVyQWN0aW9uczogKDAsIE9wdGlvbnNfanNfMS5leHBhbmRhYmxlKShfX2Fzc2lnbihfX2Fzc2lnbih7fSwgQmFzZURvY3VtZW50Lk9QVElPTlMucmVuZGVyQWN0aW9ucyksIHtcbiAgICAgIGFzc2lzdGl2ZU1tbDogW01hdGhJdGVtX2pzXzEuU1RBVEUuQVNTSVNUSVZFTU1MXVxuICAgIH0pKVxuICB9KSwgX2EuYXNzaXN0aXZlU3R5bGVzID0ge1xuICAgICdtangtYXNzaXN0aXZlLW1tbCc6IHtcbiAgICAgIHBvc2l0aW9uOiAnYWJzb2x1dGUgIWltcG9ydGFudCcsXG4gICAgICB0b3A6ICcwcHgnLFxuICAgICAgbGVmdDogJzBweCcsXG4gICAgICBjbGlwOiAncmVjdCgxcHgsIDFweCwgMXB4LCAxcHgpJyxcbiAgICAgIHBhZGRpbmc6ICcxcHggMHB4IDBweCAwcHggIWltcG9ydGFudCcsXG4gICAgICBib3JkZXI6ICcwcHggIWltcG9ydGFudCcsXG4gICAgICBkaXNwbGF5OiAnYmxvY2sgIWltcG9ydGFudCcsXG4gICAgICB3aWR0aDogJ2F1dG8gIWltcG9ydGFudCcsXG4gICAgICBvdmVyZmxvdzogJ2hpZGRlbiAhaW1wb3J0YW50JyxcbiAgICAgICctd2Via2l0LXRvdWNoLWNhbGxvdXQnOiAnbm9uZScsXG4gICAgICAnLXdlYmtpdC11c2VyLXNlbGVjdCc6ICdub25lJyxcbiAgICAgICcta2h0bWwtdXNlci1zZWxlY3QnOiAnbm9uZScsXG4gICAgICAnLW1vei11c2VyLXNlbGVjdCc6ICdub25lJyxcbiAgICAgICctbXMtdXNlci1zZWxlY3QnOiAnbm9uZScsXG4gICAgICAndXNlci1zZWxlY3QnOiAnbm9uZSdcbiAgICB9LFxuICAgICdtangtYXNzaXN0aXZlLW1tbFtkaXNwbGF5PVwiYmxvY2tcIl0nOiB7XG4gICAgICB3aWR0aDogJzEwMCUgIWltcG9ydGFudCdcbiAgICB9XG4gIH0sIF9hO1xufVxuZXhwb3J0cy5Bc3Npc3RpdmVNbWxNYXRoRG9jdW1lbnRNaXhpbiA9IEFzc2lzdGl2ZU1tbE1hdGhEb2N1bWVudE1peGluO1xuZnVuY3Rpb24gQXNzaXN0aXZlTW1sSGFuZGxlcihoYW5kbGVyKSB7XG4gIGhhbmRsZXIuZG9jdW1lbnRDbGFzcyA9IEFzc2lzdGl2ZU1tbE1hdGhEb2N1bWVudE1peGluKGhhbmRsZXIuZG9jdW1lbnRDbGFzcyk7XG4gIHJldHVybiBoYW5kbGVyO1xufVxuZXhwb3J0cy5Bc3Npc3RpdmVNbWxIYW5kbGVyID0gQXNzaXN0aXZlTW1sSGFuZGxlcjsiLCJcInVzZSBzdHJpY3RcIjtcblxudmFyIF9fdmFsdWVzID0gdGhpcyAmJiB0aGlzLl9fdmFsdWVzIHx8IGZ1bmN0aW9uIChvKSB7XG4gIHZhciBzID0gdHlwZW9mIFN5bWJvbCA9PT0gXCJmdW5jdGlvblwiICYmIFN5bWJvbC5pdGVyYXRvcixcbiAgICBtID0gcyAmJiBvW3NdLFxuICAgIGkgPSAwO1xuICBpZiAobSkgcmV0dXJuIG0uY2FsbChvKTtcbiAgaWYgKG8gJiYgdHlwZW9mIG8ubGVuZ3RoID09PSBcIm51bWJlclwiKSByZXR1cm4ge1xuICAgIG5leHQ6IGZ1bmN0aW9uICgpIHtcbiAgICAgIGlmIChvICYmIGkgPj0gby5sZW5ndGgpIG8gPSB2b2lkIDA7XG4gICAgICByZXR1cm4ge1xuICAgICAgICB2YWx1ZTogbyAmJiBvW2krK10sXG4gICAgICAgIGRvbmU6ICFvXG4gICAgICB9O1xuICAgIH1cbiAgfTtcbiAgdGhyb3cgbmV3IFR5cGVFcnJvcihzID8gXCJPYmplY3QgaXMgbm90IGl0ZXJhYmxlLlwiIDogXCJTeW1ib2wuaXRlcmF0b3IgaXMgbm90IGRlZmluZWQuXCIpO1xufTtcbnZhciBfX3JlYWQgPSB0aGlzICYmIHRoaXMuX19yZWFkIHx8IGZ1bmN0aW9uIChvLCBuKSB7XG4gIHZhciBtID0gdHlwZW9mIFN5bWJvbCA9PT0gXCJmdW5jdGlvblwiICYmIG9bU3ltYm9sLml0ZXJhdG9yXTtcbiAgaWYgKCFtKSByZXR1cm4gbztcbiAgdmFyIGkgPSBtLmNhbGwobyksXG4gICAgcixcbiAgICBhciA9IFtdLFxuICAgIGU7XG4gIHRyeSB7XG4gICAgd2hpbGUgKChuID09PSB2b2lkIDAgfHwgbi0tID4gMCkgJiYgIShyID0gaS5uZXh0KCkpLmRvbmUpIGFyLnB1c2goci52YWx1ZSk7XG4gIH0gY2F0Y2ggKGVycm9yKSB7XG4gICAgZSA9IHtcbiAgICAgIGVycm9yOiBlcnJvclxuICAgIH07XG4gIH0gZmluYWxseSB7XG4gICAgdHJ5IHtcbiAgICAgIGlmIChyICYmICFyLmRvbmUgJiYgKG0gPSBpW1wicmV0dXJuXCJdKSkgbS5jYWxsKGkpO1xuICAgIH0gZmluYWxseSB7XG4gICAgICBpZiAoZSkgdGhyb3cgZS5lcnJvcjtcbiAgICB9XG4gIH1cbiAgcmV0dXJuIGFyO1xufTtcbnZhciBfX3NwcmVhZEFycmF5ID0gdGhpcyAmJiB0aGlzLl9fc3ByZWFkQXJyYXkgfHwgZnVuY3Rpb24gKHRvLCBmcm9tLCBwYWNrKSB7XG4gIGlmIChwYWNrIHx8IGFyZ3VtZW50cy5sZW5ndGggPT09IDIpIGZvciAodmFyIGkgPSAwLCBsID0gZnJvbS5sZW5ndGgsIGFyOyBpIDwgbDsgaSsrKSB7XG4gICAgaWYgKGFyIHx8ICEoaSBpbiBmcm9tKSkge1xuICAgICAgaWYgKCFhcikgYXIgPSBBcnJheS5wcm90b3R5cGUuc2xpY2UuY2FsbChmcm9tLCAwLCBpKTtcbiAgICAgIGFyW2ldID0gZnJvbVtpXTtcbiAgICB9XG4gIH1cbiAgcmV0dXJuIHRvLmNvbmNhdChhciB8fCBBcnJheS5wcm90b3R5cGUuc2xpY2UuY2FsbChmcm9tKSk7XG59O1xuT2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFwiX19lc01vZHVsZVwiLCB7XG4gIHZhbHVlOiB0cnVlXG59KTtcbmV4cG9ydHMuQWJzdHJhY3RWaXNpdG9yID0gdm9pZCAwO1xudmFyIE5vZGVfanNfMSA9IHJlcXVpcmUoXCIuL05vZGUuanNcIik7XG52YXIgQWJzdHJhY3RWaXNpdG9yID0gZnVuY3Rpb24gKCkge1xuICBmdW5jdGlvbiBBYnN0cmFjdFZpc2l0b3IoZmFjdG9yeSkge1xuICAgIHZhciBlXzEsIF9hO1xuICAgIHRoaXMubm9kZUhhbmRsZXJzID0gbmV3IE1hcCgpO1xuICAgIHRyeSB7XG4gICAgICBmb3IgKHZhciBfYiA9IF9fdmFsdWVzKGZhY3RvcnkuZ2V0S2luZHMoKSksIF9jID0gX2IubmV4dCgpOyAhX2MuZG9uZTsgX2MgPSBfYi5uZXh0KCkpIHtcbiAgICAgICAgdmFyIGtpbmQgPSBfYy52YWx1ZTtcbiAgICAgICAgdmFyIG1ldGhvZCA9IHRoaXNbQWJzdHJhY3RWaXNpdG9yLm1ldGhvZE5hbWUoa2luZCldO1xuICAgICAgICBpZiAobWV0aG9kKSB7XG4gICAgICAgICAgdGhpcy5ub2RlSGFuZGxlcnMuc2V0KGtpbmQsIG1ldGhvZCk7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9IGNhdGNoIChlXzFfMSkge1xuICAgICAgZV8xID0ge1xuICAgICAgICBlcnJvcjogZV8xXzFcbiAgICAgIH07XG4gICAgfSBmaW5hbGx5IHtcbiAgICAgIHRyeSB7XG4gICAgICAgIGlmIChfYyAmJiAhX2MuZG9uZSAmJiAoX2EgPSBfYi5yZXR1cm4pKSBfYS5jYWxsKF9iKTtcbiAgICAgIH0gZmluYWxseSB7XG4gICAgICAgIGlmIChlXzEpIHRocm93IGVfMS5lcnJvcjtcbiAgICAgIH1cbiAgICB9XG4gIH1cbiAgQWJzdHJhY3RWaXNpdG9yLm1ldGhvZE5hbWUgPSBmdW5jdGlvbiAoa2luZCkge1xuICAgIHJldHVybiAndmlzaXQnICsgKGtpbmQuY2hhckF0KDApLnRvVXBwZXJDYXNlKCkgKyBraW5kLnN1YnN0cigxKSkucmVwbGFjZSgvW15hLXowLTlfXS9pZywgJ18nKSArICdOb2RlJztcbiAgfTtcbiAgQWJzdHJhY3RWaXNpdG9yLnByb3RvdHlwZS52aXNpdFRyZWUgPSBmdW5jdGlvbiAodHJlZSkge1xuICAgIHZhciBhcmdzID0gW107XG4gICAgZm9yICh2YXIgX2kgPSAxOyBfaSA8IGFyZ3VtZW50cy5sZW5ndGg7IF9pKyspIHtcbiAgICAgIGFyZ3NbX2kgLSAxXSA9IGFyZ3VtZW50c1tfaV07XG4gICAgfVxuICAgIHJldHVybiB0aGlzLnZpc2l0Tm9kZS5hcHBseSh0aGlzLCBfX3NwcmVhZEFycmF5KFt0cmVlXSwgX19yZWFkKGFyZ3MpLCBmYWxzZSkpO1xuICB9O1xuICBBYnN0cmFjdFZpc2l0b3IucHJvdG90eXBlLnZpc2l0Tm9kZSA9IGZ1bmN0aW9uIChub2RlKSB7XG4gICAgdmFyIGFyZ3MgPSBbXTtcbiAgICBmb3IgKHZhciBfaSA9IDE7IF9pIDwgYXJndW1lbnRzLmxlbmd0aDsgX2krKykge1xuICAgICAgYXJnc1tfaSAtIDFdID0gYXJndW1lbnRzW19pXTtcbiAgICB9XG4gICAgdmFyIGhhbmRsZXIgPSB0aGlzLm5vZGVIYW5kbGVycy5nZXQobm9kZS5raW5kKSB8fCB0aGlzLnZpc2l0RGVmYXVsdDtcbiAgICByZXR1cm4gaGFuZGxlci5jYWxsLmFwcGx5KGhhbmRsZXIsIF9fc3ByZWFkQXJyYXkoW3RoaXMsIG5vZGVdLCBfX3JlYWQoYXJncyksIGZhbHNlKSk7XG4gIH07XG4gIEFic3RyYWN0VmlzaXRvci5wcm90b3R5cGUudmlzaXREZWZhdWx0ID0gZnVuY3Rpb24gKG5vZGUpIHtcbiAgICB2YXIgZV8yLCBfYTtcbiAgICB2YXIgYXJncyA9IFtdO1xuICAgIGZvciAodmFyIF9pID0gMTsgX2kgPCBhcmd1bWVudHMubGVuZ3RoOyBfaSsrKSB7XG4gICAgICBhcmdzW19pIC0gMV0gPSBhcmd1bWVudHNbX2ldO1xuICAgIH1cbiAgICBpZiAobm9kZSBpbnN0YW5jZW9mIE5vZGVfanNfMS5BYnN0cmFjdE5vZGUpIHtcbiAgICAgIHRyeSB7XG4gICAgICAgIGZvciAodmFyIF9iID0gX192YWx1ZXMobm9kZS5jaGlsZE5vZGVzKSwgX2MgPSBfYi5uZXh0KCk7ICFfYy5kb25lOyBfYyA9IF9iLm5leHQoKSkge1xuICAgICAgICAgIHZhciBjaGlsZCA9IF9jLnZhbHVlO1xuICAgICAgICAgIHRoaXMudmlzaXROb2RlLmFwcGx5KHRoaXMsIF9fc3ByZWFkQXJyYXkoW2NoaWxkXSwgX19yZWFkKGFyZ3MpLCBmYWxzZSkpO1xuICAgICAgICB9XG4gICAgICB9IGNhdGNoIChlXzJfMSkge1xuICAgICAgICBlXzIgPSB7XG4gICAgICAgICAgZXJyb3I6IGVfMl8xXG4gICAgICAgIH07XG4gICAgICB9IGZpbmFsbHkge1xuICAgICAgICB0cnkge1xuICAgICAgICAgIGlmIChfYyAmJiAhX2MuZG9uZSAmJiAoX2EgPSBfYi5yZXR1cm4pKSBfYS5jYWxsKF9iKTtcbiAgICAgICAgfSBmaW5hbGx5IHtcbiAgICAgICAgICBpZiAoZV8yKSB0aHJvdyBlXzIuZXJyb3I7XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICB9XG4gIH07XG4gIEFic3RyYWN0VmlzaXRvci5wcm90b3R5cGUuc2V0Tm9kZUhhbmRsZXIgPSBmdW5jdGlvbiAoa2luZCwgaGFuZGxlcikge1xuICAgIHRoaXMubm9kZUhhbmRsZXJzLnNldChraW5kLCBoYW5kbGVyKTtcbiAgfTtcbiAgQWJzdHJhY3RWaXNpdG9yLnByb3RvdHlwZS5yZW1vdmVOb2RlSGFuZGxlciA9IGZ1bmN0aW9uIChraW5kKSB7XG4gICAgdGhpcy5ub2RlSGFuZGxlcnMuZGVsZXRlKGtpbmQpO1xuICB9O1xuICByZXR1cm4gQWJzdHJhY3RWaXNpdG9yO1xufSgpO1xuZXhwb3J0cy5BYnN0cmFjdFZpc2l0b3IgPSBBYnN0cmFjdFZpc2l0b3I7IiwiXCJ1c2Ugc3RyaWN0XCI7XG5cbnZhciBfX2V4dGVuZHMgPSB0aGlzICYmIHRoaXMuX19leHRlbmRzIHx8IGZ1bmN0aW9uICgpIHtcbiAgdmFyIGV4dGVuZFN0YXRpY3MgPSBmdW5jdGlvbiAoZCwgYikge1xuICAgIGV4dGVuZFN0YXRpY3MgPSBPYmplY3Quc2V0UHJvdG90eXBlT2YgfHwge1xuICAgICAgX19wcm90b19fOiBbXVxuICAgIH0gaW5zdGFuY2VvZiBBcnJheSAmJiBmdW5jdGlvbiAoZCwgYikge1xuICAgICAgZC5fX3Byb3RvX18gPSBiO1xuICAgIH0gfHwgZnVuY3Rpb24gKGQsIGIpIHtcbiAgICAgIGZvciAodmFyIHAgaW4gYikgaWYgKE9iamVjdC5wcm90b3R5cGUuaGFzT3duUHJvcGVydHkuY2FsbChiLCBwKSkgZFtwXSA9IGJbcF07XG4gICAgfTtcbiAgICByZXR1cm4gZXh0ZW5kU3RhdGljcyhkLCBiKTtcbiAgfTtcbiAgcmV0dXJuIGZ1bmN0aW9uIChkLCBiKSB7XG4gICAgaWYgKHR5cGVvZiBiICE9PSBcImZ1bmN0aW9uXCIgJiYgYiAhPT0gbnVsbCkgdGhyb3cgbmV3IFR5cGVFcnJvcihcIkNsYXNzIGV4dGVuZHMgdmFsdWUgXCIgKyBTdHJpbmcoYikgKyBcIiBpcyBub3QgYSBjb25zdHJ1Y3RvciBvciBudWxsXCIpO1xuICAgIGV4dGVuZFN0YXRpY3MoZCwgYik7XG4gICAgZnVuY3Rpb24gX18oKSB7XG4gICAgICB0aGlzLmNvbnN0cnVjdG9yID0gZDtcbiAgICB9XG4gICAgZC5wcm90b3R5cGUgPSBiID09PSBudWxsID8gT2JqZWN0LmNyZWF0ZShiKSA6IChfXy5wcm90b3R5cGUgPSBiLnByb3RvdHlwZSwgbmV3IF9fKCkpO1xuICB9O1xufSgpO1xuT2JqZWN0LmRlZmluZVByb3BlcnR5KGV4cG9ydHMsIFwiX19lc01vZHVsZVwiLCB7XG4gIHZhbHVlOiB0cnVlXG59KTtcbmV4cG9ydHMuTW1sVmlzaXRvciA9IHZvaWQgMDtcbnZhciBNbWxGYWN0b3J5X2pzXzEgPSByZXF1aXJlKFwiLi9NbWxGYWN0b3J5LmpzXCIpO1xudmFyIFZpc2l0b3JfanNfMSA9IHJlcXVpcmUoXCIuLi9UcmVlL1Zpc2l0b3IuanNcIik7XG52YXIgTW1sVmlzaXRvciA9IGZ1bmN0aW9uIChfc3VwZXIpIHtcbiAgX19leHRlbmRzKE1tbFZpc2l0b3IsIF9zdXBlcik7XG4gIGZ1bmN0aW9uIE1tbFZpc2l0b3IoZmFjdG9yeSkge1xuICAgIGlmIChmYWN0b3J5ID09PSB2b2lkIDApIHtcbiAgICAgIGZhY3RvcnkgPSBudWxsO1xuICAgIH1cbiAgICBpZiAoIWZhY3RvcnkpIHtcbiAgICAgIGZhY3RvcnkgPSBuZXcgTW1sRmFjdG9yeV9qc18xLk1tbEZhY3RvcnkoKTtcbiAgICB9XG4gICAgcmV0dXJuIF9zdXBlci5jYWxsKHRoaXMsIGZhY3RvcnkpIHx8IHRoaXM7XG4gIH1cbiAgTW1sVmlzaXRvci5wcm90b3R5cGUudmlzaXRUZXh0Tm9kZSA9IGZ1bmN0aW9uIChfbm9kZSkge1xuICAgIHZhciBfYXJncyA9IFtdO1xuICAgIGZvciAodmFyIF9pID0gMTsgX2kgPCBhcmd1bWVudHMubGVuZ3RoOyBfaSsrKSB7XG4gICAgICBfYXJnc1tfaSAtIDFdID0gYXJndW1lbnRzW19pXTtcbiAgICB9XG4gIH07XG4gIE1tbFZpc2l0b3IucHJvdG90eXBlLnZpc2l0WE1MTm9kZSA9IGZ1bmN0aW9uIChfbm9kZSkge1xuICAgIHZhciBfYXJncyA9IFtdO1xuICAgIGZvciAodmFyIF9pID0gMTsgX2kgPCBhcmd1bWVudHMubGVuZ3RoOyBfaSsrKSB7XG4gICAgICBfYXJnc1tfaSAtIDFdID0gYXJndW1lbnRzW19pXTtcbiAgICB9XG4gIH07XG4gIHJldHVybiBNbWxWaXNpdG9yO1xufShWaXNpdG9yX2pzXzEuQWJzdHJhY3RWaXNpdG9yKTtcbmV4cG9ydHMuTW1sVmlzaXRvciA9IE1tbFZpc2l0b3I7Il0sIm5hbWVzIjpbXSwiaWdub3JlTGlzdCI6W10sInNvdXJjZVJvb3QiOiIifQ==