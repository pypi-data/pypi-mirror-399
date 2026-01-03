"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["7787"],{45336:function(e,t,i){i.d(t,{H:function(){return m}});var a=i(31432),o=(i(2008),i(62062),i(26910),i(18111),i(22489),i(61701),i(2892),i(26099),i(27495),i(25440),e=>e.normalize("NFD").replace(/[\u0300-\u036F]/g,"")),r=(i(16280),i(44114),i(34782),i(38781),function(e){return e[e.Null=0]="Null",e[e.Backspace=8]="Backspace",e[e.Tab=9]="Tab",e[e.LineFeed=10]="LineFeed",e[e.CarriageReturn=13]="CarriageReturn",e[e.Space=32]="Space",e[e.ExclamationMark=33]="ExclamationMark",e[e.DoubleQuote=34]="DoubleQuote",e[e.Hash=35]="Hash",e[e.DollarSign=36]="DollarSign",e[e.PercentSign=37]="PercentSign",e[e.Ampersand=38]="Ampersand",e[e.SingleQuote=39]="SingleQuote",e[e.OpenParen=40]="OpenParen",e[e.CloseParen=41]="CloseParen",e[e.Asterisk=42]="Asterisk",e[e.Plus=43]="Plus",e[e.Comma=44]="Comma",e[e.Dash=45]="Dash",e[e.Period=46]="Period",e[e.Slash=47]="Slash",e[e.Digit0=48]="Digit0",e[e.Digit1=49]="Digit1",e[e.Digit2=50]="Digit2",e[e.Digit3=51]="Digit3",e[e.Digit4=52]="Digit4",e[e.Digit5=53]="Digit5",e[e.Digit6=54]="Digit6",e[e.Digit7=55]="Digit7",e[e.Digit8=56]="Digit8",e[e.Digit9=57]="Digit9",e[e.Colon=58]="Colon",e[e.Semicolon=59]="Semicolon",e[e.LessThan=60]="LessThan",e[e.Equals=61]="Equals",e[e.GreaterThan=62]="GreaterThan",e[e.QuestionMark=63]="QuestionMark",e[e.AtSign=64]="AtSign",e[e.A=65]="A",e[e.B=66]="B",e[e.C=67]="C",e[e.D=68]="D",e[e.E=69]="E",e[e.F=70]="F",e[e.G=71]="G",e[e.H=72]="H",e[e.I=73]="I",e[e.J=74]="J",e[e.K=75]="K",e[e.L=76]="L",e[e.M=77]="M",e[e.N=78]="N",e[e.O=79]="O",e[e.P=80]="P",e[e.Q=81]="Q",e[e.R=82]="R",e[e.S=83]="S",e[e.T=84]="T",e[e.U=85]="U",e[e.V=86]="V",e[e.W=87]="W",e[e.X=88]="X",e[e.Y=89]="Y",e[e.Z=90]="Z",e[e.OpenSquareBracket=91]="OpenSquareBracket",e[e.Backslash=92]="Backslash",e[e.CloseSquareBracket=93]="CloseSquareBracket",e[e.Caret=94]="Caret",e[e.Underline=95]="Underline",e[e.BackTick=96]="BackTick",e[e.a=97]="a",e[e.b=98]="b",e[e.c=99]="c",e[e.d=100]="d",e[e.e=101]="e",e[e.f=102]="f",e[e.g=103]="g",e[e.h=104]="h",e[e.i=105]="i",e[e.j=106]="j",e[e.k=107]="k",e[e.l=108]="l",e[e.m=109]="m",e[e.n=110]="n",e[e.o=111]="o",e[e.p=112]="p",e[e.q=113]="q",e[e.r=114]="r",e[e.s=115]="s",e[e.t=116]="t",e[e.u=117]="u",e[e.v=118]="v",e[e.w=119]="w",e[e.x=120]="x",e[e.y=121]="y",e[e.z=122]="z",e[e.OpenCurlyBrace=123]="OpenCurlyBrace",e[e.Pipe=124]="Pipe",e[e.CloseCurlyBrace=125]="CloseCurlyBrace",e[e.Tilde=126]="Tilde",e}({})),n=128;function s(){for(var e=[],t=[],i=0;i<=n;i++)t[i]=0;for(var a=0;a<=n;a++)e.push(t.slice(0));return e}function l(e,t){if(t<0||t>=e.length)return!1;var i,a=e.codePointAt(t);switch(a){case r.Underline:case r.Dash:case r.Period:case r.Space:case r.Slash:case r.Backslash:case r.SingleQuote:case r.DoubleQuote:case r.Colon:case r.DollarSign:case r.LessThan:case r.OpenParen:case r.OpenSquareBracket:return!0;case void 0:return!1;default:return(i=a)>=127462&&i<=127487||8986===i||8987===i||9200===i||9203===i||i>=9728&&i<=10175||11088===i||11093===i||i>=127744&&i<=128591||i>=128640&&i<=128764||i>=128992&&i<=129003||i>=129280&&i<=129535||i>=129648&&i<=129750}}function d(e,t){if(t<0||t>=e.length)return!1;switch(e.charCodeAt(t)){case r.Space:case r.Tab:return!0;default:return!1}}function c(e,t,i){return t[e]!==i[e]}function h(e,t,i,a,o,r,s){var l=e.length>n?n:e.length,d=a.length>n?n:a.length;if(!(i>=l||r>=d||l-i>d-r)&&function(e,t,i,a,o,r){for(var n=arguments.length>6&&void 0!==arguments[6]&&arguments[6];t<i&&o<r;)e[t]===a[o]&&(n&&(u[t]=o),t+=1),o+=1;return t===i}(t,i,l,o,r,d,!0)){var h;!function(e,t,i,a,o,r){var n=e-1,s=t-1;for(;n>=i&&s>=a;)o[n]===r[s]&&(v[n]=s,n--),s--}(l,d,i,r,t,o);var _,m,b=1,x=[!1];for(h=1,_=i;_<l;h++,_++){var k=u[_],$=v[_],w=_+1<l?v[_+1]:d;for(b=k-r+1,m=k;m<w;b++,m++){var A=Number.MIN_SAFE_INTEGER,M=!1;m<=$&&(A=p(e,t,_,i,a,o,m,d,r,0===g[h-1][b-1],x));var C=0;A!==Number.MAX_SAFE_INTEGER&&(M=!0,C=A+f[h-1][b-1]);var D=m>k,H=D?f[h][b-1]+(g[h][b-1]>0?-5:0):0,V=m>k+1&&g[h][b-1]>0,S=V?f[h][b-2]+(g[h][b-2]>0?-5:0):0;if(V&&(!D||S>=H)&&(!M||S>=C))f[h][b]=S,y[h][b]=3,g[h][b]=0;else if(D&&(!M||H>=C))f[h][b]=H,y[h][b]=2,g[h][b]=0;else{if(!M)throw new Error("not possible");f[h][b]=C,y[h][b]=1,g[h][b]=g[h-1][b-1]+1}}}if(x[0]||s){h--,b--;for(var z=[f[h][b],r],q=0,L=0;h>=1;){var P=b;do{var Z=y[h][P];if(3===Z)P-=2;else{if(2!==Z)break;P-=1}}while(P>=1);q>1&&t[i+h-1]===o[r+b-1]&&!c(P+r-1,a,o)&&q+1>g[h][P]&&(P=b),P===b?q++:q=1,L||(L=P),h--,b=P-1,z.push(b)}d===l&&(z[0]+=2);var E=L-l;return z[0]-=E,z}}}function p(e,t,i,a,o,r,n,s,h,p,u){if(t[i]!==r[n])return Number.MIN_SAFE_INTEGER;var v=1,g=!1;return n===i-a?v=e[i]===o[n]?7:5:!c(n,o,r)||0!==n&&c(n-1,o,r)?!l(r,n)||0!==n&&l(r,n-1)?(l(r,n-1)||d(r,n-1))&&(v=5,g=!0):v=5:(v=e[i]===o[n]?7:5,g=!0),v>1&&i===a&&(u[0]=!0),g||(g=c(n,o,r)||l(r,n-1)||d(r,n-1)),i===a?n>h&&(v-=g?3:5):v+=p?g?2:0:g?0:1,n+1===s&&(v-=g?3:5),v}var u=_(256),v=_(256),g=s(),f=s(),y=s();function _(e){for(var t=[],i=0;i<=e;i++)t[i]=0;return t}var m=(e,t)=>t.map((t=>(t.score=((e,t)=>{var i,r=Number.NEGATIVE_INFINITY,n=(0,a.A)(t.strings);try{for(n.s();!(i=n.n()).done;){var s=i.value,l=h(e,o(e.toLowerCase()),0,s,o(s.toLowerCase()),0,!0);if(l){var d=0===l[0]?1:l[0];d>r&&(r=d)}}}catch(c){n.e(c)}finally{n.f()}if(r!==Number.NEGATIVE_INFINITY)return r})(e,t),t))).filter((e=>void 0!==e.score)).sort(((e,t)=>{var i=e.score,a=void 0===i?0:i,o=t.score,r=void 0===o?0:o;return a>r?-1:a<r?1:0}))},46757:function(e,t,i){var a,o,r,n,s,l=i(44734),d=i(56038),c=i(69683),h=i(6454),p=(i(28706),i(48980),i(62826)),u=i(96196),v=i(77845),g=i(94333),f=i(32288),y=i(4937),_=i(92542),m=(i(22598),i(60961),e=>e),b=function(e){function t(){var e;(0,l.A)(this,t);for(var i=arguments.length,a=new Array(i),o=0;o<i;o++)a[o]=arguments[o];return(e=(0,c.A)(this,t,[].concat(a))).disabled=!1,e.vertical=!1,e.hideOptionLabel=!1,e}return(0,h.A)(t,e),(0,d.A)(t,[{key:"_handleFocus",value:function(e){if(!this.disabled&&this.options&&e.target===e.currentTarget){var t=null!=this.value?this.options.findIndex((e=>e.value===this.value)):-1,i=-1!==t?t:0;this._focusOption(i)}}},{key:"_focusOption",value:function(e){this._activeIndex=e,this.requestUpdate(),this.updateComplete.then((()=>{var t,i=null===(t=this.shadowRoot)||void 0===t?void 0:t.querySelector(`#option-${this.options[e].value}`);null==i||i.focus()}))}},{key:"_handleBlur",value:function(e){this.contains(e.relatedTarget)||(this._activeIndex=void 0)}},{key:"_handleKeydown",value:function(e){var t;if(this.options&&!this.disabled){var i=null!==(t=this._activeIndex)&&void 0!==t?t:0;switch(e.key){case" ":case"Enter":if(null!=this._activeIndex){var a=this.options[this._activeIndex].value;this.value=a,(0,_.r)(this,"value-changed",{value:a})}break;case"ArrowUp":case"ArrowLeft":i=i<=0?this.options.length-1:i-1,this._focusOption(i);break;case"ArrowDown":case"ArrowRight":i=(i+1)%this.options.length,this._focusOption(i);break;default:return}e.preventDefault()}}},{key:"_handleOptionClick",value:function(e){if(!this.disabled){var t=e.target.value;this.value=t,(0,_.r)(this,"value-changed",{value:t})}}},{key:"_handleOptionMouseDown",value:function(e){var t;if(!this.disabled){e.preventDefault();var i=e.target.value;this._activeIndex=null===(t=this.options)||void 0===t?void 0:t.findIndex((e=>e.value===i))}}},{key:"_handleOptionMouseUp",value:function(e){e.preventDefault()}},{key:"_handleOptionFocus",value:function(e){var t;if(!this.disabled){var i=e.target.value;this._activeIndex=null===(t=this.options)||void 0===t?void 0:t.findIndex((e=>e.value===i))}}},{key:"render",value:function(){return(0,u.qy)(a||(a=m`
      <div
        class="container"
        role="radiogroup"
        aria-label=${0}
        @focus=${0}
        @blur=${0}
        @keydown=${0}
        ?disabled=${0}
      >
        ${0}
      </div>
    `),(0,f.J)(this.label),this._handleFocus,this._handleBlur,this._handleKeydown,this.disabled,this.options?(0,y.u)(this.options,(e=>e.value),(e=>this._renderOption(e))):u.s6)}},{key:"_renderOption",value:function(e){var t=this.value===e.value;return(0,u.qy)(o||(o=m`
      <div
        id=${0}
        class=${0}
        role="radio"
        tabindex=${0}
        .value=${0}
        aria-checked=${0}
        aria-label=${0}
        title=${0}
        @click=${0}
        @focus=${0}
        @mousedown=${0}
        @mouseup=${0}
      >
        <div class="content">
          ${0}
          ${0}
        </div>
      </div>
    `),`option-${e.value}`,(0,g.H)({option:!0,selected:t}),t?"0":"-1",e.value,t?"true":"false",(0,f.J)(e.label),(0,f.J)(e.label),this._handleOptionClick,this._handleOptionFocus,this._handleOptionMouseDown,this._handleOptionMouseUp,e.path?(0,u.qy)(r||(r=m`<ha-svg-icon .path=${0}></ha-svg-icon>`),e.path):e.icon||u.s6,e.label&&!this.hideOptionLabel?(0,u.qy)(n||(n=m`<span>${0}</span>`),e.label):u.s6)}}])}(u.WF);b.styles=(0,u.AH)(s||(s=m`
    :host {
      display: block;
      --control-select-color: var(--primary-color);
      --control-select-focused-opacity: 0.2;
      --control-select-selected-opacity: 1;
      --control-select-background: var(--disabled-color);
      --control-select-background-opacity: 0.2;
      --control-select-thickness: 40px;
      --control-select-border-radius: 10px;
      --control-select-padding: 4px;
      --control-select-button-border-radius: calc(
        var(--control-select-border-radius) - var(--control-select-padding)
      );
      --mdc-icon-size: 20px;
      height: var(--control-select-thickness);
      width: 100%;
      font-style: normal;
      font-weight: var(--ha-font-weight-medium);
      color: var(--primary-text-color);
      user-select: none;
      -webkit-tap-highlight-color: transparent;
      border-radius: var(--control-select-border-radius);
    }
    :host([vertical]) {
      width: var(--control-select-thickness);
      height: 100%;
    }
    .container {
      position: relative;
      height: 100%;
      width: 100%;
      transform: translateZ(0);
      display: flex;
      flex-direction: row;
      padding: var(--control-select-padding);
      box-sizing: border-box;
      outline: none;
      transition: box-shadow 180ms ease-in-out;
    }
    .container::before {
      position: absolute;
      content: "";
      top: 0;
      left: 0;
      height: 100%;
      width: 100%;
      background: var(--control-select-background);
      opacity: var(--control-select-background-opacity);
      border-radius: var(--control-select-border-radius);
    }

    .container > *:not(:last-child) {
      margin-right: var(--control-select-padding);
      margin-inline-end: var(--control-select-padding);
      margin-inline-start: initial;
      direction: var(--direction);
    }
    .container[disabled] {
      --control-select-color: var(--disabled-color);
      --control-select-focused-opacity: 0;
      color: var(--disabled-color);
    }

    .container[disabled] .option {
      cursor: not-allowed;
    }

    .option {
      cursor: pointer;
      position: relative;
      flex: 1;
      height: 100%;
      width: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: var(--control-select-button-border-radius);
      /* For safari border-radius overflow */
      z-index: 0;
      outline: none;
      transition: box-shadow 180ms ease-in-out;
    }
    .option:focus-visible {
      box-shadow: 0 0 0 2px var(--control-select-color);
    }
    .content > *:not(:last-child) {
      margin-bottom: 4px;
    }
    .option::before {
      position: absolute;
      content: "";
      top: 0;
      left: 0;
      height: 100%;
      width: 100%;
      background-color: var(--control-select-color);
      opacity: 0;
      border-radius: var(--control-select-button-border-radius);
      transition:
        background-color ease-in-out 180ms,
        opacity ease-in-out 80ms;
    }
    .option:hover::before {
      opacity: var(--control-select-focused-opacity);
    }
    .option.selected {
      color: white;
    }
    .option.selected::before {
      opacity: var(--control-select-selected-opacity);
    }
    .option .content {
      position: relative;
      pointer-events: none;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-direction: column;
      text-align: center;
      padding: 2px;
      width: 100%;
      box-sizing: border-box;
    }
    .option .content span {
      display: block;
      width: 100%;
      -webkit-hyphens: auto;
      -moz-hyphens: auto;
      hyphens: auto;
    }
    :host([vertical]) {
      width: var(--control-select-thickness);
      height: auto;
    }
    :host([vertical]) .container {
      flex-direction: column;
    }
    :host([vertical]) .container > *:not(:last-child) {
      margin-right: initial;
      margin-inline-end: initial;
      margin-bottom: var(--control-select-padding);
    }
  `)),(0,p.__decorate)([(0,v.MZ)({type:Boolean})],b.prototype,"disabled",void 0),(0,p.__decorate)([(0,v.MZ)({attribute:!1})],b.prototype,"options",void 0),(0,p.__decorate)([(0,v.MZ)()],b.prototype,"value",void 0),(0,p.__decorate)([(0,v.MZ)({type:Boolean,reflect:!0})],b.prototype,"vertical",void 0),(0,p.__decorate)([(0,v.MZ)({type:Boolean,attribute:"hide-option-label"})],b.prototype,"hideOptionLabel",void 0),(0,p.__decorate)([(0,v.MZ)({type:String})],b.prototype,"label",void 0),(0,p.__decorate)([(0,v.wk)()],b.prototype,"_activeIndex",void 0),b=(0,p.__decorate)([(0,v.EM)("ha-control-select")],b)},34811:function(e,t,i){i.d(t,{p:function(){return x}});var a,o,r,n,s=i(61397),l=i(50264),d=i(44734),c=i(56038),h=i(69683),p=i(6454),u=i(25460),v=(i(28706),i(62826)),g=i(96196),f=i(77845),y=i(94333),_=i(92542),m=i(99034),b=(i(60961),e=>e),x=function(e){function t(){var e;(0,d.A)(this,t);for(var i=arguments.length,a=new Array(i),o=0;o<i;o++)a[o]=arguments[o];return(e=(0,h.A)(this,t,[].concat(a))).expanded=!1,e.outlined=!1,e.leftChevron=!1,e.noCollapse=!1,e._showContent=e.expanded,e}return(0,p.A)(t,e),(0,c.A)(t,[{key:"render",value:function(){var e=this.noCollapse?g.s6:(0,g.qy)(a||(a=b`
          <ha-svg-icon
            .path=${0}
            class="summary-icon ${0}"
          ></ha-svg-icon>
        `),"M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z",(0,y.H)({expanded:this.expanded}));return(0,g.qy)(o||(o=b`
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
    `),(0,y.H)({expanded:this.expanded}),(0,y.H)({noCollapse:this.noCollapse}),this._toggleContainer,this._toggleContainer,this._focusChanged,this._focusChanged,this.noCollapse?-1:0,this.expanded,this.leftChevron?e:g.s6,this.header,this.secondary,this.leftChevron?g.s6:e,(0,y.H)({expanded:this.expanded}),this._handleTransitionEnd,!this.expanded,this._showContent?(0,g.qy)(r||(r=b`<slot></slot>`)):"")}},{key:"willUpdate",value:function(e){(0,u.A)(t,"willUpdate",this,3)([e]),e.has("expanded")&&(this._showContent=this.expanded,setTimeout((()=>{this._container.style.overflow=this.expanded?"initial":"hidden"}),300))}},{key:"_handleTransitionEnd",value:function(){this._container.style.removeProperty("height"),this._container.style.overflow=this.expanded?"initial":"hidden",this._showContent=this.expanded}},{key:"_toggleContainer",value:(i=(0,l.A)((0,s.A)().m((function e(t){var i,a;return(0,s.A)().w((function(e){for(;;)switch(e.n){case 0:if(!t.defaultPrevented){e.n=1;break}return e.a(2);case 1:if("keydown"!==t.type||"Enter"===t.key||" "===t.key){e.n=2;break}return e.a(2);case 2:if(t.preventDefault(),!this.noCollapse){e.n=3;break}return e.a(2);case 3:if(i=!this.expanded,(0,_.r)(this,"expanded-will-change",{expanded:i}),this._container.style.overflow="hidden",!i){e.n=4;break}return this._showContent=!0,e.n=4,(0,m.E)();case 4:a=this._container.scrollHeight,this._container.style.height=`${a}px`,i||setTimeout((()=>{this._container.style.height="0px"}),0),this.expanded=i,(0,_.r)(this,"expanded-changed",{expanded:this.expanded});case 5:return e.a(2)}}),e,this)}))),function(e){return i.apply(this,arguments)})},{key:"_focusChanged",value:function(e){this.noCollapse||this.shadowRoot.querySelector(".top").classList.toggle("focused","focus"===e.type)}}]);var i}(g.WF);x.styles=(0,g.AH)(n||(n=b`
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
  `)),(0,v.__decorate)([(0,f.MZ)({type:Boolean,reflect:!0})],x.prototype,"expanded",void 0),(0,v.__decorate)([(0,f.MZ)({type:Boolean,reflect:!0})],x.prototype,"outlined",void 0),(0,v.__decorate)([(0,f.MZ)({attribute:"left-chevron",type:Boolean,reflect:!0})],x.prototype,"leftChevron",void 0),(0,v.__decorate)([(0,f.MZ)({attribute:"no-collapse",type:Boolean,reflect:!0})],x.prototype,"noCollapse",void 0),(0,v.__decorate)([(0,f.MZ)()],x.prototype,"header",void 0),(0,v.__decorate)([(0,f.MZ)()],x.prototype,"secondary",void 0),(0,v.__decorate)([(0,f.wk)()],x.prototype,"_showContent",void 0),(0,v.__decorate)([(0,f.P)(".container")],x.prototype,"_container",void 0),x=(0,v.__decorate)([(0,f.EM)("ha-expansion-panel")],x)},70748:function(e,t,i){var a,o,r,n=i(44734),s=i(56038),l=i(69683),d=i(25460),c=i(6454),h=i(62826),p=i(51978),u=i(94743),v=i(77845),g=i(96196),f=i(76679),y=e=>e,_=function(e){function t(){return(0,n.A)(this,t),(0,l.A)(this,t,arguments)}return(0,c.A)(t,e),(0,s.A)(t,[{key:"firstUpdated",value:function(e){(0,d.A)(t,"firstUpdated",this,3)([e]),this.style.setProperty("--mdc-theme-secondary","var(--primary-color)")}}])}(p.n);_.styles=[u.R,(0,g.AH)(a||(a=y`
      :host {
        --mdc-typography-button-text-transform: none;
        --mdc-typography-button-font-size: var(--ha-font-size-l);
        --mdc-typography-button-font-family: var(--ha-font-family-body);
        --mdc-typography-button-font-weight: var(--ha-font-weight-medium);
      }
      :host .mdc-fab--extended {
        border-radius: var(
          --ha-button-border-radius,
          var(--ha-border-radius-pill)
        );
      }
      :host .mdc-fab.mdc-fab--extended .ripple {
        border-radius: var(
          --ha-button-border-radius,
          var(--ha-border-radius-pill)
        );
      }
      :host .mdc-fab--extended .mdc-fab__icon {
        margin-inline-start: -8px;
        margin-inline-end: 12px;
        direction: var(--direction);
      }
      :disabled {
        --mdc-theme-secondary: var(--disabled-text-color);
        pointer-events: none;
      }
    `)),"rtl"===f.G.document.dir?(0,g.AH)(o||(o=y`
          :host .mdc-fab--extended .mdc-fab__icon {
            direction: rtl;
          }
        `)):(0,g.AH)(r||(r=y``))],_=(0,h.__decorate)([(0,v.EM)("ha-fab")],_)},95096:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t),i.d(t,{HaNumberSelector:function(){return x}});var o=i(44734),r=i(56038),n=i(69683),s=i(6454),l=(i(28706),i(2892),i(26099),i(38781),i(62826)),d=i(96196),c=i(77845),h=i(94333),p=i(92542),u=(i(56768),i(60808)),v=(i(78740),e([u]));u=(v.then?(await v)():v)[0];var g,f,y,_,m,b=e=>e,x=function(e){function t(){var e;(0,o.A)(this,t);for(var i=arguments.length,a=new Array(i),r=0;r<i;r++)a[r]=arguments[r];return(e=(0,n.A)(this,t,[].concat(a))).required=!0,e.disabled=!1,e._valueStr="",e}return(0,s.A)(t,e),(0,r.A)(t,[{key:"willUpdate",value:function(e){e.has("value")&&(""!==this._valueStr&&this.value===Number(this._valueStr)||(this._valueStr=null==this.value||isNaN(this.value)?"":this.value.toString()))}},{key:"render",value:function(){var e,t,i,a,o,r,n,s,l,c,p,u,v,m,x,k,$="box"===(null===(e=this.selector.number)||void 0===e?void 0:e.mode)||void 0===(null===(t=this.selector.number)||void 0===t?void 0:t.min)||void 0===(null===(i=this.selector.number)||void 0===i?void 0:i.max);if(!$&&"any"===(x=null!==(k=this.selector.number.step)&&void 0!==k?k:1)){x=1;for(var w=(this.selector.number.max-this.selector.number.min)/100;x>w;)x/=10}var A=null===(a=this.selector.number)||void 0===a?void 0:a.translation_key,M=null===(o=this.selector.number)||void 0===o?void 0:o.unit_of_measurement;return $&&M&&this.localizeValue&&A&&(M=this.localizeValue(`${A}.unit_of_measurement.${M}`)||M),(0,d.qy)(g||(g=b`
      ${0}
      <div class="input">
        ${0}
        <ha-textfield
          .inputMode=${0}
          .label=${0}
          .placeholder=${0}
          class=${0}
          .min=${0}
          .max=${0}
          .value=${0}
          .step=${0}
          helperPersistent
          .helper=${0}
          .disabled=${0}
          .required=${0}
          .suffix=${0}
          type="number"
          autoValidate
          ?no-spinner=${0}
          @input=${0}
        >
        </ha-textfield>
      </div>
      ${0}
    `),this.label&&!$?(0,d.qy)(f||(f=b`${0}${0}`),this.label,this.required?"*":""):d.s6,$?d.s6:(0,d.qy)(y||(y=b`
              <ha-slider
                labeled
                .min=${0}
                .max=${0}
                .value=${0}
                .step=${0}
                .disabled=${0}
                .required=${0}
                @change=${0}
                .withMarkers=${0}
              >
              </ha-slider>
            `),this.selector.number.min,this.selector.number.max,this.value,x,this.disabled,this.required,this._handleSliderChange,(null===(r=this.selector.number)||void 0===r?void 0:r.slider_ticks)||!1),"any"===(null===(n=this.selector.number)||void 0===n?void 0:n.step)||(null!==(s=null===(l=this.selector.number)||void 0===l?void 0:l.step)&&void 0!==s?s:1)%1!=0?"decimal":"numeric",$?this.label:void 0,this.placeholder,(0,h.H)({single:$}),null===(c=this.selector.number)||void 0===c?void 0:c.min,null===(p=this.selector.number)||void 0===p?void 0:p.max,null!==(u=this._valueStr)&&void 0!==u?u:"",null!==(v=null===(m=this.selector.number)||void 0===m?void 0:m.step)&&void 0!==v?v:1,$?this.helper:void 0,this.disabled,this.required,M,!$,this._handleInputChange,!$&&this.helper?(0,d.qy)(_||(_=b`<ha-input-helper-text .disabled=${0}
            >${0}</ha-input-helper-text
          >`),this.disabled,this.helper):d.s6)}},{key:"_handleInputChange",value:function(e){e.stopPropagation(),this._valueStr=e.target.value;var t=""===e.target.value||isNaN(e.target.value)?void 0:Number(e.target.value);this.value!==t&&(0,p.r)(this,"value-changed",{value:t})}},{key:"_handleSliderChange",value:function(e){e.stopPropagation();var t=Number(e.target.value);this.value!==t&&(0,p.r)(this,"value-changed",{value:t})}}])}(d.WF);x.styles=(0,d.AH)(m||(m=b`
    .input {
      display: flex;
      justify-content: space-between;
      align-items: center;
      direction: ltr;
    }
    ha-slider {
      flex: 1;
      margin-right: 16px;
      margin-inline-end: 16px;
      margin-inline-start: 0;
    }
    ha-textfield {
      --ha-textfield-input-width: 40px;
    }
    .single {
      --ha-textfield-input-width: unset;
      flex: 1;
    }
  `)),(0,l.__decorate)([(0,c.MZ)({attribute:!1})],x.prototype,"hass",void 0),(0,l.__decorate)([(0,c.MZ)({attribute:!1})],x.prototype,"selector",void 0),(0,l.__decorate)([(0,c.MZ)({type:Number})],x.prototype,"value",void 0),(0,l.__decorate)([(0,c.MZ)({type:Number})],x.prototype,"placeholder",void 0),(0,l.__decorate)([(0,c.MZ)()],x.prototype,"label",void 0),(0,l.__decorate)([(0,c.MZ)()],x.prototype,"helper",void 0),(0,l.__decorate)([(0,c.MZ)({attribute:!1})],x.prototype,"localizeValue",void 0),(0,l.__decorate)([(0,c.MZ)({type:Boolean})],x.prototype,"required",void 0),(0,l.__decorate)([(0,c.MZ)({type:Boolean})],x.prototype,"disabled",void 0),x=(0,l.__decorate)([(0,c.EM)("ha-selector-number")],x),a()}catch(k){a(k)}}))},2809:function(e,t,i){var a,o,r=i(44734),n=i(56038),s=i(69683),l=i(6454),d=(i(28706),i(62826)),c=i(96196),h=i(77845),p=e=>e,u=function(e){function t(){var e;(0,r.A)(this,t);for(var i=arguments.length,a=new Array(i),o=0;o<i;o++)a[o]=arguments[o];return(e=(0,s.A)(this,t,[].concat(a))).narrow=!1,e.slim=!1,e.threeLine=!1,e.wrapHeading=!1,e}return(0,l.A)(t,e),(0,n.A)(t,[{key:"render",value:function(){return(0,c.qy)(a||(a=p`
      <div class="prefix-wrap">
        <slot name="prefix"></slot>
        <div
          class="body"
          ?two-line=${0}
          ?three-line=${0}
        >
          <slot name="heading"></slot>
          <div class="secondary"><slot name="description"></slot></div>
        </div>
      </div>
      <div class="content"><slot></slot></div>
    `),!this.threeLine,this.threeLine)}}])}(c.WF);u.styles=(0,c.AH)(o||(o=p`
    :host {
      display: flex;
      padding: 0 16px;
      align-content: normal;
      align-self: auto;
      align-items: center;
    }
    .body {
      padding-top: 8px;
      padding-bottom: 8px;
      padding-left: 0;
      padding-inline-start: 0;
      padding-right: 16px;
      padding-inline-end: 16px;
      overflow: hidden;
      display: var(--layout-vertical_-_display, flex);
      flex-direction: var(--layout-vertical_-_flex-direction, column);
      justify-content: var(--layout-center-justified_-_justify-content, center);
      flex: var(--layout-flex_-_flex, 1);
      flex-basis: var(--layout-flex_-_flex-basis, 0.000000001px);
    }
    .body[three-line] {
      min-height: 88px;
    }
    :host(:not([wrap-heading])) body > * {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .body > .secondary {
      display: block;
      padding-top: 4px;
      font-family: var(
        --mdc-typography-body2-font-family,
        var(--mdc-typography-font-family, var(--ha-font-family-body))
      );
      font-size: var(--mdc-typography-body2-font-size, var(--ha-font-size-s));
      -webkit-font-smoothing: var(--ha-font-smoothing);
      -moz-osx-font-smoothing: var(--ha-moz-osx-font-smoothing);
      font-weight: var(
        --mdc-typography-body2-font-weight,
        var(--ha-font-weight-normal)
      );
      line-height: normal;
      color: var(--secondary-text-color);
    }
    .body[two-line] {
      min-height: calc(72px - 16px);
      flex: 1;
    }
    .content {
      display: contents;
    }
    :host(:not([narrow])) .content {
      display: var(--settings-row-content-display, flex);
      justify-content: flex-end;
      flex: 1;
      min-width: 0;
      padding: 16px 0;
    }
    .content ::slotted(*) {
      width: var(--settings-row-content-width);
    }
    :host([narrow]) {
      align-items: normal;
      flex-direction: column;
      border-top: 1px solid var(--divider-color);
      padding-bottom: 8px;
    }
    ::slotted(ha-switch) {
      padding: 16px 0;
    }
    .secondary {
      white-space: normal;
    }
    .prefix-wrap {
      display: var(--settings-row-prefix-display);
    }
    :host([narrow]) .prefix-wrap {
      display: flex;
      align-items: center;
    }
    :host([slim]),
    :host([slim]) .content,
    :host([slim]) ::slotted(ha-switch) {
      padding: 0;
    }
    :host([slim]) .body {
      min-height: 0;
    }
  `)),(0,d.__decorate)([(0,h.MZ)({type:Boolean,reflect:!0})],u.prototype,"narrow",void 0),(0,d.__decorate)([(0,h.MZ)({type:Boolean,reflect:!0})],u.prototype,"slim",void 0),(0,d.__decorate)([(0,h.MZ)({type:Boolean,attribute:"three-line"})],u.prototype,"threeLine",void 0),(0,d.__decorate)([(0,h.MZ)({type:Boolean,attribute:"wrap-heading",reflect:!0})],u.prototype,"wrapHeading",void 0),u=(0,d.__decorate)([(0,h.EM)("ha-settings-row")],u)},60808:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(44734),o=i(56038),r=i(69683),n=i(6454),s=i(25460),l=(i(28706),i(62826)),d=i(60346),c=i(96196),h=i(77845),p=i(76679),u=e([d]);d=(u.then?(await u)():u)[0];var v,g=e=>e,f=function(e){function t(){var e;(0,a.A)(this,t);for(var i=arguments.length,o=new Array(i),n=0;n<i;n++)o[n]=arguments[n];return(e=(0,r.A)(this,t,[].concat(o))).size="small",e.withTooltip=!0,e}return(0,n.A)(t,e),(0,o.A)(t,[{key:"connectedCallback",value:function(){(0,s.A)(t,"connectedCallback",this,3)([]),this.dir=p.G.document.dir}}],[{key:"styles",get:function(){return[d.A.styles,(0,c.AH)(v||(v=g`
        :host {
          --track-size: var(--ha-slider-track-size, 4px);
          --marker-height: calc(var(--ha-slider-track-size, 4px) / 2);
          --marker-width: calc(var(--ha-slider-track-size, 4px) / 2);
          --wa-color-surface-default: var(--card-background-color);
          --wa-color-neutral-fill-normal: var(--disabled-color);
          --wa-tooltip-background-color: var(--secondary-background-color);
          --wa-tooltip-color: var(--primary-text-color);
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
          min-width: 100px;
          min-inline-size: 100px;
          width: 200px;
        }

        #thumb {
          border: none;
          background-color: var(--ha-slider-thumb-color, var(--primary-color));
        }

        #thumb:after {
          content: "";
          border-radius: 50%;
          position: absolute;
          width: calc(var(--thumb-width) * 2 + 8px);
          height: calc(var(--thumb-height) * 2 + 8px);
          left: calc(-50% - 4px);
          top: calc(-50% - 4px);
          cursor: pointer;
        }

        #slider:focus-visible:not(.disabled) #thumb,
        #slider:focus-visible:not(.disabled) #thumb-min,
        #slider:focus-visible:not(.disabled) #thumb-max {
          outline: var(--wa-focus-ring);
        }

        #track:after {
          content: "";
          position: absolute;
          top: calc(-50% - 4px);
          left: 0;
          width: 100%;
          height: calc(var(--track-size) * 2 + 8px);
          cursor: pointer;
        }

        #indicator {
          background-color: var(
            --ha-slider-indicator-color,
            var(--primary-color)
          );
        }

        :host([size="medium"]) {
          --thumb-width: 20px;
          --thumb-height: 20px;
        }

        :host([size="small"]) {
          --thumb-width: 16px;
          --thumb-height: 16px;
        }
      `))]}}])}(d.A);(0,l.__decorate)([(0,h.MZ)({reflect:!0})],f.prototype,"size",void 0),(0,l.__decorate)([(0,h.MZ)({type:Boolean,attribute:"with-tooltip"})],f.prototype,"withTooltip",void 0),f=(0,l.__decorate)([(0,h.EM)("ha-slider")],f),t()}catch(y){t(y)}}))},7153:function(e,t,i){var a,o=i(44734),r=i(56038),n=i(69683),s=i(6454),l=i(25460),d=(i(28706),i(62826)),c=i(4845),h=i(49065),p=i(96196),u=i(77845),v=i(7647),g=function(e){function t(){var e;(0,o.A)(this,t);for(var i=arguments.length,a=new Array(i),r=0;r<i;r++)a[r]=arguments[r];return(e=(0,n.A)(this,t,[].concat(a))).haptic=!1,e}return(0,s.A)(t,e),(0,r.A)(t,[{key:"firstUpdated",value:function(){(0,l.A)(t,"firstUpdated",this,3)([]),this.addEventListener("change",(()=>{this.haptic&&(0,v.j)(this,"light")}))}}])}(c.U);g.styles=[h.R,(0,p.AH)(a||(a=(e=>e)`
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
    `))],(0,d.__decorate)([(0,u.MZ)({type:Boolean})],g.prototype,"haptic",void 0),g=(0,d.__decorate)([(0,u.EM)("ha-switch")],g)},7647:function(e,t,i){i.d(t,{j:function(){return o}});var a=i(92542),o=(e,t)=>{(0,a.r)(e,"haptic",t)}},54393:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t);var o=i(44734),r=i(56038),n=i(69683),s=i(6454),l=(i(28706),i(62826)),d=i(96196),c=i(77845),h=i(5871),p=i(89600),u=(i(371),i(45397),i(39396)),v=e([p]);p=(v.then?(await v)():v)[0];var g,f,y,_,m,b,x=e=>e,k=function(e){function t(){var e;(0,o.A)(this,t);for(var i=arguments.length,a=new Array(i),r=0;r<i;r++)a[r]=arguments[r];return(e=(0,n.A)(this,t,[].concat(a))).noToolbar=!1,e.rootnav=!1,e.narrow=!1,e}return(0,s.A)(t,e),(0,r.A)(t,[{key:"render",value:function(){var e;return(0,d.qy)(g||(g=x`
      ${0}
      <div class="content">
        <ha-spinner></ha-spinner>
        ${0}
      </div>
    `),this.noToolbar?"":(0,d.qy)(f||(f=x`<div class="toolbar">
            ${0}
          </div>`),this.rootnav||null!==(e=history.state)&&void 0!==e&&e.root?(0,d.qy)(y||(y=x`
                  <ha-menu-button
                    .hass=${0}
                    .narrow=${0}
                  ></ha-menu-button>
                `),this.hass,this.narrow):(0,d.qy)(_||(_=x`
                  <ha-icon-button-arrow-prev
                    .hass=${0}
                    @click=${0}
                  ></ha-icon-button-arrow-prev>
                `),this.hass,this._handleBack)),this.message?(0,d.qy)(m||(m=x`<div id="loading-text">${0}</div>`),this.message):d.s6)}},{key:"_handleBack",value:function(){(0,h.O)()}}],[{key:"styles",get:function(){return[u.RF,(0,d.AH)(b||(b=x`
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
      `))]}}])}(d.WF);(0,l.__decorate)([(0,c.MZ)({attribute:!1})],k.prototype,"hass",void 0),(0,l.__decorate)([(0,c.MZ)({type:Boolean,attribute:"no-toolbar"})],k.prototype,"noToolbar",void 0),(0,l.__decorate)([(0,c.MZ)({type:Boolean})],k.prototype,"rootnav",void 0),(0,l.__decorate)([(0,c.MZ)({type:Boolean})],k.prototype,"narrow",void 0),(0,l.__decorate)([(0,c.MZ)()],k.prototype,"message",void 0),k=(0,l.__decorate)([(0,c.EM)("hass-loading-screen")],k),a()}catch($){a($)}}))},25879:function(e,t,i){i.a(e,(async function(e,a){try{i.d(t,{Y:function(){return v}});var o=i(96196),r=(i(17963),i(95379),i(34811),i(70105)),n=i(81774),s=i(75877),l=i(53003),d=i(76674),c=e([r,n,s]);[r,n,s]=c.then?(await c)():c;var h,p,u=e=>e,v=function(e,t,i,a){var r,n,s=arguments.length>4&&void 0!==arguments[4]?arguments[4]:e=>e,c=t.device_info?(0,l.OM)(e,t.device_info):void 0,v=c?null!==(r=c.name_by_user)&&void 0!==r?r:c.name:"",g=(0,d.W)(a);return(0,o.qy)(h||(h=u`
    <ha-card outlined>
      <h1 class="card-header">${0}</h1>
      <p class="card-content">${0}</p>
      ${0}
      <ha-expansion-panel
        header=${0}
        secondary=${0}
        expanded
        .noCollapse=${0}
      >
        <knx-device-picker
          .hass=${0}
          .key=${0}
          .helper=${0}
          .value=${0}
          @value-changed=${0}
        ></knx-device-picker>
        <ha-selector-text
          .hass=${0}
          label=${0}
          helper=${0}
          .required=${0}
          .selector=${0}
          .key=${0}
          .value=${0}
          @value-changed=${0}
        ></ha-selector-text>
      </ha-expansion-panel>
      <ha-expansion-panel .header=${0} outlined>
        <ha-selector-select
          .hass=${0}
          .label=${0}
          .helper=${0}
          .required=${0}
          .selector=${0}
          .key=${0}
          .value=${0}
          @value-changed=${0}
        ></ha-selector-select>
      </ha-expansion-panel>
    </ha-card>
  `),s("entity.title"),s("entity.description"),a&&g?(0,o.qy)(p||(p=u`<ha-alert
              .alertType=${0}
              .title=${0}
            ></ha-alert>`),"error",g.error_message):o.s6,s("entity.name_title"),s("entity.name_description"),!0,e,"entity.device_info",s("entity.device_description"),null!==(n=t.device_info)&&void 0!==n?n:void 0,i,e,s("entity.entity_label"),s("entity.entity_description"),!c,{text:{type:"text",prefix:v}},"entity.name",t.name,i,s("entity.entity_category_title"),e,s("entity.entity_category_title"),s("entity.entity_category_description"),!1,{select:{multiple:!1,custom_value:!1,mode:"dropdown",options:[{value:"config",label:e.localize("ui.panel.config.devices.entities.config")},{value:"diagnostic",label:e.localize("ui.panel.config.devices.entities.diagnostic")}]}},"entity.entity_category",t.entity_category,i)};a()}catch(g){a(g)}}))},66820:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(94741),o=i(31432),r=i(78261),n=i(44734),s=i(56038),l=i(69683),d=i(6454),c=i(25460),h=(i(28706),i(48980),i(74423),i(23792),i(62062),i(44114),i(18111),i(81148),i(7588),i(61701),i(13579),i(5506),i(53921),i(26099),i(27495),i(38781),i(5746),i(23500),i(62953),i(48408),i(14603),i(47566),i(98721),i(62826)),p=i(96196),u=i(77845),v=i(52682),g=i(29485),f=(i(17963),i(95379),i(46757),i(60961),i(34811),i(87156),i(2809),i(76679)),y=i(92542),_=(i(18239),i(77812),i(35672)),m=i(25879),b=i(78577),x=i(13384),k=i(76674),$=i(36376),w=e([_,$,m]);[_,$,m]=w.then?(await w)():w;var A,M,C,D,H,V,S,z,q,L,P,Z,E=e=>e,T=new b.Q("knx-configure-entity"),O=function(e){function t(){var e;(0,n.A)(this,t);for(var i=arguments.length,a=new Array(i),o=0;o<i;o++)a[o]=arguments[o];return(e=(0,l.A)(this,t,[].concat(a)))._selectedGroupSelectOptions={},e._backendLocalize=t=>e.hass.localize(`component.knx.config_panel.entities.create.${e.platform}.${t}`)||e.hass.localize(`component.knx.config_panel.entities.create._.${t}`),e}return(0,d.A)(t,e),(0,s.A)(t,[{key:"connectedCallback",value:function(){if((0,c.A)(t,"connectedCallback",this,3)([]),this.platformStyle=(0,$.N)(this.platform),!this.config){this.config={entity:{},knx:{}};for(var e=new URLSearchParams(f.G.location.search),i=Object.fromEntries(e.entries()),a=0,o=Object.entries(i);a<o.length;a++){var n=(0,r.A)(o[a],2),s=n[0],l=n[1];(0,x.F)(this.config,s,l,T),(0,y.r)(this,"knx-entity-configuration-changed",this.config)}}}},{key:"render",value:function(){var e,t=(0,k.a)(this.validationErrors,"data"),i=(0,k.a)(t,"knx"),a=(0,k.W)(i);return(0,p.qy)(A||(A=E`
      <div class="header">
        <h1>
          <ha-svg-icon
            .path=${0}
            style=${0}
          ></ha-svg-icon>
          ${0}
        </h1>
        <p>${0}</p>
      </div>
      <slot name="knx-validation-error"></slot>
      <ha-card outlined>
        <h1 class="card-header">${0}</h1>
        ${0}
        ${0}
      </ha-card>
      ${0}
    `),this.platformStyle.iconPath,(0,g.W)({"background-color":this.platformStyle.color}),this.hass.localize(`component.${this.platform}.title`)||this.platform,this._backendLocalize("description"),this._backendLocalize("knx.title"),a?(0,p.qy)(M||(M=E`<ha-alert .alertType=${0} .title=${0}></ha-alert>`),"error",a.error_message):p.s6,this.generateRootGroups(this.schema,i),(0,m.Y)(this.hass,null!==(e=this.config.entity)&&void 0!==e?e:{},this._updateConfig,(0,k.a)(t,"entity"),this._backendLocalize))}},{key:"generateRootGroups",value:function(e,t){return this._generateItems(e,"knx",t)}},{key:"_generateSection",value:function(e,t,i){var a=(0,k.W)(i);return(0,p.qy)(C||(C=E` <ha-expansion-panel
      .header=${0}
      .secondary=${0}
      .expanded=${0}
      .noCollapse=${0}
      .outlined=${0}
    >
      ${0}
      ${0}
    </ha-expansion-panel>`),this._backendLocalize(`${t}.title`),this._backendLocalize(`${t}.description`),!e.collapsible||this._groupHasGroupAddressInConfig(e,t),!e.collapsible,!!e.collapsible,a?(0,p.qy)(D||(D=E` <ha-alert .alertType=${0} .title=${0}>
            ${0}
          </ha-alert>`),"error","Validation error",a.error_message):p.s6,this._generateItems(e.schema,t,i))}},{key:"_generateGroupSelect",value:function(e,t,i){var a=(0,k.W)(i);t in this._selectedGroupSelectOptions||(this._selectedGroupSelectOptions[t]=this._getOptionIndex(e,t));var o=this._selectedGroupSelectOptions[t],r=e.schema[o];void 0===r&&T.error("No option for index",o,e.schema);var n=e.schema.map(((e,i)=>({value:i.toString(),label:this._backendLocalize(`${t}.options.${e.translation_key}.label`)})));return(0,p.qy)(H||(H=E` <ha-expansion-panel
      .header=${0}
      .secondary=${0}
      .expanded=${0}
      .noCollapse=${0}
      outlined
    >
      ${0}
      <ha-control-select
        .options=${0}
        .value=${0}
        .key=${0}
        @value-changed=${0}
      ></ha-control-select>
      ${0}
    </ha-expansion-panel>`),this._backendLocalize(`${t}.title`),this._backendLocalize(`${t}.description`),!e.collapsible||this._groupHasGroupAddressInConfig(e,t),!e.collapsible,a?(0,p.qy)(V||(V=E` <ha-alert .alertType=${0} .title=${0}>
            ${0}
          </ha-alert>`),"error","Validation error",a.error_message):p.s6,n,o.toString(),t,this._updateGroupSelectOption,r?(0,p.qy)(S||(S=E` <p class="group-description">
              ${0}
            </p>
            <div class="group-selection">
              ${0}
            </div>`),this._backendLocalize(`${t}.options.${r.translation_key}.description`),(0,v.D)(o,this._generateItems(r.schema,t,i))):p.s6)}},{key:"_generateItems",value:function(e,t,i){var a,r,n=[],s=[],l=()=>{if(0!==s.length&&void 0!==a){var e=t+"."+a.name,o=!a.collapsible||s.some((e=>"knx_group_address"===e.type&&this._hasGroupAddressInConfig(e,t)));n.push((0,p.qy)(z||(z=E`<ha-expansion-panel
          .header=${0}
          .secondary=${0}
          .expanded=${0}
          .noCollapse=${0}
          .outlined=${0}
        >
          ${0}
        </ha-expansion-panel> `),this._backendLocalize(`${e}.title`),this._backendLocalize(`${e}.description`),o,!a.collapsible,!!a.collapsible,s.map((e=>this._generateItem(e,t,i))))),s=[]}},d=(0,o.A)(e);try{for(d.s();!(r=d.n()).done;){var c=r.value;"knx_section_flat"!==c.type?(["knx_section","knx_group_select","knx_sync_state"].includes(c.type)&&(l(),a=void 0),void 0===a?n.push(this._generateItem(c,t,i)):s.push(c)):(l(),a=c)}}catch(h){d.e(h)}finally{d.f()}return l(),n}},{key:"_generateItem",value:function(e,t,i){var a,o,r=t+"."+e.name,n=(0,k.a)(i,e.name);switch(e.type){case"knx_section":return this._generateSection(e,r,n);case"knx_group_select":return this._generateGroupSelect(e,r,n);case"knx_group_address":return(0,p.qy)(q||(q=E`
          <knx-group-address-selector
            .hass=${0}
            .knx=${0}
            .key=${0}
            .required=${0}
            .label=${0}
            .config=${0}
            .options=${0}
            .validationErrors=${0}
            .localizeFunction=${0}
            @value-changed=${0}
          ></knx-group-address-selector>
        `),this.hass,this.knx,r,e.required,this._backendLocalize(`${r}.label`),null!==(a=(0,x.L)(this.config,r))&&void 0!==a?a:{},e.options,n,this._backendLocalize,this._updateConfig);case"knx_sync_state":return(0,p.qy)(L||(L=E`
          <ha-expansion-panel
            .header=${0}
            .secondary=${0}
            .outlined=${0}
          >
            <knx-sync-state-selector-row
              .hass=${0}
              .key=${0}
              .value=${0}
              .allowFalse=${0}
              .localizeFunction=${0}
              @value-changed=${0}
            ></knx-sync-state-selector-row>
          </ha-expansion-panel>
        `),this._backendLocalize(`${r}.title`),this._backendLocalize(`${r}.description`),!0,this.hass,r,null===(o=(0,x.L)(this.config,r))||void 0===o||o,e.allow_false,this._backendLocalize,this._updateConfig);case"ha_selector":return(0,p.qy)(P||(P=E`
          <knx-selector-row
            .hass=${0}
            .key=${0}
            .selector=${0}
            .value=${0}
            .validationErrors=${0}
            .localizeFunction=${0}
            @value-changed=${0}
          ></knx-selector-row>
        `),this.hass,r,e,(0,x.L)(this.config,r),n,this._backendLocalize,this._updateConfig);default:return T.error("Unknown selector type",e),p.s6}}},{key:"_groupHasGroupAddressInConfig",value:function(e,t){return void 0!==this.config&&("knx_group_select"===e.type?!!(0,x.L)(this.config,t):e.schema.some((e=>{if("knx_group_address"===e.type)return this._hasGroupAddressInConfig(e,t);if("knx_section"===e.type||"knx_group_select"===e.type){var i=t+"."+e.name;return this._groupHasGroupAddressInConfig(e,i)}return!1})))}},{key:"_hasGroupAddressInConfig",value:function(e,t){var i,a=(0,x.L)(this.config,t+"."+e.name);return!!a&&(void 0!==a.write||(void 0!==a.state||!(null===(i=a.passive)||void 0===i||!i.length)))}},{key:"_getRequiredKeys",value:function(e){var t=[];return e.forEach((e=>{"knx_section"!==e.type?("knx_group_address"===e.type&&e.required||"ha_selector"===e.type&&e.required)&&t.push(e.name):t.push.apply(t,(0,a.A)(this._getRequiredKeys(e.schema)))})),t}},{key:"_getOptionIndex",value:function(e,t){var i=(0,x.L)(this.config,t);if(void 0===i)return T.debug("No config found for group select",t),0;var a=e.schema.findIndex((e=>{var a=this._getRequiredKeys(e.schema);return 0===a.length?(T.warn("No required keys for GroupSelect option",t,e),!1):a.every((e=>e in i))}));return-1===a?(T.debug("No valid option found for group select",t,i),0):a}},{key:"_updateGroupSelectOption",value:function(e){e.stopPropagation();var t=e.target.key,i=parseInt(e.detail.value,10);(0,x.F)(this.config,t,void 0,T),this._selectedGroupSelectOptions[t]=i,(0,y.r)(this,"knx-entity-configuration-changed",this.config),this.requestUpdate()}},{key:"_updateConfig",value:function(e){e.stopPropagation();var t=e.target.key,i=e.detail.value;(0,x.F)(this.config,t,i,T),(0,y.r)(this,"knx-entity-configuration-changed",this.config),this.requestUpdate()}}])}(p.WF);O.styles=(0,p.AH)(Z||(Z=E`
    p {
      color: var(--secondary-text-color);
    }

    .header {
      color: var(--ha-card-header-color, --primary-text-color);
      font-family: var(--ha-card-header-font-family, inherit);
      padding: 0 16px 16px;

      & h1 {
        display: inline-flex;
        align-items: center;
        font-size: 26px;
        letter-spacing: -0.012em;
        line-height: 48px;
        font-weight: normal;
        margin-bottom: 14px;

        & ha-svg-icon {
          color: var(--text-primary-color);
          padding: 8px;
          background-color: var(--blue-color);
          border-radius: 50%;
          margin-right: 8px;
        }
      }

      & p {
        margin-top: -8px;
        line-height: 24px;
      }
    }

    ::slotted(ha-alert) {
      margin-top: 0 !important;
    }

    ha-card {
      margin-bottom: 24px;
      padding: 16px;

      & .card-header {
        display: inline-flex;
        align-items: center;
      }
    }

    ha-expansion-panel {
      margin-bottom: 16px;
    }
    ha-expansion-panel > :first-child:not(ha-settings-row) {
      margin-top: 16px; /* ha-settings-row has this margin internally */
    }
    ha-expansion-panel > ha-settings-row:first-child,
    ha-expansion-panel > knx-selector-row:first-child {
      border: 0;
    }
    ha-expansion-panel > * {
      margin-left: 8px;
      margin-right: 8px;
    }

    ha-settings-row {
      margin-bottom: 8px;
      padding: 0;
    }
    ha-control-select {
      padding: 0;
      margin-left: 0;
      margin-right: 0;
      margin-bottom: 16px;
    }

    .group-description {
      align-items: center;
      margin-top: -8px;
      padding-left: 8px;
      padding-bottom: 8px;
    }

    .group-selection {
      padding-left: 8px;
      padding-right: 8px;
      & ha-settings-row:first-child {
        border-top: 0;
      }
    }

    knx-group-address-selector,
    ha-selector,
    ha-selector-text,
    ha-selector-select,
    knx-sync-state-selector-row,
    knx-device-picker {
      display: block;
      margin-bottom: 16px;
    }

    ha-alert {
      display: block;
      margin: 20px auto;
      max-width: 720px;

      & summary {
        padding: 10px;
      }
    }
  `)),(0,h.__decorate)([(0,u.MZ)({attribute:!1})],O.prototype,"hass",void 0),(0,h.__decorate)([(0,u.MZ)({attribute:!1})],O.prototype,"knx",void 0),(0,h.__decorate)([(0,u.MZ)({attribute:!1})],O.prototype,"platform",void 0),(0,h.__decorate)([(0,u.MZ)({attribute:!1})],O.prototype,"config",void 0),(0,h.__decorate)([(0,u.MZ)({attribute:!1})],O.prototype,"schema",void 0),(0,h.__decorate)([(0,u.MZ)({attribute:!1})],O.prototype,"validationErrors",void 0),(0,h.__decorate)([(0,u.wk)()],O.prototype,"_selectedGroupSelectOptions",void 0),O=(0,h.__decorate)([(0,u.EM)("knx-configure-entity")],O),t()}catch(j){t(j)}}))},75877:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(61397),o=i(50264),r=i(94741),n=i(44734),s=i(56038),l=i(69683),d=i(6454),c=(i(28706),i(50113),i(74423),i(62062),i(26910),i(18111),i(20116),i(61701),i(26099),i(62826)),h=i(96196),p=i(77845),u=i(94333),v=i(22786),g=i(55179),f=(i(56565),i(48011)),y=i(92542),_=i(45336),m=i(25749),b=i(53003),x=e([g,f]);[g,f]=x.then?(await x)():x;var k,$,w,A=e=>e,M=e=>(0,h.qy)(k||(k=A`<ha-list-item
    class=${0}
    .twoline=${0}
  >
    <span>${0}</span>
    <span slot="secondary">${0}</span>
  </ha-list-item>`),(0,u.H)({"add-new":"add_new"===e.id}),!!e.area,e.name,e.area),C=function(e){function t(){var e;(0,n.A)(this,t);for(var i=arguments.length,a=new Array(i),o=0;o<i;o++)a[o]=arguments[o];return(e=(0,l.A)(this,t,[].concat(a)))._showCreateDeviceDialog=!1,e._init=!1,e._getDevices=(0,v.A)(((t,i)=>{var a=t.map((t=>{var a,o,r=null!==(a=null!==(o=t.name_by_user)&&void 0!==o?o:t.name)&&void 0!==a?a:"";return{id:t.id,identifier:(0,b.dd)(t),name:r,area:t.area_id&&i[t.area_id]?i[t.area_id].name:e.hass.localize("ui.components.device-picker.no_area"),strings:[r||""]}}));return[{id:"add_new",name:"Add new device…",area:"",strings:[]}].concat((0,r.A)(a.sort(((t,i)=>(0,m.xL)(t.name||"",i.name||"",e.hass.locale.language)))))})),e}return(0,d.A)(t,e),(0,s.A)(t,[{key:"_addDevice",value:(u=(0,o.A)((0,a.A)().m((function e(t){var i,o;return(0,a.A)().w((function(e){for(;;)switch(e.n){case 0:return i=[].concat((0,r.A)((0,b.L0)(this.hass)),[t]),o=this._getDevices(i,this.hass.areas),this.comboBox.items=o,this.comboBox.filteredItems=o,e.n=1,this.updateComplete;case 1:return e.n=2,this.comboBox.updateComplete;case 2:return e.a(2)}}),e,this)}))),function(e){return u.apply(this,arguments)})},{key:"open",value:(p=(0,o.A)((0,a.A)().m((function e(){var t;return(0,a.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,this.updateComplete;case 1:return e.n=2,null===(t=this.comboBox)||void 0===t?void 0:t.open();case 2:return e.a(2)}}),e,this)}))),function(){return p.apply(this,arguments)})},{key:"focus",value:(c=(0,o.A)((0,a.A)().m((function e(){var t;return(0,a.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,this.updateComplete;case 1:return e.n=2,null===(t=this.comboBox)||void 0===t?void 0:t.focus();case 2:return e.a(2)}}),e,this)}))),function(){return c.apply(this,arguments)})},{key:"updated",value:function(e){if(!this._init&&this.hass||this._init&&e.has("_opened")&&this._opened){var t;this._init=!0;var i=this._getDevices((0,b.L0)(this.hass),this.hass.areas),a=this.value?null===(t=i.find((e=>e.identifier===this.value)))||void 0===t?void 0:t.id:void 0;this.comboBox.value=a,this._deviceId=a,this.comboBox.items=i,this.comboBox.filteredItems=i}}},{key:"render",value:function(){return(0,h.qy)($||($=A`
      <ha-combo-box
        .hass=${0}
        .label=${0}
        .helper=${0}
        .value=${0}
        .renderer=${0}
        item-id-path="id"
        item-value-path="id"
        item-label-path="name"
        @filter-changed=${0}
        @opened-changed=${0}
        @value-changed=${0}
      ></ha-combo-box>
      ${0}
    `),this.hass,void 0===this.label&&this.hass?this.hass.localize("ui.components.device-picker.device"):this.label,this.helper,this._deviceId,M,this._filterChanged,this._openedChanged,this._deviceChanged,this._showCreateDeviceDialog?this._renderCreateDeviceDialog():h.s6)}},{key:"_filterChanged",value:function(e){var t=e.target,i=e.detail.value;if(i){var a=(0,_.H)(i,t.items||[]);this._suggestion=i,this.comboBox.filteredItems=[].concat((0,r.A)(a),[{id:"add_new_suggestion",name:`Add new device '${this._suggestion}'`}])}else this.comboBox.filteredItems=this.comboBox.items}},{key:"_openedChanged",value:function(e){this._opened=e.detail.value}},{key:"_deviceChanged",value:function(e){e.stopPropagation();var t=e.detail.value;"no_devices"===t&&(t=""),["add_new_suggestion","add_new"].includes(t)?(e.target.value=this._deviceId,this._openCreateDeviceDialog()):t!==this._deviceId&&this._setValue(t)}},{key:"_setValue",value:function(e){var t=this.comboBox.items.find((t=>t.id===e)),i=null==t?void 0:t.identifier;this.value=i,this._deviceId=null==t?void 0:t.id,setTimeout((()=>{(0,y.r)(this,"value-changed",{value:i}),(0,y.r)(this,"change")}),0)}},{key:"_renderCreateDeviceDialog",value:function(){return(0,h.qy)(w||(w=A`
      <knx-device-create-dialog
        .hass=${0}
        @create-device-dialog-closed=${0}
        .deviceName=${0}
      ></knx-device-create-dialog>
    `),this.hass,this._closeCreateDeviceDialog,this._suggestion)}},{key:"_openCreateDeviceDialog",value:function(){this._showCreateDeviceDialog=!0}},{key:"_closeCreateDeviceDialog",value:(i=(0,o.A)((0,a.A)().m((function e(t){var i;return(0,a.A)().w((function(e){for(;;)switch(e.n){case 0:if(!(i=t.detail.newDevice)){e.n=2;break}return e.n=1,this._addDevice(i);case 1:e.n=3;break;case 2:this.comboBox.setInputValue("");case 3:this._setValue(null==i?void 0:i.id),this._suggestion=void 0,this._showCreateDeviceDialog=!1;case 4:return e.a(2)}}),e,this)}))),function(e){return i.apply(this,arguments)})}]);var i,c,p,u}(h.WF);(0,c.__decorate)([(0,p.MZ)({attribute:!1})],C.prototype,"hass",void 0),(0,c.__decorate)([(0,p.MZ)()],C.prototype,"label",void 0),(0,c.__decorate)([(0,p.MZ)()],C.prototype,"helper",void 0),(0,c.__decorate)([(0,p.MZ)()],C.prototype,"value",void 0),(0,c.__decorate)([(0,p.wk)()],C.prototype,"_opened",void 0),(0,c.__decorate)([(0,p.P)("ha-combo-box",!0)],C.prototype,"comboBox",void 0),(0,c.__decorate)([(0,p.wk)()],C.prototype,"_showCreateDeviceDialog",void 0),C=(0,c.__decorate)([(0,p.EM)("knx-device-picker")],C),t()}catch(D){t(D)}}))},18239:function(e,t,i){var a,o,r,n,s,l=i(94741),d=i(44734),c=i(56038),h=i(69683),p=i(6454),u=(i(28706),i(2008),i(50113),i(74423),i(23792),i(62062),i(54554),i(18111),i(81148),i(22489),i(20116),i(61701),i(26099),i(16034),i(31415),i(17642),i(58004),i(33853),i(45876),i(32475),i(15024),i(31698),i(62953),i(62826)),v=i(96196),g=i(77845),f=i(94333),y=i(16527),_=i(22786),m=(i(60733),i(92542)),b=(i(48543),i(1958),e=>e),x=function(e){function t(){var e;(0,d.A)(this,t);for(var i=arguments.length,a=new Array(i),o=0;o<i;o++)a[o]=arguments[o];return(e=(0,h.A)(this,t,[].concat(a))).disabled=!1,e.invalid=!1,e.localizeValue=e=>e,e}return(0,p.A)(t,e),(0,c.A)(t,[{key:"render",value:function(){return(0,v.qy)(a||(a=b`
      ${0}
      ${0}
      ${0}
    `),this.label?(0,v.qy)(o||(o=b`<div class="title">${0}</div>`),this.label):v.s6,this.options.map((e=>(0,v.qy)(r||(r=b`
          <div class="formfield">
            <ha-radio
              .checked=${0}
              .value=${0}
              .disabled=${0}
              @change=${0}
            ></ha-radio>
            <label .value=${0} @click=${0}>
              <p>
                ${0}
              </p>
              <p class="secondary">DPT ${0}</p>
            </label>
          </div>
        `),e.value===this.value,e.value,this.disabled,this._valueChanged,e.value,this._valueChanged,this.localizeValue(this.translation_key+".options."+e.translation_key),e.value))),this.invalidMessage?(0,v.qy)(n||(n=b`<p class="invalid-message">${0}</p>`),this.invalidMessage):v.s6)}},{key:"_valueChanged",value:function(e){var t;e.stopPropagation();var i=e.target.value;this.disabled||void 0===i||i===(null!==(t=this.value)&&void 0!==t?t:"")||(0,m.r)(this,"value-changed",{value:i})}}])}(v.WF);x.styles=[(0,v.AH)(s||(s=b`
      :host([invalid]) {
        color: var(--error-color);
      }

      .title {
        padding-left: 12px;
      }

      .formfield {
        display: flex;
        align-items: center;
      }

      label {
        min-width: 200px; /* to make it easier to click */
      }

      p {
        pointer-events: none;
        color: var(--primary-text-color);
        margin: 0px;
      }

      .secondary {
        padding-top: 4px;
        font-family: var(
          --mdc-typography-body2-font-family,
          var(--mdc-typography-font-family, Roboto, sans-serif)
        );
        -webkit-font-smoothing: antialiased;
        font-size: var(--mdc-typography-body2-font-size, 0.875rem);
        font-weight: var(--mdc-typography-body2-font-weight, 400);
        line-height: normal;
        color: var(--secondary-text-color);
      }

      .invalid-message {
        font-size: 0.75rem;
        color: var(--error-color);
        padding-left: 16px;
      }
    `))],(0,u.__decorate)([(0,g.MZ)({type:Array})],x.prototype,"options",void 0),(0,u.__decorate)([(0,g.MZ)()],x.prototype,"value",void 0),(0,u.__decorate)([(0,g.MZ)()],x.prototype,"label",void 0),(0,u.__decorate)([(0,g.MZ)({type:Boolean})],x.prototype,"disabled",void 0),(0,u.__decorate)([(0,g.MZ)({type:Boolean,reflect:!0})],x.prototype,"invalid",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],x.prototype,"invalidMessage",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],x.prototype,"localizeValue",void 0),(0,u.__decorate)([(0,g.MZ)({type:String})],x.prototype,"translation_key",void 0),x=(0,u.__decorate)([(0,g.EM)("knx-dpt-option-selector")],x);var k,$,w,A,M,C=i(78261),D=(i(5506),i(53921),i(3362),i(27495),i(25440),e=>e),H=function(e){function t(){var e;(0,d.A)(this,t);for(var i=arguments.length,a=new Array(i),o=0;o<i;o++)a[o]=arguments[o];return(e=(0,h.A)(this,t,[].concat(a))).disabled=!1,e.invalid=!1,e._baseTranslation=(t,i)=>e.hass.localize(`component.knx.config_panel.entities.create._.knx.knx_group_address.${t}`,i),e}return(0,p.A)(t,e),(0,c.A)(t,[{key:"render",value:function(){var e,t,i;return(0,v.qy)(k||(k=D`
      <div class="title">${0}</div>
      <div class="knx-dpt-selector">
        <ha-icon-button
          class="menu-button"
          .path=${0}
          @click=${0}
          .label=${0}
        ></ha-icon-button>

        ${0}
      </div>
      ${0}
    `),this._baseTranslation("dpt"),"M21,15.61L19.59,17L14.58,12L19.59,7L21,8.39L17.44,12L21,15.61M3,6H16V8H3V6M3,13V11H13V13H3M3,18V16H16V18H3Z",this._openDialog,this._baseTranslation("dpt_select"),this.value?(0,v.qy)($||($=D`<div class="selection">
                <div class="dpt-number">${0}</div>
                <div class="dpt-name">
                  ${0}
                </div>
                <div class="dpt-unit">${0}</div>
              </div>
              <ha-icon-button
                class="clear-button"
                .path=${0}
                .label=${0}
                @click=${0}
              ></ha-icon-button>`),this.value,this.hass.localize(`component.knx.config_panel.dpt.options.${this.value.replace(".","_")}`)||(null===(e=this.knx.dptMetadata[this.value])||void 0===e?void 0:e.name),null!==(t=null===(i=this.knx.dptMetadata[this.value])||void 0===i?void 0:i.unit)&&void 0!==t?t:"","M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",this.hass.localize("ui.common.clear"),this._clearSelection):(0,v.qy)(w||(w=D`<div no-selection class="selection">
              ${0}
            </div>`),this._baseTranslation("dpt_no_selection")),this.invalidMessage?(0,v.qy)(A||(A=D`<p class="invalid-message">${0}</p>`),this.invalidMessage):v.s6)}},{key:"_clearSelection",value:function(){this.value&&(this.value=void 0,(0,m.r)(this,"value-changed",{value:this.value}))}},{key:"_openDialog",value:function(){(0,m.r)(this,"show-dialog",{dialogTag:"knx-dpt-select-dialog",dialogImport:()=>Promise.all([i.e("5706"),i.e("321")]).then(i.bind(i,42957)),dialogParams:(()=>{var e=(()=>{if(this.validDPTs&&this.validDPTs.length){var e=new Set(this.validDPTs);return Object.fromEntries(Object.entries(this.knx.dptMetadata).filter((t=>{var i=(0,C.A)(t,1)[0];return e.has(i)})))}return Object.assign({},this.knx.dptMetadata)})();return{title:`${this.parentLabel?this.parentLabel+" - ":""}${this._baseTranslation("dpt_select")}`,dpts:e,initialSelection:this.value,onClose:e=>{e&&e!==this.value&&(this.value=e,(0,m.r)(this,"value-changed",{value:this.value}))}}})()})}}])}(v.WF);H.styles=[(0,v.AH)(M||(M=D`
      :host([invalid]) {
        color: var(--error-color);
      }

      .title {
        padding-left: 12px;
      }

      p {
        pointer-events: none;
        color: var(--primary-text-color);
        margin: 0px;
      }

      .invalid-message {
        font-size: 0.75rem;
        color: var(--error-color);
        padding-left: 16px;
      }

      .knx-dpt-selector {
        display: flex;
        align-items: center;
        gap: 8px;
      }

      .knx-dpt-selector .selection {
        display: grid;
        /* first column adapts to content, middle column gets remaining space (shrinkable)
           last column adapts to content as well (auto) — only the middle column truncates */
        grid-template-columns: auto minmax(0, 1fr) auto;
        align-items: center;
        gap: 8px;
        flex: 1 1 auto;
        min-width: 160px;
      }

      .selection[no-selection] {
        color: var(--secondary-text-color);
        font-style: italic;
      }

      .menu-button {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 0;
      }

      .clear-button {
        margin-left: 8px;
      }

      .dpt-number {
        font-family:
          ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "Courier New", monospace;
        color: var(--secondary-text-color);
        white-space: nowrap;
      }

      .dpt-name {
        font-weight: 500;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        /* allow the grid to shrink this column correctly */
        min-width: 0;
      }

      .dpt-unit {
        text-align: right;
        color: var(--secondary-text-color);
        white-space: nowrap;
        padding-left: 6px;
      }
    `))],(0,u.__decorate)([(0,g.MZ)({attribute:!1})],H.prototype,"hass",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],H.prototype,"knx",void 0),(0,u.__decorate)([(0,g.MZ)({type:String})],H.prototype,"key",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],H.prototype,"parentLabel",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1,type:Array})],H.prototype,"validDPTs",void 0),(0,u.__decorate)([(0,g.MZ)()],H.prototype,"value",void 0),(0,u.__decorate)([(0,g.MZ)({type:Boolean})],H.prototype,"disabled",void 0),(0,u.__decorate)([(0,g.MZ)({type:Boolean,reflect:!0})],H.prototype,"invalid",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],H.prototype,"invalidMessage",void 0),(0,u.__decorate)([(0,g.MZ)({type:String})],H.prototype,"translation_key",void 0),H=(0,u.__decorate)([(0,g.EM)("knx-dpt-dialog-selector")],H);i(2892),i(78740);var V,S,z,q,L,P,Z=e=>e,E=function(e){function t(){var e;(0,d.A)(this,t);for(var i=arguments.length,a=new Array(i),o=0;o<i;o++)a[o]=arguments[o];return(e=(0,h.A)(this,t,[].concat(a))).groupAddresses=[],e.disabled=!1,e.invalid=!1,e.required=!1,e._baseTranslation=(t,i)=>e.hass.localize(`component.knx.config_panel.entities.create._.knx.knx_group_address.${t}`,i),e}return(0,p.A)(t,e),(0,c.A)(t,[{key:"willUpdate",value:function(e){if(e.has("invalidMessage")&&(this.invalid=!!this.invalidMessage),(e.has("value")||e.has("groupAddresses")||e.has("knx"))&&this.knx.projectData){var t,i,a=null===(t=this.groupAddresses)||void 0===t?void 0:t.find((e=>e.address===this.value));a||(a=Object.values(this.knx.projectData.group_addresses).find((e=>e.address===this.value))),this._currentName=null===(i=a)||void 0===i?void 0:i.name}}},{key:"updated",value:function(){var e,t=null===(e=this._textField)||void 0===e||null===(e=e.shadowRoot)||void 0===e?void 0:e.querySelector("label");t&&(this.invalid?t.classList.add("mdc-text-field--invalid"):t.classList.remove("mdc-text-field--invalid"))}},{key:"render",value:function(){var e,t,i,a,o,r=!!this._currentName,n=!this.value&&0===this.groupAddresses.length,s=null!==(e=this.knx)&&void 0!==e&&e.projectData?null!==(t=this._currentName)&&void 0!==t?t:this.value?this._baseTranslation("group_address_unknown"):n?this._baseTranslation("group_address_none_for_dpt"):"":void 0;return(0,v.qy)(V||(V=Z`
      <div class="container">
        ${0}

        <div class="input-wrap">
          <div class="input-row">
            <ha-textfield
              .disabled=${0}
              .required=${0}
              .value=${0}
              .label=${0}
              @input=${0}
            ></ha-textfield>
            ${0}
          </div>
        </div>
      </div>
      ${0}
      ${0}
    `),null!==(i=this.knx)&&void 0!==i&&i.projectData?(0,v.qy)(S||(S=Z`<ha-icon-button
              class="menu-button"
              .disabled=${0}
              .path=${0}
              .label=${0}
              @click=${0}
            ></ha-icon-button>`),this.disabled||0===this.groupAddresses.length,"M9 6V8H2V6H9M9 11V13H2V11H9M18 16V18H2V16H18M19.31 11.5C19.75 10.82 20 10 20 9.11C20 6.61 18 4.61 15.5 4.61S11 6.61 11 9.11 13 13.61 15.5 13.61C16.37 13.61 17.19 13.36 17.88 12.93L21 16L22.39 14.61L19.31 11.5M15.5 11.61C14.12 11.61 13 10.5 13 9.11S14.12 6.61 15.5 6.61 18 7.73 18 9.11 16.88 11.61 15.5 11.61Z",this._baseTranslation("group_address_search"),this._openDialog):v.s6,this.disabled,this.required,null!==(a=this.value)&&void 0!==a?a:"",null!==(o=this.label)&&void 0!==o?o:"",this._onInput,s?(0,v.qy)(z||(z=Z`<div
                  class="ga-name"
                  ?unknown-ga=${0}
                  title=${0}
                >
                  ${0}
                </div>`),!r||n,s,s):v.s6,this.hintMessage?(0,v.qy)(q||(q=Z`<p class="hint-message">${0}</p>`),this.hintMessage):v.s6,this.invalidMessage?(0,v.qy)(L||(L=Z`<p class="invalid-message">${0}</p>`),this.invalidMessage):v.s6)}},{key:"_onInput",value:function(e){var t,i=e.target,a=null!==(t=null==i?void 0:i.value)&&void 0!==t?t:"";this.value=a||void 0,(0,m.r)(this,"value-changed",{value:this.value})}},{key:"_openDialog",value:function(){var e,t;(0,m.r)(this,"show-dialog",{dialogTag:"knx-ga-select-dialog",dialogImport:()=>i.e("2154").then(i.bind(i,193)),dialogParams:{title:`${this.parentLabel?this.parentLabel+" - ":""}${null!==(e=this.label)&&void 0!==e?e:""}`,groupAddresses:null!==(t=this.groupAddresses)&&void 0!==t?t:[],initialSelection:this.value,knx:this.knx,onClose:e=>{e&&e!==this.value&&(this.value=e,(0,m.r)(this,"value-changed",{value:this.value}))}}})}}])}(v.WF);E.styles=(0,v.AH)(P||(P=Z`
    :host {
      display: block;
      margin-bottom: 16px;
      transition:
        box-shadow 250ms,
        opacity 250ms;
    }

    :host([invalid]) {
      color: var(--error-color);
    }

    .container {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }

    .menu-button {
      display: inline-flex;
      align-items: center;
      padding: 4px 0;
    }

    .input-wrap {
      flex: 1 1 auto;
      display: flex;
      flex-direction: column;
      gap: 4px;
      align-items: stretch;
      min-width: 0;
    }

    .input-row {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }

    ha-textfield {
      width: 18ch; /* account for label in various languages, not only GA strings */
      flex: 0 0 auto;
      /* prevent content from expanding the field */
      --text-field-overflow: hidden;
    }

    .ga-name {
      flex: 1 1 auto;
      min-width: 0;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: normal;
      word-break: break-word;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      line-height: 1.2;
      max-height: calc(2 * 1.2em);
      color: var(--primary-text-color);
    }

    .ga-name[unknown-ga] {
      font-style: italic;
      color: var(--secondary-text-color);
    }

    .invalid-message,
    .hint-message {
      font-size: 0.75rem;
      color: var(--error-color);
      padding-left: 16px;
      margin: 4px 0 0 0;
    }

    .hint-message {
      color: var(--warning-color);
    }
  `)),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],E.prototype,"hass",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],E.prototype,"knx",void 0),(0,u.__decorate)([(0,g.MZ)({type:String})],E.prototype,"key",void 0),(0,u.__decorate)([(0,g.MZ)({type:Number})],E.prototype,"index",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],E.prototype,"groupAddresses",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],E.prototype,"hintMessage",void 0),(0,u.__decorate)([(0,g.MZ)({type:String})],E.prototype,"value",void 0),(0,u.__decorate)([(0,g.MZ)()],E.prototype,"label",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],E.prototype,"parentLabel",void 0),(0,u.__decorate)([(0,g.MZ)({type:Boolean})],E.prototype,"disabled",void 0),(0,u.__decorate)([(0,g.MZ)({type:Boolean,reflect:!0})],E.prototype,"invalid",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],E.prototype,"invalidMessage",void 0),(0,u.__decorate)([(0,g.MZ)({type:Boolean})],E.prototype,"required",void 0),(0,u.__decorate)([(0,g.wk)()],E.prototype,"_currentName",void 0),(0,u.__decorate)([(0,g.P)("ha-textfield")],E.prototype,"_textField",void 0),E=(0,u.__decorate)([(0,g.EM)("knx-single-address-selector")],E);var T,O,j,I,B,F,G,N,U,W,R,Q,K,Y,J=i(56803),X=i(19337),ee=i(76674),te=e=>e,ie=function(e){function t(){var e;(0,d.A)(this,t);for(var i=arguments.length,a=new Array(i),o=0;o<i;o++)a[o]=arguments[o];return(e=(0,h.A)(this,t,[].concat(a))).config={},e.localizeFunction=e=>e,e._showEmptyPassiveField=!1,e.validGroupAddresses=[],e.filteredGroupAddresses=[],e.dptSelectorDisabled=!1,e._dragOverTimeout={},e._baseTranslation=(t,i)=>e.hass.localize(`component.knx.config_panel.entities.create._.knx.knx_group_address.${t}`,i),e.setFilteredGroupAddresses=(0,_.A)((t=>{e.filteredGroupAddresses=t?e.getValidGroupAddresses([t]):e.validGroupAddresses})),e._getDPTsFromClasses=(0,_.A)((t=>{if(null==t||!t.length||!e.knx.dptMetadata)return[];var i=new Set(t);return Object.values(e.knx.dptMetadata).filter((e=>i.has(e.dpt_class))).map((e=>({main:e.main,sub:e.sub})))})),e._getDptStringsFromClasses=(0,_.A)((t=>e._getDPTsFromClasses(t).map(X.Vt))),e._addPassiveSelector=t=>{t&&t.preventDefault(),e._showEmptyPassiveField||(e._showEmptyPassiveField=!0,e.requestUpdate())},e._onRemovePassiveClick=t=>{var i=parseInt(t.currentTarget.getAttribute("data-index")||"-1",10);i>=0&&e._removePassiveSelector(i)},e._removePassiveSelector=t=>{var i,a;if(t<(null!==(i=null===(a=e.config.passive)||void 0===a?void 0:a.length)&&void 0!==i?i:0)){var o,r=Object.assign({},e.config),n=(0,l.A)(null!==(o=r.passive)&&void 0!==o?o:[]);n.splice(t,1),0===n.length?delete r.passive:r.passive=n,e._updateConfig(r,"passive")}else e._showEmptyPassiveField=!1,e.requestUpdate()},e._valueChangedPassive=t=>{t.stopPropagation();var i=t.target.index,a=t.detail.value;e._updatePassiveAtIndex(i,a)},e._updatePassiveAtIndex=(t,i)=>{var a,o,r=null!==(a=null===(o=e.config.passive)||void 0===o?void 0:o.length)&&void 0!==a?a:0,n=Object.assign({},e.config);if(t<r){var s,d=(0,l.A)(null!==(s=n.passive)&&void 0!==s?s:[]);d[t]=i,n.passive=d.filter((e=>!!e)),0===n.passive.length&&delete n.passive,t!==r-1||i||(e._showEmptyPassiveField=!0)}else{if(!i)return;var c;n.passive=[].concat((0,l.A)(null!==(c=n.passive)&&void 0!==c?c:[]),[i]),e._showEmptyPassiveField=!1}e._updateConfig(n,"passive")},e}return(0,p.A)(t,e),(0,c.A)(t,[{key:"_getAcceptedDPTs",value:function(){var e,t,i,a=this.options.validDPTs,o=this.options.dptClasses?this._getDPTsFromClasses(this.options.dptClasses):void 0,r=null===(e=this.options.dptSelect)||void 0===e?void 0:e.map((e=>e.dpt));return null!==(t=null!==(i=null!=a?a:o)&&void 0!==i?i:r)&&void 0!==t?t:[]}},{key:"getValidGroupAddresses",value:function(e){return this.knx.projectData?Object.values(this.knx.projectData.group_addresses).filter((t=>!!t.dpt&&(0,X.HG)(t.dpt,e))):[]}},{key:"getDptByValue",value:function(e){if(e){var t,i;if(this.options.dptSelect)return null===(t=this.options.dptSelect)||void 0===t||null===(t=t.find((t=>t.value===e)))||void 0===t?void 0:t.dpt;if(this.options.dptClasses)return null!==(i=(0,X.$k)(e))&&void 0!==i?i:void 0}}},{key:"shouldUpdate",value:function(e){return!(1===e.size&&e.has("hass"))}},{key:"willUpdate",value:function(e){var t;if(e.has("options")&&(this.validGroupAddresses=this.getValidGroupAddresses(this._getAcceptedDPTs()),this.filteredGroupAddresses=this.validGroupAddresses),e.has("config")){var i;this._selectedDPTValue=null!==(i=this.config.dpt)&&void 0!==i?i:this._selectedDPTValue;var a=this.getDptByValue(this._selectedDPTValue);if(this.setFilteredGroupAddresses(a),a&&this.knx.projectData){var o,r=[this.config.write,this.config.state].concat((0,l.A)(null!==(o=this.config.passive)&&void 0!==o?o:[])).filter((e=>!!e));this.dptSelectorDisabled=r.length>0&&r.every((e=>{var t,i=null===(t=this.knx.projectData.group_addresses[e])||void 0===t?void 0:t.dpt;return!!i&&(0,X.HG)(i,[a])}))}else this.dptSelectorDisabled=!1}this._validGADropTarget=null!==(t=this._dragDropContext)&&void 0!==t&&t.groupAddress?this.filteredGroupAddresses.includes(this._dragDropContext.groupAddress):void 0}},{key:"render",value:function(){var e,t,i,a,o,r=!0===this._validGADropTarget,n=!1===this._validGADropTarget,s=(0,ee.W)(this.validationErrors),d=this.localizeFunction(this.key+".description"),c=this.required?this.hass.localize("ui.common.error_required"):void 0;return(0,v.qy)(T||(T=te`
      <p class="title">${0}</p>
      ${0}
      ${0}
      ${0}
      <div class="main">
        <div class="selectors">
          ${0}
          ${0}
        </div>
      </div>
      ${0}
      ${0}
      ${0}
      ${0}
    `),this.label,c?(0,v.qy)(O||(O=te`<p class="description">${0}</p>`),c):v.s6,d?(0,v.qy)(j||(j=te`<p class="description">${0}</p>`),d):v.s6,s?(0,v.qy)(I||(I=te`<p class="error">
            <ha-svg-icon .path=${0}></ha-svg-icon>
            <b>Validation error:</b>
            ${0}
          </p>`),"M11,15H13V17H11V15M11,7H13V13H11V7M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20Z",s.error_message):v.s6,this.options.write?(0,v.qy)(B||(B=te`<knx-single-address-selector
                class=${0}
                .hass=${0}
                .knx=${0}
                .label=${0}
                .parentLabel=${0}
                .required=${0}
                .groupAddresses=${0}
                .key=${0}
                .value=${0}
                .invalidMessage=${0}
                .hintMessage=${0}
                @value-changed=${0}
                @dragover=${0}
                @drop=${0}
              ></knx-single-address-selector>`),(0,f.H)({"valid-drop-zone":r,"invalid-drop-zone":n}),this.hass,this.knx,this._baseTranslation("send_address"),this.label,this.options.write.required,this.filteredGroupAddresses,"write",null!==(e=this.config.write)&&void 0!==e?e:void 0,null===(t=(0,ee.W)(this.validationErrors,"write"))||void 0===t?void 0:t.error_message,this._isGaDptMismatch(this.config.write)?this._dptMismatchMessage(this.config.write):void 0,this._valueChanged,this._dragOverHandler,this._dropHandler):v.s6,this.options.state?(0,v.qy)(F||(F=te`<knx-single-address-selector
                class=${0}
                .hass=${0}
                .knx=${0}
                .label=${0}
                .parentLabel=${0}
                .required=${0}
                .groupAddresses=${0}
                .key=${0}
                .value=${0}
                .invalidMessage=${0}
                .hintMessage=${0}
                @value-changed=${0}
                @dragover=${0}
                @drop=${0}
              ></knx-single-address-selector>`),(0,f.H)({"valid-drop-zone":r,"invalid-drop-zone":n}),this.hass,this.knx,this._baseTranslation("state_address"),this.label,this.options.state.required,this.filteredGroupAddresses,"state",null!==(i=this.config.state)&&void 0!==i?i:void 0,null===(a=(0,ee.W)(this.validationErrors,"state"))||void 0===a?void 0:a.error_message,this._isGaDptMismatch(this.config.state)?this._dptMismatchMessage(this.config.state):void 0,this._valueChanged,this._dragOverHandler,this._dropHandler):v.s6,this.options.passive?(0,v.qy)(G||(G=te`<div class="passive-list">
            ${0}
          </div>`),[].concat((0,l.A)(null!==(o=this.config.passive)&&void 0!==o?o:[]),(0,l.A)(this._showEmptyPassiveField?[void 0]:[])).map(((e,t)=>{var i=this._getPassiveValidationForIndex(t);return(0,v.qy)(N||(N=te`<div class="passive-row">
                <knx-single-address-selector
                  class=${0}
                  .hass=${0}
                  .knx=${0}
                  .label=${0}
                  .parentLabel=${0}
                  .required=${0}
                  .groupAddresses=${0}
                  .key=${0}
                  .index=${0}
                  .value=${0}
                  .invalidMessage=${0}
                  .hintMessage=${0}
                  @value-changed=${0}
                  @dragover=${0}
                  @drop=${0}
                ></knx-single-address-selector>
                <ha-icon-button
                  class="remove-passive"
                  .path=${0}
                  .label=${0}
                  data-index=${0}
                  @click=${0}
                ></ha-icon-button>
              </div>`),(0,f.H)({"valid-drop-zone":r,"invalid-drop-zone":n}),this.hass,this.knx,this._baseTranslation("passive_address"),this.label,!1,this.filteredGroupAddresses,"passive",t,null!=e?e:void 0,null==i?void 0:i.error_message,this._isGaDptMismatch(e)?this._dptMismatchMessage(e):void 0,this._valueChangedPassive,this._dragOverHandler,this._dropHandler,"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z",this.hass.localize("ui.common.remove"),t,this._onRemovePassiveClick)}))):v.s6,this.options.validDPTs||this.options.passive?(0,v.qy)(U||(U=te`<div class="footer-row">
            ${0}
            ${0}
          </div>`),this.options.validDPTs?(0,v.qy)(W||(W=te`<p class="valid-dpts">
                  ${0}:
                  ${0}
                </p>`),this._baseTranslation("valid_dpts"),this.options.validDPTs.map((e=>(0,X.Vt)(e))).join(", ")):v.s6,this.options.passive?(0,v.qy)(R||(R=te`<a
                  href="#"
                  @click=${0}
                  class="add-passive-link"
                  ?disabled=${0}
                >
                  ${0}
                </a>`),this._addPassiveSelector,this._showEmptyPassiveField,this._baseTranslation("add_passive_address")):v.s6):v.s6,this.options.dptSelect?this._renderDptOptionSelector():v.s6,this.options.dptClasses?this._renderDptDialogSelector():v.s6)}},{key:"_renderDptOptionSelector",value:function(){var e=(0,ee.W)(this.validationErrors,"dpt");return(0,v.qy)(Q||(Q=te`<knx-dpt-option-selector
      .key=${0}
      .label=${0}
      .options=${0}
      .value=${0}
      .disabled=${0}
      .invalid=${0}
      .invalidMessage=${0}
      .localizeValue=${0}
      .translation_key=${0}
      @value-changed=${0}
    >
    </knx-dpt-option-selector>`),"dpt",this._baseTranslation("dpt"),this.options.dptSelect,this._selectedDPTValue,this.dptSelectorDisabled,!!e,null==e?void 0:e.error_message,this.localizeFunction,this.key,this._valueChanged)}},{key:"_renderDptDialogSelector",value:function(){var e=(0,ee.W)(this.validationErrors,"dpt");return(0,v.qy)(K||(K=te`<knx-dpt-dialog-selector
      .key=${0}
      .hass=${0}
      .knx=${0}
      .parentLabel=${0}
      .validDPTs=${0}
      .value=${0}
      .disabled=${0}
      .invalid=${0}
      .invalidMessage=${0}
      .translation_key=${0}
      @value-changed=${0}
    >
    </knx-dpt-dialog-selector>`),"dpt",this.hass,this.knx,this.label,this._getDptStringsFromClasses(this.options.dptClasses),this._selectedDPTValue,this.dptSelectorDisabled,!!e,null==e?void 0:e.error_message,this.key,this._valueChanged)}},{key:"_valueChanged",value:function(e){e.stopPropagation();var t=e.target,i=e.detail.value,a=Object.assign(Object.assign({},this.config),{},{[t.key]:i});this._updateConfig(a,t.key)}},{key:"_updateConfig",value:function(e,t){var i,a=[e.write,e.state].concat((0,l.A)(null!==(i=e.passive)&&void 0!==i?i:[])).some((e=>!!e));this._updateDptSelector(t,e,a),this.config=e;var o=a?e:void 0;(0,m.r)(this,"value-changed",{value:o}),this.requestUpdate()}},{key:"_updateDptSelector",value:function(e,t,i){var a;if(this.options.dptSelect||this.options.dptClasses){if("dpt"===e)this._selectedDPTValue=t.dpt;else{if(!i)return t.dpt=void 0,void(this._selectedDPTValue=void 0);t.dpt=this._selectedDPTValue}if(this.knx.projectData){var o=this._getAddedGroupAddress(e,t);if(o&&void 0===this._selectedDPTValue){var r=null===(a=this.validGroupAddresses.find((e=>e.address===o)))||void 0===a?void 0:a.dpt;if(r)if(this.options.dptSelect){var n,s=this.options.dptSelect.find((e=>e.dpt.main===r.main&&e.dpt.sub===r.sub));t.dpt=s?s.value:null===(n=this.options.dptSelect.find((e=>(0,X.HG)(r,[e.dpt]))))||void 0===n?void 0:n.value}else if(this.options.dptClasses){var l=(0,X.Vt)(r),d=this._getDptStringsFromClasses(this.options.dptClasses);t.dpt=d.includes(l)?l:void 0}}}}}},{key:"_getAddedGroupAddress",value:function(e,t){return"write"===e||"state"===e?t[e]:"passive"===e?null===(i=t.passive)||void 0===i?void 0:i.find((e=>{var t;return!(!e||null!==(t=this.config.passive)&&void 0!==t&&t.includes(e))})):void 0;var i}},{key:"_isGaDptMismatch",value:function(e){if(!e||!this.knx.projectData)return!1;var t=this.knx.projectData.group_addresses[e];return!!t&&!this.filteredGroupAddresses.find((e=>e===t))}},{key:"_dptMismatchMessage",value:function(e){var t,i;if(e&&this.knx.projectData){var a=null!==(t=(0,X.Vt)(null===(i=this.knx.projectData.group_addresses[e])||void 0===i?void 0:i.dpt))&&void 0!==t?t:"?";return this._baseTranslation("dpt_incompatible",{dpt:a})}}},{key:"_dragOverHandler",value:function(e){if((0,l.A)(e.dataTransfer.types).includes("text/group-address")){e.preventDefault(),e.dataTransfer.dropEffect="move";var t=e.target;this._dragOverTimeout[t.key]?clearTimeout(this._dragOverTimeout[t.key]):t.classList.add("active-drop-zone"),this._dragOverTimeout[t.key]=setTimeout((()=>{delete this._dragOverTimeout[t.key],t.classList.remove("active-drop-zone")}),100)}}},{key:"_getPassiveValidationForIndex",value:function(e){var t=(0,ee.a)(this.validationErrors,"passive");if(t){var i=String(e),a=t.find((e=>Array.isArray(e.path)&&e.path[0]===i));return null!=a?a:(0,ee.W)(t)}}},{key:"_dropHandler",value:function(e){e.stopPropagation(),e.preventDefault();var t=e.dataTransfer.getData("text/group-address");if(t){var i=e.target;if("passive"!==i.key||"number"!=typeof i.index){var a=Object.assign({},this.config);a[i.key]=t,this._updateConfig(a,i.key)}else this._updatePassiveAtIndex(i.index,t)}}}])}(v.WF);ie.styles=(0,v.AH)(Y||(Y=te`
    .main {
      display: flex;
      flex-direction: row;
    }

    .selectors {
      flex: 1;
    }

    .options {
      width: 48px;
      display: flex;
      flex-direction: column-reverse;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }

    .passive {
      overflow: hidden;
      transition: height 150ms cubic-bezier(0.4, 0, 0.2, 1);
      height: 0px;
      margin-right: 64px; /* compensate for .options */
    }

    .passive.expanded {
      height: auto;
    }

    .passive-row {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .passive-row knx-single-address-selector {
      flex: 1 1 auto;
    }

    .title {
      margin-bottom: 12px;
    }
    .description {
      margin-top: -10px;
      margin-bottom: 12px;
      color: var(--secondary-text-color);
      font-size: var(--ha-font-size-s);
    }

    .footer-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-top: -8px;
      margin-bottom: 12px;
      margin-left: 16px;
      margin-right: 0;
    }

    .valid-dpts {
      margin: 0;
      color: var(--secondary-text-color);
      font-size: var(--ha-font-size-s);
      flex: 1 1 auto;
    }

    .add-passive-link {
      color: var(--primary-color);
      text-decoration: none;
      font-size: var(--ha-font-size-s);
      padding: 4px 8px;
      border-radius: 4px;
      cursor: pointer;
      white-space: nowrap;
      transition: background-color 200ms;
      margin-left: auto;
    }

    .add-passive-link:not([disabled]):hover {
      background-color: rgba(var(--rgb-primary-color), 0.1);
      text-decoration: underline;
    }

    .add-passive-link[disabled] {
      color: var(--disabled-text-color);
      opacity: 0.5;
      cursor: default;
    }

    knx-dpt-dialog-selector,
    knx-dpt-option-selector {
      display: block;
      margin-top: -12px; /* move towards footer-row when validDPTs isn't shown */
    }

    knx-single-address-selector {
      display: block;
      margin-bottom: 16px;
      transition:
        box-shadow 250ms,
        opacity 250ms;
    }

    .valid-drop-zone {
      box-shadow: 0px 0px 5px 2px rgba(var(--rgb-primary-color), 0.5);
    }

    .valid-drop-zone.active-drop-zone {
      box-shadow: 0px 0px 5px 2px var(--primary-color);
    }

    .invalid-drop-zone {
      opacity: 0.5;
    }

    .invalid-drop-zone.active-drop-zone {
      box-shadow: 0px 0px 5px 2px var(--error-color);
    }

    .error {
      color: var(--error-color);
    }
  `)),(0,u.__decorate)([(0,y.Fg)({context:J.B,subscribe:!0})],ie.prototype,"_dragDropContext",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],ie.prototype,"hass",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],ie.prototype,"knx",void 0),(0,u.__decorate)([(0,g.MZ)()],ie.prototype,"label",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],ie.prototype,"config",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],ie.prototype,"options",void 0),(0,u.__decorate)([(0,g.MZ)({reflect:!0})],ie.prototype,"key",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],ie.prototype,"required",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],ie.prototype,"validationErrors",void 0),(0,u.__decorate)([(0,g.MZ)({attribute:!1})],ie.prototype,"localizeFunction",void 0),(0,u.__decorate)([(0,g.wk)()],ie.prototype,"_showEmptyPassiveField",void 0),ie=(0,u.__decorate)([(0,g.EM)("knx-group-address-selector")],ie)},42615:function(e,t,i){var a,o,r,n,s,l,d,c,h,p,u,v,g,f,y=i(31432),_=i(78261),m=i(44734),b=i(56038),x=i(69683),k=i(6454),$=i(25460),w=(i(52675),i(89463),i(28706),i(2008),i(23792),i(62062),i(44114),i(72712),i(18111),i(22489),i(61701),i(18237),i(5506),i(53921),i(26099),i(16034),i(27495),i(69479),i(90744),i(62826)),A=i(96196),M=i(77845),C=i(4937),D=i(16527),H=(i(17963),i(60961),i(78577)),V=i(56803),S=i(19337),z=e=>e,q=new H.Q("knx-project-device-tree"),L=function(e){function t(){var e;(0,m.A)(this,t);for(var i=arguments.length,a=new Array(i),o=0;o<i;o++)a[o]=arguments[o];return(e=(0,x.A)(this,t,[].concat(a))).deviceTree=[],e}return(0,k.A)(t,e),(0,b.A)(t,[{key:"connectedCallback",value:function(){var e;(0,$.A)(t,"connectedCallback",this,3)([]);var i=null!==(e=this.validDPTs)&&void 0!==e&&e.length?(0,S.Ah)(this.data,this.validDPTs):this.data.communication_objects,a=Object.values(this.data.devices).map((e=>{var t,a=[],o=Object.fromEntries(Object.entries(e.channels).map((e=>{var t=(0,_.A)(e,2);return[t[0],{name:t[1].name,comObjects:[]}]}))),r=(0,y.A)(e.communication_object_ids);try{for(r.s();!(t=r.n()).done;){var n=t.value;if(n in i){var s=i[n];s.channel&&s.channel in o?o[s.channel].comObjects.push(s):a.push(s)}}}catch(d){r.e(d)}finally{r.f()}var l=Object.entries(o).reduce(((e,t)=>{var i=(0,_.A)(t,2),a=i[0],o=i[1];return o.comObjects.length&&(e[a]=o),e}),{});return{ia:e.individual_address,name:e.name,manufacturer:e.manufacturer_name,description:e.description.split(/[\r\n]/,1)[0],noChannelComObjects:a,channels:l}}));this.deviceTree=a.filter((e=>!!e.noChannelComObjects.length||!!Object.keys(e.channels).length))}},{key:"render",value:function(){return(0,A.qy)(a||(a=z`<div class="device-tree-view">
      ${0}
    </div>`),this._selectedDevice?this._renderSelectedDevice(this._selectedDevice):this._renderDevices())}},{key:"_renderDevices",value:function(){return this.deviceTree.length?(0,A.qy)(r||(r=z`<ul class="devices">
      ${0}
    </ul>`),(0,C.u)(this.deviceTree,(e=>e.ia),(e=>(0,A.qy)(n||(n=z`<li class="clickable" @click=${0} .device=${0}>
            ${0}
          </li>`),this._selectDevice,e,this._renderDevice(e))))):(0,A.qy)(o||(o=z`<ha-alert alert-type="info">No suitable device found in project data.</ha-alert>`))}},{key:"_renderDevice",value:function(e){return(0,A.qy)(s||(s=z`<div class="item">
      <span class="icon ia">
        <ha-svg-icon .path=${0}></ha-svg-icon>
        <span>${0}</span>
      </span>
      <div class="description">
        <p>${0}</p>
        <p>${0}</p>
        ${0}
      </div>
    </div>`),"M15,20A1,1 0 0,0 14,19H13V17H17A2,2 0 0,0 19,15V5A2,2 0 0,0 17,3H7A2,2 0 0,0 5,5V15A2,2 0 0,0 7,17H11V19H10A1,1 0 0,0 9,20H2V22H9A1,1 0 0,0 10,23H14A1,1 0 0,0 15,22H22V20H15M7,15V5H17V15H7Z",e.ia,e.manufacturer,e.name,e.description?(0,A.qy)(l||(l=z`<p>${0}</p>`),e.description):A.s6)}},{key:"_renderSelectedDevice",value:function(e){return(0,A.qy)(d||(d=z`<ul class="selected-device">
      <li class="back-item clickable" @click=${0}>
        <div class="item">
          <ha-svg-icon class="back-icon" .path=${0}></ha-svg-icon>
          ${0}
        </div>
      </li>
      ${0}
    </ul>`),this._selectDevice,"M20,11V13H8L13.5,18.5L12.08,19.92L4.16,12L12.08,4.08L13.5,5.5L8,11H20Z",this._renderDevice(e),this._renderChannels(e))}},{key:"_renderChannels",value:function(e){return(0,A.qy)(c||(c=z`${0}
    ${0} `),this._renderComObjects(e.noChannelComObjects),(0,C.u)(Object.entries(e.channels),(t=>{var i=(0,_.A)(t,2),a=i[0];i[1];return`${e.ia}_ch_${a}`}),(e=>{var t=(0,_.A)(e,2),i=(t[0],t[1]);return i.comObjects.length?(0,A.qy)(h||(h=z`<li class="channel">${0}</li>
              ${0}`),i.name,this._renderComObjects(i.comObjects)):A.s6})))}},{key:"_renderComObjects",value:function(e){return(0,A.qy)(p||(p=z`${0} `),(0,C.u)(e,(e=>`${e.device_address}_co_${e.number}`),(e=>{return(0,A.qy)(u||(u=z`<li class="com-object">
          <div class="item">
            <span class="icon co"
              ><ha-svg-icon .path=${0}></ha-svg-icon
              ><span>${0}</span></span
            >
            <div class="description">
              <p>
                ${0}${0}
              </p>
              <p class="co-info">${0}</p>
            </div>
          </div>
          <ul class="group-addresses">
            ${0}
          </ul>
        </li>`),"M22 12C22 6.5 17.5 2 12 2S2 6.5 2 12 6.5 22 12 22 22 17.5 22 12M15 6.5L18.5 10L15 13.5V11H11V9H15V6.5M9 17.5L5.5 14L9 10.5V13H13V15H9V17.5Z",e.number,e.text,e.function_text?" - "+e.function_text:"",`${(t=e.flags).read?"R":"–"} ${t.write?"W":"–"} ${t.transmit?"T":"–"} ${t.update?"U":"–"}`,this._renderGroupAddresses(e.group_address_links));var t})))}},{key:"_renderGroupAddresses",value:function(e){var t=e.map((e=>this.data.group_addresses[e]));return(0,A.qy)(v||(v=z`${0} `),(0,C.u)(t,(e=>e.identifier),(e=>{var t,i,a,o,r,n,s,l;return(0,A.qy)(g||(g=z`<li
          draggable="true"
          @dragstart=${0}
          @dragend=${0}
          @mouseover=${0}
          @focus=${0}
          @mouseout=${0}
          @blur=${0}
          .ga=${0}
        >
          <div class="item">
            <ha-svg-icon
              class="drag-icon"
              .path=${0}
              .viewBox=${0}
            ></ha-svg-icon>
            <span class="icon ga">
              <span>${0}</span>
            </span>
            <div class="description">
              <p>${0}</p>
              <p class="ga-info">${0}</p>
            </div>
          </div>
        </li>`),null===(t=this._dragDropContext)||void 0===t?void 0:t.gaDragStartHandler,null===(i=this._dragDropContext)||void 0===i?void 0:i.gaDragEndHandler,null===(a=this._dragDropContext)||void 0===a?void 0:a.gaDragIndicatorStartHandler,null===(o=this._dragDropContext)||void 0===o?void 0:o.gaDragIndicatorStartHandler,null===(r=this._dragDropContext)||void 0===r?void 0:r.gaDragIndicatorEndHandler,null===(n=this._dragDropContext)||void 0===n?void 0:n.gaDragIndicatorEndHandler,e,"M9,3H11V5H9V3M13,3H15V5H13V3M9,7H11V9H9V7M13,7H15V9H13V7M9,11H11V13H9V11M13,11H15V13H13V11M9,15H11V17H9V15M13,15H15V17H13V15M9,19H11V21H9V19M13,19H15V21H13V19Z","4 0 16 24",e.address,e.name,(s=e,(l=(0,S.Vt)(s.dpt))?`DPT ${l}`:""))})))}},{key:"_selectDevice",value:function(e){var t=e.target.device;q.debug("select device",t),this._selectedDevice=t,this.scrollTop=0}}])}(A.WF);L.styles=(0,A.AH)(f||(f=z`
    :host {
      display: block;
      box-sizing: border-box;
      margin: 0;
      height: 100%;
      overflow-y: scroll;
      overflow-x: hidden;
      background-color: var(--sidebar-background-color);
      color: var(--sidebar-menu-button-text-color, --primary-text-color);
      margin-right: env(safe-area-inset-right);
      border-left: 1px solid var(--divider-color);
      padding-left: 8px;
    }

    ha-alert {
      display: block;
      margin-right: 8px;
      margin-top: 8px;
    }

    ul {
      list-style-type: none;
      padding: 0;
      margin-block-start: 8px;
    }

    li {
      display: block;
      margin-bottom: 4px;
      & div.item {
        /* icon and text */
        display: flex;
        align-items: center;
        pointer-events: none;
        & > div {
          /* optional container for multiple paragraphs */
          min-width: 0;
          width: 100%;
        }
      }
    }

    li p {
      margin: 0;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }

    span.icon {
      flex: 0 0 auto;
      display: inline-flex;
      /* align-self: stretch; */
      align-items: center;

      color: var(--text-primary-color);
      font-size: 1rem;
      font-weight: 700;
      border-radius: 12px;
      padding: 3px 6px;
      margin-right: 4px;

      & > ha-svg-icon {
        float: left;
        width: 16px;
        height: 16px;
        margin-right: 4px;
      }

      & > span {
        /* icon text */
        flex: 1;
        text-align: center;
      }
    }

    span.ia {
      flex-basis: 70px;
      background-color: var(--label-badge-grey);
      & > ha-svg-icon {
        transform: rotate(90deg);
      }
    }

    span.co {
      flex-basis: 44px;
      background-color: var(--amber-color);
    }

    span.ga {
      flex-basis: 54px;
      background-color: var(--knx-green);
    }

    .description {
      margin-top: 4px;
      margin-bottom: 4px;
    }

    p.co-info,
    p.ga-info {
      font-size: 0.85rem;
      font-weight: 300;
    }

    .back-item {
      margin-left: -8px; /* revert host padding to have gapless border */
      padding-left: 8px;
      margin-top: -8px; /* revert ul margin-block-start to have gapless hover effect */
      padding-top: 8px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--divider-color);
      margin-bottom: 8px;
    }

    .back-icon {
      margin-right: 8px;
      color: var(--label-badge-grey);
    }

    li.channel {
      border-top: 1px solid var(--divider-color);
      border-bottom: 1px solid var(--divider-color);
      padding: 4px 16px;
      font-weight: 500;
    }

    li.clickable {
      cursor: pointer;
    }
    li.clickable:hover {
      background-color: rgba(var(--rgb-primary-text-color), 0.04);
    }

    li[draggable="true"] {
      cursor: grab;
    }
    li[draggable="true"]:hover {
      border-radius: 12px;
      background-color: rgba(var(--rgb-primary-color), 0.2);
    }

    ul.group-addresses {
      margin-top: 0;
      margin-bottom: 8px;

      & > li:not(:first-child) {
        /* passive addresses for this com-object */
        opacity: 0.8;
      }
    }
  `)),(0,w.__decorate)([(0,D.Fg)({context:V.B})],L.prototype,"_dragDropContext",void 0),(0,w.__decorate)([(0,M.MZ)({attribute:!1})],L.prototype,"data",void 0),(0,w.__decorate)([(0,M.MZ)({attribute:!1})],L.prototype,"validDPTs",void 0),(0,w.__decorate)([(0,M.wk)()],L.prototype,"_selectedDevice",void 0),L=(0,w.__decorate)([(0,M.EM)("knx-project-device-tree")],L)},77812:function(e,t,i){var a,o,r,n,s,l=i(44734),d=i(56038),c=i(69683),h=i(6454),p=(i(28706),i(62826)),u=i(96196),v=i(77845),g=i(94333),f=i(92542),y=(i(70524),i(87156),i(7153),i(76674)),_=e=>e,m=function(e){function t(){var e;(0,l.A)(this,t);for(var i=arguments.length,a=new Array(i),o=0;o<i;o++)a[o]=arguments[o];return(e=(0,c.A)(this,t,[].concat(a))).localizeFunction=e=>e,e._enabled=!0,e._haSelectorValue=null,e._inlineSelector=!1,e._optionalBooleanSelector=!1,e}return(0,h.A)(t,e),(0,d.A)(t,[{key:"willUpdate",value:function(e){if(e.has("selector")||e.has("key")){var t=!!this.selector.required,i="boolean"in this.selector.selector,a="number"in this.selector.selector;if(this._inlineSelector=t&&(i||a),this._optionalBooleanSelector=!t&&i,this._optionalBooleanSelector){var o,r=!!this.selector.default;this._haSelectorValue=!r,this._enabled=null!==(o=this.value)&&void 0!==o?o:r}else{var n,s;this._enabled=t||void 0!==this.value,this._haSelectorValue=null!==(n=null!==(s=this.value)&&void 0!==s?s:this.selector.default)&&void 0!==n?n:null}}}},{key:"render",value:function(){var e=(0,y.W)(this.validationErrors),t=this._optionalBooleanSelector?u.s6:(0,u.qy)(a||(a=_`<ha-selector
          class=${0}
          .hass=${0}
          .selector=${0}
          .disabled=${0}
          .value=${0}
          .localizeValue=${0}
          @value-changed=${0}
        ></ha-selector>`),(0,g.H)({"newline-selector":!this._inlineSelector}),this.hass,this.selector.selector,!this._enabled,this._haSelectorValue,this.hass.localize,this._valueChange);return(0,u.qy)(o||(o=_`
      <div class="body">
        <div class="text">
          <p class="heading ${0}">
            ${0}
          </p>
          <p class="description">${0}</p>
        </div>
        ${0}
        ${0}
      </div>
      ${0}
      ${0}
    `),(0,g.H)({invalid:!!e}),this.localizeFunction(`${this.key}.label`),this.localizeFunction(`${this.key}.description`),this.selector.required?u.s6:(0,u.qy)(r||(r=_`<ha-selector
              class="optional-switch"
              .selector=${0}
              .value=${0}
              @value-changed=${0}
            ></ha-selector>`),{boolean:{}},this._enabled,this._toggleEnabled),this._inlineSelector?t:u.s6,this._inlineSelector?u.s6:t,e?(0,u.qy)(n||(n=_`<p class="invalid-message">${0}</p>`),e.error_message):u.s6)}},{key:"_toggleEnabled",value:function(e){e.stopPropagation(),this._enabled=!this._enabled,this._propagateValue()}},{key:"_valueChange",value:function(e){e.stopPropagation(),this._haSelectorValue=e.detail.value,this._propagateValue()}},{key:"_propagateValue",value:function(){this._optionalBooleanSelector?(0,f.r)(this,"value-changed",{value:this._enabled===this._haSelectorValue?this._haSelectorValue:void 0}):(0,f.r)(this,"value-changed",{value:this._enabled?this._haSelectorValue:void 0})}}])}(u.WF);m.styles=(0,u.AH)(s||(s=_`
    :host {
      display: block;
      padding: 8px 16px 8px 0;
      border-top: 1px solid var(--divider-color);
    }
    .newline-selector {
      display: block;
      padding-top: 8px;
    }
    .body {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      row-gap: 8px;
    }
    .body > * {
      flex-grow: 1;
    }
    .text {
      flex-basis: 260px; /* min size of text - if inline selector is too big it will be pushed to next row */
    }
    .heading {
      margin: 0;
    }
    .description {
      margin: 0;
      display: block;
      padding-top: 4px;
      font-family: var(
        --mdc-typography-body2-font-family,
        var(--mdc-typography-font-family, Roboto, sans-serif)
      );
      -webkit-font-smoothing: antialiased;
      font-size: var(--mdc-typography-body2-font-size, 0.875rem);
      font-weight: var(--mdc-typography-body2-font-weight, 400);
      line-height: normal;
      color: var(--secondary-text-color);
    }

    .invalid {
      color: var(--error-color);
    }
    .invalid-message {
      font-size: 0.75rem;
      color: var(--error-color);
      padding-left: 16px;
    }
  `)),(0,p.__decorate)([(0,v.MZ)({attribute:!1})],m.prototype,"hass",void 0),(0,p.__decorate)([(0,v.MZ)()],m.prototype,"key",void 0),(0,p.__decorate)([(0,v.MZ)({attribute:!1})],m.prototype,"selector",void 0),(0,p.__decorate)([(0,v.MZ)()],m.prototype,"value",void 0),(0,p.__decorate)([(0,v.MZ)({attribute:!1})],m.prototype,"validationErrors",void 0),(0,p.__decorate)([(0,v.MZ)({attribute:!1})],m.prototype,"localizeFunction",void 0),(0,p.__decorate)([(0,v.wk)()],m.prototype,"_enabled",void 0),m=(0,p.__decorate)([(0,v.EM)("knx-selector-row")],m)},35672:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(78261),o=i(44734),r=i(56038),n=i(69683),s=i(6454),l=(i(28706),i(74423),i(62826)),d=i(96196),c=i(77845),h=i(92542),p=i(95096),u=i(70105),v=e([p,u]);[p,u]=v.then?(await v)():v;var g,f,y=e=>e,_=function(e){function t(){var e;(0,o.A)(this,t);for(var i=arguments.length,a=new Array(i),r=0;r<i;r++)a[r]=arguments[r];return(e=(0,n.A)(this,t,[].concat(a))).value=!0,e.key="sync_state",e.allowFalse=!1,e.localizeFunction=e=>e,e._strategy="true",e._minutes=60,e}return(0,s.A)(t,e),(0,r.A)(t,[{key:"_options",get:function(){return this.allowFalse?["true","init","expire","every","false"]:["true","init","expire","every"]}},{key:"_hasMinutes",value:function(e){return"expire"===e||"every"===e}},{key:"willUpdate",value:function(){if("boolean"!=typeof this.value){var e=this.value.split(" "),t=(0,a.A)(e,2),i=t[0],o=t[1];["true","false","init","expire","every"].includes(i)?this._strategy=i:this._strategy="true",+o&&(this._minutes=+o)}else this._strategy=this.value?"true":"false"}},{key:"render",value:function(){return(0,d.qy)(g||(g=y` <div class="inline">
      <ha-selector-select
        .hass=${0}
        .label=${0}
        .localizeValue=${0}
        .selector=${0}
        .key=${0}
        .value=${0}
        @value-changed=${0}
      >
      </ha-selector-select>
      <ha-selector-number
        .hass=${0}
        .disabled=${0}
        .selector=${0}
        .key=${0}
        .value=${0}
        @value-changed=${0}
      >
      </ha-selector-number>
    </div>`),this.hass,this.localizeFunction(`${this.key}.title`),this.localizeFunction,{select:{translation_key:this.key,multiple:!1,custom_value:!1,mode:"dropdown",options:this._options}},"strategy",this._strategy,this._handleChange,this.hass,!this._hasMinutes(this._strategy),{number:{min:2,max:1440,step:1,unit_of_measurement:"minutes"}},"minutes",this._minutes,this._handleChange)}},{key:"_handleChange",value:function(e){var t,i,a;e.stopPropagation(),"strategy"===e.target.key?(t=e.detail.value,i=this._minutes):(t=this._strategy,i=e.detail.value),a=this._hasMinutes(t)?`${t} ${i}`:"true"===t||"false"!==t&&t,(0,h.r)(this,"value-changed",{value:a})}}])}(d.WF);_.styles=(0,d.AH)(f||(f=y`
    .description {
      margin: 0;
      display: block;
      padding-top: 4px;
      padding-bottom: 8px;
      font-family: var(
        --mdc-typography-body2-font-family,
        var(--mdc-typography-font-family, Roboto, sans-serif)
      );
      -webkit-font-smoothing: antialiased;
      font-size: var(--mdc-typography-body2-font-size, 0.875rem);
      font-weight: var(--mdc-typography-body2-font-weight, 400);
      line-height: normal;
      color: var(--secondary-text-color);
    }
    .inline {
      width: 100%;
      display: inline-flex;
      flex-flow: row wrap;
      gap: 16px;
      justify-content: space-between;
    }
    .inline > * {
      flex: 1;
      width: 100%; /* to not overflow when wrapped */
    }
  `)),(0,l.__decorate)([(0,c.MZ)({attribute:!1})],_.prototype,"hass",void 0),(0,l.__decorate)([(0,c.MZ)()],_.prototype,"value",void 0),(0,l.__decorate)([(0,c.MZ)()],_.prototype,"key",void 0),(0,l.__decorate)([(0,c.MZ)({attribute:!1})],_.prototype,"allowFalse",void 0),(0,l.__decorate)([(0,c.MZ)({attribute:!1})],_.prototype,"localizeFunction",void 0),_=(0,l.__decorate)([(0,c.EM)("knx-sync-state-selector-row")],_),t()}catch(m){t(m)}}))},48011:function(e,t,i){i.a(e,(async function(e,t){try{var a=i(44734),o=i(56038),r=i(69683),n=i(6454),s=(i(26099),i(3362),i(9391),i(62826)),l=i(96196),d=i(77845),c=i(5871),h=i(53907),p=(i(95637),i(89473)),u=i(81774),v=i(92542),g=i(39396),f=i(65294),y=i(78577),_=e([h,p,u]);[h,p,u]=_.then?(await _)():_;var m,b,x=e=>e,k=new y.Q("create_device_dialog"),$=function(e){function t(){return(0,a.A)(this,t),(0,r.A)(this,t,arguments)}return(0,n.A)(t,e),(0,o.A)(t,[{key:"closeDialog",value:function(e){(0,v.r)(this,"create-device-dialog-closed",{newDevice:this._deviceEntry},{bubbles:!1})}},{key:"_createDevice",value:function(){(0,f.Jv)(this.hass,{name:this.deviceName,area_id:this.area}).then((e=>{this._deviceEntry=e})).catch((e=>{k.error("getGroupMonitorInfo",e),(0,c.o)("/knx/error",{replace:!0,data:e})})).finally((()=>{this.closeDialog(void 0)}))}},{key:"render",value:function(){return(0,l.qy)(m||(m=x`<ha-dialog
      open
      .heading=${0}
      scrimClickAction
      escapeKeyAction
      defaultAction="ignore"
    >
      <ha-selector-text
        .hass=${0}
        .label=${0}
        .required=${0}
        .selector=${0}
        .key=${0}
        .value=${0}
        @value-changed=${0}
      ></ha-selector-text>
      <ha-area-picker
        .hass=${0}
        .label=${0}
        .key=${0}
        .value=${0}
        @value-changed=${0}
      >
      </ha-area-picker>
      <ha-button slot="secondaryAction" @click=${0}>
        ${0}
      </ha-button>
      <ha-button slot="primaryAction" @click=${0}>
        ${0}
      </ha-button>
    </ha-dialog>`),"Create new device",this.hass,"Name",!0,{text:{}},"deviceName",this.deviceName,this._valueChanged,this.hass,"Area","area",this.area,this._valueChanged,this.closeDialog,this.hass.localize("ui.common.cancel"),this._createDevice,this.hass.localize("ui.common.add"))}},{key:"_valueChanged",value:function(e){e.stopPropagation();var t=e.target;null!=t&&t.key&&(this[t.key]=e.detail.value)}}],[{key:"styles",get:function(){return[g.nA,(0,l.AH)(b||(b=x`
        @media all and (min-width: 600px) {
          ha-dialog {
            --mdc-dialog-min-width: 480px;
          }
        }
      `))]}}])}(l.WF);(0,s.__decorate)([(0,d.MZ)({attribute:!1})],$.prototype,"hass",void 0),(0,s.__decorate)([(0,d.MZ)({attribute:!1})],$.prototype,"deviceName",void 0),(0,s.__decorate)([(0,d.wk)()],$.prototype,"area",void 0),$=(0,s.__decorate)([(0,d.EM)("knx-device-create-dialog")],$),t()}catch(w){t(w)}}))},36376:function(e,t,i){i.a(e,(async function(e,a){try{i.d(t,{N:function(){return l}});var o=i(43197),r=e([o]);o=(r.then?(await r)():r)[0];var n={binary_sensor:{iconPath:"M12 2C6.5 2 2 6.5 2 12S6.5 22 12 22 22 17.5 22 12 17.5 2 12 2M10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z",color:"var(--green-color)"},button:{iconPath:"M20 20.5C20 21.3 19.3 22 18.5 22H13C12.6 22 12.3 21.9 12 21.6L8 17.4L8.7 16.6C8.9 16.4 9.2 16.3 9.5 16.3H9.7L12 18V9C12 8.4 12.4 8 13 8S14 8.4 14 9V13.5L15.2 13.6L19.1 15.8C19.6 16 20 16.6 20 17.1V20.5M20 2H4C2.9 2 2 2.9 2 4V12C2 13.1 2.9 14 4 14H8V12H4V4H20V12H18V14H20C21.1 14 22 13.1 22 12V4C22 2.9 21.1 2 20 2Z",color:"var(--purple-color)"},climate:{color:"var(--red-color)"},cover:{iconPath:"M3 4H21V8H19V20H17V8H7V20H5V8H3V4M8 9H16V11H8V9M8 12H16V14H8V12M8 15H16V17H8V15M8 18H16V20H8V18Z",color:"var(--cyan-color)"},date:{color:"var(--lime-color)"},event:{iconPath:"M13 11H11V5H13M13 15H11V13H13M20 2H4C2.9 2 2 2.9 2 4V22L6 18H20C21.1 18 22 17.1 22 16V4C22 2.9 21.1 2 20 2Z",color:"var(--deep-orange-color)"},fan:{iconPath:"M12,11A1,1 0 0,0 11,12A1,1 0 0,0 12,13A1,1 0 0,0 13,12A1,1 0 0,0 12,11M12.5,2C17,2 17.11,5.57 14.75,6.75C13.76,7.24 13.32,8.29 13.13,9.22C13.61,9.42 14.03,9.73 14.35,10.13C18.05,8.13 22.03,8.92 22.03,12.5C22.03,17 18.46,17.1 17.28,14.73C16.78,13.74 15.72,13.3 14.79,13.11C14.59,13.59 14.28,14 13.88,14.34C15.87,18.03 15.08,22 11.5,22C7,22 6.91,18.42 9.27,17.24C10.25,16.75 10.69,15.71 10.89,14.79C10.4,14.59 9.97,14.27 9.65,13.87C5.96,15.85 2,15.07 2,11.5C2,7 5.56,6.89 6.74,9.26C7.24,10.25 8.29,10.68 9.22,10.87C9.41,10.39 9.73,9.97 10.14,9.65C8.15,5.96 8.94,2 12.5,2Z",color:"var(--light-grey-color)"},light:{color:"var(--amber-color)"},notify:{color:"var(--pink-color)"},number:{color:"var(--teal-color)"},scene:{color:"var(--deep-purple-color)"},select:{color:"var(--indigo-color)"},sensor:{color:"var(--orange-color)"},switch:{iconPath:"M18.4 1.6C18 1.2 17.5 1 17 1H7C6.5 1 6 1.2 5.6 1.6C5.2 2 5 2.5 5 3V21C5 21.5 5.2 22 5.6 22.4C6 22.8 6.5 23 7 23H17C17.5 23 18 22.8 18.4 22.4C18.8 22 19 21.5 19 21V3C19 2.5 18.8 2 18.4 1.6M16 7C16 7.6 15.6 8 15 8H9C8.4 8 8 7.6 8 7V5C8 4.4 8.4 4 9 4H15C15.6 4 16 4.4 16 5V7Z",color:"var(--blue-color)"},text:{color:"var(--brown-color)"},time:{color:"var(--light-green-color)"},valve:{iconPath:"M4 22H2V2H4M22 2H20V22H22M17.24 5.34L13.24 9.34A3 3 0 0 0 9.24 13.34L5.24 17.34L6.66 18.76L10.66 14.76A3 3 0 0 0 14.66 10.76L18.66 6.76Z",color:"var(--light-blue-color)"},weather:{color:"var(--yellow-color)"}};function l(e){return Object.assign({iconPath:o.l[e],color:"var(--dark-grey-color)"},n[e])}a()}catch(s){a(s)}}))},13384:function(e,t,i){i.d(t,{F:function(){return o},L:function(){return r}});var a=i(31432);function o(e,t,i,r){var n=t.split("."),s=n.pop();if(s){var l,d=e,c=(0,a.A)(n);try{for(c.s();!(l=c.n()).done;){var h=l.value;if(!(h in d)){if(void 0===i)return;d[h]={}}d=d[h]}}catch(p){c.e(p)}finally{c.f()}void 0===i?(r&&r.debug(`remove ${s} at ${t}`),delete d[s],!Object.keys(d).length&&n.length>0&&o(e,n.join("."),void 0)):(r&&r.debug(`update ${s} at ${t} with value`,i),d[s]=i)}}function r(e,t){var i,o=t.split("."),r=e,n=(0,a.A)(o);try{for(n.s();!(i=n.n()).done;){var s=i.value;if(!(s in r))return;r=r[s]}}catch(l){n.e(l)}finally{n.f()}return r}},53003:function(e,t,i){i.d(t,{L0:function(){return r},OM:function(){return n},dd:function(){return s}});i(2008),i(50113),i(18111),i(22489),i(20116),i(13579),i(26099),i(16034);var a=e=>"knx"===e[0],o=e=>e.identifiers.some(a),r=e=>Object.values(e.devices).filter(o),n=(e,t)=>Object.values(e.devices).find((e=>e.identifiers.find((e=>a(e)&&e[1]===t)))),s=e=>{var t=e.identifiers.find(a);return t?t[1]:void 0}},19337:function(e,t,i){i.d(t,{$k:function(){return h},Ah:function(){return s},HG:function(){return n},Vt:function(){return c},Yb:function(){return d},_O:function(){return p},oJ:function(){return u}});var a=i(94741),o=i(78261),r=(i(28706),i(2008),i(74423),i(62062),i(44114),i(72712),i(18111),i(22489),i(7588),i(61701),i(18237),i(13579),i(5506),i(26099),i(16034),i(38781),i(68156),i(42762),i(23500),i(22786)),n=(e,t)=>t.some((t=>e.main===t.main&&(!t.sub||e.sub===t.sub))),s=(e,t)=>{var i=((e,t)=>Object.entries(e.group_addresses).reduce(((e,i)=>{var a=(0,o.A)(i,2),r=a[0],s=a[1];return s.dpt&&n(s.dpt,t)&&(e[r]=s),e}),{}))(e,t);return Object.entries(e.communication_objects).reduce(((e,t)=>{var a=(0,o.A)(t,2),r=a[0],n=a[1];return n.group_address_links.some((e=>e in i))&&(e[r]=n),e}),{})};function l(e,t){var i=[];return e.forEach((e=>{"knx_group_address"!==e.type?"schema"in e&&i.push.apply(i,(0,a.A)(l(e.schema,t))):e.options.validDPTs?i.push.apply(i,(0,a.A)(e.options.validDPTs)):e.options.dptSelect?i.push.apply(i,(0,a.A)(e.options.dptSelect.map((e=>e.dpt)))):e.options.dptClasses&&i.push.apply(i,(0,a.A)(Object.values(t).filter((t=>e.options.dptClasses.includes(t.dpt_class))).map((e=>({main:e.main,sub:e.sub})))))})),i}var d=(0,r.A)(((e,t)=>l(e,t).reduce(((e,t)=>e.some((e=>{return a=t,(i=e).main===a.main&&i.sub===a.sub;var i,a}))?e:e.concat([t])),[]))),c=e=>null==e?"":e.main+(null!=e.sub?"."+e.sub.toString().padStart(3,"0"):""),h=e=>{if(!e)return null;var t=e.trim().split(".");if(0===t.length||t.length>2)return null;var i=Number.parseInt(t[0],10);if(Number.isNaN(i))return null;if(1===t.length)return{main:i,sub:null};var a=Number.parseInt(t[1],10);return Number.isNaN(a)?null:{main:i,sub:a}},p=(e,t)=>{var i,a;return e.main!==t.main?e.main-t.main:(null!==(i=e.sub)&&void 0!==i?i:-1)-(null!==(a=t.sub)&&void 0!==a?a:-1)},u=(e,t,i)=>{var a=i[c(e)];return!!a&&t.includes(a.dpt_class)}},56803:function(e,t,i){i.d(t,{B:function(){return d},J:function(){return l}});var a=i(44734),o=i(56038),r=(i(52675),i(89463),i(26099),i(16527)),n=new(i(78577).Q)("knx-drag-drop-context"),s=Symbol("drag-drop-context"),l=function(){return(0,o.A)((function e(t){(0,a.A)(this,e),this.gaDragStartHandler=e=>{var t,i=e.target,a=i.ga;a?(this._groupAddress=a,n.debug("dragstart",a.address,this),null===(t=e.dataTransfer)||void 0===t||t.setData("text/group-address",a.address),this._updateObservers()):n.warn("dragstart: no 'ga' property found",i)},this.gaDragEndHandler=e=>{n.debug("dragend",this),this._groupAddress=void 0,this._updateObservers()},this.gaDragIndicatorStartHandler=e=>{var t=e.target.ga;t&&(this._groupAddress=t,n.debug("drag indicator start",t.address,this),this._updateObservers())},this.gaDragIndicatorEndHandler=e=>{n.debug("drag indicator end",this),this._groupAddress=void 0,this._updateObservers()},this._updateObservers=t}),[{key:"groupAddress",get:function(){return this._groupAddress}}])}(),d=(0,r.q6)(s)},76674:function(e,t,i){i.d(t,{W:function(){return s},a:function(){return n}});var a=i(80638),o=i(47894),r=i(31432),n=(i(50113),i(44114),i(34782),i(18111),i(20116),i(26099),(e,t)=>{if(e){var i,n=[],s=(0,r.A)(e);try{for(s.s();!(i=s.n()).done;){var l=i.value;if(l.path){var d=(0,o.A)(l.path),c=d[0],h=(0,a.A)(d).slice(1);c===t&&n.push(Object.assign(Object.assign({},l),{},{path:h}))}}}catch(p){s.e(p)}finally{s.f()}return n.length?n:void 0}}),s=function(e){var t,i=arguments.length>1&&void 0!==arguments[1]?arguments[1]:void 0;return i&&(e=n(e,i)),null===(t=e)||void 0===t?void 0:t.find((e=>{var t;return 0===(null===(t=e.path)||void 0===t?void 0:t.length)}))}},75270:function(e,t,i){i.a(e,(async function(e,a){try{i.r(t),i.d(t,{KNXCreateEntity:function(){return W}});var o=i(78261),r=i(61397),n=i(50264),s=i(44734),l=i(56038),d=i(75864),c=i(69683),h=i(6454),p=(i(16280),i(18107),i(28706),i(74423),i(62062),i(18111),i(61701),i(26099),i(67357),i(62826)),u=i(96196),v=i(77845),g=i(16527),f=i(89302),y=i(54393),_=(i(29937),i(17963),i(95379),i(70748),i(60961),i(65300),i(5871)),m=i(76679),b=i(92542),x=i(62111),k=i(66820),$=(i(42615),i(65294)),w=i(36376),A=i(19337),M=i(56803),C=i(78577),D=e([y,k,w]);[y,k,w]=D.then?(await D)():D;var H,V,S,z,q,L,P,Z,E,T,O,j,I,B,F,G,N=e=>e,U=new C.Q("knx-create-entity"),W=function(e){function t(){var e,i,a,l;(0,s.A)(this,t);for(var h=arguments.length,p=new Array(h),u=0;u<h;u++)p[u]=arguments[u];return(e=(0,c.A)(this,t,[].concat(p)))._projectLoadTask=new f.YZ((0,d.A)(e),{args:()=>[],task:(l=(0,n.A)((0,r.A)().m((function t(){return(0,r.A)().w((function(t){for(;;)switch(t.n){case 0:if(e.knx.projectInfo){t.n=1;break}return t.a(2);case 1:if(!e.knx.projectData){t.n=2;break}return t.a(2);case 2:return t.n=3,e.knx.loadProject();case 3:return t.a(2)}}),t)}))),function(){return l.apply(this,arguments)})}),e._schemaLoadTask=new f.YZ((0,d.A)(e),{args:()=>[e.entityPlatform],task:(a=(0,n.A)((0,r.A)().m((function t(i){var a,n;return(0,r.A)().w((function(t){for(;;)switch(t.n){case 0:if(a=(0,o.A)(i,1),n=a[0]){t.n=1;break}return t.a(2);case 1:return t.n=2,e.knx.loadSchema(n);case 2:return t.a(2)}}),t)}))),function(e){return a.apply(this,arguments)})}),e._entityConfigLoadTask=new f.YZ((0,d.A)(e),{args:()=>[e.entityId],task:(i=(0,n.A)((0,r.A)().m((function t(i){var a,n,s,l,d;return(0,r.A)().w((function(t){for(;;)switch(t.n){case 0:if(a=(0,o.A)(i,1),n=a[0]){t.n=1;break}return t.a(2);case 1:return t.n=2,(0,$.wE)(e.hass,n);case 2:s=t.v,l=s.platform,d=s.data,e.entityPlatform=l,e._config=d;case 3:return t.a(2)}}),t)}))),function(e){return i.apply(this,arguments)})}),e._dragDropContextProvider=new g.DT((0,d.A)(e),{context:M.B,initialValue:new M.J((()=>{e._dragDropContextProvider.updateObservers()}))}),e._entityValidate=(0,x.n)((()=>{U.debug("validate",e._config),void 0!==e._config&&void 0!==e.entityPlatform&&(0,$.UD)(e.hass,{platform:e.entityPlatform,data:e._config}).then((t=>{e._handleValidationError(t,!1)})).catch((e=>{U.error("validateEntity",e),(0,_.o)("/knx/error",{replace:!0,data:e})}))}),250),e}return(0,h.A)(t,e),(0,l.A)(t,[{key:"willUpdate",value:function(e){if(e.has("route")){var t=this.route.prefix.split("/").at(-1);if("create"!==t&&"edit"!==t)return U.error("Unknown intent",t),void(this._intent=void 0);this._intent=t,this._config=void 0,this._validationErrors=void 0,this._validationBaseError=void 0,"create"===t?(this.entityId=void 0,this.entityPlatform=this.route.path.split("/")[1]):"edit"===t&&(this.entityId=this.route.path.split("/")[1])}}},{key:"render",value:function(){return this.hass&&this._intent?this._projectLoadTask.render({initial:()=>(0,u.qy)(V||(V=N`
        <hass-loading-screen .message=${0}></hass-loading-screen>
      `),"Waiting to fetch project data."),pending:()=>(0,u.qy)(S||(S=N`
        <hass-loading-screen .message=${0}></hass-loading-screen>
      `),"Loading KNX project data."),error:e=>this._renderError("Error loading KNX project",e),complete:()=>"edit"===this._intent?this._renderEdit():this._renderCreate()}):(0,u.qy)(H||(H=N` <hass-loading-screen></hass-loading-screen> `))}},{key:"_renderCreate",value:function(){return this.entityPlatform?this.knx.supportedPlatforms.includes(this.entityPlatform)?this._renderLoadSchema():(U.error("Unknown platform",this.entityPlatform),this._renderTypeSelection()):this._renderTypeSelection()}},{key:"_renderEdit",value:function(){return this._entityConfigLoadTask.render({initial:()=>(0,u.qy)(z||(z=N`
        <hass-loading-screen .message=${0}></hass-loading-screen>
      `),"Waiting to fetch entity data."),pending:()=>(0,u.qy)(q||(q=N`
        <hass-loading-screen .message=${0}></hass-loading-screen>
      `),"Loading entity data."),error:e=>this._renderError((0,u.qy)(L||(L=N`${0}:
            <code>${0}</code>`),this.hass.localize("ui.card.common.entity_not_found"),this.entityId),e),complete:()=>this.entityPlatform?this.knx.supportedPlatforms.includes(this.entityPlatform)?this._renderLoadSchema():this._renderError("Unsupported platform","Unsupported platform: "+this.entityPlatform):this._renderError((0,u.qy)(P||(P=N`${0}:
              <code>${0}</code>`),this.hass.localize("ui.card.common.entity_not_found"),this.entityId),new Error("Entity platform unknown"))})}},{key:"_renderLoadSchema",value:function(){return this._schemaLoadTask.render({initial:()=>(0,u.qy)(Z||(Z=N`
        <hass-loading-screen .message=${0}></hass-loading-screen>
      `),"Waiting to fetch schema."),pending:()=>(0,u.qy)(E||(E=N`
        <hass-loading-screen .message=${0}></hass-loading-screen>
      `),"Loading entity platform schema."),error:e=>this._renderError("Error loading schema",e),complete:()=>this._renderEntityConfig(this.entityPlatform)})}},{key:"_renderError",value:function(e,t){return U.error("Error in create/edit entity",t),(0,u.qy)(T||(T=N`
      <hass-subpage
        .hass=${0}
        .narrow=${0}
        .back-path=${0}
        .header=${0}
      >
        <div class="content">
          <ha-alert alert-type="error"> ${0} </ha-alert>
        </div>
      </hass-subpage>
    `),this.hass,this.narrow,this.backPath,this.hass.localize("ui.panel.config.integrations.config_flow.error"),e)}},{key:"_renderTypeSelection",value:function(){return(0,u.qy)(O||(O=N`
      <hass-subpage
        .hass=${0}
        .narrow=${0}
        .back-path=${0}
        .header=${0}
      >
        <div class="type-selection">
          <ha-card
            outlined
            .header=${0}
          >
            <!-- <p>Some help text</p> -->
            <ha-navigation-list
              .hass=${0}
              .narrow=${0}
              .pages=${0}
              has-secondary
              .label=${0}
            ></ha-navigation-list>
          </ha-card>
        </div>
      </hass-subpage>
    `),this.hass,this.narrow,this.backPath,this.hass.localize("component.knx.config_panel.entities.create.title"),this.hass.localize("component.knx.config_panel.entities.create.type_selection.header"),this.hass,this.narrow,this.knx.supportedPlatforms.map((e=>{var t=(0,w.N)(e);return{name:`${this.hass.localize(`component.${e}.title`)}`,description:`${this.hass.localize(`component.knx.config_panel.entities.create.${e}.description`)}`,iconPath:t.iconPath,iconColor:t.color,path:`/knx/entities/create/${e}`}})),this.hass.localize("component.knx.config_panel.entities.create.type_selection.header"))}},{key:"_renderEntityConfig",value:function(e){var t,i,a="create"===this._intent,o=this.knx.schema[e];return(0,u.qy)(j||(j=N`<hass-subpage
      .hass=${0}
      .narrow=${0}
      .back-path=${0}
      .header=${0}
    >
      <div class="content">
        <div class="entity-config">
          <knx-configure-entity
            .hass=${0}
            .knx=${0}
            .platform=${0}
            .config=${0}
            .schema=${0}
            .validationErrors=${0}
            @knx-entity-configuration-changed=${0}
          >
            ${0}
          </knx-configure-entity>
          <ha-fab
            .label=${0}
            extended
            @click=${0}
            ?disabled=${0}
          >
            <ha-svg-icon slot="icon" .path=${0}></ha-svg-icon>
          </ha-fab>
        </div>
        ${0}
      </div>
    </hass-subpage>`),this.hass,this.narrow,this.backPath,a?this.hass.localize("component.knx.config_panel.entities.create.title"):`${this.hass.localize("ui.common.edit")}: ${this.entityId}`,this.hass,this.knx,e,this._config,o,this._validationErrors,this._configChanged,this._validationBaseError?(0,u.qy)(I||(I=N`<ha-alert slot="knx-validation-error" alert-type="error">
                  <details>
                    <summary><b>Validation error</b></summary>
                    <p>Base error: ${0}</p>
                    ${0}
                  </details>
                </ha-alert>`),this._validationBaseError,null!==(t=null===(i=this._validationErrors)||void 0===i?void 0:i.map((e=>{var t;return(0,u.qy)(B||(B=N`<p>
                          ${0}: ${0} in ${0}
                        </p>`),e.error_class,e.error_message,null===(t=e.path)||void 0===t?void 0:t.join(" / "))})))&&void 0!==t?t:u.s6):u.s6,a?this.hass.localize("ui.common.create"):this.hass.localize("ui.common.save"),a?this._entityCreate:this._entityUpdate,void 0===this._config,a?"M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z":"M5,3A2,2 0 0,0 3,5V19A2,2 0 0,0 5,21H19A2,2 0 0,0 21,19V5.5L18.5,3H17V9A1,1 0 0,1 16,10H8A1,1 0 0,1 7,9V3H5M12,4V9H15V4H12M7,12H17A1,1 0 0,1 18,13V19H6V13A1,1 0 0,1 7,12Z",this.knx.projectData?(0,u.qy)(F||(F=N` <div class="panel">
              <knx-project-device-tree
                .data=${0}
                .validDPTs=${0}
              ></knx-project-device-tree>
            </div>`),this.knx.projectData,(0,A.Yb)(o,this.knx.dptMetadata)):u.s6)}},{key:"_configChanged",value:function(e){e.stopPropagation(),U.debug("configChanged",e.detail),this._config=e.detail,this._validationErrors&&this._entityValidate()}},{key:"_entityCreate",value:function(e){e.stopPropagation(),void 0!==this._config&&void 0!==this.entityPlatform?(0,$.S$)(this.hass,{platform:this.entityPlatform,data:this._config}).then((e=>{this._handleValidationError(e,!0)||(U.debug("Successfully created entity",e.entity_id),(0,_.o)("/knx/entities",{replace:!0}),e.entity_id?this._entityMoreInfoSettings(e.entity_id):U.error("entity_id not found after creation."))})).catch((e=>{U.error("Error creating entity",e),(0,_.o)("/knx/error",{replace:!0,data:e})})):U.error("No config found.")}},{key:"_entityUpdate",value:function(e){e.stopPropagation(),void 0!==this._config&&void 0!==this.entityId&&void 0!==this.entityPlatform?(0,$.zU)(this.hass,{platform:this.entityPlatform,entity_id:this.entityId,data:this._config}).then((e=>{this._handleValidationError(e,!0)||(U.debug("Successfully updated entity",this.entityId),(0,_.o)("/knx/entities",{replace:!0}))})).catch((e=>{U.error("Error updating entity",e),(0,_.o)("/knx/error",{replace:!0,data:e})})):U.error("No config found.")}},{key:"_handleValidationError",value:function(e,t){return!1===e.success?(U.warn("Validation error",e),this._validationErrors=e.errors,this._validationBaseError=e.error_base,t&&setTimeout((()=>this._alertElement.scrollIntoView({behavior:"smooth"}))),!0):(this._validationErrors=void 0,this._validationBaseError=void 0,U.debug("Validation passed",e.entity_id),!1)}},{key:"_entityMoreInfoSettings",value:function(e){(0,b.r)(m.G.document.querySelector("home-assistant"),"hass-more-info",{entityId:e,view:"settings"})}}])}(u.WF);W.styles=(0,u.AH)(G||(G=N`
    hass-loading-screen {
      --app-header-background-color: var(--sidebar-background-color);
      --app-header-text-color: var(--sidebar-text-color);
    }

    .type-selection {
      margin: 20px auto 80px;
      max-width: 720px;
    }

    ha-card {
      overflow: hidden; /* don't cover rounded corner border by content */
    }

    @media screen and (max-width: 600px) {
      .panel {
        display: none;
      }
    }

    .content {
      display: flex;
      flex-direction: row;
      height: 100%;
      width: 100%;

      & > .entity-config {
        flex-grow: 1;
        flex-shrink: 1;
        height: 100%;
        overflow-y: scroll;
      }

      & > .panel {
        flex-grow: 0;
        flex-shrink: 3;
        width: 480px;
        min-width: 280px;
      }
    }

    knx-configure-entity {
      display: block;
      margin: 20px auto 40px; /* leave 80px space for fab */
      max-width: 720px;
    }

    ha-alert {
      display: block;
      margin: 20px auto;
      max-width: 720px;

      & summary {
        padding: 10px;
      }
    }

    ha-fab {
      /* not slot="fab" to move out of panel */
      float: right;
      margin-right: calc(16px + env(safe-area-inset-right));
      margin-bottom: 40px;
      z-index: 1;
    }
  `)),(0,p.__decorate)([(0,v.MZ)({type:Object})],W.prototype,"hass",void 0),(0,p.__decorate)([(0,v.MZ)({attribute:!1})],W.prototype,"knx",void 0),(0,p.__decorate)([(0,v.MZ)({type:Object})],W.prototype,"route",void 0),(0,p.__decorate)([(0,v.MZ)({type:Boolean,reflect:!0})],W.prototype,"narrow",void 0),(0,p.__decorate)([(0,v.MZ)({type:String,attribute:"back-path"})],W.prototype,"backPath",void 0),(0,p.__decorate)([(0,v.wk)()],W.prototype,"_config",void 0),(0,p.__decorate)([(0,v.wk)()],W.prototype,"_validationErrors",void 0),(0,p.__decorate)([(0,v.wk)()],W.prototype,"_validationBaseError",void 0),(0,p.__decorate)([(0,v.P)("ha-alert")],W.prototype,"_alertElement",void 0),W=(0,p.__decorate)([(0,v.EM)("knx-create-entity")],W),a()}catch(R){a(R)}}))}}]);
//# sourceMappingURL=7787.9617914a63da62b2.js.map