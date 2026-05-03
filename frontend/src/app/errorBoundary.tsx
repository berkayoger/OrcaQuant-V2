import { Component, ReactNode } from "react";
export class ErrorBoundary extends Component<{children: ReactNode},{hasError:boolean}>{state={hasError:false};static getDerivedStateFromError(){return {hasError:true}};render(){return this.state.hasError?<div>Something went wrong.</div>:this.props.children}}
