"use strict";
(self["webpackChunkjl_db_comp"] = self["webpackChunkjl_db_comp"] || []).push([["lib_index_js"],{

/***/ "./lib/api.js"
/*!********************!*\
  !*** ./lib/api.js ***!
  \********************/
(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   fetchPostgresCompletions: () => (/* binding */ fetchPostgresCompletions)
/* harmony export */ });
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _request__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./request */ "./lib/request.js");


/**
 * Fetch PostgreSQL table and column completions from the server.
 *
 * @param dbUrl - PostgreSQL connection string (optional if using env var)
 * @param prefix - Optional prefix to filter completions
 * @param schema - Database schema name (default: 'public')
 * @param tableName - Optional table name to filter columns (only returns columns from this table)
 * @param schemaOrTable - Ambiguous identifier that could be either a schema or table name (backend will determine)
 * @param jsonbColumn - Optional JSONB column name to extract keys from
 * @param jsonbPath - Optional JSONB path for nested key extraction
 * @returns Array of completion items
 */
async function fetchPostgresCompletions(dbUrl, prefix = '', schema = 'public', tableName, schemaOrTable, jsonbColumn, jsonbPath) {
    try {
        const params = new URLSearchParams();
        if (dbUrl) {
            params.append('db_url', encodeURIComponent(dbUrl));
        }
        if (prefix) {
            params.append('prefix', prefix);
        }
        params.append('schema', schema);
        if (tableName) {
            params.append('table', tableName);
        }
        if (schemaOrTable) {
            params.append('schema_or_table', schemaOrTable);
        }
        if (jsonbColumn) {
            params.append('jsonb_column', jsonbColumn);
            if (jsonbPath && jsonbPath.length > 0) {
                params.append('jsonb_path', JSON.stringify(jsonbPath));
            }
        }
        const endpoint = `completions?${params.toString()}`;
        const response = await (0,_request__WEBPACK_IMPORTED_MODULE_1__.requestAPI)(endpoint, {
            method: 'GET'
        });
        if (response.status === 'error') {
            console.error('PostgreSQL completion error:', response.message);
            return [];
        }
        // If JSONB keys requested, return only those
        if (jsonbColumn && response.jsonbKeys) {
            return response.jsonbKeys;
        }
        // Return appropriate results based on context
        if (tableName || schemaOrTable) {
            // If we have table context, prefer columns
            return response.columns.length > 0 ? response.columns : response.tables;
        }
        return [...response.tables, ...response.columns];
    }
    catch (err) {
        if (err instanceof _jupyterlab_services__WEBPACK_IMPORTED_MODULE_0__.ServerConnection.ResponseError) {
            const status = err.response.status;
            let detail = err.message;
            if (typeof detail === 'string' &&
                (detail.includes('<!DOCTYPE') || detail.includes('<html'))) {
                detail = `HTML error page (${detail.substring(0, 100)}...)`;
            }
            console.error(`PostgreSQL completions API failed (${status}): ${detail}`);
        }
        else {
            const msg = err instanceof Error ? err.message : 'Unknown error';
            console.error(`PostgreSQL completions API failed: ${msg}`);
        }
        return [];
    }
}


/***/ },

/***/ "./lib/index.js"
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_completer__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/completer */ "webpack/sharing/consume/default/@jupyterlab/completer");
/* harmony import */ var _jupyterlab_completer__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_completer__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _provider__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./provider */ "./lib/provider.js");



/**
 * Plugin ID constant.
 */
const PLUGIN_ID = 'jl_db_comp:plugin';
/**
 * Initialization data for the jl_db_comp extension.
 *
 * This plugin provides PostgreSQL table and column name completions
 * in JupyterLab notebooks and editors when typing SQL queries.
 */
const plugin = {
    id: PLUGIN_ID,
    description: 'A JupyterLab extension to complete db queries in jupyterlab notebooks',
    autoStart: true,
    requires: [_jupyterlab_completer__WEBPACK_IMPORTED_MODULE_0__.ICompletionProviderManager],
    optional: [_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_1__.ISettingRegistry],
    activate: (app, completionManager, settingRegistry) => {
        let provider;
        if (settingRegistry) {
            settingRegistry
                .load(PLUGIN_ID)
                .then(settings => {
                provider = new _provider__WEBPACK_IMPORTED_MODULE_2__.PostgresCompletionProvider(settings);
                completionManager.registerProvider(provider);
                console.log('JupyterLab extension jl_db_comp is activated!');
            })
                .catch(reason => {
                console.error('Failed to load settings for jl_db_comp:', reason);
                provider = new _provider__WEBPACK_IMPORTED_MODULE_2__.PostgresCompletionProvider();
                completionManager.registerProvider(provider);
                console.log('JupyterLab extension jl_db_comp is activated!');
            });
        }
        else {
            provider = new _provider__WEBPACK_IMPORTED_MODULE_2__.PostgresCompletionProvider();
            completionManager.registerProvider(provider);
            console.log('JupyterLab extension jl_db_comp is activated!');
        }
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ },

/***/ "./lib/provider.js"
/*!*************************!*\
  !*** ./lib/provider.js ***!
  \*************************/
(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   PostgresCompletionProvider: () => (/* binding */ PostgresCompletionProvider)
/* harmony export */ });
/* harmony import */ var _api__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./api */ "./lib/api.js");

/**
 * PostgreSQL completion provider for JupyterLab.
 *
 * Provides table and column name completions from PostgreSQL databases
 * when editing SQL-like code in notebooks and editors.
 */
class PostgresCompletionProvider {
    /**
     * Create a new PostgresCompletionProvider.
     *
     * @param settings - Optional settings registry to load database configuration
     */
    constructor(settings) {
        this.identifier = 'jl_db_comp:postgres-completer';
        this.renderer = null;
        this._cache = new Map();
        this._cacheTTL = 5 * 60 * 1000; // 5 minutes in milliseconds
        this._settings = null;
        this._dbUrl = '';
        this._schema = 'public';
        this._enabled = true;
        /**
         * SQL keywords that trigger completion.
         */
        this._sqlKeywords = [
            'select',
            'from',
            'join',
            'where',
            'insert',
            'update',
            'delete',
            'inner',
            'left',
            'right',
            'outer',
            'on',
            'group',
            'order',
            'by',
            'having',
            'into',
            'values',
            'set'
        ];
        if (settings) {
            this._settings = settings;
            this._loadSettings();
            settings.changed.connect(() => {
                this._loadSettings();
            });
        }
    }
    /**
     * Load database configuration from settings.
     */
    _loadSettings() {
        if (!this._settings) {
            return;
        }
        this._dbUrl = this._settings.get('databaseUrl').composite;
        this._schema = this._settings.get('schema').composite;
        this._enabled = this._settings.get('enabled').composite;
    }
    /**
     * Determine if completions should be shown in the current context.
     *
     * Checks for SQL keywords or context that suggests SQL code.
     */
    async isApplicable(context) {
        if (!this._enabled) {
            return false;
        }
        // Get editor content from context
        const editor = context.editor;
        if (!editor) {
            return false;
        }
        const text = editor.model.sharedModel.getSource();
        if (!text) {
            return false;
        }
        const textLower = text.toLowerCase();
        // Check if any SQL keyword is present
        return this._sqlKeywords.some(keyword => textLower.includes(keyword));
    }
    /**
     * Fetch completion items for the current context.
     *
     * Uses caching to minimize database calls.
     */
    async fetch(request, context) {
        var _a;
        if (!this._enabled) {
            return { start: request.offset, end: request.offset, items: [] };
        }
        const { text, offset } = request;
        // Extract context: schema, table, and prefix
        const extracted = this._extractContext(text, offset);
        // Create cache key that includes full context
        let cacheKey;
        if (extracted.jsonbColumn) {
            // JSONB key completion: table.column->path
            const pathStr = ((_a = extracted.jsonbPath) === null || _a === void 0 ? void 0 : _a.join('.')) || '';
            const tablePrefix = extracted.schemaOrTable
                ? `${extracted.schemaOrTable}.`
                : '';
            cacheKey =
                `${tablePrefix}${extracted.jsonbColumn}->${pathStr}.${extracted.prefix}`.toLowerCase();
        }
        else if (extracted.schema && extracted.tableName) {
            // schema.table.prefix
            cacheKey =
                `${extracted.schema}.${extracted.tableName}.${extracted.prefix}`.toLowerCase();
        }
        else if (extracted.schemaOrTable) {
            // schema.prefix OR table.prefix (ambiguous)
            cacheKey = `${extracted.schemaOrTable}.${extracted.prefix}`.toLowerCase();
        }
        else {
            // just prefix
            cacheKey = extracted.prefix.toLowerCase();
        }
        // Check cache first
        const cached = this._getCached(cacheKey);
        if (cached) {
            return this._formatReply(cached, request.offset, extracted.prefix);
        }
        // Fetch from database
        try {
            const items = await (0,_api__WEBPACK_IMPORTED_MODULE_0__.fetchPostgresCompletions)(this._dbUrl || undefined, extracted.prefix, extracted.schema || this._schema, extracted.tableName, extracted.schemaOrTable, extracted.jsonbColumn, extracted.jsonbPath);
            // Cache the results
            this._cache.set(cacheKey, {
                items,
                timestamp: Date.now()
            });
            return this._formatReply(items, request.offset, extracted.prefix);
        }
        catch (error) {
            console.error('Failed to fetch PostgreSQL completions:', error);
            return { start: request.offset, end: request.offset, items: [] };
        }
    }
    /**
     * Extract context from the text: prefix being typed, optional table name, optional schema, and JSONB context.
     *
     * Detects patterns like:
     * - "schema.table.col" → { schema: "schema", tableName: "table", prefix: "col" }
     * - "schema.table." → { schema: "schema", tableName: "table", prefix: "" }
     * - "schema.tab" → { schemaOrTable: "schema", prefix: "tab" }
     * - "schema." → { schemaOrTable: "schema", prefix: "" }
     * - "table.col" → { schemaOrTable: "table", prefix: "col" }
     * - "table." → { schemaOrTable: "table", prefix: "" }
     * - "prefix" → { prefix: "prefix" }
     * - "column_name->" → { jsonbColumn: "column_name", jsonbPath: [], prefix: "" }
     * - "column_name->>'key1'->" → { jsonbColumn: "column_name", jsonbPath: ["key1"], prefix: "" }
     * - "table.column_name->>'key'->" → { schemaOrTable: "table", jsonbColumn: "column_name", jsonbPath: ["key"], prefix: "" }
     *
     * Note: For single-dot patterns (schema. or table.), the backend will determine
     * whether it's a schema (list tables) or table (list columns) by checking the database.
     */
    _extractContext(text, offset) {
        const beforeCursor = text.substring(0, offset);
        // JSONB pattern: Detect -> or ->> operators
        // Examples: metadata-> or content -> or patients.metadata->>'key'->
        if (beforeCursor.includes('->')) {
            // Much simpler approach: find the last -> or ->> and work backwards
            // Look for: word characters, optional dot+word, then ->, then anything
            // Pattern: (word.)?word -> rest
            const simpleMatch = beforeCursor.match(/([\w]+\.)?([\w]+)\s*->\s*(.*)$/);
            if (simpleMatch) {
                const tableOrSchema = simpleMatch[1]
                    ? simpleMatch[1].slice(0, -1)
                    : undefined; // Remove trailing dot
                const columnName = simpleMatch[2];
                const afterOperator = simpleMatch[3];
                // Parse the path after the first ->
                // Example: "'key1'->>'key2'->" or "key1" or ""
                const jsonbPath = [];
                const pathRegex = /['"]?([\w]+)['"]?\s*->/g;
                let pathMatch;
                while ((pathMatch = pathRegex.exec(afterOperator)) !== null) {
                    jsonbPath.push(pathMatch[1]);
                }
                // Get the current prefix (what's being typed after the last ->)
                // Remove any keys that are part of the path
                const lastArrowIndex = afterOperator.lastIndexOf('->');
                let currentPrefix = '';
                if (lastArrowIndex >= 0) {
                    currentPrefix = afterOperator
                        .substring(lastArrowIndex + 2)
                        .trim()
                        .replace(/['"]/g, '');
                }
                else {
                    // No nested path, just get whatever is after the ->
                    currentPrefix = afterOperator.trim().replace(/['"]/g, '');
                }
                return {
                    schemaOrTable: tableOrSchema,
                    jsonbColumn: columnName,
                    jsonbPath,
                    prefix: currentPrefix
                };
            }
        }
        // Three-part pattern: schema.table.column
        const threePartMatch = beforeCursor.match(/([\w]+)\.([\w]+)\.([\w]*)$/);
        if (threePartMatch) {
            return {
                schema: threePartMatch[1],
                tableName: threePartMatch[2],
                prefix: threePartMatch[3]
            };
        }
        // Two-part pattern: could be schema.table OR table.column
        // Backend will determine which by checking if first part is a schema
        const twoPartMatch = beforeCursor.match(/([\w]+)\.([\w]*)$/);
        if (twoPartMatch) {
            return {
                schemaOrTable: twoPartMatch[1],
                prefix: twoPartMatch[2]
            };
        }
        // Single word: could be a table name OR a column name
        // Check if there's a FROM clause in the query to determine context
        const wordMatch = beforeCursor.match(/[\w]+$/);
        const prefix = wordMatch ? wordMatch[0] : '';
        // Look for FROM clause in the entire text (before or after cursor)
        // Match patterns like: FROM table, FROM schema.table, FROM table AS alias
        const fullText = text.toLowerCase();
        const fromMatch = fullText.match(/\bfrom\s+([\w]+\.)?[\w]+/);
        if (fromMatch) {
            // Extract the table name (with optional schema)
            const fromClause = fromMatch[0];
            const tableMatch = fromClause.match(/\bfrom\s+(?:([\w]+)\.)?([\w]+)/);
            if (tableMatch) {
                const schema = tableMatch[1];
                const table = tableMatch[2];
                // If we have a schema, return schema.table pattern
                if (schema) {
                    return {
                        schema,
                        tableName: table,
                        prefix
                    };
                }
                // Otherwise, return table as schemaOrTable (backend will check if it's a table)
                return {
                    schemaOrTable: table,
                    prefix
                };
            }
        }
        // No FROM clause found, just return prefix (will suggest tables)
        return {
            prefix
        };
    }
    /**
     * Get cached completion items if still valid.
     */
    _getCached(prefix) {
        const key = prefix.toLowerCase();
        const entry = this._cache.get(key);
        if (!entry) {
            return null;
        }
        const age = Date.now() - entry.timestamp;
        if (age > this._cacheTTL) {
            this._cache.delete(key);
            return null;
        }
        return entry.items;
    }
    /**
     * Format completion items into the reply format expected by JupyterLab.
     */
    _formatReply(items, offset, prefix) {
        const start = offset - prefix.length;
        const end = offset;
        const formattedItems = items.map(item => {
            let label = item.name;
            let insertText = item.name;
            // Add quotes around JSONB keys
            if (item.type === 'jsonb_key') {
                insertText = `'${item.name}'`;
            }
            // Add table context for columns
            if (item.type === 'column' && item.table) {
                label = `${item.name} (${item.table})`;
            }
            // Add type-specific icon
            let typeIcon = '📊'; // Default for columns
            let sortText = item.name; // Default sort order
            if (item.type === 'table') {
                typeIcon = '📋';
            }
            else if (item.type === 'view') {
                typeIcon = '👁️';
            }
            else if (item.type === 'jsonb_key') {
                typeIcon = '🔑';
                // Use 0000 prefix to sort JSONB keys to the top (numbers sort before letters)
                sortText = `0000${item.name}`;
            }
            // Build documentation
            let documentation;
            if (item.type === 'column' && item.dataType && item.table) {
                documentation = `${item.table}.${item.name}: ${item.dataType}`;
            }
            else if (item.type === 'jsonb_key' && item.keyPath) {
                documentation = `JSONB key: ${item.keyPath.join(' -> ')}`;
            }
            return {
                label: `${typeIcon} ${label}`,
                insertText,
                sortText,
                type: item.type,
                documentation
            };
        });
        return {
            start,
            end,
            items: formattedItems
        };
    }
    /**
     * Clear the completion cache.
     */
    clearCache() {
        this._cache.clear();
    }
}


/***/ },

/***/ "./lib/request.js"
/*!************************!*\
  !*** ./lib/request.js ***!
  \************************/
(__unused_webpack_module, __webpack_exports__, __webpack_require__) {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   requestAPI: () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Call the server extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = '', init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'jl-db-comp', // our server extension's API namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    let data = await response.text();
    if (data.length > 0) {
        try {
            data = JSON.parse(data);
        }
        catch (error) {
            console.log('Not a JSON response body.', response);
        }
    }
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }

}]);
//# sourceMappingURL=lib_index_js.a0969ed73da70f2cc451.js.map