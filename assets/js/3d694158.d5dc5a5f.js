"use strict";(self.webpackChunkwebsite=self.webpackChunkwebsite||[]).push([[8199],{3905:function(e,t,n){n.d(t,{Zo:function(){return p},kt:function(){return h}});var r=n(67294);function a(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function l(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function i(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?l(Object(n),!0).forEach((function(t){a(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):l(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function o(e,t){if(null==e)return{};var n,r,a=function(e,t){if(null==e)return{};var n,r,a={},l=Object.keys(e);for(r=0;r<l.length;r++)n=l[r],t.indexOf(n)>=0||(a[n]=e[n]);return a}(e,t);if(Object.getOwnPropertySymbols){var l=Object.getOwnPropertySymbols(e);for(r=0;r<l.length;r++)n=l[r],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(a[n]=e[n])}return a}var s=r.createContext({}),u=function(e){var t=r.useContext(s),n=t;return e&&(n="function"==typeof e?e(t):i(i({},t),e)),n},p=function(e){var t=u(e.components);return r.createElement(s.Provider,{value:t},e.children)},c={inlineCode:"code",wrapper:function(e){var t=e.children;return r.createElement(r.Fragment,{},t)}},d=r.forwardRef((function(e,t){var n=e.components,a=e.mdxType,l=e.originalType,s=e.parentName,p=o(e,["components","mdxType","originalType","parentName"]),d=u(n),h=a,m=d["".concat(s,".").concat(h)]||d[h]||c[h]||l;return n?r.createElement(m,i(i({ref:t},p),{},{components:n})):r.createElement(m,i({ref:t},p))}));function h(e,t){var n=arguments,a=t&&t.mdxType;if("string"==typeof e||a){var l=n.length,i=new Array(l);i[0]=d;var o={};for(var s in t)hasOwnProperty.call(t,s)&&(o[s]=t[s]);o.originalType=e,o.mdxType="string"==typeof e?e:a,i[1]=o;for(var u=2;u<l;u++)i[u]=n[u];return r.createElement.apply(null,i)}return r.createElement.apply(null,n)}d.displayName="MDXCreateElement"},98964:function(e,t,n){n.r(t),n.d(t,{frontMatter:function(){return o},contentTitle:function(){return s},metadata:function(){return u},toc:function(){return p},default:function(){return d}});var r=n(87462),a=n(63366),l=(n(67294),n(3905)),i=["components"],o={sidebar_label:"rath",title:"rath"},s=void 0,u={unversionedId:"reference/rath",id:"reference/rath",title:"rath",description:"Rath Objects",source:"@site/docs/reference/rath.md",sourceDirName:"reference",slug:"/reference/rath",permalink:"/rath/docs/reference/rath",editUrl:"https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/docs/reference/rath.md",tags:[],version:"current",frontMatter:{sidebar_label:"rath",title:"rath"},sidebar:"tutorialSidebar",previous:{title:"operation",permalink:"/rath/docs/reference/operation"},next:{title:"registry",permalink:"/rath/docs/reference/registry"}},p=[{value:"Rath Objects",id:"rath-objects",children:[{value:"link",id:"link",children:[],level:4},{value:"auto_connect",id:"auto_connect",children:[],level:4},{value:"connect_on_enter",id:"connect_on_enter",children:[],level:4},{value:"aconnect",id:"aconnect",children:[],level:4},{value:"adisconnect",id:"adisconnect",children:[],level:4},{value:"aquery",id:"aquery",children:[],level:4},{value:"query",id:"query",children:[],level:4},{value:"subscribe",id:"subscribe",children:[],level:4}],level:2}],c={toc:p};function d(e){var t=e.components,n=(0,a.Z)(e,i);return(0,l.kt)("wrapper",(0,r.Z)({},c,n,{components:t,mdxType:"MDXLayout"}),(0,l.kt)("h2",{id:"rath-objects"},"Rath Objects"),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},"class Rath(KoiledModel)\n")),(0,l.kt)("p",null,"A Rath is a client for a GraphQL API."),(0,l.kt)("p",null,"Links are used to define the transport logic of the Rath. A Rath can be\nconnected to a GraphQL API using a terminating link. By composing links to\nform a chain, you can define the transport logic of the client."),(0,l.kt)("p",null,"For example, a Rath can be connected to a GraphQL API over HTTP by\ncomposing an HTTP terminating link with a RetryLink. The RetryLink will\nretry failed requests, and the HTTP terminating link will send the\nrequests over HTTP."),(0,l.kt)("p",null,(0,l.kt)("strong",{parentName:"p"},"Example"),":"),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},"from rath import Rath\nfrom rath.links.retriy import RetryLink\nfrom rathlinks.aiohttp import  AioHttpLink\n\nretry = RetryLink()\nhttp = AioHttpLink(&quot;https://graphql-pokemon.now.sh/graphql&quot;)\n\nrath = Rath(link=compose(retry, link))\nasync with rath as rath:\nawait rath.aquery(...)\n")),(0,l.kt)("h4",{id:"link"},"link"),(0,l.kt)("p",null,"The terminating link used to send operations to the server. Can be a composed link chain."),(0,l.kt)("h4",{id:"auto_connect"},"auto","_","connect"),(0,l.kt)("p",null,"If true, the Rath will automatically connect to the server when a query is executed."),(0,l.kt)("h4",{id:"connect_on_enter"},"connect","_","on","_","enter"),(0,l.kt)("p",null,"If true, the Rath will automatically connect to the server when entering the context manager."),(0,l.kt)("h4",{id:"aconnect"},"aconnect"),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},"async def aconnect()\n")),(0,l.kt)("p",null,"Connect to the server."),(0,l.kt)("p",null,"This method needs to be called within the context of a Rath instance,\nto always ensure that the Rath is disconnected when the context is\nexited."),(0,l.kt)("p",null,"This method is called automatically when a query is executed if\n",(0,l.kt)("inlineCode",{parentName:"p"},"auto_connect")," is set to True."),(0,l.kt)("p",null,(0,l.kt)("strong",{parentName:"p"},"Raises"),":"),(0,l.kt)("ul",null,(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"NotEnteredError")," - Raises an error if the Rath is not entered.")),(0,l.kt)("h4",{id:"adisconnect"},"adisconnect"),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},"async def adisconnect()\n")),(0,l.kt)("p",null,"Disconnect from the server."),(0,l.kt)("h4",{id:"aquery"},"aquery"),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},"async def aquery(query: Union[str, DocumentNode],\n                 variables: Dict[str, Any] = None,\n                 headers: Dict[str, Any] = None,\n                 operation_name: str = None,\n                 **kwargs) -> GraphQLResult\n")),(0,l.kt)("p",null,"Query the GraphQL API."),(0,l.kt)("p",null,"Takes a querystring, variables, and headers and returns the result.\nIf provided, the operation_name will be used to identify which operation\nto execute."),(0,l.kt)("p",null,(0,l.kt)("strong",{parentName:"p"},"Arguments"),":"),(0,l.kt)("ul",null,(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"query")," ",(0,l.kt)("em",{parentName:"li"},"str | DocumentNode")," - The query string or the DocumentNode."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"variables")," ",(0,l.kt)("em",{parentName:"li"},"Dict","[str, Any]",", optional")," - The variables. Defaults to None."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"headers")," ",(0,l.kt)("em",{parentName:"li"},"Dict","[str, Any]",", optional")," - Additional headers. Defaults to None."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"operation_name")," ",(0,l.kt)("em",{parentName:"li"},"str, optional")," - The operation_name to executed. Defaults to all."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"**kwargs")," - Additional arguments to pass to the link chain")),(0,l.kt)("p",null,(0,l.kt)("strong",{parentName:"p"},"Raises"),":"),(0,l.kt)("ul",null,(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"NotConnectedError")," - An error when the Rath is not connected and autoload is set to false")),(0,l.kt)("p",null,(0,l.kt)("strong",{parentName:"p"},"Returns"),":"),(0,l.kt)("ul",null,(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"GraphQLResult")," - The result of the query")),(0,l.kt)("h4",{id:"query"},"query"),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},"def query(query: Union[str, DocumentNode],\n          variables: Dict[str, Any] = None,\n          headers: Dict[str, Any] = None,\n          operation_name: str = None,\n          **kwargs) -> GraphQLResult\n")),(0,l.kt)("p",null,"Query the GraphQL API."),(0,l.kt)("p",null,"Takes a querystring, variables, and headers and returns the result.\nIf provided, the operation_name will be used to identify which operation\nto execute."),(0,l.kt)("p",null,(0,l.kt)("strong",{parentName:"p"},"Arguments"),":"),(0,l.kt)("ul",null,(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"query")," ",(0,l.kt)("em",{parentName:"li"},"str | DocumentNode")," - The query string or the DocumentNode."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"variables")," ",(0,l.kt)("em",{parentName:"li"},"Dict","[str, Any]",", optional")," - The variables. Defaults to None."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"headers")," ",(0,l.kt)("em",{parentName:"li"},"Dict","[str, Any]",", optional")," - Additional headers. Defaults to None."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"operation_name")," ",(0,l.kt)("em",{parentName:"li"},"str, optional")," - The operation_name to executed. Defaults to all."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"**kwargs")," - Additional arguments to pass to the link chain")),(0,l.kt)("p",null,(0,l.kt)("strong",{parentName:"p"},"Raises"),":"),(0,l.kt)("ul",null,(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"NotConnectedError")," - An error when the Rath is not connected and autoload is set to false")),(0,l.kt)("p",null,(0,l.kt)("strong",{parentName:"p"},"Returns"),":"),(0,l.kt)("ul",null,(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"GraphQLResult")," - The result of the query")),(0,l.kt)("h4",{id:"subscribe"},"subscribe"),(0,l.kt)("pre",null,(0,l.kt)("code",{parentName:"pre",className:"language-python"},"def subscribe(query: str,\n              variables: Dict[str, Any] = None,\n              headers: Dict[str, Any] = None,\n              operation_name: str = None,\n              **kwargs) -> Iterator[GraphQLResult]\n")),(0,l.kt)("p",null,"Subscripe to a GraphQL API."),(0,l.kt)("p",null,"Takes a querystring, variables, and headers and returns an async iterator\nthat yields the results."),(0,l.kt)("p",null,(0,l.kt)("strong",{parentName:"p"},"Arguments"),":"),(0,l.kt)("ul",null,(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"query")," ",(0,l.kt)("em",{parentName:"li"},"str | DocumentNode")," - The query string or the DocumentNode."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"variables")," ",(0,l.kt)("em",{parentName:"li"},"Dict","[str, Any]",", optional")," - The variables. Defaults to None."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"headers")," ",(0,l.kt)("em",{parentName:"li"},"Dict","[str, Any]",", optional")," - Additional headers. Defaults to None."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"operation_name")," ",(0,l.kt)("em",{parentName:"li"},"str, optional")," - The operation_name to executed. Defaults to all."),(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"**kwargs")," - Additional arguments to pass to the link chain")),(0,l.kt)("p",null,(0,l.kt)("strong",{parentName:"p"},"Raises"),":"),(0,l.kt)("ul",null,(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"NotConnectedError")," - An error when the Rath is not connected and autoload is set to false")),(0,l.kt)("p",null,(0,l.kt)("strong",{parentName:"p"},"Yields"),":"),(0,l.kt)("ul",null,(0,l.kt)("li",{parentName:"ul"},(0,l.kt)("inlineCode",{parentName:"li"},"Iterator[GraphQLResult]")," - The result of the query as an async iterator")))}d.isMDXComponent=!0}}]);