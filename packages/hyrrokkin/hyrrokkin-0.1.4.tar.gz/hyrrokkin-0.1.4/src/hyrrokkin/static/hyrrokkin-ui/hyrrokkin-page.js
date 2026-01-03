/*   Hyrrokkin - A visual modelling tool for constructing and executing directed graphs.

     Copyright (C) 2022-2025 Visual Topology Ltd

     Licensed under the MIT License
*/

/* src/js/page/page.js */

var hyrrokkin = hyrrokkin || {};

hyrrokkin.Page = class {

    constructor() {
        this.message_handler = null;
        this.pending_messages = [];
        this.parent_window = window.opener || window.parent;
        this.parent_window.addEventListener("unload", (event) => {
            window.close();
        });
        this.connected = false;
        this.connection_handler = null;
        this.language = undefined;
        this.bundle = null;
    }

    set_connection_handler(handler) {
        this.connection_handler = handler;
        if (this.connected) {
            this.fire_connected();
        }
    }

    fire_connected() {
        if (this.connection_handler) {
            try {
                this.connection_handler();
            } catch (ex) {
            }
            this.connection_handler = null;
        }
    }

    set_message_handler(handler) {
        this.message_handler = handler;
        for(let idx=0; idx<this.pending_messages.length; idx++) {
            let msg = this.pending_messages[idx];
            this.message_handler(...msg);
        }
        this.pending_messages = [];
    }

    handle_message(msg) {
        let header = msg[0];
        let type = header["type"];
        switch (type) {
            case "page_init":
                this.language = header["language"];
                this.bundle = new hyrrokkin.L10NBundle(header["bundle"]);
                this.connected = true;
                this.fire_connected();
                break;
            case "page_message":
                let message_parts = msg[1];
                if (this.message_handler) {
                    this.message_handler(...message_parts);
                } else {
                    this.pending_messages.push(message_parts);
                }
                break;
            default:
                 console.warn("Unexpected msg received by page");
        }
    }

    localise_string(input) {
        if (this.connected) {
            return this.bundle.localise(input);
        } else {
            throw new Error("Cannot localise until page is connected. Set a connection handler to be notified")
        }
    }

    localise_body() {
        if (this.connected) {
            if (this.language === "") {
                /* no localisation available, nothing to do */
                return;
            }
            let localise = (node) => {
                if (node.nodeType === node.TEXT_NODE) {
                    let text = node.nodeValue;
                    if (text.includes("{{") && text.includes("}}")) {
                        node.nodeValue = this.bundle.localise(text);
                    }
                } else {
                    node.childNodes.forEach(node => localise(node));
                }
            }
            localise(document.body);
        } else {
            throw new Error("Cannot localise until page is connected. Set a connection handler to be notified")
        }
    }

    get_language() {
        return this.language;
    }

    send_to_network(msg) {
        this.parent_window.postMessage(msg,window.location.origin);
    }

    send_message(...message_parts) {
        this.send_to_network([{"type":"page_message"},message_parts]);
    }
}

hyrrokkin.page = new hyrrokkin.Page();

window.addEventListener("message", (event) => hyrrokkin.page.handle_message(event.data));

/* src/js/utils/l10n_bundle.js */

var hyrrokkin = hyrrokkin || {};

hyrrokkin.L10NBundle = class {

    debug = false;

    constructor(bundle_content) {
        this.bundle_content = bundle_content;
    }

    localise(input) {
        if (!input) {
            return "";
        }
        if (input in this.bundle_content) {
            let s = this.bundle_content[input];
            if (hyrrokkin.L10NBundle.debug) {
                return "*"+s+"*";
            } else {
                return s;
            }
        }
        // for empty bundles, localise returns the input
        if (Object.keys(this.bundle_content).length == 0) {
            return input;
        }
        // treat the input as possibly containing embedded keys, delimited by {{ and }},
        // for example "say {{hello}}" embeds they key hello
        // substitute any embedded keys and the surrounding delimiters with their values, if the key is present in the bundle
        let idx = 0;
        let s = "";
        while(idx<input.length) {
            if (input.slice(idx, idx+2) === "{{") {
                let startidx = idx+2;
                idx += 2;
                while(idx<input.length) {
                    if (input.slice(idx,idx+2) === "}}") {
                        let token = input.slice(startidx,idx);
                        if (token in this.bundle_content) {
                            token = this.bundle_content[token];
                            if (hyrrokkin.L10NBundle.debug) {
                                token = "*" + token + "*";
                            }
                        }
                        s += token;
                        idx += 2;
                        break;
                    } else {
                        idx += 1;
                    }
                }
            } else {
                s += input.charAt(idx);
                idx++;
            }
        }
        return s;
    }

    get_content() {
        return this.bundle_content;
    }
}



