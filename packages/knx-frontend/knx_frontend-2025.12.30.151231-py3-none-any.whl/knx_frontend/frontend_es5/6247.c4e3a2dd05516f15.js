"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["6247"],{17963:function(e,t,r){r.r(t);var o,a,i,n,s=r(44734),c=r(56038),l=r(69683),d=r(6454),h=(r(28706),r(62826)),p=r(96196),v=r(77845),u=r(94333),y=r(92542),m=(r(60733),r(60961),e=>e),g={info:"M11,9H13V7H11M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M11,17H13V11H11V17Z",warning:"M12,2L1,21H23M12,6L19.53,19H4.47M11,10V14H13V10M11,16V18H13V16",error:"M11,15H13V17H11V15M11,7H13V13H11V7M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20Z",success:"M20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4C12.76,4 13.5,4.11 14.2,4.31L15.77,2.74C14.61,2.26 13.34,2 12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12M7.91,10.08L6.5,11.5L11,16L21,6L19.59,4.58L11,13.17L7.91,10.08Z"},f=function(e){function t(){var e;(0,s.A)(this,t);for(var r=arguments.length,o=new Array(r),a=0;a<r;a++)o[a]=arguments[a];return(e=(0,l.A)(this,t,[].concat(o))).title="",e.alertType="info",e.dismissable=!1,e.narrow=!1,e}return(0,d.A)(t,e),(0,c.A)(t,[{key:"render",value:function(){return(0,p.qy)(o||(o=m`
      <div
        class="issue-type ${0}"
        role="alert"
      >
        <div class="icon ${0}">
          <slot name="icon">
            <ha-svg-icon .path=${0}></ha-svg-icon>
          </slot>
        </div>
        <div class=${0}>
          <div class="main-content">
            ${0}
            <slot></slot>
          </div>
          <div class="action">
            <slot name="action">
              ${0}
            </slot>
          </div>
        </div>
      </div>
    `),(0,u.H)({[this.alertType]:!0}),this.title?"":"no-title",g[this.alertType],(0,u.H)({content:!0,narrow:this.narrow}),this.title?(0,p.qy)(a||(a=m`<div class="title">${0}</div>`),this.title):p.s6,this.dismissable?(0,p.qy)(i||(i=m`<ha-icon-button
                    @click=${0}
                    label="Dismiss alert"
                    .path=${0}
                  ></ha-icon-button>`),this._dismissClicked,"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"):p.s6)}},{key:"_dismissClicked",value:function(){(0,y.r)(this,"alert-dismissed-clicked")}}])}(p.WF);f.styles=(0,p.AH)(n||(n=m`
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
  `)),(0,h.__decorate)([(0,v.MZ)()],f.prototype,"title",void 0),(0,h.__decorate)([(0,v.MZ)({attribute:"alert-type"})],f.prototype,"alertType",void 0),(0,h.__decorate)([(0,v.MZ)({type:Boolean})],f.prototype,"dismissable",void 0),(0,h.__decorate)([(0,v.MZ)({type:Boolean})],f.prototype,"narrow",void 0),f=(0,h.__decorate)([(0,v.EM)("ha-alert")],f)},16618:function(e,t,r){r.r(t),r.d(t,{HaQrCode:function(){return g}});var o,a,i,n=r(44734),s=r(56038),c=r(69683),l=r(6454),d=r(25460),h=(r(28706),r(62062),r(18111),r(61701),r(2892),r(26099),r(62826)),p=r(96196),v=r(77845),u=r(81298),y=(r(17963),r(99012)),m=e=>e,g=function(e){function t(){var e;(0,n.A)(this,t);for(var r=arguments.length,o=new Array(r),a=0;a<r;a++)o[a]=arguments[a];return(e=(0,c.A)(this,t,[].concat(o))).errorCorrectionLevel="medium",e.width=4,e.scale=4,e.margin=4,e}return(0,l.A)(t,e),(0,s.A)(t,[{key:"willUpdate",value:function(e){(0,d.A)(t,"willUpdate",this,3)([e]),(e.has("data")||e.has("scale")||e.has("width")||e.has("margin")||e.has("maskPattern")||e.has("errorCorrectionLevel"))&&this._error&&(this._error=void 0)}},{key:"updated",value:function(e){var t=this._canvas;if(t&&this.data&&(e.has("data")||e.has("scale")||e.has("width")||e.has("margin")||e.has("maskPattern")||e.has("errorCorrectionLevel")||e.has("centerImage"))){var r=getComputedStyle(this),o=r.getPropertyValue("--rgb-primary-text-color"),a=r.getPropertyValue("--rgb-card-background-color"),i=(0,y.v2)(o.split(",").map((e=>parseInt(e,10)))),n=(0,y.v2)(a.split(",").map((e=>parseInt(e,10))));if(u.toCanvas(t,this.data,{errorCorrectionLevel:this.errorCorrectionLevel||(this.centerImage?"Q":"M"),width:this.width,scale:this.scale,margin:this.margin,maskPattern:this.maskPattern,color:{light:n,dark:i}}).catch((e=>{this._error=e.message})),this.centerImage){var s=this._canvas.getContext("2d"),c=new Image;c.src=this.centerImage,c.onload=()=>{null==s||s.drawImage(c,.375*t.width,.375*t.height,t.width/4,t.height/4)}}}}},{key:"render",value:function(){return this.data?this._error?(0,p.qy)(o||(o=m`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):(0,p.qy)(a||(a=m`<canvas></canvas>`)):p.s6}}])}(p.WF);g.styles=(0,p.AH)(i||(i=m`
    :host {
      display: block;
    }
  `)),(0,h.__decorate)([(0,v.MZ)()],g.prototype,"data",void 0),(0,h.__decorate)([(0,v.MZ)({attribute:"error-correction-level"})],g.prototype,"errorCorrectionLevel",void 0),(0,h.__decorate)([(0,v.MZ)({type:Number})],g.prototype,"width",void 0),(0,h.__decorate)([(0,v.MZ)({type:Number})],g.prototype,"scale",void 0),(0,h.__decorate)([(0,v.MZ)({type:Number})],g.prototype,"margin",void 0),(0,h.__decorate)([(0,v.MZ)({attribute:!1,type:Number})],g.prototype,"maskPattern",void 0),(0,h.__decorate)([(0,v.MZ)({attribute:"center-image"})],g.prototype,"centerImage",void 0),(0,h.__decorate)([(0,v.wk)()],g.prototype,"_error",void 0),(0,h.__decorate)([(0,v.P)("canvas")],g.prototype,"_canvas",void 0),g=(0,h.__decorate)([(0,v.EM)("ha-qr-code")],g)}}]);
//# sourceMappingURL=6247.c4e3a2dd05516f15.js.map