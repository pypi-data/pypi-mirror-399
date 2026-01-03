/*! For license information please see 8651.515cd1e9923cbfa7.js.LICENSE.txt */
export const __webpack_id__="8651";export const __webpack_ids__=["8651"];export const __webpack_modules__={32637:function(e,t,i){i.a(e,(async function(e,t){try{var s=i(62826),r=i(96196),o=i(77845),a=i(22786),n=i(92542),d=i(45996),l=(i(63801),i(82965)),c=e([l]);l=(c.then?(await c)():c)[0];const h="M21 11H3V9H21V11M21 13H3V15H21V13Z";class u extends r.WF{render(){if(!this.hass)return r.s6;const e=this._currentEntities;return r.qy`
      ${this.label?r.qy`<label>${this.label}</label>`:r.s6}
      <ha-sortable
        .disabled=${!this.reorder||this.disabled}
        handle-selector=".entity-handle"
        @item-moved=${this._entityMoved}
      >
        <div class="list">
          ${e.map((e=>r.qy`
              <div class="entity">
                <ha-entity-picker
                  allow-custom-entity
                  .curValue=${e}
                  .hass=${this.hass}
                  .includeDomains=${this.includeDomains}
                  .excludeDomains=${this.excludeDomains}
                  .includeEntities=${this.includeEntities}
                  .excludeEntities=${this.excludeEntities}
                  .includeDeviceClasses=${this.includeDeviceClasses}
                  .includeUnitOfMeasurement=${this.includeUnitOfMeasurement}
                  .entityFilter=${this.entityFilter}
                  .value=${e}
                  .disabled=${this.disabled}
                  .createDomains=${this.createDomains}
                  @value-changed=${this._entityChanged}
                ></ha-entity-picker>
                ${this.reorder?r.qy`
                      <ha-svg-icon
                        class="entity-handle"
                        .path=${h}
                      ></ha-svg-icon>
                    `:r.s6}
              </div>
            `))}
        </div>
      </ha-sortable>
      <div>
        <ha-entity-picker
          allow-custom-entity
          .hass=${this.hass}
          .includeDomains=${this.includeDomains}
          .excludeDomains=${this.excludeDomains}
          .includeEntities=${this.includeEntities}
          .excludeEntities=${this._excludeEntities(this.value,this.excludeEntities)}
          .includeDeviceClasses=${this.includeDeviceClasses}
          .includeUnitOfMeasurement=${this.includeUnitOfMeasurement}
          .entityFilter=${this.entityFilter}
          .placeholder=${this.placeholder}
          .helper=${this.helper}
          .disabled=${this.disabled}
          .createDomains=${this.createDomains}
          .required=${this.required&&!e.length}
          @value-changed=${this._addEntity}
          .addButton=${e.length>0}
        ></ha-entity-picker>
      </div>
    `}_entityMoved(e){e.stopPropagation();const{oldIndex:t,newIndex:i}=e.detail,s=this._currentEntities,r=s[t],o=[...s];o.splice(t,1),o.splice(i,0,r),this._updateEntities(o)}get _currentEntities(){return this.value||[]}async _updateEntities(e){this.value=e,(0,n.r)(this,"value-changed",{value:e})}_entityChanged(e){e.stopPropagation();const t=e.currentTarget.curValue,i=e.detail.value;if(i===t||void 0!==i&&!(0,d.n)(i))return;const s=this._currentEntities;i&&!s.includes(i)?this._updateEntities(s.map((e=>e===t?i:e))):this._updateEntities(s.filter((e=>e!==t)))}async _addEntity(e){e.stopPropagation();const t=e.detail.value;if(!t)return;if(e.currentTarget.value="",!t)return;const i=this._currentEntities;i.includes(t)||this._updateEntities([...i,t])}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.reorder=!1,this._excludeEntities=(0,a.A)(((e,t)=>void 0===e?t:[...t||[],...e]))}}u.styles=r.AH`
    div {
      margin-top: 8px;
    }
    label {
      display: block;
      margin: 0 0 8px;
    }
    .entity {
      display: flex;
      flex-direction: row;
      align-items: center;
    }
    .entity ha-entity-picker {
      flex: 1;
    }
    .entity-handle {
      padding: 8px;
      cursor: move; /* fallback if grab cursor is unsupported */
      cursor: grab;
    }
  `,(0,s.__decorate)([(0,o.MZ)({attribute:!1})],u.prototype,"hass",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array})],u.prototype,"value",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],u.prototype,"disabled",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],u.prototype,"required",void 0),(0,s.__decorate)([(0,o.MZ)()],u.prototype,"label",void 0),(0,s.__decorate)([(0,o.MZ)()],u.prototype,"placeholder",void 0),(0,s.__decorate)([(0,o.MZ)()],u.prototype,"helper",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"include-domains"})],u.prototype,"includeDomains",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-domains"})],u.prototype,"excludeDomains",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"include-device-classes"})],u.prototype,"includeDeviceClasses",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"include-unit-of-measurement"})],u.prototype,"includeUnitOfMeasurement",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"include-entities"})],u.prototype,"includeEntities",void 0),(0,s.__decorate)([(0,o.MZ)({type:Array,attribute:"exclude-entities"})],u.prototype,"excludeEntities",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],u.prototype,"entityFilter",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1,type:Array})],u.prototype,"createDomains",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],u.prototype,"reorder",void 0),u=(0,s.__decorate)([(0,o.EM)("ha-entities-picker")],u),t()}catch(h){t(h)}}))},25394:function(e,t,i){i.a(e,(async function(e,s){try{i.r(t),i.d(t,{HaEntitySelector:()=>_});var r=i(62826),o=i(96196),a=i(77845),n=i(55376),d=i(92542),l=i(28441),c=i(82694),h=i(32637),u=i(82965),p=e([h,u]);[h,u]=p.then?(await p)():p;class _ extends o.WF{_hasIntegration(e){return e.entity?.filter&&(0,n.e)(e.entity.filter).some((e=>e.integration))}willUpdate(e){e.get("selector")&&void 0!==this.value&&(this.selector.entity?.multiple&&!Array.isArray(this.value)?(this.value=[this.value],(0,d.r)(this,"value-changed",{value:this.value})):!this.selector.entity?.multiple&&Array.isArray(this.value)&&(this.value=this.value[0],(0,d.r)(this,"value-changed",{value:this.value})))}render(){return this._hasIntegration(this.selector)&&!this._entitySources?o.s6:this.selector.entity?.multiple?o.qy`
      <ha-entities-picker
        .hass=${this.hass}
        .value=${this.value}
        .label=${this.label}
        .helper=${this.helper}
        .includeEntities=${this.selector.entity.include_entities}
        .excludeEntities=${this.selector.entity.exclude_entities}
        .reorder=${this.selector.entity.reorder??!1}
        .entityFilter=${this._filterEntities}
        .createDomains=${this._createDomains}
        .placeholder=${this.placeholder}
        .disabled=${this.disabled}
        .required=${this.required}
      ></ha-entities-picker>
    `:o.qy`<ha-entity-picker
        .hass=${this.hass}
        .value=${this.value}
        .label=${this.label}
        .helper=${this.helper}
        .includeEntities=${this.selector.entity?.include_entities}
        .excludeEntities=${this.selector.entity?.exclude_entities}
        .entityFilter=${this._filterEntities}
        .createDomains=${this._createDomains}
        .placeholder=${this.placeholder}
        .disabled=${this.disabled}
        .required=${this.required}
        allow-custom-entity
      ></ha-entity-picker>`}updated(e){super.updated(e),e.has("selector")&&this._hasIntegration(this.selector)&&!this._entitySources&&(0,l.c)(this.hass).then((e=>{this._entitySources=e})),e.has("selector")&&(this._createDomains=(0,c.Lo)(this.selector))}constructor(...e){super(...e),this.disabled=!1,this.required=!0,this._filterEntities=e=>!this.selector?.entity?.filter||(0,n.e)(this.selector.entity.filter).some((t=>(0,c.Ru)(t,e,this._entitySources)))}}(0,r.__decorate)([(0,a.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,r.__decorate)([(0,a.MZ)({attribute:!1})],_.prototype,"selector",void 0),(0,r.__decorate)([(0,a.wk)()],_.prototype,"_entitySources",void 0),(0,r.__decorate)([(0,a.MZ)()],_.prototype,"value",void 0),(0,r.__decorate)([(0,a.MZ)()],_.prototype,"label",void 0),(0,r.__decorate)([(0,a.MZ)()],_.prototype,"helper",void 0),(0,r.__decorate)([(0,a.MZ)()],_.prototype,"placeholder",void 0),(0,r.__decorate)([(0,a.MZ)({type:Boolean})],_.prototype,"disabled",void 0),(0,r.__decorate)([(0,a.MZ)({type:Boolean})],_.prototype,"required",void 0),(0,r.__decorate)([(0,a.wk)()],_.prototype,"_createDomains",void 0),_=(0,r.__decorate)([(0,a.EM)("ha-selector-entity")],_),s()}catch(_){s(_)}}))},63801:function(e,t,i){var s=i(62826),r=i(96196),o=i(77845),a=i(92542);class n extends r.WF{updated(e){e.has("disabled")&&(this.disabled?this._destroySortable():this._createSortable())}disconnectedCallback(){super.disconnectedCallback(),this._shouldBeDestroy=!0,setTimeout((()=>{this._shouldBeDestroy&&(this._destroySortable(),this._shouldBeDestroy=!1)}),1)}connectedCallback(){super.connectedCallback(),this._shouldBeDestroy=!1,this.hasUpdated&&!this.disabled&&this._createSortable()}createRenderRoot(){return this}render(){return this.noStyle?r.s6:r.qy`
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
    `}async _createSortable(){if(this._sortable)return;const e=this.children[0];if(!e)return;const t=(await Promise.all([i.e("5283"),i.e("1387")]).then(i.bind(i,38214))).default,s={scroll:!0,forceAutoScrollFallback:!0,scrollSpeed:20,animation:150,...this.options,onChoose:this._handleChoose,onStart:this._handleStart,onEnd:this._handleEnd,onUpdate:this._handleUpdate,onAdd:this._handleAdd,onRemove:this._handleRemove};this.draggableSelector&&(s.draggable=this.draggableSelector),this.handleSelector&&(s.handle=this.handleSelector),void 0!==this.invertSwap&&(s.invertSwap=this.invertSwap),this.group&&(s.group=this.group),this.filter&&(s.filter=this.filter),this._sortable=new t(e,s)}_destroySortable(){this._sortable&&(this._sortable.destroy(),this._sortable=void 0)}constructor(...e){super(...e),this.disabled=!1,this.noStyle=!1,this.invertSwap=!1,this.rollback=!0,this._shouldBeDestroy=!1,this._handleUpdate=e=>{(0,a.r)(this,"item-moved",{newIndex:e.newIndex,oldIndex:e.oldIndex})},this._handleAdd=e=>{(0,a.r)(this,"item-added",{index:e.newIndex,data:e.item.sortableData,item:e.item})},this._handleRemove=e=>{(0,a.r)(this,"item-removed",{index:e.oldIndex})},this._handleEnd=async e=>{(0,a.r)(this,"drag-end"),this.rollback&&e.item.placeholder&&(e.item.placeholder.replaceWith(e.item),delete e.item.placeholder)},this._handleStart=()=>{(0,a.r)(this,"drag-start")},this._handleChoose=e=>{this.rollback&&(e.item.placeholder=document.createComment("sort-placeholder"),e.item.after(e.item.placeholder))}}}(0,s.__decorate)([(0,o.MZ)({type:Boolean})],n.prototype,"disabled",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean,attribute:"no-style"})],n.prototype,"noStyle",void 0),(0,s.__decorate)([(0,o.MZ)({type:String,attribute:"draggable-selector"})],n.prototype,"draggableSelector",void 0),(0,s.__decorate)([(0,o.MZ)({type:String,attribute:"handle-selector"})],n.prototype,"handleSelector",void 0),(0,s.__decorate)([(0,o.MZ)({type:String,attribute:"filter"})],n.prototype,"filter",void 0),(0,s.__decorate)([(0,o.MZ)({type:String})],n.prototype,"group",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean,attribute:"invert-swap"})],n.prototype,"invertSwap",void 0),(0,s.__decorate)([(0,o.MZ)({attribute:!1})],n.prototype,"options",void 0),(0,s.__decorate)([(0,o.MZ)({type:Boolean})],n.prototype,"rollback",void 0),n=(0,s.__decorate)([(0,o.EM)("ha-sortable")],n)},28441:function(e,t,i){i.d(t,{c:()=>o});const s=async(e,t,i,r,o,...a)=>{const n=o,d=n[e],l=d=>r&&r(o,d.result)!==d.cacheKey?(n[e]=void 0,s(e,t,i,r,o,...a)):d.result;if(d)return d instanceof Promise?d.then(l):l(d);const c=i(o,...a);return n[e]=c,c.then((i=>{n[e]={result:i,cacheKey:r?.(o,i)},setTimeout((()=>{n[e]=void 0}),t)}),(()=>{n[e]=void 0})),c},r=e=>e.callWS({type:"entity/source"}),o=e=>s("_entitySources",3e4,r,(e=>Object.keys(e.states).length),e)},70570:function(e,t,i){i.d(t,{N:()=>o});const s=e=>{let t=[];function i(i,s){e=s?i:Object.assign(Object.assign({},e),i);let r=t;for(let t=0;t<r.length;t++)r[t](e)}return{get state(){return e},action(t){function s(e){i(e,!1)}return function(){let i=[e];for(let e=0;e<arguments.length;e++)i.push(arguments[e]);let r=t.apply(this,i);if(null!=r)return r instanceof Promise?r.then(s):s(r)}},setState:i,clearState(){e=void 0},subscribe(e){return t.push(e),()=>{!function(e){let i=[];for(let s=0;s<t.length;s++)t[s]===e?e=null:i.push(t[s]);t=i}(e)}}}},r=(e,t,i,r,o={unsubGrace:!0})=>{if(e[t])return e[t];let a,n,d=0,l=s();const c=()=>{if(!i)throw new Error("Collection does not support refresh");return i(e).then((e=>l.setState(e,!0)))},h=()=>c().catch((t=>{if(e.connected)throw t})),u=()=>{n=void 0,a&&a.then((e=>{e()})),l.clearState(),e.removeEventListener("ready",c),e.removeEventListener("disconnected",p)},p=()=>{n&&(clearTimeout(n),u())};return e[t]={get state(){return l.state},refresh:c,subscribe(t){d++,1===d&&(()=>{if(void 0!==n)return clearTimeout(n),void(n=void 0);r&&(a=r(e,l)),i&&(e.addEventListener("ready",h),h()),e.addEventListener("disconnected",p)})();const s=l.subscribe(t);return void 0!==l.state&&setTimeout((()=>t(l.state)),0),()=>{s(),d--,d||(o.unsubGrace?n=setTimeout(u,5e3):u())}}},e[t]},o=(e,t,i,s,o)=>r(s,e,t,i).subscribe(o)},37540:function(e,t,i){i.d(t,{Kq:()=>h});var s=i(63937),r=i(42017);const o=(e,t)=>{const i=e._$AN;if(void 0===i)return!1;for(const s of i)s._$AO?.(t,!1),o(s,t);return!0},a=e=>{let t,i;do{if(void 0===(t=e._$AM))break;i=t._$AN,i.delete(e),e=t}while(0===i?.size)},n=e=>{for(let t;t=e._$AM;e=t){let i=t._$AN;if(void 0===i)t._$AN=i=new Set;else if(i.has(e))break;i.add(e),c(t)}};function d(e){void 0!==this._$AN?(a(this),this._$AM=e,n(this)):this._$AM=e}function l(e,t=!1,i=0){const s=this._$AH,r=this._$AN;if(void 0!==r&&0!==r.size)if(t)if(Array.isArray(s))for(let n=i;n<s.length;n++)o(s[n],!1),a(s[n]);else null!=s&&(o(s,!1),a(s));else o(this,e)}const c=e=>{e.type==r.OA.CHILD&&(e._$AP??=l,e._$AQ??=d)};class h extends r.WL{_$AT(e,t,i){super._$AT(e,t,i),n(this),this.isConnected=e._$AU}_$AO(e,t=!0){e!==this.isConnected&&(this.isConnected=e,e?this.reconnected?.():this.disconnected?.()),t&&(o(this,e),a(this))}setValue(e){if((0,s.Rt)(this._$Ct))this._$Ct._$AI(e,this);else{const t=[...this._$Ct._$AH];t[this._$Ci]=e,this._$Ct._$AI(t,this,0)}}disconnected(){}reconnected(){}constructor(){super(...arguments),this._$AN=void 0}}},3890:function(e,t,i){i.d(t,{T:()=>u});var s=i(5055),r=i(63937),o=i(37540);class a{disconnect(){this.G=void 0}reconnect(e){this.G=e}deref(){return this.G}constructor(e){this.G=e}}class n{get(){return this.Y}pause(){this.Y??=new Promise((e=>this.Z=e))}resume(){this.Z?.(),this.Y=this.Z=void 0}constructor(){this.Y=void 0,this.Z=void 0}}var d=i(42017);const l=e=>!(0,r.sO)(e)&&"function"==typeof e.then,c=1073741823;class h extends o.Kq{render(...e){return e.find((e=>!l(e)))??s.c0}update(e,t){const i=this._$Cbt;let r=i.length;this._$Cbt=t;const o=this._$CK,a=this._$CX;this.isConnected||this.disconnected();for(let s=0;s<t.length&&!(s>this._$Cwt);s++){const e=t[s];if(!l(e))return this._$Cwt=s,e;s<r&&e===i[s]||(this._$Cwt=c,r=0,Promise.resolve(e).then((async t=>{for(;a.get();)await a.get();const i=o.deref();if(void 0!==i){const s=i._$Cbt.indexOf(e);s>-1&&s<i._$Cwt&&(i._$Cwt=s,i.setValue(t))}})))}return s.c0}disconnected(){this._$CK.disconnect(),this._$CX.pause()}reconnected(){this._$CK.reconnect(this),this._$CX.resume()}constructor(){super(...arguments),this._$Cwt=c,this._$Cbt=[],this._$CK=new a(this),this._$CX=new n}}const u=(0,d.u$)(h)}};
//# sourceMappingURL=8651.515cd1e9923cbfa7.js.map