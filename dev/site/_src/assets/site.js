document.addEventListener('DOMContentLoaded', () => {
  const currentNav = document.body.dataset.nav || '';
  document.querySelectorAll('[data-nav-key]').forEach((link) => {
    if (link.dataset.navKey === currentNav) {
      link.classList.add('active');
    }
  });

  const transcript = document.getElementById('demo-terminal-output');
  const transcriptUrl = document.body.dataset.transcriptUrl;
  if (transcript && transcriptUrl) {
    fetch(transcriptUrl, { cache: 'no-store' })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load demo output: ${response.status}`);
        }
        return response.text();
      })
      .then((data) => {
        transcript.textContent = data;
      })
      .catch(() => {
        transcript.textContent = 'Unable to load deterministic runtime output.';
      });
  }

  const watchDemo = document.getElementById('watch-demo');
  if (watchDemo) {
    watchDemo.addEventListener('click', (event) => {
      event.preventDefault();
      const demoSection = document.getElementById('demo');
      if (demoSection) {
        demoSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  }

  document.querySelectorAll('[data-cta]').forEach((button) => {
    button.addEventListener('click', () => {
      console.log('CTA_CLICK');
    });
  });
});
