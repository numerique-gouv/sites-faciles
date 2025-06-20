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
  // Fermer automatiquement la sidebar (userbar) si elle est ouverte
  if (sidePanelWrapper && sidePanelWrapper.classList.contains('form-side--open')) {
    try {
      localStorage.setItem('wagtail:side-panel-open', '');
    } catch (e) {}
    // Retarde légèrement pour laisser le JS Wagtail finir d’initialiser
    setTimeout(() => {
      sidePanelWrapper.classList.remove('form-side--open');
      sidePanelWrapper.removeAttribute('aria-labelledby');
      document.querySelectorAll('[data-side-panel]').forEach(panel => {
        panel.hidden = true;
      });
    }, 100);
  }
});