(function() {
  addExamples("ru", "Russian", [
    {separator: true, label: "Основы"},

    {label: "Привет Мир"},
    {label: "Орган", description: "Человеческий орган - Орган"},
    {label: "Орган", description: "Музыкальный инструмент - оргАн"},

    {separator: true, label: "Зависимые от Цифрового Значения"},

    {label: "Количество сообщений: {count}", tokens: {count: 5}},
    {label: "У вас есть {count||one:сообщение,few:сообщения,many:сообщений}", tokens: {count: 5}},
    {label: "У вас есть {count||сообщение,сообщения,сообщений}", tokens: {count: 1}},
    // {label: "У вас есть {count|новое сообщение,#count# сообщения,#count# сообщений}", tokens: {count: 1}},
    {label: "У вас есть {count|сообщение,сообщения,сообщений}",tokens: {count: 4}},

    {separator: true, label: "Зависимые от Пола"},

    {label: "{user||male:родился,female:родилась,other:родился/лась} в 1979 году. ", tokens: {"user":[{"name":"Анна", "gender":"female"},":name"]}},
    {label: "{user||родился,родилась} в 1979 году. ", tokens: {user: [{gender: "female", name: "Анна"}, ":name"]}},
    {label: "{user||загрузил,загрузила} фотографию в свой фотоальбом.", tokens: {user: [{gender: "male", name: "Михаил"}, ":name"]}},

    {separator: true, label: "Декораторы"},

    {label: "Привет [bold: Мир]"},
    {label: "Привет [bold: {user}]", tokens: {user: "Михаил"}},
    {label: "Привет [bold: {user}], у вас есть {count||сообщение,сообщения,сообщений}.", tokens: {user: "Анна", count: 5}},
    {label: "Привет [bold: {user}], [italic: у вас есть [bold: {count||сообщение,сообщения,сообщений}]].", tokens: {user: "Михаил", count: 1}},
    {label: "Привет [bold: {user}], [italic]у вас есть [bold: {count||сообщение,сообщения,сообщений}][/italic].", tokens: {user: "Михаил", count: 1}},

    {separator: true, label: "Подразумеваемые"},

    {label: "{user|Он,Она} любит читать газеты.", tokens: {user: [{gender: "male"}, ":name"]}},
    {label: "{user|Ему,Ей} нравится это сообщение.", tokens: {user: [{gender: "female"},":name"]}},
    {label: "{user|Дорогой,Дорогая} {user}", tokens: {user: [{gender: "male", name: "Михаил"}, ":name"]}},

    // {separator: true, label: "Списки"},

    // {label: "{users|Ему,Ей,Им} нравится это сообщение.", tokens: {users: [{gender: "male", name: "Михаил"}, {gender: "female", name: "Анна"}]}},
    // {label: "{users||любит,любят} этот блог.", tokens: {users: [[{gender: "female", name: "Анна"}], {attribute: "name"}, {joiner: "и"}]}},
    // {label: "{users||любит,любят} этот блог.", tokens: {users: [[{gender: "male", name:"Михаил"}], {attribute: "name"}, {joiner: "и"}]}},
    // {label: "{users||любит,любят} этот блог.", tokens: {users: [[{gender: "male", name:"Михаил"}, {gender: "female", name:"Анна"}], {attribute: "name"}, {joiner: "и"}]}},

    // {label: "{users||заходил, заходила, заходили} на этот блог.", tokens: {users: [[{gender: "male", name:"Михаил"}, {gender: "female", name:"Анна"}], {attribute: "name"}, {joiner: "и"}]}},
    // {label: "{users||заходил, заходила, заходили} на этот блог.", tokens: {users: [[{gender: "female", name:"Анна"}], {attribute: "name"}, {joiner: "и"}]}},

    {separator: true, label: "Падежи и Склонения"},

    {label: "{actor||послал,послала} сообщение {target::dat}", tokens: {
      actor: [{gender: "male", name: "Михаил"}, ":name"],
      target: [{gender: "female", name: "Анна"}, ":name"]
    }},

    // {label: "Это сообщение было адресованно {users::dat}.", tokens: {users: [[{gender: "female", name:"Анна"}], {attribute: "name"}, {joiner: "и"}]}},
    // {label: "Это сообщение было адресованно {users::dat}.", tokens: {users: [[{gender: "male", name:"Михаил"}, {gender: "female", name:"Анна"}], {attribute: "name", value: "<strong>{$0}</strong>"}, {joiner: "и"}]}},

    {label: "[bold: {actor}] {actor|загрузил,загрузила} [bold: {count||фотографию,фотографии,фотографий}] в фотоальбом [bold: {target::gen}].", tokens: {
      actor: [{gender: "male", name: "Михаил"}, ":name"],
      target: [{gender: "female", name: "Анна"}, ":name"],
      count: 3
    }}
  ])
})();
