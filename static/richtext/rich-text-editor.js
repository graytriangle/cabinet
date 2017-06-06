(function () {

	function formatDoc (oDoc, sCmd, sValue) {
		if (!validateMode(oDoc)) { return; }
		document.execCommand(sCmd, false, sValue);
		oDoc.focus();
	}

	function validateMode (oDoc) {
		if (!document.getElementById("rte-mode-" + rId.exec(oDoc.id)[0]).checked) { return true; }
		alert("Uncheck \u00AB" + sModeLabel + "\u00BB.");
		oDoc.focus();
		return false;
	}

	function extractText (oDoc) {
		if (oDoc.innerText) { return oDoc.innerText; }
		var oContent = document.createRange();
		oContent.selectNodeContents(oDoc.firstChild);
		return oContent.toString();
	}

	function setDocMode (oDoc, bToSource) {
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
			oDoc.innerHTML = extractText(oDoc);
			oDoc.contentEditable = true;
		}
		oDoc.focus();
	}
	
	function buttonClick () {
		var sBtnGroup = rId.exec(this.id)[0], sCmd = this.id.slice(0, - sBtnGroup.length);
		customCommands.hasOwnProperty(sCmd) ? customCommands[sCmd](aEditors[sBtnGroup]) : formatDoc(aEditors[sBtnGroup], sCmd, this.alt || false);
	}

	function changeMode () {
		setDocMode(aEditors[rId.exec(this.id)[0]], this.checked);
	}

	function updateField () {
		console.log("update 1");
		var sFieldNum = rId.exec(this.id)[0];
		document.getElementById("rte-field-" + sFieldNum).value = document.getElementById("rte-mode-" + sFieldNum).checked ? extractText(this) : this.innerHTML;
	}

	function createEditor (oTxtArea) {
		console.log("create 0");
		var		nEditorId = aEditors.length, oParent = document.createElement("div"),
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
				if (event.keyCode === 13) 
					// on enter wrap new paragraph in "p"
					document.execCommand('formatBlock', false, 'p');
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
		aEditors.push(oEditBox);

		if (oTxtArea.form) {
			console.log("update 0");
			var oHiddField = document.createElement("input");
			oHiddField.type = "hidden";
			oHiddField.name = oTxtArea.name;
			oHiddField.value = oEditBox.innerHTML;
			oHiddField.id = "rte-field-" + nEditorId;
			oTxtArea.form.appendChild(oHiddField);
			oEditBox.onblur = updateField;
		}

		for (var oBtnDef, oButton, nBtn = 0; nBtn < oTools.buttons.length; nBtn++) {
			oBtnDef = oTools.buttons[nBtn];
			oButton = document.createElement("img");
			oButton.className = "rte-button";
			oButton.id = oBtnDef.command + nEditorId;
			oButton.src = oBtnDef.image;
			if (oBtnDef.hasOwnProperty("value")) { oButton.alt = oBtnDef.value; }
			oButton.title = oBtnDef.text;
			oButton.onclick = buttonClick;
			oToolsBar.appendChild(oButton);
		}

		oModeBox.className = "rte-switchmode";
		oModeChB.type = "checkbox";
		oModeChB.id = "rte-mode-" + nEditorId;
		oModeChB.onchange = changeMode;
		oModeLbl.setAttribute("for", oModeChB.id);
		oModeLbl.innerHTML = sModeLabel;
		oModeBox.appendChild(oModeChB);
		oModeBox.appendChild(document.createTextNode(" "));
		oModeBox.appendChild(oModeLbl);
		oParent.appendChild(oToolsBar);
		oParent.appendChild(oEditBox);
		oParent.appendChild(oModeBox);
		oTxtArea.parentNode.replaceChild(oParent, oTxtArea);
	}

	function replaceFields (nFlag) {
		nReady |= nFlag;
		if (nReady !== 3) { return; }
		for (
			var oField, nItem = 0, aTextareas = Array.prototype.slice.call(document.getElementsByTagName("textarea"), 0);
			nItem < aTextareas.length;
			oField = aTextareas[nItem++], oField.className !== "rich-text-editor" || createEditor(oField)
		);
	}

	function toolsReady () {
		oTools = JSON.parse(this.responseText);
		replaceFields(2);
	}

	function documentReady () { replaceFields(1); }

	var		oTools, nReady = 0, sModeLabel = "Show HTML", aEditors = [], rId = /\d+$/, oToolsReq = new XMLHttpRequest(),
			customCommands = {
				"cleanDoc": function (oDoc) {
					if (validateMode(oDoc) && confirm("Are you sure?")) { oDoc.innerHTML = ""; };
				},
				"createLink": function (oDoc) {
					var sLnk = prompt("Write the URL here", "http:\/\/");
					if (sLnk && sLnk !== "http://"){ formatDoc(oDoc, "createlink", sLnk); }
				}
			};

	oToolsReq.onload = toolsReady;
	oToolsReq.open("GET", "static/richtext/rich-text-tools.json", true);
	oToolsReq.send(null);
	window.addEventListener ? addEventListener("load", documentReady, false) : window.attachEvent ? attachEvent("onload", documentReady) : window.onload = documentReady;
})();