"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["1535"],{25749:function(e,t,a){a.d(t,{SH:function(){return l},u1:function(){return d},xL:function(){return s}});a(94741),a(28706),a(33771),a(25276),a(62062),a(18111),a(61701),a(2892),a(26099),a(68156);var r=a(22786),i=(a(35937),(0,r.A)((e=>new Intl.Collator(e,{numeric:!0})))),n=(0,r.A)((e=>new Intl.Collator(e,{sensitivity:"accent",numeric:!0}))),o=(e,t)=>e<t?-1:e>t?1:0,s=function(e,t){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:void 0;return null!==Intl&&void 0!==Intl&&Intl.Collator?i(a).compare(e,t):o(e,t)},l=function(e,t){var a=arguments.length>2&&void 0!==arguments[2]?arguments[2]:void 0;return null!==Intl&&void 0!==Intl&&Intl.Collator?n(a).compare(e,t):o(e.toLowerCase(),t.toLowerCase())},d=e=>(t,a)=>{var r=e.indexOf(t),i=e.indexOf(a);return r===i?0:-1===r?1:-1===i?-1:r-i}},35937:function(e,t,a){a(27495),a(90906)},95379:function(e,t,a){var r,i,n,o=a(44734),s=a(56038),l=a(69683),d=a(6454),c=(a(28706),a(62826)),p=a(96196),u=a(77845),h=e=>e,g=function(e){function t(){var e;(0,o.A)(this,t);for(var a=arguments.length,r=new Array(a),i=0;i<a;i++)r[i]=arguments[i];return(e=(0,l.A)(this,t,[].concat(r))).raised=!1,e}return(0,d.A)(t,e),(0,s.A)(t,[{key:"render",value:function(){return(0,p.qy)(r||(r=h`
      ${0}
      <slot></slot>
    `),this.header?(0,p.qy)(i||(i=h`<h1 class="card-header">${0}</h1>`),this.header):p.s6)}}])}(p.WF);g.styles=(0,p.AH)(n||(n=h`
    :host {
      background: var(
        --ha-card-background,
        var(--card-background-color, white)
      );
      -webkit-backdrop-filter: var(--ha-card-backdrop-filter, none);
      backdrop-filter: var(--ha-card-backdrop-filter, none);
      box-shadow: var(--ha-card-box-shadow, none);
      box-sizing: border-box;
      border-radius: var(--ha-card-border-radius, var(--ha-border-radius-lg));
      border-width: var(--ha-card-border-width, 1px);
      border-style: solid;
      border-color: var(--ha-card-border-color, var(--divider-color, #e0e0e0));
      color: var(--primary-text-color);
      display: block;
      transition: all 0.3s ease-out;
      position: relative;
    }

    :host([raised]) {
      border: none;
      box-shadow: var(
        --ha-card-box-shadow,
        0px 2px 1px -1px rgba(0, 0, 0, 0.2),
        0px 1px 1px 0px rgba(0, 0, 0, 0.14),
        0px 1px 3px 0px rgba(0, 0, 0, 0.12)
      );
    }

    .card-header,
    :host ::slotted(.card-header) {
      color: var(--ha-card-header-color, var(--primary-text-color));
      font-family: var(--ha-card-header-font-family, inherit);
      font-size: var(--ha-card-header-font-size, var(--ha-font-size-2xl));
      letter-spacing: -0.012em;
      line-height: var(--ha-line-height-expanded);
      padding: var(--ha-space-3) var(--ha-space-4) var(--ha-space-4);
      display: block;
      margin-block-start: var(--ha-space-0);
      margin-block-end: var(--ha-space-0);
      font-weight: var(--ha-font-weight-normal);
    }

    :host ::slotted(.card-content:not(:first-child)),
    slot:not(:first-child)::slotted(.card-content) {
      padding-top: var(--ha-space-0);
      margin-top: calc(var(--ha-space-2) * -1);
    }

    :host ::slotted(.card-content) {
      padding: var(--ha-space-4);
    }

    :host ::slotted(.card-actions) {
      border-top: 1px solid var(--divider-color, #e8e8e8);
      padding: var(--ha-space-2);
    }
  `)),(0,c.__decorate)([(0,u.MZ)()],g.prototype,"header",void 0),(0,c.__decorate)([(0,u.MZ)({type:Boolean,reflect:!0})],g.prototype,"raised",void 0),g=(0,c.__decorate)([(0,u.EM)("ha-card")],g)},53623:function(e,t,a){a.a(e,(async function(e,r){try{a.r(t),a.d(t,{HaIconOverflowMenu:function(){return A}});var i=a(44734),n=a(56038),o=a(69683),s=a(6454),l=(a(28706),a(62062),a(18111),a(61701),a(26099),a(62826)),d=a(96196),c=a(77845),p=a(94333),u=a(39396),h=(a(63419),a(60733),a(60961),a(88422)),g=(a(99892),a(32072),e([h]));h=(g.then?(await g)():g)[0];var v,f,b,x,m,_,y,w,k=e=>e,A=function(e){function t(){var e;(0,i.A)(this,t);for(var a=arguments.length,r=new Array(a),n=0;n<a;n++)r[n]=arguments[n];return(e=(0,o.A)(this,t,[].concat(r))).items=[],e.narrow=!1,e}return(0,s.A)(t,e),(0,n.A)(t,[{key:"render",value:function(){return 0===this.items.length?d.s6:(0,d.qy)(v||(v=k`
      ${0}
    `),this.narrow?(0,d.qy)(f||(f=k` <!-- Collapsed representation for small screens -->
            <ha-md-button-menu
              @click=${0}
              positioning="popover"
            >
              <ha-icon-button
                .label=${0}
                .path=${0}
                slot="trigger"
              ></ha-icon-button>

              ${0}
            </ha-md-button-menu>`),this._handleIconOverflowMenuOpened,this.hass.localize("ui.common.overflow_menu"),"M12,16A2,2 0 0,1 14,18A2,2 0 0,1 12,20A2,2 0 0,1 10,18A2,2 0 0,1 12,16M12,10A2,2 0 0,1 14,12A2,2 0 0,1 12,14A2,2 0 0,1 10,12A2,2 0 0,1 12,10M12,4A2,2 0 0,1 14,6A2,2 0 0,1 12,8A2,2 0 0,1 10,6A2,2 0 0,1 12,4Z",this.items.map((e=>e.divider?(0,d.qy)(b||(b=k`<ha-md-divider
                      role="separator"
                      tabindex="-1"
                    ></ha-md-divider>`)):(0,d.qy)(x||(x=k`<ha-md-menu-item
                      ?disabled=${0}
                      .clickAction=${0}
                      class=${0}
                    >
                      <ha-svg-icon
                        slot="start"
                        class=${0}
                        .path=${0}
                      ></ha-svg-icon>
                      ${0}
                    </ha-md-menu-item>`),e.disabled,e.action,(0,p.H)({warning:Boolean(e.warning)}),(0,p.H)({warning:Boolean(e.warning)}),e.path,e.label)))):(0,d.qy)(m||(m=k`
            <!-- Icon representation for big screens -->
            ${0}
          `),this.items.map((e=>{var t;return e.narrowOnly?d.s6:e.divider?(0,d.qy)(_||(_=k`<div role="separator"></div>`)):(0,d.qy)(y||(y=k`<ha-tooltip
                        .disabled=${0}
                        .for="icon-button-${0}"
                        >${0} </ha-tooltip
                      ><ha-icon-button
                        .id="icon-button-${0}"
                        @click=${0}
                        .label=${0}
                        .path=${0}
                        ?disabled=${0}
                      ></ha-icon-button> `),!e.tooltip,e.label,null!==(t=e.tooltip)&&void 0!==t?t:"",e.label,e.action,e.label,e.path,e.disabled)}))))}},{key:"_handleIconOverflowMenuOpened",value:function(e){e.stopPropagation()}}],[{key:"styles",get:function(){return[u.RF,(0,d.AH)(w||(w=k`
        :host {
          display: flex;
          justify-content: flex-end;
          cursor: initial;
        }
        div[role="separator"] {
          border-right: 1px solid var(--divider-color);
          width: 1px;
        }
      `))]}}])}(d.WF);(0,l.__decorate)([(0,c.MZ)({attribute:!1})],A.prototype,"hass",void 0),(0,l.__decorate)([(0,c.MZ)({type:Array})],A.prototype,"items",void 0),(0,l.__decorate)([(0,c.MZ)({type:Boolean})],A.prototype,"narrow",void 0),A=(0,l.__decorate)([(0,c.EM)("ha-icon-overflow-menu")],A),r()}catch($){r($)}}))},89600:function(e,t,a){a.a(e,(async function(e,t){try{var r=a(44734),i=a(56038),n=a(69683),o=a(25460),s=a(6454),l=a(62826),d=a(55262),c=a(96196),p=a(77845),u=e([d]);d=(u.then?(await u)():u)[0];var h,g=e=>e,v=function(e){function t(){return(0,r.A)(this,t),(0,n.A)(this,t,arguments)}return(0,s.A)(t,e),(0,i.A)(t,[{key:"updated",value:function(e){if((0,o.A)(t,"updated",this,3)([e]),e.has("size"))switch(this.size){case"tiny":this.style.setProperty("--ha-spinner-size","16px");break;case"small":this.style.setProperty("--ha-spinner-size","28px");break;case"medium":this.style.setProperty("--ha-spinner-size","48px");break;case"large":this.style.setProperty("--ha-spinner-size","68px");break;case void 0:this.style.removeProperty("--ha-progress-ring-size")}}}],[{key:"styles",get:function(){return[d.A.styles,(0,c.AH)(h||(h=g`
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
      `))]}}])}(d.A);(0,l.__decorate)([(0,p.MZ)()],v.prototype,"size",void 0),v=(0,l.__decorate)([(0,p.EM)("ha-spinner")],v),t()}catch(f){t(f)}}))},78740:function(e,t,a){a.d(t,{h:function(){return m}});var r,i,n,o,s=a(44734),l=a(56038),d=a(69683),c=a(6454),p=a(25460),u=(a(28706),a(62826)),h=a(68846),g=a(92347),v=a(96196),f=a(77845),b=a(76679),x=e=>e,m=function(e){function t(){var e;(0,s.A)(this,t);for(var a=arguments.length,r=new Array(a),i=0;i<a;i++)r[i]=arguments[i];return(e=(0,d.A)(this,t,[].concat(r))).icon=!1,e.iconTrailing=!1,e.autocorrect=!0,e}return(0,c.A)(t,e),(0,l.A)(t,[{key:"updated",value:function(e){(0,p.A)(t,"updated",this,3)([e]),(e.has("invalid")||e.has("errorMessage"))&&(this.setCustomValidity(this.invalid?this.errorMessage||this.validationMessage||"Invalid":""),(this.invalid||this.validateOnInitialRender||e.has("invalid")&&void 0!==e.get("invalid"))&&this.reportValidity()),e.has("autocomplete")&&(this.autocomplete?this.formElement.setAttribute("autocomplete",this.autocomplete):this.formElement.removeAttribute("autocomplete")),e.has("autocorrect")&&(!1===this.autocorrect?this.formElement.setAttribute("autocorrect","off"):this.formElement.removeAttribute("autocorrect")),e.has("inputSpellcheck")&&(this.inputSpellcheck?this.formElement.setAttribute("spellcheck",this.inputSpellcheck):this.formElement.removeAttribute("spellcheck"))}},{key:"renderIcon",value:function(e){var t=arguments.length>1&&void 0!==arguments[1]&&arguments[1],a=t?"trailing":"leading";return(0,v.qy)(r||(r=x`
      <span
        class="mdc-text-field__icon mdc-text-field__icon--${0}"
        tabindex=${0}
      >
        <slot name="${0}Icon"></slot>
      </span>
    `),a,t?1:-1,a)}}])}(h.J);m.styles=[g.R,(0,v.AH)(i||(i=x`
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
    `)),"rtl"===b.G.document.dir?(0,v.AH)(n||(n=x`
          .mdc-text-field--with-leading-icon,
          .mdc-text-field__icon--leading,
          .mdc-floating-label,
          .mdc-text-field--with-leading-icon.mdc-text-field--filled
            .mdc-floating-label,
          .mdc-text-field__input[type="number"] {
            direction: rtl;
            --direction: rtl;
          }
        `)):(0,v.AH)(o||(o=x``))],(0,u.__decorate)([(0,f.MZ)({type:Boolean})],m.prototype,"invalid",void 0),(0,u.__decorate)([(0,f.MZ)({attribute:"error-message"})],m.prototype,"errorMessage",void 0),(0,u.__decorate)([(0,f.MZ)({type:Boolean})],m.prototype,"icon",void 0),(0,u.__decorate)([(0,f.MZ)({type:Boolean})],m.prototype,"iconTrailing",void 0),(0,u.__decorate)([(0,f.MZ)()],m.prototype,"autocomplete",void 0),(0,u.__decorate)([(0,f.MZ)({type:Boolean})],m.prototype,"autocorrect",void 0),(0,u.__decorate)([(0,f.MZ)({attribute:"input-spellcheck"})],m.prototype,"inputSpellcheck",void 0),(0,u.__decorate)([(0,f.P)("input")],m.prototype,"formElement",void 0),m=(0,u.__decorate)([(0,f.EM)("ha-textfield")],m)},88422:function(e,t,a){a.a(e,(async function(e,t){try{var r=a(44734),i=a(56038),n=a(69683),o=a(6454),s=(a(28706),a(2892),a(62826)),l=a(52630),d=a(96196),c=a(77845),p=e([l]);l=(p.then?(await p)():p)[0];var u,h=e=>e,g=function(e){function t(){var e;(0,r.A)(this,t);for(var a=arguments.length,i=new Array(a),o=0;o<a;o++)i[o]=arguments[o];return(e=(0,n.A)(this,t,[].concat(i))).showDelay=150,e.hideDelay=150,e}return(0,o.A)(t,e),(0,i.A)(t,null,[{key:"styles",get:function(){return[l.A.styles,(0,d.AH)(u||(u=h`
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
      `))]}}])}(l.A);(0,s.__decorate)([(0,c.MZ)({attribute:"show-delay",type:Number})],g.prototype,"showDelay",void 0),(0,s.__decorate)([(0,c.MZ)({attribute:"hide-delay",type:Number})],g.prototype,"hideDelay",void 0),g=(0,s.__decorate)([(0,c.EM)("ha-tooltip")],g),t()}catch(v){t(v)}}))},71950:function(e,t,a){a.a(e,(async function(e,t){try{a(23792),a(26099),a(3362),a(62953);var r=a(71950),i=e([r]);r=(i.then?(await i)():i)[0],"function"!=typeof window.ResizeObserver&&(window.ResizeObserver=(await a.e("1055").then(a.bind(a,52370))).default),t()}catch(n){t(n)}}),1)},84183:function(e,t,a){a.d(t,{i:function(){return n}});var r=a(61397),i=a(50264),n=(a(23792),a(26099),a(3362),a(62953),function(){var e=(0,i.A)((0,r.A)().m((function e(){return(0,r.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,a.e("8085").then(a.bind(a,40772));case 1:return e.a(2)}}),e)})));return function(){return e.apply(this,arguments)}}())},48680:function(e,t,a){var r,i,n,o,s,l,d=a(78261),c=a(44734),p=a(56038),u=a(69683),h=a(6454),g=a(25460),v=(a(28706),a(62062),a(72712),a(18111),a(7588),a(61701),a(18237),a(5506),a(26099),a(16034),a(23500),a(62826)),f=a(96196),b=a(77845),x=a(94333),m=a(92542),_=a(78577),y=e=>e,w=new _.Q("knx-project-tree-view"),k=function(e){function t(){var e;(0,c.A)(this,t);for(var a=arguments.length,r=new Array(a),i=0;i<a;i++)r[i]=arguments[i];return(e=(0,u.A)(this,t,[].concat(r))).multiselect=!1,e._selectableRanges={},e}return(0,h.A)(t,e),(0,p.A)(t,[{key:"connectedCallback",value:function(){(0,g.A)(t,"connectedCallback",this,3)([]);var e=t=>{Object.entries(t).forEach((t=>{var a=(0,d.A)(t,2),r=a[0],i=a[1];i.group_addresses.length>0&&(this._selectableRanges[r]={selected:!1,groupAddresses:i.group_addresses}),e(i.group_ranges)}))};e(this.data.group_ranges),w.debug("ranges",this._selectableRanges)}},{key:"render",value:function(){return(0,f.qy)(r||(r=y`<div class="ha-tree-view">${0}</div>`),this._recurseData(this.data.group_ranges))}},{key:"_recurseData",value:function(e){var t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:0,a=Object.entries(e).map((e=>{var a=(0,d.A)(e,2),r=a[0],s=a[1],l=Object.keys(s.group_ranges).length>0;if(!(l||s.group_addresses.length>0))return f.s6;var c=r in this._selectableRanges,p=!!c&&this._selectableRanges[r].selected,u={"range-item":!0,"root-range":0===t,"sub-range":t>0,selectable:c,"selected-range":p,"non-selected-range":c&&!p},h=(0,f.qy)(i||(i=y`<div
        class=${0}
        toggle-range=${0}
        @click=${0}
      >
        <span class="range-key">${0}</span>
        <span class="range-text">${0}</span>
      </div>`),(0,x.H)(u),c?r:f.s6,c?this.multiselect?this._selectionChangedMulti:this._selectionChangedSingle:f.s6,r,s.name);if(l){var g={"root-group":0===t,"sub-group":0!==t};return(0,f.qy)(n||(n=y`<div class=${0}>
          ${0} ${0}
        </div>`),(0,x.H)(g),h,this._recurseData(s.group_ranges,t+1))}return(0,f.qy)(o||(o=y`${0}`),h)}));return(0,f.qy)(s||(s=y`${0}`),a)}},{key:"_selectionChangedMulti",value:function(e){var t=e.target.getAttribute("toggle-range");this._selectableRanges[t].selected=!this._selectableRanges[t].selected,this._selectionUpdate(),this.requestUpdate()}},{key:"_selectionChangedSingle",value:function(e){var t=e.target.getAttribute("toggle-range"),a=this._selectableRanges[t].selected;Object.values(this._selectableRanges).forEach((e=>{e.selected=!1})),this._selectableRanges[t].selected=!a,this._selectionUpdate(),this.requestUpdate()}},{key:"_selectionUpdate",value:function(){var e=Object.values(this._selectableRanges).reduce(((e,t)=>t.selected?e.concat(t.groupAddresses):e),[]);w.debug("selection changed",e),(0,m.r)(this,"knx-group-range-selection-changed",{groupAddresses:e})}}])}(f.WF);k.styles=(0,f.AH)(l||(l=y`
    :host {
      margin: 0;
      height: 100%;
      overflow-y: scroll;
      overflow-x: hidden;
      background-color: var(--card-background-color);
    }

    .ha-tree-view {
      cursor: default;
    }

    .root-group {
      margin-bottom: 8px;
    }

    .root-group > * {
      padding-top: 5px;
      padding-bottom: 5px;
    }

    .range-item {
      display: block;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      font-size: 0.875rem;
    }

    .range-item > * {
      vertical-align: middle;
      pointer-events: none;
    }

    .range-key {
      color: var(--text-primary-color);
      font-size: 0.75rem;
      font-weight: 700;
      background-color: var(--label-badge-grey);
      border-radius: 4px;
      padding: 1px 4px;
      margin-right: 2px;
    }

    .root-range {
      padding-left: 8px;
      font-weight: 500;
      background-color: var(--secondary-background-color);

      & .range-key {
        color: var(--primary-text-color);
        background-color: var(--card-background-color);
      }
    }

    .sub-range {
      padding-left: 13px;
    }

    .selectable {
      cursor: pointer;
    }

    .selectable:hover {
      background-color: rgba(var(--rgb-primary-text-color), 0.04);
    }

    .selected-range {
      background-color: rgba(var(--rgb-primary-color), 0.12);

      & .range-key {
        background-color: var(--primary-color);
      }
    }

    .selected-range:hover {
      background-color: rgba(var(--rgb-primary-color), 0.07);
    }

    .non-selected-range {
      background-color: var(--card-background-color);
    }
  `)),(0,v.__decorate)([(0,b.MZ)({attribute:!1})],k.prototype,"data",void 0),(0,v.__decorate)([(0,b.MZ)({attribute:!1})],k.prototype,"multiselect",void 0),(0,v.__decorate)([(0,b.wk)()],k.prototype,"_selectableRanges",void 0),k=(0,v.__decorate)([(0,b.EM)("knx-project-tree-view")],k)},19337:function(e,t,a){a.d(t,{$k:function(){return p},Ah:function(){return s},HG:function(){return o},Vt:function(){return c},Yb:function(){return d},_O:function(){return u},oJ:function(){return h}});var r=a(94741),i=a(78261),n=(a(28706),a(2008),a(74423),a(62062),a(44114),a(72712),a(18111),a(22489),a(7588),a(61701),a(18237),a(13579),a(5506),a(26099),a(16034),a(38781),a(68156),a(42762),a(23500),a(22786)),o=(e,t)=>t.some((t=>e.main===t.main&&(!t.sub||e.sub===t.sub))),s=(e,t)=>{var a=((e,t)=>Object.entries(e.group_addresses).reduce(((e,a)=>{var r=(0,i.A)(a,2),n=r[0],s=r[1];return s.dpt&&o(s.dpt,t)&&(e[n]=s),e}),{}))(e,t);return Object.entries(e.communication_objects).reduce(((e,t)=>{var r=(0,i.A)(t,2),n=r[0],o=r[1];return o.group_address_links.some((e=>e in a))&&(e[n]=o),e}),{})};function l(e,t){var a=[];return e.forEach((e=>{"knx_group_address"!==e.type?"schema"in e&&a.push.apply(a,(0,r.A)(l(e.schema,t))):e.options.validDPTs?a.push.apply(a,(0,r.A)(e.options.validDPTs)):e.options.dptSelect?a.push.apply(a,(0,r.A)(e.options.dptSelect.map((e=>e.dpt)))):e.options.dptClasses&&a.push.apply(a,(0,r.A)(Object.values(t).filter((t=>e.options.dptClasses.includes(t.dpt_class))).map((e=>({main:e.main,sub:e.sub})))))})),a}var d=(0,n.A)(((e,t)=>l(e,t).reduce(((e,t)=>e.some((e=>{return r=t,(a=e).main===r.main&&a.sub===r.sub;var a,r}))?e:e.concat([t])),[]))),c=e=>null==e?"":e.main+(null!=e.sub?"."+e.sub.toString().padStart(3,"0"):""),p=e=>{if(!e)return null;var t=e.trim().split(".");if(0===t.length||t.length>2)return null;var a=Number.parseInt(t[0],10);if(Number.isNaN(a))return null;if(1===t.length)return{main:a,sub:null};var r=Number.parseInt(t[1],10);return Number.isNaN(r)?null:{main:a,sub:r}},u=(e,t)=>{var a,r;return e.main!==t.main?e.main-t.main:(null!==(a=e.sub)&&void 0!==a?a:-1)-(null!==(r=t.sub)&&void 0!==r?r:-1)},h=(e,t,a)=>{var r=a[c(e)];return!!r&&t.includes(r.dpt_class)}},29399:function(e,t,a){a.a(e,(async function(e,r){try{a.r(t),a.d(t,{KNXProjectView:function(){return F}});var i=a(61397),n=a(50264),o=a(44734),s=a(56038),l=a(75864),d=a(69683),c=a(6454),p=a(25460),u=(a(28706),a(2008),a(62062),a(44114),a(26910),a(18111),a(22489),a(61701),a(26099),a(16034),a(38781),a(68156),a(62826)),h=a(96196),g=a(77845),v=a(89302),f=a(22786),b=a(5871),x=a(54393),m=(a(84884),a(17963),a(95379),a(60733),a(53623)),_=(a(37445),a(77646)),y=(a(48680),a(87770)),w=a(19337),k=a(16404),A=a(65294),$=a(78577),M=a(25474),j=e([x,m,_]);[x,m,_]=j.then?(await j)():j;var z,H,C,q,R,V,Z,O,E,S,I,D,N,T,P,B=e=>e,W="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z",G=new $.Q("knx-project-view"),F=function(e){function t(){var e,a;(0,o.A)(this,t);for(var r=arguments.length,s=new Array(r),c=0;c<r;c++)s[c]=arguments[c];return(e=(0,d.A)(this,t,[].concat(s))).rangeSelectorHidden=!0,e._visibleGroupAddresses=[],e._groupRangeAvailable=!1,e._lastTelegrams={},e._projectLoadTask=new v.YZ((0,l.A)(e),{args:()=>[],task:(a=(0,n.A)((0,i.A)().m((function t(){return(0,i.A)().w((function(t){for(;;)switch(t.n){case 0:if(!e.knx.projectInfo||e.knx.projectData){t.n=1;break}return t.n=1,e.knx.loadProject();case 1:e._isGroupRangeAvailable();case 2:return t.a(2)}}),t)}))),function(){return a.apply(this,arguments)})}),e._columns=(0,f.A)(((t,a)=>({address:{filterable:!0,sortable:!0,title:e.knx.localize("project_view_table_address"),flex:1,minWidth:"100px",direction:"asc"},name:{filterable:!0,sortable:!0,title:e.knx.localize("project_view_table_name"),flex:3},dpt:{sortable:!0,filterable:!0,title:e.knx.localize("project_view_table_dpt"),flex:1,minWidth:"82px",template:e=>e.dpt?(0,h.qy)(z||(z=B`<span style="display:inline-block;width:24px;text-align:right;"
                  >${0}</span
                >${0} `),e.dpt.main,e.dpt.sub?"."+e.dpt.sub.toString().padStart(3,"0"):""):""},lastValue:{filterable:!0,title:e.knx.localize("project_view_table_last_value"),flex:2,template:t=>{var a=e._lastTelegrams[t.address];if(!a)return"";var r=M.e4.payload(a);return null==a.value?(0,h.qy)(H||(H=B`<code>${0}</code>`),r):(0,h.qy)(C||(C=B`<div title=${0}>
            ${0}
          </div>`),r,M.e4.valueWithUnit(e._lastTelegrams[t.address]))}},updated:{title:e.knx.localize("project_view_table_updated"),flex:1,showNarrow:!1,template:t=>{var a=e._lastTelegrams[t.address];if(!a)return"";var r=`${M.e4.dateWithMilliseconds(a)}\n\n${a.source} ${a.source_name}`;return(0,h.qy)(q||(q=B`<div title=${0}>
            ${0}
          </div>`),r,(0,_.K)(new Date(a.timestamp),e.hass.locale))}},actions:{title:"",minWidth:"72px",type:"overflow-menu",template:t=>e._groupAddressMenu(t)}}))),e._getRows=(0,f.A)(((e,t)=>e.length?e.map((e=>t[e])).filter((e=>!!e)).sort(((e,t)=>e.raw_address-t.raw_address)):Object.values(t))),e}return(0,c.A)(t,e),(0,s.A)(t,[{key:"disconnectedCallback",value:function(){(0,p.A)(t,"disconnectedCallback",this,3)([]),this._subscribed&&(this._subscribed(),this._subscribed=void 0)}},{key:"firstUpdated",value:(a=(0,n.A)((0,i.A)().m((function e(){return(0,i.A)().w((function(e){for(;;)switch(e.n){case 0:return(0,A.ke)(this.hass).then((e=>{this._lastTelegrams=e})).catch((e=>{G.error("getGroupTelegrams",e),(0,b.o)("/knx/error",{replace:!0,data:e})})),e.n=1,(0,A.EE)(this.hass,(e=>{this.telegram_callback(e)}));case 1:this._subscribed=e.v;case 2:return e.a(2)}}),e,this)}))),function(){return a.apply(this,arguments)})},{key:"_isGroupRangeAvailable",value:function(){var e,t,a=null!==(e=null===(t=this.knx.projectData)||void 0===t?void 0:t.info.xknxproject_version)&&void 0!==e?e:"0.0.0";G.debug("project version: "+a),this._groupRangeAvailable=(0,y.U)(a,"3.3.0",">=")}},{key:"telegram_callback",value:function(e){this._lastTelegrams=Object.assign(Object.assign({},this._lastTelegrams),{},{[e.destination]:e})}},{key:"_groupAddressMenu",value:function(e){var t=[];if(t.push({path:"M18 7C16.9 7 16 7.9 16 9V15C16 16.1 16.9 17 18 17H20C21.1 17 22 16.1 22 15V11H20V15H18V9H22V7H18M2 7V17H8V15H4V7H2M11 7C9.9 7 9 7.9 9 9V15C9 16.1 9.9 17 11 17H13C14.1 17 15 16.1 15 15V9C15 7.9 14.1 7 13 7H11M11 9H13V15H11V9Z",label:this.knx.localize("project_view_menu_view_telegrams"),action:()=>{(0,b.o)(`/knx/group_monitor?destination=${e.address}`)}}),e.dpt)if(1===e.dpt.main)t.push({path:W,label:this.knx.localize("project_view_menu_create_binary_sensor"),action:()=>{(0,b.o)("/knx/entities/create/binary_sensor?knx.ga_sensor.state="+e.address)}});else if((0,w.oJ)(e.dpt,["numeric","string"],this.knx.dptMetadata)){var a;t.push({path:W,label:null!==(a=this.knx.localize("project_view_menu_create_sensor"))&&void 0!==a?a:"Create Sensor",action:()=>{var t=e.dpt?`${e.dpt.main}${null!==e.dpt.sub?"."+e.dpt.sub.toString().padStart(3,"0"):""}`:"";(0,b.o)(`/knx/entities/create/sensor?knx.ga_sensor.state=${e.address}`+(t?`&knx.ga_sensor.dpt=${t}`:""))}})}return(0,h.qy)(R||(R=B`
      <ha-icon-overflow-menu .hass=${0} narrow .items=${0}> </ha-icon-overflow-menu>
    `),this.hass,t)}},{key:"_visibleAddressesChanged",value:function(e){this._visibleGroupAddresses=e.detail.groupAddresses}},{key:"render",value:function(){return this.hass?(0,h.qy)(Z||(Z=B` <hass-tabs-subpage
      .hass=${0}
      .narrow=${0}
      back-path=${0}
      .route=${0}
      .tabs=${0}
      .localizeFunc=${0}
    >
      ${0}
    </hass-tabs-subpage>`),this.hass,this.narrow,k.C1,this.route,[k.fR],this.knx.localize,this._projectLoadTask.render({initial:()=>(0,h.qy)(O||(O=B`
          <hass-loading-screen .message=${0}></hass-loading-screen>
        `),"Waiting to fetch project data."),pending:()=>(0,h.qy)(E||(E=B`
          <hass-loading-screen .message=${0}></hass-loading-screen>
        `),"Loading KNX project data."),error:e=>(G.error("Error loading KNX project",e),(0,h.qy)(S||(S=B`<ha-alert alert-type="error">"Error loading KNX project"</ha-alert>`))),complete:()=>this.renderMain()})):(0,h.qy)(V||(V=B` <hass-loading-screen></hass-loading-screen> `))}},{key:"renderMain",value:function(){var e=this._getRows(this._visibleGroupAddresses,this.knx.projectData.group_addresses);return this.knx.projectData?(0,h.qy)(I||(I=B`${0}
          <div class="sections">
            ${0}
            <ha-data-table
              class="ga-table"
              .hass=${0}
              .columns=${0}
              .data=${0}
              .hasFab=${0}
              .searchLabel=${0}
              .clickable=${0}
            ></ha-data-table>
          </div>`),this.narrow&&this._groupRangeAvailable?(0,h.qy)(D||(D=B`<ha-icon-button
                slot="toolbar-icon"
                .label=${0}
                .path=${0}
                @click=${0}
              ></ha-icon-button>`),this.hass.localize("ui.components.related-filter-menu.filter"),"M6,13H18V11H6M3,6V8H21V6M10,18H14V16H10V18Z",this._toggleRangeSelector):h.s6,this._groupRangeAvailable?(0,h.qy)(N||(N=B`
                  <knx-project-tree-view
                    .data=${0}
                    @knx-group-range-selection-changed=${0}
                  ></knx-project-tree-view>
                `),this.knx.projectData,this._visibleAddressesChanged):h.s6,this.hass,this._columns(this.narrow,this.hass.language),e,!1,this.hass.localize("ui.components.data-table.search"),!1):(0,h.qy)(T||(T=B` <ha-card .header=${0}>
          <div class="card-content">
            <p>${0}</p>
          </div>
        </ha-card>`),this.knx.localize("attention"),this.knx.localize("project_view_upload"))}},{key:"_toggleRangeSelector",value:function(){this.rangeSelectorHidden=!this.rangeSelectorHidden}}]);var a}(h.WF);F.styles=(0,h.AH)(P||(P=B`
    hass-loading-screen {
      --app-header-background-color: var(--sidebar-background-color);
      --app-header-text-color: var(--sidebar-text-color);
    }
    .sections {
      display: flex;
      flex-direction: row;
      height: 100%;
    }

    :host([narrow]) knx-project-tree-view {
      position: absolute;
      max-width: calc(100% - 60px); /* 100% -> max 871px before not narrow */
      z-index: 1;
      right: 0;
      transition: 0.5s;
      border-left: 1px solid var(--divider-color);
    }

    :host([narrow][range-selector-hidden]) knx-project-tree-view {
      width: 0;
    }

    :host(:not([narrow])) knx-project-tree-view {
      max-width: 255px; /* min 616px - 816px for tree-view + ga-table (depending on side menu) */
    }

    .ga-table {
      flex: 1;
    }
  `)),(0,u.__decorate)([(0,g.MZ)({type:Object})],F.prototype,"hass",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],F.prototype,"knx",void 0),(0,u.__decorate)([(0,g.MZ)({type:Boolean,reflect:!0})],F.prototype,"narrow",void 0),(0,u.__decorate)([(0,g.MZ)({type:Object})],F.prototype,"route",void 0),(0,u.__decorate)([(0,g.MZ)({type:Boolean,reflect:!0,attribute:"range-selector-hidden"})],F.prototype,"rangeSelectorHidden",void 0),(0,u.__decorate)([(0,g.wk)()],F.prototype,"_visibleGroupAddresses",void 0),(0,u.__decorate)([(0,g.wk)()],F.prototype,"_groupRangeAvailable",void 0),(0,u.__decorate)([(0,g.wk)()],F.prototype,"_subscribed",void 0),(0,u.__decorate)([(0,g.wk)()],F.prototype,"_lastTelegrams",void 0),F=(0,u.__decorate)([(0,g.EM)("knx-project-view")],F),r()}catch(U){r(U)}}))}}]);
//# sourceMappingURL=1535.8d0d56e409f1c4f2.js.map