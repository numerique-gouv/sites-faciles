(function() {
    'use strict';
    
    function resetAlignmentsInEditor(editorContainer) {
        if (editorContainer) {
            editorContainer.querySelectorAll('*').forEach(function(el) {
                if (el.style.textAlign === 'center') {
                    el.style.textAlign = '';
                }
            });
        }
    }
    
    function updateBlockAlignmentInEditor(editorRoot) {
        resetAlignmentsInEditor(editorRoot);
        
        const contentBlocks = editorRoot.querySelectorAll(
            '[data-contents="true"] [data-block="true"], .public-DraftStyleDefault-block'
        );
        
        contentBlocks.forEach(function(block) {
            let isTextCenter = false;
            let checkElement = block;
            
            while (checkElement && !isTextCenter) {
                if (checkElement.getAttribute('data-block-type') === 'text-center' ||
                    (checkElement.classList && checkElement.classList.contains('Draftail-block--text-center'))) {
                    isTextCenter = true;
                }
                checkElement = checkElement.parentElement;
                if (checkElement === editorRoot) {
                    break;
                }
            }
            
            if (isTextCenter) {
                block.style.textAlign = 'center';
                block.querySelectorAll('*').forEach(function(child) {
                    child.style.textAlign = 'center';
                });
            }
        });
        
        editorRoot.querySelectorAll('[data-block-type="text-center"], .Draftail-block--text-center').forEach(function(block) {
            block.style.textAlign = 'center';
            block.querySelectorAll('*').forEach(function(child) {
                child.style.textAlign = 'center';
            });
        });
    }
    
    function updateAllEditors() {
        document.querySelectorAll('.DraftEditor-root, .Draftail-Editor').forEach(function(editor) {
            updateBlockAlignmentInEditor(editor);
        });
    }
    
    let updateTimeout;
    const observer = new MutationObserver(function(mutations) {
        clearTimeout(updateTimeout);
        updateTimeout = setTimeout(function() {
            updateAllEditors();
        }, 50);
    });
    
    function startObserving() {
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['data-block-type', 'class']
        });
        updateAllEditors();
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startObserving);
    } else {
        startObserving();
    }
    
    // Check for dynamically added editors after initial load
    setTimeout(startObserving, 500);
})();