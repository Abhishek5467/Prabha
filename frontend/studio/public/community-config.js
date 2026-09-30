// Public navigation settings; never put credentials in community.json.
function httpsUrl(value) {
  try {
    const url = new URL(typeof value === 'string' ? value.trim() : '');
    return url.protocol === 'https:' && !url.username && !url.password ? url.href : '';
  } catch { return ''; }
}
export async function getCommunityLinks() {
  try {
    const response = await fetch(new URL('./community.json', import.meta.url), {cache: 'no-cache'});
    if (!response.ok) return {forum: '', chat: ''};
    const config = await response.json();
    return {forum: httpsUrl(config.url), chat: httpsUrl(config.chat_url)};
  } catch { return {forum: '', chat: ''}; }
}
export async function getCommunityUrl() {
  return (await getCommunityLinks()).forum;
}
