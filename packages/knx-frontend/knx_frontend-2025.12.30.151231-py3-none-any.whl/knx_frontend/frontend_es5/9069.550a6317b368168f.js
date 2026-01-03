"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["9069"],{68006:function(e,t,r){r.d(t,{z:function(){return o}});r(2892),r(26099),r(38781);var o=e=>{if(void 0!==e){if("object"!=typeof e){if("string"==typeof e||isNaN(e)){var t=(null==e?void 0:e.toString().split(":"))||[];if(1===t.length)return{seconds:Number(t[0])};if(t.length>3)return;var r=Number(t[2])||0,o=Math.floor(r);return{hours:Number(t[0])||0,minutes:Number(t[1])||0,seconds:o,milliseconds:Math.floor(1e3*Number((r-o).toFixed(4)))}}return{seconds:e}}if(!("days"in e))return e;var i=e.days,n=e.minutes,a=e.seconds,s=e.milliseconds,l=e.hours||0;return{hours:l=(l||0)+24*(i||0),minutes:n,seconds:a,milliseconds:s}}}},10253:function(e,t,r){r.a(e,(async function(e,o){try{r.d(t,{P:function(){return c}});r(74423),r(25276);var i=r(22),n=r(58109),a=r(81793),s=r(44740),l=e([i]);i=(l.then?(await l)():l)[0];var c=e=>e.first_weekday===a.zt.language?"weekInfo"in Intl.Locale.prototype?new Intl.Locale(e.language).weekInfo.firstDay%7:(0,n.S)(e.language)%7:s.Z.includes(e.first_weekday)?s.Z.indexOf(e.first_weekday):1;o()}catch(d){o(d)}}))},84834:function(e,t,r){r.a(e,(async function(e,o){try{r.d(t,{Yq:function(){return c},zB:function(){return u}});r(50113),r(18111),r(20116),r(26099);var i=r(22),n=r(22786),a=r(81793),s=r(74309),l=e([i,s]);[i,s]=l.then?(await l)():l;(0,n.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{weekday:"long",month:"long",day:"numeric",timeZone:(0,s.w)(e.time_zone,t)})));var c=(e,t,r)=>d(t,r.time_zone).format(e),d=(0,n.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"long",day:"numeric",timeZone:(0,s.w)(e.time_zone,t)}))),u=((0,n.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"short",day:"numeric",timeZone:(0,s.w)(e.time_zone,t)}))),(e,t,r)=>{var o,i,n,s,l=h(t,r.time_zone);if(t.date_format===a.ow.language||t.date_format===a.ow.system)return l.format(e);var c=l.formatToParts(e),d=null===(o=c.find((e=>"literal"===e.type)))||void 0===o?void 0:o.value,u=null===(i=c.find((e=>"day"===e.type)))||void 0===i?void 0:i.value,p=null===(n=c.find((e=>"month"===e.type)))||void 0===n?void 0:n.value,f=null===(s=c.find((e=>"year"===e.type)))||void 0===s?void 0:s.value,y=c[c.length-1],v="literal"===(null==y?void 0:y.type)?null==y?void 0:y.value:"";return"bg"===t.language&&t.date_format===a.ow.YMD&&(v=""),{[a.ow.DMY]:`${u}${d}${p}${d}${f}${v}`,[a.ow.MDY]:`${p}${d}${u}${d}${f}${v}`,[a.ow.YMD]:`${f}${d}${p}${d}${u}${v}`}[t.date_format]}),h=(0,n.A)(((e,t)=>{var r=e.date_format===a.ow.system?void 0:e.language;return e.date_format===a.ow.language||(e.date_format,a.ow.system),new Intl.DateTimeFormat(r,{year:"numeric",month:"numeric",day:"numeric",timeZone:(0,s.w)(e.time_zone,t)})}));(0,n.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{day:"numeric",month:"short",timeZone:(0,s.w)(e.time_zone,t)}))),(0,n.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{month:"long",year:"numeric",timeZone:(0,s.w)(e.time_zone,t)}))),(0,n.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{month:"long",timeZone:(0,s.w)(e.time_zone,t)}))),(0,n.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",timeZone:(0,s.w)(e.time_zone,t)}))),(0,n.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{weekday:"long",timeZone:(0,s.w)(e.time_zone,t)}))),(0,n.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{weekday:"short",timeZone:(0,s.w)(e.time_zone,t)})));o()}catch(p){o(p)}}))},49284:function(e,t,r){r.a(e,(async function(e,o){try{r.d(t,{r6:function(){return u},yg:function(){return p}});var i=r(22),n=r(22786),a=r(84834),s=r(4359),l=r(74309),c=r(59006),d=e([i,a,s,l]);[i,a,s,l]=d.then?(await d)():d;var u=(e,t,r)=>h(t,r.time_zone).format(e),h=(0,n.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"long",day:"numeric",hour:(0,c.J)(e)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,c.J)(e)?"h12":"h23",timeZone:(0,l.w)(e.time_zone,t)}))),p=((0,n.A)((()=>new Intl.DateTimeFormat(void 0,{year:"numeric",month:"long",day:"numeric",hour:"2-digit",minute:"2-digit"}))),(0,n.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"short",day:"numeric",hour:(0,c.J)(e)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,c.J)(e)?"h12":"h23",timeZone:(0,l.w)(e.time_zone,t)}))),(0,n.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{month:"short",day:"numeric",hour:(0,c.J)(e)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,c.J)(e)?"h12":"h23",timeZone:(0,l.w)(e.time_zone,t)}))),(e,t,r)=>f(t,r.time_zone).format(e)),f=(0,n.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{year:"numeric",month:"long",day:"numeric",hour:(0,c.J)(e)?"numeric":"2-digit",minute:"2-digit",second:"2-digit",hourCycle:(0,c.J)(e)?"h12":"h23",timeZone:(0,l.w)(e.time_zone,t)})));o()}catch(y){o(y)}}))},88738:function(e,t,r){r.a(e,(async function(e,o){try{r.d(t,{i:function(){return d},nR:function(){return l}});r(16280);var i=r(22),n=r(22786),a=e([i]);i=(a.then?(await a)():a)[0];var s=e=>e<10?`0${e}`:e,l=(e,t)=>{var r=t.days||0,o=t.hours||0,i=t.minutes||0,n=t.seconds||0,a=t.milliseconds||0;return r>0?`${Intl.NumberFormat(e.language,{style:"unit",unit:"day",unitDisplay:"long"}).format(r)} ${o}:${s(i)}:${s(n)}`:o>0?`${o}:${s(i)}:${s(n)}`:i>0?`${i}:${s(n)}`:n>0?Intl.NumberFormat(e.language,{style:"unit",unit:"second",unitDisplay:"long"}).format(n):a>0?Intl.NumberFormat(e.language,{style:"unit",unit:"millisecond",unitDisplay:"long"}).format(a):null},c=(0,n.A)((e=>new Intl.DurationFormat(e.language,{style:"long"}))),d=(e,t)=>c(e).format(t);(0,n.A)((e=>new Intl.DurationFormat(e.language,{style:"digital",hoursDisplay:"auto"}))),(0,n.A)((e=>new Intl.DurationFormat(e.language,{style:"narrow",daysDisplay:"always"}))),(0,n.A)((e=>new Intl.DurationFormat(e.language,{style:"narrow",hoursDisplay:"always"}))),(0,n.A)((e=>new Intl.DurationFormat(e.language,{style:"narrow",minutesDisplay:"always"})));o()}catch(u){o(u)}}))},4359:function(e,t,r){r.a(e,(async function(e,o){try{r.d(t,{LW:function(){return y},Xs:function(){return p},fU:function(){return c},ie:function(){return u}});var i=r(22),n=r(22786),a=r(74309),s=r(59006),l=e([i,a]);[i,a]=l.then?(await l)():l;var c=(e,t,r)=>d(t,r.time_zone).format(e),d=(0,n.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{hour:"numeric",minute:"2-digit",hourCycle:(0,s.J)(e)?"h12":"h23",timeZone:(0,a.w)(e.time_zone,t)}))),u=(e,t,r)=>h(t,r.time_zone).format(e),h=(0,n.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{hour:(0,s.J)(e)?"numeric":"2-digit",minute:"2-digit",second:"2-digit",hourCycle:(0,s.J)(e)?"h12":"h23",timeZone:(0,a.w)(e.time_zone,t)}))),p=(e,t,r)=>f(t,r.time_zone).format(e),f=(0,n.A)(((e,t)=>new Intl.DateTimeFormat(e.language,{weekday:"long",hour:(0,s.J)(e)?"numeric":"2-digit",minute:"2-digit",hourCycle:(0,s.J)(e)?"h12":"h23",timeZone:(0,a.w)(e.time_zone,t)}))),y=(e,t,r)=>v(t,r.time_zone).format(e),v=(0,n.A)(((e,t)=>new Intl.DateTimeFormat("en-GB",{hour:"numeric",minute:"2-digit",hour12:!1,timeZone:(0,a.w)(e.time_zone,t)})));o()}catch(m){o(m)}}))},74309:function(e,t,r){r.a(e,(async function(e,o){try{r.d(t,{w:function(){return h}});var i,n,a,s=r(22),l=r(81793),c=e([s]);s=(c.then?(await c)():c)[0];var d=null===(i=Intl.DateTimeFormat)||void 0===i||null===(n=(a=i.call(Intl)).resolvedOptions)||void 0===n?void 0:n.call(a).timeZone,u=null!=d?d:"UTC",h=(e,t)=>e===l.Wj.local&&d?u:t;o()}catch(p){o(p)}}))},21754:function(e,t,r){r.d(t,{A:function(){return i}});var o=e=>e<10?`0${e}`:e;function i(e){var t=Math.floor(e/3600),r=Math.floor(e%3600/60),i=Math.floor(e%3600%60);return t>0?`${t}:${o(r)}:${o(i)}`:r>0?`${r}:${o(i)}`:i>0?""+i:null}},59006:function(e,t,r){r.d(t,{J:function(){return n}});r(74423);var o=r(22786),i=r(81793),n=(0,o.A)((e=>{if(e.time_format===i.Hg.language||e.time_format===i.Hg.system){var t=e.time_format===i.Hg.language?e.language:void 0;return new Date("January 1, 2023 22:00:00").toLocaleString(t).includes("10")}return e.time_format===i.Hg.am_pm}))},44740:function(e,t,r){r.d(t,{Z:function(){return o}});var o=["sunday","monday","tuesday","wednesday","thursday","friday","saturday"]},42256:function(e,t,r){r.d(t,{I:function(){return s}});var o=r(44734),i=r(56038),n=(r(16280),r(25276),r(44114),r(54554),r(18111),r(7588),r(33110),r(26099),r(58335),r(23500),function(){return(0,i.A)((function e(){var t=arguments.length>0&&void 0!==arguments[0]?arguments[0]:window.localStorage;(0,o.A)(this,e),this._storage={},this._listeners={},this.storage=t,this.storage===window.localStorage&&window.addEventListener("storage",(e=>{e.key&&this.hasKey(e.key)&&(this._storage[e.key]=e.newValue?JSON.parse(e.newValue):e.newValue,this._listeners[e.key]&&this._listeners[e.key].forEach((t=>t(e.oldValue?JSON.parse(e.oldValue):e.oldValue,this._storage[e.key]))))}))}),[{key:"addFromStorage",value:function(e){if(!this._storage[e]){var t=this.storage.getItem(e);t&&(this._storage[e]=JSON.parse(t))}}},{key:"subscribeChanges",value:function(e,t){return this._listeners[e]?this._listeners[e].push(t):this._listeners[e]=[t],()=>{this.unsubscribeChanges(e,t)}}},{key:"unsubscribeChanges",value:function(e,t){if(e in this._listeners){var r=this._listeners[e].indexOf(t);-1!==r&&this._listeners[e].splice(r,1)}}},{key:"hasKey",value:function(e){return e in this._storage}},{key:"getValue",value:function(e){return this._storage[e]}},{key:"setValue",value:function(e,t){var r=this._storage[e];this._storage[e]=t;try{void 0===t?this.storage.removeItem(e):this.storage.setItem(e,JSON.stringify(t))}catch(o){}finally{this._listeners[e]&&this._listeners[e].forEach((e=>e(r,t)))}}}])}()),a={};function s(e){return(t,r)=>{if("object"==typeof r)throw new Error("This decorator does not support this compilation type.");var o,i=e.storage||"localStorage";i&&i in a?o=a[i]:(o=new n(window[i]),a[i]=o);var s=e.key||String(r);o.addFromStorage(s);var l=!1!==e.subscribe?e=>o.subscribeChanges(s,((t,o)=>{e.requestUpdate(r,t)})):void 0,c=()=>o.hasKey(s)?e.deserializer?e.deserializer(o.getValue(s)):o.getValue(s):void 0,d=(t,i)=>{var n;e.state&&(n=c()),o.setValue(s,e.serializer?e.serializer(i):i),e.state&&t.requestUpdate(r,n)},u=t.performUpdate;if(t.performUpdate=function(){this.__initialized=!0,u.call(this)},e.subscribe){var h=t.connectedCallback,p=t.disconnectedCallback;t.connectedCallback=function(){h.call(this);this.__unbsubLocalStorage||(this.__unbsubLocalStorage=null==l?void 0:l(this))},t.disconnectedCallback=function(){var e;p.call(this);var t=this;null===(e=t.__unbsubLocalStorage)||void 0===e||e.call(t),t.__unbsubLocalStorage=void 0}}var f,y=Object.getOwnPropertyDescriptor(t,r);if(void 0===y)f={get(){return c()},set(e){(this.__initialized||void 0===c())&&d(this,e)},configurable:!0,enumerable:!0};else{var v=y.set;f=Object.assign(Object.assign({},y),{},{get(){return c()},set(e){(this.__initialized||void 0===c())&&d(this,e),null==v||v.call(this,e)}})}Object.defineProperty(t,r,f)}}},91737:function(e,t,r){r.d(t,{C:function(){return o}});var o=e=>{e.preventDefault(),e.stopPropagation()}},55124:function(e,t,r){r.d(t,{d:function(){return o}});var o=e=>e.stopPropagation()},48551:function(e,t,r){r.a(e,(async function(e,o){try{r.d(t,{R:function(){return u}});r(62062),r(18111),r(61701),r(13579),r(33110),r(26099),r(27495),r(25440);var i=r(2654),n=(r(34099),r(84834)),a=r(49284),s=r(20679),l=r(74522),c=(r(24131),r(89919),r(41144)),d=(r(97382),e([i,n,a,s]));[i,n,a,s]=d.then?(await d)():d;var u=(e,t,r,o)=>{var i=t.entity_id,n=t.attributes.device_class,a=(0,c.m)(i),s=r[i],d=null==s?void 0:s.translation_key;return d&&e(`component.${s.platform}.entity.${a}.${d}.state_attributes.${o}.name`)||n&&e(`component.${a}.entity_component.${n}.state_attributes.${o}.name`)||e(`component.${a}.entity_component._.state_attributes.${o}.name`)||(0,l.Z)(o.replace(/_/g," ").replace(/\bid\b/g,"ID").replace(/\bip\b/g,"IP").replace(/\bmac\b/g,"MAC").replace(/\bgps\b/g,"GPS"))};o()}catch(h){o(h)}}))},28724:function(e,t,r){r.d(t,{e:function(){return o}});var o=e=>"latitude"in e.attributes&&"longitude"in e.attributes},74522:function(e,t,r){r.d(t,{Z:function(){return o}});r(34782);var o=e=>e.charAt(0).toUpperCase()+e.slice(1)},39680:function(e,t,r){r.a(e,(async function(e,o){try{r.d(t,{c:function(){return s},q:function(){return l}});var i=r(22),n=r(22786),a=e([i]);i=(a.then?(await a)():a)[0];var s=(e,t)=>c(e).format(t),l=(e,t)=>d(e).format(t),c=(0,n.A)((e=>new Intl.ListFormat(e.language,{style:"long",type:"conjunction"}))),d=(0,n.A)((e=>new Intl.ListFormat(e.language,{style:"long",type:"disjunction"})));o()}catch(u){o(u)}}))},72125:function(e,t,r){r.d(t,{F:function(){return i},r:function(){return n}});r(18111),r(13579),r(26099),r(16034),r(27495),r(90906);var o=/{%|{{/,i=e=>o.test(e),n=e=>!!e&&("string"==typeof e?i(e):"object"==typeof e&&(Array.isArray(e)?e:Object.values(e)).some((e=>e&&n(e))))},24131:function(e,t,r){r(84864),r(57465),r(27495),r(90906),r(38781);var o="^\\d{4}-(0[1-9]|1[0-2])-([12]\\d|0[1-9]|3[01])";new RegExp(o+"$"),new RegExp(o)},89919:function(e,t,r){r(27495),r(90906)},91225:function(e,t,r){r.d(t,{_:function(){return n}});var o=r(31432),i=(r(44114),r(33110),r(27495),r(25440),r(96685)),n=(e,t)=>{if(!(t instanceof i.C5))return{warnings:[t.message],errors:void 0};var r,n=[],a=[],s=(0,o.A)(t.failures());try{for(s.s();!(r=s.n()).done;){var l=r.value;if(void 0===l.value)n.push(e.localize("ui.errors.config.key_missing",{key:l.path.join(".")}));else if("never"===l.type)a.push(e.localize("ui.errors.config.key_not_expected",{key:l.path.join(".")}));else{if("union"===l.type)continue;"enums"===l.type?a.push(e.localize("ui.errors.config.key_wrong_type",{key:l.path.join("."),type_correct:l.message.replace("Expected ","").split(", ")[0],type_wrong:JSON.stringify(l.value)})):a.push(e.localize("ui.errors.config.key_wrong_type",{key:l.path.join("."),type_correct:l.refinement||l.type,type_wrong:JSON.stringify(l.value)}))}}}catch(t){s.e(t)}finally{s.f()}return{warnings:a,errors:n}}},9169:function(e,t,r){r(78261),r(31432),r(23792),r(18111),r(7588),r(5506),r(26099),r(27495),r(38781),r(5746),r(23500),r(62953),r(48408),r(14603),r(47566),r(98721),r(76679)},7078:function(e,t,r){r.d(t,{V:function(){return T}});var o,i=r(78261),n=r(61397),a=r(50264),s=r(44734),l=r(56038),c=r(69683),d=r(6454),u=r(25460),h=(r(48980),r(74423),r(62062),r(26910),r(18111),r(61701),r(26099),r(62826)),p=r(16527),f=r(96196),y=r(77845),v=r(92542),m=r(34972),g=r(74687),_=r(5691),b=r(28522),w=function(e){function t(){return(0,s.A)(this,t),(0,c.A)(this,t,arguments)}return(0,d.A)(t,e),(0,l.A)(t)}(_.$);w.styles=[b.R,(0,f.AH)(o||(o=(e=>e)`
      :host {
        --ha-icon-display: block;
        --md-sys-color-primary: var(--primary-text-color);
        --md-sys-color-secondary: var(--secondary-text-color);
        --md-sys-color-surface: var(--card-background-color);
        --md-sys-color-on-surface: var(--primary-text-color);
        --md-sys-color-on-surface-variant: var(--secondary-text-color);
      }
    `))],w=(0,h.__decorate)([(0,y.EM)("ha-md-select-option")],w);var A,x=r(38048),k=r(7138),$=r(83538),z=function(e){function t(){return(0,s.A)(this,t),(0,c.A)(this,t,arguments)}return(0,d.A)(t,e),(0,l.A)(t)}(x.V);z.styles=[k.R,$.R,(0,f.AH)(A||(A=(e=>e)`
      :host {
        --ha-icon-display: block;
        --md-sys-color-primary: var(--primary-text-color);
        --md-sys-color-secondary: var(--secondary-text-color);
        --md-sys-color-surface: var(--card-background-color);
        --md-sys-color-on-surface-variant: var(--secondary-text-color);

        --md-sys-color-surface-container-highest: var(--input-fill-color);
        --md-sys-color-on-surface: var(--input-ink-color);

        --md-sys-color-surface-container: var(--input-fill-color);
        --md-sys-color-on-secondary-container: var(--primary-text-color);
        --md-sys-color-secondary-container: var(--input-fill-color);
        --md-menu-container-color: var(--card-background-color);
      }
    `))],z=(0,h.__decorate)([(0,y.EM)("ha-md-select")],z);var M,q,C,Z,E,S=r(55124),O=e=>e,I="NO_AUTOMATION",D="UNKNOWN_AUTOMATION",T=function(e){function t(e,r,o){var i;return(0,s.A)(this,t),(i=(0,c.A)(this,t))._automations=[],i._renderEmpty=!1,i._localizeDeviceAutomation=e,i._fetchDeviceAutomations=r,i._createNoAutomation=o,i}return(0,d.A)(t,e),(0,l.A)(t,[{key:"NO_AUTOMATION_TEXT",get:function(){return this.hass.localize("ui.panel.config.devices.automation.actions.no_actions")}},{key:"UNKNOWN_AUTOMATION_TEXT",get:function(){return this.hass.localize("ui.panel.config.devices.automation.actions.unknown_action")}},{key:"_value",get:function(){if(!this.value)return"";if(!this._automations.length)return I;var e=this._automations.findIndex((e=>(0,g.Po)(this._entityReg,e,this.value)));return-1===e?D:`${this._automations[e].device_id}_${e}`}},{key:"render",value:function(){if(this._renderEmpty)return f.s6;var e=this._value;return(0,f.qy)(M||(M=O`
      <ha-md-select
        .label=${0}
        .value=${0}
        @change=${0}
        @closed=${0}
        .disabled=${0}
      >
        ${0}
        ${0}
        ${0}
      </ha-md-select>
    `),this.label,e,this._automationChanged,S.d,0===this._automations.length,e===I?(0,f.qy)(q||(q=O`<ha-md-select-option .value=${0}>
              ${0}
            </ha-md-select-option>`),I,this.NO_AUTOMATION_TEXT):f.s6,e===D?(0,f.qy)(C||(C=O`<ha-md-select-option .value=${0}>
              ${0}
            </ha-md-select-option>`),D,this.UNKNOWN_AUTOMATION_TEXT):f.s6,this._automations.map(((e,t)=>(0,f.qy)(Z||(Z=O`
            <ha-md-select-option .value=${0}>
              ${0}
            </ha-md-select-option>
          `),`${e.device_id}_${t}`,this._localizeDeviceAutomation(this.hass,this._entityReg,e)))))}},{key:"updated",value:function(e){(0,u.A)(t,"updated",this,3)([e]),e.has("deviceId")&&this._updateDeviceInfo()}},{key:"_updateDeviceInfo",value:(r=(0,a.A)((0,n.A)().m((function e(){var t;return(0,n.A)().w((function(e){for(;;)switch(e.n){case 0:if(!this.deviceId){e.n=2;break}return e.n=1,this._fetchDeviceAutomations(this.hass,this.deviceId);case 1:t=e.v.sort(g.RK),e.n=3;break;case 2:t=[];case 3:return this._automations=t,this.value&&this.value.device_id===this.deviceId||this._setValue(this._automations.length?this._automations[0]:this._createNoAutomation(this.deviceId)),this._renderEmpty=!0,e.n=4,this.updateComplete;case 4:this._renderEmpty=!1;case 5:return e.a(2)}}),e,this)}))),function(){return r.apply(this,arguments)})},{key:"_automationChanged",value:function(e){var t=e.target.value;if(t&&![D,I].includes(t)){var r=t.split("_"),o=(0,i.A)(r,2),n=o[0],a=o[1],s=this._automations[a];s.device_id===n&&this._setValue(s)}}},{key:"_setValue",value:function(e){if(!this.value||!(0,g.Po)(this._entityReg,e,this.value)){var t=Object.assign({},e);delete t.metadata,(0,v.r)(this,"value-changed",{value:t})}}}]);var r}(f.WF);T.styles=(0,f.AH)(E||(E=O`
    ha-select {
      display: block;
    }
  `)),(0,h.__decorate)([(0,y.MZ)({attribute:!1})],T.prototype,"hass",void 0),(0,h.__decorate)([(0,y.MZ)()],T.prototype,"label",void 0),(0,h.__decorate)([(0,y.MZ)({attribute:!1})],T.prototype,"deviceId",void 0),(0,h.__decorate)([(0,y.MZ)({type:Object})],T.prototype,"value",void 0),(0,h.__decorate)([(0,y.wk)()],T.prototype,"_automations",void 0),(0,h.__decorate)([(0,y.wk)()],T.prototype,"_renderEmpty",void 0),(0,h.__decorate)([(0,y.wk)(),(0,p.Fg)({context:m.ih,subscribe:!0})],T.prototype,"_entityReg",void 0)},60977:function(e,t,r){r.a(e,(async function(e,t){try{var o=r(61397),i=r(50264),n=r(44734),a=r(56038),s=r(69683),l=r(6454),c=r(25460),d=(r(28706),r(23792),r(62062),r(18111),r(61701),r(53921),r(26099),r(62826)),u=r(96196),h=r(77845),p=r(22786),f=r(92542),y=r(56403),v=r(16727),m=r(13877),g=r(3950),_=r(1491),b=r(76681),w=r(96943),A=e([w]);w=(A.then?(await A)():A)[0];var x,k,$,z,M,q,C,Z,E,S=e=>e,O=function(e){function t(){var e;(0,n.A)(this,t);for(var r=arguments.length,o=new Array(r),i=0;i<r;i++)o[i]=arguments[i];return(e=(0,s.A)(this,t,[].concat(o))).autofocus=!1,e.disabled=!1,e.required=!1,e.hideClearIcon=!1,e._configEntryLookup={},e._getDevicesMemoized=(0,p.A)(_.oG),e._getItems=()=>e._getDevicesMemoized(e.hass,e._configEntryLookup,e.includeDomains,e.excludeDomains,e.includeDeviceClasses,e.deviceFilter,e.entityFilter,e.excludeDevices,e.value),e._valueRenderer=(0,p.A)((t=>r=>{var o,i=r,n=e.hass.devices[i];if(!n)return(0,u.qy)(x||(x=S`<span slot="headline">${0}</span>`),i);var a=(0,m.w)(n,e.hass).area,s=n?(0,v.xn)(n):void 0,l=a?(0,y.A)(a):void 0,c=n.primary_config_entry?t[n.primary_config_entry]:void 0;return(0,u.qy)(k||(k=S`
        ${0}
        <span slot="headline">${0}</span>
        <span slot="supporting-text">${0}</span>
      `),c?(0,u.qy)($||($=S`<img
              slot="start"
              alt=""
              crossorigin="anonymous"
              referrerpolicy="no-referrer"
              src=${0}
            />`),(0,b.MR)({domain:c.domain,type:"icon",darkOptimized:null===(o=e.hass.themes)||void 0===o?void 0:o.darkMode})):u.s6,s,l)})),e._rowRenderer=t=>(0,u.qy)(z||(z=S`
    <ha-combo-box-item type="button">
      ${0}

      <span slot="headline">${0}</span>
      ${0}
      ${0}
    </ha-combo-box-item>
  `),t.domain?(0,u.qy)(M||(M=S`
            <img
              slot="start"
              alt=""
              crossorigin="anonymous"
              referrerpolicy="no-referrer"
              src=${0}
            />
          `),(0,b.MR)({domain:t.domain,type:"icon",darkOptimized:e.hass.themes.darkMode})):u.s6,t.primary,t.secondary?(0,u.qy)(q||(q=S`<span slot="supporting-text">${0}</span>`),t.secondary):u.s6,t.domain_name?(0,u.qy)(C||(C=S`
            <div slot="trailing-supporting-text" class="domain">
              ${0}
            </div>
          `),t.domain_name):u.s6),e._notFoundLabel=t=>e.hass.localize("ui.components.device-picker.no_match",{term:(0,u.qy)(Z||(Z=S`<b>‘${0}’</b>`),t)}),e}return(0,l.A)(t,e),(0,a.A)(t,[{key:"firstUpdated",value:function(e){(0,c.A)(t,"firstUpdated",this,3)([e]),this._loadConfigEntries()}},{key:"_loadConfigEntries",value:(d=(0,i.A)((0,o.A)().m((function e(){var t;return(0,o.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,(0,g.VN)(this.hass);case 1:t=e.v,this._configEntryLookup=Object.fromEntries(t.map((e=>[e.entry_id,e])));case 2:return e.a(2)}}),e,this)}))),function(){return d.apply(this,arguments)})},{key:"render",value:function(){var e,t=null!==(e=this.placeholder)&&void 0!==e?e:this.hass.localize("ui.components.device-picker.placeholder"),r=this._valueRenderer(this._configEntryLookup);return(0,u.qy)(E||(E=S`
      <ha-generic-picker
        .hass=${0}
        .autofocus=${0}
        .label=${0}
        .searchLabel=${0}
        .notFoundLabel=${0}
        .emptyLabel=${0}
        .placeholder=${0}
        .value=${0}
        .rowRenderer=${0}
        .getItems=${0}
        .hideClearIcon=${0}
        .valueRenderer=${0}
        @value-changed=${0}
      >
      </ha-generic-picker>
    `),this.hass,this.autofocus,this.label,this.searchLabel,this._notFoundLabel,this.hass.localize("ui.components.device-picker.no_devices"),t,this.value,this._rowRenderer,this._getItems,this.hideClearIcon,r,this._valueChanged)}},{key:"open",value:(r=(0,i.A)((0,o.A)().m((function e(){var t;return(0,o.A)().w((function(e){for(;;)switch(e.n){case 0:return e.n=1,this.updateComplete;case 1:return e.n=2,null===(t=this._picker)||void 0===t?void 0:t.open();case 2:return e.a(2)}}),e,this)}))),function(){return r.apply(this,arguments)})},{key:"_valueChanged",value:function(e){e.stopPropagation();var t=e.detail.value;this.value=t,(0,f.r)(this,"value-changed",{value:t})}}]);var r,d}(u.WF);(0,d.__decorate)([(0,h.MZ)({attribute:!1})],O.prototype,"hass",void 0),(0,d.__decorate)([(0,h.MZ)({type:Boolean})],O.prototype,"autofocus",void 0),(0,d.__decorate)([(0,h.MZ)({type:Boolean})],O.prototype,"disabled",void 0),(0,d.__decorate)([(0,h.MZ)({type:Boolean})],O.prototype,"required",void 0),(0,d.__decorate)([(0,h.MZ)()],O.prototype,"label",void 0),(0,d.__decorate)([(0,h.MZ)()],O.prototype,"value",void 0),(0,d.__decorate)([(0,h.MZ)()],O.prototype,"helper",void 0),(0,d.__decorate)([(0,h.MZ)()],O.prototype,"placeholder",void 0),(0,d.__decorate)([(0,h.MZ)({type:String,attribute:"search-label"})],O.prototype,"searchLabel",void 0),(0,d.__decorate)([(0,h.MZ)({attribute:!1,type:Array})],O.prototype,"createDomains",void 0),(0,d.__decorate)([(0,h.MZ)({type:Array,attribute:"include-domains"})],O.prototype,"includeDomains",void 0),(0,d.__decorate)([(0,h.MZ)({type:Array,attribute:"exclude-domains"})],O.prototype,"excludeDomains",void 0),(0,d.__decorate)([(0,h.MZ)({type:Array,attribute:"include-device-classes"})],O.prototype,"includeDeviceClasses",void 0),(0,d.__decorate)([(0,h.MZ)({type:Array,attribute:"exclude-devices"})],O.prototype,"excludeDevices",void 0),(0,d.__decorate)([(0,h.MZ)({attribute:!1})],O.prototype,"deviceFilter",void 0),(0,d.__decorate)([(0,h.MZ)({attribute:!1})],O.prototype,"entityFilter",void 0),(0,d.__decorate)([(0,h.MZ)({attribute:"hide-clear-icon",type:Boolean})],O.prototype,"hideClearIcon",void 0),(0,d.__decorate)([(0,h.P)("ha-generic-picker")],O.prototype,"_picker",void 0),(0,d.__decorate)([(0,h.wk)()],O.prototype,"_configEntryLookup",void 0),O=(0,d.__decorate)([(0,h.EM)("ha-device-picker")],O),t()}catch(I){t(I)}}))},27639:function(e,t,r){var o,i,n,a=r(61397),s=r(50264),l=r(44734),c=r(56038),d=r(69683),u=r(6454),h=(r(28706),r(62826)),p=r(96196),f=r(77845),y=r(92542),v=(r(60733),e=>e),m=function(e){function t(){var e;(0,l.A)(this,t);for(var r=arguments.length,o=new Array(r),i=0;i<r;i++)o[i]=arguments[i];return(e=(0,d.A)(this,t,[].concat(o))).leftChevron=!1,e.collapsed=!1,e.selected=!1,e.sortSelected=!1,e.disabled=!1,e.buildingBlock=!1,e}return(0,u.A)(t,e),(0,c.A)(t,[{key:"render",value:function(){return(0,p.qy)(o||(o=v`
      <div
        class="row"
        tabindex="0"
        role="button"
        @keydown=${0}
      >
        ${0}
        <div class="leading-icon-wrapper">
          <slot name="leading-icon"></slot>
        </div>
        <slot class="header" name="header"></slot>
        <slot name="icons"></slot>
      </div>
    `),this._handleKeydown,this.leftChevron?(0,p.qy)(i||(i=v`
              <ha-icon-button
                class="expand-button"
                .path=${0}
                @click=${0}
                @keydown=${0}
              ></ha-icon-button>
            `),"M7.41,15.41L12,10.83L16.59,15.41L18,14L12,8L6,14L7.41,15.41Z",this._handleExpand,this._handleExpand):p.s6)}},{key:"_handleExpand",value:(n=(0,s.A)((0,a.A)().m((function e(t){return(0,a.A)().w((function(e){for(;;)switch(e.n){case 0:if(!t.defaultPrevented){e.n=1;break}return e.a(2);case 1:if("keydown"!==t.type||"Enter"===t.key||" "===t.key){e.n=2;break}return e.a(2);case 2:t.stopPropagation(),t.preventDefault(),(0,y.r)(this,"toggle-collapsed");case 3:return e.a(2)}}),e,this)}))),function(e){return n.apply(this,arguments)})},{key:"_handleKeydown",value:(r=(0,s.A)((0,a.A)().m((function e(t){return(0,a.A)().w((function(e){for(;;)switch(e.n){case 0:if(!t.defaultPrevented){e.n=1;break}return e.a(2);case 1:if("Enter"===t.key||" "===t.key||!(!this.sortSelected&&!t.altKey||t.ctrlKey||t.metaKey||t.shiftKey||"ArrowUp"!==t.key&&"ArrowDown"!==t.key)){e.n=2;break}return e.a(2);case 2:if(t.preventDefault(),t.stopPropagation(),"ArrowUp"!==t.key&&"ArrowDown"!==t.key){e.n=4;break}if("ArrowUp"!==t.key){e.n=3;break}return(0,y.r)(this,"move-up"),e.a(2);case 3:return(0,y.r)(this,"move-down"),e.a(2);case 4:if(!this.sortSelected||"Enter"!==t.key&&" "!==t.key){e.n=5;break}return(0,y.r)(this,"stop-sort-selection"),e.a(2);case 5:this.click();case 6:return e.a(2)}}),e,this)}))),function(e){return r.apply(this,arguments)})},{key:"focus",value:function(){requestAnimationFrame((()=>{var e;null===(e=this._rowElement)||void 0===e||e.focus()}))}}]);var r,n}(p.WF);m.styles=(0,p.AH)(n||(n=v`
    :host {
      display: block;
    }
    .row {
      display: flex;
      padding: var(--ha-space-0) var(--ha-space-2);
      min-height: 48px;
      align-items: center;
      cursor: pointer;
      overflow: hidden;
      font-weight: var(--ha-font-weight-medium);
      outline: none;
      border-radius: var(--ha-card-border-radius, var(--ha-border-radius-lg));
    }
    .row:focus {
      outline: var(--wa-focus-ring);
      outline-offset: -2px;
    }
    .expand-button {
      transition: transform 150ms cubic-bezier(0.4, 0, 0.2, 1);
      color: var(--ha-color-on-neutral-quiet);
      margin-left: calc(var(--ha-space-2) * -1);
    }
    :host([building-block]) .leading-icon-wrapper {
      background-color: var(--ha-color-fill-neutral-loud-resting);
      border-radius: var(--ha-border-radius-md);
      padding: var(--ha-space-1);
      display: flex;
      justify-content: center;
      align-items: center;
      transform: rotate(45deg);
    }
    ::slotted([slot="leading-icon"]) {
      color: var(--ha-color-on-neutral-quiet);
    }
    :host([building-block]) ::slotted([slot="leading-icon"]) {
      --mdc-icon-size: var(--ha-space-5);
      color: var(--white-color);
      transform: rotate(-45deg);
    }
    :host([collapsed]) .expand-button {
      transform: rotate(180deg);
    }
    :host([selected]) .row,
    :host([selected]) .row:focus {
      outline: solid;
      outline-color: var(--primary-color);
      outline-offset: -2px;
      outline-width: 2px;
    }
    :host([disabled]) .row {
      border-top-right-radius: var(--ha-border-radius-square);
      border-top-left-radius: var(--ha-border-radius-square);
    }
    ::slotted([slot="header"]) {
      flex: 1;
      overflow-wrap: anywhere;
      margin: var(--ha-space-0) var(--ha-space-3);
    }
    :host([sort-selected]) .row {
      outline: solid;
      outline-color: rgba(var(--rgb-accent-color), 0.6);
      outline-offset: -2px;
      outline-width: 2px;
      background-color: rgba(var(--rgb-accent-color), 0.08);
    }
    .row:hover {
      background-color: rgba(var(--rgb-primary-text-color), 0.04);
    }
    :host([highlight]) .row {
      background-color: rgba(var(--rgb-primary-color), 0.08);
    }
    :host([highlight]) .row:hover {
      background-color: rgba(var(--rgb-primary-color), 0.16);
    }
  `)),(0,h.__decorate)([(0,f.MZ)({attribute:"left-chevron",type:Boolean})],m.prototype,"leftChevron",void 0),(0,h.__decorate)([(0,f.MZ)({type:Boolean,reflect:!0})],m.prototype,"collapsed",void 0),(0,h.__decorate)([(0,f.MZ)({type:Boolean,reflect:!0})],m.prototype,"selected",void 0),(0,h.__decorate)([(0,f.MZ)({type:Boolean,reflect:!0,attribute:"sort-selected"})],m.prototype,"sortSelected",void 0),(0,h.__decorate)([(0,f.MZ)({type:Boolean,reflect:!0})],m.prototype,"disabled",void 0),(0,h.__decorate)([(0,f.MZ)({type:Boolean,reflect:!0,attribute:"building-block"})],m.prototype,"buildingBlock",void 0),(0,h.__decorate)([(0,f.MZ)({type:Boolean,reflect:!0})],m.prototype,"highlight",void 0),(0,h.__decorate)([(0,f.P)(".row")],m.prototype,"_rowElement",void 0),m=(0,h.__decorate)([(0,f.EM)("ha-automation-row")],m)},16857:function(e,t,r){var o,i,n=r(44734),a=r(56038),s=r(69683),l=r(6454),c=r(25460),d=(r(28706),r(18111),r(7588),r(2892),r(26099),r(23500),r(62826)),u=r(96196),h=r(77845),p=r(76679),f=(r(41742),r(1554),e=>e),y=function(e){function t(){var e;(0,n.A)(this,t);for(var r=arguments.length,o=new Array(r),i=0;i<r;i++)o[i]=arguments[i];return(e=(0,s.A)(this,t,[].concat(o))).corner="BOTTOM_START",e.menuCorner="START",e.x=null,e.y=null,e.multi=!1,e.activatable=!1,e.disabled=!1,e.fixed=!1,e.noAnchor=!1,e}return(0,l.A)(t,e),(0,a.A)(t,[{key:"items",get:function(){var e;return null===(e=this._menu)||void 0===e?void 0:e.items}},{key:"selected",get:function(){var e;return null===(e=this._menu)||void 0===e?void 0:e.selected}},{key:"focus",value:function(){var e,t;null!==(e=this._menu)&&void 0!==e&&e.open?this._menu.focusItemAtIndex(0):null===(t=this._triggerButton)||void 0===t||t.focus()}},{key:"render",value:function(){return(0,u.qy)(o||(o=f`
      <div @click=${0}>
        <slot name="trigger" @slotchange=${0}></slot>
      </div>
      <ha-menu
        .corner=${0}
        .menuCorner=${0}
        .fixed=${0}
        .multi=${0}
        .activatable=${0}
        .y=${0}
        .x=${0}
      >
        <slot></slot>
      </ha-menu>
    `),this._handleClick,this._setTriggerAria,this.corner,this.menuCorner,this.fixed,this.multi,this.activatable,this.y,this.x)}},{key:"firstUpdated",value:function(e){(0,c.A)(t,"firstUpdated",this,3)([e]),"rtl"===p.G.document.dir&&this.updateComplete.then((()=>{this.querySelectorAll("ha-list-item").forEach((e=>{var t=document.createElement("style");t.innerHTML="span.material-icons:first-of-type { margin-left: var(--mdc-list-item-graphic-margin, 32px) !important; margin-right: 0px !important;}",e.shadowRoot.appendChild(t)}))}))}},{key:"_handleClick",value:function(){this.disabled||(this._menu.anchor=this.noAnchor?null:this,this._menu.show())}},{key:"_triggerButton",get:function(){return this.querySelector('ha-icon-button[slot="trigger"], ha-button[slot="trigger"]')}},{key:"_setTriggerAria",value:function(){this._triggerButton&&(this._triggerButton.ariaHasPopup="menu")}}])}(u.WF);y.styles=(0,u.AH)(i||(i=f`
    :host {
      display: inline-block;
      position: relative;
    }
    ::slotted([disabled]) {
      color: var(--disabled-text-color);
    }
  `)),(0,d.__decorate)([(0,h.MZ)()],y.prototype,"corner",void 0),(0,d.__decorate)([(0,h.MZ)({attribute:"menu-corner"})],y.prototype,"menuCorner",void 0),(0,d.__decorate)([(0,h.MZ)({type:Number})],y.prototype,"x",void 0),(0,d.__decorate)([(0,h.MZ)({type:Number})],y.prototype,"y",void 0),(0,d.__decorate)([(0,h.MZ)({type:Boolean})],y.prototype,"multi",void 0),(0,d.__decorate)([(0,h.MZ)({type:Boolean})],y.prototype,"activatable",void 0),(0,d.__decorate)([(0,h.MZ)({type:Boolean})],y.prototype,"disabled",void 0),(0,d.__decorate)([(0,h.MZ)({type:Boolean})],y.prototype,"fixed",void 0),(0,d.__decorate)([(0,h.MZ)({type:Boolean,attribute:"no-anchor"})],y.prototype,"noAnchor",void 0),(0,d.__decorate)([(0,h.P)("ha-menu",!0)],y.prototype,"_menu",void 0),y=(0,d.__decorate)([(0,h.EM)("ha-button-menu")],y)},70524:function(e,t,r){var o,i=r(56038),n=r(44734),a=r(69683),s=r(6454),l=r(62826),c=r(69162),d=r(47191),u=r(96196),h=r(77845),p=function(e){function t(){return(0,n.A)(this,t),(0,a.A)(this,t,arguments)}return(0,s.A)(t,e),(0,i.A)(t)}(c.L);p.styles=[d.R,(0,u.AH)(o||(o=(e=>e)`
      :host {
        --mdc-theme-secondary: var(--primary-color);
      }
    `))],p=(0,l.__decorate)([(0,h.EM)("ha-checkbox")],p)},34811:function(e,t,r){r.d(t,{p:function(){return w}});var o,i,n,a,s=r(61397),l=r(50264),c=r(44734),d=r(56038),u=r(69683),h=r(6454),p=r(25460),f=(r(28706),r(62826)),y=r(96196),v=r(77845),m=r(94333),g=r(92542),_=r(99034),b=(r(60961),e=>e),w=function(e){function t(){var e;(0,c.A)(this,t);for(var r=arguments.length,o=new Array(r),i=0;i<r;i++)o[i]=arguments[i];return(e=(0,u.A)(this,t,[].concat(o))).expanded=!1,e.outlined=!1,e.leftChevron=!1,e.noCollapse=!1,e._showContent=e.expanded,e}return(0,h.A)(t,e),(0,d.A)(t,[{key:"render",value:function(){var e=this.noCollapse?y.s6:(0,y.qy)(o||(o=b`
          <ha-svg-icon
            .path=${0}
            class="summary-icon ${0}"
          ></ha-svg-icon>
        `),"M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z",(0,m.H)({expanded:this.expanded}));return(0,y.qy)(i||(i=b`
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
    `),(0,m.H)({expanded:this.expanded}),(0,m.H)({noCollapse:this.noCollapse}),this._toggleContainer,this._toggleContainer,this._focusChanged,this._focusChanged,this.noCollapse?-1:0,this.expanded,this.leftChevron?e:y.s6,this.header,this.secondary,this.leftChevron?y.s6:e,(0,m.H)({expanded:this.expanded}),this._handleTransitionEnd,!this.expanded,this._showContent?(0,y.qy)(n||(n=b`<slot></slot>`)):"")}},{key:"willUpdate",value:function(e){(0,p.A)(t,"willUpdate",this,3)([e]),e.has("expanded")&&(this._showContent=this.expanded,setTimeout((()=>{this._container.style.overflow=this.expanded?"initial":"hidden"}),300))}},{key:"_handleTransitionEnd",value:function(){this._container.style.removeProperty("height"),this._container.style.overflow=this.expanded?"initial":"hidden",this._showContent=this.expanded}},{key:"_toggleContainer",value:(r=(0,l.A)((0,s.A)().m((function e(t){var r,o;return(0,s.A)().w((function(e){for(;;)switch(e.n){case 0:if(!t.defaultPrevented){e.n=1;break}return e.a(2);case 1:if("keydown"!==t.type||"Enter"===t.key||" "===t.key){e.n=2;break}return e.a(2);case 2:if(t.preventDefault(),!this.noCollapse){e.n=3;break}return e.a(2);case 3:if(r=!this.expanded,(0,g.r)(this,"expanded-will-change",{expanded:r}),this._container.style.overflow="hidden",!r){e.n=4;break}return this._showContent=!0,e.n=4,(0,_.E)();case 4:o=this._container.scrollHeight,this._container.style.height=`${o}px`,r||setTimeout((()=>{this._container.style.height="0px"}),0),this.expanded=r,(0,g.r)(this,"expanded-changed",{expanded:this.expanded});case 5:return e.a(2)}}),e,this)}))),function(e){return r.apply(this,arguments)})},{key:"_focusChanged",value:function(e){this.noCollapse||this.shadowRoot.querySelector(".top").classList.toggle("focused","focus"===e.type)}}]);var r}(y.WF);w.styles=(0,y.AH)(a||(a=b`
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
  `)),(0,f.__decorate)([(0,v.MZ)({type:Boolean,reflect:!0})],w.prototype,"expanded",void 0),(0,f.__decorate)([(0,v.MZ)({type:Boolean,reflect:!0})],w.prototype,"outlined",void 0),(0,f.__decorate)([(0,v.MZ)({attribute:"left-chevron",type:Boolean,reflect:!0})],w.prototype,"leftChevron",void 0),(0,f.__decorate)([(0,v.MZ)({attribute:"no-collapse",type:Boolean,reflect:!0})],w.prototype,"noCollapse",void 0),(0,f.__decorate)([(0,v.MZ)()],w.prototype,"header",void 0),(0,f.__decorate)([(0,v.MZ)()],w.prototype,"secondary",void 0),(0,f.__decorate)([(0,v.wk)()],w.prototype,"_showContent",void 0),(0,f.__decorate)([(0,v.P)(".container")],w.prototype,"_container",void 0),w=(0,f.__decorate)([(0,v.EM)("ha-expansion-panel")],w)},91120:function(e,t,r){var o,i,n,a,s,l,c,d,u,h=r(78261),p=r(61397),f=r(31432),y=r(50264),v=r(44734),m=r(56038),g=r(69683),_=r(6454),b=r(25460),w=(r(28706),r(23792),r(62062),r(18111),r(7588),r(61701),r(5506),r(26099),r(3362),r(23500),r(62953),r(62826)),A=r(96196),x=r(77845),k=r(51757),$=r(92542),z=(r(17963),r(87156),e=>e),M={boolean:()=>Promise.all([r.e("8477"),r.e("2018")]).then(r.bind(r,49337)),constant:()=>r.e("9938").then(r.bind(r,37449)),float:()=>r.e("812").then(r.bind(r,5863)),grid:()=>r.e("798").then(r.bind(r,81213)),expandable:()=>r.e("8550").then(r.bind(r,29989)),integer:()=>Promise.all([r.e("8477"),r.e("1543"),r.e("1364")]).then(r.bind(r,28175)),multi_select:()=>Promise.all([r.e("2239"),r.e("6767"),r.e("7251"),r.e("8477"),r.e("2016"),r.e("2202"),r.e("3616")]).then(r.bind(r,59827)),positive_time_period_dict:()=>Promise.all([r.e("2239"),r.e("6767"),r.e("7251"),r.e("3577"),r.e("4558"),r.e("2389")]).then(r.bind(r,19797)),select:()=>Promise.all([r.e("2239"),r.e("6767"),r.e("7251"),r.e("3577"),r.e("4124"),r.e("8477"),r.e("1279"),r.e("4933"),r.e("5186"),r.e("6262")]).then(r.bind(r,29317)),string:()=>r.e("8389").then(r.bind(r,33092)),optional_actions:()=>r.e("1454").then(r.bind(r,2173))},q=(e,t)=>e?!t.name||t.flatten?e:e[t.name]:null,C=function(e){function t(){var e;(0,v.A)(this,t);for(var r=arguments.length,o=new Array(r),i=0;i<r;i++)o[i]=arguments[i];return(e=(0,g.A)(this,t,[].concat(o))).narrow=!1,e.disabled=!1,e}return(0,_.A)(t,e),(0,m.A)(t,[{key:"getFormProperties",value:function(){return{}}},{key:"focus",value:(r=(0,y.A)((0,p.A)().m((function e(){var t,r,o,i,n;return(0,p.A)().w((function(e){for(;;)switch(e.p=e.n){case 0:return e.n=1,this.updateComplete;case 1:if(t=this.renderRoot.querySelector(".root")){e.n=2;break}return e.a(2);case 2:r=(0,f.A)(t.children),e.p=3,r.s();case 4:if((o=r.n()).done){e.n=7;break}if("HA-ALERT"===(i=o.value).tagName){e.n=6;break}if(!(i instanceof A.mN)){e.n=5;break}return e.n=5,i.updateComplete;case 5:return i.focus(),e.a(3,7);case 6:e.n=4;break;case 7:e.n=9;break;case 8:e.p=8,n=e.v,r.e(n);case 9:return e.p=9,r.f(),e.f(9);case 10:return e.a(2)}}),e,this,[[3,8,9,10]])}))),function(){return r.apply(this,arguments)})},{key:"willUpdate",value:function(e){e.has("schema")&&this.schema&&this.schema.forEach((e=>{var t;"selector"in e||null===(t=M[e.type])||void 0===t||t.call(M)}))}},{key:"render",value:function(){return(0,A.qy)(o||(o=z`
      <div class="root" part="root">
        ${0}
        ${0}
      </div>
    `),this.error&&this.error.base?(0,A.qy)(i||(i=z`
              <ha-alert alert-type="error">
                ${0}
              </ha-alert>
            `),this._computeError(this.error.base,this.schema)):"",this.schema.map((e=>{var t,r=((e,t)=>e&&t.name?e[t.name]:null)(this.error,e),o=((e,t)=>e&&t.name?e[t.name]:null)(this.warning,e);return(0,A.qy)(n||(n=z`
            ${0}
            ${0}
          `),r?(0,A.qy)(a||(a=z`
                  <ha-alert own-margin alert-type="error">
                    ${0}
                  </ha-alert>
                `),this._computeError(r,e)):o?(0,A.qy)(s||(s=z`
                    <ha-alert own-margin alert-type="warning">
                      ${0}
                    </ha-alert>
                  `),this._computeWarning(o,e)):"","selector"in e?(0,A.qy)(l||(l=z`<ha-selector
                  .schema=${0}
                  .hass=${0}
                  .narrow=${0}
                  .name=${0}
                  .selector=${0}
                  .value=${0}
                  .label=${0}
                  .disabled=${0}
                  .placeholder=${0}
                  .helper=${0}
                  .localizeValue=${0}
                  .required=${0}
                  .context=${0}
                ></ha-selector>`),e,this.hass,this.narrow,e.name,e.selector,q(this.data,e),this._computeLabel(e,this.data),e.disabled||this.disabled||!1,e.required?void 0:e.default,this._computeHelper(e),this.localizeValue,e.required||!1,this._generateContext(e)):(0,k._)(this.fieldElementName(e.type),Object.assign({schema:e,data:q(this.data,e),label:this._computeLabel(e,this.data),helper:this._computeHelper(e),disabled:this.disabled||e.disabled||!1,hass:this.hass,localize:null===(t=this.hass)||void 0===t?void 0:t.localize,computeLabel:this.computeLabel,computeHelper:this.computeHelper,localizeValue:this.localizeValue,context:this._generateContext(e)},this.getFormProperties())))})))}},{key:"fieldElementName",value:function(e){return`ha-form-${e}`}},{key:"_generateContext",value:function(e){if(e.context){for(var t={},r=0,o=Object.entries(e.context);r<o.length;r++){var i=(0,h.A)(o[r],2),n=i[0],a=i[1];t[n]=this.data[a]}return t}}},{key:"createRenderRoot",value:function(){var e=(0,b.A)(t,"createRenderRoot",this,3)([]);return this.addValueChangedListener(e),e}},{key:"addValueChangedListener",value:function(e){e.addEventListener("value-changed",(e=>{e.stopPropagation();var t=e.target.schema;if(e.target!==this){var r=!t.name||"flatten"in t&&t.flatten?e.detail.value:{[t.name]:e.detail.value};this.data=Object.assign(Object.assign({},this.data),r),(0,$.r)(this,"value-changed",{value:this.data})}}))}},{key:"_computeLabel",value:function(e,t){return this.computeLabel?this.computeLabel(e,t):e?e.name:""}},{key:"_computeHelper",value:function(e){return this.computeHelper?this.computeHelper(e):""}},{key:"_computeError",value:function(e,t){return Array.isArray(e)?(0,A.qy)(c||(c=z`<ul>
        ${0}
      </ul>`),e.map((e=>(0,A.qy)(d||(d=z`<li>
              ${0}
            </li>`),this.computeError?this.computeError(e,t):e)))):this.computeError?this.computeError(e,t):e}},{key:"_computeWarning",value:function(e,t){return this.computeWarning?this.computeWarning(e,t):e}}]);var r}(A.WF);C.shadowRootOptions={mode:"open",delegatesFocus:!0},C.styles=(0,A.AH)(u||(u=z`
    .root > * {
      display: block;
    }
    .root > *:not([own-margin]):not(:last-child) {
      margin-bottom: 24px;
    }
    ha-alert[own-margin] {
      margin-bottom: 4px;
    }
  `)),(0,w.__decorate)([(0,x.MZ)({attribute:!1})],C.prototype,"hass",void 0),(0,w.__decorate)([(0,x.MZ)({type:Boolean})],C.prototype,"narrow",void 0),(0,w.__decorate)([(0,x.MZ)({attribute:!1})],C.prototype,"data",void 0),(0,w.__decorate)([(0,x.MZ)({attribute:!1})],C.prototype,"schema",void 0),(0,w.__decorate)([(0,x.MZ)({attribute:!1})],C.prototype,"error",void 0),(0,w.__decorate)([(0,x.MZ)({attribute:!1})],C.prototype,"warning",void 0),(0,w.__decorate)([(0,x.MZ)({type:Boolean})],C.prototype,"disabled",void 0),(0,w.__decorate)([(0,x.MZ)({attribute:!1})],C.prototype,"computeError",void 0),(0,w.__decorate)([(0,x.MZ)({attribute:!1})],C.prototype,"computeWarning",void 0),(0,w.__decorate)([(0,x.MZ)({attribute:!1})],C.prototype,"computeLabel",void 0),(0,w.__decorate)([(0,x.MZ)({attribute:!1})],C.prototype,"computeHelper",void 0),(0,w.__decorate)([(0,x.MZ)({attribute:!1})],C.prototype,"localizeValue",void 0),C=(0,w.__decorate)([(0,x.EM)("ha-form")],C)},75261:function(e,t,r){var o=r(56038),i=r(44734),n=r(69683),a=r(6454),s=r(62826),l=r(70402),c=r(11081),d=r(77845),u=function(e){function t(){return(0,i.A)(this,t),(0,n.A)(this,t,arguments)}return(0,a.A)(t,e),(0,o.A)(t)}(l.iY);u.styles=c.R,u=(0,s.__decorate)([(0,d.EM)("ha-list")],u)},63419:function(e,t,r){var o,i=r(44734),n=r(56038),a=r(69683),s=r(6454),l=(r(28706),r(62826)),c=r(96196),d=r(77845),u=r(92542),h=(r(41742),r(25460)),p=r(26139),f=r(8889),y=r(63374),v=function(e){function t(){return(0,i.A)(this,t),(0,a.A)(this,t,arguments)}return(0,s.A)(t,e),(0,n.A)(t,[{key:"connectedCallback",value:function(){(0,h.A)(t,"connectedCallback",this,3)([]),this.addEventListener("close-menu",this._handleCloseMenu)}},{key:"_handleCloseMenu",value:function(e){var t,r;e.detail.reason.kind===y.fi.KEYDOWN&&e.detail.reason.key===y.NV.ESCAPE||null===(t=(r=e.detail.initiator).clickAction)||void 0===t||t.call(r,e.detail.initiator)}}])}(p.W1);v.styles=[f.R,(0,c.AH)(o||(o=(e=>e)`
      :host {
        --md-sys-color-surface-container: var(--card-background-color);
      }
    `))],v=(0,l.__decorate)([(0,d.EM)("ha-md-menu")],v);var m,g,_=e=>e,b=function(e){function t(){var e;(0,i.A)(this,t);for(var r=arguments.length,o=new Array(r),n=0;n<r;n++)o[n]=arguments[n];return(e=(0,a.A)(this,t,[].concat(o))).disabled=!1,e.anchorCorner="end-start",e.menuCorner="start-start",e.hasOverflow=!1,e.quick=!1,e}return(0,s.A)(t,e),(0,n.A)(t,[{key:"items",get:function(){return this._menu.items}},{key:"focus",value:function(){var e;this._menu.open?this._menu.focus():null===(e=this._triggerButton)||void 0===e||e.focus()}},{key:"render",value:function(){return(0,c.qy)(m||(m=_`
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
    `),this._handleClick,this._setTriggerAria,this.quick,this.positioning,this.hasOverflow,this.anchorCorner,this.menuCorner,this._handleOpening,this._handleClosing)}},{key:"_handleOpening",value:function(){(0,u.r)(this,"opening",void 0,{composed:!1})}},{key:"_handleClosing",value:function(){(0,u.r)(this,"closing",void 0,{composed:!1})}},{key:"_handleClick",value:function(){this.disabled||(this._menu.anchorElement=this,this._menu.open?this._menu.close():this._menu.show())}},{key:"_triggerButton",get:function(){return this.querySelector('ha-icon-button[slot="trigger"], ha-button[slot="trigger"], ha-assist-chip[slot="trigger"]')}},{key:"_setTriggerAria",value:function(){this._triggerButton&&(this._triggerButton.ariaHasPopup="menu")}}])}(c.WF);b.styles=(0,c.AH)(g||(g=_`
    :host {
      display: inline-block;
      position: relative;
    }
    ::slotted([disabled]) {
      color: var(--disabled-text-color);
    }
  `)),(0,l.__decorate)([(0,d.MZ)({type:Boolean})],b.prototype,"disabled",void 0),(0,l.__decorate)([(0,d.MZ)()],b.prototype,"positioning",void 0),(0,l.__decorate)([(0,d.MZ)({attribute:"anchor-corner"})],b.prototype,"anchorCorner",void 0),(0,l.__decorate)([(0,d.MZ)({attribute:"menu-corner"})],b.prototype,"menuCorner",void 0),(0,l.__decorate)([(0,d.MZ)({type:Boolean,attribute:"has-overflow"})],b.prototype,"hasOverflow",void 0),(0,l.__decorate)([(0,d.MZ)({type:Boolean})],b.prototype,"quick",void 0),(0,l.__decorate)([(0,d.P)("ha-md-menu",!0)],b.prototype,"_menu",void 0),b=(0,l.__decorate)([(0,d.EM)("ha-md-button-menu")],b)},32072:function(e,t,r){var o,i=r(56038),n=r(44734),a=r(69683),s=r(6454),l=r(62826),c=r(10414),d=r(18989),u=r(96196),h=r(77845),p=function(e){function t(){return(0,n.A)(this,t),(0,a.A)(this,t,arguments)}return(0,s.A)(t,e),(0,i.A)(t)}(c.c);p.styles=[d.R,(0,u.AH)(o||(o=(e=>e)`
      :host {
        --md-divider-color: var(--divider-color);
      }
    `))],p=(0,l.__decorate)([(0,h.EM)("ha-md-divider")],p)},99892:function(e,t,r){var o,i=r(56038),n=r(44734),a=r(69683),s=r(6454),l=r(62826),c=r(54407),d=r(28522),u=r(96196),h=r(77845),p=function(e){function t(){return(0,n.A)(this,t),(0,a.A)(this,t,arguments)}return(0,s.A)(t,e),(0,i.A)(t)}(c.K);p.styles=[d.R,(0,u.AH)(o||(o=(e=>e)`
      :host {
        --ha-icon-display: block;
        --md-sys-color-primary: var(--primary-text-color);
        --md-sys-color-on-primary: var(--primary-text-color);
        --md-sys-color-secondary: var(--secondary-text-color);
        --md-sys-color-surface: var(--card-background-color);
        --md-sys-color-on-surface: var(--primary-text-color);
        --md-sys-color-on-surface-variant: var(--secondary-text-color);
        --md-sys-color-secondary-container: rgba(
          var(--rgb-primary-color),
          0.15
        );
        --md-sys-color-on-secondary-container: var(--text-primary-color);
        --mdc-icon-size: 16px;

        --md-sys-color-on-primary-container: var(--primary-text-color);
        --md-sys-color-on-secondary-container: var(--primary-text-color);
        --md-menu-item-label-text-font: Roboto, sans-serif;
      }
      :host(.warning) {
        --md-menu-item-label-text-color: var(--error-color);
        --md-menu-item-leading-icon-color: var(--error-color);
      }
      ::slotted([slot="headline"]) {
        text-wrap: nowrap;
      }
      :host([disabled]) {
        opacity: 1;
        --md-menu-item-label-text-color: var(--disabled-text-color);
        --md-menu-item-leading-icon-color: var(--disabled-text-color);
      }
    `))],(0,l.__decorate)([(0,h.MZ)({attribute:!1})],p.prototype,"clickAction",void 0),p=(0,l.__decorate)([(0,h.EM)("ha-md-menu-item")],p)},2809:function(e,t,r){var o,i,n=r(44734),a=r(56038),s=r(69683),l=r(6454),c=(r(28706),r(62826)),d=r(96196),u=r(77845),h=e=>e,p=function(e){function t(){var e;(0,n.A)(this,t);for(var r=arguments.length,o=new Array(r),i=0;i<r;i++)o[i]=arguments[i];return(e=(0,s.A)(this,t,[].concat(o))).narrow=!1,e.slim=!1,e.threeLine=!1,e.wrapHeading=!1,e}return(0,l.A)(t,e),(0,a.A)(t,[{key:"render",value:function(){return(0,d.qy)(o||(o=h`
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
    `),!this.threeLine,this.threeLine)}}])}(d.WF);p.styles=(0,d.AH)(i||(i=h`
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
  `)),(0,c.__decorate)([(0,u.MZ)({type:Boolean,reflect:!0})],p.prototype,"narrow",void 0),(0,c.__decorate)([(0,u.MZ)({type:Boolean,reflect:!0})],p.prototype,"slim",void 0),(0,c.__decorate)([(0,u.MZ)({type:Boolean,attribute:"three-line"})],p.prototype,"threeLine",void 0),(0,c.__decorate)([(0,u.MZ)({type:Boolean,attribute:"wrap-heading",reflect:!0})],p.prototype,"wrapHeading",void 0),p=(0,c.__decorate)([(0,u.EM)("ha-settings-row")],p)},63801:function(e,t,r){var o,i=r(61397),n=r(50264),a=r(44734),s=r(56038),l=r(75864),c=r(69683),d=r(6454),u=r(25460),h=(r(28706),r(2008),r(23792),r(18111),r(22489),r(26099),r(3362),r(46058),r(62953),r(62826)),p=r(96196),f=r(77845),y=r(92542),v=e=>e,m=function(e){function t(){var e;(0,a.A)(this,t);for(var r=arguments.length,o=new Array(r),s=0;s<r;s++)o[s]=arguments[s];return(e=(0,c.A)(this,t,[].concat(o))).disabled=!1,e.noStyle=!1,e.invertSwap=!1,e.rollback=!0,e._shouldBeDestroy=!1,e._handleUpdate=t=>{(0,y.r)((0,l.A)(e),"item-moved",{newIndex:t.newIndex,oldIndex:t.oldIndex})},e._handleAdd=t=>{(0,y.r)((0,l.A)(e),"item-added",{index:t.newIndex,data:t.item.sortableData,item:t.item})},e._handleRemove=t=>{(0,y.r)((0,l.A)(e),"item-removed",{index:t.oldIndex})},e._handleEnd=function(){var t=(0,n.A)((0,i.A)().m((function t(r){return(0,i.A)().w((function(t){for(;;)switch(t.n){case 0:(0,y.r)((0,l.A)(e),"drag-end"),e.rollback&&r.item.placeholder&&(r.item.placeholder.replaceWith(r.item),delete r.item.placeholder);case 1:return t.a(2)}}),t)})));return function(e){return t.apply(this,arguments)}}(),e._handleStart=()=>{(0,y.r)((0,l.A)(e),"drag-start")},e._handleChoose=t=>{e.rollback&&(t.item.placeholder=document.createComment("sort-placeholder"),t.item.after(t.item.placeholder))},e}return(0,d.A)(t,e),(0,s.A)(t,[{key:"updated",value:function(e){e.has("disabled")&&(this.disabled?this._destroySortable():this._createSortable())}},{key:"disconnectedCallback",value:function(){(0,u.A)(t,"disconnectedCallback",this,3)([]),this._shouldBeDestroy=!0,setTimeout((()=>{this._shouldBeDestroy&&(this._destroySortable(),this._shouldBeDestroy=!1)}),1)}},{key:"connectedCallback",value:function(){(0,u.A)(t,"connectedCallback",this,3)([]),this._shouldBeDestroy=!1,this.hasUpdated&&!this.disabled&&this._createSortable()}},{key:"createRenderRoot",value:function(){return this}},{key:"render",value:function(){return this.noStyle?p.s6:(0,p.qy)(o||(o=v`
      <style>
        .sortable-fallback {
          display: none !important;
        }

        .sortable-ghost {
          box-shadow: 0 0 0 2px var(--primary-color);
          background: rgba(var(--rgb-primary-color), 0.25);
          border-radius: var(--ha-border-radius-sm);
          opacity: 0.4;
        }

        .sortable-drag {
          border-radius: var(--ha-border-radius-sm);
          opacity: 1;
          background: var(--card-background-color);
          box-shadow: 0px 4px 8px 3px #00000026;
          cursor: grabbing;
        }
      </style>
    `))}},{key:"_createSortable",value:(h=(0,n.A)((0,i.A)().m((function e(){var t,o,n;return(0,i.A)().w((function(e){for(;;)switch(e.n){case 0:if(!this._sortable){e.n=1;break}return e.a(2);case 1:if(t=this.children[0]){e.n=2;break}return e.a(2);case 2:return e.n=3,Promise.all([r.e("5283"),r.e("1387")]).then(r.bind(r,38214));case 3:o=e.v.default,n=Object.assign(Object.assign({scroll:!0,forceAutoScrollFallback:!0,scrollSpeed:20,animation:150},this.options),{},{onChoose:this._handleChoose,onStart:this._handleStart,onEnd:this._handleEnd,onUpdate:this._handleUpdate,onAdd:this._handleAdd,onRemove:this._handleRemove}),this.draggableSelector&&(n.draggable=this.draggableSelector),this.handleSelector&&(n.handle=this.handleSelector),void 0!==this.invertSwap&&(n.invertSwap=this.invertSwap),this.group&&(n.group=this.group),this.filter&&(n.filter=this.filter),this._sortable=new o(t,n);case 4:return e.a(2)}}),e,this)}))),function(){return h.apply(this,arguments)})},{key:"_destroySortable",value:function(){this._sortable&&(this._sortable.destroy(),this._sortable=void 0)}}]);var h}(p.WF);(0,h.__decorate)([(0,f.MZ)({type:Boolean})],m.prototype,"disabled",void 0),(0,h.__decorate)([(0,f.MZ)({type:Boolean,attribute:"no-style"})],m.prototype,"noStyle",void 0),(0,h.__decorate)([(0,f.MZ)({type:String,attribute:"draggable-selector"})],m.prototype,"draggableSelector",void 0),(0,h.__decorate)([(0,f.MZ)({type:String,attribute:"handle-selector"})],m.prototype,"handleSelector",void 0),(0,h.__decorate)([(0,f.MZ)({type:String,attribute:"filter"})],m.prototype,"filter",void 0),(0,h.__decorate)([(0,f.MZ)({type:String})],m.prototype,"group",void 0),(0,h.__decorate)([(0,f.MZ)({type:Boolean,attribute:"invert-swap"})],m.prototype,"invertSwap",void 0),(0,h.__decorate)([(0,f.MZ)({attribute:!1})],m.prototype,"options",void 0),(0,h.__decorate)([(0,f.MZ)({type:Boolean})],m.prototype,"rollback",void 0),m=(0,h.__decorate)([(0,f.EM)("ha-sortable")],m)},67591:function(e,t,r){var o,i=r(44734),n=r(56038),a=r(69683),s=r(6454),l=r(25460),c=(r(28706),r(62826)),d=r(11896),u=r(92347),h=r(75057),p=r(96196),f=r(77845),y=function(e){function t(){var e;(0,i.A)(this,t);for(var r=arguments.length,o=new Array(r),n=0;n<r;n++)o[n]=arguments[n];return(e=(0,a.A)(this,t,[].concat(o))).autogrow=!1,e}return(0,s.A)(t,e),(0,n.A)(t,[{key:"updated",value:function(e){(0,l.A)(t,"updated",this,3)([e]),this.autogrow&&e.has("value")&&(this.mdcRoot.dataset.value=this.value+'=​"')}}])}(d.u);y.styles=[u.R,h.R,(0,p.AH)(o||(o=(e=>e)`
      :host([autogrow]) .mdc-text-field {
        position: relative;
        min-height: 74px;
        min-width: 178px;
        max-height: 200px;
      }
      :host([autogrow]) .mdc-text-field:after {
        content: attr(data-value);
        margin-top: 23px;
        margin-bottom: 9px;
        line-height: var(--ha-line-height-normal);
        min-height: 42px;
        padding: 0px 32px 0 16px;
        letter-spacing: var(
          --mdc-typography-subtitle1-letter-spacing,
          0.009375em
        );
        visibility: hidden;
        white-space: pre-wrap;
      }
      :host([autogrow]) .mdc-text-field__input {
        position: absolute;
        height: calc(100% - 32px);
      }
      :host([autogrow]) .mdc-text-field.mdc-text-field--no-label:after {
        margin-top: 16px;
        margin-bottom: 16px;
      }
      .mdc-floating-label {
        inset-inline-start: 16px !important;
        inset-inline-end: initial !important;
        transform-origin: var(--float-start) top;
      }
      @media only screen and (min-width: 459px) {
        :host([mobile-multiline]) .mdc-text-field__input {
          white-space: nowrap;
          max-height: 16px;
        }
      }
    `))],(0,c.__decorate)([(0,f.MZ)({type:Boolean,reflect:!0})],y.prototype,"autogrow",void 0),y=(0,c.__decorate)([(0,f.EM)("ha-textarea")],y)},88422:function(e,t,r){r.a(e,(async function(e,t){try{var o=r(44734),i=r(56038),n=r(69683),a=r(6454),s=(r(28706),r(2892),r(62826)),l=r(52630),c=r(96196),d=r(77845),u=e([l]);l=(u.then?(await u)():u)[0];var h,p=e=>e,f=function(e){function t(){var e;(0,o.A)(this,t);for(var r=arguments.length,i=new Array(r),a=0;a<r;a++)i[a]=arguments[a];return(e=(0,n.A)(this,t,[].concat(i))).showDelay=150,e.hideDelay=150,e}return(0,a.A)(t,e),(0,i.A)(t,null,[{key:"styles",get:function(){return[l.A.styles,(0,c.AH)(h||(h=p`
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
      `))]}}])}(l.A);(0,s.__decorate)([(0,d.MZ)({attribute:"show-delay",type:Number})],f.prototype,"showDelay",void 0),(0,s.__decorate)([(0,d.MZ)({attribute:"hide-delay",type:Number})],f.prototype,"hideDelay",void 0),f=(0,s.__decorate)([(0,d.EM)("ha-tooltip")],f),t()}catch(y){t(y)}}))},23362:function(e,t,r){r.a(e,(async function(e,t){try{var o=r(61397),i=r(50264),n=r(44734),a=r(56038),s=r(69683),l=r(6454),c=r(25460),d=(r(28706),r(62826)),u=r(53289),h=r(96196),p=r(77845),f=r(92542),y=r(4657),v=r(39396),m=r(4848),g=(r(17963),r(89473)),_=r(32884),b=e([g,_]);[g,_]=b.then?(await b)():b;var w,A,x,k,$,z,M=e=>e,q=function(e){function t(){var e;(0,n.A)(this,t);for(var r=arguments.length,o=new Array(r),i=0;i<r;i++)o[i]=arguments[i];return(e=(0,s.A)(this,t,[].concat(o))).yamlSchema=u.my,e.isValid=!0,e.autoUpdate=!1,e.readOnly=!1,e.disableFullscreen=!1,e.required=!1,e.copyClipboard=!1,e.hasExtraActions=!1,e.showErrors=!0,e._yaml="",e._error="",e._showingError=!1,e}return(0,l.A)(t,e),(0,a.A)(t,[{key:"setValue",value:function(e){try{this._yaml=(e=>{if("object"!=typeof e||null===e)return!1;for(var t in e)if(Object.prototype.hasOwnProperty.call(e,t))return!1;return!0})(e)?"":(0,u.Bh)(e,{schema:this.yamlSchema,quotingType:'"',noRefs:!0})}catch(t){console.error(t,e),alert(`There was an error converting to YAML: ${t}`)}}},{key:"firstUpdated",value:function(){void 0!==this.defaultValue&&this.setValue(this.defaultValue)}},{key:"willUpdate",value:function(e){(0,c.A)(t,"willUpdate",this,3)([e]),this.autoUpdate&&e.has("value")&&this.setValue(this.value)}},{key:"focus",value:function(){var e,t;null!==(e=this._codeEditor)&&void 0!==e&&e.codemirror&&(null===(t=this._codeEditor)||void 0===t||t.codemirror.focus())}},{key:"render",value:function(){return void 0===this._yaml?h.s6:(0,h.qy)(w||(w=M`
      ${0}
      <ha-code-editor
        .hass=${0}
        .value=${0}
        .readOnly=${0}
        .disableFullscreen=${0}
        mode="yaml"
        autocomplete-entities
        autocomplete-icons
        .error=${0}
        @value-changed=${0}
        @blur=${0}
        dir="ltr"
      ></ha-code-editor>
      ${0}
      ${0}
    `),this.label?(0,h.qy)(A||(A=M`<p>${0}${0}</p>`),this.label,this.required?" *":""):h.s6,this.hass,this._yaml,this.readOnly,this.disableFullscreen,!1===this.isValid,this._onChange,this._onBlur,this._showingError?(0,h.qy)(x||(x=M`<ha-alert alert-type="error">${0}</ha-alert>`),this._error):h.s6,this.copyClipboard||this.hasExtraActions?(0,h.qy)(k||(k=M`
            <div class="card-actions">
              ${0}
              <slot name="extra-actions"></slot>
            </div>
          `),this.copyClipboard?(0,h.qy)($||($=M`
                    <ha-button appearance="plain" @click=${0}>
                      ${0}
                    </ha-button>
                  `),this._copyYaml,this.hass.localize("ui.components.yaml-editor.copy_to_clipboard")):h.s6):h.s6)}},{key:"_onChange",value:function(e){var t;e.stopPropagation(),this._yaml=e.detail.value;var r,o=!0;if(this._yaml)try{t=(0,u.Hh)(this._yaml,{schema:this.yamlSchema})}catch(i){o=!1,r=`${this.hass.localize("ui.components.yaml-editor.error",{reason:i.reason})}${i.mark?` (${this.hass.localize("ui.components.yaml-editor.error_location",{line:i.mark.line+1,column:i.mark.column+1})})`:""}`}else t={};this._error=null!=r?r:"",o&&(this._showingError=!1),this.value=t,this.isValid=o,(0,f.r)(this,"value-changed",{value:t,isValid:o,errorMsg:r})}},{key:"_onBlur",value:function(){this.showErrors&&this._error&&(this._showingError=!0)}},{key:"yaml",get:function(){return this._yaml}},{key:"_copyYaml",value:(r=(0,i.A)((0,o.A)().m((function e(){return(0,o.A)().w((function(e){for(;;)switch(e.n){case 0:if(!this.yaml){e.n=2;break}return e.n=1,(0,y.l)(this.yaml);case 1:(0,m.P)(this,{message:this.hass.localize("ui.common.copied_clipboard")});case 2:return e.a(2)}}),e,this)}))),function(){return r.apply(this,arguments)})}],[{key:"styles",get:function(){return[v.RF,(0,h.AH)(z||(z=M`
        .card-actions {
          border-radius: var(
            --actions-border-radius,
            var(--ha-border-radius-square) var(--ha-border-radius-square)
              var(--ha-card-border-radius, var(--ha-border-radius-lg))
              var(--ha-card-border-radius, var(--ha-border-radius-lg))
          );
          border: 1px solid var(--divider-color);
          padding: 5px 16px;
        }
        ha-code-editor {
          flex-grow: 1;
          min-height: 0;
        }
      `))]}}]);var r}(h.WF);(0,d.__decorate)([(0,p.MZ)({attribute:!1})],q.prototype,"hass",void 0),(0,d.__decorate)([(0,p.MZ)()],q.prototype,"value",void 0),(0,d.__decorate)([(0,p.MZ)({attribute:!1})],q.prototype,"yamlSchema",void 0),(0,d.__decorate)([(0,p.MZ)({attribute:!1})],q.prototype,"defaultValue",void 0),(0,d.__decorate)([(0,p.MZ)({attribute:"is-valid",type:Boolean})],q.prototype,"isValid",void 0),(0,d.__decorate)([(0,p.MZ)()],q.prototype,"label",void 0),(0,d.__decorate)([(0,p.MZ)({attribute:"auto-update",type:Boolean})],q.prototype,"autoUpdate",void 0),(0,d.__decorate)([(0,p.MZ)({attribute:"read-only",type:Boolean})],q.prototype,"readOnly",void 0),(0,d.__decorate)([(0,p.MZ)({type:Boolean,attribute:"disable-fullscreen"})],q.prototype,"disableFullscreen",void 0),(0,d.__decorate)([(0,p.MZ)({type:Boolean})],q.prototype,"required",void 0),(0,d.__decorate)([(0,p.MZ)({attribute:"copy-clipboard",type:Boolean})],q.prototype,"copyClipboard",void 0),(0,d.__decorate)([(0,p.MZ)({attribute:"has-extra-actions",type:Boolean})],q.prototype,"hasExtraActions",void 0),(0,d.__decorate)([(0,p.MZ)({attribute:"show-errors",type:Boolean})],q.prototype,"showErrors",void 0),(0,d.__decorate)([(0,p.wk)()],q.prototype,"_yaml",void 0),(0,d.__decorate)([(0,p.wk)()],q.prototype,"_error",void 0),(0,d.__decorate)([(0,p.wk)()],q.prototype,"_showingError",void 0),(0,d.__decorate)([(0,p.P)("ha-code-editor")],q.prototype,"_codeEditor",void 0),q=(0,d.__decorate)([(0,p.EM)("ha-yaml-editor")],q),t()}catch(C){t(C)}}))},80812:function(e,t,r){r.d(t,{Dp:function(){return y},Dt:function(){return c},G3:function(){return f},Q:function(){return l},S9:function(){return v},VH:function(){return s},XF:function(){return d},aI:function(){return h},fo:function(){return p},vO:function(){return u}});var o=r(94741),i=r(31432),n=(r(62062),r(44114),r(18111),r(7588),r(61701),r(26099),r(23500),r(55376)),a=(r(5871),r(9169),r(10038)),s=(r(29272),"__DYNAMIC__"),l=e=>null==e?void 0:e.startsWith(s),c=e=>e.substring(s.length),d=e=>{if("condition"in e&&Array.isArray(e.condition))return{condition:"and",conditions:e.condition};var t,r=(0,i.A)(a.I8);try{for(r.s();!(t=r.n()).done;){var o=t.value;if(o in e)return{condition:o,conditions:e[o]}}}catch(n){r.e(n)}finally{r.f()}return e},u=e=>e?Array.isArray(e)?e.map(u):("triggers"in e&&e.triggers&&(e.triggers=u(e.triggers)),"platform"in e&&("trigger"in e||(e.trigger=e.platform),delete e.platform),e):e,h=e=>{if(!e)return[];var t=[];return(0,n.e)(e).forEach((e=>{"triggers"in e?e.triggers&&t.push.apply(t,(0,o.A)(h(e.triggers))):t.push(e)})),t},p=e=>{if(!e||"object"!=typeof e)return!1;var t=e;return"trigger"in t&&"string"==typeof t.trigger||"platform"in t&&"string"==typeof t.platform},f=e=>{if(!e||"object"!=typeof e)return!1;return"condition"in e&&"string"==typeof e.condition},y=(e,t,r,o)=>e.connection.subscribeMessage(t,{type:"subscribe_trigger",trigger:r,variables:o}),v=(e,t,r)=>e.callWS({type:"test_condition",condition:t,variables:r})},53295:function(e,t,r){r.a(e,(async function(e,o){try{r.d(t,{g:function(){return A},p:function(){return $}});var i=r(31432),n=(r(16280),r(18107),r(50113),r(74423),r(23792),r(62062),r(44114),r(18111),r(20116),r(61701),r(33110),r(2892),r(26099),r(16034),r(27495),r(38781),r(67357),r(71761),r(62953),r(55376)),a=r(88738),s=r(4359),l=r(21754),c=r(48551),d=r(91889),u=r(45996),h=r(39680),p=r(72125),f=r(10038),y=r(74687),v=r(98995),m=e([s,a,c,h]);[s,a,c,h]=m.then?(await m)():m;var g="ui.panel.config.automation.editor.triggers.type",_="ui.panel.config.automation.editor.conditions.type",b=(e,t)=>"number"==typeof t?(0,l.A)(t):"string"==typeof t?t:(0,a.nR)(e,t),w=(e,t,r)=>{var o=e.split(":");if(o.length<2||o.length>3)return e;try{var i=new Date("1970-01-01T"+e);return 2===o.length||0===Number(o[2])?(0,s.fU)(i,t,r):(0,s.ie)(i,t,r)}catch(n){return e}},A=function(e,t,r){var o=arguments.length>3&&void 0!==arguments[3]&&arguments[3];try{var i=x(e,t,r,o);if("string"!=typeof i)throw new Error(String(i));return i}catch(a){console.error(a);var n="Error in describing trigger";return a.message&&(n+=": "+a.message),n}},x=function(e,t,r){var o=arguments.length>3&&void 0!==arguments[3]&&arguments[3];if((0,v.H4)(e)){var i=(0,n.e)(e.triggers);if(!i||0===i.length)return t.localize(`${g}.list.description.no_trigger`);var a=i.length;return t.localize(`${g}.list.description.full`,{count:a})}if(e.alias&&!o)return e.alias;var s=k(e,t,r);if(s)return s;var l=e.trigger,c=(0,v.zz)(e.trigger),d=(0,v.hN)(e.trigger);return t.localize(`component.${c}.triggers.${d}.name`)||t.localize(`ui.panel.config.automation.editor.triggers.type.${l}.label`)||t.localize("ui.panel.config.automation.editor.triggers.unknown_trigger")},k=(e,t,r)=>{if("event"===e.trigger&&e.event_type){var o=[];if(Array.isArray(e.event_type)){var s,p=(0,i.A)(e.event_type.values());try{for(p.s();!(s=p.n()).done;){var f=s.value;o.push(f)}}catch(We){p.e(We)}finally{p.f()}}else o.push(e.event_type);var v=(0,h.q)(t.locale,o);return t.localize(`${g}.event.description.full`,{eventTypes:v})}if("homeassistant"===e.trigger&&e.event)return t.localize("start"===e.event?`${g}.homeassistant.description.started`:`${g}.homeassistant.description.shutdown`);if("numeric_state"===e.trigger&&e.entity_id){var m=[],_=t.states,A=Array.isArray(e.entity_id)?t.states[e.entity_id[0]]:t.states[e.entity_id];if(Array.isArray(e.entity_id)){var x,k=(0,i.A)(e.entity_id.values());try{for(k.s();!(x=k.n()).done;){var $=x.value;_[$]&&m.push((0,d.u)(_[$])||$)}}catch(We){k.e(We)}finally{k.f()}}else e.entity_id&&m.push(_[e.entity_id]?(0,d.u)(_[e.entity_id]):e.entity_id);var z=e.attribute?A?(0,c.R)(t.localize,A,t.entities,e.attribute):e.attribute:void 0,M=e.for?b(t.locale,e.for):void 0;if(void 0!==e.above&&void 0!==e.below)return t.localize(`${g}.numeric_state.description.above-below`,{attribute:z,entity:(0,h.q)(t.locale,m),numberOfEntities:m.length,above:e.above,below:e.below,duration:M});if(void 0!==e.above)return t.localize(`${g}.numeric_state.description.above`,{attribute:z,entity:(0,h.q)(t.locale,m),numberOfEntities:m.length,above:e.above,duration:M});if(void 0!==e.below)return t.localize(`${g}.numeric_state.description.below`,{attribute:z,entity:(0,h.q)(t.locale,m),numberOfEntities:m.length,below:e.below,duration:M})}if("state"===e.trigger){var q=[],C=t.states,Z="";if(e.attribute){var E=Array.isArray(e.entity_id)?t.states[e.entity_id[0]]:t.states[e.entity_id];Z=E?(0,c.R)(t.localize,E,t.entities,e.attribute):e.attribute}var S=(0,n.e)(e.entity_id);if(S){var O,I=(0,i.A)(S);try{for(I.s();!(O=I.n()).done;){var D=O.value;C[D]&&q.push((0,d.u)(C[D])||D)}}catch(We){I.e(We)}finally{I.f()}}var T=t.states[S[0]],j="other",F="";if(void 0!==e.from){var B=[];if(null===e.from)e.attribute||(j="null");else{B=(0,n.e)(e.from);var N,R=[],H=(0,i.A)(B);try{for(H.s();!(N=H.n()).done;){var L=N.value;R.push(T?e.attribute?t.formatEntityAttributeValue(T,e.attribute,L).toString():t.formatEntityState(T,L):L)}}catch(We){H.e(We)}finally{H.f()}0!==R.length&&(F=(0,h.q)(t.locale,R),j="fromUsed")}}var P="other",W="";if(void 0!==e.to){var V=[];if(null===e.to)e.attribute||(P="null");else{V=(0,n.e)(e.to);var U,Y=[],J=(0,i.A)(V);try{for(J.s();!(U=J.n()).done;){var K=U.value;Y.push(T?e.attribute?t.formatEntityAttributeValue(T,e.attribute,K).toString():t.formatEntityState(T,K).toString():K)}}catch(We){J.e(We)}finally{J.f()}0!==Y.length&&(W=(0,h.q)(t.locale,Y),P="toUsed")}}e.attribute||void 0!==e.from||void 0!==e.to||(P="special");var X,G="";if(e.for)G=null!==(X=b(t.locale,e.for))&&void 0!==X?X:"";return t.localize(`${g}.state.description.full`,{hasAttribute:""!==Z?"true":"false",attribute:Z,hasEntity:0!==q.length?"true":"false",entity:(0,h.q)(t.locale,q),fromChoice:j,fromString:F,toChoice:P,toString:W,hasDuration:""!==G?"true":"false",duration:G})}if("sun"===e.trigger&&e.event){var Q="";return e.offset&&(Q="number"==typeof e.offset?(0,l.A)(e.offset):"string"==typeof e.offset?e.offset:JSON.stringify(e.offset)),t.localize("sunset"===e.event?`${g}.sun.description.sets`:`${g}.sun.description.rises`,{hasDuration:""!==Q?"true":"false",duration:Q})}if("tag"===e.trigger){var ee=Object.values(t.states).find((t=>t.entity_id.startsWith("tag.")&&t.attributes.tag_id===e.tag_id));return ee?t.localize(`${g}.tag.description.known_tag`,{tag_name:(0,d.u)(ee)}):t.localize(`${g}.tag.description.full`)}if("time"===e.trigger&&e.at){var te=(0,n.e)(e.at).map((e=>"string"==typeof e?(0,u.n)(e)?`entity ${t.states[e]?(0,d.u)(t.states[e]):e}`:w(e,t.locale,t.config):`${`entity ${t.states[e.entity_id]?(0,d.u)(t.states[e.entity_id]):e.entity_id}`}${e.offset?" "+t.localize(`${g}.time.offset_by`,{offset:b(t.locale,e.offset)}):""}`)),re=[];if(e.weekday){var oe=(0,n.e)(e.weekday);oe.length>0&&(re=oe.map((e=>t.localize(`ui.panel.config.automation.editor.triggers.type.time.weekdays.${e}`))))}return t.localize(`${g}.time.description.full`,{time:(0,h.q)(t.locale,te),hasWeekdays:re.length>0?"true":"false",weekdays:(0,h.q)(t.locale,re)})}if("time_pattern"===e.trigger){if(!e.seconds&&!e.minutes&&!e.hours)return t.localize(`${g}.time_pattern.description.initial`);var ie=[],ne="other",ae="other",se="other",le=0,ce=0,de=0;if(void 0!==e.seconds){var ue="*"===e.seconds,he="string"==typeof e.seconds&&e.seconds.startsWith("/");le=ue?0:"number"==typeof e.seconds?e.seconds:he?parseInt(e.seconds.substring(1)):parseInt(e.seconds),(isNaN(le)||le>59||le<0||he&&0===le)&&ie.push("seconds"),ne=ue||he&&1===le?"every":he?"every_interval":"on_the_xth"}if(void 0!==e.minutes){var pe="*"===e.minutes,fe="string"==typeof e.minutes&&e.minutes.startsWith("/");ce=pe?0:"number"==typeof e.minutes?e.minutes:fe?parseInt(e.minutes.substring(1)):parseInt(e.minutes),(isNaN(ce)||ce>59||ce<0||fe&&0===ce)&&ie.push("minutes"),ae=pe||fe&&1===ce?"every":fe?"every_interval":void 0!==e.seconds?"has_seconds":"on_the_xth"}else void 0!==e.seconds&&(void 0!==e.hours?(ce=0,ae="has_seconds"):ae="every");if(void 0!==e.hours){var ye="*"===e.hours,ve="string"==typeof e.hours&&e.hours.startsWith("/");de=ye?0:"number"==typeof e.hours?e.hours:ve?parseInt(e.hours.substring(1)):parseInt(e.hours),(isNaN(de)||de>23||de<0||ve&&0===de)&&ie.push("hours"),se=ye||ve&&1===de?"every":ve?"every_interval":void 0!==e.seconds||void 0!==e.minutes?"has_seconds_or_minutes":"on_the_xth"}else se="every";return 0!==ie.length?t.localize(`${g}.time_pattern.description.invalid`,{parts:(0,h.c)(t.locale,ie.map((e=>t.localize(`${g}.time_pattern.${e}`))))}):t.localize(`${g}.time_pattern.description.full`,{secondsChoice:ne,minutesChoice:ae,hoursChoice:se,seconds:le,minutes:ce,hours:de,secondsWithOrdinal:t.localize(`${g}.time_pattern.description.ordinal`,{part:le}),minutesWithOrdinal:t.localize(`${g}.time_pattern.description.ordinal`,{part:ce}),hoursWithOrdinal:t.localize(`${g}.time_pattern.description.ordinal`,{part:de})})}if("zone"===e.trigger&&e.entity_id&&e.zone){var me=[],ge=[],_e=t.states;if(Array.isArray(e.entity_id)){var be,we=(0,i.A)(e.entity_id.values());try{for(we.s();!(be=we.n()).done;){var Ae=be.value;_e[Ae]&&me.push((0,d.u)(_e[Ae])||Ae)}}catch(We){we.e(We)}finally{we.f()}}else me.push(_e[e.entity_id]?(0,d.u)(_e[e.entity_id]):e.entity_id);if(Array.isArray(e.zone)){var xe,ke=(0,i.A)(e.zone.values());try{for(ke.s();!(xe=ke.n()).done;){var $e=xe.value;_e[$e]&&ge.push((0,d.u)(_e[$e])||$e)}}catch(We){ke.e(We)}finally{ke.f()}}else ge.push(_e[e.zone]?(0,d.u)(_e[e.zone]):e.zone);return t.localize(`${g}.zone.description.full`,{entity:(0,h.q)(t.locale,me),event:e.event.toString(),zone:(0,h.q)(t.locale,ge),numberOfZones:ge.length})}if("geo_location"===e.trigger&&e.source&&e.zone){var ze=[],Me=[],qe=t.states;if(Array.isArray(e.source)){var Ce,Ze=(0,i.A)(e.source.values());try{for(Ze.s();!(Ce=Ze.n()).done;){var Ee=Ce.value;ze.push(Ee)}}catch(We){Ze.e(We)}finally{Ze.f()}}else ze.push(e.source);if(Array.isArray(e.zone)){var Se,Oe=(0,i.A)(e.zone.values());try{for(Oe.s();!(Se=Oe.n()).done;){var Ie=Se.value;qe[Ie]&&Me.push((0,d.u)(qe[Ie])||Ie)}}catch(We){Oe.e(We)}finally{Oe.f()}}else Me.push(qe[e.zone]?(0,d.u)(qe[e.zone]):e.zone);return t.localize(`${g}.geo_location.description.full`,{source:(0,h.q)(t.locale,ze),event:e.event.toString(),zone:(0,h.q)(t.locale,Me),numberOfZones:Me.length})}if("mqtt"===e.trigger)return t.localize(`${g}.mqtt.description.full`);if("template"===e.trigger){var De,Te="";if(e.for)Te=null!==(De=b(t.locale,e.for))&&void 0!==De?De:"";return t.localize(`${g}.template.description.full`,{hasDuration:""!==Te?"true":"false",duration:Te})}if("webhook"===e.trigger)return t.localize(`${g}.webhook.description.full`);if("conversation"===e.trigger){if(!e.command||!e.command.length)return t.localize(`${g}.conversation.description.empty`);var je=(0,n.e)(e.command);return 1===je.length?t.localize(`${g}.conversation.description.single`,{sentence:je[0]}):t.localize(`${g}.conversation.description.multiple`,{sentence:je[0],count:je.length-1})}if("persistent_notification"===e.trigger)return t.localize(`${g}.persistent_notification.description.full`);if("device"===e.trigger&&e.device_id){var Fe=e,Be=(0,y.nx)(t,r,Fe);if(Be)return Be;var Ne=t.states[Fe.entity_id];return`${Ne?(0,d.u)(Ne):Fe.entity_id} ${Fe.type}`}if("calendar"===e.trigger){var Re=t.states[e.entity_id]?(0,d.u)(t.states[e.entity_id]):e.entity_id,He="other",Le="";if(e.offset){He=e.offset.startsWith("-")?"before":"after";var Pe={hours:(Le=e.offset.startsWith("-")?e.offset.substring(1).split(":"):e.offset.split(":")).length>0?+Le[0]:0,minutes:Le.length>1?+Le[1]:0,seconds:Le.length>2?+Le[2]:0};""===(Le=(0,a.i)(t.locale,Pe))&&(He="other")}return t.localize(`${g}.calendar.description.full`,{eventChoice:e.event,offsetChoice:He,offset:Le,hasCalendar:e.entity_id?"true":"false",calendar:Re})}},$=function(e,t,r){var o=arguments.length>3&&void 0!==arguments[3]&&arguments[3];try{var i=z(e,t,r,o);if("string"!=typeof i)throw new Error(String(i));return i}catch(a){console.error(a);var n="Error in describing condition";return a.message&&(n+=": "+a.message),n}},z=function(e,t,r){var o=arguments.length>3&&void 0!==arguments[3]&&arguments[3];if("string"==typeof e&&(0,p.r)(e))return t.localize(`${_}.template.description.full`);if(e.alias&&!o)return e.alias;if(!e.condition)for(var i=0,a=["and","or","not"];i<a.length;i++){var s=a[i];s in e&&((0,n.e)(e[s])&&(e={condition:s,conditions:e[s]}))}var l=M(e,t,r);if(l)return l;var c=e.condition,d=(0,f.ob)(e.condition),u=(0,f.YQ)(e.condition);return t.localize(`component.${d}.conditions.${u}.name`)||t.localize(`ui.panel.config.automation.editor.conditions.type.${c}.label`)||t.localize("ui.panel.config.automation.editor.conditions.unknown_condition")},M=(e,t,r)=>{if("or"===e.condition){var o=(0,n.e)(e.conditions);if(!o||0===o.length)return t.localize(`${_}.or.description.no_conditions`);var a=o.length;return t.localize(`${_}.or.description.full`,{count:a})}if("and"===e.condition){var s=(0,n.e)(e.conditions);if(!s||0===s.length)return t.localize(`${_}.and.description.no_conditions`);var u=s.length;return t.localize(`${_}.and.description.full`,{count:u})}if("not"===e.condition){var p=(0,n.e)(e.conditions);return p&&0!==p.length?1===p.length?t.localize(`${_}.not.description.one_condition`):t.localize(`${_}.not.description.full`,{count:p.length}):t.localize(`${_}.not.description.no_conditions`)}if("state"===e.condition){if(!e.entity_id)return t.localize(`${_}.state.description.no_entity`);var f="";if(e.attribute){var v=Array.isArray(e.entity_id)?t.states[e.entity_id[0]]:t.states[e.entity_id];f=v?(0,c.R)(t.localize,v,t.entities,e.attribute):e.attribute}var m=[];if(Array.isArray(e.entity_id)){var g,A=(0,i.A)(e.entity_id.values());try{for(A.s();!(g=A.n()).done;){var x=g.value;t.states[x]&&m.push((0,d.u)(t.states[x])||x)}}catch(ie){A.e(ie)}finally{A.f()}}else e.entity_id&&m.push(t.states[e.entity_id]?(0,d.u)(t.states[e.entity_id]):e.entity_id);var k=[],$=t.states[Array.isArray(e.entity_id)?e.entity_id[0]:e.entity_id];if(Array.isArray(e.state)){var z,M=(0,i.A)(e.state.values());try{for(M.s();!(z=M.n()).done;){var q=z.value;k.push($?e.attribute?t.formatEntityAttributeValue($,e.attribute,q).toString():t.formatEntityState($,q):q)}}catch(ie){M.e(ie)}finally{M.f()}}else""!==e.state&&k.push($?e.attribute?t.formatEntityAttributeValue($,e.attribute,e.state).toString():t.formatEntityState($,e.state.toString()):e.state.toString());var C="";return e.for&&(C=b(t.locale,e.for)||""),t.localize(`${_}.state.description.full`,{hasAttribute:""!==f?"true":"false",attribute:f,numberOfEntities:m.length,entities:"any"===e.match?(0,h.q)(t.locale,m):(0,h.c)(t.locale,m),numberOfStates:k.length,states:(0,h.q)(t.locale,k),hasDuration:""!==C?"true":"false",duration:C})}if("numeric_state"===e.condition&&e.entity_id){var Z=(0,n.e)(e.entity_id),E=t.states[Z[0]],S=(0,h.c)(t.locale,Z.map((e=>t.states[e]?(0,d.u)(t.states[e]):e||""))),O=e.attribute?E?(0,c.R)(t.localize,E,t.entities,e.attribute):e.attribute:void 0;if(void 0!==e.above&&void 0!==e.below)return t.localize(`${_}.numeric_state.description.above-below`,{attribute:O,entity:S,numberOfEntities:Z.length,above:e.above,below:e.below});if(void 0!==e.above)return t.localize(`${_}.numeric_state.description.above`,{attribute:O,entity:S,numberOfEntities:Z.length,above:e.above});if(void 0!==e.below)return t.localize(`${_}.numeric_state.description.below`,{attribute:O,entity:S,numberOfEntities:Z.length,below:e.below})}if("time"===e.condition){var I=(0,n.e)(e.weekday),D=I&&I.length>0&&I.length<7;if(e.before||e.after||D){var T="string"!=typeof e.before?e.before:e.before.includes(".")?`entity ${t.states[e.before]?(0,d.u)(t.states[e.before]):e.before}`:w(e.before,t.locale,t.config),j="string"!=typeof e.after?e.after:e.after.includes(".")?`entity ${t.states[e.after]?(0,d.u)(t.states[e.after]):e.after}`:w(e.after,t.locale,t.config),F=[];D&&(F=I.map((e=>t.localize(`ui.panel.config.automation.editor.conditions.type.time.weekdays.${e}`))));var B="";return void 0!==j&&void 0!==T?B="after_before":void 0!==j?B="after":void 0!==T&&(B="before"),t.localize(`${_}.time.description.full`,{hasTime:B,hasTimeAndDay:(j||T)&&D?"true":"false",hasDay:D?"true":"false",time_before:T,time_after:j,day:(0,h.q)(t.locale,F)})}}if("sun"===e.condition&&(e.before||e.after)){var N,R,H="";e.after&&e.after_offset&&(H="number"==typeof e.after_offset?(0,l.A)(e.after_offset):"string"==typeof e.after_offset?e.after_offset:JSON.stringify(e.after_offset));var L="";return e.before&&e.before_offset&&(L="number"==typeof e.before_offset?(0,l.A)(e.before_offset):"string"==typeof e.before_offset?e.before_offset:JSON.stringify(e.before_offset)),t.localize(`${_}.sun.description.full`,{afterChoice:null!==(N=e.after)&&void 0!==N?N:"other",afterOffsetChoice:""!==H?"offset":"other",afterOffset:H,beforeChoice:null!==(R=e.before)&&void 0!==R?R:"other",beforeOffsetChoice:""!==L?"offset":"other",beforeOffset:L})}if("zone"===e.condition&&e.entity_id&&e.zone){var P=[],W=[],V=t.states;if(Array.isArray(e.entity_id)){var U,Y=(0,i.A)(e.entity_id.values());try{for(Y.s();!(U=Y.n()).done;){var J=U.value;V[J]&&P.push((0,d.u)(V[J])||J)}}catch(ie){Y.e(ie)}finally{Y.f()}}else P.push(V[e.entity_id]?(0,d.u)(V[e.entity_id]):e.entity_id);if(Array.isArray(e.zone)){var K,X=(0,i.A)(e.zone.values());try{for(X.s();!(K=X.n()).done;){var G=K.value;V[G]&&W.push((0,d.u)(V[G])||G)}}catch(ie){X.e(ie)}finally{X.f()}}else W.push(V[e.zone]?(0,d.u)(V[e.zone]):e.zone);var Q=(0,h.q)(t.locale,P),ee=(0,h.q)(t.locale,W);return t.localize(`${_}.zone.description.full`,{entity:Q,numberOfEntities:P.length,zone:ee,numberOfZones:W.length})}if("device"===e.condition&&e.device_id){var te=e,re=(0,y.I3)(t,r,te);if(re)return re;var oe=t.states[te.entity_id];return`${oe?(0,d.u)(oe):te.entity_id} ${te.type}`}return"template"===e.condition?t.localize(`${_}.template.description.full`):"trigger"===e.condition&&null!=e.id?t.localize(`${_}.trigger.description.full`,{id:(0,h.q)(t.locale,(0,n.e)(e.id).map((e=>e.toString())))}):void 0};o()}catch(q){o(q)}}))},34485:function(e,t,r){r.d(t,{$:function(){return o}});var o=(e,t)=>e.callWS(Object.assign({type:"validate_config"},t))},34972:function(e,t,r){r.d(t,{$F:function(){return l},HD:function(){return u},X1:function(){return n},iN:function(){return i},ih:function(){return c},rf:function(){return d},wn:function(){return s},xJ:function(){return a}});var o=r(16527),i=((0,o.q6)("connection"),(0,o.q6)("states")),n=(0,o.q6)("entities"),a=(0,o.q6)("devices"),s=(0,o.q6)("areas"),l=(0,o.q6)("localize"),c=((0,o.q6)("locale"),(0,o.q6)("config"),(0,o.q6)("themes"),(0,o.q6)("selectedTheme"),(0,o.q6)("user"),(0,o.q6)("userData"),(0,o.q6)("panels"),(0,o.q6)("extendedEntities")),d=(0,o.q6)("floors"),u=(0,o.q6)("labels")},74687:function(e,t,r){r.d(t,{I$:function(){return d},I3:function(){return m},PV:function(){return v},Po:function(){return p},RK:function(){return w},TB:function(){return u},TH:function(){return b},T_:function(){return _},am:function(){return a},jR:function(){return c},ng:function(){return s},nx:function(){return g},o9:function(){return l}});r(74423);var o=r(91889),i=r(80812),n=r(22800),a=(e,t)=>e.callWS({type:"device_automation/action/list",device_id:t}),s=(e,t)=>e.callWS({type:"device_automation/condition/list",device_id:t}),l=(e,t)=>e.callWS({type:"device_automation/trigger/list",device_id:t}).then((e=>(0,i.vO)(e))),c=(e,t)=>e.callWS({type:"device_automation/action/capabilities",action:t}),d=(e,t)=>e.callWS({type:"device_automation/condition/capabilities",condition:t}),u=(e,t)=>e.callWS({type:"device_automation/trigger/capabilities",trigger:t}),h=["device_id","domain","entity_id","type","subtype","event","condition","trigger"],p=(e,t,r)=>{if(typeof t!=typeof r)return!1;for(var o in t){var i,n;if(h.includes(o))if("entity_id"!==o||(null===(i=t[o])||void 0===i?void 0:i.includes("."))===(null===(n=r[o])||void 0===n?void 0:n.includes("."))){if(!Object.is(t[o],r[o]))return!1}else if(!f(e,t[o],r[o]))return!1}for(var a in r){var s,l;if(h.includes(a))if("entity_id"!==a||(null===(s=t[a])||void 0===s?void 0:s.includes("."))===(null===(l=r[a])||void 0===l?void 0:l.includes("."))){if(!Object.is(t[a],r[a]))return!1}else if(!f(e,t[a],r[a]))return!1}return!0},f=(e,t,r)=>{if(!t||!r)return!1;if(t.includes(".")){var o=(0,n.Ox)(e)[t];if(!o)return!1;t=o.id}if(r.includes(".")){var i=(0,n.Ox)(e)[r];if(!i)return!1;r=i.id}return t===r},y=(e,t,r)=>{if(!r)return"<"+e.localize("ui.panel.config.automation.editor.unknown_entity")+">";if(r.includes(".")){var i=e.states[r];return i?(0,o.u)(i):r}var a=(0,n.P9)(t)[r];return a?(0,n.jh)(e,a)||r:"<"+e.localize("ui.panel.config.automation.editor.unknown_entity")+">"},v=(e,t,r)=>e.localize(`component.${r.domain}.device_automation.action_type.${r.type}`,{entity_name:y(e,t,r.entity_id),subtype:r.subtype?e.localize(`component.${r.domain}.device_automation.action_subtype.${r.subtype}`)||r.subtype:""})||(r.subtype?`"${r.subtype}" ${r.type}`:r.type),m=(e,t,r)=>e.localize(`component.${r.domain}.device_automation.condition_type.${r.type}`,{entity_name:y(e,t,r.entity_id),subtype:r.subtype?e.localize(`component.${r.domain}.device_automation.condition_subtype.${r.subtype}`)||r.subtype:""})||(r.subtype?`"${r.subtype}" ${r.type}`:r.type),g=(e,t,r)=>e.localize(`component.${r.domain}.device_automation.trigger_type.${r.type}`,{entity_name:y(e,t,r.entity_id),subtype:r.subtype?e.localize(`component.${r.domain}.device_automation.trigger_subtype.${r.subtype}`)||r.subtype:""})||(r.subtype?`"${r.subtype}" ${r.type}`:r.type),_=(e,t)=>r=>e.localize(`component.${t.domain}.device_automation.extra_fields.${r.name}`)||r.name,b=(e,t)=>r=>e.localize(`component.${t.domain}.device_automation.extra_fields_descriptions.${r.name}`),w=(e,t)=>{var r,o,i,n;return null===(r=e.metadata)||void 0===r||!r.secondary||null!==(o=t.metadata)&&void 0!==o&&o.secondary?null!==(i=e.metadata)&&void 0!==i&&i.secondary||null===(n=t.metadata)||void 0===n||!n.secondary?0:-1:1}},2654:function(e,t,r){r.a(e,(async function(e,o){try{r.d(t,{We:function(){return s},rM:function(){return a}});r(23792),r(26099),r(38781),r(31415),r(17642),r(58004),r(33853),r(45876),r(32475),r(15024),r(31698),r(62953);var i=r(88738),n=e([i]);i=(n.then?(await n)():n)[0];new Set(["temperature","current_temperature","target_temperature","target_temp_temp","target_temp_high","target_temp_low","target_temp_step","min_temp","max_temp"]);var a={climate:{humidity:"%",current_humidity:"%",target_humidity_low:"%",target_humidity_high:"%",target_humidity_step:"%",min_humidity:"%",max_humidity:"%"},cover:{current_position:"%",current_tilt_position:"%"},fan:{percentage:"%"},humidifier:{humidity:"%",current_humidity:"%",min_humidity:"%",max_humidity:"%"},light:{color_temp:"mired",max_mireds:"mired",min_mireds:"mired",color_temp_kelvin:"K",min_color_temp_kelvin:"K",max_color_temp_kelvin:"K",brightness:"%"},sun:{azimuth:"°",elevation:"°"},vacuum:{battery_level:"%"},valve:{current_position:"%"},sensor:{battery_level:"%"},media_player:{volume_level:"%"}},s=["access_token","auto_update","available_modes","away_mode","changed_by","code_format","color_modes","current_activity","device_class","editable","effect_list","effect","entity_picture","event_type","event_types","fan_mode","fan_modes","fan_speed_list","forecast","friendly_name","frontend_stream_type","has_date","has_time","hs_color","hvac_mode","hvac_modes","icon","media_album_name","media_artist","media_content_type","media_position_updated_at","media_title","next_dawn","next_dusk","next_midnight","next_noon","next_rising","next_setting","operation_list","operation_mode","options","preset_mode","preset_modes","release_notes","release_summary","release_url","restored","rgb_color","rgbw_color","shuffle","sound_mode_list","sound_mode","source_list","source_type","source","state_class","supported_features","swing_mode","swing_mode","swing_modes","title","token","unit_of_measurement","xy_color"];o()}catch(l){o(l)}}))},78991:function(e,t,r){r.d(t,{CO:function(){return o}});r(61397),r(50264);var o=(e,t,r,o)=>e.subscribeMessage(o,{type:"labs/subscribe",domain:t,preview_feature:r})},29272:function(e,t,r){r.d(t,{BD:function(){return d},Rn:function(){return p},pq:function(){return u},ve:function(){return h}});var o=r(31432),i=(r(78261),r(62062),r(18111),r(81148),r(61701),r(13579),r(5506),r(26099),r(16034),r(96685)),n=r(99245),a=(r(8635),r(5871),r(72125)),s=(r(9169),r(80812)),l=((0,n.g)(["queued","parallel"]),(0,i.Ik)({alias:(0,i.lq)((0,i.Yj)()),continue_on_error:(0,i.lq)((0,i.zM)()),enabled:(0,i.lq)((0,i.zM)())})),c=(0,i.Ik)({entity_id:(0,i.lq)((0,i.KC)([(0,i.Yj)(),(0,i.YO)((0,i.Yj)())])),device_id:(0,i.lq)((0,i.KC)([(0,i.Yj)(),(0,i.YO)((0,i.Yj)())])),area_id:(0,i.lq)((0,i.KC)([(0,i.Yj)(),(0,i.YO)((0,i.Yj)())])),floor_id:(0,i.lq)((0,i.KC)([(0,i.Yj)(),(0,i.YO)((0,i.Yj)())])),label_id:(0,i.lq)((0,i.KC)([(0,i.Yj)(),(0,i.YO)((0,i.Yj)())]))}),d=(0,i.kp)(l,(0,i.Ik)({action:(0,i.lq)((0,i.Yj)()),service_template:(0,i.lq)((0,i.Yj)()),entity_id:(0,i.lq)((0,i.Yj)()),target:(0,i.lq)((0,i.KC)([c,(0,i.YP)((0,i.Yj)(),"has_template",(e=>(0,a.r)(e)))])),data:(0,i.lq)((0,i.Ik)()),response_variable:(0,i.lq)((0,i.Yj)()),metadata:(0,i.lq)((0,i.Ik)())})),u=e=>"string"==typeof e&&(0,a.r)(e)?"check_condition":"delay"in e?"delay":"wait_template"in e?"wait_template":["condition","and","or","not"].some((t=>t in e))?"check_condition":"event"in e?"fire_event":!("device_id"in e)||"trigger"in e||"condition"in e?"repeat"in e?"repeat":"choose"in e?"choose":"if"in e?"if":"wait_for_trigger"in e?"wait_for_trigger":"variables"in e?"variables":"stop"in e?"stop":"sequence"in e?"sequence":"parallel"in e?"parallel":"set_conversation_response"in e?"set_conversation_response":"action"in e||"service"in e?"service":"unknown":"device_action",h=e=>"unknown"!==u(e),p=e=>{var t,r;if(!e)return e;if(Array.isArray(e))return e.map(p);if("object"==typeof e&&null!==e&&"service"in e&&("action"in e||(e.action=e.service),delete e.service),"object"==typeof e&&null!==e&&"scene"in e&&(e.action="scene.turn_on",e.target={entity_id:e.scene},delete e.scene),"object"==typeof e&&null!==e&&"action"in e&&"media_player.play_media"===e.action&&"data"in e&&(null!==(t=e.data)&&void 0!==t&&t.media_content_id||null!==(r=e.data)&&void 0!==r&&r.media_content_type)){var i=Object.assign({},e.data),n={media_content_id:i.media_content_id,media_content_type:i.media_content_type,metadata:Object.assign({},e.metadata||{})};delete e.metadata,delete i.media_content_id,delete i.media_content_type,e.data=Object.assign(Object.assign({},i),{},{media:n})}if("object"==typeof e&&null!==e&&"sequence"in e){delete e.metadata;var a,l=(0,o.A)(e.sequence);try{for(l.s();!(a=l.n()).done;){var c=a.value;p(c)}}catch(_){l.e(_)}finally{l.f()}}var d=u(e);"parallel"===d&&p(e.parallel);if("choose"===d){var h=e;if(Array.isArray(h.choose)){var f,y=(0,o.A)(h.choose);try{for(y.s();!(f=y.n()).done;){var v=f.value;p(v.sequence)}}catch(_){y.e(_)}finally{y.f()}}else h.choose&&p(h.choose.sequence);h.default&&p(h.default)}"repeat"===d&&p(e.repeat.sequence);if("if"===d){var m=e;p(m.then),m.else&&p(m.else)}if("wait_for_trigger"===d){var g=e;(0,s.vO)(g.wait_for_trigger)}return e}},34099:function(e,t,r){r(31432),r(23792),r(44114),r(26099),r(38781),r(31415),r(17642),r(58004),r(33853),r(45876),r(32475),r(15024),r(31698),r(62953);var o,i=r(96196),n=(r(29485),r(60961),e=>e);new Set(["clear-night","cloudy","fog","lightning","lightning-rainy","partlycloudy","pouring","rainy","hail","snowy","snowy-rainy","sunny","windy","windy-variant"]),new Set(["partlycloudy","cloudy","fog","windy","windy-variant","hail","rainy","snowy","snowy-rainy","pouring","lightning","lightning-rainy"]),new Set(["hail","rainy","pouring","lightning-rainy"]),new Set(["windy","windy-variant"]),new Set(["snowy","snowy-rainy"]),new Set(["lightning","lightning-rainy"]),(0,i.AH)(o||(o=n`
  .rain {
    fill: var(--weather-icon-rain-color, #30b3ff);
  }
  .sun {
    fill: var(--weather-icon-sun-color, #fdd93c);
  }
  .moon {
    fill: var(--weather-icon-moon-color, #fcf497);
  }
  .cloud-back {
    fill: var(--weather-icon-cloud-back-color, #d4d4d4);
  }
  .cloud-front {
    fill: var(--weather-icon-cloud-front-color, #f9f9f9);
  }
  .snow {
    fill: var(--weather-icon-snow-color, #f9f9f9);
    stroke: var(--weather-icon-snow-stroke-color, #d4d4d4);
    stroke-width: 1;
    paint-order: stroke;
  }
`))},10085:function(e,t,r){r.d(t,{E:function(){return u}});var o=r(31432),i=r(44734),n=r(56038),a=r(69683),s=r(25460),l=r(6454),c=(r(74423),r(23792),r(18111),r(13579),r(26099),r(3362),r(62953),r(62826)),d=r(77845),u=e=>{var t=function(e){function t(){return(0,i.A)(this,t),(0,a.A)(this,t,arguments)}return(0,l.A)(t,e),(0,n.A)(t,[{key:"connectedCallback",value:function(){(0,s.A)(t,"connectedCallback",this,3)([]),this._checkSubscribed()}},{key:"disconnectedCallback",value:function(){if((0,s.A)(t,"disconnectedCallback",this,3)([]),this.__unsubs){for(;this.__unsubs.length;){var e=this.__unsubs.pop();e instanceof Promise?e.then((e=>e())):e()}this.__unsubs=void 0}}},{key:"updated",value:function(e){if((0,s.A)(t,"updated",this,3)([e]),e.has("hass"))this._checkSubscribed();else if(this.hassSubscribeRequiredHostProps){var r,i=(0,o.A)(e.keys());try{for(i.s();!(r=i.n()).done;){var n=r.value;if(this.hassSubscribeRequiredHostProps.includes(n))return void this._checkSubscribed()}}catch(a){i.e(a)}finally{i.f()}}}},{key:"hassSubscribe",value:function(){return[]}},{key:"_checkSubscribed",value:function(){var e;void 0!==this.__unsubs||!this.isConnected||void 0===this.hass||null!==(e=this.hassSubscribeRequiredHostProps)&&void 0!==e&&e.some((e=>void 0===this[e]))||(this.__unsubs=this.hassSubscribe())}}])}(e);return(0,c.__decorate)([(0,d.MZ)({attribute:!1})],t.prototype,"hass",void 0),t}},13295:function(e,t,r){var o,i,n,a=r(44734),s=r(56038),l=r(69683),c=r(6454),d=(r(28706),r(62062),r(18111),r(61701),r(26099),r(62826)),u=r(96196),h=r(77845),p=(r(17963),e=>e),f=function(e){function t(){var e;(0,a.A)(this,t);for(var r=arguments.length,o=new Array(r),i=0;i<r;i++)o[i]=arguments[i];return(e=(0,l.A)(this,t,[].concat(o))).warnings=[],e}return(0,c.A)(t,e),(0,s.A)(t,[{key:"render",value:function(){return(0,u.qy)(o||(o=p`
      <ha-alert
        alert-type="warning"
        .title=${0}
      >
        ${0}
        ${0}
      </ha-alert>
    `),this.alertTitle||this.localize("ui.errors.config.editor_not_supported"),this.warnings.length&&void 0!==this.warnings[0]?(0,u.qy)(i||(i=p`<ul>
              ${0}
            </ul>`),this.warnings.map((e=>(0,u.qy)(n||(n=p`<li>${0}</li>`),e)))):u.s6,this.localize("ui.errors.config.edit_in_yaml_supported"))}}])}(u.WF);(0,d.__decorate)([(0,h.MZ)({attribute:!1})],f.prototype,"localize",void 0),(0,d.__decorate)([(0,h.MZ)({attribute:"alert-title"})],f.prototype,"alertTitle",void 0),(0,d.__decorate)([(0,h.MZ)({attribute:!1})],f.prototype,"warnings",void 0),f=(0,d.__decorate)([(0,h.EM)("ha-automation-editor-warning")],f)},78232:function(e,t,r){r.d(t,{g:function(){return a},u:function(){return i}});r(23792),r(26099),r(3362),r(62953);var o=r(92542),i="__paste__",n=()=>Promise.all([r.e("7115"),r.e("3464"),r.e("5706"),r.e("9341")]).then(r.bind(r,53468)),a=(e,t)=>{(0,o.r)(e,"show-dialog",{dialogTag:"add-automation-element-dialog",dialogImport:n,dialogParams:t})}},20897:function(e,t,r){r.d(t,{V:function(){return i},b:function(){return n}});var o=r(96685),i=(0,o.Ik)({trigger:(0,o.Yj)(),id:(0,o.lq)((0,o.Yj)()),enabled:(0,o.lq)((0,o.zM)())}),n=(0,o.Ik)({days:(0,o.lq)((0,o.ai)()),hours:(0,o.lq)((0,o.ai)()),minutes:(0,o.lq)((0,o.ai)()),seconds:(0,o.lq)((0,o.ai)())})},36857:function(e,t,r){r.d(t,{Ju:function(){return v},Lt:function(){return m},aM:function(){return y},bH:function(){return p},yj:function(){return f}});var o,i,n,a,s,l,c,d,u=r(96196),h=e=>e,p=(0,u.AH)(o||(o=h`
  ha-icon-button {
    --mdc-theme-text-primary-on-background: var(--primary-text-color);
  }
  ha-expansion-panel {
    --expansion-panel-summary-padding: 0 0 0 8px;
    --expansion-panel-content-padding: 0;
  }
  h3 {
    font-size: inherit;
    font-weight: inherit;
  }

  ha-card {
    transition: outline 0.2s;
  }
  .disabled-bar {
    background: var(--divider-color, #e0e0e0);
    text-align: center;
    border-top-right-radius: var(
      --ha-card-border-radius,
      var(--ha-border-radius-lg)
    );
    border-top-left-radius: var(
      --ha-card-border-radius,
      var(--ha-border-radius-lg)
    );
  }
  .warning ul {
    margin: 4px 0;
  }
  ha-md-menu-item > ha-svg-icon {
    --mdc-icon-size: 24px;
  }
  ha-tooltip {
    cursor: default;
  }
  .hidden {
    display: none;
  }
`)),f=(0,u.AH)(i||(i=h`
  .disabled {
    pointer-events: none;
  }

  .card-content.card {
    padding: 16px;
  }
  .card-content.yaml {
    padding: 0 1px;
    border-top: 1px solid var(--divider-color);
    border-bottom: 1px solid var(--divider-color);
  }
`)),y=(0,u.AH)(n||(n=h`
  .card-content.indent,
  .selector-row,
  :host([indent]) ha-form {
    margin-inline-start: 12px;
    padding-top: 12px;
    padding-bottom: 16px;
    padding-inline-start: 16px;
    padding-inline-end: 0px;
    border-inline-start: 2px solid var(--ha-color-border-neutral-quiet);
    border-bottom: 2px solid var(--ha-color-border-neutral-quiet);
    border-radius: var(--ha-border-radius-square);
    border-end-start-radius: var(--ha-border-radius-lg);
  }
  .card-content.indent.selected,
  :host([selected]) .card-content.indent,
  .selector-row.parent-selected,
  :host([selected]) ha-form {
    border-color: var(--primary-color);
    background: var(--ha-color-fill-primary-quiet-resting);
    background: linear-gradient(
      to right,
      var(--ha-color-fill-primary-quiet-resting) 0%,
      var(--ha-color-fill-primary-quiet-resting) 80%,
      rgba(var(--rgb-primary-color), 0) 100%
    );
  }
`)),v=((0,u.AH)(a||(a=h`
  :host {
    overflow: hidden;
  }
  ha-fab {
    position: absolute;
    right: calc(16px + var(--safe-area-inset-right, 0px));
    bottom: calc(-80px - var(--safe-area-inset-bottom));
    transition: bottom 0.3s;
  }
  ha-fab.dirty {
    bottom: calc(16px + var(--safe-area-inset-bottom, 0px));
  }
`)),(0,u.AH)(s||(s=h`
  :host {
    display: block;
    --sidebar-width: 0;
    --sidebar-gap: 0;
  }

  .has-sidebar {
    --sidebar-width: min(
      max(var(--sidebar-dynamic-width), ${0}px),
      100vw - ${0}px - var(--mdc-drawer-width, 0px),
      var(--ha-automation-editor-max-width) -
        ${0}px - var(--mdc-drawer-width, 0px)
    );
    --sidebar-gap: var(--ha-space-4);
  }

  .fab-positioner {
    display: flex;
    justify-content: flex-end;
  }

  .fab-positioner ha-fab {
    position: fixed;
    right: unset;
    left: unset;
    bottom: calc(-80px - var(--safe-area-inset-bottom));
    transition: bottom 0.3s;
  }
  .fab-positioner ha-fab.dirty {
    bottom: calc(16px + var(--safe-area-inset-bottom, 0px));
  }

  .content-wrapper {
    padding-right: calc(var(--sidebar-width) + var(--sidebar-gap));
    padding-inline-end: calc(var(--sidebar-width) + var(--sidebar-gap));
    padding-inline-start: 0;
  }

  .content {
    padding-top: 24px;
    padding-bottom: max(var(--safe-area-inset-bottom), 32px);
    transition: padding-bottom 180ms ease-in-out;
  }

  .content.has-bottom-sheet {
    padding-bottom: calc(90vh - max(var(--safe-area-inset-bottom), 32px));
  }

  ha-automation-sidebar {
    position: fixed;
    top: calc(var(--header-height) + 16px);
    height: calc(-81px + 100vh - var(--safe-area-inset-top, 0px));
    height: calc(-81px + 100dvh - var(--safe-area-inset-top, 0px));
    width: var(--sidebar-width);
    display: block;
  }

  ha-automation-sidebar.hidden {
    display: none;
  }

  .sidebar-positioner {
    display: flex;
    justify-content: flex-end;
  }

  .description {
    margin: 0;
  }
  .header a {
    color: var(--secondary-text-color);
  }
`),375,350,350),(0,u.AH)(l||(l=h`
  .rows {
    display: flex;
    flex-direction: column;
    gap: var(--ha-space-4);
  }
  .rows.no-sidebar {
    margin-inline-end: 0;
  }
  .sortable-ghost {
    background: none;
    border-radius: var(--ha-card-border-radius, var(--ha-border-radius-lg));
  }
  .sortable-drag {
    background: none;
  }
  ha-automation-action-row {
    display: block;
    scroll-margin-top: 48px;
  }
  .handle {
    padding: 4px;
    cursor: move; /* fallback if grab cursor is unsupported */
    cursor: grab;
    border-radius: var(--ha-border-radius-pill);
  }
  .handle:focus {
    outline: var(--wa-focus-ring);
    background: var(--ha-color-fill-neutral-quiet-resting);
  }
  .handle.active {
    outline: var(--wa-focus-ring);
    background: var(--ha-color-fill-neutral-normal-active);
  }
  .handle ha-svg-icon {
    pointer-events: none;
    height: 24px;
  }
  .buttons {
    display: flex;
    flex-wrap: wrap;
    gap: var(--ha-space-2);
    order: 1;
  }
`))),m=((0,u.AH)(c||(c=h`
  .sidebar-editor {
    display: block;
    padding-top: 8px;
  }
  .description {
    padding-top: 16px;
  }
`)),(0,u.AH)(d||(d=h`
  .overflow-label {
    display: flex;
    justify-content: space-between;
    gap: var(--ha-space-3);
    white-space: nowrap;
  }
  .overflow-label .shortcut {
    --mdc-icon-size: 12px;
    display: inline-flex;
    flex-direction: row;
    align-items: center;
    gap: 2px;
  }
  .overflow-label .shortcut span {
    font-size: var(--ha-font-size-s);
    font-family: var(--ha-font-family-code);
    color: var(--ha-color-text-secondary);
  }
  .shortcut-placeholder {
    display: inline-block;
    width: 60px;
  }
  .shortcut-placeholder.mac {
    width: 46px;
  }
  @media all and (max-width: 870px) {
    .shortcut-placeholder {
      display: none;
    }
  }
  ha-md-menu-item {
    --mdc-icon-size: 24px;
  }
`)))},76681:function(e,t,r){r.d(t,{MR:function(){return o},a_:function(){return i},bg:function(){return n}});var o=e=>`https://brands.home-assistant.io/${e.brand?"brands/":""}${e.useFallback?"_/":""}${e.domain}/${e.darkOptimized?"dark_":""}${e.type}.png`,i=e=>e.split("/")[4],n=e=>e.startsWith("https://brands.home-assistant.io/")},62001:function(e,t,r){r.d(t,{o:function(){return o}});r(74423);var o=(e,t)=>`https://${e.config.version.includes("b")?"rc":e.config.version.includes("dev")?"next":"www"}.home-assistant.io${t}`},98315:function(e,t,r){r.d(t,{c:function(){return o}});r(27495),r(90906);var o=/Mac/i.test(navigator.userAgent)},4848:function(e,t,r){r.d(t,{P:function(){return i}});var o=r(92542),i=(e,t)=>(0,o.r)(e,"hass-notification",t)}}]);
//# sourceMappingURL=9069.550a6317b368168f.js.map