// ═══════════════════════════════════════════════════════
//  KONTFEEL STOCK — Google Apps Script Backend
//  1. Crée un Google Sheet vide
//  2. Colle ce code dans Apps Script (Extensions > Apps Script)
//  3. Remplace SHEET_ID par l'ID de ton Sheet (dans l'URL)
//  4. Lance initSheet() une fois pour créer les onglets
//  5. Déploie : Déployer > Nouveau déploiement > Application Web
//     - Exécuter en tant que : Moi
//     - Qui peut accéder : Tout le monde
//  6. Copie l'URL et colle-la dans config.js
// ═══════════════════════════════════════════════════════

const SHEET_ID = '1mJ5MBZ0zl9D137Cc_reiHMkVG6m9mr6uVZyfVdFzZGc';
const ART = 'Articles';
const MOV = 'Mouvements';

// ── Routing ──────────────────────────────────────────────

function doGet(e) {
  const action = (e.parameter && e.parameter.action) || 'list';
  const ref    = (e.parameter && e.parameter.ref)    || '';

  if (action === 'list')         return ok(getArticles());
  if (action === 'get')          return ok(getArticle(ref));
  if (action === 'history')      return ok(getHistory());
  if (action === 'gollect_list') return ok(getGollectItems());
  if (action === 'gollect_get')  return ok(getGollectItem(ref));
  return ok({ error: 'Unknown action' });
}

function doPost(e) {
  let data;
  try { data = JSON.parse(e.postData.contents); }
  catch { return ok({ error: 'Invalid JSON' }); }

  if (data.action === 'movement')          return ok(recordMovement(data));
  if (data.action === 'add_article')       return ok(addArticle(data));
  if (data.action === 'update_article')    return ok(updateArticle(data));
  if (data.action === 'delete_article')    return ok(deleteArticle(data.ref));
  if (data.action === 'add_gollect')       return ok(addGollectItem(data));
  if (data.action === 'gollect_movement')  return ok(gollectMovement(data));
  if (data.action === 'gollect_etat')      return ok(updateGollectEtat(data));
  if (data.action === 'add_gollect_photo')      return ok(addGollectPhoto(data));
  if (data.action === 'save_gollect_photo_url') return ok(saveGollectPhotoUrl(data));
  return ok({ error: 'Unknown action' });
}

function ok(data) {
  return ContentService
    .createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}

// ── Articles ─────────────────────────────────────────────

function getArticles() {
  const cache = CacheService.getScriptCache();
  const cached = cache.get('articles');
  if (cached) return JSON.parse(cached);

  const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(ART);
  const rows  = sheet.getDataRange().getValues();
  if (rows.length <= 1) return [];
  const h = rows[0];
  const articles = rows.slice(1).filter(r => r[0]).map(r => rowToObj(h, r));
  cache.put('articles', JSON.stringify(articles), 1800); // 30 min
  return articles;
}

function getArticle(ref) {
  const articles = getArticles();
  const art = articles.find(a => a.ref === ref);
  return art || { error: 'Article introuvable' };
}

function invalidateCache() {
  CacheService.getScriptCache().remove('articles');
}

function addArticle(d) {
  const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(ART);
  const rows  = sheet.getDataRange().getValues();
  const h = rows[0];

  // Ref déjà existante ?
  if (rows.slice(1).some(r => r[0] === d.ref)) {
    return { error: 'Référence déjà utilisée' };
  }

  sheet.appendRow([
    d.ref, d.nom, d.zone, d.unite || '',
    parseInt(d.stock_actuel)  || 0,
    parseInt(d.stock_mini)    || 0,
    d.conditionnement         || 'aucun',
  ]);
  invalidateCache();
  return { success: true };
}

function updateArticle(d) {
  const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(ART);
  const rows  = sheet.getDataRange().getValues();
  const h     = rows[0];
  const i     = rows.findIndex((r, idx) => idx > 0 && r[0] === d.ref);
  if (i === -1) return { error: 'Article introuvable' };

  const cols = { nom: 1, zone: 2, unite: 3, stock_actuel: 4, stock_mini: 5, conditionnement: 6 };
  Object.entries(cols).forEach(([key, col]) => {
    if (d[key] !== undefined) {
      sheet.getRange(i + 1, col + 1).setValue(
        key.startsWith('stock') ? parseInt(d[key]) || 0 : d[key]
      );
    }
  });
  invalidateCache();
  return { success: true };
}

function deleteArticle(ref) {
  const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(ART);
  const rows  = sheet.getDataRange().getValues();
  const i     = rows.findIndex((r, idx) => idx > 0 && r[0] === ref);
  if (i === -1) return { error: 'Article introuvable' };
  sheet.deleteRow(i + 1);
  invalidateCache();
  return { success: true };
}

// ── Mouvements ───────────────────────────────────────────

function recordMovement(d) {
  const ss      = SpreadsheetApp.openById(SHEET_ID);
  const artSheet = ss.getSheetByName(ART);
  const movSheet = ss.getSheetByName(MOV);

  const rows = artSheet.getDataRange().getValues();
  const h    = rows[0];
  const i    = rows.findIndex((r, idx) => idx > 0 && r[0] === d.ref);
  if (i === -1) return { error: 'Article introuvable' };

  const stockCol   = h.indexOf('stock_actuel');
  const stockBefore = parseInt(rows[i][stockCol]) || 0;
  const qty         = parseInt(d.qty)  || 1;
  const type        = d.type === 'entree' ? 'entree' : 'sortie';
  const stockAfter  = type === 'entree'
    ? stockBefore + qty
    : Math.max(0, stockBefore - qty);

  // Mise à jour stock
  artSheet.getRange(i + 1, stockCol + 1).setValue(stockAfter);

  // Enregistrement du mouvement
  movSheet.appendRow([
    new Date(),
    d.ref,
    rows[i][h.indexOf('nom')],
    rows[i][h.indexOf('zone')],
    type,
    qty,
    stockBefore,
    stockAfter,
    d.employe || 'Anonyme',
  ]);

  invalidateCache();
  return { success: true, stock_actuel: stockAfter };
}

function getHistory() {
  const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(MOV);
  const rows  = sheet.getDataRange().getValues();
  if (rows.length <= 1) return [];
  const h = rows[0];
  return rows.slice(1)
    .filter(r => r[0])
    .reverse()
    .map(r => rowToObj(h, r));
}

// ── Helpers ──────────────────────────────────────────────

function rowToObj(headers, row) {
  const obj = {};
  headers.forEach((h, i) => { obj[h] = row[i]; });
  if (obj.timestamp instanceof Date) obj.timestamp = obj.timestamp.toISOString();
  return obj;
}

// ── Gollect ──────────────────────────────────────────────

const GOL = 'Gollect';

function getGollectItems() {
  const cache = CacheService.getScriptCache();
  const cached = cache.get('gollect');
  if (cached) return JSON.parse(cached);
  const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(GOL);
  if (!sheet) return [];
  const rows = sheet.getDataRange().getValues();
  if (rows.length <= 1) return [];
  const h = rows[0];
  const items = rows.slice(1).filter(r => r[0]).map(r => rowToObj(h, r));
  cache.put('gollect', JSON.stringify(items), 1800);
  return items;
}

function getGollectItem(ref) {
  const items = getGollectItems();
  return items.find(i => i.ref === ref) || { error: 'Article introuvable' };
}

function addGollectItem(d) {
  const ss = SpreadsheetApp.openById(SHEET_ID);
  let sheet = ss.getSheetByName(GOL);
  if (!sheet) {
    sheet = ss.insertSheet(GOL);
    sheet.getRange(1,1,1,7).setValues([['ref','nom','description','etat','stock_actuel','photos','date_ajout']]);
    sheet.getRange(1,1,1,7).setFontWeight('bold').setBackground('#dcfce7');
  }
  const rows = sheet.getDataRange().getValues();
  if (rows.slice(1).some(r => r[0] === d.ref)) return { error: 'Référence déjà utilisée' };
  sheet.appendRow([d.ref, d.nom, d.description||'', d.etat||'bon_etat', parseInt(d.stock_actuel)||0, '', new Date()]);
  CacheService.getScriptCache().remove('gollect');
  return { success: true };
}

function gollectMovement(d) {
  const ss = SpreadsheetApp.openById(SHEET_ID);
  const sheet = ss.getSheetByName(GOL);
  if (!sheet) return { error: 'Onglet Gollect introuvable' };
  const rows = sheet.getDataRange().getValues();
  const h = rows[0];
  const i = rows.findIndex((r, idx) => idx > 0 && r[0] === d.ref);
  if (i === -1) return { error: 'Article introuvable' };
  const stockCol = h.indexOf('stock_actuel');
  const stockBefore = parseInt(rows[i][stockCol]) || 0;
  const qty = parseInt(d.qty) || 1;
  const stockAfter = d.type === 'entree' ? stockBefore + qty : Math.max(0, stockBefore - qty);
  sheet.getRange(i + 1, stockCol + 1).setValue(stockAfter);
  // Log dans Mouvements
  const movSheet = ss.getSheetByName(MOV);
  if (movSheet) movSheet.appendRow([new Date(), d.ref, rows[i][h.indexOf('nom')], 'GOLLECT', d.type, qty, stockBefore, stockAfter, d.employe||'Anonyme']);
  CacheService.getScriptCache().remove('gollect');
  return { success: true, stock_actuel: stockAfter };
}

function updateGollectEtat(d) {
  const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(GOL);
  if (!sheet) return { error: 'Onglet Gollect introuvable' };
  const rows = sheet.getDataRange().getValues();
  const h = rows[0];
  const i = rows.findIndex((r, idx) => idx > 0 && r[0] === d.ref);
  if (i === -1) return { error: 'Article introuvable' };
  if (d.etat) sheet.getRange(i+1, h.indexOf('etat')+1).setValue(d.etat);
  if (d.description !== undefined) sheet.getRange(i+1, h.indexOf('description')+1).setValue(d.description);
  CacheService.getScriptCache().remove('gollect');
  return { success: true };
}

function addGollectPhoto(d) {
  const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(GOL);
  if (!sheet) return { error: 'Onglet Gollect introuvable' };
  const rows = sheet.getDataRange().getValues();
  const h = rows[0];
  const i = rows.findIndex((r, idx) => idx > 0 && r[0] === d.ref);
  if (i === -1) return { error: 'Article introuvable' };

  // Upload vers Drive
  const folder = getOrCreateGollectFolder();
  const blob = Utilities.newBlob(
    Utilities.base64Decode(d.photo.split(',')[1]),
    'image/jpeg',
    `${d.ref}_${Date.now()}.jpg`
  );
  const file = folder.createFile(blob);
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  const url = `https://drive.google.com/uc?id=${file.getId()}`;

  // Ajouter l'URL dans la colonne photos
  const photosCol = h.indexOf('photos');
  const existing = rows[i][photosCol] ? rows[i][photosCol] + ',' : '';
  sheet.getRange(i+1, photosCol+1).setValue(existing + url);
  CacheService.getScriptCache().remove('gollect');
  return { success: true, url };
}

function saveGollectPhotoUrl(d) {
  const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(GOL);
  if (!sheet) return { error: 'Onglet Gollect introuvable' };
  const rows = sheet.getDataRange().getValues();
  const h = rows[0];
  const i = rows.findIndex((r, idx) => idx > 0 && r[0] === d.ref);
  if (i === -1) return { error: 'Article introuvable' };
  const photosCol = h.indexOf('photos');
  const existing = rows[i][photosCol] ? rows[i][photosCol] + ',' : '';
  sheet.getRange(i+1, photosCol+1).setValue(existing + d.url);
  CacheService.getScriptCache().remove('gollect');
  return { success: true, url: d.url };
}

function getOrCreateGollectFolder() {
  const name = 'Kontfeel-Gollect-Photos';
  const folders = DriveApp.getFoldersByName(name);
  return folders.hasNext() ? folders.next() : DriveApp.createFolder(name);
}

// ── Init (lance une seule fois) ──────────────────────────

function initSheet() {
  const ss = SpreadsheetApp.openById(SHEET_ID);

  // Onglet Articles
  let art = ss.getSheetByName(ART);
  if (!art) art = ss.insertSheet(ART);
  art.clearContents();
  art.getRange(1, 1, 1, 7).setValues([['ref','nom','zone','unite','stock_actuel','stock_mini','conditionnement']]);
  art.getRange(1, 1, 1, 7).setFontWeight('bold').setBackground('#eef2ff');

  // Exemples
  const ex = [
    ['PALETTE-01',   'Palette Europe 80×120',    'PALETTE',  'palette', 0, 2, 'palette'],
    ['CHUTE-PVC',    'Chute PVC',                'CHUTE',    'pièce',   0, 0, 'aucun'],
    ['CONSO-SCDA',   'Scotch double face 50mm',  'CONSO',    'rouleau', 0, 3, 'carton'],
    ['RACK-PCM3000', 'PCM 3000m',                'RACK',     'rouleau', 0, 2, 'aucun'],
    ['MATERIAU-01',  'Échantillon matériautheque','MATERIAU', 'feuille', 0, 0, 'aucun'],
  ];
  art.getRange(2, 1, ex.length, 7).setValues(ex);

  // Onglet Mouvements
  let mov = ss.getSheetByName(MOV);
  if (!mov) mov = ss.insertSheet(MOV);
  mov.clearContents();
  mov.getRange(1, 1, 1, 9).setValues([['timestamp','ref','nom','zone','type','quantite','stock_avant','stock_apres','employe']]);
  mov.getRange(1, 1, 1, 9).setFontWeight('bold').setBackground('#eef2ff');

  Logger.log('✅ Sheet initialisé !');
}
