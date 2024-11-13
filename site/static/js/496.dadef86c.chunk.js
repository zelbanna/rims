"use strict";(self.webpackChunkrims_frontend=self.webpackChunkrims_frontend||[]).push([[496,208],{208:(t,e,n)=>{n.r(e),n.d(e,{Info:()=>l,List:()=>h});var i=n(791),s=n(587),a=n(885),o=n(682),d=n(698),c=n(184);class h extends i.Component{constructor(t){super(t),this.deleteList=t=>window.confirm("Really delete location?")&&(0,s.Fh)("api/location/delete",{id:t}).then((e=>{e.deleted&&(this.setState({data:this.state.data.filter((e=>e.id!==t))}),this.changeContent(null))})),this.listItem=t=>[t.id,t.name,(0,c.jsxs)(c.Fragment,{children:[(0,c.jsx)(o.ConfigureButton,{onClick:()=>this.changeContent((0,c.jsx)(l,{id:t.id},"location")),title:"Edit location"},"conf"),(0,c.jsx)(o.DeleteButton,{onClick:()=>this.deleteList(t.id),title:"Delete location"},"del")]})],this.state={}}componentDidMount(){(0,s.Fh)("api/location/list").then((t=>this.setState(t)))}render(){return(0,c.jsxs)(c.Fragment,{children:[(0,c.jsxs)(a.ContentList,{header:"Locations",thead:["ID","Name",""],trows:this.state.data,listItem:this.listItem,children:[(0,c.jsx)(o.ReloadButton,{onClick:()=>this.componentDidMount()},"reload"),(0,c.jsx)(o.AddButton,{onClick:()=>this.changeContent((0,c.jsx)(l,{id:"new"},"location")),title:"Add location"},"add")]},"cl"),(0,c.jsx)(a.ContentData,{mountUpdate:t=>this.changeContent=t},"cda")]})}}class l extends i.Component{constructor(t){super(t),this.onChange=t=>this.setState({data:{...this.state.data,[t.target.name]:t.target.value}}),this.updateInfo=()=>(0,s.Fh)("api/location/info",{op:"update",...this.state.data}).then((t=>this.setState(t))),this.state={data:null,found:!0}}componentDidUpdate(t,e){t!==this.props&&this.componentDidMount()}componentDidMount(){(0,s.Fh)("api/location/info",{id:this.props.id}).then((t=>this.setState(t)))}render(){return this.state.found?this.state.data?(0,c.jsxs)(a.InfoArticle,{header:"Location",children:[(0,c.jsx)(a.InfoColumns,{children:(0,c.jsx)(d.TextInput,{id:"name",value:this.state.data.name,onChange:this.onChange},"name")},"ic"),(0,c.jsx)(o.SaveButton,{onClick:()=>this.updateInfo(),title:"Save"},"save")]},"ia_loc"):(0,c.jsx)(a.Spinner,{}):(0,c.jsxs)(a.InfoArticle,{children:["Location id: ",this.props.id," removed"]},"ia_loc")}}},496:(t,e,n)=>{n.r(e),n.d(e,{Infra:()=>g,Layout:()=>k,List:()=>C,Main:()=>_});var i=n(791),s=n(587),a=n(885),o=n(698),d=n(682),c=n(355);const h="rack_rack__l-0E+",l="rack_rackLeft__jopWv",r="rack_rackRight__cbJDU",p="rack_rackItem__UiGLd";var u=n(531),x=n(208),m=n(184);class _ extends i.Component{constructor(t){super(t),this.compileNavItems=()=>this.context.loadNavigation((0,m.jsxs)(c.NavBar,{children:[(0,m.jsxs)(c.NavDropDown,{title:"Rack",children:[(0,m.jsx)(c.NavDropButton,{title:"Racks",onClick:()=>this.changeContent((0,m.jsx)(C,{},"rack_list"))},"dev_nav_all_rack"),(0,m.jsx)(c.NavDropButton,{title:"PDUs",onClick:()=>this.changeContent((0,m.jsx)(g,{type:"pdu"},"pdu_list"))},"dev_nav_all_pdu"),(0,m.jsx)(c.NavDropButton,{title:"Consoles",onClick:()=>this.changeContent((0,m.jsx)(g,{type:"console"},"console_list"))},"dev_nav_all_con")]},"dev_nav_racks"),(0,m.jsx)(c.NavButton,{title:"Locations",onClick:()=>this.changeContent((0,m.jsx)(x.List,{},"location_list"))},"dev_nav_loc")]},"rack_navbar")),this.changeContent=t=>this.setState(t),this.state=(0,m.jsx)(C,{},"rack_list")}componentDidMount(){this.compileNavItems()}componentDidUpdate(t){t!==this.props&&this.compileNavItems()}render(){return(0,m.jsx)(m.Fragment,{children:this.state})}}_.contextType=a.RimsContext;class C extends i.Component{constructor(t){super(t),this.listItem=t=>[(0,m.jsx)(d.HrefButton,{text:t.location,onClick:()=>this.changeContent((0,m.jsx)(x.Info,{id:t.location_id},"li_"+t.location_id))},"rl_btn_loc_"+t.id),t.name,(0,m.jsxs)(m.Fragment,{children:[(0,m.jsx)(d.InfoButton,{onClick:()=>this.changeContent((0,m.jsx)(j,{id:t.id},"rack_info_"+t.id)),title:"Rack information"},"info"),(0,m.jsx)(d.GoButton,{onClick:()=>this.context.changeMain((0,m.jsx)(u.Main,{rack_id:t.id},"rack_device_"+t.id)),title:"Rack inventory"},"go"),(0,m.jsx)(d.ItemsButton,{onClick:()=>this.changeContent((0,m.jsx)(k,{id:t.id,changeSelf:this.changeContent},"rack_layout_"+t.id)),title:"Rack layout"},"items"),(0,m.jsx)(d.DeleteButton,{onClick:()=>this.deleteList(t.id),title:"Delete rack"},"del")]})],this.deleteList=t=>window.confirm("Really delete rack?")&&(0,s.Fh)("api/rack/delete",{id:t}).then((e=>{e.deleted&&(this.setState({data:this.state.data.filter((e=>e.id!==t))}),this.changeContent(null))})),this.state={}}componentDidMount(){(0,s.Fh)("api/rack/list",{sort:"name"}).then((t=>this.setState(t)))}render(){return(0,m.jsxs)(m.Fragment,{children:[(0,m.jsxs)(a.ContentList,{header:"Racks",thead:["Location","Name",""],trows:this.state.data,listItem:this.listItem,children:[(0,m.jsx)(d.ReloadButton,{onClick:()=>this.componentDidMount()},"reload"),(0,m.jsx)(d.AddButton,{onClick:()=>this.changeContent((0,m.jsx)(j,{id:"new"},"rack_new_"+(0,s.P4)())),title:"Add rack"},"add")]},"cl"),(0,m.jsx)(a.ContentData,{mountUpdate:t=>this.changeContent=t},"cda")]})}}C.contextType=a.RimsContext;class j extends i.Component{constructor(t){super(t),this.onChange=t=>this.setState({data:{...this.state.data,[t.target.name]:t.target.value}}),this.updateInfo=()=>(0,s.Fh)("api/rack/info",{op:"update",...this.state.data}).then((t=>this.setState(t))),this.state={data:null,found:!0}}componentDidMount(){(0,s.Fh)("api/rack/info",{id:this.props.id}).then((t=>this.setState(t)))}render(){return this.state.data?(0,m.jsxs)(a.InfoArticle,{header:"Rack",children:[(0,m.jsxs)(a.InfoColumns,{children:[(0,m.jsx)(o.TextInput,{id:"name",value:this.state.data.name,onChange:this.onChange},"name"),(0,m.jsx)(o.TextInput,{id:"size",value:this.state.data.size,onChange:this.onChange},"size"),(0,m.jsx)(o.SelectInput,{id:"console",value:this.state.data.console,onChange:this.onChange,children:this.state.consoles.map((t=>(0,m.jsx)("option",{value:t.id,children:t.hostname},t.id)))},"console"),(0,m.jsx)(o.SelectInput,{id:"location_id",label:"Location",value:this.state.data.location_id,onChange:this.onChange,children:this.state.locations.map((t=>(0,m.jsx)("option",{value:t.id,children:t.name},t.id)))},"location_id"),(0,m.jsx)(o.SelectInput,{id:"pdu_1",label:"PDU1",value:this.state.data.pdu_1,onChange:this.onChange,children:this.state.pdus.map((t=>(0,m.jsx)("option",{value:t.id,children:t.hostname},t.id)))},"pdu_1"),(0,m.jsx)(o.SelectInput,{id:"pdu_2",label:"PDU2",value:this.state.data.pdu_2,onChange:this.onChange,children:this.state.pdus.map((t=>(0,m.jsx)("option",{value:t.id,children:t.hostname},t.id)))},"pdu_2")]},"rack_content"),(0,m.jsx)(d.SaveButton,{onClick:()=>this.updateInfo(),title:"Save"},"ri_btn_save")]},"rack_article"):(0,m.jsx)(a.Spinner,{})}}class k extends i.Component{constructor(t){super(t),this.changeContent=t=>{this.props.changeSelf&&this.props.changeSelf(t)},this.state={}}componentDidMount(){(0,s.Fh)("api/rack/devices",{id:this.props.id}).then((t=>this.setState(t)))}createRack(t,e,n){const i=[];for(let s=1;s<this.state.size+1;s++)i.push((0,m.jsx)("div",{className:l,style:{gridRow:-s},children:s},"left_"+s),(0,m.jsx)("div",{className:r,style:{gridRow:-s},children:s},"right_"+s));return e.forEach((t=>i.push((0,m.jsx)("div",{className:p,style:{gridRowStart:this.state.size+2-n*t.rack_unit,gridRowEnd:this.state.size+2-(n*t.rack_unit+t.rack_size)},children:(0,m.jsx)(d.HrefButton,{style:{color:"var(--ui-txt-color)"},onClick:()=>this.changeContent((0,m.jsx)(u.Info,{id:t.id},"device_info")),text:t.hostname},"rd_btn_"+t.id)},"dev_"+t.id)))),(0,m.jsx)("div",{className:h,style:{grid:`repeat(${this.state.size-1}, 2vw)/2vw 25vw 2vw`},children:i})}render(){return this.state.size?(0,m.jsxs)(m.Fragment,{children:[(0,m.jsx)(a.InfoArticle,{header:"Front",children:this.createRack("front",this.state.front,1)},"rl_front"),(0,m.jsx)(a.InfoArticle,{header:"Back",children:this.createRack("back",this.state.back,-1)},"rl_back")]}):(0,m.jsx)(a.Spinner,{})}}class g extends i.Component{constructor(t){super(t),this.listItem=t=>[(0,m.jsx)(d.HrefButton,{text:t.id,onClick:()=>this.changeContent((0,m.jsx)(u.Info,{id:t.id},"device_"+t.id)),title:"Device info"},"dev_"+t.id),t.hostname,(0,m.jsx)(d.InfoButton,{onClick:()=>this.context.changeMain({module:t.type_base,function:"Manage",args:{device_id:t.id,type:t.type_name}}),title:"Manage device"},"rinfra_btn_"+t.id)],this.state={}}componentDidMount(){(0,s.Fh)("api/device/list",{field:"base",search:this.props.type,extra:["type"]}).then((t=>this.setState(t)))}render(){return(0,m.jsxs)(m.Fragment,{children:[(0,m.jsx)(a.ContentList,{header:this.props.type,thead:["ID","Name",""],trows:this.state.data,listItem:this.listItem,children:(0,m.jsx)(d.ReloadButton,{onClick:()=>this.componentDidMount()},"reload")},"cl"),(0,m.jsx)(a.ContentData,{mountUpdate:t=>this.changeContent=t},"cda")]})}}g.contextType=a.RimsContext}}]);
//# sourceMappingURL=496.dadef86c.chunk.js.map