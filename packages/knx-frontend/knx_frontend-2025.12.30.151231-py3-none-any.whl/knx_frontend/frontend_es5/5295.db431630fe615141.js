"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["5295"],{32637:function(e,t,i){i.a(e,(async function(e,t){try{var r=i(61397),a=i(50264),n=i(94741),o=i(44734),s=i(56038),l=i(69683),d=i(6454),c=(i(28706),i(2008),i(74423),i(62062),i(54554),i(18111),i(22489),i(61701),i(26099),i(62826)),u=i(96196),h=i(77845),p=i(22786),y=i(92542),v=i(45996),_=(i(63801),i(82965)),b=e([_]);_=(b.then?(await b)():b)[0];var f,m,g,A,$,k=e=>e,M=function(e){function t(){var e;(0,o.A)(this,t);for(var i=arguments.length,r=new Array(i),a=0;a<i;a++)r[a]=arguments[a];return(e=(0,l.A)(this,t,[].concat(r))).disabled=!1,e.required=!1,e.reorder=!1,e._excludeEntities=(0,p.A)(((e,t)=>void 0===e?t:[].concat((0,n.A)(t||[]),(0,n.A)(e)))),e}return(0,d.A)(t,e),(0,s.A)(t,[{key:"render",value:function(){if(!this.hass)return u.s6;var e=this._currentEntities;return(0,u.qy)(f||(f=k`
      ${0}
      <ha-sortable
        .disabled=${0}
        handle-selector=".entity-handle"
        @item-moved=${0}
      >
        <div class="list">
          ${0}
        </div>
      </ha-sortable>
      <div>
        <ha-entity-picker
          allow-custom-entity
          .hass=${0}
          .includeDomains=${0}
          .excludeDomains=${0}
          .includeEntities=${0}
          .excludeEntities=${0}
          .includeDeviceClasses=${0}
          .includeUnitOfMeasurement=${0}
          .entityFilter=${0}
          .placeholder=${0}
          .helper=${0}
          .disabled=${0}
          .createDomains=${0}
          .required=${0}
          @value-changed=${0}
          .addButton=${0}
        ></ha-entity-picker>
      </div>
    `),this.label?(0,u.qy)(m||(m=k`<label>${0}</label>`),this.label):u.s6,!this.reorder||this.disabled,this._entityMoved,e.map((e=>(0,u.qy)(g||(g=k`
              <div class="entity">
                <ha-entity-picker
                  allow-custom-entity
                  .curValue=${0}
                  .hass=${0}
                  .includeDomains=${0}
                  .excludeDomains=${0}
                  .includeEntities=${0}
                  .excludeEntities=${0}
                  .includeDeviceClasses=${0}
                  .includeUnitOfMeasurement=${0}
                  .entityFilter=${0}
                  .value=${0}
                  .disabled=${0}
                  .createDomains=${0}
                  @value-changed=${0}
                ></ha-entity-picker>
                ${0}
              </div>
            `),e,this.hass,this.includeDomains,this.excludeDomains,this.includeEntities,this.excludeEntities,this.includeDeviceClasses,this.includeUnitOfMeasurement,this.entityFilter,e,this.disabled,this.createDomains,this._entityChanged,this.reorder?(0,u.qy)(A||(A=k`
                      <ha-svg-icon
                        class="entity-handle"
                        .path=${0}
                      ></ha-svg-icon>
                    `),"M21 11H3V9H21V11M21 13H3V15H21V13Z"):u.s6))),this.hass,this.includeDomains,this.excludeDomains,this.includeEntities,this._excludeEntities(this.value,this.excludeEntities),this.includeDeviceClasses,this.includeUnitOfMeasurement,this.entityFilter,this.placeholder,this.helper,this.disabled,this.createDomains,this.required&&!e.length,this._addEntity,e.length>0)}},{key:"_entityMoved",value:function(e){e.stopPropagation();var t=e.detail,i=t.oldIndex,r=t.newIndex,a=this._currentEntities,o=a[i],s=(0,n.A)(a);s.splice(i,1),s.splice(r,0,o),this._updateEntities(s)}},{key:"_currentEntities",get:function(){return this.value||[]}},{key:"_updateEntities",value:(c=(0,a.A)((0,r.A)().m((function e(t){return(0,r.A)().w((function(e){for(;;)switch(e.n){case 0:this.value=t,(0,y.r)(this,"value-changed",{value:t});case 1:return e.a(2)}}),e,this)}))),function(e){return c.apply(this,arguments)})},{key:"_entityChanged",value:function(e){e.stopPropagation();var t=e.currentTarget.curValue,i=e.detail.value;if(i!==t&&(void 0===i||(0,v.n)(i))){var r=this._currentEntities;i&&!r.includes(i)?this._updateEntities(r.map((e=>e===t?i:e))):this._updateEntities(r.filter((e=>e!==t)))}}},{key:"_addEntity",value:(i=(0,a.A)((0,r.A)().m((function e(t){var i,a;return(0,r.A)().w((function(e){for(;;)switch(e.n){case 0:if(t.stopPropagation(),i=t.detail.value){e.n=1;break}return e.a(2);case 1:if(t.currentTarget.value="",i){e.n=2;break}return e.a(2);case 2:if(!(a=this._currentEntities).includes(i)){e.n=3;break}return e.a(2);case 3:this._updateEntities([].concat((0,n.A)(a),[i]));case 4:return e.a(2)}}),e,this)}))),function(e){return i.apply(this,arguments)})}]);var i,c}(u.WF);M.styles=(0,u.AH)($||($=k`
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
  `)),(0,c.__decorate)([(0,h.MZ)({attribute:!1})],M.prototype,"hass",void 0),(0,c.__decorate)([(0,h.MZ)({type:Array})],M.prototype,"value",void 0),(0,c.__decorate)([(0,h.MZ)({type:Boolean})],M.prototype,"disabled",void 0),(0,c.__decorate)([(0,h.MZ)({type:Boolean})],M.prototype,"required",void 0),(0,c.__decorate)([(0,h.MZ)()],M.prototype,"label",void 0),(0,c.__decorate)([(0,h.MZ)()],M.prototype,"placeholder",void 0),(0,c.__decorate)([(0,h.MZ)()],M.prototype,"helper",void 0),(0,c.__decorate)([(0,h.MZ)({type:Array,attribute:"include-domains"})],M.prototype,"includeDomains",void 0),(0,c.__decorate)([(0,h.MZ)({type:Array,attribute:"exclude-domains"})],M.prototype,"excludeDomains",void 0),(0,c.__decorate)([(0,h.MZ)({type:Array,attribute:"include-device-classes"})],M.prototype,"includeDeviceClasses",void 0),(0,c.__decorate)([(0,h.MZ)({type:Array,attribute:"include-unit-of-measurement"})],M.prototype,"includeUnitOfMeasurement",void 0),(0,c.__decorate)([(0,h.MZ)({type:Array,attribute:"include-entities"})],M.prototype,"includeEntities",void 0),(0,c.__decorate)([(0,h.MZ)({type:Array,attribute:"exclude-entities"})],M.prototype,"excludeEntities",void 0),(0,c.__decorate)([(0,h.MZ)({attribute:!1})],M.prototype,"entityFilter",void 0),(0,c.__decorate)([(0,h.MZ)({attribute:!1,type:Array})],M.prototype,"createDomains",void 0),(0,c.__decorate)([(0,h.MZ)({type:Boolean})],M.prototype,"reorder",void 0),M=(0,c.__decorate)([(0,h.EM)("ha-entities-picker")],M),t()}catch(x){t(x)}}))},25394:function(e,t,i){i.a(e,(async function(e,r){try{i.r(t),i.d(t,{HaEntitySelector:function(){return $}});var a=i(44734),n=i(56038),o=i(69683),s=i(6454),l=i(25460),d=(i(28706),i(2008),i(18111),i(22489),i(13579),i(26099),i(62826)),c=i(96196),u=i(77845),h=i(55376),p=i(92542),y=i(28441),v=i(82694),_=i(32637),b=i(82965),f=e([_,b]);[_,b]=f.then?(await f)():f;var m,g,A=e=>e,$=function(e){function t(){var e;(0,a.A)(this,t);for(var i=arguments.length,r=new Array(i),n=0;n<i;n++)r[n]=arguments[n];return(e=(0,o.A)(this,t,[].concat(r))).disabled=!1,e.required=!0,e._filterEntities=t=>{var i;return null===(i=e.selector)||void 0===i||null===(i=i.entity)||void 0===i||!i.filter||(0,h.e)(e.selector.entity.filter).some((i=>(0,v.Ru)(i,t,e._entitySources)))},e}return(0,s.A)(t,e),(0,n.A)(t,[{key:"_hasIntegration",value:function(e){var t;return(null===(t=e.entity)||void 0===t?void 0:t.filter)&&(0,h.e)(e.entity.filter).some((e=>e.integration))}},{key:"willUpdate",value:function(e){var t,i;e.get("selector")&&void 0!==this.value&&(null!==(t=this.selector.entity)&&void 0!==t&&t.multiple&&!Array.isArray(this.value)?(this.value=[this.value],(0,p.r)(this,"value-changed",{value:this.value})):null!==(i=this.selector.entity)&&void 0!==i&&i.multiple||!Array.isArray(this.value)||(this.value=this.value[0],(0,p.r)(this,"value-changed",{value:this.value})))}},{key:"render",value:function(){var e,t,i,r;return this._hasIntegration(this.selector)&&!this._entitySources?c.s6:null!==(e=this.selector.entity)&&void 0!==e&&e.multiple?(0,c.qy)(g||(g=A`
      <ha-entities-picker
        .hass=${0}
        .value=${0}
        .label=${0}
        .helper=${0}
        .includeEntities=${0}
        .excludeEntities=${0}
        .reorder=${0}
        .entityFilter=${0}
        .createDomains=${0}
        .placeholder=${0}
        .disabled=${0}
        .required=${0}
      ></ha-entities-picker>
    `),this.hass,this.value,this.label,this.helper,this.selector.entity.include_entities,this.selector.entity.exclude_entities,null!==(t=this.selector.entity.reorder)&&void 0!==t&&t,this._filterEntities,this._createDomains,this.placeholder,this.disabled,this.required):(0,c.qy)(m||(m=A`<ha-entity-picker
        .hass=${0}
        .value=${0}
        .label=${0}
        .helper=${0}
        .includeEntities=${0}
        .excludeEntities=${0}
        .entityFilter=${0}
        .createDomains=${0}
        .placeholder=${0}
        .disabled=${0}
        .required=${0}
        allow-custom-entity
      ></ha-entity-picker>`),this.hass,this.value,this.label,this.helper,null===(i=this.selector.entity)||void 0===i?void 0:i.include_entities,null===(r=this.selector.entity)||void 0===r?void 0:r.exclude_entities,this._filterEntities,this._createDomains,this.placeholder,this.disabled,this.required)}},{key:"updated",value:function(e){(0,l.A)(t,"updated",this,3)([e]),e.has("selector")&&this._hasIntegration(this.selector)&&!this._entitySources&&(0,y.c)(this.hass).then((e=>{this._entitySources=e})),e.has("selector")&&(this._createDomains=(0,v.Lo)(this.selector))}}])}(c.WF);(0,d.__decorate)([(0,u.MZ)({attribute:!1})],$.prototype,"hass",void 0),(0,d.__decorate)([(0,u.MZ)({attribute:!1})],$.prototype,"selector",void 0),(0,d.__decorate)([(0,u.wk)()],$.prototype,"_entitySources",void 0),(0,d.__decorate)([(0,u.MZ)()],$.prototype,"value",void 0),(0,d.__decorate)([(0,u.MZ)()],$.prototype,"label",void 0),(0,d.__decorate)([(0,u.MZ)()],$.prototype,"helper",void 0),(0,d.__decorate)([(0,u.MZ)()],$.prototype,"placeholder",void 0),(0,d.__decorate)([(0,u.MZ)({type:Boolean})],$.prototype,"disabled",void 0),(0,d.__decorate)([(0,u.MZ)({type:Boolean})],$.prototype,"required",void 0),(0,d.__decorate)([(0,u.wk)()],$.prototype,"_createDomains",void 0),$=(0,d.__decorate)([(0,u.EM)("ha-selector-entity")],$),r()}catch(k){r(k)}}))},63801:function(e,t,i){var r,a=i(61397),n=i(50264),o=i(44734),s=i(56038),l=i(75864),d=i(69683),c=i(6454),u=i(25460),h=(i(28706),i(2008),i(23792),i(18111),i(22489),i(26099),i(3362),i(46058),i(62953),i(62826)),p=i(96196),y=i(77845),v=i(92542),_=e=>e,b=function(e){function t(){var e;(0,o.A)(this,t);for(var i=arguments.length,r=new Array(i),s=0;s<i;s++)r[s]=arguments[s];return(e=(0,d.A)(this,t,[].concat(r))).disabled=!1,e.noStyle=!1,e.invertSwap=!1,e.rollback=!0,e._shouldBeDestroy=!1,e._handleUpdate=t=>{(0,v.r)((0,l.A)(e),"item-moved",{newIndex:t.newIndex,oldIndex:t.oldIndex})},e._handleAdd=t=>{(0,v.r)((0,l.A)(e),"item-added",{index:t.newIndex,data:t.item.sortableData,item:t.item})},e._handleRemove=t=>{(0,v.r)((0,l.A)(e),"item-removed",{index:t.oldIndex})},e._handleEnd=function(){var t=(0,n.A)((0,a.A)().m((function t(i){return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:(0,v.r)((0,l.A)(e),"drag-end"),e.rollback&&i.item.placeholder&&(i.item.placeholder.replaceWith(i.item),delete i.item.placeholder);case 1:return t.a(2)}}),t)})));return function(e){return t.apply(this,arguments)}}(),e._handleStart=()=>{(0,v.r)((0,l.A)(e),"drag-start")},e._handleChoose=t=>{e.rollback&&(t.item.placeholder=document.createComment("sort-placeholder"),t.item.after(t.item.placeholder))},e}return(0,c.A)(t,e),(0,s.A)(t,[{key:"updated",value:function(e){e.has("disabled")&&(this.disabled?this._destroySortable():this._createSortable())}},{key:"disconnectedCallback",value:function(){(0,u.A)(t,"disconnectedCallback",this,3)([]),this._shouldBeDestroy=!0,setTimeout((()=>{this._shouldBeDestroy&&(this._destroySortable(),this._shouldBeDestroy=!1)}),1)}},{key:"connectedCallback",value:function(){(0,u.A)(t,"connectedCallback",this,3)([]),this._shouldBeDestroy=!1,this.hasUpdated&&!this.disabled&&this._createSortable()}},{key:"createRenderRoot",value:function(){return this}},{key:"render",value:function(){return this.noStyle?p.s6:(0,p.qy)(r||(r=_`
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
    `))}},{key:"_createSortable",value:(h=(0,n.A)((0,a.A)().m((function e(){var t,r,n;return(0,a.A)().w((function(e){for(;;)switch(e.n){case 0:if(!this._sortable){e.n=1;break}return e.a(2);case 1:if(t=this.children[0]){e.n=2;break}return e.a(2);case 2:return e.n=3,Promise.all([i.e("5283"),i.e("1387")]).then(i.bind(i,38214));case 3:r=e.v.default,n=Object.assign(Object.assign({scroll:!0,forceAutoScrollFallback:!0,scrollSpeed:20,animation:150},this.options),{},{onChoose:this._handleChoose,onStart:this._handleStart,onEnd:this._handleEnd,onUpdate:this._handleUpdate,onAdd:this._handleAdd,onRemove:this._handleRemove}),this.draggableSelector&&(n.draggable=this.draggableSelector),this.handleSelector&&(n.handle=this.handleSelector),void 0!==this.invertSwap&&(n.invertSwap=this.invertSwap),this.group&&(n.group=this.group),this.filter&&(n.filter=this.filter),this._sortable=new r(t,n);case 4:return e.a(2)}}),e,this)}))),function(){return h.apply(this,arguments)})},{key:"_destroySortable",value:function(){this._sortable&&(this._sortable.destroy(),this._sortable=void 0)}}]);var h}(p.WF);(0,h.__decorate)([(0,y.MZ)({type:Boolean})],b.prototype,"disabled",void 0),(0,h.__decorate)([(0,y.MZ)({type:Boolean,attribute:"no-style"})],b.prototype,"noStyle",void 0),(0,h.__decorate)([(0,y.MZ)({type:String,attribute:"draggable-selector"})],b.prototype,"draggableSelector",void 0),(0,h.__decorate)([(0,y.MZ)({type:String,attribute:"handle-selector"})],b.prototype,"handleSelector",void 0),(0,h.__decorate)([(0,y.MZ)({type:String,attribute:"filter"})],b.prototype,"filter",void 0),(0,h.__decorate)([(0,y.MZ)({type:String})],b.prototype,"group",void 0),(0,h.__decorate)([(0,y.MZ)({type:Boolean,attribute:"invert-swap"})],b.prototype,"invertSwap",void 0),(0,h.__decorate)([(0,y.MZ)({attribute:!1})],b.prototype,"options",void 0),(0,h.__decorate)([(0,y.MZ)({type:Boolean})],b.prototype,"rollback",void 0),b=(0,h.__decorate)([(0,y.EM)("ha-sortable")],b)},28441:function(e,t,i){i.d(t,{c:function(){return s}});var r=i(61397),a=i(50264),n=(i(28706),i(26099),i(3362),function(){var e=(0,a.A)((0,r.A)().m((function e(t,i,a,o,s){var l,d,c,u,h,p,y,v=arguments;return(0,r.A)().w((function(e){for(;;)switch(e.n){case 0:for(l=v.length,d=new Array(l>5?l-5:0),c=5;c<l;c++)d[c-5]=v[c];if(h=(u=s)[t],p=e=>o&&o(s,e.result)!==e.cacheKey?(u[t]=void 0,n.apply(void 0,[t,i,a,o,s].concat(d))):e.result,!h){e.n=1;break}return e.a(2,h instanceof Promise?h.then(p):p(h));case 1:return y=a.apply(void 0,[s].concat(d)),u[t]=y,y.then((e=>{u[t]={result:e,cacheKey:null==o?void 0:o(s,e)},setTimeout((()=>{u[t]=void 0}),i)}),(()=>{u[t]=void 0})),e.a(2,y)}}),e)})));return function(t,i,r,a,n){return e.apply(this,arguments)}}()),o=e=>e.callWS({type:"entity/source"}),s=e=>n("_entitySources",3e4,o,(e=>Object.keys(e.states).length),e)}}]);
//# sourceMappingURL=5295.db431630fe615141.js.map