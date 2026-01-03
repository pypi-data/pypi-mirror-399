export const __webpack_id__="3428";export const __webpack_ids__=["3428"];export const __webpack_modules__={55124:function(e,t,o){o.d(t,{d:()=>i});const i=e=>e.stopPropagation()},87400:function(e,t,o){o.d(t,{l:()=>i});const i=(e,t,o,i,a)=>{const s=t[e.entity_id];return s?r(s,t,o,i,a):{entity:null,device:null,area:null,floor:null}},r=(e,t,o,i,r)=>{const a=t[e.entity_id],s=e?.device_id,l=s?o[s]:void 0,n=e?.area_id||l?.area_id,d=n?i[n]:void 0,h=d?.floor_id;return{entity:a,device:l||null,area:d||null,floor:(h?r[h]:void 0)||null}}},48565:function(e,t,o){o.d(t,{d:()=>i});const i=e=>{switch(e.language){case"cs":case"de":case"fi":case"fr":case"sk":case"sv":return" ";default:return""}}},80772:function(e,t,o){o.d(t,{A:()=>r});var i=o(48565);const r=(e,t)=>"°"===e?"":t&&"%"===e?(0,i.d)(t):" "},38852:function(e,t,o){o.d(t,{b:()=>i});const i=(e,t)=>{if(e===t)return!0;if(e&&t&&"object"==typeof e&&"object"==typeof t){if(e.constructor!==t.constructor)return!1;let o,r;if(Array.isArray(e)){if(r=e.length,r!==t.length)return!1;for(o=r;0!=o--;)if(!i(e[o],t[o]))return!1;return!0}if(e instanceof Map&&t instanceof Map){if(e.size!==t.size)return!1;for(o of e.entries())if(!t.has(o[0]))return!1;for(o of e.entries())if(!i(o[1],t.get(o[0])))return!1;return!0}if(e instanceof Set&&t instanceof Set){if(e.size!==t.size)return!1;for(o of e.entries())if(!t.has(o[0]))return!1;return!0}if(ArrayBuffer.isView(e)&&ArrayBuffer.isView(t)){if(r=e.length,r!==t.length)return!1;for(o=r;0!=o--;)if(e[o]!==t[o])return!1;return!0}if(e.constructor===RegExp)return e.source===t.source&&e.flags===t.flags;if(e.valueOf!==Object.prototype.valueOf)return e.valueOf()===t.valueOf();if(e.toString!==Object.prototype.toString)return e.toString()===t.toString();const a=Object.keys(e);if(r=a.length,r!==Object.keys(t).length)return!1;for(o=r;0!=o--;)if(!Object.prototype.hasOwnProperty.call(t,a[o]))return!1;for(o=r;0!=o--;){const r=a[o];if(!i(e[r],t[r]))return!1}return!0}return e!=e&&t!=t}},22606:function(e,t,o){o.a(e,(async function(e,i){try{o.r(t),o.d(t,{HaObjectSelector:()=>f});var r=o(62826),a=o(96196),s=o(77845),l=o(22786),n=o(55376),d=o(92542),h=o(25098),c=o(64718),p=(o(56768),o(42921),o(23897),o(63801),o(23362)),u=o(38852),m=e([p]);p=(m.then?(await m)():m)[0];const b="M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",y="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z",v="M21 11H3V9H21V11M21 13H3V15H21V13Z",_="M20.71,7.04C21.1,6.65 21.1,6 20.71,5.63L18.37,3.29C18,2.9 17.35,2.9 16.96,3.29L15.12,5.12L18.87,8.87M3,17.25V21H6.75L17.81,9.93L14.06,6.18L3,17.25Z";class f extends a.WF{_renderItem(e,t){const o=this.selector.object.label_field||Object.keys(this.selector.object.fields)[0],i=this.selector.object.fields[o].selector,r=i?(0,h.C)(this.hass,e[o],i):"";let s="";const l=this.selector.object.description_field;if(l){const t=this.selector.object.fields[l].selector;s=t?(0,h.C)(this.hass,e[l],t):""}const n=this.selector.object.multiple||!1,d=this.selector.object.multiple||!1;return a.qy`
      <ha-md-list-item class="item">
        ${n?a.qy`
              <ha-svg-icon
                class="handle"
                .path=${v}
                slot="start"
              ></ha-svg-icon>
            `:a.s6}
        <div slot="headline" class="label">${r}</div>
        ${s?a.qy`<div slot="supporting-text" class="description">
              ${s}
            </div>`:a.s6}
        <ha-icon-button
          slot="end"
          .item=${e}
          .index=${t}
          .label=${this.hass.localize("ui.common.edit")}
          .path=${_}
          @click=${this._editItem}
        ></ha-icon-button>
        <ha-icon-button
          slot="end"
          .index=${t}
          .label=${this.hass.localize("ui.common.delete")}
          .path=${d?y:b}
          @click=${this._deleteItem}
        ></ha-icon-button>
      </ha-md-list-item>
    `}render(){if(this.selector.object?.fields){if(this.selector.object.multiple){const e=(0,n.e)(this.value??[]);return a.qy`
          ${this.label?a.qy`<label>${this.label}</label>`:a.s6}
          <div class="items-container">
            <ha-sortable
              handle-selector=".handle"
              draggable-selector=".item"
              @item-moved=${this._itemMoved}
            >
              <ha-md-list>
                ${e.map(((e,t)=>this._renderItem(e,t)))}
              </ha-md-list>
            </ha-sortable>
            <ha-button appearance="filled" @click=${this._addItem}>
              ${this.hass.localize("ui.common.add")}
            </ha-button>
          </div>
        `}return a.qy`
        ${this.label?a.qy`<label>${this.label}</label>`:a.s6}
        <div class="items-container">
          ${this.value?a.qy`<ha-md-list>
                ${this._renderItem(this.value,0)}
              </ha-md-list>`:a.qy`
                <ha-button appearance="filled" @click=${this._addItem}>
                  ${this.hass.localize("ui.common.add")}
                </ha-button>
              `}
        </div>
      `}return a.qy`<ha-yaml-editor
        .hass=${this.hass}
        .readonly=${this.disabled}
        .label=${this.label}
        .required=${this.required}
        .placeholder=${this.placeholder}
        .defaultValue=${this.value}
        @value-changed=${this._handleChange}
      ></ha-yaml-editor>
      ${this.helper?a.qy`<ha-input-helper-text .disabled=${this.disabled}
            >${this.helper}</ha-input-helper-text
          >`:""} `}_itemMoved(e){e.stopPropagation();const t=e.detail.newIndex,o=e.detail.oldIndex;if(!this.selector.object.multiple)return;const i=(0,n.e)(this.value??[]).concat(),r=i.splice(o,1)[0];i.splice(t,0,r),(0,d.r)(this,"value-changed",{value:i})}async _addItem(e){e.stopPropagation();const t=await(0,c.O)(this,{title:this.hass.localize("ui.common.add"),schema:this._schema(this.selector),data:{},computeLabel:this._computeLabel,computeHelper:this._computeHelper,submitText:this.hass.localize("ui.common.add")});if(null===t)return;if(!this.selector.object.multiple)return void(0,d.r)(this,"value-changed",{value:t});const o=(0,n.e)(this.value??[]).concat();o.push(t),(0,d.r)(this,"value-changed",{value:o})}async _editItem(e){e.stopPropagation();const t=e.currentTarget.item,o=e.currentTarget.index,i=await(0,c.O)(this,{title:this.hass.localize("ui.common.edit"),schema:this._schema(this.selector),data:t,computeLabel:this._computeLabel,submitText:this.hass.localize("ui.common.save")});if(null===i)return;if(!this.selector.object.multiple)return void(0,d.r)(this,"value-changed",{value:i});const r=(0,n.e)(this.value??[]).concat();r[o]=i,(0,d.r)(this,"value-changed",{value:r})}_deleteItem(e){e.stopPropagation();const t=e.currentTarget.index;if(!this.selector.object.multiple)return void(0,d.r)(this,"value-changed",{value:void 0});const o=(0,n.e)(this.value??[]).concat();o.splice(t,1),(0,d.r)(this,"value-changed",{value:o})}updated(e){super.updated(e),e.has("value")&&!this._valueChangedFromChild&&this._yamlEditor&&!(0,u.b)(this.value,e.get("value"))&&this._yamlEditor.setValue(this.value),this._valueChangedFromChild=!1}_handleChange(e){e.stopPropagation(),this._valueChangedFromChild=!0;const t=e.target.value;e.target.isValid&&this.value!==t&&(0,d.r)(this,"value-changed",{value:t})}static get styles(){return[a.AH`
        ha-md-list {
          gap: var(--ha-space-2);
        }
        ha-md-list-item {
          border: 1px solid var(--divider-color);
          border-radius: var(--ha-border-radius-md);
          --ha-md-list-item-gap: 0;
          --md-list-item-top-space: 0;
          --md-list-item-bottom-space: 0;
          --md-list-item-leading-space: 12px;
          --md-list-item-trailing-space: 4px;
          --md-list-item-two-line-container-height: 48px;
          --md-list-item-one-line-container-height: 48px;
        }
        .handle {
          cursor: move;
          padding: 8px;
          margin-inline-start: -8px;
        }
        label {
          margin-bottom: 8px;
          display: block;
        }
        ha-md-list-item .label,
        ha-md-list-item .description {
          text-overflow: ellipsis;
          overflow: hidden;
          white-space: nowrap;
        }
      `]}constructor(...e){super(...e),this.disabled=!1,this.required=!0,this._valueChangedFromChild=!1,this._computeLabel=e=>{const t=this.selector.object?.translation_key;if(this.localizeValue&&t){const o=this.localizeValue(`${t}.fields.${e.name}.name`)||this.localizeValue(`${t}.fields.${e.name}`);if(o)return o}return this.selector.object?.fields?.[e.name]?.label||e.name},this._computeHelper=e=>{const t=this.selector.object?.translation_key;if(this.localizeValue&&t){const o=this.localizeValue(`${t}.fields.${e.name}.description`);if(o)return o}return this.selector.object?.fields?.[e.name]?.description||""},this._schema=(0,l.A)((e=>e.object&&e.object.fields?Object.entries(e.object.fields).map((([e,t])=>({name:e,selector:t.selector,required:t.required??!1}))):[]))}}(0,r.__decorate)([(0,s.MZ)({attribute:!1})],f.prototype,"hass",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],f.prototype,"selector",void 0),(0,r.__decorate)([(0,s.MZ)()],f.prototype,"value",void 0),(0,r.__decorate)([(0,s.MZ)()],f.prototype,"label",void 0),(0,r.__decorate)([(0,s.MZ)()],f.prototype,"helper",void 0),(0,r.__decorate)([(0,s.MZ)()],f.prototype,"placeholder",void 0),(0,r.__decorate)([(0,s.MZ)({type:Boolean})],f.prototype,"disabled",void 0),(0,r.__decorate)([(0,s.MZ)({type:Boolean})],f.prototype,"required",void 0),(0,r.__decorate)([(0,s.MZ)({attribute:!1})],f.prototype,"localizeValue",void 0),(0,r.__decorate)([(0,s.P)("ha-yaml-editor",!0)],f.prototype,"_yamlEditor",void 0),f=(0,r.__decorate)([(0,s.EM)("ha-selector-object")],f),i()}catch(b){i(b)}}))},63801:function(e,t,o){var i=o(62826),r=o(96196),a=o(77845),s=o(92542);class l extends r.WF{updated(e){e.has("disabled")&&(this.disabled?this._destroySortable():this._createSortable())}disconnectedCallback(){super.disconnectedCallback(),this._shouldBeDestroy=!0,setTimeout((()=>{this._shouldBeDestroy&&(this._destroySortable(),this._shouldBeDestroy=!1)}),1)}connectedCallback(){super.connectedCallback(),this._shouldBeDestroy=!1,this.hasUpdated&&!this.disabled&&this._createSortable()}createRenderRoot(){return this}render(){return this.noStyle?r.s6:r.qy`
      <style>
        .sortable-fallback {
          display: none !important;
        }

        .sortable-ghost {
          box-shadow: 0 0 0 2px var(--primary-color);
          background: rgba(var(--rgb-primary-color), 0.25);
          border-radius: var(--ha-border-radius-sm);
          opacity: 0.4;
        }

        .sortable-drag {
          border-radius: var(--ha-border-radius-sm);
          opacity: 1;
          background: var(--card-background-color);
          box-shadow: 0px 4px 8px 3px #00000026;
          cursor: grabbing;
        }
      </style>
    `}async _createSortable(){if(this._sortable)return;const e=this.children[0];if(!e)return;const t=(await Promise.all([o.e("5283"),o.e("1387")]).then(o.bind(o,38214))).default,i={scroll:!0,forceAutoScrollFallback:!0,scrollSpeed:20,animation:150,...this.options,onChoose:this._handleChoose,onStart:this._handleStart,onEnd:this._handleEnd,onUpdate:this._handleUpdate,onAdd:this._handleAdd,onRemove:this._handleRemove};this.draggableSelector&&(i.draggable=this.draggableSelector),this.handleSelector&&(i.handle=this.handleSelector),void 0!==this.invertSwap&&(i.invertSwap=this.invertSwap),this.group&&(i.group=this.group),this.filter&&(i.filter=this.filter),this._sortable=new t(e,i)}_destroySortable(){this._sortable&&(this._sortable.destroy(),this._sortable=void 0)}constructor(...e){super(...e),this.disabled=!1,this.noStyle=!1,this.invertSwap=!1,this.rollback=!0,this._shouldBeDestroy=!1,this._handleUpdate=e=>{(0,s.r)(this,"item-moved",{newIndex:e.newIndex,oldIndex:e.oldIndex})},this._handleAdd=e=>{(0,s.r)(this,"item-added",{index:e.newIndex,data:e.item.sortableData,item:e.item})},this._handleRemove=e=>{(0,s.r)(this,"item-removed",{index:e.oldIndex})},this._handleEnd=async e=>{(0,s.r)(this,"drag-end"),this.rollback&&e.item.placeholder&&(e.item.placeholder.replaceWith(e.item),delete e.item.placeholder)},this._handleStart=()=>{(0,s.r)(this,"drag-start")},this._handleChoose=e=>{this.rollback&&(e.item.placeholder=document.createComment("sort-placeholder"),e.item.after(e.item.placeholder))}}}(0,i.__decorate)([(0,a.MZ)({type:Boolean})],l.prototype,"disabled",void 0),(0,i.__decorate)([(0,a.MZ)({type:Boolean,attribute:"no-style"})],l.prototype,"noStyle",void 0),(0,i.__decorate)([(0,a.MZ)({type:String,attribute:"draggable-selector"})],l.prototype,"draggableSelector",void 0),(0,i.__decorate)([(0,a.MZ)({type:String,attribute:"handle-selector"})],l.prototype,"handleSelector",void 0),(0,i.__decorate)([(0,a.MZ)({type:String,attribute:"filter"})],l.prototype,"filter",void 0),(0,i.__decorate)([(0,a.MZ)({type:String})],l.prototype,"group",void 0),(0,i.__decorate)([(0,a.MZ)({type:Boolean,attribute:"invert-swap"})],l.prototype,"invertSwap",void 0),(0,i.__decorate)([(0,a.MZ)({attribute:!1})],l.prototype,"options",void 0),(0,i.__decorate)([(0,a.MZ)({type:Boolean})],l.prototype,"rollback",void 0),l=(0,i.__decorate)([(0,a.EM)("ha-sortable")],l)},88422:function(e,t,o){o.a(e,(async function(e,t){try{var i=o(62826),r=o(52630),a=o(96196),s=o(77845),l=e([r]);r=(l.then?(await l)():l)[0];class n extends r.A{static get styles(){return[r.A.styles,a.AH`
        :host {
          --wa-tooltip-background-color: var(--secondary-background-color);
          --wa-tooltip-content-color: var(--primary-text-color);
          --wa-tooltip-font-family: var(
            --ha-tooltip-font-family,
            var(--ha-font-family-body)
          );
          --wa-tooltip-font-size: var(
            --ha-tooltip-font-size,
            var(--ha-font-size-s)
          );
          --wa-tooltip-font-weight: var(
            --ha-tooltip-font-weight,
            var(--ha-font-weight-normal)
          );
          --wa-tooltip-line-height: var(
            --ha-tooltip-line-height,
            var(--ha-line-height-condensed)
          );
          --wa-tooltip-padding: 8px;
          --wa-tooltip-border-radius: var(
            --ha-tooltip-border-radius,
            var(--ha-border-radius-sm)
          );
          --wa-tooltip-arrow-size: var(--ha-tooltip-arrow-size, 8px);
          --wa-z-index-tooltip: var(--ha-tooltip-z-index, 1000);
        }
      `]}constructor(...e){super(...e),this.showDelay=150,this.hideDelay=150}}(0,i.__decorate)([(0,s.MZ)({attribute:"show-delay",type:Number})],n.prototype,"showDelay",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:"hide-delay",type:Number})],n.prototype,"hideDelay",void 0),n=(0,i.__decorate)([(0,s.EM)("ha-tooltip")],n),t()}catch(n){t(n)}}))},23362:function(e,t,o){o.a(e,(async function(e,t){try{var i=o(62826),r=o(53289),a=o(96196),s=o(77845),l=o(92542),n=o(4657),d=o(39396),h=o(4848),c=(o(17963),o(89473)),p=o(32884),u=e([c,p]);[c,p]=u.then?(await u)():u;const m=e=>{if("object"!=typeof e||null===e)return!1;for(const t in e)if(Object.prototype.hasOwnProperty.call(e,t))return!1;return!0};class b extends a.WF{setValue(e){try{this._yaml=m(e)?"":(0,r.Bh)(e,{schema:this.yamlSchema,quotingType:'"',noRefs:!0})}catch(t){console.error(t,e),alert(`There was an error converting to YAML: ${t}`)}}firstUpdated(){void 0!==this.defaultValue&&this.setValue(this.defaultValue)}willUpdate(e){super.willUpdate(e),this.autoUpdate&&e.has("value")&&this.setValue(this.value)}focus(){this._codeEditor?.codemirror&&this._codeEditor?.codemirror.focus()}render(){return void 0===this._yaml?a.s6:a.qy`
      ${this.label?a.qy`<p>${this.label}${this.required?" *":""}</p>`:a.s6}
      <ha-code-editor
        .hass=${this.hass}
        .value=${this._yaml}
        .readOnly=${this.readOnly}
        .disableFullscreen=${this.disableFullscreen}
        mode="yaml"
        autocomplete-entities
        autocomplete-icons
        .error=${!1===this.isValid}
        @value-changed=${this._onChange}
        @blur=${this._onBlur}
        dir="ltr"
      ></ha-code-editor>
      ${this._showingError?a.qy`<ha-alert alert-type="error">${this._error}</ha-alert>`:a.s6}
      ${this.copyClipboard||this.hasExtraActions?a.qy`
            <div class="card-actions">
              ${this.copyClipboard?a.qy`
                    <ha-button appearance="plain" @click=${this._copyYaml}>
                      ${this.hass.localize("ui.components.yaml-editor.copy_to_clipboard")}
                    </ha-button>
                  `:a.s6}
              <slot name="extra-actions"></slot>
            </div>
          `:a.s6}
    `}_onChange(e){let t;e.stopPropagation(),this._yaml=e.detail.value;let o,i=!0;if(this._yaml)try{t=(0,r.Hh)(this._yaml,{schema:this.yamlSchema})}catch(a){i=!1,o=`${this.hass.localize("ui.components.yaml-editor.error",{reason:a.reason})}${a.mark?` (${this.hass.localize("ui.components.yaml-editor.error_location",{line:a.mark.line+1,column:a.mark.column+1})})`:""}`}else t={};this._error=o??"",i&&(this._showingError=!1),this.value=t,this.isValid=i,(0,l.r)(this,"value-changed",{value:t,isValid:i,errorMsg:o})}_onBlur(){this.showErrors&&this._error&&(this._showingError=!0)}get yaml(){return this._yaml}async _copyYaml(){this.yaml&&(await(0,n.l)(this.yaml),(0,h.P)(this,{message:this.hass.localize("ui.common.copied_clipboard")}))}static get styles(){return[d.RF,a.AH`
        .card-actions {
          border-radius: var(
            --actions-border-radius,
            var(--ha-border-radius-square) var(--ha-border-radius-square)
              var(--ha-card-border-radius, var(--ha-border-radius-lg))
              var(--ha-card-border-radius, var(--ha-border-radius-lg))
          );
          border: 1px solid var(--divider-color);
          padding: 5px 16px;
        }
        ha-code-editor {
          flex-grow: 1;
          min-height: 0;
        }
      `]}constructor(...e){super(...e),this.yamlSchema=r.my,this.isValid=!0,this.autoUpdate=!1,this.readOnly=!1,this.disableFullscreen=!1,this.required=!1,this.copyClipboard=!1,this.hasExtraActions=!1,this.showErrors=!0,this._yaml="",this._error="",this._showingError=!1}}(0,i.__decorate)([(0,s.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,i.__decorate)([(0,s.MZ)()],b.prototype,"value",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:!1})],b.prototype,"yamlSchema",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:!1})],b.prototype,"defaultValue",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:"is-valid",type:Boolean})],b.prototype,"isValid",void 0),(0,i.__decorate)([(0,s.MZ)()],b.prototype,"label",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:"auto-update",type:Boolean})],b.prototype,"autoUpdate",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:"read-only",type:Boolean})],b.prototype,"readOnly",void 0),(0,i.__decorate)([(0,s.MZ)({type:Boolean,attribute:"disable-fullscreen"})],b.prototype,"disableFullscreen",void 0),(0,i.__decorate)([(0,s.MZ)({type:Boolean})],b.prototype,"required",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:"copy-clipboard",type:Boolean})],b.prototype,"copyClipboard",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:"has-extra-actions",type:Boolean})],b.prototype,"hasExtraActions",void 0),(0,i.__decorate)([(0,s.MZ)({attribute:"show-errors",type:Boolean})],b.prototype,"showErrors",void 0),(0,i.__decorate)([(0,s.wk)()],b.prototype,"_yaml",void 0),(0,i.__decorate)([(0,s.wk)()],b.prototype,"_error",void 0),(0,i.__decorate)([(0,s.wk)()],b.prototype,"_showingError",void 0),(0,i.__decorate)([(0,s.P)("ha-code-editor")],b.prototype,"_codeEditor",void 0),b=(0,i.__decorate)([(0,s.EM)("ha-yaml-editor")],b),t()}catch(m){t(m)}}))},25098:function(e,t,o){o.d(t,{C:()=>s});var i=o(55376),r=o(56403),a=o(80772);const s=(e,t,o)=>{if(null==t)return"";if(!o)return(0,i.e)(t).join(", ");if("text"in o){const{prefix:e,suffix:r}=o.text||{};return(0,i.e)(t).map((t=>`${e||""}${t}${r||""}`)).join(", ")}if("number"in o){const{unit_of_measurement:r}=o.number||{};return(0,i.e)(t).map((t=>{const o=Number(t);return isNaN(o)?t:r?`${o}${(0,a.A)(r,e.locale)}${r}`:o.toString()})).join(", ")}if("floor"in o){return(0,i.e)(t).map((t=>{const o=e.floors[t];return o&&o.name||t})).join(", ")}if("area"in o){return(0,i.e)(t).map((t=>{const o=e.areas[t];return o?(0,r.A)(o):t})).join(", ")}if("entity"in o){return(0,i.e)(t).map((t=>{const o=e.states[t];if(!o)return t;return e.formatEntityName(o,[{type:"device"},{type:"entity"}])||t})).join(", ")}if("device"in o){return(0,i.e)(t).map((t=>{const o=e.devices[t];return o&&o.name||t})).join(", ")}return(0,i.e)(t).join(", ")}},64718:function(e,t,o){o.d(t,{O:()=>r});var i=o(92542);const r=(e,t)=>new Promise((r=>{const a=t.cancel,s=t.submit;(0,i.r)(e,"show-dialog",{dialogTag:"dialog-form",dialogImport:()=>o.e("5919").then(o.bind(o,33506)),dialogParams:{...t,cancel:()=>{r(null),a&&a()},submit:e=>{r(e),s&&s(e)}}})}))},4848:function(e,t,o){o.d(t,{P:()=>r});var i=o(92542);const r=(e,t)=>(0,i.r)(e,"hass-notification",t)},61171:function(e,t,o){o.d(t,{A:()=>i});const i=o(96196).AH`:host {
  --max-width: 30ch;
  display: inline-block;
  position: absolute;
  color: var(--wa-tooltip-content-color);
  font-size: var(--wa-tooltip-font-size);
  line-height: var(--wa-tooltip-line-height);
  text-align: start;
  white-space: normal;
}
.tooltip {
  --arrow-size: var(--wa-tooltip-arrow-size);
  --arrow-color: var(--wa-tooltip-background-color);
}
.tooltip::part(popup) {
  z-index: 1000;
}
.tooltip[placement^=top]::part(popup) {
  transform-origin: bottom;
}
.tooltip[placement^=bottom]::part(popup) {
  transform-origin: top;
}
.tooltip[placement^=left]::part(popup) {
  transform-origin: right;
}
.tooltip[placement^=right]::part(popup) {
  transform-origin: left;
}
.body {
  display: block;
  width: max-content;
  max-width: var(--max-width);
  border-radius: var(--wa-tooltip-border-radius);
  background-color: var(--wa-tooltip-background-color);
  border: var(--wa-tooltip-border-width) var(--wa-tooltip-border-style) var(--wa-tooltip-border-color);
  padding: 0.25em 0.5em;
  user-select: none;
  -webkit-user-select: none;
}
.tooltip::part(arrow) {
  border-bottom: var(--wa-tooltip-border-width) var(--wa-tooltip-border-style) var(--wa-tooltip-border-color);
  border-right: var(--wa-tooltip-border-width) var(--wa-tooltip-border-style) var(--wa-tooltip-border-color);
}
`},52630:function(e,t,o){o.a(e,(async function(e,i){try{o.d(t,{A:()=>$});var r=o(96196),a=o(77845),s=o(94333),l=o(17051),n=o(42462),d=o(28438),h=o(98779),c=o(27259),p=o(984),u=o(53720),m=o(9395),b=o(32510),y=o(40158),v=o(61171),_=e([y]);y=(_.then?(await _)():_)[0];var f=Object.defineProperty,g=Object.getOwnPropertyDescriptor,w=(e,t,o,i)=>{for(var r,a=i>1?void 0:i?g(t,o):t,s=e.length-1;s>=0;s--)(r=e[s])&&(a=(i?r(t,o,a):r(a))||a);return i&&a&&f(t,o,a),a};let $=class extends b.A{connectedCallback(){super.connectedCallback(),this.eventController.signal.aborted&&(this.eventController=new AbortController),this.open&&(this.open=!1,this.updateComplete.then((()=>{this.open=!0}))),this.id||(this.id=(0,u.N)("wa-tooltip-")),this.for&&this.anchor?(this.anchor=null,this.handleForChange()):this.for&&this.handleForChange()}disconnectedCallback(){super.disconnectedCallback(),document.removeEventListener("keydown",this.handleDocumentKeyDown),this.eventController.abort(),this.anchor&&this.removeFromAriaLabelledBy(this.anchor,this.id)}firstUpdated(){this.body.hidden=!this.open,this.open&&(this.popup.active=!0,this.popup.reposition())}hasTrigger(e){return this.trigger.split(" ").includes(e)}addToAriaLabelledBy(e,t){const o=(e.getAttribute("aria-labelledby")||"").split(/\s+/).filter(Boolean);o.includes(t)||(o.push(t),e.setAttribute("aria-labelledby",o.join(" ")))}removeFromAriaLabelledBy(e,t){const o=(e.getAttribute("aria-labelledby")||"").split(/\s+/).filter(Boolean).filter((e=>e!==t));o.length>0?e.setAttribute("aria-labelledby",o.join(" ")):e.removeAttribute("aria-labelledby")}async handleOpenChange(){if(this.open){if(this.disabled)return;const e=new h.k;if(this.dispatchEvent(e),e.defaultPrevented)return void(this.open=!1);document.addEventListener("keydown",this.handleDocumentKeyDown,{signal:this.eventController.signal}),this.body.hidden=!1,this.popup.active=!0,await(0,c.Ud)(this.popup.popup,"show-with-scale"),this.popup.reposition(),this.dispatchEvent(new n.q)}else{const e=new d.L;if(this.dispatchEvent(e),e.defaultPrevented)return void(this.open=!1);document.removeEventListener("keydown",this.handleDocumentKeyDown),await(0,c.Ud)(this.popup.popup,"hide-with-scale"),this.popup.active=!1,this.body.hidden=!0,this.dispatchEvent(new l.Z)}}handleForChange(){const e=this.getRootNode();if(!e)return;const t=this.for?e.getElementById(this.for):null,o=this.anchor;if(t===o)return;const{signal:i}=this.eventController;t&&(this.addToAriaLabelledBy(t,this.id),t.addEventListener("blur",this.handleBlur,{capture:!0,signal:i}),t.addEventListener("focus",this.handleFocus,{capture:!0,signal:i}),t.addEventListener("click",this.handleClick,{signal:i}),t.addEventListener("mouseover",this.handleMouseOver,{signal:i}),t.addEventListener("mouseout",this.handleMouseOut,{signal:i})),o&&(this.removeFromAriaLabelledBy(o,this.id),o.removeEventListener("blur",this.handleBlur,{capture:!0}),o.removeEventListener("focus",this.handleFocus,{capture:!0}),o.removeEventListener("click",this.handleClick),o.removeEventListener("mouseover",this.handleMouseOver),o.removeEventListener("mouseout",this.handleMouseOut)),this.anchor=t}async handleOptionsChange(){this.hasUpdated&&(await this.updateComplete,this.popup.reposition())}handleDisabledChange(){this.disabled&&this.open&&this.hide()}async show(){if(!this.open)return this.open=!0,(0,p.l)(this,"wa-after-show")}async hide(){if(this.open)return this.open=!1,(0,p.l)(this,"wa-after-hide")}render(){return r.qy`
      <wa-popup
        part="base"
        exportparts="
          popup:base__popup,
          arrow:base__arrow
        "
        class=${(0,s.H)({tooltip:!0,"tooltip-open":this.open})}
        placement=${this.placement}
        distance=${this.distance}
        skidding=${this.skidding}
        flip
        shift
        ?arrow=${!this.withoutArrow}
        hover-bridge
        .anchor=${this.anchor}
      >
        <div part="body" class="body">
          <slot></slot>
        </div>
      </wa-popup>
    `}constructor(){super(...arguments),this.placement="top",this.disabled=!1,this.distance=8,this.open=!1,this.skidding=0,this.showDelay=150,this.hideDelay=0,this.trigger="hover focus",this.withoutArrow=!1,this.for=null,this.anchor=null,this.eventController=new AbortController,this.handleBlur=()=>{this.hasTrigger("focus")&&this.hide()},this.handleClick=()=>{this.hasTrigger("click")&&(this.open?this.hide():this.show())},this.handleFocus=()=>{this.hasTrigger("focus")&&this.show()},this.handleDocumentKeyDown=e=>{"Escape"===e.key&&(e.stopPropagation(),this.hide())},this.handleMouseOver=()=>{this.hasTrigger("hover")&&(clearTimeout(this.hoverTimeout),this.hoverTimeout=window.setTimeout((()=>this.show()),this.showDelay))},this.handleMouseOut=()=>{this.hasTrigger("hover")&&(clearTimeout(this.hoverTimeout),this.hoverTimeout=window.setTimeout((()=>this.hide()),this.hideDelay))}}};$.css=v.A,$.dependencies={"wa-popup":y.A},w([(0,a.P)("slot:not([name])")],$.prototype,"defaultSlot",2),w([(0,a.P)(".body")],$.prototype,"body",2),w([(0,a.P)("wa-popup")],$.prototype,"popup",2),w([(0,a.MZ)()],$.prototype,"placement",2),w([(0,a.MZ)({type:Boolean,reflect:!0})],$.prototype,"disabled",2),w([(0,a.MZ)({type:Number})],$.prototype,"distance",2),w([(0,a.MZ)({type:Boolean,reflect:!0})],$.prototype,"open",2),w([(0,a.MZ)({type:Number})],$.prototype,"skidding",2),w([(0,a.MZ)({attribute:"show-delay",type:Number})],$.prototype,"showDelay",2),w([(0,a.MZ)({attribute:"hide-delay",type:Number})],$.prototype,"hideDelay",2),w([(0,a.MZ)()],$.prototype,"trigger",2),w([(0,a.MZ)({attribute:"without-arrow",type:Boolean,reflect:!0})],$.prototype,"withoutArrow",2),w([(0,a.MZ)()],$.prototype,"for",2),w([(0,a.wk)()],$.prototype,"anchor",2),w([(0,m.w)("open",{waitUntilFirstUpdate:!0})],$.prototype,"handleOpenChange",1),w([(0,m.w)("for")],$.prototype,"handleForChange",1),w([(0,m.w)(["distance","placement","skidding"])],$.prototype,"handleOptionsChange",1),w([(0,m.w)("disabled")],$.prototype,"handleDisabledChange",1),$=w([(0,a.EM)("wa-tooltip")],$),i()}catch($){i($)}}))}};
//# sourceMappingURL=3428.9e60722dcb46f19a.js.map