"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2379"],{34811:function(e,t,i){i.d(t,{p:function(){return w}});var o,a,r,n,s=i(61397),d=i(50264),c=i(44734),l=i(56038),h=i(69683),u=i(6454),p=i(25460),m=(i(28706),i(62826)),v=i(96196),_=i(77845),f=i(94333),b=i(92542),y=i(99034),g=(i(60961),e=>e),w=function(e){function t(){var e;(0,c.A)(this,t);for(var i=arguments.length,o=new Array(i),a=0;a<i;a++)o[a]=arguments[a];return(e=(0,h.A)(this,t,[].concat(o))).expanded=!1,e.outlined=!1,e.leftChevron=!1,e.noCollapse=!1,e._showContent=e.expanded,e}return(0,u.A)(t,e),(0,l.A)(t,[{key:"render",value:function(){var e=this.noCollapse?v.s6:(0,v.qy)(o||(o=g`
          <ha-svg-icon
            .path=${0}
            class="summary-icon ${0}"
          ></ha-svg-icon>
        `),"M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z",(0,f.H)({expanded:this.expanded}));return(0,v.qy)(a||(a=g`
      <div class="top ${0}">
        <div
          id="summary"
          class=${0}
          @click=${0}
          @keydown=${0}
          @focus=${0}
          @blur=${0}
          role="button"
          tabindex=${0}
          aria-expanded=${0}
          aria-controls="sect1"
          part="summary"
        >
          ${0}
          <slot name="leading-icon"></slot>
          <slot name="header">
            <div class="header">
              ${0}
              <slot class="secondary" name="secondary">${0}</slot>
            </div>
          </slot>
          ${0}
          <slot name="icons"></slot>
        </div>
      </div>
      <div
        class="container ${0}"
        @transitionend=${0}
        role="region"
        aria-labelledby="summary"
        aria-hidden=${0}
        tabindex="-1"
      >
        ${0}
      </div>
    `),(0,f.H)({expanded:this.expanded}),(0,f.H)({noCollapse:this.noCollapse}),this._toggleContainer,this._toggleContainer,this._focusChanged,this._focusChanged,this.noCollapse?-1:0,this.expanded,this.leftChevron?e:v.s6,this.header,this.secondary,this.leftChevron?v.s6:e,(0,f.H)({expanded:this.expanded}),this._handleTransitionEnd,!this.expanded,this._showContent?(0,v.qy)(r||(r=g`<slot></slot>`)):"")}},{key:"willUpdate",value:function(e){(0,p.A)(t,"willUpdate",this,3)([e]),e.has("expanded")&&(this._showContent=this.expanded,setTimeout((()=>{this._container.style.overflow=this.expanded?"initial":"hidden"}),300))}},{key:"_handleTransitionEnd",value:function(){this._container.style.removeProperty("height"),this._container.style.overflow=this.expanded?"initial":"hidden",this._showContent=this.expanded}},{key:"_toggleContainer",value:(i=(0,d.A)((0,s.A)().m((function e(t){var i,o;return(0,s.A)().w((function(e){for(;;)switch(e.n){case 0:if(!t.defaultPrevented){e.n=1;break}return e.a(2);case 1:if("keydown"!==t.type||"Enter"===t.key||" "===t.key){e.n=2;break}return e.a(2);case 2:if(t.preventDefault(),!this.noCollapse){e.n=3;break}return e.a(2);case 3:if(i=!this.expanded,(0,b.r)(this,"expanded-will-change",{expanded:i}),this._container.style.overflow="hidden",!i){e.n=4;break}return this._showContent=!0,e.n=4,(0,y.E)();case 4:o=this._container.scrollHeight,this._container.style.height=`${o}px`,i||setTimeout((()=>{this._container.style.height="0px"}),0),this.expanded=i,(0,b.r)(this,"expanded-changed",{expanded:this.expanded});case 5:return e.a(2)}}),e,this)}))),function(e){return i.apply(this,arguments)})},{key:"_focusChanged",value:function(e){this.noCollapse||this.shadowRoot.querySelector(".top").classList.toggle("focused","focus"===e.type)}}]);var i}(v.WF);w.styles=(0,v.AH)(n||(n=g`
    :host {
      display: block;
    }

    .top {
      display: flex;
      align-items: center;
      border-radius: var(--ha-card-border-radius, var(--ha-border-radius-lg));
    }

    .top.expanded {
      border-bottom-left-radius: 0px;
      border-bottom-right-radius: 0px;
    }

    .top.focused {
      background: var(--input-fill-color);
    }

    :host([outlined]) {
      box-shadow: none;
      border-width: 1px;
      border-style: solid;
      border-color: var(--outline-color);
      border-radius: var(--ha-card-border-radius, var(--ha-border-radius-lg));
    }

    .summary-icon {
      transition: transform 150ms cubic-bezier(0.4, 0, 0.2, 1);
      direction: var(--direction);
      margin-left: 8px;
      margin-inline-start: 8px;
      margin-inline-end: initial;
      border-radius: var(--ha-border-radius-circle);
    }

    #summary:focus-visible ha-svg-icon.summary-icon {
      background-color: var(--ha-color-fill-neutral-normal-active);
    }

    :host([left-chevron]) .summary-icon,
    ::slotted([slot="leading-icon"]) {
      margin-left: 0;
      margin-right: 8px;
      margin-inline-start: 0;
      margin-inline-end: 8px;
    }

    #summary {
      flex: 1;
      display: flex;
      padding: var(--expansion-panel-summary-padding, 0 8px);
      min-height: 48px;
      align-items: center;
      cursor: pointer;
      overflow: hidden;
      font-weight: var(--ha-font-weight-medium);
      outline: none;
    }
    #summary.noCollapse {
      cursor: default;
    }

    .summary-icon.expanded {
      transform: rotate(180deg);
    }

    .header,
    ::slotted([slot="header"]) {
      flex: 1;
      overflow-wrap: anywhere;
      color: var(--primary-text-color);
    }

    .container {
      padding: var(--expansion-panel-content-padding, 0 8px);
      overflow: hidden;
      transition: height 300ms cubic-bezier(0.4, 0, 0.2, 1);
      height: 0px;
    }

    .container.expanded {
      height: auto;
    }

    .secondary {
      display: block;
      color: var(--secondary-text-color);
      font-size: var(--ha-font-size-s);
    }
  `)),(0,m.__decorate)([(0,_.MZ)({type:Boolean,reflect:!0})],w.prototype,"expanded",void 0),(0,m.__decorate)([(0,_.MZ)({type:Boolean,reflect:!0})],w.prototype,"outlined",void 0),(0,m.__decorate)([(0,_.MZ)({attribute:"left-chevron",type:Boolean,reflect:!0})],w.prototype,"leftChevron",void 0),(0,m.__decorate)([(0,_.MZ)({attribute:"no-collapse",type:Boolean,reflect:!0})],w.prototype,"noCollapse",void 0),(0,m.__decorate)([(0,_.MZ)()],w.prototype,"header",void 0),(0,m.__decorate)([(0,_.MZ)()],w.prototype,"secondary",void 0),(0,m.__decorate)([(0,_.wk)()],w.prototype,"_showContent",void 0),(0,m.__decorate)([(0,_.P)(".container")],w.prototype,"_container",void 0),w=(0,m.__decorate)([(0,_.EM)("ha-expansion-panel")],w)},7153:function(e,t,i){var o,a=i(44734),r=i(56038),n=i(69683),s=i(6454),d=i(25460),c=(i(28706),i(62826)),l=i(4845),h=i(49065),u=i(96196),p=i(77845),m=i(7647),v=function(e){function t(){var e;(0,a.A)(this,t);for(var i=arguments.length,o=new Array(i),r=0;r<i;r++)o[r]=arguments[r];return(e=(0,n.A)(this,t,[].concat(o))).haptic=!1,e}return(0,s.A)(t,e),(0,r.A)(t,[{key:"firstUpdated",value:function(){(0,d.A)(t,"firstUpdated",this,3)([]),this.addEventListener("change",(()=>{this.haptic&&(0,m.j)(this,"light")}))}}])}(l.U);v.styles=[h.R,(0,u.AH)(o||(o=(e=>e)`
      :host {
        --mdc-theme-secondary: var(--switch-checked-color);
      }
      .mdc-switch.mdc-switch--checked .mdc-switch__thumb {
        background-color: var(--switch-checked-button-color);
        border-color: var(--switch-checked-button-color);
      }
      .mdc-switch.mdc-switch--checked .mdc-switch__track {
        background-color: var(--switch-checked-track-color);
        border-color: var(--switch-checked-track-color);
      }
      .mdc-switch:not(.mdc-switch--checked) .mdc-switch__thumb {
        background-color: var(--switch-unchecked-button-color);
        border-color: var(--switch-unchecked-button-color);
      }
      .mdc-switch:not(.mdc-switch--checked) .mdc-switch__track {
        background-color: var(--switch-unchecked-track-color);
        border-color: var(--switch-unchecked-track-color);
      }
    `))],(0,c.__decorate)([(0,p.MZ)({type:Boolean})],v.prototype,"haptic",void 0),v=(0,c.__decorate)([(0,p.EM)("ha-switch")],v)},7647:function(e,t,i){i.d(t,{j:function(){return a}});var o=i(92542),a=(e,t)=>{(0,o.r)(e,"haptic",t)}},77238:function(e,t,i){i.a(e,(async function(e,o){try{i.r(t);var a=i(44734),r=i(56038),n=i(69683),s=i(6454),d=(i(28706),i(2892),i(62826)),c=i(96196),l=i(77845),h=i(92542),u=(i(34811),i(88867)),p=(i(7153),i(78740),i(39396)),m=e([u]);u=(m.then?(await m)():m)[0];var v,_,f=e=>e,b=function(e){function t(){var e;(0,a.A)(this,t);for(var i=arguments.length,o=new Array(i),r=0;r<i;r++)o[r]=arguments[r];return(e=(0,n.A)(this,t,[].concat(o))).new=!1,e.disabled=!1,e}return(0,s.A)(t,e),(0,r.A)(t,[{key:"item",set:function(e){var t,i,o,a,r;(this._item=e,e)?(this._name=e.name||"",this._icon=e.icon||"",this._maximum=null!==(t=e.maximum)&&void 0!==t?t:void 0,this._minimum=null!==(i=e.minimum)&&void 0!==i?i:void 0,this._restore=null===(o=e.restore)||void 0===o||o,this._step=null!==(a=e.step)&&void 0!==a?a:1,this._initial=null!==(r=e.initial)&&void 0!==r?r:0):(this._name="",this._icon="",this._maximum=void 0,this._minimum=void 0,this._restore=!0,this._step=1,this._initial=0)}},{key:"focus",value:function(){this.updateComplete.then((()=>{var e;return null===(e=this.shadowRoot)||void 0===e||null===(e=e.querySelector("[dialogInitialFocus]"))||void 0===e?void 0:e.focus()}))}},{key:"render",value:function(){return this.hass?(0,c.qy)(v||(v=f`
      <div class="form">
        <ha-textfield
          .value=${0}
          .configValue=${0}
          @input=${0}
          .label=${0}
          autoValidate
          required
          .validationMessage=${0}
          dialogInitialFocus
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
        <ha-textfield
          .value=${0}
          .configValue=${0}
          type="number"
          @input=${0}
          .label=${0}
          .disabled=${0}
        ></ha-textfield>
        <ha-textfield
          .value=${0}
          .configValue=${0}
          type="number"
          @input=${0}
          .label=${0}
          .disabled=${0}
        ></ha-textfield>
        <ha-textfield
          .value=${0}
          .configValue=${0}
          type="number"
          @input=${0}
          .label=${0}
          .disabled=${0}
        ></ha-textfield>
        <ha-expansion-panel
          header=${0}
          outlined
        >
          <ha-textfield
            .value=${0}
            .configValue=${0}
            type="number"
            @input=${0}
            .label=${0}
            .disabled=${0}
          ></ha-textfield>
          <div class="row">
            <ha-switch
              .checked=${0}
              .configValue=${0}
              @change=${0}
              .disabled=${0}
            >
            </ha-switch>
            <div>
              ${0}
            </div>
          </div>
        </ha-expansion-panel>
      </div>
    `),this._name,"name",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.name"),this.hass.localize("ui.dialogs.helper_settings.required_error_msg"),this.disabled,this.hass,this._icon,"icon",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.generic.icon"),this.disabled,this._minimum,"minimum",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.counter.minimum"),this.disabled,this._maximum,"maximum",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.counter.maximum"),this.disabled,this._initial,"initial",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.counter.initial"),this.disabled,this.hass.localize("ui.dialogs.helper_settings.generic.advanced_settings"),this._step,"step",this._valueChanged,this.hass.localize("ui.dialogs.helper_settings.counter.step"),this.disabled,this._restore,"restore",this._valueChanged,this.disabled,this.hass.localize("ui.dialogs.helper_settings.counter.restore")):c.s6}},{key:"_valueChanged",value:function(e){var t;if(this.new||this._item){e.stopPropagation();var i=e.target,o=i.configValue,a="number"===i.type?""!==i.value?Number(i.value):void 0:"ha-switch"===i.localName?e.target.checked:(null===(t=e.detail)||void 0===t?void 0:t.value)||i.value;if(this[`_${o}`]!==a){var r=Object.assign({},this._item);void 0===a||""===a?delete r[o]:r[o]=a,(0,h.r)(this,"value-changed",{value:r})}}}}],[{key:"styles",get:function(){return[p.RF,(0,c.AH)(_||(_=f`
        .form {
          color: var(--primary-text-color);
        }
        .row {
          margin-top: 12px;
          margin-bottom: 12px;
          color: var(--primary-text-color);
          display: flex;
          align-items: center;
        }
        .row div {
          margin-left: 16px;
          margin-inline-start: 16px;
          margin-inline-end: initial;
        }
        ha-textfield {
          display: block;
          margin: 8px 0;
        }
      `))]}}])}(c.WF);(0,d.__decorate)([(0,l.MZ)({attribute:!1})],b.prototype,"hass",void 0),(0,d.__decorate)([(0,l.MZ)({type:Boolean})],b.prototype,"new",void 0),(0,d.__decorate)([(0,l.MZ)({type:Boolean})],b.prototype,"disabled",void 0),(0,d.__decorate)([(0,l.wk)()],b.prototype,"_name",void 0),(0,d.__decorate)([(0,l.wk)()],b.prototype,"_icon",void 0),(0,d.__decorate)([(0,l.wk)()],b.prototype,"_maximum",void 0),(0,d.__decorate)([(0,l.wk)()],b.prototype,"_minimum",void 0),(0,d.__decorate)([(0,l.wk)()],b.prototype,"_restore",void 0),(0,d.__decorate)([(0,l.wk)()],b.prototype,"_initial",void 0),(0,d.__decorate)([(0,l.wk)()],b.prototype,"_step",void 0),b=(0,d.__decorate)([(0,l.EM)("ha-counter-form")],b),o()}catch(y){o(y)}}))},4845:function(e,t,i){i.d(t,{U:function(){return x}});var o,a,r=i(44734),n=i(56038),s=i(69683),d=i(6454),c=i(25460),l=i(62826),h=(i(27673),i(9270)),u=i(12451),p=i(56161),m=i(99864),v=i(7658),_={CHECKED:"mdc-switch--checked",DISABLED:"mdc-switch--disabled"},f={ARIA_CHECKED_ATTR:"aria-checked",NATIVE_CONTROL_SELECTOR:".mdc-switch__native-control",RIPPLE_SURFACE_SELECTOR:".mdc-switch__thumb-underlay"},b=function(e){function t(i){return e.call(this,(0,l.__assign)((0,l.__assign)({},t.defaultAdapter),i))||this}return(0,l.__extends)(t,e),Object.defineProperty(t,"strings",{get:function(){return f},enumerable:!1,configurable:!0}),Object.defineProperty(t,"cssClasses",{get:function(){return _},enumerable:!1,configurable:!0}),Object.defineProperty(t,"defaultAdapter",{get:function(){return{addClass:function(){},removeClass:function(){},setNativeControlChecked:function(){},setNativeControlDisabled:function(){},setNativeControlAttr:function(){}}},enumerable:!1,configurable:!0}),t.prototype.setChecked=function(e){this.adapter.setNativeControlChecked(e),this.updateAriaChecked(e),this.updateCheckedStyling(e)},t.prototype.setDisabled=function(e){this.adapter.setNativeControlDisabled(e),e?this.adapter.addClass(_.DISABLED):this.adapter.removeClass(_.DISABLED)},t.prototype.handleChange=function(e){var t=e.target;this.updateAriaChecked(t.checked),this.updateCheckedStyling(t.checked)},t.prototype.updateCheckedStyling=function(e){e?this.adapter.addClass(_.CHECKED):this.adapter.removeClass(_.CHECKED)},t.prototype.updateAriaChecked=function(e){this.adapter.setNativeControlAttr(f.ARIA_CHECKED_ATTR,""+!!e)},t}(v.I),y=i(96196),g=i(77845),w=i(32288),k=e=>e,x=function(e){function t(){var e;return(0,r.A)(this,t),(e=(0,s.A)(this,t,arguments)).checked=!1,e.disabled=!1,e.shouldRenderRipple=!1,e.mdcFoundationClass=b,e.rippleHandlers=new m.I((()=>(e.shouldRenderRipple=!0,e.ripple))),e}return(0,d.A)(t,e),(0,n.A)(t,[{key:"changeHandler",value:function(e){this.mdcFoundation.handleChange(e),this.checked=this.formElement.checked}},{key:"createAdapter",value:function(){return Object.assign(Object.assign({},(0,u.i)(this.mdcRoot)),{setNativeControlChecked:e=>{this.formElement.checked=e},setNativeControlDisabled:e=>{this.formElement.disabled=e},setNativeControlAttr:(e,t)=>{this.formElement.setAttribute(e,t)}})}},{key:"renderRipple",value:function(){return this.shouldRenderRipple?(0,y.qy)(o||(o=k`
        <mwc-ripple
          .accent="${0}"
          .disabled="${0}"
          unbounded>
        </mwc-ripple>`),this.checked,this.disabled):""}},{key:"focus",value:function(){var e=this.formElement;e&&(this.rippleHandlers.startFocus(),e.focus())}},{key:"blur",value:function(){var e=this.formElement;e&&(this.rippleHandlers.endFocus(),e.blur())}},{key:"click",value:function(){this.formElement&&!this.disabled&&(this.formElement.focus(),this.formElement.click())}},{key:"firstUpdated",value:function(){(0,c.A)(t,"firstUpdated",this,3)([]),this.shadowRoot&&this.mdcRoot.addEventListener("change",(e=>{this.dispatchEvent(new Event("change",e))}))}},{key:"render",value:function(){return(0,y.qy)(a||(a=k`
      <div class="mdc-switch">
        <div class="mdc-switch__track"></div>
        <div class="mdc-switch__thumb-underlay">
          ${0}
          <div class="mdc-switch__thumb">
            <input
              type="checkbox"
              id="basic-switch"
              class="mdc-switch__native-control"
              role="switch"
              aria-label="${0}"
              aria-labelledby="${0}"
              @change="${0}"
              @focus="${0}"
              @blur="${0}"
              @mousedown="${0}"
              @mouseenter="${0}"
              @mouseleave="${0}"
              @touchstart="${0}"
              @touchend="${0}"
              @touchcancel="${0}">
          </div>
        </div>
      </div>`),this.renderRipple(),(0,w.J)(this.ariaLabel),(0,w.J)(this.ariaLabelledBy),this.changeHandler,this.handleRippleFocus,this.handleRippleBlur,this.handleRippleMouseDown,this.handleRippleMouseEnter,this.handleRippleMouseLeave,this.handleRippleTouchStart,this.handleRippleDeactivate,this.handleRippleDeactivate)}},{key:"handleRippleMouseDown",value:function(e){var t=()=>{window.removeEventListener("mouseup",t),this.handleRippleDeactivate()};window.addEventListener("mouseup",t),this.rippleHandlers.startPress(e)}},{key:"handleRippleTouchStart",value:function(e){this.rippleHandlers.startPress(e)}},{key:"handleRippleDeactivate",value:function(){this.rippleHandlers.endPress()}},{key:"handleRippleMouseEnter",value:function(){this.rippleHandlers.startHover()}},{key:"handleRippleMouseLeave",value:function(){this.rippleHandlers.endHover()}},{key:"handleRippleFocus",value:function(){this.rippleHandlers.startFocus()}},{key:"handleRippleBlur",value:function(){this.rippleHandlers.endFocus()}}])}(u.O);(0,l.__decorate)([(0,g.MZ)({type:Boolean}),(0,p.P)((function(e){this.mdcFoundation.setChecked(e)}))],x.prototype,"checked",void 0),(0,l.__decorate)([(0,g.MZ)({type:Boolean}),(0,p.P)((function(e){this.mdcFoundation.setDisabled(e)}))],x.prototype,"disabled",void 0),(0,l.__decorate)([h.T,(0,g.MZ)({attribute:"aria-label"})],x.prototype,"ariaLabel",void 0),(0,l.__decorate)([h.T,(0,g.MZ)({attribute:"aria-labelledby"})],x.prototype,"ariaLabelledBy",void 0),(0,l.__decorate)([(0,g.P)(".mdc-switch")],x.prototype,"mdcRoot",void 0),(0,l.__decorate)([(0,g.P)("input")],x.prototype,"formElement",void 0),(0,l.__decorate)([(0,g.nJ)("mwc-ripple")],x.prototype,"ripple",void 0),(0,l.__decorate)([(0,g.wk)()],x.prototype,"shouldRenderRipple",void 0),(0,l.__decorate)([(0,g.Ls)({passive:!0})],x.prototype,"handleRippleMouseDown",null),(0,l.__decorate)([(0,g.Ls)({passive:!0})],x.prototype,"handleRippleTouchStart",null)},49065:function(e,t,i){i.d(t,{R:function(){return a}});var o,a=(0,i(96196).AH)(o||(o=(e=>e)`.mdc-switch__thumb-underlay{left:-14px;right:initial;top:-17px;width:48px;height:48px}[dir=rtl] .mdc-switch__thumb-underlay,.mdc-switch__thumb-underlay[dir=rtl]{left:initial;right:-14px}.mdc-switch__native-control{width:64px;height:48px}.mdc-switch{display:inline-block;position:relative;outline:none;user-select:none}.mdc-switch.mdc-switch--checked .mdc-switch__track{background-color:#018786;background-color:var(--mdc-theme-secondary, #018786)}.mdc-switch.mdc-switch--checked .mdc-switch__thumb{background-color:#018786;background-color:var(--mdc-theme-secondary, #018786);border-color:#018786;border-color:var(--mdc-theme-secondary, #018786)}.mdc-switch:not(.mdc-switch--checked) .mdc-switch__track{background-color:#000;background-color:var(--mdc-theme-on-surface, #000)}.mdc-switch:not(.mdc-switch--checked) .mdc-switch__thumb{background-color:#fff;background-color:var(--mdc-theme-surface, #fff);border-color:#fff;border-color:var(--mdc-theme-surface, #fff)}.mdc-switch__native-control{left:0;right:initial;position:absolute;top:0;margin:0;opacity:0;cursor:pointer;pointer-events:auto;transition:transform 90ms cubic-bezier(0.4, 0, 0.2, 1)}[dir=rtl] .mdc-switch__native-control,.mdc-switch__native-control[dir=rtl]{left:initial;right:0}.mdc-switch__track{box-sizing:border-box;width:36px;height:14px;border:1px solid transparent;border-radius:7px;opacity:.38;transition:opacity 90ms cubic-bezier(0.4, 0, 0.2, 1),background-color 90ms cubic-bezier(0.4, 0, 0.2, 1),border-color 90ms cubic-bezier(0.4, 0, 0.2, 1)}.mdc-switch__thumb-underlay{display:flex;position:absolute;align-items:center;justify-content:center;transform:translateX(0);transition:transform 90ms cubic-bezier(0.4, 0, 0.2, 1),background-color 90ms cubic-bezier(0.4, 0, 0.2, 1),border-color 90ms cubic-bezier(0.4, 0, 0.2, 1)}.mdc-switch__thumb{box-shadow:0px 3px 1px -2px rgba(0, 0, 0, 0.2),0px 2px 2px 0px rgba(0, 0, 0, 0.14),0px 1px 5px 0px rgba(0,0,0,.12);box-sizing:border-box;width:20px;height:20px;border:10px solid;border-radius:50%;pointer-events:none;z-index:1}.mdc-switch--checked .mdc-switch__track{opacity:.54}.mdc-switch--checked .mdc-switch__thumb-underlay{transform:translateX(16px)}[dir=rtl] .mdc-switch--checked .mdc-switch__thumb-underlay,.mdc-switch--checked .mdc-switch__thumb-underlay[dir=rtl]{transform:translateX(-16px)}.mdc-switch--checked .mdc-switch__native-control{transform:translateX(-16px)}[dir=rtl] .mdc-switch--checked .mdc-switch__native-control,.mdc-switch--checked .mdc-switch__native-control[dir=rtl]{transform:translateX(16px)}.mdc-switch--disabled{opacity:.38;pointer-events:none}.mdc-switch--disabled .mdc-switch__thumb{border-width:1px}.mdc-switch--disabled .mdc-switch__native-control{cursor:default;pointer-events:none}:host{display:inline-flex;outline:none;-webkit-tap-highlight-color:transparent}`))}}]);
//# sourceMappingURL=2379.752a6e66b0404b78.js.map