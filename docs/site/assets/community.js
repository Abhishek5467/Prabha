// Resolve from this script so /docs/, /Prabha/docs/ and bundled desktop paths work.
(() => {
  const appRoot = new URL('../../', document.currentScript.src);
  import(new URL('platform.js', appRoot).href).then(module => module.installNavigation()).catch(() => {});
  const content = document.querySelector('.wy-nav-content');
  if (content) {
    const back = document.createElement('a');
    back.href = appRoot.href;
    back.textContent = '← Back to Prabha Studio';
    back.style.cssText = 'display:inline-block;margin-bottom:20px;font-size:14px';
    content.prepend(back);
  }
  import(new URL('community-config.js', appRoot).href).then(module => module.getCommunityLinks()).then(links => {
    for (const [id, href] of [['community-join-link', links.forum], ['community-chat-link', links.chat]]) {
      const link = document.getElementById(id);
      if (link && href) link.href = href;
    }
  }).catch(() => {});
})();
