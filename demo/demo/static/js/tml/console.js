var examples = {};
var lastSelectedSection = null;

function selectExamplesSection(element) {
  if (lastSelectedSection != null)
    lastSelectedSection.className = "tml_example_section";

  element.className = "tml_example_section_selected";
  lastSelectedSection = element;
  var locale = element.getAttribute("data-locale");
  populateExamples(locale, examples[locale]);
}

function populateExamples(locale, list) {
  var root =  $("#tml_examples");
  root.empty();

  for (var i = 0; i < list.length; i++) {
    if (list[i].separator) {
      var separator = document.createElement("div");
      separator.className = "tml_example_separator";
      if (list[i].separator) {
        separator.innerText = list[i].label;
      }
      root.append(separator);
      continue;
    }

    var example = document.createElement("div");
    example.className = "tml_example";
    example.setAttribute("data-locale", locale);
    example.setAttribute("data-index", i);
    $(example).click(function(e) {
      loadExample(this.getAttribute("data-locale"), this.getAttribute("data-index"));
    });

    var exampleLabel = document.createElement("div");
    exampleLabel.className = "tml_label";
    exampleLabel.innerText = list[i].label;
    $(example).append(exampleLabel);

    if (list[i].description) {
      var exampleDesc = document.createElement("div");
      exampleDesc.className = "tml_description";
      exampleDesc.innerText = list[i].description;
      $(example).append(exampleDesc);
    }

    if (list[i].tokens) {
      var exampleTokens = document.createElement("div");
      exampleTokens.className = "tml_tokens";
      exampleTokens.innerText = JSON.stringify(list[i].tokens);
      $(example).append(exampleTokens);
    }

    if (list[i].options) {
      var exampleOptions = document.createElement("div");
      exampleOptions.className = "tml_options";
      exampleOptions.innerText = JSON.stringify(list[i].options);
      $(example).append(exampleOptions);
    }

    root.append(example);
  }
}

function addExamples(locale, title, list) {
  if (!examples[locale]) {
    examples[locale] = [];
  }
  examples[locale] = examples[locale].concat(list);

  var section = document.createElement("div");
  if (locale == currentLocale) {
    section.className = "tml_example_section_selected";
    lastSelectedSection = section;
    populateExamples(locale, list);
  } else {
    section.className = "tml_example_section";
  }
  section.setAttribute("data-locale", locale);
  section.innerHTML = title + " <span style='font-size:8px'>(" + (list.length) + ")</span>";
  $("#tml_example_sections").append(section);
  $(section).click(function(e) {
    selectExamplesSection(e.target);
    e.stopPropagation();
  });
}

function loadExample(locale, index) {
  var example = examples[locale][index];

  label_editor.setValue(example.label);

  if (example.description)
    context_editor.setValue(example.description);
  else
    context_editor.setValue("");

  if (example.tokens)
    tokens_editor.setValue(JSON.stringify(example.tokens, null, 2));
  else
    tokens_editor.setValue("{}");

  if (example.options)
    options_editor.setValue(JSON.stringify(example.options, null, 2));
  else
    options_editor.setValue("{}");

  $("#tml_locale").val(locale);
  $("#tml_locale").trigger('liszt:updated');

  submitTml();
}

function submitTml() {
  $("#tml_label").val(label_editor.getValue());
  $("#tml_context").val(context_editor.getValue());
  $("#tml_tokens").val(tokens_editor.getValue());
  $("#tml_options").val(options_editor.getValue());
  $("#tml_form").submit();
}

function newSample() {
  location.reload();
}
