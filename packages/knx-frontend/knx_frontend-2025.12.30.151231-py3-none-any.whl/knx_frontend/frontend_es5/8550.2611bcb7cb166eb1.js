"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["8550"],{34811:function(e,t,a){a.d(t,{p:function(){return _}});var o,n,i,r,s=a(61397),d=a(50264),l=a(44734),c=a(56038),h=a(69683),p=a(6454),u=a(25460),v=(a(28706),a(62826)),m=a(96196),y=a(77845),f=a(94333),b=a(92542),x=a(99034),g=(a(60961),e=>e),_=function(e){function t(){var e;(0,l.A)(this,t);for(var a=arguments.length,o=new Array(a),n=0;n<a;n++)o[n]=arguments[n];return(e=(0,h.A)(this,t,[].concat(o))).expanded=!1,e.outlined=!1,e.leftChevron=!1,e.noCollapse=!1,e._showContent=e.expanded,e}return(0,p.A)(t,e),(0,c.A)(t,[{key:"render",value:function(){var e=this.noCollapse?m.s6:(0,m.qy)(o||(o=g`
          <ha-svg-icon
            .path=${0}
            class="summary-icon ${0}"
          ></ha-svg-icon>
        `),"M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z",(0,f.H)({expanded:this.expanded}));return(0,m.qy)(n||(n=g`
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
    `),(0,f.H)({expanded:this.expanded}),(0,f.H)({noCollapse:this.noCollapse}),this._toggleContainer,this._toggleContainer,this._focusChanged,this._focusChanged,this.noCollapse?-1:0,this.expanded,this.leftChevron?e:m.s6,this.header,this.secondary,this.leftChevron?m.s6:e,(0,f.H)({expanded:this.expanded}),this._handleTransitionEnd,!this.expanded,this._showContent?(0,m.qy)(i||(i=g`<slot></slot>`)):"")}},{key:"willUpdate",value:function(e){(0,u.A)(t,"willUpdate",this,3)([e]),e.has("expanded")&&(this._showContent=this.expanded,setTimeout((()=>{this._container.style.overflow=this.expanded?"initial":"hidden"}),300))}},{key:"_handleTransitionEnd",value:function(){this._container.style.removeProperty("height"),this._container.style.overflow=this.expanded?"initial":"hidden",this._showContent=this.expanded}},{key:"_toggleContainer",value:(a=(0,d.A)((0,s.A)().m((function e(t){var a,o;return(0,s.A)().w((function(e){for(;;)switch(e.n){case 0:if(!t.defaultPrevented){e.n=1;break}return e.a(2);case 1:if("keydown"!==t.type||"Enter"===t.key||" "===t.key){e.n=2;break}return e.a(2);case 2:if(t.preventDefault(),!this.noCollapse){e.n=3;break}return e.a(2);case 3:if(a=!this.expanded,(0,b.r)(this,"expanded-will-change",{expanded:a}),this._container.style.overflow="hidden",!a){e.n=4;break}return this._showContent=!0,e.n=4,(0,x.E)();case 4:o=this._container.scrollHeight,this._container.style.height=`${o}px`,a||setTimeout((()=>{this._container.style.height="0px"}),0),this.expanded=a,(0,b.r)(this,"expanded-changed",{expanded:this.expanded});case 5:return e.a(2)}}),e,this)}))),function(e){return a.apply(this,arguments)})},{key:"_focusChanged",value:function(e){this.noCollapse||this.shadowRoot.querySelector(".top").classList.toggle("focused","focus"===e.type)}}]);var a}(m.WF);_.styles=(0,m.AH)(r||(r=g`
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
  `)),(0,v.__decorate)([(0,y.MZ)({type:Boolean,reflect:!0})],_.prototype,"expanded",void 0),(0,v.__decorate)([(0,y.MZ)({type:Boolean,reflect:!0})],_.prototype,"outlined",void 0),(0,v.__decorate)([(0,y.MZ)({attribute:"left-chevron",type:Boolean,reflect:!0})],_.prototype,"leftChevron",void 0),(0,v.__decorate)([(0,y.MZ)({attribute:"no-collapse",type:Boolean,reflect:!0})],_.prototype,"noCollapse",void 0),(0,v.__decorate)([(0,y.MZ)()],_.prototype,"header",void 0),(0,v.__decorate)([(0,y.MZ)()],_.prototype,"secondary",void 0),(0,v.__decorate)([(0,y.wk)()],_.prototype,"_showContent",void 0),(0,v.__decorate)([(0,y.P)(".container")],_.prototype,"_container",void 0),_=(0,v.__decorate)([(0,y.EM)("ha-expansion-panel")],_)},29989:function(e,t,a){a.r(t),a.d(t,{HaFormExpandable:function(){return f}});var o,n,i,r,s,d=a(94741),l=a(44734),c=a(56038),h=a(69683),p=a(6454),u=(a(28706),a(26099),a(38781),a(62826)),v=a(96196),m=a(77845),y=(a(91120),a(34811),e=>e),f=function(e){function t(){var e;(0,l.A)(this,t);for(var a=arguments.length,o=new Array(a),n=0;n<a;n++)o[n]=arguments[n];return(e=(0,h.A)(this,t,[].concat(o))).disabled=!1,e._computeLabel=(t,a,o)=>e.computeLabel?e.computeLabel(t,a,Object.assign(Object.assign({},o),{},{path:[].concat((0,d.A)((null==o?void 0:o.path)||[]),[e.schema.name])})):e.computeLabel,e._computeHelper=(t,a)=>e.computeHelper?e.computeHelper(t,Object.assign(Object.assign({},a),{},{path:[].concat((0,d.A)((null==a?void 0:a.path)||[]),[e.schema.name])})):e.computeHelper,e}return(0,p.A)(t,e),(0,c.A)(t,[{key:"_renderDescription",value:function(){var e,t=null===(e=this.computeHelper)||void 0===e?void 0:e.call(this,this.schema);return t?(0,v.qy)(o||(o=y`<p>${0}</p>`),t):v.s6}},{key:"render",value:function(){var e,t,a;return(0,v.qy)(n||(n=y`
      <ha-expansion-panel outlined .expanded=${0}>
        ${0}
        <div
          slot="header"
          role="heading"
          aria-level=${0}
        >
          ${0}
        </div>
        <div class="content">
          ${0}
          <ha-form
            .hass=${0}
            .data=${0}
            .schema=${0}
            .disabled=${0}
            .computeLabel=${0}
            .computeHelper=${0}
            .localizeValue=${0}
          ></ha-form>
        </div>
      </ha-expansion-panel>
    `),Boolean(this.schema.expanded),this.schema.icon?(0,v.qy)(i||(i=y`
              <ha-icon slot="leading-icon" .icon=${0}></ha-icon>
            `),this.schema.icon):this.schema.iconPath?(0,v.qy)(r||(r=y`
                <ha-svg-icon
                  slot="leading-icon"
                  .path=${0}
                ></ha-svg-icon>
              `),this.schema.iconPath):v.s6,null!==(e=null===(t=this.schema.headingLevel)||void 0===t?void 0:t.toString())&&void 0!==e?e:"3",this.schema.title||(null===(a=this.computeLabel)||void 0===a?void 0:a.call(this,this.schema)),this._renderDescription(),this.hass,this.data,this.schema.schema,this.disabled,this._computeLabel,this._computeHelper,this.localizeValue)}}])}(v.WF);f.styles=(0,v.AH)(s||(s=y`
    :host {
      display: flex !important;
      flex-direction: column;
    }
    :host ha-form {
      display: block;
    }
    .content {
      padding: 12px;
    }
    .content p {
      margin: 0 0 24px;
    }
    ha-expansion-panel {
      display: block;
      --expansion-panel-content-padding: 0;
      border-radius: var(--ha-border-radius-md);
      --ha-card-border-radius: var(--ha-border-radius-md);
    }
    ha-svg-icon,
    ha-icon {
      color: var(--secondary-text-color);
    }
  `)),(0,u.__decorate)([(0,m.MZ)({attribute:!1})],f.prototype,"hass",void 0),(0,u.__decorate)([(0,m.MZ)({attribute:!1})],f.prototype,"data",void 0),(0,u.__decorate)([(0,m.MZ)({attribute:!1})],f.prototype,"schema",void 0),(0,u.__decorate)([(0,m.MZ)({type:Boolean})],f.prototype,"disabled",void 0),(0,u.__decorate)([(0,m.MZ)({attribute:!1})],f.prototype,"computeLabel",void 0),(0,u.__decorate)([(0,m.MZ)({attribute:!1})],f.prototype,"computeHelper",void 0),(0,u.__decorate)([(0,m.MZ)({attribute:!1})],f.prototype,"localizeValue",void 0),f=(0,u.__decorate)([(0,m.EM)("ha-form-expandable")],f)}}]);
//# sourceMappingURL=8550.2611bcb7cb166eb1.js.map