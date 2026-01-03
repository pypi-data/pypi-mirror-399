"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2097"],{10253:function(t,e,i){i.a(t,(async function(t,a){try{i.d(e,{P:function(){return c}});i(74423),i(25276);var s=i(22),n=i(58109),o=i(81793),r=i(44740),l=t([s]);s=(l.then?(await l)():l)[0];var c=t=>t.first_weekday===o.zt.language?"weekInfo"in Intl.Locale.prototype?new Intl.Locale(t.language).weekInfo.firstDay%7:(0,n.S)(t.language)%7:r.Z.includes(t.first_weekday)?r.Z.indexOf(t.first_weekday):1;a()}catch(u){a(u)}}))},84834:function(t,e,i){i.a(t,(async function(t,a){try{i.d(e,{Yq:function(){return c},zB:function(){return d}});i(50113),i(18111),i(20116),i(26099);var s=i(22),n=i(22786),o=i(81793),r=i(74309),l=t([s,r]);[s,r]=l.then?(await l)():l;(0,n.A)(((t,e)=>new Intl.DateTimeFormat(t.language,{weekday:"long",month:"long",day:"numeric",timeZone:(0,r.w)(t.time_zone,e)})));var c=(t,e,i)=>u(e,i.time_zone).format(t),u=(0,n.A)(((t,e)=>new Intl.DateTimeFormat(t.language,{year:"numeric",month:"long",day:"numeric",timeZone:(0,r.w)(t.time_zone,e)}))),d=((0,n.A)(((t,e)=>new Intl.DateTimeFormat(t.language,{year:"numeric",month:"short",day:"numeric",timeZone:(0,r.w)(t.time_zone,e)}))),(t,e,i)=>{var a,s,n,r,l=h(e,i.time_zone);if(e.date_format===o.ow.language||e.date_format===o.ow.system)return l.format(t);var c=l.formatToParts(t),u=null===(a=c.find((t=>"literal"===t.type)))||void 0===a?void 0:a.value,d=null===(s=c.find((t=>"day"===t.type)))||void 0===s?void 0:s.value,p=null===(n=c.find((t=>"month"===t.type)))||void 0===n?void 0:n.value,v=null===(r=c.find((t=>"year"===t.type)))||void 0===r?void 0:r.value,_=c[c.length-1],g="literal"===(null==_?void 0:_.type)?null==_?void 0:_.value:"";return"bg"===e.language&&e.date_format===o.ow.YMD&&(g=""),{[o.ow.DMY]:`${d}${u}${p}${u}${v}${g}`,[o.ow.MDY]:`${p}${u}${d}${u}${v}${g}`,[o.ow.YMD]:`${v}${u}${p}${u}${d}${g}`}[e.date_format]}),h=(0,n.A)(((t,e)=>{var i=t.date_format===o.ow.system?void 0:t.language;return t.date_format===o.ow.language||(t.date_format,o.ow.system),new Intl.DateTimeFormat(i,{year:"numeric",month:"numeric",day:"numeric",timeZone:(0,r.w)(t.time_zone,e)})}));(0,n.A)(((t,e)=>new Intl.DateTimeFormat(t.language,{day:"numeric",month:"short",timeZone:(0,r.w)(t.time_zone,e)}))),(0,n.A)(((t,e)=>new Intl.DateTimeFormat(t.language,{month:"long",year:"numeric",timeZone:(0,r.w)(t.time_zone,e)}))),(0,n.A)(((t,e)=>new Intl.DateTimeFormat(t.language,{month:"long",timeZone:(0,r.w)(t.time_zone,e)}))),(0,n.A)(((t,e)=>new Intl.DateTimeFormat(t.language,{year:"numeric",timeZone:(0,r.w)(t.time_zone,e)}))),(0,n.A)(((t,e)=>new Intl.DateTimeFormat(t.language,{weekday:"long",timeZone:(0,r.w)(t.time_zone,e)}))),(0,n.A)(((t,e)=>new Intl.DateTimeFormat(t.language,{weekday:"short",timeZone:(0,r.w)(t.time_zone,e)})));a()}catch(p){a(p)}}))},49284:function(t,e,i){i.a(t,(async function(t,a){try{i.d(e,{r6:function(){return d},yg:function(){return p}});var s=i(22),n=i(22786),o=i(84834),r=i(4359),l=i(74309),c=i(59006),u=t([s,o,r,l]);[s,o,r,l]=u.then?(await u)():u;var d=(t,e,i)=>h(e,i.time_zone).format(t),h=(0,n.A)(((t,e)=>new Intl.DateTimeFormat(t.language,{year:"numeric",month:"long",day:"numeric",hour:(0,c.J)(t)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,c.J)(t)?"h12":"h23",timeZone:(0,l.w)(t.time_zone,e)}))),p=((0,n.A)((()=>new Intl.DateTimeFormat(void 0,{year:"numeric",month:"long",day:"numeric",hour:"2-digit",minute:"2-digit"}))),(0,n.A)(((t,e)=>new Intl.DateTimeFormat(t.language,{year:"numeric",month:"short",day:"numeric",hour:(0,c.J)(t)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,c.J)(t)?"h12":"h23",timeZone:(0,l.w)(t.time_zone,e)}))),(0,n.A)(((t,e)=>new Intl.DateTimeFormat(t.language,{month:"short",day:"numeric",hour:(0,c.J)(t)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,c.J)(t)?"h12":"h23",timeZone:(0,l.w)(t.time_zone,e)}))),(t,e,i)=>v(e,i.time_zone).format(t)),v=(0,n.A)(((t,e)=>new Intl.DateTimeFormat(t.language,{year:"numeric",month:"long",day:"numeric",hour:(0,c.J)(t)?"numeric":"2-digit",minute:"2-digit",second:"2-digit",hourCycle:(0,c.J)(t)?"h12":"h23",timeZone:(0,l.w)(t.time_zone,e)})));a()}catch(_){a(_)}}))},4359:function(t,e,i){i.a(t,(async function(t,a){try{i.d(e,{LW:function(){return _},Xs:function(){return p},fU:function(){return c},ie:function(){return d}});var s=i(22),n=i(22786),o=i(74309),r=i(59006),l=t([s,o]);[s,o]=l.then?(await l)():l;var c=(t,e,i)=>u(e,i.time_zone).format(t),u=(0,n.A)(((t,e)=>new Intl.DateTimeFormat(t.language,{hour:"numeric",minute:"2-digit",hourCycle:(0,r.J)(t)?"h12":"h23",timeZone:(0,o.w)(t.time_zone,e)}))),d=(t,e,i)=>h(e,i.time_zone).format(t),h=(0,n.A)(((t,e)=>new Intl.DateTimeFormat(t.language,{hour:(0,r.J)(t)?"numeric":"2-digit",minute:"2-digit",second:"2-digit",hourCycle:(0,r.J)(t)?"h12":"h23",timeZone:(0,o.w)(t.time_zone,e)}))),p=(t,e,i)=>v(e,i.time_zone).format(t),v=(0,n.A)(((t,e)=>new Intl.DateTimeFormat(t.language,{weekday:"long",hour:(0,r.J)(t)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,r.J)(t)?"h12":"h23",timeZone:(0,o.w)(t.time_zone,e)}))),_=(t,e,i)=>g(e,i.time_zone).format(t),g=(0,n.A)(((t,e)=>new Intl.DateTimeFormat("en-GB",{hour:"numeric",minute:"2-digit",hour12:!1,timeZone:(0,o.w)(t.time_zone,e)})));a()}catch(f){a(f)}}))},77646:function(t,e,i){i.a(t,(async function(t,a){try{i.d(e,{K:function(){return c}});var s=i(22),n=i(22786),o=i(97518),r=t([s,o]);[s,o]=r.then?(await r)():r;var l=(0,n.A)((t=>new Intl.RelativeTimeFormat(t.language,{numeric:"auto"}))),c=function(t,e,i){var a=!(arguments.length>3&&void 0!==arguments[3])||arguments[3],s=(0,o.x)(t,i,e);return a?l(e).format(s.value,s.unit):Intl.NumberFormat(e.language,{style:"unit",unit:s.unit,unitDisplay:"long"}).format(Math.abs(s.value))};a()}catch(u){a(u)}}))},74309:function(t,e,i){i.a(t,(async function(t,a){try{i.d(e,{w:function(){return h}});var s,n,o,r=i(22),l=i(81793),c=t([r]);r=(c.then?(await c)():c)[0];var u=null===(s=Intl.DateTimeFormat)||void 0===s||null===(n=(o=s.call(Intl)).resolvedOptions)||void 0===n?void 0:n.call(o).timeZone,d=null!=u?u:"UTC",h=(t,e)=>t===l.Wj.local&&u?d:e;a()}catch(p){a(p)}}))},59006:function(t,e,i){i.d(e,{J:function(){return n}});i(74423);var a=i(22786),s=i(81793),n=(0,a.A)((t=>{if(t.time_format===s.Hg.language||t.time_format===s.Hg.system){var e=t.time_format===s.Hg.language?t.language:void 0;return new Date("January 1, 2023 22:00:00").toLocaleString(e).includes("10")}return t.time_format===s.Hg.am_pm}))},44740:function(t,e,i){i.d(e,{Z:function(){return a}});var a=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"]},32470:function(t,e,i){i.d(e,{j:function(){return a}});var a=(t,e,i)=>(void 0!==i&&(i=!!i),t.hasAttribute(e)?!!i||(t.removeAttribute(e),!1):!1!==i&&(t.setAttribute(e,""),!0))},45996:function(t,e,i){i.d(e,{n:function(){return s}});i(27495),i(90906);var a=/^(\w+)\.(\w+)$/,s=t=>a.test(t)},74522:function(t,e,i){i.d(e,{Z:function(){return a}});i(34782);var a=t=>t.charAt(0).toUpperCase()+t.slice(1)},38852:function(t,e,i){i.d(e,{b:function(){return s}});var a=i(31432),s=(i(23792),i(36033),i(26099),i(84864),i(57465),i(27495),i(69479),i(38781),i(31415),i(17642),i(58004),i(33853),i(45876),i(32475),i(15024),i(31698),i(62953),(t,e)=>{if(t===e)return!0;if(t&&e&&"object"==typeof t&&"object"==typeof e){if(t.constructor!==e.constructor)return!1;var i,n;if(Array.isArray(t)){if((n=t.length)!==e.length)return!1;for(i=n;0!=i--;)if(!s(t[i],e[i]))return!1;return!0}if(t instanceof Map&&e instanceof Map){if(t.size!==e.size)return!1;var o,r=(0,a.A)(t.entries());try{for(r.s();!(o=r.n()).done;)if(i=o.value,!e.has(i[0]))return!1}catch(v){r.e(v)}finally{r.f()}var l,c=(0,a.A)(t.entries());try{for(c.s();!(l=c.n()).done;)if(i=l.value,!s(i[1],e.get(i[0])))return!1}catch(v){c.e(v)}finally{c.f()}return!0}if(t instanceof Set&&e instanceof Set){if(t.size!==e.size)return!1;var u,d=(0,a.A)(t.entries());try{for(d.s();!(u=d.n()).done;)if(i=u.value,!e.has(i[0]))return!1}catch(v){d.e(v)}finally{d.f()}return!0}if(ArrayBuffer.isView(t)&&ArrayBuffer.isView(e)){if((n=t.length)!==e.length)return!1;for(i=n;0!=i--;)if(t[i]!==e[i])return!1;return!0}if(t.constructor===RegExp)return t.source===e.source&&t.flags===e.flags;if(t.valueOf!==Object.prototype.valueOf)return t.valueOf()===e.valueOf();if(t.toString!==Object.prototype.toString)return t.toString()===e.toString();var h=Object.keys(t);if((n=h.length)!==Object.keys(e).length)return!1;for(i=n;0!=i--;)if(!Object.prototype.hasOwnProperty.call(e,h[i]))return!1;for(i=n;0!=i--;){var p=h[i];if(!s(t[p],e[p]))return!1}return!0}return t!=t&&e!=e})},97518:function(t,e,i){i.a(t,(async function(t,a){try{i.d(e,{x:function(){return v}});var s=i(6946),n=i(52640),o=i(56232),r=i(10253),l=t([r]);r=(l.then?(await l)():l)[0];var c=1e3,u=60,d=60*u;function v(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:Date.now(),i=arguments.length>2?arguments[2]:void 0,a=arguments.length>3&&void 0!==arguments[3]?arguments[3]:{},l=Object.assign(Object.assign({},h),a||{}),p=(+t-+e)/c;if(Math.abs(p)<l.second)return{value:Math.round(p),unit:"second"};var v=p/u;if(Math.abs(v)<l.minute)return{value:Math.round(v),unit:"minute"};var _=p/d;if(Math.abs(_)<l.hour)return{value:Math.round(_),unit:"hour"};var g=new Date(t),f=new Date(e);g.setHours(0,0,0,0),f.setHours(0,0,0,0);var y=(0,s.c)(g,f);if(0===y)return{value:Math.round(_),unit:"hour"};if(Math.abs(y)<l.day)return{value:y,unit:"day"};var m=(0,r.P)(i),w=(0,n.k)(g,{weekStartsOn:m}),b=(0,n.k)(f,{weekStartsOn:m}),k=(0,o.I)(w,b);if(0===k)return{value:y,unit:"day"};if(Math.abs(k)<l.week)return{value:k,unit:"week"};var A=g.getFullYear()-f.getFullYear(),$=12*A+g.getMonth()-f.getMonth();return 0===$?{value:k,unit:"week"}:Math.abs($)<l.month||0===A?{value:$,unit:"month"}:{value:Math.round(A),unit:"year"}}var h={second:59,minute:59,hour:22,day:5,week:4,month:11};a()}catch(p){a(p)}}))},28561:function(t,e,i){i.d(e,{L:function(){return s}});i(26099),i(38781);function a(){return Math.floor(65536*(1+Math.random())).toString(16).substring(1)}function s(){return a()+a()+a()+a()+a()}},74529:function(t,e,i){var a,s,n,o,r=i(44734),l=i(56038),c=i(69683),u=i(6454),d=i(25460),h=(i(28706),i(62826)),p=i(96229),v=i(26069),_=i(91735),g=i(42034),f=i(96196),y=i(77845),m=t=>t,w=function(t){function e(){var t;(0,r.A)(this,e);for(var i=arguments.length,a=new Array(i),s=0;s<i;s++)a[s]=arguments[s];return(t=(0,c.A)(this,e,[].concat(a))).filled=!1,t.active=!1,t}return(0,u.A)(e,t),(0,l.A)(e,[{key:"renderOutline",value:function(){return this.filled?(0,f.qy)(a||(a=m`<span class="filled"></span>`)):(0,d.A)(e,"renderOutline",this,3)([])}},{key:"getContainerClasses",value:function(){return Object.assign(Object.assign({},(0,d.A)(e,"getContainerClasses",this,3)([])),{},{active:this.active})}},{key:"renderPrimaryContent",value:function(){return(0,f.qy)(s||(s=m`
      <span class="leading icon" aria-hidden="true">
        ${0}
      </span>
      <span class="label">${0}</span>
      <span class="touch"></span>
      <span class="trailing leading icon" aria-hidden="true">
        ${0}
      </span>
    `),this.renderLeadingIcon(),this.label,this.renderTrailingIcon())}},{key:"renderTrailingIcon",value:function(){return(0,f.qy)(n||(n=m`<slot name="trailing-icon"></slot>`))}}])}(p.k);w.styles=[_.R,g.R,v.R,(0,f.AH)(o||(o=m`
      :host {
        --md-sys-color-primary: var(--primary-text-color);
        --md-sys-color-on-surface: var(--primary-text-color);
        --md-assist-chip-container-shape: var(
          --ha-assist-chip-container-shape,
          16px
        );
        --md-assist-chip-outline-color: var(--outline-color);
        --md-assist-chip-label-text-weight: 400;
      }
      /** Material 3 doesn't have a filled chip, so we have to make our own **/
      .filled {
        display: flex;
        pointer-events: none;
        border-radius: inherit;
        inset: 0;
        position: absolute;
        background-color: var(--ha-assist-chip-filled-container-color);
      }
      /** Set the size of mdc icons **/
      ::slotted([slot="icon"]),
      ::slotted([slot="trailing-icon"]) {
        display: flex;
        --mdc-icon-size: var(--md-input-chip-icon-size, 18px);
        font-size: var(--_label-text-size) !important;
      }

      .trailing.icon ::slotted(*),
      .trailing.icon svg {
        margin-inline-end: unset;
        margin-inline-start: var(--_icon-label-space);
      }
      ::before {
        background: var(--ha-assist-chip-container-color, transparent);
        opacity: var(--ha-assist-chip-container-opacity, 1);
      }
      :where(.active)::before {
        background: var(--ha-assist-chip-active-container-color);
        opacity: var(--ha-assist-chip-active-container-opacity);
      }
      .label {
        font-family: var(--ha-font-family-body);
      }
    `))],(0,h.__decorate)([(0,y.MZ)({type:Boolean,reflect:!0})],w.prototype,"filled",void 0),(0,h.__decorate)([(0,y.MZ)({type:Boolean})],w.prototype,"active",void 0),w=(0,h.__decorate)([(0,y.EM)("ha-assist-chip")],w)},63419:function(t,e,i){var a,s=i(44734),n=i(56038),o=i(69683),r=i(6454),l=(i(28706),i(62826)),c=i(96196),u=i(77845),d=i(92542),h=(i(41742),i(25460)),p=i(26139),v=i(8889),_=i(63374),g=function(t){function e(){return(0,s.A)(this,e),(0,o.A)(this,e,arguments)}return(0,r.A)(e,t),(0,n.A)(e,[{key:"connectedCallback",value:function(){(0,h.A)(e,"connectedCallback",this,3)([]),this.addEventListener("close-menu",this._handleCloseMenu)}},{key:"_handleCloseMenu",value:function(t){var e,i;t.detail.reason.kind===_.fi.KEYDOWN&&t.detail.reason.key===_.NV.ESCAPE||null===(e=(i=t.detail.initiator).clickAction)||void 0===e||e.call(i,t.detail.initiator)}}])}(p.W1);g.styles=[v.R,(0,c.AH)(a||(a=(t=>t)`
      :host {
        --md-sys-color-surface-container: var(--card-background-color);
      }
    `))],g=(0,l.__decorate)([(0,u.EM)("ha-md-menu")],g);var f,y,m=t=>t,w=function(t){function e(){var t;(0,s.A)(this,e);for(var i=arguments.length,a=new Array(i),n=0;n<i;n++)a[n]=arguments[n];return(t=(0,o.A)(this,e,[].concat(a))).disabled=!1,t.anchorCorner="end-start",t.menuCorner="start-start",t.hasOverflow=!1,t.quick=!1,t}return(0,r.A)(e,t),(0,n.A)(e,[{key:"items",get:function(){return this._menu.items}},{key:"focus",value:function(){var t;this._menu.open?this._menu.focus():null===(t=this._triggerButton)||void 0===t||t.focus()}},{key:"render",value:function(){return(0,c.qy)(f||(f=m`
      <div @click=${0}>
        <slot name="trigger" @slotchange=${0}></slot>
      </div>
      <ha-md-menu
        .quick=${0}
        .positioning=${0}
        .hasOverflow=${0}
        .anchorCorner=${0}
        .menuCorner=${0}
        @opening=${0}
        @closing=${0}
      >
        <slot></slot>
      </ha-md-menu>
    `),this._handleClick,this._setTriggerAria,this.quick,this.positioning,this.hasOverflow,this.anchorCorner,this.menuCorner,this._handleOpening,this._handleClosing)}},{key:"_handleOpening",value:function(){(0,d.r)(this,"opening",void 0,{composed:!1})}},{key:"_handleClosing",value:function(){(0,d.r)(this,"closing",void 0,{composed:!1})}},{key:"_handleClick",value:function(){this.disabled||(this._menu.anchorElement=this,this._menu.open?this._menu.close():this._menu.show())}},{key:"_triggerButton",get:function(){return this.querySelector('ha-icon-button[slot="trigger"], ha-button[slot="trigger"], ha-assist-chip[slot="trigger"]')}},{key:"_setTriggerAria",value:function(){this._triggerButton&&(this._triggerButton.ariaHasPopup="menu")}}])}(c.WF);w.styles=(0,c.AH)(y||(y=m`
    :host {
      display: inline-block;
      position: relative;
    }
    ::slotted([disabled]) {
      color: var(--disabled-text-color);
    }
  `)),(0,l.__decorate)([(0,u.MZ)({type:Boolean})],w.prototype,"disabled",void 0),(0,l.__decorate)([(0,u.MZ)()],w.prototype,"positioning",void 0),(0,l.__decorate)([(0,u.MZ)({attribute:"anchor-corner"})],w.prototype,"anchorCorner",void 0),(0,l.__decorate)([(0,u.MZ)({attribute:"menu-corner"})],w.prototype,"menuCorner",void 0),(0,l.__decorate)([(0,u.MZ)({type:Boolean,attribute:"has-overflow"})],w.prototype,"hasOverflow",void 0),(0,l.__decorate)([(0,u.MZ)({type:Boolean})],w.prototype,"quick",void 0),(0,l.__decorate)([(0,u.P)("ha-md-menu",!0)],w.prototype,"_menu",void 0),w=(0,l.__decorate)([(0,u.EM)("ha-md-button-menu")],w)},68757:function(t,e,i){var a,s,n,o=i(44734),r=i(56038),l=i(69683),c=i(6454),u=(i(28706),i(2892),i(62826)),d=i(96196),h=i(77845),p=(i(60733),i(78740),t=>t),v=function(t){function e(){var t;(0,o.A)(this,e);for(var i=arguments.length,a=new Array(i),s=0;s<i;s++)a[s]=arguments[s];return(t=(0,l.A)(this,e,[].concat(a))).icon=!1,t.iconTrailing=!1,t.autocorrect=!0,t.value="",t.placeholder="",t.label="",t.disabled=!1,t.required=!1,t.minLength=-1,t.maxLength=-1,t.outlined=!1,t.helper="",t.validateOnInitialRender=!1,t.validationMessage="",t.autoValidate=!1,t.pattern="",t.size=null,t.helperPersistent=!1,t.charCounter=!1,t.endAligned=!1,t.prefix="",t.suffix="",t.name="",t.readOnly=!1,t.autocapitalize="",t._unmaskedPassword=!1,t}return(0,c.A)(e,t),(0,r.A)(e,[{key:"render",value:function(){var t;return(0,d.qy)(a||(a=p`<ha-textfield
        .invalid=${0}
        .errorMessage=${0}
        .icon=${0}
        .iconTrailing=${0}
        .autocomplete=${0}
        .autocorrect=${0}
        .inputSpellcheck=${0}
        .value=${0}
        .placeholder=${0}
        .label=${0}
        .disabled=${0}
        .required=${0}
        .minLength=${0}
        .maxLength=${0}
        .outlined=${0}
        .helper=${0}
        .validateOnInitialRender=${0}
        .validationMessage=${0}
        .autoValidate=${0}
        .pattern=${0}
        .size=${0}
        .helperPersistent=${0}
        .charCounter=${0}
        .endAligned=${0}
        .prefix=${0}
        .name=${0}
        .inputMode=${0}
        .readOnly=${0}
        .autocapitalize=${0}
        .type=${0}
        .suffix=${0}
        @input=${0}
        @change=${0}
      ></ha-textfield>
      <ha-icon-button
        .label=${0}
        @click=${0}
        .path=${0}
      ></ha-icon-button>`),this.invalid,this.errorMessage,this.icon,this.iconTrailing,this.autocomplete,this.autocorrect,this.inputSpellcheck,this.value,this.placeholder,this.label,this.disabled,this.required,this.minLength,this.maxLength,this.outlined,this.helper,this.validateOnInitialRender,this.validationMessage,this.autoValidate,this.pattern,this.size,this.helperPersistent,this.charCounter,this.endAligned,this.prefix,this.name,this.inputMode,this.readOnly,this.autocapitalize,this._unmaskedPassword?"text":"password",(0,d.qy)(s||(s=p`<div style="width: 24px"></div>`)),this._handleInputEvent,this._handleChangeEvent,(null===(t=this.hass)||void 0===t?void 0:t.localize(this._unmaskedPassword?"ui.components.selectors.text.hide_password":"ui.components.selectors.text.show_password"))||(this._unmaskedPassword?"Hide password":"Show password"),this._toggleUnmaskedPassword,this._unmaskedPassword?"M11.83,9L15,12.16C15,12.11 15,12.05 15,12A3,3 0 0,0 12,9C11.94,9 11.89,9 11.83,9M7.53,9.8L9.08,11.35C9.03,11.56 9,11.77 9,12A3,3 0 0,0 12,15C12.22,15 12.44,14.97 12.65,14.92L14.2,16.47C13.53,16.8 12.79,17 12,17A5,5 0 0,1 7,12C7,11.21 7.2,10.47 7.53,9.8M2,4.27L4.28,6.55L4.73,7C3.08,8.3 1.78,10 1,12C2.73,16.39 7,19.5 12,19.5C13.55,19.5 15.03,19.2 16.38,18.66L16.81,19.08L19.73,22L21,20.73L3.27,3M12,7A5,5 0 0,1 17,12C17,12.64 16.87,13.26 16.64,13.82L19.57,16.75C21.07,15.5 22.27,13.86 23,12C21.27,7.61 17,4.5 12,4.5C10.6,4.5 9.26,4.75 8,5.2L10.17,7.35C10.74,7.13 11.35,7 12,7Z":"M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z")}},{key:"focus",value:function(){this._textField.focus()}},{key:"checkValidity",value:function(){return this._textField.checkValidity()}},{key:"reportValidity",value:function(){return this._textField.reportValidity()}},{key:"setCustomValidity",value:function(t){return this._textField.setCustomValidity(t)}},{key:"layout",value:function(){return this._textField.layout()}},{key:"_toggleUnmaskedPassword",value:function(){this._unmaskedPassword=!this._unmaskedPassword}},{key:"_handleInputEvent",value:function(t){this.value=t.target.value}},{key:"_handleChangeEvent",value:function(t){this.value=t.target.value,this._reDispatchEvent(t)}},{key:"_reDispatchEvent",value:function(t){var e=new Event(t.type,t);this.dispatchEvent(e)}}])}(d.WF);v.styles=(0,d.AH)(n||(n=p`
    :host {
      display: block;
      position: relative;
    }
    ha-textfield {
      width: 100%;
    }
    ha-icon-button {
      position: absolute;
      top: 8px;
      right: 8px;
      inset-inline-start: initial;
      inset-inline-end: 8px;
      --mdc-icon-button-size: 40px;
      --mdc-icon-size: 20px;
      color: var(--secondary-text-color);
      direction: var(--direction);
    }
  `)),(0,u.__decorate)([(0,h.MZ)({attribute:!1})],v.prototype,"hass",void 0),(0,u.__decorate)([(0,h.MZ)({type:Boolean})],v.prototype,"invalid",void 0),(0,u.__decorate)([(0,h.MZ)({attribute:"error-message"})],v.prototype,"errorMessage",void 0),(0,u.__decorate)([(0,h.MZ)({type:Boolean})],v.prototype,"icon",void 0),(0,u.__decorate)([(0,h.MZ)({type:Boolean})],v.prototype,"iconTrailing",void 0),(0,u.__decorate)([(0,h.MZ)()],v.prototype,"autocomplete",void 0),(0,u.__decorate)([(0,h.MZ)({type:Boolean})],v.prototype,"autocorrect",void 0),(0,u.__decorate)([(0,h.MZ)({attribute:"input-spellcheck"})],v.prototype,"inputSpellcheck",void 0),(0,u.__decorate)([(0,h.MZ)({type:String})],v.prototype,"value",void 0),(0,u.__decorate)([(0,h.MZ)({type:String})],v.prototype,"placeholder",void 0),(0,u.__decorate)([(0,h.MZ)({type:String})],v.prototype,"label",void 0),(0,u.__decorate)([(0,h.MZ)({type:Boolean,reflect:!0})],v.prototype,"disabled",void 0),(0,u.__decorate)([(0,h.MZ)({type:Boolean})],v.prototype,"required",void 0),(0,u.__decorate)([(0,h.MZ)({type:Number})],v.prototype,"minLength",void 0),(0,u.__decorate)([(0,h.MZ)({type:Number})],v.prototype,"maxLength",void 0),(0,u.__decorate)([(0,h.MZ)({type:Boolean,reflect:!0})],v.prototype,"outlined",void 0),(0,u.__decorate)([(0,h.MZ)({type:String})],v.prototype,"helper",void 0),(0,u.__decorate)([(0,h.MZ)({type:Boolean})],v.prototype,"validateOnInitialRender",void 0),(0,u.__decorate)([(0,h.MZ)({type:String})],v.prototype,"validationMessage",void 0),(0,u.__decorate)([(0,h.MZ)({type:Boolean})],v.prototype,"autoValidate",void 0),(0,u.__decorate)([(0,h.MZ)({type:String})],v.prototype,"pattern",void 0),(0,u.__decorate)([(0,h.MZ)({type:Number})],v.prototype,"size",void 0),(0,u.__decorate)([(0,h.MZ)({type:Boolean})],v.prototype,"helperPersistent",void 0),(0,u.__decorate)([(0,h.MZ)({type:Boolean})],v.prototype,"charCounter",void 0),(0,u.__decorate)([(0,h.MZ)({type:Boolean})],v.prototype,"endAligned",void 0),(0,u.__decorate)([(0,h.MZ)({type:String})],v.prototype,"prefix",void 0),(0,u.__decorate)([(0,h.MZ)({type:String})],v.prototype,"suffix",void 0),(0,u.__decorate)([(0,h.MZ)({type:String})],v.prototype,"name",void 0),(0,u.__decorate)([(0,h.MZ)({type:String,attribute:"input-mode"})],v.prototype,"inputMode",void 0),(0,u.__decorate)([(0,h.MZ)({type:Boolean})],v.prototype,"readOnly",void 0),(0,u.__decorate)([(0,h.MZ)({attribute:!1,type:String})],v.prototype,"autocapitalize",void 0),(0,u.__decorate)([(0,h.wk)()],v.prototype,"_unmaskedPassword",void 0),(0,u.__decorate)([(0,h.P)("ha-textfield")],v.prototype,"_textField",void 0),(0,u.__decorate)([(0,h.Ls)({passive:!0})],v.prototype,"_handleInputEvent",null),(0,u.__decorate)([(0,h.Ls)({passive:!0})],v.prototype,"_handleChangeEvent",null),v=(0,u.__decorate)([(0,h.EM)("ha-password-field")],v)},1958:function(t,e,i){var a,s=i(56038),n=i(44734),o=i(69683),r=i(6454),l=i(62826),c=i(22652),u=i(98887),d=i(96196),h=i(77845),p=function(t){function e(){return(0,n.A)(this,e),(0,o.A)(this,e,arguments)}return(0,r.A)(e,t),(0,s.A)(e)}(c.F);p.styles=[u.R,(0,d.AH)(a||(a=(t=>t)`
      :host {
        --mdc-theme-secondary: var(--primary-color);
      }
    `))],p=(0,l.__decorate)([(0,h.EM)("ha-radio")],p)},18043:function(t,e,i){i.a(t,(async function(t,e){try{var a=i(44734),s=i(56038),n=i(69683),o=i(6454),r=i(25460),l=(i(28706),i(62826)),c=i(25625),u=i(96196),d=i(77845),h=i(77646),p=i(74522),v=t([h]);h=(v.then?(await v)():v)[0];var _=function(t){function e(){var t;(0,a.A)(this,e);for(var i=arguments.length,s=new Array(i),o=0;o<i;o++)s[o]=arguments[o];return(t=(0,n.A)(this,e,[].concat(s))).capitalize=!1,t}return(0,o.A)(e,t),(0,s.A)(e,[{key:"disconnectedCallback",value:function(){(0,r.A)(e,"disconnectedCallback",this,3)([]),this._clearInterval()}},{key:"connectedCallback",value:function(){(0,r.A)(e,"connectedCallback",this,3)([]),this.datetime&&this._startInterval()}},{key:"createRenderRoot",value:function(){return this}},{key:"firstUpdated",value:function(t){(0,r.A)(e,"firstUpdated",this,3)([t]),this._updateRelative()}},{key:"update",value:function(t){(0,r.A)(e,"update",this,3)([t]),this._updateRelative()}},{key:"_clearInterval",value:function(){this._interval&&(window.clearInterval(this._interval),this._interval=void 0)}},{key:"_startInterval",value:function(){this._clearInterval(),this._interval=window.setInterval((()=>this._updateRelative()),6e4)}},{key:"_updateRelative",value:function(){if(this.datetime){var t="string"==typeof this.datetime?(0,c.H)(this.datetime):this.datetime,e=(0,h.K)(t,this.hass.locale);this.innerHTML=this.capitalize?(0,p.Z)(e):e}else this.innerHTML=this.hass.localize("ui.components.relative_time.never")}}])}(u.mN);(0,l.__decorate)([(0,d.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,l.__decorate)([(0,d.MZ)({attribute:!1})],_.prototype,"datetime",void 0),(0,l.__decorate)([(0,d.MZ)({type:Boolean})],_.prototype,"capitalize",void 0),_=(0,l.__decorate)([(0,d.EM)("ha-relative-time")],_),e()}catch(g){e(g)}}))},47813:function(t,e,i){var a,s,n,o,r,l=i(44734),c=i(56038),u=i(69683),d=i(6454),h=(i(52675),i(89463),i(28706),i(62062),i(18111),i(61701),i(2892),i(26099),i(62826)),p=i(96196),v=i(77845),_=i(94333),g=i(29485),f=i(92542),y=i(55124),m=i(79599),w=(i(1958),t=>t),b=function(t){function e(){var t;(0,l.A)(this,e);for(var i=arguments.length,a=new Array(i),s=0;s<i;s++)a[s]=arguments[s];return(t=(0,u.A)(this,e,[].concat(a))).options=[],t}return(0,d.A)(e,t),(0,c.A)(e,[{key:"render",value:function(){var t,e=null!==(t=this.maxColumns)&&void 0!==t?t:3,i=Math.min(e,this.options.length);return(0,p.qy)(a||(a=w`
      <div class="list" style=${0}>
        ${0}
      </div>
    `),(0,g.W)({"--columns":i}),this.options.map((t=>this._renderOption(t))))}},{key:"_renderOption",value:function(t){var e,i=1===this.maxColumns,a=t.disabled||this.disabled||!1,r=t.value===this.value,l=(null===(e=this.hass)||void 0===e?void 0:e.themes.darkMode)||!1,c=!!this.hass&&(0,m.qC)(this.hass),u="object"==typeof t.image?l&&t.image.src_dark||t.image.src:t.image,d="object"==typeof t.image&&(c&&t.image.flip_rtl);return(0,p.qy)(s||(s=w`
      <label
        class="option ${0}"
        ?disabled=${0}
        @click=${0}
      >
        <div class="content">
          <ha-radio
            .checked=${0}
            .value=${0}
            .disabled=${0}
            @change=${0}
            @click=${0}
          ></ha-radio>
          <div class="text">
            <span class="label">${0}</span>
            ${0}
          </div>
        </div>
        ${0}
      </label>
    `),(0,_.H)({horizontal:i,selected:r}),a,this._labelClick,t.value===this.value,t.value,a,this._radioChanged,y.d,t.label,t.description?(0,p.qy)(n||(n=w`<span class="description">${0}</span>`),t.description):p.s6,u?(0,p.qy)(o||(o=w`
              <img class=${0} alt="" src=${0} />
            `),d?"flipped":"",u):p.s6)}},{key:"_labelClick",value:function(t){var e;t.stopPropagation(),null===(e=t.currentTarget.querySelector("ha-radio"))||void 0===e||e.click()}},{key:"_radioChanged",value:function(t){var e;t.stopPropagation();var i=t.currentTarget.value;this.disabled||void 0===i||i===(null!==(e=this.value)&&void 0!==e?e:"")||(0,f.r)(this,"value-changed",{value:i})}}])}(p.WF);b.styles=(0,p.AH)(r||(r=w`
    .list {
      display: grid;
      grid-template-columns: repeat(var(--columns, 1), minmax(0, 1fr));
      gap: var(--ha-space-3);
    }
    .option {
      position: relative;
      display: block;
      border: 1px solid var(--divider-color);
      border-radius: var(--ha-card-border-radius, var(--ha-border-radius-lg));
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      padding: 12px;
      gap: var(--ha-space-2);
      overflow: hidden;
      cursor: pointer;
    }

    .option .content {
      position: relative;
      display: flex;
      flex-direction: row;
      gap: var(--ha-space-2);
      min-width: 0;
      width: 100%;
    }
    .option .content ha-radio {
      margin: -12px;
      flex: none;
    }
    .option .content .text {
      display: flex;
      flex-direction: column;
      gap: var(--ha-space-1);
      min-width: 0;
      flex: 1;
    }
    .option .content .text .label {
      color: var(--primary-text-color);
      font-size: var(--ha-font-size-m);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-condensed);
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
    .option .content .text .description {
      color: var(--secondary-text-color);
      font-size: var(--ha-font-size-s);
      font-weight: var(--ha-font-weight-normal);
      line-height: var(--ha-line-height-condensed);
    }
    img {
      position: relative;
      max-width: var(--ha-select-box-image-size, 96px);
      max-height: var(--ha-select-box-image-size, 96px);
      margin: auto;
    }

    .flipped {
      transform: scaleX(-1);
    }

    .option.horizontal {
      flex-direction: row;
      align-items: flex-start;
    }

    .option.horizontal img {
      margin: 0;
    }

    .option:before {
      content: "";
      display: block;
      inset: 0;
      position: absolute;
      background-color: transparent;
      pointer-events: none;
      opacity: 0.2;
      transition:
        background-color 180ms ease-in-out,
        opacity 180ms ease-in-out;
    }
    .option:hover:before {
      background-color: var(--divider-color);
    }
    .option.selected:before {
      background-color: var(--primary-color);
    }
    .option[disabled] {
      cursor: not-allowed;
    }
    .option[disabled] .content,
    .option[disabled] img {
      opacity: 0.5;
    }
    .option[disabled]:before {
      background-color: var(--disabled-color);
      opacity: 0.05;
    }
  `)),(0,h.__decorate)([(0,v.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,h.__decorate)([(0,v.MZ)({attribute:!1})],b.prototype,"options",void 0),(0,h.__decorate)([(0,v.MZ)({attribute:!1})],b.prototype,"value",void 0),(0,h.__decorate)([(0,v.MZ)({type:Boolean})],b.prototype,"disabled",void 0),(0,h.__decorate)([(0,v.MZ)({type:Number,attribute:"max_columns"})],b.prototype,"maxColumns",void 0),b=(0,h.__decorate)([(0,v.EM)("ha-select-box")],b)},45369:function(t,e,i){i.d(e,{QC:function(){return s},ds:function(){return u},mp:function(){return r},nx:function(){return o},u6:function(){return l},vU:function(){return n},zn:function(){return c}});var a=i(94741),s=(i(28706),(t,e,i)=>"run-start"===e.type?t={init_options:i,stage:"ready",run:e.data,events:[e],started:new Date(e.timestamp)}:t?((t="wake_word-start"===e.type?Object.assign(Object.assign({},t),{},{stage:"wake_word",wake_word:Object.assign(Object.assign({},e.data),{},{done:!1})}):"wake_word-end"===e.type?Object.assign(Object.assign({},t),{},{wake_word:Object.assign(Object.assign(Object.assign({},t.wake_word),e.data),{},{done:!0})}):"stt-start"===e.type?Object.assign(Object.assign({},t),{},{stage:"stt",stt:Object.assign(Object.assign({},e.data),{},{done:!1})}):"stt-end"===e.type?Object.assign(Object.assign({},t),{},{stt:Object.assign(Object.assign(Object.assign({},t.stt),e.data),{},{done:!0})}):"intent-start"===e.type?Object.assign(Object.assign({},t),{},{stage:"intent",intent:Object.assign(Object.assign({},e.data),{},{done:!1})}):"intent-end"===e.type?Object.assign(Object.assign({},t),{},{intent:Object.assign(Object.assign(Object.assign({},t.intent),e.data),{},{done:!0})}):"tts-start"===e.type?Object.assign(Object.assign({},t),{},{stage:"tts",tts:Object.assign(Object.assign({},e.data),{},{done:!1})}):"tts-end"===e.type?Object.assign(Object.assign({},t),{},{tts:Object.assign(Object.assign(Object.assign({},t.tts),e.data),{},{done:!0})}):"run-end"===e.type?Object.assign(Object.assign({},t),{},{finished:new Date(e.timestamp),stage:"done"}):"error"===e.type?Object.assign(Object.assign({},t),{},{finished:new Date(e.timestamp),stage:"error",error:e.data}):Object.assign({},t)).events=[].concat((0,a.A)(t.events),[e]),t):void console.warn("Received unexpected event before receiving session",e)),n=(t,e,i)=>t.connection.subscribeMessage(e,Object.assign(Object.assign({},i),{},{type:"assist_pipeline/run"})),o=t=>t.callWS({type:"assist_pipeline/pipeline/list"}),r=(t,e)=>t.callWS({type:"assist_pipeline/pipeline/get",pipeline_id:e}),l=(t,e)=>t.callWS(Object.assign({type:"assist_pipeline/pipeline/create"},e)),c=(t,e,i)=>t.callWS(Object.assign({type:"assist_pipeline/pipeline/update",pipeline_id:e},i)),u=t=>t.callWS({type:"assist_pipeline/language/list"})},98320:function(t,e,i){i.d(e,{ZE:function(){return a},e1:function(){return n},vc:function(){return s}});var a=function(t){return t[t.CONTROL=1]="CONTROL",t}({}),s=(t,e,i)=>t.callWS({type:"conversation/agent/list",language:e,country:i}),n=(t,e,i)=>t.callWS({type:"conversation/agent/homeassistant/language_scores",language:e,country:i})},7647:function(t,e,i){i.d(e,{j:function(){return s}});var a=i(92542),s=(t,e)=>{(0,a.r)(t,"haptic",e)}},34402:function(t,e,i){i.d(e,{xG:function(){return c},b3:function(){return r},eK:function(){return l}});var a=i(61397),s=i(50264),n=(i(16280),i(50113),i(18111),i(20116),i(26099),i(53045)),o=i(95260),r=function(){var t=(0,s.A)((0,a.A)().m((function t(e){var i;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:if(!(0,n.v)(e.config.version,2021,2,4)){t.n=1;break}return t.a(2,e.callWS({type:"supervisor/api",endpoint:"/addons",method:"get"}));case 1:return i=o.PS,t.n=2,e.callApi("GET","hassio/addons");case 2:return t.a(2,i(t.v))}}),t)})));return function(e){return t.apply(this,arguments)}}(),l=function(){var t=(0,s.A)((0,a.A)().m((function t(e,i){return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:if(!(0,n.v)(e.config.version,2021,2,4)){t.n=1;break}return t.a(2,e.callWS({type:"supervisor/api",endpoint:`/addons/${i}/start`,method:"post",timeout:null}));case 1:return t.a(2,e.callApi("POST",`hassio/addons/${i}/start`))}}),t)})));return function(e,i){return t.apply(this,arguments)}}(),c=function(){var t=(0,s.A)((0,a.A)().m((function t(e,i){return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:if(!(0,n.v)(e.config.version,2021,2,4)){t.n=2;break}return t.n=1,e.callWS({type:"supervisor/api",endpoint:`/addons/${i}/install`,method:"post",timeout:null});case 1:case 3:return t.a(2);case 2:return t.n=3,e.callApi("POST",`hassio/addons/${i}/install`)}}),t)})));return function(e,i){return t.apply(this,arguments)}}()},95260:function(t,e,i){i.d(e,{PS:function(){return a},VR:function(){return s}});i(61397),i(50264),i(74423),i(23792),i(26099),i(31415),i(17642),i(58004),i(33853),i(45876),i(32475),i(15024),i(31698),i(62953),i(53045);var a=t=>t.data,s=t=>"object"==typeof t?"object"==typeof t.body?t.body.message||"Unknown error, see supervisor logs":t.body||t.message||"Unknown error, see supervisor logs":t;new Set([502,503,504])},84043:function(t,e,i){i.d(e,{w:function(){return a}});var a=(t,e,i)=>t.callService("select","select_option",{option:i},{entity_id:e})},61970:function(t,e,i){i.d(e,{T:function(){return a}});var a=(t,e,i)=>t.callWS({type:"stt/engine/list",language:e,country:i})},40979:function(t,e,i){i.d(e,{d:function(){return a}});var a=t=>t.callWS({type:"wyoming/info"})},41745:function(t,e,i){i.a(t,(async function(t,e){try{var a=i(44734),s=i(56038),n=i(69683),o=i(6454),r=i(62826),l=i(96196),c=i(77845),u=i(92542),d=i(89473),h=(i(60961),i(76681)),p=i(51120),v=t([d]);d=(v.then?(await v)():v)[0];var _,g,f=t=>t,y=function(t){function e(){return(0,a.A)(this,e),(0,n.A)(this,e,arguments)}return(0,o.A)(e,t),(0,s.A)(e,[{key:"render",value:function(){var t,e,i;return(0,l.qy)(_||(_=f`<div class="content">
        <img
          src=${0}
          alt="Nabu Casa logo"
        />
        <h1>
          ${0}
        </h1>
        <div class="features">
          <div class="feature speech">
            <div class="logos">
              <div class="round-icon">
                <ha-svg-icon .path=${0}></ha-svg-icon>
              </div>
            </div>
            <h2>
              ${0}
              <span class="no-wrap"></span>
            </h2>
            <p>
              ${0}
            </p>
          </div>
          <div class="feature access">
            <div class="logos">
              <div class="round-icon">
                <ha-svg-icon .path=${0}></ha-svg-icon>
              </div>
            </div>
            <h2>
              ${0}
              <span class="no-wrap"></span>
            </h2>
            <p>
              ${0}
            </p>
          </div>
          <div class="feature">
            <div class="logos">
              <img
                alt="Google Assistant"
                src=${0}
                crossorigin="anonymous"
                referrerpolicy="no-referrer"
              />
              <img
                alt="Amazon Alexa"
                src=${0}
                crossorigin="anonymous"
                referrerpolicy="no-referrer"
              />
            </div>
            <h2>
              ${0}
            </h2>
            <p>
              ${0}
            </p>
          </div>
        </div>
      </div>
      <div class="footer side-by-side">
        <ha-button
          href="https://www.nabucasa.com"
          target="_blank"
          rel="noreferrer noopener"
          appearance="plain"
        >
          <ha-svg-icon .path=${0} slot="start"></ha-svg-icon>
          nabucasa.com
        </ha-button>
        <ha-button @click=${0}
          >${0}</ha-button
        >
      </div>`),`/static/images/logo_nabu_casa${null!==(t=this.hass.themes)&&void 0!==t&&t.darkMode?"_dark":""}.png`,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.cloud.title"),"M8,7A2,2 0 0,1 10,9V14A2,2 0 0,1 8,16A2,2 0 0,1 6,14V9A2,2 0 0,1 8,7M14,14C14,16.97 11.84,19.44 9,19.92V22H7V19.92C4.16,19.44 2,16.97 2,14H4A4,4 0 0,0 8,18A4,4 0 0,0 12,14H14M21.41,9.41L17.17,13.66L18.18,10H14A2,2 0 0,1 12,8V4A2,2 0 0,1 14,2H20A2,2 0 0,1 22,4V8C22,8.55 21.78,9.05 21.41,9.41Z",this.hass.localize("ui.panel.config.voice_assistants.assistants.cloud.features.speech.title"),this.hass.localize("ui.panel.config.voice_assistants.assistants.cloud.features.speech.text"),"M17.9,17.39C17.64,16.59 16.89,16 16,16H15V13A1,1 0 0,0 14,12H8V10H10A1,1 0 0,0 11,9V7H13A2,2 0 0,0 15,5V4.59C17.93,5.77 20,8.64 20,12C20,14.08 19.2,15.97 17.9,17.39M11,19.93C7.05,19.44 4,16.08 4,12C4,11.38 4.08,10.78 4.21,10.21L9,15V16A2,2 0 0,0 11,18M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z",this.hass.localize("ui.panel.config.voice_assistants.assistants.cloud.features.remote_access.title"),this.hass.localize("ui.panel.config.voice_assistants.assistants.cloud.features.remote_access.text"),(0,h.MR)({domain:"google_assistant",type:"icon",darkOptimized:null===(e=this.hass.themes)||void 0===e?void 0:e.darkMode}),(0,h.MR)({domain:"alexa",type:"icon",darkOptimized:null===(i=this.hass.themes)||void 0===i?void 0:i.darkMode}),this.hass.localize("ui.panel.config.voice_assistants.assistants.cloud.features.assistants.title"),this.hass.localize("ui.panel.config.voice_assistants.assistants.cloud.features.assistants.text"),"M14,3V5H17.59L7.76,14.83L9.17,16.24L19,6.41V10H21V3M19,19H5V5H12V3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V12H19V19Z",this._signUp,this.hass.localize("ui.panel.config.cloud.register.headline"))}},{key:"_signUp",value:function(){(0,u.r)(this,"cloud-step",{step:"SIGNUP"})}}])}(l.WF);y.styles=[p.s,(0,l.AH)(g||(g=f`
      :host {
        display: flex;
      }
      .features {
        display: flex;
        flex-direction: column;
        grid-gap: var(--ha-space-4);
        padding: 16px;
      }
      .feature {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        margin-bottom: 16px;
      }
      .feature .logos {
        margin-bottom: 16px;
      }
      .feature .logos > * {
        width: 40px;
        height: 40px;
        margin: 0 4px;
      }
      .round-icon {
        border-radius: var(--ha-border-radius-circle);
        color: #6e41ab;
        background-color: #e8dcf7;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: var(--ha-font-size-2xl);
      }
      .access .round-icon {
        color: #00aef8;
        background-color: #cceffe;
      }
      .feature h2 {
        font-size: var(--ha-font-size-l);
        font-weight: var(--ha-font-weight-medium);
        line-height: var(--ha-line-height-normal);
        margin-top: 0;
        margin-bottom: 8px;
      }
      .feature p {
        font-size: var(--ha-font-size-m);
        font-weight: var(--ha-font-weight-normal);
        line-height: var(--ha-line-height-condensed);
        margin: 0;
      }
    `))],(0,r.__decorate)([(0,c.MZ)({attribute:!1})],y.prototype,"hass",void 0),y=(0,r.__decorate)([(0,c.EM)("cloud-step-intro")],y),e()}catch(m){e(m)}}))},50577:function(t,e,i){i.a(t,(async function(t,e){try{var a=i(61397),s=i(50264),n=i(44734),o=i(56038),r=i(69683),l=i(6454),c=(i(28706),i(58335),i(62826)),u=i(96196),d=i(77845),h=i(92542),p=i(5871),v=(i(17963),i(89473)),_=(i(68757),i(60961),i(78740),i(71750)),g=i(86466),f=i(10234),y=i(51120),m=t([v]);v=(m.then?(await m)():m)[0];var w,b,k,A=t=>t,$=function(t){function e(){var t;(0,n.A)(this,e);for(var i=arguments.length,a=new Array(i),s=0;s<i;s++)a[s]=arguments[s];return(t=(0,r.A)(this,e,[].concat(a)))._requestInProgress=!1,t._checkConnection=!0,t}return(0,l.A)(e,t),(0,o.A)(e,[{key:"render",value:function(){var t;return(0,u.qy)(w||(w=A`<div class="content">
        <img
          src=${0}
          alt="Nabu Casa logo"
        />
        <h1>${0}</h1>
        ${0}
        <ha-textfield
          autofocus
          id="email"
          name="email"
          .label=${0}
          .disabled=${0}
          type="email"
          autocomplete="email"
          required
          @keydown=${0}
          validationMessage=${0}
        ></ha-textfield>
        <ha-password-field
          id="password"
          name="password"
          .label=${0}
          .disabled=${0}
          autocomplete="new-password"
          minlength="8"
          required
          @keydown=${0}
          validationMessage=${0}
        ></ha-password-field>
      </div>
      <div class="footer">
        <ha-button
          @click=${0}
          .disabled=${0}
          >${0}</ha-button
        >
      </div>`),`/static/images/logo_nabu_casa${null!==(t=this.hass.themes)&&void 0!==t&&t.darkMode?"_dark":""}.png`,this.hass.localize("ui.panel.config.cloud.login.sign_in"),this._error?(0,u.qy)(b||(b=A`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):"",this.hass.localize("ui.panel.config.cloud.register.email_address"),this._requestInProgress,this._keyDown,this.hass.localize("ui.panel.config.cloud.register.email_error_msg"),this.hass.localize("ui.panel.config.cloud.register.password"),this._requestInProgress,this._keyDown,this.hass.localize("ui.panel.config.cloud.register.password_error_msg"),this._handleLogin,this._requestInProgress,this.hass.localize("ui.panel.config.cloud.login.sign_in"))}},{key:"_keyDown",value:function(t){"Enter"===t.key&&this._handleLogin()}},{key:"_handleLogin",value:(i=(0,s.A)((0,a.A)().m((function t(){var e,i,n,o,r,l=this;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:if(e=this._emailField,i=this._passwordField,n=e.value,o=i.value,e.reportValidity()){t.n=1;break}return i.reportValidity(),e.focus(),t.a(2);case 1:if(i.reportValidity()){t.n=2;break}return i.focus(),t.a(2);case 2:return this._requestInProgress=!0,r=function(){var t=(0,s.A)((0,a.A)().m((function t(i,s){var n,c,u,d;return(0,a.A)().w((function(t){for(;;)switch(t.p=t.n){case 0:return t.p=0,t.n=1,(0,_.p7)(Object.assign(Object.assign({hass:l.hass,email:i},s?{code:s}:{password:o}),{},{check_connection:l._checkConnection}));case 1:t.n=16;break;case 2:if(t.p=2,u=t.v,"mfarequired"!==(n=u&&u.body&&u.body.code)){t.n=5;break}return t.n=3,(0,f.an)(l,{title:l.hass.localize("ui.panel.config.cloud.login.totp_code_prompt_title"),inputLabel:l.hass.localize("ui.panel.config.cloud.login.totp_code"),inputType:"text",defaultValue:"",confirmText:l.hass.localize("ui.panel.config.cloud.login.submit")});case 3:if(null===(c=t.v)||""===c){t.n=5;break}return t.n=4,r(i,c);case 4:return t.a(2);case 5:if("alreadyconnectederror"!==n){t.n=6;break}return(0,g.o)(l,{details:JSON.parse(u.body.message),logInHereAction:()=>{l._checkConnection=!1,r(i)},closeDialog:()=>{l._requestInProgress=!1}}),t.a(2);case 6:if("usernotfound"!==n||i===i.toLowerCase()){t.n=8;break}return t.n=7,r(i.toLowerCase());case 7:return t.a(2);case 8:if("PasswordChangeRequired"!==n){t.n=9;break}return(0,f.K$)(l,{title:l.hass.localize("ui.panel.config.cloud.login.alert_password_change_required")}),(0,p.o)("/config/cloud/forgot-password"),(0,h.r)(l,"closed"),t.a(2);case 9:l._requestInProgress=!1,d=n,t.n="UserNotConfirmed"===d?10:"mfarequired"===d?11:"mfaexpiredornotstarted"===d?12:"invalidtotpcode"===d?13:14;break;case 10:return l._error=l.hass.localize("ui.panel.config.cloud.login.alert_email_confirm_necessary"),t.a(3,15);case 11:return l._error=l.hass.localize("ui.panel.config.cloud.login.alert_mfa_code_required"),t.a(3,15);case 12:return l._error=l.hass.localize("ui.panel.config.cloud.login.alert_mfa_expired_or_not_started"),t.a(3,15);case 13:return l._error=l.hass.localize("ui.panel.config.cloud.login.alert_totp_code_invalid"),t.a(3,15);case 14:return l._error=u&&u.body&&u.body.message?u.body.message:"Unknown error",t.a(3,15);case 15:e.focus();case 16:return t.a(2)}}),t,null,[[0,2]])})));return function(e,i){return t.apply(this,arguments)}}(),t.n=3,r(n);case 3:return t.a(2)}}),t,this)}))),function(){return i.apply(this,arguments)})}]);var i}(u.WF);$.styles=[y.s,(0,u.AH)(k||(k=A`
      :host {
        display: block;
      }
      ha-textfield,
      ha-password-field {
        display: block;
      }
    `))],(0,c.__decorate)([(0,d.MZ)({attribute:!1})],$.prototype,"hass",void 0),(0,c.__decorate)([(0,d.wk)()],$.prototype,"_requestInProgress",void 0),(0,c.__decorate)([(0,d.wk)()],$.prototype,"_error",void 0),(0,c.__decorate)([(0,d.wk)()],$.prototype,"_checkConnection",void 0),(0,c.__decorate)([(0,d.P)("#email",!0)],$.prototype,"_emailField",void 0),(0,c.__decorate)([(0,d.P)("#password",!0)],$.prototype,"_passwordField",void 0),$=(0,c.__decorate)([(0,d.EM)("cloud-step-signin")],$),e()}catch(x){e(x)}}))},35215:function(t,e,i){i.a(t,(async function(t,e){try{var a=i(61397),s=i(50264),n=i(44734),o=i(56038),r=i(69683),l=i(6454),c=(i(28706),i(62826)),u=i(96196),d=i(77845),h=i(92542),p=(i(17963),i(89473)),v=(i(68757),i(60961),i(78740),i(71750)),_=i(51120),g=t([p]);p=(g.then?(await g)():g)[0];var f,y,m,w,b,k,A,$=t=>t,x=function(t){function e(){var t;(0,n.A)(this,e);for(var i=arguments.length,a=new Array(i),s=0;s<i;s++)a[s]=arguments[s];return(t=(0,r.A)(this,e,[].concat(a)))._requestInProgress=!1,t}return(0,l.A)(e,t),(0,o.A)(e,[{key:"render",value:function(){var t;return(0,u.qy)(f||(f=$`<div class="content">
        <img
          src=${0}
          alt="Nabu Casa logo"
        />
        <h1>
          ${0}
        </h1>
        ${0}
        ${0}
      </div>
      <div class="footer side-by-side">
        ${0}
      </div>`),`/static/images/logo_nabu_casa${null!==(t=this.hass.themes)&&void 0!==t&&t.darkMode?"_dark":""}.png`,this.hass.localize("ui.panel.config.cloud.register.create_account"),this._error?(0,u.qy)(y||(y=$`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):"","VERIFY"===this._state?(0,u.qy)(m||(m=$`<p>
              ${0}
            </p>`),this.hass.localize("ui.panel.config.cloud.register.confirm_email",{email:this._email})):(0,u.qy)(w||(w=$`<ha-textfield
                autofocus
                id="email"
                name="email"
                .label=${0}
                .disabled=${0}
                type="email"
                autocomplete="email"
                required
                @keydown=${0}
                validationMessage=${0}
              ></ha-textfield>
              <ha-password-field
                id="password"
                name="password"
                .label=${0}
                .disabled=${0}
                autocomplete="new-password"
                minlength="8"
                required
                @keydown=${0}
                validationMessage=${0}
              ></ha-password-field>`),this.hass.localize("ui.panel.config.cloud.register.email_address"),this._requestInProgress,this._keyDown,this.hass.localize("ui.panel.config.cloud.register.email_error_msg"),this.hass.localize("ui.panel.config.cloud.register.password"),this._requestInProgress,this._keyDown,this.hass.localize("ui.panel.config.cloud.register.password_error_msg")),"VERIFY"===this._state?(0,u.qy)(b||(b=$`<ha-button
                @click=${0}
                .disabled=${0}
                appearance="plain"
                >${0}</ha-button
              ><ha-button
                @click=${0}
                .disabled=${0}
                >${0}</ha-button
              >`),this._handleResendVerifyEmail,this._requestInProgress,this.hass.localize("ui.panel.config.cloud.register.resend_confirm_email"),this._login,this._requestInProgress,this.hass.localize("ui.panel.config.cloud.register.clicked_confirm")):(0,u.qy)(k||(k=$`<ha-button
                @click=${0}
                .disabled=${0}
                appearance="plain"
                >${0}</ha-button
              >
              <ha-button
                @click=${0}
                .disabled=${0}
                >${0}</ha-button
              >`),this._signIn,this._requestInProgress,this.hass.localize("ui.panel.config.cloud.login.sign_in"),this._handleRegister,this._requestInProgress,this.hass.localize("ui.common.next")))}},{key:"_signIn",value:function(){(0,h.r)(this,"cloud-step",{step:"SIGNIN"})}},{key:"_keyDown",value:function(t){"Enter"===t.key&&this._handleRegister()}},{key:"_handleRegister",value:(d=(0,s.A)((0,a.A)().m((function t(){var e,i,s,n,o;return(0,a.A)().w((function(t){for(;;)switch(t.p=t.n){case 0:if(e=this._emailField,i=this._passwordField,e.reportValidity()){t.n=1;break}return i.reportValidity(),e.focus(),t.a(2);case 1:if(i.reportValidity()){t.n=2;break}return i.focus(),t.a(2);case 2:return s=e.value.toLowerCase(),n=i.value,this._requestInProgress=!0,t.p=3,t.n=4,(0,v.vO)(this.hass,s,n);case 4:this._email=s,this._password=n,this._verificationEmailSent(),t.n=6;break;case 5:t.p=5,o=t.v,this._password="",this._error=o&&o.body&&o.body.message?o.body.message:"Unknown error";case 6:return t.p=6,this._requestInProgress=!1,t.f(6);case 7:return t.a(2)}}),t,this,[[3,5,6,7]])}))),function(){return d.apply(this,arguments)})},{key:"_handleResendVerifyEmail",value:(c=(0,s.A)((0,a.A)().m((function t(){var e;return(0,a.A)().w((function(t){for(;;)switch(t.p=t.n){case 0:if(this._email){t.n=1;break}return t.a(2);case 1:return t.p=1,t.n=2,(0,v.q3)(this.hass,this._email);case 2:this._verificationEmailSent(),t.n=4;break;case 3:t.p=3,e=t.v,this._error=e&&e.body&&e.body.message?e.body.message:"Unknown error";case 4:return t.a(2)}}),t,this,[[1,3]])}))),function(){return c.apply(this,arguments)})},{key:"_verificationEmailSent",value:function(){this._state="VERIFY",setTimeout((()=>this._login()),5e3)}},{key:"_login",value:(i=(0,s.A)((0,a.A)().m((function t(){var e,i;return(0,a.A)().w((function(t){for(;;)switch(t.p=t.n){case 0:if(this._email&&this._password){t.n=1;break}return t.a(2);case 1:return t.p=1,t.n=2,(0,v.p7)({hass:this.hass,email:this._email,password:this._password});case 2:(0,h.r)(this,"cloud-step",{step:"DONE"}),t.n=4;break;case 3:t.p=3,"usernotconfirmed"===(null==(i=t.v)||null===(e=i.body)||void 0===e?void 0:e.code)?this._verificationEmailSent():this._error="Something went wrong. Please try again.";case 4:return t.a(2)}}),t,this,[[1,3]])}))),function(){return i.apply(this,arguments)})}]);var i,c,d}(u.WF);x.styles=[_.s,(0,u.AH)(A||(A=$`
      .content {
        width: 100%;
      }
      ha-textfield,
      ha-password-field {
        display: block;
      }
    `))],(0,c.__decorate)([(0,d.MZ)({attribute:!1})],x.prototype,"hass",void 0),(0,c.__decorate)([(0,d.wk)()],x.prototype,"_requestInProgress",void 0),(0,c.__decorate)([(0,d.wk)()],x.prototype,"_email",void 0),(0,c.__decorate)([(0,d.wk)()],x.prototype,"_password",void 0),(0,c.__decorate)([(0,d.wk)()],x.prototype,"_error",void 0),(0,c.__decorate)([(0,d.wk)()],x.prototype,"_state",void 0),(0,c.__decorate)([(0,d.P)("#email",!0)],x.prototype,"_emailField",void 0),(0,c.__decorate)([(0,d.P)("#password",!0)],x.prototype,"_passwordField",void 0),x=(0,c.__decorate)([(0,d.EM)("cloud-step-signup")],x),e()}catch(z){e(z)}}))},51120:function(t,e,i){i.d(e,{s:function(){return n}});var a,s=i(96196),n=[i(39396).RF,(0,s.AH)(a||(a=(t=>t)`
    :host {
      align-items: center;
      text-align: center;
      min-height: 400px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      height: 100%;
      padding: 24px;
      box-sizing: border-box;
    }
    .content {
      flex: 1;
    }
    .content img {
      width: 120px;
    }
    @media all and (max-width: 450px), all and (max-height: 500px) {
      :host {
        min-height: 100%;
        height: auto;
      }
      .content img {
        margin-top: 68px;
        margin-bottom: 68px;
      }
    }
    .footer {
      display: flex;
      width: 100%;
      flex-direction: row;
      justify-content: flex-end;
    }
    .footer.full-width {
      flex-direction: column;
    }
    .footer.full-width ha-button {
      width: 100%;
    }
    .footer.centered {
      justify-content: center;
    }
    .footer.side-by-side {
      justify-content: space-between;
    }
  `))]},54728:function(t,e,i){i.a(t,(async function(t,a){try{i.r(e),i.d(e,{HaVoiceAssistantSetupDialog:function(){return Q},STEP:function(){return X}});var s=i(78261),n=i(61397),o=i(50264),r=i(44734),l=i(56038),c=i(69683),u=i(6454),d=(i(28706),i(2008),i(50113),i(74423),i(62062),i(44114),i(18111),i(22489),i(20116),i(61701),i(5506),i(26099),i(16034),i(62826)),h=i(96196),p=i(77845),v=i(22786),_=i(92542),g=i(41144),f=i(31747),y=(i(74529),i(95637),i(51362)),m=(i(63419),i(41558)),w=i(98320),b=i(31136),k=i(39396),A=i(12914),$=i(12849),x=i(8439),z=i(24946),C=i(52124),E=i(67993),M=i(93008),S=i(33694),I=i(6960),O=t([A,$,x,z,C,E,M,S,I,f,y]);[A,$,x,z,C,E,M,S,I,f,y]=O.then?(await O)():O;var P,L,q,T,H,Z,j,N,W,D,V,F,R,U,B,K,J,G,Y=t=>t,X=function(t){return t[t.INIT=0]="INIT",t[t.UPDATE=1]="UPDATE",t[t.CHECK=2]="CHECK",t[t.WAKEWORD=3]="WAKEWORD",t[t.AREA=4]="AREA",t[t.PIPELINE=5]="PIPELINE",t[t.SUCCESS=6]="SUCCESS",t[t.CLOUD=7]="CLOUD",t[t.LOCAL=8]="LOCAL",t[t.CHANGE_WAKEWORD=9]="CHANGE_WAKEWORD",t}({}),Q=function(t){function e(){var t;(0,r.A)(this,e);for(var i=arguments.length,a=new Array(i),s=0;s<i;s++)a[s]=arguments[s];return(t=(0,c.A)(this,e,[].concat(a)))._step=0,t._languages=[],t._previousSteps=[],t._deviceEntities=(0,v.A)(((t,e)=>Object.values(e).filter((e=>e.device_id===t)))),t._findDomainEntityId=(0,v.A)(((e,i,a)=>{var s;return null===(s=t._deviceEntities(e,i).find((t=>(0,g.m)(t.entity_id)===a)))||void 0===s?void 0:s.entity_id})),t}return(0,u.A)(e,t),(0,l.A)(e,[{key:"showDialog",value:(p=(0,o.A)((0,n.A)().m((function t(e){return(0,n.A)().w((function(t){for(;;)switch(t.n){case 0:return this._params=e,t.n=1,this._fetchAssistConfiguration();case 1:this._step=1;case 2:return t.a(2)}}),t,this)}))),function(t){return p.apply(this,arguments)})},{key:"closeDialog",value:(d=(0,o.A)((0,n.A)().m((function t(){var e;return(0,n.A)().w((function(t){for(;;)switch(t.n){case 0:null===(e=this.renderRoot.querySelector("ha-dialog"))||void 0===e||e.close();case 1:return t.a(2)}}),t,this)}))),function(){return d.apply(this,arguments)})},{key:"willUpdate",value:function(t){t.has("_step")&&5===this._step&&this._getLanguages()}},{key:"_dialogClosed",value:function(){this._params=void 0,this._assistConfiguration=void 0,this._previousSteps=[],this._nextStep=void 0,this._step=0,this._language=void 0,this._languages=[],this._localOption=void 0,(0,_.r)(this,"dialog-closed",{dialog:this.localName})}},{key:"render",value:function(){var t,e;if(!this._params)return h.s6;var i=this._findDomainEntityId(this._params.deviceId,this.hass.entities,"assist_satellite"),a=i?this.hass.states[i]:void 0;return(0,h.qy)(P||(P=Y`
      <ha-dialog
        open
        @closed=${0}
        .heading=${0}
        hideActions
        escapeKeyAction
        scrimClickAction
      >
        <ha-dialog-header slot="heading">
          ${0}
          ${0}
        </ha-dialog-header>
        <div
          class="content"
          @next-step=${0}
          @prev-step=${0}
        >
          ${0}
        </div>
      </ha-dialog>
    `),this._dialogClosed,"Voice Satellite setup",8===this._step?h.s6:this._previousSteps.length?(0,h.qy)(L||(L=Y`<ha-icon-button
                  slot="navigationIcon"
                  .label=${0}
                  .path=${0}
                  @click=${0}
                ></ha-icon-button>`),null!==(t=this.hass.localize("ui.common.back"))&&void 0!==t?t:"Back","M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z",this._goToPreviousStep):1!==this._step?(0,h.qy)(q||(q=Y`<ha-icon-button
                    slot="navigationIcon"
                    .label=${0}
                    .path=${0}
                    @click=${0}
                  ></ha-icon-button>`),null!==(e=this.hass.localize("ui.common.close"))&&void 0!==e?e:"Close","M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",this.closeDialog):h.s6,3===this._step||4===this._step?(0,h.qy)(T||(T=Y`<ha-button
                @click=${0}
                class="skip-btn"
                slot="actionItems"
                >${0}</ha-button
              >`),this._goToNextStep,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.skip")):5===this._step&&this._language?(0,h.qy)(H||(H=Y`<ha-md-button-menu
                    slot="actionItems"
                    positioning="fixed"
                  >
                    <ha-assist-chip
                      .label=${0}
                      slot="trigger"
                    >
                      <ha-svg-icon
                        slot="trailing-icon"
                        .path=${0}
                      ></ha-svg-icon
                    ></ha-assist-chip>
                    ${0}
                  </ha-md-button-menu>`),(0,f.T)(this._language,this.hass.locale),"M7,10L12,15L17,10H7Z",(0,y.t)(this._languages,!1,!1,this.hass.locale).map((t=>(0,h.qy)(Z||(Z=Y`<ha-md-menu-item
                          .value=${0}
                          @click=${0}
                          @keydown=${0}
                          .selected=${0}
                        >
                          ${0}
                        </ha-md-menu-item>`),t.id,this._handlePickLanguage,this._handlePickLanguage,this._language===t.id,t.primary)))):h.s6,this._goToNextStep,this._goToPreviousStep,1===this._step?(0,h.qy)(j||(j=Y`<ha-voice-assistant-setup-step-update
                .hass=${0}
                .updateEntityId=${0}
              ></ha-voice-assistant-setup-step-update>`),this.hass,this._findDomainEntityId(this._params.deviceId,this.hass.entities,"update")):this._error?(0,h.qy)(N||(N=Y`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):(null==a?void 0:a.state)===b.Hh?(0,h.qy)(W||(W=Y`<ha-alert alert-type="error"
                    >${0}</ha-alert
                  >`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.not_available")):2===this._step?(0,h.qy)(D||(D=Y`<ha-voice-assistant-setup-step-check
                      .hass=${0}
                      .assistEntityId=${0}
                    ></ha-voice-assistant-setup-step-check>`),this.hass,i):3===this._step?(0,h.qy)(V||(V=Y`<ha-voice-assistant-setup-step-wake-word
                        .hass=${0}
                        .assistConfiguration=${0}
                        .assistEntityId=${0}
                        .deviceEntities=${0}
                      ></ha-voice-assistant-setup-step-wake-word>`),this.hass,this._assistConfiguration,i,this._deviceEntities(this._params.deviceId,this.hass.entities)):9===this._step?(0,h.qy)(F||(F=Y`
                          <ha-voice-assistant-setup-step-change-wake-word
                            .hass=${0}
                            .assistConfiguration=${0}
                            .assistEntityId=${0}
                          ></ha-voice-assistant-setup-step-change-wake-word>
                        `),this.hass,this._assistConfiguration,i):4===this._step?(0,h.qy)(R||(R=Y`
                            <ha-voice-assistant-setup-step-area
                              .hass=${0}
                              .deviceId=${0}
                            ></ha-voice-assistant-setup-step-area>
                          `),this.hass,this._params.deviceId):5===this._step?(0,h.qy)(U||(U=Y`<ha-voice-assistant-setup-step-pipeline
                              .hass=${0}
                              .languages=${0}
                              .language=${0}
                              .assistConfiguration=${0}
                              .assistEntityId=${0}
                              @language-changed=${0}
                            ></ha-voice-assistant-setup-step-pipeline>`),this.hass,this._languages,this._language,this._assistConfiguration,i,this._languageChanged):7===this._step?(0,h.qy)(B||(B=Y`<ha-voice-assistant-setup-step-cloud
                                .hass=${0}
                              ></ha-voice-assistant-setup-step-cloud>`),this.hass):8===this._step?(0,h.qy)(K||(K=Y`<ha-voice-assistant-setup-step-local
                                  .hass=${0}
                                  .language=${0}
                                  .localOption=${0}
                                  .assistConfiguration=${0}
                                ></ha-voice-assistant-setup-step-local>`),this.hass,this._language,this._localOption,this._assistConfiguration):6===this._step?(0,h.qy)(J||(J=Y`<ha-voice-assistant-setup-step-success
                                    .hass=${0}
                                    .assistConfiguration=${0}
                                    .assistEntityId=${0}
                                    .deviceId=${0}
                                  ></ha-voice-assistant-setup-step-success>`),this.hass,this._assistConfiguration,i,this._params.deviceId):h.s6)}},{key:"_getLanguages",value:(a=(0,o.A)((0,n.A)().m((function t(){var e;return(0,n.A)().w((function(t){for(;;)switch(t.n){case 0:if(!this._languages.length){t.n=1;break}return t.a(2);case 1:return t.n=2,(0,w.e1)(this.hass);case 2:e=t.v,this._languages=Object.entries(e.languages).filter((t=>{var e=(0,s.A)(t,2),i=(e[0],e[1]);return i.cloud>0||i.full_local>0||i.focused_local>0})).map((t=>{var e=(0,s.A)(t,2),i=e[0];return e[1],i})),this._language=e.preferred_language&&this._languages.includes(e.preferred_language)?e.preferred_language:void 0;case 3:return t.a(2)}}),t,this)}))),function(){return a.apply(this,arguments)})},{key:"_fetchAssistConfiguration",value:(i=(0,o.A)((0,n.A)().m((function t(){var e;return(0,n.A)().w((function(t){for(;;)switch(t.p=t.n){case 0:return t.p=0,t.n=1,(0,m.Vy)(this.hass,this._findDomainEntityId(this._params.deviceId,this.hass.entities,"assist_satellite"));case 1:this._assistConfiguration=t.v,t.n=3;break;case 2:t.p=2,e=t.v,this._error=e.message;case 3:return t.a(2)}}),t,this,[[0,2]])}))),function(){return i.apply(this,arguments)})},{key:"_handlePickLanguage",value:function(t){"keydown"===t.type&&"Enter"!==t.key&&" "!==t.key||(this._language=t.target.value)}},{key:"_languageChanged",value:function(t){t.detail.value&&(this._language=t.detail.value)}},{key:"_goToPreviousStep",value:function(){this._previousSteps.length&&(this._step=this._previousSteps.pop())}},{key:"_goToNextStep",value:function(t){var e,i,a,s;null!=t&&null!==(e=t.detail)&&void 0!==e&&e.updateConfig&&this._fetchAssistConfiguration(),null!=t&&null!==(i=t.detail)&&void 0!==i&&i.nextStep&&(this._nextStep=t.detail.nextStep),null!=t&&null!==(a=t.detail)&&void 0!==a&&a.noPrevious||this._previousSteps.push(this._step),null!=t&&null!==(s=t.detail)&&void 0!==s&&s.step?(this._step=t.detail.step,8===t.detail.step&&(this._localOption=t.detail.option)):this._nextStep?(this._step=this._nextStep,this._nextStep=void 0):this._step+=1}}],[{key:"styles",get:function(){return[k.nA,(0,h.AH)(G||(G=Y`
        ha-dialog {
          --dialog-content-padding: 0;
        }
        @media all and (min-width: 450px) and (min-height: 500px) {
          ha-dialog {
            --mdc-dialog-min-width: 560px;
            --mdc-dialog-max-width: 560px;
            --mdc-dialog-min-width: min(560px, 95vw);
            --mdc-dialog-max-width: min(560px, 95vw);
          }
        }
        ha-dialog-header {
          height: 56px;
        }
        @media all and (max-width: 450px), all and (max-height: 500px) {
          .content {
            height: calc(100vh - 56px);
          }
        }
        .skip-btn {
          margin-top: 6px;
        }
        ha-alert {
          margin: 24px;
          display: block;
        }
        ha-md-button-menu {
          height: 48px;
          display: flex;
          align-items: center;
          margin-right: 12px;
          margin-inline-end: 12px;
          margin-inline-start: initial;
        }
      `))]}}]);var i,a,d,p}(h.WF);(0,d.__decorate)([(0,p.MZ)({attribute:!1})],Q.prototype,"hass",void 0),(0,d.__decorate)([(0,p.wk)()],Q.prototype,"_params",void 0),(0,d.__decorate)([(0,p.wk)()],Q.prototype,"_step",void 0),(0,d.__decorate)([(0,p.wk)()],Q.prototype,"_assistConfiguration",void 0),(0,d.__decorate)([(0,p.wk)()],Q.prototype,"_error",void 0),(0,d.__decorate)([(0,p.wk)()],Q.prototype,"_language",void 0),(0,d.__decorate)([(0,p.wk)()],Q.prototype,"_languages",void 0),(0,d.__decorate)([(0,p.wk)()],Q.prototype,"_localOption",void 0),Q=(0,d.__decorate)([(0,p.EM)("ha-voice-assistant-setup-dialog")],Q),a()}catch(tt){a(tt)}}))},12914:function(t,e,i){i.a(t,(async function(t,e){try{var a=i(61397),s=i(50264),n=i(44734),o=i(56038),r=i(69683),l=i(6454),c=i(62826),u=i(96196),d=i(77845),h=i(92542),p=i(53907),v=i(1491),_=i(10234),g=i(51120),f=t([p]);p=(f.then?(await f)():f)[0];var y,m,w=t=>t,b=function(t){function e(){return(0,n.A)(this,e),(0,r.A)(this,e,arguments)}return(0,l.A)(e,t),(0,o.A)(e,[{key:"render",value:function(){var t=this.hass.devices[this.deviceId];return(0,u.qy)(y||(y=w`<div class="content">
        <img
          src="/static/images/voice-assistant/area.png"
          alt="Casita Home Assistant logo"
        />
        <h1>
          ${0}
        </h1>
        <p class="secondary">
          ${0}
        </p>
        <ha-area-picker
          .hass=${0}
          .value=${0}
        ></ha-area-picker>
      </div>
      <div class="footer">
        <ha-button @click=${0}
          >${0}</ha-button
        >
      </div>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.area.title"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.area.secondary"),this.hass,t.area_id,this._setArea,this.hass.localize("ui.common.next"))}},{key:"_setArea",value:(i=(0,s.A)((0,a.A)().m((function t(){var e;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:if(e=this.shadowRoot.querySelector("ha-area-picker").value){t.n=1;break}return(0,_.K$)(this,{text:this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.area.no_selection")}),t.a(2);case 1:return t.n=2,(0,v.FB)(this.hass,this.deviceId,{area_id:e});case 2:this._nextStep();case 3:return t.a(2)}}),t,this)}))),function(){return i.apply(this,arguments)})},{key:"_nextStep",value:function(){(0,h.r)(this,"next-step")}}]);var i}(u.WF);b.styles=[g.s,(0,u.AH)(m||(m=w`
      ha-area-picker {
        display: block;
        width: 100%;
        margin-bottom: 24px;
        text-align: initial;
      }
    `))],(0,c.__decorate)([(0,d.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,c.__decorate)([(0,d.MZ)({attribute:!1})],b.prototype,"deviceId",void 0),b=(0,c.__decorate)([(0,d.EM)("ha-voice-assistant-setup-step-area")],b),e()}catch(k){e(k)}}))},12849:function(t,e,i){i.a(t,(async function(t,e){try{var a=i(61397),s=i(50264),n=i(44734),o=i(56038),r=i(69683),l=i(6454),c=(i(62062),i(18111),i(61701),i(26099),i(62826)),u=i(96196),d=i(77845),h=i(92542),p=(i(42921),i(23897),i(41558)),v=i(51120),_=i(54728),g=t([_]);_=(g.then?(await g)():g)[0];var f,y,m,w=t=>t,b=function(t){function e(){return(0,n.A)(this,e),(0,r.A)(this,e,arguments)}return(0,l.A)(e,t),(0,o.A)(e,[{key:"render",value:function(){return(0,u.qy)(f||(f=w`<div class="padding content">
        <img
          src="/static/images/voice-assistant/change-wake-word.png"
          alt="Casita Home Assistant logo"
        />
        <h1>
          ${0}
        </h1>
        <p class="secondary">
          ${0}
        </p>
      </div>
      <ha-md-list>
        ${0}
      </ha-md-list>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.change_wake_word.title"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.change_wake_word.secondary"),this.assistConfiguration.available_wake_words.map((t=>(0,u.qy)(y||(y=w`<ha-md-list-item
              interactive
              type="button"
              @click=${0}
              .value=${0}
            >
              ${0}
              <ha-icon-next slot="end"></ha-icon-next>
            </ha-md-list-item>`),this._wakeWordPicked,t.id,t.wake_word))))}},{key:"_wakeWordPicked",value:(i=(0,s.A)((0,a.A)().m((function t(e){var i;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:if(this.assistEntityId){t.n=1;break}return t.a(2);case 1:return i=e.currentTarget.value,t.n=2,(0,p.g5)(this.hass,this.assistEntityId,[i]);case 2:this._nextStep();case 3:return t.a(2)}}),t,this)}))),function(t){return i.apply(this,arguments)})},{key:"_nextStep",value:function(){(0,h.r)(this,"next-step",{step:_.STEP.WAKEWORD,updateConfig:!0})}}]);var i}(u.WF);b.styles=[v.s,(0,u.AH)(m||(m=w`
      :host {
        padding: 0;
      }
      .padding {
        padding: 24px;
      }
      ha-md-list {
        width: 100%;
        text-align: initial;
        margin-bottom: 24px;
      }
    `))],(0,c.__decorate)([(0,d.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,c.__decorate)([(0,d.MZ)({attribute:!1})],b.prototype,"assistConfiguration",void 0),(0,c.__decorate)([(0,d.MZ)({attribute:!1})],b.prototype,"assistEntityId",void 0),b=(0,c.__decorate)([(0,d.EM)("ha-voice-assistant-setup-step-change-wake-word")],b),e()}catch(k){e(k)}}))},8439:function(t,e,i){i.a(t,(async function(t,e){try{var a=i(61397),s=i(50264),n=i(44734),o=i(56038),r=i(69683),l=i(6454),c=i(25460),u=(i(28706),i(62826)),d=i(96196),h=i(77845),p=i(92542),v=i(89473),_=i(89600),g=i(41558),f=i(51120),y=i(62001),m=t([v,_]);[v,_]=m.then?(await m)():m;var w,b,k,A,$=t=>t,x=function(t){function e(){var t;(0,n.A)(this,e);for(var i=arguments.length,a=new Array(i),s=0;s<i;s++)a[s]=arguments[s];return(t=(0,r.A)(this,e,[].concat(a)))._showLoader=!1,t}return(0,l.A)(e,t),(0,o.A)(e,[{key:"willUpdate",value:function(t){var i;(0,c.A)(e,"willUpdate",this,3)([t]),this.hasUpdated?"success"===this._status&&t.has("hass")&&"idle"===(null===(i=this.hass.states[this.assistEntityId])||void 0===i?void 0:i.state)&&this._nextStep():this._testConnection()}},{key:"render",value:function(){return(0,d.qy)(w||(w=$`<div class="content">
      ${0}
    </div>`),"timeout"===this._status?(0,d.qy)(b||(b=$`<img
              src="/static/images/voice-assistant/error.png"
              alt="Casita Home Assistant error logo"
            />
            <h1>
              ${0}
            </h1>
            <p class="secondary">
              ${0}
            </p>
            <div class="footer">
              <ha-button
                appearance="plain"
                href=${0}
              >
                >${0}</ha-button
              >
              <ha-button @click=${0}
                >${0}</ha-button
              >
            </div>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.check.failed_title"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.check.failed_secondary"),(0,y.o)(this.hass,"/voice_control/troubleshooting/#i-dont-get-a-voice-response"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.check.help"),this._testConnection,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.check.retry")):(0,d.qy)(k||(k=$`<img
              src="/static/images/voice-assistant/hi.png"
              alt="Casita Home Assistant hi logo"
            />
            <h1>
              ${0}
            </h1>
            <p class="secondary">
              ${0}
            </p>

            ${0}`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.check.title"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.check.secondary"),this._showLoader?(0,d.qy)(A||(A=$`<ha-spinner></ha-spinner>`)):d.s6))}},{key:"_testConnection",value:(i=(0,s.A)((0,a.A)().m((function t(){var e,i;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:return this._status=void 0,this._showLoader=!1,e=setTimeout((()=>{this._showLoader=!0}),3e3),t.n=1,(0,g.tl)(this.hass,this.assistEntityId);case 1:i=t.v,clearTimeout(e),this._showLoader=!1,this._status=i.status;case 2:return t.a(2)}}),t,this)}))),function(){return i.apply(this,arguments)})},{key:"_nextStep",value:function(){(0,p.r)(this,"next-step",{noPrevious:!0})}}]);var i}(d.WF);x.styles=f.s,(0,u.__decorate)([(0,h.MZ)({attribute:!1})],x.prototype,"hass",void 0),(0,u.__decorate)([(0,h.MZ)({attribute:!1})],x.prototype,"assistEntityId",void 0),(0,u.__decorate)([(0,h.wk)()],x.prototype,"_status",void 0),(0,u.__decorate)([(0,h.wk)()],x.prototype,"_showLoader",void 0),x=(0,u.__decorate)([(0,h.EM)("ha-voice-assistant-setup-step-check")],x),e()}catch(z){e(z)}}))},24946:function(t,e,i){i.a(t,(async function(t,e){try{var a=i(44734),s=i(56038),n=i(69683),o=i(6454),r=(i(28706),i(62826)),l=i(96196),c=i(77845),u=i(41745),d=i(50577),h=i(35215),p=i(92542),v=i(54728),_=t([u,d,h,v]);[u,d,h,v]=_.then?(await _)():_;var g,f,y,m=t=>t,w=function(t){function e(){var t;(0,a.A)(this,e);for(var i=arguments.length,s=new Array(i),o=0;o<i;o++)s[o]=arguments[o];return(t=(0,n.A)(this,e,[].concat(s)))._state="INTRO",t}return(0,o.A)(e,t),(0,s.A)(e,[{key:"render",value:function(){return"SIGNUP"===this._state?(0,l.qy)(g||(g=m`<cloud-step-signup
        .hass=${0}
        @cloud-step=${0}
      ></cloud-step-signup>`),this.hass,this._cloudStep):"SIGNIN"===this._state?(0,l.qy)(f||(f=m`<cloud-step-signin
        .hass=${0}
        @cloud-step=${0}
      ></cloud-step-signin>`),this.hass,this._cloudStep):(0,l.qy)(y||(y=m`<cloud-step-intro
      .hass=${0}
      @cloud-step=${0}
    ></cloud-step-intro>`),this.hass,this._cloudStep)}},{key:"_cloudStep",value:function(t){"DONE"!==t.detail.step?this._state=t.detail.step:(0,p.r)(this,"next-step",{step:v.STEP.PIPELINE,noPrevious:!0})}}])}(l.WF);(0,r.__decorate)([(0,c.MZ)({attribute:!1})],w.prototype,"hass",void 0),(0,r.__decorate)([(0,c.wk)()],w.prototype,"_state",void 0),w=(0,r.__decorate)([(0,c.EM)("ha-voice-assistant-setup-step-cloud")],w),e()}catch(b){e(b)}}))},52124:function(t,e,i){i.a(t,(async function(t,e){try{var a=i(61397),s=i(50264),n=i(44734),o=i(56038),r=i(69683),l=i(6454),c=i(25460),u=(i(16280),i(28706),i(2008),i(50113),i(74423),i(23792),i(62062),i(26910),i(18111),i(22489),i(20116),i(61701),i(13579),i(26099),i(16034),i(3362),i(62953),i(62826)),d=i(96196),h=i(77845),p=i(92209),v=i(92542),_=i(41144),g=i(89600),f=i(45369),y=i(23608),m=i(22800),w=i(34402),b=i(61970),k=i(62146),A=i(40979),$=i(62001),x=i(51120),z=i(54728),C=i(98320),E=t([g,z]);[g,z]=E.then?(await E)():E;var M,S,I,O,P,L=t=>t,q="M14,3V5H17.59L7.76,14.83L9.17,16.24L19,6.41V10H21V3M19,19H5V5H12V3H5C3.89,3 3,3.9 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V12H19V19Z",T=function(t){function e(){var t;(0,n.A)(this,e);for(var i=arguments.length,a=new Array(i),s=0;s<i;s++)a[s]=arguments[s];return(t=(0,r.A)(this,e,[].concat(a)))._state="INTRO",t._ttsProviderName="piper",t._ttsAddonName="core_piper",t._ttsHostName="core-piper",t._ttsPort=10200,t._sttPort=10300,t}return(0,l.A)(e,t),(0,o.A)(e,[{key:"render",value:function(){return(0,d.qy)(M||(M=L`<div class="content">
      ${0}
    </div>`),"INSTALLING"===this._state?(0,d.qy)(S||(S=L`<img
              src="/static/images/voice-assistant/update.png"
              alt="Casita Home Assistant loading logo"
            />
            <h1>
              ${0}
            </h1>
            <p>
              ${0}
            </p>
            <ha-spinner></ha-spinner>
            <p>
              ${0}
            </p>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.title"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.secondary"),this._detailState||"Installation can take several minutes"):"ERROR"===this._state?(0,d.qy)(I||(I=L`<img
                src="/static/images/voice-assistant/error.png"
                alt="Casita Home Assistant error logo"
              />
              <h1>
                ${0}
              </h1>
              <p>${0}</p>
              <p>
                ${0}
              </p>
              <ha-button
                appearance="plain"
                size="small"
                @click=${0}
                >${0}</ha-button
              >
              <ha-button
                href=${0}
                target="_blank"
                rel="noreferrer noopener"
                size="small"
                appearance="plain"
              >
                <ha-svg-icon .path=${0} slot="start"></ha-svg-icon>
                ${0}</ha-button
              >`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.failed_title"),this._error,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.failed_secondary"),this._prevStep,this.hass.localize("ui.common.back"),(0,$.o)(this.hass,"/voice_control/voice_remote_local_assistant/"),q,this.hass.localize("ui.panel.config.common.learn_more")):"NOT_SUPPORTED"===this._state?(0,d.qy)(O||(O=L`<img
                  src="/static/images/voice-assistant/error.png"
                  alt="Casita Home Assistant error logo"
                />
                <h1>
                  ${0}
                </h1>
                <p>
                  ${0}
                </p>
                <ha-button
                  appearance="plain"
                  size="small"
                  @click=${0}
                  >${0}</ha-button
                >
                <ha-button
                  href=${0}
                  target="_blank"
                  rel="noreferrer noopener"
                  appearance="plain"
                  size="small"
                >
                  <ha-svg-icon .path=${0} slot="start"></ha-svg-icon>
                  ${0}</ha-button
                >`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.not_supported_title"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.not_supported_secondary"),this._prevStep,this.hass.localize("ui.common.back"),(0,$.o)(this.hass,"/voice_control/voice_remote_local_assistant/"),q,this.hass.localize("ui.panel.config.common.learn_more")):d.s6)}},{key:"willUpdate",value:function(t){(0,c.A)(e,"willUpdate",this,3)([t]),this.hasUpdated||this._checkLocal()}},{key:"_prevStep",value:function(){(0,v.r)(this,"prev-step")}},{key:"_nextStep",value:function(){(0,v.r)(this,"next-step",{step:z.STEP.SUCCESS,noPrevious:!0})}},{key:"_checkLocal",value:(T=(0,s.A)((0,a.A)().m((function t(){var e,i,s,n,o;return(0,a.A)().w((function(t){for(;;)switch(t.p=t.n){case 0:return t.n=1,this._findLocalEntities();case 1:if(this._localTts&&this._localStt){t.n=2;break}return t.a(2);case 2:if(t.p=2,!this._localTts.length||!this._localStt.length){t.n=4;break}return t.n=3,this._pickOrCreatePipelineExists();case 3:return t.a(2);case 4:if((0,p.x)(this.hass,"hassio")){t.n=5;break}return this._state="NOT_SUPPORTED",t.a(2);case 5:return this._state="INSTALLING",t.n=6,(0,w.b3)(this.hass);case 6:if(e=t.v,i=e.addons,s=i.find((t=>t.slug===this._ttsAddonName)),n=i.find((t=>t.slug===this._sttAddonName)),this._localTts.length){t.n=9;break}if(s){t.n=7;break}return this._detailState=this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.local.state.installing_${this._ttsProviderName}`),t.n=7,(0,w.xG)(this.hass,this._ttsAddonName);case 7:if(s&&"started"===s.state){t.n=8;break}return this._detailState=this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.local.state.starting_${this._ttsProviderName}`),t.n=8,(0,w.eK)(this.hass,this._ttsAddonName);case 8:return this._detailState=this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.local.state.setup_${this._ttsProviderName}`),t.n=9,this._setupConfigEntry("tts");case 9:if(this._localStt.length){t.n=12;break}if(n){t.n=10;break}return this._detailState=this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.local.state.installing_${this._sttProviderName}`),t.n=10,(0,w.xG)(this.hass,this._sttAddonName);case 10:if(n&&"started"===n.state){t.n=11;break}return this._detailState=this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.local.state.starting_${this._sttProviderName}`),t.n=11,(0,w.eK)(this.hass,this._sttAddonName);case 11:return this._detailState=this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.local.state.setup_${this._sttProviderName}`),t.n=12,this._setupConfigEntry("stt");case 12:return this._detailState=this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.state.creating_pipeline"),t.n=13,this._findEntitiesAndCreatePipeline();case 13:t.n=15;break;case 14:t.p=14,o=t.v,this._state="ERROR",this._error=o.message;case 15:return t.a(2)}}),t,this,[[2,14]])}))),function(){return T.apply(this,arguments)})},{key:"_sttProviderName",get:function(){return"focused_local"===this.localOption?"speech-to-phrase":"faster-whisper"}},{key:"_sttAddonName",get:function(){return"focused_local"===this.localOption?"core_speech-to-phrase":"core_whisper"}},{key:"_sttHostName",get:function(){return"focused_local"===this.localOption?"core-speech-to-phrase":"core-whisper"}},{key:"_findLocalEntities",value:(P=(0,s.A)((0,a.A)().m((function t(){var e,i,s,n;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:if((e=Object.values(this.hass.entities).filter((t=>"wyoming"===t.platform))).length){t.n=1;break}return this._localStt=[],this._localTts=[],t.a(2);case 1:return t.n=2,(0,A.d)(this.hass);case 2:return i=t.v,n=Object,t.n=3,(0,m.G3)(this.hass,e.map((t=>t.entity_id)));case 3:s=n.values.call(n,t.v),this._localTts=s.filter((t=>{var e;return"tts"===(0,_.m)(t.entity_id)&&t.config_entry_id&&(null===(e=i.info[t.config_entry_id])||void 0===e?void 0:e.tts.some((t=>t.name===this._ttsProviderName)))})),this._localStt=s.filter((t=>{var e;return"stt"===(0,_.m)(t.entity_id)&&t.config_entry_id&&(null===(e=i.info[t.config_entry_id])||void 0===e?void 0:e.asr.some((t=>t.name===this._sttProviderName)))}));case 4:return t.a(2)}}),t,this)}))),function(){return P.apply(this,arguments)})},{key:"_setupConfigEntry",value:(E=(0,s.A)((0,a.A)().m((function t(e){var i;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:return t.n=1,this._findConfigFlowInProgress(e);case 1:if(!(i=t.v)){t.n=3;break}return t.n=2,(0,y.jm)(this.hass,i.flow_id,{});case 2:if("create_entry"!==t.v.type){t.n=3;break}return t.a(2,void 0);case 3:return t.a(2,this._createConfigEntry(e))}}),t,this)}))),function(t){return E.apply(this,arguments)})},{key:"_findConfigFlowInProgress",value:(x=(0,s.A)((0,a.A)().m((function t(e){var i;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:return t.n=1,(0,y.t2)(this.hass.connection);case 1:return i=t.v,t.a(2,i.find((t=>"wyoming"===t.handler&&"hassio"===t.context.source&&(t.context.configuration_url&&t.context.configuration_url.includes("tts"===e?this._ttsAddonName:this._sttAddonName)||t.context.title_placeholders.name&&t.context.title_placeholders.name.toLowerCase().includes("tts"===e?this._ttsProviderName:this._sttProviderName)))))}}),t,this)}))),function(t){return x.apply(this,arguments)})},{key:"_createConfigEntry",value:(g=(0,s.A)((0,a.A)().m((function t(e){var i,s;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:return t.n=1,(0,y.t1)(this.hass,"wyoming");case 1:return i=t.v,t.n=2,(0,y.jm)(this.hass,i.flow_id,{host:"tts"===e?this._ttsHostName:this._sttHostName,port:"tts"===e?this._ttsPort:this._sttPort});case 2:if("create_entry"===(s=t.v).type){t.n=3;break}throw new Error(`${this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.errors.failed_create_entry",{addon:"tts"===e?this._ttsProviderName:this._sttProviderName})}${"errors"in s?`: ${s.errors.base}`:""}`);case 3:return t.a(2)}}),t,this)}))),function(t){return g.apply(this,arguments)})},{key:"_pickOrCreatePipelineExists",value:(h=(0,s.A)((0,a.A)().m((function t(){var e,i,s,n,o,r,l;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:if(null!==(e=this._localStt)&&void 0!==e&&e.length&&null!==(i=this._localTts)&&void 0!==i&&i.length){t.n=1;break}return t.a(2);case 1:return t.n=2,(0,f.nx)(this.hass);case 2:if((n=t.v).preferred_pipeline&&n.pipelines.sort((t=>t.id===n.preferred_pipeline?-1:0)),o=this._localTts.map((t=>t.entity_id)),r=this._localStt.map((t=>t.entity_id)),l=n.pipelines.find((t=>"conversation.home_assistant"===t.conversation_engine&&t.tts_engine&&o.includes(t.tts_engine)&&t.stt_engine&&r.includes(t.stt_engine)&&t.language.split("-")[0]===this.language.split("-")[0]))){t.n=4;break}return t.n=3,this._createPipeline(this._localTts[0].entity_id,this._localStt[0].entity_id);case 3:l=t.v;case 4:return t.n=5,this.hass.callService("select","select_option",{option:l.name},{entity_id:null===(s=this.assistConfiguration)||void 0===s?void 0:s.pipeline_entity_id});case 5:this._nextStep();case 6:return t.a(2)}}),t,this)}))),function(){return h.apply(this,arguments)})},{key:"_createPipeline",value:(u=(0,s.A)((0,a.A)().m((function t(e,i){var s,n,o,r,l,c,u,d,h,p;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:return t.n=1,(0,f.nx)(this.hass);case 1:return r=t.v,t.n=2,(0,C.vc)(this.hass,this.language||this.hass.config.language,this.hass.config.country||void 0);case 2:if(null!=(l=t.v.agents.find((t=>"conversation.home_assistant"===t.id)))&&l.supported_languages.length){t.n=3;break}throw new Error("Conversation agent does not support requested language.");case 3:return t.n=4,(0,k.Xv)(this.hass,this.language,this.hass.config.country||void 0);case 4:if(null!=(c=t.v.providers.find((t=>t.engine_id===e)))&&null!==(s=c.supported_languages)&&void 0!==s&&s.length){t.n=5;break}throw new Error("TTS engine does not support requested language.");case 5:return t.n=6,(0,k.z3)(this.hass,e,c.supported_languages[0]);case 6:if(u=t.v,null!==(n=u.voices)&&void 0!==n&&n.length){t.n=7;break}throw new Error("No voice available for requested language.");case 7:return t.n=8,(0,b.T)(this.hass,this.language,this.hass.config.country||void 0);case 8:if(null!=(d=t.v.providers.find((t=>t.engine_id===i)))&&null!==(o=d.supported_languages)&&void 0!==o&&o.length){t.n=9;break}throw new Error("STT engine does not support requested language.");case 9:for(h=this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.local.${this.localOption}_pipeline`),p=1;r.pipelines.find((t=>t.name===h));)h=`${this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.local.${this.localOption}_pipeline`)} ${p}`,p++;return t.a(2,(0,f.u6)(this.hass,{name:h,language:this.language.split("-")[0],conversation_engine:"conversation.home_assistant",conversation_language:l.supported_languages[0],stt_engine:i,stt_language:d.supported_languages[0],tts_engine:e,tts_language:c.supported_languages[0],tts_voice:u.voices[0].voice_id,wake_word_entity:null,wake_word_id:null}))}}),t,this)}))),function(t,e){return u.apply(this,arguments)})},{key:"_findEntitiesAndCreatePipeline",value:(i=(0,s.A)((0,a.A)().m((function t(){var e,i,s,n,o,r=arguments;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:return n=r.length>0&&void 0!==r[0]?r[0]:0,t.n=1,this._findLocalEntities();case 1:if(null!==(e=this._localTts)&&void 0!==e&&e.length&&null!==(i=this._localStt)&&void 0!==i&&i.length){t.n=4;break}if(!(n>3)){t.n=2;break}throw new Error(this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.local.errors.could_not_find_entities"));case 2:return t.n=3,new Promise((t=>{setTimeout(t,2e3)}));case 3:return t.a(2,this._findEntitiesAndCreatePipeline(n+1));case 4:return t.n=5,this._createPipeline(this._localTts[0].entity_id,this._localStt[0].entity_id);case 5:return o=t.v,t.n=6,this.hass.callService("select","select_option",{option:o.name},{entity_id:null===(s=this.assistConfiguration)||void 0===s?void 0:s.pipeline_entity_id});case 6:return this._nextStep(),t.a(2,void 0)}}),t,this)}))),function(){return i.apply(this,arguments)})}]);var i,u,h,g,x,E,P,T}(d.WF);T.styles=[x.s,(0,d.AH)(P||(P=L`
      ha-spinner {
        margin-top: 24px;
        margin-bottom: 24px;
      }
    `))],(0,u.__decorate)([(0,h.MZ)({attribute:!1})],T.prototype,"hass",void 0),(0,u.__decorate)([(0,h.MZ)({attribute:!1})],T.prototype,"assistConfiguration",void 0),(0,u.__decorate)([(0,h.MZ)({attribute:!1})],T.prototype,"localOption",void 0),(0,u.__decorate)([(0,h.MZ)({attribute:!1})],T.prototype,"language",void 0),(0,u.__decorate)([(0,h.wk)()],T.prototype,"_state",void 0),(0,u.__decorate)([(0,h.wk)()],T.prototype,"_detailState",void 0),(0,u.__decorate)([(0,h.wk)()],T.prototype,"_error",void 0),(0,u.__decorate)([(0,h.wk)()],T.prototype,"_localTts",void 0),(0,u.__decorate)([(0,h.wk)()],T.prototype,"_localStt",void 0),T=(0,u.__decorate)([(0,h.EM)("ha-voice-assistant-setup-step-local")],T),e()}catch(H){e(H)}}))},67993:function(t,e,i){i.a(t,(async function(t,e){try{var a=i(61397),s=i(50264),n=i(44734),o=i(56038),r=i(69683),l=i(6454),c=i(25460),u=(i(28706),i(50113),i(44114),i(26910),i(18111),i(20116),i(26099),i(16034),i(62826)),d=i(96196),h=i(77845),p=i(22786),v=i(92209),_=i(92542),g=i(41144),f=i(31747),y=(i(47813),i(45369)),m=i(71750),w=i(98320),b=i(61970),k=i(62146),A=i(51120),$=i(54728),x=i(62001),z=t([f,$]);[f,$]=z.then?(await z)():z;var C,E,M,S,I=t=>t,O=["cloud","focused_local","full_local"],P={cloud:0,focused_local:0,full_local:0},L=function(t){function e(){var t;(0,n.A)(this,e);for(var i=arguments.length,a=new Array(i),s=0;s<i;s++)a[s]=arguments[s];return(t=(0,r.A)(this,e,[].concat(a))).languages=[],t._cloudChecked=!1,t._getOptions=(0,p.A)(((t,e)=>{var i=[],a=[];return O.forEach((s=>{t[s]>0?i.push({label:e(`ui.panel.config.voice_assistants.satellite_wizard.pipeline.options.${s}.label`),description:e(`ui.panel.config.voice_assistants.satellite_wizard.pipeline.options.${s}.description`),value:s}):a.push({label:e(`ui.panel.config.voice_assistants.satellite_wizard.pipeline.options.${s}.label`),value:s})})),{supportedOptions:i,unsupportedOptions:a}})),t}return(0,l.A)(e,t),(0,o.A)(e,[{key:"willUpdate",value:function(t){if((0,c.A)(e,"willUpdate",this,3)([t]),this.hasUpdated||this._fetchData(),(t.has("language")||t.has("_languageScores"))&&this.language&&this._languageScores){var i,a,s=this.language;if(this._value&&0===(null===(i=this._languageScores[s])||void 0===i?void 0:i[this._value])&&(this._value=void 0),!this._value)this._value=null===(a=this._getOptions(this._languageScores[s]||P,this.hass.localize).supportedOptions[0])||void 0===a?void 0:a.value}}},{key:"render",value:function(){if(!this._cloudChecked||!this._languageScores)return d.s6;if(!this.language){var t=(0,f.T)(this.hass.config.language,this.hass.locale);return(0,d.qy)(C||(C=I`<div class="content">
        <h1>
          ${0}
        </h1>
        ${0}
        <ha-language-picker
          .hass=${0}
          .label=${0}
          .languages=${0}
          @value-changed=${0}
        ></ha-language-picker>

        <a
          href=${0}
          >${0}</a
        >
      </div>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.pipeline.unsupported_language.header"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.pipeline.unsupported_language.secondary",{language:t}),this.hass,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.pipeline.unsupported_language.language_picker"),this.languages,this._languageChanged,(0,x.o)(this.hass,"/voice_control/contribute-voice/"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.pipeline.unsupported_language.contribute",{language:t}))}var e=this._languageScores[this.language]||P,i=this._getOptions(e,this.hass.localize),a=this._value?"full_local"===this._value?"low":"high":"",s=this._value?e[this._value]>2?"high":e[this._value]>1?"ready":e[this._value]>0?"low":"":"";return(0,d.qy)(E||(E=I`<div class="content">
        <h1>
          ${0}
        </h1>
        <div class="bar-header">
          <span
            >${0}</span
          ><span
            >${0}</span
          >
        </div>
        <div class="perf-bar ${0}">
          <div class="segment"></div>
          <div class="segment"></div>
          <div class="segment"></div>
        </div>
        <div class="bar-header">
          <span
            >${0}</span
          ><span
            >${0}</span
          >
        </div>
        <div class="perf-bar ${0}">
          <div class="segment"></div>
          <div class="segment"></div>
          <div class="segment"></div>
        </div>
        <ha-select-box
          max_columns="1"
          .options=${0}
          .value=${0}
          @value-changed=${0}
        ></ha-select-box>
        ${0}
      </div>
      <div class="footer">
        <ha-button @click=${0} .disabled=${0}
          >${0}</ha-button
        >
      </div>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.pipeline.title"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.pipeline.performance.header"),a?this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.pipeline.performance.${a}`):"",a,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.pipeline.commands.header"),s?this.hass.localize(`ui.panel.config.voice_assistants.satellite_wizard.pipeline.commands.${s}`):"",s,i.supportedOptions,this._value,this._valueChanged,i.unsupportedOptions.length?(0,d.qy)(M||(M=I`<h3>
                ${0}
              </h3>
              <ha-select-box
                max_columns="1"
                .options=${0}
                disabled
              ></ha-select-box>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.pipeline.unsupported"),i.unsupportedOptions):d.s6,this._createPipeline,!this._value,this.hass.localize("ui.common.next"))}},{key:"_fetchData",value:(A=(0,s.A)((0,a.A)().m((function t(){var e;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:return t.n=1,this._hasCloud();case 1:if(!(e=t.v)){t.n=3;break}return t.n=2,this._createCloudPipeline(!1);case 2:e=t.v;case 3:if(e){t.n=5;break}return this._cloudChecked=!0,t.n=4,(0,w.e1)(this.hass);case 4:this._languageScores=t.v.languages;case 5:return t.a(2)}}),t,this)}))),function(){return A.apply(this,arguments)})},{key:"_hasCloud",value:(h=(0,s.A)((0,a.A)().m((function t(){var e;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:if((0,v.x)(this.hass,"cloud")){t.n=1;break}return t.a(2,!1);case 1:return t.n=2,(0,m.eN)(this.hass);case 2:if((e=t.v).logged_in&&e.active_subscription){t.n=3;break}return t.a(2,!1);case 3:return t.a(2,!0)}}),t,this)}))),function(){return h.apply(this,arguments)})},{key:"_createCloudPipeline",value:(u=(0,s.A)((0,a.A)().m((function t(e){var i,s,n,o,r,l,c,u,d,h,p,v,f,m,A,x,z;return(0,a.A)().w((function(t){for(;;)switch(t.p=t.n){case 0:n=0,o=Object.values(this.hass.entities);case 1:if(!(n<o.length)){t.n=6;break}if("cloud"!==(r=o[n]).platform){t.n=5;break}if("tts"!==(l=(0,g.m)(r.entity_id))){t.n=2;break}i=r.entity_id,t.n=4;break;case 2:if("stt"!==l){t.n=3;break}s=r.entity_id,t.n=4;break;case 3:return t.a(3,5);case 4:if(!i||!s){t.n=5;break}return t.a(3,6);case 5:n++,t.n=1;break;case 6:return t.p=6,t.n=7,(0,y.nx)(this.hass);case 7:if((u=t.v).preferred_pipeline&&u.pipelines.sort((t=>t.id===u.preferred_pipeline?-1:0)),d=u.pipelines.find((t=>"conversation.home_assistant"===t.conversation_engine&&t.tts_engine===i&&t.stt_engine===s&&(!e||t.language.split("-")[0]===this.language.split("-")[0])))){t.n=16;break}return t.n=8,(0,w.vc)(this.hass,this.language||this.hass.config.language,this.hass.config.country||void 0);case 8:if(null!=(v=t.v.agents.find((t=>"conversation.home_assistant"===t.id)))&&v.supported_languages.length){t.n=9;break}return t.a(2,!1);case 9:return t.n=10,(0,k.Xv)(this.hass,this.language||this.hass.config.language,this.hass.config.country||void 0);case 10:if(null!=(f=t.v.providers.find((t=>t.engine_id===i)))&&null!==(h=f.supported_languages)&&void 0!==h&&h.length){t.n=11;break}return t.a(2,!1);case 11:return t.n=12,(0,k.z3)(this.hass,i,f.supported_languages[0]);case 12:return m=t.v,t.n=13,(0,b.T)(this.hass,this.language||this.hass.config.language,this.hass.config.country||void 0);case 13:if(null!=(A=t.v.providers.find((t=>t.engine_id===s)))&&null!==(p=A.supported_languages)&&void 0!==p&&p.length){t.n=14;break}return t.a(2,!1);case 14:for(x="Home Assistant Cloud",z=1;u.pipelines.find((t=>t.name===x));)x=`Home Assistant Cloud ${z}`,z++;return t.n=15,(0,y.u6)(this.hass,{name:x,language:(this.language||this.hass.config.language).split("-")[0],conversation_engine:"conversation.home_assistant",conversation_language:v.supported_languages[0],stt_engine:s,stt_language:A.supported_languages[0],tts_engine:i,tts_language:f.supported_languages[0],tts_voice:m.voices[0].voice_id,wake_word_entity:null,wake_word_id:null});case 15:d=t.v;case 16:return t.n=17,this.hass.callService("select","select_option",{option:d.name},{entity_id:null===(c=this.assistConfiguration)||void 0===c?void 0:c.pipeline_entity_id});case 17:return(0,_.r)(this,"next-step",{step:$.STEP.SUCCESS,noPrevious:!0}),t.a(2,!0);case 18:return t.p=18,t.v,t.a(2,!1)}}),t,this,[[6,18]])}))),function(t){return u.apply(this,arguments)})},{key:"_valueChanged",value:function(t){this._value=t.detail.value}},{key:"_setupCloud",value:(i=(0,s.A)((0,a.A)().m((function t(){return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:return t.n=1,this._hasCloud();case 1:if(!t.v){t.n=2;break}return this._createCloudPipeline(!0),t.a(2);case 2:(0,_.r)(this,"next-step",{step:$.STEP.CLOUD});case 3:return t.a(2)}}),t,this)}))),function(){return i.apply(this,arguments)})},{key:"_createPipeline",value:function(){"cloud"===this._value?this._setupCloud():"focused_local"===this._value?this._setupLocalFocused():this._setupLocalFull()}},{key:"_setupLocalFocused",value:function(){(0,_.r)(this,"next-step",{step:$.STEP.LOCAL,option:this._value})}},{key:"_setupLocalFull",value:function(){(0,_.r)(this,"next-step",{step:$.STEP.LOCAL,option:this._value})}},{key:"_languageChanged",value:function(t){t.detail.value&&(0,_.r)(this,"language-changed",{value:t.detail.value})}}]);var i,u,h,A}(d.WF);L.styles=[A.s,(0,d.AH)(S||(S=I`
      :host {
        text-align: left;
      }
      .perf-bar {
        width: 100%;
        height: 10px;
        display: flex;
        gap: var(--ha-space-1);
        margin: 8px 0;
      }
      .segment {
        flex-grow: 1;
        background-color: var(--disabled-color);
        transition: background-color 0.3s;
      }
      .segment:first-child {
        border-radius: var(--ha-border-radius-sm) var(--ha-border-radius-square)
          var(--ha-border-radius-square) var(--ha-border-radius-sm);
      }
      .segment:last-child {
        border-radius: var(--ha-border-radius-square) var(--ha-border-radius-sm)
          var(--ha-border-radius-sm) var(--ha-border-radius-square);
      }
      .perf-bar.high .segment {
        background-color: var(--success-color);
      }
      .perf-bar.ready .segment:nth-child(-n + 2) {
        background-color: var(--warning-color);
      }
      .perf-bar.low .segment:nth-child(1) {
        background-color: var(--error-color);
      }
      .bar-header {
        display: flex;
        justify-content: space-between;
        margin: 8px 0;
        margin-top: 16px;
      }
      ha-select-box {
        display: block;
      }
      ha-select-box:first-of-type {
        margin-top: 32px;
      }
      .footer {
        margin-top: 16px;
      }
      ha-language-picker {
        display: block;
        margin-top: 16px;
        margin-bottom: 16px;
      }
    `))],(0,u.__decorate)([(0,h.MZ)({attribute:!1})],L.prototype,"hass",void 0),(0,u.__decorate)([(0,h.MZ)({attribute:!1})],L.prototype,"assistConfiguration",void 0),(0,u.__decorate)([(0,h.MZ)({attribute:!1})],L.prototype,"deviceId",void 0),(0,u.__decorate)([(0,h.MZ)({attribute:!1})],L.prototype,"assistEntityId",void 0),(0,u.__decorate)([(0,h.MZ)({attribute:!1})],L.prototype,"language",void 0),(0,u.__decorate)([(0,h.MZ)({attribute:!1})],L.prototype,"languages",void 0),(0,u.__decorate)([(0,h.wk)()],L.prototype,"_cloudChecked",void 0),(0,u.__decorate)([(0,h.wk)()],L.prototype,"_value",void 0),(0,u.__decorate)([(0,h.wk)()],L.prototype,"_languageScores",void 0),L=(0,u.__decorate)([(0,h.EM)("ha-voice-assistant-setup-step-pipeline")],L),e()}catch(q){e(q)}}))},93008:function(t,e,i){i.a(t,(async function(t,e){try{var a=i(78261),s=i(61397),n=i(50264),o=i(44734),r=i(56038),l=i(69683),c=i(25460),u=i(6454),d=(i(50113),i(74423),i(62062),i(18111),i(20116),i(61701),i(26099),i(62826)),h=i(96196),p=i(77845),v=i(92542),_=i(55124),g=i(16727),f=(i(56565),i(69869),i(10054),i(45369)),y=i(41558),m=i(71750),w=i(1491),b=i(84043),k=i(18511),A=i(82472),$=i(82888),x=i(51120),z=i(54728),C=t([A,z]);[A,z]=C.then?(await C)():C;var E,M,S,I,O,P,L,q,T=t=>t,H=function(t){function e(){return(0,o.A)(this,e),(0,l.A)(this,e,arguments)}return(0,u.A)(e,t),(0,r.A)(e,[{key:"willUpdate",value:function(t){if((0,c.A)(e,"willUpdate",this,3)([t]),t.has("assistConfiguration"))this._setTtsSettings();else if(t.has("hass")&&this.assistConfiguration){var i=t.get("hass");if(i){var a=i.states[this.assistConfiguration.pipeline_entity_id],s=this.hass.states[this.assistConfiguration.pipeline_entity_id];a.state!==s.state&&this._setTtsSettings()}}}},{key:"render",value:function(){var t,e=this.assistConfiguration?this.hass.states[this.assistConfiguration.pipeline_entity_id]:void 0,i=this.hass.devices[this.deviceId];return(0,h.qy)(E||(E=T`<div class="content">
        <img
          src="/static/images/voice-assistant/heart.png"
          alt="Casita Home Assistant logo"
        />
        <h1>
          ${0}
        </h1>
        <p class="secondary">
          ${0}
        </p>
        ${0}
        <div class="rows">
          <div class="row">
            <ha-textfield
              .label=${0}
              .placeholder=${0}
              .value=${0}
              @change=${0}
            ></ha-textfield>
          </div>
          ${0}
          ${0}
          ${0}
        </div>
      </div>
      <div class="footer">
        <ha-button @click=${0}
          >${0}</ha-button
        >
      </div>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.success.title"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.success.secondary"),this._error?(0,h.qy)(M||(M=T`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):h.s6,this.hass.localize("ui.panel.config.integrations.config_flow.device_name"),(0,g.T)(i,this.hass),null!==(t=this._deviceName)&&void 0!==t?t:(0,g.xn)(i),this._deviceNameChanged,this.assistConfiguration&&this.assistConfiguration.available_wake_words.length>1?(0,h.qy)(S||(S=T`<div class="row">
                <ha-select
                  .label=${0}
                  @closed=${0}
                  fixedMenuPosition
                  naturalMenuWidth
                  .value=${0}
                  @selected=${0}
                >
                  ${0}
                </ha-select>
                <ha-button
                  appearance="plain"
                  size="small"
                  @click=${0}
                >
                  <ha-svg-icon
                    slot="start"
                    .path=${0}
                  ></ha-svg-icon>
                  ${0}
                </ha-button>
              </div>`),this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.detail.form.wake_word_id"),_.d,this.assistConfiguration.active_wake_words[0],this._wakeWordPicked,this.assistConfiguration.available_wake_words.map((t=>(0,h.qy)(I||(I=T`<ha-list-item .value=${0}>
                        ${0}
                      </ha-list-item>`),t.id,t.wake_word))),this._testWakeWord,"M12,2A3,3 0 0,1 15,5V11A3,3 0 0,1 12,14A3,3 0 0,1 9,11V5A3,3 0 0,1 12,2M19,11C19,14.53 16.39,17.44 13,17.93V21H11V17.93C7.61,17.44 5,14.53 5,11H7A5,5 0 0,0 12,16A5,5 0 0,0 17,11H19Z",this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.success.test_wakeword")):h.s6,e?(0,h.qy)(O||(O=T`<div class="row">
                <ha-select
                  .label=${0}
                  @closed=${0}
                  .value=${0}
                  fixedMenuPosition
                  naturalMenuWidth
                  @selected=${0}
                >
                  ${0}
                </ha-select>
                <ha-button
                  appearance="plain"
                  size="small"
                  @click=${0}
                >
                  <ha-svg-icon slot="start" .path=${0}></ha-svg-icon>
                  ${0}
                </ha-button>
              </div>`),this.hass.localize("ui.panel.config.voice_assistants.assistants.pipeline.devices.pipeline"),_.d,null==e?void 0:e.state,this._pipelinePicked,null==e?void 0:e.attributes.options.map((t=>(0,h.qy)(P||(P=T`<ha-list-item .value=${0}>
                        ${0}
                      </ha-list-item>`),t,this.hass.formatEntityState(e,t)))),this._openPipeline,"M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.67 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z",this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.success.edit_pipeline")):h.s6,this._ttsSettings?(0,h.qy)(L||(L=T`<div class="row">
                <ha-tts-voice-picker
                  .hass=${0}
                  .engineId=${0}
                  .language=${0}
                  .value=${0}
                  @value-changed=${0}
                  @closed=${0}
                ></ha-tts-voice-picker>
                <ha-button
                  appearance="plain"
                  size="small"
                  @click=${0}
                >
                  <ha-svg-icon slot="start" .path=${0}></ha-svg-icon>
                  ${0}
                </ha-button>
              </div>`),this.hass,this._ttsSettings.engine,this._ttsSettings.language,this._ttsSettings.voice,this._voicePicked,_.d,this._testTts,"M8,5.14V19.14L19,12.14L8,5.14Z",this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.success.try_tts")):h.s6,this._done,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.success.done"))}},{key:"_getPipeline",value:(H=(0,n.A)((0,s.A)().m((function t(){var e,i,a,n,o;return(0,s.A)().w((function(t){for(;;)switch(t.n){case 0:if(null!==(e=this.assistConfiguration)&&void 0!==e&&e.pipeline_entity_id){t.n=1;break}return t.a(2,[void 0,void 0]);case 1:return a=this.hass.states[null===(i=this.assistConfiguration)||void 0===i?void 0:i.pipeline_entity_id].state,t.n=2,(0,f.nx)(this.hass);case 2:return n=t.v,o="preferred"===a?n.pipelines.find((t=>t.id===n.preferred_pipeline)):n.pipelines.find((t=>t.name===a)),t.a(2,[o,n.preferred_pipeline])}}),t,this)}))),function(){return H.apply(this,arguments)})},{key:"_deviceNameChanged",value:function(t){this._deviceName=t.target.value}},{key:"_wakeWordPicked",value:(q=(0,n.A)((0,s.A)().m((function t(e){var i;return(0,s.A)().w((function(t){for(;;)switch(t.n){case 0:return i=e.target.value,t.n=1,(0,y.g5)(this.hass,this.assistEntityId,[i]);case 1:return t.a(2)}}),t,this)}))),function(t){return q.apply(this,arguments)})},{key:"_pipelinePicked",value:function(t){var e=this.hass.states[this.assistConfiguration.pipeline_entity_id],i=t.target.value;i!==e.state&&e.attributes.options.includes(i)&&(0,b.w)(this.hass,e.entity_id,i)}},{key:"_setTtsSettings",value:(C=(0,n.A)((0,s.A)().m((function t(){var e,i,n;return(0,s.A)().w((function(t){for(;;)switch(t.n){case 0:return t.n=1,this._getPipeline();case 1:if(e=t.v,i=(0,a.A)(e,1),n=i[0]){t.n=2;break}return this._ttsSettings=void 0,t.a(2);case 2:this._ttsSettings={engine:n.tts_engine,voice:n.tts_voice,language:n.tts_language};case 3:return t.a(2)}}),t,this)}))),function(){return C.apply(this,arguments)})},{key:"_voicePicked",value:(x=(0,n.A)((0,s.A)().m((function t(e){var i,n,o;return(0,s.A)().w((function(t){for(;;)switch(t.n){case 0:return t.n=1,this._getPipeline();case 1:if(i=t.v,n=(0,a.A)(i,1),o=n[0]){t.n=2;break}return t.a(2);case 2:return t.n=3,(0,f.zn)(this.hass,o.id,Object.assign(Object.assign({},o),{},{tts_voice:e.detail.value}));case 3:return t.a(2)}}),t,this)}))),function(t){return x.apply(this,arguments)})},{key:"_testTts",value:(A=(0,n.A)((0,s.A)().m((function t(){var e,i,n,o;return(0,s.A)().w((function(t){for(;;)switch(t.p=t.n){case 0:return t.n=1,this._getPipeline();case 1:if(e=t.v,i=(0,a.A)(e,1),n=i[0]){t.n=2;break}return t.a(2);case 2:if(n.language===this.hass.locale.language){t.n=6;break}return t.p=3,t.n=4,(0,$.sC)(null,n.language,!1);case 4:return o=t.v,this._announce(o.data["ui.dialogs.tts-try.message_example"]),t.a(2);case 5:t.p=5,t.v;case 6:this._announce(this.hass.localize("ui.dialogs.tts-try.message_example"));case 7:return t.a(2)}}),t,this,[[3,5]])}))),function(){return A.apply(this,arguments)})},{key:"_announce",value:(p=(0,n.A)((0,s.A)().m((function t(e){return(0,s.A)().w((function(t){for(;;)switch(t.n){case 0:if(this.assistEntityId){t.n=1;break}return t.a(2);case 1:return t.n=2,(0,y.ew)(this.hass,this.assistEntityId,{message:e,preannounce:!1});case 2:return t.a(2)}}),t,this)}))),function(t){return p.apply(this,arguments)})},{key:"_testWakeWord",value:function(){(0,v.r)(this,"next-step",{step:z.STEP.WAKEWORD,nextStep:z.STEP.SUCCESS,updateConfig:!0})}},{key:"_openPipeline",value:(d=(0,n.A)((0,s.A)().m((function t(){var e,i,o,r,l=this;return(0,s.A)().w((function(t){for(;;)switch(t.n){case 0:return t.n=1,this._getPipeline();case 1:if(e=t.v,i=(0,a.A)(e,1),o=i[0]){t.n=2;break}return t.a(2);case 2:return t.n=3,(0,m.eN)(this.hass);case 3:r=t.v,(0,k.L)(this,{cloudActiveSubscription:r.logged_in&&r.active_subscription,pipeline:o,updatePipeline:function(){var t=(0,n.A)((0,s.A)().m((function t(e){return(0,s.A)().w((function(t){for(;;)switch(t.n){case 0:return t.n=1,(0,f.zn)(l.hass,o.id,e);case 1:return t.a(2)}}),t)})));return function(e){return t.apply(this,arguments)}}(),hideWakeWord:!0});case 4:return t.a(2)}}),t,this)}))),function(){return d.apply(this,arguments)})},{key:"_done",value:(i=(0,n.A)((0,s.A)().m((function t(){var e;return(0,s.A)().w((function(t){for(;;)switch(t.p=t.n){case 0:if(!this._deviceName){t.n=3;break}t.p=1,(0,w.FB)(this.hass,this.deviceId,{name_by_user:this._deviceName}),t.n=3;break;case 2:return t.p=2,e=t.v,this._error=this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.success.failed_rename",{error:e.message||e}),t.a(2);case 3:(0,v.r)(this,"closed");case 4:return t.a(2)}}),t,this,[[1,2]])}))),function(){return i.apply(this,arguments)})}]);var i,d,p,A,x,C,q,H}(h.WF);H.styles=[x.s,(0,h.AH)(q||(q=T`
      ha-md-list-item {
        text-align: initial;
      }
      ha-tts-voice-picker {
        display: block;
      }
      .footer {
        margin-top: 24px;
      }
      .rows {
        gap: var(--ha-space-4);
        display: flex;
        flex-direction: column;
      }
      .row {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .row > *:first-child {
        flex: 1;
        margin-right: 4px;
      }
      .row ha-button {
        width: 82px;
      }
    `))],(0,d.__decorate)([(0,p.MZ)({attribute:!1})],H.prototype,"hass",void 0),(0,d.__decorate)([(0,p.MZ)({attribute:!1})],H.prototype,"assistConfiguration",void 0),(0,d.__decorate)([(0,p.MZ)({attribute:!1})],H.prototype,"deviceId",void 0),(0,d.__decorate)([(0,p.MZ)({attribute:!1})],H.prototype,"assistEntityId",void 0),(0,d.__decorate)([(0,p.wk)()],H.prototype,"_ttsSettings",void 0),(0,d.__decorate)([(0,p.wk)()],H.prototype,"_error",void 0),H=(0,d.__decorate)([(0,p.EM)("ha-voice-assistant-setup-step-success")],H),e()}catch(Z){e(Z)}}))},33694:function(t,e,i){i.a(t,(async function(t,e){try{var a=i(61397),s=i(50264),n=i(44734),o=i(56038),r=i(69683),l=i(6454),c=i(25460),u=(i(28706),i(62826)),d=i(96196),h=i(77845),p=i(92542),v=i(64109),_=i(89600),g=i(31136),f=i(17498),y=i(51120),m=t([v,_,f]);[v,_,f]=m.then?(await m)():m;var w,b,k,A,$=t=>t,x=function(t){function e(){var t;(0,n.A)(this,e);for(var i=arguments.length,a=new Array(i),s=0;s<i;s++)a[s]=arguments[s];return(t=(0,r.A)(this,e,[].concat(a)))._updated=!1,t}return(0,l.A)(e,t),(0,o.A)(e,[{key:"willUpdate",value:function(t){if((0,c.A)(e,"willUpdate",this,3)([t]),this.updateEntityId){if(t.has("hass")&&this.updateEntityId){var i=t.get("hass");if(i){var a=i.states[this.updateEntityId],s=this.hass.states[this.updateEntityId];if((null==a?void 0:a.state)===g.Hh&&(null==s?void 0:s.state)!==g.Hh||(null==a?void 0:a.state)!==g.ON&&(null==s?void 0:s.state)===g.ON)return void this._tryUpdate(!1)}}t.has("updateEntityId")&&this._tryUpdate(!0)}else this._nextStep()}},{key:"render",value:function(){if(!this.updateEntityId||!(this.updateEntityId in this.hass.states))return d.s6;var t=this.hass.states[this.updateEntityId],e=t&&(0,f.RJ)(t);return(0,d.qy)(w||(w=$`<div class="content">
      <img
        src="/static/images/voice-assistant/update.png"
        alt="Casita Home Assistant loading logo"
      />
      <h1>
        ${0}
      </h1>
      <p class="secondary">
        ${0}
      </p>
      ${0}
      <p>
        ${0}
      </p>
    </div>`),t&&("unavailable"===t.state||(0,f.Jy)(t))?this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.update.title"):this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.update.checking"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.update.secondary"),e?(0,d.qy)(b||(b=$`
            <ha-progress-ring
              .value=${0}
            ></ha-progress-ring>
          `),t.attributes.update_percentage):(0,d.qy)(k||(k=$`<ha-spinner></ha-spinner>`)),(null==t?void 0:t.state)===g.Hh?"Restarting voice assistant":e?`Installing ${t.attributes.update_percentage}%`:"")}},{key:"_tryUpdate",value:(i=(0,s.A)((0,a.A)().m((function t(e){var i;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:if(clearTimeout(this._refreshTimeout),this.updateEntityId){t.n=1;break}return t.a(2);case 1:if(!(i=this.hass.states[this.updateEntityId])||this.hass.states[i.entity_id].state!==g.ON||!(0,f.VK)(i)){t.n=3;break}return this._updated=!0,t.n=2,this.hass.callService("update","install",{},{entity_id:i.entity_id});case 2:t.n=6;break;case 3:if(!e){t.n=5;break}return t.n=4,this.hass.callService("homeassistant","update_entity",{},{entity_id:this.updateEntityId});case 4:this._refreshTimeout=window.setTimeout((()=>{this._nextStep()}),1e4),t.n=6;break;case 5:this._nextStep();case 6:return t.a(2)}}),t,this)}))),function(t){return i.apply(this,arguments)})},{key:"_nextStep",value:function(){(0,p.r)(this,"next-step",{noPrevious:!0,updateConfig:this._updated})}}]);var i}(d.WF);x.styles=[y.s,(0,d.AH)(A||(A=$`
      ha-progress-ring,
      ha-spinner {
        margin-top: 24px;
        margin-bottom: 24px;
      }
    `))],(0,u.__decorate)([(0,h.MZ)({attribute:!1})],x.prototype,"hass",void 0),(0,u.__decorate)([(0,h.MZ)({attribute:!1})],x.prototype,"updateEntityId",void 0),x=(0,u.__decorate)([(0,h.EM)("ha-voice-assistant-setup-step-update")],x),e()}catch(z){e(z)}}))},6960:function(t,e,i){i.a(t,(async function(t,e){try{var a=i(61397),s=i(50264),n=i(44734),o=i(56038),r=i(69683),l=i(6454),c=i(25460),u=(i(28706),i(50113),i(74423),i(18111),i(20116),i(26099),i(62826)),d=i(96196),h=i(77845),p=i(22786),v=i(92542),_=i(89473),g=i(89600),f=(i(86451),i(41558)),y=i(51120),m=i(54728),w=i(41144),b=t([_,g,m]);[_,g,m]=b.then?(await b)():b;var k,A,$,x,z,C,E,M=t=>t,S=function(t){function e(){var t;(0,n.A)(this,e);for(var i=arguments.length,a=new Array(i),s=0;s<i;s++)a[s]=arguments[s];return(t=(0,r.A)(this,e,[].concat(a)))._detected=!1,t._timedout=!1,t._activeWakeWord=(0,p.A)((t=>{var e;if(!t)return"";var i=t.active_wake_words[0];return null===(e=t.available_wake_words.find((t=>t.id===i)))||void 0===e?void 0:e.wake_word})),t}return(0,l.A)(e,t),(0,o.A)(e,[{key:"disconnectedCallback",value:function(){(0,c.A)(e,"disconnectedCallback",this,3)([]),this._stopListeningWakeWord()}},{key:"willUpdate",value:function(t){var i;((0,c.A)(e,"willUpdate",this,3)([t]),t.has("assistConfiguration")&&this.assistConfiguration&&!this.assistConfiguration.available_wake_words.length&&this._nextStep(),t.has("assistEntityId"))&&(this._detected=!1,this._muteSwitchEntity=null===(i=this.deviceEntities)||void 0===i||null===(i=i.find((t=>"switch"===(0,w.m)(t.entity_id)&&t.entity_id.includes("mute"))))||void 0===i?void 0:i.entity_id,this._muteSwitchEntity||this._startTimeOut(),this._listenWakeWord())}},{key:"_startTimeOut",value:function(){this._timeout=window.setTimeout((()=>{this._timeout=void 0,this._timedout=!0}),15e3)}},{key:"render",value:function(){return this.assistEntityId?"idle"!==this.hass.states[this.assistEntityId].state?(0,d.qy)(k||(k=M`<ha-spinner></ha-spinner>`)):(0,d.qy)(A||(A=M`<div class="content">
        ${0}
        ${0}
      </div>
      ${0}`),this._detected?(0,d.qy)(x||(x=M`<img
                src="/static/images/voice-assistant/ok-nabu.png"
                alt="Casita Home Assistant logo"
              />
              <h1>
                ${0}
              </h1>
              <p class="secondary">
                ${0}
              </p>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.wake_word.title_2",{wakeword:this._activeWakeWord(this.assistConfiguration)}),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.wake_word.secondary_2")):(0,d.qy)($||($=M`
          <img src="/static/images/voice-assistant/sleep.png" alt="Casita Home Assistant logo"/>
          <h1>
          ${0}  
          </h1>
          <p class="secondary">${0}</p>
        </div>`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.wake_word.title",{wakeword:this._activeWakeWord(this.assistConfiguration)}),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.wake_word.secondary")),this._timedout?(0,d.qy)(z||(z=M`<ha-alert alert-type="warning"
              >${0}</ha-alert
            >`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.wake_word.time_out")):this._muteSwitchEntity&&"on"===this.hass.states[this._muteSwitchEntity].state?(0,d.qy)(C||(C=M`<ha-alert
                alert-type="warning"
                .title=${0}
                >${0}</ha-alert
              >`),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.wake_word.muted"),this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.wake_word.muted_description")):d.s6,this.assistConfiguration&&this.assistConfiguration.available_wake_words.length>1?(0,d.qy)(E||(E=M`<div class="footer centered">
            <ha-button
              appearance="plain"
              size="small"
              @click=${0}
              >${0}</ha-button
            >
          </div>`),this._changeWakeWord,this.hass.localize("ui.panel.config.voice_assistants.satellite_wizard.wake_word.change_wake_word")):d.s6):d.s6}},{key:"_listenWakeWord",value:(u=(0,s.A)((0,a.A)().m((function t(){var e;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:if(e=this.assistEntityId){t.n=1;break}return t.a(2);case 1:return t.n=2,this._stopListeningWakeWord();case 2:this._sub=(0,f.ds)(this.hass,e,(()=>{this._timedout=!1,clearTimeout(this._timeout),this._stopListeningWakeWord(),this._detected?this._nextStep():(this._detected=!0,this._listenWakeWord())}));case 3:return t.a(2)}}),t,this)}))),function(){return u.apply(this,arguments)})},{key:"_stopListeningWakeWord",value:(i=(0,s.A)((0,a.A)().m((function t(){var e,i,s;return(0,a.A)().w((function(t){for(;;)switch(t.p=t.n){case 0:return t.p=0,t.n=1,this._sub;case 1:if(s=e=t.v,i=null===s){t.n=2;break}i=void 0===e;case 2:if(i){t.n=3;break}e();case 3:t.n=5;break;case 4:t.p=4,t.v;case 5:this._sub=void 0;case 6:return t.a(2)}}),t,this,[[0,4]])}))),function(){return i.apply(this,arguments)})},{key:"_nextStep",value:function(){(0,v.r)(this,"next-step")}},{key:"_changeWakeWord",value:function(){(0,v.r)(this,"next-step",{step:m.STEP.CHANGE_WAKEWORD})}}]);var i,u}(d.WF);S.styles=y.s,(0,u.__decorate)([(0,h.MZ)({attribute:!1})],S.prototype,"hass",void 0),(0,u.__decorate)([(0,h.MZ)({attribute:!1})],S.prototype,"assistConfiguration",void 0),(0,u.__decorate)([(0,h.MZ)({attribute:!1})],S.prototype,"assistEntityId",void 0),(0,u.__decorate)([(0,h.MZ)({attribute:!1})],S.prototype,"deviceEntities",void 0),(0,u.__decorate)([(0,h.wk)()],S.prototype,"_muteSwitchEntity",void 0),(0,u.__decorate)([(0,h.wk)()],S.prototype,"_detected",void 0),(0,u.__decorate)([(0,h.wk)()],S.prototype,"_timedout",void 0),S=(0,u.__decorate)([(0,h.EM)("ha-voice-assistant-setup-step-wake-word")],S),e()}catch(I){e(I)}}))},86466:function(t,e,i){i.d(e,{o:function(){return s}});i(23792),i(26099),i(3362),i(62953);var a=i(92542),s=(t,e)=>new Promise((s=>{var n=e.closeDialog,o=e.logInHereAction;(0,a.r)(t,"show-dialog",{dialogTag:"dialog-cloud-already-connected",dialogImport:()=>i.e("8547").then(i.bind(i,6062)),dialogParams:Object.assign(Object.assign({},e),{},{closeDialog:()=>{null==n||n(),s(!1)},logInHereAction:()=>{null==o||o(),s(!0)}})})}))},18511:function(t,e,i){i.d(e,{L:function(){return n}});i(23792),i(26099),i(3362),i(62953);var a=i(92542),s=()=>Promise.all([i.e("5010"),i.e("2130"),i.e("1557"),i.e("7154")]).then(i.bind(i,67065)),n=(t,e)=>{(0,a.r)(t,"show-dialog",{dialogTag:"dialog-voice-assistant-pipeline-detail",dialogImport:s,dialogParams:e})}},24082:function(t,e,i){i.d(e,{T:function(){return g}});var a=i(78261),s=i(44734),n=i(56038),o=i(69683),r=i(6454),l=i(79993),c=(i(28706),i(74423),i(26099),i(96196)),u=i(54495),d=i(92542),h=i(38852),p=i(80111),v=function(t){function e(){var t;(0,s.A)(this,e);for(var i=arguments.length,a=new Array(i),n=0;n<i;n++)a[n]=arguments[n];return(t=(0,o.A)(this,e,[].concat(a))).holdTime=500,t.held=!1,t.cancelled=!1,t}return(0,r.A)(e,t),(0,n.A)(e,[{key:"connectedCallback",value:function(){Object.assign(this.style,{position:"fixed",width:p.C?"100px":"50px",height:p.C?"100px":"50px",transform:"translate(-50%, -50%) scale(0)",pointerEvents:"none",zIndex:"999",background:"var(--primary-color)",display:null,opacity:"0.2",borderRadius:"50%",transition:"transform 180ms ease-in-out"}),["touchcancel","mouseout","mouseup","touchmove","mousewheel","wheel","scroll"].forEach((t=>{document.addEventListener(t,(()=>{this.cancelled=!0,this.timer&&(this._stopAnimation(),clearTimeout(this.timer),this.timer=void 0)}),{passive:!0})}))}},{key:"bind",value:function(t){var e=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{};t.actionHandler&&(0,h.b)(e,t.actionHandler.options)||(t.actionHandler?(t.removeEventListener("touchstart",t.actionHandler.start),t.removeEventListener("touchend",t.actionHandler.end),t.removeEventListener("touchcancel",t.actionHandler.end),t.removeEventListener("mousedown",t.actionHandler.start),t.removeEventListener("click",t.actionHandler.end),t.removeEventListener("keydown",t.actionHandler.handleKeyDown)):t.addEventListener("contextmenu",(t=>{var e=t||window.event;return e.preventDefault&&e.preventDefault(),e.stopPropagation&&e.stopPropagation(),e.cancelBubble=!0,e.returnValue=!1,!1})),t.actionHandler={options:e},e.disabled||(t.actionHandler.start=t=>{var i,a;this.cancelled=!1,t.touches?(i=t.touches[0].clientX,a=t.touches[0].clientY):(i=t.clientX,a=t.clientY),e.hasHold&&(this.held=!1,this.timer=window.setTimeout((()=>{this._startAnimation(i,a),this.held=!0}),this.holdTime))},t.actionHandler.end=t=>{if(!("touchcancel"===t.type||"touchend"===t.type&&this.cancelled)){var i=t.target;t.cancelable&&t.preventDefault(),e.hasHold&&(clearTimeout(this.timer),this._stopAnimation(),this.timer=void 0),e.hasHold&&this.held?(0,d.r)(i,"action",{action:"hold"}):e.hasDoubleClick?"click"===t.type&&t.detail<2||!this.dblClickTimeout?this.dblClickTimeout=window.setTimeout((()=>{this.dblClickTimeout=void 0,!1!==e.hasTap&&(0,d.r)(i,"action",{action:"tap"})}),250):(clearTimeout(this.dblClickTimeout),this.dblClickTimeout=void 0,(0,d.r)(i,"action",{action:"double_tap"})):!1!==e.hasTap&&(0,d.r)(i,"action",{action:"tap"})}},t.actionHandler.handleKeyDown=t=>{["Enter"," "].includes(t.key)&&t.currentTarget.actionHandler.end(t)},t.addEventListener("touchstart",t.actionHandler.start,{passive:!0}),t.addEventListener("touchend",t.actionHandler.end),t.addEventListener("touchcancel",t.actionHandler.end),t.addEventListener("mousedown",t.actionHandler.start,{passive:!0}),t.addEventListener("click",t.actionHandler.end),t.addEventListener("keydown",t.actionHandler.handleKeyDown)))}},{key:"_startAnimation",value:function(t,e){Object.assign(this.style,{left:`${t}px`,top:`${e}px`,transform:"translate(-50%, -50%) scale(1)"})}},{key:"_stopAnimation",value:function(){Object.assign(this.style,{left:null,top:null,transform:"translate(-50%, -50%) scale(0)"})}}])}((0,l.A)(HTMLElement));customElements.define("action-handler",v);var _=(t,e)=>{var i=(()=>{var t=document.body;if(t.querySelector("action-handler"))return t.querySelector("action-handler");var e=document.createElement("action-handler");return t.appendChild(e),e})();i&&i.bind(t,e)},g=(0,u.u$)(function(t){function e(){return(0,s.A)(this,e),(0,o.A)(this,e,arguments)}return(0,r.A)(e,t),(0,n.A)(e,[{key:"update",value:function(t,e){var i=(0,a.A)(e,1)[0];return _(t.element,i),c.c0}},{key:"render",value:function(t){}}])}(u.WL))},78413:function(t,e,i){i.d(e,{v:function(){return n}});i(2008),i(62062),i(18111),i(22489),i(61701),i(26099);var a=i(55376),s=i(91889),n=(t,e,i)=>{if(!i)return e?(0,s.u)(e):"";if("object"!=typeof i)return String(i);if(e)return t.formatEntityName(e,i);var n=(0,a.e)(i).filter((t=>"text"===t.type)).map((t=>"text"in t?t.text:""));return n.length?n.join(" "):""}},67618:function(t,e,i){i.d(e,{$:function(){return f}});var a=i(61397),s=i(78261),n=i(50264),o=(i(18111),i(13579),i(26099),i(92542)),r=i(5871),l=i(7647),c=i(84125),u=i(10234),d=(i(23792),i(3362),i(62953),()=>i.e("8004").then(i.bind(i,28959))),h=(t,e,i)=>{var a,s,n;null!==(a=e.auth.external)&&void 0!==a&&a.config.hasAssist?e.auth.external.fireMessage({type:"assist/show",payload:{pipeline_id:i.pipeline_id,start_listening:null===(n=i.start_listening)||void 0===n||n}}):(0,o.r)(t,"show-dialog",{dialogTag:"ha-voice-command-dialog",dialogImport:d,dialogParams:{pipeline_id:i.pipeline_id,start_listening:null!==(s=i.start_listening)&&void 0!==s&&s}})},p=i(4848),v=(i(74423),i(72261)),_=i(41144),g=(t,e)=>function(t,e){var i,a=!(arguments.length>2&&void 0!==arguments[2])||arguments[2],s=(0,_.m)(e),n="group"===s?"homeassistant":s;switch(s){case"lock":i=a?"unlock":"lock";break;case"cover":i=a?"open_cover":"close_cover";break;case"button":case"input_button":i="press";break;case"scene":i="turn_on";break;case"valve":i=a?"open_valve":"close_valve";break;default:i=a?"turn_on":"turn_off"}return t.callService(n,i,{entity_id:e})}(t,e,v.jj.includes(t.states[e].state)),f=function(){var t=(0,n.A)((0,a.A)().m((function t(e,i,n,d){var v,_,f,y,m,w,b,k,A,$,x,z,C,E,M,S,I;return(0,a.A)().w((function(t){for(;;)switch(t.n){case 0:if("double_tap"===d&&n.double_tap_action?v=n.double_tap_action:"hold"===d&&n.hold_action?v=n.hold_action:"tap"===d&&n.tap_action&&(v=n.tap_action),v||(v={action:"more-info"}),!v.confirmation||v.confirmation.exemptions&&v.confirmation.exemptions.some((t=>{var e;return t.user===(null===(e=i.user)||void 0===e?void 0:e.id)}))){t.n=5;break}if((0,l.j)(e,"warning"),"call-service"!==v.action&&"perform-action"!==v.action){t.n=3;break}if(f=(v.perform_action||v.service).split(".",2),y=(0,s.A)(f,2),m=y[0],w=y[1],b=i.services,!(m in b)||!(w in b[m])){t.n=3;break}return t.n=1,i.loadBackendTranslation("title");case 1:return t.n=2,i.loadBackendTranslation("services");case 2:k=t.v,_=`${(0,c.p$)(k,m)}: ${k(`component.${m}.services.${w}.name`,i.services[m][w].description_placeholders)||b[m][w].name||w}`;case 3:return t.n=4,(0,u.dk)(e,{text:v.confirmation.text||i.localize("ui.panel.lovelace.cards.actions.action_confirmation",{action:_||i.localize(`ui.panel.lovelace.editor.action-editor.actions.${v.action}`)||v.action})});case 4:if(t.v){t.n=5;break}return t.a(2);case 5:I=v.action,t.n="more-info"===I?6:"navigate"===I?7:"url"===I?8:"toggle"===I?9:"perform-action"===I||"call-service"===I?10:"assist"===I?12:"fire-dom-event"===I?13:14;break;case 6:return(A=v.entity||n.entity||n.camera_image||n.image_entity)?(0,o.r)(e,"hass-more-info",{entityId:A}):((0,p.P)(e,{message:i.localize("ui.panel.lovelace.cards.actions.no_entity_more_info")}),(0,l.j)(e,"failure")),t.a(3,14);case 7:return v.navigation_path?(0,r.o)(v.navigation_path,{replace:v.navigation_replace}):((0,p.P)(e,{message:i.localize("ui.panel.lovelace.cards.actions.no_navigation_path")}),(0,l.j)(e,"failure")),t.a(3,14);case 8:return v.url_path?window.open(v.url_path):((0,p.P)(e,{message:i.localize("ui.panel.lovelace.cards.actions.no_url")}),(0,l.j)(e,"failure")),t.a(3,14);case 9:return n.entity?(g(i,n.entity),(0,l.j)(e,"light")):((0,p.P)(e,{message:i.localize("ui.panel.lovelace.cards.actions.no_entity_toggle")}),(0,l.j)(e,"failure")),t.a(3,14);case 10:if(v.perform_action||v.service){t.n=11;break}return(0,p.P)(e,{message:i.localize("ui.panel.lovelace.cards.actions.no_action")}),(0,l.j)(e,"failure"),t.a(2);case 11:return x=(v.perform_action||v.service).split(".",2),z=(0,s.A)(x,2),C=z[0],E=z[1],i.callService(C,E,null!==($=v.data)&&void 0!==$?$:v.service_data,v.target),(0,l.j)(e,"light"),t.a(3,14);case 12:return h(e,i,{start_listening:null!==(M=v.start_listening)&&void 0!==M&&M,pipeline_id:null!==(S=v.pipeline_id)&&void 0!==S?S:"last_used"}),t.a(3,14);case 13:(0,o.r)(e,"ll-custom",v);case 14:return t.a(2)}}),t)})));return function(e,i,a,s){return t.apply(this,arguments)}}()},46713:function(t,e,i){function a(t){return void 0!==t&&"none"!==t.action}function s(t){return!t.tap_action||a(t.tap_action)||a(t.hold_action)||a(t.double_tap_action)}i.d(e,{A:function(){return s},h:function(){return a}})},6731:function(t,e,i){i.d(e,{LX:function(){return o}});i(18111),i(13579),i(26099),i(16280),i(62062),i(61701),i(45996);function a(t,e){if(e.has("_config"))return!0;if(!e.has("hass"))return!1;var i=e.get("hass");return!i||(i.connected!==t.hass.connected||i.themes!==t.hass.themes||i.locale!==t.hass.locale||i.localize!==t.hass.localize||i.formatEntityState!==t.hass.formatEntityState||i.formatEntityAttributeName!==t.hass.formatEntityAttributeName||i.formatEntityAttributeValue!==t.hass.formatEntityAttributeValue||i.config.state!==t.hass.config.state)}function s(t,e,i){return t.states[i]!==e.states[i]}function n(t,e,i){var a=t.entities[i],s=e.entities[i];return(null==a?void 0:a.display_precision)!==(null==s?void 0:s.display_precision)}function o(t,e){if(a(t,e))return!0;if(!e.has("hass"))return!1;var i=e.get("hass"),o=t.hass;return s(i,o,t._config.entity)||n(i,o,t._config.entity)}},28064:function(t,e,i){i.a(t,(async function(t,e){try{var a=i(44734),s=i(56038),n=i(69683),o=i(6454),r=i(25460),l=(i(28706),i(74423),i(62826)),c=i(96196),u=i(77845),d=i(94333),h=i(32288),p=i(72261),v=i(28561),_=i(55124),g=i(32470),f=i(41144),y=i(49284),m=i(91720),w=i(18043),b=i(88422),k=i(24082),A=i(78413),$=i(67618),x=i(46713),z=i(95053),C=t([m,w,b,y]);[m,w,b,y]=C.then?(await C)():C;var E,M,S,I,O,P,L,q,T,H,Z,j,N=t=>t,W=function(t){function e(){var t;(0,a.A)(this,e);for(var i=arguments.length,s=new Array(i),o=0;o<i;o++)s[o]=arguments[o];return(t=(0,n.A)(this,e,[].concat(s))).hideName=!1,t._secondaryInfoElementId="-"+(0,v.L)(),t}return(0,o.A)(e,t),(0,s.A)(e,[{key:"render",value:function(){var t;if(!this.hass||!this.config)return c.s6;var e=this.config.entity?this.hass.states[this.config.entity]:void 0;if(!e)return(0,c.qy)(E||(E=N`
        <hui-warning .hass=${0}>
          ${0}
        </hui-warning>
      `),this.hass,(0,z.j)(this.hass,this.config.entity));var i=(0,f.m)(this.config.entity),a=(0,x.A)(this.config),s=this.secondaryText||this.config.secondary_info,n=(0,A.v)(this.hass,e,this.config.name);return(0,c.qy)(M||(M=N`
      <div
        class="row ${0}"
        @action=${0}
        .actionHandler=${0}
        tabindex=${0}
      >
        <state-badge
          .hass=${0}
          .stateObj=${0}
          .overrideIcon=${0}
          .overrideImage=${0}
          .stateColor=${0}
        ></state-badge>
        ${0}
        ${0}
      </div>
    `),(0,d.H)({pointer:a}),this._handleAction,(0,k.T)({hasHold:(0,x.h)(this.config.hold_action),hasDoubleClick:(0,x.h)(this.config.double_tap_action)}),(0,h.J)(!this.config.tap_action||(0,x.h)(this.config.tap_action)?"0":void 0),this.hass,e,this.config.icon,this.config.image,this.config.state_color,this.hideName?c.s6:(0,c.qy)(S||(S=N`<div
              class="info ${0}"
              .title=${0}
            >
              ${0}
              ${0}
            </div>`),(0,d.H)({"text-content":!s}),n,n,s?(0,c.qy)(I||(I=N`
                    <div class="secondary">
                      ${0}
                    </div>
                  `),this.secondaryText||("entity-id"===this.config.secondary_info?e.entity_id:"last-changed"===this.config.secondary_info?(0,c.qy)(O||(O=N`
                              <ha-tooltip
                                for="last-changed${0}"
                                placement="right"
                              >
                                ${0}
                              </ha-tooltip>
                              <ha-relative-time
                                id="last-changed${0}"
                                .hass=${0}
                                .datetime=${0}
                                capitalize
                              ></ha-relative-time>
                            `),this._secondaryInfoElementId,(0,y.yg)(new Date(e.last_changed),this.hass.locale,this.hass.config),this._secondaryInfoElementId,this.hass,e.last_changed):"last-updated"===this.config.secondary_info?(0,c.qy)(P||(P=N`
                                <ha-tooltip
                                  for="last-updated${0}"
                                  placement="right"
                                >
                                  ${0}
                                </ha-tooltip>
                                <ha-relative-time
                                  id="last-updated${0}"
                                  .hass=${0}
                                  .datetime=${0}
                                  capitalize
                                ></ha-relative-time>
                              `),this._secondaryInfoElementId,(0,y.yg)(new Date(e.last_updated),this.hass.locale,this.hass.config),this._secondaryInfoElementId,this.hass,e.last_updated):"last-triggered"===this.config.secondary_info?e.attributes.last_triggered?(0,c.qy)(L||(L=N`
                                    <ha-tooltip
                                      for="last-triggered${0}"
                                      placement="right"
                                    >
                                      ${0}
                                    </ha-tooltip>
                                    <ha-relative-time
                                      id="last-triggered${0}"
                                      .hass=${0}
                                      .datetime=${0}
                                      capitalize
                                    ></ha-relative-time>
                                  `),this._secondaryInfoElementId,(0,y.yg)(new Date(e.attributes.last_triggered),this.hass.locale,this.hass.config),this._secondaryInfoElementId,this.hass,e.attributes.last_triggered):this.hass.localize("ui.panel.lovelace.cards.entities.never_triggered"):"position"===this.config.secondary_info&&void 0!==e.attributes.current_position?`${this.hass.localize("ui.card.cover.position")}: ${e.attributes.current_position}`:"tilt-position"===this.config.secondary_info&&void 0!==e.attributes.current_tilt_position?`${this.hass.localize("ui.card.cover.tilt_position")}: ${e.attributes.current_tilt_position}`:"brightness"===this.config.secondary_info&&e.attributes.brightness?(0,c.qy)(q||(q=N`${0}
                                      %`),Math.round(e.attributes.brightness/255*100)):"state"===this.config.secondary_info?(0,c.qy)(T||(T=N`${0}`),this.hass.formatEntityState(e)):c.s6)):c.s6),(null!==(t=this.catchInteraction)&&void 0!==t?t:!p.yd.includes(i))?(0,c.qy)(H||(H=N`
              <div class="text-content value">
                <div class="state"><slot></slot></div>
              </div>
            `)):(0,c.qy)(Z||(Z=N`<slot
              @touchcancel=${0}
              @touchend=${0}
              @keydown=${0}
              @click=${0}
              @action=${0}
            ></slot>`),_.d,_.d,_.d,_.d,_.d))}},{key:"updated",value:function(t){var i;(0,r.A)(e,"updated",this,3)([t]),(0,g.j)(this,"no-secondary",!(this.secondaryText||null!==(i=this.config)&&void 0!==i&&i.secondary_info))}},{key:"_handleAction",value:function(t){(0,$.$)(this,this.hass,this.config,t.detail.action)}}])}(c.WF);W.styles=(0,c.AH)(j||(j=N`
    :host {
      display: flex;
      align-items: center;
      flex-direction: row;
    }
    .row {
      display: flex;
      align-items: center;
      flex-direction: row;
      width: 100%;
      outline: none;
      transition: background-color 180ms ease-in-out;
    }
    .row:focus-visible {
      background-color: var(--primary-background-color);
    }
    .info {
      padding-left: 16px;
      padding-right: 8px;
      padding-inline-start: 16px;
      padding-inline-end: 8px;
      flex: 1 1 30%;
    }
    .info,
    .info > * {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .flex ::slotted(*) {
      margin-left: 8px;
      margin-inline-start: 8px;
      margin-inline-end: initial;
      min-width: 0;
    }
    .flex ::slotted([slot="secondary"]) {
      margin-left: 0;
      margin-inline-start: 0;
      margin-inline-end: initial;
    }
    .secondary,
    ha-relative-time {
      color: var(--secondary-text-color);
    }
    state-badge {
      flex: 0 0 40px;
    }
    .pointer {
      cursor: pointer;
    }
    .state {
      text-align: var(--float-end);
    }
    .value {
      direction: ltr;
    }
  `)),(0,l.__decorate)([(0,u.MZ)({attribute:!1})],W.prototype,"hass",void 0),(0,l.__decorate)([(0,u.MZ)({attribute:!1})],W.prototype,"config",void 0),(0,l.__decorate)([(0,u.MZ)({attribute:"secondary-text"})],W.prototype,"secondaryText",void 0),(0,l.__decorate)([(0,u.MZ)({attribute:"hide-name",type:Boolean})],W.prototype,"hideName",void 0),(0,l.__decorate)([(0,u.MZ)({attribute:"catch-interaction",type:Boolean})],W.prototype,"catchInteraction",void 0),W=(0,l.__decorate)([(0,u.EM)("hui-generic-entity-row")],W),e()}catch(D){e(D)}}))},95053:function(t,e,i){i.d(e,{j:function(){return w}});var a,s,n,o,r=i(44734),l=i(56038),c=i(69683),u=i(6454),d=i(62826),h=i(58888),p=i(96196),v=i(77845),_=(i(17963),i(28706),i(95379),i(60961),t=>t),g={warning:"M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16",error:"M11,15H13V17H11V15M11,7H13V13H11V7M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20Z"},f=function(t){function e(){var t;(0,r.A)(this,e);for(var i=arguments.length,a=new Array(i),s=0;s<i;s++)a[s]=arguments[s];return(t=(0,c.A)(this,e,[].concat(a))).preview=!1,t.severity="error",t}return(0,u.A)(e,t),(0,l.A)(e,[{key:"getCardSize",value:function(){return 1}},{key:"getGridOptions",value:function(){return{columns:6,rows:this.preview?"auto":1,min_rows:1,min_columns:6,fixed_rows:this.preview}}},{key:"setConfig",value:function(t){this._config=t,this.severity=t.severity||"error"}},{key:"render",value:function(){var t,e,i,o,r,l=(null===(t=this._config)||void 0===t?void 0:t.error)||"warning"===this.severity&&(null===(e=this.hass)||void 0===e?void 0:e.localize("ui.errors.config.configuration_warning"))||(null===(i=this.hass)||void 0===i?void 0:i.localize("ui.errors.config.configuration_error")),c=void 0===this.hass||(null===(o=this.hass)||void 0===o||null===(o=o.user)||void 0===o?void 0:o.is_admin)||this.preview,u=this.preview;return(0,p.qy)(a||(a=_`
      <ha-card class="${0} ${0}">
        <div class="header">
          <div class="icon">
            <slot name="icon">
              <ha-svg-icon .path=${0}></ha-svg-icon>
            </slot>
          </div>
          ${0}
        </div>
        ${0}
      </ha-card>
    `),this.severity,c?"":"no-title",g[this.severity],c?(0,p.qy)(s||(s=_`<div class="title"><slot>${0}</slot></div>`),l):p.s6,u&&null!==(r=this._config)&&void 0!==r&&r.message?(0,p.qy)(n||(n=_`<div class="message">${0}</div>`),this._config.message):p.s6)}}])}(p.WF);f.styles=(0,p.AH)(o||(o=_`
    ha-card {
      height: 100%;
      border-width: 0;
    }
    ha-card::after {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      opacity: 0.12;
      pointer-events: none;
      content: "";
      border-radius: var(--ha-card-border-radius, var(--ha-border-radius-lg));
    }
    .header {
      display: flex;
      align-items: center;
      gap: var(--ha-space-2);
      padding: 16px;
    }
    .message {
      padding: 0 16px 16px 16px;
    }
    .no-title {
      justify-content: center;
    }
    .title {
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      font-weight: var(--ha-font-weight-bold);
    }
    ha-card.warning .icon {
      color: var(--warning-color);
    }
    ha-card.warning::after {
      background-color: var(--warning-color);
    }
    ha-card.error .icon {
      color: var(--error-color);
    }
    ha-card.error::after {
      background-color: var(--error-color);
    }
  `)),(0,d.__decorate)([(0,v.MZ)({attribute:!1})],f.prototype,"hass",void 0),(0,d.__decorate)([(0,v.MZ)({attribute:!1})],f.prototype,"preview",void 0),(0,d.__decorate)([(0,v.MZ)({attribute:"severity"})],f.prototype,"severity",void 0),(0,d.__decorate)([(0,v.wk)()],f.prototype,"_config",void 0),f=(0,d.__decorate)([(0,v.EM)("hui-error-card")],f);var y,m=t=>t,w=(t,e)=>t.config.state!==h.m2?t.localize("ui.card.common.entity_not_found"):t.localize("ui.panel.lovelace.warning.starting"),b=function(t){function e(){return(0,r.A)(this,e),(0,c.A)(this,e,arguments)}return(0,u.A)(e,t),(0,l.A)(e,[{key:"render",value:function(){return(0,p.qy)(y||(y=m`<hui-error-card .hass=${0} severity="warning"
      ><slot></slot
    ></hui-error-card>`),this.hass)}}])}(p.WF);(0,d.__decorate)([(0,v.MZ)({attribute:!1})],b.prototype,"hass",void 0),b=(0,d.__decorate)([(0,v.EM)("hui-warning")],b)},82472:function(t,e,i){i.a(t,(async function(t,e){try{var a=i(44734),s=i(56038),n=i(69683),o=i(6454),r=(i(16280),i(74423),i(62062),i(18111),i(61701),i(26099),i(62826)),l=i(96196),c=i(77845),u=i(55124),d=(i(56565),i(69869),i(31136)),h=i(7647),p=i(84043),v=i(78413),_=i(6731),g=i(28064),f=i(95053),y=t([g]);g=(y.then?(await y)():y)[0];var m,w,b,k,A=t=>t,$=function(t){function e(){return(0,a.A)(this,e),(0,n.A)(this,e,arguments)}return(0,o.A)(e,t),(0,s.A)(e,[{key:"setConfig",value:function(t){if(!t||!t.entity)throw new Error("Entity must be specified");this._config=t}},{key:"shouldUpdate",value:function(t){return(0,_.LX)(this,t)}},{key:"render",value:function(){if(!this.hass||!this._config)return l.s6;var t=this.hass.states[this._config.entity];if(!t)return(0,l.qy)(m||(m=A`
        <hui-warning .hass=${0}>
          ${0}
        </hui-warning>
      `),this.hass,(0,f.j)(this.hass,this._config.entity));var e=(0,v.v)(this.hass,t,this._config.name);return(0,l.qy)(w||(w=A`
      <hui-generic-entity-row
        .hass=${0}
        .config=${0}
        hide-name
      >
        <ha-select
          .label=${0}
          .value=${0}
          .options=${0}
          .disabled=${0}
          naturalMenuWidth
          @action=${0}
          @click=${0}
          @closed=${0}
        >
          ${0}
        </ha-select>
      </hui-generic-entity-row>
    `),this.hass,this._config,e,t.state,t.attributes.options,t.state===d.Hh,this._handleAction,u.d,u.d,t.attributes.options?t.attributes.options.map((e=>(0,l.qy)(b||(b=A`
                  <ha-list-item .value=${0}>
                    ${0}
                  </ha-list-item>
                `),e,this.hass.formatEntityState(t,e)))):"")}},{key:"_handleAction",value:function(t){var e=this.hass.states[this._config.entity],i=t.target.value;i!==e.state&&e.attributes.options.includes(i)&&((0,h.j)(this,"light"),(0,p.w)(this.hass,e.entity_id,i))}}])}(l.WF);$.styles=(0,l.AH)(k||(k=A`
    hui-generic-entity-row {
      display: flex;
      align-items: center;
    }
    ha-select {
      width: 100%;
      --ha-select-min-width: 0;
    }
  `)),(0,r.__decorate)([(0,c.MZ)({attribute:!1})],$.prototype,"hass",void 0),(0,r.__decorate)([(0,c.wk)()],$.prototype,"_config",void 0),$=(0,r.__decorate)([(0,c.EM)("hui-select-entity-row")],$),e()}catch(x){e(x)}}))},80111:function(t,e,i){i.d(e,{C:function(){return a}});var a="ontouchstart"in window||navigator.maxTouchPoints>0||navigator.msMaxTouchPoints>0}}]);
//# sourceMappingURL=2097.78a68eca972372f0.js.map