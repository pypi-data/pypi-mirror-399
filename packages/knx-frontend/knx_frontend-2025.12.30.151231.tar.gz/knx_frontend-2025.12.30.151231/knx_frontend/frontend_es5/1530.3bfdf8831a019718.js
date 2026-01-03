"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["1530"],{89473:function(t,e,a){a.a(t,(async function(t,e){try{var o=a(44734),i=a(56038),r=a(69683),l=a(6454),n=(a(28706),a(62826)),d=a(88496),s=a(96196),c=a(77845),h=t([d]);d=(h.then?(await h)():h)[0];var p,f=t=>t,v=function(t){function e(){var t;(0,o.A)(this,e);for(var a=arguments.length,i=new Array(a),l=0;l<a;l++)i[l]=arguments[l];return(t=(0,r.A)(this,e,[].concat(i))).variant="brand",t}return(0,l.A)(e,t),(0,i.A)(e,null,[{key:"styles",get:function(){return[d.A.styles,(0,s.AH)(p||(p=f`
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
      `))]}}])}(d.A);v=(0,n.__decorate)([(0,c.EM)("ha-button")],v),e()}catch(u){e(u)}}))},5841:function(t,e,a){var o,i,r=a(44734),l=a(56038),n=a(69683),d=a(6454),s=a(62826),c=a(96196),h=a(77845),p=t=>t,f=function(t){function e(){return(0,r.A)(this,e),(0,n.A)(this,e,arguments)}return(0,d.A)(e,t),(0,l.A)(e,[{key:"render",value:function(){return(0,c.qy)(o||(o=p`
      <footer>
        <slot name="secondaryAction"></slot>
        <slot name="primaryAction"></slot>
      </footer>
    `))}}],[{key:"styles",get:function(){return[(0,c.AH)(i||(i=p`
        footer {
          display: flex;
          gap: var(--ha-space-3);
          justify-content: flex-end;
          align-items: center;
          width: 100%;
        }
      `))]}}])}(c.WF);f=(0,s.__decorate)([(0,h.EM)("ha-dialog-footer")],f)},86451:function(t,e,a){var o,i,r,l,n,d,s=a(44734),c=a(56038),h=a(69683),p=a(6454),f=(a(28706),a(62826)),v=a(96196),u=a(77845),g=t=>t,m=function(t){function e(){var t;(0,s.A)(this,e);for(var a=arguments.length,o=new Array(a),i=0;i<a;i++)o[i]=arguments[i];return(t=(0,h.A)(this,e,[].concat(o))).subtitlePosition="below",t.showBorder=!1,t}return(0,p.A)(e,t),(0,c.A)(e,[{key:"render",value:function(){var t=(0,v.qy)(o||(o=g`<div class="header-title">
      <slot name="title"></slot>
    </div>`)),e=(0,v.qy)(i||(i=g`<div class="header-subtitle">
      <slot name="subtitle"></slot>
    </div>`));return(0,v.qy)(r||(r=g`
      <header class="header">
        <div class="header-bar">
          <section class="header-navigation-icon">
            <slot name="navigationIcon"></slot>
          </section>
          <section class="header-content">
            ${0}
          </section>
          <section class="header-action-items">
            <slot name="actionItems"></slot>
          </section>
        </div>
        <slot></slot>
      </header>
    `),"above"===this.subtitlePosition?(0,v.qy)(l||(l=g`${0}${0}`),e,t):(0,v.qy)(n||(n=g`${0}${0}`),t,e))}}],[{key:"styles",get:function(){return[(0,v.AH)(d||(d=g`
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
      `))]}}])}(v.WF);(0,f.__decorate)([(0,u.MZ)({type:String,attribute:"subtitle-position"})],m.prototype,"subtitlePosition",void 0),(0,f.__decorate)([(0,u.MZ)({type:Boolean,reflect:!0,attribute:"show-border"})],m.prototype,"showBorder",void 0),m=(0,f.__decorate)([(0,u.EM)("ha-dialog-header")],m)},78740:function(t,e,a){a.d(e,{h:function(){return x}});var o,i,r,l,n=a(44734),d=a(56038),s=a(69683),c=a(6454),h=a(25460),p=(a(28706),a(62826)),f=a(68846),v=a(92347),u=a(96196),g=a(77845),m=a(76679),b=t=>t,x=function(t){function e(){var t;(0,n.A)(this,e);for(var a=arguments.length,o=new Array(a),i=0;i<a;i++)o[i]=arguments[i];return(t=(0,s.A)(this,e,[].concat(o))).icon=!1,t.iconTrailing=!1,t.autocorrect=!0,t}return(0,c.A)(e,t),(0,d.A)(e,[{key:"updated",value:function(t){(0,h.A)(e,"updated",this,3)([t]),(t.has("invalid")||t.has("errorMessage"))&&(this.setCustomValidity(this.invalid?this.errorMessage||this.validationMessage||"Invalid":""),(this.invalid||this.validateOnInitialRender||t.has("invalid")&&void 0!==t.get("invalid"))&&this.reportValidity()),t.has("autocomplete")&&(this.autocomplete?this.formElement.setAttribute("autocomplete",this.autocomplete):this.formElement.removeAttribute("autocomplete")),t.has("autocorrect")&&(!1===this.autocorrect?this.formElement.setAttribute("autocorrect","off"):this.formElement.removeAttribute("autocorrect")),t.has("inputSpellcheck")&&(this.inputSpellcheck?this.formElement.setAttribute("spellcheck",this.inputSpellcheck):this.formElement.removeAttribute("spellcheck"))}},{key:"renderIcon",value:function(t){var e=arguments.length>1&&void 0!==arguments[1]&&arguments[1],a=e?"trailing":"leading";return(0,u.qy)(o||(o=b`
      <span
        class="mdc-text-field__icon mdc-text-field__icon--${0}"
        tabindex=${0}
      >
        <slot name="${0}Icon"></slot>
      </span>
    `),a,e?1:-1,a)}}])}(f.J);x.styles=[v.R,(0,u.AH)(i||(i=b`
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
    `)),"rtl"===m.G.document.dir?(0,u.AH)(r||(r=b`
          .mdc-text-field--with-leading-icon,
          .mdc-text-field__icon--leading,
          .mdc-floating-label,
          .mdc-text-field--with-leading-icon.mdc-text-field--filled
            .mdc-floating-label,
          .mdc-text-field__input[type="number"] {
            direction: rtl;
            --direction: rtl;
          }
        `)):(0,u.AH)(l||(l=b``))],(0,p.__decorate)([(0,g.MZ)({type:Boolean})],x.prototype,"invalid",void 0),(0,p.__decorate)([(0,g.MZ)({attribute:"error-message"})],x.prototype,"errorMessage",void 0),(0,p.__decorate)([(0,g.MZ)({type:Boolean})],x.prototype,"icon",void 0),(0,p.__decorate)([(0,g.MZ)({type:Boolean})],x.prototype,"iconTrailing",void 0),(0,p.__decorate)([(0,g.MZ)()],x.prototype,"autocomplete",void 0),(0,p.__decorate)([(0,g.MZ)({type:Boolean})],x.prototype,"autocorrect",void 0),(0,p.__decorate)([(0,g.MZ)({attribute:"input-spellcheck"})],x.prototype,"inputSpellcheck",void 0),(0,p.__decorate)([(0,g.P)("input")],x.prototype,"formElement",void 0),x=(0,p.__decorate)([(0,g.EM)("ha-textfield")],x)},36626:function(t,e,a){a.a(t,(async function(t,e){try{var o=a(61397),i=a(50264),r=a(44734),l=a(56038),n=a(75864),d=a(69683),s=a(6454),c=a(25460),h=(a(28706),a(62826)),p=a(93900),f=a(96196),v=a(77845),u=a(32288),g=a(92542),m=a(39396),b=(a(86451),a(60733),t([p]));p=(b.then?(await b)():b)[0];var x,_,w,y,k,A,$=t=>t,M=function(t){function e(){var t;(0,r.A)(this,e);for(var a=arguments.length,l=new Array(a),s=0;s<a;s++)l[s]=arguments[s];return(t=(0,d.A)(this,e,[].concat(l))).open=!1,t.type="standard",t.width="medium",t.preventScrimClose=!1,t.headerSubtitlePosition="below",t.flexContent=!1,t._open=!1,t._bodyScrolled=!1,t._handleShow=(0,i.A)((0,o.A)().m((function e(){return(0,o.A)().w((function(e){for(;;)switch(e.n){case 0:return t._open=!0,(0,g.r)((0,n.A)(t),"opened"),e.n=1,t.updateComplete;case 1:requestAnimationFrame((()=>{var e;null===(e=t.querySelector("[autofocus]"))||void 0===e||e.focus()}));case 2:return e.a(2)}}),e)}))),t._handleAfterShow=()=>{(0,g.r)((0,n.A)(t),"after-show")},t._handleAfterHide=()=>{t._open=!1,(0,g.r)((0,n.A)(t),"closed")},t}return(0,s.A)(e,t),(0,l.A)(e,[{key:"updated",value:function(t){(0,c.A)(e,"updated",this,3)([t]),t.has("open")&&(this._open=this.open)}},{key:"render",value:function(){var t,e;return(0,f.qy)(x||(x=$`
      <wa-dialog
        .open=${0}
        .lightDismiss=${0}
        without-header
        aria-labelledby=${0}
        aria-describedby=${0}
        @wa-show=${0}
        @wa-after-show=${0}
        @wa-after-hide=${0}
      >
        <slot name="header">
          <ha-dialog-header
            .subtitlePosition=${0}
            .showBorder=${0}
          >
            <slot name="headerNavigationIcon" slot="navigationIcon">
              <ha-icon-button
                data-dialog="close"
                .label=${0}
                .path=${0}
              ></ha-icon-button>
            </slot>
            ${0}
            ${0}
            <slot name="headerActionItems" slot="actionItems"></slot>
          </ha-dialog-header>
        </slot>
        <div class="body ha-scrollbar" @scroll=${0}>
          <slot></slot>
        </div>
        <slot name="footer" slot="footer"></slot>
      </wa-dialog>
    `),this._open,!this.preventScrimClose,(0,u.J)(this.ariaLabelledBy||(void 0!==this.headerTitle?"ha-wa-dialog-title":void 0)),(0,u.J)(this.ariaDescribedBy),this._handleShow,this._handleAfterShow,this._handleAfterHide,this.headerSubtitlePosition,this._bodyScrolled,null!==(t=null===(e=this.hass)||void 0===e?void 0:e.localize("ui.common.close"))&&void 0!==t?t:"Close","M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",void 0!==this.headerTitle?(0,f.qy)(_||(_=$`<span slot="title" class="title" id="ha-wa-dialog-title">
                  ${0}
                </span>`),this.headerTitle):(0,f.qy)(w||(w=$`<slot name="headerTitle" slot="title"></slot>`)),void 0!==this.headerSubtitle?(0,f.qy)(y||(y=$`<span slot="subtitle">${0}</span>`),this.headerSubtitle):(0,f.qy)(k||(k=$`<slot name="headerSubtitle" slot="subtitle"></slot>`)),this._handleBodyScroll)}},{key:"disconnectedCallback",value:function(){(0,c.A)(e,"disconnectedCallback",this,3)([]),this._open=!1}},{key:"_handleBodyScroll",value:function(t){this._bodyScrolled=t.target.scrollTop>0}}])}(f.WF);M.styles=[m.dp,(0,f.AH)(A||(A=$`
      wa-dialog {
        --full-width: var(--ha-dialog-width-full, min(95vw, var(--safe-width)));
        --width: min(var(--ha-dialog-width-md, 580px), var(--full-width));
        --spacing: var(--dialog-content-padding, var(--ha-space-6));
        --show-duration: var(--ha-dialog-show-duration, 200ms);
        --hide-duration: var(--ha-dialog-hide-duration, 200ms);
        --ha-dialog-surface-background: var(
          --card-background-color,
          var(--ha-color-surface-default)
        );
        --wa-color-surface-raised: var(
          --ha-dialog-surface-background,
          var(--card-background-color, var(--ha-color-surface-default))
        );
        --wa-panel-border-radius: var(
          --ha-dialog-border-radius,
          var(--ha-border-radius-3xl)
        );
        max-width: var(--ha-dialog-max-width, var(--safe-width));
      }

      :host([width="small"]) wa-dialog {
        --width: min(var(--ha-dialog-width-sm, 320px), var(--full-width));
      }

      :host([width="large"]) wa-dialog {
        --width: min(var(--ha-dialog-width-lg, 1024px), var(--full-width));
      }

      :host([width="full"]) wa-dialog {
        --width: var(--full-width);
      }

      wa-dialog::part(dialog) {
        min-width: var(--width, var(--full-width));
        max-width: var(--width, var(--full-width));
        max-height: var(
          --ha-dialog-max-height,
          calc(var(--safe-height) - var(--ha-space-20))
        );
        min-height: var(--ha-dialog-min-height);
        margin-top: var(--dialog-surface-margin-top, auto);
        /* Used to offset the dialog from the safe areas when space is limited */
        transform: translate(
          calc(
            var(--safe-area-offset-left, var(--ha-space-0)) - var(
                --safe-area-offset-right,
                var(--ha-space-0)
              )
          ),
          calc(
            var(--safe-area-offset-top, var(--ha-space-0)) - var(
                --safe-area-offset-bottom,
                var(--ha-space-0)
              )
          )
        );
        display: flex;
        flex-direction: column;
        overflow: hidden;
      }

      @media all and (max-width: 450px), all and (max-height: 500px) {
        :host([type="standard"]) {
          --ha-dialog-border-radius: var(--ha-space-0);

          wa-dialog {
            /* Make the container fill the whole screen width and not the safe width */
            --full-width: var(--ha-dialog-width-full, 100vw);
            --width: var(--full-width);
          }

          wa-dialog::part(dialog) {
            /* Make the dialog fill the whole screen height and not the safe height */
            min-height: var(--ha-dialog-min-height, 100vh);
            min-height: var(--ha-dialog-min-height, 100dvh);
            max-height: var(--ha-dialog-max-height, 100vh);
            max-height: var(--ha-dialog-max-height, 100dvh);
            margin-top: 0;
            margin-bottom: 0;
            /* Use safe area as padding instead of the container size */
            padding-top: var(--safe-area-inset-top);
            padding-bottom: var(--safe-area-inset-bottom);
            padding-left: var(--safe-area-inset-left);
            padding-right: var(--safe-area-inset-right);
            /* Reset the transform to center the dialog */
            transform: none;
          }
        }
      }

      .header-title-container {
        display: flex;
        align-items: center;
      }

      .header-title {
        margin: 0;
        margin-bottom: 0;
        color: var(--ha-dialog-header-title-color, var(--primary-text-color));
        font-size: var(
          --ha-dialog-header-title-font-size,
          var(--ha-font-size-2xl)
        );
        line-height: var(
          --ha-dialog-header-title-line-height,
          var(--ha-line-height-condensed)
        );
        font-weight: var(
          --ha-dialog-header-title-font-weight,
          var(--ha-font-weight-normal)
        );
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        margin-right: var(--ha-space-3);
      }

      wa-dialog::part(body) {
        padding: 0;
        display: flex;
        flex-direction: column;
        max-width: 100%;
        overflow: hidden;
      }

      .body {
        position: var(--dialog-content-position, relative);
        padding: 0 var(--dialog-content-padding, var(--ha-space-6))
          var(--dialog-content-padding, var(--ha-space-6))
          var(--dialog-content-padding, var(--ha-space-6));
        overflow: auto;
        flex-grow: 1;
      }
      :host([flexcontent]) .body {
        max-width: 100%;
        flex: 1;
        display: flex;
        flex-direction: column;
      }

      wa-dialog::part(footer) {
        padding: var(--ha-space-0);
      }

      ::slotted([slot="footer"]) {
        display: flex;
        padding: var(--ha-space-3) var(--ha-space-4) var(--ha-space-4)
          var(--ha-space-4);
        gap: var(--ha-space-3);
        justify-content: flex-end;
        align-items: center;
        width: 100%;
      }
    `))],(0,h.__decorate)([(0,v.MZ)({attribute:!1})],M.prototype,"hass",void 0),(0,h.__decorate)([(0,v.MZ)({attribute:"aria-labelledby"})],M.prototype,"ariaLabelledBy",void 0),(0,h.__decorate)([(0,v.MZ)({attribute:"aria-describedby"})],M.prototype,"ariaDescribedBy",void 0),(0,h.__decorate)([(0,v.MZ)({type:Boolean,reflect:!0})],M.prototype,"open",void 0),(0,h.__decorate)([(0,v.MZ)({reflect:!0})],M.prototype,"type",void 0),(0,h.__decorate)([(0,v.MZ)({type:String,reflect:!0,attribute:"width"})],M.prototype,"width",void 0),(0,h.__decorate)([(0,v.MZ)({type:Boolean,reflect:!0,attribute:"prevent-scrim-close"})],M.prototype,"preventScrimClose",void 0),(0,h.__decorate)([(0,v.MZ)({attribute:"header-title"})],M.prototype,"headerTitle",void 0),(0,h.__decorate)([(0,v.MZ)({attribute:"header-subtitle"})],M.prototype,"headerSubtitle",void 0),(0,h.__decorate)([(0,v.MZ)({type:String,attribute:"header-subtitle-position"})],M.prototype,"headerSubtitlePosition",void 0),(0,h.__decorate)([(0,v.MZ)({type:Boolean,reflect:!0,attribute:"flexcontent"})],M.prototype,"flexContent",void 0),(0,h.__decorate)([(0,v.wk)()],M.prototype,"_open",void 0),(0,h.__decorate)([(0,v.P)(".body")],M.prototype,"bodyContainer",void 0),(0,h.__decorate)([(0,v.wk)()],M.prototype,"_bodyScrolled",void 0),(0,h.__decorate)([(0,v.Ls)({passive:!0})],M.prototype,"_handleBodyScroll",null),M=(0,h.__decorate)([(0,v.EM)("ha-wa-dialog")],M),e()}catch(S){e(S)}}))},22316:function(t,e,a){a.a(t,(async function(t,o){try{a.r(e);var i=a(61397),r=a(50264),l=a(44734),n=a(56038),d=a(69683),s=a(6454),c=(a(28706),a(26099),a(3362),a(62826)),h=a(96196),p=a(77845),f=a(94333),v=a(32288),u=a(92542),g=a(89473),m=(a(5841),a(86451),a(60961),a(78740),a(36626)),b=t([g,m]);[g,m]=b.then?(await b)():b;var x,_,w,y,k,A,$,M=t=>t,S=function(t){function e(){var t;(0,l.A)(this,e);for(var a=arguments.length,o=new Array(a),i=0;i<a;i++)o[i]=arguments[i];return(t=(0,d.A)(this,e,[].concat(o)))._open=!1,t}return(0,s.A)(e,t),(0,n.A)(e,[{key:"showDialog",value:(a=(0,r.A)((0,i.A)().m((function t(e){return(0,i.A)().w((function(t){for(;;)switch(t.n){case 0:if(!this._closePromise){t.n=1;break}return t.n=1,this._closePromise;case 1:this._params=e,this._open=!0;case 2:return t.a(2)}}),t,this)}))),function(t){return a.apply(this,arguments)})},{key:"closeDialog",value:function(){var t,e;return!(null!==(t=this._params)&&void 0!==t&&t.confirmation||null!==(e=this._params)&&void 0!==e&&e.prompt)&&(!this._params||(this._dismiss(),!0))}},{key:"render",value:function(){var t,e;if(!this._params)return h.s6;var a=this._params.confirmation||!!this._params.prompt,o=this._params.title||this._params.confirmation&&this.hass.localize("ui.dialogs.generic.default_confirmation_title");return(0,h.qy)(x||(x=M`
      <ha-wa-dialog
        .hass=${0}
        .open=${0}
        type=${0}
        ?prevent-scrim-close=${0}
        @closed=${0}
        aria-labelledby="dialog-box-title"
        aria-describedby="dialog-box-description"
      >
        <ha-dialog-header slot="header">
          ${0}
          <span
            class=${0}
            slot="title"
            id="dialog-box-title"
          >
            ${0}
            ${0}
          </span>
        </ha-dialog-header>
        <div id="dialog-box-description">
          ${0}
          ${0}
        </div>
        <ha-dialog-footer slot="footer">
          ${0}
          <ha-button
            slot="primaryAction"
            @click=${0}
            ?autofocus=${0}
            variant=${0}
          >
            ${0}
          </ha-button>
        </ha-dialog-footer>
      </ha-wa-dialog>
    `),this.hass,this._open,a?"alert":"standard",a,this._dialogClosed,a?h.s6:(0,h.qy)(_||(_=M`<slot name="headerNavigationIcon" slot="navigationIcon">
                <ha-icon-button
                  data-dialog="close"
                  .label=${0}
                  .path=${0}
                ></ha-icon-button
              ></slot>`),null!==(t=null===(e=this.hass)||void 0===e?void 0:e.localize("ui.common.close"))&&void 0!==t?t:"Close","M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"),(0,f.H)({title:!0,alert:a}),this._params.warning?(0,h.qy)(w||(w=M`<ha-svg-icon
                  .path=${0}
                  style="color: var(--warning-color)"
                ></ha-svg-icon> `),"M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16"):h.s6,o,this._params.text?(0,h.qy)(y||(y=M` <p>${0}</p> `),this._params.text):"",this._params.prompt?(0,h.qy)(k||(k=M`
                <ha-textfield
                  autofocus
                  value=${0}
                  .placeholder=${0}
                  .label=${0}
                  .type=${0}
                  .min=${0}
                  .max=${0}
                ></ha-textfield>
              `),(0,v.J)(this._params.defaultValue),this._params.placeholder,this._params.inputLabel?this._params.inputLabel:"",this._params.inputType?this._params.inputType:"text",this._params.inputMin,this._params.inputMax):"",a?(0,h.qy)(A||(A=M`
                <ha-button
                  slot="secondaryAction"
                  @click=${0}
                  ?autofocus=${0}
                  appearance="plain"
                >
                  ${0}
                </ha-button>
              `),this._dismiss,!this._params.prompt&&this._params.destructive,this._params.dismissText?this._params.dismissText:this.hass.localize("ui.common.cancel")):h.s6,this._confirm,!this._params.prompt&&!this._params.destructive,this._params.destructive?"danger":"brand",this._params.confirmText?this._params.confirmText:this.hass.localize("ui.common.ok"))}},{key:"_cancel",value:function(){var t;null!==(t=this._params)&&void 0!==t&&t.cancel&&this._params.cancel()}},{key:"_dismiss",value:function(){this._closeState="canceled",this._cancel(),this._closeDialog()}},{key:"_confirm",value:function(){var t;(this._closeState="confirmed",this._params.confirm)&&this._params.confirm(null===(t=this._textField)||void 0===t?void 0:t.value);this._closeDialog()}},{key:"_closeDialog",value:function(){this._open=!1,this._closePromise=new Promise((t=>{this._closeResolve=t}))}},{key:"_dialogClosed",value:function(){var t;(0,u.r)(this,"dialog-closed",{dialog:this.localName}),this._closeState||this._cancel(),this._closeState=void 0,this._params=void 0,this._open=!1,null===(t=this._closeResolve)||void 0===t||t.call(this),this._closeResolve=void 0}}]);var a}(h.WF);S.styles=(0,h.AH)($||($=M`
    :host([inert]) {
      pointer-events: initial !important;
      cursor: initial !important;
    }
    a {
      color: var(--primary-color);
    }
    p {
      margin: 0;
      color: var(--primary-text-color);
    }
    .no-bottom-padding {
      padding-bottom: 0;
    }
    .secondary {
      color: var(--secondary-text-color);
    }
    ha-textfield {
      width: 100%;
    }
    .title.alert {
      padding: 0 var(--ha-space-2);
    }
    @media all and (min-width: 450px) and (min-height: 500px) {
      .title.alert {
        padding: 0 var(--ha-space-1);
      }
    }
  `)),(0,c.__decorate)([(0,p.MZ)({attribute:!1})],S.prototype,"hass",void 0),(0,c.__decorate)([(0,p.wk)()],S.prototype,"_params",void 0),(0,c.__decorate)([(0,p.wk)()],S.prototype,"_open",void 0),(0,c.__decorate)([(0,p.wk)()],S.prototype,"_closeState",void 0),(0,c.__decorate)([(0,p.P)("ha-textfield")],S.prototype,"_textField",void 0),S=(0,c.__decorate)([(0,p.EM)("dialog-box")],S),o()}catch(L){o(L)}}))}}]);
//# sourceMappingURL=1530.3bfdf8831a019718.js.map