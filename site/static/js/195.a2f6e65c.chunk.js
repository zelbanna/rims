"use strict";(self.webpackChunkrims_frontend=self.webpackChunkrims_frontend||[]).push([[195],{195:function(t,e,n){n.r(e),n.d(e,{AddressInfo:function(){return g},Main:function(){return v},NetworkList:function(){return _}});var i=n(942),a=n(413),r=n(671),s=n(144),o=n(340),d=n(882),u=n(791),c=n(252),l=n(885),h=n(698),p=n(682),f=n(184),v=function(t){(0,o.Z)(n,t);var e=(0,d.Z)(n);function n(t){var i;return(0,r.Z)(this,n),(i=e.call(this,t)).changeContent=function(t){return i.setState(t)},i.state=(0,f.jsx)(_,{},"network_list"),i}return(0,s.Z)(n,[{key:"render",value:function(){return(0,f.jsx)(f.Fragment,{children:this.state})}}]),n}(u.Component),_=function(t){(0,o.Z)(n,t);var e=(0,d.Z)(n);function n(t){var i;return(0,r.Z)(this,n),(i=e.call(this,t)).listItem=function(t){return[t.id,t.netasc,t.description,t.service,(0,f.jsxs)(f.Fragment,{children:[(0,f.jsx)(p.ConfigureButton,{onClick:function(){return i.changeContent((0,f.jsx)(m,{id:t.id},"network_"+t.id))},title:"Edit network properties"},"conf"),(0,f.jsx)(p.ItemsButton,{onClick:function(){return i.changeContent((0,f.jsx)(C,{network_id:t.id,changeSelf:i.changeContent},"address_list_"+t.id))},title:"View addresses"},"items"),"v4"===t.class&&(0,f.jsx)(p.ViewButton,{onClick:function(){return i.changeContent((0,f.jsx)(x,{network_id:t.id,changeSelf:i.changeContent},"address_layout_"+t.id))},title:"View usage map"},"layout"),"v4"===t.class&&(0,f.jsx)(p.CheckButton,{onClick:function(){return i.changeContent((0,f.jsx)(w,{network_id:t.id,changeSelf:i.changeContent},"resv_list_"+t.id))},title:"Reserved addresses for network"},"resv"),(0,f.jsx)(p.DeleteButton,{onClick:function(){return i.deleteList(t.id)},title:"Delete network"},"del"),(0,f.jsx)(p.ReloadButton,{onClick:function(){return i.resetStatus(t.id)},title:"Reset state for network addresses"},"reset")]})]},i.deleteList=function(t){return window.confirm("Really delete network")&&(0,c.Fh)("api/ipam/network_delete",{id:t}).then((function(e){e.deleted&&(i.setState({data:i.state.data.filter((function(e){return e.id!==t}))}),i.changeContent(null))}))},i.resetStatus=function(t){return(0,c.Fh)("api/ipam/clear",{network_id:t}).then((function(t){return i.setState({result:t.count})}))},i.state={},i}return(0,s.Z)(n,[{key:"componentDidMount",value:function(){var t=this;(0,c.Fh)("api/ipam/network_list").then((function(e){return t.setState(e)}))}},{key:"render",value:function(){var t=this;return(0,f.jsxs)(f.Fragment,{children:[(0,f.jsxs)(l.ContentList,{header:"Networks",thead:["ID","Network","Description","DHCP",""],trows:this.state.data,listItem:this.listItem,result:this.state.result,children:[(0,f.jsx)(p.ReloadButton,{onClick:function(){return t.componentDidMount()}},"reload"),(0,f.jsx)(p.AddButton,{onClick:function(){return t.changeContent((0,f.jsx)(m,{id:"new"},"network_new_"+(0,c.P4)()))},title:"Add network"},"add"),(0,f.jsx)(p.LogButton,{onClick:function(){return t.changeContent((0,f.jsx)(k,{},"network_leases"))},title:"View IPAM/DHCP leases"},"leases")]},"cl"),(0,f.jsx)(l.ContentData,{mountUpdate:function(e){return t.changeContent=e}},"cda")]})}}]),n}(u.Component),m=function(t){(0,o.Z)(n,t);var e=(0,d.Z)(n);function n(t){var s;return(0,r.Z)(this,n),(s=e.call(this,t)).onChange=function(t){return s.setState({data:(0,a.Z)((0,a.Z)({},s.state.data),{},(0,i.Z)({},t.target.name,t.target.value))})},s.changeContent=function(t){return s.setState({content:t})},s.updateInfo=function(){return(0,c.Fh)("api/ipam/network_info",(0,a.Z)({op:"update"},s.state.data)).then((function(t){return s.setState(t)}))},s.state={data:null,found:!0},s}return(0,s.Z)(n,[{key:"componentDidMount",value:function(){var t=this;(0,c.Fh)("api/ipam/network_info",{id:this.props.id,extra:["servers","domains"]}).then((function(e){return t.setState(e)}))}},{key:"render",value:function(){var t=this;return this.state.data?(0,f.jsxs)(l.InfoArticle,{header:"Network",children:[(0,f.jsxs)(l.InfoColumns,{children:[(0,f.jsx)(h.TextLine,{id:"id",label:"ID",text:this.state.data.id},"id"),(0,f.jsx)(h.TextInput,{id:"description",value:this.state.data.description,onChange:this.onChange},"description"),(0,f.jsx)(h.TextInput,{id:"network",value:this.state.data.network,onChange:this.onChange},"network"),(0,f.jsx)(h.TextInput,{id:"mask",value:this.state.data.mask,onChange:this.onChange},"mask"),(0,f.jsx)(h.TextInput,{id:"gateway",value:this.state.data.gateway,onChange:this.onChange},"gateway"),(0,f.jsx)(h.SelectInput,{id:"server_id",label:"Server",value:this.state.data.server_id,onChange:this.onChange,children:this.state.servers.map((function(t,e){return(0,f.jsx)("option",{value:t.id,children:"".concat(t.service,"@").concat(t.node)},e)}))},"server_id"),(0,f.jsx)(h.SelectInput,{id:"reverse_zone_id",label:"Reverse Zone",value:this.state.data.reverse_zone_id,onChange:this.onChange,children:this.state.domains.map((function(t,e){return(0,f.jsx)("option",{value:t.id,children:"".concat(t.server," (").concat(t.name,")")},e)}))},"reverse_zone_id")]},"network_content"),(0,f.jsx)(p.SaveButton,{onClick:function(){return t.updateInfo()},title:"Save"},"network_btn_save")]},"net_article"):(0,f.jsx)(l.Spinner,{})}}]),n}(u.Component),x=function(t){(0,o.Z)(i,t);var e=(0,d.Z)(i);function i(){var t;(0,r.Z)(this,i);for(var a=arguments.length,s=new Array(a),o=0;o<a;o++)s[o]=arguments[o];return(t=e.call.apply(e,[this].concat(s))).changeContent=function(e){return t.props.changeSelf(e)},t.changeDevice=function(e){return n.e(531).then(n.bind(n,531)).then((function(n){return t.changeContent((0,f.jsx)(n.Info,{id:e},"di_"+e))}))},t.createDevice=function(e,i){return n.e(531).then(n.bind(n,531)).then((function(n){return t.changeContent((0,f.jsx)(n.New,{ipam_network_id:e,ip:i},"dn_new"))}))},t}return(0,s.Z)(i,[{key:"componentDidMount",value:function(){var t=this;(0,c.Fh)("api/ipam/address_list",{network_id:this.props.network_id,dict:"ip_integer",extra:["device_id","reservation","ip_integer"]}).then((function(e){return t.setState(e)}))}},{key:"render",value:function(){var t=this;if(this.state){for(var e=this.state.data,n=(0,c.$Y)(this.state.network),i=[],a=function(){var a=n+r;a in e?e[a].device_id?i.push((0,f.jsx)(p.IpamRedButton,{onClick:function(){return t.changeDevice(e[a].device_id)},text:r%256},"btn_"+a)):i.push((0,f.jsx)(p.IpamGreyButton,{text:r%256},"btn_"+a)):i.push((0,f.jsx)(p.IpamGreenButton,{onClick:function(){return t.createDevice(t.props.network_id,(0,c._v)(a))},text:r%256},"btn_"+a))},r=0;r<this.state.size;r++)a();return(0,f.jsx)(l.Article,{header:this.state.network+"/"+this.state.mask,children:i},"il_art")}return(0,f.jsx)(l.Spinner,{})}}]),i}(u.Component),k=function(t){(0,o.Z)(n,t);var e=(0,d.Z)(n);function n(t){var i;return(0,r.Z)(this,n),(i=e.call(this,t)).listItem=function(t){return[t.ip,t.mac,t.hostname,t.oui,t.starts,t.ends]},i.state={},i}return(0,s.Z)(n,[{key:"componentDidMount",value:function(){var t=this;(0,c.Fh)("api/ipam/server_leases",{type:"active"}).then((function(e){return t.setState(e)}))}},{key:"render",value:function(){return(0,f.jsx)(l.ContentReport,{header:"Leases",thead:["IP","Mac","Hostname","OUI","Starts","End"],trows:this.state.data,listItem:this.listItem},"lease_cr")}}]),n}(u.Component),C=function(t){(0,o.Z)(n,t);var e=(0,d.Z)(n);function n(t){var i;return(0,r.Z)(this,n),(i=e.call(this,t)).changeContent=function(t){return i.props.changeSelf(t)},i.listItem=function(t){return[t.id,t.ip,t.hostname,t.domain,(0,f.jsxs)(f.Fragment,{children:[(0,f.jsx)(l.StateLeds,{state:t.state},"state"),(0,f.jsx)(p.ConfigureButton,{onClick:function(){return i.changeContent((0,f.jsx)(g,{id:t.id,changeSelf:i.changeContent},"address_info_"+t.id))},title:"Edit address entry"},"info"),(0,f.jsx)(p.DeleteButton,{onClick:function(){return i.deleteList(t.id)},title:"Delete address entry"},"del")]})]},i.deleteList=function(t){return window.confirm("Delete address?")&&(0,c.Fh)("api/ipam/address_delete",{id:t}).then((function(e){return e.deleted&&i.setState({data:i.state.data.filter((function(e){return e.id!==t}))})}))},i.state={data:null,result:null},i}return(0,s.Z)(n,[{key:"componentDidMount",value:function(){var t=this;(0,c.Fh)("api/ipam/address_list",{network_id:this.props.network_id,extra:["hostname","a_domain_id","device_id"]}).then((function(e){return t.setState(e)}))}},{key:"render",value:function(){var t=this;return(0,f.jsxs)(l.ContentReport,{header:"Allocated IP Addresses",thead:["ID","IP","Hostname","Domain",""],trows:this.state.data,listItem:this.listItem,result:this.state.result,children:[(0,f.jsx)(p.ReloadButton,{onClick:function(){return t.componentDidMount()}},"al_btn_reload"),(0,f.jsx)(p.AddButton,{onClick:function(){return t.changeContent((0,f.jsx)(g,{network_id:t.props.network_id,id:"new"},"address_new_"+(0,c.P4)()))},title:"Add address entry"},"al_btn_add")]},"al_cr")}}]),n}(u.Component),g=function(t){(0,o.Z)(n,t);var e=(0,d.Z)(n);function n(t){var s;return(0,r.Z)(this,n),(s=e.call(this,t)).onChange=function(t){return s.setState({data:(0,a.Z)((0,a.Z)({},s.state.data),{},(0,i.Z)({},t.target.name,t.target.value))})},s.updateInfo=function(){s.setState({status:void 0}),(0,c.Fh)("api/ipam/address_info",(0,a.Z)({op:"update"},s.state.data)).then((function(t){return s.setState(t)}))},s.state={data:null},s}return(0,s.Z)(n,[{key:"componentDidMount",value:function(){var t=this;(0,c.Fh)("api/ipam/address_info",{id:this.props.id,network_id:this.props.network_id}).then((function(e){return t.setState(e)})),(0,c.Fh)("api/dns/domain_list",{filter:"forward"}).then((function(e){return t.setState({domains:e.data})}))}},{key:"render",value:function(){var t=this;if(this.state&&this.state.data&&this.state.domains){var e="";return this.state.status&&(e="OK"===this.state.status?"OK":this.state.info),(0,f.jsxs)(l.InfoArticle,{header:"IP Address",children:[(0,f.jsxs)(l.InfoColumns,{children:[(0,f.jsx)(h.TextLine,{id:"id",label:"ID",text:this.state.data.id},"id"),(0,f.jsx)(h.TextLine,{id:"network",text:this.state.extra.network},"network"),(0,f.jsx)(h.TextInput,{id:"ip",label:"IP",value:this.state.data.ip,onChange:this.onChange},"ip"),(0,f.jsx)(h.TextInput,{id:"hostname",value:this.state.data.hostname,onChange:this.onChange,title:"Hostname when creating FQDN for DNS entry"},"hostname"),(0,f.jsx)(h.SelectInput,{id:"a_domain_id",label:"Domain",value:this.state.data.a_domain_id,onChange:this.onChange,children:this.state.domains.map((function(t,e){return(0,f.jsx)("option",{value:t.id,children:t.name},e)}))},"a_domain_id")]},"ip_content"),(0,f.jsx)(p.SaveButton,{onClick:function(){return t.updateInfo()},title:"Save"},"ip_btn_save"),(0,f.jsx)(l.Result,{result:e},"ip_operation")]},"ip_article")}return(0,f.jsx)(l.Spinner,{})}}]),n}(u.Component),w=function(t){(0,o.Z)(n,t);var e=(0,d.Z)(n);function n(t){var i;return(0,r.Z)(this,n),(i=e.call(this,t)).deleteList=function(t){return(0,c.Fh)("api/ipam/reservation_delete",{id:t}).then((function(e){return e.deleted&&i.setState({data:i.state.data.filter((function(e){return e.id!==t}))})}))},i.listItem=function(t,e){return[t.ip,t.type,(0,f.jsx)(p.DeleteButton,{onClick:function(){return i.deleteList(t.id)}},"resv_list_delete_"+t.id)]},i.addEntry=function(){return i.props.changeSelf((0,f.jsx)(j,{network_id:i.props.network_id,changeSelf:i.props.changeSelf},"resv_new_"+i.props.network_id))},i.state={},i}return(0,s.Z)(n,[{key:"componentDidMount",value:function(){var t=this;(0,c.Fh)("api/ipam/reservation_list",{network_id:this.props.network_id}).then((function(e){return t.setState(e)}))}},{key:"render",value:function(){var t=this;return this.state.data?(0,f.jsx)(l.ContentReport,{header:"Reservations",thead:["IP","Type",""],trows:this.state.data,listItem:this.listItem,children:(0,f.jsx)(p.AddButton,{onClick:function(){return t.addEntry()}},"resv_list_add_btn")},"resv_list_"+this.props.server_id):(0,f.jsx)(l.Spinner,{})}}]),n}(u.Component),j=function(t){(0,o.Z)(n,t);var e=(0,d.Z)(n);function n(t){var a;return(0,r.Z)(this,n),(a=e.call(this,t)).onChange=function(t){return a.setState((0,i.Z)({},t.target.name,t.target.value))},a.updateInfo=function(){return(0,c.Fh)("api/ipam/reservation_new",{network_id:a.props.network_id,ip:a.state.ip,type:a.state.type,a_domain_id:a.state.a_domain_id,start:a.state.start,end:a.state.end}).then((function(t){return a.setState({result:t})}))},a.state={ip:"",start:"",end:"",result:void 0,type:"dhcp"},a}return(0,s.Z)(n,[{key:"componentDidMount",value:function(){var t=this;(0,c.Fh)("api/ipam/network_info",{id:this.props.network_id}).then((function(e){return t.setState((0,a.Z)({},e.data))})),(0,c.Fh)("api/dns/domain_list",{filter:"forward"}).then((function(e){return t.setState({domains:e.data})}))}},{key:"render",value:function(){var t=this;if(this.state.domains){var e=this.props.network_id,n=this.state.result?JSON.stringify(this.state.result.resv):"";return(0,f.jsxs)(l.InfoArticle,{header:"Reservation Address/Scope",children:[(0,f.jsx)("span",{children:"Allocate address with either 'ip' or 'start' to 'end' (e.g. a scope)"}),(0,f.jsxs)(l.InfoColumns,{children:[(0,f.jsx)(h.TextLine,{id:"network_id",label:"Network ID",text:e},"id"),(0,f.jsx)(h.TextLine,{id:"network",text:this.state.network+"/"+this.state.mask},"network"),(0,f.jsx)(h.TextInput,{id:"ip",label:"IP",value:this.state.ip,onChange:this.onChange},"ip"),(0,f.jsx)(h.TextInput,{id:"start",label:"Start IP",value:this.state.start,onChange:this.onChange},"start"),(0,f.jsx)(h.TextInput,{id:"end",label:"End IP",value:this.state.end,onChange:this.onChange},"end"),(0,f.jsxs)(h.SelectInput,{id:"type",label:"Type",value:this.state.type,onChange:this.onChange,children:[(0,f.jsx)("option",{value:"dhcp",children:"dhcp"},"dhcp"),(0,f.jsx)("option",{value:"reservation",children:"reservation"},"reservation")]},"type"),(0,f.jsx)(h.SelectInput,{id:"a_domain_id",label:"Domain",value:this.state.a_domain_id,onChange:this.onChange,children:this.state.domains.map((function(t,e){return(0,f.jsx)("option",{value:t.id,children:t.name},e)}))},"a_domain_id")]},"dn_content"),this.props.changeSelf&&(0,f.jsx)(p.BackButton,{onClick:function(){return t.props.changeSelf((0,f.jsx)(w,{network_id:e,changeSelf:t.props.changeSelf},"resv_list_"+e))}},"dn_btn_back"),(0,f.jsx)(p.SaveButton,{onClick:function(){return t.updateInfo()},title:"Save"},"dn_btn_save"),(0,f.jsx)(l.Result,{result:n},"dn_operation")]},"dn_article")}return(0,f.jsx)(l.Spinner,{})}}]),n}(u.Component)}}]);
//# sourceMappingURL=195.a2f6e65c.chunk.js.map