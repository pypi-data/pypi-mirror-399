"use strict";(self.webpackChunkknx_frontend=self.webpackChunkknx_frontend||[]).push([["2389"],{55124:function(e,t,i){i.d(t,{d:function(){return a}});var a=e=>e.stopPropagation()},33464:function(e,t,i){var a,s=i(44734),o=i(56038),n=i(69683),r=i(6454),d=(i(28706),i(2892),i(62826)),l=i(96196),u=i(77845),h=i(92542),c=(i(29261),e=>e),p=function(e){function t(){var e;(0,s.A)(this,t);for(var i=arguments.length,a=new Array(i),o=0;o<i;o++)a[o]=arguments[o];return(e=(0,n.A)(this,t,[].concat(a))).required=!1,e.enableMillisecond=!1,e.enableDay=!1,e.disabled=!1,e}return(0,r.A)(t,e),(0,o.A)(t,[{key:"render",value:function(){return(0,l.qy)(a||(a=c`
      <ha-base-time-input
        .label=${0}
        .helper=${0}
        .required=${0}
        .clearable=${0}
        .autoValidate=${0}
        .disabled=${0}
        errorMessage="Required"
        enable-second
        .enableMillisecond=${0}
        .enableDay=${0}
        format="24"
        .days=${0}
        .hours=${0}
        .minutes=${0}
        .seconds=${0}
        .milliseconds=${0}
        @value-changed=${0}
        no-hours-limit
        day-label="dd"
        hour-label="hh"
        min-label="mm"
        sec-label="ss"
        ms-label="ms"
      ></ha-base-time-input>
    `),this.label,this.helper,this.required,!this.required&&void 0!==this.data,this.required,this.disabled,this.enableMillisecond,this.enableDay,this._days,this._hours,this._minutes,this._seconds,this._milliseconds,this._durationChanged)}},{key:"_days",get:function(){var e;return null!==(e=this.data)&&void 0!==e&&e.days?Number(this.data.days):this.required||this.data?0:NaN}},{key:"_hours",get:function(){var e;return null!==(e=this.data)&&void 0!==e&&e.hours?Number(this.data.hours):this.required||this.data?0:NaN}},{key:"_minutes",get:function(){var e;return null!==(e=this.data)&&void 0!==e&&e.minutes?Number(this.data.minutes):this.required||this.data?0:NaN}},{key:"_seconds",get:function(){var e;return null!==(e=this.data)&&void 0!==e&&e.seconds?Number(this.data.seconds):this.required||this.data?0:NaN}},{key:"_milliseconds",get:function(){var e;return null!==(e=this.data)&&void 0!==e&&e.milliseconds?Number(this.data.milliseconds):this.required||this.data?0:NaN}},{key:"_durationChanged",value:function(e){e.stopPropagation();var t,i=e.detail.value?Object.assign({},e.detail.value):void 0;i&&(i.hours||(i.hours=0),i.minutes||(i.minutes=0),i.seconds||(i.seconds=0),"days"in i&&(i.days||(i.days=0)),"milliseconds"in i&&(i.milliseconds||(i.milliseconds=0)),this.enableMillisecond||i.milliseconds?i.milliseconds>999&&(i.seconds+=Math.floor(i.milliseconds/1e3),i.milliseconds%=1e3):delete i.milliseconds,i.seconds>59&&(i.minutes+=Math.floor(i.seconds/60),i.seconds%=60),i.minutes>59&&(i.hours+=Math.floor(i.minutes/60),i.minutes%=60),this.enableDay&&i.hours>24&&(i.days=(null!==(t=i.days)&&void 0!==t?t:0)+Math.floor(i.hours/24),i.hours%=24));(0,h.r)(this,"value-changed",{value:i})}}])}(l.WF);(0,d.__decorate)([(0,u.MZ)({attribute:!1})],p.prototype,"data",void 0),(0,d.__decorate)([(0,u.MZ)()],p.prototype,"label",void 0),(0,d.__decorate)([(0,u.MZ)()],p.prototype,"helper",void 0),(0,d.__decorate)([(0,u.MZ)({type:Boolean})],p.prototype,"required",void 0),(0,d.__decorate)([(0,u.MZ)({attribute:"enable-millisecond",type:Boolean})],p.prototype,"enableMillisecond",void 0),(0,d.__decorate)([(0,u.MZ)({attribute:"enable-day",type:Boolean})],p.prototype,"enableDay",void 0),(0,d.__decorate)([(0,u.MZ)({type:Boolean})],p.prototype,"disabled",void 0),p=(0,d.__decorate)([(0,u.EM)("ha-duration-input")],p)},19797:function(e,t,i){i.r(t),i.d(t,{HaFormTimePeriod:function(){return c}});var a,s=i(44734),o=i(56038),n=i(69683),r=i(6454),d=(i(28706),i(62826)),l=i(96196),u=i(77845),h=(i(33464),e=>e),c=function(e){function t(){var e;(0,s.A)(this,t);for(var i=arguments.length,a=new Array(i),o=0;o<i;o++)a[o]=arguments[o];return(e=(0,n.A)(this,t,[].concat(a))).disabled=!1,e}return(0,r.A)(t,e),(0,o.A)(t,[{key:"focus",value:function(){this._input&&this._input.focus()}},{key:"render",value:function(){return(0,l.qy)(a||(a=h`
      <ha-duration-input
        .label=${0}
        ?required=${0}
        .data=${0}
        .disabled=${0}
      ></ha-duration-input>
    `),this.label,this.schema.required,this.data,this.disabled)}}])}(l.WF);(0,d.__decorate)([(0,u.MZ)({attribute:!1})],c.prototype,"schema",void 0),(0,d.__decorate)([(0,u.MZ)({attribute:!1})],c.prototype,"data",void 0),(0,d.__decorate)([(0,u.MZ)()],c.prototype,"label",void 0),(0,d.__decorate)([(0,u.MZ)({type:Boolean})],c.prototype,"disabled",void 0),(0,d.__decorate)([(0,u.P)("ha-time-input",!0)],c.prototype,"_input",void 0),c=(0,d.__decorate)([(0,u.EM)("ha-form-positive_time_period_dict")],c)},75261:function(e,t,i){var a=i(56038),s=i(44734),o=i(69683),n=i(6454),r=i(62826),d=i(70402),l=i(11081),u=i(77845),h=function(e){function t(){return(0,s.A)(this,t),(0,o.A)(this,t,arguments)}return(0,n.A)(t,e),(0,a.A)(t)}(d.iY);h.styles=l.R,h=(0,r.__decorate)([(0,u.EM)("ha-list")],h)}}]);
//# sourceMappingURL=2389.108c2890ace0e870.js.map