const API = {
  async get(action, params = {}) {
    const url = new URL(CONFIG.API_URL);
    url.searchParams.set('action', action);
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    const res = await fetch(url.toString(), { redirect: 'follow' });
    return res.json();
  },

  async post(data) {
    const res = await fetch(CONFIG.API_URL, {
      method: 'POST',
      redirect: 'follow',
      body: JSON.stringify(data),
    });
    return res.json();
  },

  async listArticles() {
    return this.get('list');
  },

  async getArticle(ref) {
    return this.get('get', { ref });
  },

  async movement(ref, type, qty, employe) {
    return this.post({ action: 'movement', ref, type, qty, employe });
  },

  async addArticle(article) {
    return this.post({ action: 'add_article', ...article });
  },

  async updateArticle(article) {
    return this.post({ action: 'update_article', ...article });
  },

  async deleteArticle(ref) {
    return this.post({ action: 'delete_article', ref });
  },

  async getHistory() {
    return this.get('history');
  },

  // ── Gollect ──
  async listGollect() { return this.get('gollect_list'); },
  async getGollectItem(ref) { return this.get('gollect_get', { ref }); },
  async addGollectItem(d) { return this.post({ action: 'add_gollect', ...d }); },
  async gollectMovement(ref, type, qty, employe) { return this.post({ action: 'gollect_movement', ref, type, qty, employe }); },
  async updateGollectEtat(ref, etat, description) { return this.post({ action: 'gollect_etat', ref, etat, description }); },
  async addGollectPhoto(ref, photo) { return this.post({ action: 'add_gollect_photo', ref, photo }); },
  async saveGollectPhotoUrl(ref, url) { return this.post({ action: 'save_gollect_photo_url', ref, url }); },
  async savePhotoUrl(ref, url) { return this.post({ action: 'save_photo_url', ref, url }); },

  async uploadPhoto(base64) {
    const b64 = base64.includes(',') ? base64.split(',')[1] : base64;
    const form = new FormData();
    form.append('image', b64);
    const res = await fetch(`https://api.imgbb.com/1/upload?key=${CONFIG.IMGBB_KEY}`, { method: 'POST', body: form });
    const json = await res.json();
    if (json.success) return json.data.display_url || json.data.url;
    throw new Error('Échec upload ImgBB');
  },
};
