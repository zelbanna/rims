"use strict";(self.webpackChunkrims_frontend=self.webpackChunkrims_frontend||[]).push([[823],{823:function(t,e,n){n.r(e),n.d(e,{List:function(){return v},LogShow:function(){return x},TaskShow:function(){return k}});var o=n(942),i=n(413),r=n(671),a=n(144),s=n(340),u=n(882),d=n(791),c=n(252),l=n(885),h=n(355),f=n(698),p=n(682),m=n(184),v=function(t){(0,s.Z)(n,t);var e=(0,u.Z)(n);function n(t){var o;return(0,r.Z)(this,n),(o=e.call(this,t)).listItem=function(t){return[t.node,t.url,(0,m.jsxs)(m.Fragment,{children:[(0,m.jsx)(p.InfoButton,{onClick:function(){return o.changeContent((0,m.jsx)(g,{id:t.id},"node_info"))},title:"Node information"},"info"),(0,m.jsx)(p.DeleteButton,{onClick:function(){return o.deleteList(t.id)},title:"Delete node"},"del")]})]},o.deleteList=function(t){return window.confirm("Really delete node?")&&(0,c.Fh)("api/master/node_delete",{id:t}).then((function(e){e.deleted&&(o.setState({data:o.state.data.filter((function(e){return e.id!==t}))}),o.changeContent(null))}))},o.state={},o}return(0,a.Z)(n,[{key:"componentDidMount",value:function(){var t=this;(0,c.Fh)("api/master/node_list").then((function(e){return t.setState(e)}))}},{key:"render",value:function(){var t=this;return(0,m.jsxs)(m.Fragment,{children:[(0,m.jsxs)(l.ContentList,{header:"Nodes",thead:["Node","URL",""],trows:this.state.data,listItem:this.listItem,children:[(0,m.jsx)(p.ReloadButton,{onClick:function(){return t.componentDidMount()}},"reload"),(0,m.jsx)(p.AddButton,{onClick:function(){return t.changeContent((0,m.jsx)(g,{id:"new"},"node_info"))},title:"Add node"},"add")]},"cl"),(0,m.jsx)(l.ContentData,{mountUpdate:function(e){return t.changeContent=e}},"cda")]})}}]),n}(d.Component),g=function(t){(0,s.Z)(n,t);var e=(0,u.Z)(n);function n(t){var a;return(0,r.Z)(this,n),(a=e.call(this,t)).searchInfo=function(){return(0,c.Fh)("api/device/search",{node:a.state.data.node}).then((function(t){return t.found&&a.setState({data:(0,i.Z)((0,i.Z)({},a.state.data),{},{hostname:t.data.hostname,device_id:t.data.id})})}))},a.onChange=function(t){return a.setState({data:(0,i.Z)((0,i.Z)({},a.state.data),{},(0,o.Z)({},t.target.name,t.target.value))})},a.changeContent=function(t){return a.setState({content:t})},a.updateInfo=function(){return(0,c.Fh)("api/master/node_info",(0,i.Z)({op:"update"},a.state.data)).then((function(t){return a.setState(t)}))},a.state={data:null,found:!0},a}return(0,a.Z)(n,[{key:"componentDidUpdate",value:function(t){t!==this.props&&this.componentDidMount()}},{key:"componentDidMount",value:function(){var t=this;(0,c.Fh)("api/master/node_info",{id:this.props.id}).then((function(e){return t.setState((0,i.Z)((0,i.Z)({},e),{},{content:null}))}))}},{key:"render",value:function(){var t=this;if(this.state.found){if(this.state.data){var e=this.state.data.id,n="new"!==e;return(0,m.jsxs)(m.Fragment,{children:[(0,m.jsxs)(l.InfoArticle,{header:"Node",children:[(0,m.jsxs)(l.InfoColumns,{children:[(0,m.jsx)(f.TextInput,{id:"node",value:this.state.data.node,onChange:this.onChange},"node"),(0,m.jsx)(f.UrlInput,{id:"url",value:this.state.data.url,onChange:this.onChange},"url"),(0,m.jsx)(f.TextInput,{id:"hostname",value:this.state.data.hostname,onChange:this.onChange},"hostname")]},"ic"),(0,m.jsx)(p.SaveButton,{onClick:function(){return t.updateInfo()},title:"Save information"},"save"),n&&!this.state.data.hostname&&(0,m.jsx)(p.SearchButton,{onClick:this.searchInfo,title:"Try to map node to device"},"search"),n&&(0,m.jsx)(p.ReloadButton,{onClick:function(){return t.changeContent((0,m.jsx)(j,{node:t.state.data.node},"node_reload_"+e))}},"reload"),n&&(0,m.jsx)(p.LogButton,{onClick:function(){return t.changeContent((0,m.jsx)(x,{node:t.state.data.node},"node_logs_"+e))},title:"View node logs"},"logs"),n&&(0,m.jsx)(p.DeleteButton,{onClick:function(){return t.changeContent((0,m.jsx)(C,{node:t.state.data.node},"node_logc_"+e))},title:"Clear logs"},"logc"),n&&(0,m.jsx)(p.TimeButton,{onClick:function(){return t.changeContent((0,m.jsx)(k,{node:t.state.data.node},"node_tasks_"+e))},title:"View node tasks"},"tasks")]},"ia_node"),(0,m.jsx)(h.NavBar,{id:"node_navigation"},"node_navigation"),this.state.content]})}return(0,m.jsx)(l.Spinner,{})}return(0,m.jsxs)(l.InfoArticle,{children:["Node with id: ",this.props.id," removed"]},"ia_node")}}]),n}(d.Component),j=function(t){(0,s.Z)(n,t);var e=(0,u.Z)(n);function n(){return(0,r.Z)(this,n),e.apply(this,arguments)}return(0,a.Z)(n,[{key:"componentDidMount",value:function(){var t=this;(0,c.Fh)("api/system/reload",{},{"X-Route":this.props.node}).then((function(e){e?t.setState(e):t.setState({modules:["error reloading modules (check REST call)"]})}))}},{key:"render",value:function(){return this.state?(0,m.jsx)(l.CodeArticle,{header:"Module",children:this.state.modules.join("\n")},"nr_code"):(0,m.jsx)(l.Spinner,{})}}]),n}(d.Component),C=function(t){(0,s.Z)(n,t);var e=(0,u.Z)(n);function n(){return(0,r.Z)(this,n),e.apply(this,arguments)}return(0,a.Z)(n,[{key:"componentDidMount",value:function(){var t=this;(0,c.Fh)("api/system/logs_clear",{},{"X-Route":this.props.node}).then((function(e){return t.setState({logs:e.file})}))}},{key:"render",value:function(){return this.state?(0,m.jsx)(l.CodeArticle,{header:"Cleared",children:Object.entries(this.state.logs).map((function(t){return"".concat(t[0],": ").concat(t[1])})).join("\n")},"nc_code"):(0,m.jsx)(l.Spinner,{})}}]),n}(d.Component),x=function(t){(0,s.Z)(n,t);var e=(0,u.Z)(n);function n(t){var o;return(0,r.Z)(this,n),(o=e.call(this,t)).state={},o}return(0,a.Z)(n,[{key:"componentDidMount",value:function(){var t=this;(0,c.Fh)("api/system/logs_get",{},{"X-Route":this.props.node}).then((function(e){var n=e?{logs:e}:{error:!0};t.setState(n)}))}},{key:"render",value:function(){return this.state.logs?(0,m.jsx)("div",{children:Object.entries(this.state.logs).map((function(t,e){return(0,m.jsx)(l.CodeArticle,{header:t[0],children:t[1].join("\n")},e)}))}):this.state.error?(0,m.jsx)(l.CodeArticle,{children:"error retrieving logs (check REST call)"}):(0,m.jsx)(l.Spinner,{})}}]),n}(d.Component),k=function(t){(0,s.Z)(n,t);var e=(0,u.Z)(n);function n(t){var o;return(0,r.Z)(this,n),(o=e.call(this,t)).listItem=function(t){return[t.module,t.function,t.frequency,JSON.stringify(t.output),JSON.stringify(t.args)]},o.state={},o}return(0,a.Z)(n,[{key:"componentDidMount",value:function(){var t=this;(0,c.Fh)("api/system/task_list",{},{"X-Route":this.props.node}).then((function(e){var n=e?{tasks:e}:{error:!0};t.setState(n)}))}},{key:"render",value:function(){return this.state.tasks?(0,m.jsx)(l.ContentReport,{header:"Tasks",thead:["Module","Function","Frequency","Output","Arguments"],trows:this.state.tasks.data,listItem:this.listItem},"cr_task_show"):this.state.error?(0,m.jsx)(l.CodeArticle,{children:"error retrieving tasks (check REST call)"}):(0,m.jsx)(l.Spinner,{})}}]),n}(d.Component)}}]);
//# sourceMappingURL=823.497d8be4.chunk.js.map