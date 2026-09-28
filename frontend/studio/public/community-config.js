// Public navigation setting. Never place credentials in community.json.
export async function getCommunityUrl() {
  try {
    const response = await fetch(new URL('./community.json', import.meta.url), {cache: 'no-cache'});
    if (!response.ok) return '';
    const config = await response.json();
    if (typeof config.url !== 'string' || !config.url.trim()) return '';
    const url = new URL(config.url.trim());
    if (url.protocol !== 'https:' || url.username || url.password) return '';
    return url.href;
  } catch {
    return '';
  }
}
