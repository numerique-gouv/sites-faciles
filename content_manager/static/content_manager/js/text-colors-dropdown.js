// Script pour ajouter un menu déroulant de couleurs dans Draftail
(function() {
    'use strict';
    
    const COLORS = [
        { label: 'Bleu', value: '#000091', color: '#000091' },
        { label: 'Blanc', value: '#ffffff', color: '#ffffff' },
        { label: 'Par défaut', value: 'remove', color: 'transparent' }
    ];
    
    const MENU_STYLES = `
        position: absolute;
        top: 100%;
        left: 0;
        background: white;
        border: 1px solid #e3e3e3;
        border-radius: 3px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        padding: 4px 0;
        display: none;
        z-index: 10000;
        min-width: 140px;
        margin-top: 2px;
    `;
    
    const OPTION_STYLES = `
        display: block;
        width: 100%;
        padding: 8px 12px;
        border: none;
        background: white;
        text-align: left;
        cursor: pointer;
        font-size: 14px;
    `;
    
    // Création des éléments DOM
    function createWrapper() {
        const wrapper = document.createElement('div');
        wrapper.className = 'color-dropdown-wrapper';
        Object.assign(wrapper.style, {
            display: 'inline-block',
            position: 'relative',
            verticalAlign: 'middle'
        });
        return wrapper;
    }
    
    function createButton() {
        const button = document.createElement('button');
        button.className = 'Draftail-ToolbarButton';
        button.type = 'button';
        button.setAttribute('aria-label', 'Couleur du texte');
        button.setAttribute('title', 'Couleur du texte');
        Object.assign(button.style, { width: '32px', height: '32px' });
        button.innerHTML = `
            <span class="Draftail-ToolbarButton__label" style="color: ${COLORS[0].value}; font-weight: bold; font-size: 16px;">
                A
            </span>
        `;
        return button;
    }
    
    function createMenu() {
        const menu = document.createElement('div');
        menu.className = 'color-dropdown-menu';
        menu.style.cssText = MENU_STYLES;
        return menu;
    }
    
    function createColorSquare(color) {
        const square = document.createElement('span');
        const baseStyles = `
            display: inline-block;
            width: 14px;
            height: 14px;
            margin-right: 8px;
            vertical-align: middle;
            border-radius: 2px;
        `;
        
        if (color.value === 'remove') {
            square.style.cssText = baseStyles + `
                background: linear-gradient(45deg, transparent 45%, #999 45%, #999 55%, transparent 55%);
                border: 1px solid #999;
            `;
        } else {
            const borderColor = color.value === COLORS[1].value ? '#999' : '#ccc';
            square.style.cssText = baseStyles + `
                background-color: ${color.color};
                border: 1px solid ${borderColor};
            `;
        }
        
        return square;
    }
    
    function createColorOption(color, onSelect) {
        const option = document.createElement('button');
        option.className = 'color-option';
        option.style.cssText = OPTION_STYLES;
        
        option.appendChild(createColorSquare(color));
        option.appendChild(document.createTextNode(color.label));
        
        option.onmouseover = () => option.style.background = '#f0f0f0';
        option.onmouseout = () => option.style.background = 'white';
        option.onmousedown = onSelect;
        
        return option;
    }
    
    // Gestion des événements
    function setupHoverBehavior(wrapper, menu) {
        let hoverTimeout;
        
        const showMenu = () => {
            clearTimeout(hoverTimeout);
            menu.style.display = 'block';
        };
        
        const hideMenuDelayed = (delay = 200) => {
            hoverTimeout = setTimeout(() => {
                menu.style.display = 'none';
            }, delay);
        };
        
        wrapper.onmouseenter = showMenu;
        wrapper.onmouseleave = () => hideMenuDelayed(200);
        menu.onmouseenter = showMenu;
        menu.onmouseleave = () => hideMenuDelayed(100);
        
        return hoverTimeout;
    }
    
    // Recherche et manipulation DraftJS
    function findDraftJSInstance(editorWrapper) {
        const reactKeys = Object.keys(editorWrapper).filter(key => key.startsWith('__react'));
        
        for (const key of reactKeys) {
            let fiber = editorWrapper[key];
            while (fiber) {
                if (fiber.stateNode?.getEditorState && fiber.stateNode?.onChange) {
                    return fiber.stateNode;
                }
                fiber = fiber.return || fiber.child;
                if (!fiber) break;
            }
        }
        return null;
    }
    
    function removeColorStyles(contentState, selection) {
        ['BLUETEXT', 'WHITETEXT'].forEach(style => {
            contentState = window.DraftJS.Modifier.removeInlineStyle(contentState, selection, style);
        });
        return contentState;
    }
    
    function applyColorStyle(editorInstance, color) {
        const { EditorState, RichUtils, Modifier } = window.DraftJS;
        const editorState = editorInstance.getEditorState();
        const selection = editorState.getSelection();
        
        if (selection.isCollapsed()) return false;
        
        let contentState = editorState.getCurrentContent();
        let newEditorState;
        
        if (color === 'remove') {
            contentState = removeColorStyles(contentState, selection);
            newEditorState = EditorState.push(editorState, contentState, 'change-inline-style');
        } else {
             const styleMap = { [COLORS[0].value]: 'BLUETEXT', [COLORS[1].value]: 'WHITETEXT' };
            const targetStyle = styleMap[color];
            const otherStyle = targetStyle === 'BLUETEXT' ? 'WHITETEXT' : 'BLUETEXT';
            
            contentState = Modifier.removeInlineStyle(contentState, selection, otherStyle);
            newEditorState = EditorState.push(editorState, contentState, 'change-inline-style');
            newEditorState = RichUtils.toggleInlineStyle(newEditorState, targetStyle);
        }
        
        if (newEditorState) {
            editorInstance.onChange(newEditorState);
            return true;
        }
        return false;
    }
    
    function applyColor(toolbar, color) {
        const editorWrapper = toolbar.closest('.DraftEditor-root, .Draftail-Editor');
        if (!editorWrapper || !window.DraftJS) return;
        
        const editorInstance = findDraftJSInstance(editorWrapper);
        if (editorInstance) {
            applyColorStyle(editorInstance, color);
        }
    }
    
    // Utilitaires de style
    function forceColorStyles() {
        const applyForcedStyles = (selector, styles) => {
            document.querySelectorAll(selector).forEach(el => {
                if (el.style.display === 'none') {
                    Object.assign(el.style, styles);
                }
            });
        };
        
        applyForcedStyles('.BLUETEXT', {
            display: 'inline',
            color: COLORS[0].value,
            visibility: 'visible'
        });
        
        applyForcedStyles('.WHITETEXT', {
            display: 'inline',
            color: COLORS[1].value,
            backgroundColor: '#1e1e1e',
            padding: '2px 4px',
            borderRadius: '3px',
            visibility: 'visible'
        });
    }
    
    // Construction du dropdown
    function buildDropdown(toolbar) {
        const wrapper = createWrapper();
        const button = createButton();
        const menu = createMenu();
        
        button.onclick = e => e.preventDefault();
        
        COLORS.forEach(color => {
            const onSelect = (e) => {
                e.preventDefault();
                e.stopPropagation();
                applyColor(toolbar, color.value);
                menu.style.display = 'none';
            };
            
            const option = createColorOption(color, onSelect);
            menu.appendChild(option);
        });
        
        wrapper.appendChild(button);
        wrapper.appendChild(menu);
        setupHoverBehavior(wrapper, menu);
        
        return wrapper;
    }
    
    function insertDropdown(toolbar, dropdown) {
        const metaToolbar = toolbar.querySelector('.Draftail-MetaToolbar');
        if (metaToolbar) {
            toolbar.insertBefore(dropdown, metaToolbar);
        } else {
            toolbar.appendChild(dropdown);
        }
    }
    
    // Fonctions principales
    function addDropdownToToolbar(toolbar) {
        if (toolbar.querySelector('.color-dropdown-wrapper')) return false;
        
        const dropdown = buildDropdown(toolbar);
        insertDropdown(toolbar, dropdown);
        return true;
    }
    
    function initDropdowns() {
        document.querySelectorAll('.Draftail-Toolbar')
            .forEach(addDropdownToToolbar);
        forceColorStyles();
    }
    
    function observeNewToolbars() {
        const observer = new MutationObserver(mutations => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType !== 1) return;
                    
                    if (node.classList?.contains('Draftail-Toolbar')) {
                        addDropdownToToolbar(node);
                    } else {
                        node.querySelectorAll?.('.Draftail-Toolbar')
                            .forEach(addDropdownToToolbar);
                    }
                });
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    function observeStyleChanges() {
        const observer = new MutationObserver(forceColorStyles);
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['class', 'style']
        });
    }
    
    // Initialisation
    function init() {
        initDropdowns();
        observeNewToolbars();
        observeStyleChanges();
        
        // Tentatives différées
        [500, 1500, 3000].forEach(delay => {
            setTimeout(initDropdowns, delay);
        });
        
        // Force périodique
        setInterval(forceColorStyles, 2000);
        
        // Export pour debug
        window.initColorDropdowns = initDropdowns;
    }
    
    init();
    
})();