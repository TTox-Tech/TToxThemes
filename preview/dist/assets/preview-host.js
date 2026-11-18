(() => {
  const key = 'ttox-preview-design-v1';
  let saved = null;
  try { saved = JSON.parse(localStorage.getItem(key) || 'null'); } catch {}
  window.openai = {
    widgetState: saved,
    setWidgetState(snapshot) {
      this.widgetState = snapshot;
      try { localStorage.setItem(key, JSON.stringify(snapshot)); } catch {}
      return Promise.resolve();
    }
  };
})();
