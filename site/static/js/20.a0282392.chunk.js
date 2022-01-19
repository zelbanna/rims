(this.webpackJsonprims=this.webpackJsonprims||[]).push([[20],{51:function(t,e,n){"use strict";n.r(e),n.d(e,"List",(function(){return f})),n.d(e,"Report",(function(){return O}));var i=n(19),a=n(10),s=n(5),r=n(6),c=n(8),d=n(7),o=n(3),u=n(14),v=n(15),h=n(21),j=n(16),l=n(0),f=function(t){Object(c.a)(n,t);var e=Object(d.a)(n);function n(t){var i;return Object(s.a)(this,n),(i=e.call(this,t)).extendItem=function(t,e,n){Object(u.d)("api/reservation/extend",{device_id:t,user_id:e,days:n}).then((function(t){return i.componentDidMount()}))},i.deleteItem=function(t,e){return window.confirm("Remove reservation?")&&Object(u.d)("api/reservation/delete",{device_id:t,user_id:e}).then((function(e){e.deleted&&(i.setState({data:i.state.data.filter((function(e){return e.device_id!==t}))}),i.changeContent(null))}))},i.listItem=function(t){var e=i.context.settings.id===t.user_id||!t.valid;return[t.alias,t.hostname,t.end,Object(l.jsxs)(l.Fragment,{children:[e&&Object(l.jsx)(h.InfoButton,{onClick:function(){i.changeContent(Object(l.jsx)(b,{device_id:t.device_id,user_id:t.user_id},"rsv_device_"+t.device_id))},title:"Info"},"info"),e&&Object(l.jsx)(h.AddButton,{onClick:function(){i.extendItem(t.device_id,t.user_id,14)},title:"Extend reservation"},"ext"),e&&Object(l.jsx)(h.DeleteButton,{onClick:function(){i.deleteItem(t.device_id,t.user_id)},title:"Remove reservation"},"del")]})]},i.state={},i}return Object(r.a)(n,[{key:"componentDidMount",value:function(){var t=this;Object(u.d)("api/reservation/list").then((function(e){return t.setState(e)}))}},{key:"render",value:function(){var t=this;return Object(l.jsxs)(l.Fragment,{children:[Object(l.jsxs)(v.ContentList,{header:"Reservations",thead:["User","Device","Until",""],trows:this.state.data,listItem:this.listItem,children:[Object(l.jsx)(h.ReloadButton,{onClick:function(){return t.componentDidMount()}},"reload"),Object(l.jsx)(h.AddButton,{onClick:function(){return t.changeContent(Object(l.jsx)(x,{},"rsv_new"))}},"add")]},"cl"),Object(l.jsx)(v.ContentData,{mountUpdate:function(e){return t.changeContent=e}},"cda")]})}}]),n}(o.Component);f.contextType=v.RimsContext;var b=function(t){Object(c.a)(n,t);var e=Object(d.a)(n);function n(t){var r;return Object(s.a)(this,n),(r=e.call(this,t)).onChange=function(t){return r.setState({data:Object(a.a)(Object(a.a)({},r.state.data),{},Object(i.a)({},t.target.name,t.target.value))})},r.updateInfo=function(){return Object(u.d)("api/reservation/info",Object(a.a)({op:"update"},r.state.data)).then((function(t){return r.setState(t)}))},r.extendItem=function(t){Object(u.d)("api/reservation/extend",{device_id:r.state.data.device_id,user_id:r.state.data.user_id,days:t}).then((function(t){return"OK"===t.status&&r.componentDidMount()}))},r.state={data:null,found:!0},r}return Object(r.a)(n,[{key:"componentDidMount",value:function(){var t=this;Object(u.d)("api/reservation/info",{device_id:this.props.device_id}).then((function(e){return t.setState(e)}))}},{key:"render",value:function(){var t=this;return this.state.data?Object(l.jsxs)(v.InfoArticle,{header:"Reservation",children:[Object(l.jsxs)(v.InfoColumns,{children:[Object(l.jsx)(j.TextLine,{id:"alias",text:this.state.data.alias},"alias"),Object(l.jsx)(j.TextLine,{id:"Start",text:this.state.data.time_start},"time_start"),Object(l.jsx)(j.TextLine,{id:"End",text:this.state.data.time_end},"time_end"),Object(l.jsx)(j.RadioInput,{id:"shutdown",value:this.state.data.shutdown,options:[{text:"no",value:"no"},{text:"yes",value:"yes"},{text:"reset",value:"reset"}],onChange:this.onChange},"shutdown"),Object(l.jsx)(j.TextInput,{id:"info",value:this.state.data.info,onChange:this.onChange},"info")]},"reservation_content"),this.state.data.user_id===this.context.settings.id&&Object(l.jsx)(h.SaveButton,{onClick:function(){return t.updateInfo()},title:"Save"},"rsv_btn_save"),this.state.data.user_id===this.context.settings.id&&Object(l.jsx)(h.AddButton,{onClick:function(){return t.extendItem(14)},title:"Extend"},"rsv_btn_extend")]},"rsv_article"):Object(l.jsx)(v.Spinner,{})}}]),n}(o.Component);b.contextType=v.RimsContext;var x=function(t){Object(c.a)(n,t);var e=Object(d.a)(n);function n(t){var i;return Object(s.a)(this,n),(i=e.call(this,t)).onChange=function(t){i.setState({device:t.target.value})},i.findDevice=function(){return Object(u.d)("api/device/search",{hostname:i.state.device}).then((function(t){return t.found&&i.setState({device_id:t.data.id,matching:t.data.hostname})}))},i.reserveDevice=function(){return Object(u.d)("api/reservation/new",{device_id:i.state.device_id,user_id:i.context.settings.id}).then((function(t){return"OK"===t.status&&i.setState({device:"",device_id:void 0,matching:""})}))},i.state={device:"",device_id:void 0,matching:""},i}return Object(r.a)(n,[{key:"render",value:function(){var t=this;return Object(l.jsxs)(v.LineArticle,{header:"New reservation",children:[Object(l.jsx)(j.TextInput,{id:"device",label:"Search device",onChange:this.onChange,value:this.state.device,placeholder:"search"},"device")," found ",Object(l.jsx)(j.TextLine,{id:"matching device",text:this.state.matching},"matching"),this.state.device&&Object(l.jsx)(h.SearchButton,{onClick:function(){return t.findDevice()},title:"Find device"},"rsv_btn_search"),this.state.device_id&&Object(l.jsx)(h.AddButton,{onClick:function(){return t.reserveDevice()},title:"Reserve device"},"rsv_btn_new")]},"rsv_art")}}]),n}(o.Component);x.contextType=v.RimsContext;var O=function(t){Object(c.a)(n,t);var e=Object(d.a)(n);function n(t){var i;return Object(s.a)(this,n),(i=e.call(this,t)).listItem=function(t){return[t.alias,t.hostname,t.start,t.end,t.info]},i.state={},i}return Object(r.a)(n,[{key:"componentDidMount",value:function(){var t=this;Object(u.d)("api/reservation/list",{extended:!0}).then((function(e){return t.setState(e)}))}},{key:"render",value:function(){return Object(l.jsx)(v.ContentReport,{header:"Reservations",thead:["User","Device","Start","End","Info"],trows:this.state.data,listItem:this.listItem},"rsv_cr")}}]),n}(o.Component)}}]);
//# sourceMappingURL=20.a0282392.chunk.js.map