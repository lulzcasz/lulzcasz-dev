import { Editor, Node, mergeAttributes } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight'
import { createLowlight } from 'lowlight'

import arduino from 'highlight.js/lib/languages/arduino';
import armasm from 'highlight.js/lib/languages/armasm';
import avrasm from 'highlight.js/lib/languages/avrasm';
import bash from 'highlight.js/lib/languages/bash';
import c from 'highlight.js/lib/languages/c';
import cmake from 'highlight.js/lib/languages/cmake';
import cpp from 'highlight.js/lib/languages/cpp';
import css from 'highlight.js/lib/languages/css';
import django from 'highlight.js/lib/languages/django';
import dockerfile from 'highlight.js/lib/languages/dockerfile';
import javascript from 'highlight.js/lib/languages/javascript';
import json from 'highlight.js/lib/languages/json';
import makefile from 'highlight.js/lib/languages/makefile';
import x86asm from 'highlight.js/lib/languages/x86asm';
import powershell from 'highlight.js/lib/languages/powershell';
import python from 'highlight.js/lib/languages/python';
import sql from 'highlight.js/lib/languages/sql';
import ini from 'highlight.js/lib/languages/ini';
import yaml from 'highlight.js/lib/languages/yaml';
import shell from 'highlight.js/lib/languages/shell';
import plaintext from 'highlight.js/lib/languages/plaintext';

import { Underline } from '@tiptap/extension-underline'
import { TextAlign } from '@tiptap/extension-text-align'
import { Link } from '@tiptap/extension-link'
import { Image } from '@tiptap/extension-image'
import { Table } from '@tiptap/extension-table'
import { TableRow } from '@tiptap/extension-table-row'
import { TableCell } from '@tiptap/extension-table-cell'
import { TableHeader } from '@tiptap/extension-table-header'
import { TextStyle } from '@tiptap/extension-text-style'
import { Color } from '@tiptap/extension-color'
import { Highlight } from '@tiptap/extension-highlight'
import { FileHandler } from '@tiptap/extension-file-handler'

const lowlight = createLowlight();
lowlight.register({
    arduino, armasm, avrasm, bash, c, cmake, cpp, css, django, 
    dockerfile, javascript, json, makefile, powershell, python, 
    sql, yaml, shell, plaintext,
    nasm: x86asm,
    toml: ini 
});

const CustomImage = Image.extend({
    addAttributes() {
        return {
            ...this.parent?.(),
            alt: { default: null },
            alignment: {
                default: 'left',
                parseHTML: element => element.getAttribute('data-alignment') || 'left',
                renderHTML: attributes => {
                    if (!attributes.alignment) return {};
                    if (attributes.alignment === 'center') {
                        return { 'data-alignment': 'center', style: 'display: block; margin-left: auto; margin-right: auto;' };
                    }
                    if (attributes.alignment === 'left') {
                        return { 'data-alignment': 'left', style: 'display: block; margin-left: 0; margin-right: auto;' };
                    }
                    if (attributes.alignment === 'right') {
                        return { 'data-alignment': 'right', style: 'display: block; margin-left: auto; margin-right: 0;' };
                    }
                    return {};
                },
            },
        }
    }
});

const Video = Node.create({
    name: 'video',
    group: 'block',
    selectable: true,
    draggable: true,
    addAttributes() {
        return { src: { default: null } };
    },
    parseHTML() {
        return [{ tag: 'video' }];
    },
    renderHTML({ HTMLAttributes }) {
        return ['video', mergeAttributes(HTMLAttributes, { controls: true, style: 'max-width: 100%; border-radius: 8px;' })];
    },
    addCommands() {
        return {
            setVideo: (options) => ({ commands }) => {
                return commands.insertContent({ type: this.name, attrs: options });
            },
        };
    },
});

function getCookie(name) {
    let cookieArray = document.cookie.split(';');
    for (let i = 0; i < cookieArray.length; i++) {
        let cookie = cookieArray[i].trim();
        if (cookie.startsWith(name + '=')) return decodeURIComponent(cookie.substring(name.length + 1));
    }
    return null;
}

function getArticleUuid() {
    let articleUuid = null;
    const uuidMatch = document.body.textContent.match(/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/i);
    if (uuidMatch) {
        articleUuid = uuidMatch[0];
    } else {
        const uuidInput = document.querySelector('input[name="uuid"]');
        if (uuidInput) articleUuid = uuidInput.value;
    }
    return articleUuid;
}

window.createTiptapEditor = function({ element, content, onUpdate, onSelectionUpdate }) {
    return new Editor({
        element: element,
        editorProps: {
            attributes: {
                class: 'focus:outline-none min-h-full h-full',
                style: 'min-height: 500px;'
            },
        },
        extensions: [
            StarterKit.configure({ codeBlock: false }),
            CodeBlockLowlight.configure({ lowlight }),
            Underline,
            CustomImage.configure({ inline: false }),
            Video,
            Link.configure({ openOnClick: false }),
            TextAlign.configure({ types: ['heading', 'paragraph'] }),
            Table.configure({ resizable: true }),
            TableRow,
            TableHeader,
            TableCell,
            TextStyle,
            Color,
            Highlight.configure({ multicolor: true }),
            FileHandler.configure({
                allowedMimeTypes: ['image/png', 'image/jpeg', 'image/gif', 'image/webp'],
                onDrop: async (currentEditor, files, pos) => {
                    files.forEach(async (file) => {
                        try {
                            const url = await window.uploadTiptapImage(file);
                            currentEditor.chain().setNodeSelection(pos).setImage({ src: url }).run();
                        } catch (err) {}
                    });
                },
                onPaste: async (currentEditor, files) => {
                    files.forEach(async (file) => {
                        try {
                            const url = await window.uploadTiptapImage(file);
                            currentEditor.chain().setImage({ src: url }).run();
                        } catch (err) {}
                    });
                },
            })
        ],
        content: content,
        onUpdate: ({ editor }) => { if (onUpdate) onUpdate(editor.getHTML()); },
        onSelectionUpdate: ({ editor }) => { if (onSelectionUpdate) onSelectionUpdate(); }
    });
};

window.uploadTiptapImage = function(file) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/tinymce/upload-image/');
        xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
        xhr.onload = () => {
            if (xhr.status < 200 || xhr.status >= 300) return reject();
            const json = JSON.parse(xhr.responseText);
            if (!json || typeof json.location != 'string') return reject();
            resolve(json.location);
        };
        xhr.onerror = () => reject();
        const formData = new FormData();
        formData.append('file', file);
        const uuid = getArticleUuid();
        if (uuid) formData.append('article_uuid', uuid);
        xhr.send(formData);
    });
};

window.uploadTiptapVideo = function(file) {
    const formData = new FormData();
    formData.append('file', file);
    const uuid = getArticleUuid();
    if (uuid) formData.append('article_uuid', uuid);
    return fetch('/tinymce/upload-video/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        body: formData
    }).then(res => {
        if (!res.ok) throw new Error();
        return res.json();
    }).then(json => {
        if (!json || typeof json.location != 'string') throw new Error();
        return json.location;
    });
};

window.dispatchEvent(new CustomEvent('tiptap:ready'));
