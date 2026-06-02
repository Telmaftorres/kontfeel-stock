const API = {

  _headers() {
    return {
      'Content-Type': 'application/json',
      'X-API-Key': CONFIG.API_KEY,
    };
  },

  async _get(path, params = {}) {
    const url = new URL(CONFIG.API_URL + path);
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    const res = await fetch(url.toString(), { headers: this._headers() });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Erreur ${res.status}`);
    }
    return res.json();
  },

  async _post(path, data) {
    const res = await fetch(CONFIG.API_URL + path, {
      method: 'POST',
      headers: this._headers(),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Erreur ${res.status}`);
    }
    return res.json();
  },

  async _patch(path, data) {
    const res = await fetch(CONFIG.API_URL + path, {
      method: 'PATCH',
      headers: this._headers(),
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Erreur ${res.status}`);
    }
    return res.json();
  },

  async _delete(path) {
    const res = await fetch(CONFIG.API_URL + path, {
      method: 'DELETE',
      headers: this._headers(),
    });
    if (!res.ok && res.status !== 204) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Erreur ${res.status}`);
    }
  },

  // ── Articles ─────────────────────────────────────────────

  async listArticles() {
    return this._get('/articles');
  },

  async getArticle(ref) {
    return this._get(`/articles/${encodeURIComponent(ref)}`);
  },

  async addArticle(d) {
    try {
      await this._post('/articles', d);
      return { success: true };
    } catch (e) {
      if (e.message === 'Référence déjà utilisée') return { error: 'Référence déjà utilisée' };
      return { error: e.message };
    }
  },

  async updateArticle(d) {
    const { ref, ...rest } = d;
    return this._patch(`/articles/${encodeURIComponent(ref)}`, rest);
  },

  async deleteArticle(ref) {
    await this._delete(`/articles/${encodeURIComponent(ref)}`);
    return { success: true };
  },

  async savePhotoUrl(ref, url) {
    await this._patch(`/articles/${encodeURIComponent(ref)}`, { photos: url });
    return { success: true, url };
  },

  // ── Mouvements ───────────────────────────────────────────

  async movement(ref, type, qty, employe) {
    const res = await this._post('/movements', {
      article_ref: ref,
      type,
      quantite: qty,
      employe,
      source: 'stock-app',
    });
    return { success: true, stock_actuel: Number(res.stock_apres) };
  },

  async getHistory() {
    return this._get('/movements');
  },

  // ── Stats ─────────────────────────────────────────────────

  async getStats() {
    return this._get('/stats');
  },

  // ── Gollect ──────────────────────────────────────────────

  async listGollect() {
    return this._get('/gollect');
  },

  async getGollectItem(ref) {
    return this._get(`/gollect/${encodeURIComponent(ref)}`);
  },

  async addGollectItem(d) {
    try {
      await this._post('/gollect', d);
      return { success: true };
    } catch (e) {
      if (e.message === 'Référence déjà utilisée') return { error: 'Référence déjà utilisée' };
      return { error: e.message };
    }
  },

  async gollectMovement(ref, type, qty, employe) {
    const res = await this._post(`/gollect/${encodeURIComponent(ref)}/movement`, {
      type, quantite: qty, employe,
    });
    return { success: true, stock_actuel: Number(res.stock_actuel) };
  },

  async updateGollectEtat(ref, etat, description) {
    await this._patch(`/gollect/${encodeURIComponent(ref)}`, { etat, description });
    return { success: true };
  },

  async saveGollectPhotoUrl(ref, url) {
    await this._post(`/gollect/${encodeURIComponent(ref)}/photo`, { url });
    return { success: true, url };
  },

  // ── Upload photo (ImgBB — inchangé) ──────────────────────

  downloadXlsx(path) {
    const url = `${CONFIG.API_URL}${path}?api_key=${CONFIG.API_KEY}`;
    if (window.navigator.standalone) {
      // iOS PWA : afficher un panneau pour éviter de quitter l'appli
      const existing = document.getElementById('_dl-overlay');
      if (existing) existing.remove();
      const el = document.createElement('div');
      el.id = '_dl-overlay';
      el.style.cssText = 'position:fixed;bottom:0;left:0;right:0;background:#fff;border-radius:16px 16px 0 0;padding:24px;box-shadow:0 -4px 24px rgba(0,0,0,.15);z-index:9999;text-align:center';
      el.innerHTML = `<p style="font-weight:700;font-size:16px;margin:0 0 8px">Télécharger le fichier</p>
        <p style="font-size:13px;color:#64748b;margin:0 0 20px">Appuie sur le lien ci-dessous puis choisis "Ouvrir avec Sheets"</p>
        <a href="${url}" style="display:block;background:#4f46e5;color:#fff;padding:14px;border-radius:10px;font-weight:600;text-decoration:none;margin-bottom:12px">📥 Télécharger kontfeel-stock.xlsx</a>
        <button onclick="document.getElementById('_dl-overlay').remove()" style="background:none;border:none;color:#64748b;font-size:14px;padding:8px;cursor:pointer">Annuler</button>`;
      document.body.appendChild(el);
    } else {
      window.open(url, '_blank');
    }
  },

  async uploadPhoto(base64) {
    const b64 = base64.includes(',') ? base64.split(',')[1] : base64;
    const form = new FormData();
    form.append('image', b64);
    const res = await fetch(`https://api.imgbb.com/1/upload?key=${CONFIG.IMGBB_KEY}`, {
      method: 'POST',
      body: form,
    });
    const json = await res.json();
    if (json.success) return json.data.display_url || json.data.url;
    throw new Error('Échec upload ImgBB');
  },
};
