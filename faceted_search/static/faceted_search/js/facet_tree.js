(function () {
    function checkboxOf(li) {
        return li.querySelector(":scope > .fr-checkbox-group > input[type=checkbox]");
    }

    function descendantCheckboxes(li) {
        const nested = li.querySelector(":scope > ul");
        if (!nested) {
            return [];
        }
        return Array.from(nested.querySelectorAll("input[type=checkbox]"));
    }

    function setChecked(checkbox, checked) {
        checkbox.checked = checked;
        checkbox.indeterminate = false;
    }

    function syncFromDescendants(parentCheckbox, descendants) {
        const checkedCount = descendants.filter(function (checkbox) {
            return checkbox.checked;
        }).length;
        if (checkedCount === 0) {
            setChecked(parentCheckbox, false);
        } else if (checkedCount === descendants.length) {
            setChecked(parentCheckbox, true);
        } else {
            parentCheckbox.checked = false;
            parentCheckbox.indeterminate = true;
        }
    }

    function syncAncestors(li) {
        let current = li;
        while (current) {
            const parentElement = current.parentElement;
            const parentLi = parentElement ? parentElement.closest("li") : null;
            if (!parentLi) {
                break;
            }
            const parentBox = checkboxOf(parentLi);
            const descendants = descendantCheckboxes(parentLi);
            if (parentBox && descendants.length) {
                syncFromDescendants(parentBox, descendants);
            }
            current = parentLi;
        }
    }

    function restoreTree(rootUl) {
        rootUl.querySelectorAll("li").forEach(function (li) {
            const checkbox = checkboxOf(li);
            const descendants = descendantCheckboxes(li);
            if (checkbox && checkbox.checked && descendants.length) {
                descendants.forEach(function (child) {
                    setChecked(child, true);
                });
            }
        });
        Array.from(rootUl.querySelectorAll("li")).reverse().forEach(function (li) {
            const checkbox = checkboxOf(li);
            const descendants = descendantCheckboxes(li);
            if (checkbox && descendants.length && !checkbox.checked) {
                syncFromDescendants(checkbox, descendants);
            }
        });
    }

    function initTree(rootUl) {
        restoreTree(rootUl);
        rootUl.addEventListener("change", function (event) {
            const checkbox = event.target;
            if (!(checkbox instanceof HTMLInputElement) || checkbox.type !== "checkbox") {
                return;
            }
            const li = checkbox.closest("li");
            if (!li) {
                return;
            }
            const descendants = descendantCheckboxes(li);
            if (descendants.length) {
                descendants.forEach(function (child) {
                    setChecked(child, checkbox.checked);
                });
            }
            syncAncestors(li);
            if (checkbox.form) {
                checkbox.form.submit();
            }
        });
    }

    function start() {
        document.querySelectorAll("ul.fr-facet-tree").forEach(function (ul) {
            if (ul.parentElement && ul.parentElement.closest("ul.fr-facet-tree")) {
                return;
            }
            initTree(ul);
        });
    }

    // Added for the backport of DSFR 1.15+ to work
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", start);
    } else {
        start();
    }
})();
