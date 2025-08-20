import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux'; 
import App from './App.jsx';
import './index.css';
import './index copy.css';
import ContextProvider from "./context/Context.jsx";
import store from './store/store'; 

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Provider store={store}> 
      <ContextProvider> 
        <App />
      </ContextProvider>
    </Provider>
  </React.StrictMode>
);