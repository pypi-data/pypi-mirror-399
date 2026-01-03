export const __webpack_id__="7394";export const __webpack_ids__=["7394"];export const __webpack_modules__={61974:function(e,t,i){var a={"./ha-icon-prev":["48268","2477"],"./ha-icon-button-toolbar":["48939","2791","3736"],"./ha-alert":["17963","6632"],"./ha-icon-button-toggle":["35150","2851"],"./ha-svg-icon.ts":["60961"],"./ha-alert.ts":["17963","6632"],"./ha-icon":["22598","7163"],"./ha-icon-next.ts":["28608"],"./ha-qr-code.ts":["16618","1343","6247"],"./ha-icon-overflow-menu.ts":["53623","2016","2791","2691","1296"],"./ha-icon-button-toggle.ts":["35150","2851"],"./ha-icon-button-group":["39651","7760"],"./ha-svg-icon":["60961"],"./ha-icon-button-prev":["80263","8076"],"./ha-icon-button.ts":["60733"],"./ha-icon-overflow-menu":["53623","2016","2791","2691","1296"],"./ha-icon-button-arrow-next":["56231","5500"],"./ha-icon-button-prev.ts":["80263","8076"],"./ha-icon-picker":["88867","8654","1955"],"./ha-icon-button-toolbar.ts":["48939","2791","3736"],"./ha-icon-button-arrow-prev.ts":["371"],"./ha-icon-button-next":["29795","9488"],"./ha-icon-next":["28608"],"./ha-icon-picker.ts":["88867","8654","1955"],"./ha-icon-prev.ts":["48268","2477"],"./ha-icon-button-arrow-prev":["371"],"./ha-icon-button-next.ts":["29795","9488"],"./ha-icon.ts":["22598","7163"],"./ha-qr-code":["16618","1343","6247"],"./ha-icon-button":["60733"],"./ha-icon-button-group.ts":["39651","7760"],"./ha-icon-button-arrow-next.ts":["56231","5500"]};function o(e){if(!i.o(a,e))return Promise.resolve().then((function(){var t=new Error("Cannot find module '"+e+"'");throw t.code="MODULE_NOT_FOUND",t}));var t=a[e],o=t[0];return Promise.all(t.slice(1).map(i.e)).then((function(){return i(o)}))}o.keys=()=>Object.keys(a),o.id=61974,e.exports=o},25115:function(e,t,i){var a={"./flow-preview-generic.ts":["66633","2239","6767","7251","3577","1543","3806","4916","8457","4398","5633","2478","3196","1794"],"./flow-preview-template":["71996","2239","6767","7251","3577","1543","3806","4916","8457","4398","5633","2478","3196","9149"],"./flow-preview-generic_camera":["93143","2239","6767","7251","3577","1543","3806","4916","8457","4398","5633","2478","3196","1628"],"./flow-preview-generic_camera.ts":["93143","2239","6767","7251","3577","1543","3806","4916","8457","4398","5633","2478","3196","1628"],"./flow-preview-generic":["66633","2239","6767","7251","3577","1543","3806","4916","8457","4398","5633","2478","3196","1794"],"./flow-preview-template.ts":["71996","2239","6767","7251","3577","1543","3806","4916","8457","4398","5633","2478","3196","9149"]};function o(e){if(!i.o(a,e))return Promise.resolve().then((function(){var t=new Error("Cannot find module '"+e+"'");throw t.code="MODULE_NOT_FOUND",t}));var t=a[e],o=t[0];return Promise.all(t.slice(1).map(i.e)).then((function(){return i(o)}))}o.keys=()=>Object.keys(a),o.id=25115,e.exports=o},45817:function(e,t,i){i.d(t,{d:()=>a});const a=(e,t=!0)=>{if(e.defaultPrevented||0!==e.button||e.metaKey||e.ctrlKey||e.shiftKey)return;const i=e.composedPath().find((e=>"A"===e.tagName));if(!i||i.target||i.hasAttribute("download")||"external"===i.getAttribute("rel"))return;let a=i.href;if(!a||-1!==a.indexOf("mailto:"))return;const o=window.location,s=o.origin||o.protocol+"//"+o.host;return a.startsWith(s)&&(a=a.slice(s.length),"#"!==a)?(t&&e.preventDefault(),a):void 0}},48565:function(e,t,i){i.d(t,{d:()=>a});const a=e=>{switch(e.language){case"cs":case"de":case"fi":case"fr":case"sk":case"sv":return" ";default:return""}}},86451:function(e,t,i){var a=i(62826),o=i(96196),s=i(77845);class r extends o.WF{render(){const e=o.qy`<div class="header-title">
      <slot name="title"></slot>
    </div>`,t=o.qy`<div class="header-subtitle">
      <slot name="subtitle"></slot>
    </div>`;return o.qy`
      <header class="header">
        <div class="header-bar">
          <section class="header-navigation-icon">
            <slot name="navigationIcon"></slot>
          </section>
          <section class="header-content">
            ${"above"===this.subtitlePosition?o.qy`${t}${e}`:o.qy`${e}${t}`}
          </section>
          <section class="header-action-items">
            <slot name="actionItems"></slot>
          </section>
        </div>
        <slot></slot>
      </header>
    `}static get styles(){return[o.AH`
        :host {
          display: block;
        }
        :host([show-border]) {
          border-bottom: 1px solid
            var(--mdc-dialog-scroll-divider-color, rgba(0, 0, 0, 0.12));
        }
        .header-bar {
          display: flex;
          flex-direction: row;
          align-items: center;
          padding: 0 var(--ha-space-1);
          box-sizing: border-box;
        }
        .header-content {
          flex: 1;
          padding: 10px var(--ha-space-1);
          display: flex;
          flex-direction: column;
          justify-content: center;
          min-height: var(--ha-space-12);
          min-width: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .header-title {
          height: var(
            --ha-dialog-header-title-height,
            calc(var(--ha-font-size-xl) + var(--ha-space-1))
          );
          font-size: var(--ha-font-size-xl);
          line-height: var(--ha-line-height-condensed);
          font-weight: var(--ha-font-weight-medium);
          color: var(--ha-dialog-header-title-color, var(--primary-text-color));
        }
        .header-subtitle {
          font-size: var(--ha-font-size-m);
          line-height: var(--ha-line-height-normal);
          color: var(
            --ha-dialog-header-subtitle-color,
            var(--secondary-text-color)
          );
        }
        @media all and (min-width: 450px) and (min-height: 500px) {
          .header-bar {
            padding: 0 var(--ha-space-2);
          }
        }
        .header-navigation-icon {
          flex: none;
          min-width: var(--ha-space-2);
          height: 100%;
          display: flex;
          flex-direction: row;
        }
        .header-action-items {
          flex: none;
          min-width: var(--ha-space-2);
          height: 100%;
          display: flex;
          flex-direction: row;
        }
      `]}constructor(...e){super(...e),this.subtitlePosition="below",this.showBorder=!1}}(0,a.__decorate)([(0,s.MZ)({type:String,attribute:"subtitle-position"})],r.prototype,"subtitlePosition",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0,attribute:"show-border"})],r.prototype,"showBorder",void 0),r=(0,a.__decorate)([(0,s.EM)("ha-dialog-header")],r)},23442:function(e,t,i){i.d(t,{$:()=>a});const a=e=>{const t={};return e.forEach((e=>{if(void 0!==e.description?.suggested_value&&null!==e.description?.suggested_value)t[e.name]=e.description.suggested_value;else if("default"in e)t[e.name]=e.default;else if("expandable"===e.type){const i=a(e.schema);(e.required||Object.keys(i).length)&&(t[e.name]=i)}else if(e.required){if("boolean"===e.type)t[e.name]=!1;else if("string"===e.type)t[e.name]="";else if("integer"===e.type)t[e.name]="valueMin"in e?e.valueMin:0;else if("constant"===e.type)t[e.name]=e.value;else if("float"===e.type)t[e.name]=0;else if("select"===e.type){if(e.options.length){const i=e.options[0];t[e.name]=Array.isArray(i)?i[0]:i}}else if("positive_time_period_dict"===e.type)t[e.name]={hours:0,minutes:0,seconds:0};else if("selector"in e){const i=e.selector;if("device"in i)t[e.name]=i.device?.multiple?[]:"";else if("entity"in i)t[e.name]=i.entity?.multiple?[]:"";else if("area"in i)t[e.name]=i.area?.multiple?[]:"";else if("label"in i)t[e.name]=i.label?.multiple?[]:"";else if("boolean"in i)t[e.name]=!1;else if("addon"in i||"attribute"in i||"file"in i||"icon"in i||"template"in i||"text"in i||"theme"in i||"object"in i)t[e.name]="";else if("number"in i)t[e.name]=i.number?.min??0;else if("select"in i){if(i.select?.options.length){const a=i.select.options[0],o="string"==typeof a?a:a.value;t[e.name]=i.select.multiple?[o]:o}}else if("country"in i)i.country?.countries?.length&&(t[e.name]=i.country.countries[0]);else if("language"in i)i.language?.languages?.length&&(t[e.name]=i.language.languages[0]);else if("duration"in i)t[e.name]={hours:0,minutes:0,seconds:0};else if("time"in i)t[e.name]="00:00:00";else if("date"in i||"datetime"in i){const i=(new Date).toISOString().slice(0,10);t[e.name]=`${i}T00:00:00`}else if("color_rgb"in i)t[e.name]=[0,0,0];else if("color_temp"in i)t[e.name]=i.color_temp?.min_mireds??153;else if("action"in i||"trigger"in i||"condition"in i)t[e.name]=[];else if("media"in i||"target"in i)t[e.name]={};else{if(!("state"in i))throw new Error(`Selector ${Object.keys(i)[0]} not supported in initial form data`);t[e.name]=i.state?.multiple?[]:""}}}else;})),t}},91120:function(e,t,i){var a=i(62826),o=i(96196),s=i(77845),r=i(51757),n=i(92542);i(17963),i(87156);const l={boolean:()=>Promise.all([i.e("8477"),i.e("2018")]).then(i.bind(i,49337)),constant:()=>i.e("9938").then(i.bind(i,37449)),float:()=>i.e("812").then(i.bind(i,5863)),grid:()=>i.e("798").then(i.bind(i,81213)),expandable:()=>i.e("8550").then(i.bind(i,29989)),integer:()=>Promise.all([i.e("8477"),i.e("1543"),i.e("1364")]).then(i.bind(i,28175)),multi_select:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("8477"),i.e("2016"),i.e("2067"),i.e("3616")]).then(i.bind(i,59827)),positive_time_period_dict:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("3777"),i.e("2389")]).then(i.bind(i,19797)),select:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("8654"),i.e("8477"),i.e("1279"),i.e("4933"),i.e("5186"),i.e("6262")]).then(i.bind(i,29317)),string:()=>i.e("8389").then(i.bind(i,33092)),optional_actions:()=>i.e("1454").then(i.bind(i,2173))},c=(e,t)=>e?!t.name||t.flatten?e:e[t.name]:null;class d extends o.WF{getFormProperties(){return{}}async focus(){await this.updateComplete;const e=this.renderRoot.querySelector(".root");if(e)for(const t of e.children)if("HA-ALERT"!==t.tagName){t instanceof o.mN&&await t.updateComplete,t.focus();break}}willUpdate(e){e.has("schema")&&this.schema&&this.schema.forEach((e=>{"selector"in e||l[e.type]?.()}))}render(){return o.qy`
      <div class="root" part="root">
        ${this.error&&this.error.base?o.qy`
              <ha-alert alert-type="error">
                ${this._computeError(this.error.base,this.schema)}
              </ha-alert>
            `:""}
        ${this.schema.map((e=>{const t=((e,t)=>e&&t.name?e[t.name]:null)(this.error,e),i=((e,t)=>e&&t.name?e[t.name]:null)(this.warning,e);return o.qy`
            ${t?o.qy`
                  <ha-alert own-margin alert-type="error">
                    ${this._computeError(t,e)}
                  </ha-alert>
                `:i?o.qy`
                    <ha-alert own-margin alert-type="warning">
                      ${this._computeWarning(i,e)}
                    </ha-alert>
                  `:""}
            ${"selector"in e?o.qy`<ha-selector
                  .schema=${e}
                  .hass=${this.hass}
                  .narrow=${this.narrow}
                  .name=${e.name}
                  .selector=${e.selector}
                  .value=${c(this.data,e)}
                  .label=${this._computeLabel(e,this.data)}
                  .disabled=${e.disabled||this.disabled||!1}
                  .placeholder=${e.required?void 0:e.default}
                  .helper=${this._computeHelper(e)}
                  .localizeValue=${this.localizeValue}
                  .required=${e.required||!1}
                  .context=${this._generateContext(e)}
                ></ha-selector>`:(0,r._)(this.fieldElementName(e.type),{schema:e,data:c(this.data,e),label:this._computeLabel(e,this.data),helper:this._computeHelper(e),disabled:this.disabled||e.disabled||!1,hass:this.hass,localize:this.hass?.localize,computeLabel:this.computeLabel,computeHelper:this.computeHelper,localizeValue:this.localizeValue,context:this._generateContext(e),...this.getFormProperties()})}
          `}))}
      </div>
    `}fieldElementName(e){return`ha-form-${e}`}_generateContext(e){if(!e.context)return;const t={};for(const[i,a]of Object.entries(e.context))t[i]=this.data[a];return t}createRenderRoot(){const e=super.createRenderRoot();return this.addValueChangedListener(e),e}addValueChangedListener(e){e.addEventListener("value-changed",(e=>{e.stopPropagation();const t=e.target.schema;if(e.target===this)return;const i=!t.name||"flatten"in t&&t.flatten?e.detail.value:{[t.name]:e.detail.value};this.data={...this.data,...i},(0,n.r)(this,"value-changed",{value:this.data})}))}_computeLabel(e,t){return this.computeLabel?this.computeLabel(e,t):e?e.name:""}_computeHelper(e){return this.computeHelper?this.computeHelper(e):""}_computeError(e,t){return Array.isArray(e)?o.qy`<ul>
        ${e.map((e=>o.qy`<li>
              ${this.computeError?this.computeError(e,t):e}
            </li>`))}
      </ul>`:this.computeError?this.computeError(e,t):e}_computeWarning(e,t){return this.computeWarning?this.computeWarning(e,t):e}constructor(...e){super(...e),this.narrow=!1,this.disabled=!1}}d.shadowRootOptions={mode:"open",delegatesFocus:!0},d.styles=o.AH`
    .root > * {
      display: block;
    }
    .root > *:not([own-margin]):not(:last-child) {
      margin-bottom: 24px;
    }
    ha-alert[own-margin] {
      margin-bottom: 4px;
    }
  `,(0,a.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],d.prototype,"narrow",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"data",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"schema",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"error",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"warning",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],d.prototype,"disabled",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"computeError",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"computeWarning",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"computeLabel",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"computeHelper",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],d.prototype,"localizeValue",void 0),d=(0,a.__decorate)([(0,s.EM)("ha-form")],d)},28089:function(e,t,i){var a=i(62826),o=i(96196),s=i(77845),r=i(1420),n=i(30015),l=i.n(n),c=i(92542),d=i(2209);let h;const p=e=>o.qy`${e}`,u=new class{get(e){return this._cache.get(e)}set(e,t){this._cache.set(e,t),this._expiration&&window.setTimeout((()=>this._cache.delete(e)),this._expiration)}has(e){return this._cache.has(e)}constructor(e){this._cache=new Map,this._expiration=e}}(1e3),_={reType:/(?<input>(\[!(?<type>caution|important|note|tip|warning)\])(?:\s|\\n)?)/i,typeToHaAlert:{caution:"error",important:"info",note:"info",tip:"success",warning:"warning"}};class g extends o.mN{disconnectedCallback(){if(super.disconnectedCallback(),this.cache){const e=this._computeCacheKey();u.set(e,this.innerHTML)}}createRenderRoot(){return this}update(e){super.update(e),void 0!==this.content&&(this._renderPromise=this._render())}async getUpdateComplete(){return await super.getUpdateComplete(),await this._renderPromise,!0}willUpdate(e){if(!this.innerHTML&&this.cache){const e=this._computeCacheKey();u.has(e)&&((0,o.XX)(p((0,r._)(u.get(e))),this.renderRoot),this._resize())}}_computeCacheKey(){return l()({content:this.content,allowSvg:this.allowSvg,allowDataUrl:this.allowDataUrl,breaks:this.breaks})}async _render(){const e=await(async(e,t,a)=>(h||(h=(0,d.LV)(new Worker(new URL(i.p+i.u("5640"),i.b)))),h.renderMarkdown(e,t,a)))(String(this.content),{breaks:this.breaks,gfm:!0},{allowSvg:this.allowSvg,allowDataUrl:this.allowDataUrl});(0,o.XX)(p((0,r._)(e.join(""))),this.renderRoot),this._resize();const t=document.createTreeWalker(this,NodeFilter.SHOW_ELEMENT,null);for(;t.nextNode();){const e=t.currentNode;if(e instanceof HTMLAnchorElement&&e.host!==document.location.host)e.target="_blank",e.rel="noreferrer noopener";else if(e instanceof HTMLImageElement)this.lazyImages&&(e.loading="lazy"),e.addEventListener("load",this._resize);else if(e instanceof HTMLQuoteElement){const i=e.firstElementChild?.firstChild?.textContent&&_.reType.exec(e.firstElementChild.firstChild.textContent);if(i){const{type:a}=i.groups,o=document.createElement("ha-alert");o.alertType=_.typeToHaAlert[a.toLowerCase()],o.append(...Array.from(e.childNodes).map((e=>{const t=Array.from(e.childNodes);if(!this.breaks&&t.length){const e=t[0];e.nodeType===Node.TEXT_NODE&&e.textContent===i.input&&e.textContent?.includes("\n")&&(e.textContent=e.textContent.split("\n").slice(1).join("\n"))}return t})).reduce(((e,t)=>e.concat(t)),[]).filter((e=>e.textContent&&e.textContent!==i.input))),t.parentNode().replaceChild(o,e)}}else e instanceof HTMLElement&&["ha-alert","ha-qr-code","ha-icon","ha-svg-icon"].includes(e.localName)&&i(61974)(`./${e.localName}`)}}constructor(...e){super(...e),this.allowSvg=!1,this.allowDataUrl=!1,this.breaks=!1,this.lazyImages=!1,this.cache=!1,this._renderPromise=Promise.resolve(),this._resize=()=>(0,c.r)(this,"content-resize")}}(0,a.__decorate)([(0,s.MZ)()],g.prototype,"content",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:"allow-svg",type:Boolean})],g.prototype,"allowSvg",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:"allow-data-url",type:Boolean})],g.prototype,"allowDataUrl",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],g.prototype,"breaks",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean,attribute:"lazy-images"})],g.prototype,"lazyImages",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],g.prototype,"cache",void 0),g=(0,a.__decorate)([(0,s.EM)("ha-markdown-element")],g);class m extends o.WF{async getUpdateComplete(){const e=await super.getUpdateComplete();return await(this._markdownElement?.updateComplete),e}render(){return this.content?o.qy`<ha-markdown-element
      .content=${this.content}
      .allowSvg=${this.allowSvg}
      .allowDataUrl=${this.allowDataUrl}
      .breaks=${this.breaks}
      .lazyImages=${this.lazyImages}
      .cache=${this.cache}
    ></ha-markdown-element>`:o.s6}constructor(...e){super(...e),this.allowSvg=!1,this.allowDataUrl=!1,this.breaks=!1,this.lazyImages=!1,this.cache=!1}}m.styles=o.AH`
    :host {
      display: block;
    }
    ha-markdown-element {
      -ms-user-select: text;
      -webkit-user-select: text;
      -moz-user-select: text;
    }
    ha-markdown-element > *:first-child {
      margin-top: 0;
    }
    ha-markdown-element > *:last-child {
      margin-bottom: 0;
    }
    ha-alert {
      display: block;
      margin: var(--ha-space-1) 0;
    }
    a {
      color: var(--markdown-link-color, var(--primary-color));
    }
    img {
      background-color: var(--markdown-image-background-color);
      border-radius: var(--markdown-image-border-radius);
      max-width: 100%;
      height: auto;
      width: auto;
      transition: height 0.2s ease-in-out;
    }
    p:first-child > img:first-child {
      vertical-align: top;
    }
    p:first-child > img:last-child {
      vertical-align: top;
    }
    :host > ul,
    :host > ol {
      padding-inline-start: var(--markdown-list-indent, revert);
    }
    li {
      &:has(input[type="checkbox"]) {
        list-style: none;
        & > input[type="checkbox"] {
          margin-left: 0;
        }
      }
    }
    svg {
      background-color: var(--markdown-svg-background-color, none);
      color: var(--markdown-svg-color, none);
    }
    code,
    pre {
      background-color: var(--markdown-code-background-color, none);
      border-radius: var(--ha-border-radius-sm);
      color: var(--markdown-code-text-color, inherit);
    }
    code {
      font-size: var(--ha-font-size-s);
      padding: 0.2em 0.4em;
    }
    pre code {
      padding: 0;
    }
    pre {
      padding: var(--ha-space-4);
      overflow: auto;
      line-height: var(--ha-line-height-condensed);
      font-family: var(--ha-font-family-code);
    }
    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
      line-height: initial;
    }
    h2 {
      font-size: var(--ha-font-size-xl);
      font-weight: var(--ha-font-weight-bold);
    }
    hr {
      border-color: var(--divider-color);
      border-bottom: none;
      margin: var(--ha-space-4) 0;
    }
    table {
      border-collapse: var(--markdown-table-border-collapse, collapse);
    }
    div:has(> table) {
      overflow: auto;
    }
    th {
      text-align: start;
    }
    td,
    th {
      border-width: var(--markdown-table-border-width, 1px);
      border-style: var(--markdown-table-border-style, solid);
      border-color: var(--markdown-table-border-color, var(--divider-color));
      padding: 0.25em 0.5em;
    }
    blockquote {
      border-left: 4px solid var(--divider-color);
      margin-inline: 0;
      padding-inline: 1em;
    }
  `,(0,a.__decorate)([(0,s.MZ)()],m.prototype,"content",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:"allow-svg",type:Boolean})],m.prototype,"allowSvg",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:"allow-data-url",type:Boolean})],m.prototype,"allowDataUrl",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],m.prototype,"breaks",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean,attribute:"lazy-images"})],m.prototype,"lazyImages",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],m.prototype,"cache",void 0),(0,a.__decorate)([(0,s.P)("ha-markdown-element")],m.prototype,"_markdownElement",void 0),m=(0,a.__decorate)([(0,s.EM)("ha-markdown")],m)},64109:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(62826),o=i(65686),s=i(96196),r=i(77845),n=e([o]);o=(n.then?(await n)():n)[0];class l extends o.A{updated(e){if(super.updated(e),e.has("size"))switch(this.size){case"tiny":this.style.setProperty("--ha-progress-ring-size","16px");break;case"small":this.style.setProperty("--ha-progress-ring-size","28px");break;case"medium":this.style.setProperty("--ha-progress-ring-size","48px");break;case"large":this.style.setProperty("--ha-progress-ring-size","68px");break;case void 0:this.style.removeProperty("--ha-progress-ring-size")}}static get styles(){return[o.A.styles,s.AH`
        :host {
          --indicator-color: var(
            --ha-progress-ring-indicator-color,
            var(--primary-color)
          );
          --track-color: var(
            --ha-progress-ring-divider-color,
            var(--divider-color)
          );
          --track-width: 4px;
          --speed: 3.5s;
          --size: var(--ha-progress-ring-size, 48px);
        }
      `]}}(0,a.__decorate)([(0,r.MZ)()],l.prototype,"size",void 0),l=(0,a.__decorate)([(0,r.EM)("ha-progress-ring")],l),t()}catch(l){t(l)}}))},41558:function(e,t,i){i.d(t,{KC:()=>d,Vy:()=>l,ds:()=>s,ew:()=>n,g5:()=>c,tl:()=>r});var a=i(9477),o=i(31136);const s=(e,t,i)=>e.connection.subscribeMessage(i,{type:"assist_satellite/intercept_wake_word",entity_id:t}),r=(e,t)=>e.callWS({type:"assist_satellite/test_connection",entity_id:t}),n=(e,t,i)=>e.callService("assist_satellite","announce",i,{entity_id:t}),l=(e,t)=>e.callWS({type:"assist_satellite/get_configuration",entity_id:t}),c=(e,t,i)=>e.callWS({type:"assist_satellite/set_wake_words",entity_id:t,wake_word_ids:i}),d=e=>e&&e.state!==o.Hh&&(0,a.$)(e,1)},54193:function(e,t,i){i.d(t,{Hg:()=>a,e0:()=>o});const a=e=>e.map((e=>{if("string"!==e.type)return e;switch(e.name){case"username":return{...e,autocomplete:"username",autofocus:!0};case"password":return{...e,autocomplete:"current-password"};case"code":return{...e,autocomplete:"one-time-code",autofocus:!0};default:return e}})),o=(e,t)=>e.callWS({type:"auth/sign_path",path:t})},23608:function(e,t,i){i.d(t,{PN:()=>s,jm:()=>r,sR:()=>n,t1:()=>o,t2:()=>c,yu:()=>l});const a={"HA-Frontend-Base":`${location.protocol}//${location.host}`},o=(e,t,i)=>e.callApi("POST","config/config_entries/flow",{handler:t,show_advanced_options:Boolean(e.userData?.showAdvanced),entry_id:i},a),s=(e,t)=>e.callApi("GET",`config/config_entries/flow/${t}`,void 0,a),r=(e,t,i)=>e.callApi("POST",`config/config_entries/flow/${t}`,i,a),n=(e,t)=>e.callApi("DELETE",`config/config_entries/flow/${t}`),l=(e,t)=>e.callApi("GET","config/config_entries/flow_handlers"+(t?`?type=${t}`:"")),c=e=>e.sendMessagePromise({type:"config_entries/flow/progress"})},86807:function(e,t,i){i.d(t,{K:()=>o,P:()=>a});const a=(e,t)=>e.subscribeEvents(t,"data_entry_flow_progressed"),o=(e,t)=>e.subscribeEvents(t,"data_entry_flow_progress_update")},31136:function(e,t,i){i.d(t,{HV:()=>s,Hh:()=>o,KF:()=>n,ON:()=>r,g0:()=>d,s7:()=>l});var a=i(99245);const o="unavailable",s="unknown",r="on",n="off",l=[o,s],c=[o,s,n],d=(0,a.g)(l);(0,a.g)(c)},73103:function(e,t,i){i.d(t,{F:()=>s,Q:()=>o});const a=["generic_camera","template"],o=(e,t,i,a,o,s)=>e.connection.subscribeMessage(s,{type:`${t}/start_preview`,flow_id:i,flow_type:a,user_input:o}),s=e=>a.includes(e)?e:"generic"},90313:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t);var o=i(62826),s=i(96196),r=i(77845),n=i(22786),l=i(92542),c=(i(95637),i(86451),i(60733),i(86807)),d=i(39396),h=i(62001),p=i(10234),u=i(93056),_=i(64533),g=i(12083),m=i(84398),f=i(19486),v=(i(59395),i(12527)),w=i(35804),y=i(53264),b=i(73042),$=e([u,_,g,m,f,v]);[u,_,g,m,f,v]=$.then?(await $)():$;const x="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",k="M15.07,11.25L14.17,12.17C13.45,12.89 13,13.5 13,15H11V14.5C11,13.39 11.45,12.39 12.17,11.67L13.41,10.41C13.78,10.05 14,9.55 14,9C14,7.89 13.1,7 12,7A2,2 0 0,0 10,9H8A4,4 0 0,1 12,5A4,4 0 0,1 16,9C16,9.88 15.64,10.67 15.07,11.25M13,19H11V17H13M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12C22,6.47 17.5,2 12,2Z";let C=0;class M extends s.WF{async showDialog(e){this._params=e,this._instance=C++;const t=this._instance;let i;if(e.startFlowHandler){this._loading="loading_flow",this._handler=e.startFlowHandler;try{i=await this._params.flowConfig.createFlow(this.hass,e.startFlowHandler)}catch(a){this.closeDialog();let e=a.message||a.body||"Unknown error";return"string"!=typeof e&&(e=JSON.stringify(e)),void(0,p.K$)(this,{title:this.hass.localize("ui.panel.config.integrations.config_flow.error"),text:`${this.hass.localize("ui.panel.config.integrations.config_flow.could_not_load")}: ${e}`})}if(t!==this._instance)return}else{if(!e.continueFlowId)return;this._loading="loading_flow";try{i=await e.flowConfig.fetchFlow(this.hass,e.continueFlowId)}catch(a){this.closeDialog();let e=a.message||a.body||"Unknown error";return"string"!=typeof e&&(e=JSON.stringify(e)),void(0,p.K$)(this,{title:this.hass.localize("ui.panel.config.integrations.config_flow.error"),text:`${this.hass.localize("ui.panel.config.integrations.config_flow.could_not_load")}: ${e}`})}}t===this._instance&&(this._processStep(i),this._loading=void 0)}closeDialog(){if(!this._params)return;const e=Boolean(this._step&&["create_entry","abort"].includes(this._step.type));!this._step||e||this._params.continueFlowId||this._params.flowConfig.deleteFlow(this.hass,this._step.flow_id),this._step&&this._params.dialogClosedCallback&&this._params.dialogClosedCallback({flowFinished:e,entryId:"result"in this._step?this._step.result?.entry_id:void 0}),this._loading=void 0,this._step=void 0,this._params=void 0,this._handler=void 0,this._unsubDataEntryFlowProgress&&(this._unsubDataEntryFlowProgress(),this._unsubDataEntryFlowProgress=void 0),(0,l.r)(this,"dialog-closed",{dialog:this.localName})}_getDialogTitle(){if(this._loading||!this._step||!this._params)return"";switch(this._step.type){case"form":return this._params.flowConfig.renderShowFormStepHeader(this.hass,this._step);case"abort":return this._params.flowConfig.renderAbortHeader?this._params.flowConfig.renderAbortHeader(this.hass,this._step):this.hass.localize(`component.${this._params.domain??this._step.handler}.title`);case"progress":return this._params.flowConfig.renderShowFormProgressHeader(this.hass,this._step);case"menu":return this._params.flowConfig.renderMenuHeader(this.hass,this._step);case"create_entry":{const e=this._devices(this._params.flowConfig.showDevices,Object.values(this.hass.devices),this._step.result?.entry_id,this._params.carryOverDevices).length;return this.hass.localize("ui.panel.config.integrations.config_flow."+(e?"device_created":"success"),{number:e})}default:return""}}_getDialogSubtitle(){if(this._loading||!this._step||!this._params)return"";switch(this._step.type){case"form":return this._params.flowConfig.renderShowFormStepSubheader?.(this.hass,this._step);case"abort":return this._params.flowConfig.renderAbortSubheader?.(this.hass,this._step);case"progress":return this._params.flowConfig.renderShowFormProgressSubheader?.(this.hass,this._step);case"menu":return this._params.flowConfig.renderMenuSubheader?.(this.hass,this._step);default:return""}}render(){if(!this._params)return s.s6;const e=["form","menu","external","progress","data_entry_flow_progressed"].includes(this._step?.type)&&this._params.manifest?.is_built_in||!!this._params.manifest?.documentation,t=this._getDialogTitle(),i=this._getDialogSubtitle();return s.qy`
      <ha-dialog
        open
        @closed=${this.closeDialog}
        scrimClickAction
        escapeKeyAction
        hideActions
        .heading=${t||!0}
      >
        <ha-dialog-header slot="heading">
          <ha-icon-button
            .label=${this.hass.localize("ui.common.close")}
            .path=${x}
            dialogAction="close"
            slot="navigationIcon"
          ></ha-icon-button>

          <div
            slot="title"
            class="dialog-title${"form"===this._step?.type?" form":""}"
            title=${t}
          >
            ${t}
          </div>

          ${i?s.qy` <div slot="subtitle">${i}</div>`:s.s6}
          ${e&&!this._loading&&this._step?s.qy`
                <a
                  slot="actionItems"
                  class="help"
                  href=${this._params.manifest.is_built_in?(0,h.o)(this.hass,`/integrations/${this._params.manifest.domain}`):this._params.manifest.documentation}
                  target="_blank"
                  rel="noreferrer noopener"
                >
                  <ha-icon-button
                    .label=${this.hass.localize("ui.common.help")}
                    .path=${k}
                  >
                  </ha-icon-button
                ></a>
              `:s.s6}
        </ha-dialog-header>
        <div>
          ${this._loading||null===this._step?s.qy`
                <step-flow-loading
                  .flowConfig=${this._params.flowConfig}
                  .hass=${this.hass}
                  .loadingReason=${this._loading}
                  .handler=${this._handler}
                  .step=${this._step}
                ></step-flow-loading>
              `:void 0===this._step?s.s6:s.qy`
                  ${"form"===this._step.type?s.qy`
                        <step-flow-form
                          narrow
                          .flowConfig=${this._params.flowConfig}
                          .step=${this._step}
                          .hass=${this.hass}
                        ></step-flow-form>
                      `:"external"===this._step.type?s.qy`
                          <step-flow-external
                            .flowConfig=${this._params.flowConfig}
                            .step=${this._step}
                            .hass=${this.hass}
                          ></step-flow-external>
                        `:"abort"===this._step.type?s.qy`
                            <step-flow-abort
                              .params=${this._params}
                              .step=${this._step}
                              .hass=${this.hass}
                              .handler=${this._step.handler}
                              .domain=${this._params.domain??this._step.handler}
                            ></step-flow-abort>
                          `:"progress"===this._step.type?s.qy`
                              <step-flow-progress
                                .flowConfig=${this._params.flowConfig}
                                .step=${this._step}
                                .hass=${this.hass}
                                .progress=${this._progress}
                              ></step-flow-progress>
                            `:"menu"===this._step.type?s.qy`
                                <step-flow-menu
                                  .flowConfig=${this._params.flowConfig}
                                  .step=${this._step}
                                  .hass=${this.hass}
                                ></step-flow-menu>
                              `:s.qy`
                                <step-flow-create-entry
                                  .flowConfig=${this._params.flowConfig}
                                  .step=${this._step}
                                  .hass=${this.hass}
                                  .navigateToResult=${this._params.navigateToResult??!1}
                                  .devices=${this._devices(this._params.flowConfig.showDevices,Object.values(this.hass.devices),this._step.result?.entry_id,this._params.carryOverDevices)}
                                ></step-flow-create-entry>
                              `}
                `}
        </div>
      </ha-dialog>
    `}firstUpdated(e){super.firstUpdated(e),this.addEventListener("flow-update",(e=>{const{step:t,stepPromise:i}=e.detail;this._processStep(t||i)}))}willUpdate(e){super.willUpdate(e),e.has("_step")&&this._step&&["external","progress"].includes(this._step.type)&&this._subscribeDataEntryFlowProgressed()}async _processStep(e){if(void 0===e)return void this.closeDialog();const t=setTimeout((()=>{this._loading="loading_step"}),250);let i;try{i=await e}catch(a){return this.closeDialog(),void(0,p.K$)(this,{title:this.hass.localize("ui.panel.config.integrations.config_flow.error"),text:a?.body?.message})}finally{clearTimeout(t),this._loading=void 0}this._step=void 0,await this.updateComplete,this._step=i,"create_entry"!==i.type&&"abort"!==i.type||!i.next_flow||(this._step=void 0,this._handler=void 0,this._unsubDataEntryFlowProgress&&(this._unsubDataEntryFlowProgress(),this._unsubDataEntryFlowProgress=void 0),"config_flow"===i.next_flow[0]?(0,b.W)(this,{continueFlowId:i.next_flow[1],carryOverDevices:this._devices(this._params.flowConfig.showDevices,Object.values(this.hass.devices),"create_entry"===i.type?i.result?.entry_id:void 0,this._params.carryOverDevices).map((e=>e.id)),dialogClosedCallback:this._params.dialogClosedCallback}):"options_flow"===i.next_flow[0]?"create_entry"===i.type&&(0,w.Q)(this,i.result,{continueFlowId:i.next_flow[1],navigateToResult:this._params.navigateToResult,dialogClosedCallback:this._params.dialogClosedCallback}):"config_subentries_flow"===i.next_flow[0]?"create_entry"===i.type&&(0,y.a)(this,i.result,i.next_flow[0],{continueFlowId:i.next_flow[1],navigateToResult:this._params.navigateToResult,dialogClosedCallback:this._params.dialogClosedCallback}):(this.closeDialog(),(0,p.K$)(this,{text:this.hass.localize("ui.panel.config.integrations.config_flow.error",{error:`Unsupported next flow type: ${i.next_flow[0]}`})})))}async _subscribeDataEntryFlowProgressed(){if(this._unsubDataEntryFlowProgress)return;this._progress=void 0;const e=[(0,c.P)(this.hass.connection,(e=>{e.data.flow_id===this._step?.flow_id&&(this._processStep(this._params.flowConfig.fetchFlow(this.hass,this._step.flow_id)),this._progress=void 0)})),(0,c.K)(this.hass.connection,(e=>{this._progress=Math.ceil(100*e.data.progress)}))];this._unsubDataEntryFlowProgress=async()=>{(await Promise.all(e)).map((e=>e()))}}static get styles(){return[d.nA,s.AH`
        ha-dialog {
          --dialog-content-padding: 0;
        }
        .dialog-title {
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .dialog-title.form {
          white-space: normal;
        }
        .help {
          color: var(--secondary-text-color);
        }
      `]}constructor(...e){super(...e),this._instance=C,this._devices=(0,n.A)(((e,t,i,a)=>e&&i?t.filter((e=>e.config_entries.includes(i)||a?.includes(e.id))):[]))}}(0,o.__decorate)([(0,r.MZ)({attribute:!1})],M.prototype,"hass",void 0),(0,o.__decorate)([(0,r.wk)()],M.prototype,"_params",void 0),(0,o.__decorate)([(0,r.wk)()],M.prototype,"_loading",void 0),(0,o.__decorate)([(0,r.wk)()],M.prototype,"_progress",void 0),(0,o.__decorate)([(0,r.wk)()],M.prototype,"_step",void 0),(0,o.__decorate)([(0,r.wk)()],M.prototype,"_handler",void 0),M=(0,o.__decorate)([(0,r.EM)("dialog-data-entry-flow")],M),a()}catch(x){a(x)}}))},73042:function(e,t,i){i.d(t,{W:()=>n});var a=i(96196),o=i(23608),s=i(84125),r=i(73347);const n=(e,t)=>(0,r.g)(e,t,{flowType:"config_flow",showDevices:!0,createFlow:async(e,i)=>{const[a]=await Promise.all([(0,o.t1)(e,i,t.entryId),e.loadFragmentTranslation("config"),e.loadBackendTranslation("config",i),e.loadBackendTranslation("selector",i),e.loadBackendTranslation("title",i)]);return a},fetchFlow:async(e,t)=>{const[i]=await Promise.all([(0,o.PN)(e,t),e.loadFragmentTranslation("config")]);return await Promise.all([e.loadBackendTranslation("config",i.handler),e.loadBackendTranslation("selector",i.handler),e.loadBackendTranslation("title",i.handler)]),i},handleFlowStep:o.jm,deleteFlow:o.sR,renderAbortDescription(e,t){const i=e.localize(`component.${t.translation_domain||t.handler}.config.abort.${t.reason}`,t.description_placeholders);return i?a.qy`
            <ha-markdown allow-svg breaks .content=${i}></ha-markdown>
          `:t.reason},renderShowFormStepHeader(e,t){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.title`,t.description_placeholders)||e.localize(`component.${t.handler}.title`)},renderShowFormStepDescription(e,t){const i=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.description`,t.description_placeholders);return i?a.qy`
            <ha-markdown
              .allowDataUrl=${"zwave_js"===t.handler}
              allow-svg
              breaks
              .content=${i}
            ></ha-markdown>
          `:""},renderShowFormStepFieldLabel(e,t,i,a){if("expandable"===i.type)return e.localize(`component.${t.handler}.config.step.${t.step_id}.sections.${i.name}.name`,t.description_placeholders);const o=a?.path?.[0]?`sections.${a.path[0]}.`:"";return e.localize(`component.${t.handler}.config.step.${t.step_id}.${o}data.${i.name}`,t.description_placeholders)||i.name},renderShowFormStepFieldHelper(e,t,i,o){if("expandable"===i.type)return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.sections.${i.name}.description`,t.description_placeholders);const s=o?.path?.[0]?`sections.${o.path[0]}.`:"",r=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.${s}data_description.${i.name}`,t.description_placeholders);return r?a.qy`<ha-markdown breaks .content=${r}></ha-markdown>`:""},renderShowFormStepFieldError(e,t,i){return e.localize(`component.${t.translation_domain||t.translation_domain||t.handler}.config.error.${i}`,t.description_placeholders)||i},renderShowFormStepFieldLocalizeValue(e,t,i){return e.localize(`component.${t.handler}.selector.${i}`)},renderShowFormStepSubmitButton(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.submit`)||e.localize("ui.panel.config.integrations.config_flow."+(!1===t.last_step?"next":"submit"))},renderExternalStepHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize("ui.panel.config.integrations.config_flow.external_step.open_site")},renderExternalStepDescription(e,t){const i=e.localize(`component.${t.translation_domain||t.handler}.config.${t.step_id}.description`,t.description_placeholders);return a.qy`
        <p>
          ${e.localize("ui.panel.config.integrations.config_flow.external_step.description")}
        </p>
        ${i?a.qy`
              <ha-markdown
                allow-svg
                breaks
                .content=${i}
              ></ha-markdown>
            `:""}
      `},renderCreateEntryDescription(e,t){const i=e.localize(`component.${t.translation_domain||t.handler}.config.create_entry.${t.description||"default"}`,t.description_placeholders);return a.qy`
        ${i?a.qy`
              <ha-markdown
                allow-svg
                breaks
                .content=${i}
              ></ha-markdown>
            `:a.s6}
      `},renderShowFormProgressHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize(`component.${t.handler}.title`)},renderShowFormProgressDescription(e,t){const i=e.localize(`component.${t.translation_domain||t.handler}.config.progress.${t.progress_action}`,t.description_placeholders);return i?a.qy`
            <ha-markdown allow-svg breaks .content=${i}></ha-markdown>
          `:""},renderMenuHeader(e,t){return e.localize(`component.${t.handler}.config.step.${t.step_id}.title`)||e.localize(`component.${t.handler}.title`)},renderMenuDescription(e,t){const i=e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.description`,t.description_placeholders);return i?a.qy`
            <ha-markdown allow-svg breaks .content=${i}></ha-markdown>
          `:""},renderMenuOption(e,t,i){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.menu_options.${i}`,t.description_placeholders)},renderMenuOptionDescription(e,t,i){return e.localize(`component.${t.translation_domain||t.handler}.config.step.${t.step_id}.menu_option_descriptions.${i}`,t.description_placeholders)},renderLoadingDescription(e,t,i,a){if("loading_flow"!==t&&"loading_step"!==t)return"";const o=a?.handler||i;return e.localize(`ui.panel.config.integrations.config_flow.loading.${t}`,{integration:o?(0,s.p$)(e.localize,o):e.localize("ui.panel.config.integrations.config_flow.loading.fallback_title")})}})},93056:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(62826),o=i(96196),s=i(77845),r=i(92542),n=i(78778),l=i(73042),c=i(97854),d=i(89473),h=e([d]);d=(h.then?(await h)():h)[0];class p extends o.WF{firstUpdated(e){super.firstUpdated(e),"missing_credentials"===this.step.reason&&this._handleMissingCreds()}render(){return"missing_credentials"===this.step.reason?o.s6:o.qy`
      <div class="content">
        ${this.params.flowConfig.renderAbortDescription(this.hass,this.step)}
      </div>
      <div class="buttons">
        <ha-button appearance="plain" @click=${this._flowDone}
          >${this.hass.localize("ui.panel.config.integrations.config_flow.close")}</ha-button
        >
      </div>
    `}async _handleMissingCreds(){(0,n.a)(this.params.dialogParentElement,{selectedDomain:this.domain,manifest:this.params.manifest,applicationCredentialAddedCallback:()=>{(0,l.W)(this.params.dialogParentElement,{dialogClosedCallback:this.params.dialogClosedCallback,startFlowHandler:this.handler,showAdvanced:this.hass.userData?.showAdvanced,navigateToResult:this.params.navigateToResult})}}),this._flowDone()}_flowDone(){(0,r.r)(this,"flow-update",{step:void 0})}static get styles(){return c.G}}(0,a.__decorate)([(0,s.MZ)({attribute:!1})],p.prototype,"params",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],p.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],p.prototype,"step",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],p.prototype,"domain",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],p.prototype,"handler",void 0),p=(0,a.__decorate)([(0,s.EM)("step-flow-abort")],p),t()}catch(p){t(p)}}))},64533:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(62826),o=i(96196),s=i(77845),r=i(22786),n=i(92542),l=i(16727),c=i(41144),d=i(5871),h=i(53907),p=i(89473),u=i(41558),_=i(1491),g=i(22800),m=i(84125),f=i(76681),v=i(10234),w=i(6358),y=i(97854),b=i(3950),$=e([h,p]);[h,p]=$.then?(await $)():$;class x extends o.WF{firstUpdated(e){super.firstUpdated(e),this._loadDomains()}willUpdate(e){if(!e.has("devices")&&!e.has("hass"))return;if(1!==this.devices.length||this.devices[0].primary_config_entry!==this.step.result?.entry_id||"voip"===this.step.result.domain)return;const t=this._deviceEntities(this.devices[0].id,Object.values(this.hass.entities),"assist_satellite");t.length&&t.some((e=>(0,u.KC)(this.hass.states[e.entity_id])))&&(this.navigateToResult=!1,this._flowDone(),(0,w.L)(this,{deviceId:this.devices[0].id}))}render(){const e=this.hass.localize,t=this.step.result?{...this._domains,[this.step.result.entry_id]:this.step.result.domain}:this._domains;return o.qy`
      <div class="content">
        ${this.flowConfig.renderCreateEntryDescription(this.hass,this.step)}
        ${"not_loaded"===this.step.result?.state?o.qy`<span class="error"
              >${e("ui.panel.config.integrations.config_flow.not_loaded")}</span
            >`:o.s6}
        ${0===this.devices.length&&["options_flow","repair_flow"].includes(this.flowConfig.flowType)?o.s6:0===this.devices.length?o.qy`<p>
                ${e("ui.panel.config.integrations.config_flow.created_config",{name:this.step.title})}
              </p>`:o.qy`
                <div class="devices">
                  ${this.devices.map((i=>o.qy`
                      <div class="device">
                        <div class="device-info">
                          ${i.primary_config_entry&&t[i.primary_config_entry]?o.qy`<img
                                slot="graphic"
                                alt=${(0,m.p$)(this.hass.localize,t[i.primary_config_entry])}
                                src=${(0,f.MR)({domain:t[i.primary_config_entry],type:"icon",darkOptimized:this.hass.themes?.darkMode})}
                                crossorigin="anonymous"
                                referrerpolicy="no-referrer"
                              />`:o.s6}
                          <div class="device-info-details">
                            <span>${i.model||i.manufacturer}</span>
                            ${i.model?o.qy`<span class="secondary">
                                  ${i.manufacturer}
                                </span>`:o.s6}
                          </div>
                        </div>
                        <ha-textfield
                          .label=${e("ui.panel.config.integrations.config_flow.device_name")}
                          .placeholder=${(0,l.T)(i,this.hass)}
                          .value=${this._deviceUpdate[i.id]?.name??(0,l.xn)(i)}
                          @change=${this._deviceNameChanged}
                          .device=${i.id}
                        ></ha-textfield>
                        <ha-area-picker
                          .hass=${this.hass}
                          .device=${i.id}
                          .value=${this._deviceUpdate[i.id]?.area??i.area_id??void 0}
                          @value-changed=${this._areaPicked}
                        ></ha-area-picker>
                      </div>
                    `))}
                </div>
              `}
      </div>
      <div class="buttons">
        <ha-button @click=${this._flowDone}
          >${e("ui.panel.config.integrations.config_flow."+(!this.devices.length||Object.keys(this._deviceUpdate).length?"finish":"finish_skip"))}</ha-button
        >
      </div>
    `}async _loadDomains(){const e=await(0,b.VN)(this.hass);this._domains=Object.fromEntries(e.map((e=>[e.entry_id,e.domain])))}async _flowDone(){if(Object.keys(this._deviceUpdate).length){const e=[],t=Object.entries(this._deviceUpdate).map((([t,i])=>(i.name&&e.push(t),(0,_.FB)(this.hass,t,{name_by_user:i.name,area_id:i.area}).catch((e=>{(0,v.K$)(this,{text:this.hass.localize("ui.panel.config.integrations.config_flow.error_saving_device",{error:e.message})})})))));await Promise.allSettled(t);const i=[],a=[];e.forEach((e=>{const t=this._deviceEntities(e,Object.values(this.hass.entities));a.push(...t.map((e=>e.entity_id)))}));const o=await(0,g.BM)(this.hass,a);Object.entries(o).forEach((([e,t])=>{t&&i.push((0,g.G_)(this.hass,e,{new_entity_id:t}).catch((e=>(0,v.K$)(this,{text:this.hass.localize("ui.panel.config.integrations.config_flow.error_saving_entity",{error:e.message})}))))})),await Promise.allSettled(i)}(0,n.r)(this,"flow-update",{step:void 0}),this.step.result&&this.navigateToResult&&(1===this.devices.length?(0,d.o)(`/config/devices/device/${this.devices[0].id}`):(0,d.o)(`/config/integrations/integration/${this.step.result.domain}#config_entry=${this.step.result.entry_id}`))}async _areaPicked(e){const t=e.currentTarget.device,i=e.detail.value;t in this._deviceUpdate||(this._deviceUpdate[t]={}),this._deviceUpdate[t].area=i,this.requestUpdate("_deviceUpdate")}_deviceNameChanged(e){const t=e.currentTarget,i=t.device,a=t.value;i in this._deviceUpdate||(this._deviceUpdate[i]={}),this._deviceUpdate[i].name=a,this.requestUpdate("_deviceUpdate")}static get styles(){return[y.G,o.AH`
        .devices {
          display: flex;
          margin: -4px;
          max-height: 600px;
          overflow-y: auto;
          flex-direction: column;
        }
        @media all and (max-width: 450px), all and (max-height: 500px) {
          .devices {
            /* header - margin content - footer */
            max-height: calc(100vh - 52px - 20px - 52px);
          }
        }
        .device {
          border: 1px solid var(--divider-color);
          padding: 6px;
          border-radius: var(--ha-border-radius-sm);
          margin: 4px;
          display: inline-block;
        }
        .device-info {
          display: flex;
          align-items: center;
          gap: var(--ha-space-2);
        }
        .device-info img {
          width: 40px;
          height: 40px;
        }
        .device-info-details {
          display: flex;
          flex-direction: column;
          justify-content: center;
        }
        .secondary {
          color: var(--secondary-text-color);
        }
        ha-textfield,
        ha-area-picker {
          display: block;
        }
        ha-textfield {
          margin: 8px 0;
        }
        .buttons > *:last-child {
          margin-left: auto;
          margin-inline-start: auto;
          margin-inline-end: initial;
        }
        .error {
          color: var(--error-color);
        }
      `]}constructor(...e){super(...e),this._domains={},this.navigateToResult=!1,this._deviceUpdate={},this._deviceEntities=(0,r.A)(((e,t,i)=>t.filter((t=>t.device_id===e&&(!i||(0,c.m)(t.entity_id)===i)))))}}(0,a.__decorate)([(0,s.MZ)({attribute:!1})],x.prototype,"flowConfig",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],x.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],x.prototype,"step",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],x.prototype,"devices",void 0),(0,a.__decorate)([(0,s.wk)()],x.prototype,"_deviceUpdate",void 0),x=(0,a.__decorate)([(0,s.EM)("step-flow-create-entry")],x),t()}catch(x){t(x)}}))},12083:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(62826),o=i(96196),s=i(77845),r=i(97854),n=i(89473),l=e([n]);n=(l.then?(await l)():l)[0];class c extends o.WF{render(){const e=this.hass.localize;return o.qy`
      <div class="content">
        ${this.flowConfig.renderExternalStepDescription(this.hass,this.step)}
        <div class="open-button">
          <ha-button href=${this.step.url} target="_blank" rel="noreferrer">
            ${e("ui.panel.config.integrations.config_flow.external_step.open_site")}
          </ha-button>
        </div>
      </div>
    `}firstUpdated(e){super.firstUpdated(e),window.open(this.step.url)}static get styles(){return[r.G,o.AH`
        .open-button {
          text-align: center;
          padding: 24px 0;
        }
        .open-button a {
          text-decoration: none;
        }
      `]}}(0,a.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"flowConfig",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"step",void 0),c=(0,a.__decorate)([(0,s.EM)("step-flow-external")],c),t()}catch(c){t(c)}}))},84398:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(62826),o=i(96196),s=i(77845),r=i(22786),n=i(51757),l=i(92542),c=i(45817),d=i(89473),h=(i(17963),i(23442)),p=(i(91120),i(28089),i(89600)),u=i(54193),_=i(73103),g=i(39396),m=i(97854),f=e([d,p]);[d,p]=f.then?(await f)():f;class v extends o.WF{disconnectedCallback(){super.disconnectedCallback(),this.removeEventListener("keydown",this._handleKeyDown)}render(){const e=this.step,t=this._stepDataProcessed;return o.qy`
      <div class="content" @click=${this._clickHandler}>
        ${this.flowConfig.renderShowFormStepDescription(this.hass,this.step)}
        ${this._errorMsg?o.qy`<ha-alert alert-type="error">${this._errorMsg}</ha-alert>`:""}
        <ha-form
          .hass=${this.hass}
          .narrow=${this.narrow}
          .data=${t}
          .disabled=${this._loading}
          @value-changed=${this._stepDataChanged}
          .schema=${(0,u.Hg)(this.handleReadOnlyFields(e.data_schema))}
          .error=${this._errors}
          .computeLabel=${this._labelCallback}
          .computeHelper=${this._helperCallback}
          .computeError=${this._errorCallback}
          .localizeValue=${this._localizeValueCallback}
        ></ha-form>
      </div>
      ${e.preview?o.qy`<div class="preview" @set-flow-errors=${this._setError}>
            <h3>
              ${this.hass.localize("ui.panel.config.integrations.config_flow.preview")}:
            </h3>
            ${(0,n._)(`flow-preview-${(0,_.F)(e.preview)}`,{hass:this.hass,domain:e.preview,flowType:this.flowConfig.flowType,handler:e.handler,stepId:e.step_id,flowId:e.flow_id,stepData:t})}
          </div>`:o.s6}
      <div class="buttons">
        <ha-button @click=${this._submitStep} .loading=${this._loading}>
          ${this.flowConfig.renderShowFormStepSubmitButton(this.hass,this.step)}
        </ha-button>
      </div>
    `}_setError(e){this._previewErrors=e.detail}firstUpdated(e){super.firstUpdated(e),setTimeout((()=>this.shadowRoot.querySelector("ha-form").focus()),0),this.addEventListener("keydown",this._handleKeyDown)}willUpdate(e){super.willUpdate(e),e.has("step")&&this.step?.preview&&i(25115)(`./flow-preview-${(0,_.F)(this.step.preview)}`),(e.has("step")||e.has("_previewErrors")||e.has("_submitErrors"))&&(this._errors=this.step.errors||this._previewErrors||this._submitErrors?{...this.step.errors,...this._previewErrors,...this._submitErrors}:void 0)}_clickHandler(e){(0,c.d)(e,!1)&&(0,l.r)(this,"flow-update",{step:void 0})}get _stepDataProcessed(){return void 0!==this._stepData||(this._stepData=(0,h.$)(this.step.data_schema)),this._stepData}async _submitStep(){const e=this._stepData||{},t=(e,i)=>e.every((e=>(!e.required||!["",void 0].includes(i[e.name]))&&("expandable"!==e.type||!e.required&&void 0===i[e.name]||t(e.schema,i[e.name]))));if(!(void 0===e?void 0===this.step.data_schema.find((e=>e.required)):t(this.step.data_schema,e)))return void(this._errorMsg=this.hass.localize("ui.panel.config.integrations.config_flow.not_all_required_fields"));this._loading=!0,this._errorMsg=void 0,this._submitErrors=void 0;const i=this.step.flow_id,a={};Object.keys(e).forEach((t=>{const i=e[t],o=[void 0,""].includes(i),s=this.step.data_schema?.find((e=>e.name===t)),r=s?.selector??{},n=Object.values(r)[0]?.read_only;o||n||(a[t]=i)}));try{const e=await this.flowConfig.handleFlowStep(this.hass,this.step.flow_id,a);if(!this.step||i!==this.step.flow_id)return;this._previewErrors=void 0,(0,l.r)(this,"flow-update",{step:e})}catch(o){o&&o.body?(o.body.message&&(this._errorMsg=o.body.message),o.body.errors&&(this._submitErrors=o.body.errors),o.body.message||o.body.errors||(this._errorMsg="Unknown error occurred")):this._errorMsg="Unknown error occurred"}finally{this._loading=!1}}_stepDataChanged(e){this._stepData=e.detail.value}static get styles(){return[g.RF,m.G,o.AH`
        .error {
          color: red;
        }

        ha-alert,
        ha-form {
          margin-top: 24px;
          display: block;
        }

        .buttons {
          padding: 16px;
        }
      `]}constructor(...e){super(...e),this.narrow=!1,this._loading=!1,this.handleReadOnlyFields=(0,r.A)((e=>e?.map((e=>({...e,...Object.values(e?.selector??{})[0]?.read_only?{disabled:!0}:{}}))))),this._handleKeyDown=e=>{"Enter"===e.key&&this._submitStep()},this._labelCallback=(e,t,i)=>this.flowConfig.renderShowFormStepFieldLabel(this.hass,this.step,e,i),this._helperCallback=(e,t)=>this.flowConfig.renderShowFormStepFieldHelper(this.hass,this.step,e,t),this._errorCallback=e=>this.flowConfig.renderShowFormStepFieldError(this.hass,this.step,e),this._localizeValueCallback=e=>this.flowConfig.renderShowFormStepFieldLocalizeValue(this.hass,this.step,e)}}(0,a.__decorate)([(0,s.MZ)({attribute:!1})],v.prototype,"flowConfig",void 0),(0,a.__decorate)([(0,s.MZ)({type:Boolean})],v.prototype,"narrow",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],v.prototype,"step",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],v.prototype,"hass",void 0),(0,a.__decorate)([(0,s.wk)()],v.prototype,"_loading",void 0),(0,a.__decorate)([(0,s.wk)()],v.prototype,"_stepData",void 0),(0,a.__decorate)([(0,s.wk)()],v.prototype,"_previewErrors",void 0),(0,a.__decorate)([(0,s.wk)()],v.prototype,"_submitErrors",void 0),(0,a.__decorate)([(0,s.wk)()],v.prototype,"_errorMsg",void 0),v=(0,a.__decorate)([(0,s.EM)("step-flow-form")],v),t()}catch(v){t(v)}}))},19486:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(62826),o=i(96196),s=i(77845),r=i(89600),n=e([r]);r=(n.then?(await n)():n)[0];class l extends o.WF{render(){const e=this.flowConfig.renderLoadingDescription(this.hass,this.loadingReason,this.handler,this.step);return o.qy`
      <div class="content">
        <ha-spinner size="large"></ha-spinner>
        ${e?o.qy`<div>${e}</div>`:""}
      </div>
    `}}l.styles=o.AH`
    .content {
      margin-top: 0;
      padding: 50px 100px;
      text-align: center;
    }
    ha-spinner {
      margin-bottom: 16px;
    }
  `,(0,a.__decorate)([(0,s.MZ)({attribute:!1})],l.prototype,"flowConfig",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],l.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],l.prototype,"loadingReason",void 0),(0,a.__decorate)([(0,s.MZ)()],l.prototype,"handler",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],l.prototype,"step",void 0),l=(0,a.__decorate)([(0,s.EM)("step-flow-loading")],l),t()}catch(l){t(l)}}))},59395:function(e,t,i){var a=i(62826),o=i(96196),s=i(77845),r=i(92542),n=(i(28608),i(56565),i(97854)),l=i(25749);class c extends o.WF{shouldUpdate(e){return e.size>1||!e.has("hass")||this.hass.localize!==e.get("hass")?.localize}render(){let e,t,i={};if(Array.isArray(this.step.menu_options)){e=this.step.menu_options,t={};for(const a of e)t[a]=this.flowConfig.renderMenuOption(this.hass,this.step,a),i[a]=this.flowConfig.renderMenuOptionDescription(this.hass,this.step,a)}else e=Object.keys(this.step.menu_options),t=this.step.menu_options,i=Object.fromEntries(e.map((e=>[e,this.flowConfig.renderMenuOptionDescription(this.hass,this.step,e)])));this.step.sort&&(e=e.sort(((e,i)=>(0,l.xL)(t[e],t[i],this.hass.locale.language))));const a=this.flowConfig.renderMenuDescription(this.hass,this.step);return o.qy`
      ${a?o.qy`<div class="content">${a}</div>`:""}
      <div class="options">
        ${e.map((e=>o.qy`
            <ha-list-item
              hasMeta
              .step=${e}
              @click=${this._handleStep}
              ?twoline=${i[e]}
              ?multiline-secondary=${i[e]}
            >
              <span>${t[e]}</span>
              ${i[e]?o.qy`<span slot="secondary">
                    ${i[e]}
                  </span>`:o.s6}
              <ha-icon-next slot="meta"></ha-icon-next>
            </ha-list-item>
          `))}
      </div>
    `}_handleStep(e){(0,r.r)(this,"flow-update",{stepPromise:this.flowConfig.handleFlowStep(this.hass,this.step.flow_id,{next_step_id:e.currentTarget.step})})}}c.styles=[n.G,o.AH`
      .options {
        margin-top: 20px;
        margin-bottom: 16px;
      }
      .content {
        padding-bottom: 16px;
      }
      .content + .options {
        margin-top: 8px;
      }
      ha-list-item {
        --mdc-list-side-padding: 24px;
      }
    `],(0,a.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"flowConfig",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],c.prototype,"step",void 0),c=(0,a.__decorate)([(0,s.EM)("step-flow-menu")],c)},12527:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(62826),o=i(96196),s=i(77845),r=i(48565),n=i(64109),l=i(89600),c=i(97854),d=e([n,l]);[n,l]=d.then?(await d)():d;class h extends o.WF{render(){return o.qy`
      <div class="content">
        ${this.progress?o.qy`
              <ha-progress-ring .value=${this.progress} size="large"
                >${this.progress}${(0,r.d)(this.hass.locale)}%</ha-progress-ring
              >
            `:o.qy`<ha-spinner size="large"></ha-spinner>`}
        ${this.flowConfig.renderShowFormProgressDescription(this.hass,this.step)}
      </div>
    `}static get styles(){return[c.G,o.AH`
        .content {
          margin-top: 0;
          padding: 50px 100px;
          text-align: center;
        }
        ha-spinner {
          margin-bottom: 16px;
        }
      `]}}(0,a.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"flowConfig",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"hass",void 0),(0,a.__decorate)([(0,s.MZ)({attribute:!1})],h.prototype,"step",void 0),(0,a.__decorate)([(0,s.MZ)({type:Number})],h.prototype,"progress",void 0),h=(0,a.__decorate)([(0,s.EM)("step-flow-progress")],h),t()}catch(h){t(h)}}))},97854:function(e,t,i){i.d(t,{G:()=>a});const a=i(96196).AH`
  h2 {
    margin: 24px 38px 0 0;
    margin-inline-start: 0px;
    margin-inline-end: 38px;
    padding: 0 24px;
    padding-inline-start: 24px;
    padding-inline-end: 24px;
    -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
    -webkit-font-smoothing: var(--ha-font-smoothing);
    font-family: var(
      --mdc-typography-headline6-font-family,
      var(--mdc-typography-font-family, var(--ha-font-family-body))
    );
    font-size: var(--mdc-typography-headline6-font-size, var(--ha-font-size-l));
    line-height: var(--mdc-typography-headline6-line-height, 2rem);
    font-weight: var(
      --mdc-typography-headline6-font-weight,
      var(--ha-font-weight-medium)
    );
    letter-spacing: var(--mdc-typography-headline6-letter-spacing, 0.0125em);
    text-decoration: var(--mdc-typography-headline6-text-decoration, inherit);
    text-transform: var(--mdc-typography-headline6-text-transform, inherit);
    box-sizing: border-box;
  }

  .content,
  .preview {
    margin-top: 20px;
    padding: 0 24px;
  }

  .buttons {
    position: relative;
    padding: 16px;
    margin: 8px 0 0;
    color: var(--primary-color);
    display: flex;
    justify-content: flex-end;
  }

  ha-markdown {
    overflow-wrap: break-word;
  }
  ha-markdown a {
    color: var(--primary-color);
  }
  ha-markdown img:first-child:last-child {
    display: block;
    margin: 0 auto;
  }
`},6358:function(e,t,i){i.d(t,{L:()=>s});var a=i(92542);const o=()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("2016"),i.e("1279"),i.e("3806"),i.e("661"),i.e("4398"),i.e("5633"),i.e("1283"),i.e("2097")]).then(i.bind(i,54728)),s=(e,t)=>{(0,a.r)(e,"show-dialog",{dialogTag:"ha-voice-assistant-setup-dialog",dialogImport:o,dialogParams:t})}},78778:function(e,t,i){i.d(t,{a:()=>s});var a=i(92542);const o=()=>Promise.all([i.e("8654"),i.e("4556"),i.e("8451")]).then(i.bind(i,71614)),s=(e,t)=>{(0,a.r)(e,"show-dialog",{dialogTag:"dialog-add-application-credential",dialogImport:o,dialogParams:t})}},76681:function(e,t,i){i.d(t,{MR:()=>a,a_:()=>o,bg:()=>s});const a=e=>`https://brands.home-assistant.io/${e.brand?"brands/":""}${e.useFallback?"_/":""}${e.domain}/${e.darkOptimized?"dark_":""}${e.type}.png`,o=e=>e.split("/")[4],s=e=>e.startsWith("https://brands.home-assistant.io/")},62001:function(e,t,i){i.d(t,{o:()=>a});const a=(e,t)=>`https://${e.config.version.includes("b")?"rc":e.config.version.includes("dev")?"next":"www"}.home-assistant.io${t}`},2355:function(e,t,i){i.d(t,{A:()=>a});const a=i(96196).AH`:host {
  --size: 8rem;
  --track-width: 0.25em;
  --track-color: var(--wa-color-neutral-fill-normal);
  --indicator-width: var(--track-width);
  --indicator-color: var(--wa-color-brand-fill-loud);
  --indicator-transition-duration: 0.35s;
  display: inline-flex;
}
.progress-ring {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.image {
  width: var(--size);
  height: var(--size);
  rotate: -90deg;
  transform-origin: 50% 50%;
}
.track,
.indicator {
  --radius: calc(var(--size) / 2 - max(var(--track-width), var(--indicator-width)) * 0.5);
  --circumference: calc(var(--radius) * 2 * 3.141592654);
  fill: none;
  r: var(--radius);
  cx: calc(var(--size) / 2);
  cy: calc(var(--size) / 2);
}
.track {
  stroke: var(--track-color);
  stroke-width: var(--track-width);
}
.indicator {
  stroke: var(--indicator-color);
  stroke-width: var(--indicator-width);
  stroke-linecap: round;
  transition-property: stroke-dashoffset;
  transition-duration: var(--indicator-transition-duration);
  stroke-dasharray: var(--circumference) var(--circumference);
  stroke-dashoffset: calc(var(--circumference) - var(--percentage) * var(--circumference));
}
.label {
  display: flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  text-align: center;
  user-select: none;
  -webkit-user-select: none;
}
`},65686:function(e,t,i){i.a(e,(async function(e,a){try{i.d(t,{A:()=>u});var o=i(96196),s=i(77845),r=i(32510),n=i(17060),l=i(2355),c=e([n]);n=(c.then?(await c)():c)[0];var d=Object.defineProperty,h=Object.getOwnPropertyDescriptor,p=(e,t,i,a)=>{for(var o,s=a>1?void 0:a?h(t,i):t,r=e.length-1;r>=0;r--)(o=e[r])&&(s=(a?o(t,i,s):o(s))||s);return a&&s&&d(t,i,s),s};let u=class extends r.A{updated(e){if(super.updated(e),e.has("value")){const e=parseFloat(getComputedStyle(this.indicator).getPropertyValue("r")),t=2*Math.PI*e,i=t-this.value/100*t;this.indicatorOffset=`${i}px`}}render(){return o.qy`
      <div
        part="base"
        class="progress-ring"
        role="progressbar"
        aria-label=${this.label.length>0?this.label:this.localize.term("progress")}
        aria-describedby="label"
        aria-valuemin="0"
        aria-valuemax="100"
        aria-valuenow="${this.value}"
        style="--percentage: ${this.value/100}"
      >
        <svg class="image">
          <circle class="track"></circle>
          <circle class="indicator" style="stroke-dashoffset: ${this.indicatorOffset}"></circle>
        </svg>

        <slot id="label" part="label" class="label"></slot>
      </div>
    `}constructor(){super(...arguments),this.localize=new n.c(this),this.value=0,this.label=""}};u.css=l.A,p([(0,s.P)(".indicator")],u.prototype,"indicator",2),p([(0,s.wk)()],u.prototype,"indicatorOffset",2),p([(0,s.MZ)({type:Number,reflect:!0})],u.prototype,"value",2),p([(0,s.MZ)()],u.prototype,"label",2),u=p([(0,s.EM)("wa-progress-ring")],u),a()}catch(u){a(u)}}))}};
//# sourceMappingURL=7394.e8691b5ab907236b.js.map