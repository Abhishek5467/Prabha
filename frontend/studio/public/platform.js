// Shared by Studio, bundled docs and the designer. Native privileges stay in Rust.
export const isDesktop = () => Boolean(globalThis.__TAURI__?.core?.invoke);
const MAX_EXPORT_BYTES = 16 * 1024 * 1024;
export async function saveBlob(name, blob) {
  if (isDesktop()) {
    if (blob.size > MAX_EXPORT_BYTES) throw new Error('Desktop exports are limited to 16 MB. Download this file from the project website.');
    return globalThis.__TAURI__.core.invoke('save_export', {
      name, bytes: Array.from(new Uint8Array(await blob.arrayBuffer()))
    });
  }
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = name;
  link.dataset.prabhaDownload = 'true';
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(link.href), 10_000);
  return true;
}
export const saveText = (name, text, type = 'application/json') =>
  saveBlob(name, new Blob([text], {type}));
export function installNavigation(onError = error => alert(error.message || String(error))) {
  if (!isDesktop()) return () => {};
  const click = event => {
    const link = event.target.closest?.('a[href]');
    if (!link || event.defaultPrevented || link.dataset.prabhaDownload) return;
    const url = new URL(link.href, document.baseURI);
    const local = url.origin === location.origin;
    if (!local && url.protocol === 'https:') {
      event.preventDefault();
      globalThis.__TAURI__.core.invoke('open_external', {url: url.href}).catch(onError);
    } else if (link.hasAttribute('download') && (local || url.protocol === 'blob:')) {
      event.preventDefault();
      (async () => {
        const response = await fetch(url);
        if (!response.ok) throw new Error('Download failed: HTTP ' + response.status);
        const name = link.getAttribute('download') || decodeURIComponent(url.pathname.split('/').pop());
        await saveBlob(name, await response.blob());
      })().catch(onError);
    } else if (local && link.target === '_blank') {
      link.removeAttribute('target');
    }
  };
  document.addEventListener('click', click);
  return () => document.removeEventListener('click', click);
}
