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
};
