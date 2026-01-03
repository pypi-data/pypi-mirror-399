(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["8195"],{61974:function(e,t,a){var o={"./ha-icon-prev":["48268","2477"],"./ha-icon-button-toolbar":["48939","7770","7163","9387"],"./ha-alert":["17963","6632"],"./ha-icon-button-toggle":["35150","2851"],"./ha-svg-icon.ts":["60961"],"./ha-alert.ts":["17963","6632"],"./ha-icon":["22598","7163","894"],"./ha-icon-next.ts":["28608"],"./ha-qr-code.ts":["16618","1343","6247"],"./ha-icon-overflow-menu.ts":["53623","2016","7770","1296"],"./ha-icon-button-toggle.ts":["35150","2851"],"./ha-icon-button-group":["39651","7760"],"./ha-svg-icon":["60961"],"./ha-icon-button-prev":["80263","8076"],"./ha-icon-button.ts":["60733"],"./ha-icon-overflow-menu":["53623","2016","7770","1296"],"./ha-icon-button-arrow-next":["56231","5500"],"./ha-icon-button-prev.ts":["80263","8076"],"./ha-icon-picker":["88867","4124","624","7163","2386"],"./ha-icon-button-toolbar.ts":["48939","7770","7163","9387"],"./ha-icon-button-arrow-prev.ts":["371"],"./ha-icon-button-next":["29795","9488"],"./ha-icon-next":["28608"],"./ha-icon-picker.ts":["88867","4124","624","7163","2386"],"./ha-icon-prev.ts":["48268","2477"],"./ha-icon-button-arrow-prev":["371"],"./ha-icon-button-next.ts":["29795","9488"],"./ha-icon.ts":["22598","7163","894"],"./ha-qr-code":["16618","1343","6247"],"./ha-icon-button":["60733"],"./ha-icon-button-group.ts":["39651","7760"],"./ha-icon-button-arrow-next.ts":["56231","5500"]};function i(e){if(!a.o(o,e))return Promise.resolve().then((function(){var t=new Error("Cannot find module '"+e+"'");throw t.code="MODULE_NOT_FOUND",t}));var t=o[e],i=t[0];return Promise.all(t.slice(1).map(a.e)).then((function(){return a(i)}))}i.keys=function(){return Object.keys(o)},i.id=61974,e.exports=i},55376:function(e,t,a){"use strict";function o(e){return null==e||Array.isArray(e)?e:[e]}a.d(t,{e:function(){return o}})},53045:function(e,t,a){"use strict";a.d(t,{v:function(){return i}});var o=a(78261),i=(a(74423),a(2892),(e,t,a,i)=>{var r=e.split(".",3),n=(0,o.A)(r,3),l=n[0],d=n[1],s=n[2];return Number(l)>t||Number(l)===t&&(void 0===i?Number(d)>=a:Number(d)>a)||void 0!==i&&Number(l)===t&&Number(d)===a&&Number(s)>=i})},48565:function(e,t,a){"use strict";a.d(t,{d:function(){return o}});var o=e=>{switch(e.language){case"cs":case"de":case"fi":case"fr":case"sk":case"sv":return" ";default:return""}}},89473:function(e,t,a){"use strict";a.a(e,(async function(e,t){try{var o=a(44734),i=a(56038),r=a(69683),n=a(6454),l=(a(28706),a(62826)),d=a(88496),s=a(96196),c=a(77845),h=e([d]);d=(h.then?(await h)():h)[0];var p,u=e=>e,v=function(e){function t(){var e;(0,o.A)(this,t);for(var a=arguments.length,i=new Array(a),n=0;n<a;n++)i[n]=arguments[n];return(e=(0,r.A)(this,t,[].concat(i))).variant="brand",e}return(0,n.A)(t,e),(0,i.A)(t,null,[{key:"styles",get:function(){return[d.A.styles,(0,s.AH)(p||(p=u`
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
      `))]}}])}(d.A);v=(0,l.__decorate)([(0,c.EM)("ha-button")],v),t()}catch(f){t(f)}}))},5841:function(e,t,a){"use strict";var o,i,r=a(44734),n=a(56038),l=a(69683),d=a(6454),s=a(62826),c=a(96196),h=a(77845),p=e=>e,u=function(e){function t(){return(0,r.A)(this,t),(0,l.A)(this,t,arguments)}return(0,d.A)(t,e),(0,n.A)(t,[{key:"render",value:function(){return(0,c.qy)(o||(o=p`
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
      `))]}}])}(c.WF);u=(0,s.__decorate)([(0,h.EM)("ha-dialog-footer")],u)},86451:function(e,t,a){"use strict";var o,i,r,n,l,d,s=a(44734),c=a(56038),h=a(69683),p=a(6454),u=(a(28706),a(62826)),v=a(96196),f=a(77845),g=e=>e,m=function(e){function t(){var e;(0,s.A)(this,t);for(var a=arguments.length,o=new Array(a),i=0;i<a;i++)o[i]=arguments[i];return(e=(0,h.A)(this,t,[].concat(o))).subtitlePosition="below",e.showBorder=!1,e}return(0,p.A)(t,e),(0,c.A)(t,[{key:"render",value:function(){var e=(0,v.qy)(o||(o=g`<div class="header-title">
      <slot name="title"></slot>
    </div>`)),t=(0,v.qy)(i||(i=g`<div class="header-subtitle">
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
    `),"above"===this.subtitlePosition?(0,v.qy)(n||(n=g`${0}${0}`),t,e):(0,v.qy)(l||(l=g`${0}${0}`),e,t))}}],[{key:"styles",get:function(){return[(0,v.AH)(d||(d=g`
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
      `))]}}])}(v.WF);(0,u.__decorate)([(0,f.MZ)({type:String,attribute:"subtitle-position"})],m.prototype,"subtitlePosition",void 0),(0,u.__decorate)([(0,f.MZ)({type:Boolean,reflect:!0,attribute:"show-border"})],m.prototype,"showBorder",void 0),m=(0,u.__decorate)([(0,f.EM)("ha-dialog-header")],m)},485:function(e,t,a){"use strict";a.a(e,(async function(e,t){try{var o=a(44734),i=a(56038),r=a(69683),n=a(6454),l=a(25460),d=(a(28706),a(23418),a(62062),a(18111),a(61701),a(2892),a(26099),a(62826)),s=a(43306),c=a(96196),h=a(77845),p=a(94333),u=a(92542),v=a(89473),f=(a(60733),a(48565)),g=a(55376),m=a(78436),b=e([s,v]);[s,v]=b.then?(await b)():b;var y,w,_,x,k,A,$,M,z=e=>e,Z="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z",L="M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M13.5,16V19H10.5V16H8L12,12L16,16H13.5M13,9V3.5L18.5,9H13Z",S=function(e){function t(){var e;(0,o.A)(this,t);for(var a=arguments.length,i=new Array(a),n=0;n<a;n++)i[n]=arguments[n];return(e=(0,r.A)(this,t,[].concat(i))).multiple=!1,e.disabled=!1,e.uploading=!1,e.autoOpenFileDialog=!1,e._drag=!1,e}return(0,n.A)(t,e),(0,i.A)(t,[{key:"firstUpdated",value:function(e){(0,l.A)(t,"firstUpdated",this,3)([e]),this.autoOpenFileDialog&&this._openFilePicker()}},{key:"_name",get:function(){return void 0===this.value?"":"string"==typeof this.value?this.value:(this.value instanceof FileList?Array.from(this.value):(0,g.e)(this.value)).map((e=>e.name)).join(", ")}},{key:"render",value:function(){var e=this.localize||this.hass.localize;return(0,c.qy)(y||(y=z`
      ${0}
    `),this.uploading?(0,c.qy)(w||(w=z`<div class="container">
            <div class="uploading">
              <span class="header"
                >${0}</span
              >
              ${0}
            </div>
            <mwc-linear-progress
              .indeterminate=${0}
              .progress=${0}
            ></mwc-linear-progress>
          </div>`),this.uploadingLabel||(this.value?e("ui.components.file-upload.uploading_name",{name:this._name}):e("ui.components.file-upload.uploading")),this.progress?(0,c.qy)(_||(_=z`<div class="progress">
                    ${0}${0}%
                  </div>`),this.progress,this.hass&&(0,f.d)(this.hass.locale)):c.s6,!this.progress,this.progress?this.progress/100:void 0):(0,c.qy)(x||(x=z`<label
            for=${0}
            class="container ${0}"
            @drop=${0}
            @dragenter=${0}
            @dragover=${0}
            @dragleave=${0}
            @dragend=${0}
            >${0}
            <input
              id="input"
              type="file"
              class="file"
              .accept=${0}
              .multiple=${0}
              @change=${0}
          /></label>`),this.value?"":"input",(0,p.H)({dragged:this._drag,multiple:this.multiple,value:Boolean(this.value)}),this._handleDrop,this._handleDragStart,this._handleDragStart,this._handleDragEnd,this._handleDragEnd,this.value?"string"==typeof this.value?(0,c.qy)(A||(A=z`<div class="row">
                    <div class="value" @click=${0}>
                      <ha-svg-icon
                        .path=${0}
                      ></ha-svg-icon>
                      ${0}
                    </div>
                    <ha-icon-button
                      @click=${0}
                      .label=${0}
                      .path=${0}
                    ></ha-icon-button>
                  </div>`),this._openFilePicker,this.icon||L,this.value,this._clearValue,this.deleteLabel||e("ui.common.delete"),Z):(this.value instanceof FileList?Array.from(this.value):(0,g.e)(this.value)).map((t=>(0,c.qy)($||($=z`<div class="row">
                        <div class="value" @click=${0}>
                          <ha-svg-icon
                            .path=${0}
                          ></ha-svg-icon>
                          ${0} - ${0}
                        </div>
                        <ha-icon-button
                          @click=${0}
                          .label=${0}
                          .path=${0}
                        ></ha-icon-button>
                      </div>`),this._openFilePicker,this.icon||L,t.name,(0,m.A)(t.size),this._clearValue,this.deleteLabel||e("ui.common.delete"),Z))):(0,c.qy)(k||(k=z`<ha-button
                    size="small"
                    appearance="filled"
                    @click=${0}
                  >
                    <ha-svg-icon
                      slot="start"
                      .path=${0}
                    ></ha-svg-icon>
                    ${0}
                  </ha-button>
                  <span class="secondary"
                    >${0}</span
                  >
                  <span class="supports">${0}</span>`),this._openFilePicker,this.icon||L,this.label||e("ui.components.file-upload.label"),this.secondary||e("ui.components.file-upload.secondary"),this.supports),this.accept,this.multiple,this._handleFilePicked))}},{key:"_openFilePicker",value:function(){var e;null===(e=this._input)||void 0===e||e.click()}},{key:"_handleDrop",value:function(e){var t;e.preventDefault(),e.stopPropagation(),null!==(t=e.dataTransfer)&&void 0!==t&&t.files&&(0,u.r)(this,"file-picked",{files:this.multiple||1===e.dataTransfer.files.length?Array.from(e.dataTransfer.files):[e.dataTransfer.files[0]]}),this._drag=!1}},{key:"_handleDragStart",value:function(e){e.preventDefault(),e.stopPropagation(),this._drag=!0}},{key:"_handleDragEnd",value:function(e){e.preventDefault(),e.stopPropagation(),this._drag=!1}},{key:"_handleFilePicked",value:function(e){0!==e.target.files.length&&(this.value=e.target.files,(0,u.r)(this,"file-picked",{files:e.target.files}))}},{key:"_clearValue",value:function(e){e.preventDefault(),this._input.value="",this.value=void 0,(0,u.r)(this,"change"),(0,u.r)(this,"files-cleared")}}])}(c.WF);S.styles=(0,c.AH)(M||(M=z`
    :host {
      display: block;
      height: 240px;
    }
    :host([disabled]) {
      pointer-events: none;
      color: var(--disabled-text-color);
    }
    .container {
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      border: solid 1px
        var(--mdc-text-field-idle-line-color, rgba(0, 0, 0, 0.42));
      border-radius: var(--mdc-shape-small, var(--ha-border-radius-sm));
      height: 100%;
    }
    .row {
      display: flex;
      align-items: center;
    }
    label.container {
      border: dashed 1px
        var(--mdc-text-field-idle-line-color, rgba(0, 0, 0, 0.42));
      cursor: pointer;
    }
    .container .uploading {
      display: flex;
      flex-direction: column;
      width: 100%;
      align-items: flex-start;
      padding: 0 32px;
      box-sizing: border-box;
    }
    :host([disabled]) .container {
      border-color: var(--disabled-color);
    }
    label:hover,
    label.dragged {
      border-style: solid;
    }
    label.dragged {
      border-color: var(--primary-color);
    }
    .dragged:before {
      position: absolute;
      top: 0;
      right: 0;
      bottom: 0;
      left: 0;
      background-color: var(--primary-color);
      content: "";
      opacity: var(--dark-divider-opacity);
      pointer-events: none;
      border-radius: var(--mdc-shape-small, 4px);
    }
    label.value {
      cursor: default;
    }
    label.value.multiple {
      justify-content: unset;
      overflow: auto;
    }
    .highlight {
      color: var(--primary-color);
    }
    ha-button {
      margin-bottom: 8px;
    }
    .supports {
      color: var(--secondary-text-color);
      font-size: var(--ha-font-size-s);
    }
    :host([disabled]) .secondary {
      color: var(--disabled-text-color);
    }
    input.file {
      display: none;
    }
    .value {
      cursor: pointer;
    }
    .value ha-svg-icon {
      margin-right: 8px;
      margin-inline-end: 8px;
      margin-inline-start: initial;
    }
    ha-button {
      --mdc-button-outline-color: var(--primary-color);
      --mdc-icon-button-size: 24px;
    }
    mwc-linear-progress {
      width: 100%;
      padding: 8px 32px;
      box-sizing: border-box;
    }
    .header {
      font-weight: var(--ha-font-weight-medium);
    }
    .progress {
      color: var(--secondary-text-color);
    }
    button.link {
      background: none;
      border: none;
      padding: 0;
      font-size: var(--ha-font-size-m);
      color: var(--primary-color);
      text-decoration: underline;
      cursor: pointer;
    }
  `)),(0,d.__decorate)([(0,h.MZ)({attribute:!1})],S.prototype,"hass",void 0),(0,d.__decorate)([(0,h.MZ)({attribute:!1})],S.prototype,"localize",void 0),(0,d.__decorate)([(0,h.MZ)()],S.prototype,"accept",void 0),(0,d.__decorate)([(0,h.MZ)()],S.prototype,"icon",void 0),(0,d.__decorate)([(0,h.MZ)()],S.prototype,"label",void 0),(0,d.__decorate)([(0,h.MZ)()],S.prototype,"secondary",void 0),(0,d.__decorate)([(0,h.MZ)({attribute:"uploading-label"})],S.prototype,"uploadingLabel",void 0),(0,d.__decorate)([(0,h.MZ)({attribute:"delete-label"})],S.prototype,"deleteLabel",void 0),(0,d.__decorate)([(0,h.MZ)()],S.prototype,"supports",void 0),(0,d.__decorate)([(0,h.MZ)({type:Object})],S.prototype,"value",void 0),(0,d.__decorate)([(0,h.MZ)({type:Boolean})],S.prototype,"multiple",void 0),(0,d.__decorate)([(0,h.MZ)({type:Boolean,reflect:!0})],S.prototype,"disabled",void 0),(0,d.__decorate)([(0,h.MZ)({type:Boolean})],S.prototype,"uploading",void 0),(0,d.__decorate)([(0,h.MZ)({type:Number})],S.prototype,"progress",void 0),(0,d.__decorate)([(0,h.MZ)({type:Boolean,attribute:"auto-open-file-dialog"})],S.prototype,"autoOpenFileDialog",void 0),(0,d.__decorate)([(0,h.wk)()],S.prototype,"_drag",void 0),(0,d.__decorate)([(0,h.P)("#input")],S.prototype,"_input",void 0),S=(0,d.__decorate)([(0,h.EM)("ha-file-upload")],S),t()}catch(E){t(E)}}))},56768:function(e,t,a){"use strict";var o,i,r=a(44734),n=a(56038),l=a(69683),d=a(6454),s=(a(28706),a(62826)),c=a(96196),h=a(77845),p=e=>e,u=function(e){function t(){var e;(0,r.A)(this,t);for(var a=arguments.length,o=new Array(a),i=0;i<a;i++)o[i]=arguments[i];return(e=(0,l.A)(this,t,[].concat(o))).disabled=!1,e}return(0,d.A)(t,e),(0,n.A)(t,[{key:"render",value:function(){return(0,c.qy)(o||(o=p`<slot></slot>`))}}])}(c.WF);u.styles=(0,c.AH)(i||(i=p`
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
  `)),(0,s.__decorate)([(0,h.MZ)({type:Boolean,reflect:!0})],u.prototype,"disabled",void 0),u=(0,s.__decorate)([(0,h.EM)("ha-input-helper-text")],u)},28089:function(e,t,a){"use strict";var o,i,r=a(61397),n=a(50264),l=a(44734),d=a(56038),s=a(69683),c=a(6454),h=a(25460),p=(a(28706),a(62826)),u=a(96196),v=a(77845),f=a(3164),g=a(94741),m=a(75864),b=a(59787),y=(a(2008),a(23418),a(74423),a(23792),a(62062),a(72712),a(34782),a(18111),a(22489),a(61701),a(18237),a(26099),a(3362),a(27495),a(62953),a(1420)),w=a(30015),_=a.n(w),x=a(92542),k=(a(3296),a(27208),a(48408),a(14603),a(47566),a(98721),a(2209)),A=function(){var e=(0,n.A)((0,r.A)().m((function e(t,i,n){return(0,r.A)().w((function(e){for(;;)if(0===e.n)return o||(o=(0,k.LV)(new Worker(new URL(a.p+a.u("5640"),a.b)))),e.a(2,o.renderMarkdown(t,i,n))}),e)})));return function(t,a,o){return e.apply(this,arguments)}}(),$=(a(36033),e=>e),M=e=>(0,u.qy)(i||(i=$`${0}`),e),z=new(function(){return(0,d.A)((function e(t){(0,l.A)(this,e),this._cache=new Map,this._expiration=t}),[{key:"get",value:function(e){return this._cache.get(e)}},{key:"set",value:function(e,t){this._cache.set(e,t),this._expiration&&window.setTimeout((()=>this._cache.delete(e)),this._expiration)}},{key:"has",value:function(e){return this._cache.has(e)}}])}())(1e3),Z={reType:(0,b.A)(/((\[!(caution|important|note|tip|warning)\])(?:\s|\\n)?)/i,{input:1,type:3}),typeToHaAlert:{caution:"error",important:"info",note:"info",tip:"success",warning:"warning"}},L=function(e){function t(){var e;(0,l.A)(this,t);for(var a=arguments.length,o=new Array(a),i=0;i<a;i++)o[i]=arguments[i];return(e=(0,s.A)(this,t,[].concat(o))).allowSvg=!1,e.allowDataUrl=!1,e.breaks=!1,e.lazyImages=!1,e.cache=!1,e._renderPromise=Promise.resolve(),e._resize=()=>(0,x.r)((0,m.A)(e),"content-resize"),e}return(0,c.A)(t,e),(0,d.A)(t,[{key:"disconnectedCallback",value:function(){if((0,h.A)(t,"disconnectedCallback",this,3)([]),this.cache){var e=this._computeCacheKey();z.set(e,this.innerHTML)}}},{key:"createRenderRoot",value:function(){return this}},{key:"update",value:function(e){(0,h.A)(t,"update",this,3)([e]),void 0!==this.content&&(this._renderPromise=this._render())}},{key:"getUpdateComplete",value:(i=(0,n.A)((0,r.A)().m((function e(){return(0,r.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,(0,h.A)(t,"getUpdateComplete",this,3)([]);case 1:return e.n=2,this._renderPromise;case 2:return e.a(2,!0)}}),e,this)}))),function(){return i.apply(this,arguments)})},{key:"willUpdate",value:function(e){if(!this.innerHTML&&this.cache){var t=this._computeCacheKey();z.has(t)&&((0,u.XX)(M((0,y._)(z.get(t))),this.renderRoot),this._resize())}}},{key:"_computeCacheKey",value:function(){return _()({content:this.content,allowSvg:this.allowSvg,allowDataUrl:this.allowDataUrl,breaks:this.breaks})}},{key:"_render",value:(o=(0,n.A)((0,r.A)().m((function e(){var t,o,i,n=this;return(0,r.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,A(String(this.content),{breaks:this.breaks,gfm:!0},{allowSvg:this.allowSvg,allowDataUrl:this.allowDataUrl});case 1:t=e.v,(0,u.XX)(M((0,y._)(t.join(""))),this.renderRoot),this._resize(),o=document.createTreeWalker(this,NodeFilter.SHOW_ELEMENT,null),i=(0,r.A)().m((function e(){var t,i,l,d,s;return(0,r.A)().w((function(e){for(;;)switch(e.n){case 0:(t=o.currentNode)instanceof HTMLAnchorElement&&t.host!==document.location.host?(t.target="_blank",t.rel="noreferrer noopener"):t instanceof HTMLImageElement?(n.lazyImages&&(t.loading="lazy"),t.addEventListener("load",n._resize)):t instanceof HTMLQuoteElement?(l=(null===(i=t.firstElementChild)||void 0===i||null===(i=i.firstChild)||void 0===i?void 0:i.textContent)&&Z.reType.exec(t.firstElementChild.firstChild.textContent))&&(d=l.groups.type,(s=document.createElement("ha-alert")).alertType=Z.typeToHaAlert[d.toLowerCase()],s.append.apply(s,(0,g.A)(Array.from(t.childNodes).map((e=>{var t=Array.from(e.childNodes);if(!n.breaks&&t.length){var a,o=t[0];o.nodeType===Node.TEXT_NODE&&o.textContent===l.input&&null!==(a=o.textContent)&&void 0!==a&&a.includes("\n")&&(o.textContent=o.textContent.split("\n").slice(1).join("\n"))}return t})).reduce(((e,t)=>e.concat(t)),[]).filter((e=>e.textContent&&e.textContent!==l.input)))),o.parentNode().replaceChild(s,t)):t instanceof HTMLElement&&["ha-alert","ha-qr-code","ha-icon","ha-svg-icon"].includes(t.localName)&&a(61974)(`./${t.localName}`);case 1:return e.a(2)}}),e)}));case 2:if(!o.nextNode()){e.n=4;break}return e.d((0,f.A)(i()),3);case 3:e.n=2;break;case 4:return e.a(2)}}),e,this)}))),function(){return o.apply(this,arguments)})}]);var o,i}(u.mN);(0,p.__decorate)([(0,v.MZ)()],L.prototype,"content",void 0),(0,p.__decorate)([(0,v.MZ)({attribute:"allow-svg",type:Boolean})],L.prototype,"allowSvg",void 0),(0,p.__decorate)([(0,v.MZ)({attribute:"allow-data-url",type:Boolean})],L.prototype,"allowDataUrl",void 0),(0,p.__decorate)([(0,v.MZ)({type:Boolean})],L.prototype,"breaks",void 0),(0,p.__decorate)([(0,v.MZ)({type:Boolean,attribute:"lazy-images"})],L.prototype,"lazyImages",void 0),(0,p.__decorate)([(0,v.MZ)({type:Boolean})],L.prototype,"cache",void 0),L=(0,p.__decorate)([(0,v.EM)("ha-markdown-element")],L);var S,E,B=e=>e,P=function(e){function t(){var e;(0,l.A)(this,t);for(var a=arguments.length,o=new Array(a),i=0;i<a;i++)o[i]=arguments[i];return(e=(0,s.A)(this,t,[].concat(o))).allowSvg=!1,e.allowDataUrl=!1,e.breaks=!1,e.lazyImages=!1,e.cache=!1,e}return(0,c.A)(t,e),(0,d.A)(t,[{key:"getUpdateComplete",value:(a=(0,n.A)((0,r.A)().m((function e(){var a,o;return(0,r.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,(0,h.A)(t,"getUpdateComplete",this,3)([]);case 1:return o=e.v,e.n=2,null===(a=this._markdownElement)||void 0===a?void 0:a.updateComplete;case 2:return e.a(2,o)}}),e,this)}))),function(){return a.apply(this,arguments)})},{key:"render",value:function(){return this.content?(0,u.qy)(S||(S=B`<ha-markdown-element
      .content=${0}
      .allowSvg=${0}
      .allowDataUrl=${0}
      .breaks=${0}
      .lazyImages=${0}
      .cache=${0}
    ></ha-markdown-element>`),this.content,this.allowSvg,this.allowDataUrl,this.breaks,this.lazyImages,this.cache):u.s6}}]);var a}(u.WF);P.styles=(0,u.AH)(E||(E=B`
    :host {
      display: block;
    }
    ha-markdown-element {
      -ms-user-select: text;
      -webkit-user-select: text;
      -moz-user-select: text;
    }
    ha-markdown-element > *:first-child {
      margin-top: 0;
    }
    ha-markdown-element > *:last-child {
      margin-bottom: 0;
    }
    ha-alert {
      display: block;
      margin: var(--ha-space-1) 0;
    }
    a {
      color: var(--markdown-link-color, var(--primary-color));
    }
    img {
      background-color: var(--markdown-image-background-color);
      border-radius: var(--markdown-image-border-radius);
      max-width: 100%;
      height: auto;
      width: auto;
      transition: height 0.2s ease-in-out;
    }
    p:first-child > img:first-child {
      vertical-align: top;
    }
    p:first-child > img:last-child {
      vertical-align: top;
    }
    :host > ul,
    :host > ol {
      padding-inline-start: var(--markdown-list-indent, revert);
    }
    li {
      &:has(input[type="checkbox"]) {
        list-style: none;
        & > input[type="checkbox"] {
          margin-left: 0;
        }
      }
    }
    svg {
      background-color: var(--markdown-svg-background-color, none);
      color: var(--markdown-svg-color, none);
    }
    code,
    pre {
      background-color: var(--markdown-code-background-color, none);
      border-radius: var(--ha-border-radius-sm);
      color: var(--markdown-code-text-color, inherit);
    }
    code {
      font-size: var(--ha-font-size-s);
      padding: 0.2em 0.4em;
    }
    pre code {
      padding: 0;
    }
    pre {
      padding: var(--ha-space-4);
      overflow: auto;
      line-height: var(--ha-line-height-condensed);
      font-family: var(--ha-font-family-code);
    }
    h1,
    h2,
    h3,
    h4,
    h5,
    h6 {
      line-height: initial;
    }
    h2 {
      font-size: var(--ha-font-size-xl);
      font-weight: var(--ha-font-weight-bold);
    }
    hr {
      border-color: var(--divider-color);
      border-bottom: none;
      margin: var(--ha-space-4) 0;
    }
    table {
      border-collapse: var(--markdown-table-border-collapse, collapse);
    }
    div:has(> table) {
      overflow: auto;
    }
    th {
      text-align: start;
    }
    td,
    th {
      border-width: var(--markdown-table-border-width, 1px);
      border-style: var(--markdown-table-border-style, solid);
      border-color: var(--markdown-table-border-color, var(--divider-color));
      padding: 0.25em 0.5em;
    }
    blockquote {
      border-left: 4px solid var(--divider-color);
      margin-inline: 0;
      padding-inline: 1em;
    }
  `)),(0,p.__decorate)([(0,v.MZ)()],P.prototype,"content",void 0),(0,p.__decorate)([(0,v.MZ)({attribute:"allow-svg",type:Boolean})],P.prototype,"allowSvg",void 0),(0,p.__decorate)([(0,v.MZ)({attribute:"allow-data-url",type:Boolean})],P.prototype,"allowDataUrl",void 0),(0,p.__decorate)([(0,v.MZ)({type:Boolean})],P.prototype,"breaks",void 0),(0,p.__decorate)([(0,v.MZ)({type:Boolean,attribute:"lazy-images"})],P.prototype,"lazyImages",void 0),(0,p.__decorate)([(0,v.MZ)({type:Boolean})],P.prototype,"cache",void 0),(0,p.__decorate)([(0,v.P)("ha-markdown-element")],P.prototype,"_markdownElement",void 0),P=(0,p.__decorate)([(0,v.EM)("ha-markdown")],P)},78740:function(e,t,a){"use strict";a.d(t,{h:function(){return y}});var o,i,r,n,l=a(44734),d=a(56038),s=a(69683),c=a(6454),h=a(25460),p=(a(28706),a(62826)),u=a(68846),v=a(92347),f=a(96196),g=a(77845),m=a(76679),b=e=>e,y=function(e){function t(){var e;(0,l.A)(this,t);for(var a=arguments.length,o=new Array(a),i=0;i<a;i++)o[i]=arguments[i];return(e=(0,s.A)(this,t,[].concat(o))).icon=!1,e.iconTrailing=!1,e.autocorrect=!0,e}return(0,c.A)(t,e),(0,d.A)(t,[{key:"updated",value:function(e){(0,h.A)(t,"updated",this,3)([e]),(e.has("invalid")||e.has("errorMessage"))&&(this.setCustomValidity(this.invalid?this.errorMessage||this.validationMessage||"Invalid":""),(this.invalid||this.validateOnInitialRender||e.has("invalid")&&void 0!==e.get("invalid"))&&this.reportValidity()),e.has("autocomplete")&&(this.autocomplete?this.formElement.setAttribute("autocomplete",this.autocomplete):this.formElement.removeAttribute("autocomplete")),e.has("autocorrect")&&(!1===this.autocorrect?this.formElement.setAttribute("autocorrect","off"):this.formElement.removeAttribute("autocorrect")),e.has("inputSpellcheck")&&(this.inputSpellcheck?this.formElement.setAttribute("spellcheck",this.inputSpellcheck):this.formElement.removeAttribute("spellcheck"))}},{key:"renderIcon",value:function(e){var t=arguments.length>1&&void 0!==arguments[1]&&arguments[1],a=t?"trailing":"leading";return(0,f.qy)(o||(o=b`
      <span
        class="mdc-text-field__icon mdc-text-field__icon--${0}"
        tabindex=${0}
      >
        <slot name="${0}Icon"></slot>
      </span>
    `),a,t?1:-1,a)}}])}(u.J);y.styles=[v.R,(0,f.AH)(i||(i=b`
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
    `)),"rtl"===m.G.document.dir?(0,f.AH)(r||(r=b`
          .mdc-text-field--with-leading-icon,
          .mdc-text-field__icon--leading,
          .mdc-floating-label,
          .mdc-text-field--with-leading-icon.mdc-text-field--filled
            .mdc-floating-label,
          .mdc-text-field__input[type="number"] {
            direction: rtl;
            --direction: rtl;
          }
        `)):(0,f.AH)(n||(n=b``))],(0,p.__decorate)([(0,g.MZ)({type:Boolean})],y.prototype,"invalid",void 0),(0,p.__decorate)([(0,g.MZ)({attribute:"error-message"})],y.prototype,"errorMessage",void 0),(0,p.__decorate)([(0,g.MZ)({type:Boolean})],y.prototype,"icon",void 0),(0,p.__decorate)([(0,g.MZ)({type:Boolean})],y.prototype,"iconTrailing",void 0),(0,p.__decorate)([(0,g.MZ)()],y.prototype,"autocomplete",void 0),(0,p.__decorate)([(0,g.MZ)({type:Boolean})],y.prototype,"autocorrect",void 0),(0,p.__decorate)([(0,g.MZ)({attribute:"input-spellcheck"})],y.prototype,"inputSpellcheck",void 0),(0,p.__decorate)([(0,g.P)("input")],y.prototype,"formElement",void 0),y=(0,p.__decorate)([(0,g.EM)("ha-textfield")],y)},36626:function(e,t,a){"use strict";a.a(e,(async function(e,t){try{var o=a(61397),i=a(50264),r=a(44734),n=a(56038),l=a(75864),d=a(69683),s=a(6454),c=a(25460),h=(a(28706),a(62826)),p=a(93900),u=a(96196),v=a(77845),f=a(32288),g=a(92542),m=a(39396),b=(a(86451),a(60733),e([p]));p=(b.then?(await b)():b)[0];var y,w,_,x,k,A,$=e=>e,M=function(e){function t(){var e;(0,r.A)(this,t);for(var a=arguments.length,n=new Array(a),s=0;s<a;s++)n[s]=arguments[s];return(e=(0,d.A)(this,t,[].concat(n))).open=!1,e.type="standard",e.width="medium",e.preventScrimClose=!1,e.headerSubtitlePosition="below",e.flexContent=!1,e._open=!1,e._bodyScrolled=!1,e._handleShow=(0,i.A)((0,o.A)().m((function t(){return(0,o.A)().w((function(t){for(;;)switch(t.n){case 0:return e._open=!0,(0,g.r)((0,l.A)(e),"opened"),t.n=1,e.updateComplete;case 1:requestAnimationFrame((()=>{var t;null===(t=e.querySelector("[autofocus]"))||void 0===t||t.focus()}));case 2:return t.a(2)}}),t)}))),e._handleAfterShow=()=>{(0,g.r)((0,l.A)(e),"after-show")},e._handleAfterHide=()=>{e._open=!1,(0,g.r)((0,l.A)(e),"closed")},e}return(0,s.A)(t,e),(0,n.A)(t,[{key:"updated",value:function(e){(0,c.A)(t,"updated",this,3)([e]),e.has("open")&&(this._open=this.open)}},{key:"render",value:function(){var e,t;return(0,u.qy)(y||(y=$`
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
    `),this._open,!this.preventScrimClose,(0,f.J)(this.ariaLabelledBy||(void 0!==this.headerTitle?"ha-wa-dialog-title":void 0)),(0,f.J)(this.ariaDescribedBy),this._handleShow,this._handleAfterShow,this._handleAfterHide,this.headerSubtitlePosition,this._bodyScrolled,null!==(e=null===(t=this.hass)||void 0===t?void 0:t.localize("ui.common.close"))&&void 0!==e?e:"Close","M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",void 0!==this.headerTitle?(0,u.qy)(w||(w=$`<span slot="title" class="title" id="ha-wa-dialog-title">
                  ${0}
                </span>`),this.headerTitle):(0,u.qy)(_||(_=$`<slot name="headerTitle" slot="title"></slot>`)),void 0!==this.headerSubtitle?(0,u.qy)(x||(x=$`<span slot="subtitle">${0}</span>`),this.headerSubtitle):(0,u.qy)(k||(k=$`<slot name="headerSubtitle" slot="subtitle"></slot>`)),this._handleBodyScroll)}},{key:"disconnectedCallback",value:function(){(0,c.A)(t,"disconnectedCallback",this,3)([]),this._open=!1}},{key:"_handleBodyScroll",value:function(e){this._bodyScrolled=e.target.scrollTop>0}}])}(u.WF);M.styles=[m.dp,(0,u.AH)(A||(A=$`
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
    `))],(0,h.__decorate)([(0,v.MZ)({attribute:!1})],M.prototype,"hass",void 0),(0,h.__decorate)([(0,v.MZ)({attribute:"aria-labelledby"})],M.prototype,"ariaLabelledBy",void 0),(0,h.__decorate)([(0,v.MZ)({attribute:"aria-describedby"})],M.prototype,"ariaDescribedBy",void 0),(0,h.__decorate)([(0,v.MZ)({type:Boolean,reflect:!0})],M.prototype,"open",void 0),(0,h.__decorate)([(0,v.MZ)({reflect:!0})],M.prototype,"type",void 0),(0,h.__decorate)([(0,v.MZ)({type:String,reflect:!0,attribute:"width"})],M.prototype,"width",void 0),(0,h.__decorate)([(0,v.MZ)({type:Boolean,reflect:!0,attribute:"prevent-scrim-close"})],M.prototype,"preventScrimClose",void 0),(0,h.__decorate)([(0,v.MZ)({attribute:"header-title"})],M.prototype,"headerTitle",void 0),(0,h.__decorate)([(0,v.MZ)({attribute:"header-subtitle"})],M.prototype,"headerSubtitle",void 0),(0,h.__decorate)([(0,v.MZ)({type:String,attribute:"header-subtitle-position"})],M.prototype,"headerSubtitlePosition",void 0),(0,h.__decorate)([(0,v.MZ)({type:Boolean,reflect:!0,attribute:"flexcontent"})],M.prototype,"flexContent",void 0),(0,h.__decorate)([(0,v.wk)()],M.prototype,"_open",void 0),(0,h.__decorate)([(0,v.P)(".body")],M.prototype,"bodyContainer",void 0),(0,h.__decorate)([(0,v.wk)()],M.prototype,"_bodyScrolled",void 0),(0,h.__decorate)([(0,v.Ls)({passive:!0})],M.prototype,"_handleBodyScroll",null),M=(0,h.__decorate)([(0,v.EM)("ha-wa-dialog")],M),t()}catch(z){t(z)}}))},31169:function(e,t,a){"use strict";a.d(t,{Q:function(){return r},n:function(){return n}});var o=a(61397),i=a(50264),r=(a(16280),function(){var e=(0,i.A)((0,o.A)().m((function e(t,a){var i,r,n;return(0,o.A)().w((function(e){for(;;)switch(e.n){case 0:return(i=new FormData).append("file",a),e.n=1,t.fetchWithAuth("/api/file_upload",{method:"POST",body:i});case 1:if(413!==(r=e.v).status){e.n=2;break}throw new Error(`Uploaded file is too large (${a.name})`);case 2:if(200===r.status){e.n=3;break}throw new Error("Unknown error");case 3:return e.n=4,r.json();case 4:return n=e.v,e.a(2,n.file_id)}}),e)})));return function(t,a){return e.apply(this,arguments)}}()),n=function(){var e=(0,i.A)((0,o.A)().m((function e(t,a){return(0,o.A)().w((function(e){for(;;)if(0===e.n)return e.a(2,t.callApi("DELETE","file_upload",{file_id:a}))}),e)})));return function(t,a){return e.apply(this,arguments)}}()},95260:function(e,t,a){"use strict";a.d(t,{PS:function(){return o},VR:function(){return i}});a(61397),a(50264),a(74423),a(23792),a(26099),a(31415),a(17642),a(58004),a(33853),a(45876),a(32475),a(15024),a(31698),a(62953),a(53045);var o=e=>e.data,i=e=>"object"==typeof e?"object"==typeof e.body?e.body.message||"Unknown error, see supervisor logs":e.body||e.message||"Unknown error, see supervisor logs":e;new Set([502,503,504])},10234:function(e,t,a){"use strict";a.d(t,{K$:function(){return n},an:function(){return d},dk:function(){return l}});a(23792),a(26099),a(3362),a(62953);var o=a(92542),i=()=>Promise.all([a.e("6009"),a.e("4533"),a.e("2013"),a.e("1530")]).then(a.bind(a,22316)),r=(e,t,a)=>new Promise((r=>{var n=t.cancel,l=t.confirm;(0,o.r)(e,"show-dialog",{dialogTag:"dialog-box",dialogImport:i,dialogParams:Object.assign(Object.assign(Object.assign({},t),a),{},{cancel:()=>{r(!(null==a||!a.prompt)&&null),n&&n()},confirm:e=>{r(null==a||!a.prompt||e),l&&l(e)}})})})),n=(e,t)=>r(e,t),l=(e,t)=>r(e,t,{confirmation:!0}),d=(e,t)=>r(e,t,{prompt:!0})},71950:function(e,t,a){"use strict";a.a(e,(async function(e,t){try{a(23792),a(26099),a(3362),a(62953);var o=a(71950),i=e([o]);o=(i.then?(await i)():i)[0],"function"!=typeof window.ResizeObserver&&(window.ResizeObserver=(await a.e("1055").then(a.bind(a,52370))).default),t()}catch(r){t(r)}}),1)},78436:function(e,t,a){"use strict";a.d(t,{A:function(){return o}});var o=function(){var e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:0,t=arguments.length>1&&void 0!==arguments[1]?arguments[1]:2;if(0===e)return"0 Bytes";t=t<0?0:t;var a=Math.floor(Math.log(e)/Math.log(1024));return`${parseFloat((e/Math.pow(1024,a)).toFixed(t))} ${["Bytes","KB","MB","GB","TB","PB","EB","ZB","YB"][a]}`}},21199:function(e,t,a){"use strict";a.a(e,(async function(e,o){try{a.r(t),a.d(t,{KnxProjectUploadDialog:function(){return M}});var i=a(61397),r=a(50264),n=a(44734),l=a(56038),d=a(69683),s=a(6454),c=(a(28706),a(62826)),h=a(96196),p=a(77845),u=a(89473),v=(a(5841),a(485)),f=(a(28089),a(81774)),g=a(36626),m=a(92542),b=a(31169),y=a(95260),w=a(10234),_=a(65294),x=e([u,v,f,g]);[u,v,f,g]=x.then?(await x)():x;var k,A,$=e=>e,M=function(e){function t(){var e;(0,n.A)(this,t);for(var a=arguments.length,o=new Array(a),i=0;i<a;i++)o[i]=arguments[i];return(e=(0,d.A)(this,t,[].concat(o)))._opened=!1,e._uploading=!1,e._backendLocalize=t=>e.hass.localize(`component.knx.config_panel.dialogs.project_upload.${t}`),e}return(0,s.A)(t,e),(0,l.A)(t,[{key:"showDialog",value:function(e){this._opened=!0,this._projectFile=void 0,this._projectPassword=void 0,this._uploading=!1}},{key:"closeDialog",value:function(e){return this._projectFile=void 0,this._projectPassword=void 0,this._uploading=!1,this._opened=!1,!0}},{key:"render",value:function(){var e;return(0,h.qy)(k||(k=$`
      <ha-wa-dialog
        .hass=${0}
        .open=${0}
        @closed=${0}
        .headerTitle=${0}
      >
        <div class="content">
          <ha-markdown
            class="description"
            breaks
            .content=${0}
          ></ha-markdown>
          <ha-file-upload
            .hass=${0}
            accept=".knxproj, .knxprojarchive"
            .icon=${0}
            .label=${0}
            .value=${0}
            .uploading=${0}
            @file-picked=${0}
          ></ha-file-upload>
          <ha-selector-text
            .hass=${0}
            .value=${0}
            .label=${0}
            .selector=${0}
            .required=${0}
            @value-changed=${0}
          >
          </ha-selector-text>
        </div>
        <ha-dialog-footer slot="footer">
          <ha-button
            slot="primaryAction"
            @click=${0}
            .disabled=${0}
          >
            ${0}
          </ha-button>
          <ha-button slot="secondaryAction" @click=${0} .disabled=${0}>
            ${0}
          </ha-button></ha-dialog-footer
        >
      </ha-wa-dialog>
    `),this.hass,this._opened,this.closeDialog,this._backendLocalize("title"),this._backendLocalize("description"),this.hass,"M14,2H6A2,2 0 0,0 4,4V20A2,2 0 0,0 6,22H18A2,2 0 0,0 20,20V8L14,2M13.5,16V19H10.5V16H8L12,12L16,16H13.5M13,9V3.5L18.5,9H13Z",this._backendLocalize("file_upload_label"),null===(e=this._projectFile)||void 0===e?void 0:e.name,this._uploading,this._filePicked,this.hass,this._projectPassword||"",this.hass.localize("ui.login-form.password"),{text:{multiline:!1,type:"password"}},!1,this._passwordChanged,this._uploadFile,this._uploading||!this._projectFile,this.hass.localize("ui.common.submit"),this.closeDialog,this._uploading,this.hass.localize("ui.common.cancel"))}},{key:"_filePicked",value:function(e){this._projectFile=e.detail.files[0]}},{key:"_passwordChanged",value:function(e){this._projectPassword=e.detail.value}},{key:"_uploadFile",value:(a=(0,r.A)((0,i.A)().m((function e(){var t,a,o,r;return(0,i.A)().w((function(e){for(;;)switch(e.p=e.n){case 0:if(void 0!==(t=this._projectFile)){e.n=1;break}return e.a(2);case 1:return this._uploading=!0,e.p=2,e.n=3,(0,b.Q)(this.hass,t);case 3:return o=e.v,e.n=4,(0,_.dc)(this.hass,o,this._projectPassword||"");case 4:e.n=6;break;case 5:e.p=5,r=e.v,a=r,(0,w.K$)(this,{title:"Upload failed",text:(0,y.VR)(r)});case 6:return e.p=6,this._uploading=!1,a||(this.closeDialog(),(0,m.r)(this,"knx-reload")),e.f(6);case 7:return e.a(2)}}),e,this,[[2,5,6,7]])}))),function(){return a.apply(this,arguments)})}]);var a}(h.WF);M.styles=(0,h.AH)(A||(A=$`
    .content {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .description {
      margin-bottom: 8px;
    }

    ha-file-upload,
    ha-selector-text {
      width: 100%;
    }
  `)),(0,c.__decorate)([(0,p.MZ)({attribute:!1})],M.prototype,"hass",void 0),(0,c.__decorate)([(0,p.wk)()],M.prototype,"_opened",void 0),(0,c.__decorate)([(0,p.wk)()],M.prototype,"_projectPassword",void 0),(0,c.__decorate)([(0,p.wk)()],M.prototype,"_uploading",void 0),(0,c.__decorate)([(0,p.wk)()],M.prototype,"_projectFile",void 0),M=(0,c.__decorate)([(0,p.EM)("knx-project-upload-dialog")],M),o()}catch(z){o(z)}}))}}]);
//# sourceMappingURL=8195.bbdabc7c308c3c05.js.map