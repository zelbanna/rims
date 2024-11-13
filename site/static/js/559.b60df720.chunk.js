"use strict";(self.webpackChunkrims_frontend=self.webpackChunkrims_frontend||[]).push([[559],{559:(t,e,s)=>{s.r(e),s.d(e,{Edit:()=>p,List:()=>c,Main:()=>r});var i=s(791),n=s(587),o=s(885),a=s(682),h=s(698),d=s(582),l=s(184);class r extends i.Component{constructor(t){super(t),this.changeContent=t=>this.setState(t),this.state=(0,l.jsx)(c,{},"viz_list")}render(){return(0,l.jsx)(l.Fragment,{children:this.state})}}class c extends i.Component{constructor(t){super(t),this.listItem=t=>[t.id,t.name,(0,l.jsxs)(l.Fragment,{children:[(0,l.jsx)(a.EditButton,{onClick:()=>this.changeContent((0,l.jsx)(p,{id:t.id,changeSelf:this.changeContent,type:"map"},"viz_edit_"+t.id)),title:"Show and edit map"},"edit"),(0,l.jsx)(a.NetworkButton,{onClick:()=>window.open(`viz.html?id=${t.id}`,"_blank"),title:"Show resulting map"},"net"),(0,l.jsx)(a.DeleteButton,{onClick:()=>this.deleteList(t.id)},"del")]})],this.deleteList=t=>window.confirm("Delete map?")&&(0,n.Fh)("api/visualize/delete",{id:t}).then((e=>{e.deleted&&(this.setState({data:this.state.data.filter((e=>e.id!==t))}),this.changeContent(null))})),this.state={}}componentDidMount(){(0,n.Fh)("api/visualize/list").then((t=>{this.setState(t)}))}render(){return(0,l.jsxs)(l.Fragment,{children:[(0,l.jsx)(o.ContentList,{header:"Maps",thead:["ID","Name",""],trows:this.state.data,listItem:this.listItem,children:(0,l.jsx)(a.ReloadButton,{onClick:()=>this.componentDidMount()},"reload")},"cl"),(0,l.jsx)(o.ContentData,{mountUpdate:t=>this.changeContent=t},"cda")]})}}class p extends i.Component{constructor(t){super(t),this.changeContent=t=>this.setState({content:t}),this.changeImport=t=>s.e(531).then(s.bind(s,531)).then((e=>this.props.changeSelf((0,l.jsx)(e.Info,{id:t},"di_"+t)))),this.onChange=t=>this.setState({data:{...this.state.data,[t.target.name]:t.target.value}}),this.jsonHandler=t=>{var e={...this.state.data};try{e[t.target.name]=JSON.parse(t.target.value),this.setState({data:e})}catch{console.log("Error converting string to JSON")}},this.updateInfo=()=>(0,n.Fh)("api/visualize/network",{op:"update",...this.state.data}).then((t=>this.setState(t))),this.doubleClick=t=>{console.log("DoubleClick",t.nodes[0]),this.props.changeSelf&&this.changeImport(t.nodes[0])},this.toggleEdit=()=>{this.edit=!this.edit,this.viz.network.setOptions({manipulation:{enabled:this.edit}}),this.setState({result:"Edit:"+this.edit})},this.toggleFix=()=>{this.viz.nodes.forEach(((t,e)=>this.viz.nodes.update({id:e,fixed:!t.fixed}))),this.setState({data:{...this.state.data,nodes:this.viz.nodes.get()},result:"Fix/Unfix positions"})},this.togglePhysics=()=>{const t=this.state.data;t.options.physics.enabled=!t.options.physics.enabled,this.viz.network.setOptions({physics:t.options.physics.enabled}),this.setState({data:t,physics_button:t.options.physics.enabled?a.StopButton:a.StartButton,result:"Physics:"+t.options.physics.enabled})},this.networkSync=t=>{this.viz.network.storePositions(),this.setState({data:{...this.state.data,nodes:this.viz.nodes.get(),edges:this.viz.edges.get()},result:"Moved "+this.viz.nodes.get(t.nodes[0]).label})},this.showDiv=t=>t===this.state.content?{display:"block"}:{display:"none"},this.state={content:"network",physics_button:a.StartButton,found:!0,data:{name:"N/A"},result:""},this.viz={network:null,nodes:null,edges:null},this.canvas=i.createRef(),this.edit=!1}componentDidMount(){s.e(778).then(s.bind(s,778)).then((t=>{(0,n.Fh)("api/visualize/network",{id:this.props.id,type:this.props.type}).then((e=>{this.viz.nodes=new t.DataSet(e.data.nodes),this.viz.edges=new t.DataSet(e.data.edges),e.data.options.physics.enabled=!0,e.data.options.clickToUse=!0,this.viz.network=new t.Network(this.canvas.current,{nodes:this.viz.nodes,edges:this.viz.edges},e.data.options),this.viz.network.on("stabilizationIterationsDone",(()=>this.viz.network.setOptions({physics:!1}))),this.viz.network.on("doubleClick",(t=>this.doubleClick(t))),this.viz.network.on("dragEnd",(t=>this.networkSync(t))),e.data.options.physics.enabled=!1,this.setState(e)}))}))}render(){const t=this.state.physics_button;return(0,l.jsxs)(o.Article,{header:"Network Map",children:["device"===this.props.type&&this.props.changeSelf&&(0,l.jsx)(a.BackButton,{onClick:()=>this.changeImport(this.props.id)},"viz_back"),(0,l.jsx)(a.ReloadButton,{onClick:()=>this.componentDidMount()},"viz_reload"),(0,l.jsx)(a.EditButton,{onClick:()=>this.toggleEdit()},"viz_edit"),(0,l.jsx)(t,{onClick:()=>this.togglePhysics()},"viz_physics"),(0,l.jsx)(a.FixButton,{onClick:()=>this.toggleFix()},"viz_fix"),(0,l.jsx)(a.SaveButton,{onClick:()=>this.updateInfo()},"viz_save"),(0,l.jsx)(a.NetworkButton,{onClick:()=>this.changeContent("network")},"viz_net"),(0,l.jsx)(a.TextButton,{text:"Options",onClick:()=>this.changeContent("options")},"viz_opt"),(0,l.jsx)(a.TextButton,{text:"Nodes",onClick:()=>this.changeContent("nodes")},"viz_nodes"),(0,l.jsx)(a.TextButton,{text:"Edges",onClick:()=>this.changeContent("edges")},"viz_edges"),(0,l.jsx)(h.TextInput,{id:"name",value:this.state.data.name,onChange:this.onChange},"viz_name"),(0,l.jsx)(o.Result,{result:this.state.result},"viz_result"),(0,l.jsx)("div",{className:d.Z.network,style:this.showDiv("network"),ref:this.canvas}),(0,l.jsx)("div",{className:d.Z.network,style:this.showDiv("options"),children:(0,l.jsx)("textarea",{id:"options",name:"options",value:JSON.stringify(this.state.data.options,void 0,2),onChange:this.jsonHandler})}),(0,l.jsx)("div",{className:d.Z.network,style:this.showDiv("nodes"),children:(0,l.jsx)("textarea",{id:"nodes",name:"nodes",value:JSON.stringify(this.state.data.nodes,void 0,2),onChange:this.jsonHandler})}),(0,l.jsx)("div",{className:d.Z.network,style:this.showDiv("edges"),children:(0,l.jsx)("textarea",{id:"edges",name:"edges",value:JSON.stringify(this.state.data.edges,void 0,2),onChange:this.jsonHandler})})]},"viz_art")}}}}]);
//# sourceMappingURL=559.b60df720.chunk.js.map