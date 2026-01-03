"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["8434"],{89600:function(e,t,r){r.a(e,(async function(e,t){try{var o=r(44734),a=r(56038),n=r(69683),i=r(25460),s=r(6454),h=r(62826),c=r(55262),p=r(96196),d=r(77845),l=e([c]);c=(l.then?(await l)():l)[0];var u,v=e=>e,y=function(e){function t(){return(0,o.A)(this,t),(0,n.A)(this,t,arguments)}return(0,s.A)(t,e),(0,a.A)(t,[{key:"updated",value:function(e){if((0,i.A)(t,"updated",this,3)([e]),e.has("size"))switch(this.size){case"tiny":this.style.setProperty("--ha-spinner-size","16px");break;case"small":this.style.setProperty("--ha-spinner-size","28px");break;case"medium":this.style.setProperty("--ha-spinner-size","48px");break;case"large":this.style.setProperty("--ha-spinner-size","68px");break;case void 0:this.style.removeProperty("--ha-progress-ring-size")}}}],[{key:"styles",get:function(){return[c.A.styles,(0,p.AH)(u||(u=v`
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
      `))]}}])}(c.A);(0,h.__decorate)([(0,d.MZ)()],y.prototype,"size",void 0),y=(0,h.__decorate)([(0,d.EM)("ha-spinner")],y),t()}catch(b){t(b)}}))},54393:function(e,t,r){r.a(e,(async function(e,o){try{r.r(t);var a=r(44734),n=r(56038),i=r(69683),s=r(6454),h=(r(28706),r(62826)),c=r(96196),p=r(77845),d=r(5871),l=r(89600),u=(r(371),r(45397),r(39396)),v=e([l]);l=(v.then?(await v)():v)[0];var y,b,g,f,k,x,m=e=>e,_=function(e){function t(){var e;(0,a.A)(this,t);for(var r=arguments.length,o=new Array(r),n=0;n<r;n++)o[n]=arguments[n];return(e=(0,i.A)(this,t,[].concat(o))).noToolbar=!1,e.rootnav=!1,e.narrow=!1,e}return(0,s.A)(t,e),(0,n.A)(t,[{key:"render",value:function(){var e;return(0,c.qy)(y||(y=m`
      ${0}
      <div class="content">
        <ha-spinner></ha-spinner>
        ${0}
      </div>
    `),this.noToolbar?"":(0,c.qy)(b||(b=m`<div class="toolbar">
            ${0}
          </div>`),this.rootnav||null!==(e=history.state)&&void 0!==e&&e.root?(0,c.qy)(g||(g=m`
                  <ha-menu-button
                    .hass=${0}
                    .narrow=${0}
                  ></ha-menu-button>
                `),this.hass,this.narrow):(0,c.qy)(f||(f=m`
                  <ha-icon-button-arrow-prev
                    .hass=${0}
                    @click=${0}
                  ></ha-icon-button-arrow-prev>
                `),this.hass,this._handleBack)),this.message?(0,c.qy)(k||(k=m`<div id="loading-text">${0}</div>`),this.message):c.s6)}},{key:"_handleBack",value:function(){(0,d.O)()}}],[{key:"styles",get:function(){return[u.RF,(0,c.AH)(x||(x=m`
        :host {
          display: block;
          height: 100%;
          background-color: var(--primary-background-color);
        }
        .toolbar {
          display: flex;
          align-items: center;
          font-size: var(--ha-font-size-xl);
          height: var(--header-height);
          padding: 8px 12px;
          pointer-events: none;
          background-color: var(--app-header-background-color);
          font-weight: var(--ha-font-weight-normal);
          color: var(--app-header-text-color, white);
          border-bottom: var(--app-header-border-bottom, none);
          box-sizing: border-box;
        }
        @media (max-width: 599px) {
          .toolbar {
            padding: 4px;
          }
        }
        ha-menu-button,
        ha-icon-button-arrow-prev {
          pointer-events: auto;
        }
        .content {
          height: calc(100% - var(--header-height));
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
        }
        #loading-text {
          max-width: 350px;
          margin-top: 16px;
        }
      `))]}}])}(c.WF);(0,h.__decorate)([(0,p.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean,attribute:"no-toolbar"})],_.prototype,"noToolbar",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean})],_.prototype,"rootnav",void 0),(0,h.__decorate)([(0,p.MZ)({type:Boolean})],_.prototype,"narrow",void 0),(0,h.__decorate)([(0,p.MZ)()],_.prototype,"message",void 0),_=(0,h.__decorate)([(0,p.EM)("hass-loading-screen")],_),o()}catch(w){o(w)}}))}}]);
//# sourceMappingURL=8434.5e93bf32ca3015b0.js.map