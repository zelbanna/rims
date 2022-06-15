(this.webpackJsonprims=this.webpackJsonprims||[]).push([[13],{43:function(t,e,n){"use strict";n.r(e),n.d(e,"Main",(function(){return O})),n.d(e,"DomainList",(function(){return b}));var i=n(20),a=n(19),r=n(10),o=n(5),s=n(6),c=n(8),d=n(7),u=n(3),l=n(14),j=n(15),h=n(16),p=n(21),f=n(0),O=function(t){Object(c.a)(n,t);var e=Object(d.a)(n);function n(){var t;Object(o.a)(this,n);for(var i=arguments.length,a=new Array(i),r=0;r<i;r++)a[r]=arguments[r];return(t=e.call.apply(e,[this].concat(a))).changeContent=function(e){return t.setState(e)},t}return Object(s.a)(n,[{key:"componentDidMount",value:function(){this.setState(Object(f.jsx)(b,{},"domain_list"))}},{key:"render",value:function(){return Object(f.jsx)(f.Fragment,{children:this.state})}}]),n}(u.Component),b=function(t){Object(c.a)(n,t);var e=Object(d.a)(n);function n(t){var i;return Object(o.a)(this,n),(i=e.call(this,t)).listItem=function(t){return[t.id,t.name,t.service,Object(f.jsxs)(f.Fragment,{children:[Object(f.jsx)(p.ConfigureButton,{onClick:function(){return i.changeContent(Object(f.jsx)(m,{id:t.id},"domain_info"))},title:"Edit domain information"},"info"),Object(f.jsx)(p.ItemsButton,{onClick:function(){return i.changeContent(Object(f.jsx)(x,{changeSelf:i.changeContent,domain_id:t.id},"record_list"))},title:"View domain records"},"items"),Object(f.jsx)(p.DeleteButton,{onClick:function(){return i.deleteList(t.id)},title:"Delete domain"},"del")]})]},i.changeContent=function(t){return i.setState({content:t})},i.deleteList=function(t){return window.confirm("Really delete domain")&&Object(l.d)("api/dns/domain_delete",{id:t}).then((function(e){e.deleted&&(i.setState({data:i.state.data.filter((function(e){return e.id!==t}))}),i.changeContent(null))}))},i.state={},i}return Object(s.a)(n,[{key:"componentDidMount",value:function(){var t=this;Object(l.d)("api/dns/domain_list").then((function(e){e.result="OK",t.setState(e)}))}},{key:"syncDomains",value:function(){var t=this;Object(l.d)("api/dns/domain_list",{sync:!0}).then((function(e){e.result="NS:"+e.ns.status+", Recursors:"+e.rec.status,t.setState(e)}))}},{key:"render",value:function(){var t=this;return Object(f.jsxs)(f.Fragment,{children:[Object(f.jsxs)(j.ContentList,{header:"Domains",thead:["ID","Domain","Server",""],trows:this.state.data,listItem:this.listItem,result:this.state.result,children:[Object(f.jsx)(p.ReloadButton,{onClick:function(){return t.componentDidMount()}},"reload"),Object(f.jsx)(p.AddButton,{onClick:function(){return t.changeContent(Object(f.jsx)(m,{id:"new"},"domain_info"))},title:"Add domain"},"add"),Object(f.jsx)(p.SyncButton,{onClick:function(){return t.syncDomains()},title:"Sync external DNS servers with cache"},"sync"),Object(f.jsx)(p.HealthButton,{onClick:function(){return t.changeContent(Object(f.jsx)(v,{},"recursor_statistics"))},title:"View DNS statistics"},"stats")]},"cl"),Object(f.jsx)(j.ContentData,{mountUpdate:function(e){return t.changeContent=e}},"cda")]})}}]),n}(u.Component),m=function(t){Object(c.a)(n,t);var e=Object(d.a)(n);function n(t){var i;return Object(o.a)(this,n),(i=e.call(this,t)).onChange=function(t){return i.setState({data:Object(r.a)(Object(r.a)({},i.state.data),{},Object(a.a)({},t.target.name,t.target.value))})},i.changeContent=function(t){return i.setState({content:t})},i.updateInfo=function(){return Object(l.d)("api/dns/domain_info",Object(r.a)({op:"update"},i.state.data)).then((function(t){return i.setState(t)}))},i.state={data:null},i}return Object(s.a)(n,[{key:"componentDidUpdate",value:function(t){t!==this.props&&this.componentDidMount()}},{key:"componentDidMount",value:function(){var t=this;Object(l.d)("api/dns/domain_info",{id:this.props.id}).then((function(e){return t.setState(e)}))}},{key:"render",value:function(){var t=this;if(this.state.data){var e="new"!==this.state.data.id;return Object(f.jsxs)(j.InfoArticle,{header:"Domain",children:[Object(f.jsxs)(j.InfoColumns,{children:[e&&Object(f.jsx)(h.TextLine,{id:"node",text:this.state.infra.node},"node"),e&&Object(f.jsx)(h.TextLine,{id:"service",text:this.state.infra.service},"service"),e&&Object(f.jsx)(h.TextLine,{id:"foreign_id",label:"Foreign ID",text:this.state.infra.foreign_id},"foreign_id"),!e&&Object(f.jsx)(h.SelectInput,{id:"server_id",label:"Server",value:this.state.data.server_id,onChange:this.onChange,children:this.state.servers.map((function(t,e){return Object(f.jsx)("option",{value:t.id,children:"".concat(t.service,"@").concat(t.node)},"srv_"+e)}))},"server_id"),Object(f.jsx)(h.TextInput,{id:"name",value:this.state.data.name,onChange:this.onChange},"name"),Object(f.jsx)(h.TextInput,{id:"master",value:this.state.data.master,onChange:this.onChange},"master"),Object(f.jsx)(h.TextInput,{id:"type",value:this.state.data.type,onChange:this.onChange},"type"),Object(f.jsx)(h.TextLine,{id:"serial",text:this.state.data.serial},"serial")]},"ic"),Object(f.jsx)(p.SaveButton,{onClick:function(){return t.updateInfo()},title:"Save domain information"},"save")]},"ia_dom")}return Object(f.jsx)(j.Spinner,{})}}]),n}(u.Component),v=function(t){Object(c.a)(n,t);var e=Object(d.a)(n);function n(t){var i;return Object(o.a)(this,n),(i=e.call(this,t)).state={},i}return Object(s.a)(n,[{key:"componentDidMount",value:function(){var t=this;Object(l.d)("api/dns/statistics").then((function(e){for(var n=[],a=function(){var t=Object(i.a)(o[r],2),e=t[0],a=t[1],s=e.split("_");a.forEach((function(t){return n.push([s[0],s[1],t[0],t[1],t[2]])}))},r=0,o=Object.entries(e.queries);r<o.length;r++)a();for(var s=[],c=function(){var t=Object(i.a)(u[d],2),e=t[0],n=t[1],a=e.split("_");n.forEach((function(t){return s.push([a[0],a[1],t[0],t[1]])}))},d=0,u=Object.entries(e.remotes);d<u.length;d++)c();t.setState({queries:n,remotes:s})}))}},{key:"render",value:function(){return this.state.queries&&this.state.remotes?Object(f.jsxs)(j.Flex,{children:[Object(f.jsx)(j.ContentReport,{header:"Looked up FQDN",thead:["Node","Service","Hits","FQDN","Type"],trows:this.state.queries,listItem:function(t){return t}},"queries_cr"),Object(f.jsx)(j.ContentReport,{header:"Queriers",thead:["Node","Service","Hits","Who"],trows:this.state.remotes,listItem:function(t){return t}},"remotes_cr")]},"statistics_flex"):Object(f.jsx)(j.Spinner,{})}}]),n}(u.Component),x=function(t){Object(c.a)(n,t);var e=Object(d.a)(n);function n(t){var i;return Object(o.a)(this,n),(i=e.call(this,t)).changeContent=function(t){return i.props.changeSelf(t)},i.listItem=function(t){return[t.name,t.content,t.type,t.ttl,Object(f.jsxs)(f.Fragment,{children:[Object(f.jsx)(p.ConfigureButton,{onClick:function(){return i.changeContent(Object(f.jsx)(C,Object(r.a)({domain_id:i.props.domain_id,op:"info"},t),"record_info"))},title:"Configure record"},"info"),["A","AAAA","CNAME","PTR"].includes(t.type)&&Object(f.jsx)(p.DeleteButton,{onClick:function(){return i.deleteList(t.name,t.type)},title:"Delete record"},"del")]})]},i.deleteList=function(t,e){return window.confirm("Delete record?")&&Object(l.d)("api/dns/record_delete",{domain_id:i.props.domain_id,name:t,type:e}).then((function(n){return n.deleted&&i.setState({data:i.state.data.filter((function(n){return!(n.name===t&&n.type===e)}))})}))},i.state={},i}return Object(s.a)(n,[{key:"componentDidUpdate",value:function(t){t!==this.props&&this.componentDidMount()}},{key:"componentDidMount",value:function(){var t=this;Object(l.d)("api/dns/record_list",{domain_id:this.props.domain_id}).then((function(e){return t.setState(e)}))}},{key:"render",value:function(){var t=this,e=this.state.status;if(e){if("OK"===e){var n=this.state.data;return Object(f.jsxs)(j.ContentReport,{header:"Records",thead:["Name","Content","Type","TTL",""],trows:n,listItem:this.listItem,result:this.state.result,children:[Object(f.jsx)(p.ReloadButton,{onClick:function(){return t.componentDidMount()}},"reload"),Object(f.jsx)(p.AddButton,{onClick:function(){return t.changeContent(Object(f.jsx)(C,{domain_id:t.props.domain_id,name:"new",op:"new"},"record_info"))},title:"Add DNS record"},"add")]},"rl_cr")}return Object(f.jsxs)(j.CodeArticle,{children:["Error retrieving record list: ",JSON.stringify(this.state.info)]},"ca_rl")}return Object(f.jsx)(j.Spinner,{})}}]),n}(u.Component),C=function(t){Object(c.a)(n,t);var e=Object(d.a)(n);function n(t){var i;return Object(o.a)(this,n),(i=e.call(this,t)).onChange=function(t){return i.setState({data:Object(r.a)(Object(r.a)({},i.state.data),{},Object(a.a)({},t.target.name,t.target.value))})},i.updateInfo=function(){return Object(l.d)("api/dns/record_info",Object(r.a)({op:i.state.op},i.state.data)).then((function(t){i.setState(Object(r.a)({op:"OK"===t.status?"update":i.state.op},t))}))},i.state={data:null,info:void 0},"info"===i.props.op?(i.state.data={domain_id:i.props.domain_id,name:i.props.name,type:i.props.type,ttl:i.props.ttl,content:i.props.content},i.state.op="update"):(i.state.data={domain_id:i.props.domain_id,name:"",type:"A",ttl:3600,content:""},i.state.op="insert"),i}return Object(s.a)(n,[{key:"render",value:function(){var t=this;return this.state.data?Object(f.jsxs)(j.InfoArticle,{header:"Record",children:[Object(f.jsxs)(j.InfoColumns,{children:[Object(f.jsx)(h.TextInput,{id:"name",value:this.state.data.name,title:"E.g. A:FQDN, PTR:x.y.z.in-addr.arpa",onChange:this.onChange,placeholder:"name"},"name"),Object(f.jsx)(h.TextInput,{id:"type",value:this.state.data.type,onChange:this.onChange,placeholder:"A, PTR or CNAME typically"},"type"),Object(f.jsx)(h.TextInput,{id:"ttl",label:"TTL",value:this.state.data.ttl,onChange:this.onChange},"ttl"),Object(f.jsx)(h.TextInput,{id:"content",value:this.state.data.content,title:"E.g. A:IP, PTR:x.y.x-inaddr.arpa, CNAME:A - remember dot on PTR/CNAME",onChange:this.onChange,placeholder:"content"},"content"),this.props.serial&&Object(f.jsx)(h.TextLine,{id:"serial",text:this.props.serial},"serial")]},"ic"),Object(f.jsx)(p.SaveButton,{onClick:function(){return t.updateInfo()},title:"Save record information"},"save"),Object(f.jsx)(j.Result,{result:"OK"!==this.state.status?JSON.stringify(this.state.info):"OK"},"result")]},"rec_art"):Object(f.jsx)(j.Spinner,{})}}]),n}(u.Component)}}]);
//# sourceMappingURL=13.64228b9d.chunk.js.map