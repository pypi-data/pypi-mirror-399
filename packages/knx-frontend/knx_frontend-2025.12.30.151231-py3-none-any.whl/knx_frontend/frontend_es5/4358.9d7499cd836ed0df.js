"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["4358"],{63801:function(e,t,i){var a,o=i(61397),n=i(50264),r=i(44734),s=i(56038),l=i(75864),d=i(69683),c=i(6454),h=i(25460),u=(i(28706),i(2008),i(23792),i(18111),i(22489),i(26099),i(3362),i(46058),i(62953),i(62826)),p=i(96196),v=i(77845),_=i(92542),b=e=>e,g=function(e){function t(){var e;(0,r.A)(this,t);for(var i=arguments.length,a=new Array(i),s=0;s<i;s++)a[s]=arguments[s];return(e=(0,d.A)(this,t,[].concat(a))).disabled=!1,e.noStyle=!1,e.invertSwap=!1,e.rollback=!0,e._shouldBeDestroy=!1,e._handleUpdate=t=>{(0,_.r)((0,l.A)(e),"item-moved",{newIndex:t.newIndex,oldIndex:t.oldIndex})},e._handleAdd=t=>{(0,_.r)((0,l.A)(e),"item-added",{index:t.newIndex,data:t.item.sortableData,item:t.item})},e._handleRemove=t=>{(0,_.r)((0,l.A)(e),"item-removed",{index:t.oldIndex})},e._handleEnd=function(){var t=(0,n.A)((0,o.A)().m((function t(i){return(0,o.A)().w((function(t){for(;;)switch(t.n){case 0:(0,_.r)((0,l.A)(e),"drag-end"),e.rollback&&i.item.placeholder&&(i.item.placeholder.replaceWith(i.item),delete i.item.placeholder);case 1:return t.a(2)}}),t)})));return function(e){return t.apply(this,arguments)}}(),e._handleStart=()=>{(0,_.r)((0,l.A)(e),"drag-start")},e._handleChoose=t=>{e.rollback&&(t.item.placeholder=document.createComment("sort-placeholder"),t.item.after(t.item.placeholder))},e}return(0,c.A)(t,e),(0,s.A)(t,[{key:"updated",value:function(e){e.has("disabled")&&(this.disabled?this._destroySortable():this._createSortable())}},{key:"disconnectedCallback",value:function(){(0,h.A)(t,"disconnectedCallback",this,3)([]),this._shouldBeDestroy=!0,setTimeout((()=>{this._shouldBeDestroy&&(this._destroySortable(),this._shouldBeDestroy=!1)}),1)}},{key:"connectedCallback",value:function(){(0,h.A)(t,"connectedCallback",this,3)([]),this._shouldBeDestroy=!1,this.hasUpdated&&!this.disabled&&this._createSortable()}},{key:"createRenderRoot",value:function(){return this}},{key:"render",value:function(){return this.noStyle?p.s6:(0,p.qy)(a||(a=b`
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
    `))}},{key:"_createSortable",value:(u=(0,n.A)((0,o.A)().m((function e(){var t,a,n;return(0,o.A)().w((function(e){for(;;)switch(e.n){case 0:if(!this._sortable){e.n=1;break}return e.a(2);case 1:if(t=this.children[0]){e.n=2;break}return e.a(2);case 2:return e.n=3,Promise.all([i.e("5283"),i.e("1387")]).then(i.bind(i,38214));case 3:a=e.v.default,n=Object.assign(Object.assign({scroll:!0,forceAutoScrollFallback:!0,scrollSpeed:20,animation:150},this.options),{},{onChoose:this._handleChoose,onStart:this._handleStart,onEnd:this._handleEnd,onUpdate:this._handleUpdate,onAdd:this._handleAdd,onRemove:this._handleRemove}),this.draggableSelector&&(n.draggable=this.draggableSelector),this.handleSelector&&(n.handle=this.handleSelector),void 0!==this.invertSwap&&(n.invertSwap=this.invertSwap),this.group&&(n.group=this.group),this.filter&&(n.filter=this.filter),this._sortable=new a(t,n);case 4:return e.a(2)}}),e,this)}))),function(){return u.apply(this,arguments)})},{key:"_destroySortable",value:function(){this._sortable&&(this._sortable.destroy(),this._sortable=void 0)}}]);var u}(p.WF);(0,u.__decorate)([(0,v.MZ)({type:Boolean})],g.prototype,"disabled",void 0),(0,u.__decorate)([(0,v.MZ)({type:Boolean,attribute:"no-style"})],g.prototype,"noStyle",void 0),(0,u.__decorate)([(0,v.MZ)({type:String,attribute:"draggable-selector"})],g.prototype,"draggableSelector",void 0),(0,u.__decorate)([(0,v.MZ)({type:String,attribute:"handle-selector"})],g.prototype,"handleSelector",void 0),(0,u.__decorate)([(0,v.MZ)({type:String,attribute:"filter"})],g.prototype,"filter",void 0),(0,u.__decorate)([(0,v.MZ)({type:String})],g.prototype,"group",void 0),(0,u.__decorate)([(0,v.MZ)({type:Boolean,attribute:"invert-swap"})],g.prototype,"invertSwap",void 0),(0,u.__decorate)([(0,v.MZ)({attribute:!1})],g.prototype,"options",void 0),(0,u.__decorate)([(0,v.MZ)({type:Boolean})],g.prototype,"rollback",void 0),g=(0,u.__decorate)([(0,v.EM)("ha-sortable")],g)},24933:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t);var o=i(61397),n=i(50264),r=i(94741),s=i(44734),l=i(56038),d=i(69683),c=i(6454),h=(i(28706),i(54554),i(62826)),u=i(96196),p=i(77845),v=i(4937),_=i(92542),b=i(89473),g=(i(60733),i(88867)),f=(i(75261),i(56565),i(63801),i(78740),i(10234)),y=i(39396),m=e([b,g]);[b,g]=m.then?(await m)():m;var k,x,A,w,$=e=>e,S=function(e){function t(){var e;(0,s.A)(this,t);for(var i=arguments.length,a=new Array(i),o=0;o<i;o++)a[o]=arguments[o];return(e=(0,d.A)(this,t,[].concat(a))).new=!1,e.disabled=!1,e._options=[],e}return(0,c.A)(t,e),(0,l.A)(t,[{key:"_optionMoved",value:function(e){e.stopPropagation();var t=e.detail,i=t.oldIndex,a=t.newIndex,o=this._options.concat(),n=o.splice(i,1)[0];o.splice(a,0,n),(0,_.r)(this,"value-changed",{value:Object.assign(Object.assign({},this._item),{},{options:o})})}},{key:"item",set:function(e){this._item=e,e?(this._name=e.name||"",this._icon=e.icon||"",this._options=e.options||[]):(this._name="",this._icon="",this._options=[])}},{key:"focus",value:function(){this.updateComplete.then((()=>{var e;return null===(e=this.shadowRoot)||void 0===e||null===(e=e.querySelector("[dialogInitialFocus]"))||void 0===e?void 0:e.focus()}))}},{key:"render",value:function(){return this.hass?(0,u.qy)(k||(k=$`
      <div class="form">
        <ha-textfield
          dialogInitialFocus
          autoValidate
          required
          .validationMessage=${0}
          .value=${0}
          .label=${0}
          .configValue=${0}
          @input=${0}
          .disabled=${0}
        ></ha-textfield>
        <ha-icon-picker
          .hass=${0}
          .value=${0}
          .configValue=${0}
          @value-changed=${0}
          .label=${0}
          .disabled=${0}
        ></ha-icon-picker>
        <div class="header">
          ${0}:
        </div>
        <ha-sortable
          @item-moved=${0}
          handle-selector=".handle"
          .disabled=${0}
        >
          <ha-list class="options">
            ${0}
          </ha-list>
        </ha-sortable>
        <div class="layout horizontal center">
          <ha-textfield
            class="flex-auto"
            id="option_input"
            .label=${0}
            @keydown=${0}
            .disabled=${0}
          ></ha-textfield>
          <ha-button
            size="small"
            appearance="plain"
            @click=${0}
            .disabled=${0}
            >${0}</ha-button
          >
        </div>
      </div>
    `),this.hass.localize("ui.dialogs.helper_settings.required_error_msg"),this._name,this.hass.localize("ui.dialogs.helper_settings.generic.name"),"name",this._valueChanged,this.disabled,this.hass,this._icon,"icon",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.icon"),this.disabled,this.hass.localize("ui.dialogs.helper_settings.input_select.options"),this._optionMoved,this.disabled,this._options.length?(0,v.u)(this._options,(e=>e),((e,t)=>(0,u.qy)(x||(x=$`
                    <ha-list-item class="option" hasMeta>
                      <div class="optioncontent">
                        <div class="handle">
                          <ha-svg-icon
                            .path=${0}
                          ></ha-svg-icon>
                        </div>
                        ${0}
                      </div>
                      <ha-icon-button
                        slot="meta"
                        .index=${0}
                        .label=${0}
                        @click=${0}
                        .disabled=${0}
                        .path=${0}
                      ></ha-icon-button>
                    </ha-list-item>
                  `),"M21 11H3V9H21V11M21 13H3V15H21V13Z",e,t,this.hass.localize("ui.dialogs.helper_settings.input_select.remove_option"),this._removeOption,this.disabled,"M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"))):(0,u.qy)(A||(A=$`
                  <ha-list-item noninteractive>
                    ${0}
                  </ha-list-item>
                `),this.hass.localize("ui.dialogs.helper_settings.input_select.no_options")),this.hass.localize("ui.dialogs.helper_settings.input_select.add_option"),this._handleKeyAdd,this.disabled,this._addOption,this.disabled,this.hass.localize("ui.dialogs.helper_settings.input_select.add")):u.s6}},{key:"_handleKeyAdd",value:function(e){e.stopPropagation(),"Enter"===e.key&&this._addOption()}},{key:"_addOption",value:function(){var e=this._optionInput;null!=e&&e.value&&((0,_.r)(this,"value-changed",{value:Object.assign(Object.assign({},this._item),{},{options:[].concat((0,r.A)(this._options),[e.value])})}),e.value="")}},{key:"_removeOption",value:(i=(0,n.A)((0,o.A)().m((function e(t){var i,a;return(0,o.A)().w((function(e){for(;;)switch(e.n){case 0:return i=t.target.index,e.n=1,(0,f.dk)(this,{title:this.hass.localize("ui.dialogs.helper_settings.input_select.confirm_delete.delete"),text:this.hass.localize("ui.dialogs.helper_settings.input_select.confirm_delete.prompt"),destructive:!0});case 1:if(e.v){e.n=2;break}return e.a(2);case 2:(a=(0,r.A)(this._options)).splice(i,1),(0,_.r)(this,"value-changed",{value:Object.assign(Object.assign({},this._item),{},{options:a})});case 3:return e.a(2)}}),e,this)}))),function(e){return i.apply(this,arguments)})},{key:"_valueChanged",value:function(e){var t;if(this.new||this._item){e.stopPropagation();var i=e.target.configValue,a=(null===(t=e.detail)||void 0===t?void 0:t.value)||e.target.value;if(this[`_${i}`]!==a){var o=Object.assign({},this._item);a?o[i]=a:delete o[i],(0,_.r)(this,"value-changed",{value:o})}}}}],[{key:"styles",get:function(){return[y.RF,(0,u.AH)(w||(w=$`
        .form {
          color: var(--primary-text-color);
        }
        .option {
          border: 1px solid var(--divider-color);
          border-radius: var(--ha-border-radius-sm);
          margin-top: 4px;
          --mdc-icon-button-size: 24px;
          --mdc-ripple-color: transparent;
          --mdc-list-side-padding: 16px;
          cursor: default;
          background-color: var(--card-background-color);
        }
        ha-textfield {
          display: block;
          margin-bottom: 8px;
        }
        #option_input {
          margin-top: 8px;
        }
        .header {
          margin-top: 8px;
          margin-bottom: 8px;
        }
        .handle {
          cursor: move; /* fallback if grab cursor is unsupported */
          cursor: grab;
          padding-right: 12px;
          padding-inline-end: 12px;
          padding-inline-start: initial;
        }
        .handle ha-svg-icon {
          pointer-events: none;
          height: 24px;
        }
        .optioncontent {
          display: flex;
          align-items: center;
        }
      `))]}}]);var i}(u.WF);(0,h.__decorate)([(0,p.MZ)({attribute:!1})],S.prototype,"hass",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean})],S.prototype,"new",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean})],S.prototype,"disabled",void 0),(0,h.__decorate)([(0,p.wk)()],S.prototype,"_name",void 0),(0,h.__decorate)([(0,p.wk)()],S.prototype,"_icon",void 0),(0,h.__decorate)([(0,p.wk)()],S.prototype,"_options",void 0),(0,h.__decorate)([(0,p.P)("#option_input",!0)],S.prototype,"_optionInput",void 0),S=(0,h.__decorate)([(0,p.EM)("ha-input_select-form")],S),a()}catch(M){a(M)}}))},4937:function(e,t,i){i.d(t,{u:function(){return p}});var a=i(78261),o=i(31432),n=i(44734),r=i(56038),s=i(69683),l=i(6454),d=(i(16280),i(23792),i(36033),i(26099),i(62953),i(4610)),c=i(42017),h=i(63937),u=(e,t,i)=>{for(var a=new Map,o=t;o<=i;o++)a.set(e[o],o);return a},p=(0,c.u$)(function(e){function t(e){var i;if((0,n.A)(this,t),i=(0,s.A)(this,t,[e]),e.type!==c.OA.CHILD)throw Error("repeat() can only be used in text expressions");return i}return(0,l.A)(t,e),(0,r.A)(t,[{key:"dt",value:function(e,t,i){var a;void 0===i?i=t:void 0!==t&&(a=t);var n,r=[],s=[],l=0,d=(0,o.A)(e);try{for(d.s();!(n=d.n()).done;){var c=n.value;r[l]=a?a(c,l):l,s[l]=i(c,l),l++}}catch(h){d.e(h)}finally{d.f()}return{values:s,keys:r}}},{key:"render",value:function(e,t,i){return this.dt(e,t,i).values}},{key:"update",value:function(e,t){var i,o=(0,a.A)(t,3),n=o[0],r=o[1],s=o[2],l=(0,h.cN)(e),c=this.dt(n,r,s),p=c.values,v=c.keys;if(!Array.isArray(l))return this.ut=v,p;for(var _,b,g=null!==(i=this.ut)&&void 0!==i?i:this.ut=[],f=[],y=0,m=l.length-1,k=0,x=p.length-1;y<=m&&k<=x;)if(null===l[y])y++;else if(null===l[m])m--;else if(g[y]===v[k])f[k]=(0,h.lx)(l[y],p[k]),y++,k++;else if(g[m]===v[x])f[x]=(0,h.lx)(l[m],p[x]),m--,x--;else if(g[y]===v[x])f[x]=(0,h.lx)(l[y],p[x]),(0,h.Dx)(e,f[x+1],l[y]),y++,x--;else if(g[m]===v[k])f[k]=(0,h.lx)(l[m],p[k]),(0,h.Dx)(e,l[y],l[m]),m--,k++;else if(void 0===_&&(_=u(v,k,x),b=u(g,y,m)),_.has(g[y]))if(_.has(g[m])){var A=b.get(v[k]),w=void 0!==A?l[A]:null;if(null===w){var $=(0,h.Dx)(e,l[y]);(0,h.lx)($,p[k]),f[k]=$}else f[k]=(0,h.lx)(w,p[k]),(0,h.Dx)(e,l[y],w),l[A]=null;k++}else(0,h.KO)(l[m]),m--;else(0,h.KO)(l[y]),y++;for(;k<=x;){var S=(0,h.Dx)(e,f[x+1]);(0,h.lx)(S,p[k]),f[k++]=S}for(;y<=m;){var M=l[y++];null!==M&&(0,h.KO)(M)}return this.ut=v,(0,h.mY)(e,f),d.c0}}])}(c.WL))}}]);
//# sourceMappingURL=4358.9d7499cd836ed0df.js.map