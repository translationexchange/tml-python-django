(function() {
  addExamples("en", "English", [
    {separator: true, label: "Baiscs"},

    {label: "Hello World"},
    {label: "Invite", description: "An invitation"},
    {label: "Invite", description: "Action to invite someone"},

    {separator: true, label: "Numeric Rules"},

    {label: "Number of messages: {count}", tokens: {"count": 5}},
    {label: "You have {count||one:message,other:messages}", tokens: {"count": 5}},
    {label: "You have {count||message,messages}", tokens: {"count": 5}},
    {label: "You have {count|message}", tokens: {"count": 5}},

    {separator: true, label: "Gender Rules"},
    {label: "{user|male:He,female:She,other:He/She} likes this movie.", tokens: {user: "other"}},
    {label: "{user|He,She} likes this movie.", tokens: {user: "male"}},
    {label: "{user} uploaded a photo of {user|himself,herself}.", tokens: {user: [{"gender": "female", "name": "Anna"}, ":name"]}},

    {separator: true, label: "Decorators"},

    {label: "Hello [bold: World]"},
    {label: "Hello [bold: {user}]", tokens: {"user": "Michael"}},
    {label: "Hello [bold: {user}], you have {count||message,messages}.", tokens: {"user": "Michael", "count": 5}},
    {label: "Hello [bold: {user}], [italic: you have [bold: {count||message}]].", tokens: {"user": "Michael", "count": 1}},
    {label: "Hello [bold: {user}], [italic]you have [bold: {count||message,messages}][/italic].", tokens: {"user": "Michael", "count": 3}},

    {separator: true, label: "Implied Tokens"},

    {label: "{user|He,She} likes this post.", tokens: {"user": [{"gender": "male", "name": "Michael"}, ":name"]}},
    {label: "{user|Dear} {user}", tokens: {"user": [{"gender": "other", "name": "Michael"},":name"]}},

    {separator: true, label: "Lists"},

    {label: "{users} likes this post.", tokens: {"users": [[{"gender": "male", "name": "Michael"}, {"gender": "female", "name": "Anna"}], ":name", {'limit': 2, 'joiner': 'or'}]}},
    // {label: "{users||likes,like} this post.", tokens: {"users": [{"gender": "female", "name": "Anna"}]}},
    // {label: "{users|He likes,She likes,They like} this post.", tokens: {"users": [{"gender": "male", "name":"Michael"}, {"gender": "female", "name":"Anna"}]}},
    // {label: "{users|He likes,She likes,They like} this post.", tokens: {"users": [{"gender": "female", "name":"Anna"}]}},
    // {label: "{users|He likes,She likes,They like} this post.", tokens: {"users": [{"gender": "male", "name":"Michael"}]}}
  ])
})();
