import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import '@babel/polyfill';

ReactDOM.render(
    <App />,
    /* <React.StrictMode>
        <App />
        </React.StrictMode>, */
    document.getElementById('root')
);
