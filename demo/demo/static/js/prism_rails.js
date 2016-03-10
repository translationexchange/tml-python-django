// borrowed from https://github.com/samflores
Prism.languages.ruby = {
  'comment': /#[^\r\n]*(\r?\n|$)/g,
  'string': /("|')(\\?.)*?\1/g,
  'regex': {
    pattern: /(^|[^/])\/(?!\/)(\[.+?]|\\.|[^/\r\n])+\/[gim]{0,3}(?=\s*($|[\r\n,.;})]))/g,
    lookbehind: true
  },
  'keyword': /\b(alias|and|BEGIN|begin|break|case|class|def|define_method|defined|do|each|else|elsif|END|end|ensure|false|for|if|in|module|new|next|nil|not|or|raise|redo|rescue|retry|return|self|super|then|throw|true|undef|unless|until|when|while|yield)\b/g,
  'builtin': /\b(Array|Bignum|Binding|Class|Continuation|Dir|Exception|FalseClass|File|Stat|File|Fixnum|Fload|Hash|Integer|IO|MatchData|Method|Module|NilClass|Numeric|Object|Proc|Range|Regexp|String|Struct|TMS|Symbol|ThreadGroup|Thread|Time|TrueClass)\b/,
  'boolean': /\b(true|false)\b/g,
  'number': /\b-?(0x)?\d*\.?\d+\b/g,
  'operator': /[-+]{1,2}|!|=?&lt;|=?&gt;|={1,2}|(&amp;){1,2}|\|?\||\?|\*|\//g,
  'inst-var': /[@&]\b[a-zA-Z_][a-zA-Z_0-9]*[?!]?\b/g,
  'namespace': /::\b[a-zA-Z_][a-zA-Z_0-9]*[?!]?\b/g,
  'symbol': /:\b[a-zA-Z_][a-zA-Z_0-9]*[?!]?\b/g,
  'const': /\b[A-Z][a-zA-Z_0-9]*[?!]?\b/g,
  'ignore': /&(lt|gt|amp);/gi,
  'punctuation': /[{}[\];(),.:]/g
};

Prism.languages.coffee = {
  'string': /("|')(\\?.)*?\1/g,
  'comment': /#[^\r\n]*(\r?\n|$)/g,
  'regex': {
    pattern: /(^|[^/])\/(?!\/)(\[.+?]|\\.|[^/\r\n])+\/[gim]{0,3}(?=\s*($|[\r\n,.;})]))/g,
    lookbehind: true
  },
  'boolean': /\b(true|false)\b/g,
  'number': /\b-?(0x)?\d*\.?\d+\b/g,
  'arrow': /(-|=)&gt;/g,
  'operator': /[-+]{1,2}|!|={1,2}|(&amp;){1,2}|\|?\||\?|\*|\//g,
  'var': /[@&]\b[a-zA-Z_][a-zA-Z_0-9]*[?!]?\b/g,
  'class': /\b[A-Z][a-zA-Z_0-9]*[?!]?\b/g,
  'ignore': /&(lt|gt|amp);/gi,
  'punctuation': /[{}[\];(),.:]/g
};

Prism.languages.haml = {
  'string': /("|')(\\?.)*?\1/g,
  'comment': /\/[^\r\n]*(\r?\n|$)/g,
  'boolean': /\b(true|false)\b/g,
  'number': /\b-?(0x)?\d*\.?\d+\b/g,
  'tag': /%[a-zA-Z_0-9]*\b/g,
  'var': /[@&]\b[a-zA-Z_0-9]*[?!]?\b/g,
  'operator': /[-+]{1,2}|!|={1,2}|(&amp;){1,2}|\|?\||\?|\*|\//g,
  'rails': /(form_tag|do|end|link_to|image_tag|content_for)/g,
  'ignore': /&(lt|gt|amp);/gi
};

Prism.languages.python={"triple-quoted-string":{pattern:/"""[\s\S]+?"""|'''[\s\S]+?'''/,alias:"string"},comment:{pattern:/(^|[^\\])#.*/,lookbehind:!0},string:/("|')(?:\\?.)*?\1/,"function":{pattern:/((?:^|\s)def[ \t]+)[a-zA-Z_][a-zA-Z0-9_]*(?=\()/g,lookbehind:!0},"class-name":{pattern:/(\bclass\s+)[a-z0-9_]+/i,lookbehind:!0},keyword:/\b(?:as|assert|async|await|break|class|continue|def|del|elif|else|except|exec|finally|for|from|global|if|import|in|is|lambda|pass|print|raise|return|try|while|with|yield)\b/,"boolean":/\b(?:True|False)\b/,number:/\b-?(?:0[bo])?(?:(?:\d|0x[\da-f])[\da-f]*\.?\d*|\.\d+)(?:e[+-]?\d+)?j?\b/i,operator:/[-+%=]=?|!=|\*\*?=?|\/\/?=?|<[<=>]?|>[=>]?|[&|^~]|\b(?:or|and|not)\b/,punctuation:/[{}[\];(),.:]/};
