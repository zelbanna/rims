"use strict";(self.webpackChunkrims_frontend=self.webpackChunkrims_frontend||[]).push([[823],{823:(t,e,n)=>{n.r(e),n.d(e,{Info:()=>h,List:()=>c});var i=n(43),s=n(524),o=n(662),a=n(728),d=n(97),l=n(579);class c extends i.Component{constructor(t){super(t),this.deleteList=t=>window.confirm("Really delete location?")&&(0,s.Cc)("api/location/delete",{id:t}).then((e=>{e.deleted&&(this.setState({data:this.state.data.filter((e=>e.id!==t))}),this.changeContent(null))})),this.listItem=t=>[t.id,t.name,(0,l.jsxs)(l.Fragment,{children:[(0,l.jsx)(a.ConfigureButton,{onClick:()=>this.changeContent((0,l.jsx)(h,{id:t.id},"location")),title:"Edit location"},"conf"),(0,l.jsx)(a.DeleteButton,{onClick:()=>this.deleteList(t.id),title:"Delete location"},"del")]})],this.state={}}componentDidMount(){(0,s.Cc)("api/location/list").then((t=>this.setState(t)))}render(){return(0,l.jsxs)(l.Fragment,{children:[(0,l.jsxs)(o.ContentList,{header:"Locations",thead:["ID","Name",""],trows:this.state.data,listItem:this.listItem,children:[(0,l.jsx)(a.ReloadButton,{onClick:()=>this.componentDidMount()},"reload"),(0,l.jsx)(a.AddButton,{onClick:()=>this.changeContent((0,l.jsx)(h,{id:"new"},"location")),title:"Add location"},"add")]},"cl"),(0,l.jsx)(o.ContentData,{mountUpdate:t=>this.changeContent=t},"cda")]})}}class h extends i.Component{constructor(t){super(t),this.onChange=t=>this.setState({data:{...this.state.data,[t.target.name]:t.target.value}}),this.updateInfo=()=>(0,s.Cc)("api/location/info",{op:"update",...this.state.data}).then((t=>this.setState(t))),this.state={data:null,found:!0}}componentDidUpdate(t,e){t!==this.props&&this.componentDidMount()}componentDidMount(){(0,s.Cc)("api/location/info",{id:this.props.id}).then((t=>this.setState(t)))}render(){return this.state.found?this.state.data?(0,l.jsxs)(o.InfoArticle,{header:"Location",children:[(0,l.jsx)(o.InfoColumns,{children:(0,l.jsx)(d.TextInput,{id:"name",value:this.state.data.name,onChange:this.onChange},"name")},"ic"),(0,l.jsx)(a.SaveButton,{onClick:()=>this.updateInfo(),title:"Save"},"save")]},"ia_loc"):(0,l.jsx)(o.Spinner,{}):(0,l.jsxs)(o.InfoArticle,{children:["Location id: ",this.props.id," removed"]},"ia_loc")}}}}]);
//# sourceMappingURL=823.e6f71b1f.chunk.js.map