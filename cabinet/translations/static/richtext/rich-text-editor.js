var richtext = {

	formatDoc: function(oDoc, sCmd, sValue) {
		if (!richtext.validateMode(oDoc)) { return; }
		document.execCommand(sCmd, false, sValue);
		oDoc.focus();
	},

	validateMode: function(oDoc) {
		if (!document.getElementById("rte-mode-" + richtext.rId.exec(oDoc.id)[0]).checked) { return true; }
		alert("Выключите режим \u00AB" + this.sModeLabel + "\u00BB.");
		oDoc.focus();
		return false;
	},

	extractText: function(oDoc) {
		if (oDoc.innerText) { return oDoc.innerText; }
		var oContent = document.createRange();
		oContent.selectNodeContents(oDoc.firstChild);
		return oContent.toString();
	},

	setDocMode: function(oDoc, bToSource) {
		if (bToSource) {
			var oContent = document.createTextNode(oDoc.innerHTML), oPre = document.createElement("pre");
			oDoc.innerHTML = "";
			oDoc.contentEditable = false;
			oPre.className = "rte-sourcetext";
			oPre.id = "rte-source-" + oDoc.id;
			oPre.onblur = oDoc.onblur;
			oPre.contentEditable = true;
			oPre.appendChild(oContent);
			oDoc.appendChild(oPre);
		} else {
			oDoc.innerHTML = richtext.extractText(oDoc);
			oDoc.contentEditable = true;
		}
		oDoc.focus();
	},
	
	buttonClick: function() {
		var sBtnGroup = richtext.rId.exec(this.id)[0], sCmd = this.id.slice(0, - sBtnGroup.length);
		richtext.customCommands.hasOwnProperty(sCmd) ? richtext.customCommands[sCmd](richtext.aEditors[sBtnGroup]) : richtext.formatDoc(richtext.aEditors[sBtnGroup], sCmd, this.alt || false);
	},

	changeMode: function() {
		richtext.setDocMode(richtext.aEditors[richtext.rId.exec(this.id)[0]], this.checked);
	},

	updateField: function() {
		var sFieldNum = richtext.rId.exec(this.id)[0];
		document.getElementById("rte-field-" + sFieldNum).value = document.getElementById("rte-mode-" + sFieldNum).checked ? richtext.extractText(this) : this.innerHTML;
	},

	createEditor: function(oTxtArea) {
		var		nEditorId = this.aEditors.length, oParent = document.createElement("div"),
				oToolsBar = document.createElement("div"), oEditBox = document.createElement("div"),
				oModeBox = document.createElement("div"), oModeChB = document.createElement("input"),
				oModeLbl = document.createElement("label");

		oParent.className = "rich-text-editor";
		oParent.id = oTxtArea.id || "rich-text-" + nEditorId;
		oToolsBar.className = "rte-tools";
		oEditBox.className = "rte-editbox";
		oEditBox.id = "rte-editbox-" + nEditorId;
		oEditBox.contentEditable = true;
		oEditBox.innerHTML = oTxtArea.value;
		if (oEditBox.innerHTML === "") {
			oEditBox.innerHTML = "<p><br></p>"
		}
		oEditBox.onkeydown = 
			function(event) {
				if (event.keyCode === 13) {
					// on enter wrap new paragraph in "p"
					document.execCommand('formatBlock', false, 'p');
				}
				if ((event.keyCode === 8 || event.keyCode === 46) && (oEditBox.innerHTML === "" || oEditBox.innerHTML === "<br>")) {
					// add empty "p" on backspace or delete when the field is empty
					oEditBox.innerHTML = "<p><br></p>";
				}
				if((event.keyCode === 8 || event.keyCode === 46) && oEditBox.innerHTML=="<p><br></p>"){  // 8 is backspace
					// interrupt on backspace or delete when the field is "just right" empty
					event.preventDefault();
				}
				if (window.getSelection && (event.keyCode === 8 || event.keyCode === 46)){ // 8 is backspace, 46 is delete
					// unification of newlines and carriage returns for Chrome/FF
					let selection = window.getSelection().toString().replace(/\r+|\n+$/gm, ""); 
					let editorText = oEditBox.innerText.replace(/\n+/g, "\n").replace(/\n+$/g, "");

					// when you try to ctrl+a and delete everything, add empty paragraph and put the cursor inside
					if (editorText == selection) {
						event.preventDefault();
						oEditBox.innerHTML="<p><br></p>";
						var range = document.createRange();
						var sel = window.getSelection();
						range.setStart(oEditBox.childNodes[0], 0);
						range.collapse(true);
						sel.removeAllRanges();
						sel.addRange(range);
					}
					
				}
			};
		oEditBox.onkeyup = 
			function(event) {
				richtext.removeTag(oEditBox, 'span');
			}

		this.aEditors.push(oEditBox);

		if (oTxtArea.form) {
			var oHiddField = document.createElement("input");
			oHiddField.type = "hidden";
			oHiddField.name = oTxtArea.name;
			oHiddField.value = oEditBox.innerHTML;
			oHiddField.id = "rte-field-" + nEditorId;
			oTxtArea.form.appendChild(oHiddField);
			oEditBox.onblur = this.updateField;
		}

		for (var oBtnDef, oButton, nBtn = 0; nBtn < this.oTools.buttons.length; nBtn++) {
			oBtnDef = this.oTools.buttons[nBtn];
			oButton = document.createElement("img");
			oButton.className = "rte-button";
			oButton.id = oBtnDef.command + nEditorId;
			oButton.src = oBtnDef.image;
			if (oBtnDef.hasOwnProperty("value")) { oButton.alt = oBtnDef.value; }
			oButton.title = oBtnDef.text;
			oButton.onclick = this.buttonClick;
			oToolsBar.appendChild(oButton);
		}

		oModeBox.className = "rte-switchmode";
		oModeChB.type = "checkbox";
		oModeChB.id = "rte-mode-" + nEditorId;
		oModeChB.onchange = this.changeMode;
		oModeLbl.setAttribute("for", oModeChB.id);
		oModeLbl.innerHTML = this.sModeLabel;
		oModeBox.appendChild(oModeChB);
		oModeBox.appendChild(document.createTextNode(" "));
		oModeBox.appendChild(oModeLbl);
		oParent.appendChild(oToolsBar);
		oParent.appendChild(oModeBox);
		oParent.appendChild(oEditBox);
		oTxtArea.parentNode.replaceChild(oParent, oTxtArea);
	},

	replaceFields: function(nFlag) {
		this.nReady |= nFlag;
		if (this.nReady !== 3) { return; }
		for (
			var oField, nItem = 0, aTextareas = Array.prototype.slice.call(document.getElementsByTagName("textarea"), 0);
			nItem < aTextareas.length;
			oField = aTextareas[nItem++], oField.className !== "rich-text-editor" || richtext.createEditor(oField)
		);
		var event = new CustomEvent("rteReadyEvent", { "detail": "Event that fires when richtext module has finished executing" });
		document.dispatchEvent(event);
	},

	toolsReady: function() {
		richtext.oTools = JSON.parse(this.responseText);
		richtext.replaceFields(2);
	},

	documentReady: function() { 
		richtext.replaceFields(1); 
	},

	oTools: undefined,
	nReady: 0,
	sModeLabel: "Показать HTML-разметку",
	aEditors: [],
	rId: /\d+$/,
	oToolsReq: new XMLHttpRequest(),
	customCommands: {
		"cleanDoc": function (oDoc, confirmed=false) {
			if (confirmed === false) { // if we ask for confirmation explicitly
				confirmed = confirm("Подтвердите удаление записи!");
			}
			if (richtext.validateMode(oDoc) && confirmed) { oDoc.innerHTML = "<p><br></p>"; };
		},
		"createLink": function (oDoc) {
			var sLnk = prompt("Введите ссылку на источник:", "");
			if (sLnk) {
				if (sLnk.indexOf("//") == -1) {
					sLnk = "//" + sLnk;
				}
				richtext.formatDoc(oDoc, "createlink", sLnk); 
			}
		},
		// todo remove insertHTML crap and replace with range.insertNode (create_tr.html)
		"blockquote": function (oDoc) {
			var sLnk = prompt("Введите адрес ссылки:", "");
			if (sLnk) { 
				richtext.formatDoc(oDoc, "insertHTML", '<blockquote cite="' + sLnk + '">' + richtext.getSelectionHtml() + '</blockquote>');
			} else {
				richtext.formatDoc(oDoc, "insertHTML", '<blockquote>' + richtext.getSelectionHtml() + '</blockquote>');
			}
		},
		"preformat": function (oDoc) {
			richtext.formatDoc(oDoc, "insertHTML", '<pre>' + richtext.getSelectionHtml() + '</pre>');
		},

	},

	richTextStart: function() {
		this.oToolsReq.onload = this.toolsReady;
		this.oToolsReq.open("GET", "/translations/static/richtext/rich-text-tools.json", true);
		this.oToolsReq.send(null);
		window.addEventListener ? addEventListener("load", this.documentReady, false) : window.attachEvent ? attachEvent("onload", this.documentReady) : window.onload = this.documentReady;
	},

	getSelectionHtml: function() {
	    var html = "";
	    if (typeof window.getSelection != "undefined") {
	        var sel = window.getSelection();
	        if (sel.rangeCount) {
	            var container = document.createElement("div");
	            for (var i = 0, len = sel.rangeCount; i < len; ++i) {
	                container.appendChild(sel.getRangeAt(i).cloneContents());
	            }
	            html = container.innerHTML;
	        }
	    } else if (typeof document.selection != "undefined") {
	        if (document.selection.type == "Text") {
	            html = document.selection.createRange().htmlText;
	        }
	    }
	    return html;
	},

	removeTag: function(root,tagname) {
	    var elms = root.getElementsByTagName(tagname), l = elms.length, i;
	    for( i=l-1; i>=0; i--) {
	        // work backwards to avoid possible complications with nested spans
	        while(elms[i].firstChild)
	            elms[i].parentNode.insertBefore(elms[i].firstChild,elms[i]);
	        elms[i].parentNode.removeChild(elms[i]);
	    }
	}
}