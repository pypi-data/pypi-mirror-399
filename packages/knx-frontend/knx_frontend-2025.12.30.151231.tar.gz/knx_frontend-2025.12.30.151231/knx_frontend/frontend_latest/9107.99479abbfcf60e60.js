export const __webpack_id__="9107";export const __webpack_ids__=["9107"];export const __webpack_modules__={55376:function(e,t,i){function o(e){return null==e||Array.isArray(e)?e:[e]}i.d(t,{e:()=>o})},99245:function(e,t,i){i.d(t,{g:()=>o});const o=e=>(t,i)=>e.includes(t,i)},51757:function(e,t,i){i.d(t,{_:()=>r});var o=i(96196),a=i(42017);const r=(0,a.u$)(class extends a.WL{update(e,[t,i]){return this._element&&this._element.localName===t?(i&&Object.entries(i).forEach((([e,t])=>{this._element[e]=t})),o.c0):this.render(t,i)}render(e,t){return this._element=document.createElement(e),t&&Object.entries(t).forEach((([e,t])=>{this._element[e]=t})),this._element}constructor(e){if(super(e),e.type!==a.OA.CHILD)throw new Error("dynamicElementDirective can only be used in content bindings")}})},48774:function(e,t,i){i.d(t,{L:()=>o});const o=(e,t)=>{const i=e.floor_id;return{area:e,floor:(i?t[i]:void 0)||null}}},13877:function(e,t,i){i.d(t,{w:()=>o});const o=(e,t)=>{const i=e.area_id,o=i?t.areas[i]:void 0,a=o?.floor_id;return{device:e,area:o||null,floor:(a?t.floors[a]:void 0)||null}}},25749:function(e,t,i){i.d(t,{SH:()=>l,u1:()=>d,xL:()=>n});var o=i(22786);const a=(0,o.A)((e=>new Intl.Collator(e,{numeric:!0}))),r=(0,o.A)((e=>new Intl.Collator(e,{sensitivity:"accent",numeric:!0}))),s=(e,t)=>e<t?-1:e>t?1:0,n=(e,t,i=void 0)=>Intl?.Collator?a(i).compare(e,t):s(e,t),l=(e,t,i=void 0)=>Intl?.Collator?r(i).compare(e,t):s(e.toLowerCase(),t.toLowerCase()),d=e=>(t,i)=>{const o=e.indexOf(t),a=e.indexOf(i);return o===a?0:-1===o?1:-1===a?-1:o-a}},40404:function(e,t,i){i.d(t,{s:()=>o});const o=(e,t,i=!1)=>{let o;const a=(...a)=>{const r=i&&!o;clearTimeout(o),o=window.setTimeout((()=>{o=void 0,e(...a)}),t),r&&e(...a)};return a.cancel=()=>{clearTimeout(o)},a}},56830:function(e,t,i){i.d(t,{u:()=>o});class o{start(e){const t=Date.now();this._startY=e,this._startTime=t,this._lastY=e,this._lastTime=t,this._delta=0}move(e){const t=Date.now();return this._delta=this._startY-e,this._lastY=e,this._lastTime=t,this._delta}end(){const e=this.getVelocity(),t=Math.abs(e)>this._velocityThreshold;return{velocity:e,delta:this._delta,isSwipe:t,isDownwardSwipe:e>0}}getDelta(){return this._delta}getVelocity(){if(Date.now()-this._lastTime>=this._movementTimeThreshold)return 0;const e=this._lastTime-this._startTime;return e>0?(this._lastY-this._startY)/e:0}reset(){this._startY=0,this._delta=0,this._startTime=0,this._lastY=0,this._lastTime=0}constructor(e={}){this._startY=0,this._delta=0,this._startTime=0,this._lastY=0,this._lastTime=0,this._velocityThreshold=e.velocitySwipeThreshold??.5,this._movementTimeThreshold=e.movementTimeThreshold??100}}},96294:function(e,t,i){var o=i(62826),a=i(4720),r=i(77845);class s extends a.Y{}s=(0,o.__decorate)([(0,r.EM)("ha-chip-set")],s)},72434:function(e,t,i){var o=i(62826),a=i(42034),r=i(36034),s=i(40993),n=i(75640),l=i(91735),d=i(43826),c=i(96196),h=i(77845);class p extends r.${renderLeadingIcon(){return this.noLeadingIcon?c.qy``:super.renderLeadingIcon()}constructor(...e){super(...e),this.noLeadingIcon=!1}}p.styles=[l.R,a.R,d.R,n.R,s.R,c.AH`
      :host {
        --md-sys-color-primary: var(--primary-text-color);
        --md-sys-color-on-surface: var(--primary-text-color);
        --md-sys-color-on-surface-variant: var(--primary-text-color);
        --md-sys-color-on-secondary-container: var(--primary-text-color);
        --md-filter-chip-container-shape: 16px;
        --md-filter-chip-outline-color: var(--outline-color);
        --md-filter-chip-selected-container-color: rgba(
          var(--rgb-primary-text-color),
          0.15
        );
        --_label-text-font: var(--ha-font-family-body);
        border-radius: var(--ha-border-radius-md);
      }
    `],(0,o.__decorate)([(0,h.MZ)({type:Boolean,reflect:!0,attribute:"no-leading-icon"})],p.prototype,"noLeadingIcon",void 0),p=(0,o.__decorate)([(0,h.EM)("ha-filter-chip")],p)},17963:function(e,t,i){i.r(t);var o=i(62826),a=i(96196),r=i(77845),s=i(94333),n=i(92542);i(60733),i(60961);const l={info:"M11,9H13V7H11M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,17H13V11H11V17Z",warning:"M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16",error:"M11,15H13V17H11V15M11,7H13V13H11V7M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20Z",success:"M20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4C12.76,4 13.5,4.11 14.2,4.31L15.77,2.74C14.61,2.26 13.34,2 12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12M7.91,10.08L6.5,11.5L11,16L21,6L19.59,4.58L11,13.17L7.91,10.08Z"};class d extends a.WF{render(){return a.qy`
      <div
        class="issue-type ${(0,s.H)({[this.alertType]:!0})}"
        role="alert"
      >
        <div class="icon ${this.title?"":"no-title"}">
          <slot name="icon">
            <ha-svg-icon .path=${l[this.alertType]}></ha-svg-icon>
          </slot>
        </div>
        <div class=${(0,s.H)({content:!0,narrow:this.narrow})}>
          <div class="main-content">
            ${this.title?a.qy`<div class="title">${this.title}</div>`:a.s6}
            <slot></slot>
          </div>
          <div class="action">
            <slot name="action">
              ${this.dismissable?a.qy`<ha-icon-button
                    @click=${this._dismissClicked}
                    label="Dismiss alert"
                    .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
                  ></ha-icon-button>`:a.s6}
            </slot>
          </div>
        </div>
      </div>
    `}_dismissClicked(){(0,n.r)(this,"alert-dismissed-clicked")}constructor(...e){super(...e),this.title="",this.alertType="info",this.dismissable=!1,this.narrow=!1}}d.styles=a.AH`
    .issue-type {
      position: relative;
      padding: 8px;
      display: flex;
    }
    .icon {
      height: var(--ha-alert-icon-size, 24px);
      width: var(--ha-alert-icon-size, 24px);
    }
    .issue-type::after {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      opacity: 0.12;
      pointer-events: none;
      content: "";
      border-radius: var(--ha-border-radius-sm);
    }
    .icon.no-title {
      align-self: center;
    }
    .content {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      text-align: var(--float-start);
    }
    .content.narrow {
      flex-direction: column;
      align-items: flex-end;
    }
    .action {
      z-index: 1;
      width: min-content;
      --mdc-theme-primary: var(--primary-text-color);
    }
    .main-content {
      overflow-wrap: anywhere;
      word-break: break-word;
      line-height: normal;
      margin-left: 8px;
      margin-right: 0;
      margin-inline-start: 8px;
      margin-inline-end: 8px;
    }
    .title {
      margin-top: 2px;
      font-weight: var(--ha-font-weight-bold);
    }
    .action ha-icon-button {
      --mdc-theme-primary: var(--primary-text-color);
      --mdc-icon-button-size: 36px;
    }
    .issue-type.info > .icon {
      color: var(--info-color);
    }
    .issue-type.info::after {
      background-color: var(--info-color);
    }

    .issue-type.warning > .icon {
      color: var(--warning-color);
    }
    .issue-type.warning::after {
      background-color: var(--warning-color);
    }

    .issue-type.error > .icon {
      color: var(--error-color);
    }
    .issue-type.error::after {
      background-color: var(--error-color);
    }

    .issue-type.success > .icon {
      color: var(--success-color);
    }
    .issue-type.success::after {
      background-color: var(--success-color);
    }
    :host ::slotted(ul) {
      margin: 0;
      padding-inline-start: 20px;
    }
  `,(0,o.__decorate)([(0,r.MZ)()],d.prototype,"title",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"alert-type"})],d.prototype,"alertType",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],d.prototype,"dismissable",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],d.prototype,"narrow",void 0),d=(0,o.__decorate)([(0,r.EM)("ha-alert")],d)},53907:function(e,t,i){i.a(e,(async function(e,t){try{var o=i(62826),a=i(96196),r=i(77845),s=i(22786),n=i(92542),l=i(56403),d=i(41144),c=i(47644),h=i(48774),p=i(54110),u=i(1491),m=i(10234),_=i(82160),v=(i(94343),i(96943)),b=(i(60733),i(60961),e([v]));v=(b.then?(await b)():b)[0];const f="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",g="M20 2H4C2.9 2 2 2.9 2 4V20C2 21.11 2.9 22 4 22H20C21.11 22 22 21.11 22 20V4C22 2.9 21.11 2 20 2M4 6L6 4H10.9L4 10.9V6M4 13.7L13.7 4H18.6L4 18.6V13.7M20 18L18 20H13.1L20 13.1V18M20 10.3L10.3 20H5.4L20 5.4V10.3Z",y="___ADD_NEW___";class x extends a.WF{async open(){await this.updateComplete,await(this._picker?.open())}render(){const e=this.placeholder??this.hass.localize("ui.components.area-picker.area"),t=this._computeValueRenderer(this.hass.areas);return a.qy`
      <ha-generic-picker
        .hass=${this.hass}
        .autofocus=${this.autofocus}
        .label=${this.label}
        .helper=${this.helper}
        .notFoundLabel=${this._notFoundLabel}
        .emptyLabel=${this.hass.localize("ui.components.area-picker.no_areas")}
        .disabled=${this.disabled}
        .required=${this.required}
        .placeholder=${e}
        .value=${this.value}
        .getItems=${this._getItems}
        .getAdditionalItems=${this._getAdditionalItems}
        .valueRenderer=${t}
        .addButtonLabel=${this.addButtonLabel}
        @value-changed=${this._valueChanged}
      >
      </ha-generic-picker>
    `}_valueChanged(e){e.stopPropagation();const t=e.detail.value;if(t)if(t.startsWith(y)){this.hass.loadFragmentTranslation("config");const e=t.substring(y.length);(0,_.J)(this,{suggestedName:e,createEntry:async e=>{try{const t=await(0,p.L3)(this.hass,e);this._setValue(t.area_id)}catch(t){(0,m.K$)(this,{title:this.hass.localize("ui.components.area-picker.failed_create_area"),text:t.message})}}})}else this._setValue(t);else this._setValue(void 0)}_setValue(e){this.value=e,(0,n.r)(this,"value-changed",{value:e}),(0,n.r)(this,"change")}constructor(...e){super(...e),this.noAdd=!1,this.disabled=!1,this.required=!1,this._computeValueRenderer=(0,s.A)((e=>e=>{const t=this.hass.areas[e];if(!t)return a.qy`
            <ha-svg-icon slot="start" .path=${g}></ha-svg-icon>
            <span slot="headline">${t}</span>
          `;const{floor:i}=(0,h.L)(t,this.hass.floors),o=t?(0,l.A)(t):void 0,r=i?(0,c.X)(i):void 0,s=t.icon;return a.qy`
          ${s?a.qy`<ha-icon slot="start" .icon=${s}></ha-icon>`:a.qy`<ha-svg-icon
                slot="start"
                .path=${g}
              ></ha-svg-icon>`}
          <span slot="headline">${o}</span>
          ${r?a.qy`<span slot="supporting-text">${r}</span>`:a.s6}
        `})),this._getAreas=(0,s.A)(((e,t,i,o,a,r,s,n,p)=>{let m,_,v={};const b=Object.values(e),f=Object.values(t),y=Object.values(i);(o||a||r||s||n)&&(v=(0,u.g2)(y),m=f,_=y.filter((e=>e.area_id)),o&&(m=m.filter((e=>{const t=v[e.id];return!(!t||!t.length)&&v[e.id].some((e=>o.includes((0,d.m)(e.entity_id))))})),_=_.filter((e=>o.includes((0,d.m)(e.entity_id))))),a&&(m=m.filter((e=>{const t=v[e.id];return!t||!t.length||y.every((e=>!a.includes((0,d.m)(e.entity_id))))})),_=_.filter((e=>!a.includes((0,d.m)(e.entity_id))))),r&&(m=m.filter((e=>{const t=v[e.id];return!(!t||!t.length)&&v[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&(t.attributes.device_class&&r.includes(t.attributes.device_class))}))})),_=_.filter((e=>{const t=this.hass.states[e.entity_id];return t.attributes.device_class&&r.includes(t.attributes.device_class)}))),s&&(m=m.filter((e=>s(e)))),n&&(m=m.filter((e=>{const t=v[e.id];return!(!t||!t.length)&&v[e.id].some((e=>{const t=this.hass.states[e.entity_id];return!!t&&n(t)}))})),_=_.filter((e=>{const t=this.hass.states[e.entity_id];return!!t&&n(t)}))));let x,w=b;m&&(x=m.filter((e=>e.area_id)).map((e=>e.area_id))),_&&(x=(x??[]).concat(_.filter((e=>e.area_id)).map((e=>e.area_id)))),x&&(w=w.filter((e=>x.includes(e.area_id)))),p&&(w=w.filter((e=>!p.includes(e.area_id))));return w.map((e=>{const{floor:t}=(0,h.L)(e,this.hass.floors),i=t?(0,c.X)(t):void 0,o=(0,l.A)(e);return{id:e.area_id,primary:o||e.area_id,secondary:i,icon:e.icon||void 0,icon_path:e.icon?void 0:g,sorting_label:o,search_labels:[o,i,e.area_id,...e.aliases].filter((e=>Boolean(e)))}}))})),this._getItems=()=>this._getAreas(this.hass.areas,this.hass.devices,this.hass.entities,this.includeDomains,this.excludeDomains,this.includeDeviceClasses,this.deviceFilter,this.entityFilter,this.excludeAreas),this._allAreaNames=(0,s.A)((e=>Object.values(e).map((e=>(0,l.A)(e)?.toLowerCase())).filter(Boolean))),this._getAdditionalItems=e=>{if(this.noAdd)return[];const t=this._allAreaNames(this.hass.areas);return e&&!t.includes(e.toLowerCase())?[{id:y+e,primary:this.hass.localize("ui.components.area-picker.add_new_sugestion",{name:e}),icon_path:f}]:[{id:y,primary:this.hass.localize("ui.components.area-picker.add_new"),icon_path:f}]},this._notFoundLabel=e=>this.hass.localize("ui.components.area-picker.no_match",{term:a.qy`<b>‘${e}’</b>`})}}(0,o.__decorate)([(0,r.MZ)({attribute:!1})],x.prototype,"hass",void 0),(0,o.__decorate)([(0,r.MZ)()],x.prototype,"label",void 0),(0,o.__decorate)([(0,r.MZ)()],x.prototype,"value",void 0),(0,o.__decorate)([(0,r.MZ)()],x.prototype,"helper",void 0),(0,o.__decorate)([(0,r.MZ)()],x.prototype,"placeholder",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean,attribute:"no-add"})],x.prototype,"noAdd",void 0),(0,o.__decorate)([(0,r.MZ)({type:Array,attribute:"include-domains"})],x.prototype,"includeDomains",void 0),(0,o.__decorate)([(0,r.MZ)({type:Array,attribute:"exclude-domains"})],x.prototype,"excludeDomains",void 0),(0,o.__decorate)([(0,r.MZ)({type:Array,attribute:"include-device-classes"})],x.prototype,"includeDeviceClasses",void 0),(0,o.__decorate)([(0,r.MZ)({type:Array,attribute:"exclude-areas"})],x.prototype,"excludeAreas",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:!1})],x.prototype,"deviceFilter",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:!1})],x.prototype,"entityFilter",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],x.prototype,"disabled",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],x.prototype,"required",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"add-button-label"})],x.prototype,"addButtonLabel",void 0),(0,o.__decorate)([(0,r.P)("ha-generic-picker")],x.prototype,"_picker",void 0),x=(0,o.__decorate)([(0,r.EM)("ha-area-picker")],x),t()}catch(f){t(f)}}))},92312:function(e,t,i){i.a(e,(async function(e,t){try{var o=i(62826),a=i(1126),r=i(96196),s=i(77845),n=i(56830),l=i(39396),d=e([a]);a=(d.then?(await d)():d)[0];const c=300;class h extends r.WF{_handleAfterHide(e){e.stopPropagation(),this.open=!1;const t=new Event("closed",{bubbles:!0,composed:!0});this.dispatchEvent(t)}updated(e){super.updated(e),e.has("open")&&(this._drawerOpen=this.open)}render(){return r.qy`
      <wa-drawer
        id="drawer"
        placement="bottom"
        .open=${this._drawerOpen}
        @wa-after-hide=${this._handleAfterHide}
        without-header
        @touchstart=${this._handleTouchStart}
      >
        <slot name="header"></slot>
        <div id="body" class="body ha-scrollbar">
          <slot></slot>
        </div>
      </wa-drawer>
    `}_startResizing(e){document.addEventListener("touchmove",this._handleTouchMove,{passive:!1}),document.addEventListener("touchend",this._handleTouchEnd),document.addEventListener("touchcancel",this._handleTouchEnd),this._gestureRecognizer.start(e)}_animateSnapBack(){this.style.setProperty("--dialog-transition",`transform ${c}ms ease-out`),this.style.removeProperty("--dialog-transform"),setTimeout((()=>{this.style.removeProperty("--dialog-transition")}),c)}disconnectedCallback(){super.disconnectedCallback(),this._unregisterResizeHandlers(),this._isDragging=!1}constructor(...e){super(...e),this.open=!1,this.flexContent=!1,this._drawerOpen=!1,this._gestureRecognizer=new n.u,this._isDragging=!1,this._handleTouchStart=e=>{for(const t of e.composedPath()){const e=t;if(e===this._drawer)break;if(e.scrollTop>0)return}this._startResizing(e.touches[0].clientY)},this._handleTouchMove=e=>{const t=e.touches[0].clientY,i=this._gestureRecognizer.move(t);i<0&&(e.preventDefault(),this._isDragging=!0,requestAnimationFrame((()=>{this._isDragging&&this.style.setProperty("--dialog-transform",`translateY(${-1*i}px)`)})))},this._handleTouchEnd=()=>{this._unregisterResizeHandlers(),this._isDragging=!1;const e=this._gestureRecognizer.end();if(e.isSwipe)return void(e.isDownwardSwipe?this._drawerOpen=!1:this._animateSnapBack());const t=this._drawer.shadowRoot?.querySelector('[part="body"]'),i=t?.offsetHeight||0;i>0&&e.delta<0&&Math.abs(e.delta)>.5*i?this._drawerOpen=!1:this._animateSnapBack()},this._unregisterResizeHandlers=()=>{document.removeEventListener("touchmove",this._handleTouchMove),document.removeEventListener("touchend",this._handleTouchEnd),document.removeEventListener("touchcancel",this._handleTouchEnd)}}}h.styles=[l.dp,r.AH`
      wa-drawer {
        --wa-color-surface-raised: transparent;
        --spacing: 0;
        --size: var(--ha-bottom-sheet-height, auto);
        --show-duration: ${c}ms;
        --hide-duration: ${c}ms;
      }
      wa-drawer::part(dialog) {
        max-height: var(--ha-bottom-sheet-max-height, 90vh);
        align-items: center;
        transform: var(--dialog-transform);
        transition: var(--dialog-transition);
      }
      wa-drawer::part(body) {
        max-width: var(--ha-bottom-sheet-max-width);
        width: 100%;
        border-top-left-radius: var(
          --ha-bottom-sheet-border-radius,
          var(--ha-dialog-border-radius, var(--ha-border-radius-2xl))
        );
        border-top-right-radius: var(
          --ha-bottom-sheet-border-radius,
          var(--ha-dialog-border-radius, var(--ha-border-radius-2xl))
        );
        background-color: var(
          --ha-bottom-sheet-surface-background,
          var(--ha-dialog-surface-background, var(--mdc-theme-surface, #fff)),
        );
        padding: var(
          --ha-bottom-sheet-padding,
          0 var(--safe-area-inset-right) var(--safe-area-inset-bottom)
            var(--safe-area-inset-left)
        );
      }
      :host([flexcontent]) wa-drawer::part(body) {
        display: flex;
        flex-direction: column;
      }
      :host([flexcontent]) .body {
        flex: 1;
        max-width: 100%;
        display: flex;
        flex-direction: column;
        padding: var(
          --ha-bottom-sheet-padding,
          0 var(--safe-area-inset-right) var(--safe-area-inset-bottom)
            var(--safe-area-inset-left)
        );
      }
    `],(0,o.__decorate)([(0,s.MZ)({type:Boolean})],h.prototype,"open",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,reflect:!0,attribute:"flexcontent"})],h.prototype,"flexContent",void 0),(0,o.__decorate)([(0,s.wk)()],h.prototype,"_drawerOpen",void 0),(0,o.__decorate)([(0,s.P)("#drawer")],h.prototype,"_drawer",void 0),h=(0,o.__decorate)([(0,s.EM)("ha-bottom-sheet")],h),t()}catch(c){t(c)}}))},89473:function(e,t,i){i.a(e,(async function(e,t){try{var o=i(62826),a=i(88496),r=i(96196),s=i(77845),n=e([a]);a=(n.then?(await n)():n)[0];class l extends a.A{static get styles(){return[a.A.styles,r.AH`
        :host {
          --wa-form-control-padding-inline: 16px;
          --wa-font-weight-action: var(--ha-font-weight-medium);
          --wa-form-control-border-radius: var(
            --ha-button-border-radius,
            var(--ha-border-radius-pill)
          );

          --wa-form-control-height: var(
            --ha-button-height,
            var(--button-height, 40px)
          );
        }
        .button {
          font-size: var(--ha-font-size-m);
          line-height: 1;

          transition: background-color 0.15s ease-in-out;
          text-wrap: wrap;
        }

        :host([size="small"]) .button {
          --wa-form-control-height: var(
            --ha-button-height,
            var(--button-height, 32px)
          );
          font-size: var(--wa-font-size-s, var(--ha-font-size-m));
          --wa-form-control-padding-inline: 12px;
        }

        :host([variant="brand"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-primary-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-primary-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-primary-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-primary-loud-hover
          );
        }

        :host([variant="neutral"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-neutral-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-neutral-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-neutral-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-neutral-loud-hover
          );
        }

        :host([variant="success"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-success-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-success-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-success-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-success-loud-hover
          );
        }

        :host([variant="warning"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-warning-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-warning-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-warning-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-warning-loud-hover
          );
        }

        :host([variant="danger"]) {
          --button-color-fill-normal-active: var(
            --ha-color-fill-danger-normal-active
          );
          --button-color-fill-normal-hover: var(
            --ha-color-fill-danger-normal-hover
          );
          --button-color-fill-loud-active: var(
            --ha-color-fill-danger-loud-active
          );
          --button-color-fill-loud-hover: var(
            --ha-color-fill-danger-loud-hover
          );
        }

        :host([appearance~="plain"]) .button {
          color: var(--wa-color-on-normal);
          background-color: transparent;
        }
        :host([appearance~="plain"]) .button.disabled {
          background-color: transparent;
          color: var(--ha-color-on-disabled-quiet);
        }

        :host([appearance~="outlined"]) .button.disabled {
          background-color: transparent;
          color: var(--ha-color-on-disabled-quiet);
        }

        @media (hover: hover) {
          :host([appearance~="filled"])
            .button:not(.disabled):not(.loading):hover {
            background-color: var(--button-color-fill-normal-hover);
          }
          :host([appearance~="accent"])
            .button:not(.disabled):not(.loading):hover {
            background-color: var(--button-color-fill-loud-hover);
          }
          :host([appearance~="plain"])
            .button:not(.disabled):not(.loading):hover {
            color: var(--wa-color-on-normal);
          }
        }
        :host([appearance~="filled"]) .button {
          color: var(--wa-color-on-normal);
          background-color: var(--wa-color-fill-normal);
          border-color: transparent;
        }
        :host([appearance~="filled"])
          .button:not(.disabled):not(.loading):active {
          background-color: var(--button-color-fill-normal-active);
        }
        :host([appearance~="filled"]) .button.disabled {
          background-color: var(--ha-color-fill-disabled-normal-resting);
          color: var(--ha-color-on-disabled-normal);
        }

        :host([appearance~="accent"]) .button {
          background-color: var(
            --wa-color-fill-loud,
            var(--wa-color-neutral-fill-loud)
          );
        }
        :host([appearance~="accent"])
          .button:not(.disabled):not(.loading):active {
          background-color: var(--button-color-fill-loud-active);
        }
        :host([appearance~="accent"]) .button.disabled {
          background-color: var(--ha-color-fill-disabled-loud-resting);
          color: var(--ha-color-on-disabled-loud);
        }

        :host([loading]) {
          pointer-events: none;
        }

        .button.disabled {
          opacity: 1;
        }

        slot[name="start"]::slotted(*) {
          margin-inline-end: 4px;
        }
        slot[name="end"]::slotted(*) {
          margin-inline-start: 4px;
        }

        .button.has-start {
          padding-inline-start: 8px;
        }
        .button.has-end {
          padding-inline-end: 8px;
        }

        .label {
          overflow: hidden;
          text-overflow: ellipsis;
          padding: var(--ha-space-1) 0;
        }
      `]}constructor(...e){super(...e),this.variant="brand"}}l=(0,o.__decorate)([(0,s.EM)("ha-button")],l),t()}catch(l){t(l)}}))},94343:function(e,t,i){var o=i(62826),a=i(96196),r=i(77845),s=i(23897);class n extends s.G{constructor(...e){super(...e),this.borderTop=!1}}n.styles=[...s.J,a.AH`
      :host {
        --md-list-item-one-line-container-height: 48px;
        --md-list-item-two-line-container-height: 64px;
      }
      :host([border-top]) md-item {
        border-top: 1px solid var(--divider-color);
      }
      [slot="start"] {
        --state-icon-color: var(--secondary-text-color);
      }
      [slot="headline"] {
        line-height: var(--ha-line-height-normal);
        font-size: var(--ha-font-size-m);
        white-space: nowrap;
      }
      [slot="supporting-text"] {
        line-height: var(--ha-line-height-normal);
        font-size: var(--ha-font-size-s);
        white-space: nowrap;
      }
      ::slotted(state-badge),
      ::slotted(img) {
        width: 32px;
        height: 32px;
      }
      ::slotted(.code) {
        font-family: var(--ha-font-family-code);
        font-size: var(--ha-font-size-xs);
      }
      ::slotted(.domain) {
        font-size: var(--ha-font-size-s);
        font-weight: var(--ha-font-weight-normal);
        line-height: var(--ha-line-height-normal);
        align-self: flex-end;
        max-width: 30%;
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
      }
    `],(0,o.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0,attribute:"border-top"})],n.prototype,"borderTop",void 0),n=(0,o.__decorate)([(0,r.EM)("ha-combo-box-item")],n)},96943:function(e,t,i){i.a(e,(async function(e,t){try{var o=i(62826),a=i(61366),r=i(96196),s=i(77845),n=i(32288),l=i(57947),d=i(92542),c=i(92312),h=i(89473),p=(i(94343),i(56768),i(13208),i(74554),i(60961),e([a,c,h]));[a,c,h]=p.then?(await p)():p;const u="M3 16H10V14H3M18 14V10H16V14H12V16H16V20H18V16H22V14M14 6H3V8H14M14 10H3V12H14V10Z";class m extends r.WF{render(){return r.qy`
      ${this.label?r.qy`<label ?disabled=${this.disabled}>${this.label}</label>`:r.s6}
      <div class="container">
        <div id="picker">
          <slot name="field">
            ${this.addButtonLabel&&!this.value?r.qy`<ha-button
                  size="small"
                  appearance="filled"
                  @click=${this.open}
                  .disabled=${this.disabled}
                >
                  <ha-svg-icon
                    .path=${u}
                    slot="start"
                  ></ha-svg-icon>
                  ${this.addButtonLabel}
                </ha-button>`:r.qy`<ha-picker-field
                  type="button"
                  class=${this._opened?"opened":""}
                  compact
                  aria-label=${(0,n.J)(this.label)}
                  @click=${this.open}
                  @clear=${this._clear}
                  .placeholder=${this.placeholder}
                  .value=${this.value}
                  .required=${this.required}
                  .disabled=${this.disabled}
                  .hideClearIcon=${this.hideClearIcon}
                  .valueRenderer=${this.valueRenderer}
                >
                </ha-picker-field>`}
          </slot>
        </div>
        ${this._openedNarrow||!this._pickerWrapperOpen&&!this._opened?this._pickerWrapperOpen||this._opened?r.qy`<ha-bottom-sheet
                flexcontent
                .open=${this._pickerWrapperOpen}
                @wa-after-show=${this._dialogOpened}
                @closed=${this._hidePicker}
                role="dialog"
                aria-modal="true"
                aria-label=${this.label||"Select option"}
              >
                ${this._renderComboBox(!0)}
              </ha-bottom-sheet>`:r.s6:r.qy`
              <wa-popover
                .open=${this._pickerWrapperOpen}
                style="--body-width: ${this._popoverWidth}px;"
                without-arrow
                distance="-4"
                .placement=${this.popoverPlacement}
                for="picker"
                auto-size="vertical"
                auto-size-padding="16"
                @wa-after-show=${this._dialogOpened}
                @wa-after-hide=${this._hidePicker}
                trap-focus
                role="dialog"
                aria-modal="true"
                aria-label=${this.label||"Select option"}
              >
                ${this._renderComboBox()}
              </wa-popover>
            `}
      </div>
      ${this._renderHelper()}
    `}_renderComboBox(e=!1){return this._opened?r.qy`
      <ha-picker-combo-box
        .hass=${this.hass}
        .allowCustomValue=${this.allowCustomValue}
        .label=${this.searchLabel}
        .value=${this.value}
        @value-changed=${this._valueChanged}
        .rowRenderer=${this.rowRenderer}
        .notFoundLabel=${this.notFoundLabel}
        .emptyLabel=${this.emptyLabel}
        .getItems=${this.getItems}
        .getAdditionalItems=${this.getAdditionalItems}
        .searchFn=${this.searchFn}
        .mode=${e?"dialog":"popover"}
        .sections=${this.sections}
        .sectionTitleFunction=${this.sectionTitleFunction}
        .selectedSection=${this.selectedSection}
      ></ha-picker-combo-box>
    `:r.s6}_renderHelper(){return this.helper?r.qy`<ha-input-helper-text .disabled=${this.disabled}
          >${this.helper}</ha-input-helper-text
        >`:r.s6}_hidePicker(e){e.stopPropagation(),this._newValue&&((0,d.r)(this,"value-changed",{value:this._newValue}),this._newValue=void 0),this._opened=!1,this._pickerWrapperOpen=!1,this._unsubscribeTinyKeys?.()}_valueChanged(e){e.stopPropagation();const t=e.detail.value;t&&(this._pickerWrapperOpen=!1,this._newValue=t)}_clear(e){e.stopPropagation(),this._setValue(void 0)}_setValue(e){this.value=e,(0,d.r)(this,"value-changed",{value:e})}async open(e){e?.stopPropagation(),this.disabled||(this._openedNarrow=this._narrow,this._popoverWidth=this._containerElement?.offsetWidth||250,this._pickerWrapperOpen=!0,this._unsubscribeTinyKeys=(0,l.Tc)(this,{Escape:this._handleEscClose}))}connectedCallback(){super.connectedCallback(),this._handleResize(),window.addEventListener("resize",this._handleResize)}disconnectedCallback(){super.disconnectedCallback(),window.removeEventListener("resize",this._handleResize),this._unsubscribeTinyKeys?.()}static get styles(){return[r.AH`
        .container {
          position: relative;
          display: block;
        }
        label[disabled] {
          color: var(--mdc-text-field-disabled-ink-color, rgba(0, 0, 0, 0.6));
        }
        label {
          display: block;
          margin: 0 0 8px;
        }
        ha-input-helper-text {
          display: block;
          margin: var(--ha-space-2) 0 0;
        }

        wa-popover {
          --wa-space-l: var(--ha-space-0);
        }

        wa-popover::part(body) {
          width: max(var(--body-width), 250px);
          max-width: max(var(--body-width), 250px);
          max-height: 500px;
          height: 70vh;
          overflow: hidden;
        }

        @media (max-height: 1000px) {
          wa-popover::part(body) {
            max-height: 400px;
          }
        }

        @media (max-height: 1000px) {
          wa-popover::part(body) {
            max-height: 400px;
          }
        }

        ha-bottom-sheet {
          --ha-bottom-sheet-height: 90vh;
          --ha-bottom-sheet-height: calc(100dvh - var(--ha-space-12));
          --ha-bottom-sheet-max-height: var(--ha-bottom-sheet-height);
          --ha-bottom-sheet-max-width: 600px;
          --ha-bottom-sheet-padding: var(--ha-space-0);
          --ha-bottom-sheet-surface-background: var(--card-background-color);
          --ha-bottom-sheet-border-radius: var(--ha-border-radius-2xl);
        }

        ha-picker-field.opened {
          --mdc-text-field-idle-line-color: var(--primary-color);
        }
      `]}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.hideClearIcon=!1,this.popoverPlacement="bottom-start",this._opened=!1,this._pickerWrapperOpen=!1,this._popoverWidth=0,this._openedNarrow=!1,this._narrow=!1,this._dialogOpened=()=>{this._opened=!0,requestAnimationFrame((()=>{this._comboBox?.focus()}))},this._handleResize=()=>{this._narrow=window.matchMedia("(max-width: 870px)").matches||window.matchMedia("(max-height: 500px)").matches,!this._openedNarrow&&this._pickerWrapperOpen&&(this._popoverWidth=this._containerElement?.offsetWidth||250)},this._handleEscClose=e=>{e.stopPropagation()}}}m.shadowRootOptions={...r.WF.shadowRootOptions,delegatesFocus:!0},(0,o.__decorate)([(0,s.MZ)({attribute:!1})],m.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],m.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],m.prototype,"required",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"allow-custom-value"})],m.prototype,"allowCustomValue",void 0),(0,o.__decorate)([(0,s.MZ)()],m.prototype,"label",void 0),(0,o.__decorate)([(0,s.MZ)()],m.prototype,"value",void 0),(0,o.__decorate)([(0,s.MZ)()],m.prototype,"helper",void 0),(0,o.__decorate)([(0,s.MZ)()],m.prototype,"placeholder",void 0),(0,o.__decorate)([(0,s.MZ)({type:String,attribute:"search-label"})],m.prototype,"searchLabel",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"hide-clear-icon",type:Boolean})],m.prototype,"hideClearIcon",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],m.prototype,"getItems",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1,type:Array})],m.prototype,"getAdditionalItems",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],m.prototype,"rowRenderer",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],m.prototype,"valueRenderer",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],m.prototype,"searchFn",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],m.prototype,"notFoundLabel",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"empty-label"})],m.prototype,"emptyLabel",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"popover-placement"})],m.prototype,"popoverPlacement",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"add-button-label"})],m.prototype,"addButtonLabel",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],m.prototype,"sections",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],m.prototype,"sectionTitleFunction",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"selected-section"})],m.prototype,"selectedSection",void 0),(0,o.__decorate)([(0,s.P)(".container")],m.prototype,"_containerElement",void 0),(0,o.__decorate)([(0,s.P)("ha-picker-combo-box")],m.prototype,"_comboBox",void 0),(0,o.__decorate)([(0,s.wk)()],m.prototype,"_opened",void 0),(0,o.__decorate)([(0,s.wk)()],m.prototype,"_pickerWrapperOpen",void 0),(0,o.__decorate)([(0,s.wk)()],m.prototype,"_popoverWidth",void 0),(0,o.__decorate)([(0,s.wk)()],m.prototype,"_openedNarrow",void 0),m=(0,o.__decorate)([(0,s.EM)("ha-generic-picker")],m),t()}catch(u){t(u)}}))},56768:function(e,t,i){var o=i(62826),a=i(96196),r=i(77845);class s extends a.WF{render(){return a.qy`<slot></slot>`}constructor(...e){super(...e),this.disabled=!1}}s.styles=a.AH`
    :host {
      display: block;
      color: var(--mdc-text-field-label-ink-color, rgba(0, 0, 0, 0.6));
      font-size: 0.75rem;
      padding-left: 16px;
      padding-right: 16px;
      padding-inline-start: 16px;
      padding-inline-end: 16px;
      letter-spacing: var(
        --mdc-typography-caption-letter-spacing,
        0.0333333333em
      );
      line-height: normal;
    }
    :host([disabled]) {
      color: var(--mdc-text-field-disabled-ink-color, rgba(0, 0, 0, 0.6));
    }
  `,(0,o.__decorate)([(0,r.MZ)({type:Boolean,reflect:!0})],s.prototype,"disabled",void 0),s=(0,o.__decorate)([(0,r.EM)("ha-input-helper-text")],s)},56565:function(e,t,i){var o=i(62826),a=i(27686),r=i(7731),s=i(96196),n=i(77845);class l extends a.J{renderRipple(){return this.noninteractive?"":super.renderRipple()}static get styles(){return[r.R,s.AH`
        :host {
          padding-left: var(
            --mdc-list-side-padding-left,
            var(--mdc-list-side-padding, 20px)
          );
          padding-inline-start: var(
            --mdc-list-side-padding-left,
            var(--mdc-list-side-padding, 20px)
          );
          padding-right: var(
            --mdc-list-side-padding-right,
            var(--mdc-list-side-padding, 20px)
          );
          padding-inline-end: var(
            --mdc-list-side-padding-right,
            var(--mdc-list-side-padding, 20px)
          );
        }
        :host([graphic="avatar"]:not([twoLine])),
        :host([graphic="icon"]:not([twoLine])) {
          height: 48px;
        }
        span.material-icons:first-of-type {
          margin-inline-start: 0px !important;
          margin-inline-end: var(
            --mdc-list-item-graphic-margin,
            16px
          ) !important;
          direction: var(--direction) !important;
        }
        span.material-icons:last-of-type {
          margin-inline-start: auto !important;
          margin-inline-end: 0px !important;
          direction: var(--direction) !important;
        }
        .mdc-deprecated-list-item__meta {
          display: var(--mdc-list-item-meta-display);
          align-items: center;
          flex-shrink: 0;
        }
        :host([graphic="icon"]:not([twoline]))
          .mdc-deprecated-list-item__graphic {
          margin-inline-end: var(
            --mdc-list-item-graphic-margin,
            20px
          ) !important;
        }
        :host([multiline-secondary]) {
          height: auto;
        }
        :host([multiline-secondary]) .mdc-deprecated-list-item__text {
          padding: 8px 0;
        }
        :host([multiline-secondary]) .mdc-deprecated-list-item__secondary-text {
          text-overflow: initial;
          white-space: normal;
          overflow: auto;
          display: inline-block;
          margin-top: 10px;
        }
        :host([multiline-secondary]) .mdc-deprecated-list-item__primary-text {
          margin-top: 10px;
        }
        :host([multiline-secondary])
          .mdc-deprecated-list-item__secondary-text::before {
          display: none;
        }
        :host([multiline-secondary])
          .mdc-deprecated-list-item__primary-text::before {
          display: none;
        }
        :host([disabled]) {
          color: var(--disabled-text-color);
        }
        :host([noninteractive]) {
          pointer-events: unset;
        }
      `,"rtl"===document.dir?s.AH`
            span.material-icons:first-of-type,
            span.material-icons:last-of-type {
              direction: rtl !important;
              --direction: rtl;
            }
          `:s.AH``]}}l=(0,o.__decorate)([(0,n.EM)("ha-list-item")],l)},13208:function(e,t,i){var o=i(62826),a=i(78648),r=i(96196),s=i(77845),n=i(22786),l=i(57947),d=i(92542),c=i(25749),h=i(69847),p=i(39396),u=i(84183);i(96294),i(72434),i(94343),i(22598),i(78740);const m="___no_items_available___",_=e=>r.qy`
  <ha-combo-box-item type="button" compact>
    ${e.icon?r.qy`<ha-icon slot="start" .icon=${e.icon}></ha-icon>`:e.icon_path?r.qy`<ha-svg-icon slot="start" .path=${e.icon_path}></ha-svg-icon>`:r.s6}
    <span slot="headline">${e.primary}</span>
    ${e.secondary?r.qy`<span slot="supporting-text">${e.secondary}</span>`:r.s6}
  </ha-combo-box-item>
`;class v extends r.WF{firstUpdated(){this._registerKeyboardShortcuts()}willUpdate(){this.hasUpdated||((0,u.i)(),this._allItems=this._getItems(),this._items=this._allItems)}disconnectedCallback(){super.disconnectedCallback(),this._removeKeyboardShortcuts?.()}render(){return r.qy`<ha-textfield
        .label=${this.label??this.hass?.localize("ui.common.search")??"Search"}
        @input=${this._filterChanged}
      ></ha-textfield>
      ${this._renderSectionButtons()}
      ${this.sections?.length?r.qy`
            <div class="section-title-wrapper">
              <div
                class="section-title ${!this.selectedSection&&this._sectionTitle?"show":""}"
              >
                ${this._sectionTitle}
              </div>
            </div>
          `:r.s6}
      <lit-virtualizer
        .keyFunction=${this._keyFunction}
        tabindex="0"
        scroller
        .items=${this._items}
        .renderItem=${this._renderItem}
        style="min-height: 36px;"
        class=${this._listScrolled?"scrolled":""}
        @scroll=${this._onScrollList}
        @focus=${this._focusList}
        @visibilityChanged=${this._visibilityChanged}
      >
      </lit-virtualizer>`}_renderSectionButtons(){return this.sections&&0!==this.sections.length?r.qy`
      <ha-chip-set class="sections">
        ${this.sections.map((e=>"separator"===e?r.qy`<div class="separator"></div>`:r.qy`<ha-filter-chip
                @click=${this._toggleSection}
                .section-id=${e.id}
                .selected=${this.selectedSection===e.id}
                .label=${e.label}
              >
              </ha-filter-chip>`))}
      </ha-chip-set>
    `:r.s6}_visibilityChanged(e){if(this._virtualizerElement&&this.sectionTitleFunction&&this.sections?.length){const t=this._virtualizerElement.items[e.first],i=this._virtualizerElement.items[e.first+1];this._sectionTitle=this.sectionTitleFunction({firstIndex:e.first,lastIndex:e.last,firstItem:t,secondItem:i,itemsCount:this._virtualizerElement.items.length})}}_onScrollList(e){const t=e.target.scrollTop??0;this._listScrolled=t>0}get _value(){return this.value||""}_toggleSection(e){e.stopPropagation(),this._resetSelectedItem(),this._sectionTitle=void 0;const t=e.target["section-id"];t&&(this.selectedSection===t?this.selectedSection=void 0:this.selectedSection=t,this._items=this._getItems(),this._virtualizerElement&&this._virtualizerElement.scrollToIndex(0))}_registerKeyboardShortcuts(){this._removeKeyboardShortcuts=(0,l.Tc)(this,{ArrowUp:this._selectPreviousItem,ArrowDown:this._selectNextItem,Home:this._selectFirstItem,End:this._selectLastItem,Enter:this._pickSelectedItem})}_focusList(){-1===this._selectedItemIndex&&this._selectNextItem()}_resetSelectedItem(){this._virtualizerElement?.querySelector(".selected")?.classList.remove("selected"),this._selectedItemIndex=-1}constructor(...e){super(...e),this.autofocus=!1,this.disabled=!1,this.required=!1,this._listScrolled=!1,this.mode="popover",this._items=[],this._allItems=[],this._selectedItemIndex=-1,this._search="",this._getAdditionalItems=e=>this.getAdditionalItems?.(e)||[],this._getItems=()=>{let e=[...this.getItems?this.getItems(this._search,this.selectedSection):[]];this.sections?.length||(e=e.sort(((e,t)=>(0,c.SH)(e.sorting_label,t.sorting_label,this.hass?.locale.language??navigator.language)))),e.length||e.push(m);const t=this._getAdditionalItems();return e.push(...t),"dialog"===this.mode&&e.push("padding"),e},this._renderItem=(e,t)=>{if("padding"===e)return r.qy`<div class="bottom-padding"></div>`;if(e===m)return r.qy`
        <div class="combo-box-row">
          <ha-combo-box-item type="text" compact>
            <ha-svg-icon
              slot="start"
              .path=${this._search?"M9.5,3A6.5,6.5 0 0,1 16,9.5C16,11.11 15.41,12.59 14.44,13.73L14.71,14H15.5L20.5,19L19,20.5L14,15.5V14.71L13.73,14.44C12.59,15.41 11.11,16 9.5,16A6.5,6.5 0 0,1 3,9.5A6.5,6.5 0 0,1 9.5,3M9.5,5C7,5 5,7 5,9.5C5,12 7,14 9.5,14C12,14 14,12 14,9.5C14,7 12,5 9.5,5Z":"M19,19V5H5V19H19M19,3A2,2 0 0,1 21,5V19A2,2 0 0,1 19,21H5A2,2 0 0,1 3,19V5C3,3.89 3.9,3 5,3H19M17,11V13H7V11H17Z"}
            ></ha-svg-icon>
            <span slot="headline"
              >${this._search?"function"==typeof this.notFoundLabel?this.notFoundLabel(this._search):this.notFoundLabel||this.hass?.localize("ui.components.combo-box.no_match")||"No matching items found":this.emptyLabel||this.hass?.localize("ui.components.combo-box.no_items")||"No items available"}</span
            >
          </ha-combo-box-item>
        </div>
      `;if("string"==typeof e)return r.qy`<div class="title">${e}</div>`;const i=this.rowRenderer||_;return r.qy`<div
      id=${`list-item-${t}`}
      class="combo-box-row ${this._value===e.id?"current-value":""}"
      .value=${e.id}
      .index=${t}
      @click=${this._valueSelected}
    >
      ${i(e,t)}
    </div>`},this._valueSelected=e=>{e.stopPropagation();const t=e.currentTarget.value,i=t?.trim();(0,d.r)(this,"value-changed",{value:i})},this._fuseIndex=(0,n.A)((e=>a.A.createIndex(["search_labels"],e))),this._filterChanged=e=>{const t=e.target.value.trim();if(this._search=t,this.sections?.length)this._items=this._getItems();else{if(!t)return void(this._items=this._allItems);const e=this._fuseIndex(this._allItems),i=new h.b(this._allItems,{shouldSort:!1,minMatchCharLength:Math.min(t.length,2)},e).multiTermsSearch(t);let o=[...this._allItems];if(i){const e=i.map((e=>e.item));e.length||o.push(m);const t=this._getAdditionalItems();e.push(...t),o=e}this.searchFn&&(o=this.searchFn(t,o,this._allItems)),this._items=o}this._selectedItemIndex=-1,this._virtualizerElement&&this._virtualizerElement.scrollTo(0,0)},this._selectNextItem=e=>{if(e?.stopPropagation(),e?.preventDefault(),!this._virtualizerElement)return;this._searchFieldElement?.focus();const t=this._virtualizerElement.items,i=t.length-1;if(-1===i)return void this._resetSelectedItem();const o=i===this._selectedItemIndex?this._selectedItemIndex:this._selectedItemIndex+1;if(t[o]){if("string"==typeof t[o]){if(o===i)return;this._selectedItemIndex=o+1}else this._selectedItemIndex=o;this._scrollToSelectedItem()}},this._selectPreviousItem=e=>{if(e.stopPropagation(),e.preventDefault(),this._virtualizerElement&&this._selectedItemIndex>0){const e=this._selectedItemIndex-1,t=this._virtualizerElement.items;if(!t[e])return;if("string"==typeof t[e]){if(0===e)return;this._selectedItemIndex=e-1}else this._selectedItemIndex=e;this._scrollToSelectedItem()}},this._selectFirstItem=e=>{if(e.stopPropagation(),!this._virtualizerElement||!this._virtualizerElement.items.length)return;"string"==typeof this._virtualizerElement.items[0]?this._selectedItemIndex=1:this._selectedItemIndex=0,this._scrollToSelectedItem()},this._selectLastItem=e=>{if(e.stopPropagation(),!this._virtualizerElement||!this._virtualizerElement.items.length)return;const t=this._virtualizerElement.items.length-1;"string"==typeof this._virtualizerElement.items[t]?this._selectedItemIndex=t-1:this._selectedItemIndex=t,this._scrollToSelectedItem()},this._scrollToSelectedItem=()=>{this._virtualizerElement?.querySelector(".selected")?.classList.remove("selected"),this._virtualizerElement?.scrollToIndex(this._selectedItemIndex,"end"),requestAnimationFrame((()=>{this._virtualizerElement?.querySelector(`#list-item-${this._selectedItemIndex}`)?.classList.add("selected")}))},this._pickSelectedItem=e=>{e.stopPropagation();const t=this._virtualizerElement?.items[0];if(1===this._virtualizerElement?.items.length&&(0,d.r)(this,"value-changed",{value:t.id}),-1===this._selectedItemIndex)return;e.preventDefault();const i=this._virtualizerElement?.items[this._selectedItemIndex];i&&(0,d.r)(this,"value-changed",{value:i.id})},this._keyFunction=e=>"string"==typeof e?e:e.id}}v.shadowRootOptions={...r.WF.shadowRootOptions,delegatesFocus:!0},v.styles=[p.dp,r.AH`
      :host {
        display: flex;
        flex-direction: column;
        padding-top: var(--ha-space-3);
        flex: 1;
      }

      ha-textfield {
        padding: 0 var(--ha-space-3);
        margin-bottom: var(--ha-space-3);
      }

      :host([mode="dialog"]) ha-textfield {
        padding: 0 var(--ha-space-4);
      }

      ha-combo-box-item {
        width: 100%;
      }

      ha-combo-box-item.selected {
        background-color: var(--ha-color-fill-neutral-quiet-hover);
      }

      @media (prefers-color-scheme: dark) {
        ha-combo-box-item.selected {
          background-color: var(--ha-color-fill-neutral-normal-hover);
        }
      }

      lit-virtualizer {
        flex: 1;
      }

      lit-virtualizer:focus-visible {
        outline: none;
      }

      lit-virtualizer.scrolled {
        border-top: 1px solid var(--ha-color-border-neutral-quiet);
      }

      .bottom-padding {
        height: max(var(--safe-area-inset-bottom, 0px), var(--ha-space-8));
        width: 100%;
      }

      .empty {
        text-align: center;
      }

      .combo-box-row {
        display: flex;
        width: 100%;
        align-items: center;
        box-sizing: border-box;
        min-height: 36px;
      }
      .combo-box-row.current-value {
        background-color: var(--ha-color-fill-primary-quiet-resting);
      }

      .combo-box-row.selected {
        background-color: var(--ha-color-fill-neutral-quiet-hover);
      }

      @media (prefers-color-scheme: dark) {
        .combo-box-row.selected {
          background-color: var(--ha-color-fill-neutral-normal-hover);
        }
      }

      .sections {
        display: flex;
        flex-wrap: nowrap;
        gap: var(--ha-space-2);
        padding: var(--ha-space-3) var(--ha-space-3);
        overflow: auto;
      }

      :host([mode="dialog"]) .sections {
        padding: var(--ha-space-3) var(--ha-space-4);
      }

      .sections ha-filter-chip {
        flex-shrink: 0;
        --md-filter-chip-selected-container-color: var(
          --ha-color-fill-primary-normal-hover
        );
        color: var(--primary-color);
      }

      .sections .separator {
        height: var(--ha-space-8);
        width: 0;
        border: 1px solid var(--ha-color-border-neutral-quiet);
      }

      .section-title,
      .title {
        background-color: var(--ha-color-fill-neutral-quiet-resting);
        padding: var(--ha-space-1) var(--ha-space-2);
        font-weight: var(--ha-font-weight-bold);
        color: var(--secondary-text-color);
        min-height: var(--ha-space-6);
        display: flex;
        align-items: center;
      }

      .title {
        width: 100%;
      }

      :host([mode="dialog"]) .title {
        padding: var(--ha-space-1) var(--ha-space-4);
      }

      :host([mode="dialog"]) ha-textfield {
        padding: 0 var(--ha-space-4);
      }

      .section-title-wrapper {
        height: 0;
        position: relative;
      }

      .section-title {
        opacity: 0;
        position: absolute;
        top: 1px;
        width: calc(100% - var(--ha-space-8));
      }

      .section-title.show {
        opacity: 1;
        z-index: 1;
      }

      .empty-search {
        display: flex;
        width: 100%;
        flex-direction: column;
        align-items: center;
        padding: var(--ha-space-3);
      }
    `],(0,o.__decorate)([(0,s.MZ)({attribute:!1})],v.prototype,"hass",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],v.prototype,"autofocus",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],v.prototype,"disabled",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean})],v.prototype,"required",void 0),(0,o.__decorate)([(0,s.MZ)({type:Boolean,attribute:"allow-custom-value"})],v.prototype,"allowCustomValue",void 0),(0,o.__decorate)([(0,s.MZ)()],v.prototype,"label",void 0),(0,o.__decorate)([(0,s.MZ)()],v.prototype,"value",void 0),(0,o.__decorate)([(0,s.wk)()],v.prototype,"_listScrolled",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],v.prototype,"getItems",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1,type:Array})],v.prototype,"getAdditionalItems",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],v.prototype,"rowRenderer",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],v.prototype,"notFoundLabel",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"empty-label"})],v.prototype,"emptyLabel",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],v.prototype,"searchFn",void 0),(0,o.__decorate)([(0,s.MZ)({reflect:!0})],v.prototype,"mode",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],v.prototype,"sections",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:!1})],v.prototype,"sectionTitleFunction",void 0),(0,o.__decorate)([(0,s.MZ)({attribute:"selected-section"})],v.prototype,"selectedSection",void 0),(0,o.__decorate)([(0,s.P)("lit-virtualizer")],v.prototype,"_virtualizerElement",void 0),(0,o.__decorate)([(0,s.P)("ha-textfield")],v.prototype,"_searchFieldElement",void 0),(0,o.__decorate)([(0,s.wk)()],v.prototype,"_items",void 0),(0,o.__decorate)([(0,s.wk)()],v.prototype,"_sectionTitle",void 0),(0,o.__decorate)([(0,s.Ls)({passive:!0})],v.prototype,"_visibilityChanged",null),(0,o.__decorate)([(0,s.Ls)({passive:!0})],v.prototype,"_onScrollList",null),v=(0,o.__decorate)([(0,s.EM)("ha-picker-combo-box")],v)},74554:function(e,t,i){var o=i(62826),a=i(96196),r=i(77845),s=i(92542);i(94343),i(60733);class n extends a.WF{async focus(){await this.updateComplete,await(this.item?.focus())}render(){const e=!(!this.value||this.required||this.disabled||this.hideClearIcon);return a.qy`
      <ha-combo-box-item .disabled=${this.disabled} type="button" compact>
        ${this.value?this.valueRenderer?this.valueRenderer(this.value):a.qy`<slot name="headline">${this.value}</slot>`:a.qy`
              <span slot="headline" class="placeholder">
                ${this.placeholder}
              </span>
            `}
        ${e?a.qy`
              <ha-icon-button
                class="clear"
                slot="end"
                @click=${this._clear}
                .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
              ></ha-icon-button>
            `:a.s6}
        <ha-svg-icon
          class="arrow"
          slot="end"
          .path=${"M7,10L12,15L17,10H7Z"}
        ></ha-svg-icon>
      </ha-combo-box-item>
    `}_clear(e){e.stopPropagation(),(0,s.r)(this,"clear")}static get styles(){return[a.AH`
        ha-combo-box-item[disabled] {
          background-color: var(
            --mdc-text-field-disabled-fill-color,
            whitesmoke
          );
        }
        ha-combo-box-item {
          background-color: var(--mdc-text-field-fill-color, whitesmoke);
          border-radius: var(--ha-border-radius-sm);
          border-end-end-radius: 0;
          border-end-start-radius: 0;
          --md-list-item-one-line-container-height: 56px;
          --md-list-item-two-line-container-height: 56px;
          --md-list-item-top-space: 0px;
          --md-list-item-bottom-space: 0px;
          --md-list-item-leading-space: 8px;
          --md-list-item-trailing-space: 8px;
          --ha-md-list-item-gap: var(--ha-space-2);
          /* Remove the default focus ring */
          --md-focus-ring-width: 0px;
          --md-focus-ring-duration: 0s;
        }

        /* Add Similar focus style as the text field */
        ha-combo-box-item[disabled]:after {
          background-color: var(
            --mdc-text-field-disabled-line-color,
            rgba(0, 0, 0, 0.42)
          );
        }
        ha-combo-box-item:after {
          display: block;
          content: "";
          position: absolute;
          pointer-events: none;
          bottom: 0;
          left: 0;
          right: 0;
          height: 1px;
          width: 100%;
          background-color: var(
            --mdc-text-field-idle-line-color,
            rgba(0, 0, 0, 0.42)
          );
          transform:
            height 180ms ease-in-out,
            background-color 180ms ease-in-out;
        }

        ha-combo-box-item:focus:after {
          height: 2px;
          background-color: var(--mdc-theme-primary);
        }

        .clear {
          margin: 0 -8px;
          --mdc-icon-button-size: 32px;
          --mdc-icon-size: 20px;
        }
        .arrow {
          --mdc-icon-size: 20px;
          width: 32px;
        }

        .placeholder {
          color: var(--secondary-text-color);
          padding: 0 8px;
        }
      `]}constructor(...e){super(...e),this.disabled=!1,this.required=!1,this.hideClearIcon=!1}}(0,o.__decorate)([(0,r.MZ)({type:Boolean})],n.prototype,"disabled",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],n.prototype,"required",void 0),(0,o.__decorate)([(0,r.MZ)()],n.prototype,"value",void 0),(0,o.__decorate)([(0,r.MZ)()],n.prototype,"helper",void 0),(0,o.__decorate)([(0,r.MZ)()],n.prototype,"placeholder",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:"hide-clear-icon",type:Boolean})],n.prototype,"hideClearIcon",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:!1})],n.prototype,"valueRenderer",void 0),(0,o.__decorate)([(0,r.P)("ha-combo-box-item",!0)],n.prototype,"item",void 0),n=(0,o.__decorate)([(0,r.EM)("ha-picker-field")],n)},87156:function(e,t,i){var o=i(62826),a=i(96196),r=i(77845),s=i(22786),n=i(51757),l=i(82694);const d={action:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("8477"),i.e("2016"),i.e("5010"),i.e("2130"),i.e("8261"),i.e("4899"),i.e("5611"),i.e("9058"),i.e("2132"),i.e("4398"),i.e("5633"),i.e("1557"),i.e("2757"),i.e("3777"),i.e("4183"),i.e("3538"),i.e("9986"),i.e("6935"),i.e("5600")]).then(i.bind(i,35219)),addon:()=>Promise.all([i.e("8654"),i.e("5946")]).then(i.bind(i,41944)),area:()=>i.e("1417").then(i.bind(i,87888)),areas_display:()=>i.e("8496").then(i.bind(i,15219)),attribute:()=>Promise.all([i.e("8654"),i.e("8327")]).then(i.bind(i,99903)),assist_pipeline:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("2562")]).then(i.bind(i,83353)),boolean:()=>Promise.all([i.e("2736"),i.e("3038")]).then(i.bind(i,6061)),color_rgb:()=>i.e("3505").then(i.bind(i,1048)),condition:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("8477"),i.e("2016"),i.e("5010"),i.e("2130"),i.e("8261"),i.e("5611"),i.e("9058"),i.e("4398"),i.e("5633"),i.e("1557"),i.e("2757"),i.e("4183"),i.e("9986"),i.e("8817")]).then(i.bind(i,84748)),config_entry:()=>Promise.all([i.e("8654"),i.e("5769")]).then(i.bind(i,1629)),conversation_agent:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("8061"),i.e("3295")]).then(i.bind(i,73796)),constant:()=>i.e("4038").then(i.bind(i,28053)),country:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("3104")]).then(i.bind(i,17875)),date:()=>i.e("5494").then(i.bind(i,22421)),datetime:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("2478"),i.e("6045")]).then(i.bind(i,86284)),device:()=>i.e("2816").then(i.bind(i,95907)),duration:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("3777"),i.e("9115")]).then(i.bind(i,53089)),entity:()=>Promise.all([i.e("4398"),i.e("5633"),i.e("2757"),i.e("8651")]).then(i.bind(i,25394)),entity_name:()=>Promise.all([i.e("2239"),i.e("8654"),i.e("3571"),i.e("6080")]).then(i.bind(i,27891)),statistic:()=>Promise.all([i.e("4398"),i.e("5633"),i.e("3012")]).then(i.bind(i,10675)),file:()=>i.e("7636").then(i.bind(i,74575)),floor:()=>i.e("4468").then(i.bind(i,31631)),label:()=>Promise.all([i.e("7360"),i.e("7298"),i.e("3005")]).then(i.bind(i,39623)),language:()=>i.e("3488").then(i.bind(i,48227)),navigation:()=>Promise.all([i.e("8654"),i.e("9853"),i.e("5960")]).then(i.bind(i,79691)),number:()=>Promise.all([i.e("1543"),i.e("8881")]).then(i.bind(i,95096)),object:()=>Promise.all([i.e("5010"),i.e("2130"),i.e("1557"),i.e("3428")]).then(i.bind(i,22606)),qr_code:()=>Promise.all([i.e("1343"),i.e("4755")]).then(i.bind(i,414)),select:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("8654"),i.e("8477"),i.e("1279"),i.e("4933"),i.e("5186")]).then(i.bind(i,70105)),selector:()=>i.e("1850").then(i.bind(i,49100)),state:()=>Promise.all([i.e("8654"),i.e("7335")]).then(i.bind(i,6159)),backup_location:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("1656")]).then(i.bind(i,66971)),stt:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("4821")]).then(i.bind(i,97956)),target:()=>Promise.all([i.e("5611"),i.e("4398"),i.e("3464"),i.e("3161")]).then(i.bind(i,17504)),template:()=>Promise.all([i.e("2130"),i.e("1557"),i.e("4310")]).then(i.bind(i,27075)),text:()=>i.e("6563").then(i.bind(i,81774)),time:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("2478"),i.e("4532")]).then(i.bind(i,23152)),icon:()=>Promise.all([i.e("8654"),i.e("4398"),i.e("1761")]).then(i.bind(i,66280)),media:()=>Promise.all([i.e("274"),i.e("9481"),i.e("3097")]).then(i.bind(i,17509)),theme:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("5927")]).then(i.bind(i,14042)),button_toggle:()=>i.e("280").then(i.bind(i,52518)),trigger:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("8477"),i.e("2016"),i.e("5010"),i.e("2130"),i.e("8261"),i.e("5611"),i.e("9058"),i.e("4398"),i.e("5633"),i.e("1557"),i.e("2757"),i.e("4183"),i.e("3538"),i.e("696")]).then(i.bind(i,13037)),tts:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("5487")]).then(i.bind(i,34818)),tts_voice:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("3708")]).then(i.bind(i,42839)),location:()=>Promise.all([i.e("4540"),i.e("4398"),i.e("2099")]).then(i.bind(i,74686)),color_temp:()=>Promise.all([i.e("1543"),i.e("9788"),i.e("2206")]).then(i.bind(i,42845)),ui_action:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("8654"),i.e("8477"),i.e("5010"),i.e("2130"),i.e("4899"),i.e("4398"),i.e("1557"),i.e("6935"),i.e("9853"),i.e("637")]).then(i.bind(i,28238)),ui_color:()=>Promise.all([i.e("2239"),i.e("6767"),i.e("7251"),i.e("3577"),i.e("3818")]).then(i.bind(i,9217)),ui_state_content:()=>Promise.all([i.e("2239"),i.e("8654"),i.e("3806"),i.e("641"),i.e("364")]).then(i.bind(i,19239))},c=new Set(["ui-action","ui-color"]);class h extends a.WF{async focus(){await this.updateComplete,this.renderRoot.querySelector("#selector")?.focus()}get _type(){const e=Object.keys(this.selector)[0];return c.has(e)?e.replace("-","_"):e}willUpdate(e){e.has("selector")&&this.selector&&d[this._type]?.()}render(){return a.qy`
      ${(0,n._)(`ha-selector-${this._type}`,{hass:this.hass,narrow:this.narrow,name:this.name,selector:this._handleLegacySelector(this.selector),value:this.value,label:this.label,placeholder:this.placeholder,disabled:this.disabled,required:this.required,helper:this.helper,context:this.context,localizeValue:this.localizeValue,id:"selector"})}
    `}constructor(...e){super(...e),this.narrow=!1,this.disabled=!1,this.required=!0,this._handleLegacySelector=(0,s.A)((e=>{if("entity"in e)return(0,l.UU)(e);if("device"in e)return(0,l.tD)(e);const t=Object.keys(this.selector)[0];return c.has(t)?{[t.replace("-","_")]:e[t]}:e}))}}(0,o.__decorate)([(0,r.MZ)({attribute:!1})],h.prototype,"hass",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],h.prototype,"narrow",void 0),(0,o.__decorate)([(0,r.MZ)()],h.prototype,"name",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:!1})],h.prototype,"selector",void 0),(0,o.__decorate)([(0,r.MZ)()],h.prototype,"value",void 0),(0,o.__decorate)([(0,r.MZ)()],h.prototype,"label",void 0),(0,o.__decorate)([(0,r.MZ)()],h.prototype,"helper",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:!1})],h.prototype,"localizeValue",void 0),(0,o.__decorate)([(0,r.MZ)()],h.prototype,"placeholder",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],h.prototype,"disabled",void 0),(0,o.__decorate)([(0,r.MZ)({type:Boolean})],h.prototype,"required",void 0),(0,o.__decorate)([(0,r.MZ)({attribute:!1})],h.prototype,"context",void 0),h=(0,o.__decorate)([(0,r.EM)("ha-selector")],h)},89600:function(e,t,i){i.a(e,(async function(e,t){try{var o=i(62826),a=i(55262),r=i(96196),s=i(77845),n=e([a]);a=(n.then?(await n)():n)[0];class l extends a.A{updated(e){if(super.updated(e),e.has("size"))switch(this.size){case"tiny":this.style.setProperty("--ha-spinner-size","16px");break;case"small":this.style.setProperty("--ha-spinner-size","28px");break;case"medium":this.style.setProperty("--ha-spinner-size","48px");break;case"large":this.style.setProperty("--ha-spinner-size","68px");break;case void 0:this.style.removeProperty("--ha-progress-ring-size")}}static get styles(){return[a.A.styles,r.AH`
        :host {
          --indicator-color: var(
            --ha-spinner-indicator-color,
            var(--primary-color)
          );
          --track-color: var(--ha-spinner-divider-color, var(--divider-color));
          --track-width: 4px;
          --speed: 3.5s;
          font-size: var(--ha-spinner-size, 48px);
        }
      `]}}(0,o.__decorate)([(0,s.MZ)()],l.prototype,"size",void 0),l=(0,o.__decorate)([(0,s.EM)("ha-spinner")],l),t()}catch(l){t(l)}}))},78740:function(e,t,i){i.d(t,{h:()=>d});var o=i(62826),a=i(68846),r=i(92347),s=i(96196),n=i(77845),l=i(76679);class d extends a.J{updated(e){super.updated(e),(e.has("invalid")||e.has("errorMessage"))&&(this.setCustomValidity(this.invalid?this.errorMessage||this.validationMessage||"Invalid":""),(this.invalid||this.validateOnInitialRender||e.has("invalid")&&void 0!==e.get("invalid"))&&this.reportValidity()),e.has("autocomplete")&&(this.autocomplete?this.formElement.setAttribute("autocomplete",this.autocomplete):this.formElement.removeAttribute("autocomplete")),e.has("autocorrect")&&(!1===this.autocorrect?this.formElement.setAttribute("autocorrect","off"):this.formElement.removeAttribute("autocorrect")),e.has("inputSpellcheck")&&(this.inputSpellcheck?this.formElement.setAttribute("spellcheck",this.inputSpellcheck):this.formElement.removeAttribute("spellcheck"))}renderIcon(e,t=!1){const i=t?"trailing":"leading";return s.qy`
      <span
        class="mdc-text-field__icon mdc-text-field__icon--${i}"
        tabindex=${t?1:-1}
      >
        <slot name="${i}Icon"></slot>
      </span>
    `}constructor(...e){super(...e),this.icon=!1,this.iconTrailing=!1,this.autocorrect=!0}}d.styles=[r.R,s.AH`
      .mdc-text-field__input {
        width: var(--ha-textfield-input-width, 100%);
      }
      .mdc-text-field:not(.mdc-text-field--with-leading-icon) {
        padding: var(--text-field-padding, 0px 16px);
      }
      .mdc-text-field__affix--suffix {
        padding-left: var(--text-field-suffix-padding-left, 12px);
        padding-right: var(--text-field-suffix-padding-right, 0px);
        padding-inline-start: var(--text-field-suffix-padding-left, 12px);
        padding-inline-end: var(--text-field-suffix-padding-right, 0px);
        direction: ltr;
      }
      .mdc-text-field--with-leading-icon {
        padding-inline-start: var(--text-field-suffix-padding-left, 0px);
        padding-inline-end: var(--text-field-suffix-padding-right, 16px);
        direction: var(--direction);
      }

      .mdc-text-field--with-leading-icon.mdc-text-field--with-trailing-icon {
        padding-left: var(--text-field-suffix-padding-left, 0px);
        padding-right: var(--text-field-suffix-padding-right, 0px);
        padding-inline-start: var(--text-field-suffix-padding-left, 0px);
        padding-inline-end: var(--text-field-suffix-padding-right, 0px);
      }
      .mdc-text-field:not(.mdc-text-field--disabled)
        .mdc-text-field__affix--suffix {
        color: var(--secondary-text-color);
      }

      .mdc-text-field:not(.mdc-text-field--disabled) .mdc-text-field__icon {
        color: var(--secondary-text-color);
      }

      .mdc-text-field__icon--leading {
        margin-inline-start: 16px;
        margin-inline-end: 8px;
        direction: var(--direction);
      }

      .mdc-text-field__icon--trailing {
        padding: var(--textfield-icon-trailing-padding, 12px);
      }

      .mdc-floating-label:not(.mdc-floating-label--float-above) {
        max-width: calc(100% - 16px);
      }

      .mdc-floating-label--float-above {
        max-width: calc((100% - 16px) / 0.75);
        transition: none;
      }

      input {
        text-align: var(--text-field-text-align, start);
      }

      input[type="color"] {
        height: 20px;
      }

      /* Edge, hide reveal password icon */
      ::-ms-reveal {
        display: none;
      }

      /* Chrome, Safari, Edge, Opera */
      :host([no-spinner]) input::-webkit-outer-spin-button,
      :host([no-spinner]) input::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
      }

      input[type="color"]::-webkit-color-swatch-wrapper {
        padding: 0;
      }

      /* Firefox */
      :host([no-spinner]) input[type="number"] {
        -moz-appearance: textfield;
      }

      .mdc-text-field__ripple {
        overflow: hidden;
      }

      .mdc-text-field {
        overflow: var(--text-field-overflow);
      }

      .mdc-floating-label {
        padding-inline-end: 16px;
        padding-inline-start: initial;
        inset-inline-start: 16px !important;
        inset-inline-end: initial !important;
        transform-origin: var(--float-start);
        direction: var(--direction);
        text-align: var(--float-start);
        box-sizing: border-box;
        text-overflow: ellipsis;
      }

      .mdc-text-field--with-leading-icon.mdc-text-field--filled
        .mdc-floating-label {
        max-width: calc(
          100% - 48px - var(--text-field-suffix-padding-left, 0px)
        );
        inset-inline-start: calc(
          48px + var(--text-field-suffix-padding-left, 0px)
        ) !important;
        inset-inline-end: initial !important;
        direction: var(--direction);
      }

      .mdc-text-field__input[type="number"] {
        direction: var(--direction);
      }
      .mdc-text-field__affix--prefix {
        padding-right: var(--text-field-prefix-padding-right, 2px);
        padding-inline-end: var(--text-field-prefix-padding-right, 2px);
        padding-inline-start: initial;
      }

      .mdc-text-field:not(.mdc-text-field--disabled)
        .mdc-text-field__affix--prefix {
        color: var(--mdc-text-field-label-ink-color);
      }
      #helper-text ha-markdown {
        display: inline-block;
      }
    `,"rtl"===l.G.document.dir?s.AH`
          .mdc-text-field--with-leading-icon,
          .mdc-text-field__icon--leading,
          .mdc-floating-label,
          .mdc-text-field--with-leading-icon.mdc-text-field--filled
            .mdc-floating-label,
          .mdc-text-field__input[type="number"] {
            direction: rtl;
            --direction: rtl;
          }
        `:s.AH``],(0,o.__decorate)([(0,n.MZ)({type:Boolean})],d.prototype,"invalid",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"error-message"})],d.prototype,"errorMessage",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],d.prototype,"icon",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],d.prototype,"iconTrailing",void 0),(0,o.__decorate)([(0,n.MZ)()],d.prototype,"autocomplete",void 0),(0,o.__decorate)([(0,n.MZ)({type:Boolean})],d.prototype,"autocorrect",void 0),(0,o.__decorate)([(0,n.MZ)({attribute:"input-spellcheck"})],d.prototype,"inputSpellcheck",void 0),(0,o.__decorate)([(0,n.P)("input")],d.prototype,"formElement",void 0),d=(0,o.__decorate)([(0,n.EM)("ha-textfield")],d)},54110:function(e,t,i){i.d(t,{L3:()=>o,QI:()=>n,bQ:()=>s,gs:()=>a,uG:()=>r});const o=(e,t)=>e.callWS({type:"config/area_registry/create",...t}),a=(e,t,i)=>e.callWS({type:"config/area_registry/update",area_id:t,...i}),r=(e,t)=>e.callWS({type:"config/area_registry/delete",area_id:t}),s=e=>{const t={};for(const i of e)i.area_id&&(i.area_id in t||(t[i.area_id]=[]),t[i.area_id].push(i));return t},n=e=>{const t={};for(const i of e)i.area_id&&(i.area_id in t||(t[i.area_id]=[]),t[i.area_id].push(i));return t}},1491:function(e,t,i){i.d(t,{FB:()=>l,I3:()=>d,fk:()=>h,g2:()=>c,oG:()=>p});var o=i(56403),a=i(16727),r=i(41144),s=i(13877),n=(i(25749),i(84125));const l=(e,t,i)=>e.callWS({type:"config/device_registry/update",device_id:t,...i}),d=e=>{const t={};for(const i of e)i.device_id&&(i.device_id in t||(t[i.device_id]=[]),t[i.device_id].push(i));return t},c=e=>{const t={};for(const i of e)i.device_id&&(i.device_id in t||(t[i.device_id]=[]),t[i.device_id].push(i));return t},h=(e,t,i,o)=>{const a={};for(const r of t){const t=e[r.entity_id];t?.domain&&null!==r.device_id&&(a[r.device_id]=a[r.device_id]||new Set,a[r.device_id].add(t.domain))}if(i&&o)for(const r of i)for(const e of r.config_entries){const t=o.find((t=>t.entry_id===e));t?.domain&&(a[r.id]=a[r.id]||new Set,a[r.id].add(t.domain))}return a},p=(e,t,i,l,d,h,p,u,m,_="")=>{const v=Object.values(e.devices),b=Object.values(e.entities);let f={};(i||l||d||p)&&(f=c(b));let g=v.filter((e=>e.id===m||!e.disabled_by));i&&(g=g.filter((e=>{const t=f[e.id];return!(!t||!t.length)&&f[e.id].some((e=>i.includes((0,r.m)(e.entity_id))))}))),l&&(g=g.filter((e=>{const t=f[e.id];return!t||!t.length||b.every((e=>!l.includes((0,r.m)(e.entity_id))))}))),u&&(g=g.filter((e=>!u.includes(e.id)))),d&&(g=g.filter((t=>{const i=f[t.id];return!(!i||!i.length)&&f[t.id].some((t=>{const i=e.states[t.entity_id];return!!i&&(i.attributes.device_class&&d.includes(i.attributes.device_class))}))}))),p&&(g=g.filter((t=>{const i=f[t.id];return!(!i||!i.length)&&i.some((t=>{const i=e.states[t.entity_id];return!!i&&p(i)}))}))),h&&(g=g.filter((e=>e.id===m||h(e))));return g.map((i=>{const r=(0,a.T)(i,e,f[i.id]),{area:l}=(0,s.w)(i,e),d=l?(0,o.A)(l):void 0,c=i.primary_config_entry?t?.[i.primary_config_entry]:void 0,h=c?.domain,p=h?(0,n.p$)(e.localize,h):void 0;return{id:`${_}${i.id}`,label:"",primary:r||e.localize("ui.components.device-picker.unnamed_device"),secondary:d,domain:c?.domain,domain_name:p,search_labels:[r,d,h,p].filter(Boolean),sorting_label:r||"zzz"}}))}},82694:function(e,t,i){i.d(t,{DF:()=>u,Lo:()=>g,MH:()=>d,MM:()=>m,Qz:()=>p,Ru:()=>v,UU:()=>b,_7:()=>h,bZ:()=>c,m0:()=>l,tD:()=>f,vX:()=>_});var o=i(55376),a=i(97382),r=i(9477),s=i(50218),n=i(1491);const l=(e,t,i,o,a,r,s)=>{const n=[],l=[],d=[];return Object.values(i).forEach((i=>{i.labels.includes(t)&&p(e,a,o,i.area_id,r,s)&&d.push(i.area_id)})),Object.values(o).forEach((i=>{i.labels.includes(t)&&u(e,Object.values(a),i,r,s)&&l.push(i.id)})),Object.values(a).forEach((i=>{i.labels.includes(t)&&m(e.states[i.entity_id],r,s)&&n.push(i.entity_id)})),{areas:d,devices:l,entities:n}},d=(e,t,i,o,a)=>{const r=[];return Object.values(i).forEach((i=>{i.floor_id===t&&p(e,e.entities,e.devices,i.area_id,o,a)&&r.push(i.area_id)})),{areas:r}},c=(e,t,i,o,a,r)=>{const s=[],n=[];return Object.values(i).forEach((i=>{i.area_id===t&&u(e,Object.values(o),i,a,r)&&n.push(i.id)})),Object.values(o).forEach((i=>{i.area_id===t&&m(e.states[i.entity_id],a,r)&&s.push(i.entity_id)})),{devices:n,entities:s}},h=(e,t,i,o,a)=>{const r=[];return Object.values(i).forEach((i=>{i.device_id===t&&m(e.states[i.entity_id],o,a)&&r.push(i.entity_id)})),{entities:r}},p=(e,t,i,o,a,r)=>!!Object.values(i).some((i=>!(i.area_id!==o||!u(e,Object.values(t),i,a,r))))||Object.values(t).some((t=>!(t.area_id!==o||!m(e.states[t.entity_id],a,r)))),u=(e,t,i,a,r)=>{const s=r?(0,n.fk)(r,t):void 0;if(a.target?.device&&!(0,o.e)(a.target.device).some((e=>_(e,i,s))))return!1;if(a.target?.entity){return t.filter((e=>e.device_id===i.id)).some((t=>{const i=e.states[t.entity_id];return m(i,a,r)}))}return!0},m=(e,t,i)=>!!e&&(!t.target?.entity||(0,o.e)(t.target.entity).some((t=>v(t,e,i)))),_=(e,t,i)=>{const{manufacturer:o,model:a,model_id:r,integration:s}=e;return(!o||t.manufacturer===o)&&((!a||t.model===a)&&((!r||t.model_id===r)&&!(s&&i&&!i?.[t.id]?.has(s))))},v=(e,t,i)=>{const{domain:s,device_class:n,supported_features:l,integration:d}=e;if(s){const e=(0,a.t)(t);if(Array.isArray(s)?!s.includes(e):e!==s)return!1}if(n){const e=t.attributes.device_class;if(e&&Array.isArray(n)?!n.includes(e):e!==n)return!1}return!(l&&!(0,o.e)(l).some((e=>(0,r.$)(t,e))))&&(!d||i?.[t.entity_id]?.domain===d)},b=e=>{if(!e.entity)return{entity:null};if("filter"in e.entity)return e;const{domain:t,integration:i,device_class:o,...a}=e.entity;return t||i||o?{entity:{...a,filter:{domain:t,integration:i,device_class:o}}}:{entity:a}},f=e=>{if(!e.device)return{device:null};if("filter"in e.device)return e;const{integration:t,manufacturer:i,model:o,...a}=e.device;return t||i||o?{device:{...a,filter:{integration:t,manufacturer:i,model:o}}}:{device:a}},g=e=>{let t;if("target"in e)t=(0,o.e)(e.target?.entity);else if("entity"in e){if(e.entity?.include_entities)return;t=(0,o.e)(e.entity?.filter)}if(!t)return;const i=t.flatMap((e=>e.integration||e.device_class||e.supported_features||!e.domain?[]:(0,o.e)(e.domain).filter((e=>(0,s.z)(e)))));return[...new Set(i)]}},82160:function(e,t,i){i.d(t,{J:()=>r});var o=i(92542);const a=()=>Promise.all([i.e("8654"),i.e("5989"),i.e("4398"),i.e("5633"),i.e("2757"),i.e("274"),i.e("5429"),i.e("7298"),i.e("4944")]).then(i.bind(i,76218)),r=(e,t)=>{(0,o.r)(e,"show-dialog",{dialogTag:"dialog-area-registry-detail",dialogImport:a,dialogParams:t})}},50218:function(e,t,i){i.d(t,{z:()=>o});const o=(0,i(99245).g)(["input_boolean","input_button","input_text","input_number","input_datetime","input_select","counter","timer","schedule"])},69847:function(e,t,i){i.d(t,{b:()=>r});var o=i(78648);const a={ignoreDiacritics:!0,isCaseSensitive:!1,threshold:.3,minMatchCharLength:2};class r extends o.A{multiTermsSearch(e,t){const i=e.toLowerCase().split(" "),{minMatchCharLength:o}=this.options,a=o?i.filter((e=>e.length>=o)):i;if(0===a.length)return null;const r=this.getIndex().toJSON().keys,s={$and:a.map((e=>({$or:r.map((t=>({$path:t.path,$val:e})))})))};return this.search(s,t)}constructor(e,t,i){super(e,{...a,...t},i)}}},84183:function(e,t,i){i.d(t,{i:()=>o});const o=async()=>{await i.e("2564").then(i.bind(i,42735))}}};
//# sourceMappingURL=9107.99479abbfcf60e60.js.map