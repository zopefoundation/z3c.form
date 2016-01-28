function moveItems(from, to)
  {
  // shortcuts for selection fields
  var src = document.getElementById(from);
  var tgt = document.getElementById(to);

  if (src.selectedIndex == -1) selectionError();
  else
    {
    // iterate over all selected items
    // --> attribute "selectedIndex" doesn't support multiple selection.
    // Anyway, it works here, as a moved item isn't selected anymore,
    // thus "selectedIndex" indicating the "next" selected item :)
    while (src.selectedIndex > -1)
      if (src.options[src.selectedIndex].selected)
        {
        // create a new virtal object with values of item to copy
        temp = new Option(src.options[src.selectedIndex].text,
                      src.options[src.selectedIndex].value);
        // append virtual object to targe
        tgt.options[tgt.length] = temp;
        // want to select newly created item
        temp.selected = true;
        // delete moved item in source
        src.options[src.selectedIndex] = null;
      }
    }
  }

// move item from "from" selection to "to" selection
function from2to(name)
  {
  moveItems(name+"-from", name+"-to");
  copyDataForSubmit(name);
  }

// move item from "to" selection back to "from" selection
function to2from(name)
  {
  moveItems(name+"-to", name+"-from");
  copyDataForSubmit(name);
  }

function swapFields(a, b)
  {
  // swap text
  var temp = a.text;
  a.text = b.text;
  b.text = temp;
  // swap value
  temp = a.value;
  a.value = b.value;
  b.value = temp;
  // swap selection
  temp = a.selected;
  a.selected = b.selected;
  b.selected = temp;
  }

// move selected item in "to" selection one up
function moveUp(name)
  {
  // shortcuts for selection field
  var toSel = document.getElementById(name+"-to");

  if (toSel.selectedIndex == -1)
      selectionError();
  else for (var i = 1; i < toSel.length; i++)
    if (toSel.options[i].selected)
      {
      swapFields(toSel.options[i-1], toSel.options[i]);
      copyDataForSubmit(name);
      }
  }

// move selected item in "to" selection one down
function moveDown(name)
  {
    // shortcuts for selection field
    var toSel = document.getElementById(name+"-to");

    if (toSel.selectedIndex == -1) {
        selectionError();
    } else {
      for (var i = toSel.length-2; i >= 0; i--) {
        if (toSel.options[i].selected) {
          swapFields(toSel.options[i+1], toSel.options[i]);
        }
      }
      copyDataForSubmit(name);
    }
  }

// copy each item of "toSel" into one hidden input field
function copyDataForSubmit(name)
  {
  // shortcuts for selection field and hidden data field
  var toSel = document.getElementById(name+"-to");
  var toDataContainer = document.getElementById(name+"-toDataContainer");

  // delete all child nodes (--> complete content) of "toDataContainer" span
  while (toDataContainer.hasChildNodes())
      toDataContainer.removeChild(toDataContainer.firstChild);

  // create new hidden input fields - one for each selection item of
  // "to" selection
  for (var i = 0; i < toSel.options.length; i++)
    {
    // create virtual node with suitable attributes
    var newNode = document.createElement("input");
    newNode.setAttribute("name", name.replace(/-/g, '.')+':list');
    newNode.setAttribute("type", "hidden");
    newNode.setAttribute("value",toSel.options[i].value );

    // actually append virtual node to DOM tree
    toDataContainer.appendChild(newNode);
    }
  }

// error message for missing selection
function selectionError()
  {alert("Must select something!")}
