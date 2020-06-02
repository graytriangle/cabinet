function highlight(event, color) {
    console.log(event.target.tagName);
    if (event.target.tagName == "P") {
        event.target.style.background=color;
        i = index(event.target);
        replacement = (document.getElementById("original").contains(event.target)) ? "translation" : "original";
        tmplist = document.getElementById(replacement).getElementsByTagName("p");
        if (tmplist.length > i+1)
        {
        	document.getElementById(replacement).getElementsByTagName("p")[i].style.background=color;
        }
    }
}

function index(el) {
    if (!el) return -1;
    var i = 0;
    while (el = el.previousElementSibling) {
        i++;
    };
    return i;
} 


// Functions for saving/restoring the selection in contenteditable
// Apparently it's ridiculously complicated task
// Courtesy of https://stackoverflow.com/a/38752483

/*
 Gets the offset of a node within another node. Text nodes are
 counted a n where n is the length. Entering (or passing) an
 element is one offset. Exiting is 0.
 */
function getNodeOffset(start, dest) {
  var offset = 0;

  var node = start;
  var stack = [];

  while (true) {
    if (node === dest) {
      return offset;
    }

    // Go into children
    if (node.firstChild) {
      // Going into first one doesn't count
      if (node !== start)
        offset += 1;
      stack.push(node);
      node = node.firstChild;
    }
    // If can go to next sibling
    else if (stack.length > 0 && node.nextSibling) {
      // If text, count length (plus 1)
      if (node.nodeType === 3)
        offset += node.nodeValue.length + 1;
      else
        offset += 1;

      node = node.nextSibling;
    }
    else {
      // If text, count length
      if (node.nodeType === 3)
        offset += node.nodeValue.length + 1;
      else
        offset += 1;

      // No children or siblings, move up stack
      while (true) {
        if (stack.length <= 1)
          return offset;

        var next = stack.pop();

        // Go to sibling
        if (next.nextSibling) {
          node = next.nextSibling;
          break;
        }
      }
    }
  }
};

// Calculate the total offsets of a node
function calculateNodeOffset(node) {
  var offset = 0;

  // If text, count length
  if (node.nodeType === 3)
    offset += node.nodeValue.length + 1;
  else
    offset += 1;

  if (node.childNodes) {
    for (var i=0;i<node.childNodes.length;i++) {
      offset += calculateNodeOffset(node.childNodes[i]);
    }
  }

  return offset;
};

// Determine total offset length from returned offset from ranges
function totalOffsets(parentNode, offset) {
  if (parentNode.nodeType == 3)
    return offset;

  if (parentNode.nodeType == 1) {
    var total = 0;
    // Get child nodes
    for (var i=0;i<offset;i++) {
      total += calculateNodeOffset(parentNode.childNodes[i]);
    }
    return total;
  }

  return 0;
};

function getNodeAndOffsetAt(start, offset) {
  var node = start;
  var stack = [];

  while (true) {
    // If arrived
    if (offset <= 0)
      return { node: node, offset: 0 };

    // If will be within current text node
    if (node.nodeType == 3 && (offset <= node.nodeValue.length))
      return { node: node, offset: Math.min(offset, node.nodeValue.length) };

    // Go into children (first one doesn't count)
    if (node.firstChild) {
      if (node !== start)
        offset -= 1;
      stack.push(node);
      node = node.firstChild;
    }
    // If can go to next sibling
    else if (stack.length > 0 && node.nextSibling) {
      // If text, count length
      if (node.nodeType === 3)
        offset -= node.nodeValue.length + 1;
      else
        offset -= 1;

      node = node.nextSibling;
    }
    else {
      // No children or siblings, move up stack
      while (true) {
        if (stack.length <= 1) {
          // No more options, use current node
          if (node.nodeType == 3)
            return { node: node, offset: Math.min(offset, node.nodeValue.length) };
          else
            return { node: node, offset: 0 };
        }

        var next = stack.pop();

        // Go to sibling
        if (next.nextSibling) {
          // If text, count length
          if (node.nodeType === 3)
            offset -= node.nodeValue.length + 1;
          else
            offset -= 1;

          node = next.nextSibling;
          break;
        }
      }
    }
  }
};

function selection_save(containerEl) {
  // Get range
  var selection = window.getSelection();
  if (selection.rangeCount > 0) {
    var range = selection.getRangeAt(0);
    return {
      start: getNodeOffset(containerEl, range.startContainer) + totalOffsets(range.startContainer, range.startOffset),
      end: getNodeOffset(containerEl, range.endContainer) + totalOffsets(range.endContainer, range.endOffset)
    };
  }
  else
    return null;
};

function selection_restore(containerEl, savedSel) {
  if (!savedSel)
    return;

  var range = document.createRange();

  var startNodeOffset, endNodeOffset;
  startNodeOffset = getNodeAndOffsetAt(containerEl, savedSel.start);
  endNodeOffset = getNodeAndOffsetAt(containerEl, savedSel.end);

  range.setStart(startNodeOffset.node, startNodeOffset.offset);
  range.setEnd(endNodeOffset.node, endNodeOffset.offset);

  var sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
};

function htmlToElement(html) {
    var template = document.createElement('template');
    html = html.trim(); // Never return a text node of whitespace as the result
    template.innerHTML = html;
    return template.content.firstChild;
}