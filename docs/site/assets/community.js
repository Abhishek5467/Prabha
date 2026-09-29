// Resolve from this script so both /docs/ and /Prabha/docs/ hosting work.
(() => {
  const link = document.getElementById('community-join-link');
  const status = document.getElementById('community-status');
  if (!link || !status) return;
  const loader = new URL('../../community-config.js', document.currentScript.src);
  import(loader.href).then(module => module.getCommunityUrl()).then(url => {
    if (!url) return;
    link.href = url;
    link.hidden = false;
    status.textContent = 'Join the Prabha community to ask questions, share experiments and discuss the project.';
  }).catch(() => {});
})();
