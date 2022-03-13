import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import List from './list';
import reportWebVitals from './reportWebVitals';

// export default class App extends React.Component{
// 	render() {
// 		return <List />, document.getElementById('root')
// 	}
// }

ReactDOM.render(<List />, document.getElementById('root'));

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
