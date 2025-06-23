window.addEventListener('DOMContentLoaded', (event) => {
  const previewPanel = document.querySelector('[data-side-panel="preview"]');

  if (previewPanel) {
    try {
      // Si aucune largeur n’a été enregistrée, on en définit une à 60% de la fenêtre
      if (!localStorage.getItem('wagtail:side-panel-width')) {
        const width = Math.round(window.innerWidth * 0.6); // 60% de la fenêtre
        localStorage.setItem('wagtail:side-panel-width', width.toString());
      }
    } catch (e) {
      // Silencieux en cas d'erreur (quota, etc.)
    }

    // Déclenche l'ouverture du panneau via l’événement personnalisé "open"
    previewPanel.dispatchEvent(new CustomEvent('open'));
  }
 
});

window.addEventListener('DOMContentLoaded', () => {
  const isEditPage = window.location.pathname.includes('/edit/'); // ajuste au besoin

  if (!isEditPage) return;

  const previewPanel = document.querySelector('[data-side-panel="preview"]');

  if (!previewPanel) return;

  // Petite attente pour laisser React finir de monter
  setTimeout(() => {
    const sidebarAlreadyCollapsed = document.body.classList.contains('sidebar-collapsed');
    const toggleButton = document.querySelector('button.sidebar__collapse-toggle');

    if (!sidebarAlreadyCollapsed && toggleButton) {
      toggleButton.click();
      console.log('Sidebar repliée automatiquement sur page d’édition avec preview');
    }
  }, 300);
});